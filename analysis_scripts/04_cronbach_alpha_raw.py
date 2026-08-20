"""
04_cronbach_alpha_raw.py
========================
Purpose : Compute the raw Cronbach's alpha for the six-dimension GAQI
          instrument.

Formula used
------------
Raw alpha (Cronbach 1951):

    alpha = (k / (k-1)) * (1 - sum(var_i) / var_total)

where
    k         = number of items (6 dimensions)
    var_i     = variance of item i (ddof = 1)
    var_total = variance of the summed composite (ddof = 1)

Note: "raw" alpha uses the actual (unstandardised) variances of the items.
Because the six GAQI dimensions have different maximum scores (10, 20, 20, 15,
20, 15), raw alpha is influenced by scale differences; see
05_cronbach_alpha_standardised.py for the scale-adjusted version.

Interpretation benchmarks (George & Mallery, 2003)
---------------------------------------------------
alpha >= 0.90 : Excellent
alpha >= 0.80 : Good
alpha >= 0.70 : Acceptable
alpha >= 0.60 : Questionable
alpha <  0.60 : Unacceptable

Expected output (as reported in paper)
---------------------------------------
Raw alpha = 0.846  -> interpretation: Good

Paper reference : Section 3.2 — internal consistency of the GAQI instrument
Output saved to : outputs/04_cronbach_alpha_raw_output.csv

Run from the folder containing the Excel file:
    python 04_cronbach_alpha_raw.py
"""

import os
import pandas as pd
import numpy as np

# ── paths ──────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "..", "Manual_Extraction_Paper2_Final Outcome_VS code.csv")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "04_cronbach_alpha_raw_output.csv")
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
for c in DIMS:
    df[c] = pd.to_numeric(df[c], errors="coerce")

X = df[DIMS].dropna()
N = len(X)
k = len(DIMS)

# ── compute ────────────────────────────────────────────────────────────────
var_items = X.var(axis=0, ddof=1)         # variance of each dimension
var_total = X.sum(axis=1).var(ddof=1)     # variance of composite sum
alpha_raw = (k / (k - 1)) * (1 - var_items.sum() / var_total)

# interpretation
def interpret(a):
    if a >= 0.90: return "Excellent"
    if a >= 0.80: return "Good"
    if a >= 0.70: return "Acceptable"
    if a >= 0.60: return "Questionable"
    return "Unacceptable"

# ── build output ───────────────────────────────────────────────────────────
summary_rows = [
    {"Metric":           "Raw Cronbach's alpha",
     "Value":            round(alpha_raw, 3),
     "N_reports":        N,
     "k_dimensions":     k,
     "Interpretation":   interpret(alpha_raw),
     "Paper_Section":    "Section 3.2",
     "Reported_In_Paper":"alpha = 0.846",
     "Match_Paper":      abs(alpha_raw - 0.846) < 0.001,
    }
]

item_rows = []
for dim, v in var_items.items():
    item_rows.append({"Dimension": dim, "Variance_ddof1": round(v, 4),
                      "Note": "Item variance used in raw-alpha formula"})

out_summary = pd.DataFrame(summary_rows)
out_items   = pd.DataFrame(item_rows)
out_items["Composite_Variance"] = round(var_total, 4)

# save
out_summary.to_csv(OUTPUT_FILE, index=False)
out_items_file = os.path.join(OUTPUT_DIR, "04_cronbach_alpha_raw_item_variances.csv")
out_items.to_csv(out_items_file, index=False)

# ── console output ─────────────────────────────────────────────────────────
print("=" * 65)
print("04 — CRONBACH'S ALPHA (RAW)")
print("=" * 65)
print(f"  N reports      : {N}")
print(f"  k dimensions   : {k}")
print(f"  Sum of item var: {var_items.sum():.4f}")
print(f"  Composite var  : {var_total:.4f}")
print(f"  Raw alpha      : {alpha_raw:.4f}")
print(f"  Interpretation : {interpret(alpha_raw)}")
print(f"\n  Paper reports  : alpha = 0.846")
print(f"  Match          : {abs(alpha_raw - 0.846) < 0.001}")
print(f"\n  Item variances:")
for dim, v in var_items.items():
    print(f"    {dim}: {v:.4f}")
print(f"\nSummary saved to  : {OUTPUT_FILE}")
print(f"Item vars saved to: {out_items_file}")
