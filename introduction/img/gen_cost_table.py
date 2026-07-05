"""
Generate the LaTeX cost-model table (longtable) for the introduction.

Reads:
  cases.json       -> the 24 cost-model scenarios (from the Word report)
  lit_cases.json   -> the 13 literature reference cases overlaid on Fig. 1
  ../../MAIN.aux   -> \\bibcite{key}{N} mapping for the "Ref [N]" labels

Writes:
  cost_table.tex   -> \\input-ed by the introduction

Run AFTER a LaTeX pass has refreshed MAIN.aux (so the ref numbers are current),
then recompile the paper.
"""
import os, re, json, math

HERE = os.path.dirname(os.path.abspath(__file__))
cases = json.load(open(os.path.join(HERE, "cases.json")))
lit   = json.load(open(os.path.join(HERE, "lit_cases.json")))

# ---- ref numbers from MAIN.aux ----
REFNUM = {}
aux = os.path.join(HERE, "..", "..", "MAIN.aux")
if os.path.exists(aux):
    for m in re.finditer(r"\\bibcite\{([^}]+)\}\{([^}]+)\}", open(aux).read()):
        REFNUM[m.group(1)] = m.group(2)

C_BY_MODEL = {"LES": 3e-5, "URANS": 2e-4}   # core-s / cell / step (report calibration)

def sci(v):
    e = int(math.floor(math.log10(v)))
    m = v / 10**e
    return f"${m:.1f}\\!\\times\\!10^{{{e}}}$"

def fmt_cells(mcells):              # value already in millions
    return f"{mcells:,.1f}" if mcells < 1000 else f"{mcells:,.0f}"

def fmt_ch(v):
    if v >= 1e6: return f"{v/1e6:,.1f}M"
    if v >= 1e3: return f"{v/1e3:,.0f}k"
    return f"{v:.0f}"

def abbr_config(cfg):
    cfg = cfg.replace("Single turbine", "Single").replace("Wind farm 20", "WF-20").replace("Wind farm 40", "WF-40")
    cfg = cfg.replace(" - full geometry", ", full-geom.").replace(" - actuator line/disk", ", actuator")
    return cfg

def esc(s):
    return s

rows = []

# ---- 24 cost-model scenarios ----
for r in cases:
    rows.append(" & ".join([
        str(r["case"]),
        abbr_config(r["config"]),
        r["model"],
        str(r["size_MW"]),
        fmt_cells(r["cells_M"]),
        sci(r["n_steps"]),
        fmt_ch(r["core_hours"]),
        f"{r['cost_EUR']:,.0f}",
    ]) + r" \\")

# ---- 13 literature reference cases (ordered by ref number) ----
def keynum(rec):
    n = REFNUM.get(rec["key"]);  return int(n) if n else 9999
lit_sorted = sorted(lit, key=keynum)

lit_rows = []
missing = []
for rec in lit_sorted:
    num = REFNUM.get(rec["key"])
    if num is None:
        missing.append(rec["key"]); continue
    scale = "Single" if rec["scale"] == "single" else "Farm"
    geom  = "full-geom." if rec["geom"] == "full" else "actuator"
    cfg   = f"{scale}, {geom}"
    cells = rec["cells"]; steps = rec["steps"]
    ch    = cells * steps * C_BY_MODEL[rec["model"]] / 3600.0
    lit_rows.append(" & ".join([
        f"Ref [{num}]",
        cfg,
        rec["model"],
        "--",
        fmt_cells(cells / 1e6),
        sci(steps),
        fmt_ch(ch) + r"$^{\dagger}$",
        "--",
    ]) + r" \\")

if missing:
    print("WARNING: no ref number for:", ", ".join(missing))

header = (r"Case & Configuration & Model & MW & Cells [$10^{6}$] & "
          r"$N_\mathrm{steps}$ & Core-h & Cost [EUR] \\")

out = []
out.append(r"\begingroup")
out.append(r"\scriptsize")
out.append(r"\setlength{\tabcolsep}{3pt}")
out.append(r"\begin{longtable}{@{}llccrrrr@{}}")
out.append(r"\caption{Cost-model scenarios behind Fig.~\ref{fig:cost_landscape} (order-of-magnitude "
           r"estimates) and the literature reference cases overlaid on it. The calculation chain is "
           r"detailed in the text.}\label{tab:cost_model}\\")
out.append(r"\hline")
out.append(header)
out.append(r"\hline")
out.append(r"\endfirsthead")
out.append(r"\multicolumn{8}{@{}l}{\footnotesize\itshape Table~\ref{tab:cost_model} -- continued} \\")
out.append(r"\hline")
out.append(header)
out.append(r"\hline")
out.append(r"\endhead")
out.append(r"\hline")
out.append(r"\endfoot")
out.append(r"\multicolumn{8}{@{}p{0.96\linewidth}}{\footnotesize $^{\dagger}$~Reference-case "
           r"core-hours are indicative, computed with the same per-cell solver cost as the cost-model "
           r"scenarios ($C=2\times10^{-4}$~core-s/cell/step for URANS, $3\times10^{-5}$ for LES); the "
           r"cells and $N_\mathrm{steps}$ of the reference cases are order-of-magnitude placements "
           r"(see Fig.~\ref{fig:cost_landscape}).} \\")
out.append(r"\hline")
out.append(r"\endlastfoot")
out.extend(rows)
out.append(r"\hline")
out.append(r"\multicolumn{8}{@{}l}{\itshape Literature reference cases (Fig.~\ref{fig:cost_landscape})} \\")
out.append(r"\hline")
out.extend(lit_rows)
out.append(r"\end{longtable}")
out.append(r"\endgroup")

open(os.path.join(HERE, "cost_table.tex"), "w").write("\n".join(out) + "\n")
print(f"done: cost_table.tex  ({len(rows)} model rows + {len(lit_rows)} literature rows)")
