import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyvista as pv
import scienceplots

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


# Datasets processed: (predictions file, output-name suffix). The no-clustering
# case reuses the same metric and produces the *_no_clustering.png figures used
# in the manuscript.
DATASETS = [
    (r"dataset\risultati_rete\output_seep_con_clustering_11ms\results\rans_with_predictions.vtu", ""),
    (r"dataset\risultati_rete_noclustering\output_seep_\results\rans_with_predictions.vtu", "_no_clustering"),
]
OUTPUT_DIR = r"results\img\ml_results\bias_points"

ROTOR_DIAMETER = 126.0

# --- Standard bias metric -------------------------------------------------
# A point belongs to the bias region when the reconstructed eddy viscosity is
# UNDERESTIMATED by more than BIAS_REL_THRESHOLD relative to the true value, i.e.
#       nut_pred < nut_eq   and   |nut_pred - nut_eq| / |nut_eq| > BIAS_REL_THRESHOLD .
# Because nut_pred = nut + delta_pred and nut_eq = nut + delta_true, the absolute
# reconstruction error of nut and of delta_nut is identical; the SAME mask is
# therefore used for both the nut and the delta-nut scatter plots, so the two
# selected populations coincide exactly. Near-zero true values are excluded
# (BIAS_MIN_TRUE) because the relative error is not meaningful there.
BIAS_REL_THRESHOLD = 0.9      # 90 % relative underestimation
BIAS_MIN_TRUE = 1.0           # ignore |nut_eq| below this value [m^2/s]

FIELD_TO_PLOT = "nutEq"
FIELD_LABEL = r"$\nu_{t,eq}$"
DELTA_SCATTER_X_LABEL = r"True $\Delta \nu_t$"
DELTA_SCATTER_Y_LABEL = r"Predicted $\Delta \nu_{t,ML}$"
NUT_SCATTER_X_LABEL = r"True $\nu_{t,eq}$"
NUT_SCATTER_Y_LABEL = r"Predicted $\nu_{t,ML}$"

# Slice used for the field plot.
SLICE_AXIS = "y"
SLICE_VALUE = 0.0
SLICE_TOLERANCE = 1e-9


def axis_index(axis_name):
    return {"x": 0, "y": 1, "z": 2}[axis_name.lower()]


def bias_mask_from_error(nut_eq, nut_pred):
    """Single, metric-based selection of the bias (underestimation) region."""
    abs_error = nut_pred - nut_eq
    with np.errstate(divide="ignore", invalid="ignore"):
        rel_error = np.abs(abs_error) / np.abs(nut_eq)
    return (abs_error < 0) & (rel_error > BIAS_REL_THRESHOLD) & (np.abs(nut_eq) > BIAS_MIN_TRUE)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for dataset, suffix in DATASETS:
        process_dataset(dataset, suffix)


def process_dataset(dataset, suffix):
    mesh = pv.read(dataset)

    nut_base = np.asarray(mesh["nut"])
    nut_eq = np.asarray(mesh["nutEq"])
    nut_pred = np.asarray(mesh["nut_pred"])
    delta_true = nut_eq - nut_base
    delta_pred = np.asarray(mesh["delta_pred"])

    with np.errstate(divide="ignore", invalid="ignore"):
        relative_error = (delta_pred - delta_true) / delta_true

    # one mask, shared by the nut and the delta-nut views
    bias_mask = bias_mask_from_error(nut_eq, nut_pred)
    bias_idx = np.where(bias_mask)[0]

    table = build_points_table(
        mesh, bias_mask, bias_idx, nut_base, nut_eq, nut_pred,
        delta_true, delta_pred, relative_error,
    )
    delta_csv_path = os.path.join(OUTPUT_DIR, f"delta_bias_points_coordinates{suffix}.csv")
    nut_csv_path = os.path.join(OUTPUT_DIR, f"nut_bias_points_coordinates{suffix}.csv")
    table.to_csv(delta_csv_path, index=False)
    table.to_csv(nut_csv_path, index=False)

    scatter_path = os.path.join(OUTPUT_DIR, f"delta_scatter_bias_points_highlighted{suffix}.png")
    plot_scatter(
        delta_true, delta_pred, bias_mask,
        DELTA_SCATTER_X_LABEL, DELTA_SCATTER_Y_LABEL,
        r"Selected $\Delta \nu_t$ points", scatter_path,
    )

    nut_scatter_path = os.path.join(OUTPUT_DIR, f"nut_scatter_bias_points_highlighted{suffix}.png")
    plot_scatter(
        nut_eq, nut_pred, bias_mask,
        NUT_SCATTER_X_LABEL, NUT_SCATTER_Y_LABEL,
        r"Selected $\nu_t$ points", nut_scatter_path,
    )

    slice_path = os.path.join(OUTPUT_DIR, f"delta_bias_points_on_{SLICE_AXIS}{SLICE_VALUE:g}_slice{suffix}.png")
    plot_slice(mesh, bias_mask, slice_path)

    nut_slice_path = os.path.join(OUTPUT_DIR, f"nut_bias_points_on_{SLICE_AXIS}{SLICE_VALUE:g}_slice{suffix}.png")
    plot_slice(mesh, bias_mask, nut_slice_path)

    print(f"[{dataset}] selected bias points: {len(bias_idx)} (of {mesh.n_points})")


