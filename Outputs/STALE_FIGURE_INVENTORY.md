# Stale figure inventory

Regenerated 2026-09-03 by `python tools/stale_figure_inventory.py`, against the paper set locked as `EXPECTED_BUILD_OUT` in `build_results.py`.

Generated, not hand-written. An earlier hand-written version of this file went stale itself, twice: it treated 9,558.2 Mt and 309.1 Mt as current after they had been superseded, and a later generated run still listed 9,298.1 Mt as current after Discovery LNG was returned to cancelled. Re-run this script after every re-lock; that is the only thing that keeps it honest.

## Current locked values

| quantity | value |
|---|---|
| lifetime CO2e | **7,162.0 Mt** |
| lifetime CO2 only | **6,895.6 Mt (plus 8,942 kt CH4)** |
| peak | **235.6 Mt in 2037** |
| territorial CAN / BUNK / FOR | **17.6 / 3.2 / 79.2 %** |
| ECCC 2% damages | **C$3,103 bn** |
| committed | **1,845.8 Mt, C$739 bn** |
| committed plus advanced | **3,757.5 Mt, C$1,559 bn** |
| export capacity | **80.1 mtpa across nine projects** |

## Superseded values, and where they still appear

| superseded | replaced by | when it moved | live hits | deliberate records |
|---|---|---|---|---|
| 9,558.2 Mt lifetime (all assets) | 9,298.1 Mt | export-scope filter, then route-scaled shipping | **none** | `build_results.py`, `Outputs/DECK_RECONCILIATION.md`, `Outputs/SCOPE_DIAGNOSTIC.md`, `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py` · data series (not published text): `Outputs/figure_data/mc_draws.csv` |
| 309.1 Mt peak (all assets) | 298.2 Mt in 2037 | export-scope filter, then route-scaled shipping | **none** | `build_results.py`, `Outputs/DECK_RECONCILIATION.md`, `Outputs/SCOPE_DIAGNOSTIC.md`, `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py` |
| 18.5 / 5.6 / 75.9 territorial | 18.1 / 3.2 / 78.7 | export-scope filter, then route-scaled shipping | **none** | `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py` |
| 9,315.3 Mt lifetime (export scope, flat shipping) | 9,298.1 Mt | Task 4, route-scaled shipping | **none** | `build_results.py`, `Outputs/BASELINE_2026-08-29.md`, `Outputs/CHANGE_REPORT_2026-08-29.md`, `Outputs/DECK_RECONCILIATION.md`, `Outputs/SCOPE_DIAGNOSTIC.md`, `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py` |
| 298.7 Mt peak (flat shipping) | 298.2 Mt in 2037 | Task 4, route-scaled shipping | **none** | `build_results.py`, `Outputs/BASELINE_2026-08-29.md`, `Outputs/CHANGE_REPORT_2026-08-29.md`, `Outputs/DECK_RECONCILIATION.md`, `Outputs/SCOPE_DIAGNOSTIC.md`, `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py` |
| 18.0 / 3.4 / 78.6 territorial | 18.1 / 3.2 / 78.7 | Task 4, route-scaled shipping | **none** | `Outputs/BASELINE_2026-08-29.md`, `Outputs/CHANGE_REPORT_2026-08-29.md`, `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py`, `tools/update_data_inputs_readme_task4.py` |
| C$4,164bn ECCC 2% damages (whole CO2e at SC-CO2) | C$4,073bn | Task 3 per-gas pricing, then Task 4 | **none** | `Outputs/BASELINE_2026-08-29.md`, `Outputs/DECK_RECONCILIATION.md` · data series (not published text): `Outputs/figure_data/mc_draws.csv` |
| 258.9 Mt/yr life-average | 258.5 Mt/yr | Task 4, route-scaled shipping | **none** | `Outputs/BASELINE_2026-08-29.md`, `Outputs/CHANGE_REPORT_2026-08-29.md`, `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py` |
| 10,704.7 Mt lifetime | 7,254.2 Mt | superseded before this task sequence | **none** | `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py` |
| 272.0 Mt peak | 238.6 Mt in 2037 | superseded before this task sequence | **none** | `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py` |
| 9,298.1 Mt lifetime (Discovery counted as early_proposed) | 7,254.2 Mt | Discovery returned to cancelled | **none** | `build_results.py`, `README.md`, `Outputs/CHANGE_REPORT_2026-08-29.md`, `Outputs/CHANGE_REPORT_2026-09-03.md`, `Outputs/DECK_RECONCILIATION.md`, `Outputs/SCOPE_DIAGNOSTIC.md`, `Outputs/SOURCING_AUDIT.md`, `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py` · data series (not published text): `Outputs/figure_data/mc_draws.csv` |
| 298.2 Mt peak (Discovery in) | 238.6 Mt in 2037 | Discovery returned to cancelled | **none** | `build_results.py`, `Outputs/CHANGE_REPORT_2026-08-29.md`, `Outputs/CHANGE_REPORT_2026-09-03.md`, `Outputs/DECK_RECONCILIATION.md`, `Outputs/SCOPE_DIAGNOSTIC.md`, `Outputs/SOURCING_AUDIT.md`, `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py` |
| 8,955.2 Mt CO2-only (Discovery in) | 6,987.7 Mt | Discovery returned to cancelled | **none** | `Outputs/CHANGE_REPORT_2026-08-29.md`, `Outputs/CHANGE_REPORT_2026-09-03.md`, `Outputs/DECK_RECONCILIATION.md`, `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py` |
| 18.1 / 3.2 / 78.7 territorial | 18.1 / 3.2 / 78.8 | Discovery returned to cancelled | **none** | `Outputs/CHANGE_REPORT_2026-08-29.md`, `Outputs/CHANGE_REPORT_2026-09-03.md`, `Outputs/DECK_RECONCILIATION.md`, `Outputs/SCOPE_DIAGNOSTIC.md`, `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py`, `tools/update_data_inputs_readme_task4.py` |
| C$4,073bn ECCC 2% damages (Discovery in) | C$3,143bn | Discovery returned to cancelled | **none** | `Outputs/CHANGE_REPORT_2026-08-29.md`, `Outputs/CHANGE_REPORT_2026-09-03.md`, `Outputs/DECK_RECONCILIATION.md`, `Outputs/SOURCING_AUDIT.md` · data series (not published text): `Outputs/figure_data/mc_draws.csv` |
| 258.5 Mt/yr life-average (Discovery in) | 207.4 Mt/yr | Discovery returned to cancelled | **none** | `Outputs/CHANGE_REPORT_2026-08-29.md`, `Outputs/CHANGE_REPORT_2026-09-03.md`, `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py` |
| 100.1 mtpa export capacity (ten projects) | 80.1 mtpa (nine projects) | Discovery returned to cancelled | **none** | `README.md`, `Outputs/BASELINE_2026-08-29.md`, `Outputs/CHANGE_REPORT_2026-08-29.md`, `Outputs/CHANGE_REPORT_2026-09-03.md`, `Outputs/DECK_RECONCILIATION.md`, `Outputs/SCOPE_DIAGNOSTIC.md`, `Outputs/SOURCING_AUDIT.md`, `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py`, `tools/update_chains_applies_to.py` |
| 11,505 kt CH4 (Discovery in) | 8,942 kt | Discovery returned to cancelled | **none** | `Outputs/CHANGE_REPORT_2026-08-29.md`, `Outputs/CHANGE_REPORT_2026-09-03.md`, `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py` · data series (not published text): `Outputs/figure_data/mc_draws.csv` |
| upstream 0.33 GWP20 (whole factor x1.5) | 0.428 (methane portion only) | GWP20 recomputed on the methane portion | **none** | `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py` |
| 7,254.2 Mt lifetime (regasification 0.04) | 7,215.3 Mt | regasification 0.04 -> 0.021 | **none** | `build_results.py`, `Outputs/CHANGE_REPORT_2026-09-03.md`, `Outputs/CHANGE_REPORT_2026-09-03b.md`, `Outputs/DECK_RECONCILIATION.md`, `Outputs/SOURCING_AUDIT.md`, `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py` · data series (not published text): `Outputs/figure_data/mc_draws.csv` |
| 238.6 Mt peak (regasification 0.04) | 237.3 Mt in 2037 | regasification 0.04 -> 0.021 | **none** | `build_results.py`, `Outputs/CHANGE_REPORT_2026-09-03.md`, `Outputs/CHANGE_REPORT_2026-09-03b.md`, `Outputs/DECK_RECONCILIATION.md`, `Outputs/SOURCING_AUDIT.md`, `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py` |
| 6,987.7 Mt CO2-only (regasification 0.04) | 6,948.8 Mt | regasification 0.04 -> 0.021 | **none** | `Outputs/CHANGE_REPORT_2026-09-03.md`, `Outputs/CHANGE_REPORT_2026-09-03b.md`, `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py` · data series (not published text): `Outputs/figure_data/mc_draws.csv` |
| 18.1 / 3.2 / 78.8 territorial | 18.2 / 3.2 / 78.6 | regasification 0.04 -> 0.021 (regas is FOR-tagged) | **none** | `Outputs/CHANGE_REPORT_2026-09-03.md`, `Outputs/CHANGE_REPORT_2026-09-03b.md`, `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py` |
| C$3,143bn ECCC 2% damages (regasification 0.04) | C$3,126bn | regasification 0.04 -> 0.021 | **none** | `Outputs/CHANGE_REPORT_2026-09-03.md`, `Outputs/CHANGE_REPORT_2026-09-03b.md`, `Outputs/DECK_RECONCILIATION.md`, `Outputs/SOURCING_AUDIT.md` · data series (not published text): `Outputs/figure_data/mc_draws.csv` |
| 207.4 Mt/yr life-average (regasification 0.04) | 206.3 Mt/yr | regasification 0.04 -> 0.021 | **none** | `Outputs/CHANGE_REPORT_2026-09-03.md`, `Outputs/CHANGE_REPORT_2026-09-03b.md`, `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py` |
| regasification central 0.04 (uncited) | 0.021 (Gan et al. 2024) | moved onto a cited value | **none** | `Outputs/CHANGE_REPORT_2026-09-03.md`, `Outputs/CHANGE_REPORT_2026-09-03b.md`, `Outputs/CITATIONS_WANTED.md`, `Outputs/SOURCING_AUDIT.md`, `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py` |
| combustion range low 2.50 (uncited) | 2.58 (IPCC 2006 uncertainty band) | moved onto a cited derivation | **none** | `Outputs/CHANGE_REPORT_2026-09-03.md`, `Outputs/SOURCING_AUDIT.md`, `tools/apply_found_citations.py` |
| 7,215.3 Mt lifetime (pipeline 0.10) | 7,162.0 Mt | pipeline 0.10 -> 0.074 | **none** | `build_results.py`, `Outputs/CHANGE_REPORT_2026-09-03b.md`, `Outputs/CHANGE_REPORT_2026-09-03c.md`, `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py` · data series (not published text): `Outputs/figure_data/mc_draws.csv` |
| 237.3 Mt peak (pipeline 0.10) | 235.6 Mt in 2037 | pipeline 0.10 -> 0.074 | **none** | - |
| 6,948.8 Mt CO2-only (pipeline 0.10) | 6,895.6 Mt | pipeline 0.10 -> 0.074 | **none** | `Outputs/CHANGE_REPORT_2026-09-03b.md`, `Outputs/CHANGE_REPORT_2026-09-03c.md`, `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py` · data series (not published text): `Outputs/figure_data/mc_draws.csv` |
| 18.2 / 3.2 / 78.6 territorial | 17.6 / 3.2 / 79.2 | pipeline 0.10 -> 0.074 (pipeline is CAN-tagged) | **none** | `Outputs/CHANGE_REPORT_2026-09-03b.md`, `Outputs/CHANGE_REPORT_2026-09-03c.md`, `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py` |
| C$3,126bn ECCC 2% damages (pipeline 0.10) | C$3,103bn | pipeline 0.10 -> 0.074 | **none** | - |
| 206.3 Mt/yr life-average (pipeline 0.10) | 204.7 Mt/yr | pipeline 0.10 -> 0.074 | **none** | - |
| pipeline central 0.10 (assumed) | 0.074 (Liu 2021 / CER 2022) | moved onto two converging cited routes | **none** | - |

**No live hits.** Every remaining occurrence is a deliberate record of what a number used to be: the lock history comment in `build_results.py`, the baseline record, the change report, or this script's own value table. Monte Carlo draw files may contain coincidental samples near a superseded figure; those are data, not published text.

