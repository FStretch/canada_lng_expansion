# Canada LNG lifecycle emissions — review summary

Default scenario: `measurement_central`. Run at 2026-09-03 17:20 UTC. Numbers to one decimal. Inputs read-only. `calc_group` from `Asset Register:calc_group`.

Deck-facing tables (one sheet per table, 1-decimal): `Outputs/SLIDE_TABLES.xlsx`. Send that workbook to the PPT chat.

## Paper set

Decision taken 29 August 2026. The paper reports the **central case** — the point estimate from the central factor values — with the Monte Carlo **5th to 95th percentile** as its interval. The Monte Carlo median is stated once, in its own column, and is not the reported figure. Damages are carried as two figures that answer two questions: the **calendar-year sum** values each year's damage when it is caused (the loss-and-damage figure, the central), and the **NPV to 2025** at the same 2% is what the stream is worth today (the cost-benefit figure, the aggregation Government of Canada regulatory guidance uses). Neither is a sensitivity on the other; see section 11.

| build-out | lifetime CO2e Mt | lifetime CO2-only Mt | peak | ECCC 2% damages CAD bn, valued when caused | ECCC 2% damages CAD bn, NPV to 2025 | MC median (lifetime / peak / damages)¹ |
|---|---|---|---|---|---|---|
| committed | **1,860.0** [1,826.8, 2,023.7] | **1,792.0** [1,743.4, 1,910.7] | **58.0** in 2030 [57.0, 63.1] | **745** [729, 801] | **524** | 1,918.6 / 59.9 / 763 |
| committed_plus_advanced | **3,786.4** [3,636.2, 4,095.8] | **3,648.0** [3,466.4, 3,871.1] | **135.1** in 2037 [132.7, 147.0] | **1,572** [1,509, 1,681] | **1,051** | 3,855.5 / 139.3 / 1,589 |
| full | **7,167.1** [6,515.3, 8,089.1] | **6,909.5** [6,193.4, 7,664.5] | **235.9** in 2037 [231.8, 256.4] | **3,106** [2,764, 3,546] | **1,945** | 7,274.0 / 243.2 / 3,135 |

¹ The Monte Carlo median sits **above** the central case (7,274.0 against 7,167.1 Mt at full buildout) because the sampled stage triangles are right-skewed — shipping 0.05 / 0.12 / 0.31 especially, where the central 0.12 sits well below the midpoint of the range. The median of a right-skewed draw is not the point estimate from central values. Both are reported; only the central case is the paper's number.

Membership: **committed** = committed (operating + under construction) (3 assets); **committed_plus_advanced** = committed plus advanced (+ tier advanced_proposed) (5 assets); **full** = full (every headline-scope asset) (9 assets). Interval basis: Monte Carlo p5-p95, 10000 draws, seed 20260828.

**How the headline is reported.** The headline is the three-point ladder above — committed, committed plus advanced, full slate — with the tier label on each figure. The single full-slate number is not fronted alone: about three quarters of it has no final investment decision, and the ladder is what makes each clause separately defensible. The Monte Carlo interval on each row is **factor uncertainty conditional on that build-out** at modelled utilisation and licence-term lives. It is not the uncertainty on what Canada's expansion will emit; that uncertainty is the spread across the build-outs, from the committed row to the full row, which is about five times wider than the full-row interval.

### Territorial split and carbon-budget shares

Territorial shares are the life-average split. Budget shares are the **CO2-only** lifetime against the GCB 2025 remaining CO2 budgets from the start of 2026, like for like.

| build-out | CAN % | BUNK % | FOR % | 1.5°C (170 GtCO2) | 1.7°C (525) | 2.0°C (1,055) |
|---|---|---|---|---|---|---|
| committed | 18.1 | 3.4 | 78.5 | 1.05% | 0.34% | 0.17% |
| committed_plus_advanced | 18.1 | 3.4 | 78.5 | 2.15% | 0.69% | 0.35% |
| full | 18.2 | 3.2 | 78.6 | 4.06% | 1.32% | 0.65% |

Locked in `build_results.py` as `EXPECTED_BUILD_OUT`; the run asserts every cell of the central column. Machine-readable copy: `Outputs/figure_data/paper_set.csv`.

## 1. Headline

