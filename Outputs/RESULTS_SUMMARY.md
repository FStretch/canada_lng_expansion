# Canada LNG lifecycle emissions — review summary

Default scenario: `measurement_central`. Run at 2026-08-29 09:13 UTC. Numbers to one decimal. Inputs read-only. `calc_group` from `Asset Register:calc_group`.

Deck-facing tables (one sheet per table, 1-decimal): `Outputs/SLIDE_TABLES.xlsx`. Send that workbook to the PPT chat.

## 1. Headline

- **Annual total (panel peak):** 298.7 MtCO2e in 2037 (10 assets emitting that year)
- **life_average_annual_mt:** 258.9 MtCO2e/yr (mean utilisation over each asset's operating window; not a calendar year)
- **Lifetime total (calendar panel 2025–2069):** 9315.3 MtCO2e (headline scope; remaining years from 2025, not duration × life-average)
- **Headline capacity (export chain only):** 100.1 mtpa (liquefaction; not summed with import regasification or other chains)
- **Scope:** Headline results include assets whose chain is in headline_scope_chains and whose calc_group is in headline_scope_calc_groups (export / operating,under_construction,proposed). Excluded 8 in-total non-export assets totalling 242.9 MtCO2e on the full-register panel (2.5% of the all-assets 9558.2 Mt). They remain in the register.

| chain | mtpa |
|---|---|
| export | 100.1 |

- **Scope 1+2:** 46.7 MtCO2e/yr (18.0%)  |  **Scope 3:** 212.2 MtCO2e/yr (82.0%)
- **Territorial:** CAN 46.7 (18.0%)  |  BUNK 8.8 (3.4%)  |  FOR 203.5 (78.6%)
- **Share of remaining carbon budget (GCB 2025, from start of 2026), on the CO2-only lifetime of 8,967.2 MtCO2:** 1.5°C, 50% from start of 2026 5.3% of 170 GtCO2  |  1.7°C, 50% from start of 2026 1.7% of 525 GtCO2  |  2.0°C, 50% from start of 2026 0.8% of 1055 GtCO2. This is **like for like**: CO2 against a CO2 budget. Residual caveats: pipeline fugitive methane is not split out of the CO2 total, and non-CO2 gases other than CH4 are not counted. On the older GWP100 CO2e basis the same shares are 5.5%  |  1.8%  |  0.9%.

## 2. By group

| calc_group | export mtpa | life_average_annual_mt | Lifecycle Mt | CAN / BUNK / FOR Mt/yr |
|---|---|---|---|---|
| operating | 14.0 | 40.9 | 1309.6 | 7.4 / 1.4 / 32.2 |
| under_construction | 5.4 | 15.8 | 559.9 | 2.8 / 0.5 / 12.4 |
| proposed | 80.7 | 202.2 | 7445.8 | 36.5 / 6.8 / 158.9 |

Capacity by chain within each calc_group (not summed across chains):

| calc_group | export | bunkering | domestic | import |
|---|---|---|---|---|
| operating | 14.0 | 0.0 | 0.0 | 0.0 |
| under_construction | 5.4 | 0.0 | 0.0 | 0.0 |
| proposed | 80.7 | 0.0 | 0.0 | 0.0 |

### Proposed: advanced vs early (tier split)

| tier | chain scope | mtpa | life_average_annual_mt | CAN / BUNK / FOR |
|---|---|---|---|---|
| advanced_proposed | export | 26.0 | 62.8 | 11.3 / 2.1 / 49.4 |
| early_proposed | export | 54.7 | 139.4 | 25.1 / 4.7 / 109.5 |

## 3. By chain

| chain | stages | mtpa | life_average_annual_mt | Lifecycle Mt | CAN / BUNK / FOR |
|---|---|---|---|---|---|
| export | upstream_production@CAN → pipeline_transport@CAN → liquefaction@CAN → shipping@BUNK → regasification@FOR → combustion@FOR | 100.1 | 258.9 | 9315.3 | 46.7 / 8.8 / 203.5 |

## 4. By project

| project | mtpa | chain | calc_group | tier | drive | life (source) | effective Mt/yr | annual Mt/yr | lifecycle Mt | CAN / BUNK / FOR | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| lng_canada_phase_1 | 14.0 | export | operating | operating | gas_turbine | 32 (Asset Register:authorised_export_end_year=2056 (hard stop; cuts 8y from Asset Register:authorised_export_term_years)) | 11.53 | 40.9 | 1309.6 | 7.4 / 1.4 / 32.2 |  |
| discovery_t1t4 | 20.0 | export | proposed | early_proposed | gas_turbine | 40 (Parameters:lifecycle_years_default) | 14.39 | 51.1 | 2043.9 | 9.2 / 1.7 / 40.2 |  |
| fermeuse_energy_flng | 5.0 | export | proposed | early_proposed | gas_turbine | 40 (Parameters:lifecycle_years_default) | 3.60 | 12.8 | 511.0 | 2.3 / 0.4 / 10.0 |  |
| kanata_lng | 12.0 | export | proposed | early_proposed | gas_turbine | 40 (Parameters:lifecycle_years_default) | 8.64 | 30.7 | 1226.3 | 5.5 / 1.0 / 24.1 |  |
| ksi_lisims_lng | 12.0 | export | proposed | advanced_proposed | gas_turbine | 35 (Asset Register:authorised_export_end_year=2063 (hard stop; cuts 5y from Asset Register:authorised_export_term_years)) | 8.43 | 29.9 | 1047.6 | 5.4 / 1.0 / 23.5 |  |
| lng_canada_phase_2 | 14.0 | export | proposed | advanced_proposed | gas_turbine | 27 (Asset Register:authorised_export_end_year=2056 (hard stop; cuts 13y from Asset Register:authorised_export_term_years)) | 9.27 | 32.9 | 888.6 | 5.9 / 1.1 / 25.9 |  |
| marinvest_baie_comeau | 15.0 | export | proposed | early_proposed | gas_turbine | 40 (Parameters:lifecycle_years_default) | 10.80 | 38.3 | 1532.9 | 6.9 / 1.3 / 30.1 |  |
| summit_lake_pg_lng | 2.7 | export | proposed | early_proposed | gas_turbine | 30 (Asset Register:project_life_years) | 1.84 | 6.5 | 195.5 | 1.2 / 0.2 / 5.1 |  |
| cedar_lng | 3.3 | export | under_construction | under_construction | gas_turbine | 39 (Asset Register:authorised_export_end_year=2066 (hard stop; cuts 1y from Asset Register:authorised_export_term_years)) | 2.72 | 9.7 | 376.6 | 1.7 / 0.3 / 7.6 |  |
| woodfibre_lng | 2.1 | export | under_construction | under_construction | gas_turbine | 30 (Asset Register:authorised_export_end_year=2057 (hard stop; cuts 10y from Asset Register:authorised_export_term_years)) | 1.72 | 6.1 | 183.3 | 1.1 / 0.2 / 4.8 |  |

## Headline exclusion (retained in the register)

Headline results include assets whose chain is in headline_scope_chains and whose calc_group is in headline_scope_calc_groups (export / operating,under_construction,proposed). Combined excluded tonnage: **242.9 MtCO2e** (8 in-total assets; 10.4 Mt in the all-assets peak year 2037). Already out of totals: ['port_of_hamilton_lng'].

| project | chain | calc_group | start | mtpa | lifetime Mt | legacy |
|---|---|---|---:|---:|---:|---|
| tilbury_phase_2 | bunkering | proposed | — | 2.50 | 137.3 |  |
| tilbury_phase_1b | bunkering | proposed | 2028 | 0.65 | 63.4 |  |
| tilbury_phase_1a | bunkering | operating | 2018 | 0.25 | 23.5 |  |
| saint_john_import_facility | import | operating | 2009 | 7.50 | 12.6 |  |
| mt_hayes_lng | domestic | operating | 2011 | 0.06 | 4.5 |  |
| tamaska_fort_nelson_lng | domestic | operating | 2021 | 0.02 | 1.7 |  |
| tilbury_original | domestic | operating | 1971 | 0.03 | 0.0 | yes |
| energir_montreal_lng | domestic | operating | 1976 | 0.21 | 0.0 | yes |

| chain | n | mtpa | lifetime Mt |
|---|---:|---:|---:|
| bunkering | 3 | 3.4 | 224.2 |
| domestic | 4 | 0.3 | 6.1 |
| import | 1 | 7.5 | 12.6 |

## 5. By stage

| stage | destination | life_average_annual_mt | share |
|---|---|---|---|
| upstream_production | CAN | 18.2 | 7.0% |
| pipeline_transport | CAN | 7.3 | 2.8% |
| liquefaction | CAN | 21.1 | 8.2% |
| shipping | BUNK | 8.8 | 3.4% |
| regasification | FOR | 2.9 | 1.1% |
| combustion | FOR | 200.6 | 77.5% |

## 5a. Carbon dioxide and methane split

Every asset-year in the panel now carries `co2_mt`, `ch4_derived_co2e_mt` and `ch4_mass_kt`, with `emissions_mtco2e = co2_mt + ch4_derived_co2e_mt` exactly. The split uses only parameters already on the workbook. **Upstream:** CH4-derived CO2e per tonne LNG is the scenario upstream factor less the CO2 part of the official inventory (`inventory_as_reported x (1 - upstream_ch4_share)` = 0.154), i.e. 0.096 tCO2e/t at central. **Shipping:** the 1.44 carrier uplift is entirely measured methane slip, so `1 - 1/1.44` = 0.306 of the shipping CO2e is CH4-derived (0.037 tCO2e/t). **Pipeline transport, liquefaction, regasification and combustion are treated as CO2; pipeline fugitive methane is not split**, because the workbook carries a single pipeline factor with no methane share behind it. CO2e totals are unchanged by this task.

| slice | lifetime CO2e Mt | lifetime CO2-only Mt | CH4-derived CO2e Mt | CH4 mass kt | CH4 share of CO2e |
|---|---|---|---|---|---|
| committed (build_out) | 1,869.5 | 1,799.6 | 69.9 | 2,344 | 3.7% |
| committed_plus_advanced (build_out) | 3,805.7 | 3,663.5 | 142.2 | 4,773 | 3.7% |
| full (build_out) | 9,315.3 | 8,967.2 | 348.1 | 11,682 | 3.7% |
| operating (calc_group) | 1,309.6 | 1,260.7 | 48.9 | 1,642 | 3.7% |
| under_construction (calc_group) | 559.9 | 539.0 | 20.9 | 702 | 3.7% |
| proposed (calc_group) | 7,445.8 | 7,167.6 | 278.3 | 9,338 | 3.7% |

CH4 mass is CH4-derived CO2e divided by `gwp100_ch4` = 29.8. It is left blank for the `near_term_methane_gwp20` scenario, whose upstream factor is not a GWP100 CO2e figure (see below).

### Reconciliation with `near_term_methane_gwp20`

That scenario's lifetime is **9,525.2 Mt** with upstream at 0.33 and every other stage central. Rebuilding it from the Task 1 CH4 mass (`co2_mt + ch4_mass_kt/1000 x gwp20_ch4`, gwp20 = 82.5) gives **9,931.0 Mt**, **+4.3%** apart. That is well over 0.1%, so the two routes are reported rather than forced together. Two reasons, in order of size:

1. **The workbook's 0.33 is not a GWP20 re-weighting.** It is `inventory_as_reported x 1.5` = 0.22 x 1.5, the whole factor scaled. Re-weighting only the methane portion at GWP20 gives an upstream factor of 0.420, worth 445.5 Mt over the central case against the scenario's 209.9 the mass route lands at 9,760.8 Mt, still +2.5% apart.
2. **The scenario does not touch shipping.** The mass route re-weights shipping methane slip too, worth a further 170.2 Mt.

The repository README describes the GWP20 uplift as applying to "the methane portion of upstream and pipeline emissions only". **No pipeline methane portion is defined anywhere in the workbook**, and the code changes only the upstream factor, so the pipeline half of that sentence is not implemented. It is recorded here rather than invented. `near_term_methane_gwp20` remains a named scenario as the workbook defines it; the CH4-mass route is not substituted for it.

## 6. Scenario range

| scenario | upstream | life_average_annual_mt | Lifecycle Mt | CAN Mt/yr |
|---|---|---|---|---|
| inventory_as_reported | 0.22 | 256.7 | 9236.6 | 44.5 |
| measurement_central | 0.25 | 258.9 | 9315.3 | 46.7 |
| measurement_high | 0.26 | 259.6 | 9341.6 | 47.4 |
| near_term_methane_gwp20 | 0.33 | 264.7 | 9525.2 | 52.5 |
| howarth_high | 0.55 | 280.8 | 10102.5 | 68.6 |

## 7. Context

Canada territorial under `measurement_central` is **46.7 MtCO2e/yr**.

- **6.7%** of national inventory (694 Mt, inventory basis — excludes LULUCF).
- **11.2% to 10.3%** of the 2030 target range (417–455 Mt). Targets include land-use accounting; the 694 inventory figure does not.
- **23.3%** of the 2030 overshoot gap (200 Mt, projected emissions minus the target path).

## 8. Assumptions that move the number most

- **Upstream factor** (central 0.25): inventory_as_reported (0.22) → 256.7 Mt/yr (-2.2); howarth_high (0.55) → 280.8 Mt/yr (+21.9).
- **Lifespan** (default mostly 40 yr licence / Parameters default): sensitivity bounds in Parameters are 30 and 50 yr. Lifecycle total scales roughly with lifespan (~-25% at 30 yr, ~+25% at 50 yr on a pure scale basis). Annual changes only via the util_sum/life ratio and FID-delay share of the window. Legacy facilities (outlived design life) use steady-state util and report annual only.
- **FID delay** (`fid_delay_mid`=5 yr inside lifespan): applies to 7 projects (80.7 mtpa export), currently 202.2 Mt/yr. Removing the delay would raise their annual emissions by roughly the ratio of lost ramp years (order-of-magnitude: several Mt/yr on the proposed export slate).
- **Utilisation** (default steady-state 0.839; Phase 1 override 0.85; Saint John flat 0.025): annual emissions scale almost linearly with effective util. A +10% relative move in steady-state util moves the headline by about 25.9 Mt/yr if applied uniformly.
- **Liquefaction** (central 0.29 tCO2e/t, gas turbine for every terminal): electrification is not assumed (`liquefaction_electrification_assumed`=none). 0.12 is retained as range_low and applies only if electrification is contracted and delivered. Previous drive classifications are in `liquefaction_drive_note`.
- **Placeholder start year** (`assumed_first_export_year_if_missing`=2030): 5509.6 MtCO2e (59.1% of lifetime) from 5 assets with a blank `first_export_year`. The 2069 tail is entirely this fill. Sensitivity at 2033 and 2035 is tabulated below.
- **Liquefaction drive default** for remaining `not_published` (domestic) rows: `gas_turbine` → intensity 0.29 tCO2e/t from Emission Factors central.

## 9. Appendix · electrification counterfactual (Canada territorial)

Headline case is gas turbine for every terminal. The rows below ask what Canada-territorial LNG would be if liquefaction ran at the electric factor (0.12 instead of 0.29 tCO2e/t). Liquefaction is tagged CAN, so the whole delta is territorial. This does not change the headline totals.

| case | CAN Mt/yr | vs gas | share of 694 Mt inventory | share of 2030 target low |
|---|---|---|---|---|
| Gas turbine (current) | 46.7 | — | 6.7% | 11.2% |
| Claimed electric delivered | 40.8 | -5.9 | 5.9% | 9.8% |
| All terminals electric | 34.3 | -12.4 | 4.9% | 8.2% |

Claimed-electric assets (previous `electric_committed` / `electric_planned`): cedar_lng, ksi_lisims_lng, lng_canada_phase_2, marinvest_baie_comeau, summit_lake_pg_lng, woodfibre_lng.

| calc_group | gas | claimed electric | all electric |
|---|---|---|---|
| operating | 7.4 | 7.4 | 5.4 |
| under_construction | 2.8 | 2.1 | 2.1 |
| proposed | 36.5 | 31.3 | 26.8 |

Figure: `Outputs/figures/fig08_electrification_canada_territorial.png`.

## 10. Anything that looks wrong

- FINDING: tilbury_marine_jetty: chain=none — no lifecycle applies; excluded (not zeroed).
- Flag: port_of_hamilton_lng.capacity_mtpa=missing
- Excluded (chain=none or blank, not zeroed): ['tilbury_marine_jetty']
- Remaining carbon budgets (GCB 2025) are CO2 from the start of 2026. The paper's share-of-budget figures are now the **CO2-only** lifetime against those budgets, from the Task 1 per-gas split. Residual caveats: pipeline fugitive methane is not split out of the CO2 total, so a small amount of methane sits inside it; and non-CO2 gases other than CH4 (N2O, refrigerants) are not counted anywhere in the model.
- Reconciliations close within floating-point tolerance (1e-6 to 1e-3); no material rounding residuals.
- Saint John at ~0.5 Mt/yr depends entirely on `saint_john_utilisation=0.025`; nameplate at default util would be ~17 Mt/yr. tier=watch but calc_group=operating (operating import terminal).
- Tilbury Phase 2 (2.5 mtpa) sits on bunkering by register judgement (`chain_note`); NRCan lists it as export — classification is a stated judgement, not re-derived in code.
- Loss and damage central case is ECCC SC-CO2 at 2%, applied per calendar year to the full GWP100 CO2e total (`central_price_family=eccc`). That overstates methane (CH4-derived CO2e is charged at SC-CO2 rather than SC-CH4). Burke is an upper-bracket sensitivity (g = 0). Damages after 2100, sea-level rise, extremes and mortality outside GDP are omitted. The Conference Board denominator is Table 1 GDP in 2020 CAD, inflated to 2025 CAD.

## 11. Climate loss and damage (global)

Monetised economic damages from the modelled lifecycle emissions. The **central case** is ECCC official SC-CO2 at the **2%** discount rate, applied per calendar year of emissions, in 2025 CAD (named parameters `central_price_family=eccc`, `central_aggregation=calendar_year`). ECCC 1.5% and 2.5% are the central case's sensitivity range. Burke et al. (2026) is an **upper-bracket sensitivity** across discount rates and Figure 2e horizons (default g = 0; Hatton +2% is not used). Damages are **global**. They are not a legal bill. ECCC SC-CO2 is applied to the full GWP100 CO2e total. That **overstates** the methane contribution (CH4-derived CO2e is charged at SC-CO2 rather than at SC-CH4) and is not conservative in that direction. Construction, sea-level rise, extremes, and mortality outside GDP are omitted.

Methane share of the CO2e total is **3.7%** (348 of 9,315 MtCO2e). That is the excess of the central upstream factor (0.25) over inventory CO2 (0.154), i.e. 0.096 tCO2e per t LNG, as a share of the chain total. Pipeline and shipping methane stay inside CO2e as CO2 and are not in this share. GWP100 = 29.8; ECCC SC-CH4/SC-CO2 is 9.6 in 2025 and 16.7 by 2080. Pricing that methane CO2e as CO2 therefore charges it at roughly 3.1× the ECCC CH4 price in 2025. The resulting overstatement is **2.0%** of the central damage bill. This treatment overstates methane and is not conservative in that direction.

Implied average price is **$447/t** CAD 2025 (total damages / lifetime tonnes). That is the emissions-weighted mean of the ECCC 2% schedule after a **single** CAD 2021→2025 inflation of 1.1535 (deflators 124.81689 / 143.98050). The unweighted mean of the same series over panel years is $434/t. In CAD 2021 the weighted mean is $387/t (2025 official schedule value is $271/t). Prices are looked up on the **calendar year of emission**. 45% of lifetime tonnes are after 2050, so the weighted mean sits above the 2037 peak-year price. Year table: `Outputs/figure_data/ld_price_by_year.csv`.

- **Central (ECCC 2%, calendar year), all in-scope:** **$4.2 trillion** (operating $526 billion  |  under construction $240 billion  |  proposed $3.4 trillion)
- **Central sensitivity (ECCC 1.5%–2.5%, calendar year):** $2.8 trillion to $6.5 trillion
- **ECCC 2% NPV to 2025 (sensitivity, not central):** $2.6 trillion (proposed $2.0 trillion)
- **Burke upper bracket (g = 0, year-by-year 2100 path, 1.5%–5%):** $4.5 trillion to $20.7 trillion; Figure 2e through-2300 at 2% fixed: **$51.0 trillion** (proposed $40.7 trillion)
- **Canadian value (proposed, CBoC scaled, 40 yr, 2025 CAD):** **$799 billion**
- **Externality ratio, ECCC central (proposed):** **4.3x** global damages / Canadian value (Hatton UK range was 5.9x–16.8x; Burke through-2300 is 51x)
- **Canada Burke-channel victim share (sensitivity, not central):** **0.17%** of a 1990 1 Gt pulse, so it externalises 99.8% ($69 billion borne at the through-2300 2% price)
- **National test, Burke channel only (not the headline):** Canadian value is 11.5x the damages Canada itself bears. Reported as indeterminate.
- **30-year denominator sensitivity (ECCC central, proposed):** $599 billion Canadian value, ratio **6x** (research sketch used 30 years; central uses 40).
- **Operating + under construction only (ECCC central):** $765 billion global L&D / $192 billion value = **4x** (19.4 mtpa export).

Burke Figure 4 sankey (`damages_and_benefits_k90.rds`) is emitter/recipient flows for 1990–2020 **all** emissions, not LNG. Canada as emitter caused **$1.33 trillion** (2.40% of global owing; USA $10.18T validates against the paper's $10.2T). Canada is **not** a plotted recipient, so CAN-on-CAN cannot be read from this file. Victim share stays 0.17% from the 1 Gt pulse.

Canada denominator: Conference Board *A Rising Tide* Table 1, Canada GDP at market prices **C$11.153bn/yr (2020 CAD)** at 56 mtpa, scaled linearly on proposed export nameplate (80.7 mtpa) over 40 years (Appendix A operating life). Whole-chain including upstream (76% of the GDP). Industry-commissioned. Inflated to 2025 CAD with FRED NGDPDIXCAA. Uninflated 2020 CAD value is $643 billion.

Burke horizon rows (g = 0, proposed slate; upper bracket, not central). Global L&D and value in trillion 2025 CAD; Canada-borne in billion 2025 CAD. Bold is the Burke default horizon, not the paper central.

| horizon | discounting | SC USD2020/t | global L&D (tn) | value (tn) | ratio | Canada-borne (bn) |
|---|---|---|---|---|---|---|
| through_2100 | 2pct_fixed | 1,013 | 12.9 | 0.80 | 16x | 22.0 |
| no_growth_after_2100 | 2pct_fixed | 2,120 | 27.0 | 0.80 | 34x | 46.0 |
| **through_2300** | 2pct_fixed | 3,198 | **40.7** | 0.80 | **51x** | 69.4 |
| through_2100 | ramsey | 1,322 | 16.8 | 0.80 | 21x | 28.7 |
| no_growth_after_2100 | ramsey | 4,045 | 51.5 | 0.80 | 64x | 87.8 |
| through_2300 | ramsey | 7,056 | 89.9 | 0.80 | 112x | 153.2 |

Burke through-2100 year-by-year path, g bracket (trillion 2025 CAD, all / proposed). Burke default g = 0; +2% is Hatton's headline and is not used.

| discount | g=−2% | g=0% | g=+2% |
|---|---|---|---|
| 1.5% | 11.7 / 9.0 | 20.7 / 16.5 | 37.7 / 31.1 |
| 2% | 9.1 / 7.0 | **16.1 / 12.9** | 29.4 / 24.2 |
| 3% | 5.7 / 4.4 | 10.1 / 8.1 | 18.4 / 15.2 |
| 5% | 2.6 / 2.0 | 4.5 / 3.6 | 8.2 / 6.8 |

Figure: `Outputs/figures/fig09_loss_damage_by_group.png`.

## Placeholder start-year sensitivity

Parameter `assumed_first_export_year_if_missing` = **2030** (Parameters sheet). Six in-scope assets have a blank `first_export_year`. With licence-end stops on licensed terminals, every dated end year is 2056–2066; the panel tail is entirely this placeholder.

Placeholder-start assets account for **5509.6 MtCO2e** (59.1% of the 9315.3 Mt lifetime total).

| project | mtpa | lifetime Mt | share of lifetime | last year |
|---|---|---|---|---|
| discovery_t1t4 | 20.0 | 2043.9 | 21.9% | 2069 |
| marinvest_baie_comeau | 15.0 | 1532.9 | 16.5% | 2069 |
| kanata_lng | 12.0 | 1226.3 | 13.2% | 2069 |
| fermeuse_energy_flng | 5.0 | 511.0 | 5.5% | 2069 |
| summit_lake_pg_lng | 2.7 | 195.5 | 2.1% | 2059 |

| start year | lifetime Mt | peak year | peak Mt | last year | central damage CAD bn |
|---|---|---|---|---|---|
| 2030 (central) | 9315.3 | 2037 | 298.7 | 2069 | 4164 |
| 2033 | 9315.3 | 2040 | 298.7 | 2072 | 4252 |
| 2035 | 9315.3 | 2042 | 298.7 | 2074 | 4310 |

## Monte Carlo (physics sampled, ECCC 2% applied after)

10,000 draws, seed `20260828`. Physics 0.12s; pricing 0.02s. Kernel vs published panel max abs 1.8e-15 Mt. Liquefaction held at 0.29. Howarth 0.55 is a named point, not a draw. Draws are on the headline scope (export chain).

| build-out | lifetime median [p5, p95] Mt | peak-year median [p5, p95] Mt | ECCC 2% damage median [p5, p95] CAD bn |
|---|---|---|---|
| committed | 1903.6 [1800.2, 2011.3] | 59.4 [56.2, 62.8] | 779 [737, 823] |
| committed_plus_advanced | 3874.0 [3641.4, 4123.9] | 138.2 [130.7, 146.1] | 1642 [1546, 1745] |
| full | 9477.1 [8290.3, 10752.6] | 304.1 [287.6, 321.3] | 4236 [3625, 4915] |

Howarth 0.55 (other stages central, not inside the interval):

| build-out | lifetime Mt | peak year / Mt | ECCC 2% CAD bn |
|---|---|---|---|
| committed | 2027.5 | 2030 / 63.3 | 830 |
| committed_plus_advanced | 4127.4 | 2037 / 147.2 | 1749 |
| full | 10102.5 | 2037 / 323.9 | 4516 |

Central case versus Monte Carlo median (full build-out):

| quantity | central case | Monte Carlo median [p5, p95] |
|---|---|---|
| Lifetime (Mt) | 9315.3 | 9477.1 [8290.3, 10752.6] |
| Peak-year (Mt) | 298.7 in 2037 | 304.1 [287.6, 321.3] |
| ECCC 2% damage (CAD bn) | 4164 | 4236 [3625, 4915] |

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
