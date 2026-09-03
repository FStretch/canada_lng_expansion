# Update report — 3 September 2026

Everything that has changed since the 29 August task sequence
(`Outputs/CHANGE_REPORT_2026-08-29.md`, commit `2061036`).

Two things drove this round. A **sourcing audit** of every number in the model
(`Outputs/SOURCING_AUDIT.md`, 1 September) and a **deck reconciliation** against
an older presentation (`Outputs/DECK_RECONCILIATION.md`, 1 September). The audit's
findings were then applied to the workbooks by `tools/fix_audit_findings.py`, and
the code was changed to read from the workbooks what it had been hardcoding.

**The headline moved a long way, and the reason is a scope decision, not physics.**
Discovery LNG has gone back to cancelled. Everything else in this report is
sourcing hygiene.

`python build_results.py` passes 41 assertions and ends "No input file was
modified during the run."

---

## 1. Headline numbers

| quantity | 29 Aug lock | now | why |
|---|---|---|---|
| Lifetime CO2e | 9,298.1 Mt | **7,254.2 Mt** [6,659, 8,295] | Discovery removed (−2,043.9 Mt) |
| Lifetime CO2-only | 8,955.2 Mt | **6,987.7 Mt** [6,316, 7,853] | same |
| Peak | 298.2 Mt (2037) | **238.6 Mt** (2037) [231, 260] | same |
| CAN / BUNK / FOR | 18.1 / 3.2 / 78.7 | **18.1 / 3.2 / 78.8** | rounding on the smaller set |
| ECCC 2% damages | C$4,073 bn | **C$3,143 bn** [2,815, 3,622] | same |
| `life_average_annual_mt` | 258.5 Mt/yr | **207.4 Mt/yr** | same |
| Lifetime CH4 | 11,505 kt | **8,942 kt** | same |
| Export capacity | 100.1 mtpa, 10 projects | **80.1 mtpa, 9 projects** | same |
| Share of 1.5 °C budget (CO2-only) | 5.3% | **4.1%** | same |
| Assets in the calculation | 19 | **18** | same |

`committed` (1,869.5 Mt, C$749 bn) and `committed_plus_advanced` (3,805.7 Mt,
C$1,579 bn) are **unchanged**: Discovery was `early_proposed` and sat in neither.

Monte Carlo intervals widened slightly on their own account — see §3.

---

## 2. Discovery LNG returned to cancelled

The 29 August report flagged this as the one thing that had to be resolved before
publication. It is now resolved, in the direction the evidence pointed.

| | |
|---|---|
| Was | `status=proposed`, `calc_group=proposed`, `tier=early_proposed`, 20 mtpa, 2,043.9 MtCO2e (22.0% of the then-headline) |
| Now | `status=cancelled`, `calc_group=inactive`, `tier=inactive`. Capacity stays 20 mtpa in the register; the asset is out of every total |

Reasons recorded in `tier_reason` and Data Gaps:

- GEM records `cancelled (inferred 4 y)`. The register now matches rather than
  disagreeing.
- No regulatory filing, proponent statement or news report of current activity
  after GEM's September 2025 snapshot.
- Rockyview Resources was struck off the Alberta corporate registry in 2017.
- The third-party table that had prompted the `early_proposed` classification was
  **wrong about Grassy Point, Bear Head and Goldboro**, all confirmed cancelled.
- Discovery is not on NRCan's proposed-and-under-construction list.

This is a scope change. The physics of the remaining nine assets is untouched.

---

## 3. GWP20 scenario recomputed on the methane portion only

The 29 August report recorded a contradiction it did not resolve: the Scenarios
sheet and the README both said the GWP20 uplift applied to the methane portion
only, while the stored value `0.33` was `0.22 × 1.5` — the whole factor scaled.

Now fixed at source. `near_term_methane_gwp20` upstream is **0.33 → 0.428**:

```
0.22 × (1 − 0.30)                          = 0.154   non-methane inventory, unchanged
0.22 × 0.30 × 1.5 × (82.5 / 29.8)          = 0.274   methane portion, corrected then GWP20-weighted
                                             -----
                                             0.428
```

The value depends on `upstream_ch4_share = 0.30`, which is an assumption; the
Scenarios note says so. Pipeline methane is still not re-weighted, because no
pipeline methane share exists in the workbook.

