# Canada LNG lifecycle emissions — review summary

Default scenario: `measurement_central`. Run at 2026-08-28 15:48 UTC. Numbers to one decimal. Inputs read-only. `calc_group` from `Asset Register:calc_group`.

Deck-facing tables (one sheet per table, 1-decimal): `Outputs/SLIDE_TABLES.xlsx`. Send that workbook to the PPT chat.

## 1. Headline

- **Annual total (panel peak):** 309.1 MtCO2e in 2037 (16 assets emitting that year)
- **life_average_annual_mt:** 268.1 MtCO2e/yr (mean utilisation over each asset's operating window; not a calendar year)
- **Lifetime total (calendar panel 2025–2069):** 9558.2 MtCO2e (excludes legacy facilities; remaining years from 2025, not duration × life-average)
- **Headline capacity (export chain only):** 100.1 mtpa (liquefaction; not summed with import regasification or other chains)

| chain | mtpa |
|---|---|
| export | 100.1 |
| bunkering | 3.4 |
| domestic | 0.3 |
| import | 7.5 |

- **Scope 1+2:** 48.3 MtCO2e/yr (18.0%)  |  **Scope 3:** 219.8 MtCO2e/yr (82.0%)
- **Territorial:** CAN 49.6 (18.5%)  |  BUNK 15.1 (5.6%)  |  FOR 203.5 (75.9%)
- **Share of remaining carbon budget (GCB 2025, from start of 2026):** 1.5°C, 50% from start of 2026 5.6% of 170 GtCO2  |  1.7°C, 50% from start of 2026 1.8% of 525 GtCO2  |  2.0°C, 50% from start of 2026 0.9% of 1055 GtCO2. Comparison is **CO2e against a CO2 budget** (approximation); a true CO2-only total is not derivable.

## 2. By group

| calc_group | export mtpa | life_average_annual_mt | Lifecycle Mt | CAN / BUNK / FOR Mt/yr |
|---|---|---|---|---|
| operating | 14.0 | 43.1 | 1351.8 | 8.9 / 2.0 / 32.2 |
| under_construction | 5.4 | 15.8 | 559.9 | 2.8 / 0.5 / 12.4 |
| proposed | 80.7 | 209.3 | 7646.6 | 37.8 / 12.6 / 158.9 |

Capacity by chain within each calc_group (not summed across chains):

| calc_group | export | bunkering | domestic | import |
|---|---|---|---|---|
| operating | 14.0 | 0.2 | 0.3 | 7.5 |
| under_construction | 5.4 | 0.0 | 0.0 | 0.0 |
| proposed | 80.7 | 3.1 | 0.0 | 0.0 |

### Proposed: advanced vs early (tier split)

| tier | chain scope | mtpa | life_average_annual_mt | CAN / BUNK / FOR |
|---|---|---|---|---|
| advanced_proposed | export | 26.0 | 62.8 | 11.3 / 2.1 / 49.4 |
| advanced_proposed | bunkering | 3.1 | 7.1 | 1.3 / 5.7 / 0.0 |
| early_proposed | export | 54.7 | 139.4 | 25.1 / 4.7 / 109.5 |

## 3. By chain

| chain | stages | mtpa | life_average_annual_mt | Lifecycle Mt | CAN / BUNK / FOR |
|---|---|---|---|---|---|
| export | upstream_production@CAN → pipeline_transport@CAN → liquefaction@CAN → shipping@BUNK → regasification@FOR → combustion@FOR | 100.1 | 258.9 | 9315.3 | 46.7 / 8.8 / 203.5 |
| bunkering | upstream_production@CAN → pipeline_transport@CAN → liquefaction@CAN → combustion@BUNK | 3.4 | 7.8 | 224.2 | 1.5 / 6.3 / 0.0 |
| domestic | upstream_production@CAN → pipeline_transport@CAN → liquefaction@CAN → regasification@CAN → combustion@CAN | 0.3 | 0.9 | 6.1 | 0.9 / 0.0 / 0.0 |
| import | regasification@CAN → combustion@CAN | 7.5 | 0.5 | 12.6 | 0.5 / 0.0 / 0.0 |

## 4. By project

| project | mtpa | chain | calc_group | tier | drive | life (source) | effective Mt/yr | annual Mt/yr | lifecycle Mt | CAN / BUNK / FOR | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| tilbury_phase_1a | 0.2 | bunkering | operating | operating | gas_turbine | 40 (Parameters:lifecycle_years_default) | 0.21 | 0.7 | 23.5 | 0.1 / 0.6 / 0.0 |  |
| energir_montreal_lng | 0.2 | domestic | operating | operating | not_published | 40 (Parameters:lifecycle_years_default) | 0.18 | 0.6 | — | 0.6 / 0.0 / 0.0 | legacy: outlived nominal design life; steady-state util; annual only |
| mt_hayes_lng | 0.1 | domestic | operating | operating | not_published | 40 (Parameters:lifecycle_years_default) | 0.05 | 0.2 | 4.5 | 0.2 / 0.0 / 0.0 |  |
| tamaska_fort_nelson_lng | 0.0 | domestic | operating | operating | not_published | 40 (Parameters:lifecycle_years_default) | 0.01 | 0.0 | 1.7 | 0.0 / 0.0 / 0.0 |  |
| tilbury_original | 0.0 | domestic | operating | operating | not_published | 40 (Parameters:lifecycle_years_default) | 0.03 | 0.1 | — | 0.1 / 0.0 / 0.0 | legacy: outlived nominal design life; steady-state util; annual only |
| lng_canada_phase_1 | 14.0 | export | operating | operating | gas_turbine | 32 (Asset Register:authorised_export_end_year=2056 (hard stop; cuts 8y from Asset Register:authorised_export_term_years)) | 11.53 | 40.9 | 1309.6 | 7.4 / 1.4 / 32.2 |  |
| saint_john_import_facility | 7.5 | import | operating | watch | — | 40 (Parameters:lifecycle_years_default) | 0.19 | 0.5 | 12.6 | 0.5 / 0.0 / 0.0 |  |
| tilbury_phase_1b | 0.7 | bunkering | proposed | advanced_proposed | gas_turbine | 40 (Parameters:lifecycle_years_default) | 0.47 | 1.6 | 63.4 | 0.3 / 1.3 / 0.0 |  |
| tilbury_phase_2 | 2.5 | bunkering | proposed | advanced_proposed | gas_turbine | 25 (Asset Register:authorised_export_term_years) | 1.62 | 5.5 | 137.3 | 1.0 / 4.5 / 0.0 |  |
| discovery_t1t4 | 20.0 | export | proposed | early_proposed | gas_turbine | 40 (Parameters:lifecycle_years_default) | 14.39 | 51.1 | 2043.9 | 9.2 / 1.7 / 40.2 |  |
| fermeuse_energy_flng | 5.0 | export | proposed | early_proposed | gas_turbine | 40 (Parameters:lifecycle_years_default) | 3.60 | 12.8 | 511.0 | 2.3 / 0.4 / 10.0 |  |
| kanata_lng | 12.0 | export | proposed | early_proposed | gas_turbine | 40 (Parameters:lifecycle_years_default) | 8.64 | 30.7 | 1226.3 | 5.5 / 1.0 / 24.1 |  |
| ksi_lisims_lng | 12.0 | export | proposed | advanced_proposed | gas_turbine | 35 (Asset Register:authorised_export_end_year=2063 (hard stop; cuts 5y from Asset Register:authorised_export_term_years)) | 8.43 | 29.9 | 1047.6 | 5.4 / 1.0 / 23.5 |  |
| lng_canada_phase_2 | 14.0 | export | proposed | advanced_proposed | gas_turbine | 27 (Asset Register:authorised_export_end_year=2056 (hard stop; cuts 13y from Asset Register:authorised_export_term_years)) | 9.27 | 32.9 | 888.6 | 5.9 / 1.1 / 25.9 |  |
| marinvest_baie_comeau | 15.0 | export | proposed | early_proposed | gas_turbine | 40 (Parameters:lifecycle_years_default) | 10.80 | 38.3 | 1532.9 | 6.9 / 1.3 / 30.1 |  |
| summit_lake_pg_lng | 2.7 | export | proposed | early_proposed | gas_turbine | 30 (Asset Register:project_life_years) | 1.84 | 6.5 | 195.5 | 1.2 / 0.2 / 5.1 |  |
| cedar_lng | 3.3 | export | under_construction | under_construction | gas_turbine | 39 (Asset Register:authorised_export_end_year=2066 (hard stop; cuts 1y from Asset Register:authorised_export_term_years)) | 2.72 | 9.7 | 376.6 | 1.7 / 0.3 / 7.6 |  |
| woodfibre_lng | 2.1 | export | under_construction | under_construction | gas_turbine | 30 (Asset Register:authorised_export_end_year=2057 (hard stop; cuts 10y from Asset Register:authorised_export_term_years)) | 1.72 | 6.1 | 183.3 | 1.1 / 0.2 / 4.8 |  |

## 5. By stage

| stage | destination | life_average_annual_mt | share |
|---|---|---|---|
| upstream_production | CAN | 18.9 | 7.0% |
| pipeline_transport | CAN | 7.5 | 2.8% |
| liquefaction | CAN | 21.9 | 8.2% |
| shipping | BUNK | 8.8 | 3.3% |
| regasification | CAN,FOR | 2.9 | 1.1% |
| combustion | BUNK,CAN,FOR | 208.1 | 77.6% |

## 6. Scenario range

| scenario | upstream | life_average_annual_mt | Lifecycle Mt | CAN Mt/yr |
|---|---|---|---|---|
| inventory_as_reported | 0.22 | 265.8 | 9477.5 | 47.3 |
| measurement_central | 0.25 | 268.1 | 9558.2 | 49.6 |
| measurement_high | 0.26 | 268.9 | 9585.2 | 50.3 |
| near_term_methane_gwp20 | 0.33 | 274.1 | 9773.6 | 55.6 |
| howarth_high | 0.55 | 290.8 | 10365.8 | 72.2 |

## 7. Context

Canada territorial under `measurement_central` is **49.6 MtCO2e/yr**.

- **7.1%** of national inventory (694 Mt, inventory basis — excludes LULUCF).
- **11.9% to 10.9%** of the 2030 target range (417–455 Mt). Targets include land-use accounting; the 694 inventory figure does not.
- **24.8%** of the 2030 overshoot gap (200 Mt, projected emissions minus the target path).

## 8. Assumptions that move the number most

- **Upstream factor** (central 0.25): inventory_as_reported (0.22) → 265.8 Mt/yr (-2.3); howarth_high (0.55) → 290.8 Mt/yr (+22.6).
- **Lifespan** (default mostly 40 yr licence / Parameters default): sensitivity bounds in Parameters are 30 and 50 yr. Lifecycle total scales roughly with lifespan (~-25% at 30 yr, ~+25% at 50 yr on a pure scale basis). Annual changes only via the util_sum/life ratio and FID-delay share of the window. Legacy facilities (outlived design life) use steady-state util and report annual only.
- **FID delay** (`fid_delay_mid`=5 yr inside lifespan): applies to 9 projects (80.7 mtpa export), currently 209.3 Mt/yr. Removing the delay would raise their annual emissions by roughly the ratio of lost ramp years (order-of-magnitude: several Mt/yr on the proposed export slate).
- **Utilisation** (default steady-state 0.839; Phase 1 override 0.85; Saint John flat 0.025): annual emissions scale almost linearly with effective util. A +10% relative move in steady-state util moves the headline by about 26.8 Mt/yr if applied uniformly.
- **Liquefaction** (central 0.29 tCO2e/t, gas turbine for every terminal): electrification is not assumed (`liquefaction_electrification_assumed`=none). 0.12 is retained as range_low and applies only if electrification is contracted and delivered. Previous drive classifications are in `liquefaction_drive_note`.
- **Placeholder start year** (`assumed_first_export_year_if_missing`=2030): 5646.9 MtCO2e (59.1% of lifetime) from six assets with a blank `first_export_year`. The 2069 tail is entirely this fill. Sensitivity at 2033 and 2035 is tabulated below.
- **Liquefaction drive default** for remaining `not_published` (domestic) rows: `gas_turbine` → intensity 0.29 tCO2e/t from Emission Factors central.

## 9. Appendix · electrification counterfactual (Canada territorial)

Headline case is gas turbine for every terminal. The rows below ask what Canada-territorial LNG would be if liquefaction ran at the electric factor (0.12 instead of 0.29 tCO2e/t). Liquefaction is tagged CAN, so the whole delta is territorial. This does not change the headline totals.

| case | CAN Mt/yr | vs gas | share of 694 Mt inventory | share of 2030 target low |
|---|---|---|---|---|
| Gas turbine (current) | 49.6 | — | 7.1% | 11.9% |
| Claimed electric delivered | 43.7 | -5.9 | 6.3% | 10.5% |
| All terminals electric | 36.7 | -12.8 | 5.3% | 8.8% |

Claimed-electric assets (previous `electric_committed` / `electric_planned`): cedar_lng, ksi_lisims_lng, lng_canada_phase_2, marinvest_baie_comeau, summit_lake_pg_lng, woodfibre_lng.

| calc_group | gas | claimed electric | all electric |
|---|---|---|---|
| operating | 8.9 | 8.9 | 6.9 |
| under_construction | 2.8 | 2.1 | 2.1 |
| proposed | 37.8 | 32.6 | 27.8 |

Figure: `Outputs/figures/fig08_electrification_canada_territorial.png`.

## 10. Anything that looks wrong

- FINDING: tilbury_marine_jetty: chain=none — no lifecycle applies; excluded (not zeroed).
- Flag: port_of_hamilton_lng.capacity_mtpa=missing
- Excluded (chain=none or blank, not zeroed): ['tilbury_marine_jetty']
- Legacy facilities (outlived nominal design life; annual only, no lifecycle total): energir_montreal_lng (first_export_year=1976.0), tilbury_original (first_export_year=1971.0).
- Remaining carbon budgets (GCB 2025) are CO2 from the start of 2026. Lifetime totals are GWP100 CO2e. The share-of-budget figures compare CO2e to a CO2 budget and are an approximation; a true CO2-only total is not derivable from this model.
- Reconciliations close within floating-point tolerance (1e-6 to 1e-3); no material rounding residuals.
- Saint John at ~0.5 Mt/yr depends entirely on `saint_john_utilisation=0.025`; nameplate at default util would be ~17 Mt/yr. tier=watch but calc_group=operating (operating import terminal).
- Tilbury Phase 2 (2.5 mtpa) sits on bunkering by register judgement (`chain_note`); NRCan lists it as export — classification is a stated judgement, not re-derived in code.
- Loss and damage central case is ECCC SC-CO2 at 2%, applied per calendar year to the full GWP100 CO2e total (`central_price_family=eccc`). That overstates methane (CH4-derived CO2e is charged at SC-CO2 rather than SC-CH4). Burke is an upper-bracket sensitivity (g = 0). Damages after 2100, sea-level rise, extremes and mortality outside GDP are omitted. The Conference Board denominator is Table 1 GDP in 2020 CAD, inflated to 2025 CAD.

## 11. Climate loss and damage (global)

Monetised economic damages from the modelled lifecycle emissions. The **central case** is ECCC official SC-CO2 at the **2%** discount rate, applied per calendar year of emissions, in 2025 CAD (named parameters `central_price_family=eccc`, `central_aggregation=calendar_year`). ECCC 1.5% and 2.5% are the central case's sensitivity range. Burke et al. (2026) is an **upper-bracket sensitivity** across discount rates and Figure 2e horizons (default g = 0; Hatton +2% is not used). Damages are **global**. They are not a legal bill. ECCC SC-CO2 is applied to the full GWP100 CO2e total. That **overstates** the methane contribution (CH4-derived CO2e is charged at SC-CO2 rather than at SC-CH4) and is not conservative in that direction. Construction, sea-level rise, extremes, and mortality outside GDP are omitted.

Methane share of the CO2e total is **2.7%** (258 of 9,558 MtCO2e). That is the excess of the central upstream factor (0.25) over inventory CO2 (0.154), i.e. 0.096 tCO2e per t LNG, as a share of the chain total. Pipeline and shipping methane stay inside CO2e as CO2 and are not in this share. GWP100 = 29.8; ECCC SC-CH4/SC-CO2 is 9.6 in 2025 and 16.7 by 2080. Pricing that methane CO2e as CO2 therefore charges it at roughly 3.1× the ECCC CH4 price in 2025. The resulting overstatement is **1.5%** of the central damage bill. This treatment overstates methane and is not conservative in that direction.

Implied average price is **$446/t** CAD 2025 (total damages / lifetime tonnes). That is the emissions-weighted mean of the ECCC 2% schedule after a **single** CAD 2021→2025 inflation of 1.1535 (deflators 124.81689 / 143.98050). The unweighted mean of the same series over panel years is $434/t. In CAD 2021 the weighted mean is $387/t (2025 official schedule value is $271/t). Prices are looked up on the **calendar year of emission**. 44% of lifetime tonnes are after 2050, so the weighted mean sits above the 2037 peak-year price. Year table: `Outputs/figure_data/ld_price_by_year.csv`.

- **Central (ECCC 2%, calendar year), all in-scope:** **$4.3 trillion** (operating $542 billion  |  under construction $240 billion  |  proposed $3.5 trillion)
- **Central sensitivity (ECCC 1.5%–2.5%, calendar year):** $2.8 trillion to $6.7 trillion
- **ECCC 2% NPV to 2025 (sensitivity, not central):** $2.6 trillion (proposed $2.1 trillion)
- **Burke upper bracket (g = 0, year-by-year 2100 path, 1.5%–5%):** $4.6 trillion to $21.2 trillion; Figure 2e through-2300 at 2% fixed: **$52.3 trillion** (proposed $41.8 trillion)
- **Canadian value (proposed, CBoC scaled, 40 yr, 2025 CAD):** **$799 billion**
- **Externality ratio, ECCC central (proposed):** **4.4x** global damages / Canadian value (Hatton UK range was 5.9x–16.8x; Burke through-2300 is 52x)
- **Canada Burke-channel victim share (sensitivity, not central):** **0.17%** of a 1990 1 Gt pulse, so it externalises 99.8% ($71 billion borne at the through-2300 2% price)
- **National test, Burke channel only (not the headline):** Canadian value is 11.2x the damages Canada itself bears. Reported as indeterminate.
- **30-year denominator sensitivity (ECCC central, proposed):** $599 billion Canadian value, ratio **6x** (research sketch used 30 years; central uses 40).
- **Operating + under construction only (ECCC central):** $782 billion global L&D / $192 billion value = **4x** (19.4 mtpa export).

Burke Figure 4 sankey (`damages_and_benefits_k90.rds`) is emitter/recipient flows for 1990–2020 **all** emissions, not LNG. Canada as emitter caused **$1.33 trillion** (2.40% of global owing; USA $10.18T validates against the paper's $10.2T). Canada is **not** a plotted recipient, so CAN-on-CAN cannot be read from this file. Victim share stays 0.17% from the 1 Gt pulse.

Canada denominator: Conference Board *A Rising Tide* Table 1, Canada GDP at market prices **C$11.153bn/yr (2020 CAD)** at 56 mtpa, scaled linearly on proposed export nameplate (80.7 mtpa) over 40 years (Appendix A operating life). Whole-chain including upstream (76% of the GDP). Industry-commissioned. Inflated to 2025 CAD with FRED NGDPDIXCAA. Uninflated 2020 CAD value is $643 billion.

Burke horizon rows (g = 0, proposed slate; upper bracket, not central). Global L&D and value in trillion 2025 CAD; Canada-borne in billion 2025 CAD. Bold is the Burke default horizon, not the paper central.

| horizon | discounting | SC USD2020/t | global L&D (tn) | value (tn) | ratio | Canada-borne (bn) |
|---|---|---|---|---|---|---|
| through_2100 | 2pct_fixed | 1,013 | 13.3 | 0.80 | 17x | 22.6 |
| no_growth_after_2100 | 2pct_fixed | 2,120 | 27.7 | 0.80 | 35x | 47.3 |
| **through_2300** | 2pct_fixed | 3,198 | **41.8** | 0.80 | **52x** | 71.3 |
| through_2100 | ramsey | 1,322 | 17.3 | 0.80 | 22x | 29.5 |
| no_growth_after_2100 | ramsey | 4,045 | 52.9 | 0.80 | 66x | 90.2 |
| through_2300 | ramsey | 7,056 | 92.3 | 0.80 | 115x | 157.3 |

Burke through-2100 year-by-year path, g bracket (trillion 2025 CAD, all / proposed). Burke default g = 0; +2% is Hatton's headline and is not used.

| discount | g=−2% | g=0% | g=+2% |
|---|---|---|---|
| 1.5% | 12.0 / 9.3 | 21.2 / 17.0 | 38.6 / 31.8 |
| 2% | 9.4 / 7.2 | **16.6 / 13.3** | 30.1 / 24.8 |
| 3% | 5.9 / 4.5 | 10.4 / 8.3 | 18.9 / 15.6 |
| 5% | 2.6 / 2.0 | 4.6 / 3.7 | 8.4 / 6.9 |

Figure: `Outputs/figures/fig09_loss_damage_by_group.png`.

## Placeholder start-year sensitivity

Parameter `assumed_first_export_year_if_missing` = **2030** (Parameters sheet). Six in-scope assets have a blank `first_export_year`. With licence-end stops on licensed terminals, every dated end year is 2056–2066; the panel tail is entirely this placeholder.

Placeholder-start assets account for **5646.9 MtCO2e** (59.1% of the 9558.2 Mt lifetime total).

| project | mtpa | lifetime Mt | share of lifetime | last year |
|---|---|---|---|---|
| discovery_t1t4 | 20.0 | 2043.9 | 21.4% | 2069 |
| marinvest_baie_comeau | 15.0 | 1532.9 | 16.0% | 2069 |
| kanata_lng | 12.0 | 1226.3 | 12.8% | 2069 |
| fermeuse_energy_flng | 5.0 | 511.0 | 5.3% | 2069 |
| summit_lake_pg_lng | 2.7 | 195.5 | 2.0% | 2059 |
| tilbury_phase_2 | 2.5 | 137.3 | 1.4% | 2054 |

| start year | lifetime Mt | peak year | peak Mt | last year | central damage CAD bn |
|---|---|---|---|---|---|
| 2030 (central) | 9558.2 | 2037 | 309.1 | 2069 | 4267 |
| 2033 | 9558.2 | 2040 | 309.1 | 2072 | 4358 |
| 2035 | 9558.2 | 2042 | 309.1 | 2074 | 4418 |

## Monte Carlo (physics sampled, ECCC 2% applied after)

10,000 draws, seed `20260828`. Physics 0.18s; pricing 0.03s. Kernel vs published panel max abs 5.7e-14 Mt. Liquefaction held at 0.29. Howarth 0.55 is a named point, not a draw.

| build-out | lifetime median [p5, p95] Mt | peak-year median [p5, p95] Mt | ECCC 2% damage median [p5, p95] CAD bn |
|---|---|---|---|
| committed | 1945.4 [1840.3, 2056.5] | 60.8 [57.6, 64.3] | 796 [753, 841] |
| committed_plus_advanced | 4118.6 [3870.4, 4386.5] | 148.7 [140.7, 157.0] | 1746 [1644, 1856] |
| full | 9721.1 [8509.6, 11026.1] | 314.6 [297.6, 332.3] | 4340 [3715, 5034] |

Howarth 0.55 (other stages central, not inside the interval):

| build-out | lifetime Mt | peak year / Mt | ECCC 2% CAD bn |
|---|---|---|---|
| committed | 2072.2 | 2030 / 64.8 | 848 |
| committed_plus_advanced | 4390.6 | 2037 / 158.5 | 1861 |
| full | 10365.8 | 2037 / 335.2 | 4628 |

Central case versus Monte Carlo median (full build-out):

| quantity | central case | Monte Carlo median [p5, p95] |
|---|---|---|
| Lifetime (Mt) | 9558.2 | 9721.1 [8509.6, 11026.1] |
| Peak-year (Mt) | 309.1 in 2037 | 314.6 [297.6, 332.3] |
| ECCC 2% damage (CAD bn) | 4267 | 4340 [3715, 5034] |

They differ because the stage triangles are right-skewed (shipping 0.05 / 0.12 / 0.31 especially): the Monte Carlo median is not the point estimate from central factor values.

Which of the two should be the paper's headline number is not chosen here.

## Lifecycle intensity comparison

tCO2e per tonne LNG. This model is recomputed on each comparator's boundary. Ranges are shown as published; midpoints are not substituted. GWP20 is not mixed with GWP100.

| study | year | geography | boundary | combustion | shipping | total tCO2e/t |
|---|---|---|---|---|---|---|
| This model (export chain) | 2026 | Canada | Well → combustion (GWP100) | yes | yes | 3.55 |
| This model, aligned to Roman-White 2021 | 2026 | Canada | Well → regasification (no combustion, GWP100) | no | yes | 0.80 |
| Roman-White et al. 2021 (Balcombe co-author) | 2021 | US Gulf Coast → China (Cheniere SPL) | Well → regasification (no combustion, GWP100) | no | yes | 0.94–1.51 (expected 1.19) |
| This model, aligned to Balcombe 2016 LNG stages | 2026 | Canada | Liquefaction + shipping + regasification (GWP100) | no | yes | 0.45 |
| Balcombe et al. 2016 (LNG-stage literature range) | 2016 | Global compilation | Liquefaction + tanker + regasification (not upstream) | no | yes | 0.62–1.71 |
| Howarth 2024 | 2024 | US shale LNG exports | Well → combustion, GWP20 (not GWP100) | yes | yes | 7.37–8.03 |

This model's export-chain GWP100 is 3.55 t/t (well-to-regas 0.80; liquefaction+shipping+regas 0.45). Liquefaction remains 0.29. Howarth's GWP100 totals are only in supplemental figures and are not converted here. Howarth also includes destination transmission methane that this model does not.

Excluded (boundary not an LNG lifecycle, or not determined):

- **MacKay et al. 2021:** 6,650-site methane measurements in western Canada. No LNG system boundary and no lifecycle total.
- **Johnson et al. 2023:** Alberta measurement inventory of oil and gas methane. No LNG system boundary and no lifecycle total.
- **Di Lullo et al.:** Published work is a transmission-pipeline LCA (construction/operation/decommissioning) and crude WTT studies. No LNG well-to-wire or well-to-combustion total with a readable boundary.

Figure: `Outputs/figures/fig10_lca_comparison.png`.
