# Canada LNG lifecycle emissions — review summary

Default scenario: `measurement_central`. Run at 2026-09-03 12:12 UTC. Numbers to one decimal. Inputs read-only. `calc_group` from `Asset Register:calc_group`.

Deck-facing tables (one sheet per table, 1-decimal): `Outputs/SLIDE_TABLES.xlsx`. Send that workbook to the PPT chat.

## Paper set

Decision taken 29 August 2026. The paper reports the **central case** — the point estimate from the central factor values — with the Monte Carlo **5th to 95th percentile** as its interval. The Monte Carlo median is stated once, in its own column, and is not the reported figure.

| build-out | lifetime CO2e Mt | lifetime CO2-only Mt | peak | ECCC 2% damages CAD bn | MC median (lifetime / peak / damages)¹ |
|---|---|---|---|---|---|
| committed | **1,845.8** [1,810.5, 2,004.6] | **1,781.7** [1,733.1, 1,900.5] | **57.6** in 2030 [56.5, 62.5] | **741** [724, 796] | 1,901.2 / 59.3 / 757 |
| committed_plus_advanced | **3,757.5** [3,603.8, 4,055.5] | **3,627.1** [3,446.3, 3,850.5] | **134.0** in 2037 [131.5, 145.6] | **1,561** [1,497, 1,669] | 3,820.0 / 138.1 / 1,578 |
| full | **7,162.0** [6,493.9, 8,074.8] | **6,918.1** [6,196.6, 7,680.0] | **235.6** in 2037 [231.1, 255.6] | **3,108** [2,761, 3,548] | 7,257.1 / 242.5 / 3,135 |

¹ The Monte Carlo median sits **above** the central case (7,257.1 against 7,162.0 Mt at full buildout) because the sampled stage triangles are right-skewed — shipping 0.05 / 0.12 / 0.31 especially, where the central 0.12 sits well below the midpoint of the range. The median of a right-skewed draw is not the point estimate from central values. Both are reported; only the central case is the paper's number.

Membership: **committed** = committed (operating + under construction) (3 assets); **committed_plus_advanced** = committed plus advanced (+ tier advanced_proposed) (5 assets); **full** = full (every headline-scope asset) (9 assets). Interval basis: Monte Carlo p5-p95, 10000 draws, seed 20260828.

### Territorial split and carbon-budget shares

Territorial shares are the life-average split. Budget shares are the **CO2-only** lifetime against the GCB 2025 remaining CO2 budgets from the start of 2026, like for like.

| build-out | CAN % | BUNK % | FOR % | 1.5°C (170 GtCO2) | 1.7°C (525) | 2.0°C (1,055) |
|---|---|---|---|---|---|---|
| committed | 17.5 | 3.4 | 79.1 | 1.05% | 0.34% | 0.17% |
| committed_plus_advanced | 17.5 | 3.4 | 79.1 | 2.13% | 0.69% | 0.34% |
| full | 17.6 | 3.2 | 79.2 | 4.07% | 1.32% | 0.66% |

Locked in `build_results.py` as `EXPECTED_BUILD_OUT`; the run asserts every cell of the central column. Machine-readable copy: `Outputs/figure_data/paper_set.csv`.

## 1. Headline

