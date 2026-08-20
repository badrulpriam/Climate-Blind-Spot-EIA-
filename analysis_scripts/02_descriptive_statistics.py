"""
02_descriptive_statistics.py
============================
Purpose : Compute all descriptive statistics reported in the Results section.

Statistics produced
-------------------
A. GAQI composite — mean, SD, median, Q1, Q3, IQR, min, max
B. GAQI classification — count and % per quality band
C. Six dimension scores — mean, SD, median, min, max, % of maximum attainable
D. Scope coverage — count per status category (Quantified / Qualitative /
   Not Stated / Zero) for Scope 1, 2, 3
E. Lifecycle coverage — count per status category for Construction,
   Operation, Decommissioning
F. Binary reporting-element completeness — count and % Yes for 13 elements
G. Corpus composition — technology, fuel class, temporal era, financier

Paper reference : Sections 3.1, 3.3, 3.4, 3.5, 3.6, 3.7
Output saved to : outputs/02_descriptive_statistics_output.csv

Run from the folder containing the Excel file:
    python 02_descriptive_statistics.py
"""

import os
import pandas as pd
import numpy as np

# ── paths ──────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "..", "Manual_Extraction_Paper2_Final Outcome_VS code.csv")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "02_descriptive_statistics_output.csv")
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
DIM_MAX = [10, 20, 20, 15, 20, 15]
DIM_LABELS = ["D1_Presence", "D2_Scopes", "D3_Methodology",
              "D4_Lifecycle", "D5_Quantification", "D6_Policy"]

TOTAL_COL = "GAQI_Total (0-100)"
N = len(df)

for c in DIMS + [TOTAL_COL]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

df["Year_n"] = pd.to_numeric(df["Year"], errors="coerce")

rows = []  # collector

# ── A. GAQI composite ──────────────────────────────────────────────────────
g = df[TOTAL_COL]
for stat, val in [
    ("Mean",   round(g.mean(), 2)),
    ("SD",     round(g.std(),  2)),
    ("Median", round(g.median(), 1)),
    ("Q1 (25th percentile)", round(g.quantile(0.25), 2)),
    ("Q3 (75th percentile)", round(g.quantile(0.75), 2)),
    ("IQR",    round(g.quantile(0.75) - g.quantile(0.25), 2)),
    ("Min",    int(g.min())),
    ("Max",    int(g.max())),
    ("N",      int(g.notna().sum())),
]:
    rows.append({"Block": "A — GAQI Composite", "Statistic": stat,
                 "Value": val, "n": N, "Pct_of_N": "",
                 "Paper_Section": "Section 3.3",
                 "Reported_In_Paper": "mean 48.3 (SD 21.9); median 55.5; IQR 24.8–67.5; range 12–81"})

# ── B. Classification ──────────────────────────────────────────────────────
class_order = ["Excellent", "Good", "Satisfactory", "Poor", "Inadequate"]
for cls in class_order:
    n_cls = (df["GAQI_Class"] == cls).sum()
    rows.append({"Block": "B — GAQI Classification", "Statistic": cls,
                 "Value": n_cls, "n": N,
                 "Pct_of_N": round(100 * n_cls / N, 1),
                 "Paper_Section": "Section 3.3",
                 "Reported_In_Paper": f"{cls}: n and %"})
# combined bands
for label, cats in [("Good + Excellent", ["Good","Excellent"]),
                    ("Inadequate + Poor", ["Inadequate","Poor"])]:
    n_c = df["GAQI_Class"].isin(cats).sum()
    rows.append({"Block": "B — GAQI Classification", "Statistic": label,
                 "Value": n_c, "n": N, "Pct_of_N": round(100*n_c/N,1),
                 "Paper_Section": "Section 3.3", "Reported_In_Paper": f"{label}: combined"})

