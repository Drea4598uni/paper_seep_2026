"""
Simulation-cost SELECTION CHART - SciencePlots / IEEE styled variant.
Same content as make_selection_chart.py (all cases resolve the wake), but rendered
with the user's scienceplots('science','ieee') settings.
('no-latex' is used because the labels contain Unicode (euro sign, etc.); the few
mathematical symbols are written as mathtext so they render without LaTeX.)
Output: fig_selection_chart_ieee.{svg,pdf,png}
"""
import json, math, numpy as np
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import scienceplots  # noqa: F401
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D

plt.style.use(['science', 'ieee', 'no-latex'])
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
plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['pdf.fonttype'] = 42

HALO = [pe.withStroke(linewidth=2.0, foreground="white")]
rows = json.load(open("cases.json"))
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
    if is_single(r): return f"S {r['size_MW']} MW"
    n = 20 if "20" in r["config"] else 40
    return f"WF {n}x{r['size_MW']} MW"

fig, ax = plt.subplots()           # uses rcParams figure.figsize = (6, 4)
xlim = (6e6, 8e10); ylim = (3e4, 6e8)
xx = np.array(xlim)

edges = [1e4, 1e5, 1e6, 1e7, 1e8, 1e9, 1e10, 1e11]
band_lbl = ["Small cluster", "Departmental\ncluster", "Tier-0 allocation\n(e.g. Leonardo)",
            "Large Tier-0", "Leadership /\nfull machine", "Exascale", "Beyond exascale\n(infeasible)"]
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
    t = ax.text(*band_pos[i], lbl, fontsize=6.0, color=band_txt[i], ha="center",
                va="center", style="italic", zorder=5)
    t.set_path_effects(HALO)

for ch in edges:
    ax.plot(xx, ch * K / xx, color="#9a9a9a", lw=0.7, ls=(0, (6, 4)), zorder=1)

for r in rows:
    cells = r["cells_M"] * 1e6
    steps = r["n_steps"]
    shape = "^" if is_single(r) else "o"
    face = col(r) if r["model"] == "LES" else "white"
    sz = 34 if is_single(r) else 24
    ax.scatter(cells, steps, marker=shape, s=sz, facecolors=face,
               edgecolors=col(r), linewidths=0.9, zorder=6)
    if r["size_MW"] == 15:
        dx, dy, ha, va = 4, 5, "left", "bottom"
    else:
        dx, dy, ha, va = -4, -5, "right", "top"
    t = ax.annotate(label(r), (cells, steps), textcoords="offset points",
                    xytext=(dx, dy), ha=ha, va=va, fontsize=4.6, color=col(r), zorder=8)
    t.set_path_effects(HALO)

ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlim(*xlim); ax.set_ylim(*ylim)
ax.set_xlabel("Total grid size  (number of cells)")
ax.set_ylabel("Number of time steps")

gray = "#666666"
leg = [
    Line2D([0],[0], marker="o", color="w", markerfacecolor=C_FG, markeredgecolor=C_FG, markersize=5, label="Full geometry"),
    Line2D([0],[0], marker="o", color="w", markerfacecolor=C_AL, markeredgecolor=C_AL, markersize=5, label="Actuator line/disk"),
    Line2D([0],[0], marker="^", color="w", markerfacecolor=gray, markeredgecolor=gray, markersize=5.5, label="Single turbine"),
    Line2D([0],[0], marker="o", color="w", markerfacecolor=gray, markeredgecolor=gray, markersize=5, label="Wind farm"),
    Line2D([0],[0], marker="o", color="w", markerfacecolor=gray, markeredgecolor=gray, markersize=5, label="LES (filled)"),
    Line2D([0],[0], marker="o", color="w", markerfacecolor="white", markeredgecolor=gray, markersize=5, label="URANS (open)"),
]
ax.legend(handles=leg, loc="upper left", fontsize=5.6, ncol=1, handletextpad=0.3,
          labelspacing=0.3, borderpad=0.3)
t = ax.text(0.99, 0.02,
            r"all cases resolve the wake; labels: S = single, WF = wind farm (cols$\times$MW)"
            "\n"
            r"iso-lines: $C\approx2.5{\times}10^{-5}$ core-s/cell/step; cost = Booster(GPU)–DCGP(CPU)",
            transform=ax.transAxes, fontsize=5.0, color="#777777", ha="right", va="bottom")
t.set_path_effects(HALO)
fig.subplots_adjust(left=0.13, right=0.97, top=0.96, bottom=0.13)

# iso-line labels: ride each line at its left/upper-left entry, at the true screen angle
fig.canvas.draw()
p1 = ax.transData.transform((1e8, 1e6 * K / 1e8))
p2 = ax.transData.transform((1e10, 1e6 * K / 1e10))
ang = math.degrees(math.atan2(p2[1] - p1[1], p2[0] - p1[0]))
for ch in edges:
    e = int(round(np.log10(ch)))
    txt = f"$10^{{{e}}}$ core-h: {euro(ch*EUR_GPU)}–{euro(ch*EUR_CPU)}"
    if ch * K / xlim[0] <= ylim[1]:
        px = xlim[0] * 1.6; py = ch * K / px
        if py > 8e7:
            py = 7e7; px = ch * K / py
    else:
        py = ylim[1] * 0.9; px = ch * K / py
        if px < 2e8:
            px = 3e8; py = ch * K / px
    t = ax.text(px, py, txt, fontsize=4.4, color="#4a4a4a", rotation=ang,
                rotation_mode="anchor", ha="left", va="bottom", zorder=9)
    t.set_path_effects(HALO)

for ext in ("svg", "pdf", "png"):
    fig.savefig(f"fig_selection_chart_ieee.{ext}", bbox_inches=None)
print("done: fig_selection_chart_ieee")
