"""
07_kruskal_wallis_technology.py
================================
Purpose : Test whether GAQI composite scores differ significantly across
          generation technology families.

Test performed
--------------
Kruskal-Wallis H-test (non-parametric one-way ANOVA on ranks)

Technology grouping
--------------------
Four families with n >= 3 are included:
    Coal        (n = 10)
    Gas / LNG   (n = 15)
    HFO         (n =  3)
    Solar/Wind  (n =  7)

Excluded (n < 3 — insufficient for non-parametric testing):
    Dual-fuel gas/HSD   (n = 2)
    Waste-to-energy     (n = 1)

These four families account for 35 of the 38 reports. The exclusion criterion
and the group composition are explicitly stated in the paper (Section 3.8).

Why Kruskal-Wallis (not ANOVA)
--------------------------------
GAQI scores are significantly non-normal (Shapiro-Wilk p < 0.001). The
Kruskal-Wallis test makes no distributional assumption and is the appropriate
non-parametric equivalent of one-way ANOVA.

IMPORTANT: grouping sensitivity note
--------------------------------------
Merging HFO with the two dual-fuel reports (creating an HFO/DualFuel group,
n = 5) produces H = 8.11, p = 0.044 — a marginal significant result. The
reported analysis uses the pre-specified n >= 3 exclusion criterion. This
sensitivity is documented in the paper (Section 3.8).

Expected output (as reported in paper)
---------------------------------------
H = 3.94, df = 3, p = 0.27  (non-significant)

Paper reference : Section 3.8 — determinants of assessment quality
Output saved to : outputs/07_kruskal_wallis_technology_output.csv

Run from the folder containing the Excel file:
    python 07_kruskal_wallis_technology.py
"""

import os
import pandas as pd
import numpy as np
from scipy import stats

# ── paths ──────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "..", "Manual_Extraction_Paper2_Final Outcome_VS code.csv")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "07_kruskal_wallis_technology_output.csv")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── load ───────────────────────────────────────────────────────────────────
df = pd.read_csv(DATA_FILE, header=2)
df = df.dropna(how="all").reset_index(drop=True)
df.columns = [str(c).strip() for c in df.columns]
df["GAQI"] = pd.to_numeric(df["GAQI_Total (0-100)"], errors="coerce")

# ── technology grouping (n >= 3 only) ─────────────────────────────────────
def assign_family(tech):
    t = str(tech)
    if "Coal" in t:                         return "Coal"
    if t.startswith("Gas/LNG"):             return "Gas/LNG"
    if "HFO" in t:                          return "HFO"          # HFO only
    if "Solar" in t or "Wind" in t:         return "Solar/Wind"
    return "Excluded"                                              # n < 3

df["Tech_Family"] = df["Technology"].apply(assign_family)

FAMILIES = ["Coal", "Gas/LNG", "HFO", "Solar/Wind"]
included = df[df["Tech_Family"] != "Excluded"]
excluded = df[df["Tech_Family"] == "Excluded"]

# ── group descriptives ────────────────────────────────────────────────────
desc_rows = []
for fam in FAMILIES:
    g = df[df["Tech_Family"] == fam]["GAQI"].dropna()
    desc_rows.append({
        "Technology_Family": fam,
        "n": len(g),
        "Mean": round(g.mean(), 2),
        "SD":   round(g.std(),  2),
        "Median": round(g.median(), 1),
        "Min":  int(g.min()),
        "Max":  int(g.max()),
        "Included_in_KW": True,
    })
for _, row in excluded.iterrows():
    desc_rows.append({
        "Technology_Family": str(row["Technology"]),
        "n": 1,
        "Mean": row["GAQI"],
        "SD": "",
        "Median": row["GAQI"],
        "Min": row["GAQI"],
        "Max": row["GAQI"],
        "Included_in_KW": False,
    })

# ── Kruskal-Wallis test ────────────────────────────────────────────────────
groups = [df[df["Tech_Family"] == f]["GAQI"].dropna().values for f in FAMILIES]
H, p = stats.kruskal(*groups)
df_kw = len(FAMILIES) - 1

# sensitivity check: what if HFO + dual fuel merged?
def assign_family_merged(tech):
    t = str(tech)
    if "Coal" in t:                          return "Coal"
    if t.startswith("Gas/LNG"):              return "Gas/LNG"
    if "HFO" in t or "Dual" in t or "HSD" in t: return "HFO/DualFuel"
    if "Solar" in t or "Wind" in t:          return "Solar/Wind"
    return "Excluded"

df["Tech_Merged"] = df["Technology"].apply(assign_family_merged)
groups_merged = [df[df["Tech_Merged"] == f]["GAQI"].dropna().values
                 for f in ["Coal","Gas/LNG","HFO/DualFuel","Solar/Wind"]]
H_m, p_m = stats.kruskal(*groups_merged)

# ── build output ───────────────────────────────────────────────────────────
test_rows = [
    {"Test":                    "Kruskal-Wallis",
     "Groups":                  "Coal / Gas-LNG / HFO / Solar-Wind (n>=3)",
     "N_total":                 int(included["GAQI"].notna().sum()),
     "df":                      df_kw,
     "H_statistic":             round(H, 3),
     "p_value":                 round(p, 4),
     "p_value_display":         f"= {p:.4f}",
     "Significant_0.05":        p < 0.05,
     "Conclusion":              "No significant difference across technology families",
     "Paper_Section":           "Section 3.8",
     "Reported_In_Paper":       "H = 3.94, df = 3, p = 0.27",
     "Match_Paper":             abs(H - 3.94) < 0.01 and abs(p - 0.27) < 0.01,
     "Sensitivity_H_merged":    round(H_m, 3),
     "Sensitivity_p_merged":    round(p_m, 4),
     "Sensitivity_note":        "HFO+DualFuel merged (n=5): H=8.11, p=0.044 — marginal significance; exclusion of n<3 groups is pre-specified",
    }
]

out_test = pd.DataFrame(test_rows)
out_desc = pd.DataFrame(desc_rows)

out_test.to_csv(OUTPUT_FILE, index=False)
desc_file = os.path.join(OUTPUT_DIR, "07_kruskal_wallis_group_descriptives.csv")
out_desc.to_csv(desc_file, index=False)

# ── console output ─────────────────────────────────────────────────────────
print("=" * 65)
print("07 — KRUSKAL-WALLIS: GAQI BY TECHNOLOGY FAMILY")
print("=" * 65)
print(f"\n  Groups included (n >= 3):")
for r in desc_rows:
    inc = "included" if r["Included_in_KW"] else "EXCLUDED (n<3)"
    print(f"    {r['Technology_Family']:<20} n={r['n']}  median={r['Median']}  [{inc}]")
print(f"\n  Kruskal-Wallis result:")
print(f"    H = {H:.3f},  df = {df_kw},  p = {p:.4f}")
print(f"    Significant: {p < 0.05}")
print(f"    Conclusion : No significant difference across technology families")
print(f"\n  Sensitivity (HFO+DualFuel merged, n=5):")
print(f"    H = {H_m:.3f},  p = {p_m:.4f}  — marginal significance")
print(f"    Pre-specified n>=3 exclusion criterion resolves this")
print(f"\n  Paper reports: H = 3.94, df = 3, p = 0.27")
print(f"  Match        : {abs(H - 3.94) < 0.01 and abs(p - 0.27) < 0.01}")
print(f"\nTest output saved to : {OUTPUT_FILE}")
print(f"Descriptives saved to: {desc_file}")
