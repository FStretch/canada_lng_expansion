# Sourcing audit of every number in the model

<!-- lock-banner:start -->
> **Dated document.** Sourcing audit of every number in the model, 1 September 2026.
> Written against the pre-Discovery lock: 9,298.1 Mt lifetime, 298.2 Mt peak, C$4,073 bn damages, 100.1 mtpa across ten projects.
> Its own findings were then applied (`tools/fix_audit_findings.py`): Discovery LNG returned to cancelled and the GWP20 scenario was recomputed on the methane portion only. Regasification, the combustion range, pipeline transport, the methane share and the FID band have all moved onto cited values since; each move is a commit in the git history. The verdicts below stand; the headline figures they were measured against do not.
> **Current lock:** **7,167.1 Mt** lifetime CO2e, **235.9 Mt** peak in 2037, **18.2 / 3.2 / 78.6** CAN / BUNK / FOR, **C$3,106 bn** ECCC 2% damages valued when caused (**C$1,945 bn** discounted to 2025), **79.6 mtpa** of export capacity.
> This banner is generated from the lock in `build_results.py` and asserted on every run; edit nothing between the markers.
<!-- lock-banner:end -->

**Date:** 1 September 2026  
**Scope:** Read-only. No input, output, or code file was modified except this note.  
**Headline the numbers move:** full-buildout central lifetime **9,298.1 MtCO2e** (calendar panel 2025–2069, export chain, 10 assets). A 1% move is about **93 Mt**. Percentages below are of that lifetime, holding everything else fixed and treating the stage as linear in intensity × throughput × years.

`41.2`, Pembina `0.12`, and “emissions figures pending rerun” were answered in an internal deck reconciliation of 1 September 2026, kept in git history.

Source types are only: `citation`, `url`, `proponent`, `derived`, `assumption`, `none`.  
Verdicts are only: `sourced`, `derived and traceable`, `assumption, declared`, `assumption, undeclared`, `unsourced`.

A number typed `cited` or `derived` with a homepage, a missing URL, or a formula whose addends have no citation is **unsourced**, not sourced. That is the credibility problem, not the declared ramps.

---

## 1. Master table

### Emission factors (tCO2e per t LNG)

| value | where it is used | source as recorded | source type | verdict |
|---|---|---|---|---|
| upstream central **0.25** | every export/bunkering/domestic tonne; default scenario `measurement_central` | CER BC 14.6 Mt (2022) / ~63 bcm → inventory 0.22; × 1.5 on assumed 30% CH4 share → 0.25. Rounded from 0.253. | derived | derived and traceable |
| upstream low **0.22** | EF range; scenario `inventory_as_reported`; MC triangle low | Same CER inventory, uncorrected. “Roughly 63 bcm/y” is not a cited table cell. | derived | derived and traceable |
| upstream high **0.55** | EF range; named scenario `howarth_high` only. **Not** the MC high. | Howarth 2024 DOI 10.1002/ese3.1934. US-focused, not Canadian. | citation | sourced |
| pipeline central **0.10** | every chain with pipeline | “Literature band”; CGL EAO 3.517 Mt at 5 Bcf/d scaled to Phase 1 → 1.48 vs model 1.47. ICF/Sphera “cited in BC EAO LNG reviews” — no paper, page, or URL. | none | unsourced |
| pipeline low **0.05** | EF range; MC triangle | Same uncited literature band. | none | unsourced |
| pipeline high **0.18** | EF range; MC triangle | Same. | none | unsourced |
| liquefaction central **0.29** | every terminal, whole life, headline and MC (fixed) | LNG Canada EA “roughly 4 Mt/yr” / 14 mtpa = 0.286, rounded to 0.29. No EA document URL on the EF sheet. | derived | derived and traceable |
| liquefaction low **0.12** | EF range_low; Parameters `liquefaction_electric`; figure 8 appendix. **Not** headline. | “Pembina Institute electrified LNG scenario.” URL `https://www.pembina.org/` (homepage). Notes also mention Woodfibre 0.059. | url | unsourced |
| liquefaction high **0.36** | EF range only (MC does not sample liquefaction) | “Literature upper bound for gas-turbine plants.” No study, page, or URL. | none | unsourced |
| shipping central **0.12** | BC-basis shipping; scaled by `route_distance_nm / 3800` | Howarth 2024; reconstructed as IMO 8.50 gCO2/DWT/nm × 7,600 nm / 0.85 cargo × 1.44 slip → 0.110, then **kept at 0.12**. | citation | sourced |
| shipping low **0.05** | EF range; MC | Roman-White et al. 2021 ACS DOI 10.1021/acssuschemeng.1c03307 (short routes). | citation | sourced |
| shipping high **0.31** | EF range; MC | Same paper (long routes). | citation | sourced |
| regasification central **0.04** | export and domestic/import chains | “RMI Oil Climate Index benchmarks.” No URL, table, or vintage on the sheet. | none | unsourced |
| regasification low **0.02** | EF range; MC | Same RMI, plus “corroborated by a peer-reviewed LCA placing regasification at 0.021” — unnamed. | none | unsourced |
| regasification high **0.06** | EF range; MC | Same RMI, no URL. | none | unsourced |
| combustion central **2.75** | every chain with combustion; ~77.6% of headline | IPCC 2006 default for natural gas. URL is the 2006 Guidelines landing page, not the fuel-factor table. | citation | sourced |
| combustion low **2.50** | EF range; MC | “Variation in delivered gas composition.” No citation. | none | unsourced |
| combustion high **3.00** | EF range; MC | Same. | none | unsourced |

