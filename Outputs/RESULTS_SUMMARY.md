# Canada LNG lifecycle emissions — review summary

Default scenario: `measurement_central`. Run at 2026-08-21 15:47 UTC. Numbers to one decimal. Inputs read-only. `calc_group` from `Asset Register:calc_group`.

Deck-facing tables (one sheet per table, 1-decimal): `Outputs/SLIDE_TABLES.xlsx`. Send that workbook to the PPT chat.

## 1. Headline

- **Annual total:** 272.0 MtCO2e/yr
- **Lifecycle total:** 10704.7 MtCO2e (excludes legacy facilities)
- **Headline capacity (export chain only):** 100.1 mtpa (liquefaction; not summed with import regasification or other chains)

| chain | mtpa |
|---|---|
| export | 100.1 |
| bunkering | 3.4 |
| domestic | 0.3 |
| import | 7.5 |

- **Scope 1+2:** 49.0 MtCO2e/yr (18.0%)  |  **Scope 3:** 223.0 MtCO2e/yr (82.0%)
- **Territorial:** CAN 50.3 (18.5%)  |  BUNK 15.2 (5.6%)  |  FOR 206.5 (75.9%)

## 2. By group

| calc_group | export mtpa | Annual Mt/yr | Lifecycle Mt | CAN / BUNK / FOR Mt/yr |
|---|---|---|---|---|
| operating | 14.0 | 43.3 | 1705.0 | 9.0 / 2.0 / 32.4 |
| under_construction | 5.4 | 15.8 | 632.3 | 2.8 / 0.5 / 12.4 |
| proposed | 80.7 | 212.9 | 8367.4 | 38.4 / 12.7 / 161.7 |

Capacity by chain within each calc_group (not summed across chains):

| calc_group | export | bunkering | domestic | import |
|---|---|---|---|---|
| operating | 14.0 | 0.2 | 0.3 | 7.5 |
| under_construction | 5.4 | 0.0 | 0.0 | 0.0 |
| proposed | 80.7 | 3.1 | 0.0 | 0.0 |

### Proposed: advanced vs early (tier split)

| tier | chain scope | mtpa | Annual Mt/yr | CAN / BUNK / FOR |
|---|---|---|---|---|
| advanced_proposed | export | 26.0 | 66.4 | 12.0 / 2.2 / 52.2 |
| advanced_proposed | bunkering | 3.1 | 7.1 | 1.3 / 5.7 / 0.0 |
| early_proposed | export | 54.7 | 139.4 | 25.1 / 4.7 / 109.5 |

## 3. By chain

| chain | stages | mtpa | Annual Mt/yr | Lifecycle Mt | CAN / BUNK / FOR |
|---|---|---|---|---|---|
| export | upstream_production@CAN → pipeline_transport@CAN → liquefaction@CAN → shipping@BUNK → regasification@FOR → combustion@FOR | 100.1 | 262.8 | 10446.4 | 47.4 / 8.9 / 206.5 |
| bunkering | upstream_production@CAN → pipeline_transport@CAN → liquefaction@CAN → combustion@BUNK | 3.4 | 7.8 | 228.7 | 1.5 / 6.3 / 0.0 |
| domestic | upstream_production@CAN → pipeline_transport@CAN → liquefaction@CAN → regasification@CAN → combustion@CAN | 0.3 | 0.9 | 8.6 | 0.9 / 0.0 / 0.0 |
| import | regasification@CAN → combustion@CAN | 7.5 | 0.5 | 20.9 | 0.5 / 0.0 / 0.0 |

## 4. By project

