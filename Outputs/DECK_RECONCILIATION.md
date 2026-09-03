# Deck reconciliation — present state of the register and model

> **Superseded headline, updated 3 September 2026.** This document was written against the
> pre-Discovery lock: **9,298.1 Mt** lifetime, **298.2 Mt** peak, **C$4,073 bn**
> damages, 100.1 mtpa across ten projects. Its own findings were then applied
> (`tools/fix_audit_findings.py`): Discovery LNG went back to cancelled and the
> GWP20 scenario was recomputed on the methane portion only. Current locked
> values are **7,254.2 Mt** lifetime, **238.6 Mt** peak in 2037, **C$3,143 bn**
> damages, **80.1 mtpa across nine projects**. The findings and reasoning below
> stand; the headline figures they are measured against have moved. See
> `Outputs/CHANGE_REPORT_2026-09-03.md`.

**Date:** 1 September 2026  
**Scope:** Read-only. This file is a dump of what the model now holds. **The presentation was not edited.** There is no `.pptx` in the repository. “Last export” here means the last generated `Outputs/SLIDE_TABLES.xlsx` / `Outputs/RESULTS_SUMMARY.md` (run 29 August 2026, paper set locked after Task 4 shipping scale). Older figures that are recoverable from git are noted.

Headline lock: **9,298.1 MtCO2e** lifetime, **298.2 Mt** peak in 2037, CAN/BUNK/FOR **18.1 / 3.2 / 78.7**.

---

## Three you already suspect

### 1. LNG Canada Phase 1 at 41.2 MtCO2e/yr

**No. That figure is stale.**

Current SLIDE_TABLES `07_By_project` / RESULTS_SUMMARY:

| | now |
|---|---|
| Capacity | 14.0 mtpa |
| Drive | gas_turbine |
| First export | 2025 |
| Licence end | **2056** (hard stop; 32 emitting years, 8 years cut from the 40-year term) |
| Life-average annual | **40.9 MtCO2e/yr** |
| Lifetime | **1,309.6 Mt** |

Licence-end caps **are** applied. They cut **years**, not the intensity. 1,309.6 / 32 = 40.9. If someone still divides by 40 they get 32.7, which is worse, not 41.2.

41.2 does **not** appear anywhere in this repository (grep). Closest reconstruction: `14 × 3.55 × 0.829 ≈ 41.2` (nameplate × central intensity × something near IGU 83.9% without the Phase 1 0.85 override and without ramp averaging). Current Phase 1 steady-state util is **0.85**, which at nameplate would be `14 × 3.55 × 0.85 = 42.2`. The published 40.9 is the life-average over the 32-year licensed window including ramp years.

**Unchanged since last SLIDE_TABLES export** (Phase 1 1,309.6 / 40.9 was already in the 29 Aug baseline, before Task 4). **Changed relative to a deck that still says 41.2.**

### 2. Electric-drive liquefaction 0.12, Pembina Institute

**The headline model still uses 0.29 gas turbine for every terminal. It does not use 0.021 or 0.156.**

| figure | what uses it |
|---|---|
| **0.29** | Central liquefaction, every asset, paper set, Monte Carlo (held fixed), figure 8 “gas turbine” bar |
| **0.12** | Emission Factors `range_low`; Parameters `liquefaction_electric`; **figure 8 appendix only** (claimed-electric and all-electric). Still labelled Pembina. URL is pembina.org. **Yes, 0.12 is still referenced.** |
| **0.156** | Parameters `liquefaction_electric_drive_gas_generation`. SI drive sensitivity, Ksi Lisims (sourced) + Cedar (assumption). BC EAO Ksi Lisims AR pp. 847–848, Alternative Case (gas barges). Facility total including marine, not like-for-like with 0.29. |
| **0.021** | Parameters `liquefaction_electric_drive_grid`. Same document, Base Case, grid. Same SI, same two assets, same boundary caveat. |

Figure 8 still moves Canada territorial from 46.7 → 40.8 (claimed electric at 0.12) → 34.3 (all electric at 0.12). The EAO pair moves the **lifetime** total by −54 / −108 Mt if applied to Ksi Lisims and Cedar only (`sens_liquefaction_drive.csv`).

**Changed since a deck that only knew Pembina 0.12:** EAO 0.021 / 0.156 were added 29 Aug 2026 (Task 8). They did **not** replace 0.12. **Unchanged since last SLIDE_TABLES export** for the headline 0.29 and the figure-8 0.12.

### 3. Proposed-assets footnote “emissions figures pending rerun”

