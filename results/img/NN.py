import pyvista as pv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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

path = 'dataset\\risultati_rete\\output_seep_con_clustering_11ms\\results\\rans_with_predictions.vtu'
mesh = pv.read(path)
rotor_diameter = 126.0
mesh.points = mesh.points / rotor_diameter

rans_reference_path = 'dataset\\ref_rans\\yNormal_11ms.vtp'
rans_reference_mesh = pv.read(rans_reference_path)
rans_reference_mesh.points = rans_reference_mesh.points / rotor_diameter

def crop_to_low_z(mesh, z_max=2.5):
    return mesh.clip(normal='z', origin=(0.0, 0.0, z_max), invert=True)

mesh_low_z = crop_to_low_z(mesh)
rans_reference_mesh_low_z = crop_to_low_z(rans_reference_mesh)

colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
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
    'fmt': '%.1fD',
    'font_size': 12,
    'font_family': 'times',
    'location': 'outer',
    'grid': None,
    'bounds': (-5, 15, 0, 0, 0, 2.5),
    'n_xlabels': 5,
    'n_zlabels': 3,
}

scalar_bar_args = {
    'title_font_size': 22,
    'label_font_size': 18,
    'font_family': 'times',
    'position_x': 0.2,
    'position_y': 0.205,
    'fmt': '%.0f',
}

def add_xz_axis_titles(plotter):
    plotter.add_text('x/D', position=(500, 270), font_size=11, font='times', color='black')
    plotter.add_text('z/D', position=(75, 365), font_size=11, font='times', color='black', orientation=90)

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
        x_pos, y_pos = 0.75, 0.31
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

fields = [
    (mesh_low_z, 'nut_pred', r'$\nu_{t,ML}$', 'results\\img\\nut_pred_field_xz.png'),
    (mesh_low_z, 'nutEq', r'$\nu_{t,Eq}$', 'results\\img\\nutEq_field_xz.png'),
    (rans_reference_mesh_low_z, 'nut', r'$\nu_t$', 'results\\img\\nut_rans_field_xz.png'),
]

for field_mesh, scalars, title, output_path in fields:
    field_scalar_bar_args = scalar_bar_args.copy()
    field_scalar_bar_args['title'] = ' '
    clim = (0.0, float(np.nanmax(field_mesh[scalars])))

    plotter = pv.Plotter(off_screen=True)
    plotter.add_mesh(
        field_mesh,
        scalars=scalars,
        cmap='turbo',
        clim=clim,
        show_scalar_bar=True,
        scalar_bar_args=field_scalar_bar_args,
    )
    plotter.add_mesh(rotor_line_xz, color='black')
    plotter.add_mesh(rotor_hub, color='black')
    plotter.show_bounds(**bounds_args_xz)
    add_xz_axis_titles(plotter)
    plotter.view_xz()
    plotter.enable_parallel_projection()
    plotter.screenshot(output_path)
    plotter.close()
    add_scalar_bar_math_title(output_path, title)


# Load the dataset
dataset = "dataset\\risultati_rete\\output_seep_con_clustering_11ms\\results\\rans_with_predictions.vtu"
data = pv.read(dataset)

# Fields saved by the training script:
# - nut: reference viscosity used as the baseline in the reconstruction
# - nutEq: LES-equivalent viscosity
# - delta_pred: NN correction already inverse-transformed by y_scaler_nut.pkl
nut_base = data["nut"]
nut_eq = data["nutEq"]
delta_nut_pred = data["delta_pred"]
delta_nut_true = nut_eq - nut_base
nut_pred = data["nut_pred"]

# Reconstruct the prediction from the saved delta, as done during training.
nut_pred_from_delta = nut_base + delta_nut_pred

# Create a scatter plot of the true vs predicted values of nutEq
plt.figure(figsize=(6, 4))
plt.scatter(nut_eq, nut_pred, alpha=0.5, label="Predicted vs True", s=1)
lims = [min(nut_eq.min(), nut_pred.min()), max(nut_eq.max(), nut_pred.max())]
plt.plot(lims, lims, 'r--', label="Ideal Fit")
plt.xlabel(r"True $\nu_{t,eq}$")
plt.ylabel(r"Predicted $\nu_{t,ML}$")
rect = mpatches.Rectangle((-1, -1), 42, 5, facecolor='none', edgecolor='blue', linestyle='--', label="Bias Region")
plt.gca().add_patch(rect)
plt.legend()
plt.savefig("results/img/NN_scatter_plot.png", bbox_inches='tight')
plt.close()

# Create a scatter plot of the true vs predicted delta
plt.figure(figsize=(6, 4))
plt.scatter(delta_nut_true, delta_nut_pred, alpha=0.5, label="Predicted vs True", s=1)
lims = [
    min(delta_nut_true.min(), delta_nut_pred.min()),
    max(delta_nut_true.max(), delta_nut_pred.max()),
]
plt.plot(lims, lims, 'r--', label="Ideal Fit")
plt.xlabel(r"True $\Delta \nu_{t}$")
plt.ylabel(r"Predicted $\Delta \nu_{t,ML}$")
rect = mpatches.Rectangle((-35, -35), 43, 6, facecolor='none', edgecolor='blue', linestyle='--', label="Bias Region")
plt.gca().add_patch(rect)
plt.legend()
plt.savefig("results/img/NN_delta_scatter_plot.png", bbox_inches='tight')
plt.close()

# plot train val loss curves
path = "dataset\\risultati_rete\\output_seep_con_clustering_11ms\\results\\training_history_nut.csv"
datas = pd.read_csv(path)
datas.plot(y=["loss", "val_loss"], logy=True, use_index=True)
plt.xlabel("Epoch")
plt.ylabel("Loss")
# plt.title("Training and Validation Loss Curves")
plt.legend(["Training Loss", "Validation Loss"])
plt.savefig("results/img/NN_loss_curves.png", bbox_inches='tight')
plt.close()

datas.plot(y=["mae", "val_mae"], logy=True, use_index=True)
plt.xlabel("Epoch")
plt.ylabel("MAE")
# plt.title("Training and Validation MAE Curves")
plt.legend(["Training MAE", "Validation MAE"])
plt.savefig("results/img/NN_MAE_curves.png", bbox_inches='tight')
plt.close()

datas.plot(y=["rmse", "val_rmse"], logy=True, use_index=True)
plt.xlabel("Epoch")
plt.ylabel("RMSE")
# plt.title("Training and Validation RMSE Curves")
plt.legend(["Training RMSE", "Validation RMSE"])
plt.savefig("results/img/NN_RMSE_curves.png", bbox_inches='tight')
plt.close()