| project | mtpa | chain | calc_group | tier | drive | life (source) | effective Mt/yr | annual Mt/yr | lifecycle Mt | CAN / BUNK / FOR | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| tilbury_phase_1a | 0.2 | bunkering | operating | operating | gas_turbine | 40 (Parameters:lifecycle_years_default) | 0.21 | 0.7 | 28.0 | 0.1 / 0.6 / 0.0 |  |
| energir_montreal_lng | 0.2 | domestic | operating | operating | not_published | 40 (Parameters:lifecycle_years_default) | 0.18 | 0.6 | — | 0.6 / 0.0 / 0.0 | legacy: outlived nominal design life; steady-state util; annual only |
| mt_hayes_lng | 0.1 | domestic | operating | operating | not_published | 40 (Parameters:lifecycle_years_default) | 0.05 | 0.2 | 6.8 | 0.2 / 0.0 / 0.0 |  |
| tamaska_fort_nelson_lng | 0.0 | domestic | operating | operating | not_published | 40 (Parameters:lifecycle_years_default) | 0.01 | 0.0 | 1.8 | 0.0 / 0.0 / 0.0 |  |
| tilbury_original | 0.0 | domestic | operating | operating | not_published | 40 (Parameters:lifecycle_years_default) | 0.03 | 0.1 | — | 0.1 / 0.0 / 0.0 | legacy: outlived nominal design life; steady-state util; annual only |
| lng_canada_phase_1 | 14.0 | export | operating | operating | gas_turbine | 40 (Asset Register:authorised_export_term_years) | 11.60 | 41.2 | 1647.6 | 7.4 / 1.4 / 32.4 |  |
| saint_john_import_facility | 7.5 | import | operating | watch | — | 40 (Parameters:lifecycle_years_default) | 0.19 | 0.5 | 20.9 | 0.5 / 0.0 / 0.0 |  |
| tilbury_phase_1b | 0.7 | bunkering | proposed | advanced_proposed | gas_turbine | 40 (Parameters:lifecycle_years_default) | 0.47 | 1.6 | 63.4 | 0.3 / 1.3 / 0.0 |  |
| tilbury_phase_2 | 2.5 | bunkering | proposed | advanced_proposed | gas_turbine | 25 (Asset Register:authorised_export_term_years) | 1.62 | 5.5 | 137.3 | 1.0 / 4.5 / 0.0 |  |
| discovery_t1t4 | 20.0 | export | proposed | early_proposed | gas_turbine | 40 (Parameters:lifecycle_years_default) | 14.39 | 51.1 | 2043.9 | 9.2 / 1.7 / 40.2 |  |
| fermeuse_energy_flng | 5.0 | export | proposed | early_proposed | gas_turbine | 40 (Parameters:lifecycle_years_default) | 3.60 | 12.8 | 511.0 | 2.3 / 0.4 / 10.0 |  |
| kanata_lng | 12.0 | export | proposed | early_proposed | gas_turbine | 40 (Parameters:lifecycle_years_default) | 8.64 | 30.7 | 1226.3 | 5.5 / 1.0 / 24.1 |  |
| ksi_lisims_lng | 12.0 | export | proposed | advanced_proposed | gas_turbine | 40 (Asset Register:authorised_export_term_years) | 8.64 | 30.7 | 1226.3 | 5.5 / 1.0 / 24.1 |  |
| lng_canada_phase_2 | 14.0 | export | proposed | advanced_proposed | gas_turbine | 40 (Asset Register:authorised_export_term_years) | 10.08 | 35.8 | 1430.7 | 6.4 / 1.2 / 28.1 |  |
| marinvest_baie_comeau | 15.0 | export | proposed | early_proposed | gas_turbine | 40 (Parameters:lifecycle_years_default) | 10.80 | 38.3 | 1532.9 | 6.9 / 1.3 / 30.1 |  |
| summit_lake_pg_lng | 2.7 | export | proposed | early_proposed | gas_turbine | 30 (Asset Register:project_life_years) | 1.84 | 6.5 | 195.5 | 1.2 / 0.2 / 5.1 |  |
| cedar_lng | 3.3 | export | under_construction | under_construction | gas_turbine | 40 (Asset Register:authorised_export_term_years) | 2.72 | 9.7 | 386.4 | 1.7 / 0.3 / 7.6 |  |
| woodfibre_lng | 2.1 | export | under_construction | under_construction | gas_turbine | 40 (Asset Register:authorised_export_term_years) | 1.73 | 6.1 | 245.9 | 1.1 / 0.2 / 4.8 |  |

## 5. By stage

| stage | destination | Annual Mt/yr | share |
|---|---|---|---|
| upstream_production | CAN | 19.1 | 7.0% |
| pipeline_transport | CAN | 7.7 | 2.8% |
| liquefaction | CAN | 22.2 | 8.2% |
| shipping | BUNK | 8.9 | 3.3% |
| regasification | CAN,FOR | 3.0 | 1.1% |
| combustion | BUNK,CAN,FOR | 211.1 | 77.6% |

## 6. Scenario range

| scenario | upstream | Annual Mt/yr | Lifecycle Mt | CAN Mt/yr |
|---|---|---|---|---|
| inventory_as_reported | 0.22 | 269.7 | 10614.3 | 48.0 |
| measurement_central | 0.25 | 272.0 | 10704.7 | 50.3 |
| measurement_high | 0.26 | 272.8 | 10734.8 | 51.0 |
| near_term_methane_gwp20 | 0.33 | 278.1 | 10945.7 | 56.4 |
| howarth_high | 0.55 | 295.0 | 11608.5 | 73.2 |