**0.25 construction check:** `0.22 × (1 − 0.30 + 0.30 × 1.5) = 0.253`, stored as 0.25. The rounding is not declared on the EF sheet. `measurement_high` 0.26 is `0.22 × (0.70 + 0.30 × 1.7) = 0.266`, also rounded.

### Parameters sheet (every row)

| value | where it is used | source as recorded | source type | verdict |
|---|---|---|---|---|
| `steady_state_utilisation` **0.839** | default throughput after ramp | IGU World LNG Report 2026, global liquefaction utilisation 83.9% in 2025. URL `https://www.igu.org/` (homepage). | citation | sourced |
| `year_1_utilisation` **0.40** | year-1 ramp (all but Phase 1 / Saint John) | “Model assumption - no external source.” | assumption | assumption, declared |
| `year_2_utilisation` **0.70** | year-2 ramp | Same. | assumption | assumption, declared |
| `ramp_years` **2** | length of ramp | “Model assumption.” | assumption | assumption, declared |
| `lifecycle_years_default` **40** | life where no licence end and no stated life; oil comparator years | Typed `assumption`. Notes say the four main export licences are 40 years (GL-330 etc.). Fallback for unlicensed assets **is** an assumption. URL is the CER applications **list**, not a licence. | assumption | assumption, declared |
| `lifespan_sensitivity_low` **30** | MC life triangle low; SI uniform-life bound | “Matches Summit Lake stated operating life.” | assumption | assumption, declared |
| `lifespan_sensitivity_high` **50** | MC life triangle high | CER may issue LNG licences up to 50 years. URL is an FAQ page. | citation | sourced |
| `canada_net_zero_year` **2050** | pathway figures | Canadian Net-Zero Emissions Accountability Act. URL is a government **summary**, not the Act. | url | sourced |
| `fid_delay_low` **3** | MC FID triangle | “Planning range - no published empirical average.” | assumption | assumption, declared |
| `fid_delay_mid` **5** | start year for non-FID assets (7 proposed, 80.7 mtpa) | “Planning range, default.” | assumption | assumption, declared |
| `fid_delay_high` **7** | MC FID triangle | Same. | assumption | assumption, declared |
| `post_fid_to_completion` **4.5** | **not used** in utilisation or the panel | IEA Global LNG Capacity Tracker, “4 to 5 year global average.” URL is a tool homepage. Notes: “Documented, not used in the utilisation calculation.” | citation | sourced |
| `methane_leakage_low/mid/high` **1 / 1.25 / 1.6** | **not read by any Python module** | “Scenario design parameter.” Dead rows. | assumption | assumption, declared |
| `gwp100_ch4` **29.8** | CH4 mass from CO2e; L&D split | IPCC AR6 WG I, fossil methane. URL is the WG I **report homepage**, not Table 7.15. | citation | sourced |
| `gwp20_ch4` **82.5** | GWP20 scenario text; mass-route reconciliation | Same. | citation | sourced |
| `mtpa_to_tonnes` **1,000,000** | unit conversion | Unit conversion. | derived | derived and traceable |
| `lng_to_gas_bcm_per_mtpa` **1.38** | feedgas demand vs pipeline capacity; Fermeuse 5.0 mtpa derivation | “Method constant… No external citation identified.” | none | unsourced |
| `canada_2005_baseline` **758** | implied by target arithmetic | 2025 Progress Report. URL is a government page. | citation | sourced |
| `canada_2026_interim_objective` **607** | context | Same report. | citation | sourced |
| `canada_2030_target_low` **417** | figure 8 shares; slide table 10 | Same. | citation | sourced |
| `canada_2030_target_high` **455** | same | Same. | citation | sourced |
| `canada_2030_projected` **646** | overshoot gap ingredients | Climate Action Tracker country page, not ECCC. | url | sourced |
| `canada_2035_target_low/high` **379 / 417** | unused in headline physics | 2035 target page. | citation | sourced |
| `canada_national_emissions` **694** | 6.7% of inventory | NIR 2025, 2023 total ex LULUCF. | citation | sourced |
| `remaining_15c_budget` **170** GtCO2 | paper budget share | GCB 2025, ESSD 18:3211 (2026), from 1 Jan 2026, 50%. | citation | sourced |
| `remaining_17c_budget` **525** | same | Same. | citation | sourced |
| `remaining_2c_budget` **1055** | same | Same. | citation | sourced |
| `coal_plant_reference_mw` **500** | unused in current figure path (no grep hit in `src/`) | “Comparator assumption.” | assumption | assumption, declared |
| `coal_plant_capacity_factor` **0.55** | unused | Same. | assumption | assumption, declared |
| `coal_tco2e_per_mwh` **0.95** | unused | Same. | assumption | assumption, declared |
| `tmx_total_system_bpd` **890,000** | figure 7 full-system bar | “Trans Mountain system capacity after the May 2024 expansion.” URL `https://www.transmountain.com/` (homepage). | url | unsourced |
| `lng_canada_ph1_year_1_utilisation` **0.25** | Phase 1 year 1 only | Typed `assumption`. URL is LNG Canada homepage. “LNG Canada does not publish utilisation figures.” | assumption | assumption, declared |
| `lng_canada_ph1_year_2_utilisation` **0.60** | Phase 1 year 2 | Same. | assumption | assumption, declared |
| `lng_canada_ph1_steady_state_utilisation` **0.85** | Phase 1 after ramp | “Slightly above the 83.9% global average. Judgement, not a published figure.” URL still lngcanada.ca. | assumption | assumption, declared |
| `liquefaction_drive_default` **gas_turbine** | domestic `not_published` rows | Declared fallback. | assumption | assumption, declared |
| `saint_john_utilisation` **0.025** | Saint John import only (out of headline) | Repsol AR 8 TBtu (2023) vs 7.5 mtpa, via an **LNGPrime news URL**, not the annual report. | url | sourced |
| `lng_energy_content` **52** GJ/t | Saint John TBtu→tonnes; unused HHV vs Balcombe 55 | “Method constant.” No citation. | none | unsourced |
| `lng_export_licence_max_term` **50** | documentation | Bill C-15 royal assent. URL is a Parliament viewer. | citation | sourced |
| `canada_2030_overshoot_gap` **200** | 23.3% share | Typed `derived`: 646 minus 417–455. 646−417=229, 646−455=191. **200 is a round number, not the arithmetic.** URL is CAT again. | derived | assumption, undeclared |
| `upstream_ch4_share` **0.30** | 0.25/0.26 construction; CH4 split | Typed `assumption`. Gazette methane-regs URL. Notes: NIR is 20% nationally; 30% is a BC-gas judgement. | assumption | assumption, declared |
| `upstream_measurement_correction` **1.5** | 0.25 construction | MacKay et al. 2021 Nature Sci Rep (6,650 sites). 1.7 from BC aircraft in notes. | citation | sourced |
| `liquefaction_gas_turbine` **0.29** | duplicate of EF central | Same LNG Canada EA implication. | derived | derived and traceable |
| `liquefaction_electric` **0.12** | figure 8; not headline | Pembina homepage. Typed `cited`. | url | unsourced |
| `bc_lng_emission_intensity_benchmark` **0.16** | not used as a factor | GGIRCA benchmark. URL is the BC industry-reporting **portal**, not the regulation that states 0.16. | url | sourced |
| `route_bc_to_northeast_asia_nm` **3800** | shipping scale denominator; Discovery/Kanata fill | “Oxford Institute… as cited by CAPP.” URL is a **CAPP advocacy PDF**. | citation | sourced |
| `route_us_gulf_to_northeast_asia_nm` **9200** | not used in headline physics | Black & Veatch perspective page. | url | sourced |
| `voyage_days_bc_to_north_asia` **10** | **not read by the model** | Globe and Mail on first cargo. | url | sourced |
| `ocean_transport_intensity_range_low/high` **0.05 / 0.31** | duplicate of shipping EF range | Roman-White 2021 DOI. | citation | sourced |
| `route_atlantic_routing_factor` **1.125** | Atlantic distances | SeaRates 3,050 nm / great circle 2,712 nm. URL is the SeaRates tool homepage. | derived | derived and traceable |
| `route_baie_comeau_to_rotterdam_nm` **2980** | Kino Aski shipping | Great circle × 1.125. Notes: “Estimate, not a published sailing distance.” | derived | derived and traceable |
| `route_fermeuse_to_rotterdam_nm` **2470** | Fermeuse shipping | Same method. | derived | derived and traceable |
| `route_saint_john_to_rotterdam_nm` **3050** | calibration point | SeaRates 5,648 km. | url | sourced |
| `lng_carrier_aer_gco2_per_dwt_nm` **8.5** | shipping reconstruction (0.110), not the stored 0.12 | IMO DCS 2023 as reported in an MDPI paper. | citation | sourced |
| `lng_carrier_kgco2_per_nm` **940** | **not used** in the panel | EU JRC 2019 MRV. | citation | sourced |
| `lng_carrier_methane_slip_uplift` **1.44** | shipping CH4 share `1−1/1.44`; reconstruction | Balcombe et al. 2022 ES&T: 68.1 t CH4 vs 4,600 t CO2 → 68.1×29.8/4600 = 0.441 → 1.441, stored as 1.44. | derived | derived and traceable |
| `cargo_tonnes_per_dwt` **0.85** | shipping reconstruction 0.110 only | “Model assumption - typical ratio.” Data Gaps: no source. | assumption | assumption, declared |
| `tmx_oil_lifecycle_per_barrel` **0.513** | figure 7 | Typed `derived`. Source: `0.075 + 0.008 + 0.43`. URL **Not available**. Components have no citation, vintage, or crude slate. | derived | unsourced |
| `liquefaction_electrification_assumed` **none** | headline drive | Declared: electric not assumed. | assumption | assumption, declared |
| `assumed_first_export_year_if_missing` **2030** | Discovery, Kino Aski, Summit Lake, Fermeuse, Kanata (and Tilbury P2 out of headline) | Named parameter. Lifetime **does not** move if this shifts (licence-uncapped assets just slide); damages do. | assumption | assumption, declared |
| `monte_carlo_seed` **20260828** | MC reproducibility | Declared seed. | assumption | assumption, declared |
| `monte_carlo_n_draws` **10000** | MC | Declared. | assumption | assumption, declared |
| `headline_scope_chains` **export** | who is in 9,298.1 | Declared scope filter. | assumption | assumption, declared |
| `headline_scope_calc_groups` **operating,under_construction,proposed** | same | Declared. | assumption | assumption, declared |
| `liquefaction_electric_drive_gas_generation` **0.156** | SI drive sensitivity only (Ksi Lisims sourced; Cedar assumed) | BC EAO Ksi Lisims AR, 7 Aug 2025, CIAR 163192E pp. 847–848, Alternative Case. **Facility total including marine**, not liquefaction-stage. | citation | sourced |
| `liquefaction_electric_drive_grid` **0.021** | SI drive sensitivity only | Same document, Base Case, grid. Same boundary caveat. | citation | sourced |

