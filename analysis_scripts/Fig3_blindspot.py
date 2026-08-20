"""
Fig3_blindspot.py
=================
Purpose : Generate Figure 3 for the manuscript:
          
Figure content
--------------
Panel (a): Stacked horizontal bar chart showing depth of GHG treatment for
           Scope 1, Scope 2, and Scope 3 emissions.
Panel (b): Stacked horizontal bar chart showing depth of GHG treatment across
           the three project lifecycle phases (Construction, Operation,
           Decommissioning).

Categories shown: Quantified / Qualitative only / Not addressed / Stated as zero
Percentage annotations: rounds to nearest integer (standard for figure labels).

Caption note added: percentages rounded to nearest integer; precise 1dp values
are reported in the Results section text.

Output
------
outputs/Fig3_blindspot.png  (300 DPI, journal-ready)

Run from the folder containing the Excel file:
    python Fig3_blindspot.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
matplotlib.rcParams['font.family'] = 'serif'
matplotlib.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']

# ── paths ──────────────────────────────────────────────────────────────────
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
DATA_FILE   = os.path.join(SCRIPT_DIR, "..", "Manual_Extraction_Paper2_Final Outcome_VS code.csv")
OUTPUT_DIR  = os.path.join(SCRIPT_DIR, "outputs")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "Fig3_blindspot.png")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── load ───────────────────────────────────────────────────────────────────
df = pd.read_csv(DATA_FILE, header=2)
df = df.dropna(how="all").reset_index(drop=True)
df.columns = [str(c).strip() for c in df.columns]
N = len(df)

# ── colour palette ─────────────────────────────────────────────────────────
C_Q    = "#D55E00"   # Quantified
C_QL   = "#E69F00"   # Qualitative only
C_NS   = "#FABF8F"   # Not addressed
C_ZERO = "#009E73"   # Stated as zero

# ── helper: get status counts for one column ──────────────────────────────
def get_counts(col):
    s = df[col].astype(str).str.strip()
    return [
        (s == "Quantified").sum(),
        (s == "Qualitative").sum(),
        (s == "Not Stated").sum(),
        (s == "Zero").sum(),
    ]

# ── data ───────────────────────────────────────────────────────────────────
SCOPE_COLS  = ["Scope1_Status", "Scope2_Status", "Scope3_Status"]
SCOPE_LBLS  = [
    "Scope 1\n(direct emissions)",
    "Scope 2\n(purchased energy)",
    "Scope 3\n(value chain)",
]
LIFE_COLS   = ["Construction_Status", "Operation_Status", "Decommission_Status"]
LIFE_LBLS   = ["Construction", "Operation", "Decommissioning"]

# verify totals sum to N for each column
for col in SCOPE_COLS + LIFE_COLS:
    counts = get_counts(col)
    total  = sum(counts)
    assert total == N, f"{col}: counts sum to {total}, expected {N}"

# ── global style ───────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":    "serif",
    "font.serif":     ["Times New Roman", "DejaVu Serif"],
    "font.size":      13,
    "axes.linewidth": 0.8,
    "figure.dpi":     300,
    "savefig.dpi":    300,
    "axes.edgecolor": "#333",
    "xtick.color":    "#333",
    "ytick.color":    "#333",
})

# ── figure layout ──────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))

CAT_LABELS = ["Quantified", "Qualitative only", "Not addressed", "Stated as zero"]
CAT_COLS   = [C_Q, C_QL, C_NS, C_ZERO]


def draw_stacked(ax, cols, row_labels, title):
    data  = np.array([get_counts(c) for c in cols])   # shape (n_rows, 4)
    ypos  = np.arange(len(cols))[::-1]                 # top-to-bottom

    left = np.zeros(len(cols))
    for j, (cat, col) in enumerate(zip(CAT_LABELS, CAT_COLS)):
        vals = data[:, j]
        ax.barh(ypos, vals, left=left,
                color=col, edgecolor="white", height=0.62, label=cat)
        # label inside bar if segment is wide enough
        for yi, v, l in zip(ypos, vals, left):
            if v > 0:
                text_col = "white" if col in [C_Q, C_ZERO] else "#222222"
                ax.text(l + v / 2, yi, str(int(v)),
                        ha="center", va="center",
                        fontsize=12, color=text_col, fontweight="bold")
        left += vals

    ax.set_yticks(ypos)
    ax.set_yticklabels(row_labels, fontsize=14)
    ax.set_xlim(0, N)
    ax.set_xlabel(f"Number of reports (N = {N})", fontsize=14)
    ax.tick_params(axis='x', labelsize=14)
    ax.set_title(title, fontweight="bold", loc="left", fontsize=14)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)

    # percentage-quantified annotation (integer rounding — standard for figures)
    for yi, col in zip(ypos, cols):
        q   = get_counts(col)[0]
        pct = round(100 * q / N, 1)
        ax.text(N + 0.5, yi, f"{'0' if pct == 0 else f'{pct:.1f}'}% quant.",
                va="center", fontsize=12, color="#000000")


draw_stacked(axes[0], SCOPE_COLS, SCOPE_LBLS, "(a) Emission-scope coverage")
draw_stacked(axes[1], LIFE_COLS,  LIFE_LBLS,  "(b) Lifecycle-phase coverage")

# shared legend at bottom
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels,
           loc="lower center", ncol=4,
           frameon=False, fontsize=12,
           bbox_to_anchor=(0.5, -0.04))

plt.tight_layout(rect=[0, 0.03, 1, 1])
plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight')
plt.close()

print(f"Figure 3 saved to: {OUTPUT_FILE}")
print("  Scope counts verified:")
for col, lbl in zip(SCOPE_COLS, ["S1","S2","S3"]):
    c = get_counts(col)
    print(f"    {lbl}: Q={c[0]}, Qual={c[1]}, NS={c[2]}, Zero={c[3]}")
print("  Lifecycle counts verified:")
for col, lbl in zip(LIFE_COLS, ["Con","Op","Dec"]):
    c = get_counts(col)
    print(f"    {lbl}: Q={c[0]}, Qual={c[1]}, NS={c[2]}")
print("  Note: figure % annotations use integer rounding (standard for figures).")
print("        Precise 1dp values are in the Results section text.")
