# Task A diagnostic: gap vs Roman-White 2021

<!-- lock-banner:start -->
> **Dated document.** Diagnostic of the gap to Roman-White et al. (2021) on the aligned well-to-regasification boundary, 28 August 2026.
> Written against a model well-to-regasification intensity of 0.80 tCO2e/t LNG, before regasification moved from 0.04 to 0.021 and pipeline transport from 0.10 to 0.074.
> The stage mapping and the reasoning below stand; the model side of the comparison has moved. The current figure is in `Outputs/figure_data/fig10_lca_comparison.csv` and the six-row boundary-aligned comparison in `Outputs/benchmark_comparison.csv`.
> **Current lock:** **7,162.0 Mt** lifetime CO2e, **235.6 Mt** peak in 2037, **17.6 / 3.2 / 79.2** CAN / BUNK / FOR, **C$3,108 bn** ECCC damages, **80.1 mtpa** of export capacity; well-to-regasification **0.76 tCO2e/t LNG**.
> This banner is generated from the lock in `build_results.py` and asserted on every run; edit nothing between the markers.
<!-- lock-banner:end -->

Diagnostic only. No emission factor was changed. Liquefaction remains 0.29.

On the aligned well-to-regasification GWP100 boundary this model is **0.80 tCO2e/t LNG** against Roman-White et al. 2021 expected **1.19** (P2.5–P97.5: 0.94–1.51). Gap to expected: **0.39**.

## Stage taxonomy mapping

| This model | Roman-White 2021 (Cheniere SPL) | Mapping |
|---|---|---|
| `upstream_production` 0.25 | production; gathering & boosting; processing | This model’s 0.25 is a Canadian inventory-plus-measurement factor covering extraction through processing. Roman-White publish **extraction only** at 0.25 tCO2e/t regasified (GWP100). G&B and processing are additional in their model and are **not published as standalone t/t**. |
| `pipeline_transport` 0.10 | transmission compression, storage, pipeline (US, basin → Sabine Pass; mean 975 miles for known suppliers) | Same physical idea (feedgas to the terminal). Not published as a standalone t/t. |
| `liquefaction` 0.29 | Sabine Pass operational GHGRP + AGRU CO2, gas turbine | Not published as a standalone t/t. Text says SPL is 8–13% below Gan et al. and comparable to NETL. |
| `shipping` 0.12 | ocean transport, 2018 voyage logs, round trip | Figure 3 publishes **0.05 (Jamaica) to 0.31 (Taiwan)** tCO2e/t delivered. **China is not tabulated as a stage.** |
| `regasification` 0.04 | destination-port ORV, 0.00367 kg NG / kg LNG | Not published as a standalone t/t in Table 1. SI energy intensity implies ~0.01 t/t at 2.75 tCO2e/t combustion. |
| (not in this model) | foreign pipeline, regas → power plant (China 50–200 miles) | Outside the well-to-regas Table 1 boundary. |

Roman-White Table 1 publishes **cumulative** boundaries, not a stage vector. Figure S12 is a stacked stage chart for China/UK; the extracted SI text does not give the bar values, so those are not used.

## Cumulative comparison (published Table 1 expected vs this model)

Functional units differ slightly across Table 1 rows (t liquefied / t shipped / t regasified) because boil-off changes the denominator. Increments below are exact differences of published expected values; they are **not** published stage totals.

| Boundary | This model | Roman-White expected | Difference | Share of 0.39 gap |
|---|---:|---:|---:|---:|
| Cradle → liquefaction | 0.64 | 0.82 | 0.18 | **46%** |
| Cradle → shipping (China) | 0.76 | 1.18 | 0.42 | — |
| of which ocean increment (1.18−0.82 vs 0.12) | 0.12 | 0.36 | 0.24 | **62%** |
| Cradle → regasification (China) | 0.80 | 1.19 | 0.39 | 100% |
| of which regas increment (1.19−1.18 vs 0.04) | 0.04 | 0.01 | −0.03 | **−8%** |

Check: 0.18 + 0.24 − 0.03 = 0.39.

## What is published as a stage, not inferred

| Quantity | Value | Source |
|---|---|---|
| Cheniere extraction | 0.25 tCO2e/t regasified GWP100 | Roman-White text; same number as this model’s upstream central |
| Ocean transport by market | 0.05–0.31 tCO2e/t delivered | Figure 3; Jamaica / Taiwan. China not listed |
| This model shipping reconstruction | 0.110 t/t | IMO 8.50 gCO2/dwt-nm × 7,600 nm round trip / 0.85 cargo-per-dwt × 1.44 methane-slip uplift. Central factor is 0.12 |

## Shipping hypothesis (quantitative)

Route distances are on the Parameters sheet and are **not used by the model**. Shipping is a flat 0.12 from Emission Factors. The 0.12 was reconstructed (README) from `route_bc_to_northeast_asia_nm` = 3,800 nm one-way (7,600 nm round trip).