### Report-only parameters (`src/report_params.py`, not on the Parameters sheet)

| value | where it is used | source as recorded | source type | verdict |
|---|---|---|---|---|
| `tmx_expansion_bpd` **590,000** | figure 7 expansion bar | “Commonly cited as 590,000 bpd above the pre-expansion system.” **No URL.** | none | unsourced |
| `alberta_bc_bitumen_pipeline_bpd` **1,000,000** | figure 7 hatched bar | MPO submission 2 Jul 2026; floor of 1 Mbpd. Flagged `unvalidated`. | none | unsourced |
| `365` days | `oil_lifecycle_gt`: bpd × 0.513 × 365 × 40 / 1e9 | Hardcoded. 365.25 would move oil ~0.07%. | assumption | assumption, undeclared |

### Scenarios (upstream value each scenario sets)

| value | where it is used | source as recorded | source type | verdict |
|---|---|---|---|---|
| `inventory_as_reported` **0.22** | named scenario | Official BC inventory at face value. | derived | derived and traceable |
| `measurement_central` **0.25** | **paper default** | 1.5× on the methane portion only. Arithmetic uses `upstream_ch4_share` 0.30. | derived | derived and traceable |
| `measurement_high` **0.26** | named scenario | 1.7× on the methane portion (BC aircraft). | derived | derived and traceable |
| `near_term_methane_gwp20` **0.33** | named scenario | Sheet says “x1.5, then GWP20 on the methane portion” and “Not to the whole factor.” **The stored value is 0.22 × 1.5 = 0.33, the whole factor.** A methane-only GWP20 reweight is ~0.42. README still claims methane-portion only. RESULTS_SUMMARY §5a already records the contradiction. | derived | unsourced |
| `howarth_high` **0.55** | named point, excluded from MC draws | Howarth 2024. | citation | sourced |