**The rerun has happened.** Proposed export is **80.7 mtpa**, life-average **201.8 MtCO2e/yr**, lifetime **7,428.6 Mt**. Per-asset lifetimes are in SLIDE_TABLES `07_By_project` and `Outputs/si_table_assets.csv`.

| project | mtpa | lifetime Mt |
|---|---|---|
| Discovery | 20.0 | 2,043.9 |
| Kino Aski (Baie-Comeau) | 15.0 | 1,521.7 |
| Kanata | 12.0 | 1,226.3 |
| Ksi Lisims | 12.0 | 1,047.6 |
| LNG Canada Phase 2 | 14.0 | 888.6 |
| Fermeuse | 5.0 | 504.9 |
| Summit Lake | 2.7 | 195.5 |
| **Proposed total** | **80.7** | **7,428.6** |

If the footnote is still on the slide, it is leftover from before the 29 Aug run (and before Kino 10→15). **Changed. Delete the footnote; the figures exist.**

---

## Committed assets

Operating + under construction, export chain (the paper’s “committed” = 3 assets). Lifetime is the calendar panel, licence-end applied.

| name | capacity mtpa | calc_group | liquefaction drive | first export | licence end | lifetime MtCO2e |
|---|---:|---|---|---:|---:|---:|
| LNG Canada Terminal (Phase 1) | 14.0 | operating | gas_turbine | 2025 | 2056 | 1,309.6 |
| Cedar FLNG Terminal | 3.3 | under_construction | gas_turbine | 2028 | 2066 | 376.6 |
| Woodfibre LNG Terminal | 2.1 | under_construction | gas_turbine | 2028 | 2057 | 183.3 |
| **Committed total** | **19.4** | | | | | **1,869.5** |

Drive notes (not used in the central case): Cedar and Woodfibre were previously `electric_committed`; interconnection works are under construction. Headline still applies 0.29.

**Unchanged since last export** for these lifetimes (already in BASELINE_2026-08-29). Licence-end caps were already on.

---

## Proposed assets

| name | capacity mtpa | tier | location | first export | placeholder? | lifetime MtCO2e |
|---|---:|---|---|---:|---|---:|
| Discovery LNG Terminal | 20.0 | early_proposed | Campbell River, BC | 2030 | **yes** | 2,043.9 |
| Kino Aski LNG (formerly Marinvest Energy, Baie-Comeau) | **15.0** | early_proposed | Baie-Comeau, Côte-Nord | 2030 | **yes** | 1,521.7 |
| Kanata LNG | 12.0 | early_proposed | Prince Rupert, BC | 2030 | **yes** | 1,226.3 |
| Ksi Lisims FLNG Terminal | 12.0 | advanced_proposed | Gingolx | 2029 | no | 1,047.6 |
| LNG Canada Terminal (Phase 2) | 14.0 | advanced_proposed | Kitimat | 2030 | no | 888.6 |
| Fermeuse Energy FLNG | 5.0 | early_proposed | Fermeuse, NL | 2030 | **yes** | 504.9 |
| Summit Lake PG LNG | 2.7 | early_proposed | ~30 km N of Prince George | 2030 | **yes** | 195.5 |
| **Proposed total** | **80.7** | | | | | **7,428.6** |

Advanced 26.0 mtpa / early 54.7 mtpa.

**Baie-Comeau is now recorded as Kino Aski LNG** (`project_id` remains `marinvest_baie_comeau`). Capacity **15.0 mtpa** (proponent newswire 17 Aug 2026). Old capacity **10 mtpa** is recoverable from git commit `7cc179b` (“Update Kino Aski to 15 mtpa…”).

Lifetime vs 29 Aug **baseline** (before route-scaled shipping): Kino Aski 1,532.9 → **1,521.7**; Fermeuse 511.0 → **504.9**. Other proposed lifetimes were already at the current figures in that baseline.

**Changed, see above** (name, 15 mtpa, Atlantic shipping cut on Kino/Fermeuse).

---

## Other chains

Headline filter is export only. These remain in the register.

| name | chain | capacity mtpa | status / calc_group | lifetime Mt (all-assets panel) |
|---|---|---|---|---:|
| Tilbury Island LNG (Phase 1a) | bunkering | 0.25 | operating | 23.5 |
| Tilbury Island LNG (Phase 1b) | bunkering | 0.65 | proposed | 63.4 |
| Tilbury Island LNG (Phase 2) | bunkering | 2.50 | proposed (start blank → 2030) | 137.3 |
| Saint John LNG Terminal | import | 7.50 | operating (`tier=watch`) | 12.6 |
| Mt. Hayes LNG | domestic | 0.06 | operating | 4.5 |
| Tamaska LNG (Fort Nelson) | domestic | 0.02 | operating | 1.7 |
| Tilbury original | domestic | 0.03 | operating, **legacy** | 0.0 |
| Energir Montreal | domestic | 0.21 | operating, **legacy** | 0.0 |
| Port of Hamilton | import | **missing** | operating | excluded, not zeroed |
| Tilbury Marine Jetty | none | — | proposed | excluded, not zeroed |

