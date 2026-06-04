from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pyvista as pv
import scienceplots
from PIL import Image


plt.style.use(['science', 'ieee'])
# --- SEEP2026 template: force Times New Roman to match the manuscript body ---
plt.rcParams.update({
    'text.usetex': False,
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'Nimbus Roman No9 L', 'DejaVu Serif'],
    'mathtext.fontset': 'stix',
})
plt.rcParams['figure.dpi'] = 300
plt.rcParams['figure.figsize'] = (6, 4)
plt.rcParams['font.size'] = 18
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['legend.fontsize'] = 14
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['lines.linewidth'] = 1.2
plt.rcParams['lines.markersize'] = 4
plt.rcParams['legend.loc'] = 'best'
plt.rcParams['legend.frameon'] = False
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
plt.rcParams['xtick.top'] = False
plt.rcParams['ytick.right'] = False


ROTOR_DIAMETER = 126.0
ROTOR_CENTER = np.array([0.0, 0.0, 90.0]) / ROTOR_DIAMETER
ROTOR_RADIUS = 63.0 / ROTOR_DIAMETER
ROTOR_LINE_RADIUS = 2.5 / ROTOR_DIAMETER

PATH_RANS_ORIGINAL_XZ = Path('dataset') / 'riferimento rans' / 'yNormal.vtp'
PATH_LES_AND_MODIFIED = Path('dataset') / 'dati_per_rete' / 'rans_mesh_with_les_data_.vtp'
OUTPUT_RANS_NUT = Path('methodology') / 'img' / 'cfds_rans_nut_xz.png'
OUTPUT_LES_NUTEQ = Path('methodology') / 'img' / 'cfds_les_nutEq_xz.png'
OUTPUT_MODIFIED_NUT = Path('methodology') / 'img' / 'cfds_modified_nut_xz.png'
Z_MAX = 2.5


def read_mesh(path):
    mesh = pv.read(path)
    mesh.points = mesh.points / ROTOR_DIAMETER
    mesh['U_mag'] = np.linalg.norm(mesh['U'], axis=1)
    return mesh


def extract_xz(mesh):
    mask = np.isclose(mesh.points[:, 1], 0.0, atol=1e-8)
    return mesh.extract_points(mask, adjacent_cells=False, include_cells=True)


def crop_to_low_z(mesh, z_max=Z_MAX):
    return mesh.clip(normal='z', origin=(0.0, 0.0, z_max), invert=True)


def make_rotor_geometry():
    rotor_line_xz = pv.Line(
        ROTOR_CENTER + np.array([0.0, 0.0, -ROTOR_RADIUS]),
        ROTOR_CENTER + np.array([0.0, 0.0, ROTOR_RADIUS]),
    ).tube(radius=ROTOR_LINE_RADIUS)
    rotor_hub = pv.Sphere(radius=4.0 / ROTOR_DIAMETER, center=ROTOR_CENTER)
    return rotor_line_xz, rotor_hub

BOUNDS_ARGS_XZ = {
    'xtitle': '',
    'ytitle': '',
    'ztitle': '',
    'fmt': '%.1fD',
    'font_size': 10,
    'font_family': 'times',
    'location': 'outer',
    'grid': None,
    'bounds': (-5, 15, 0, 0, 0, Z_MAX),
    'n_xlabels': 5,
    'n_zlabels': 3,
}


def add_xz_axis_titles(plotter):
    plotter.add_text('x/D', position=(500, 275), font_size=11, font='times', color='black')
    plotter.add_text('z/D', position=(75, 365), font_size=11, font='times', color='black', orientation=90)


def add_velocity_contours(plotter, mesh, contour_levels):
    contours = mesh.contour(isosurfaces=contour_levels, scalars='U_mag')
    plotter.add_mesh(contours, color='white', line_width=0.5, render_lines_as_tubes=False)


def crop_white_margins(path, margin=20):
    image = Image.open(path).convert('RGB')
    pixels = np.asarray(image)

    non_white_rows = np.where(np.any(pixels < 250, axis=(1, 2)))[0]
    non_white_cols = np.where(np.any(pixels < 250, axis=(0, 2)))[0]

    if non_white_rows.size == 0 or non_white_cols.size == 0:
        return

    top = max(int(non_white_rows[0]) - margin, 0)
    bottom = min(int(non_white_rows[-1]) + margin + 1, image.height)
    left = max(int(non_white_cols[0]) - margin, 0)
    right = min(int(non_white_cols[-1]) + margin + 1, image.width)

    image.crop((left, top, right, bottom)).save(path)


