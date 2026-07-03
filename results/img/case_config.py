"""Shared per-inflow-case configuration for the results figures.

All result scripts are launched from the repository root, so the paths here are
relative to it. The dataset was reorganised into three inflow-velocity cases
(8/11/15 m/s); this module centralises the (slightly inhomogeneous) file layout
so the individual plotting scripts stay clean.

Layout reminder
---------------
- solver (RANS-ML) results : dataset/risultati_solver/<case>/{y,z}Normal_<suffix>.vtp
      suffix in {15ml, 10ml, 5ml|5, noClustering}; note the 5M mesh at 11 m/s is
      named "_5" (without "ml").
- RANS reference           : dataset/ref_rans/{y,z}Normal_<case>.vtp
- LES reference            : 11ms -> dataset/ref_les/les_mesh_with_k.vtp (has k)
                             8ms  -> dataset/ref_les/8ms/yNormal.vtp     (has k)
                             15ms -> dataset/ref_les/15ms/yNormal.vtp    (NO k)
- NN predictions (11 m/s)  : dataset/risultati_rete/output_seep_con_clustering_11ms/...
- NN predictions no clust. : dataset/risultati_rete_noclustering/output_seep_/...
- clustering mesh          : dataset/clustering _simpleFoam_corretto/0-NC_7final.vtu
"""

from pathlib import Path

# --- geometry -------------------------------------------------------------
ROTOR_DIAMETER = 126.0
ROTOR_RADIUS = 63.0

# --- inflow cases ---------------------------------------------------------
CASES = ["8ms", "11ms", "15ms"]
PRINCIPAL = "11ms"
UREF = {"8ms": 8.0, "11ms": 11.0, "15ms": 15.0}

# RANS-ML variants -> solver file suffix (label as used in the legends)
SOLVER_SUFFIX = {
    "RANS-ML 15M": ["15ml"],
    "RANS-ML 10M": ["10ml"],
    "RANS-ML 5M": ["5ml", "5"],          # 11 m/s uses "_5" (no "ml")
    "RANS-ML no clustering": ["noClustering"],
}

# --- prediction / clustering meshes (single, 11 m/s training) -------------
PRED_CLU = "dataset/risultati_rete/output_seep_con_clustering_11ms/results/rans_with_predictions.vtu"
PRED_CLU_HISTORY = "dataset/risultati_rete/output_seep_con_clustering_11ms/results/training_history_nut.csv"
PRED_CLU_METRICS = "dataset/risultati_rete/output_seep_con_clustering_11ms/results/metrics_nut.json"
PRED_NOCLU = "dataset/risultati_rete_noclustering/output_seep_/results/rans_with_predictions.vtu"
PRED_NOCLU_HISTORY = "dataset/risultati_rete_noclustering/output_seep_/results/training_history_nut.csv"
PRED_NOCLU_METRICS = "dataset/risultati_rete_noclustering/output_seep_/results/metrics_nut.json"

CLUSTER_DIR = Path("dataset/clustering _simpleFoam_corretto")
CLUSTER_MESH = str(CLUSTER_DIR / "0-NC_7final.vtu")        # carries the cluster "ID" field
CLUSTER_RANS_MESH = str(CLUSTER_DIR / "rans_mod.vtk")      # baseline RANS nut field
CLUSTER_ELBOW = str(CLUSTER_DIR / "elbow.csv")
CLUSTER_PCA_VARIANCE = str(CLUSTER_DIR / "pca_explained_variance_ratio0PCA-Cyl-normalizedOriginalFeats.csv")
CLUSTER_PCA_IMPORTANCE = str(CLUSTER_DIR / "pca_importance0PCA-Cyl-normalizedOriginalFeats.csv")


def first_existing(paths):
    """Return the first path that exists (handles the _5ml vs _5 naming)."""
    for path in paths:
        if Path(path).exists():
            return path
    raise FileNotFoundError(f"None of the candidate paths exist: {paths}")


def solver_meshes(case, label):
    """Return [yNormal, zNormal] solver result paths for a RANS-ML variant."""
    base = Path("dataset/risultati_solver") / case
    out = []
    for plane in ("yNormal", "zNormal"):
        candidates = [str(base / f"{plane}_{suffix}.vtp") for suffix in SOLVER_SUFFIX[label]]
        out.append(first_existing(candidates))
    return out


def rans_ref_meshes(case):
    """Return [yNormal, zNormal] RANS-reference paths for a case."""
    base = Path("dataset/ref_rans")
    return [str(base / f"yNormal_{case}.vtp"), str(base / f"zNormal_{case}.vtp")]


def les_ref(case):
    """Return (paths, velocity_field, has_k) for the LES reference of a case."""
    if case == "11ms":
        return (["dataset/ref_les/les_mesh_with_k.vtp"], "UMean", True)
    if case == "8ms":
        return (["dataset/ref_les/8ms/yNormal.vtp"], "UMean", True)
    if case == "15ms":
        return (["dataset/ref_les/15ms/yNormal.vtp"], "UMean", False)
    raise ValueError(f"Unknown case: {case}")
