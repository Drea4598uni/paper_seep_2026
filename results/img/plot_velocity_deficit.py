import glob
import re
import sys

import matplotlib.pyplot as plt
import numpy as np
import pyvista as pv
import scienceplots
from pathlib import Path
from PIL import Image
from matplotlib.gridspec import GridSpec

sys.path.insert(0, str(Path(__file__).resolve().parent))
import case_config as cc

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

OUTPUT_ROOT = Path("results/img/ml_results")

rotor_diameter = cc.ROTOR_DIAMETER
rotor_radius = cc.ROTOR_RADIUS

ML_COLORS = {
    "RANS-ML 15M": "red",
    "RANS-ML 10M": "green",
    "RANS-ML 5M": "blue",
    "RANS-ML no clustering": "magenta",
}

# sample line stations (x/D); negative ones are upstream of the rotor
x = [0.5, 1, 2, 3, 4, 5, 6, 7]
# the integral metric only makes sense in the wake (downstream of the rotor)
x_metric = [i for i in x if i > 0]

# labels (and their order) used in the integral-difference metric plot
METRIC_LABELS = ["RANS-ML 15M", "RANS-ML 10M", "RANS-ML 5M", "RANS-ML no clustering", "RANS"]

comparison_groups = [
    ("rans_ml_15m_vs_rans_les", ["RANS-ML 15M", "RANS", "LES"]),
    ("rans_ml_10m_vs_rans_les", ["RANS-ML 10M", "RANS", "LES"]),
    ("rans_ml_5m_vs_rans_les", ["RANS-ML 5M", "RANS", "LES", "RANS-ML no clustering"]),
    ("rans_ml_no_clustering_vs_rans_les", ["RANS-ML no clustering", "RANS", "LES"]),
    ("ml_models_comparison", ["RANS-ML 15M", "RANS-ML 10M", "RANS-ML 5M", "RANS-ML no clustering", "RANS", "LES"]),
]


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


def velocity_magnitude(sampled, velocity_field):
    velocity = np.asarray(sampled[velocity_field])
    if velocity.ndim == 2:
        velocity = np.linalg.norm(velocity, axis=1)
    return velocity


def velocity_deficit_profile(sampled, velocity_field, uref):
    """Interpolated (over invalid samples) velocity-deficit profile and z/D grid."""
    deficit = 1 - velocity_magnitude(sampled, velocity_field) / uref
    z_over_d = sampled.points[:, 2] / rotor_diameter
    valid = valid_sample_mask(sampled)
    deficit = interpolate_invalid_samples(deficit, z_over_d, valid)
    return deficit, z_over_d


def plot_velocity_deficit(label, sampled, velocity_field, uref):
    velocity = velocity_magnitude(sampled, velocity_field)
    velocity_deficit = 1 - velocity / uref
    z_over_d = sampled.points[:, 2] / rotor_diameter
    valid = valid_sample_mask(sampled)

    if label == "LES":
        plt.scatter(velocity_deficit[valid][::20], z_over_d[valid][::20], label=label, marker="x", color="black", s=18, linewidths=0.8)
    elif label == "RANS":
        plt.plot(velocity_deficit[valid], z_over_d[valid], label=label, color="black", linewidth=1.2, linestyle="--")
    else:
        velocity_deficit = interpolate_invalid_samples(velocity_deficit, z_over_d, valid)
        plt.plot(velocity_deficit, z_over_d, label=label, color=ML_COLORS[label], linestyle="-")


def plot_k_deficit(label, sampled):
    z_over_d = sampled.points[:, 2] / rotor_diameter
    valid = valid_sample_mask(sampled)

    if label == "LES":
        plt.scatter(sampled["k"][valid][::20], z_over_d[valid][::20], label=label, marker="x", facecolor="black", s=18, linewidths=0.8)
    elif label == "RANS":
        plt.scatter(sampled["k"][valid][::20], z_over_d[valid][::20], label=label, marker="^", facecolor="none", edgecolors="black", s=18)
    else:
        k = interpolate_invalid_samples(sampled["k"], z_over_d, valid)
        plt.plot(k, z_over_d, label=label, color=ML_COLORS[label], linestyle="-")


def build_case_simulations(case):
    """Read every mesh needed for a given inflow case and pre-interpolate cell data."""
    les_paths, les_field, les_has_k = cc.les_ref(case)
    raw = [
        ("RANS-ML 15M", cc.solver_meshes(case, "RANS-ML 15M"), "U"),
        ("RANS-ML 10M", cc.solver_meshes(case, "RANS-ML 10M"), "U"),
        ("RANS-ML 5M", cc.solver_meshes(case, "RANS-ML 5M"), "U"),
        ("RANS-ML no clustering", cc.solver_meshes(case, "RANS-ML no clustering"), "U"),
        ("RANS", cc.rans_ref_meshes(case), "U"),
        ("LES", les_paths, les_field),
    ]
    simulations = {}
    for label, paths, field in raw:
        meshes = [pv.read(p) for p in paths]
        mesh = pv.merge(meshes) if len(meshes) > 1 else meshes[0]
        simulations[label] = (interpolate_cell_fields_to_points(mesh, [field]), field)
    return simulations, les_has_k


