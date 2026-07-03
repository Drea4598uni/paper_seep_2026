import sys
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path
from PIL import Image
import scienceplots
sys.path.insert(0, str(Path(__file__).resolve().parent))
import case_config as cc
plt.style.use(['science', 'ieee'])
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

### elbow plot
elbow_df = pd.read_csv(cc.CLUSTER_ELBOW)
NC = elbow_df['NC']
inertia = elbow_df['Inertia']

plt.figure()
plt.plot(NC, inertia, marker='o', linestyle='--')
plt.scatter([7], inertia[NC == 7], marker='x', color='red', label='Selected NC', zorder=5, s=75)
plt.xlabel('NC')
plt.ylabel('Inertia')
plt.legend()
plt.grid(axis='x')
plt.savefig(Path('results') / 'img' / 'elbow_plot.png', bbox_inches='tight')
plt.close()

### PCA plot
pca_df = pd.read_csv(cc.CLUSTER_PCA_VARIANCE)
PCs = pca_df.iloc[:, 0]
explained_variance_ratio = pca_df['Explained Variance Ratio']
x_pcs = range(1, len(PCs) + 1)
cumulative_explained_variance_ratio = []
for i in range(len(PCs)):
    cumulative_explained_variance_ratio.append(explained_variance_ratio[:i+1].sum())
    
plt.figure()
plt.plot(x_pcs, cumulative_explained_variance_ratio, marker='o', label='Cumulative Explained Variance Ratio')
plt.xlabel('PCs')
plt.ylabel('Cumulative explained variance ratio')
plt.xticks(ticks=x_pcs)
plt.grid(axis='y')
plt.savefig(Path('results') / 'img' / 'pca_explained_variance_ratio.png', bbox_inches='tight')
plt.close() 

### plot features weights on first 6 PCs
dict = {
    'Q': r'$Q$',
    'Rrr': r'$R_{rr}$',
    'Rrt': r'$R_{rt}$',
    'Rtt': r'$R_{tt}$',
    'Rxr': r'$R_{xr}$',
    'Rxt': r'$R_{xt}$',
    'Rxx': r'$R_{xx}$',
    'Ur': r'$U_\rho$',
    'Ut': r'$U_\theta$',
    'Ux': r'$U_x$',
    'k': r'$k$',
    'nut': r'$\nu_t$',
    'p': r'$p$',
    'vort_r': r'$\omega_r$',
    'vort_t': r'$\omega_t$',
    'vort_ax': r'$\omega_{ax}$',
    'ax': r'$ax$',
    'rho': r'$\rho$',
    'theta': r'$\theta$'
}

features_weights_df = pd.read_csv(cc.CLUSTER_PCA_IMPORTANCE)
features = [features_weights_df.columns[i] for i in range(0, len(features_weights_df.columns))]
weights = features_weights_df[features].values
plt.figure()
for i in range(len(weights)):
    plt.bar(features, weights[i], color=plt.cm.tab10(i), alpha=0.5)
plt.ylabel('Weights')
plt.xticks(ticks=range(len(features)), labels=[dict[feat] for feat in features], rotation=45, ha='right')
plt.tight_layout()
plt.savefig(Path('results') / 'img' / 'pca_features_weights.png', bbox_inches='tight')
plt.close()

### plot clustering results
import pyvista as pv

path = cc.CLUSTER_MESH
mesh = pv.read(path)
rotor_diameter = 126.0
mesh.points = mesh.points / rotor_diameter
colors = ['#1f77b4', '#ff7f0e', "#bc1f1f", "#49ff01", "#8c704b", "#0be4d2", '#bcbd22']
rotor_center = np.array([0.0, 0.0, 90.0]) / rotor_diameter
rotor_radius = 63.0 / rotor_diameter
rotor_line_radius = 2.5 / rotor_diameter
rotor_line_xz = pv.Line(
    rotor_center + np.array([0.0, 0.0, -rotor_radius]),
    rotor_center + np.array([0.0, 0.0, rotor_radius]),
).tube(radius=rotor_line_radius)
rotor_line_xy = pv.Line(
    rotor_center + np.array([0.0, -rotor_radius, 0.0]),
    rotor_center + np.array([0.0, rotor_radius, 0.0]),
).tube(radius=rotor_line_radius)
rotor_hub = pv.Sphere(radius=4.0 / rotor_diameter, center=rotor_center)

bounds_args_xz = {
    'xtitle': '',
    'ytitle': '',
    'ztitle': '',
    'fmt': '%.0fD',
    'font_size': 12,
    'font_family': 'times',
    'location': 'outer',
    'grid': None,
}

bounds_args_xy = {
    'xtitle': 'x/D',
    'ytitle': 'y/D',
    'ztitle': '',
    'fmt': '%.0fD',
    'font_size': 12,
    'font_family': 'times',
    'location': 'outer',
    'grid': None,
    'show_zaxis': False,
    'show_zlabels': False,
    'use_2d': True,
    'use_3d_text': False,
}

