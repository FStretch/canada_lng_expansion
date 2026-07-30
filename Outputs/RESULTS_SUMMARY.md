# Canada LNG lifecycle emissions — review summary

Default scenario: `measurement_central`. Run at 2026-07-29 15:09 UTC. Numbers to one decimal. Inputs read-only. `calc_group` from `Asset Register:calc_group`.

## 1. Headline

- **Annual total:** 159.2 MtCO2e/yr
- **Lifecycle total:** 6196.7 MtCO2e (excludes legacy facilities)
- **Headline capacity (export chain only):** 58.1 mtpa (liquefaction; not summed with import regasification or other chains)

| chain | mtpa |
|---|---|
| export | 58.1 |
| bunkering | 3.4 |
| domestic | 0.3 |
| import | 7.5 |

- **Scope 1+2:** 24.2 MtCO2e/yr (15.2%)  |  **Scope 3:** 135.0 MtCO2e/yr (84.8%)
- **Territorial:** CAN 25.5 (16.0%)  |  BUNK 11.6 (7.3%)  |  FOR 122.2 (76.7%)

## 2. By group

| calc_group | export mtpa | Annual Mt/yr | Lifecycle Mt | CAN / BUNK / FOR Mt/yr |
|---|---|---|---|---|
| operating | 14.0 | 43.3 | 1705.0 | 9.0 / 2.0 / 32.4 |
| under_construction | 5.4 | 15.0 | 602.0 | 2.1 / 0.5 / 12.4 |
| proposed | 38.7 | 100.9 | 3889.7 | 14.4 / 9.1 / 77.4 |

Capacity by chain within each calc_group (not summed across chains):

| calc_group | export | bunkering | domestic | import |
|---|---|---|---|---|
| operating | 14.0 | 0.2 | 0.3 | 7.5 |
| under_construction | 5.4 | 0.0 | 0.0 | 0.0 |
| proposed | 38.7 | 3.1 | 0.0 | 0.0 |

### Proposed: advanced vs early (tier split)

| tier | chain scope | mtpa | Annual Mt/yr | CAN / BUNK / FOR |
|---|---|---|---|---|
| advanced_proposed | export | 26.0 | 63.2 | 8.8 / 2.2 / 52.2 |
| advanced_proposed | bunkering | 3.1 | 7.1 | 1.3 / 5.7 / 0.0 |
| early_proposed | export | 12.7 | 30.5 | 4.2 / 1.1 / 25.2 |

## 3. By chain

| chain | stages | mtpa | Annual Mt/yr | Lifecycle Mt | CAN / BUNK / FOR |
|---|---|---|---|---|---|
| export | upstream_production@CAN → pipeline_transport@CAN → liquefaction@CAN → shipping@BUNK → regasification@FOR → combustion@FOR | 58.1 | 150.0 | 5938.5 | 22.6 / 5.3 / 122.2 |
| bunkering | upstream_production@CAN → pipeline_transport@CAN → liquefaction@CAN → combustion@BUNK | 3.4 | 7.8 | 228.7 | 1.5 / 6.3 / 0.0 |
| domestic | upstream_production@CAN → pipeline_transport@CAN → liquefaction@CAN → regasification@CAN → combustion@CAN | 0.3 | 0.9 | 8.6 | 0.9 / 0.0 / 0.0 |
| import | regasification@CAN → combustion@CAN | 7.5 | 0.5 | 20.9 | 0.5 / 0.0 / 0.0 |

## 4. By project

| project | mtpa | chain | calc_group | tier | drive | life (source) | effective Mt/yr | annual Mt/yr | lifecycle Mt | CAN / BUNK / FOR | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| tilbury_phase_1a | 0.2 | bunkering | operating | operating | not_published | 40 (Parameters:lifecycle_years_default) | 0.21 | 0.7 | 28.0 | 0.1 / 0.6 / 0.0 |  |
| energir_montreal_lng | 0.2 | domestic | operating | operating | not_published | 40 (Parameters:lifecycle_years_default) | 0.18 | 0.6 | — | 0.6 / 0.0 / 0.0 | legacy: outlived nominal design life; steady-state util; annual only |
| mt_hayes_lng | 0.1 | domestic | operating | operating | not_published | 40 (Parameters:lifecycle_years_default) | 0.05 | 0.2 | 6.8 | 0.2 / 0.0 / 0.0 |  |
| tamaska_fort_nelson_lng | 0.0 | domestic | operating | operating | not_published | 40 (Parameters:lifecycle_years_default) | 0.01 | 0.0 | 1.8 | 0.0 / 0.0 / 0.0 |  |
| tilbury_original | 0.0 | domestic | operating | operating | not_published | 40 (Parameters:lifecycle_years_default) | 0.03 | 0.1 | — | 0.1 / 0.0 / 0.0 | legacy: outlived nominal design life; steady-state util; annual only |
| lng_canada_phase_1 | 14.0 | export | operating | operating | gas_turbine | 40 (Asset Register:authorised_export_term_years) | 11.60 | 41.2 | 1647.6 | 7.4 / 1.4 / 32.4 |  |
| saint_john_import_facility | 7.5 | import | operating | watch | — | 40 (Parameters:lifecycle_years_default) | 0.19 | 0.5 | 20.9 | 0.5 / 0.0 / 0.0 |  |
| tilbury_phase_1b | 0.7 | bunkering | proposed | advanced_proposed | not_published | 40 (Parameters:lifecycle_years_default) | 0.47 | 1.6 | 63.4 | 0.3 / 1.3 / 0.0 |  |
| tilbury_phase_2 | 2.5 | bunkering | proposed | advanced_proposed | not_published | 25 (Asset Register:authorised_export_term_years) | 1.62 | 5.5 | 137.3 | 1.0 / 4.5 / 0.0 |  |
| ksi_lisims_lng | 12.0 | export | proposed | advanced_proposed | electric_planned | 40 (Asset Register:authorised_export_term_years) | 8.64 | 29.2 | 1167.6 | 4.1 / 1.0 / 24.1 |  |
| lng_canada_phase_2 | 14.0 | export | proposed | advanced_proposed | electric_planned | 40 (Asset Register:authorised_export_term_years) | 10.08 | 34.1 | 1362.2 | 4.7 / 1.2 / 28.1 |  |
| marinvest_baie_comeau | 10.0 | export | proposed | early_proposed | electric_planned | 40 (Parameters:lifecycle_years_default) | 7.20 | 24.3 | 973.0 | 3.4 / 0.9 / 20.1 |  |
| summit_lake_pg_lng | 2.7 | export | proposed | early_proposed | electric_planned | 30 (Asset Register:project_life_years) | 1.84 | 6.2 | 186.1 | 0.9 / 0.2 / 5.1 |  |
| cedar_lng | 3.3 | export | under_construction | under_construction | electric_committed | 40 (Asset Register:authorised_export_term_years) | 2.72 | 9.2 | 367.9 | 1.3 / 0.3 / 7.6 |  |
| woodfibre_lng | 2.1 | export | under_construction | under_construction | electric_committed | 40 (Asset Register:authorised_export_term_years) | 1.73 | 5.9 | 234.1 | 0.8 / 0.2 / 4.8 |  |

