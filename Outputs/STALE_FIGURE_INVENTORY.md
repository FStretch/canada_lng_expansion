# Task B inventory — stale figures (before any edit)

Grep of the whole repository (md, py, txt, csv, both input workbooks including README/Chains sheets). Produced before any Task B edit.

## Specified superseded values

| Old value | Current | Hits | Action |
|---|---|---|---|
| 10,704.7 / 10,705 / ~10,700 | 9,558.2 Mt lifetime | **None** in md/py/xlsx. `Outputs/figure_data/mc_draws.csv` contains coincidental MC samples near 10,704 (e.g. draw 5855 full = 10704.679). Not a published figure. | Leave mc_draws. No text to update. |
| 272.0 / ~272 | 309.1 Mt in 2037 | **None** | None |
| 268.1 as unlabelled “annual emissions” | `life_average_annual_mt` | 268.1 appears only **with** the life-average label in `README.md` (L15, L27, L284), `Outputs/RESULTS_SUMMARY.md` (L10, L97). Related stale **label**: `src/figures_report.py` “40-year average” (comments, trajectory captions, fig 8 title) and fig 7 caption “40-year model lifecycle sum” (LNG bars are the calendar-panel sum). | Relabel to life-average / calendar-panel. Do not change 268.1. |
| roughly 16 / 5 / 80 | 18.5 / 5.6 / 75.9 | **None** of the old split. README L21, Data Inputs README row 24, RESULTS_SUMMARY L22, and `EXPECTED_TERRITORIAL_SHARE_PCT` in `build_results.py` L94 already 18.5 / 5.6 / 75.9. Assertion already present L888–894 (Task 4). | Keep assertion. Do not change the expected dict. |
| 200 GtCO2 | 170 / 525 / 1,055 | **None**. Parameters and README already GCB 2025. `canada_2030_overshoot_gap` = 200 is **MtCO2e** vs the 2030 target, not a GtCO2 carbon budget. | Leave the 200 Mt gap. Not the superseded budget. |
| 8,367 Mt proposed-export lifetime | recompute | **None**. Current proposed lifetime in RESULTS_SUMMARY L31 is **7,646.6 Mt**. | None to update. |

## Extra find (not in the search list; Inputs not edited)

`Inputs/Canada_LNG_Data_Inputs.xlsx` Chains sheet, export `applies_to`: **“45.4 mtpa active, 12.7 mtpa early stage”**. That is the pre-expansion 58.1 mtpa headline, not current 100.1 / 54.7 early. Flagged only. Workbook left untouched.

Chains export note “18 / 3 / 79 per cent” is the export-chain split (computed 18.0 / 3.4 / 78.6), not the old all-asset 16/5/80.

## External-circulation surfaces

These are the files a non-technical reader would see. Numbers on them **already match** 9,558.2 / 309.1 / 18.5–5.6–75.9 / GCB 170–525–1055:

- `README.md`
- `Outputs/RESULTS_SUMMARY.md`
- `Outputs/SLIDE_TABLES.xlsx` (regenerated)
- Figure **captions** in `src/figures_report.py` (except the “40-year average” wording)
- Data Inputs README row 24 (18.5 / 5.6 / 75.9)

**Still circulating under the old label** if fig 8 was already shared: PNG title “40-year average” (`fig08_electrification_canada_territorial.png`). Relabel on regenerate.

`Outputs/OIL_COMPARATOR_AUDIT.md`: no hits; left as a dated audit.

## Assertions

- Territorial split: **already present**, expected {CAN: 18.5, BUNK: 5.6, FOR: 75.9}. Unchanged.
- Lifetime 9,558.2 and peak 2037 / 309.1: **not yet asserted**. To be added. These are new locks, not silent updates of an existing expected value.
