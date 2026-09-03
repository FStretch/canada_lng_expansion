# Oil comparator audit

<!-- lock-banner:start -->
> **Dated document.** Audit of the oil-pipeline comparator behind figure 7, 25 August 2026.
> Written against a model that still carried figure 7, `src/report_params.py` and the `tmx_*` and bitumen-pipeline parameters.
> **The analysis this document audits has been retired.** Figure 7, `src/report_params.py`, `oil_lifecycle_gt` and the oil comparator parameters were removed on 3 September 2026 (`Outputs/CHANGE_REPORT_2026-09-03b.md`, section 5) because of the findings below: the factor had no citation, no URL and no vintage, and the bitumen-pipeline bar was an unvalidated first pass. This file is kept as the working behind that decision, not as a description of anything now in the model.
> **Current lock:** **7,162.0 Mt** lifetime CO2e, **235.6 Mt** peak in 2037, **17.6 / 3.2 / 79.2** CAN / BUNK / FOR, **C$3,108 bn** ECCC damages, **80.1 mtpa** of export capacity.
> This banner is generated from the lock in `build_results.py` and asserted on every run; edit nothing between the markers.
<!-- lock-banner:end -->

**Date:** 25 August 2026  
**Scope:** Read-only. No files were modified except this note.  
**Question that triggered this:** does the Trans Mountain figure include scope 3 (downstream combustion), and could the proposed Alberta–BC bitumen pipeline be added on the same basis?

**Short answers, before the working:**

1. Downstream combustion **is included**. It is 0.43 of the 0.513 tCO₂e/bbl lumped factor — about **84%** of the oil total.
2. There is **no** `config/oil_pipeline_factors.yaml`. The oil chain is not a staged factor file. It is one workbook parameter plus a one-line formula.
3. The three numbers that make up 0.513 have **no citation, no URL, and no vintage**. The workbook records the source URL as `"Not available"`.
4. The Alberta–BC bitumen line is **already in figure 7 and slide table 15**, flagged unvalidated, using the same Trans Mountain factor. It is not waiting to be added; it is waiting to be sourced.

---

## 1. The oil emission factors

### Where they live

There is no YAML, no `config/` directory, and no oil row on the **Emission Factors** sheet. That sheet is LNG-only (`tCO2e per t LNG`, six stages).

Oil lives on **`Inputs/Canada_LNG_Data_Inputs.xlsx` → Parameters**, as two rows, plus three component numbers that exist only as text inside one `source` cell.

The project’s own typing rule (Excel README) is: *anything typed `cited` or `derived` carries a real URL to a specific document, never an organisation homepage.* Both oil rows fail that rule.

### The two Parameters rows (full)

| Field | `tmx_oil_lifecycle_per_barrel` | `tmx_total_system_bpd` |
|---|---|---|
| value | **0.513** | **890,000** |
| unit | tCO2e/bbl | barrels per day |
| type | `derived` | `cited` |
| source | `Sum of upstream 0.075, transport 0.008 and combustion 0.43` | `Trans Mountain system capacity after the May 2024 expansion` |
| source_url | **`Not available`** | `https://www.transmountain.com/` (organisation homepage) |
| vintage | *(blank)* | 2024 |
| notes | *(blank)* | *(blank)* |

`tmx_oil_lifecycle_per_barrel` is not in `REQUIRED_PARAMS`. The main model never reads it. Figure 7 and `oil_lifecycle_gt()` do.

### The three component factors (the ones that actually matter)

These are **not stored as parameters**. They appear only in the source string of `tmx_oil_lifecycle_per_barrel`. There is no per-stage oil table, no low/high range, no GWP note, no slate note, and no “TODO”.