Bunkering 3 assets, 3.4 mtpa, 224.2 Mt. Domestic 4 assets, 0.3 mtpa, 6.1 Mt. Import 1 counted asset, 7.5 mtpa, 12.6 Mt. Combined excluded **242.9 Mt**.

**Unchanged since last export.**

---

## Cancelled and shelved

| | now |
|---|---|
| Count | **36** (35 cancelled + 1 shelved) |
| Total mtpa (non-missing) | **305.7** |
| Goldboro T1/T2, Nisga'a, Saint John second proposal | capacity blank — not in the 305.7 |

**Discovery has not moved out of the live register.** It is `early_proposed` / `proposed`, 20 mtpa, 2,043.9 Mt (22% of the paper lifetime). GEM verbatim: `cancelled (inferred 4 y)` (2026-08-29). The disagreement is in RESULTS_SUMMARY SI and Data Gaps. Classification was left as a scope decision.

**Year and reason:** the Asset Register has **no cancellation-year column and no reason column**. Asset Sources for these rows point at GEM GGIT LNG Terminals (Sep 2025) Status / CapacityinMtpa. A deck that lists a year and a reason is not quoting this register; those fields are not there to export.

Twelve largest by capacity (status as recorded):

| rank | name | mtpa | status | first export year in register |
|---|---|---:|---|---|
| 1 | Orca FLNG | 30 | cancelled | blank |
| 2 | WCC LNG | 30 | cancelled | blank |
| 3 | Kwispaa LNG | 24 | cancelled | blank |
| 4 | Prince Rupert LNG | 21 | cancelled | blank |
| 5 | Kitsault LNG | 20 | cancelled | blank |
| 6 | Kitimat LNG | 18 | cancelled | blank |
| 7 | Pacific NorthWest LNG | 18 | cancelled | blank |
| 8 | Atlantic Coast LNG | 16 | cancelled | 2024 (planned; never ran) |
| 9 | Grassy Point Phase 1 | 15 | cancelled | blank |
| 10–11 | Aurora Phase 1 / Phase 2 | 12 + 12 | cancelled | blank |
| 12 | Bear Head LNG | 12 | cancelled | blank |

(Aurora is two units; Energie Saguenay at 11 sits just below Bear Head.)

Placentia Bay FLNG is the one **shelved** row (4.0 mtpa).

**Unchanged since last export** as a count/total, unless a slide still treated Discovery as cancelled. **Changed relative to that slide:** Discovery is in proposed, not in this group.

---

## Feedgas pipelines

Supporting Infrastructure sheet (GEM GGIT Gas Pipelines Nov 2025). Demand uses `lng_to_gas_bcm_per_mtpa = 1.38`.

| name | status | capacity bcm/y | serves | headroom bcm/y | ownership as recorded |
|---|---|---:|---|---:|---|
| Coastal GasLink | operating | 21.46 | LNG Canada; Cedar | **−2.41 SHORTFALL** | TC Energy 35%; AIMCo 32.5%; KKR 32.5% |
| Coastal GasLink expansion | proposed | 21.46 | LNG Canada (Phase 2) | +2.14 sufficient | same as CGL |
| Prince Rupert Gas Transmission | construction | 20.44 | Ksi Lisims | +3.88 sufficient | TC Energy 100% via NW Infrastructure LP |
| Cedar LNG Pipeline | construction | 4.09 | 8 km connector; demand counted on CGL | 4.09 “not allocated to a live terminal” | Pembina 50%; remainder unattributed in GEM |
| FortisBC Eagle Mountain | construction | 2.33 | Woodfibre | **−0.57 SHORTFALL** | Fortis Inc 100% |
| Pacific Trail | shelved | 13.90 | none (was Kitimat LNG) | n/a | Enbridge 100% |

**Ownership tracker:** there is no separate ownership-tracker file in this repo. Owners are GEM attributions on this sheet. **No prior snapshot is stored**, so an ownership change since “last read” cannot be flagged from git beyond “whatever GEM said when the sheet was filled.” Last register commit that touched supporting columns in this sequence: Task 7 (`d432859`, feedgas_basin on terminals) and Task 9 (GEM status columns). Pipeline owner strings themselves date from the initial register.

