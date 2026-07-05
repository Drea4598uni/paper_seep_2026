"""
Simulation-cost SELECTION CHART (turbine-selection-nomogram style).
All cases resolve the WAKE (run for several flow-through times).
x = total grid cells, y = number of time steps (log-log).
Diagonal lines = iso-core-hours (slope -1), labelled with the energy-bill cost.
Shaded bands = compute-cost / feasibility regimes.
Points: colour = geometry, shape = single(▲)/farm(●), fill = LES(solid)/URANS(open).
Output: fig_selection_chart.{svg,pdf,png}  (vector = editable).
"""
import os, json, math, numpy as np
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Liberation Sans", "DejaVu Sans"],
    "font.size": 9, "axes.linewidth": 0.8, "savefig.dpi": 300,
    "pdf.fonttype": 42, "svg.fonttype": "none",
})
HALO = [pe.withStroke(linewidth=2.2, foreground="white")]
HERE = os.path.dirname(os.path.abspath(__file__))
rows = json.load(open(os.path.join(HERE, "cases.json")))
C_REF = 2.5e-5
K = 3600.0 / C_REF
EUR_GPU = (1/600) * 2.5 * 1.2 * 0.15
EUR_CPU = (1/112) * 1.1 * 1.2 * 0.15

C_FG, C_AL = "#1D9E75", "#D85A30"
col = lambda r: C_FG if "full geometry" in r["config"] else C_AL
is_single = lambda r: "Single" in r["config"]

def euro(v):
    if v >= 1e6: return f"€{v/1e6:.1f}M"
    if v >= 1e3: return f"€{v/1e3:.0f}k"
    return f"€{v:.0f}"

def label(r):
    if is_single(r): return f"{r['size_MW']} MW"
    n = 20 if "20" in r["config"] else 40
    return f"{n}x{r['size_MW']} MW"

fig, ax = plt.subplots(figsize=(8.2, 6.6))
xlim = (6e6, 8e10); ylim = (3e4, 6e8)
xx = np.array(xlim)

edges = [1e4, 1e5, 1e6, 1e7, 1e8, 1e9, 1e10, 1e11]
band_lbl = ["Small cluster", "Departmental\ncluster", "Tier-0 allocation\n(e.g. CINECA Leonardo)",
            "Large Tier-0", "Leadership /\nfull machine", "Exascale", "Beyond exascale\n(not feasible)"]
band_col = ["#eef5ee", "#e3efe0", "#f6efe0", "#f4ddca", "#edbfa6", "#e08f6f", "#cf6440"]
band_pos = [(1.0e8, 4.4e4), (5e8, 9.5e4), (1.6e8, 3e6), (1.7e9, 3e6),
            (1.7e10, 3e6), (5.5e9, 1.1e8), (3.6e10, 1.0e8)]
band_txt = ["#3f5a3f", "#3f5a3f", "#6a5320", "#7a4a2a", "#8a3f25", "#8a2d2d", "#7a1f1f"]
xfill = np.logspace(np.log10(xlim[0]), np.log10(xlim[1]), 240)
for i in range(len(edges) - 1):
    lo = np.clip(edges[i] * K / xfill, ylim[0], ylim[1])
    hi = np.clip(edges[i + 1] * K / xfill, ylim[0], ylim[1])
    ax.fill_between(xfill, lo, hi, color=band_col[i], lw=0, zorder=0)
for i, lbl in enumerate(band_lbl):
    t = ax.text(*band_pos[i], lbl, fontsize=7.3, color=band_txt[i], ha="center",
                va="center", style="italic", zorder=5)
    t.set_path_effects(HALO)

# iso-core-hour diagonal lines (labels added after layout, see below)
for ch in edges:
    ax.plot(xx, ch * K / xx, color="#9a9a9a", lw=0.8, ls=(0, (6, 4)), zorder=1)