| Stage named in the source string | Value | Unit | Source recorded | What that source actually is |
|---|---|---|---|---|
| upstream | **0.075** | tCO₂e/bbl (implied) | nothing | Not a citation. Not a URL. Not a TODO. The number is mentioned once, as an addend. |
| transport | **0.008** | tCO₂e/bbl (implied) | nothing | Same. |
| combustion | **0.43** | tCO₂e/bbl (implied) | nothing | Same. |
| **sum (the parameter)** | **0.513** | tCO₂e/bbl | “Sum of …” | Arithmetic identity only. `0.075 + 0.008 + 0.43 = 0.513`. |

Check: `0.075 + 0.008 + 0.43 = 0.513` exactly. The “derivation” is addition of three unsourced numbers.

**Stages not named at all:** refining, product distribution, tanker shipping from Westridge, diluent production, oil-sands upgrading. They are not zeroed with a comment. They are absent.

### Placeholder, rounded estimate, or carried over from LNG?

- **Not carried over from the LNG config.** LNG factors are `tCO2e per t LNG` on Emission Factors (`upstream` 0.25, `pipeline` 0.10, `combustion` 2.75, …). Different units, different sheet, different code path. Nothing in `oil_lifecycle_gt` reads the LNG factor table.
- **Not labelled a placeholder or TODO.** Type is `derived`.
- **They read as rounded estimates.** 0.43 is a commonly published round figure for crude-oil combustion; 0.075 and 0.008 look like rounded kg/bbl figures (75 and 8 kgCO₂e/bbl). The workbook does not say so, and it does not cite IPCC, EPA, GHGenius, PRELIM, the Oil Climate Index, or anyone else.
- **`source_url: Not available`** is this repository’s standard phrase for “entered with nothing external behind it.”

**The single most important finding:** the oil intensity that produces 6.67 Gt is unsourced. The capacity row is weakly sourced (homepage, not a document). The component stages have no sources at all.

### Other oil-related inputs (not factors, but used)

| Name | Where | Value | Source quality |
|---|---|---|---|
| `lifecycle_years_default` | Parameters | 40 years | Typed `assumption`. Source text is about CER LNG export licences, not oil pipelines. Oil reuses it anyway. |
| `tmx_expansion_bpd` | `src/report_params.py` only (not on the Parameters sheet) | 590,000 bpd | “commonly cited as 590,000 bpd above the pre-expansion system.” No URL. |
| `alberta_bc_bitumen_pipeline_bpd` | `src/report_params.py` only | 1,000,000 bpd | MPO submission 2 July 2026, Bruderheim–Delta, floor of 1 Mbpd. Flagged `unvalidated`. |
| `alberta_bc_bitumen_pipeline_label` | `src/report_params.py` only | label string | Report label. Unvalidated. |

Data Gaps sheet: **no oil/TMX rows**. Derived Fields sheet: **no oil fields**.

---

## 2. How the Trans Mountain figure is calculated

Oil is not an asset in the register and not a chain in `model.py`. It is a figure overlay.

```267:271:src/trajectories.py
def oil_lifecycle_gt(bpd: float, params: dict) -> float:
    """Same method as TMX: bpd × tCO2e/bbl × 365 × lifecycle_years / 1e9."""
    per_bbl = float(get_param(params, "tmx_oil_lifecycle_per_barrel"))
    life = float(get_param(params, "lifecycle_years_default"))
    return float(bpd) * per_bbl * 365.0 * life / 1e9
```

Figure 7 (`src/figures_report.py`) calls this once per bar. Slide table 15 does the same.

### Capacity

**890,000 barrels per day**, from Parameters `tmx_total_system_bpd`.

- **Hardcoded in the workbook, not reconciled in code.** Python does not read GEM. There is no Oil/NGL Pipelines tracker file, no GEM join, no check against 300,000 + 590,000. The number is used as given.
- Source text: “Trans Mountain system capacity after the May 2024 expansion.”
- URL: `https://www.transmountain.com/` — operator homepage, not a capacity table or filing.
- The public post-expansion figure *is* 890,000 bpd (pre-expansion 300,000 plus a 590,000 increment). That arithmetic is consistent with what operators and governments publish. **It is not in this repository as a GEM reconciliation.** The 590,000 increment used for the “expansion only” bar lives in `report_params.py` as “commonly cited,” with no URL.

