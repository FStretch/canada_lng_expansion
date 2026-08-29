# Stale figure inventory

Regenerated 2026-08-29 by `python tools/stale_figure_inventory.py`, against the paper set locked as `EXPECTED_BUILD_OUT` in `build_results.py`.

The previous version of this file was a hand-written snapshot and had itself gone stale: it treated 9,558.2 Mt, 309.1 Mt and 18.5 / 5.6 / 75.9 as current, two scope changes after they stopped being so. This one is generated, so it can be re-run after any re-lock.

## Current locked values

| quantity | value |
|---|---|
| lifetime CO2e | **9,298.1 Mt** |
| lifetime CO2 only | **8,955.2 Mt (plus 11,505 kt CH4)** |
| peak | **298.2 Mt in 2037** |
| territorial CAN / BUNK / FOR | **18.1 / 3.2 / 78.7 %** |
| ECCC 2% damages | **C$4,073 bn** |
| committed | **1,869.5 Mt, C$749 bn** |
| committed plus advanced | **3,805.7 Mt, C$1,579 bn** |

## Superseded values, and where they still appear

| superseded | replaced by | when it moved | live hits | deliberate records |
|---|---|---|---|---|
| 9,558.2 Mt lifetime (all assets) | 9,298.1 Mt | export-scope filter, then route-scaled shipping | **none** | `build_results.py`, `Outputs/SCOPE_DIAGNOSTIC.md`, `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py` |
| 309.1 Mt peak (all assets) | 298.2 Mt in 2037 | export-scope filter, then route-scaled shipping | **none** | `build_results.py`, `Outputs/SCOPE_DIAGNOSTIC.md`, `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py` |
| 18.5 / 5.6 / 75.9 territorial | 18.1 / 3.2 / 78.7 | export-scope filter, then route-scaled shipping | **none** | `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py` |
| 9,315.3 Mt lifetime (export scope, flat shipping) | 9,298.1 Mt | Task 4, route-scaled shipping | **none** | `build_results.py`, `Outputs/BASELINE_2026-08-29.md`, `Outputs/SCOPE_DIAGNOSTIC.md`, `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py` · data series (not published text): `Outputs/figure_data/mc_draws.csv` |
| 298.7 Mt peak (flat shipping) | 298.2 Mt in 2037 | Task 4, route-scaled shipping | **none** | `build_results.py`, `Outputs/BASELINE_2026-08-29.md`, `Outputs/SCOPE_DIAGNOSTIC.md`, `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py` |
| 18.0 / 3.4 / 78.6 territorial | 18.1 / 3.2 / 78.7 | Task 4, route-scaled shipping | **none** | `Outputs/BASELINE_2026-08-29.md`, `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py`, `tools/update_data_inputs_readme_task4.py` |
| C$4,164bn ECCC 2% damages (whole CO2e at SC-CO2) | C$4,073bn | Task 3 per-gas pricing, then Task 4 | **none** | `Outputs/BASELINE_2026-08-29.md` · data series (not published text): `Outputs/figure_data/mc_draws.csv` |
| 258.9 Mt/yr life-average | 258.5 Mt/yr | Task 4, route-scaled shipping | **none** | `Outputs/BASELINE_2026-08-29.md`, `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py` |
| 10,704.7 Mt lifetime | 9,298.1 Mt | superseded before this task sequence | **none** | `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py` |
| 272.0 Mt peak | 298.2 Mt in 2037 | superseded before this task sequence | **none** | `Outputs/STALE_FIGURE_INVENTORY.md`, `tools/stale_figure_inventory.py` |

**No live hits.** Every remaining occurrence is a deliberate record of what a number used to be: the lock history comment in `build_results.py`, the baseline record, the change report, or this script's own value table. Monte Carlo draw files may contain coincidental samples near a superseded figure; those are data, not published text.

