# Change report — 29 August 2026

Tasks 0 to 12 against the baseline recorded in `Outputs/BASELINE_2026-08-29.md`
(commit `3c680fc`). One commit per task. `python build_results.py` was run after
every task; 41 assertions pass and every run ends "No input file was modified
during the run."

**Only two tasks moved a published number.** Task 3 (methane priced at ECCC
SC-CH4) moved the damages. Task 4 (shipping scaled by route distance) moved the
physics. Tasks 5 to 12 changed no published figure: they lock, document,
add supplementary information, and tidy the deposit.

---

## 1. Headline numbers

Central case throughout, with the Monte Carlo 5th to 95th percentile in
brackets (10,000 draws, seed 20260828). "After all tasks" is identical to
"after Task 4" for every cell, because Tasks 5 to 12 moved nothing.

### Committed (operating + under construction, 3 assets)

| quantity | baseline | after Task 4 | after all tasks |
|---|---|---|---|
| Lifetime CO2e, Mt | 1,869.5 [1,800.2, 2,011.3] | 1,869.5 [1,800.2, 2,011.3] | **1,869.5** [1,800.2, 2,011.3] |
| Lifetime CO2-only, Mt | not computed | 1,799.6 [1,722.2, 1,917.6] | **1,799.6** [1,722.2, 1,917.6] |
| Peak, Mt (year) | not computed | 58.3 (2030) [56.2, 62.8] | **58.3** (2030) [56.2, 62.8] |
| CAN / BUNK / FOR, % | 18.0 / 3.4 / 78.6 | 18.0 / 3.4 / 78.6 | **18.0 / 3.4 / 78.6** |
| ECCC 2% damages, C$bn | 765.3 [737, 823] | 748.9 [719, 801] | **748.9** [719, 801] |

### Committed plus advanced (+ tier `advanced_proposed`, 5 assets)

| quantity | baseline | after Task 4 | after all tasks |
|---|---|---|---|
| Lifetime CO2e, Mt | 3,805.7 [3,641.4, 4,123.9] | 3,805.7 [3,641.4, 4,123.9] | **3,805.7** [3,641.4, 4,123.9] |
| Lifetime CO2-only, Mt | not computed | 3,663.5 [3,482.1, 3,933.1] | **3,663.5** [3,482.1, 3,933.1] |
| Peak, Mt (year) | not computed | 135.8 (2037) [130.7, 146.1] | **135.8** (2037) [130.7, 146.1] |
| CAN / BUNK / FOR, % | 18.0 / 3.4 / 78.6 | 18.0 / 3.4 / 78.6 | **18.0 / 3.4 / 78.6** |
| ECCC 2% damages, C$bn | not computed [1,546, 1,745] | 1,579.1 [1,509, 1,698] | **1,579.1** [1,509, 1,698] |

### Full buildout (10 export assets, 100.1 mtpa)

| quantity | baseline | after Task 4 | after all tasks |
|---|---|---|---|
| Lifetime CO2e, Mt | 9,315.3 [8,290.3, 10,752.6] | 9,298.1 [8,274.6, 10,727.0] | **9,298.1** [8,274.6, 10,727.0] |
| Lifetime CO2-only, Mt | not computed | 8,955.2 [7,914.4, 10,245.9] | **8,955.2** [7,914.4, 10,245.9] |
| Peak, Mt (year) | 298.7 (2037) [287.6, 321.3] | 298.2 (2037) [287.1, 320.5] | **298.2** (2037) [287.1, 320.5] |
| CAN / BUNK / FOR, % | 18.0 / 3.4 / 78.6 | 18.1 / 3.2 / 78.7 | **18.1 / 3.2 / 78.7** |
| ECCC 2% damages, C$bn | 4,163.9 [3,625, 4,915] | 4,072.8 [3,529, 4,785] | **4,072.8** [3,529, 4,785] |

Notes on the "not computed" cells. Lifetime CO2-only did not exist before
Task 1. `committed_plus_advanced` existed in the Monte Carlo but not in the
central-case outputs before Task 5, so it had a Monte Carlo interval and no
central point. Per-build-out peaks were not computed centrally before Task 5.

Other headline movements, full buildout:

