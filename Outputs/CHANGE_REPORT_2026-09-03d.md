# Change report — 3 September 2026 (d): methane share, FID band, shipping and ramp documentation

Fourth change of 3 September. Both source quotations were read from the primary documents.

`python build_results.py` passes 42 assertions and ends "No input file was modified during the
run." Stale-figure inventory: 0 live hits.

**One disagreement with the brief, flagged rather than done silently: the FID band change moves
the Monte Carlo interval DOWN, not up.** Section 2.

---

## 1. Headline

The lifetime, the peak and the territorial split are **bit-identical** to before this round.
Neither change touches them.

| quantity | before | now | moved by |
|---|---|---|---|
| Lifetime CO2e | 7,162.0 Mt | **7,162.0 Mt** — unchanged | — |
| Peak | 235.6 Mt (2037) | **235.6 Mt** (2037) — unchanged | — |
| CAN / BUNK / FOR | 17.6 / 3.2 / 79.2 | **17.6 / 3.2 / 79.2** — unchanged | — |
| Lifetime CO2-only | 6,895.6 Mt | **6,918.1 Mt** (+22.5) | methane share |
| Lifetime CH4 | 8,942 kt | **8,186 kt** (−756) | methane share |
| ECCC 2% damages | C$3,103 bn | **C$3,108 bn** (+5) | methane share |
| Methane share of the damage bill | 1.70% | **1.57%** | methane share |
| `near_term_methane_gwp20` upstream | 0.428 | **0.393** | methane share |
| Committed | 1,845.8 Mt, C$739 bn | **1,845.8 Mt, C$741 bn** | methane share |
| Committed plus advanced | 3,757.5 Mt, C$1,559 bn | **3,757.5 Mt, C$1,561 bn** | methane share |

Damages rise slightly because less of the total is now methane, and methane priced at SC-CH4 is
cheaper per tonne of CO2e than CO2 priced at SC-CO2. Moving mass from the CH4 column to the CO2
column therefore costs more, not less.

---

## 2. `upstream_ch4_share` 0.30 → 0.25

Done as instructed. Johnson et al. (2023) cited as the basis, with the 18–34% bracket and both
derivation routes recorded in the source cell, and the "do not substitute the national
fugitives-only share" warning kept.

**Your prediction held exactly.** The stored `measurement_central` upstream factor is 0.2530 at a
share of 0.30 and 0.2475 at 0.25, both rounding to the stored 0.25 — so the headline did not move
by so much as a rounding artefact. Nothing to stop for.

`near_term_methane_gwp20` was updated with it, since it is derived from the share:

```
0.22 × (1 − 0.25)                          = 0.165   non-methane inventory, unchanged
0.22 × 0.25 × 1.5 × (82.5 / 29.8)          = 0.228   methane portion, corrected then GWP20-weighted
                                             -----
                                             0.393
```

Scenario range on the new share:

| scenario | upstream | lifetime Mt |
|---|---|---|
| `inventory_as_reported` | 0.220 | 7,100.6 |
| `measurement_central` (paper) | 0.250 | **7,162.0** |
| `measurement_high` | 0.260 | 7,182.5 |
| `near_term_methane_gwp20` | 0.393 | 7,455.0 |
| `howarth_high` | 0.550 | 7,776.5 |

---

## 3. FID delay 3 / 5 / 7 → 4 / 5 / 8

Both quotations confirmed from the primary sources.

- **IEA Global LNG Capacity Tracker:** *"the long time lag of 4 to 5 years, on average, between
  project FID and completion."*
- **Rogers (2017), OIES Energy Insight 4, February 2017, page 1** — you asked me to confirm the
  page: *"Note that the time from FID to project completion is typically 5 years, before
  unforeseen slippage."* It sits on page 1, in a bulleted list of the factors that explain why
  2004–2009 LNG capacity forecasts overshot what was actually delivered. That context supports
  your asymmetry argument directly: the sentence exists to explain projects arriving *late*.

The mid stays 5 and the central case is untouched. The asymmetry and its reason are in all three
source cells.

`post_fid_to_completion = 4.5` is now **marked reference-only**, with a note that it rests on the
same IEA statement as `fid_delay_mid`, that the model reads `fid_delay_mid` instead, and that the
two must not be cited as independent facts. Wiring it in would have meant retiring
`fid_delay_mid`, which is a larger change than the brief asked for.

### The disagreement: this moves the interval down, not up

You expected the band change to *"widen the published p5/p95 upward"*. It does neither. Decomposed
on the full build-out lifetime, holding the seed:

| state | median | p5 | p95 | width |
|---|---|---|---|---|
| before, share 0.30 and FID 3/5/7 | 7,397.4 | 6,632.3 | 8,221.5 | 1,589.2 |
| methane share only | 7,375.9 | 6,618.7 | 8,188.1 | 1,569.4 |
| **FID band only** | **7,280.8** | **6,518.1** | **8,103.8** | **1,585.7** |
| both (published) | 7,257.1 | 6,493.9 | 8,074.8 | 1,580.9 |

