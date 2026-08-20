"""
05_cronbach_alpha_standardised.py
==================================
Purpose : Compute the standardised Cronbach's alpha for the six-dimension
          GAQI instrument.

Formula used
------------
Standardised alpha (based on average inter-item correlation):

    alpha_std = (k * mean_r) / (1 + (k - 1) * mean_r)

where
    k      = number of items (6 dimensions)
    mean_r = mean of all unique pairwise Pearson correlations among items
             (upper triangle of the k x k correlation matrix, k*(k-1)/2 pairs)

Why standardised alpha is preferred here
-----------------------------------------
The six GAQI dimensions have different maximum scores (10, 20, 20, 15, 20, 15).
Raw alpha is sensitive to scale differences between items. Standardised alpha
corrects for this by operating on the inter-item correlation matrix rather than
the raw covariance matrix. It is therefore the more appropriate reliability
estimate for a composite index with heterogeneous item scales.

Expected output (as reported in paper)
---------------------------------------
Standardised alpha = 0.867
Mean inter-item r  = 0.520

Paper reference : Section 3.2 — internal consistency of the GAQI instrument
Output saved to : outputs/05_cronbach_alpha_standardised_output.csv

Run from the folder containing the Excel file:
    python 05_cronbach_alpha_standardised.py
"""

import os
import pandas as pd
import numpy as np

# ── paths ──────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "..", "Manual_Extraction_Paper2_Final Outcome_VS code.csv")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "05_cronbach_alpha_standardised_output.csv")
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
corr_matrix = X.corr()                                    # k x k Pearson corr
upper_tri   = corr_matrix.values[np.triu_indices(k, 1)]  # upper triangle only
mean_r      = upper_tri.mean()
alpha_std   = (k * mean_r) / (1 + (k - 1) * mean_r)

def interpret(a):
    if a >= 0.90: return "Excellent"
    if a >= 0.80: return "Good"
    if a >= 0.70: return "Acceptable"
    if a >= 0.60: return "Questionable"
    return "Unacceptable"

# ── build output ───────────────────────────────────────────────────────────
summary_rows = [
    {"Metric":             "Standardised Cronbach's alpha",
     "Value":              round(alpha_std, 3),
     "Mean_inter_item_r":  round(mean_r, 3),
     "N_pairs":            len(upper_tri),
     "N_reports":          N,
     "k_dimensions":       k,
     "Interpretation":     interpret(alpha_std),
     "Paper_Section":      "Section 3.2",
     "Reported_In_Paper":  "standardised alpha = 0.867; mean inter-item r = 0.520",
     "Match_Alpha":        abs(alpha_std - 0.867) < 0.001,
     "Match_MeanR":        abs(mean_r - 0.520) < 0.001,
    }
]

# full inter-item correlation matrix as separate file
corr_out = corr_matrix.round(3).reset_index()
corr_out.columns = ["Dimension"] + list(corr_matrix.columns)

out_summary = pd.DataFrame(summary_rows)
out_summary.to_csv(OUTPUT_FILE, index=False)

corr_file = os.path.join(OUTPUT_DIR, "05_inter_item_correlation_matrix.csv")
corr_out.to_csv(corr_file, index=False)

# ── console output ─────────────────────────────────────────────────────────
print("=" * 65)
print("05 — CRONBACH'S ALPHA (STANDARDISED)")
print("=" * 65)
print(f"  N reports          : {N}")
print(f"  k dimensions       : {k}")
print(f"  Unique pairs       : {len(upper_tri)}")
print(f"  Mean inter-item r  : {mean_r:.4f}")
print(f"  Standardised alpha : {alpha_std:.4f}")
print(f"  Interpretation     : {interpret(alpha_std)}")
print(f"\n  Paper reports      : standardised alpha = 0.867; mean r = 0.520")
print(f"  Match alpha        : {abs(alpha_std - 0.867) < 0.001}")
print(f"  Match mean r       : {abs(mean_r - 0.520) < 0.001}")
print(f"\n  Inter-item correlation matrix:")
print(corr_matrix.round(3).to_string())
print(f"\nSummary saved to      : {OUTPUT_FILE}")
print(f"Corr matrix saved to  : {corr_file}")
