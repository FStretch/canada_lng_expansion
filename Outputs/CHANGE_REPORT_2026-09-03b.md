# Change report — 3 September 2026 (b): citations applied

Second change of 3 September. The first (`CHANGE_REPORT_2026-09-03.md`) applied the sourcing
audit and returned Discovery LNG to cancelled. This one applies the citations found against
`Outputs/CITATIONS_WANTED.md`.

Two central factors moved off uncited numbers onto documents. One figure was retired. The
headline fell 38.9 Mt.

`python build_results.py` passes 41 assertions and ends "No input file was modified during the
run." Stale-figure inventory: 0 live hits.

---

## 1. Headline

| quantity | before | now | why |
|---|---|---|---|
| Lifetime CO2e | 7,254.2 Mt | **7,215.3 Mt** [6,689, 8,290] | regasification 0.04 → 0.021 |
| Lifetime CO2-only | 6,987.7 Mt | **6,948.8 Mt** [6,347, 7,845] | same |
| Peak | 238.6 Mt (2037) | **237.3 Mt** (2037) [233, 259] | same |
| CAN / BUNK / FOR | 18.1 / 3.2 / 78.8 | **18.2 / 3.2 / 78.6** | regas is FOR-tagged, so cutting it shifts weight to CAN |
| ECCC 2% damages | C$3,143 bn | **C$3,126 bn** [2,827, 3,619] | same |
| `life_average_annual_mt` | 207.4 Mt/yr | **206.3 Mt/yr** | same |
| Committed | 1,869.5 Mt, C$749 bn | **1,859.5 Mt, C$745 bn** | same |
| Committed plus advanced | 3,805.7 Mt, C$1,579 bn | **3,785.4 Mt, C$1,570 bn** | same |
| Lifetime CH4 | 8,942 kt | 8,942 kt (unchanged) | regas carries no methane in the split |

Unlike the Discovery removal, this moves **every** build-out: regasification is on the export
chain for all nine assets.

---

## 2. Regasification 0.04 → 0.021 (item 3)

The row was entirely uncited: 0.04 was attributed to the RMI Oil Climate Index, which states no
such figure. It is now fully cited, central and range.

| | value | source |
|---|---|---|
| central | **0.021** tCO2e/t | Gan et al. (2024), *Communications Earth & Environment*, doi 10.1038/s43247-024-01988-2 — peer-reviewed US LNG lifecycle assessment |
| range_low | **0.011** | IEA (2025), *Assessing Emissions from LNG Supply and Abatement Options*, p. 16: "Total GHG emissions from regasification are around 0.2-0.5 g CO2-eq/MJ of gas regasified" |
| range_high | **0.0275** | same, upper end |

Converted at the IEA's own stated basis of 55 MJ per kg of methane (footnote 2, p. 7):
0.2 g/MJ × 55,000 MJ/t = 0.011 t/t; 0.5 g/MJ = 0.0275 t/t. The IEA takes 1 t methane as 30 t CO2
on a 100-year GWP, against this model's 29.8 — close enough not to matter at this stage's size.

The Gan central sits inside the IEA band, so the two sources agree. The old 0.04 sat **above** the
top of the IEA range.

Effect: −38.9 Mt on the lifetime (−0.54%), and regasification falls from ~1.1% to ~0.6% of the
lifecycle total.

---

## 3. Combustion range 2.50 → 2.58 (item 5)

The **central 2.75 is unchanged.** Only the lower bound moved, and only because the old one was
uncited and wider than the evidence supports.

Derived from IPCC 2006 Guidelines Vol. 2 Ch. 1, both 95% confidence intervals:

| | NCV (Table 1.2) | carbon (Table 1.3) | × 44/12 |
|---|---|---|---|
| lower | 46.5 TJ/Gg | 14.8 kgC/GJ | **2.523** tCO2/t |
| central | 48.0 | 15.3 | 2.693 |
| upper | 50.4 | 15.9 | **2.938** |

Cross-checked against Table 2.2: 56,100 kgCO2/TJ × 48.0 TJ/Gg = 2.693. Consistent.

IPCC's central of 2.693 is **pipeline natural gas**. This model's 2.75 is the stoichiometric value
for pure methane (44/16), which is the right central for LNG because liquefaction strips inerts
and heavier fractions. So the IPCC *relative* uncertainty (0.937 / 1.091) is applied to 2.75,
giving **2.58 / 3.00**. The old 3.00 was already right; the old 2.50 was too wide.

The two uncertainty ranges are combined multiplicatively, which is conservative — it treats NCV
and carbon content as perfectly correlated. That is recorded in the cell.

This changes no central value. It narrows the Monte Carlo interval slightly from below, on the
stage that is 77.6% of the total.

---

## 4. Liquefaction electric 0.12 → 0.15 (item 7)

Figure 8 only; not in the headline. 0.12 appears to have been a **misreading of a delta as a
level**: Pembina's *Wellhead to Waterline* (2014) reports a 0.11 tCO2e/t *reduction* from
electrification, not a 0.12 absolute intensity, and no Pembina document states 0.12.

Replaced with **0.15**, Pembina's published figure for LNG Canada Phase 1 under electric drive
(*Squaring the Circle: State of LNG 2023*). Applied to both `liquefaction_electric` on the
Parameters sheet and `range_low` on the Emission Factors sheet.

Figure 8's Canada-territorial bars move: gas 37.5 → claimed-electric 32.6 → all-electric 29.3
Mt/yr (previously 32.4 / 28.8 at 0.12).