### Asset register — headline export assets

Lifetime Mt are **outputs** (derived from the factors, util, life). They are listed because the deck quotes them. Capacity / years are inputs.

| value | where it is used | source as recorded | source type | verdict |
|---|---|---|---|---|
| LNG Canada P1 **14.0 mtpa** | committed | GEM GGIT Sep 2025 + NRCan. | citation | sourced |
| LNG Canada P1 first export **2025** | panel start | GEM ActualStartYear=2025. | citation | sourced |
| LNG Canada P1 licence end **2056** | 32 emitting years; lifetime 1,309.6 | Derived: issued year + 40-year term. CER URL is the **applications list**, not GL-330. Notes: term may run from first export instead. | derived | derived and traceable |
| LNG Canada P1 drive **gas_turbine** | 0.29 applied | Register note: on-site turbines; partial BC Hydro for other loads. | proponent | sourced |
| Cedar **3.3 mtpa** | committed | Proponent FID 25 Jun 2024 (cedarlng.com). NRCan/CER cite 3.0; nameplate used. | proponent | sourced |
| Cedar first export **2028** | panel | GEM LatestPlannedStartYear. | citation | sourced |
| Cedar licence end **2066** | 39 years; 376.6 Mt | Same issued+term derivation. | derived | derived and traceable |
| Cedar drive **gas_turbine** (central) | headline 0.29 | Previously `electric_committed`; interconnection under construction. Headline ignores that. | assumption | assumption, declared |
| Woodfibre **2.1 mtpa** | committed | GEM + NRCan. Licence applied for 2.9 mtpa; nameplate used. | citation | sourced |
| Woodfibre first export **2028** | panel | GEM. | citation | sourced |
| Woodfibre licence end **2057** | 30 years; 183.3 Mt | Issued+term. | derived | derived and traceable |
| LNG Canada P2 **14.0 mtpa** | advanced proposed | GEM + NRCan. | citation | sourced |
| LNG Canada P2 first export **2030** | panel (not placeholder) | GEM LatestPlannedStartYear. | citation | sourced |
| LNG Canada P2 licence end **2056** | 27 years; 888.6 Mt | Same 2056 as Phase 1; cuts 13 years off a 40-year term. | derived | derived and traceable |
| Ksi Lisims **12.0 mtpa** | advanced | GEM + NRCan. | citation | sourced |
| Ksi Lisims first export **2029** | panel | GEM. | citation | sourced |
| Ksi Lisims licence end **2063** | 35 years; 1,047.6 Mt | Issued+term. | derived | derived and traceable |
| Kino Aski (Baie-Comeau) **15.0 mtpa** | early proposed; 1,521.7 Mt | Kino Aski Inc. newswire, 17 Aug 2026. Replaced earlier **10 mtpa**. No filing. | proponent | sourced |
| Kino Aski first export **(blank → 2030)** | placeholder | Source: Not available. | assumption | assumption, declared |
| Summit Lake **2.7 mtpa** | early; 195.5 Mt | IAAC project page; “up to 2.7”; assessment the proponent asked to suspend. | citation | sourced |
| Summit Lake life **30** | overrides default 40 | Proponent impact assessment. | proponent | sourced |
| Summit Lake first export **(blank → 2030)** | placeholder | Not available. | assumption | assumption, declared |
| Fermeuse **5.0 mtpa** | early; 504.9 Mt | **Derived**, not published. 9.7 Tcf / 40 yr / 1.38 bcm per mtpa. Proponent has not stated nameplate. Unsourced third-party tables say 10. | derived | derived and traceable |
| Fermeuse first export **(blank → 2030)** | placeholder | GEM start year field exists in the sources sheet template; register cell is blank so 2030 is used. | assumption | assumption, declared |
| Discovery **20.0 mtpa** | early; **2,043.9 Mt, 22% of headline** | GEM CapacityinMtpa. GEM status verbatim **cancelled (inferred 4 y)**; register keeps `proposed`. | citation | sourced |
| Discovery first export **(blank → 2030)** | placeholder | Not available. | assumption | assumption, declared |
| Discovery status **proposed** | keeps 2,044 Mt in the paper | “Assigned: proposed, pending verification August 2026.” GEM disagrees. | assumption | assumption, declared |
| Kanata **12.0 mtpa** | early; 1,226.3 Mt | Hanwha Ocean / Kanata newswire 16 Jun 2026. Not in GEM. | proponent | sourced |
| Kanata first export **(blank → 2030)** | placeholder | Not available. | assumption | assumption, declared |
| CER licence URL (all licensed rows) | end-year derivation | `https://www.cer-rec.gc.ca/en/applications-hearings/view-applications-projects/export-licence-applications/` — **index page**, not the licence PDF. | url | unsourced |

