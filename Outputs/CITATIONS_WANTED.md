# Citations wanted

Refreshed 3 September 2026, after the publication audit and the housekeeping sweep.
Checked against the workbooks as they stand.

Current lock: **7,162.0 Mt** lifetime, **235.6 Mt** peak in 2037,
**17.6 / 3.2 / 79.2** territorial, **C$3,108 bn** damages.

**Closed so far:** regasification central and range, combustion range,
liquefaction electric, pipeline central, `lng_energy_content`,
`lng_to_gas_bcm_per_mtpa`, the oil comparator (retired with figure 7),
`upstream_ch4_share`, the FID delay band, and `lifespan_sensitivity_low`.

---

## A. Decisions for the authors — more research will not help

| item | position | what it moves |
|---|---|---|
| **Shipping 0.12** | IEA 2025 gives 0.18 tCO2e/t to China on a *shorter* average voyage (10,000 km vs our 14,075 km). Per km the IEA implies ~2.3× our intensity. All four non-comparabilities are now recorded in `range_sources`. | The largest remaining exposure. Shipping is ~3% of the lifetime; moving to the IEA basis would be worth roughly **+100 Mt**. Held because our 0.12 is Howarth reconstructed from IMO DCS data on the voyage we actually model. |
| **Liquefaction 0.29** | IEA 2025 global average is 0.33 — ours is 14% below the world average. | Held by the paper's ground rules, not by a missing source. Worth ~**+280 Mt**. |
| **Pipeline range 0.037 / 0.133** | Set as the relative width of the retired band, not the gap between the two cited routes. Those two are estimates of the *central*. | A band set from the routes would assert pipeline is known to ±0.6% and collapse its share of the published p5/p95. |
| **Generic utilisation ramp 0.40 / 0.70** | **New, and sharper than before.** The LNG Canada Phase 1 observed data now recorded shows the model starts too high and ramps too slowly: 11% of a full year in calendar 2025 against an assumed 25%, then 86% and 103% of nameplate in April and May 2026 against an assumed 60%. | Phase 1 has its own override, so this is about the *generic* ramp applied to every other asset. The average is about right and the errors offset over a full life, so this is a shape question, not a level one. Fixing it properly needs a decision about whether one facility's profile generalises. |

---

## B. Research still open — someone needs to find a document

| value | where used | what would close it |
|---|---|---|
| **Pipeline range structure** | Monte Carlo triangle | "Regional greenhouse gas analysis of compressor drivers in natural gas transmission systems in Canada", *J. Cleaner Production* (2023), doi 10.1016/j.jclepro.2023.137150 — **paywalled, HTTP 403**. Institutional access closes it. |
| **Liquefaction range_high 0.36** | Emission Factors range only; the Monte Carlo does **not** sample liquefaction | Any study or EA with a high-end gas-turbine liquefaction intensity. Low stakes — display only. |
| **Utilisation ramp 0.40 / 0.70, `ramp_years` 2** | Year-1 and year-2 throughput for every asset except Phase 1 and Saint John | A published multi-facility LNG ramp-up profile. See A4 — we now know the shape is wrong, but not what to replace it with. |
| **`cargo_tonnes_per_dwt` 0.85** | The shipping 0.110 reconstruction in the README validation only — **no module reads it** | A class-society (DNV, Lloyd's) or IMO figure for LNG carrier cargo-to-deadweight ratio. Now marked `reference-only` on the Parameters sheet, so the open citation affects the reconstruction narrative and no published number. |

---

## C. Housekeeping — no sourcing needed

**23 Parameters rows no module reads — done, 3 September 2026.** The Parameters sheet now carries
a `status` column, `live` or `reference-only`, derived by scanning the code rather than typed by
hand. 53 live, 23 reference-only. Every reference-only row names what it is for and, where one
exists, its live counterpart, so the workbook never holds two disconnected versions of one fact.

**One decision left over from that sweep.** Three of the 23 have **no live counterpart at all**:
`coal_plant_reference_mw` 500, `coal_plant_capacity_factor` 0.55, `coal_tco2e_per_mwh` 0.95. The
coal-plant equivalence comparator they would support is in no figure, no slide table and no
output. Their notes say so plainly. They are the only genuinely orphaned rows in the workbook —
keep them as a stub for a comparator someone may want, or drop all three. Sourcing them would be
work spent on a calculation nothing performs.

**Upstream 0.25 and 0.26 are two-decimal rounds** of 0.2475 and 0.2585 at the current methane
share. Declared in the README.

---

## Not worth chasing

Model design choices, uncitable by nature: `monte_carlo_seed`, `monte_carlo_n_draws`,
`headline_scope_chains`, `headline_scope_calc_groups`, `liquefaction_drive_default`,
`liquefaction_electrification_assumed`, `assumed_first_export_year_if_missing`,
`placeholder_sensitivity_years`, `mtpa_to_tonnes`.

---

## What a usable answer looks like

Issuing body, title, year; a **direct link** to the document, not a homepage or a search page;
page, table or figure number; and the value as stated, with its units and boundary.

"No document exists" is a fine answer — that is how pipeline 0.10 and regasification 0.04 came to
be typed as assumptions before they were replaced.
