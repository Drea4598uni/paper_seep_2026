"""
Publication-quality static figures for the 24-case wind-CFD cost study.
Outputs (vector = editable in Inkscape/Illustrator, plus PNG preview):
  fig_parallel_coordinates.{svg,pdf,png}   <- editable version of the interactive chart
  fig_dotplot_small_multiples.{svg,pdf,png} <- recommended figure for the paper
  fig_heatmap.{svg,pdf,png}                  <- compact alternative
Data are read from cases.json (produced by model.py).
"""
import json, numpy as np
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

mpl.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8.5,
    "axes.linewidth": 0.7, "axes.edgecolor": "#444444",
    "xtick.major.width": 0.7, "ytick.major.width": 0.7,
    "savefig.dpi": 300, "savefig.bbox": "tight", "pdf.fonttype": 42, "svg.fonttype": "none",
})

rows = json.load(open("cases.json"))
def short(r):
    g = "FG" if "full geometry" in r["config"] else "AL"
    sc = "S" if "Single" in r["config"] else ("F20" if "20" in r["config"] else "F40")
    return f"#{r['case']} {g}·{sc} {r['model']} {r['size_MW']}MW"
for r in rows:
    r["geom"] = "Full geometry" if "full geometry" in r["config"] else "Actuator"
    r["label"] = short(r)

C_FG, C_AL = "#1D9E75", "#D85A30"
col = lambda r: C_FG if r["geom"] == "Full geometry" else C_AL

METRICS = [
    ("cells_M",   "Grid size\n(10⁶ cells)", False),
    ("dx_min_m",  "Min cell Δx\n(m)",        True),   # reversed: up/right = finer
    ("core_hours","Core-hours\n(CPU-core-h)",     False),
    ("wall_days", "Wall-clock\n(days)",           False),
    ("energy_MWh","Energy\n(MWh)",                 False),
    ("cost_EUR",  "Cost\n(€)",               False),
]

def fmt(v, k):
    if k == "dx_min_m":
        return f"{v:.0e}" if v < 0.01 else f"{v:.2f}"
    if k == "cells_M":
        return f"{v:,.0f}"
    if k in ("wall_days",):
        return f"{v:.2f}" if v < 1 else f"{v:,.0f}"
    if k == "energy_MWh":
        return f"{v:.2f}" if v < 1 else f"{v:,.0f}"
    return f"{v:,.0f}"

# ----------------------------------------------------------------------
# 1. PARALLEL COORDINATES (editable version of the interactive chart)
# ----------------------------------------------------------------------
def parallel_coordinates():
    keys = [m[0] for m in METRICS]
    lo = {k: np.log10(min(r[k] for r in rows)) for k in keys}
    hi = {k: np.log10(max(r[k] for r in rows)) for k in keys}
    def npos(k, v, rev):
        p = (np.log10(v) - lo[k]) / (hi[k] - lo[k])
        return 1 - p if rev else p
    fig, ax = plt.subplots(figsize=(7.4, 4.3))
    xs = np.arange(len(METRICS))
    for r in rows:
        ys = [npos(k, r[k], rev) for (k, _, rev) in METRICS]
        ax.plot(xs, ys, color=col(r), lw=1.0, alpha=0.55,
                ls="-" if r["model"] == "LES" else (0, (5, 3)))
    for i, (k, name, rev) in enumerate(METRICS):
        ax.axvline(i, color="#888888", lw=0.8, zorder=0)
        for frac in (0.0, 0.5, 1.0):
            logv = lo[k] + (1 - frac if rev else frac) * (hi[k] - lo[k])
            ax.text(i + 0.04, frac, fmt(10 ** logv, k), fontsize=6.5,
                    va="center", ha="left", color="#333333")
    ax.set_xticks(xs)
    ax.set_xticklabels([m[1] for m in METRICS], fontsize=8)
    ax.set_yticks([]); ax.set_ylim(-0.05, 1.08); ax.set_xlim(-0.3, len(METRICS) - 0.55)
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.annotate("", xy=(-0.18, 1.0), xytext=(-0.18, 0.0),
                arrowprops=dict(arrowstyle="->", color="#555555", lw=0.8))
    ax.text(-0.30, 0.5, "higher = more demanding (Δx: finer)", rotation=90,
            va="center", ha="center", fontsize=7, color="#555555")
    leg = [Line2D([0],[0], color=C_FG, lw=2, label="Full geometry (blade-resolved)"),
           Line2D([0],[0], color=C_AL, lw=2, label="Actuator line/disk"),
           Line2D([0],[0], color="#555555", lw=1.3, ls="-", label="LES"),
           Line2D([0],[0], color="#555555", lw=1.3, ls=(0,(5,3)), label="URANS")]
    ax.legend(handles=leg, loc="lower center", bbox_to_anchor=(0.5, -0.27),
              ncol=4, frameon=False, fontsize=7.5, handlelength=2.2, columnspacing=1.4)
    fig.subplots_adjust(left=0.10, right=0.98, top=0.97, bottom=0.20)
    for ext in ("svg", "pdf", "png"):
        fig.savefig(f"fig_parallel_coordinates.{ext}")
    plt.close(fig)