**This widens the Monte Carlo upstream triangle**, whose high is the GWP20
scenario factor: `(0.22, 0.25, 0.33)` → `(0.22, 0.25, 0.428)`. That is why the
intervals moved by more than Discovery alone explains. Full-buildout MC median is
now 7,444.7 Mt [6,659, 8,295].

Scenario range on the new asset set:

| scenario | upstream | lifetime Mt |
|---|---|---|
| `inventory_as_reported` | 0.220 | 7,192.8 |
| `measurement_central` (paper) | 0.250 | **7,254.2** |
| `measurement_high` | 0.260 | 7,274.7 |
| `near_term_methane_gwp20` | 0.428 | 7,618.8 |
| `howarth_high` | 0.550 | 7,868.7 |

---

## 4. Sourcing: what the audit found and what was done

`Outputs/SOURCING_AUDIT.md` types every number as `citation` / `url` /
`proponent` / `derived` / `assumption` / `none` and gives a verdict. Its central
finding: a `derived` or `cited` label sitting on a homepage URL, a missing URL, or
addends with no source is **unsourced**, not sourced — and that pattern was not
confined to the oil comparator.

### Citations replaced with something a reviewer can actually open

| number | was | now |
|---|---|---|
| `steady_state_utilisation` 0.839 | `igu.org` homepage | IGU World LNG Report 2026 report page + PDF, with the note that it is nameplate utilisation |
| `tmx_total_system_bpd` 890,000 | `transmountain.com` homepage | Trans Mountain Corporation MD&A, 31 March 2025, direct PDF |
| Licence end years 2056–2066 | CER applications **index page** | licence filings GL-330 / GL-340 / GL-346 / GL-349 on Asset Sources |

### Values demoted to declared assumptions rather than dressed as citations

| number | was | now |
|---|---|---|
| `liquefaction_electric` 0.12 | typed `cited`, `pembina.org` homepage | typed **assumption**, `source_url` = "Not available". No Pembina document stating 0.12 was located; Pembina's *Squaring the Circle* (2023) uses 0.15, 0.059 and 0.04 — not 0.12 |
| Pipeline 0.10 (and 0.05 / 0.18) | "literature band, independently validated" | **assumed**. No ICF or Sphera document stating it was located. The Coastal GasLink check confirms throughput scaling, not the factor |
| Regasification 0.04 (and 0.02 / 0.06) | "RMI Oil Climate Index benchmarks" | **assumed**. No OCI+ table states 0.04 t/t |
| `canada_2030_overshoot_gap` 200 | typed `derived` | typed **assumption**. The arithmetic interval is 191–229; 200 is a round judgement |

None of these changed a value. They changed what the workbook claims about the
value, which is the point.

### Oil comparator components promoted to real parameters

`tmx_oil_lifecycle_per_barrel = 0.513` had been a `derived` label over three
addends that existed only inside a source string. They are now rows in their own
right, and the code sums them and asserts the sum matches:

| parameter | value | type |
|---|---|---|
| `tmx_oil_upstream_per_barrel` | 0.075 | cited |
| `tmx_oil_transport_per_barrel` | 0.008 | assumption |
| `tmx_oil_combustion_per_barrel` | 0.43 | cited |
| `tmx_expansion_bpd` | 590,000 | derived (890,000 less the pre-expansion ~300,000) |
| `days_per_year` | 365 | method constant |

Figure 7 now also states the **utilisation asymmetry**: oil runs at nameplate ×
365 × 40 years while LNG carries a ramp, a utilisation curve and an FID delay,
which understates LNG relative to oil by roughly 19%. The Alberta–BC bitumen bar
uses the TMX mixed-slate factor, too light for a dedicated dilbit line; it stays
labelled unvalidated.

---

## 5. Hardcoded values moved into the workbooks

The audit found the README sentence *"The model has no hardcoded emission
factors, capacities or parameters"* to be false. Rather than soften the sentence,
the values were moved.

**Monte Carlo** (`src/monte_carlo.py`) — `UPSTREAM_TRI`, `FID_TRI`, `LIFE_TRI` and
`LIQUEFACTION_FIXED` are gone. The triangles are now read from the workbooks:

