# Citations wanted

Generated 3 September 2026 against the current workbooks (post sourcing-audit fixes).

Every number below is either **unsourced** (no document states it) or **declared as an
assumption where a real source may exist**. Values that cannot be cited by their nature — model
design choices, unit conversions, scope filters, the Monte Carlo seed — are listed at the end so
nobody wastes time on them.

Impact figures are the approximate move in the **7,254.2 Mt** headline lifetime if the value were
25% wrong, holding everything else fixed.

---

## Tier 1 — central emission factors with no document

These are the ones a reviewer will go for. All five sit on the Emission Factors sheet.

| # | value | where used | what is recorded now | what would close it |
|---|---|---|---|---|
| 1 | **pipeline_transport central 0.10** tCO2e/t | every chain with a pipeline; ~3% of lifetime. 25% error ≈ **±54 Mt** | "Assumed 0.10. No ICF or Sphera document stating this figure was located." The BC EAO Coastal GasLink check (1.47 vs 1.48 Mt/yr) confirms throughput scaling, not the factor | Any peer-reviewed or regulatory study giving a tCO2e per tonne LNG figure for **Canadian long-distance feedgas transmission**. A compressor-fuel intensity per km would also do — we could scale it on the 670 km Coastal GasLink calibration |
| 2 | **pipeline_transport range 0.05 / 0.18** | Monte Carlo triangle | "Assumed literature band, not a cited interval" | A published range, or two studies bracketing it |
| 3 | **regasification central 0.04** tCO2e/t | export/domestic/import chains; ~1%. 25% ≈ **±21 Mt** | "Assumed. Previously labelled RMI Oil Climate Index; no OCI+ table states 0.04 t/t." Gan et al. 2024 gives **0.021**, which sits at our range_low | Either a document supporting 0.04, **or** agreement to move the central to a cited value. Gan et al. 2024 (doi 10.1038/s43247-024-01988-2) is already in the sheet at 0.021 — if that is the best available number, the honest move is to adopt it and re-lock |
| 4 | **regasification range 0.02 / 0.06** | Monte Carlo triangle | Assumed band | A published range for import-terminal regasification, ideally splitting waste-heat-recovery designs from seawater vaporisers |
| 5 | **combustion range 2.50 / 3.00** tCO2e/t | Monte Carlo triangle on the **largest** stage (77.6% of lifetime). The bounds drive most of the published interval | "Range reflects variation in delivered gas composition." No citation. *(Central 2.75 is IPCC-cited and fine)* | A source for the spread in delivered pipeline-gas carbon content — IPCC 2006 Vol. 2 Table 1.2/1.3 give NCV and carbon-content **uncertainty ranges** that would derive these directly. That is probably the cleanest fix |
| 6 | **liquefaction range_high 0.36** | Emission Factors range only (MC does not sample liquefaction) | "Literature upper bound for gas-turbine plants." No study, page or URL | Any study or EA giving a high-end gas-turbine liquefaction intensity |
| 7 | **liquefaction_electric 0.12** | figure 8 appendix + Emission Factors range_low. **Not** in the headline | Now typed *assumption*, URL "Not available". No Pembina document states 0.12 — their *Squaring the Circle* (2023) uses 0.15 / 0.059 / 0.04, and *Wellhead to Waterline* (2014) reports a 0.11 t/t **reduction**, not a 0.12 absolute | Either a document stating 0.12 tCO2e/t for electric-drive liquefaction, or agreement to replace figure 8's counterfactual with a cited value (we already hold BC EAO 0.021 grid / 0.156 gas-barge, but those are facility totals including marine, not liquefaction-stage) |

---

## Tier 2 — method constants with no document

Small, but they are `method constant` labels over numbers with no source line.

| # | value | where used | what would close it |
|---|---|---|---|
| 8 | **lng_to_gas_bcm_per_mtpa = 1.38** | feedgas headroom vs pipeline capacity; the Fermeuse 5.0 mtpa derivation | A standard conversion from a gas-industry or regulator reference (LNG density × regas expansion ratio). Currently "Method constant used for feedgas allocation share", no URL |
| 9 | **lng_energy_content = 52 MMBtu/t** | Saint John TBtu → tonnes | Any LNG heating-value reference. Note our figure-10 comparison separately uses **55 MJ/kg HHV** for Balcombe — worth confirming the two are consistent or documenting why they differ |
| 10 | **cargo_tonnes_per_dwt = 0.85** | the shipping 0.110 reconstruction only | "Model assumption — typical ratio." An IMO, class-society or shipbuilder figure for LNG carrier cargo-to-deadweight ratio |

---

