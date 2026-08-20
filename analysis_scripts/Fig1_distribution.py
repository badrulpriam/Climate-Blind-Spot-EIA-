"""
Fig1_distribution.py
====================
Purpose : Generate Figure 1 for the manuscript:
          
Figure content
--------------
Panel (a): Histogram of GAQI composite scores (5-point bins) with the five
           quality classification bands shaded and mean/median lines marked.
Panel (b): Horizontal bar chart showing frequency and percentage of reports
           in each GAQI quality class.

Fix applied vs original
-----------------------
Median label corrected from 56 to 55.5 (computed value: exactly 55.5).

Output
------
outputs/Fig1_distribution.png  (300 DPI, journal-ready)

Run from the folder containing the Excel file:
    python Fig1_distribution.py
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
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "Fig1_distribution.png")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── load ───────────────────────────────────────────────────────────────────
df = pd.read_csv(DATA_FILE, header=2)
df = df.dropna(how="all").reset_index(drop=True)
df.columns = [str(c).strip() for c in df.columns]
df["GAQI"] = pd.to_numeric(df["GAQI_Total (0-100)"], errors="coerce")
N = len(df)

# ── verified statistics ────────────────────────────────────────────────────
mean_val   = df["GAQI"].mean()
median_val = df["GAQI"].median()   # exactly 55.5 — corrected from 56 in original
assert abs(mean_val   - 48.3) < 0.1, f"Mean mismatch: {mean_val}"
assert abs(median_val - 55.5) < 0.1, f"Median mismatch: {median_val}"

# ── global style ───────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":        "serif",
    "font.serif":         ["Times New Roman", "DejaVu Serif"],
    "font.size":          14,
    "axes.titlesize":     14,
    "axes.labelsize":     14,
    "axes.linewidth":     0.8,
    "figure.dpi":         300,
    "savefig.dpi":        300,
    "axes.edgecolor":     "#333333",
    "xtick.color":        "#333333",
    "ytick.color":        "#333333",
    "axes.labelcolor":    "#111111",
    "text.color":         "#111111",
})

# ── colour palette ─────────────────────────────────────────────────────────
BAND_COLS = {
    "Inadequate (0–19)":   ("#9e3b3b", 0,  19),
    "Poor (20–39)":        ("#c77f2a", 20, 39),
    "Satisfactory (40–59)":("#d9c14a", 40, 59),
    "Good (60–79)":        ("#4a7c59", 60, 79),
    "Excellent (80–100)":  ("#1f6b4a", 80, 100),
}
CLASS_COLS = ["#D55E00", "#E69F00", "#56B4E9", "#0072B2", "#009E73"]
C_BAR = "#1f3b57"

# ── figure ─────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(
    1, 2, figsize=(10, 4.0),
    gridspec_kw={"width_ratios": [1.25, 1]}
)

# ── panel (a) — histogram ─────────────────────────────────────────────────
ax = axes[0]
ax.set_facecolor("white")
bins = np.arange(0, 101, 5)

ax.hist(df["GAQI"], bins=bins, color=C_BAR,
        edgecolor="white", linewidth=0.6, zorder=3)

# mean and median lines — median label CORRECTED to 55.5
ax.axvline(mean_val,   color="black",    ls="--", lw=1.8, zorder=4,
           label=f"Mean = {mean_val:.1f}")
ax.axvline(median_val, color="#9e3b3b",  ls=":",  lw=2.0, zorder=4,
           label=f"Median = {median_val:.1f}")

ax.set_xlabel("GAQI total score (0–100)")
ax.set_ylabel("Number of EIA reports")
ax.set_xlim(0, 100)
ax.set_ylim(0, 8)
ax.legend(frameon=False, fontsize=12, loc="upper left")
ax.set_title("(a) Distribution of GAQI scores",
             loc="left", fontweight="bold")
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)

# ── panel (b) — classification bar chart ─────────────────────────────────
ax = axes[1]
class_order = ["Inadequate", "Poor", "Satisfactory", "Good", "Excellent"]
counts = [(df["GAQI_Class"] == c).sum() for c in class_order]

# verify counts match data
assert counts == [8, 3, 11, 15, 1], f"Class counts mismatch: {counts}"

bars = ax.barh(range(len(class_order)), counts,
               color=CLASS_COLS, edgecolor="white", height=0.7)
ax.set_yticks(range(len(class_order)))
ax.set_yticklabels(class_order)
ax.invert_yaxis()

for i, (c, b) in enumerate(zip(counts, bars)):
    ax.text(c + 0.15, i,
            f"{c} ({100 * c / N:.1f}%)",
            va="center", fontsize=14)


ax.set_xlabel("Number of EIA reports")
ax.set_xlim(0, 17.5)
ax.set_title("(b) GAQI classification",
             loc="left", fontweight="bold")
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)

plt.tight_layout()
plt.savefig(OUTPUT_FILE, bbox_inches="tight")
plt.close()

print(f"Figure 1 saved to: {OUTPUT_FILE}")
print(f"  Mean   = {mean_val:.1f}  (label: {mean_val:.1f})")
print(f"  Median = {median_val:.1f}  (label: {median_val:.1f})  <-- CORRECTED from 56")
print(f"  N = {N}")
