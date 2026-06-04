from pathlib import Path

import numpy as np
import pyvista as pv


OUTPUT_ROOT = Path("results/img/ml_results/error_fields")
OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

VARIABLES = ("U", "k")
COLOR_PERCENTILES = (5, 95)
ROTOR_DIAMETER = 126.0
ROTOR_CENTER = np.array([0.0, 0.0, 90.0]) / ROTOR_DIAMETER
ROTOR_RADIUS = 63.0 / ROTOR_DIAMETER
ROTOR_LINE_RADIUS = 2.5 / ROTOR_DIAMETER

rotor_line_xz = pv.Line(
    ROTOR_CENTER + np.array([0.0, 0.0, -ROTOR_RADIUS]),
    ROTOR_CENTER + np.array([0.0, 0.0, ROTOR_RADIUS]),
).tube(radius=ROTOR_LINE_RADIUS)
rotor_hub = pv.Sphere(radius=4.0 / ROTOR_DIAMETER, center=ROTOR_CENTER)

bounds_args_xz = {
    "xtitle": "",
    "ytitle": "",
    "ztitle": "",
    "bounds": (-5, 15, 0, 0, 0, 3),
    "fmt": "%.1fD",
    "font_size": 12,
    "font_family": "times",
    "location": "outer",
    "grid": None,
    "n_xlabels": 5,
    "n_zlabels": 4,
}

scalar_bar_args = {
    "title_font_size": 22,
    "label_font_size": 18,
    "font_family": "times",
    "position_x": 0.2,
    "position_y": 0.17,
    "fmt": "%.1f",
}


def read_case(mesh_paths, velocity_field):
    meshes = [pv.read(path) for path in mesh_paths]
    mesh = pv.merge(meshes) if len(meshes) > 1 else meshes[0]
    mesh.points = mesh.points / ROTOR_DIAMETER
    return {
        "mesh": cell_data_to_point_data(mesh),
        "velocity_field": velocity_field,
    }


def cell_data_to_point_data(mesh):
    if mesh.cell_data:
        return mesh.cell_data_to_point_data()
    return mesh


def safe_name(label):
    return label.lower().replace(" ", "_").replace("-", "_")


def field_values(mesh, velocity_field, variable):
    if variable == "U":
        velocity = np.asarray(mesh[velocity_field])
        return np.linalg.norm(velocity, axis=1)
    return np.asarray(mesh[variable])


def sampled_reference_values(target_mesh, reference_case, variable):
    sampled = target_mesh.sample(reference_case["mesh"])
    valid_mask = np.asarray(sampled["vtkValidPointMask"], dtype=bool)
    values = field_values(sampled, reference_case["velocity_field"], variable)
    values = values.astype(float)
    values[~valid_mask] = np.nan
    return values


def add_error_field(target_case, reference_case, variable):
    mesh = target_case["mesh"].copy()
    target_values = field_values(mesh, target_case["velocity_field"], variable).astype(float)
    reference_values = sampled_reference_values(mesh, reference_case, variable)
    error_name = f"error_{variable}_percent"
    denominator = np.abs(reference_values)
    error = np.full_like(target_values, np.nan, dtype=float)
    valid = denominator > np.finfo(float).eps
    error[valid] = 100.0 * np.abs(target_values[valid] - reference_values[valid]) / denominator[valid]
    mesh[error_name] = error
    return mesh, error_name


def crop_to_low_z(mesh, z_max=3.0):
    return mesh.clip(normal="z", origin=(0.0, 0.0, z_max), invert=True)


def percentile_color_limits(mesh, scalars, percentiles=COLOR_PERCENTILES):
    values = np.asarray(mesh[scalars])
    values = values[np.isfinite(values)]
    if values.size == 0:
        return None

    lower, upper = np.percentile(values, percentiles)
    if np.isclose(lower, upper):
        return None
    return float(lower), float(upper)


def add_xz_axis_titles(plotter):
    plotter.add_text("x/D", position=(900, 425), font_size=11, font="times", color="black")
    plotter.add_text("z/D", position=(250, 585), font_size=11, font="times", color="black", orientation=90)


def plot_error_mesh(mesh, error_name, output_path, title):
    cropped_mesh = crop_to_low_z(mesh)
    clim = percentile_color_limits(cropped_mesh, error_name)
    plotter = pv.Plotter(off_screen=True, window_size=(1800, 1200))
    scalar_args = scalar_bar_args.copy()
    scalar_args["title"] = "Error [%]"
    plotter.add_mesh(
        cropped_mesh,
        scalars=error_name,
        clim=[0,30],
        cmap="viridis",
        nan_color="lightgray",
        show_scalar_bar=True,
        scalar_bar_args=scalar_args,
    )
    plotter.add_mesh(rotor_line_xz, color="black")
    plotter.add_mesh(rotor_hub, color="black")
    plotter.show_bounds(**bounds_args_xz)
    add_xz_axis_titles(plotter)
    plotter.add_text(title, position="upper_left", font_size=12, font="times", color="black")
    plotter.view_xz()
    plotter.enable_parallel_projection()
    plotter.screenshot(str(output_path))
    plotter.close()


cases = {
    "RANS-ML 15M": read_case(
        [
            "dataset/risultati_solver/yNormal_15ml.vtp",
            "dataset/risultati_solver/zNormal_15ml.vtp",
        ],
        "U",
    ),
    "RANS-ML 10M": read_case(
        [
            "dataset/risultati_solver/yNormal_10ml.vtp",
            "dataset/risultati_solver/zNormal_10ml.vtp",
        ],
        "U",
    ),
    "RANS-ML 5M": read_case(
        [
            "dataset/risultati_solver/yNormal_5ml.vtp",
            "dataset/risultati_solver/zNormal_5ml.vtp",
        ],
        "U",
    ),
    "RANS": read_case(["dataset/riferimento rans/yNormal.vtp"], "U"),
    "LES": read_case(["dataset/les_reference/les_mesh_with_k.vtp"], "UMean"),
}

comparisons = [
    ("RANS-ML 15M", "LES"),
    ("RANS-ML 10M", "LES"),
    ("RANS-ML 5M", "LES"),
    ("RANS", "LES"),
    ("RANS", "RANS-ML 15M"),
    ("RANS", "RANS-ML 10M"),
    ("RANS", "RANS-ML 5M"),
]


for target_label, reference_label in comparisons:
    target_case = cases[target_label]
    reference_case = cases[reference_label]
    comparison_dir = OUTPUT_ROOT / f"{safe_name(target_label)}_vs_{safe_name(reference_label)}"
    comparison_dir.mkdir(parents=True, exist_ok=True)

    for variable in VARIABLES:
        mesh, error_name = add_error_field(target_case, reference_case, variable)
        output_path = comparison_dir / f"error_{variable}.png"
        title = f"{target_label} vs {reference_label} - {variable} error [%]"
        plot_error_mesh(mesh, error_name, output_path, title)