### Other chains (out of headline; still in register)

| value | where it is used | source as recorded | source type | verdict |
|---|---|---|---|---|
| Tilbury P1a **0.25 mtpa**, bunkering, operating, 2018 | excluded 23.5 Mt | GEM/Fortis. | citation | sourced |
| Tilbury P1b **0.65 mtpa**, bunkering, proposed, 2028 | excluded 63.4 Mt | GEM. | citation | sourced |
| Tilbury P2 **2.50 mtpa**, bunkering, proposed, start blank | excluded 137.3 Mt; NRCan lists export | Register judgement (`chain_note`). | assumption | assumption, declared |
| Saint John import **7.5 mtpa**, 2009 | 12.6 Mt at 2.5% util | GEM / Repsol. | citation | sourced |
| Mt Hayes **0.06**, Tamaska **0.016**, Energir **0.21**, Tilbury original **0.03** | domestic; last two legacy (0 lifetime) | GEM. | citation | sourced |
| Port of Hamilton capacity **missing** | excluded, not zeroed | Blank beats wrong. | none | unsourced |
| Tilbury Marine Jetty chain **none** | excluded | No lifecycle. | assumption | assumption, declared |

Cancelled/shelved capacities are GEM GGIT Sep 2025. **The register has no cancellation-year column and no reason column.** Twelve largest are listed in the reconciliation file.

### Loss and damage

| value | where it is used | source as recorded | source type | verdict |
|---|---|---|---|---|
| ECCC SC-CO2 schedule (e.g. 2020 @ 2% = **247** CAD2021/t) | paper central damages | ECCC interim guidance Table 1 / A.1.1 / A.1.2. URL is the SC-GHG landing page. | citation | sourced |
| ECCC SC-CH4 2020 @ 2% **2107** CAD2021/t | per-gas pricing; hardcoded assert in `loss_damage.py` | Same tables. Code refuses to run if 2020/2% ≠ 2107. | citation | sourced |
| `eccc_central_discount_rate_pct` **2.0** | paper central | ECCC recommended near-term Ramsey rate. | citation | sourced |
| CAD2021→2025 deflators **124.81689 / 143.98050** (ratio **1.1535**) | all ECCC CAD | FRED NGDPDIXCAA (IMF IFS). | citation | sourced |
| US GDP deflators 2020/2025 **105.377 / 128.979** | Burke USD→CAD path | FRED A191RD3A086NBEA. | citation | sourced |
| `usd_cad_2025` **1.3978** | Burke conversion | Bank of Canada annual average. | citation | sourced |
| Burke Canada share_FD **0.1704%** | Canada-borne Burke channel | `burke_country_damage_shares.csv`, CAN row, 1990 pulse, future window. UK HD 1.61% used as a check. | citation | sourced |
| Pulse year **1990** not 2020 | that share | Replication package has no 2020-pulse country table. Declared. | assumption | assumption, declared |
| Burke through-2300 2% **3,198** USD2020/t | SI upper bracket | Burke 2026 Figure 2e. | citation | sourced |
| Burke through-2100 2% **1,013** | SI | Burke ED Table 1 / pulse file. | citation | sourced |
| `central_growth_rate` **0** | Burke default g | Declared; Hatton +2% not used. | assumption | assumption, declared |
| `cboc_gdp_cad_per_year` **11,153,000,000** (2020 CAD) | dropped-from-paper denominator | CBoC *A Rising Tide* (Jul 2020) Table 1. Industry-commissioned. | citation | sourced |
| `cboc_scenario_mtpa` **56** | scale to 80.7 mtpa | Appendix A. | citation | sourced |
| `cboc_operating_years` **40** | 40 × annual GDP | Appendix A. Research sketch used 30. | citation | sourced |
| Linear scale CBoC 56 → **80.7** mtpa | $799 bn proposed value | No CBoC warrant that GDP is linear in mtpa. | assumption | assumption, undeclared |