| quantity | baseline | after all tasks |
|---|---|---|
| `life_average_annual_mt` | 258.9 Mt/yr | 258.5 Mt/yr |
| Lifetime CH4 mass | not computed | 11,505 kt |
| Share of 1.5 °C budget (170 GtCO2) | 5.5% (CO2e vs CO2) | **5.3%** (CO2 vs CO2, like for like) |
| Share of 1.7 °C budget (525 GtCO2) | 1.8% | 1.7% |
| Share of 2.0 °C budget (1,055 GtCO2) | 0.9% | 0.8% |
| Implied blended SC price | C$447/t | C$438/t |
| Methane share of the damage bill | not priced separately | 1.7% (C$71 bn) |

---

## 2. Assertions re-locked

Only Task 4 moved an existing locked value. Everything else here is new.

| constant / assertion | old | new | task | why |
|---|---|---|---|---|
| `EXPECTED_LIFETIME_MT` | 9315.3 | **9298.1** | 4 | shipping scaled by route distance per asset |
| `EXPECTED_PEAK_MT` | 298.7 | **298.2** | 4 | same |
| `EXPECTED_PEAK_YEAR` | 2037 | 2037 (unchanged) | 4 | the two Atlantic assets do not set the peak |
| `EXPECTED_TERRITORIAL_SHARE_PCT` | CAN 18.0 / BUNK 3.4 / FOR 78.6 | **CAN 18.1 / BUNK 3.2 / FOR 78.7** | 4 | shipping is the only BUNK stage, so a shorter Atlantic haul cuts the bunkers share |
| `EXPECTED_BUILD_OUT` | did not exist | committed 1869.5 / 1799.6 / 58.3 (2030) / 749; committed_plus_advanced 3805.7 / 3663.5 / 135.8 (2037) / 1579; full 9298.1 / 8955.2 / 298.2 (2037) / 4073 | 5 | nothing was locked at build-out grain before |
| `EXPECTED_PAPER_SET_SHA256` | did not exist | `9e33c691…72a0946` over `Outputs/paper_set_locked.csv` | 12 | any published digit moving now fails the run |
| `_validate_loss_damage`: `0.0 < methane_overstatement_pct < 0.10` | present | **removed** | 3 | the quantity it bounded no longer exists; methane is priced at SC-CH4, not bounded |
| `_validate_loss_damage`: methane replacements | did not exist | `0 < eccc_ch4_damage_share < 0.05`; `old_treatment_cad > published`; `0 < old_treatment_delta_pct < 0.10`; `co2_damage + ch4_damage = total` | 3 | per-gas pricing needs per-gas checks |
| `_validate_loss_damage`: `0.01 < methane_share_of_co2e < 0.08` | present, 2.7% | present, **3.7%** | 1 | bound unchanged; the value moved because shipping methane slip joined the split |
| `_validate_loss_damage`: `0.0015 < canada_share < 0.0020` | present | **present, deliberately not relaxed** | 11 | no by-pulse country table exists, so no 2020-pulse share can replace it |
| Burke share provenance | not asserted | pulse year = 1990; `P_dam_FD` = 0.41; `P_dam_HD` = 0.33 | 11 | new |
| SC-CH4 schedule coverage | asserted for SC-CO2 only | asserted for SC-CH4 too, failing loudly rather than extrapolating or falling back | 3 | new |
| Panel gas identity | did not exist | `emissions_mtco2e = co2_mt + ch4_derived_co2e_mt` to 1e-9 per row | 1 | new |
| Monte Carlo CO2-only kernel | did not exist | MC CO2-only kernel must reproduce the published panel | 3 | new |
| Paper-set consistency | did not exist | `full` row must equal `EXPECTED_LIFETIME_MT` / `EXPECTED_PEAK_MT` / `EXPECTED_PEAK_YEAR`; p5 ≤ median ≤ p95 | 5 | the two locks cannot drift apart |
| Sensitivity central rows | did not exist | uniform-life, feedgas and drive sensitivities each assert their central row reproduces the published panel | 6, 7, 8 | an SI switch must not touch the central case |
| SI asset table | did not exist | 10 rows; lifetimes sum to the panel total; shares sum to 100% | 9 | new |
| Liquefaction = 0.29 | asserted | **asserted, unchanged** | 8 | the drive sensitivity is defined against it and refuses to run if it moves |