The same Pembina report gives 0.059 for LNG Canada Phase 2 and 0.04 for Woodfibre; those are
facility-specific and are not used. The BC EAO 0.021 / 0.156 pair stays a separate SI sensitivity
on a facility-total boundary.

---

## 5. Figure 7 retired (items 11 and 12)

The Trans Mountain slide has been dropped from the deck, so the comparison was removed from the
model rather than left generating an unpublished figure on unsourced arithmetic.

Removed: `figure_7_oil_comparison`, slide table `15_Oil_comparison`, `oil_lifecycle_gt`,
`src/report_params.py` (its only remaining contents were the oil comparators), the two `fig07_*`
CSVs and the PNG, six entries in `REQUIRED_PARAMS`, and seven Parameters rows —
`tmx_oil_upstream_per_barrel`, `tmx_oil_transport_per_barrel`, `tmx_oil_combustion_per_barrel`,
`tmx_oil_lifecycle_per_barrel`, `tmx_total_system_bpd`, `tmx_expansion_bpd`, `days_per_year`.

What it had wrong, for the record: three addends never separately sourced; NRCan's oil-sands
intensity applied to a mixed ticket slate; oil at nameplate × 365 × 40 against an LNG side
carrying a ramp, a utilisation curve and an FID delay, understating LNG by roughly 19%; and an
unvalidated 1 Mbpd capacity for a pipeline with no published design figure. Slide table numbering
keeps the gap at 15 so existing deck references do not shift. History is in git.

---

## 6. Documented without changing a value (items 8 and 9)

**`lng_energy_content = 52 MMBtu/t`.** No inconsistency to fix: 52 × 1.05506 = 54.86 GJ/t against
the 55 MJ/kg HHV used for the Balcombe comparison and by the IEA. A 0.25% difference, both HHV.
The conversion is now recorded in the cell and the row is typed `cited`.

**`lng_to_gas_bcm_per_mtpa = 1.38`.** Kept, with the basis recorded: LNG density ~450 kg/m³ and a
liquid-to-gas expansion ratio near 600:1 at 15 °C and 101.325 kPa. The Energy Institute
conversion gives 1.36 on its own reference conditions; 1.38 is 1.5% higher. At 1.36 the Fermeuse
derivation gives 5.05 mtpa rather than 4.98 — it rounds to 5.0 either way, and no published figure
moves. No module reads this parameter; it backs the stored feedgas headroom columns, which stay
consistent with 1.38.

---

## 7. Assertions re-locked

| constant | old | new |
|---|---|---|
| `EXPECTED_LIFETIME_MT` | 7254.2 | **7215.3** |
| `EXPECTED_PEAK_MT` | 238.6 | **237.3** |
| `EXPECTED_PEAK_YEAR` | 2037 | 2037 (unchanged) |
| `EXPECTED_TERRITORIAL_SHARE_PCT` | 18.1 / 3.2 / 78.8 | **18.2 / 3.2 / 78.6** |
| `EXPECTED_BUILD_OUT` committed | 1869.5 / 1799.6 / 58.3 / 749 | **1859.5 / 1789.6 / 58.0 / 745** |
| `EXPECTED_BUILD_OUT` committed_plus_advanced | 3805.7 / 3663.5 / 135.8 / 1579 | **3785.4 / 3643.1 / 135.0 / 1570** |
| `EXPECTED_BUILD_OUT` full | 7254.2 / 6987.7 / 238.6 / 3143 | **7215.3 / 6948.8 / 237.3 / 3126** |
| `EXPECTED_PAPER_SET_SHA256` | `58236e9b…16012985c` | **`5d20d7fe…19eca7f4d`** |
| `EXPECTED_EXPORT_TOTAL`, `EXPECTED_EXPORT_BY_CALC`, early/advanced | — | unchanged (no capacity moved) |

---

## 8. Still open after this round

**Item 1 and 2 — pipeline transport 0.10 and its 0.05/0.18 range.** The IEA report was the best
candidate and it does **not** close them: it bundles transmission with production and processing
and never reports it separately. This is now the largest uncited number in the model.

**Item 6 — liquefaction range_high 0.36.** Still an uncited literature upper bound. Context from
the IEA: global average liquefaction is about 6 gCO2e/MJ = 0.33 tCO2e/t, which sits between our
central 0.29 and our high 0.36 — so 0.29 is *below* the world average, not a high-side choice.

**Item 17 — `upstream_ch4_share = 0.30`.** Still the highest-leverage assumption in the model. I
could not close it: the Nature paper (Johnson et al.) is behind an authentication redirect, and
ECCC's provincial-by-gas tables exist but sit behind a JavaScript portal rather than a direct
download. The route that would work is the UNFCCC Common Reporting Tables for Canada, category
1.B.2 fugitive emissions, provincial breakdown — those report CO2 and CH4 separately.

**Items 10, 13–16, 18** — not searched this round; all honestly declared.

**Two IEA figures worth a decision later, not acted on:**

- **Shipping.** IEA gives 3.3 gCO2e/MJ for LNG delivered to China = 0.18 tCO2e/t, against this
  model's 0.12 on a *longer* voyage (14,075 km round trip vs the IEA's 10,000 km average). The
  boundaries differ — IEA is fleet-average with methane slip at GWP 30 — but the direction
  suggests 0.12 may be low.
- **Liquefaction.** IEA's 0.33 t/t global average against our 0.29, as above.

Neither is a like-for-like drop-in, and the original ground rules hold liquefaction at 0.29. Both
are recorded in the Emission Factors `range_sources` cells so a reviewer meets them there.