### Monte Carlo (distributions actually drawn)

| value | where it is used | source as recorded | source type | verdict |
|---|---|---|---|---|
| upstream triangle **(0.22, 0.25, 0.33)** | physics draws | **Hardcoded** in `src/monte_carlo.py`. High is GWP20-equivalent 0.33, **not** EF high 0.55. Recorded in `mc_parameters.csv`. | assumption | assumption, declared |
| liquefaction **fixed 0.29** | not sampled | Hardcoded `LIQUEFACTION_FIXED = 0.29`. 0.12 is not an uncertainty band. | assumption | assumption, declared |
| pipeline **(0.05, 0.10, 0.18)** | sampled | EF low/central/high. Those bounds are unsourced (see above). | none | unsourced |
| shipping **(0.05, 0.12, 0.31)** | sampled | EF; low/high sourced, central sourced. | citation | sourced |
| regas **(0.02, 0.04, 0.06)** | sampled | EF; all three unsourced. | none | unsourced |
| combustion **(2.50, 2.75, 3.00)** | sampled | Central sourced; low/high unsourced. | citation | sourced |
| FID triangle **(3, 5, 7)** | non-FID assets | Parameters, hardcoded as `FID_TRI`. | assumption | assumption, declared |
| life triangle **(30, 40, 50)** | only unlicensed: Kino, Fermeuse, Discovery, Kanata | Parameters. Licensed lives held. | assumption | assumption, declared |
| utilisation ramp **fixed** | not sampled | “No published range.” | assumption | assumption, declared |
| `upstream_ch4_share` **fixed 0.30** | not sampled | Avoid double-counting 0.22×1.5. | assumption | assumption, declared |
| Howarth **0.55** | named point, not a draw | Scenarios sheet. | citation | sourced |

### Hardcoded in Python (not structural 0/1/1e6)

| value | where it is used | source as recorded | source type | verdict |
|---|---|---|---|---|
| `UPSTREAM_TRI = (0.22, 0.25, 0.33)` | MC | Comment only. Will **not** follow the workbook if EF high moves. | assumption | assumption, undeclared |
| `LIQUEFACTION_FIXED = 0.29` | MC | Duplicates EF central; `build_results` asserts 0.29. | derived | derived and traceable |
| `FID_TRI`, `LIFE_TRI` | MC | Duplicate Parameters. Drift risk. | assumption | assumption, undeclared |
| `ECCC_RATE = 2.0` | MC pricing | Duplicates `eccc_central_discount_rate_pct`. | citation | sourced |
| `PANEL_START_YEAR = 2025` | calendar panel | Matches analysis year. | assumption | assumption, declared |
| `CGL_CALIBRATION_KM = 670` | Kino feedgas SI only | Supporting Infrastructure length_km. | citation | sourced |
| `PLACEHOLDER_START_YEARS = (2030, 2033, 2035)` | SI | 2033/2035 not on Parameters. | assumption | assumption, undeclared |
| `HOWARTH_GWP20_T_PER_T = (7.37, 8.03)` | figure 10 | Howarth 2024 Table 3. | citation | sourced |
| `ROMAN_WHITE_W2R_T_PER_T = (0.94, 1.19, 1.51)` | figure 10 | Roman-White 2021 Table 1. | citation | sourced |
| `BALCOMBE_LNG_STAGES_G_PER_MJ_HHV = (11.2, 31.1)` | figure 10 | Balcombe 2016. | citation | sourced |
| `HHV_MJ_PER_KG = 55.0` | convert Balcombe | Comment: not this model’s `lng_energy_content=52`. | citation | sourced |
| `assert … liquefaction - 0.29` | drive SI / LCA | Will refuse to run if EF central moves. | derived | derived and traceable |
| README claim: “The model has no hardcoded emission factors, capacities or parameters.” | README | **False.** MC triangles, oil 365, report_params, LCA comparators, 670 km, 2107. | none | unsourced |

Oil addends that exist only in a source-string, not as parameters:

| value | where it is used | source as recorded | source type | verdict |
|---|---|---|---|---|
| oil upstream **0.075** tCO2e/bbl | 0.513 | Mentioned once in the source cell. | none | unsourced |
| oil transport **0.008** | 0.513 | Nothing. | none | unsourced |
| oil combustion **0.43** | 0.513 | Nothing. Looks like a rounded combustion factor; not cited. | none | unsourced |

---

## 2. How to read the verdicts

**Sourced** means a reviewer can open a named document or a URL that actually contains the figure, or a GEM/NRCan/CER field that does.