# operating points + labels (no connector lines)
for r in rows:
    cells = r["cells_M"] * 1e6
    steps = r["n_steps"]
    shape = "^" if is_single(r) else "o"
    face = col(r) if r["model"] == "LES" else "white"
    sz = 74 if is_single(r) else 54
    ax.scatter(cells, steps, marker=shape, s=sz, facecolors=face,
               edgecolors=col(r), linewidths=1.2, zorder=6)

    if r["size_MW"] == 15:
        dx, dy, ha, va = 5, 0, "left", "center"
    else:
        dx, dy, ha, va = -5, 0, "right", "center"
    #dx, dy, ha,va = 0,0, "right", "bottom"
    t = ax.annotate(label(r), (cells, steps), textcoords="offset points",
                    xytext=(dx, dy), ha=ha, va=va, fontsize=5.6, color=col(r), zorder=8)
    t.set_path_effects(HALO)

ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlim(*xlim); ax.set_ylim(*ylim)
ax.set_xlabel("Total grid size  (number of cells)")
ax.set_ylabel("Number of time steps")
ax.tick_params(labelsize=8)
for s in ("top", "right"): ax.spines[s].set_visible(False)

gray = "#666666"
leg = [
    Line2D([0],[0], marker="o", color="w", markerfacecolor=C_FG, markeredgecolor=C_FG, markersize=8, label="Full geometry"),
    Line2D([0],[0], marker="o", color="w", markerfacecolor=C_AL, markeredgecolor=C_AL, markersize=8, label="Actuator line/disk"),
    Line2D([0],[0], marker="^", color="w", markerfacecolor=gray, markeredgecolor=gray, markersize=9, label="Single turbine"),
    Line2D([0],[0], marker="o", color="w", markerfacecolor=gray, markeredgecolor=gray, markersize=8, label="Wind farm"),
    Line2D([0],[0], marker="o", color="w", markerfacecolor=gray, markeredgecolor=gray, markersize=8, label="LES (filled)"),
    Line2D([0],[0], marker="o", color="w", markerfacecolor="white", markeredgecolor=gray, markersize=8, label="URANS (open)"),
]
ax.legend(handles=leg, loc="upper left", fontsize=7.5, frameon=True, framealpha=0.92,
          edgecolor="#cccccc", handletextpad=0.4, borderpad=0.6, labelspacing=0.5)
t = ax.text(0.99, 0.02,
            r"iso-lines: C $\sim 2.5×10^{-5}$ core-s/cell/step; cost range = Booster(GPU)–DCGP(CPU)",
            transform=ax.transAxes, fontsize=6.2, color="#777777", ha="right", va="bottom")
t.set_path_effects(HALO)
fig.subplots_adjust(left=0.085, right=0.985, top=0.97, bottom=0.085)

# iso-line labels: ride each line at its left/upper-left entry, at the true screen angle
fig.canvas.draw()
p1 = ax.transData.transform((1e8, 1e6 * K / 1e8))
p2 = ax.transData.transform((1e10, 1e6 * K / 1e10))
ang = math.degrees(math.atan2(p2[1] - p1[1], p2[0] - p1[0]))
for ch in edges:
    e = int(round(np.log10(ch)))
    txt = f"$10^{{{e}}}$ core-h · {euro(ch*EUR_GPU)}–{euro(ch*EUR_CPU)}"
    if ch * K / xlim[0] <= ylim[1]:           # line enters the left edge
        px = xlim[0] * 1.6; py = ch * K / px
        if py > 8e7:                          # would sit under the top-left legend
            py = 7e7; px = ch * K / py
    else:                                     # line enters the top edge (anchor near top)
        py = ylim[1] * 0.9; px = ch * K / py
        if px < 2e8:                          # would sit under the top-left legend
            px = 3e8; py = ch * K / px
    t = ax.text(px, py, txt, fontsize=5.4, color="#4a4a4a", rotation=ang,
                rotation_mode="anchor", ha="left", va="bottom", zorder=9)
    t.set_path_effects(HALO)

for ext in ("svg", "pdf", "png"):
    fig.savefig(os.path.join(HERE, f"fig_selection_chart.{ext}"), bbox_inches=None)
print("done: fig_selection_chart")