Kino Aski, Discovery, Kanata: `feedgas_basin` = not available.

**Unchanged since last export** (no ownership delta recoverable).

---

## Emission factors

Current Emission Factors sheet (headline uses **central**; MC uses the triangles except liquefaction).

| stage | central | low | high |
|---|---:|---:|---:|
| upstream_production | 0.25 | 0.22 | 0.55 |
| pipeline_transport | 0.10 | 0.05 | 0.18 |
| liquefaction | **0.29** | **0.12** | 0.36 |
| shipping | 0.12 | 0.05 | 0.31 |
| regasification | 0.04 | 0.02 | 0.06 |
| combustion | 2.75 | 2.50 | 3.00 |

**Drive values**

| parameter | value | in headline? |
|---|---:|---|
| `liquefaction_gas_turbine` | 0.29 | **yes** (every terminal) |
| `liquefaction_electric` | 0.12 | figure 8 only; still the Pembina number |
| `liquefaction_electric_drive_gas_generation` | 0.156 | SI only |
| `liquefaction_electric_drive_grid` | 0.021 | SI only |
| `bc_lng_emission_intensity_benchmark` | 0.16 | not used as a factor |

The electric figure in the **central/appendix pair** is still Pembina 0.12. It has **not** been replaced by the BC EAO grid or barge figures. Those sit beside it as a separate sensitivity with a boundary caveat (facility total vs liquefaction stage).

Shipping 0.12 is the BC–NE Asia basis, then scaled by `route_distance_nm / 3800` (Kino 0.784, Fermeuse 0.650, rest 1.0).

**Changed since a deck that omitted EAO 0.021/0.156. Unchanged since last SLIDE_TABLES export** for 0.29 / 0.12 centrals.

---

## Throughput and timing

| parameter | current value | note |
|---|---|---|
| Utilisation curve | year 1 **0.40**, year 2 **0.70**, then **0.839** | 0.40/0.70 assumed; 0.839 IGU 2025 |
| LNG Canada Phase 1 ramp | **0.25 / 0.60 / 0.85** | overrides the generic curve for that asset only |
| Saint John utilisation | **0.025** flat | import only; out of headline |
| FID delay | **5** years (tested 3–7 in MC) | inside the life window, not added after it |
| Default lifespan | **40** years | then cut at `authorised_export_end_year` if present; Summit Lake 30 from proponent |
| GWP100 / GWP20 | **29.8 / 82.5** | IPCC AR6 fossil methane |
| Placeholder start if missing | **2030** | 5 of 10 headline assets; 5,492.4 Mt (59.1%) sit on this fill |

**Unchanged since last export.**

---

## Recoverable old values (git / BASELINE)

| item | old (recoverable) | now |
|---|---|---|
| Full lifetime | 9,558.2 (all assets) → 9,315.3 (export, flat shipping) | **9,298.1** (export, route-scaled shipping) |
| Peak | 309.1 → 298.7 | **298.2** in 2037 |
| Kino Aski capacity | 10 mtpa (pre-`7cc179b`) | **15 mtpa** |
| Kino Aski lifetime | 1,532.9 (29 Aug baseline) | **1,521.7** |
| Fermeuse lifetime | 511.0 (baseline) | **504.9** |
| README CO2-only lifetime | still says **8,967.2** in one paragraph | paper set **8,955.2** (README is stale; not the deck) |
| ECCC 2% damages | C$4,164 bn (whole CO2e at SC-CO2) | **C$4,073 bn** (per-gas) |

Committed lifetimes 1,309.6 / 376.6 / 183.3 did not move in the 29 Aug task sequence.

---

## Block-by-block stamp

| block | stamp |
|---|---|
| Three suspicions | **changed relative to the deck** (41.2 → 40.9; 0.12 still used in fig 8, EAO is SI-only; proposed rerun **done**) |
| Committed assets | **unchanged since last export** |
| Proposed assets | **changed, see above** (Kino Aski name and 15 mtpa; Atlantic shipping on Kino/Fermeuse) |
| Other chains | **unchanged since last export** |
| Cancelled and shelved | **unchanged since last export**, except Discovery is **not** in this group |
| Feedgas pipelines | **unchanged since last export**; ownership change vs a tracker **not recoverable** |
| Emission factors | **unchanged since last export** for 0.29/0.12; EAO 0.021/0.156 added as SI (Task 8) |
| Throughput and timing | **unchanged since last export** |