The FID band alone shifts the whole distribution **down by 117 Mt** and leaves the width
essentially unchanged (−3.5 Mt).

The mechanism is that **the FID delay sits inside the lifespan window rather than extending it**.
A delayed project does not run later for the same number of years — it runs *fewer* years, because
the delay years are consumed from the front of a fixed life. The mean of triangular(4, 5, 8) is
5.67 years against 5.00 for triangular(3, 5, 7), so the seven non-FID assets lose about two-thirds
of a year of production each.

The change is still right — the asymmetry argument is sound and the sources support it. But the
consequence is a **downward shift in the emissions distribution**, and anyone told to expect a
widening will read the new interval as an error. Worth knowing before it reaches a reviewer.

The published interval is now **7,162.0 Mt [6,494, 8,075]** against [6,632, 8,222] before.

---

## 4. Shipping 0.12 — held, comparison documented

Value untouched. `range_sources` now answers the IEA comparison before a reviewer raises it, with
all four differences you listed:

1. **Distance** — IEA average round trip 10,000 km against our 14,075 km, so the IEA figure is for
   a *shorter* voyage
2. **Fleet average, not route** — about 7,000 round trips in 2024 across the world fleet,
   including Arctic ice-class voyages such as Yamal to China
3. **GWP basis** — IEA takes 1 t CH4 as 30 t CO2 against our 29.8, with fleet-wide slip rather than
   the measured 1.44 uplift
4. **Origin-blended** — "to China" mixes US Gulf, Qatari, Australian and Russian origins

And the honest statement of the gap: **per kilometre the IEA implies roughly 2.3× our intensity**,
which the boundary differences do not resolve. The cell states why 0.12 is kept anyway — it is
Howarth's figure independently reconstructed from IMO DCS fleet data on the voyage we actually
model (8.50 gCO2/DWT/nm over 7,600 nm, to cargo tonnes, uplifted 44% for slip, giving 0.110), and
a route-specific derivation on our own voyage beats a fleet average on a different one.

---

## 5. LNG Canada Phase 1 ramp — observed data recorded, model unchanged

All five observations recorded against the three ramp parameters, with sources: first cargo
30 June 2025 and Train 2 from November 2025 (GEM, Norton Rose Fulbright); 4 / 10 / 11 vessel
departures in December 2025, January and February 2026 (Kpler via Globe and Mail); ~4.6 Mt to
mid-March 2026 (RBC via the same article); 60th cargo mid-March and ~80 cargoes by early May 2026
(EnergyNow); first month above 1 Mt in April 2026, 1.2 Mt/month by May.

Your arithmetic checks out against 14 mtpa nameplate: calendar 2025 at roughly 11% of a full year
against the assumed 25%, then 86% and 103% of nameplate in April and May 2026 against the assumed
60% for year two. **The average is about right; the shape is not** — the model starts too high and
ramps too slowly, and the two errors largely offset over the life. Recorded as a known limitation
in the parameter cells and the README, not corrected, because one facility's observed profile is
not a basis for the generic ramp applied to every other asset.

---

## 6. Assertions re-locked

| constant | old | new |
|---|---|---|
| `EXPECTED_LIFETIME_MT` | 7162.0 | **7162.0 — unchanged** |
| `EXPECTED_PEAK_MT` / `EXPECTED_PEAK_YEAR` | 235.6 / 2037 | **unchanged** |
| `EXPECTED_TERRITORIAL_SHARE_PCT` | 17.6 / 3.2 / 79.2 | **unchanged** |
| `EXPECTED_BUILD_OUT` committed | 1845.8 / 1775.9 / 57.6 / 739 | **1845.8 / 1781.7 / 57.6 / 741** |
| `EXPECTED_BUILD_OUT` committed_plus_advanced | 3757.5 / 3615.3 / 134.0 / 1559 | **3757.5 / 3627.1 / 134.0 / 1561** |
| `EXPECTED_BUILD_OUT` full | 7162.0 / 6895.6 / 235.6 / 3103 | **7162.0 / 6918.1 / 235.6 / 3108** |
| `EXPECTED_PAPER_SET_SHA256` | `3e325c3a…125b8f949` | **`fd506c3a…0b0bbae6`** |

Only the CO2-only and damages columns moved. Every capacity lock is untouched.

---

## 7. Still open

- **Liquefaction range_high 0.36** — uncited literature upper bound; display only.
- **Pipeline range 0.037 / 0.133** — declared assumption; the compressor-drivers paper is paywalled.
- **Shipping 0.12 vs the IEA's 0.18** — now fully documented, still a live disagreement rather
  than a closed question.
- **Utilisation ramp 0.40 / 0.70** for the generic assets — still an assumption with no source,
  and the Phase 1 observed data now suggests the *shape* is wrong in a way that would apply to
  every asset, not just Phase 1.
- **`lifespan_sensitivity_low` 30**, **`cargo_tonnes_per_dwt` 0.85** — untouched.
- **23 Parameters rows no module reads** — housekeeping; `post_fid_to_completion` is now one fewer
  loose end among them.