# ── C. Dimension scores ────────────────────────────────────────────────────
for dim, mx, lbl in zip(DIMS, DIM_MAX, DIM_LABELS):
    s = df[dim]
    rows.append({"Block": "C — Dimension Descriptives", "Statistic": lbl,
                 "Value": (f"mean={s.mean():.2f} SD={s.std():.2f} "
                           f"median={s.median():.1f} min={s.min():.0f} max={s.max():.0f} "
                           f"pct_of_max={100*s.mean()/mx:.1f}%"),
                 "n": N, "Pct_of_N": round(100*s.mean()/mx, 1),
                 "Paper_Section": "Section 3.4",
                 "Reported_In_Paper": f"{lbl}: mean and % of max"})

# ── D. Scope coverage ──────────────────────────────────────────────────────
scope_cols = {"Scope 1": "Scope1_Status",
              "Scope 2": "Scope2_Status",
              "Scope 3": "Scope3_Status"}
for scope_lbl, col in scope_cols.items():
    s = df[col].astype(str).str.strip()
    for cat in ["Quantified", "Qualitative", "Not Stated", "Zero"]:
        n_cat = (s == cat).sum()
        rows.append({"Block": "D — Scope Coverage", "Statistic": f"{scope_lbl} — {cat}",
                     "Value": n_cat, "n": N, "Pct_of_N": round(100*n_cat/N, 1),
                     "Paper_Section": "Section 3.5",
                     "Reported_In_Paper": f"{scope_lbl} {cat} count and %"})

# ── E. Lifecycle coverage ──────────────────────────────────────────────────
life_cols = {"Construction": "Construction_Status",
             "Operation":    "Operation_Status",
             "Decommission": "Decommission_Status"}
for phase_lbl, col in life_cols.items():
    s = df[col].astype(str).str.strip()
    for cat in ["Quantified", "Qualitative", "Not Stated"]:
        n_cat = (s == cat).sum()
        rows.append({"Block": "E — Lifecycle Coverage", "Statistic": f"{phase_lbl} — {cat}",
                     "Value": n_cat, "n": N, "Pct_of_N": round(100*n_cat/N, 1),
                     "Paper_Section": "Section 3.5",
                     "Reported_In_Paper": f"{phase_lbl} {cat} count and %"})

# operational tunnel vision
op_q = df["Operation_Status"].astype(str).str.strip() == "Quantified"
con_q = df["Construction_Status"].astype(str).str.strip() == "Quantified"
dec_q = df["Decommission_Status"].astype(str).str.strip() == "Quantified"
op28 = df[op_q]
rows.append({"Block": "E — Lifecycle Coverage",
             "Statistic": "Of 28 quantifying Operation — also quantify Construction",
             "Value": (op28["Construction_Status"].astype(str).str.strip()=="Quantified").sum(),
             "n": op_q.sum(), "Pct_of_N": "",
             "Paper_Section": "Section 3.5", "Reported_In_Paper": "3 of 28"})
rows.append({"Block": "E — Lifecycle Coverage",
             "Statistic": "Of 28 quantifying Operation — also quantify Decommission",
             "Value": (op28["Decommission_Status"].astype(str).str.strip()=="Quantified").sum(),
             "n": op_q.sum(), "Pct_of_N": "",
             "Paper_Section": "Section 3.5", "Reported_In_Paper": "0 of 28"})

# ── F. Reporting completeness ──────────────────────────────────────────────
binary_items = {
    "GHG mentioned anywhere":          "GHG_Mentioned (Y/N)",
    "Dedicated GHG chapter":           "Dedicated_GHG_Chapter (Y/N)",
    "GHG-specific sub-sections":       "Sub-Chapters/Sections_with_GHG (Y/N)",
    "Any GHG quantified":              "GHG_Quantified (Y/N)",
    "Annual emissions stated":         "Annual_Emissions_Stated (Y/N)",
    "Lifetime emissions stated":       "Lifetime_Emissions_Stated (Y/N)",
    "Gas-species breakdown provided":  "Gas_Breakdown_Provided (Y/N)",
    "Protocol / tool named":           "Protocol_Named (Y/N)",
    "Emission factors provided":       "EF_Provided (Y/N)",
    "Activity data disclosed":         "Activity_Data_Provided (Y/N)",
    "National policy named":           "National_Policy_Named (Y/N)",
    "NDC mentioned":                   "NDC_Mentioned (Y/N)",
    "NDC contribution quantified":     "Quantified_National_Contribution (Y/N)",
}
for label, col in binary_items.items():
    n_yes = (df[col].astype(str).str.strip() == "Yes").sum()
    rows.append({"Block": "F — Reporting Completeness", "Statistic": label,
                 "Value": n_yes, "n": N, "Pct_of_N": round(100*n_yes/N, 1),
                 "Paper_Section": "Sections 3.6 / 3.7",
                 "Reported_In_Paper": f"{label}: n and %"})