| draw | source |
|---|---|
| upstream | Scenarios: `inventory_as_reported` / `measurement_central` / `near_term_methane_gwp20` |
| pipeline, shipping, regas, combustion | Emission Factors `range_low` / `central` / `range_high` |
| FID delay | Parameters `fid_delay_low` / `mid` / `high` |
| life | Parameters `lifespan_sensitivity_low` / `lifecycle_years_default` / `_high` |
| liquefaction | Emission Factors central, asserted equal to Parameters `liquefaction_gas_turbine` |

Each triangle is checked for ordering, so a workbook edit that inverts one fails
the run rather than sampling nonsense.

**Figure 10 comparators** (`src/lca_comparison.py`) — eight new Parameters rows
replace the module constants: `lca_howarth_gwp20_low/high`,
`lca_roman_white_w2r_p025/expected/p975`,
`lca_balcombe_lng_stages_low/high_g_per_mj_hhv`, `lca_hhv_mj_per_kg`.

**Placeholder sensitivity** (`src/placeholder_sensitivity.py`) — the 2033 and 2035
cases were a module tuple; they are now `placeholder_sensitivity_years` on the
Parameters sheet, validated to be after the central 2030 fill.

All nineteen new or newly-required parameters are in `REQUIRED_PARAMS`, so a
workbook missing one fails at load rather than silently falling back.

---

## 6. Assertions re-locked

| constant | old | new |
|---|---|---|
| `EXPECTED_LIFETIME_MT` | 9298.1 | **7254.2** |
| `EXPECTED_PEAK_MT` | 298.2 | **238.6** |
| `EXPECTED_PEAK_YEAR` | 2037 | 2037 (unchanged) |
| `EXPECTED_TERRITORIAL_SHARE_PCT` | 18.1 / 3.2 / 78.7 | **18.1 / 3.2 / 78.8** |
| `EXPECTED_EXPORT_TOTAL` | 100.1 | **80.1** |
| `EXPECTED_EXPORT_BY_CALC` proposed | 80.7 | **60.7** |
| `EXPECTED_EARLY_EXPORT` | 54.7 | **34.7** |
| `EXPECTED_ADVANCED_EXPORT` | 26.0 | 26.0 (unchanged) |
| `EXPECTED_BUILD_OUT` full | 9298.1 / 8955.2 / 298.2 / 4073 | **7254.2 / 6987.7 / 238.6 / 3143** |
| `EXPECTED_BUILD_OUT` committed, committed_plus_advanced | — | unchanged |
| `EXPECTED_PAPER_SET_SHA256` | `9e33c691…72a0946` | **`58236e9b…16012985c`** |
| headline sample size | 10 export assets | **9** |
| Monte Carlo liquefaction guard | `abs(liq − 0.29)` against a module constant | `abs(liq − Parameters liquefaction_gas_turbine)` |
| `lca_comparison` liquefaction guard | hardcoded 0.29 | Parameters `liquefaction_gas_turbine` |
| `oil_lifecycle_gt` | — | new: the three oil addends must sum to `tmx_oil_lifecycle_per_barrel` |
| MC triangles | — | new: each must be ordered low ≤ mode ≤ high |

---

## 7. Documentation brought back into line

This is the part I did in this session; everything above is yours.

- **README structure listing was stale.** Seven `src/` modules added since the
  original listing were missing (`monte_carlo`, `lca_comparison`,
  `placeholder_sensitivity`, `lifespan_sensitivity`, `feedgas_sensitivity`,
  `drive_sensitivity`, `si_table`), and the `Outputs/` block named none of the new
  deliverables. Both now match what is on disk.
- **README loss-and-damage paragraph contradicted itself.** The central-case
  sentence still said ECCC SC-CO2 was "applied per calendar year of emissions to
  the full GWP100 CO2e total" — the treatment retired in Task 3 — two paragraphs
  above the per-gas description. Rewritten, and the Burke share now carries
  `P_dam_FD` = 0.41 and the note that no 2020-pulse country table exists.
- **`Outputs/STALE_FIGURE_INVENTORY.md` had itself gone stale again.** It listed
  9,298.1 Mt / 298.2 Mt / C$4,073 bn as *current* after Discovery was removed —
  precisely the failure it was built to catch. `tools/stale_figure_inventory.py`
  now carries the new lock and nine more superseded values, and gained a
  per-file-per-value allowance so the README can keep its one deliberate
  before/after sentence without the whole file being exempted.
