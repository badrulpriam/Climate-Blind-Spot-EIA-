"""
09_spearman_temporal_mitigation.py
====================================
Purpose : Compute Spearman rank correlations for the temporal trend in
          assessment quality and the association between mitigation-measure
          count and quality.

Tests performed (2 total)
--------------------------
1. Year of preparation vs GAQI composite
   H0: No monotonic association between year and assessment quality
   Expected: rho = 0.24, p = 0.15  (non-significant)

2. Mitigation-measure count vs GAQI composite
   H0: No monotonic association between mitigation count and quality
   Expected: rho = 0.58, p < 0.001  (significant)

Why Spearman (not Pearson)
---------------------------
GAQI scores are significantly non-normal (Shapiro-Wilk p < 0.001). Both
Year and Mitigation count also contain outliers that would distort Pearson
coefficients. Spearman is robust to both issues.

Note on Year: one report has no stated year (excluded from this test).
N for year correlation = 37.

Comparison with Pearson
-----------------------
The script also reports Pearson r alongside Spearman rho for transparency.
The Year-GAQI Pearson r = 0.137 (p = 0.418) and Mitigation-GAQI Pearson
r = 0.370 (p = 0.022) are reported for completeness; Spearman is used in
the paper because it is more appropriate for this data structure.

Paper reference : Section 3.8 — determinants of assessment quality
Output saved to : outputs/09_spearman_temporal_mitigation_output.csv

Run from the folder containing the Excel file:
    python 09_spearman_temporal_mitigation.py
"""

import os
import pandas as pd
import numpy as np
from scipy import stats

# ── paths ──────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "..", "Manual_Extraction_Paper2_Final Outcome_VS code.csv")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "09_spearman_temporal_mitigation_output.csv")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── load ───────────────────────────────────────────────────────────────────
df = pd.read_csv(DATA_FILE, header=2)
df = df.dropna(how="all").reset_index(drop=True)
df.columns = [str(c).strip() for c in df.columns]
df["GAQI"]     = pd.to_numeric(df["GAQI_Total (0-100)"], errors="coerce")
df["Year_n"]   = pd.to_numeric(df["Year"], errors="coerce")
df["MitCount"] = pd.to_numeric(df["Mitigation_Measures_Count2"], errors="coerce")

# ── define pairs ───────────────────────────────────────────────────────────
pairs = [
    {
        "label":       "Year vs GAQI",
        "x_col":       "Year_n",
        "x_name":      "Year of preparation",
        "expected_rho": 0.242,
        "expected_p":   0.15,
        "paper_str":    "rho = 0.24, p = 0.15 (n.s.)",
        "paper_section":"Section 3.8",
        "purpose":      "Temporal trend in assessment quality",
    },
    {
        "label":       "Mitigation count vs GAQI",
        "x_col":       "MitCount",
        "x_name":      "Mitigation-measure count",
        "expected_rho": 0.582,
        "expected_p":   0.001,
        "paper_str":    "rho = 0.58, p < 0.001",
        "paper_section":"Section 3.8",
        "purpose":      "Content-quality association",
    },
]

rows = []
for pair in pairs:
    sub = df[[pair["x_col"], "GAQI"]].dropna()
    rho,  p_s = stats.spearmanr(sub[pair["x_col"]], sub["GAQI"])
    r_p,  p_p = stats.pearsonr( sub[pair["x_col"]], sub["GAQI"])

    exp_rho = pair["expected_rho"]
    match   = abs(rho - exp_rho) < 0.002

    rows.append({
        "Test":                  "Spearman correlation",
        "Comparison":            pair["label"],
        "Purpose":               pair["purpose"],
        "Variable_X":            pair["x_name"],
        "Variable_Y":            "GAQI_Total (0-100)",
        "N":                     len(sub),
        "Spearman_rho":          round(rho, 3),
        "Spearman_p":            round(p_s, 4),
        "Spearman_p_display":    "< 0.001" if p_s < 0.001 else f"= {p_s:.4f}",
        "Significant_0.05":      p_s < 0.05,
        "Pearson_r":             round(r_p, 3),
        "Pearson_p":             round(p_p, 4),
        "Pearson_vs_Spearman":   f"Difference = {abs(rho-r_p):.3f}",
        "Expected_rho":          exp_rho,
        "Match_Paper":           match,
        "Paper_Section":         pair["paper_section"],
        "Reported_In_Paper":     pair["paper_str"],
    })

out = pd.DataFrame(rows)
out.to_csv(OUTPUT_FILE, index=False)

# ── console output ─────────────────────────────────────────────────────────
print("=" * 65)
print("09 — SPEARMAN CORRELATIONS: TEMPORAL & MITIGATION")
print("=" * 65)
for _, r in out.iterrows():
    print(f"\n  {r['Comparison']}")
    print(f"    N              : {r['N']}")
    print(f"    Spearman rho   : {r['Spearman_rho']}  (p {r['Spearman_p_display']})")
    print(f"    Pearson r      : {r['Pearson_r']}  (p = {r['Pearson_p']:.4f})")
    print(f"    Significant    : {r['Significant_0.05']}")
    print(f"    Paper reports  : {r['Reported_In_Paper']}")
    print(f"    Match paper    : {r['Match_Paper']}")
print(f"\nOutput saved to: {OUTPUT_FILE}")