# unit consistency
stated26 = df[df["Annual_Emissions_Stated (Y/N)"].astype(str).str.strip()=="Yes"]
co2e = stated26["Annual_tCO2_Value"].astype(str).str.lower().str.contains("co2eq|co2e").sum()
rows.append({"Block": "F — Reporting Completeness",
             "Statistic": "CO2-equivalent units used (of 26 stating annual figure)",
             "Value": co2e, "n": len(stated26), "Pct_of_N": round(100*co2e/len(stated26),1),
             "Paper_Section": "Section 3.6",
             "Reported_In_Paper": "8 of 26 (30.8%)"})

# internal contradictions
n_conflict = df["Notes_and_Flags"].astype(str).str.contains(
    "CONFLICT|CONTRADICTION|Contradict|conflicting", regex=True).sum()
rows.append({"Block": "F — Reporting Completeness",
             "Statistic": "Reports with internal contradiction flagged",
             "Value": n_conflict, "n": N, "Pct_of_N": round(100*n_conflict/N,1),
             "Paper_Section": "Section 3.6", "Reported_In_Paper": "12 (31.6%)"})

# CDM references
n_cdm = df["Remarks"].astype(str).str.upper().str.contains("CDM").sum()
rows.append({"Block": "F — Reporting Completeness",
             "Statistic": "Reports invoking CDM",
             "Value": n_cdm, "n": N, "Pct_of_N": round(100*n_cdm/N,1),
             "Paper_Section": "Section 3.7", "Reported_In_Paper": "15 (39.5%)"})

# ── G. Corpus composition ──────────────────────────────────────────────────
for tech, count in df["Technology"].value_counts().items():
    rows.append({"Block": "G — Corpus Composition", "Statistic": f"Technology: {tech}",
                 "Value": count, "n": N, "Pct_of_N": round(100*count/N,1),
                 "Paper_Section": "Section 3.1", "Reported_In_Paper": "Table 1"})

yr = df["Year_n"].dropna()
pre  = (yr <= 2015).sum()
post = (yr >= 2016).sum()
rows.append({"Block": "G — Corpus Composition", "Statistic": "Pre-Paris (<=2015)",
             "Value": pre, "n": len(yr), "Pct_of_N": round(100*pre/len(yr),1),
             "Paper_Section": "Section 3.1", "Reported_In_Paper": "14 (37.8%)"})
rows.append({"Block": "G — Corpus Composition", "Statistic": "Post-Paris (>=2016)",
             "Value": post, "n": len(yr), "Pct_of_N": round(100*post/len(yr),1),
             "Paper_Section": "Section 3.1", "Reported_In_Paper": "23 (62.2%)"})

# ── save ───────────────────────────────────────────────────────────────────
out = pd.DataFrame(rows)
out.to_csv(OUTPUT_FILE, index=False)

# ── console summary ────────────────────────────────────────────────────────
print("=" * 65)
print("02 — DESCRIPTIVE STATISTICS")
print("=" * 65)
for block in out["Block"].unique():
    sub = out[out["Block"] == block]
    print(f"\n{block}")
    print(sub[["Statistic","Value","n","Pct_of_N"]].to_string(index=False))
print(f"\nOutput saved to: {OUTPUT_FILE}")
