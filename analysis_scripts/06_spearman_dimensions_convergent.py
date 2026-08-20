"""
06_spearman_dimensions_convergent.py
=====================================
Purpose : Compute Spearman rank correlations between each GAQI dimension
          and the composite score, and the convergent validity check between
          the composite and the total GHG mention count.

Tests performed (7 total)
--------------------------
1.  D1_Presence        vs GAQI composite
2.  D2_Scopes          vs GAQI composite
3.  D3_Methodology     vs GAQI composite
4.  D4_Lifecycle       vs GAQI composite
5.  D5_Quantification  vs GAQI composite
6.  D6_Policy          vs GAQI composite
7.  Total_Mentions     vs GAQI composite  [convergent validity]

Why Spearman (not Pearson)
---------------------------
GAQI scores are significantly non-normal (Shapiro-Wilk W = 0.880, p < 0.001;
see 03_shapiro_wilk.py). GAQI is also a composite index whose interval
properties cannot be assumed. Spearman rank correlation is appropriate for
non-normal and ordinal-interpretable data.

Expected output (as reported in paper)
---------------------------------------
D1: rho = 0.845, p < 0.001
D2: rho = 0.868, p < 0.001
D3: rho = 0.861, p < 0.001
D4: rho = 0.691, p < 0.001
D5: rho = 0.829, p < 0.001
D6: rho = 0.456, p = 0.004
Total_Mentions: rho = 0.840, p < 0.001

Paper reference : Section 3.2 — dimension-composite relationships and
                  convergent validity
Output saved to : outputs/06_spearman_dimensions_convergent_output.csv

Run from the folder containing the Excel file:
    python 06_spearman_dimensions_convergent.py
"""

import os
import pandas as pd
import numpy as np
from scipy import stats

# ── paths ──────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "..", "Manual_Extraction_Paper2_Final Outcome_VS code.csv")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "06_spearman_dimensions_convergent_output.csv")
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
DIM_LABELS = ["D1_Presence", "D2_Scopes", "D3_Methodology",
              "D4_Lifecycle", "D5_Quantification", "D6_Policy"]
TOTAL_COL   = "GAQI_Total (0-100)"
MENTION_COL = "Total_Mentions"

for c in DIMS + [TOTAL_COL, MENTION_COL]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# expected values from paper
EXPECTED = {
    "D1_Presence":         (0.845, 0.001),
    "D2_Scopes":           (0.868, 0.001),
    "D3_Methodology":      (0.861, 0.001),
    "D4_Lifecycle":        (0.691, 0.001),
    "D5_Quantification":   (0.829, 0.001),
    "D6_Policy":           (0.456, 0.004),
    "Total_Mentions":      (0.840, 0.001),
}

# ── compute ────────────────────────────────────────────────────────────────
rows = []

# Dimension vs composite
for dim, label in zip(DIMS, DIM_LABELS):
    sub = df[[dim, TOTAL_COL]].dropna()
    rho, p = stats.spearmanr(sub[dim], sub[TOTAL_COL])
    exp_rho, exp_p_thresh = EXPECTED[label]
    rows.append({
        "Test":              "Spearman correlation",
        "Variable_X":        dim,
        "Variable_Y":        "GAQI_Total (0-100)",
        "Purpose":           "Dimension-composite relationship",
        "N":                 len(sub),
        "Spearman_rho":      round(rho, 3),
        "p_value":           round(p, 4),
        "p_value_display":   "< 0.001" if p < 0.001 else f"= {p:.4f}",
        "Significant_0.05":  p < 0.05,
        "Expected_rho":      exp_rho,
        "Match_rho":         abs(rho - exp_rho) < 0.002,
        "Paper_Section":     "Section 3.2",
        "Reported_In_Paper": f"rho = {exp_rho}, p {'< 0.001' if exp_p_thresh==0.001 else '= '+str(exp_p_thresh)}",
    })

# Convergent validity: Total_Mentions vs GAQI
sub_m = df[[MENTION_COL, TOTAL_COL]].dropna()
rho_m, p_m = stats.spearmanr(sub_m[MENTION_COL], sub_m[TOTAL_COL])
rows.append({
    "Test":              "Spearman correlation",
    "Variable_X":        "Total_Mentions",
    "Variable_Y":        "GAQI_Total (0-100)",
    "Purpose":           "Convergent validity check",
    "N":                 len(sub_m),
    "Spearman_rho":      round(rho_m, 3),
    "p_value":           round(p_m, 6),
    "p_value_display":   "< 0.001" if p_m < 0.001 else f"= {p_m:.4f}",
    "Significant_0.05":  p_m < 0.05,
    "Expected_rho":      0.840,
    "Match_rho":         abs(rho_m - 0.840) < 0.002,
    "Paper_Section":     "Section 3.2",
    "Reported_In_Paper": "rho = 0.840, p < 0.001",
})

out = pd.DataFrame(rows)
out.to_csv(OUTPUT_FILE, index=False)

# ── console output ─────────────────────────────────────────────────────────
print("=" * 65)
print("06 — SPEARMAN CORRELATIONS: DIMENSIONS & CONVERGENT VALIDITY")
print("=" * 65)
print(f"\n{'Variable X':<30} {'rho':>6} {'p':>10} {'Match':>6}")
print("-" * 60)
for _, r in out.iterrows():
    print(f"  {r['Variable_X']:<28} {r['Spearman_rho']:>6.3f} "
          f"{r['p_value_display']:>10}  {'YES' if r['Match_rho'] else 'NO':>5}")
all_match = out["Match_rho"].all()
print(f"\nAll values match paper: {all_match}")
print(f"\nOutput saved to: {OUTPUT_FILE}")
