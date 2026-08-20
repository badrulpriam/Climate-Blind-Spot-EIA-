"""
08_mann_whitney_group_comparisons.py
=====================================
Purpose : Test whether GAQI composite scores differ across three binary
          groupings: fuel class, financing source, and temporal era.

Tests performed (3 total)
--------------------------
1. Fossil-fuelled vs Renewable
   H0: No difference in GAQI between fossil and renewable projects
   Expected: U = 109, p = 0.89, rank-biserial r = -0.04

2. DFI / MDB named vs not named
   H0: No difference in GAQI between DFI-financed and other projects
   Expected: U = 156.5, p = 0.87

3. Pre-Paris (<=2015) vs Post-Paris (>=2016)
   H0: No difference in GAQI before and after Paris Agreement adoption
   Expected: U = 130.5, p = 0.35

Why Mann-Whitney U (not t-test)
---------------------------------
GAQI scores are significantly non-normal (Shapiro-Wilk p < 0.001). The
Mann-Whitney U test is the appropriate non-parametric equivalent of an
independent samples t-test.

Effect size
-----------
Rank-biserial correlation r = 1 - (2U / n1*n2)
Interpretation: |r| < 0.1 = negligible, 0.1-0.3 = small, 0.3-0.5 = medium,
                > 0.5 = large (Cohen, 1988)

Paper reference : Section 3.8 — determinants of assessment quality
Output saved to : outputs/08_mann_whitney_group_comparisons_output.csv

Run from the folder containing the Excel file:
    python 08_mann_whitney_group_comparisons.py
"""

import os
import pandas as pd
import numpy as np
from scipy import stats

# ── paths ──────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "..", "Manual_Extraction_Paper2_Final Outcome_VS code.csv")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "08_mann_whitney_group_comparisons_output.csv")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── load ───────────────────────────────────────────────────────────────────
df = pd.read_csv(DATA_FILE, header=2)
df = df.dropna(how="all").reset_index(drop=True)
df.columns = [str(c).strip() for c in df.columns]
df["GAQI"]   = pd.to_numeric(df["GAQI_Total (0-100)"], errors="coerce")
df["Year_n"] = pd.to_numeric(df["Year"], errors="coerce")

# ── group definitions ──────────────────────────────────────────────────────

# 1. Fossil vs Renewable
FOSSIL_TECHS  = ["Gas/LNG", "Coal", "HFO", "Dual Fuel(Gas/HSD)", "Gas/HSD"]
RENEW_TECHS   = ["Solar", "Solar & Wind"]
fossil = df[df["Technology"].isin(FOSSIL_TECHS)]["GAQI"].dropna()
renew  = df[df["Technology"].isin(RENEW_TECHS)]["GAQI"].dropna()

# 2. DFI / MDB named vs not
MDB_KEYWORDS = ["ADB", "Asian Development", "World Bank", "IFC",
                "International Finance", "AIIB", "Asian Infrastructure",
                "JICA", "Japan International", "IsDB", "Islamic Development",
                "US Exim", "IDCOL", "IPFF", "CDC", "DEG"]
df["Has_DFI"] = df["Donor"].apply(
    lambda d: any(k in str(d) for k in MDB_KEYWORDS))
dfi    = df[df["Has_DFI"]]["GAQI"].dropna()
no_dfi = df[~df["Has_DFI"]]["GAQI"].dropna()

# 3. Pre-Paris vs Post-Paris
pre  = df[df["Year_n"] <= 2015]["GAQI"].dropna()
post = df[df["Year_n"] >= 2016]["GAQI"].dropna()

# ── run tests ─────────────────────────────────────────────────────────────
def mwu_row(label, g1, g2, g1_name, g2_name, section, paper_report):
    U, p = stats.mannwhitneyu(g1, g2, alternative="two-sided")
    r_rb = 1 - (2 * U) / (len(g1) * len(g2))   # rank-biserial r
    return {
        "Comparison":           label,
        "Group_1":              g1_name,
        "Group_2":              g2_name,
        "n_Group1":             len(g1),
        "n_Group2":             len(g2),
        "Median_Group1":        round(g1.median(), 1),
        "Median_Group2":        round(g2.median(), 1),
        "U_statistic":          round(U, 1),
        "p_value":              round(p, 4),
        "p_value_display":      f"= {p:.4f}",
        "Rank_biserial_r":      round(r_rb, 3),
        "Effect_size_interp":   ("Negligible" if abs(r_rb) < 0.1
                                 else "Small" if abs(r_rb) < 0.3
                                 else "Medium" if abs(r_rb) < 0.5
                                 else "Large"),
        "Significant_0.05":     p < 0.05,
        "Conclusion":           "No significant difference" if p >= 0.05
                                else "Significant difference",
        "Paper_Section":        section,
        "Reported_In_Paper":    paper_report,
    }

rows = [
    mwu_row("Fossil vs Renewable",
            fossil, renew, "Fossil", "Renewable",
            "Section 3.8",
            "U = 109, p = 0.89, rank-biserial r = -0.04"),
    mwu_row("DFI named vs not named",
            dfi, no_dfi, "DFI_named", "No_DFI",
            "Section 3.8",
            "U = 156.5, p = 0.87"),
    mwu_row("Pre-Paris vs Post-Paris",
            pre, post, "Pre_Paris_<=2015", "Post_Paris_>=2016",
            "Section 3.8",
            "U = 130.5, p = 0.35"),
]

# add match flag against paper
EXPECTED_U = {"Fossil vs Renewable": 109, "DFI named vs not named": 156.5,
              "Pre-Paris vs Post-Paris": 130.5}
for r in rows:
    exp_u = EXPECTED_U[r["Comparison"]]
    r["Match_U"] = abs(r["U_statistic"] - exp_u) < 0.6

out = pd.DataFrame(rows)
out.to_csv(OUTPUT_FILE, index=False)

# ── console output ─────────────────────────────────────────────────────────
print("=" * 65)
print("08 — MANN-WHITNEY U: BINARY GROUP COMPARISONS")
print("=" * 65)
for _, r in out.iterrows():
    print(f"\n  {r['Comparison']}")
    print(f"    {r['Group_1']} (n={r['n_Group1']}, median={r['Median_Group1']})  vs  "
          f"{r['Group_2']} (n={r['n_Group2']}, median={r['Median_Group2']})")
    print(f"    U = {r['U_statistic']},  p {r['p_value_display']},  "
          f"rank-biserial r = {r['Rank_biserial_r']}  [{r['Effect_size_interp']}]")
    print(f"    Conclusion : {r['Conclusion']}")
    print(f"    Paper      : {r['Reported_In_Paper']}")
    print(f"    Match U    : {r['Match_U']}")
print(f"\nOutput saved to: {OUTPUT_FILE}")