**Derived and traceable** means the arithmetic is in the workbook and the inputs to that arithmetic are themselves identified. It does **not** mean the inputs are good. 0.25 is traceable to 0.22, 1.5 and 0.30; 0.30 is an assumption.

**Assumption, declared** means the type field or the README says so.

**Assumption, undeclared** means the number behaves as a judgement (rounding, dead formula, hardcoded duplicate, linear scale) while being labelled `derived`/`cited` or not labelled at all.

**Unsourced** means nothing a reviewer can click survives, or a `derived` label is covering addends with no source. That is the oil 0.513 pattern.

---

## 3. Four lists

### 1. Unsourced numbers, ordered by headline impact

If the number were **25% wrong**, approximate move in the **9,298 Mt** lifetime (central, other things fixed). Oil and SI-only numbers are called out as not moving the paper set.

1. **Combustion range bounds 2.50 / 3.00** (MC interval; central 2.75 is sourced). Central itself: 25% error → **~1,800 Mt** (~19%). The bounds are what a reviewer will test; they have no citation.  
2. **Pipeline 0.10 / 0.05 / 0.18** — 25% on central → **~65 Mt** (~0.7%). Small share, fully unsourced band.  
3. **Regasification 0.04 / 0.02 / 0.06** — 25% on central → **~26 Mt** (~0.3%).  
4. **Liquefaction 0.12 (Pembina)** — not in the headline. If someone treated it as central instead of 0.29, Canada territorial falls ~12 Mt/yr; lifetime liquefaction stage is 8.2% so swapping 0.29→0.12 is **~−545 Mt** (−5.9%), not a 25% error. 25% error on 0.12 in figure 8 only.  
5. **Liquefaction high 0.36** — unused in MC. If it were the central, +0.07 on 0.29 is **~+225 Mt**.  
6. **Oil 0.513 and addends 0.075 / 0.008 / 0.43** — figure 7 only. 25% on 0.513 moves TMX full system **~1.67 Gt** (bar is 6.67 Gt). **Does not move 9,298.** This is still the worst `derived` costume in the file.  
7. **`tmx_total_system_bpd` 890,000** (homepage) and **`tmx_expansion_bpd` 590,000** (no URL) — figure 7 only. 25% → **~1.67 Gt / ~1.10 Gt** on those bars.  
8. **`alberta_bc_bitumen_pipeline_bpd` 1,000,000** — figure 7, flagged unvalidated. 25% → **~1.87 Gt** on that bar.  
9. **`lng_to_gas_bcm_per_mtpa` 1.38** — not in the emissions product; 25% would rescale Fermeuse 5.0 mtpa by 25% → **~126 Mt** if it flowed into capacity. Feedgas headroom figures would move.  
10. **`lng_energy_content` 52** — Saint John only (out of headline).  
11. **CER licence index URL** used as if it were GL-330/340/346/349 — the **2056/2057/2063/2066** hard stops rest on issued-year + 40. If those end years are 25% too short, licensed lifetime (LNG Canada both trains, Ksi Lisims, Cedar, Woodfibre) moves on the order of **several hundred Mt**. The numbers may be right; the recorded URL does not prove them.

**Not unsourced but high-leverage if wrong:** utilisation 0.839 (declared cited; URL is a homepage) — 25% → **~2,300 Mt**. Combustion central 2.75 (IPCC, landing-page URL) — **~1,800 Mt**. Discovery 20 mtpa (GEM, but GEM says cancelled) — 25% → **~511 Mt**. FID delay 5 years (declared assumption) — 25% (~1.25 years of proposed throughput) → **~250 Mt**.

### 2. Assumptions not currently declared in the outputs or the README

These are judgements that are labelled `derived`/`cited`, hardcoded without a Parameters row, or omitted from README §Assumptions / §Limitations.

- **`canada_2030_overshoot_gap` = 200** typed `derived` from 646 vs 417–455. The interval is 191–229. 200 is a round number. README does not say so.  
- **Upstream 0.25 / 0.26 stored as two-decimal rounds** of 0.253 / 0.266. Not declared.  
- **Shipping kept at 0.12** after a reconstruction that produced **0.110**. README says “within 8%” but presents 0.12 as the Howarth/IMO figure.  
- **`near_term_methane_gwp20` = 0.33** is whole-factor ×1.5. README and the Scenarios sheet both say the GWP20 uplift is methane-only. RESULTS_SUMMARY §5a records this; the README still does not.  
- **Linear scaling of CBoC GDP from 56 mtpa to 80.7 mtpa.** The denominator is dropped from the paper but still computed. Not declared as an extra assumption on top of CBoC’s own 56 mtpa scenario.  
- **MC / report_params hardcoded duplicates** (`UPSTREAM_TRI`, `FID_TRI`, `LIFE_TRI`, `365`, `tmx_expansion_bpd`). README says the model has **no** hardcoded parameters. That sentence is false.  
- **Placeholder years 2033 and 2035** exist only in `placeholder_sensitivity.py`.  
- **Cedar = same electric-drive class as Ksi Lisims** in the EAO sensitivity — declared in RESULTS_SUMMARY SI, **not** in the README.  
- **Atlantic distances are great-circle × 1.125**, not published sailings (declared on the parameter notes; README only flags Discovery/Kanata 3,800 nm as west-coast basis).  
- **Oil 365-day year** and reuse of **LNG** `lifecycle_years_default` for pipelines.