- **The inventory then found a real hit:** the Chains sheet still read "100.1
  mtpa (14.0 operating, 5.4 under construction, 80.7 proposed)". Fixed by
  `tools/update_chains_applies_to.py` to 80.1 / 14.0 / 5.4 / 60.7. Nothing else
  in the repository carried an old figure as current.
- **`SOURCING_AUDIT.md` and `DECK_RECONCILIATION.md` carry superseded-headline
  banners.** Both were written against the pre-Discovery lock and their headline
  reference figures are no longer current; their findings and reasoning stand.

Inventory now reports **0 live hits**.

---

## 8. Sensitivities on the new asset set

### Uniform 40-year life, no licence stop (SI)

| build-out | central Mt | uniform 40 yr Mt | central C$bn | uniform C$bn |
|---|---|---|---|---|
| committed | 1,869.5 | 2,279.8 | 749 | 955 |
| committed plus advanced | 3,805.7 | 4,936.9 | 1,579 | 2,157 |
| full | 7,254.2 | **8,465.8** | 3,143 | 3,763 |

Full buildout **+16.7%** (was +13.0% with Discovery in — Discovery ran on the
Parameters default with no licence stop, so removing it raises the share of the
total that the licence caps actually bite on). Committed-to-full ratio: central
**3.88**, uniform **3.71**. The licence-end cut is **1.2 GtCO2e**.

### Kino Aski feedgas (SI)

| case | headline Mt | Canada share |
|---|---|---|
| central | 7,254.2 | 18.1% |
| A, Western Canadian, pipeline ×3 (illustrative) | 7,340.6 | 19.0% |
| A, Western Canadian, pipeline ×5 (illustrative) | 7,426.9 | 20.0% |
| B, United States supply (upstream + pipeline tagged FOR) | 7,254.2 | **16.0%** |

Kino Aski is a larger share of a smaller total, so both cases bite harder than
before. Still no cited route distance for Western Canadian gas to the Quebec
north shore; the ×3 / ×5 band remains explicitly illustrative.

### Liquefaction drive type (SI)

| case | headline Mt | Δ Mt (all in CAN) |
|---|---|---|
| central, gas turbine 0.29 | 7,254.2 | — |
| Alternative Case, gas-fired power barges 0.156 | 7,200.5 | −53.8 |
| Base Case, grid 0.021 | 7,146.3 | −107.9 |

Unchanged in absolute terms: the sensitivity touches only Ksi Lisims and Cedar,
neither affected by the Discovery removal.

### Burke pulse year (SI)

Unchanged. Only the 1990-pulse country share exists in the replication package;
Canada 0.17% future window, `P_dam_FD` = 0.41, `P_dam_HD` = 0.33. The
`0.0015 < share < 0.0020` assertion is still not relaxed.

---

## 9. Still open

1. **The paper's headline has fallen 22% on a classification call.** Discovery's
   removal is well evidenced and the register now agrees with GEM, but anyone
   holding an older version of this work will see a very different number. The
   README says so in the "What this produces" section; any deck or draft needs
   the same sentence.
2. **Pipeline 0.10 and regasification 0.04 are now declared assumptions with no
   supporting document.** Together they are about 3.9% of the lifecycle total, so
   the headline does not hinge on them — but they are two of the six central
   factors and a reviewer will ask. The audit's impact ranking puts a 25% error
   on pipeline at ~65 Mt and on regas at ~26 Mt.
3. **Combustion range bounds 2.50 / 3.00 have no citation**, and they set the
   Monte Carlo interval on the largest stage (77.6% of the total). The central
   2.75 is IPCC; the bounds are not.
4. **The Conference Board denominator is still scaled linearly** from 56 mtpa to
   the proposed nameplate (now 60.7 mtpa) with no warrant from CBoC that GDP is
   linear in capacity. It is out of the paper, so this is a labelling matter
   only.
5. **Two 1 September audits now describe a superseded headline.** Bannered rather
   than rewritten, because their findings are what produced the current state.
6. **The Ksi Lisims assessment PDF was not read at page level** — it exceeds
   the fetch size limit. The 0.156 / 0.021 values and their pp. 847–848
   reference stand on the author's warrant (confirmed 3 September 2026).