## 5. By stage

| stage | destination | Annual Mt/yr | share |
|---|---|---|---|
| upstream_production | CAN | 11.6 | 7.3% |
| pipeline_transport | CAN | 4.6 | 2.9% |
| liquefaction | CAN | 8.0 | 5.0% |
| shipping | BUNK | 5.3 | 3.3% |
| regasification | CAN,FOR | 1.8 | 1.1% |
| combustion | BUNK,CAN,FOR | 128.0 | 80.4% |

## 6. Scenario range

| scenario | upstream | Annual Mt/yr | Lifecycle Mt | CAN Mt/yr |
|---|---|---|---|---|
| inventory_as_reported | 0.22 | 157.8 | 6142.6 | 24.1 |
| measurement_central | 0.25 | 159.2 | 6196.7 | 25.5 |
| measurement_high | 0.26 | 159.7 | 6214.7 | 25.9 |
| near_term_methane_gwp20 | 0.33 | 162.9 | 6341.0 | 29.2 |
| howarth_high | 0.55 | 173.1 | 6737.8 | 39.4 |

## 7. Context

Canada territorial under `measurement_central` is **25.5 MtCO2e/yr**.

- **3.7%** of national inventory (694 Mt, inventory basis — excludes LULUCF).
- **6.1% to 5.6%** of the 2030 target range (417–455 Mt). Targets include land-use accounting; the 694 inventory figure does not.
- **12.7%** of the 2030 overshoot gap (200 Mt, projected emissions minus the target path).

## 8. Assumptions that move the number most

- **Upstream factor** (central 0.25): inventory_as_reported (0.22) → 157.8 Mt/yr (-1.4); howarth_high (0.55) → 173.1 Mt/yr (+13.9).
- **Lifespan** (default mostly 40 yr licence / Parameters default): sensitivity bounds in Parameters are 30 and 50 yr. Lifecycle total scales roughly with lifespan (~-25% at 30 yr, ~+25% at 50 yr on a pure scale basis). Annual changes only via the util_sum/life ratio and FID-delay share of the window. Legacy facilities (outlived design life) use steady-state util and report annual only.
- **FID delay** (`fid_delay_mid`=5 yr inside lifespan): applies to 6 projects (38.7 mtpa export), currently 100.9 Mt/yr. Removing the delay would raise their annual emissions by roughly the ratio of lost ramp years (order-of-magnitude: several Mt/yr on the proposed export slate).
- **Utilisation** (default steady-state 0.839; Phase 1 override 0.85; Saint John flat 0.025): annual emissions scale almost linearly with effective util. A +10% relative move in steady-state util moves the headline by about 15.9 Mt/yr if applied uniformly.
- **Liquefaction drive** (gas_turbine 0.29 vs electric 0.12): 44.1 mtpa export currently electric. Switching them all to gas_turbine would add about **5.5 Mt/yr**; the reverse (all gas to electric) is not applicable to Phase 1.
- **Liquefaction drive default** for `not_published` rows: `gas_turbine` → intensity 0.29 tCO2e/t.

## 9. Anything that looks wrong

- FINDING: tilbury_marine_jetty: chain=none — no lifecycle applies; excluded (not zeroed).
- Flag: port_of_hamilton_lng.capacity_mtpa=missing
- Flag: fermeuse_energy_flng.capacity_mtpa=missing
- Flag: fermeuse_energy_flng.liquefaction_drive=missing
- Excluded (chain=none or blank, not zeroed): ['tilbury_marine_jetty']
- Legacy facilities (outlived nominal design life; annual only, no lifecycle total): energir_montreal_lng (first_export_year=1976.0), tilbury_original (first_export_year=1971.0).
- Capacity is never summed across chains (liquefaction ≠ regasification). Headline capacity is export-chain only.
- Reconciliations close within floating-point tolerance (1e-6 to 1e-3); no material rounding residuals.
- Saint John at ~0.5 Mt/yr depends entirely on `saint_john_utilisation=0.025`; nameplate at default util would be ~17 Mt/yr. tier=watch but calc_group=operating (operating import terminal).
- Tilbury Phase 2 (2.5 mtpa) sits on bunkering by register judgement (`chain_note`); NRCan lists it as export — classification is a stated judgement, not re-derived in code.