## Tier 3 — oil comparator (figure 7 only; does **not** move the headline)

| # | value | what is recorded now | what would close it |
|---|---|---|---|
| 11 | **tmx_oil_transport_per_barrel = 0.008** | "Declared assumption. 8 kgCO2e/bbl for pipeline transport. No document stating this figure for TMX was located." | A pipeline-transport emissions intensity per barrel for TMX or a comparable Canadian crude line |
| 12 | **alberta_bc_bitumen_pipeline_bpd = 1,000,000** | Still in `src/report_params.py`, flagged **UNVALIDATED**. Major Projects Office submission 2 July 2026 gives "over 1 million bpd"; we use the floor | A published design capacity. Until then the bar stays labelled unvalidated |

Two related things that are cited but worth a second opinion: `tmx_oil_upstream_per_barrel` 0.075
is NRCan's **oil sands** intensity while TMX also carries conventional crude (~48–49 kg/bbl), so
0.075 is on the heavy side for the actual ticket mix; and `tmx_oil_combustion_per_barrel` 0.43 is
IPCC generic crude, not a WCSB assay. Both are declared in the source cells.

---

## Tier 4 — declared assumptions a citation would upgrade

These are honestly labelled and defensible as judgements. A source would make them stronger.

| # | value | what would close it |
|---|---|---|
| 13 | **year_1_utilisation 0.40 / year_2 0.70 / ramp_years 2** | Any published LNG plant ramp-up profile — IGU, IEA or a facility EA |
| 14 | **fid_delay_low/mid/high 3 / 5 / 7 years** | An empirical average of FID-to-first-cargo slippage. IEA's Global LNG Capacity Tracker gives 4–5 years FID→completion (already on the sheet as `post_fid_to_completion`, currently unused) |
| 15 | **LNG Canada Phase 1 ramp 0.25 / 0.60 / 0.85** | URL is the company homepage. Actual reported throughput for 2025–26 would replace all three |
| 16 | **lifespan_sensitivity_low 30 years** | The Summit Lake PG LNG impact assessment states it; we just need the document URL |
| 17 | **upstream_ch4_share 0.30** | Has a Canada Gazette URL, but that is the methane regulations, not the share. **This is the highest-leverage assumption in the model** — it sets the 0.25 central upstream factor and the 0.428 GWP20 scenario. A BC-specific CO2/CH4 split for upstream oil and gas would be the single most valuable citation on this list |
| 18 | **canada_2030_overshoot_gap 200 Mt** | Now typed *assumption*; the arithmetic interval is 191–229. Either cite a published "gap" figure or keep it declared |

---

## Not worth chasing

**Model design choices** — cannot and should not be cited: `monte_carlo_seed`,
`monte_carlo_n_draws`, `headline_scope_chains`, `headline_scope_calc_groups`,
`liquefaction_drive_default`, `liquefaction_electrification_assumed`,
`assumed_first_export_year_if_missing`, `placeholder_sensitivity_years`, `mtpa_to_tonnes`,
`days_per_year`.

**Rows no code reads** (23 of them) — documentation and context only. Sourcing them buys nothing;
they should be marked as reference rows or deleted: `post_fid_to_completion`,
`methane_leakage_low/mid/high`, `canada_2005_baseline`, `canada_2030_projected`,
`canada_2035_target_low`, `coal_plant_reference_mw`, `coal_plant_capacity_factor`,
`coal_tco2e_per_mwh`, `bc_lng_emission_intensity_benchmark`,
`route_us_gulf_to_northeast_asia_nm`, `voyage_days_bc_to_north_asia`,
`ocean_transport_intensity_range_low/high`, `route_atlantic_routing_factor`,
`route_baie_comeau_to_rotterdam_nm`, `route_fermeuse_to_rotterdam_nm`,
`route_saint_john_to_rotterdam_nm`, `lng_carrier_aer_gco2_per_dwt_nm`,
`lng_carrier_kgco2_per_nm`, `cargo_tonnes_per_dwt`.

*(`cargo_tonnes_per_dwt` appears in both lists: no module reads it, but it is load-bearing for the
shipping reconstruction quoted in the README validation section.)*

---

## What a usable answer looks like

For each number, we need enough to put in a `source` cell and a `source_url` that a reviewer can
click and find the figure on:

- Author / issuing body, title, year
- **A direct link to the document**, not a homepage or a search page
- Page, table or figure number
- The value as stated, and its units and boundary (e.g. "tCO2e per tonne LNG, well-to-tank")

A homepage link is what got most of these flagged in the first place. If no document exists, say
so — we will type it `assumption` and declare it, which is what happened to pipeline 0.10 and
regasification 0.04.