Declared (do not belong on this list): year-1/2 util 0.40/0.70, FID 5, placeholder 2030, CH4 share 0.30, cargo 0.85, electric-not-assumed, Discovery kept as proposed, Tilbury P2 bunkering, Fermeuse 5.0 derivation, headline export-only scope.

### 3. Numbers sourced to a proponent

These need a “proponent” label on the slide, not a regulator voice.

- **Cedar 3.3 mtpa** — Cedar LNG FID announcement. (3.0 is the regulator figure they rejected.)  
- **Kino Aski 15 mtpa** — Kino Aski Inc. 17 Aug 2026 newswire. No EA, no CER licence.  
- **Kanata 12 mtpa** — Hanwha Ocean / Kanata MOU newswire. No GEM row, no filing.  
- **Summit Lake 30-year life** (capacity 2.7 is IAAC “up to”).  
- **LNG Canada Phase 1 ramp 0.25 / 0.60 / 0.85** — judgement “informed by” startup; URL is the company homepage. Typed assumption, but the URL dresses it as company data.  
- **CBoC $11.153 bn/yr** — commissioned by the Canadian LNG Alliance. Cited, but it is an industry document.  
- **Route 3,800 nm** — Oxford via **CAPP** PDF.  
- **Woodfibre claimed 0.059** (mentioned in `liquefaction_electric` notes; not used).

GEM is a tracker, not a proponent. NRCan/CER are not proponents.

### 4. Recorded source does not actually support the value

A reviewer who clicks the cell loses.

| number | what is recorded | what a click actually is |
|---|---|---|
| **0.513** oil | type `derived`, “0.075+0.008+0.43” | No document. Arithmetic of three unsourced addends. **Same pattern as the oil audit.** |
| **890,000 bpd** | type `cited` | transmountain.com **homepage**. |
| **0.12 electric** | type `cited`, Pembina Institute | pembina.org **homepage**. No report title, year, table, or page. Woodfibre’s 0.059 sits in the same note and is a different number. |
| **0.839 utilisation** | IGU World LNG Report 2026 | igu.org **homepage**. The report name is enough to hunt; the URL is not a figure. |
| **GWP 29.8 / 82.5** | IPCC AR6 WG I | ipcc.ch/report/ar6/wg1/ **homepage**, not the GWP table. The values are standard; the link would not survive a picky reviewer. |
| **0.10 pipeline** | ICF and Sphera “cited in BC EAO LNG reviews” | No document. The CGL 1.47 vs 1.48 check validates **throughput scaling**, not the 0.10 literature pick. |
| **0.04 regas** | RMI Oil Climate Index | No URL. Unnamed “0.021 LCA” corroboration. |
| **Licence end years 2056–2066** | CER export-licence applications | CER **list page**, not GL-330/340/346/349. End year is issued+term, with a note that the term might run from first export instead — which would **lengthen** lives. |
| **`canada_net_zero_year` 2050** | the Act | Summary landing page. Notes already say this. |
| **`canada_2030_projected` 646** and **gap 200** | CAT country page | Not the 2025 Progress Report that supplies the targets. 200 ≠ 646−417 or 646−455. |
| **`bc_lng_emission_intensity_benchmark` 0.16** | GGIRCA | BC reporting **portal**, not the 0.16 legal text. Unused as a factor, still on the sheet. |
| **`near_term_methane_gwp20` 0.33** | “GWP20 on the methane portion only” | Value is `0.22 × 1.5`. Methane-only GWP20 is a different number (~0.42). **The source text contradicts the cell.** |
| **Shipping 0.12 as IMO-validated** | reconstruction gives 0.110 | 0.12 is Howarth, not the IMO reconstruction. Validation is “within 8%,” then the higher figure is kept. |
| **Saint John 0.025** | Repsol annual report | LNGPrime **news** URL. Arithmetic from 8 TBtu is plausible; the file is not the AR. |
| **IEA 4.5 yr FID-to-completion** | IEA tracker | Tool homepage; unused anyway. |
| **Discovery `proposed`** | GEM wiki | GEM verbatim is **cancelled (inferred 4 y)**. The capacity is GEM; the status is ours. |

---

## 4. Blunt summary

The oil 0.513 cell is **not** the only unsourced number. It is the cleanest example of a `derived` label on unsourced addends. The same costume appears on **pipeline 0.10**, **regas 0.04**, **combustion 2.50/3.00**, **liquefaction 0.12 via pembina.org**, **TMX 890,000 via a homepage**, and **`near_term_methane_gwp20` 0.33**.

What is actually in good shape: IPCC combustion 2.75 (as a default, if not as a URL), GCB budgets, ECCC SC-CO2/SC-CH4 schedules, Burke shares and Figure 2e, GWP values as numbers, most GEM capacities for operating/UC assets, Cedar 3.3 from the FID page, EAO 0.021 / 0.156 as an SI (with the facility-total caveat), and the declared ramps / FID / placeholder / CH4-share assumptions.

The README sentence *“The model has no hardcoded emission factors, capacities or parameters”* is false. That is the sentence a reviewer will use against the deposit.
