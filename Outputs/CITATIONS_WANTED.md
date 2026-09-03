# Citations wanted

Refreshed 3 September 2026, after the pipeline, regasification, combustion and
liquefaction-electric changes. Checked against the workbooks as they stand.

Current lock: **7,162.0 Mt** lifetime, **235.6 Mt** peak in 2037,
**17.6 / 3.2 / 79.2** territorial, **C$3,103 bn** damages.

**Closed since the first version of this list:** regasification central and range,
combustion range, liquefaction electric, pipeline central, `lng_energy_content`,
`lng_to_gas_bcm_per_mtpa`, and the oil comparator (retired with figure 7).

---

## A. Decisions for the authors — more research will not help

| # | item | position | what it moves |
|---|---|---|---|
| A1 | **`upstream_ch4_share` 0.30** | Johnson et al. (2023) brackets it at **18–34%, centring near 25%**. 0.30 sits high but is not excluded. | Headline **insensitive** — central upstream is 0.2530 at 0.30 against 0.2475 at 0.25, both rounding to 0.25. Moves only the `near_term_methane_gwp20` SI scenario (0.428 → 0.393) and the CO2/CH4 split behind the SC-CH4 damages line. |
| A2 | **Shipping 0.12** | IEA 2025 gives 0.18 tCO2e/t to China on a *shorter* average voyage (10,000 km against our 14,075 km). Per km the IEA implies roughly 2.3× our intensity. | The most likely understatement left in the model. Shipping is ~3% of the lifetime, so a move to the IEA basis would be worth roughly +100 Mt. Not like-for-like: fleet average, methane slip at GWP 30, origin-blended. |
| A3 | **Liquefaction 0.29** | IEA 2025 global average is 0.33. Ours is 14% below the world average. | Held at 0.29 by the paper's ground rules. Lifting that rule is the decision, not finding a source. Worth ~+280 Mt. |
| A4 | **Pipeline range 0.037 / 0.133** | I set this against your brief: the relative width of the retired band, not the gap between the two routes. The two routes are estimates of the *central*; their 1.2% agreement is convergence, not precision. | If you want it set from the routes it is a one-line change — but it would assert pipeline is known to ±0.6% and collapse its share of the published p5/p95. |

---

## B. Research still open — someone needs to find a document

| # | value | where used | what would close it |
|---|---|---|---|
| B1 | **Pipeline range structure** | Monte Carlo triangle | "Regional greenhouse gas analysis of compressor drivers in natural gas transmission systems in Canada", J. Cleaner Production (2023), doi 10.1016/j.jclepro.2023.137150 — **paywalled, HTTP 403**. Institutional access would close it. |
| B2 | **Liquefaction range_high 0.36** | Emission Factors range only; the Monte Carlo does **not** sample liquefaction | Any study or EA giving a high-end gas-turbine liquefaction intensity. Low stakes: display only. |
| B3 | **Utilisation ramp 0.40 / 0.70, `ramp_years` 2** | year-1 and year-2 throughput for every asset but Phase 1 and Saint John | Any published LNG plant ramp-up profile — IGU, IEA, or a facility EA. |
| B4 | **`fid_delay_low/mid/high` 3 / 5 / 7 years** | start year for the seven non-FID assets | An empirical FID-to-first-cargo distribution. Note `post_fid_to_completion` = 4.5 (IEA, 4–5 years) already sits on the sheet **unused** — it may be enough to derive the mid. |
| B5 | **LNG Canada Phase 1 ramp 0.25 / 0.60 / 0.85** | Phase 1 only | URL is the company homepage. Actual reported 2025–26 throughput replaces all three and turns a judgement into an observation. |
| B6 | **`lifespan_sensitivity_low` 30 years** | Monte Carlo life triangle low | The Summit Lake PG LNG impact assessment states it. This is a **lookup, not research** — we just need the document URL. |
| B7 | **`cargo_tonnes_per_dwt` 0.85** | the shipping 0.110 reconstruction quoted in the README validation section only — **no module reads it** | A class-society or IMO figure for LNG carrier cargo-to-deadweight ratio. |

---

## C. Housekeeping — no sourcing needed

- **23 Parameters rows no module reads.** Documentation and context only. They should be marked
  reference-only or deleted; sourcing them buys nothing. Includes `post_fid_to_completion`,
  `methane_leakage_low/mid/high`, the three coal-plant comparators,
  `bc_lng_emission_intensity_benchmark`, most `route_*` rows, `cargo_tonnes_per_dwt` and
  `lng_to_gas_bcm_per_mtpa`.
- **Upstream 0.25 and 0.26 are two-decimal rounds** of 0.2530 and 0.2662. Declared in the README.

---

## Not worth chasing

Model design choices, uncitable by nature: `monte_carlo_seed`, `monte_carlo_n_draws`,
`headline_scope_chains`, `headline_scope_calc_groups`, `liquefaction_drive_default`,
`liquefaction_electrification_assumed`, `assumed_first_export_year_if_missing`,
`placeholder_sensitivity_years`, `mtpa_to_tonnes`.

---

## What a usable answer looks like

Issuing body, title, year; a **direct link** to the document, not a homepage or a search page;
page, table or figure number; and the value as stated with its units and boundary. "No document
exists" is a fine answer — that is how pipeline 0.10 and regasification 0.04 came to be typed as
assumptions before they were replaced.