def build_comparison_image(velocity_dir):
    """Stitch the per-station velocity-deficit PNGs into a single comparison figure."""
    def extract_x(fname):
        m = re.search(r'_x_([-+]?\d+[.,]?\d*)D', fname)
        if m:
            return float(m.group(1).replace(',', '.'))
        return float('inf')

    image_files = sorted(glob.glob(str(velocity_dir / "*D.png")), key=extract_x)
    images = [Image.open(f) for f in image_files]
    if not images:
        return

    # split the panels over two balanced rows sized to the actual station count
    n = len(images)
    top_cols = (n + 1) // 2
    bottom_cols = n - top_cols
    max_cols = max(top_cols, bottom_cols, 1)
    # aspect chosen so the (landscape) panels fill their cells with little white space
    fig = plt.figure(figsize=(15, 5), dpi=300)
    gs = GridSpec(2, max_cols, figure=fig, hspace=0.0, wspace=0.0)

    top_start = (max_cols - top_cols) // 2
    top_axes = [fig.add_subplot(gs[0, top_start + i]) for i in range(top_cols)]
    bottom_start = (max_cols - bottom_cols) // 2
    bottom_axes = [fig.add_subplot(gs[1, bottom_start + i]) for i in range(bottom_cols)]

    for ax, img in zip(top_axes, images[:top_cols]):
        ax.imshow(img)
    for ax, img in zip(bottom_axes, images[top_cols:]):
        ax.imshow(img)
    for ax in top_axes + bottom_axes:
        ax.axis('off')

    plt.subplots_adjust(hspace=0.01, left=0.02, right=0.98, top=0.98, bottom=0.02)
    plt.tight_layout()
    plt.savefig(velocity_dir / "comparison.png", bbox_inches='tight')
    plt.close()


def plot_integral_metric(case, uref, metric_x, metric_results, output_path):
    """Signed integral of (deficit_sim - deficit_LES) over z/D versus downstream distance."""
    plt.figure()
    plt.axhline(0.0, color="black", linewidth=0.8, linestyle=":")
    for label in METRIC_LABELS:
        if label == "RANS":
            plt.plot(metric_x, metric_results[label], label=label, color="black", linestyle="--", marker="^", markersize=4)
        else:
            plt.plot(metric_x, metric_results[label], label=label, color=ML_COLORS[label], linestyle="-", marker="o", markersize=3)
    plt.xlabel("x/D")
    plt.ylabel(r"$\int (\Delta U_{\mathrm{sim}} - \Delta U_{\mathrm{LES}})\, \mathrm{d}(z/D)$")
    plt.title(rf"$U_\infty = {uref:g}$ m/s")
    plt.legend()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()


for case in cc.CASES:
    uref = cc.UREF[case]
    simulations_by_label, les_has_k = build_case_simulations(case)
    case_root = OUTPUT_ROOT / case / "deficit"

    # prepare output dirs
    group_dirs = {}
    for comparison_name, _ in comparison_groups:
        velocity_dir = case_root / comparison_name / "velocity"
        k_dir = case_root / comparison_name / "k"
        velocity_dir.mkdir(parents=True, exist_ok=True)
        if les_has_k:
            k_dir.mkdir(parents=True, exist_ok=True)
        group_dirs[comparison_name] = (velocity_dir, k_dir)

    metric_results = {label: [] for label in METRIC_LABELS}
    metric_x = []

    for i in x:
        line = pv.Line((i * rotor_diameter, 0, 0), (i * rotor_diameter, 0, 5 * rotor_radius), resolution=1000)
        # sample every mesh on this line once and reuse across groups/metric
        sampled = {label: line.sample(mesh) for label, (mesh, _) in simulations_by_label.items()}

        for comparison_name, labels in comparison_groups:
            velocity_dir, k_dir = group_dirs[comparison_name]

            plt.figure()
            for label in labels:
                _, velocity_field = simulations_by_label[label]
                plot_velocity_deficit(label, sampled[label], velocity_field, uref)
            plt.xlabel(r"$\Delta U / U_\infty$")
            plt.ylabel("z/D")
            if i == x[-1]:
                plt.legend(fontsize=11, loc="upper right")
            plt.title(f"x/D={i}")
            plt.savefig(velocity_dir / f"velocity_deficit_x_{i}D.png", bbox_inches='tight')
            plt.close()

            if les_has_k:
                plt.figure()
                for label in labels:
                    plot_k_deficit(label, sampled[label])
                plt.xlabel(r"$k$")
                plt.ylabel("z/D")
                if i == 0.25:
                    plt.legend()
                plt.title(f"x/D={i}")
                plt.savefig(k_dir / f"k_deficit_x_{i}D.png", bbox_inches='tight')
                plt.close()

        # integral-difference metric (downstream stations only)
        if i in x_metric:
            les_field = simulations_by_label["LES"][1]
            les_deficit, z_over_d = velocity_deficit_profile(sampled["LES"], les_field, uref)
            metric_x.append(i)
            for label in METRIC_LABELS:
                sim_field = simulations_by_label[label][1]
                sim_deficit, _ = velocity_deficit_profile(sampled[label], sim_field, uref)
                metric_results[label].append(float(np.trapz(sim_deficit - les_deficit, z_over_d)))

    # stitch the ml_models_comparison velocity panels
    build_comparison_image(group_dirs["ml_models_comparison"][0])

    # integral-difference metric plot for this inflow case
    plot_integral_metric(case, uref, metric_x, metric_results, OUTPUT_ROOT / case / "integral_deficit_difference.png")
