# Change report — 3 September 2026 (c): pipeline, methane share, benchmark table

Third change of 3 September. Both figures behind the pipeline move were read from the primary
documents; the methane-share research produced a bracket rather than a value, so nothing moved
there.

`python build_results.py` passes 42 assertions and ends "No input file was modified during the
run." Stale-figure inventory: 0 live hits.

---

## 1. Pipeline transport 0.10 → 0.074

Both routes verified from source, and both reproduce your arithmetic exactly.

**Route A — confirmed, with one correction to your note.** Liu et al. (2021), Results section,
**page 9713**: *"The company emissions intensities using both mass and energy allocation are
4.2 gCO2e/MJ NG at transmission pipeline outlet."* The paper does **not** report transmission
separately — Figure 2 shows it only as a stacked-bar component — so the subtraction stands as
the method.

I found the ERA restatement and it is more direct than expected. Modern West Advisory for
Emissions Reduction Alberta (2022), section 5.3, **page 43**: *"If the transmission emissions are
excluded to make the boundaries consistent with the present report, the estimated emission
intensity at NG plant exit is approximately 2.86 gCO2e/MJ NG."* The report states in terms that
the difference **is** the transmission pipeline, so this is not an inference across two
incompatible boundaries.

4.20 − 2.86 = 1.34 gCO2e/MJ × 54.863 GJ/t = **0.0735 tCO2e/t**.

**Route B — confirmed verbatim.** CER Market Snapshot (2022): *"In 2019, emissions resulting from
pipeline transport, primarily emissions related to combustion at compressor stations, accounted
for 8.3 MT CO2e"*, attributed to ECCC NIR 1990-2019 Part 1 Table 2-5. Over 170 bcm × 36 PJ/bcm =
6,120 PJ: 1.356 gCO2e/MJ = **0.0744 tCO2e/t**.

The two agree to **1.2%**. Stored as 0.074.

### Two corrections to your brief

**The transmission distance *is* stated.** Liu et al. Table 1, Section D gives pipeline length as
**1,100 km** (company data; US default 971 km). Your note said it was not stated. This matters
more than it looks: it means Route A is calibrated on a line *longer* than any of ours — Coastal
GasLink 670 km, PRGT 750 km, FortisBC Eagle Mountain 47 km — and Route B is a national average
haul. **Since we apply pipeline flat, with no distance scaling, 0.074 is more likely high than low
for these assets, Woodfibre most of all.** Recorded in the factor cell and the README as a stated
limitation, not corrected here.

**The paper contradicts itself on the headline number.** The abstract says 3.1–4.0 gCO2e/MJ; the
Results text says 4.2 for mass and energy allocation, and 3.1 / 3.3 for financial and
condensate-displacement allocation. The 4.2 used here is the Results figure on the allocation
basis this model uses. Noted in the cell so a reviewer meeting the abstract first is not
surprised.

### Where I disagree with the brief

You suggested that if no band could be built from the compressor-drivers paper, the range should
be **set from the two routes**. I have not done that, and I think it would be a mistake. The
paper is paywalled (HTTP 403) so the band could not be built — but 0.0735 and 0.0744 are two
independent estimates of the **central**, and their agreement is convergence, not precision. A
0.0735–0.0744 Monte Carlo band would assert that pipeline intensity is known to ±0.6%, which
would collapse its contribution to the published p5/p95 and imply a confidence nothing supports.

Instead the range is **0.037 / 0.133** — the relative width of the retired 0.05/0.18 band carried
onto the new central — typed **assumption, declared**, with the reasoning and the failed
attempt recorded in `range_sources`. Say the word if you want it set differently.

### Effect

| quantity | before | now |
|---|---|---|
| Lifetime CO2e | 7,215.3 Mt | **7,162.0 Mt** [6,632, 8,222] |
| Lifetime CO2-only | 6,948.8 Mt | **6,895.6 Mt** [6,295, 7,775] |
| Peak | 237.3 Mt (2037) | **235.6 Mt** (2037) [232, 257] |
| CAN / BUNK / FOR | 18.2 / 3.2 / 78.6 | **17.6 / 3.2 / 79.2** |
| ECCC 2% damages | C$3,126 bn | **C$3,103 bn** [2,804, 3,589] |
| `life_average_annual_mt` | 206.3 Mt/yr | **204.7 Mt/yr** |
| Committed | 1,859.5 Mt, C$745 bn | **1,845.8 Mt, C$739 bn** |
| Committed plus advanced | 3,785.4 Mt, C$1,570 bn | **3,757.5 Mt, C$1,559 bn** |

−53.3 Mt, in the 50–60 Mt you predicted. Pipeline is CAN-tagged, so cutting it moves the Canada
share down 0.6 points — the opposite direction to the regasification change earlier today.

### Re-locked

| constant | old | new |
|---|---|---|
| `EXPECTED_LIFETIME_MT` | 7215.3 | **7162.0** |
| `EXPECTED_PEAK_MT` | 237.3 | **235.6** |
| `EXPECTED_TERRITORIAL_SHARE_PCT` | 18.2 / 3.2 / 78.6 | **17.6 / 3.2 / 79.2** |
| `EXPECTED_BUILD_OUT` committed | 1859.5 / 1789.6 / 58.0 / 745 | **1845.8 / 1775.9 / 57.6 / 739** |
| `EXPECTED_BUILD_OUT` committed_plus_advanced | 3785.4 / 3643.1 / 135.0 / 1570 | **3757.5 / 3615.3 / 134.0 / 1559** |
| `EXPECTED_BUILD_OUT` full | 7215.3 / 6948.8 / 237.3 / 3126 | **7162.0 / 6895.6 / 235.6 / 3103** |
| `EXPECTED_PAPER_SET_SHA256` | `5d20d7fe…19eca7f4d` | **`3e325c3a…125b8f949`** |
| `EXPECTED_PEAK_YEAR`, capacity locks | — | unchanged |