def build_points_table(
    mesh,
    point_mask,
    point_idx,
    nut_base,
    nut_eq,
    nut_pred,
    delta_true,
    delta_pred,
    relative_error,
):
    points = mesh.points
    table = pd.DataFrame(
        {
            "point_index": point_idx,
            "x": points[point_mask, 0],
            "y": points[point_mask, 1],
            "z": points[point_mask, 2],
            "x_D": points[point_mask, 0] / ROTOR_DIAMETER,
            "y_D": points[point_mask, 1] / ROTOR_DIAMETER,
            "z_D": points[point_mask, 2] / ROTOR_DIAMETER,
            "nut": nut_base[point_mask],
            "nutEq_true": nut_eq[point_mask],
            "nut_pred": nut_pred[point_mask],
            "delta_nut_true": delta_true[point_mask],
            "delta_nut_pred": delta_pred[point_mask],
            "delta_error": delta_pred[point_mask] - delta_true[point_mask],
            "relative_error": relative_error[point_mask],
        }
    )

    for optional_field in ["ID", "ax", "theta", "z_original", "ax_d", "z_d"]:
        if optional_field in mesh.point_data:
            values = np.asarray(mesh[optional_field])
            if values.ndim == 1:
                table[optional_field] = values[point_mask]

    return table


def plot_scatter(x_values, y_values, bias_mask, xlabel, ylabel, selected_label, output_path):
    plt.figure(figsize=(6, 4), dpi=300)
    plt.scatter(x_values, y_values, alpha=0.5, c="black", label="Predicted vs True", s=1)
    plt.scatter(
        x_values[bias_mask],
        y_values[bias_mask],
        s=3,
        c="tab:red",
        linewidths=0.8,
        label=selected_label,
    )

    lims = [min(x_values.min(), y_values.min()), max(x_values.max(), y_values.max())]
    plt.plot(lims, lims, "r--", label="Ideal Fit")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()


def plot_slice(mesh, bias_mask, output_path):
    points = mesh.points
    values = np.asarray(mesh[FIELD_TO_PLOT])

    slice_dim = axis_index(SLICE_AXIS)
    slice_mask = np.abs(points[:, slice_dim] - SLICE_VALUE) <= SLICE_TOLERANCE
    marker_mask = slice_mask & bias_mask

    if SLICE_AXIS.lower() == "x":
        horizontal_dim, vertical_dim = 1, 2
        xlabel, ylabel = "y/D", "z/D"
    elif SLICE_AXIS.lower() == "y":
        horizontal_dim, vertical_dim = 0, 2
        xlabel, ylabel = "x/D", "z/D"
    else:
        horizontal_dim, vertical_dim = 0, 1
        xlabel, ylabel = "x/D", "y/D"

    plt.figure(figsize=(7, 4), dpi=300)
    sc = plt.scatter(
        points[slice_mask, horizontal_dim] / ROTOR_DIAMETER,
        points[slice_mask, vertical_dim] / ROTOR_DIAMETER,
        c=values[slice_mask],
        s=1,
        cmap="viridis",
        alpha=0.85,
        linewidths=0,
    )
    plt.colorbar(sc, label=FIELD_LABEL)

    plt.scatter(
        points[marker_mask, horizontal_dim] / ROTOR_DIAMETER,
        points[marker_mask, vertical_dim] / ROTOR_DIAMETER,
        s=3,
        marker="o",
        c="red",
        linewidths=1.0,
        label="Selected points",
    )

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.axis("equal")
    plt.legend(frameon=False, loc="best")
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()

    print(
        f"Slice points: {np.count_nonzero(slice_mask)}; "
        f"selected points on slice: {np.count_nonzero(marker_mask)}"
    )


if __name__ == "__main__":
    main()