# ----------------------------------------------------------------------
# 2. SMALL-MULTIPLES DOT / LOLLIPOP PLOT  (recommended for the paper)
# ----------------------------------------------------------------------
def dotplot():
    data = sorted(rows, key=lambda r: r["cost_EUR"])
    y = np.arange(len(data))
    fig, axes = plt.subplots(1, len(METRICS), figsize=(9.6, 6.6), sharey=True)
    for ax, (k, name, rev) in zip(axes, METRICS):
        vals = [r[k] for r in data]
        x0 = min(vals) * 0.6
        for yi, r in zip(y, data):
            ax.plot([x0, r[k]], [yi, yi], color="#cccccc", lw=0.6, zorder=1)
            mk = "o" if r["model"] == "LES" else "s"
            face = col(r) if r["model"] == "LES" else "white"
            ax.scatter(r[k], yi, marker=mk, s=24, facecolors=face,
                       edgecolors=col(r), linewidths=0.9, zorder=3)
        ax.set_xscale("log")
        ax.set_title(name, fontsize=8)
        ax.tick_params(axis="x", labelsize=6.5)
        ax.grid(axis="x", color="#eeeeee", lw=0.5)
        for s in ("top", "right"): ax.spines[s].set_visible(False)
        if rev: ax.invert_xaxis()
    axes[0].set_yticks(y)
    axes[0].set_yticklabels([r["label"] for r in data], fontsize=6.3)
    axes[0].set_ylim(-0.6, len(data) - 0.4)
    leg = [Line2D([0],[0], marker="o", color="w", markerfacecolor=C_FG, markeredgecolor=C_FG, label="Full geometry", markersize=7),
           Line2D([0],[0], marker="o", color="w", markerfacecolor=C_AL, markeredgecolor=C_AL, label="Actuator", markersize=7),
           Line2D([0],[0], marker="o", color="w", markerfacecolor="#555", markeredgecolor="#555", label="LES (filled)", markersize=7),
           Line2D([0],[0], marker="s", color="w", markerfacecolor="white", markeredgecolor="#555", label="URANS (open)", markersize=7)]
    fig.legend(handles=leg, loc="upper center", ncol=4, frameon=False, fontsize=8,
               bbox_to_anchor=(0.5, 1.005))
    fig.text(0.5, 0.005, "cases sorted by cost (ascending); x-axes logarithmic; Δx axis reversed (finer to the right)",
             ha="center", fontsize=6.8, color="#555555")
    fig.subplots_adjust(left=0.16, right=0.99, top=0.93, bottom=0.06, wspace=0.18)
    for ext in ("svg", "pdf", "png"):
        fig.savefig(f"fig_dotplot_small_multiples.{ext}")
    plt.close(fig)

# ----------------------------------------------------------------------
# 3. HEATMAP  (compact alternative)
# ----------------------------------------------------------------------
def heatmap():
    data = sorted(rows, key=lambda r: r["cost_EUR"])
    keys = [m[0] for m in METRICS]
    M = np.zeros((len(data), len(METRICS)))
    for j, (k, name, rev) in enumerate(METRICS):
        v = np.array([np.log10(r[k]) for r in data])
        n = (v - v.min()) / (v.max() - v.min())
        M[:, j] = (1 - n) if rev else n          # darker = more demanding
    fig, ax = plt.subplots(figsize=(7.0, 7.4))
    im = ax.imshow(M, aspect="auto", cmap="cividis_r", vmin=0, vmax=1)
    ax.set_xticks(range(len(METRICS)))
    ax.set_xticklabels([m[1].replace("\n", " ") for m in METRICS], fontsize=7.5, rotation=25, ha="right")
    ax.set_yticks(range(len(data)))
    ax.set_yticklabels([r["label"] for r in data], fontsize=6.3)
    for i, r in enumerate(data):
        for j, (k, name, rev) in enumerate(METRICS):
            ax.text(j, i, fmt(r[k], k), ha="center", va="center", fontsize=5.6,
                    color="white" if M[i, j] > 0.55 else "black")
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.02)
    cb.set_label("normalized log value  (darker = more demanding)", fontsize=7.5)
    cb.ax.tick_params(labelsize=6.5)
    ax.set_xticks(np.arange(-.5, len(METRICS), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(data), 1), minor=True)
    ax.grid(which="minor", color="white", lw=0.6)
    ax.tick_params(which="minor", length=0)
    fig.subplots_adjust(left=0.17, right=0.99, top=0.95, bottom=0.08)
    for ext in ("svg", "pdf", "png"):
        fig.savefig(f"fig_heatmap.{ext}")
    plt.close(fig)

parallel_coordinates(); dotplot(); heatmap()
print("done: parallel_coordinates, dotplot_small_multiples, heatmap (svg/pdf/png)")