`EXPECTED_EXPORT_TOTAL` (100.1), `EXPECTED_EXPORT_BY_CALC`, `EXPECTED_ADVANCED_EXPORT`
(26.0) and `EXPECTED_EARLY_EXPORT` (54.7) were not touched: no capacity changed.

---

## 3. New parameters and register columns

### Parameters sheet, `Canada_LNG_Data_Inputs.xlsx`

| parameter | value | unit | type | source |
|---|---|---|---|---|
| `liquefaction_electric_drive_gas_generation` | 0.156 | tCO2e per t LNG | cited | BC Environmental Assessment Office, Assessment Report for Ksi Lisims LNG, 7 Aug 2025, Canadian Impact Assessment Registry doc 163192E, pp. 847–848, Alternative Case (gas-fired power barges). `https://iaac-aeic.gc.ca/050/documents/p82797/163192E.pdf` |
| `liquefaction_electric_drive_grid` | 0.021 | tCO2e per t LNG | cited | Same document and pages, Base Case (grid supply) |

Both rows carry the boundary note that these are **facility total intensity
including marine sources**, not liquefaction alone, so comparison against the
0.29 liquefaction-stage factor is approximate. Sensitivity only; the central
0.29 and its assertion are untouched.

### Derived Fields sheet, `Canada_LNG_Data_Inputs.xlsx`

| field | unit | type | derivation |
|---|---|---|---|
| `upstream_ch4_derived_co2e` | tCO2e per t LNG | derived | `max(scenario upstream − inventory_as_reported × (1 − upstream_ch4_share), 0)`. At central: 0.25 − 0.22 × 0.7 = 0.096 |
| `shipping_ch4_derived_co2e_share` | fraction | derived | `1 − 1 / lng_carrier_methane_slip_uplift` = 1 − 1/1.44 = 0.3056; 0.0367 tCO2e/t at the 0.12 factor |
| `ch4_mass_kt` | kt CH4 | derived | `ch4_derived_co2e_mt / gwp100_ch4 × 1000`. Undefined for `near_term_methane_gwp20` |

### Asset Register columns

| column | type | populated from |
|---|---|---|
| `feedgas_basin` | sourced | Per row. Six BC assets: "Western Canada Sedimentary Basin (northeast British Columbia)", from TC Energy's Coastal GasLink page, the Province of BC's Coastal GasLink page and the GEM wiki pages for CGL / PRGT / FortisBC. Fermeuse: "Jeanne d'Arc Basin (offshore Newfoundland)", from the proponent statement already cited for its capacity. Kino Aski, Discovery, Kanata: "not available" |
| `feedgas_basin_note` | sourced | Delivering pipeline, and what the cited sources do and do not say about the producing formation |
| `gem_status_verbatim` | sourced | Each row's own `gem_wiki_url`, quoted exactly. Not normalised, not reconciled with the register's own status |
| `gem_status_date` | sourced | The GEM page's last-modified date when read. Not a GEM-asserted "status as of" date |

Also filled: `route_distance_nm` = 3,800 for `discovery_t1t4` and `kanata_lng`,
both blank before, on the cited CAPP / Oxford Institute for Energy Studies
west-coast-Canada basis, with Asset Sources cells stating it is a coast-level
basis rather than a port-specific sailing distance.

Every new column has an Asset Sources cell on **every** register row, a Field
Definitions entry, and Data Gaps rows where a value could not be sourced. All
workbook edits were made by documented one-off scripts under `tools/`; the model
still never writes to `Inputs/`.

---

## 4. What could not be sourced or computed

Stated plainly rather than filled.

1. **No producing formation for the British Columbia feedgas.** The brief
   expected "Montney" for the Kitimat cluster. TC Energy's own Coastal GasLink
   page, the Province of BC's Coastal GasLink page, the CER market snapshot
   cited in the LNG Canada row and the GEM wiki all describe the supply only as
   "northeastern British Columbia" and none names a formation. Northeast BC
   production is overwhelmingly Montney, but that is an inference, not a
   citation. `feedgas_basin` therefore stops at the WCSB, the note on each row
   says so, and a Data Gaps row records it.

2. **No route distance for Western Canadian gas to the Quebec north shore.**
   No such route is defined. The CER's pipeline profile for the TransCanada
   Canadian Mainline publishes only a 14,123 km total regulated system length
   across all segments including deactivated and abandoned ones — not a route
   distance — and Baie-Comeau is not on the Mainline in any case. Task 7 Case A
   therefore runs as an explicit ×3 and ×5 multiplier band against the 670 km
   Coastal GasLink calibration, labelled illustrative, with the gap in Data Gaps.

