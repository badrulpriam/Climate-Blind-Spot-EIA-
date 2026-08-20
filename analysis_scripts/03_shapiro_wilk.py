"""
03_shapiro_wilk.py
==================
Purpose : Test whether GAQI composite scores follow a normal distribution.

Test performed
--------------
Shapiro-Wilk test on GAQI_Total (0-100)

Justification for use
---------------------
The Shapiro-Wilk test is the recommended normality test for small samples
(n < 50). With N = 38 it is more powerful than the Kolmogorov-Smirnov test.
A significant result (p < 0.05) confirms non-normality and justifies the use
of non-parametric tests throughout the analysis (Kruskal-Wallis, Mann-Whitney
U, and Spearman correlations).

Expected output (as reported in paper)
---------------------------------------
W = 0.880, p < 0.001
Conclusion: GAQI scores are significantly non-normal

Paper reference : Methods — justification for non-parametric test selection
                  Section 3.2 — instrument behaviour
Output saved to : outputs/03_shapiro_wilk_output.csv

Run from the folder containing the Excel file:
    python 03_shapiro_wilk.py
"""

import os
import pandas as pd
import numpy as np
from scipy import stats

# ── paths ──────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "..", "Manual_Extraction_Paper2_Final Outcome_VS code.csv")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "03_shapiro_wilk_output.csv")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── load ───────────────────────────────────────────────────────────────────
df = pd.read_csv(DATA_FILE, header=2)
df = df.dropna(how="all").reset_index(drop=True)
df.columns = [str(c).strip() for c in df.columns]
df["GAQI"] = pd.to_numeric(df["GAQI_Total (0-100)"], errors="coerce")
gaqi = df["GAQI"].dropna()

# ── test ───────────────────────────────────────────────────────────────────
W, p_value = stats.shapiro(gaqi)
skewness   = stats.skew(gaqi)
kurt       = stats.kurtosis(gaqi)       # excess kurtosis (normal = 0)

# significance at alpha = 0.05
significant = p_value < 0.05
conclusion = "Non-normal distribution confirmed — use non-parametric tests" \
             if significant else \
             "Cannot reject normality — parametric tests may be appropriate"

# ── build output ───────────────────────────────────────────────────────────
rows = [
    {"Test":              "Shapiro-Wilk",
     "Variable":          "GAQI_Total (0-100)",
     "N":                 int(gaqi.notna().sum()),
     "Statistic_Label":   "W",
     "Statistic_Value":   round(W, 4),
     "p_value":           round(p_value, 4),
     "p_value_display":   "< 0.001" if p_value < 0.001 else f"= {p_value:.4f}",
     "Significant_0.05":  significant,
     "Skewness":          round(skewness, 3),
     "Excess_Kurtosis":   round(kurt, 3),
     "Conclusion":        conclusion,
     "Paper_Section":     "Methods / Section 3.2",
     "Reported_In_Paper": "W = 0.880, p < 0.001",
     "Match_Paper":       abs(W - 0.880) < 0.001 and p_value < 0.001,
    }
]

out = pd.DataFrame(rows)
out.to_csv(OUTPUT_FILE, index=False)

# ── console output ─────────────────────────────────────────────────────────
print("=" * 65)
print("03 — SHAPIRO-WILK NORMALITY TEST")
print("=" * 65)
print(f"  Variable       : GAQI_Total (0-100)")
print(f"  N              : {int(gaqi.notna().sum())}")
print(f"  W statistic    : {W:.4f}")
print(f"  p-value        : {p_value:.6f}  (reported as < 0.001)")
print(f"  Skewness       : {skewness:.3f}")
print(f"  Excess kurtosis: {kurt:.3f}")
print(f"  Significant    : {significant}")
print(f"  Conclusion     : {conclusion}")
print(f"\n  Paper reports  : W = 0.880, p < 0.001")
print(f"  Match          : {abs(W - 0.880) < 0.001 and p_value < 0.001}")
print(f"\nOutput saved to: {OUTPUT_FILE}")