- **Annual total (panel peak):** 235.9 MtCO2e in 2037 (9 assets emitting that year)
- **life_average_annual_mt:** 205.1 MtCO2e/yr (mean utilisation over each asset's operating window; not a calendar year)
- **Lifetime total (calendar panel 2025–2069):** 7167.1 MtCO2e (headline scope; remaining years from 2025, not duration × life-average)
- **Headline capacity (export chain only):** 79.6 mtpa (liquefaction; not summed with import regasification or other chains)
- **Scope:** Headline results include assets whose chain is in headline_scope_chains and whose calc_group is in headline_scope_calc_groups (export / operating,under_construction,proposed). Excluded 8 in-total non-export assets totalling 242.9 MtCO2e on the full-register panel (3.3% of the all-assets 7410.0 Mt). They remain in the register.

| chain | mtpa |
|---|---|
| export | 79.6 |

- **Scope 1+2:** 37.3 MtCO2e/yr (18.2%)  |  **Scope 3:** 167.8 MtCO2e/yr (81.8%)
- **Territorial:** CAN 37.3 (18.2%)  |  BUNK 6.6 (3.2%)  |  FOR 161.2 (78.6%)
- **Share of remaining carbon budget (GCB 2025, from start of 2026), on the CO2-only lifetime of 6,909.5 MtCO2:** 1.5°C, 50% from start of 2026 4.1% of 170 GtCO2  |  1.7°C, 50% from start of 2026 1.3% of 525 GtCO2  |  2.0°C, 50% from start of 2026 0.7% of 1055 GtCO2. This is **like for like**: CO2 against a CO2 budget. Residual caveats: pipeline fugitive methane is not split out of the CO2 total, and non-CO2 gases other than CH4 are not counted. On the older GWP100 CO2e basis the same shares are 4.2%  |  1.4%  |  0.7%.

## 2. By group

| calc_group | export mtpa | life_average_annual_mt | Lifecycle Mt | CAN / BUNK / FOR Mt/yr |
|---|---|---|---|---|
| operating | 14.0 | 40.7 | 1303.0 | 7.4 / 1.4 / 31.9 |
| under_construction | 5.4 | 15.7 | 557.0 | 2.8 / 0.5 / 12.3 |
| proposed | 60.2 | 148.7 | 5307.1 | 27.1 / 4.6 / 117.0 |

Capacity by chain within each calc_group (not summed across chains):

| calc_group | export | bunkering | domestic | import |
|---|---|---|---|---|
| operating | 14.0 | 0.0 | 0.0 | 0.0 |
| under_construction | 5.4 | 0.0 | 0.0 | 0.0 |
| proposed | 60.2 | 0.0 | 0.0 | 0.0 |

### Proposed: advanced vs early (tier split)

| tier | chain scope | mtpa | life_average_annual_mt | CAN / BUNK / FOR |
|---|---|---|---|---|
| advanced_proposed | export | 26.0 | 62.5 | 11.3 / 2.1 / 49.1 |
| early_proposed | export | 34.2 | 86.1 | 15.7 / 2.5 / 67.9 |

## 3. By chain

| chain | stages | mtpa | life_average_annual_mt | Lifecycle Mt | CAN / BUNK / FOR |
|---|---|---|---|---|---|
| export | upstream_production@CAN → pipeline_transport@CAN → liquefaction@CAN → shipping@BUNK → regasification@FOR → combustion@FOR | 79.6 | 205.1 | 7167.1 | 37.3 / 6.6 / 161.2 |

## 4. By project

| project | mtpa | chain | calc_group | tier | drive | life (source) | effective Mt/yr | annual Mt/yr | lifecycle Mt | CAN / BUNK / FOR | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| lng_canada_phase_1 | 14.0 | export | operating | operating | gas_turbine | 32 (Asset Register:authorised_export_end_year=2056 (hard stop; cuts 8y from Asset Register:authorised_export_term_years)) | 11.53 | 40.7 | 1303.0 | 7.4 / 1.4 / 31.9 |  |
| fermeuse_energy_flng | 4.5 | export | proposed | early_proposed | gas_turbine | 40 (Parameters:lifecycle_years_default) | 3.24 | 11.3 | 452.1 | 2.1 / 0.3 / 9.0 |  |
| kanata_lng | 12.0 | export | proposed | early_proposed | gas_turbine | 40 (Parameters:lifecycle_years_default) | 8.64 | 30.5 | 1220.1 | 5.5 / 1.0 / 23.9 |  |
| ksi_lisims_lng | 12.0 | export | proposed | advanced_proposed | gas_turbine | 35 (Asset Register:authorised_export_end_year=2063 (hard stop; cuts 5y from Asset Register:authorised_export_term_years)) | 8.43 | 29.8 | 1042.3 | 5.4 / 1.0 / 23.4 |  |
| lng_canada_phase_2 | 14.0 | export | proposed | advanced_proposed | gas_turbine | 27 (Asset Register:authorised_export_end_year=2056 (hard stop; cuts 13y from Asset Register:authorised_export_term_years)) | 9.27 | 32.7 | 884.1 | 5.9 / 1.1 / 25.7 |  |
| marinvest_baie_comeau | 15.0 | export | proposed | early_proposed | gas_turbine | 40 (Parameters:lifecycle_years_default) | 10.80 | 37.8 | 1514.0 | 6.9 / 1.0 / 29.9 |  |
| summit_lake_pg_lng | 2.7 | export | proposed | early_proposed | gas_turbine | 30 (Asset Register:project_life_years) | 1.84 | 6.5 | 194.5 | 1.2 / 0.2 / 5.1 |  |
| cedar_lng | 3.3 | export | under_construction | under_construction | gas_turbine | 39 (Asset Register:authorised_export_end_year=2066 (hard stop; cuts 1y from Asset Register:authorised_export_term_years)) | 2.72 | 9.6 | 374.6 | 1.7 / 0.3 / 7.5 |  |
| woodfibre_lng | 2.1 | export | under_construction | under_construction | gas_turbine | 30 (Asset Register:authorised_export_end_year=2057 (hard stop; cuts 10y from Asset Register:authorised_export_term_years)) | 1.72 | 6.1 | 182.4 | 1.1 / 0.2 / 4.8 |  |

## Headline exclusion (retained in the register)

Headline results include assets whose chain is in headline_scope_chains and whose calc_group is in headline_scope_calc_groups (export / operating,under_construction,proposed). Combined excluded tonnage: **242.9 MtCO2e** (8 in-total assets; 10.4 Mt in the all-assets peak year 2037). Already out of totals: ['port_of_hamilton_lng'].

| project | chain | calc_group | start | mtpa | lifetime Mt | legacy |
|---|---|---|---:|---:|---:|---|
| tilbury_phase_2 | bunkering | proposed | — | 2.50 | 137.4 |  |
| tilbury_phase_1b | bunkering | proposed | 2028 | 0.65 | 63.5 |  |
| tilbury_phase_1a | bunkering | operating | 2018 | 0.25 | 23.5 |  |
| saint_john_import_facility | import | operating | 2009 | 7.50 | 12.5 |  |
| mt_hayes_lng | domestic | operating | 2011 | 0.06 | 4.5 |  |
| tamaska_fort_nelson_lng | domestic | operating | 2021 | 0.02 | 1.6 |  |
| tilbury_original | domestic | operating | 1971 | 0.03 | 0.0 | yes |
| energir_montreal_lng | domestic | operating | 1976 | 0.21 | 0.0 | yes |

| chain | n | mtpa | lifetime Mt |
|---|---:|---:|---:|
| bunkering | 3 | 3.4 | 224.3 |
| domestic | 4 | 0.3 | 6.1 |
| import | 1 | 7.5 | 12.5 |

## 5. By stage

| stage | destination | life_average_annual_mt | share |
|---|---|---|---|
| upstream_production | CAN | 16.1 | 7.9% |
| pipeline_transport | CAN | 4.3 | 2.1% |
| liquefaction | CAN | 16.9 | 8.2% |
| shipping | BUNK | 6.6 | 3.2% |
| regasification | FOR | 1.2 | 0.6% |
| combustion | FOR | 160.0 | 78.0% |

## 5a. Carbon dioxide and methane split

Every asset-year in the panel now carries `co2_mt`, `ch4_derived_co2e_mt` and `ch4_mass_kt`, with `emissions_mtco2e = co2_mt + ch4_derived_co2e_mt` exactly. The split uses only parameters already on the workbook. **Upstream:** CH4-derived CO2e per tonne LNG is the scenario upstream factor less the CO2 part of the official inventory (`inventory_as_reported x (1 - upstream_ch4_share)` = 0.1845), i.e. 0.0925 tCO2e/t at central. **Shipping:** the 1.44 carrier uplift is entirely measured methane slip, so `1 - 1/1.44` = 0.306 of the shipping CO2e is CH4-derived (0.037 tCO2e/t). **Pipeline transport, liquefaction, regasification and combustion are treated as CO2; pipeline fugitive methane is not split**, because the workbook carries a single pipeline factor with no methane share behind it. CO2e totals are unchanged by this task.

| slice | lifetime CO2e Mt | lifetime CO2-only Mt | CH4-derived CO2e Mt | CH4 mass kt | CH4 share of CO2e |
|---|---|---|---|---|---|
| committed (build_out) | 1,860.0 | 1,792.0 | 68.0 | 2,283 | 3.7% |
| committed_plus_advanced (build_out) | 3,786.4 | 3,648.0 | 138.5 | 4,647 | 3.7% |
| full (build_out) | 7,167.1 | 6,909.5 | 257.6 | 8,645 | 3.6% |
| operating (calc_group) | 1,303.0 | 1,255.3 | 47.6 | 1,599 | 3.7% |
| under_construction (calc_group) | 557.0 | 536.7 | 20.4 | 684 | 3.7% |
| proposed (calc_group) | 5,307.1 | 5,117.5 | 189.6 | 6,363 | 3.6% |

CH4 mass is CH4-derived CO2e divided by `gwp100_ch4` = 29.8. It is left blank for the `near_term_methane_gwp20` scenario, whose upstream factor is not a GWP100 CO2e figure (see below).

### Reconciliation with `near_term_methane_gwp20`

That scenario's lifetime is **7,498.6 Mt** with upstream at 0.440 and every other stage central. The workbook now re-weights only the methane portion of upstream: non-methane inventory stays at 0.246 × (1 − upstream_ch4_share), and the methane portion is multiplied by 1.5 then by gwp20/gwp100 (82.5/29.8). Rebuilding from the Task 1 CH4 mass (`co2_mt + ch4_mass_kt/1000 x gwp20_ch4`, gwp20 = 82.5) gives **7,622.7 Mt**, **+1.7%** apart. The remaining gap is shipping methane slip, which the named scenario does not re-weight (129.3 Mt). The two routes are reported rather than forced together.

The CH4-mass route's implied methane-only GWP20 upstream factor is 0.441, against the workbook's 0.440. They differ because the workbook starts from the inventory factor and the 0.25 methane share, while the mass route starts from the central-case CH4 mass (inventory CO2 plus the 1.5× methane correction already in `measurement_central`). **No pipeline methane portion is defined anywhere in the workbook**, so pipeline is not re-weighted. `near_term_methane_gwp20` remains a named scenario as the workbook defines it; the CH4-mass route is not substituted for it.

## 6. Scenario range

| scenario | upstream | life_average_annual_mt | Lifecycle Mt | CAN Mt/yr |
|---|---|---|---|---|
| inventory_as_reported | 0.246 | 203.3 | 7104.1 | 35.5 |
| measurement_central | 0.277 | 205.1 | 7167.1 | 37.3 |
| measurement_high | 0.289 | 205.8 | 7191.5 | 38.0 |
| near_term_methane_gwp20 | 0.440 | 214.6 | 7498.6 | 46.8 |
| howarth_high | 0.550 | 220.9 | 7722.4 | 53.2 |

## 7. Context

Canada territorial under `measurement_central` is **37.3 MtCO2e/yr**.

- **5.4%** of national inventory (694 Mt, inventory basis — excludes LULUCF).
- **8.9% to 8.2%** of the 2030 target range (417–455 Mt). Targets include land-use accounting; the 694 inventory figure does not.
- **18.6%** of the 2030 overshoot gap (200 Mt, projected emissions minus the target path).

## 8. Assumptions that move the number most

- **Upstream factor** (central 0.277): inventory_as_reported (0.246) → 203.3 Mt/yr (-1.8); howarth_high (0.55) → 220.9 Mt/yr (+15.9).
- **Lifespan** (default mostly 40 yr licence / Parameters default): sensitivity bounds in Parameters are 30 and 50 yr. Lifecycle total scales roughly with lifespan (~-25% at 30 yr, ~+25% at 50 yr on a pure scale basis). Annual changes only via the util_sum/life ratio and FID-delay share of the window. Legacy facilities (outlived design life) use steady-state util and report annual only.
- **FID delay** (`fid_delay_mid`=5 yr inside lifespan): applies to 6 projects (60.2 mtpa export), currently 148.7 Mt/yr. Removing the delay would raise their annual emissions by roughly the ratio of lost ramp years (order-of-magnitude: several Mt/yr on the proposed export slate).
- **Utilisation** (default steady-state 0.839; Phase 1 override 0.85; Saint John flat 0.025): annual emissions scale almost linearly with effective util. A +10% relative move in steady-state util moves the headline by about 20.5 Mt/yr if applied uniformly.
- **Liquefaction** (central 0.29 tCO2e/t, gas turbine for every terminal): electrification is not assumed (`liquefaction_electrification_assumed`=none). 0.15 is retained as range_low and applies only if electrification is contracted and delivered. Previous drive classifications are in `liquefaction_drive_note`.
- **Placeholder start year** (`assumed_first_export_year_if_missing`=2030): 3380.7 MtCO2e (47.2% of lifetime) from 4 assets with a blank `first_export_year`. The 2069 tail is entirely this fill. Sensitivity at 2033 and 2035 is tabulated below.
- **Liquefaction drive default** for remaining `not_published` (domestic) rows: `gas_turbine` → intensity 0.29 tCO2e/t from Emission Factors central.

## 9. Appendix · electrification counterfactual (Canada territorial)

Headline case is gas turbine for every terminal. The rows below ask what Canada-territorial LNG would be if liquefaction ran at the electric factor (0.15 instead of 0.29 tCO2e/t). Liquefaction is tagged CAN, so the whole delta is territorial. This does not change the headline totals.

| case | CAN Mt/yr | vs gas | share of 694 Mt inventory | share of 2030 target low |
|---|---|---|---|---|
| Gas turbine (current) | 37.3 | — | 5.4% | 8.9% |
| Claimed electric delivered | 32.4 | -4.9 | 4.7% | 7.8% |
| All terminals electric | 29.1 | -8.1 | 4.2% | 7.0% |

Claimed-electric assets (previous `electric_committed` / `electric_planned`): cedar_lng, ksi_lisims_lng, lng_canada_phase_2, marinvest_baie_comeau, summit_lake_pg_lng, woodfibre_lng.

| calc_group | gas | claimed electric | all electric |
|---|---|---|---|
| operating | 7.4 | 7.4 | 5.8 |
| under_construction | 2.8 | 2.2 | 2.2 |
| proposed | 27.1 | 22.8 | 21.1 |

Figure: `Outputs/figures/fig08_electrification_canada_territorial.png`.

## 10. Anything that looks wrong

- FINDING: tilbury_marine_jetty: chain=none — no lifecycle applies; excluded (not zeroed).
- Flag: port_of_hamilton_lng.capacity_mtpa=missing
- Excluded (chain=none or blank, not zeroed): ['tilbury_marine_jetty']
- Remaining carbon budgets (GCB 2025) are CO2 from the start of 2026. The paper's share-of-budget figures are now the **CO2-only** lifetime against those budgets, from the Task 1 per-gas split. Residual caveats: pipeline fugitive methane is not split out of the CO2 total, so a small amount of methane sits inside it; and non-CO2 gases other than CH4 (N2O, refrigerants) are not counted anywhere in the model.
- Reconciliations close within floating-point tolerance (1e-6 to 1e-3); no material rounding residuals.
- Saint John at ~0.5 Mt/yr depends entirely on `saint_john_utilisation=0.025`; nameplate at default util would be ~17 Mt/yr. tier=watch but calc_group=operating (operating import terminal).
- Tilbury Phase 2 (2.5 mtpa) sits on bunkering by register judgement (`chain_note`); NRCan lists it as export — classification is a stated judgement, not re-derived in code.
- Loss and damage central case is ECCC SC-CO2 and SC-CH4 at 2%, priced per gas on the panel's CO2 / CH4 split and summed per calendar year (`central_price_family=eccc`, `central_aggregation=calendar_year`): damage valued when it is caused, the loss-and-damage figure. The NPV of the same stream to 2025 at 2% is the cost-benefit figure and is carried beside it in the paper set; neither is a sensitivity on the other (section 11). Burke is an upper-bracket sensitivity (g = 0) with no SC-CH4. Damages after 2100, sea-level rise, extremes and mortality outside GDP are omitted. The Conference Board denominator is Table 1 GDP in 2020 CAD, inflated to 2025 CAD.

## 11. Climate loss and damage (global)

Monetised economic damages from the modelled lifecycle emissions. The **central case** is ECCC official SC-CO2 **and SC-CH4** at the **2%** discount rate, applied per calendar year of emissions, in 2025 CAD (named parameters `central_price_family=eccc`, `central_aggregation=calendar_year`). Each year's damage is `co2_t x SC-CO2_t + ch4_mass_t x SC-CH4_t`, from the Task 1 per-gas split, both schedules at the same discount rate and both inflated CAD 2021 to CAD 2025 exactly once. ECCC 1.5% and 2.5% are the central case's sensitivity range. Burke et al. (2026) is an **upper-bracket sensitivity** across discount rates and Figure 2e horizons (default g = 0; Hatton +2% is not used); **Burke has no SC-CH4, so the Burke family prices the whole GWP100 CO2e total at Burke's SC-CO2**. Damages are **global**. They are not a legal bill. Construction, sea-level rise, extremes, and mortality outside GDP are omitted.

**Per-gas pricing.** The panel splits every asset-year into CO2 and CH4 (see section 5a). Central lifetime is 6,909 MtCO2 plus 8,645 kt CH4, the latter worth 258 MtCO2e at GWP100 = 29.8, i.e. **3.6%** of the 7,167 MtCO2e total. The CH4 is the upstream excess over inventory CO2 (0.28 less 0.184 = 0.093 tCO2e per t LNG) plus shipping methane slip. Pipeline fugitive methane is not split and stays inside the CO2 total. CO2 is priced at SC-CO2 and CH4 mass at ECCC SC-CH4 (SC-CH4/SC-CO2 is 9.6 in 2025 and 16.7 by 2080, against GWP100 of 29.8). Methane is **1.7%** of the central damage bill ($52 billion), CO2 the rest ($3.1 trillion).

Reconciliation with the retired treatment: pricing the whole GWP100 CO2e total at SC-CO2 would have given $3.2 trillion, **+2.0%** against the per-gas figure. The overstatement-bound machinery it supported is retired.

Implied average price is **$433/t** CAD 2025 (total damages / lifetime CO2e tonnes; an effective blended rate across CO2 at SC-CO2 and CH4 at SC-CH4, not a schedule value). The underlying SC-CO2 series is the emissions-weighted mean of the ECCC 2% schedule after a **single** CAD 2021→2025 inflation of 1.1535 (deflators 124.81689 / 143.98050). The unweighted mean of the same series over panel years is $434/t. In CAD 2021 the weighted mean is $383/t (2025 official schedule value is $271/t). Prices are looked up on the **calendar year of emission**. 42% of lifetime tonnes are after 2050, so the weighted mean sits above the 2037 peak-year price. Year table: `Outputs/figure_data/ld_price_by_year.csv`.

**Two aggregations, two questions.** Each year's SC is already the present value, at that year, of the future damage stream from a tonne emitted then. Summing the years without further discounting values each year's damage **when it is caused**, in constant 2025 CAD: that is the loss-and-damage question, and it is how Burke et al. (2026) aggregate a multi-year stream. Discounting each year's damage back to 2025 at the same 2% answers the cost-benefit question - what the stream is worth today, to set against benefits also expressed today - and is how Government of Canada regulatory guidance aggregates a multi-year stream. The calendar sum is the central because the paper asks the loss-and-damage question; the NPV is the answer to the other question, not a sensitivity on this one, and the two are carried together wherever the total appears.

- **Central, all in-scope:** **$3.1 trillion** damage valued when caused (ECCC 2%, calendar-year sum; the loss-and-damage figure), which is **$1.9 trillion** discounted to 2025 at 2% (the cost-benefit figure). Calendar-year sum by group: operating $512 billion  |  under construction $234 billion  |  proposed $2.4 trillion; NPV proposed $1.4 trillion.
- **Central sensitivity (ECCC 1.5%–2.5%, calendar year):** $2.1 trillion to $4.9 trillion
- **Burke upper bracket (whole CO2e at Burke SC-CO2, no SC-CH4; g = 0, year-by-year 2100 path, 1.5%–5%):** $3.5 trillion to $15.9 trillion; Figure 2e through-2300 at 2% fixed: **$39.2 trillion** (proposed $29.0 trillion)
- **Canada Burke-channel victim share (sensitivity, not central):** **0.17%** of a **1990** 1 Gt pulse, future window, so it externalises 99.8% ($49 billion borne at the through-2300 2% price). Alongside it, **P_dam_FD = 0.41**: the share of Burke draws in which Canada's damage from that pulse is positive. Only 41 per cent of draws put Canada in net loss at all, against 0.33 on the historical window and 0.98 for the United States and China. The 0.17% is a mean over a distribution that is not reliably signed for Canada, and should be read with the P_dam figure attached.

**Pulse year: only the 1990 pulse is available.** The paper's emissions are 2025 onward, so the natural question is Canada's share of a **2020** pulse. It cannot be computed from the replication package. `burke_country_damage_shares.csv` in this repository holds one row per country and is derived from the package's `1gtco2_damages_1990_2020.rds` and `1gtco2_damages_2020_2100.rds`; the script that writes both (`scripts/working/figures/preparing_data/fig2a_b_c_d_ED5_ED7.R`) begins `subset(total_damages_1gtco2_cd, emitter == 1990)`, so both files are the **1990 pulse** and their `year_cat` values ("1990-2020", "2021-2100") are damage-accumulation windows, not pulse years. The shipped `total_damages_by_pulse_2020.rds` and `_2100.rds` are global totals by emitter year with no country column. The country-by-emitter-year intermediate that would answer the question, `total_damages_1gtco2_1990_2020.rds`, is read by that script from a pipeline output path and is **not shipped** - not on the default branch and not in the tagged v1.1 release archived on Zenodo (concept DOI 10.5281/zenodo.18158445, v1.1 10.5281/zenodo.18199013, CC BY 4.0). Checked 29 August 2026. No 2020-pulse share is reported, and the `0.0015 < share < 0.0020` assertion is **not** relaxed.

### Not in paper (economic-value comparison dropped 26 August 2026)

The bullets and the Conference Board paragraph under this heading compare global damages against a **Canadian economic-value denominator** (the one Burke sankey paragraph below is a Burke-channel diagnostic and is marked as such). That comparison was dropped from the paper on 26 August 2026. The code is retained, still runs, and is still asserted, so the figures below are live rather than frozen - but none of them is a paper result. The denominator is the Conference Board of Canada's *A Rising Tide* whole-chain GDP figure, which is industry-commissioned; the externality ratios, the Hatton comparison and the Burke national test all rest on it.
- **Canadian value (proposed, CBoC scaled, 40 yr, 2025 CAD):** **$596 billion**
- **Externality ratio, ECCC central (proposed):** **4.0x** global damages / Canadian value (Hatton UK range was 5.9x–16.8x; Burke through-2300 is 49x)
- **National test, Burke channel only (not the headline):** Canadian value is 12.1x the damages Canada itself bears. Reported as indeterminate.
- **30-year denominator sensitivity (ECCC central, proposed):** $447 billion Canadian value, ratio **5x** (research sketch used 30 years; central uses 40).
- **Operating + under construction only (ECCC central):** $745 billion global L&D / $192 billion value = **4x** (19.4 mtpa export).

(Burke-channel diagnostic, not part of the dropped economic-value comparison.) Burke Figure 4 sankey (`damages_and_benefits_k90.rds`) is emitter/recipient flows for 1990–2020 **all** emissions, not LNG. Canada as emitter caused **$1.33 trillion** (2.40% of global owing; USA $10.18T validates against the paper's $10.2T). Canada is **not** a plotted recipient, so CAN-on-CAN cannot be read from this file. Victim share stays 0.17% from the 1 Gt pulse.

Canada denominator (not in paper, dropped 26 August 2026): Conference Board *A Rising Tide* Table 1, Canada GDP at market prices **C$11.153bn/yr (2020 CAD)** at 56 mtpa, scaled linearly on proposed export nameplate (60.2 mtpa) over 40 years (Appendix A operating life). Whole-chain including upstream (76% of the GDP). Industry-commissioned. Inflated to 2025 CAD with FRED NGDPDIXCAA. Uninflated 2020 CAD value is $480 billion.

### End of dropped economic-value comparison. What follows is a damages sensitivity and is in the SI.

Burke horizon rows (whole GWP100 CO2e at Burke SC-CO2 — Burke has no SC-CH4; g = 0, proposed slate; upper bracket, not central). Global L&D and value in trillion 2025 CAD; Canada-borne in billion 2025 CAD. Bold is the Burke default horizon, not the paper central.

| horizon | discounting | SC USD2020/t | global L&D (tn) | value (tn) | ratio | Canada-borne (bn) |
|---|---|---|---|---|---|---|
| through_2100 | 2pct_fixed | 1,013 | 9.2 | 0.60 | 15x | 15.7 |
| no_growth_after_2100 | 2pct_fixed | 2,120 | 19.2 | 0.60 | 32x | 32.8 |
| **through_2300** | 2pct_fixed | 3,198 | **29.0** | 0.60 | **49x** | 49.5 |
| through_2100 | ramsey | 1,322 | 12.0 | 0.60 | 20x | 20.5 |
| no_growth_after_2100 | ramsey | 4,045 | 36.7 | 0.60 | 62x | 62.6 |
| through_2300 | ramsey | 7,056 | 64.1 | 0.60 | 107x | 109.2 |

Burke through-2100 year-by-year path, g bracket (trillion 2025 CAD, all / proposed). Burke default g = 0; +2% is Hatton's headline and is not used.

| discount | g=−2% | g=0% | g=+2% |
|---|---|---|---|
| 1.5% | 9.2 / 6.5 | 15.9 / 11.8 | 28.5 / 21.9 |
| 2% | 7.2 / 5.1 | **12.4 / 9.2** | 22.2 / 17.1 |
| 3% | 4.5 / 3.2 | 7.8 / 5.8 | 13.9 / 10.7 |
| 5% | 2.0 / 1.4 | 3.5 / 2.6 | 6.2 / 4.8 |

Figure: `Outputs/figures/fig09_loss_damage_by_group.png`.

## Placeholder start-year sensitivity

Parameter `assumed_first_export_year_if_missing` = **2030** (Parameters sheet). 4 headline-scope assets have a blank `first_export_year`. With licence-end stops on licensed terminals, every dated end year is 2056–2066; the panel tail is entirely this placeholder.

Placeholder-start assets account for **3380.7 MtCO2e** (47.2% of the 7167.1 Mt lifetime total).

| project | mtpa | lifetime Mt | share of lifetime | last year |
|---|---|---|---|---|
| marinvest_baie_comeau | 15.0 | 1514.0 | 21.1% | 2069 |
| kanata_lng | 12.0 | 1220.1 | 17.0% | 2069 |
| fermeuse_energy_flng | 4.5 | 452.1 | 6.3% | 2069 |
| summit_lake_pg_lng | 2.7 | 194.5 | 2.7% | 2059 |

| start year | lifetime Mt | peak year | peak Mt | last year | central damage CAD bn |
|---|---|---|---|---|---|
| 2030 (central) | 7167.1 | 2037 | 235.9 | 2069 | 3106 |
| 2033 | 7167.1 | 2040 | 235.9 | 2072 | 3160 |
| 2035 | 7167.1 | 2042 | 235.9 | 2074 | 3195 |

## Uniform 40-year life sensitivity (SI only)

Every in-scope asset run at **40 years from its first export year with no `authorised_export_end_year` stop** (`lifespan_override_years=40`, `ignore_licence_end=True` on the panel builder). The central case is unchanged and stays the paper's number; this is supplementary information. Lives in the central case run from 27 to 40 years, and the licence-end stops bite hardest on the two LNG Canada trains and Ksi Lisims — the assets furthest along — so the central case is not simply a shorter version of this one.

| build-out | case | lifetime CO2e Mt | lifetime CO2-only Mt | peak Mt (year) | ECCC 2% damages CAD bn, calendar-year sum (valued when caused; the NPV-to-2025 figure is carried in the paper set) |
|---|---|---|---|---|---|
| committed | central | 1,860.0 | 1,792.0 | 58.0 (2030) | 745 |
| committed | uniform_40yr_no_licence_stop | 2,268.3 | 2,185.3 | 58.0 (2030) | 951 |
| committed_plus_advanced | central | 3,786.4 | 3,648.0 | 135.1 (2037) | 1,572 |
| committed_plus_advanced | uniform_40yr_no_licence_stop | 4,911.8 | 4,732.2 | 135.1 (2037) | 2,147 |
| full | central | 7,167.1 | 6,909.5 | 235.9 (2037) | 3,106 |
| full | uniform_40yr_no_licence_stop | 8,372.5 | 8,070.8 | 235.9 (2037) | 3,723 |

Full buildout moves **+16.8%** on the uniform life. Committed-to-full ratio, both ways:

| case | full / committed | committed as % of full |
|---|---|---|
| central | 3.85 | 26.0% |
| uniform_40yr_no_licence_stop | 3.69 | 27.1% |

Series: `Outputs/figure_data/sens_uniform_life.csv`. No locked value changes: the central case is untouched.

## Kino Aski feedgas sensitivity (SI only)

Kino Aski LNG (15 mtpa, Baie-Comeau) has **no stated feedgas route**. The register now carries `feedgas_basin` = "not available" for it, with the two candidate supplies named in `feedgas_basin_note`: Western Canadian gas via the TC Energy Canadian Mainline, and United States Appalachian gas. The distinction decides both the pipeline haul and whether upstream and pipeline emissions are Canada territorial. Central factors are untouched and the central case is unchanged; this is supplementary information.

**Case A, Western Canadian supply.** Pipeline transport is scaled by distance, expressed as multiples of the 670 km Coastal GasLink length used only as a yardstick; the 0.074 tCO2e/t pipeline factor is not calibrated on that line. **No cited distance is available**: no route to the Quebec north shore is defined, and the CER's pipeline profile for the TransCanada Canadian Mainline publishes only a 14,123 km total regulated system length covering all segments including deactivated and abandoned ones, which is not a route distance - and Baie-Comeau is not on the Mainline in any case. Case A is therefore run as an **explicit x3 and x5 multiplier band, labelled illustrative**, and the gap is recorded on the register's Data Gaps sheet. Territory stays CAN.

**Case B, United States supply.** Intensities are unchanged - this model has no US-specific factors and does not invent any - but upstream and pipeline emissions occur outside Canada and are tagged FOR instead of CAN.

| case | pipeline tCO2e/t | Kino Aski lifetime Mt | headline lifetime Mt | headline Canada-territorial Mt | headline Canada share |
|---|---|---|---|---|---|
| Central (as published) | 0.074 | 1,514.0 | 7,167.1 | 1,303.7 | 18.2% |
| Case A, Western Canadian supply, pipeline x3 (illustrative: 3 x 670 km = 2,010 km, no cited route) | 0.222 | 1,577.9 | 7,231.0 | 1,367.6 | 18.9% |
| Case A, Western Canadian supply, pipeline x5 (illustrative: 5 x 670 km = 3,350 km, no cited route) | 0.370 | 1,641.8 | 7,294.9 | 1,431.5 | 19.6% |
| Case B, United States supply (intensities unchanged, upstream and pipeline tagged FOR) | 0.074 | 1,514.0 | 7,167.1 | 1,152.2 | 16.1% |

Case B leaves the total unchanged (7,167.1 Mt) and moves 151.6 Mt out of the Canada-territorial column, taking the Canada share from 18.2% to 16.1%. That is the larger of the two effects: which country's gas Kino Aski burns matters more to the territorial answer than how far it travels. Series: `Outputs/figure_data/sens_kino_aski_feedgas.csv`.

### Limitations: feedgas basin and route

**All assets use Western Canadian upstream and pipeline factors.** The upstream factor is derived from Canada Energy Regulator British Columbia oil and gas production, processing and transmission emissions against BC marketable gas, corrected for measured methane. The pipeline factor is 0.074 tCO2e/t, cited, from two independent routes that agree to 1.2 per cent: Liu et al. (2021) on an 1,100 km Alberta line and the CER/ECCC national pipeline-transport inventory. The British Columbia assessment of Coastal GasLink implies about 0.094 tCO2e/t at the line's design capacity; the difference is discussed in the Emission Factors basis cell and the README. The upstream factor is a British Columbia figure; the pipeline factor is not. For the seven Pacific-coast assets the upstream geography is right. For the two Atlantic projects it is a **substitution**, and the direction of bias differs:

- **Kino Aski (Baie-Comeau, 15 mtpa).** If the feedgas is Western Canadian, the upstream factor is right but the pipeline factor is **too low**, because a haul to the Quebec north shore is several times the 670 km Coastal GasLink yardstick: the illustrative band above puts the understatement at roughly 64 to 128 MtCO2e over the asset's life. If the feedgas is United States Appalachian, the upstream factor is the wrong jurisdiction entirely - measured Appalachian methane intensities are generally **higher** than Montney-area ones, so the factor is again likely too low - and the territorial attribution is wrong by the whole of upstream and pipeline. No US factor is substituted, because this model has none.
- **Fermeuse (Avalon Peninsula, 4.5 mtpa).** The feedgas is offshore associated gas from the Jeanne d'Arc Basin, not Western Canadian pipeline gas. The bias runs the other way on pipeline transport: there is essentially no onshore transmission haul, so applying the 0.074 tCO2e/t pipeline factor **overstates** that stage. Offshore associated gas production has a different emissions profile from onshore unconventional production - platform power, flaring and venting rather than well-pad and gathering methane - and no Canadian offshore factor was located, so the Western Canadian upstream factor is applied and the direction of that bias is **not determined**. No factor change is made for Fermeuse; this is limitations text only.
- **Shipping is now route-scaled** (see the emission factors section), so the Atlantic projects no longer carry a Pacific shipping distance. That correction is in the central case; the upstream and pipeline substitutions above are not.

## Liquefaction drive-type sensitivity (SI only)

Central liquefaction stays **0.29** tCO2e per tonne LNG (gas turbine drive) for every terminal, and the run still asserts it. Two electric-drive figures from the British Columbia Environmental Assessment Office's assessment of Ksi Lisims LNG (7 August 2025, Canadian Impact Assessment Registry document 163192E, pages 847 to 848) are applied as a sensitivity: **0.156** for the Alternative Case with gas-fired power barges, and **0.021** for the Base Case on grid supply.

**Boundary caveat.** The two drive figures are facility total intensity including marine sources, not the liquefaction stage alone; 0.29 is a liquefaction-stage factor. The comparison is approximate. Both parameter rows on the Parameters sheet carry the same note.

Scope: **Ksi Lisims**, where the figures are sourced, and **Cedar**, on the stated **assumption** that it belongs to the same floating-LNG electric-drive class - no Cedar-specific figure was located. No other terminal is touched. The existing electrification appendix (0.12 versus 0.29, figure 8) is unchanged and is a separate comparator.

| case | liquefaction tCO2e/t | headline lifetime Mt | delta Mt | headline Canada-territorial Mt | Canada delta Mt |
|---|---|---|---|---|---|
| Central: gas turbine 0.29 for every terminal | 0.290 | 7,167.1 | +0.0 | 1,303.7 | +0.0 |
| Alternative Case, gas-fired power barges (BC EAO Ksi Lisims), applied to Ksi Lisims and Cedar | 0.156 | 7,113.4 | -53.8 | 1,250.0 | -53.8 |
| Base Case, grid supply (BC EAO Ksi Lisims), applied to Ksi Lisims and Cedar | 0.021 | 7,059.2 | -107.9 | 1,195.8 | -107.9 |

Liquefaction is CAN-tagged on every chain that includes it, so the whole delta lands in the Canada-territorial column: the total and the Canada figure move by the same amount. Per-asset split: `Outputs/figure_data/sens_liquefaction_drive.csv`.

## Benchmark comparison

Every external comparison the model holds, in one place. Each row carries **both** boundaries, because the like-for-like question is what makes the comparison worth anything. Machine-readable copy: `Outputs/benchmark_comparison.csv`; also a sheet in `SLIDE_TABLES.xlsx`.

| comparison | ours | external | source | like for like? | direction |
|---|---|---|---|---|---|
| Liquefaction | **0.290** | 0.330 | IEA (2025) | Close | ours LOWER than the world average |
| Shipping | **0.120** | 0.181 [0.138, 0.193] | IEA (2025) | NO | ours LOWER, on a LONGER voyage |
| Pipeline transport | **0.074** | 0.074 [0.073, 0.074] | Liu et al. (2021) | Partly | ADOPTED as the central, 3 September 2026 |
| Regasification | **0.021** | 0.021 [0.011, 0.028] | Mukherjee et al. (2025) | Yes | ADOPTED as the central, 3 September 2026 |
| Well to regasification (no combustion) | **0.782** | 1.190 [0.940, 1.510] | Roman-White et al. (2021) | NO on geography | ours LOWER, and expected to be |
| LNG stages only (liquefaction + shipping + regasification) | **0.431** | 0.62–1.71 | Balcombe et al. (2016) | Boundary yes, vintage no | ours LOWER than the bottom of the range |

All values in tCO2e per tonne LNG. **Every comparison that is not an adopted value points the same way: this model sits at or below the external figure.** The two that matter most are shipping, where the IEA implies roughly 2.3x our intensity per kilometre, and liquefaction, where the IEA global average is 14% above our 0.29. Neither is like-for-like enough to act on, and both are recorded here rather than left in a source cell.

## SI table: per-asset detail

One row per headline-scope asset. Full machine-readable version, with capacity_basis and life_source in full, at `Outputs/si_table_assets.csv` and on the `SI Assets` sheet of the results workbook.

| project | coast | tier | calc_group | mtpa | first export | life (basis) | lifetime Mt | share | CAN / BUNK / FOR Mt per year | FID | GEM status (date) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Kino Aski LNG (formerly Marinvest Energy, Baie-Comeau) | Atlantic | early_proposed | proposed | 15 | 2030 * | 40 (parameters default) | 1,514.0 | 21.1% | 7.9 / 1.2 / 34.2 | no | not available (not available) |
| LNG Canada Terminal | Pacific | operating | operating | 14 | 2025 | 32 (licence end) | 1,303.0 | 18.2% | 7.4 / 1.4 / 31.9 | yes | operating (2026-08-28) |
| Kanata LNG | Pacific | early_proposed | proposed | 12 | 2030 * | 40 (parameters default) | 1,220.1 | 17.0% | 6.3 / 1.2 / 27.3 | no | not available (not available) |
| Ksi Lisims FLNG Terminal | Pacific | advanced_proposed | proposed | 12 | 2029 | 35 (licence end) | 1,042.3 | 14.5% | 6.3 / 1.2 / 27.3 | no | proposed (2026-08-28) |
| LNG Canada Terminal | Pacific | advanced_proposed | proposed | 14 | 2030 | 27 (licence end) | 884.1 | 12.3% | 7.3 / 1.4 / 31.5 | no | proposed (2026-08-28) |
| Fermeuse Energy FLNG Terminal | Atlantic | early_proposed | proposed | 4.5 | 2030 * | 40 (parameters default) | 452.1 | 6.3% | 2.4 / 0.3 / 10.3 | no | proposed (2026-08-28) |
| Cedar FLNG Terminal | Pacific | under_construction | under_construction | 3.3 | 2028 | 39 (licence end) | 374.6 | 5.2% | 1.7 / 0.3 / 7.5 | yes | construction (2026-08-28) |
| Summit Lake PG LNG | Pacific | early_proposed | proposed | 2.7 | 2030 * | 30 (proponent) | 194.5 | 2.7% | 1.4 / 0.3 / 6.1 | no | not available (not available) |
| Woodfibre LNG Terminal | Pacific | under_construction | under_construction | 2.1 | 2028 | 30 (licence end) | 182.4 | 2.5% | 1.1 / 0.2 / 4.8 | yes | construction (2026-08-28) |

\* first export year is the `assumed_first_export_year_if_missing` placeholder, not a register value (4 of 9 assets). Per-year territorial figures are the asset's lifetime split over its own emitting years, not calendar-panel years.

## Monte Carlo (physics sampled, ECCC 2% per gas applied after)

10,000 draws, seed `20260828`. Physics 0.22s; pricing 0.03s. Kernel vs published panel max abs 2.8e-14 Mt. Liquefaction held at Emission Factors central. Howarth 0.55 is a named point, not a draw. Draws are on the headline scope (export chain). Each draw carries its own upstream and shipping factor, so its CH4 mass moves with it; damages are CO2 at SC-CO2 plus CH4 mass at SC-CH4, the same per-gas treatment as the central case.

| build-out | lifetime median [p5, p95] Mt | peak-year median [p5, p95] Mt | ECCC 2% damage median [p5, p95] CAD bn |
|---|---|---|---|
| committed | 1918.6 [1826.8, 2023.7] | 59.9 [57.0, 63.1] | 763 [729, 801] |
| committed_plus_advanced | 3855.5 [3636.2, 4095.8] | 139.3 [132.7, 147.0] | 1589 [1509, 1681] |
| full | 7274.0 [6515.3, 8089.1] | 243.2 [231.8, 256.4] | 3135 [2764, 3546] |

Howarth 0.55 (other stages central, not inside the interval):

| build-out | lifetime Mt | peak year / Mt | ECCC 2% CAD bn |
|---|---|---|---|
| committed | 2003.8 | 2030 / 62.5 | 771 |
| committed_plus_advanced | 4079.1 | 2037 / 145.5 | 1626 |
| full | 7722.4 | 2037 / 254.2 | 3217 |

Central case versus Monte Carlo median (full build-out):

| quantity | central case | Monte Carlo median [p5, p95] |
|---|---|---|
| Lifetime (Mt) | 7167.1 | 7274.0 [6515.3, 8089.1] |
| Peak-year (Mt) | 235.9 in 2037 | 243.2 [231.8, 256.4] |
| ECCC 2% damage (CAD bn) | 3106 | 3135 [2764, 3546] |

They differ because the stage triangles are right-skewed (shipping 0.05 / 0.12 / 0.31 especially): the Monte Carlo median is not the point estimate from central factor values.

Decision taken 29 August 2026: the paper reports the central case with the 5th to 95th percentile above as its interval. The Monte Carlo median is stated once, with this reason. See the Paper set section.

## Lifecycle intensity comparison

tCO2e per tonne LNG. This model is recomputed on each comparator's boundary. Ranges are shown as published; midpoints are not substituted. GWP20 is not mixed with GWP100.

| study | year | geography | boundary | combustion | shipping | total tCO2e/t |
|---|---|---|---|---|---|---|
| This model (export chain) | 2026 | Canada | Well → combustion (GWP100) | yes | yes | 3.53 |
| This model, aligned to Roman-White 2021 | 2026 | Canada | Well → regasification (no combustion, GWP100) | no | yes | 0.78 |
| Roman-White et al. 2021 (Balcombe co-author) | 2021 | US Gulf Coast → China (Cheniere SPL) | Well → regasification (no combustion, GWP100) | no | yes | 0.94–1.51 (expected 1.19) |
| This model, aligned to Balcombe 2016 LNG stages | 2026 | Canada | Liquefaction + shipping + regasification (GWP100) | no | yes | 0.43 |
| Balcombe et al. 2016 (LNG-stage literature range) | 2016 | Global compilation | Liquefaction + tanker + regasification (not upstream) | no | yes | 0.62–1.71 |
| Howarth 2024 | 2024 | US shale LNG exports | Well → combustion, GWP20 (not GWP100) | yes | yes | 7.37–8.03 |

This model's export-chain GWP100 is 3.53 t/t (well-to-regas 0.78; liquefaction+shipping+regas 0.43). **Shipping here is the unscaled 0.12 British Columbia to north-east Asia factor**, not the per-asset route-scaled figure the headline model uses, because the comparator studies are single-route. Liquefaction remains 0.29. Howarth's GWP100 totals are only in supplemental figures and are not converted here. Howarth also includes destination transmission methane that this model does not.

Excluded (boundary not an LNG lifecycle, or not determined):

- **MacKay et al. 2021:** 6,650-site methane measurements in western Canada. No LNG system boundary and no lifecycle total.
- **Johnson et al. 2023:** Alberta measurement inventory of oil and gas methane. No LNG system boundary and no lifecycle total.
- **Di Lullo et al.:** Published work is a transmission-pipeline LCA (construction/operation/decommissioning) and crude WTT studies. No LNG well-to-wire or well-to-combustion total with a readable boundary.

Figure: `Outputs/figures/fig10_lca_comparison.png`.
