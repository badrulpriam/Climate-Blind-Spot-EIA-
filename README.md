# GAQI Analysis Scripts

Analysis and figure-generation pipeline for the manuscript *"The Climate
Blind Spot: A Systematic Assessment of GHG Evaluation Quality in
Bangladesh's Energy Infrastructure EIAs."*

All scripts read from the single source dataset in this folder and write
their results to `analysis_scripts/outputs/`.

## Data

Scripts expect `Manual_Extraction_Paper2_Final Outcome_VS code.csv` (manually
extracted GAQI scoring data, N = 38 EIA reports, header on row 3) in this
folder. The file is **not included in this repository** — it is submitted to
the journal as a supplementary file. Place a copy here before running any
script.

## Requirements

- Python 3
- `pandas`, `numpy`, `matplotlib`, `scipy` (statistical tests use `scipy.stats`)

Install with:

```
pip install -r requirements.txt
```

Run each script from the `analysis_scripts/` folder (so the relative path to
the CSV resolves correctly):

```
cd analysis_scripts
python 01_data_verification.py
```

## Statistical analysis scripts

| Script | Purpose | Output |
|---|---|---|
| `01_data_verification.py` | Verifies dataset integrity: row count, expected columns, no missing dimension/total scores, D1–D6 sum to GAQI_Total, GAQI_Class categories valid. | `01_data_verification_output.csv` |
| `02_descriptive_statistics.py` | Descriptive statistics (mean, SD, median, range, etc.) for the Results section. | `02_descriptive_statistics_output.csv` |
| `03_shapiro_wilk.py` | Shapiro–Wilk test of normality for GAQI composite scores. | `03_shapiro_wilk_output.csv` |
| `04_cronbach_alpha_raw.py` | Raw Cronbach's alpha for the six-dimension GAQI instrument. | `04_cronbach_alpha_raw_output.csv`, `04_cronbach_alpha_raw_item_variances.csv` |
| `05_cronbach_alpha_standardised.py` | Standardised Cronbach's alpha for the six-dimension GAQI instrument. | `05_cronbach_alpha_standardised_output.csv`, `05_inter_item_correlation_matrix.csv` |
| `06_spearman_dimensions_convergent.py` | Spearman correlations between each GAQI dimension and the composite score; convergent validity vs. total GHG mention count. | `06_spearman_dimensions_convergent_output.csv` |
| `07_kruskal_wallis_technology.py` | Kruskal–Wallis test of GAQI score differences across generation technology families. | `07_kruskal_wallis_technology_output.csv`, `07_kruskal_wallis_group_descriptives.csv` |
| `08_mann_whitney_group_comparisons.py` | Mann–Whitney U tests of GAQI score differences across fuel class, financing source, and temporal era. | `08_mann_whitney_group_comparisons_output.csv` |
| `09_spearman_temporal_mitigation.py` | Spearman correlations for the temporal trend in assessment quality and mitigation-measure count vs. quality. | `09_spearman_temporal_mitigation_output.csv` |

Scripts are numbered in the order they should be run and correspond to the
order statistics are reported in the manuscript's Results section.

## Figure scripts

| Script | Figure content | Output |
|---|---|---|
| `Fig1_distribution.py` | (a) Histogram of GAQI composite scores with quality bands, mean/median lines. (b) Horizontal bar chart of report counts per quality class. | `Fig1_distribution.png` |
| `Fig2_dimensions.py` | Bar chart of mean attainment per GAQI dimension (% of maximum), colour-coded by severity, with 50% reference line. | `Fig2_dimensions.png` |
| `Fig3_blindspot.py` | (a) Stacked bar chart of GHG treatment depth by emission scope (1/2/3). (b) Same, by project lifecycle phase. | `Fig3_blindspot.png` |
| `Fig4_tech_temporal.py` | (a) Boxplot of GAQI score by generation technology (Kruskal–Wallis). (b) Scatter of GAQI score vs. report year with OLS trend (Spearman), Paris Agreement marker. | `Fig4_tech_temporal.png` |

All figures are saved at 300 DPI, serif font (Times New Roman / DejaVu
Serif fallback), styled for direct use in the manuscript.

## Outputs

`analysis_scripts/outputs/` contains every CSV and PNG produced by the
scripts above. Re-running a script overwrites its corresponding output
file(s).