3. **No country-level Burke damages table by pulse year.** Checked 29 August
   2026 across the GitHub default branch and the tagged v1.1 release archived on
   Zenodo. Both shipped country-level files are the **1990** pulse — the script
   that writes them opens `subset(total_damages_1gtco2_cd, emitter == 1990)` and
   their `year_cat` values are damage-accumulation windows, not pulse years. The
   by-pulse files shipped are global totals with no country column. The
   country-by-emitter-year intermediate is not shipped. So no 2020-pulse share
   is reported and the `0.0015 < share < 0.0020` assertion is not relaxed. The
   1990-pulse share is reported with `P_dam_FD` = 0.41 attached.

4. **No port-specific sailing distance for Discovery or Kanata.** Both take the
   coast-level 3,800 nm figure. Prince Rupert is nearer north Asia and Campbell
   River further, so the two errors point in opposite directions. Recorded in
   Data Gaps.

5. **No United States upstream factor.** Task 7 Case B changes the territorial
   tag only and leaves intensities untouched. Appalachian methane intensities
   are generally higher than northeast BC ones, so the factor is probably too
   low under that case, but no substitute is invented.

6. **No Canadian offshore upstream factor.** Fermeuse's feedgas is offshore
   associated gas from the Jeanne d'Arc Basin. The pipeline factor overstates
   its stage (there is essentially no onshore haul); the direction of the
   upstream bias is **not determined**. Limitations text only, no factor change.

7. **The GWP20 scenario cannot be rebuilt from the CH4-mass route.** The two
   routes differ by +4.3%, well over the 0.1% tolerance, so they are reported
   rather than forced together. The workbook's 0.33 is `inventory × 1.5`, the
   whole factor scaled, not a GWP20 re-weighting of the methane portion (which
   would give upstream 0.420); and the scenario does not touch shipping. Related:
   **no pipeline methane portion is defined anywhere in the workbook**, so the
   README's claim that the GWP20 uplift applies to "upstream and pipeline" is
   not implemented in code. Recorded, not invented.

8. **Pipeline fugitive methane is not split.** The workbook carries one pipeline
   factor with no methane share behind it, so a small amount of methane sits
   inside the CO2-only total. This is the main residual caveat on the
   carbon-budget share, alongside non-CO2 gases other than CH4 (N2O,
   refrigerants) not being counted anywhere in the model.

9. **The two drive-type figures are not like-for-like with 0.29.** They are
   facility totals including marine sources; 0.29 is a liquefaction-stage
   factor. The comparison is approximate and is labelled so in the parameter
   rows and every output.

10. **The Ksi Lisims assessment PDF was not re-read at page level.** The URL
    resolves but the document exceeds the fetch size limit, so the two values
    and their page reference were taken as supplied rather than independently
    verified against pp. 847–848.

11. **FINDING, recorded and not acted on: GEM now lists Discovery LNG as
    cancelled.** Its GEM page reads `"cancelled (inferred 4 y)"` as of the
    29 August 2026 edit; the register classes Discovery as `proposed` /
    `early_proposed`. Discovery is 2,043.9 MtCO2e, **22.0% of the headline
    lifetime**. The verbatim status is in the register, a high-priority Data
    Gaps row is open, the run prints it as a FINDING, and both the SI table and
    RESULTS_SUMMARY flag it. `calc_group` and `tier` were **not** changed: that
    is a scope decision for the authors, not a side effect of a data-capture
    task, and it would move every locked number. **It should be resolved before
    publication.**

---

## 5. Sensitivity results

### Task 6 — uniform 40-year life, no licence-end stop (SI only)

| build-out | case | lifetime CO2e Mt | lifetime CO2-only Mt | peak Mt (year) | ECCC 2% C$bn |
|---|---|---|---|---|---|
| committed | central | 1,869.5 | 1,799.6 | 58.3 (2030) | 749 |
| committed | uniform 40 yr | 2,279.8 | 2,194.6 | 58.3 (2030) | 955 |
| committed plus advanced | central | 3,805.7 | 3,663.5 | 135.8 (2037) | 1,579 |
| committed plus advanced | uniform 40 yr | 4,936.9 | 4,752.4 | 135.8 (2037) | 2,157 |
| full | central | 9,298.1 | 8,955.2 | 298.2 (2037) | 4,073 |
| full | uniform 40 yr | 10,509.6 | 10,121.5 | 298.2 (2037) | 4,693 |

