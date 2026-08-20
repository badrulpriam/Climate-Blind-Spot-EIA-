"""
01_data_verification.py
=======================
Purpose : Load the GAQI dataset and verify its structural integrity before
          any analysis is conducted.

Checks performed
----------------
1. Total number of reports (N = 38)
2. All 50 expected columns present
3. No missing values in the six GAQI dimension score columns
4. No missing values in the GAQI_Total column
5. Arithmetic check: D1 + D2 + D3 + D4 + D5 + D6 == GAQI_Total for every row
6. GAQI_Class values match the expected five categories

Paper reference : Methods section — instrument integrity
Output saved to : outputs/01_data_verification_output.csv

Run from the folder containing the Excel file:
    python 01_data_verification.py
"""

import os
import pandas as pd
import numpy as np

# ── paths ──────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "..", "Manual_Extraction_Paper2_Final Outcome_VS code.csv")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "01_data_verification_output.csv")
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
TOTAL_COL = "GAQI_Total (0-100)"
CLASS_COL = "GAQI_Class"
EXPECTED_CLASSES = {"Inadequate", "Poor", "Satisfactory", "Good", "Excellent"}

for c in DIMS + [TOTAL_COL]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# ── checks ─────────────────────────────────────────────────────────────────
results = []

# 1. Total N
n = len(df)
results.append({
    "Check": "Total reports (N)",
    "Expected": 38,
    "Observed": n,
    "Pass": n == 38,
    "Note": "Row count after dropping fully empty rows",
})

# 2. Total columns
ncols = len(df.columns)
results.append({
    "Check": "Total columns",
    "Expected": 50,
    "Observed": ncols,
    "Pass": ncols == 50,
    "Note": "Column count as per instrument design",
})

# 3. Missing values in dimension columns
for dim in DIMS:
    missing = df[dim].isna().sum()
    results.append({
        "Check": f"Missing values — {dim}",
        "Expected": 0,
        "Observed": missing,
        "Pass": missing == 0,
        "Note": "No dimension score should be missing",
    })

# 4. Missing values in GAQI_Total
missing_total = df[TOTAL_COL].isna().sum()
results.append({
    "Check": "Missing values — GAQI_Total",
    "Expected": 0,
    "Observed": missing_total,
    "Pass": missing_total == 0,
    "Note": "No composite score should be missing",
})

# 5. Arithmetic integrity: sum of dimensions == GAQI_Total
df["_computed_total"] = df[DIMS].sum(axis=1)
df["_diff"] = (df["_computed_total"] - df[TOTAL_COL]).abs()
mismatches = (df["_diff"] > 0.001).sum()
results.append({
    "Check": "Arithmetic integrity (D1+D2+D3+D4+D5+D6 == GAQI_Total)",
    "Expected": 0,
    "Observed": mismatches,
    "Pass": mismatches == 0,
    "Note": "All 38 rows must sum exactly to GAQI_Total",
})

# 6. GAQI_Class categories
observed_classes = set(df[CLASS_COL].dropna().unique())
unexpected = observed_classes - EXPECTED_CLASSES
results.append({
    "Check": "GAQI_Class — unexpected categories",
    "Expected": 0,
    "Observed": len(unexpected),
    "Pass": len(unexpected) == 0,
    "Note": f"Unexpected values if any: {unexpected if unexpected else 'None'}",
})

# ── compile output ─────────────────────────────────────────────────────────
out = pd.DataFrame(results)
out["Pass"] = out["Pass"].map({True: "PASS", False: "FAIL"})
out.insert(0, "Paper_Section", "Methods — data integrity")

# ── save ───────────────────────────────────────────────────────────────────
out.to_csv(OUTPUT_FILE, index=False)

# ── console summary ────────────────────────────────────────────────────────
print("=" * 65)
print("01 — DATA VERIFICATION")
print("=" * 65)
print(out[["Check", "Expected", "Observed", "Pass"]].to_string(index=False))
overall = "ALL CHECKS PASSED" if (out["Pass"] == "PASS").all() else "ONE OR MORE CHECKS FAILED"
print(f"\nOverall: {overall}")
print(f"Output saved to: {OUTPUT_FILE}")
