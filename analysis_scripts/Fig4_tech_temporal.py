"""
Fig4_tech_temporal.py
=====================
Purpose : Generate Figure 4 for the manuscript:
          
Figure content
--------------
Panel (a): Boxplot of GAQI scores across four technology families (n >= 3),
           with individual report scores jittered and overlaid.
           Technology families with n < 3 (dual-fuel, waste-to-energy)
           are excluded per the pre-specified threshold stated in the paper.
           Note: HFO group n = 3 produces a compressed box — this is
           mathematically correct and noted in the figure caption.

Panel (b): Scatter plot of GAQI score versus year of preparation (n = 37;
           one report without a stated year excluded), with an OLS trend
           line and the Paris Agreement adoption marker.

Output
------
outputs/Fig4_tech_temporal.png  (300 DPI, journal-ready)

Run from the folder containing the Excel file:
    python Fig4_tech_temporal.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
matplotlib.rcParams['font.family'] = 'serif'
matplotlib.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']

# ── paths ──────────────────────────────────────────────────────────────────
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
DATA_FILE   = os.path.join(SCRIPT_DIR, "..", "Manual_Extraction_Paper2_Final Outcome_VS code.csv")
OUTPUT_DIR  = os.path.join(SCRIPT_DIR, "outputs")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "Fig4_tech_temporal.png")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── load ───────────────────────────────────────────────────────────────────
df = pd.read_csv(DATA_FILE, header=2)
df = df.dropna(how="all").reset_index(drop=True)
df.columns = [str(c).strip() for c in df.columns]
df["GAQI"]   = pd.to_numeric(df["GAQI_Total (0-100)"], errors="coerce")
df["Year_n"] = pd.to_numeric(df["Year"],               errors="coerce")

# ── technology grouping (n >= 3 only; n < 3 excluded per paper) ────────────
def assign_family(tech):
    t = str(tech)
    if "Coal" in t:                        return "Coal"
    if t.startswith("Gas/LNG"):            return "Gas/LNG"
    if "HFO" in t:                         return "HFO"        # n=3 only
    if "Solar" in t or "Wind" in t:        return "Solar/Wind"
    return "Excluded"   # Dual-fuel (n=2) and Waste-to-Energy (n=1) excluded

df["Fam"] = df["Technology"].apply(assign_family)
FAMILIES   = ["Coal", "Gas/LNG", "HFO", "Solar/Wind"]
FCOLS      = ["#D55E00", "#56B4E9", "#0072B2", "#009E73"]

# ── verify group sizes ────────────────────────────────────────────────────
expected_n = {"Coal": 10, "Gas/LNG": 15, "HFO": 3, "Solar/Wind": 7}
for f, en in expected_n.items():
    actual_n = df[df["Fam"] == f]["GAQI"].notna().sum()
    assert actual_n == en, f"{f}: n={actual_n}, expected {en}"

# ── verify statistics ─────────────────────────────────────────────────────
groups = [df[df["Fam"] == f]["GAQI"].dropna().values for f in FAMILIES]
H, pk  = stats.kruskal(*groups)
assert abs(H  - 3.94) < 0.01, f"KW H mismatch: {H:.2f}"
assert abs(pk - 0.27) < 0.01, f"KW p mismatch: {pk:.2f}"

sub = df.dropna(subset=["Year_n", "GAQI"])
rho, p_rho = stats.spearmanr(sub["Year_n"], sub["GAQI"])
assert len(sub) == 37,          f"Scatter N mismatch: {len(sub)}"
assert abs(rho   - 0.24) < 0.005, f"Spearman rho mismatch: {rho:.3f}"
assert abs(p_rho - 0.15) < 0.01,  f"Spearman p mismatch: {p_rho:.3f}"

# ── global style ───────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":    "serif",
    "font.serif":     ["DejaVu Serif"],
    "font.size":      13,
    "axes.linewidth": 0.8,
    "figure.dpi":     300,
    "savefig.dpi":    300,
    "axes.edgecolor": "#333",
    "xtick.color":    "#333",
    "ytick.color":    "#333",
})

# ── figure ─────────────────────────────────────────────────────────────────
np.random.seed(7)   # fixed seed for reproducible jitter
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))

# ── panel (a) — technology boxplot ────────────────────────────────────────
ax = axes[0]
bp = ax.boxplot(
    groups, vert=True, patch_artist=True, widths=0.55,
    medianprops=dict(color="black", lw=1.4),
    flierprops=dict(marker="o", markersize=3,
                    markerfacecolor="#888888", markeredgecolor="none"),
)
for patch, col in zip(bp["boxes"], FCOLS):
    patch.set_facecolor(col)
    patch.set_alpha(0.55)
    patch.set_edgecolor("#333333")

# jittered individual points
for i, (grp, col) in enumerate(zip(groups, FCOLS)):
    jitter = np.random.normal(i + 1, 0.05, len(grp))
    ax.scatter(jitter, grp, s=14, color="#333333",
               edgecolor="white", linewidth=0.4,
               zorder=3, alpha=0.9)

ns = [len(g) for g in groups]
ax.set_xticks(range(1, len(FAMILIES) + 1))
ax.set_xticklabels(
    [f"{f}\n(n={n})" for f, n in zip(FAMILIES, ns)],
    fontsize=13
)
ax.set_ylabel("GAQI total score")
ax.set_xlabel("Generation technology")
ax.set_ylim(0, 90)
ax.set_title("(a) GAQI by generation technology",
             fontweight="bold", loc="left")

# KW result annotation
ax.text(0.97, 0.96,
        f"Kruskal–Wallis H = {H:.2f}, p = {pk:.2f} (n.s.)",
        transform=ax.transAxes, ha="right", va="top", fontsize=8,
        style="italic",
        bbox=dict(boxstyle="round,pad=0.3",
                  fc="#f5f5f0", ec="#cccccc", lw=0.6))

for s in ["top", "right"]:
    ax.spines[s].set_visible(False)

# ── panel (b) — temporal scatter ─────────────────────────────────────────
ax = axes[1]
ax.scatter(sub["Year_n"], sub["GAQI"],
           s=34, color="#0072B2",
           edgecolor="white", linewidth=0.5,
           alpha=0.85, zorder=3)

# OLS trend line
z  = np.polyfit(sub["Year_n"], sub["GAQI"], 1)
xp = np.array([sub["Year_n"].min(), sub["Year_n"].max()])
ax.plot(xp, np.poly1d(z)(xp),
        color="#D55E00", lw=1.4, ls="--", zorder=2)

# Paris Agreement marker
ax.axvline(2015.5, color="#444444", lw=1.0, ls=":")
ax.text(2015.7, 30,
        "Paris Agreement\n(adopted Dec 2015)",
        fontsize=12, color="#444444", va="center")

# Spearman annotation
ax.text(0.97, 0.96,
        f"Spearman \u03c1 = {rho:.2f}, p = {p_rho:.2f} (n.s., N = 37)",
        transform=ax.transAxes, ha="right", fontsize=8,
        style="italic", va="top",
        bbox=dict(boxstyle="round,pad=0.3",
                  fc="#f5f5f0", ec="#cccccc", lw=0.6))

ax.set_xlabel("Year of EIA report")
ax.set_ylabel("GAQI total score")
ax.set_ylim(0, 90)
ax.set_title("(b) Temporal pattern in assessment quality",
             fontweight="bold", loc="left")
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)

plt.tight_layout()
plt.savefig(OUTPUT_FILE, bbox_inches="tight")
plt.close()

print(f"Figure 4 saved to: {OUTPUT_FILE}")
print(f"  Technology groups: {dict(zip(FAMILIES, ns))}")
print(f"  KW: H = {H:.2f}, p = {pk:.2f}")
print(f"  Spearman rho = {rho:.2f}, p = {p_rho:.2f}")
print(f"  Scatter N = {len(sub)} (1 report without year excluded)")
print("  Note: HFO n=3 produces compressed boxplot — mathematically correct.")