Full buildout **+13.0%**. Peaks are unchanged in all three: the licence stops
bite after 2037, not at the peak. Committed-to-full ratio, both ways: central
full/committed **4.97** and committed **20.1%** of full; uniform **4.61** and
**21.7%**. `Outputs/figure_data/sens_uniform_life.csv`.

### Task 7 — Kino Aski feedgas (SI only)

| case | pipeline tCO2e/t | Kino Aski lifetime Mt | headline lifetime Mt | headline CAN Mt | headline CAN share |
|---|---|---|---|---|---|
| Central (as published) | 0.10 | 1,521.7 | 9,298.1 | 1,679.4 | 18.1% |
| A, Western Canadian, pipeline ×3 (illustrative, 2,010 km, no cited route) | 0.30 | 1,608.1 | 9,384.5 | 1,765.7 | 18.8% |
| A, Western Canadian, pipeline ×5 (illustrative, 3,350 km, no cited route) | 0.50 | 1,694.4 | 9,470.8 | 1,852.1 | 19.6% |
| B, United States supply (intensities unchanged, upstream and pipeline tagged FOR) | 0.10 | 1,521.7 | 9,298.1 | 1,528.3 | 16.4% |

Case B leaves the total unchanged and moves 151.1 Mt out of the
Canada-territorial column. Which country's gas Kino Aski burns matters more to
the territorial answer than how far it travels.
`Outputs/figure_data/sens_kino_aski_feedgas.csv`.

### Task 8 — liquefaction drive type (SI only)

Applied to Ksi Lisims (sourced) and Cedar (assumption: same floating-LNG
electric-drive class). Liquefaction is CAN-tagged, so the whole delta lands in
Canada territorial.

| case | liquefaction tCO2e/t | headline lifetime Mt | Δ Mt | headline CAN Mt | Δ CAN Mt |
|---|---|---|---|---|---|
| Central, gas turbine, every terminal | 0.290 | 9,298.1 | — | 1,679.4 | — |
| Alternative Case, gas-fired power barges | 0.156 | 9,244.3 | −53.8 | 1,625.6 | −53.8 |
| Base Case, grid supply | 0.021 | 9,190.2 | −107.9 | 1,571.5 | −107.9 |

`Outputs/figure_data/sens_liquefaction_drive.csv`.

### Task 11 — Burke pulse year and P_dam

| item | value | pulse year | note |
|---|---|---|---|
| Canada share, future window (`share_FD_%`) | **0.17%** | 1990 | the figure applied to Burke damages |
| Canada share, historical window (`share_HD_%`) | 0.20% | 1990 | for contrast |
| **`P_dam_FD`** | **0.41** | 1990 | share of Burke draws in which Canada's damage from that pulse is positive |
| `P_dam_HD` | 0.33 | 1990 | same, historical window |
| 2020-pulse share | **not computable** | — | no country-level damages table by pulse year exists in the replication package |

Only 41% of draws put Canada in net loss at all, against 0.98 for the United
States and China. The 0.17% is a mean over a distribution that is not reliably
signed for Canada and should be read with `P_dam_FD` attached.
`Outputs/figure_data/burke_canada_share.csv`.

---

## 6. New and regenerated outputs

`Outputs/paper_set_locked.csv` (hashed), `Outputs/si_table_assets.csv`,
`Outputs/figure_data/`: `paper_set.csv`, `gas_split.csv`,
`sens_uniform_life.csv`, `sens_uniform_life_by_asset.csv`,
`sens_kino_aski_feedgas.csv`, `sens_liquefaction_drive.csv`,
`sens_liquefaction_drive_by_asset.csv`, `burke_canada_share.csv`.
Results workbook gains `Gas Split`, `Paper Set` and `SI Assets` sheets.
`Outputs/STALE_FIGURE_INVENTORY.md` is now generated by
`tools/stale_figure_inventory.py` and reports 0 live hits.
`Outputs/SCOPE_DIAGNOSTIC.md` carries a superseded-snapshot banner.
`requirements.txt` is pinned exactly; `CITATION.cff` added.