### Stages included

Named in the factor’s source string only:

1. **Upstream production** — 0.075 tCO₂e/bbl
2. **Transport** — 0.008 tCO₂e/bbl (pipeline-scale; not broken into TMX mainline vs. feeder vs. marine)
3. **End-use combustion** — 0.43 tCO₂e/bbl

**Not included:** refining, product distribution, crude tanker shipping, upgrading, diluent, construction.

The code does not compute stages. It multiplies the sum.

### Is downstream combustion by the end user included?

**Yes.** Directly.

Combustion is a named addend (0.43 of 0.513). On the Trans Mountain total that is **5.59 Gt of 6.67 Gt**, about **84%**. That is scope 3 / territorial-foreign in LNG language. Oil has no scope or territory columns; the combustion term is still in the number.

If someone wanted a Canada-inventory-only oil figure, this model cannot produce one without splitting the lumped factor.

### Operating life, utilisation, ramp, FID delay

| Treatment | Oil | LNG (for contrast) |
|---|---|---|
| Life | 40 years (`lifecycle_years_default`), always | Per asset: CER licence, else proponent life, else 40 |
| Utilisation | **None. Nameplate × 365 days.** | Year 1 = 40%, year 2 = 70%, then 83.9% (IGU 2025) |
| Ramp | None | 2 years |
| FID delay | **None** | 5 years *inside* the lifespan if `fid_confirmed` is false |
| Calendar start | None. No trajectory. | `first_export_year`; blank → 2030 for figures only |

Oil runs at **100% of nameplate from year one, every day, for 40 years**. A proposed LNG project with no FID gets five zero years and then a ramp, so its 40-year effective utilisation is about **72%** of nameplate (0.4 + 0.7 + 33 × 0.839 = 28.787 operating-year equivalents / 40). Operating LNG with FID is about **82.5%**.

### GWP basis

**Not stated for oil, and not applied in code.** `oil_lifecycle_gt` never reads `gwp100_ch4` (29.8) or `gwp20_ch4` (82.5). The 0.513 is already labelled tCO₂e. Whatever GWP sits inside the 0.075 upstream term is unknown. LNG methane is explicit AR6 GWP100, with a GWP20 scenario.

### Working: 6.67 Gt from stated inputs

```
capacity        = 890,000 bpd          (tmx_total_system_bpd)
factor          = 0.513 tCO₂e/bbl      (tmx_oil_lifecycle_per_barrel)
days            = 365
years           = 40                   (lifecycle_years_default)
utilisation     = 1.0                  (implicit; not in the formula)

annual  = 890,000 × 0.513 × 365
        = 166,648,050 tCO₂e/yr
        = 166.65 MtCO₂e/yr

lifetime = 166,648,050 × 40
         = 6,665,922,000 tCO₂e
         = 6.665922 GtCO₂e
```

Published figure CSV: **6.665922 Gt**, labelled “TMX full system (890,000 bpd)”. Rounded in slide tables to **6.67 Gt**.

By named stage (same formula, split by the source-string addends):

| Stage | tCO₂e/bbl | Lifetime Gt | Share |
|---|---|---|---|
| upstream | 0.075 | 0.975 | 14.6% |
| transport | 0.008 | 0.104 | 1.6% |
| combustion | 0.43 | 5.587 | 83.8% |
| **total** | **0.513** | **6.666** | **100%** |

Expansion-only bar, same method: `590,000 × 0.513 × 365 × 40 / 1e9 = 4.418982 Gt`.

---

## 3. How comparable is it to the LNG chain, really?

LNG export chain: upstream → pipeline → liquefaction → shipping → regasification → combustion.  
Oil “chain”: a lumped well-to-combustion factor with three named pieces and no refining.

“Same method” here means **same *shape* of headline**: capacity × intensity × 365 × 40 years, expressed as a lifecycle Gt, plotted next to the LNG 40-year model sum. It does **not** mean same stages, same utilisation, same GWP handling, or same sourcing standard.