def add_scalar_bar_math_title(path, title):
    image = Image.open(path).convert('RGB')
    pixels = np.asarray(image)
    width, height = image.size
    dpi = 100

    y0 = int(0.72 * height)
    panel = pixels[y0:]
    color_mask = (
        (panel.max(axis=2) - panel.min(axis=2) > 40)
        & (panel.max(axis=2) < 245)
        & (panel.min(axis=2) < 230)
    )
    ys, xs = np.where(color_mask)
    if xs.size == 0:
        x_pos, y_pos = 0.5, 0.31
    else:
        left = int(xs.min())
        right = int(xs.max())
        top = y0 + int(ys.min())
        x_pos = ((left + right) / 2) / width
        y_pos = 1 - (top - 50) / height

    with plt.rc_context({'text.usetex': False, 'font.family': 'serif', 'font.serif': ['Times New Roman', 'Nimbus Roman No9 L', 'DejaVu Serif'], 'mathtext.fontset': 'stix'}):
        fig = plt.figure(figsize=(width / dpi, height / dpi), dpi=dpi)
        ax = fig.add_axes((0, 0, 1, 1))
        ax.imshow(image)
        ax.axis('off')
        ax.text(
            x_pos,
            y_pos,
            title,
            transform=ax.transAxes,
            ha='center',
            va='center',
            fontsize=16,
            color='black',
        )
        fig.savefig(path, dpi=dpi, pad_inches=0)
        plt.close(fig)



def add_panel(plotter, mesh, field, scalar_bar_title):
    rotor_line, rotor_hub = make_rotor_geometry()
    scalar_bar_args = {
        'title': ' ',
        'title_font_size': 13,
        'label_font_size': 16,
        'font_family': 'times',
        'position_x': 0.23,
        'position_y': 0.21,
        'width': 0.54,
        'height': 0.08,
        'fmt': '%.0f',
        'vertical': False,
    }
    clim = (0.0, float(np.nanmax(mesh[field])))

    plotter.add_mesh(
        mesh,
        scalars=field,
        cmap='turbo',
        clim=clim,
        show_scalar_bar=True,
        scalar_bar_args=scalar_bar_args,
    )
    add_velocity_contours(plotter, mesh, CONTOUR_LEVELS)
    plotter.add_mesh(rotor_line, color='black')
    plotter.add_mesh(rotor_hub, color='black')
    plotter.show_bounds(**BOUNDS_ARGS_XZ)
    add_xz_axis_titles(plotter)
    plotter.view_xz()
    plotter.enable_parallel_projection()
    plotter.camera.parallel_scale *= 1.02


rans_original_xz = crop_to_low_z(extract_xz(read_mesh(PATH_RANS_ORIGINAL_XZ)))
les_and_modified_xz = crop_to_low_z(extract_xz(read_mesh(PATH_LES_AND_MODIFIED)))

panels = [
    {
        'title': 'RANS nut',
        'field': 'nut',
        'scalar_bar_title': r'$\nu_t$',
        'xz': rans_original_xz,
        'output': OUTPUT_RANS_NUT,
    },
    {
        'title': 'LES nutEq',
        'field': 'nutEq',
        'scalar_bar_title': r'$\nu_{t,eq}$',
        'xz': les_and_modified_xz,
        'output': OUTPUT_LES_NUTEQ,
    },
    {
        'title': 'Modified RANS nut',
        'field': 'nut',
        'scalar_bar_title': r'$\nu_{t,mod}$',
        'xz': les_and_modified_xz,
        'output': OUTPUT_MODIFIED_NUT,
    },
]

velocity_values = np.concatenate(
    [panel['xz']['U_mag'] for panel in panels]
)
CONTOUR_LEVELS = np.linspace(
    np.nanpercentile(velocity_values, 15),
    np.nanpercentile(velocity_values, 95),
    7,
)

for panel in panels:
    plotter = pv.Plotter(off_screen=True)
    add_panel(plotter, panel['xz'], panel['field'], scalar_bar_title=panel['scalar_bar_title'])
    plotter.screenshot(panel['output'])
    plotter.close()
    add_scalar_bar_math_title(panel['output'], panel['scalar_bar_title'])
    crop_white_margins(panel['output'])