---

## 2. Benchmark comparison table

New `Outputs/benchmark_comparison.csv`, a `Benchmark` sheet in `SLIDE_TABLES.xlsx`, and a section
in `RESULTS_SUMMARY.md`. Six rows, each carrying **both** boundaries and a like-for-like verdict
on the row rather than in a footnote. Built from the workbooks and `src.lca_comparison`, so it
cannot drift from the factors it compares. Asserted at six rows on every run.

| comparison | ours | external | like for like? | direction |
|---|---|---|---|---|
| Liquefaction | 0.290 | 0.330 (IEA 2025 global avg) | Close | ours **lower** |
| Shipping | 0.120 | 0.181 [0.138, 0.193] (IEA, to China / global / EU) | **No** — 10,000 km avg vs our 14,075 km | ours **lower on a longer voyage** |
| Pipeline transport | 0.074 | 0.0735 / 0.0744 (Liu 2021, CER 2022) | Partly | adopted |
| Regasification | 0.021 | 0.021 [0.011, 0.028] (Gan 2024, IEA) | Yes | adopted |
| Well → regasification | 0.755 | 1.19 [0.94, 1.51] (Roman-White 2021) | **No on geography** | ours **lower** |
| LNG stages only | 0.431 | 0.62–1.71 (Balcombe 2016) | Boundary yes, vintage no | ours **below the floor** |

**Every comparison that is not an adopted value points the same way: this model sits at or below
the external figure.** That is the table's real content. The two worth watching are shipping,
where the IEA implies roughly 2.3× our intensity per kilometre, and liquefaction, where the IEA
global average is 14% above our 0.29. Neither is like-for-like enough to act on; both are now
visible in one place instead of buried in `range_sources`.

---

## 3. upstream_ch4_share — bracketed, not closed

Johnson et al. (2023) is open access and I read it. It gives, for British Columbia in 2021:
total measurement-based upstream oil and gas methane of **144.5 kt/y**; an upstream methane
intensity of marketed gas of **0.38%** (95% CI 0.33–0.44%, SI section S3); and that this
measurement-based inventory is nominally **1.7×** the official ECCC bottom-up figure (range
1.5–2.0).

Two derivations onto the official inventory basis that `upstream_ch4_share` is defined against:

| route | method | at GWP 29.8 | at GWP 25 |
|---|---|---|---|
| **A, intensity** | 0.38% / 1.7 = 0.224% of marketed gas → 0.0666 tCO2e/t against the 0.22 factor | **30.3%** | 25.4% |
| **B, absolute** | 144.5 / 1.7 = 85.0 kt CH4 = 2.53 MtCO2e against the 10.04 MtCO2e the 0.22 factor implies over 63 bcm | **25.2%** | 21.2% |

Across the 1.5–2.0 correction range and both GWP vintages the bracket is roughly **18% to 34%,
centring near 25%**.

**So it does not close.** It corroborates 0.30 as being within range while showing it sits high.
I have not changed it: the evidence brackets rather than pins, and the choice has consequences
you should take deliberately. What it would move, if you did:

- Central upstream factor: **insensitive.** 0.2530 at 0.30 against 0.2475 at 0.25 — both round to
  0.25. `measurement_high` likewise rounds to 0.26 either way.
- `near_term_methane_gwp20`: **0.428 → 0.393.** An SI scenario.
- The CO2/CH4 split in the physics, and through it the SC-CH4 damages line.

The headline is untouched either way. That is worth knowing before spending more on it.

**Also recorded, per your instruction:** a note in the parameter cell that the national
fugitives-only share (~70%) must not be substituted here, because this model's upstream stage
includes stationary combustion and flaring, which are nearly all CO2 — using it would roughly
double the methane.

**Routes 2 and 3 not closed.** The ECCC NIR Part 3 provincial tables exist but are served through
a JavaScript data-mart portal rather than a direct download, so category 1.B.2 for BC could not
be pulled; the UNFCCC Common Reporting Tables are the route that would work. The BC methodology
report confirms upstream fugitives are Tier 3 bottom-up facility by facility, so the underlying
data does distinguish gases even though the published provincial tables are CO2e only. Both are
recorded in the parameter's notes.

---

## 4. One thing to fix on your side

`Outputs/CITATIONS_OUTSTANDING.md` is **not in the repository** — the file your message pointed at
for the full working does not exist here, on any branch. Everything above was done from the detail
in your message, which was sufficient. If that file has the underlying working, it is worth
committing so the derivations are in the deposit rather than in chat history.

---

## 5. Still open

- **Liquefaction range_high 0.36** — still an uncited literature upper bound.
- **Pipeline range 0.037/0.133** — declared assumption; the compressor-drivers paper is paywalled.
- **`upstream_ch4_share` 0.30** — bracketed at 18–34%, sitting high. Your call.
- **`cargo_tonnes_per_dwt` 0.85** and items 13–16, 18 from the wanted list — untouched.
- **Shipping 0.12** — the benchmark table now makes the gap against the IEA explicit. It is the
  most likely understatement left in the model.