## 7. Context

Canada territorial under `measurement_central` is **50.3 MtCO2e/yr**.

- **7.2%** of national inventory (694 Mt, inventory basis — excludes LULUCF).
- **12.1% to 11.0%** of the 2030 target range (417–455 Mt). Targets include land-use accounting; the 694 inventory figure does not.
- **25.1%** of the 2030 overshoot gap (200 Mt, projected emissions minus the target path).

## 8. Assumptions that move the number most

- **Upstream factor** (central 0.25): inventory_as_reported (0.22) → 269.7 Mt/yr (-2.3); howarth_high (0.55) → 295.0 Mt/yr (+23.0).
- **Lifespan** (default mostly 40 yr licence / Parameters default): sensitivity bounds in Parameters are 30 and 50 yr. Lifecycle total scales roughly with lifespan (~-25% at 30 yr, ~+25% at 50 yr on a pure scale basis). Annual changes only via the util_sum/life ratio and FID-delay share of the window. Legacy facilities (outlived design life) use steady-state util and report annual only.
- **FID delay** (`fid_delay_mid`=5 yr inside lifespan): applies to 9 projects (80.7 mtpa export), currently 212.9 Mt/yr. Removing the delay would raise their annual emissions by roughly the ratio of lost ramp years (order-of-magnitude: several Mt/yr on the proposed export slate).
- **Utilisation** (default steady-state 0.839; Phase 1 override 0.85; Saint John flat 0.025): annual emissions scale almost linearly with effective util. A +10% relative move in steady-state util moves the headline by about 27.2 Mt/yr if applied uniformly.
- **Liquefaction** (central 0.29 tCO2e/t, gas turbine for every terminal): electrification is not assumed (`liquefaction_electrification_assumed`=none). 0.12 is retained as range_low and applies only if electrification is contracted and delivered. Previous drive classifications are in `liquefaction_drive_note`.
- **Liquefaction drive default** for remaining `not_published` (domestic) rows: `gas_turbine` → intensity 0.29 tCO2e/t from Emission Factors central.

## 9. Appendix · electrification counterfactual (Canada territorial)

Headline case is gas turbine for every terminal. The rows below ask what Canada-territorial LNG would be if liquefaction ran at the electric factor (0.12 instead of 0.29 tCO2e/t). Liquefaction is tagged CAN, so the whole delta is territorial. This does not change the headline totals.

| case | CAN Mt/yr | vs gas | share of 694 Mt inventory | share of 2030 target low |
|---|---|---|---|---|
| Gas turbine (current) | 50.3 | — | 7.2% | 12.1% |
| Claimed electric delivered | 44.2 | -6.1 | 6.4% | 10.6% |
| All terminals electric | 37.3 | -13.0 | 5.4% | 8.9% |

Claimed-electric assets (previous `electric_committed` / `electric_planned`): cedar_lng, ksi_lisims_lng, lng_canada_phase_2, marinvest_baie_comeau, summit_lake_pg_lng, woodfibre_lng.

| calc_group | gas | claimed electric | all electric |
|---|---|---|---|
| operating | 9.0 | 9.0 | 6.9 |
| under_construction | 2.8 | 2.1 | 2.1 |
| proposed | 38.4 | 33.1 | 28.2 |

Figure: `Outputs/figures/fig08_electrification_canada_territorial.png`.

## 10. Anything that looks wrong

- FINDING: tilbury_marine_jetty: chain=none — no lifecycle applies; excluded (not zeroed).
- Flag: port_of_hamilton_lng.capacity_mtpa=missing
- Excluded (chain=none or blank, not zeroed): ['tilbury_marine_jetty']
- Legacy facilities (outlived nominal design life; annual only, no lifecycle total): energir_montreal_lng (first_export_year=1976.0), tilbury_original (first_export_year=1971.0).
- Capacity is never summed across chains (liquefaction ≠ regasification). Headline capacity is export-chain only.
- Reconciliations close within floating-point tolerance (1e-6 to 1e-3); no material rounding residuals.
- Saint John at ~0.5 Mt/yr depends entirely on `saint_john_utilisation=0.025`; nameplate at default util would be ~17 Mt/yr. tier=watch but calc_group=operating (operating import terminal).
- Tilbury Phase 2 (2.5 mtpa) sits on bunkering by register judgement (`chain_note`); NRCan lists it as export — classification is a stated judgement, not re-derived in code.
