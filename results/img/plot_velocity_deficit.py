import matplotlib.pyplot as plt
import numpy as np
import pyvista as pv
import scienceplots
from pathlib import Path
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
plt.rcParams['legend.fontsize'] = 13
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

OUTPUT_ROOT = Path("results/img/ml_results/deficit")
OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

ML_COLORS = {
    "RANS-ML 15M": "red",
    "RANS-ML 10M": "green",
    "RANS-ML 5M": "blue",
    "RANS-ML no clustering": "magenta",
}


def interpolate_cell_fields_to_points(mesh, fields):
    fields_to_check = set(fields) | {"k"}
    if any(field in mesh.cell_data for field in fields_to_check):
        return mesh.cell_data_to_point_data()
    return mesh


def valid_sample_mask(sampled):
    if "vtkValidPointMask" not in sampled.array_names:
        return np.ones(sampled.n_points, dtype=bool)
    return np.asarray(sampled["vtkValidPointMask"]).astype(bool)


def interpolate_invalid_samples(values, z_over_d, valid):
    values = np.asarray(values, dtype=float)
    if valid.all():
        return values
    if valid.sum() < 2:
        return values
    return np.interp(z_over_d, z_over_d[valid], values[valid])


def plot_velocity_deficit(label, sampled, velocity_field):
    velocity = sampled[velocity_field]
    if velocity.ndim == 2:
        velocity = (velocity ** 2).sum(axis=1) ** 0.5
    velocity_deficit = 1 - velocity / Uref
    z_over_d = sampled.points[:, 2] / rotor_diameter
    valid = valid_sample_mask(sampled)

    if label == "LES":
        plt.scatter(velocity_deficit[valid][::20], z_over_d[valid][::20], label=label, marker="x", color="black", s=18, linewidths=0.8)
    elif label == "RANS":
        plt.scatter(velocity_deficit[valid][::20], z_over_d[valid][::20], label=label, marker="^", facecolor="none", edgecolors="black", s=18 )
    else:
        velocity_deficit = interpolate_invalid_samples(velocity_deficit, z_over_d, valid)
        plt.plot(velocity_deficit, z_over_d, label=label, color=ML_COLORS[label], linestyle="-")


def plot_k_deficit(label, sampled):
    z_over_d = sampled.points[:, 2] / rotor_diameter
    valid = valid_sample_mask(sampled)

    if label == "LES":
        plt.scatter(sampled["k"][valid][::20], z_over_d[valid][::20], label=label, marker="x", facecolor="black", s=18, linewidths=0.8)
    elif label == "RANS":
        plt.scatter(sampled["k"][valid][::20], z_over_d[valid][::20], label=label, marker="^", facecolor="none", edgecolors="black", s=18 )
    else:
        k = interpolate_invalid_samples(sampled["k"], z_over_d, valid)
        plt.plot(k, z_over_d, label=label, color=ML_COLORS[label], linestyle="-")

### definition of the sample line for the velocity and k deficit plot
rotor_diameter = 126.0
rotor_radius = 63.0
x = [-0.25, 0.25, 0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
Uref = 8.0

simulations = [
    ("RANS-ML 15M", pv.merge([
        pv.read("dataset/risultati_solver/yNormal_15ml.vtp"),
        pv.read("dataset/risultati_solver/zNormal_15ml.vtp"),
    ]), "U"),
    ("RANS-ML 10M", pv.merge([
        pv.read("dataset/risultati_solver/yNormal_10ml.vtp"),
        pv.read("dataset/risultati_solver/zNormal_10ml.vtp"),
    ]), "U"),
    ("RANS-ML 5M", pv.merge([
        pv.read("dataset/risultati_solver/yNormal_5ml.vtp"),
        pv.read("dataset/risultati_solver/zNormal_5ml.vtp"),
    ]), "U"),
    ("RANS-ML no clustering", pv.merge([
        pv.read("dataset/risultati_solver/yNormal.vtp"),
        pv.read("dataset/risultati_solver/zNormal.vtp"),
    ]), "U"),
    ("RANS", pv.read("dataset/riferimento rans/yNormal.vtp"), "U"),
    ("LES", pv.read("dataset/les_reference/les_mesh_with_k.vtp"), "UMean"),
]

simulations_by_label = {
    label: (interpolate_cell_fields_to_points(mesh, [velocity_field]), velocity_field)
    for label, mesh, velocity_field in simulations
}

comparison_groups = [
    ("rans_ml_15m_vs_rans_les", ["RANS-ML 15M", "RANS", "LES"]),
    ("rans_ml_10m_vs_rans_les", ["RANS-ML 10M", "RANS", "LES"]),
    ("rans_ml_5m_vs_rans_les", ["RANS-ML 5M", "RANS", "LES", "RANS-ML no clustering"]),
    ("rans_ml_no_clustering_vs_rans_les", ["RANS-ML no clustering", "RANS", "LES"]),
    ("ml_models_comparison", ["RANS-ML 15M", "RANS-ML 10M", "RANS-ML 5M", "RANS-ML no clustering", "RANS", "LES"]),
]

for comparison_name, labels in comparison_groups:
    comparison_dir = OUTPUT_ROOT / comparison_name
    velocity_dir = comparison_dir / "velocity"
    k_dir = comparison_dir / "k"
    velocity_dir.mkdir(parents=True, exist_ok=True)
    k_dir.mkdir(parents=True, exist_ok=True)

    for i in x:
        line = pv.Line((i * rotor_diameter, 0, 0), (i * rotor_diameter, 0, 5 * rotor_radius), resolution=1000)

        plt.figure()
        for label in labels:
            mesh, velocity_field = simulations_by_label[label]
            sampled = line.sample(mesh)
            plot_velocity_deficit(label, sampled, velocity_field)
        plt.xlabel(r"$\Delta U / U_\infty$")
        plt.ylabel("z/D")
        if  i == 0.25:
            plt.legend()
        plt.title(f"x/D={i}")
        plt.savefig(velocity_dir / f"velocity_deficit_x_{i}D.png", bbox_inches='tight')
        plt.close()

        plt.figure()
        for label in labels:
            mesh, _ = simulations_by_label[label]
            sampled = line.sample(mesh)
            plot_k_deficit(label, sampled)
        plt.xlabel(r"$k$")
        plt.ylabel("z/D")
        if  i == 0.25:
            plt.legend()
        plt.title(f"x/D={i}")
        plt.savefig(k_dir / f"k_deficit_x_{i}D.png", bbox_inches='tight')
        plt.close()