scalar_bar_args = {
    'title': 'Cluster ID',
    'title_font_size': 22,
    'label_font_size': 18,
    'font_family': 'times',
    'position_x': 0.2,
    'position_y': 0.10,
    'fmt': '%.0f',
}
scalar_bar_args_xy = scalar_bar_args.copy()
scalar_bar_args_xy['position_y'] = 0.15

def add_xz_axis_titles(plotter, x_position=(500, 180), z_position=(75, 365)):
    plotter.add_text('x/D', position=x_position, font_size=11, font='times', color='black')
    plotter.add_text('z/D', position=z_position, font_size=11, font='times', color='black', orientation=90)

plotter = pv.Plotter(off_screen=True)
plotter.add_mesh(mesh, scalars='ID', cmap=colors, show_scalar_bar=False, 
          scalar_bar_args=scalar_bar_args)
plotter.add_mesh(rotor_line_xz, color='black')
plotter.add_mesh(rotor_hub, color='black')
plotter.show_bounds(**bounds_args_xz)
add_xz_axis_titles(plotter)
plotter.view_xz()
plotter.enable_parallel_projection()
plotter.screenshot(Path('results') / 'img' / 'clustering_result_xz.png')
plotter.close()

plotter_2 = pv.Plotter(off_screen=True)
plotter_2.add_mesh(mesh, scalars='ID', cmap=colors, show_scalar_bar=False, 
          scalar_bar_args=scalar_bar_args_xy)
plotter_2.add_mesh(rotor_line_xy, color='black')
plotter_2.add_mesh(rotor_hub, color='black')
plotter_2.show_bounds(**bounds_args_xy)
plotter_2.view_xy()
plotter_2.enable_parallel_projection()
plotter_2.screenshot(Path('results') / 'img' / 'clustering_result_xy.png')
plotter_2.close()

### plot a figure with only the scalar bar and no mesh, to be used as legend in the paper
plotter_3 = pv.Plotter(off_screen=True)
plotter_3.add_mesh(mesh, scalars='ID', cmap=colors, show_scalar_bar=True, 
          scalar_bar_args=scalar_bar_args)
plotter_3.show_bounds(**bounds_args_xz)
add_xz_axis_titles(plotter_3)
plotter_3.view_xz()
plotter_3.enable_parallel_projection()
plotter_3.screenshot(Path('results') / 'img' / 'clustering_result_legend.png')
plotter_3.close()

### plot nut fields with the same visual style
prediction_path = cc.PRED_CLU
rans_path = cc.CLUSTER_RANS_MESH

prediction_mesh = pv.read(prediction_path)
rans_mesh = pv.read(rans_path)
prediction_mesh.points = prediction_mesh.points / rotor_diameter
rans_mesh.points = rans_mesh.points / rotor_diameter

def crop_to_low_z(mesh, z_max=2.5):
    return mesh.clip(normal='z', origin=(0.0, 0.0, z_max), invert=True)

prediction_mesh_low_z = crop_to_low_z(prediction_mesh)
rans_mesh_low_z = crop_to_low_z(rans_mesh)

nut_fields = [
    {
        'mesh': prediction_mesh_low_z,
        'scalars': 'nutEq',
        'title': r'$\nu_{t,Eq}$',
        'output': Path('results') / 'img' / 'nutEq_field_xz.png',
    },
    {
        'mesh': prediction_mesh_low_z,
        'scalars': 'nut_pred',
        'title': r'$\nu_{t,ML}$',
        'output': Path('results') / 'img' / 'nut_pred_field_xz.png',
    },
    {
        'mesh': rans_mesh_low_z,
        'scalars': 'nut',
        'title': r'$\nu_{t,RANS}$',
        'output': Path('results') / 'img' / 'nut_rans_field_xz.png',
    },
]

nut_scalar_bar_args = {
    'title_font_size': 22,
    'label_font_size': 18,
    'font_family': 'times',
    'position_x': 0.2,
    'position_y': 0.17,
    'fmt': '%.2f',
}

nut_bounds_args_xz = bounds_args_xz.copy()
nut_bounds_args_xz['bounds'] = (-5, 15, 0, 0, 0, 2.5)
nut_bounds_args_xz['fmt'] = '%.1fD'
nut_bounds_args_xz['n_zlabels'] = 3
nut_bounds_args_xz['n_xlabels'] = 5

def add_nut_field(plotter, field, show_scalar_bar=True):
    scalar_args = nut_scalar_bar_args.copy()
    scalar_args['title'] = ' '
    plotter.add_mesh(
        field['mesh'],
        scalars=field['scalars'],
        cmap='viridis',
        show_scalar_bar=show_scalar_bar,
        scalar_bar_args=scalar_args,
    )
    plotter.add_mesh(rotor_line_xz, color='black')
    plotter.add_mesh(rotor_hub, color='black')
    plotter.show_bounds(**nut_bounds_args_xz)
    add_xz_axis_titles(plotter, x_position=(500, 270))
    plotter.view_xz()
    plotter.enable_parallel_projection()

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

for field in nut_fields:
    plotter = pv.Plotter(off_screen=True)
    add_nut_field(plotter, field, show_scalar_bar=True)
    plotter.screenshot(field['output'])
    plotter.close()
    add_scalar_bar_math_title(field['output'], field['title'])