| Dimension | LNG | Oil | Same? |
|---|---|---|---|
| Boundary intent | Full chain including end-use combustion | Named pieces include end-use combustion | **Same intent** for “include scope 3 combustion” |
| Horizon | ~40 years (licence / stated / default) | Always 40 | **Same default**, but LNG can differ per asset |
| GWP | AR6 fossil methane 29.8 / 82.5, applied | Pre-baked CO₂e, undocumented | **No** |
| Utilisation | Ramp + 83.9% steady; FID delay for unconfirmed | Nameplate 365 d/yr | **No** |
| Stage structure | Six named stages, each sourced | Three unsourced addends, then one multiply | **No** |
| Slate / basin | BC gas, measurement-corrected methane | One number for “TMX oil” | n/a, but not analogous |
| Territorial / scope split | Yes | No | **No** |
| Construction | Excluded both sides | Excluded | Same omission |
| Engine | `model.py` over the asset register | Figure helper only | **No** |

### Asymmetries that pull the comparison

**Unfair against LNG (oil looks larger than a like-for-like util treatment would):**

- Oil at 100% nameplate; LNG at ~72% (proposed, no FID) to ~82.5% (operating). If TMX were run at the LNG steady-state 83.9%, it would be **5.59 Gt**, not 6.67 Gt. That is a **1.07 Gt** swing on TMX alone — not a rounding issue.
- Proposed LNG loses five years to FID delay inside the 40-year window. Oil has no analogue, including for the unbuilt bitumen line.

**Unfair against oil (oil looks smaller than a full well-to-wheel would):**

- **Refining is missing.** For a mixed Canadian export slate that is a material omission, not a rounding error.
- **Marine shipping of crude** from Westridge is almost certainly not in the 0.008 transport term (that term is ~8 kg/bbl, pipeline-scale). LNG *does* count shipping.
- Upstream 0.075 tCO₂e/bbl is on the low side for a TMX slate that includes diluted bitumen / oil sands. If that number is conventional-weighted, TMX itself is understated.

**Unfair against a bitumen line, if the TMX factor is reused:**

- Dedicated diluted bitumen is more extraction-intensive than a mixed TMX slate. Same factor ⇒ understatement. See §4.

**Ambiguous:**

- GWP inside oil upstream methane: unknown, so it cannot be aligned with LNG’s AR6 GWP100 / GWP20 split.
- “Transport” for oil vs “pipeline + shipping + regas” for LNG are not matched stages; they should not be compared stage-by-stage.

Combustion share is similar in spirit (LNG combustion 2.75 / 3.55 ≈ 77% of the export intensity; oil combustion 84% of 0.513). That is the honest overlap: **both headlines are lifecycle-including-burn**, not Canada-inventory-only.

---

## 4. What it would take to add a third project

**Do not treat this as unbuilt.** It is already in the current outputs.

| Output | Alberta–BC bitumen row |
|---|---|
| `Outputs/figure_data/fig07_oil_infrastructure_comparison.csv` | `7.4898` Gt, `unvalidated=True` |
| Figure 7 | Orange hatched bar, “Proposed Alberta–BC bitumen pipeline (≥1 Mbpd)” |
| `Outputs/SLIDE_TABLES.xlsx` sheet `15_Oil_comparison` | Same figure, two decimals |
| `src/report_params.py` | `alberta_bc_bitumen_pipeline_bpd = 1_000_000`, MPO 2 July 2026, Bruderheim–Delta, ~1,200 km, 2032–2034, **UNVALIDATED** |

It uses **the Trans Mountain factor unchanged**.

### Is capacity a parameter, or is TMX hardcoded?

**Capacity is a function argument.** `oil_lifecycle_gt(bpd, params)` will compute any bpd. A second project is “pass another number.”

What is *not* a per-project config:

- The intensity is always `tmx_oil_lifecycle_per_barrel`. The name is TMX-specific; the code does not allow a second factor.
- Life is always `lifecycle_years_default` (40). No per-project oil life.
- No utilisation, ramp, FID, or start year.
- TMX full-system capacity is a workbook parameter (`tmx_total_system_bpd`). The expansion increment and the bitumen capacity are Python defaults in `report_params.py`, not Parameters-sheet rows.

To do a second project *properly* (not another `bpd` through the TMX scalar) you would need at least: a named capacity with a real citation; a **separate** well-to-combustion (or staged) factor for diluted bitumen; a life/util/FID rule you are willing to defend next to LNG; and Data Gaps / source_url filled in. That is a config-and-source job, not a one-line addition — except that the one-line addition has already been made.

### Would diluted bitumen need different upstream factors?

**Yes.** Oil-sands extraction (mining or SAGD) plus diluent is substantially more intensive than conventional light/medium crude. TMX carries a mixed slate. A dedicated Bruderheim–Delta bitumen line does not.

**The current config cannot express that difference.** One scalar, used for every oil bar. Applying it to 1 Mbpd of bitumen **understates** that project. How much is unknown, because the 0.075 itself is unsourced — so you cannot even say “TMX was conventional-weighted.” You can only say the same number is being reused.

Refining of heavy/sour/bitumen-derived crude is also more intensive than refining light crude. Refining is already missing for TMX; missing it for bitumen is a larger hole.

### Unvalidated first pass: existing factors × 1,000,000 bpd × 40 years

```
1,000,000 × 0.513 × 365 × 40 / 1e9 = 7.4898 GtCO₂e
```

**7.49 GtCO₂e.** Label: **unvalidated first pass — TMX mixed-slate factor applied to a dedicated bitumen line at a 1 Mbpd floor, nameplate, 365 d, 40 years, no util, no FID delay, no bitumen-specific upstream, no refining.** This is the number already in figure 7.

It is a capacity scaling, not an estimate of that project.

---

## 5. Judgement

**Not solid enough to extend, and not solid enough to publish as a sourced comparator.** The arithmetic is fine. The factors are not.

What works:

- The 6.67 Gt identity is exact and reproducible from 890,000 × 0.513 × 365 × 40.
- Downstream combustion **is** in the number. A reviewer who asks “does TMX include scope 3?” can be told yes, as a named 0.43 tCO₂e/bbl term, ~84% of the total.
- Capacity 890,000 bpd matches the public post-expansion nameplate, even though GEM reconciliation is not in the code.

What does not:

1. **The intensity is unsourced.** Three component factors with no citation, no URL, no vintage, no slate, no GWP. `source_url: Not available`. That would not pass this repo’s rule for a cited or derived LNG factor.
2. **Utilisation asymmetry.** Nameplate oil vs ramped, delayed, 83.9%-util LNG understates LNG relative to oil. State it or fix it before any chart goes in a slide.
3. **Missing refining** (and likely missing tanker shipping) understates oil. Opposite direction to (2); they do not cancel in a controlled way.
4. **Bitumen is already on the figure** with the TMX factor. That is the wrong basis, and it is already labelled only as “unvalidated,” not as “wrong slate.”
5. **No GEM reconciliation** exists in code. If a reviewer was told that, it is not what the repository does.
6. Oil is a figure overlay, not a chain. It has none of the register / source / gap discipline the LNG side uses.

**Before publishing TMX:** source 0.075 / 0.008 / 0.43 (or replace them) with documents, not homepages; say whether refining is in or out; say GWP; decide nameplate vs utilisation; put that in Parameters with real `source_url`s; add a Data Gaps row if any of it remains weak.

**Before publishing Alberta–BC:** do all of the above, **plus** a bitumen-specific upstream (and likely refining) factor. Do not ship 7.49 Gt as anything other than “same TMX factor × 1 Mbpd, unvalidated, likely low.”

I would rather this note say the factors are unsourced than have that discovered after the figure is out. They are unsourced.