| Route | Parameter | One-way nm | Round-trip nm |
|---|---|---:|---:|
| BC → northeast Asia (this model’s 0.12 basis) | `route_bc_to_northeast_asia_nm` | 3,800 | 7,600 |
| US Gulf → northeast Asia (stored, unused) | `route_us_gulf_to_northeast_asia_nm` | 9,200 | 18,400 |

Distance ratio Gulf / BC = **2.42**.

Roman-White do not publish a China nautical-mile figure; they use 2018 Sabine Pass voyage logs. 9,200 nm is this model’s stored Gulf–NE-Asia distance, not a Roman-White number.

If this model’s shipping scaled linearly with that ratio:

- 0.12 × 2.42 = **0.29**
- IMO reconstruction 0.110 × 2.42 = **0.27**

Compare with Roman-White:

- Table 1 ocean *increment* (China, not a stage): **0.36** — 3.0× this model’s 0.12, **24% above** distance-scaled 0.29
- Figure 3 long-Asia *stage* (Taiwan): **0.31** — 2.6× this model’s 0.12, **7% above** distance-scaled 0.29

The shipping difference is **mostly** a route-length effect. It is not the whole 0.39 gap. After replacing 0.12 with the distance-scaled 0.29, this model’s well-to-regas would be **0.97**, which sits inside Roman-White’s 0.94–1.51 and still **0.22 below** their expected 1.19. That remainder is the cradle-to-liquefaction block (0.18) plus a small residual on ocean/regas.

## Upstream is not the explanation

Cheniere extraction 0.25 equals this model’s upstream 0.25. The 0.18 cradle-to-liq gap sits in the unpublished combination of G&B, processing, US transmission, and SPL liquefaction versus this model’s pipeline 0.10 + liquefaction 0.29. Those four Roman-White stages are **not published as t/t**, so they are not split further.

## Liquefaction cannot be shown to dominate

This model 0.29 is LNG Canada EA gas-turbine. Roman-White SPL is also gas-turbine operational data. Without a published SPL liquefaction-only t/t, liquefaction is not identified as the carrier of the 0.18.

## Which of the three outcomes

**Mixed, not a single carrier.**

- Shipping is the largest *attributable increment* (0.24, 62% of the gap) and is **largely proportionate to route length** (2.42× distance → 0.29 vs Taiwan stage 0.31). That part of the referee exposure is a route-length argument, and it is already sitting in this model as `range_high` 0.31.
- Shipping does **not** account for the whole gap. Cradle-to-liquefaction is 0.18 (46%). Extraction matching 0.25 means this is not “Canadian upstream is quieter than a US basin.” It is an unpublished mix of G&B / processing / transmission / liquefaction.
- Liquefaction is **not** shown to dominate. Do not change 0.29 on the basis of this.

No factor change is warranted from this diagnostic. If a later decision is to *report* a China-equivalent shipping intensity, that is a discrete scenario using the existing 0.31 high, not a change to the central 0.12 (which is BC–NE Asia).

## Balcombe 2016 compilation (liq + shipping + regas)

This model: **0.45** (0.29 + 0.12 + 0.04).
Balcombe total LNG-stage range: **11.2–31.1 gCO2e/MJ HHV** → **0.62–1.71 t/t** at 55 MJ/kg HHV (conversion stated; not Balcombe’s own mass basis).

Gap to the compilation *low* end: **0.17**. Gap to the high end is not a single-study gap.

Balcombe (2016, ACS) *does* publish literature ranges by LNG stage, compiled from other papers. They are not one chain and the stage minima do not sum to 11.2.

| Stage | Balcombe 2016 literature (gCO2e/MJ HHV) | Same, t/t at 55 MJ/kg | This model t/t | Inside the compilation range? |
|---|---|---:|---:|---|
| Liquefaction (fuel CO2) | 4.1–7.7 | 0.23–0.42 | 0.29 | yes |
| Liquefaction methane (additional) | 0.01–4.22 | 0.00–0.23 | (inside 0.29) | — |
| Tanker | 0.9–7.3 | 0.05–0.40 | 0.12 | yes |
| Regasification | 0.26–2.53 | 0.01–0.14 | 0.04 | yes |
| LNG stages **total** (separate compilation) | 11.2–31.1 | 0.62–1.71 | **0.45** | **below the low end** |

This model’s stages sit inside each compiled *stage* band. The 0.45 total sits below 0.62 because 11.2 is not the sum of the stage lows (4.1 + 0.9 + 0.26 = 5.26 g/MJ). Different studies populate different stages; adding this model’s centrals produces a quieter total than any full-chain study in that compilation.

Converted the other way: 0.45 t/t ÷ 55 MJ/kg = **8.2 gCO2e/MJ HHV**, below 11.2.

No stage in this model is outside Balcombe’s per-stage literature band. The total gap is a compilation-arithmetic feature, not evidence that a single factor is wrong. No factor change.