- **Annual total (panel peak):** 235.6 MtCO2e in 2037 (9 assets emitting that year)
- **life_average_annual_mt:** 204.7 MtCO2e/yr (mean utilisation over each asset's operating window; not a calendar year)
- **Lifetime total (calendar panel 2025–2069):** 7162.0 MtCO2e (headline scope; remaining years from 2025, not duration × life-average)
- **Headline capacity (export chain only):** 80.1 mtpa (liquefaction; not summed with import regasification or other chains)
- **Scope:** Headline results include assets whose chain is in headline_scope_chains and whose calc_group is in headline_scope_calc_groups (export / operating,under_construction,proposed). Excluded 8 in-total non-export assets totalling 241.0 MtCO2e on the full-register panel (3.3% of the all-assets 7403.1 Mt). They remain in the register.

| chain | mtpa |
|---|---|
| export | 80.1 |

- **Scope 1+2:** 35.9 MtCO2e/yr (17.6%)  |  **Scope 3:** 168.8 MtCO2e/yr (82.4%)
- **Territorial:** CAN 35.9 (17.6%)  |  BUNK 6.6 (3.2%)  |  FOR 162.2 (79.2%)
- **Share of remaining carbon budget (GCB 2025, from start of 2026), on the CO2-only lifetime of 6,918.1 MtCO2:** 1.5°C, 50% from start of 2026 4.1% of 170 GtCO2  |  1.7°C, 50% from start of 2026 1.3% of 525 GtCO2  |  2.0°C, 50% from start of 2026 0.7% of 1055 GtCO2. This is **like for like**: CO2 against a CO2 budget. Residual caveats: pipeline fugitive methane is not split out of the CO2 total, and non-CO2 gases other than CH4 are not counted. On the older GWP100 CO2e basis the same shares are 4.2%  |  1.4%  |  0.7%.

## 2. By group

| calc_group | export mtpa | life_average_annual_mt | Lifecycle Mt | CAN / BUNK / FOR Mt/yr |
|---|---|---|---|---|
| operating | 14.0 | 40.4 | 1293.0 | 7.1 / 1.4 / 31.9 |
| under_construction | 5.4 | 15.6 | 552.8 | 2.7 / 0.5 / 12.3 |
| proposed | 60.7 | 148.8 | 5316.3 | 26.1 / 4.7 / 118.0 |

Capacity by chain within each calc_group (not summed across chains):

| calc_group | export | bunkering | domestic | import |
|---|---|---|---|---|
| operating | 14.0 | 0.0 | 0.0 | 0.0 |
| under_construction | 5.4 | 0.0 | 0.0 | 0.0 |
| proposed | 60.7 | 0.0 | 0.0 | 0.0 |

### Proposed: advanced vs early (tier split)

| tier | chain scope | mtpa | life_average_annual_mt | CAN / BUNK / FOR |
|---|---|---|---|---|
| advanced_proposed | export | 26.0 | 62.0 | 10.9 / 2.1 / 49.1 |
| early_proposed | export | 34.7 | 86.7 | 15.3 / 2.6 / 68.9 |

## 3. By chain

| chain | stages | mtpa | life_average_annual_mt | Lifecycle Mt | CAN / BUNK / FOR |
|---|---|---|---|---|---|
| export | upstream_production@CAN → pipeline_transport@CAN → liquefaction@CAN → shipping@BUNK → regasification@FOR → combustion@FOR | 80.1 | 204.7 | 7162.0 | 35.9 / 6.6 / 162.2 |

## 4. By project

| project | mtpa | chain | calc_group | tier | drive | life (source) | effective Mt/yr | annual Mt/yr | lifecycle Mt | CAN / BUNK / FOR | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| lng_canada_phase_1 | 14.0 | export | operating | operating | gas_turbine | 32 (Asset Register:authorised_export_end_year=2056 (hard stop; cuts 8y from Asset Register:authorised_export_term_years)) | 11.53 | 40.4 | 1293.0 | 7.1 / 1.4 / 31.9 |  |
| fermeuse_energy_flng | 5.0 | export | proposed | early_proposed | gas_turbine | 40 (Parameters:lifecycle_years_default) | 3.60 | 12.5 | 498.4 | 2.2 / 0.3 / 10.0 |  |
| kanata_lng | 12.0 | export | proposed | early_proposed | gas_turbine | 40 (Parameters:lifecycle_years_default) | 8.64 | 30.3 | 1210.8 | 5.3 / 1.0 / 23.9 |  |
| ksi_lisims_lng | 12.0 | export | proposed | advanced_proposed | gas_turbine | 35 (Asset Register:authorised_export_end_year=2063 (hard stop; cuts 5y from Asset Register:authorised_export_term_years)) | 8.43 | 29.6 | 1034.3 | 5.2 / 1.0 / 23.4 |  |
| lng_canada_phase_2 | 14.0 | export | proposed | advanced_proposed | gas_turbine | 27 (Asset Register:authorised_export_end_year=2056 (hard stop; cuts 13y from Asset Register:authorised_export_term_years)) | 9.27 | 32.5 | 877.4 | 5.7 / 1.1 / 25.7 |  |
| marinvest_baie_comeau | 15.0 | export | proposed | early_proposed | gas_turbine | 40 (Parameters:lifecycle_years_default) | 10.80 | 37.6 | 1502.3 | 6.6 / 1.0 / 29.9 |  |
| summit_lake_pg_lng | 2.7 | export | proposed | early_proposed | gas_turbine | 30 (Asset Register:project_life_years) | 1.84 | 6.4 | 193.0 | 1.1 / 0.2 / 5.1 |  |
| cedar_lng | 3.3 | export | under_construction | under_construction | gas_turbine | 39 (Asset Register:authorised_export_end_year=2066 (hard stop; cuts 1y from Asset Register:authorised_export_term_years)) | 2.72 | 9.5 | 371.8 | 1.7 / 0.3 / 7.5 |  |
| woodfibre_lng | 2.1 | export | under_construction | under_construction | gas_turbine | 30 (Asset Register:authorised_export_end_year=2057 (hard stop; cuts 10y from Asset Register:authorised_export_term_years)) | 1.72 | 6.0 | 181.0 | 1.1 / 0.2 / 4.8 |  |

## Headline exclusion (retained in the register)

Headline results include assets whose chain is in headline_scope_chains and whose calc_group is in headline_scope_calc_groups (export / operating,under_construction,proposed). Combined excluded tonnage: **241.0 MtCO2e** (8 in-total assets; 10.3 Mt in the all-assets peak year 2037). Already out of totals: ['port_of_hamilton_lng'].

| project | chain | calc_group | start | mtpa | lifetime Mt | legacy |
|---|---|---|---:|---:|---:|---|
| tilbury_phase_2 | bunkering | proposed | — | 2.50 | 136.3 |  |
| tilbury_phase_1b | bunkering | proposed | 2028 | 0.65 | 62.9 |  |
| tilbury_phase_1a | bunkering | operating | 2018 | 0.25 | 23.3 |  |
| saint_john_import_facility | import | operating | 2009 | 7.50 | 12.5 |  |
| mt_hayes_lng | domestic | operating | 2011 | 0.06 | 4.4 |  |
| tamaska_fort_nelson_lng | domestic | operating | 2021 | 0.02 | 1.6 |  |
| tilbury_original | domestic | operating | 1971 | 0.03 | 0.0 | yes |
| energir_montreal_lng | domestic | operating | 1976 | 0.21 | 0.0 | yes |

| chain | n | mtpa | lifetime Mt |
|---|---:|---:|---:|
| bunkering | 3 | 3.4 | 222.5 |
| domestic | 4 | 0.3 | 6.1 |
| import | 1 | 7.5 | 12.5 |

## 5. By stage

| stage | destination | life_average_annual_mt | share |
|---|---|---|---|
| upstream_production | CAN | 14.6 | 7.1% |
| pipeline_transport | CAN | 4.3 | 2.1% |
| liquefaction | CAN | 17.0 | 8.3% |
| shipping | BUNK | 6.6 | 3.2% |
| regasification | FOR | 1.2 | 0.6% |
| combustion | FOR | 161.0 | 78.6% |

## 5a. Carbon dioxide and methane split

Every asset-year in the panel now carries `co2_mt`, `ch4_derived_co2e_mt` and `ch4_mass_kt`, with `emissions_mtco2e = co2_mt + ch4_derived_co2e_mt` exactly. The split uses only parameters already on the workbook. **Upstream:** CH4-derived CO2e per tonne LNG is the scenario upstream factor less the CO2 part of the official inventory (`inventory_as_reported x (1 - upstream_ch4_share)` = 0.154), i.e. 0.096 tCO2e/t at central. **Shipping:** the 1.44 carrier uplift is entirely measured methane slip, so `1 - 1/1.44` = 0.306 of the shipping CO2e is CH4-derived (0.037 tCO2e/t). **Pipeline transport, liquefaction, regasification and combustion are treated as CO2; pipeline fugitive methane is not split**, because the workbook carries a single pipeline factor with no methane share behind it. CO2e totals are unchanged by this task.

| slice | lifetime CO2e Mt | lifetime CO2-only Mt | CH4-derived CO2e Mt | CH4 mass kt | CH4 share of CO2e |
|---|---|---|---|---|---|
| committed (build_out) | 1,845.8 | 1,781.7 | 64.1 | 2,150 | 3.5% |
| committed_plus_advanced (build_out) | 3,757.5 | 3,627.1 | 130.4 | 4,377 | 3.5% |
| full (build_out) | 7,162.0 | 6,918.1 | 243.9 | 8,186 | 3.4% |
| operating (calc_group) | 1,293.0 | 1,248.1 | 44.9 | 1,506 | 3.5% |
| under_construction (calc_group) | 552.8 | 533.6 | 19.2 | 644 | 3.5% |
| proposed (calc_group) | 5,316.3 | 5,136.4 | 179.9 | 6,036 | 3.4% |

CH4 mass is CH4-derived CO2e divided by `gwp100_ch4` = 29.8. It is left blank for the `near_term_methane_gwp20` scenario, whose upstream factor is not a GWP100 CO2e figure (see below).

### Reconciliation with `near_term_methane_gwp20`

That scenario's lifetime is **7,455.0 Mt** with upstream at 0.393 and every other stage central. The workbook now re-weights only the methane portion of upstream: non-methane inventory stays at 0.22 × (1 − upstream_ch4_share), and the methane portion is multiplied by 1.5 then by gwp20/gwp100 (82.5/29.8). Rebuilding from the Task 1 CH4 mass (`co2_mt + ch4_mass_kt/1000 x gwp20_ch4`, gwp20 = 82.5) gives **7,593.5 Mt**, **+1.9%** apart. The remaining gap is shipping methane slip, which the named scenario does not re-weight (130.0 Mt). The two routes are reported rather than forced together.

The CH4-mass route's implied methane-only GWP20 upstream factor is 0.400, against the workbook's 0.393. They differ because the workbook starts from the inventory factor and an assumed 30% methane share, while the mass route starts from the central-case CH4 mass (inventory CO2 plus the 1.5× methane correction already in `measurement_central`). **No pipeline methane portion is defined anywhere in the workbook**, so pipeline is not re-weighted. `near_term_methane_gwp20` remains a named scenario as the workbook defines it; the CH4-mass route is not substituted for it.

## 6. Scenario range

| scenario | upstream | life_average_annual_mt | Lifecycle Mt | CAN Mt/yr |
|---|---|---|---|---|
| inventory_as_reported | 0.220 | 203.0 | 7100.6 | 34.2 |
| measurement_central | 0.250 | 204.7 | 7162.0 | 35.9 |
| measurement_high | 0.260 | 205.3 | 7182.5 | 36.5 |
| near_term_methane_gwp20 | 0.393 | 213.1 | 7455.0 | 44.3 |
| howarth_high | 0.550 | 222.3 | 7776.5 | 53.5 |

## 7. Context

Canada territorial under `measurement_central` is **35.9 MtCO2e/yr**.

- **5.2%** of national inventory (694 Mt, inventory basis — excludes LULUCF).
- **8.6% to 7.9%** of the 2030 target range (417–455 Mt). Targets include land-use accounting; the 694 inventory figure does not.
- **18.0%** of the 2030 overshoot gap (200 Mt, projected emissions minus the target path).

## 8. Assumptions that move the number most

- **Upstream factor** (central 0.25): inventory_as_reported (0.22) → 203.0 Mt/yr (-1.8); howarth_high (0.55) → 222.3 Mt/yr (+17.6).
- **Lifespan** (default mostly 40 yr licence / Parameters default): sensitivity bounds in Parameters are 30 and 50 yr. Lifecycle total scales roughly with lifespan (~-25% at 30 yr, ~+25% at 50 yr on a pure scale basis). Annual changes only via the util_sum/life ratio and FID-delay share of the window. Legacy facilities (outlived design life) use steady-state util and report annual only.
- **FID delay** (`fid_delay_mid`=5 yr inside lifespan): applies to 6 projects (60.7 mtpa export), currently 148.8 Mt/yr. Removing the delay would raise their annual emissions by roughly the ratio of lost ramp years (order-of-magnitude: several Mt/yr on the proposed export slate).
- **Utilisation** (default steady-state 0.839; Phase 1 override 0.85; Saint John flat 0.025): annual emissions scale almost linearly with effective util. A +10% relative move in steady-state util moves the headline by about 20.5 Mt/yr if applied uniformly.
- **Liquefaction** (central 0.29 tCO2e/t, gas turbine for every terminal): electrification is not assumed (`liquefaction_electrification_assumed`=none). 0.12 is retained as range_low and applies only if electrification is contracted and delivered. Previous drive classifications are in `liquefaction_drive_note`.
- **Placeholder start year** (`assumed_first_export_year_if_missing`=2030): 3404.6 MtCO2e (47.5% of lifetime) from 4 assets with a blank `first_export_year`. The 2069 tail is entirely this fill. Sensitivity at 2033 and 2035 is tabulated below.
- **Liquefaction drive default** for remaining `not_published` (domestic) rows: `gas_turbine` → intensity 0.29 tCO2e/t from Emission Factors central.

## 9. Appendix · electrification counterfactual (Canada territorial)

Headline case is gas turbine for every terminal. The rows below ask what Canada-territorial LNG would be if liquefaction ran at the electric factor (0.15 instead of 0.29 tCO2e/t). Liquefaction is tagged CAN, so the whole delta is territorial. This does not change the headline totals.

| case | CAN Mt/yr | vs gas | share of 694 Mt inventory | share of 2030 target low |
|---|---|---|---|---|
| Gas turbine (current) | 35.9 | — | 5.2% | 8.6% |
| Claimed electric delivered | 31.1 | -4.9 | 4.5% | 7.5% |
| All terminals electric | 27.7 | -8.2 | 4.0% | 6.7% |

Claimed-electric assets (previous `electric_committed` / `electric_planned`): cedar_lng, ksi_lisims_lng, lng_canada_phase_2, marinvest_baie_comeau, summit_lake_pg_lng, woodfibre_lng.

| calc_group | gas | claimed electric | all electric |
|---|---|---|---|
| operating | 7.1 | 7.1 | 5.5 |
| under_construction | 2.7 | 2.1 | 2.1 |
| proposed | 26.1 | 21.9 | 20.2 |

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

Monetised economic damages from the modelled lifecycle emissions. The **central case** is ECCC official SC-CO2 **and SC-CH4** at the **2%** discount rate, applied per calendar year of emissions, in 2025 CAD (named parameters `central_price_family=eccc`, `central_aggregation=calendar_year`). Each year's damage is `co2_t x SC-CO2_t + ch4_mass_t x SC-CH4_t`, from the Task 1 per-gas split, both schedules at the same discount rate and both inflated CAD 2021 to CAD 2025 exactly once. ECCC 1.5% and 2.5% are the central case's sensitivity range. Burke et al. (2026) is an **upper-bracket sensitivity** across discount rates and Figure 2e horizons (default g = 0; Hatton +2% is not used); **Burke has no SC-CH4, so the Burke family prices the whole GWP100 CO2e total at Burke's SC-CO2**. Damages are **global**. They are not a legal bill. Construction, sea-level rise, extremes, and mortality outside GDP are omitted.

**Per-gas pricing.** The panel splits every asset-year into CO2 and CH4 (see section 5a). Central lifetime is 6,918 MtCO2 plus 8,186 kt CH4, the latter worth 244 MtCO2e at GWP100 = 29.8, i.e. **3.4%** of the 7,162 MtCO2e total. The CH4 is the upstream excess over inventory CO2 (0.25 less 0.165 = 0.085 tCO2e per t LNG) plus shipping methane slip. Pipeline fugitive methane is not split and stays inside the CO2 total. CO2 is priced at SC-CO2 and CH4 mass at ECCC SC-CH4 (SC-CH4/SC-CO2 is 9.6 in 2025 and 16.7 by 2080, against GWP100 of 29.8). Methane is **1.6%** of the central damage bill ($49 billion), CO2 the rest ($3.1 trillion).

Reconciliation with the retired treatment: pricing the whole GWP100 CO2e total at SC-CO2 would have given $3.2 trillion, **+1.9%** against the per-gas figure. The overstatement-bound machinery it supported is retired.

Implied average price is **$434/t** CAD 2025 (total damages / lifetime CO2e tonnes; an effective blended rate across CO2 at SC-CO2 and CH4 at SC-CH4, not a schedule value). The underlying SC-CO2 series is the emissions-weighted mean of the ECCC 2% schedule after a **single** CAD 2021→2025 inflation of 1.1535 (deflators 124.81689 / 143.98050). The unweighted mean of the same series over panel years is $434/t. In CAD 2021 the weighted mean is $383/t (2025 official schedule value is $271/t). Prices are looked up on the **calendar year of emission**. 42% of lifetime tonnes are after 2050, so the weighted mean sits above the 2037 peak-year price. Year table: `Outputs/figure_data/ld_price_by_year.csv`.

- **Central (ECCC 2%, calendar year), all in-scope:** **$3.1 trillion** (operating $508 billion  |  under construction $232 billion  |  proposed $2.4 trillion)
- **Central sensitivity (ECCC 1.5%–2.5%, calendar year):** $2.1 trillion to $4.9 trillion
- **ECCC 2% NPV to 2025 (sensitivity, not central):** $1.9 trillion (proposed $1.4 trillion)
- **Burke upper bracket (whole CO2e at Burke SC-CO2, no SC-CH4; g = 0, year-by-year 2100 path, 1.5%–5%):** $3.5 trillion to $15.9 trillion; Figure 2e through-2300 at 2% fixed: **$39.2 trillion** (proposed $29.1 trillion)
- **Canada Burke-channel victim share (sensitivity, not central):** **0.17%** of a **1990** 1 Gt pulse, future window, so it externalises 99.8% ($50 billion borne at the through-2300 2% price). Alongside it, **P_dam_FD = 0.41**: the share of Burke draws in which Canada's damage from that pulse is positive. Only 41 per cent of draws put Canada in net loss at all, against 0.33 on the historical window and 0.98 for the United States and China. The 0.17% is a mean over a distribution that is not reliably signed for Canada, and should be read with the P_dam figure attached.

**Pulse year: only the 1990 pulse is available.** The paper's emissions are 2025 onward, so the natural question is Canada's share of a **2020** pulse. It cannot be computed from the replication package. `burke_country_damage_shares.csv` in this repository holds one row per country and is derived from the package's `1gtco2_damages_1990_2020.rds` and `1gtco2_damages_2020_2100.rds`; the script that writes both (`scripts/working/figures/preparing_data/fig2a_b_c_d_ED5_ED7.R`) begins `subset(total_damages_1gtco2_cd, emitter == 1990)`, so both files are the **1990 pulse** and their `year_cat` values ("1990-2020", "2021-2100") are damage-accumulation windows, not pulse years. The shipped `total_damages_by_pulse_2020.rds` and `_2100.rds` are global totals by emitter year with no country column. The country-by-emitter-year intermediate that would answer the question, `total_damages_1gtco2_1990_2020.rds`, is read by that script from a pipeline output path and is **not shipped** - not on the default branch and not in the tagged v1.1 release archived on Zenodo (concept DOI 10.5281/zenodo.18158445, v1.1 10.5281/zenodo.18199013, CC BY 4.0). Checked 29 August 2026. No 2020-pulse share is reported, and the `0.0015 < share < 0.0020` assertion is **not** relaxed.

### Not in paper (economic-value comparison dropped 26 August 2026)

The bullets and the Conference Board paragraph under this heading compare global damages against a **Canadian economic-value denominator** (the one Burke sankey paragraph below is a Burke-channel diagnostic and is marked as such). That comparison was dropped from the paper on 26 August 2026. The code is retained, still runs, and is still asserted, so the figures below are live rather than frozen - but none of them is a paper result. The denominator is the Conference Board of Canada's *A Rising Tide* whole-chain GDP figure, which is industry-commissioned; the externality ratios, the Hatton comparison and the Burke national test all rest on it.
- **Canadian value (proposed, CBoC scaled, 40 yr, 2025 CAD):** **$601 billion**
- **Externality ratio, ECCC central (proposed):** **3.9x** global damages / Canadian value (Hatton UK range was 5.9x–16.8x; Burke through-2300 is 48x)
- **National test, Burke channel only (not the headline):** Canadian value is 12.1x the damages Canada itself bears. Reported as indeterminate.
- **30-year denominator sensitivity (ECCC central, proposed):** $451 billion Canadian value, ratio **5x** (research sketch used 30 years; central uses 40).
- **Operating + under construction only (ECCC central):** $741 billion global L&D / $192 billion value = **4x** (19.4 mtpa export).

(Burke-channel diagnostic, not part of the dropped economic-value comparison.) Burke Figure 4 sankey (`damages_and_benefits_k90.rds`) is emitter/recipient flows for 1990–2020 **all** emissions, not LNG. Canada as emitter caused **$1.33 trillion** (2.40% of global owing; USA $10.18T validates against the paper's $10.2T). Canada is **not** a plotted recipient, so CAN-on-CAN cannot be read from this file. Victim share stays 0.17% from the 1 Gt pulse.

Canada denominator (not in paper, dropped 26 August 2026): Conference Board *A Rising Tide* Table 1, Canada GDP at market prices **C$11.153bn/yr (2020 CAD)** at 56 mtpa, scaled linearly on proposed export nameplate (60.7 mtpa) over 40 years (Appendix A operating life). Whole-chain including upstream (76% of the GDP). Industry-commissioned. Inflated to 2025 CAD with FRED NGDPDIXCAA. Uninflated 2020 CAD value is $484 billion.

### End of dropped economic-value comparison. What follows is a damages sensitivity and is in the SI.

Burke horizon rows (whole GWP100 CO2e at Burke SC-CO2 — Burke has no SC-CH4; g = 0, proposed slate; upper bracket, not central). Global L&D and value in trillion 2025 CAD; Canada-borne in billion 2025 CAD. Bold is the Burke default horizon, not the paper central.

| horizon | discounting | SC USD2020/t | global L&D (tn) | value (tn) | ratio | Canada-borne (bn) |
|---|---|---|---|---|---|---|
| through_2100 | 2pct_fixed | 1,013 | 9.2 | 0.60 | 15x | 15.7 |
| no_growth_after_2100 | 2pct_fixed | 2,120 | 19.3 | 0.60 | 32x | 32.9 |
| **through_2300** | 2pct_fixed | 3,198 | **29.1** | 0.60 | **48x** | 49.6 |
| through_2100 | ramsey | 1,322 | 12.0 | 0.60 | 20x | 20.5 |
| no_growth_after_2100 | ramsey | 4,045 | 36.8 | 0.60 | 61x | 62.7 |
| through_2300 | ramsey | 7,056 | 64.2 | 0.60 | 107x | 109.4 |

Burke through-2100 year-by-year path, g bracket (trillion 2025 CAD, all / proposed). Burke default g = 0; +2% is Hatton's headline and is not used.

| discount | g=−2% | g=0% | g=+2% |
|---|---|---|---|
| 1.5% | 9.2 / 6.5 | 15.9 / 11.8 | 28.5 / 21.9 |
| 2% | 7.1 / 5.1 | **12.4 / 9.2** | 22.2 / 17.1 |
| 3% | 4.5 / 3.2 | 7.8 / 5.8 | 13.9 / 10.7 |
| 5% | 2.0 / 1.4 | 3.5 / 2.6 | 6.2 / 4.8 |

Figure: `Outputs/figures/fig09_loss_damage_by_group.png`.

## Placeholder start-year sensitivity

Parameter `assumed_first_export_year_if_missing` = **2030** (Parameters sheet). 4 headline-scope assets have a blank `first_export_year`. With licence-end stops on licensed terminals, every dated end year is 2056–2066; the panel tail is entirely this placeholder.

Placeholder-start assets account for **3404.6 MtCO2e** (47.5% of the 7162.0 Mt lifetime total).

| project | mtpa | lifetime Mt | share of lifetime | last year |
|---|---|---|---|---|
| marinvest_baie_comeau | 15.0 | 1502.3 | 21.0% | 2069 |
| kanata_lng | 12.0 | 1210.8 | 16.9% | 2069 |
| fermeuse_energy_flng | 5.0 | 498.4 | 7.0% | 2069 |
| summit_lake_pg_lng | 2.7 | 193.0 | 2.7% | 2059 |

| start year | lifetime Mt | peak year | peak Mt | last year | central damage CAD bn |
|---|---|---|---|---|---|
| 2030 (central) | 7162.0 | 2037 | 235.6 | 2069 | 3108 |
| 2033 | 7162.0 | 2040 | 235.6 | 2072 | 3162 |
| 2035 | 7162.0 | 2042 | 235.6 | 2074 | 3198 |

## Uniform 40-year life sensitivity (SI only)

Every in-scope asset run at **40 years from its first export year with no `authorised_export_end_year` stop** (`lifespan_override_years=40`, `ignore_licence_end=True` on the panel builder). The central case is unchanged and stays the paper's number; this is supplementary information. Lives in the central case run from 27 to 40 years, and the licence-end stops bite hardest on the two LNG Canada trains and Ksi Lisims — the assets furthest along — so the central case is not simply a shorter version of this one.

| build-out | case | lifetime CO2e Mt | lifetime CO2-only Mt | peak Mt (year) | ECCC 2% damages CAD bn |
|---|---|---|---|---|---|
| committed | central | 1,845.8 | 1,781.7 | 57.6 (2030) | 741 |
| committed | uniform_40yr_no_licence_stop | 2,250.9 | 2,172.8 | 57.6 (2030) | 945 |
| committed_plus_advanced | central | 3,757.5 | 3,627.1 | 134.0 (2037) | 1,561 |
| committed_plus_advanced | uniform_40yr_no_licence_stop | 4,874.3 | 4,705.1 | 134.0 (2037) | 2,133 |
| full | central | 7,162.0 | 6,918.1 | 235.6 (2037) | 3,108 |
| full | uniform_40yr_no_licence_stop | 8,358.2 | 8,072.8 | 235.6 (2037) | 3,721 |

Full buildout moves **+16.7%** on the uniform life. Committed-to-full ratio, both ways:

| case | full / committed | committed as % of full |
|---|---|---|
| central | 3.88 | 25.8% |
| uniform_40yr_no_licence_stop | 3.71 | 26.9% |

Series: `Outputs/figure_data/sens_uniform_life.csv`. No locked value changes: the central case is untouched.

## Kino Aski feedgas sensitivity (SI only)

Kino Aski LNG (15 mtpa, Baie-Comeau) has **no stated feedgas route**. The register now carries `feedgas_basin` = "not available" for it, with the two candidate supplies named in `feedgas_basin_note`: Western Canadian gas via the TC Energy Canadian Mainline, and United States Appalachian gas. The distinction decides both the pipeline haul and whether upstream and pipeline emissions are Canada territorial. Central factors are untouched and the central case is unchanged; this is supplementary information.

**Case A, Western Canadian supply.** Pipeline transport is scaled by distance against the 670 km Coastal GasLink line that the 0.07 tCO2e/t pipeline factor is scaled against. **No cited distance is available**: no route to the Quebec north shore is defined, and the CER's pipeline profile for the TransCanada Canadian Mainline publishes only a 14,123 km total regulated system length covering all segments including deactivated and abandoned ones, which is not a route distance - and Baie-Comeau is not on the Mainline in any case. Case A is therefore run as an **explicit x3 and x5 multiplier band, labelled illustrative**, and the gap is recorded on the register's Data Gaps sheet. Territory stays CAN.

**Case B, United States supply.** Intensities are unchanged - this model has no US-specific factors and does not invent any - but upstream and pipeline emissions occur outside Canada and are tagged FOR instead of CAN.

| case | pipeline tCO2e/t | Kino Aski lifetime Mt | headline lifetime Mt | headline Canada-territorial Mt | headline Canada share |
|---|---|---|---|---|---|
| Central (as published) | 0.07 | 1,502.3 | 7,162.0 | 1,257.7 | 17.6% |
| Case A, Western Canadian supply, pipeline x3 (illustrative: 3 x 670 km = 2,010 km, no cited route) | 0.22 | 1,566.2 | 7,226.0 | 1,321.6 | 18.3% |
| Case A, Western Canadian supply, pipeline x5 (illustrative: 5 x 670 km = 3,350 km, no cited route) | 0.37 | 1,630.1 | 7,289.9 | 1,385.5 | 19.0% |
| Case B, United States supply (intensities unchanged, upstream and pipeline tagged FOR) | 0.07 | 1,502.3 | 7,162.0 | 1,117.7 | 15.6% |

Case B leaves the total unchanged (7,162.0 Mt) and moves 139.9 Mt out of the Canada-territorial column, taking the Canada share from 17.6% to 15.6%. That is the larger of the two effects: which country's gas Kino Aski burns matters more to the territorial answer than how far it travels. Series: `Outputs/figure_data/sens_kino_aski_feedgas.csv`.

### Limitations: feedgas basin and route

**All assets use Western Canadian upstream and pipeline factors.** The upstream factor is derived from Canada Energy Regulator British Columbia oil and gas production, processing and transmission emissions against BC marketable gas, corrected for measured methane. The pipeline factor is an assumed 0.10 tCO2e/t. The British Columbia assessment of Coastal GasLink is used as a scaling check (1.47 vs 1.48 MtCO2e/yr on Phase 1 throughput), not as an independent measurement of the factor. Both the factor and the check are British Columbia figures. For the seven Pacific-coast assets that is the right geography. For the two Atlantic projects it is a **substitution**, and the direction of bias differs:

- **Kino Aski (Baie-Comeau, 15 mtpa).** If the feedgas is Western Canadian, the upstream factor is right but the pipeline factor is **too low**, because a haul to the Quebec north shore is several times the 670 km the factor is scaled against: the illustrative band above puts the understatement at roughly 64 to 128 MtCO2e over the asset's life. If the feedgas is United States Appalachian, the upstream factor is the wrong jurisdiction entirely - measured Appalachian methane intensities are generally **higher** than Montney-area ones, so the factor is again likely too low - and the territorial attribution is wrong by the whole of upstream and pipeline. No US factor is substituted, because this model has none.
- **Fermeuse (Avalon Peninsula, 5.0 mtpa).** The feedgas is offshore associated gas from the Jeanne d'Arc Basin, not Western Canadian pipeline gas. The bias runs the other way on pipeline transport: there is essentially no onshore transmission haul, so applying the 0.10 tCO2e/t pipeline factor **overstates** that stage. Offshore associated gas production has a different emissions profile from onshore unconventional production - platform power, flaring and venting rather than well-pad and gathering methane - and no Canadian offshore factor was located, so the Western Canadian upstream factor is applied and the direction of that bias is **not determined**. No factor change is made for Fermeuse; this is limitations text only.
- **Shipping is now route-scaled** (see the emission factors section), so the Atlantic projects no longer carry a Pacific shipping distance. That correction is in the central case; the upstream and pipeline substitutions above are not.

## Liquefaction drive-type sensitivity (SI only)

Central liquefaction stays **0.29** tCO2e per tonne LNG (gas turbine drive) for every terminal, and the run still asserts it. Two electric-drive figures from the British Columbia Environmental Assessment Office's assessment of Ksi Lisims LNG (7 August 2025, Canadian Impact Assessment Registry document 163192E, pages 847 to 848) are applied as a sensitivity: **0.156** for the Alternative Case with gas-fired power barges, and **0.021** for the Base Case on grid supply.

**Boundary caveat.** The two drive figures are facility total intensity including marine sources, not the liquefaction stage alone; 0.29 is a liquefaction-stage factor. The comparison is approximate. Both parameter rows on the Parameters sheet carry the same note.

Scope: **Ksi Lisims**, where the figures are sourced, and **Cedar**, on the stated **assumption** that it belongs to the same floating-LNG electric-drive class - no Cedar-specific figure was located. No other terminal is touched. The existing electrification appendix (0.12 versus 0.29, figure 8) is unchanged and is a separate comparator.

| case | liquefaction tCO2e/t | headline lifetime Mt | delta Mt | headline Canada-territorial Mt | Canada delta Mt |
|---|---|---|---|---|---|
| Central: gas turbine 0.29 for every terminal | 0.290 | 7,162.0 | +0.0 | 1,257.7 | +0.0 |
| Alternative Case, gas-fired power barges (BC EAO Ksi Lisims), applied to Ksi Lisims and Cedar | 0.156 | 7,108.3 | -53.8 | 1,203.9 | -53.8 |
| Base Case, grid supply (BC EAO Ksi Lisims), applied to Ksi Lisims and Cedar | 0.021 | 7,054.1 | -107.9 | 1,149.7 | -107.9 |

Liquefaction is CAN-tagged on every chain that includes it, so the whole delta lands in the Canada-territorial column: the total and the Canada figure move by the same amount. Per-asset split: `Outputs/figure_data/sens_liquefaction_drive.csv`.

## Benchmark comparison

Every external comparison the model holds, in one place. Each row carries **both** boundaries, because the like-for-like question is what makes the comparison worth anything. Machine-readable copy: `Outputs/benchmark_comparison.csv`; also a sheet in `SLIDE_TABLES.xlsx`.

| comparison | ours | external | source | like for like? | direction |
|---|---|---|---|---|---|
| Liquefaction | **0.290** | 0.330 | IEA (2025) | Close | ours LOWER than the world average |
| Shipping | **0.120** | 0.181 [0.138, 0.193] | IEA (2025) | NO | ours LOWER, on a LONGER voyage |
| Pipeline transport | **0.074** | 0.074 [0.073, 0.074] | Liu et al. (2021) | Partly | ADOPTED as the central, 3 September 2026 |
| Regasification | **0.021** | 0.021 [0.011, 0.028] | Gan et al. (2024) | Yes | ADOPTED as the central, 3 September 2026 |
| Well to regasification (no combustion) | **0.755** | 1.190 [0.940, 1.510] | Roman-White et al. (2021) | NO on geography | ours LOWER, and expected to be |
| LNG stages only (liquefaction + shipping + regasification) | **0.431** | 0.62–1.71 | Balcombe et al. (2016) | Boundary yes, vintage no | ours LOWER than the bottom of the range |

All values in tCO2e per tonne LNG. **Every comparison that is not an adopted value points the same way: this model sits at or below the external figure.** The two that matter most are shipping, where the IEA implies roughly 2.3x our intensity per kilometre, and liquefaction, where the IEA global average is 14% above our 0.29. Neither is like-for-like enough to act on, and both are recorded here rather than left in a source cell.

## SI table: per-asset detail

One row per headline-scope asset. Full machine-readable version, with capacity_basis and life_source in full, at `Outputs/si_table_assets.csv` and on the `SI Assets` sheet of the results workbook.

| project | coast | tier | calc_group | mtpa | first export | life (basis) | lifetime Mt | share | CAN / BUNK / FOR Mt per year | FID | GEM status (date) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Kino Aski LNG (formerly Marinvest Energy, Baie-Comeau) | Atlantic | early_proposed | proposed | 15 | 2030 * | 40 (parameters default) | 1,502.3 | 21.0% | 7.6 / 1.2 / 34.2 | no | not available (not available) |
| LNG Canada Terminal | Pacific | operating | operating | 14 | 2025 | 32 (licence end) | 1,293.0 | 18.1% | 7.1 / 1.4 / 31.9 | yes | operating (2026-08-28) |
| Kanata LNG | Pacific | early_proposed | proposed | 12 | 2030 * | 40 (parameters default) | 1,210.8 | 16.9% | 6.1 / 1.2 / 27.3 | no | not available (not available) |
| Ksi Lisims FLNG Terminal | Pacific | advanced_proposed | proposed | 12 | 2029 | 35 (licence end) | 1,034.3 | 14.4% | 6.0 / 1.2 / 27.3 | no | proposed (2026-08-28) |
| LNG Canada Terminal | Pacific | advanced_proposed | proposed | 14 | 2030 | 27 (licence end) | 877.4 | 12.3% | 7.0 / 1.4 / 31.5 | no | proposed (2026-08-28) |
| Fermeuse Energy FLNG Terminal | Atlantic | early_proposed | proposed | 5 | 2030 * | 40 (parameters default) | 498.4 | 7.0% | 2.5 / 0.3 / 11.4 | no | proposed (2026-08-28) |
| Cedar FLNG Terminal | Pacific | under_construction | under_construction | 3.3 | 2028 | 39 (licence end) | 371.8 | 5.2% | 1.7 / 0.3 / 7.5 | yes | construction (2026-08-28) |
| Summit Lake PG LNG | Pacific | early_proposed | proposed | 2.7 | 2030 * | 30 (proponent) | 193.0 | 2.7% | 1.4 / 0.3 / 6.1 | no | not available (not available) |
| Woodfibre LNG Terminal | Pacific | under_construction | under_construction | 2.1 | 2028 | 30 (licence end) | 181.0 | 2.5% | 1.1 / 0.2 / 4.8 | yes | construction (2026-08-28) |

\* first export year is the `assumed_first_export_year_if_missing` placeholder, not a register value (4 of 9 assets). Per-year territorial figures are the asset's lifetime split over its own emitting years, not calendar-panel years.

## Monte Carlo (physics sampled, ECCC 2% per gas applied after)

10,000 draws, seed `20260828`. Physics 0.20s; pricing 0.04s. Kernel vs published panel max abs 7.1e-15 Mt. Liquefaction held at Emission Factors central. Howarth 0.55 is a named point, not a draw. Draws are on the headline scope (export chain). Each draw carries its own upstream and shipping factor, so its CH4 mass moves with it; damages are CO2 at SC-CO2 plus CH4 mass at SC-CH4, the same per-gas treatment as the central case.

| build-out | lifetime median [p5, p95] Mt | peak-year median [p5, p95] Mt | ECCC 2% damage median [p5, p95] CAD bn |
|---|---|---|---|
| committed | 1901.2 [1810.5, 2004.6] | 59.3 [56.5, 62.5] | 757 [724, 796] |
| committed_plus_advanced | 3820.0 [3603.8, 4055.5] | 138.1 [131.5, 145.6] | 1578 [1497, 1669] |
| full | 7257.1 [6493.9, 8074.8] | 242.5 [231.1, 255.6] | 3135 [2761, 3548] |

Howarth 0.55 (other stages central, not inside the interval):

| build-out | lifetime Mt | peak year / Mt | ECCC 2% CAD bn |
|---|---|---|---|
| committed | 2003.8 | 2030 / 62.5 | 768 |
| committed_plus_advanced | 4079.1 | 2037 / 145.5 | 1621 |
| full | 7776.5 | 2037 / 255.8 | 3231 |

Central case versus Monte Carlo median (full build-out):

| quantity | central case | Monte Carlo median [p5, p95] |
|---|---|---|
| Lifetime (Mt) | 7162.0 | 7257.1 [6493.9, 8074.8] |
| Peak-year (Mt) | 235.6 in 2037 | 242.5 [231.1, 255.6] |
| ECCC 2% damage (CAD bn) | 3108 | 3135 [2761, 3548] |

They differ because the stage triangles are right-skewed (shipping 0.05 / 0.12 / 0.31 especially): the Monte Carlo median is not the point estimate from central factor values.

Decision taken 29 August 2026: the paper reports the central case with the 5th to 95th percentile above as its interval. The Monte Carlo median is stated once, with this reason. See the Paper set section.

## Lifecycle intensity comparison

tCO2e per tonne LNG. This model is recomputed on each comparator's boundary. Ranges are shown as published; midpoints are not substituted. GWP20 is not mixed with GWP100.

| study | year | geography | boundary | combustion | shipping | total tCO2e/t |
|---|---|---|---|---|---|---|
| This model (export chain) | 2026 | Canada | Well → combustion (GWP100) | yes | yes | 3.50 |
| This model, aligned to Roman-White 2021 | 2026 | Canada | Well → regasification (no combustion, GWP100) | no | yes | 0.76 |
| Roman-White et al. 2021 (Balcombe co-author) | 2021 | US Gulf Coast → China (Cheniere SPL) | Well → regasification (no combustion, GWP100) | no | yes | 0.94–1.51 (expected 1.19) |
| This model, aligned to Balcombe 2016 LNG stages | 2026 | Canada | Liquefaction + shipping + regasification (GWP100) | no | yes | 0.43 |
| Balcombe et al. 2016 (LNG-stage literature range) | 2016 | Global compilation | Liquefaction + tanker + regasification (not upstream) | no | yes | 0.62–1.71 |
| Howarth 2024 | 2024 | US shale LNG exports | Well → combustion, GWP20 (not GWP100) | yes | yes | 7.37–8.03 |

This model's export-chain GWP100 is 3.50 t/t (well-to-regas 0.76; liquefaction+shipping+regas 0.43). **Shipping here is the unscaled 0.12 British Columbia to north-east Asia factor**, not the per-asset route-scaled figure the headline model uses, because the comparator studies are single-route. Liquefaction remains 0.29. Howarth's GWP100 totals are only in supplemental figures and are not converted here. Howarth also includes destination transmission methane that this model does not.

Excluded (boundary not an LNG lifecycle, or not determined):

- **MacKay et al. 2021:** 6,650-site methane measurements in western Canada. No LNG system boundary and no lifecycle total.
- **Johnson et al. 2023:** Alberta measurement inventory of oil and gas methane. No LNG system boundary and no lifecycle total.
- **Di Lullo et al.:** Published work is a transmission-pipeline LCA (construction/operation/decommissioning) and crude WTT studies. No LNG well-to-wire or well-to-combustion total with a readable boundary.

Figure: `Outputs/figures/fig10_lca_comparison.png`.
