"""
Fig2_dimensions.py
==================
Purpose : Generate Figure 2 for the manuscript:
          
Figure content
--------------
Vertical bar chart showing mean attainment of each GAQI dimension expressed
as a percentage of its maximum attainable score. Bars are colour-coded by
performance severity. Mean raw score and maximum are printed inside each bar.
A 50% reference line is included.

Output
------
outputs/Fig2_dimensions.png  (300 DPI, journal-ready)

Run from the folder containing the Excel file:
    python Fig2_dimensions.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# ── paths ──────────────────────────────────────────────────────────────────
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
DATA_FILE   = os.path.join(SCRIPT_DIR, "..", "Manual_Extraction_Paper2_Final Outcome_VS code.csv")
OUTPUT_DIR  = os.path.join(SCRIPT_DIR, "outputs")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "Fig2_dimensions.png")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── load ───────────────────────────────────────────────────────────────────
df = pd.read_csv(DATA_FILE, header=2)
df = df.dropna(how="all").reset_index(drop=True)
df.columns = [str(c).strip() for c in df.columns]

DIMS = [
    "D1_Presence (0-10)",
    "D2_Scopes (0-20)",
    "D3_Methodology (0-20)",
    "D4_Lifecycle (0-15)",
    "D5_Quantification (0-20)",
    "D6_Policy (0-15)",
]
DIM_MAX    = [10, 20, 20, 15, 20, 15]
DIM_LABELS = [
    "D1 Presence\n& prominence",
    "D2 Scope\ncoverage",
    "D3 Methodology\n& transparency",
    "D4 Lifecycle\ncoverage",
    "D5 Quantification\n& reporting",
    "D6 Policy\nintegration",
]

for c in DIMS:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# ── compute and verify ────────────────────────────────────────────────────
means   = [df[d].mean() for d in DIMS]
pct_max = [100 * m / mx for m, mx in zip(means, DIM_MAX)]

# Verify against paper-reported values
EXPECTED_PCT = [70.0, 39.7, 52.1, 54.6, 38.2, 47.5]
for d, pct, exp in zip(DIMS, pct_max, EXPECTED_PCT):
    assert abs(pct - exp) < 0.1, f"{d}: computed {pct:.1f}% vs expected {exp}%"

# ── global style ───────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":     "serif",
    "font.serif":      ["Times New Roman", "DejaVu Serif"],
    "font.size":       13,
    "axes.linewidth":  0.8,
    "figure.dpi":      300,
    "savefig.dpi":     300,
    "axes.edgecolor":  "#333",
    "xtick.color":     "#333",
    "ytick.color":     "#333",
})

# ── colour palette ─────────────────────────────────────────────────────────
C_RED    = "#D55E00"   # < 40% critical gap
C_AMBER  = "#E69F00"   # 40–55% weak
C_GREEN  = "#009E73"   # > 55% relative strength

def bar_colour(pct):
    if pct < 40:  return C_RED
    if pct < 55:  return C_AMBER
    return C_GREEN

colours = [bar_colour(p) for p in pct_max]

# ── figure ─────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8.2, 4.3))
xpos = np.arange(len(DIMS))

bars = ax.bar(xpos, pct_max, color=colours,
              edgecolor="white", width=0.66, zorder=3)

# 50% reference line
ax.axhline(50, color="#888", ls="--", lw=0.9, zorder=1)





ax.set_xticks(xpos)
ax.set_xticklabels(DIM_LABELS, fontsize=13)
ax.set_ylabel("Mean attainment (% of dimension maximum)")
ax.set_ylim(0, 80)

for s in ["top", "right"]:
    ax.spines[s].set_visible(False)

# legend
legend_handles = [
    Patch(fc=C_RED,   label="< 40% (critical gap)"),
    Patch(fc=C_AMBER, label="40–55% (weak)"),
    Patch(fc=C_GREEN, label="> 55% (relative strength)"),
]
ax.legend(handles=legend_handles, frameon=False,
          fontsize=12, loc="upper right", ncol=1)

plt.tight_layout()
plt.savefig(OUTPUT_FILE, bbox_inches="tight")
plt.close()

print(f"Figure 2 saved to: {OUTPUT_FILE}")
print("  Dimension attainment (verified):")
for lbl, pct, m, mx in zip(["D1","D2","D3","D4","D5","D6"], pct_max, means, DIM_MAX):
    print(f"    {lbl}: {m:.2f}/{mx} = {pct:.1f}%")
