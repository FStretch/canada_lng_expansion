# Canada LNG Expansion: Lifecycle Emissions Model

An open, reproducible model of the greenhouse gas emissions caused by Canada's liquefied natural
gas export expansion, covering every LNG asset in the country in the register: operating, under
construction and proposed. Headline results are the export chain.

**Start here.** Five files carry the whole thing:

1. `README.md` — this file: method, assumptions, limitations.
2. `Outputs/RESULTS_SUMMARY.md` — the numbers, from the current run.
3. `Inputs/Canada_LNG_Data_Inputs.xlsx` — every factor and parameter, with its type and source.
4. `build_results.py` — what is asserted: every published digit is locked there.
5. `Outputs/SOURCING_AUDIT.md` — the verdict on each number's provenance.

**Status.** A manuscript is in preparation. Results are locked to the 3 September 2026
paper set (run 17:20 UTC) pending submission.

**Reproduce the locked results.** Python 3.13.0, then `pip install -r requirements.txt`
and `python build_results.py`.

---

## What this produces

**The paper set.** Locked 3 September 2026 (run 17:20 UTC). Central case, with the Monte
Carlo 5th to 95th percentile as its interval (10,000 draws, seed 20260828). Central is the
point estimate from the central factor values.

| build-out | lifetime CO2e Mt | lifetime CO2-only Mt | peak | ECCC 2% damages C$bn, valued when caused | ECCC 2% damages C$bn, NPV to 2025 |
|---|---|---|---|---|---|
| Committed (operating + under construction, 3 assets) | **1,860.0** [1,827, 2,024] | **1,792.0** [1,743, 1,911] | **58.0** in 2030 [57, 63] | **745** [729, 801] | **524** |
| Committed plus advanced (5 assets) | **3,786.4** [3,636, 4,096] | **3,648.0** [3,466, 3,871] | **135.1** in 2037 [133, 147] | **1,572** [1,509, 1,681] | **1,051** |
| Full buildout (9 projects, 79.6 mtpa) | **7,167.1** [6,515, 8,089] | **6,909.5** [6,193, 7,665] | **235.9** in 2037 [232, 256] | **3,106** [2,764, 3,546] | **1,945** |

**How the headline is reported.** As the three-point ladder above, with the tier label on each
figure; the single full-slate number is not fronted alone, since about three quarters of it has
no final investment decision. The Monte Carlo interval on each row is factor uncertainty
*conditional on that build-out*. It is not the uncertainty on what Canada's expansion will emit:
that is the spread from the committed row to the full row, about five times wider.

**Damages are two figures answering two questions.** The calendar-year sum values each year's
damage when it is caused, in constant 2025 dollars: the loss-and-damage figure, and the central.
The NPV discounts the same stream to 2025 at the same 2%: the cost-benefit figure, and the
aggregation Government of Canada regulatory guidance uses. Wherever one appears, so does the other.

The Monte Carlo median sits above the central case (7,274.0 Mt at full buildout) because the
sampled stage triangles are right-skewed, shipping 0.05 / 0.12 / 0.31 especially. It is stated
once, with that reason, and is not the reported figure. The upstream triangle high is the GWP20
scenario factor (0.440), not Howarth 0.55.

At full buildout:

| | |
|---|---|
| Headline annual (panel peak) | **235.9 MtCO2e** in 2037 |
| life_average_annual_mt | **205.1 MtCO2e/yr** (not a calendar year) |
| Lifetime emissions | **7,167.1 MtCO2e** (calendar panel 2025–2069) |
| Lifetime, CO2 only | **6,909.5 MtCO2** (plus 8,645 kt CH4) |
| Export capacity | 79.6 mtpa across nine projects |
| Scope 1 and 2 | 37.3 Mt/yr, 18.2% |
| Scope 3 | 167.8 Mt/yr, 81.8% |

Split by where the emissions are counted: **18.2% Canada, 3.2% international marine bunkers,
78.6% foreign**. The CO2-only lifetime is 4.1% of the 170 GtCO2 remaining for 1.5°C.

Every figure in the paper-set table is locked as `EXPECTED_BUILD_OUT` in `build_results.py` and
asserted on every run.

Headline results include assets whose chain is in `headline_scope_chains` (export) and whose
calc_group is in `headline_scope_calc_groups` (operating, under construction, proposed). Eight
non-export assets totalling 242.9 MtCO2e stay in the register as a stated exclusion.

The published lifetime total is the sum of a per-asset, per-calendar-year panel from 2025
through each asset's last emitting year (currently 2069). It is not duration × life-average.
The headline annual figure is the panel peak (235.9 MtCO2e in 2037). `life_average_annual_mt`
(205.1 MtCO2e/yr) is a life-average of utilisation over each facility's operating window,
including start-up years; it is not a calendar year.

These headlines are below the 9,298.1 Mt / 100.1 mtpa figures that included Discovery LNG as
early_proposed. Discovery is now cancelled, matching Global Energy Monitor. That is a scope
change, not a change in the physics of the remaining nine assets. A further 38.9 Mt came off on
3 September 2026 when regasification moved from an uncited 0.04 to the cited 0.021 of
Mukherjee et al. (2025), and a further 53.3 Mt when pipeline transport moved from an assumed 0.10 to
0.074, the figure two independent cited routes converge on. Then 55.4 Mt came back on when the
upstream factor was re-derived on that pipeline value: the old 0.22 inventory figure had netted
the retired 0.10 from the CER anchor, and netting 0.074 instead gives 0.246, a central of 0.277.
Finally 50.3 Mt came off when Fermeuse's derived capacity was netted for the gas liquefaction
burns as fuel (5.0 to 4.5 mtpa). The two 3 September corrections run in opposite directions and
net to +5.1 Mt against the 7,162.0 Mt that preceded them.

---

## Repository structure

```
Inputs/
  Canada_LNG_Asset_Register.xlsx    facts about physical assets, one row per terminal or unit
  Canada_LNG_Data_Inputs.xlsx       emission factors, parameters, scenarios and chain definitions
  loss_damage/                      SC-CO2 schedules, currency conversion, L&D parameters
  loss_damage_r1/                   Burke et al. (2026) pulse damages and the raw replication
                                    files the derived CSVs came from
src/
  inputs.py                         loads and validates both workbooks, exposes typed frames
  model.py                          the lifecycle calculation, per-gas split and aggregation
  trajectories.py                   calendar panel (published lifetime) and 2025–2050 figures
  scope.py                          headline chain/calc_group filter and build-out membership
  loss_damage.py                    global L&D, ECCC per gas + Burke upper bracket
  monte_carlo.py                    sampled physics, then ECCC pricing per gas
  lca_comparison.py                 figure 10, comparator studies on their own boundaries
  benchmark_table.py                six-row boundary-aligned comparison to external estimates
  placeholder_sensitivity.py        first-export-year fill sensitivity (SI)
  lifespan_sensitivity.py           uniform 40-year life, no licence stop (SI)
  feedgas_sensitivity.py            Kino Aski Western Canadian vs US supply (SI)
  drive_sensitivity.py              BC EAO electric-drive liquefaction cases (SI)
  si_table.py                       one row per headline asset for the SI
  figures_report.py                 report figures and their CSV series
  slide_tables.py                   deck-facing Excel tables
  banners.py                        generated lock banners for the dated documents in Outputs/
build_results.py                    orchestrates a run, asserts every lock, writes the outputs
tools/                              one-off, documented scripts that edit an input workbook, plus
                                    stale_figure_inventory.py and refresh_banners.py (re-run after
                                    any re-lock)
requirements.txt                    exact pins for the environment the published run used
CITATION.cff                        citation metadata
Outputs/
  Canada_LNG_Emissions_Results.xlsx results by project, chain, stage, group and scenario
  SLIDE_TABLES.xlsx                 deck-facing tables (one sheet per table; send this file)
  RESULTS_SUMMARY.md                a review summary of the current run
  paper_set_locked.csv              the rounded paper set; its SHA-256 is asserted on every run
  si_table_assets.csv               per-asset SI table
  benchmark_comparison.csv          the boundary-aligned external comparison
  SOURCING_AUDIT.md                 every number, its recorded source, and a verdict (dated)
  LCA_ROMAN_WHITE_GAP.md            well-to-regasification gap diagnostic (dated)
  OIL_COMPARATOR_AUDIT.md           the audit that retired the oil comparator (dated)
  figures/                          the figures used in the report and deck
  figure_data/                      CSV series behind each figure
```

The two input workbooks are the source of truth for emission factors, capacities, scenarios and
named parameters. The model reads them and never writes to them. Where the model needs a value
the inputs do not provide, it raises an error rather than substituting a default. A short list of
structural constants and figure-only fallbacks still lives in code; those are named in
Reproducing a run, below.

---

## Method

### The asset register

Eighteen assets in the calculation, drawn from Global Energy Monitor's Global Gas Infrastructure Tracker
(LNG Terminals, September 2025), Natural Resources Canada's project list, and Canada Energy
Regulator export licence records. Kanata LNG (June 2026) is added from proponent sources and is
not in GEM. Discovery LNG is in GEM as cancelled; the register now matches. Port of Hamilton has
no published capacity and is excluded from totals rather than estimated. Tilbury Marine Jetty
has no lifecycle chain and is excluded, not zeroed.

Three rules govern the register:

- **No fabricated sources.** Every source is a dataset, publication, regulator or filing, never a
  file in this repository. Where a value was entered manually with nothing external behind it, the
  source field says so.
- **Blank beats wrong.** Where a value is unknown the cell is empty and the source reads
  "not available". Assets without a capacity are excluded from all totals rather than estimated.
- **Capacity is nameplate.** Where sources disagree the nameplate design figure is used and the
  alternative recorded. Cedar LNG is the worked example: the proponent's own final investment
  decision announcement states 3.3 mtpa, while NRCan and the CER publish 3.0.

Assets carry two classifications. `tier` describes progress as an export project. `calc_group`
describes simply whether the asset is running, being built, or proposed, and is what the model
groups by.

### Four lifecycle chains

Not every asset passes through the same stages. **Stages absent from a chain are not computed at
all, rather than set to zero.**

| Chain | Stages | Reason |
|---|---|---|
| Export | upstream, pipeline, liquefaction, shipping, regasification, combustion | The full chain |
| Bunkering | upstream, pipeline, liquefaction, combustion | Burned by the vessel that collected it, so never shipped as cargo or regasified |
| Domestic | upstream, pipeline, liquefaction, regasification, combustion | Regasified and burned in Canada, never shipped |
| Import | regasification, combustion | Upstream, liquefaction and shipping occurred abroad |

### Territorial tagging

Every stage carries a tag recording where the emission physically occurs:

- `CAN`, Canada territorial: counts against Canada's national inventory and targets
- `BUNK`, international marine bunkers: reported separately under UNFCCC guidelines and
  attributed to no country. This covers LNG carrier voyages as well as fuel sold to ships at a
  Canadian port
- `FOR`, foreign territorial: counted by the importing country

Territorial tagging is independent of the scope 1, 2 and 3 classification. Scope describes who
controls an emission; territory describes where it occurs. For export LNG the two nearly coincide.
For domestic LNG they diverge, because scope 3 combustion happens in Canada.

**Attributing the whole chain to the Canadian buildout is an accounting choice, not a physical
fact, and it is made deliberately.** The territorial tags record where each tonne is emitted; the
lifetime total then attributes every tonne, including the 79 per cent combusted abroad, to the
Canadian decision to build. That is extraction-based accounting, one of the three recognised
frames alongside territorial (production) and consumption accounting: Davis, Peters and Caldeira
(2011) formalise it as the supply chain of CO2 traced back to the fossil fuel extracted; Andrew,
Davis and Peters (2013) show how the three frames allocate the same emissions differently; and
Steininger et al. (2016) argue the frames should be used together because each makes a different
actor's responsibility visible. This model reports the territorial split *and* the extraction
total so a reader can use either.

### Emission factors

Each stage carries a single central value in tonnes of CO2 equivalent per tonne of LNG. Low and
high figures are recorded for reference but are not used to construct scenarios, because the stages
are not correlated.

| Stage | Central | Basis |
|---|---|---|
| Upstream production | 0.277 | Canada Energy Regulator British Columbia oil and gas emissions, net of the 0.074 pipeline stage, corrected for measured methane on the methane share; every step in the basis cell |
| Pipeline transport | 0.074 | Liu et al. (2021) via the ERA/Modern West restatement, 0.0735; cross-checked against CER/ECCC 2019 national pipeline transport, 0.0744. Applied flat, not distance-scaled |
| Liquefaction | 0.29 | Gas turbine drive, applied to every terminal for its whole operating life. 0.15 is retained as the low bound and applies only if electrification is contracted and delivered |
| Shipping | 0.12 | Howarth (2024), reconstructed against IMO carrier data. Derived on the British Columbia to north-east Asia route and **scaled per asset by route distance** |
| Regasification | 0.021 | Mukherjee et al. (2025), *Communications Earth & Environment* 6:16, peer-reviewed US LNG lifecycle assessment. Range 0.011–0.0275 from IEA (2025) |
| Combustion | 2.75 | Stoichiometric methane (44/16), the right central for de-inerted LNG. Range 2.58–3.00 derived from the IPCC 2006 uncertainty intervals |

**Shipping is scaled by route distance per asset.** The 0.12 central factor is derived on the
British Columbia to north-east Asia route (`route_bc_to_northeast_asia_nm` = 3,800 nm). Each
asset's shipping intensity is `0.12 × route_distance_nm / 3,800`. Seven British Columbia
terminals sit at the 3,800 nm basis; Kino Aski is 2,980 nm and Fermeuse 2,470 nm to Rotterdam,
so the two Atlantic projects carry proportionally less shipping. An asset on a chain that
includes the shipping stage with a blank `route_distance_nm` raises rather than defaulting to
the BC basis; bunkering has no shipping stage. The lifecycle-intensity
comparison in `src/lca_comparison.py` deliberately stays on the unscaled BC basis, because the
comparator studies are single-route figures.

**Canadian sources are used wherever the stage occurs in Canada.** Upstream, pipeline and
liquefaction all happen here and draw on Canadian regulatory and inventory data. Shipping,
regasification and combustion occur elsewhere and use international sources. That boundary
matches the scope 1 and 2 versus scope 3 split.

**Two factors moved onto cited values on 3 September 2026.** Regasification was an uncited 0.04
attributed to the RMI Oil Climate Index, which states no such figure; it is now **0.021** from
Mukherjee et al. (2025), with a 0.011–0.0275 range from the IEA's 0.2–0.5 gCO2e/MJ (converted at the
IEA's own 55 MJ/kg basis). That took 38.9 Mt off the lifetime. The combustion **range** was an
uncited 2.50–3.00; it is now **2.58–3.00**, derived from the IPCC 2006 Vol. 2 Ch. 1 uncertainty
intervals on natural gas NCV (Table 1.2) and carbon content (Table 1.3), applied as a relative
band to our 2.75 central. The central 2.75 is unchanged: it is the stoichiometric value for pure
methane, which is right for LNG because liquefaction strips inerts and heavier fractions. IPCC's
own natural-gas central of 2.693 is for pipeline gas.

**Pipeline transport moved onto two converging cited routes on 3 September 2026**, from an
assumed 0.10 to **0.074**. Route A: Liu et al. (2021) report 4.2 gCO2e/MJ at transmission
pipeline outlet, and the ERA / Modern West restatement puts the same study at 2.86 gCO2e/MJ at
plant exit; the difference, 1.34 gCO2e/MJ, is the transmission stage, which at 54.863 GJ/t is
0.0735 tCO2e/t. Route B: the CER reports 8.3 MtCO2e of Canadian pipeline transport emissions in
2019, primarily compressor-station combustion, which over roughly 170 bcm of marketable gas at
36 PJ/bcm is 0.0744 tCO2e/t. The two agree to within 1.2%; the retired 0.10 was about 35% above
both.

**The pipeline factor is applied flat, not scaled by distance** — unlike shipping. Route A is
calibrated on a 1,100 km line and Route B is a national average haul, while the in-scope feedgas
lines are Coastal GasLink 670 km, Prince Rupert Gas Transmission 750 km and FortisBC Eagle
Mountain 47 km. If transmission emissions scale with distance, 0.074 is high for all three,
Woodfibre most of all. That is a stated limitation rather than a correction applied here. The
0.037–0.133 range is a declared assumption: it keeps the relative width of the retired band, and
the 1.2% agreement between the two routes is convergence on the central, not an uncertainty
interval.

**The pipeline factor sets aside British Columbia evidence, deliberately.** The model's rule is
that Canadian sources are used wherever a stage occurs in Canada, and for this stage a British
Columbia document exists: the Coastal GasLink assessment implies about 0.094 tCO2e/t at design
capacity, above the retired 0.10-era check and the adopted 0.074 alike. It was not adopted
because it is a projection from an environmental assessment, made before the line operated,
whereas Liu et al. (2021) is peer-reviewed and measurement-informed and the CER route is an
observed national inventory; two independent routes agreeing to 1.2 per cent is the stronger
evidence, and the projection sits inside the sampled band. The basis cell says the same.

All the external comparisons the model holds are now assembled in one place — see **Benchmark
comparison** in `Outputs/RESULTS_SUMMARY.md` and `Outputs/benchmark_comparison.csv`. Every
comparison that is not an adopted value points the same way: this model sits at or below the
external figure.

**Electric drive is not assumed for any terminal.** Of the projects claiming electrification, only
Cedar and Woodfibre have interconnection works under construction; the remainder rest on memoranda
of understanding, aspirations conditional on transmission that has not been built, or statements
with no firm date. Ksi Lisims holds an MOU with BC Hydro for up to 600 MW conditional on the North
Coast Transmission Line expansion, which is not built. LNG Canada Phase 2 states an intention to
transition to electric motors as more renewable power becomes available, with no date and no
contracted supply. A commitment contingent on infrastructure that does not exist is not a basis for
lowering the emissions factor. Previous drive classifications are retained in
`liquefaction_drive_note`. Where electrification is later contracted and built, this assumption
should be revisited. An appendix comparator (`Outputs/figures/fig08_electrification_canada_territorial.png`)
shows Canada-territorial LNG if liquefaction ran at 0.15 instead of 0.29, both for the assets that
previously claimed electric drive and for every terminal. That 0.15 is Pembina's published figure
for LNG Canada Phase 1 under electric drive (*Squaring the Circle: State of LNG 2023*). It
replaced 0.12 on 3 September 2026: no Pembina document states 0.12, which appears to have been a
misreading of the 0.11 tCO2e/t *reduction* in *Wellhead to Waterline* (2014) as an absolute
intensity.

**Upstream is derived rather than adopted, and every step is shown.** The CER reports British
Columbia oil and gas production, processing and transmission emissions of 14.6 MtCO2e for 2022,
against roughly 63 billion cubic metres of marketable gas. At 1.38 bcm per Mt of LNG that is
45.65 Mt LNG-equivalent, so the anchor is 0.320 tCO2e per tonne *including* transmission.
Transmission is this model's separate pipeline stage, so its central of 0.074 is removed:
0.320 − 0.074 = **0.246**, the official-inventory upstream factor. Peer-reviewed measurement
studies consistently find Canadian inventories understate upstream methane by 1.5 to 1.7 times.
Applied to the methane portion only, at the 0.25 methane share, that gives
0.246 × (1 − 0.25 + 1.5 × 0.25) = 0.2765, stored as **0.277**. The basis cell on the Emission
Factors sheet carries the same arithmetic, so the number reproduces from the workbook alone.
Until 3 September 2026 the inventory figure was 0.22, which had netted the *retired* pipeline
value of 0.10; when pipeline moved to 0.074 that arithmetic stopped closing and the chain was
dropping about 0.026 tCO2e/t against its own anchor. Re-deriving added 55.4 Mt to the lifetime.

Howarth (2024) is retained as the upper bound at 0.55 rather than used as the central value. That
study addresses United States supply chains using higher leakage assumptions, while Canadian
measurement evidence finds the Montney formation among the lowest-intensity gas plays in North
America.

### Throughput and timing

| Assumption | Value | Basis |
|---|---|---|
| Utilisation, year 1 and 2 | 40% / 70% | Model assumption |
| Utilisation, steady state | 83.9% | IGU World LNG Report 2026, global average for 2025 |
| LNG Canada Phase 1 ramp | 25 / 60 / 85% | Observed startup, first cargo June 2025 |
| Saint John import | 2.5% flat | Repsol annual report, 8 TBtu regasified in 2023 |
| Delay where no FID | 5 years | IEA Global LNG Capacity Tracker and Rogers (2017), OIES Energy Insight 4 p. 1. Tested across an asymmetric 4 to 8 years |
| Operating life | licence end, else 40 years | CER export licence expiry where filed; not a uniform 40-year run |
| Methane GWP100 / GWP20 | 29.8 / 82.5 | IPCC AR6 Working Group I, fossil methane |
| Remaining 1.5°C budget (50%) | 170 GtCO2 | Global Carbon Budget 2025, from start of 2026 |
| Remaining 1.7°C / 2°C (50%) | 525 / 1,055 GtCO2 | Same source |

**Lifespans are capped at each project's export licence expiry** rather than running a uniform 40
years. The end year may emit; the year after may not. That cut is 1.2 GtCO2e against the same
nine assets at a uniform 40 years from first export with no licence stop (8,372.5 Mt versus
7,167.1 Mt). Anyone comparing versions should treat that as a methodological improvement, not
an error in the lower total. Where a proponent states a different operating life, that is used
instead: Summit Lake PG LNG states 30 years.

Lifetime emissions are also reported as a share of those remaining budgets. The budgets are
CO2, so the **paper value is the CO2-only lifetime** (6,909.5 MtCO2 at full buildout, 4.1% of
the 170 GtCO2 remaining for 1.5°C). That is like for like. The panel carries an explicit
per-gas split — `co2_mt`, `ch4_derived_co2e_mt` and `ch4_mass_kt` per asset-year, summing to
`emissions_mtco2e` exactly — built from parameters already on the workbook: upstream CH4 is
the scenario factor less the CO2 part of the official inventory, and shipping CH4 is the
measured methane-slip share of the carrier uplift (1 − 1/1.44). Two residual caveats remain:
pipeline fugitive methane is not split, so a small amount of methane sits inside the CO2
total; and non-CO2 gases other than methane (N2O, refrigerants) are not counted anywhere in
the model. The GWP100 CO2e share against the same budgets (4.3% for 1.5°C) is still reported
alongside for continuity.

The FID delay sits inside the lifespan window rather than extending it, so a delayed project has
fewer operating years. It is the least evidenced parameter in the model.

### Loss and damage

A separate module (`src/loss_damage.py`) multiplies the same full-lifecycle, year-of-emission
CO2e series by a social cost of carbon. It does not change the emissions totals.

The **central case** is named in `Inputs/loss_damage/parameters.csv`
(`central_price_family=eccc`, `central_aggregation=calendar_year`,
`eccc_central_discount_rate_pct=2`): ECCC official SC-CO2 **and SC-CH4**
applied per calendar year of emissions to the panel's per-gas split, converted
to 2025 CAD. ECCC 1.5% and 2.5% are the central case's sensitivity range.

**Why the calendar-year sum is the central, and why the NPV travels with it.** Each year's
social cost is already the present value, at that year, of the future damage stream from a tonne
emitted then. Summing the years without further discounting therefore values each year's damage
*when it is caused*, held at 2025 prices. That is the loss-and-damage question — what harm does
this buildout do, valued as it does it — and it is how Burke et al. (2026) aggregate a multi-year
stream. Discounting each year's damage back to 2025 at the same 2% answers a different question,
the cost-benefit one — what is the stream worth today, to weigh against benefits also expressed
today — and it is how the Government of Canada's regulatory guidance aggregates a multi-year
stream. At full buildout the two are **C$3,106 bn** valued when caused and **C$1,945 bn** as an
NPV to 2025. The paper asks the loss-and-damage question, so the calendar sum is the central; the
NPV is not a sensitivity on it but the answer to the other question, and the two are carried
together wherever the total is stated. An earlier note that "the official schedule already embeds
Ramsey discounting, so a second NPV is a sensitivity only" was true of a single year's social
cost and did not settle the cross-year question; it has been withdrawn.
Burke et al. (2026) is an upper-bracket sensitivity across discount rates and
Figure 2e horizons (default g = 0; Hatton +2% is not used). Canada's 0.17%
share of a 1990 pulse (future window) is applied to Burke damages only, and is
reported with `P_dam_FD` = 0.41 attached: only 41% of Burke draws put Canada in
net loss from that pulse at all, against 0.98 for the United States and China.
The replication package ships no country-level damages table by pulse year, so
no 2020-pulse share is available. The Conference
Board whole-chain GDP figure (Table 1: C$11.153bn/yr in 2020 CAD at 56 mtpa),
scaled linearly on proposed export nameplate (now 60.2 mtpa) and inflated to
2025 CAD, is the Canada denominator.

Damages are priced **per gas**. Each calendar year contributes
`co2_t × SC-CO2_t + ch4_mass_t × SC-CH4_t`, both official ECCC schedules, both
at the same discount rate, both inflated CAD 2021 to CAD 2025 exactly once.
The CO2 and CH4 series come from the panel's explicit split (upstream excess
over inventory CO2, plus shipping methane slip). Methane is about 1.7% of the
central damage bill. Burke has no SC-CH4, so the Burke family still prices the
whole GWP100 CO2e total at Burke's SC-CO2; that is stated in its labels.
Pricing the whole CO2e at SC-CO2, the retired treatment, would raise the
central figure by about 2%; that is reported as a one-line reconciliation.

### Scenarios

Five scenarios vary the upstream factor, each named for its basis rather than described as a
percentage.

| Scenario | Upstream | Basis |
|---|---|---|
| `inventory_as_reported` | 0.246 | Official Canadian inventory at face value, net of the 0.074 pipeline stage |
| `measurement_central` | 0.277 | Default. Three measurement studies agree on a 1.5x correction |
| `measurement_high` | 0.289 | 1.7x, from a British Columbia aircraft survey |
| `near_term_methane_gwp20` | 0.440 | Methane weighted over 20 years rather than 100 |
| `howarth_high` | 0.55 | United States focused study, high leakage assumptions |

The 20-year warming uplift is applied to the methane portion of upstream emissions only. The
non-methane portion of the inventory factor is unchanged. The methane portion is multiplied by
the 1.5 measurement correction and then by the ratio of GWP20 to GWP100 for fossil methane
(82.5 / 29.8). The result, 0.440, depends on the methane share of 0.25 and the 0.246 inventory
base. Applying the
uplift to the whole factor would assume all upstream emissions are methane. Pipeline methane is
not re-weighted: no pipeline methane share is defined in the workbook.

### Declared assumptions

These are judgements, not derivations. They are typed as such on the Parameters or Emission
Factors sheets.

- The 2030 overshoot gap of 200 Mt is a round figure. The interval behind it is 191 to 229 Mt
  (projected 646 Mt minus the 417–455 Mt target range).
- Upstream factors are stored to three decimals: 0.277 and 0.289 are rounded from 0.2765 and
  0.2888 on the 0.2458 inventory base. Two-decimal storage was dropped on 3 September 2026
  because it hid the dependence of the stored central on the methane share.
- Shipping is held at 0.12 although the IMO reconstruction gives 0.110.
- The Conference Board GDP figure is scaled linearly from 56 mtpa to the proposed export
  nameplate (60.2 mtpa).
- First-export years of 2033 and 2035 are placeholder sensitivity cases, not filed dates.
  Central fill remains 2030.
- Cedar is assumed to share Ksi Lisims' electric-drive class in the SI drive sensitivity. The
  central case is gas turbine for every terminal.
- The pipeline 0.037–0.133 range is assumed. The central 0.074 is cited; no published
  uncertainty interval for Canadian gas transmission intensity was located.
- Liquefaction range_high 0.36 is an uncited literature upper bound.
- `upstream_ch4_share` is **0.25**, the centre of the 18–34% bracket that Johnson et al. (2023)
  supports. It is still a judgement within a bracket rather than a single reported figure, so it
  stays typed as an assumption.
- The FID-delay band **4 / 5 / 8** is deliberately asymmetric. The cited mid of 5 years is
  "typically 5 years, *before* unforeseen slippage", and slippage in LNG construction runs one
  way. A symmetric band would imply a project is as likely to be early as late.

### Proponent-sourced values

These are taken from the proponent, not from an independent regulator or inventory, and are
labelled as such in the register.

- Cedar LNG at 3.3 mtpa. NRCan and the CER publish 3.0.
- Kino Aski at 15 mtpa (proponent press coverage; no regulatory process has begun).
- Kanata LNG at 12 mtpa (proponent; not in GEM).
- Summit Lake's 30-year operating life.
- LNG Canada Phase 1 ramp 25 / 60 / 85%.
- The Conference Board GDP figure, published via the LNG Alliance.
- The 3,800 nautical mile British Columbia to north-east Asia route, via CAPP / Oxford.

---

## Validation

**Pipeline transport.** The British Columbia Environmental Assessment Office's 2014 assessment
of Coastal GasLink put operations at 3.517 MtCO2e a year at the line's full 5 Bcf/d design
capacity. Over that throughput (51.7 bcm a year, 37.4 Mt of LNG-equivalent at 1.38 bcm per Mt)
it implies about **0.094 tCO2e per tonne**. The model holds **0.074**, from two independent
routes that agree to 1.2 per cent: Liu et al. (2021) on an 1,100 km Alberta line and the
CER/ECCC national pipeline-transport inventory. The assessment figure is 27 per cent above the
adopted value. It is a pre-operation projection rather than a measurement, which is why the
peer-reviewed and inventory routes are preferred; the gap is inside the sampled 0.037–0.133
band, and if the line runs at its assessed intensity the model is low on the LNG Canada and
Cedar share of throughput by roughly 1 MtCO2e a year. An earlier version of this paragraph
reported a 0.6 per cent agreement between the model and the assessment; that was the output at
the retired assumed value of 0.10 and confirmed only the arithmetic of scaling it.

**Shipping.** The 0.12 factor was reconstructed from the International Maritime Organization's 2023
LNG carrier fleet average of 8.50 gCO2 per deadweight tonne per nautical mile, applied over a round
trip and uplifted for measured methane slip, giving 0.110. Within 8 per cent. The model holds
0.12; 0.110 is the reconstruction.

**Liquefaction.** LNG Canada Phase 1 produces 4.06 MtCO2e a year on a nameplate basis, against the
approximately 4 Mt in the facility's own environmental assessment.

Every run also asserts that capacity totals tie to the register, that scope and territorial splits
sum to the total, and that no stage is computed for a chain that does not include it.

---

## Limitations

**No displacement counterfactual is modelled, and that is a choice.** The quantity reported is
the gross emissions committed by the buildout on the extraction axis: every tonne of LNG the
slate would produce, followed through to combustion. The model does not ask whether that gas
displaces coal, other LNG, or nothing, and does not net any of it off. Gross extraction-basis
accounting is a recognised frame with regulatory precedent. The UK Supreme Court in *R (Finch) v
Surrey County Council* [2024] UKSC 20 held that downstream combustion emissions are an effect of
an extraction project that must be assessed; the UK government's supplementary guidance that
implements it (Department for Energy Security and Net Zero, *Environmental Impact Assessment:
assessing effects of downstream scope 3 emissions on climate*, June 2025) directs that the
starting point is "a (rebuttable) presumption that all produced hydrocarbons over the lifetime of
a project will eventually be combusted" (p. 9), and that substitution "is not considered to be a
factor affecting whether scope 3 emissions from a project's downstream activities are an effect
that needs to be assessed" (p. 7). That is exactly this model's construction. A displacement
argument is a separate claim that a proponent can make with evidence; it does not change what
the buildout commits.

**Construction emissions are excluded.** Literature suggests these would add roughly 50 to 150
MtCO2e, about 1 to 2 per cent of the lifecycle total. All figures are conservative in this respect.

**Abandoned well methane is not counted.** Measured diffusive flux from abandoned shale wells
reaches 20,000 cubic metres per well per day. The buildout requires 12,558 to 32,000 new wells, all
of which are eventually abandoned.

**The methane share of upstream emissions is a bracketed judgement, not a reported figure.**
British Columbia does not publish the carbon dioxide and methane split separately. The share is
**0.25**, set on 3 September 2026 from Johnson et al. (2023): their British Columbia 2021 upstream
methane intensity of 0.38 per cent of marketed gas, divided by the 1.7 times factor by which their
measurement-based inventory exceeds the official one, implies a methane share of 25 to 30 per cent
depending on the methane GWP vintage; an absolute route over the same paper's 144.5 kt/y gives 21
to 25 per cent. The bracket spans roughly 18 to 34 per cent and centres near 25, which is the value
adopted. It replaced an assumed 0.30 that sat high in the bracket without a stated reason. The
share now visibly moves the stored central: 0.246 × (1 − s + 1.5s) is 0.283 at a share of 0.30 and
0.277 at 0.25, stored to three decimals since 3 September 2026. Under the earlier two-decimal
storage both rounded to 0.25 and the headline looked insensitive to the share; that was a rounding
artefact, not a property of the model. The share also sets the CO2/CH4 split, the SC-CH4 damages
line, and the `near_term_methane_gwp20` scenario.

**Two projects rest on weak capacity figures.** Kino Aski LNG's 15 mtpa (formerly Marinvest,
Baie-Comeau) is from a 17 August 2026 press release; no regulatory process has begun and the
feedgas pipeline route is undefined. Summit Lake's 2.7 mtpa is an upper bound from an assessment
the proponent asked to suspend. Both are identified by tier and can be removed from any total.

**Discovery LNG is cancelled in this version.** GEM records cancelled (inferred 4 y). No
regulatory filing, proponent statement or news of current activity was found after GEM's
September 2025 snapshot. The register had carried it as early_proposed at 20 mtpa on the basis
of a third-party table that was wrong about Grassy Point, Bear Head and Goldboro. It is now
inactive, matching GEM. That removes 2,043.9 MtCO2e and 20 mtpa from the headline.

**Fermeuse's 4.5 mtpa is derived, not published, and conditional on the proponent's resource
claim.** The proponent has not stated a liquefaction capacity. The figure divides the stated
9.7 Tcf (275 bcm) Jeanne d'Arc resource by 1.38 bcm per mtpa over a 40-year life, which gives
4.98 mtpa if every molecule became LNG, and then nets the gas liquefaction burns as fuel using the
model's own factors: 0.29 tCO2e/t liquefaction over 2.75 tCO2/t combustion is 0.1055 t of gas per
tonne of LNG, so 4.98 / 1.1055 = 4.5 mtpa. Until 3 September 2026 the register carried 5.0,
without the fuel netting, and called it "the lowest defensible derivation". It was not: the
derivation assumes full recovery of a resource stated by the proponent, on a flat 40-year profile
for an associated-gas play whose output would follow the oil decline, with nothing reserved for
platform fuel or reinjection. Each of those choices pushes the figure up, so it sits closer to an
upper bound on the proponent's claim than to a conservative one. A 25-year life gives about 8
mtpa and capital-cost benchmarking 9 to 12; neither is used.

**Tilbury Phase 2's classification is a judgement.** FortisBC describes the expansion as serving
Lower Mainland resilience and marine fuelling; NRCan lists it as an export project. This analysis
places it on the bunkering chain and records the disagreement rather than resolving it.

**Capacity is never summed across chains.** Export and bunkering capacity is liquefaction; import
capacity is regasification. They measure opposite operations.

**The LNG Canada Phase 1 ramp has the right average and the wrong shape.** The model assumes
25 / 60 / 85 per cent for years one, two and steady state. Observed throughput now exists: first
cargo 30 June 2025, Train 2 in production from November 2025, roughly 4.6 Mt exported to
mid-March 2026, the first month above 1 Mt in April 2026 and 1.2 Mt a month by May 2026. Against
14 mtpa nameplate that is about 11 per cent of a full year in calendar 2025 against the assumed 25
per cent, then 86 and 103 per cent of nameplate in April and May 2026 against the assumed 60 per
cent for year two. The model starts too high and ramps too slowly, and the two errors largely
offset over the asset's life. Recorded against the parameters rather than corrected, because one
facility's observed profile is not a basis for the generic ramp applied to every other asset.
The same shape problem applies to the generic 0.40 / 0.70 ramp on the other eight assets: the
observed data say it is too high in year one and too slow to full rates. Lifetime totals are
insensitive, because the two errors offset; the **2037 peak year is not**, because the peak is
set by which assets reach full rates in which calendar year. **No ramp-shape sensitivity
exists.** A reader should treat the peak year as ramp-dependent to within a year or two either
side, and the peak magnitude as more robust than its timing.

**The chain sits at or below every external benchmark it is compared against, and here is what
that is worth.** `Outputs/benchmark_comparison.csv` assembles six boundary-aligned comparisons;
none shows this model above the external figure. Liquefaction is held at 0.29 against the IEA's
0.33 global average: adopting the IEA figure would add roughly **80 Mt** to the
7,167 Mt lifetime. Shipping is held at 0.12 against the IEA's 0.18 to China: adopting that
figure as it stands would add roughly **110 Mt**, and on a per-kilometre basis, since the
IEA voyage is shorter, the IEA intensity would add closer to **300 Mt**. On the aligned
well-to-regasification boundary the model is 0.78 tCO2e/t against Roman-White et al.'s expected
1.19, and on liquefaction plus shipping plus regasification it is 0.43 against Balcombe et al.'s
0.62 to 1.71. Every held-low choice is recorded with its reason in the Emission Factors sheet;
the direction is uniformly conservative, and a reader who prefers the external values can scale
from the stage series in `Outputs/figure_data/fig01_stage_breakdown.csv`.

**Annual figures come in two forms.** The headline annual is the panel peak (235.9 MtCO2e in
2037). `life_average_annual_mt` (205.1 MtCO2e/yr) is a life-average across each facility's
operating window. The published lifetime (7,167.1 MtCO2e) is the sum of the calendar panel
from 2025 through 2069. Duration × life-average is no longer published.

**One route distance is the west-coast basis rather than a port-specific figure.** Kanata LNG
(Prince Rupert) has no published port-to-port sailing distance, so it takes the cited west-coast
Canada figure of 3,800 nm used for the other BC export assets. Prince Rupert is nearer north Asia,
so that is a small overstatement. Recorded in the register's Data Gaps sheet.

**The oil comparison has been retired.** Figure 7 compared Canadian LNG against Trans Mountain
and a proposed Alberta–BC bitumen line. It was removed from the model on 3 September 2026 when
the Trans Mountain slide was dropped from the deck. It rested on three addends (0.075 upstream,
0.008 transport, 0.43 combustion) that were never separately sourced, applied NRCan's oil-sands
intensity to a mixed ticket slate, ran oil at nameplate × 365 days × 40 years against an LNG side
that carries a ramp, a utilisation curve and an FID delay — understating LNG by roughly 19% — and
used an unvalidated 1 Mbpd capacity for a pipeline with no published design figure. Rather than
leave it generating an unpublished figure on unsourced arithmetic, the figure, slide table 15,
`src/report_params.py` and the seven `tmx_*` / `days_per_year` parameters were all removed. The
history is in git.

---

## Reproducing a run

Built and published on **Python 3.13.0** (Windows 11). Dependencies are pinned exactly in
`requirements.txt` — `pandas==2.3.2`, `numpy==2.3.3`, `matplotlib==3.10.8`, `openpyxl==3.1.5` —
rather than ranged, because the run asserts a SHA-256 over the locked paper-set table and a
library upgrade that changed float formatting should fail the run rather than quietly republish
different digits.

```bash
pip install -r requirements.txt
```

```bash
python build_results.py
```

The build sets Matplotlib's Agg backend, so figures write without a display.

Reads both workbooks from `Inputs/`, runs all five scenarios, and writes the results workbook,
`SLIDE_TABLES.xlsx`, the summary and the figures to `Outputs/`. The inputs are opened read-only
and the run asserts they are unmodified on completion.

**Every published number is locked.** `EXPECTED_BUILD_OUT` in `build_results.py` holds the paper
set for all three build-outs, and `EXPECTED_PAPER_SET_SHA256` is a SHA-256 over
`Outputs/paper_set_locked.csv`, the rounded canonical copy of that table. A re-run that moves any
published digit fails with the expected and actual hash rather than silently rewriting the
outputs. Re-locking is deliberate: both constants change in the same commit, with the old and
new values in the commit message.

Repository metadata for citation is in `CITATION.cff`.

Workbook edits are deliberate and scripted. The model never writes to `Inputs/`; the one-off
scripts that changed an input workbook or the register live in `tools/`, each documenting what it
changed and why.

The three dated documents in `Outputs/` — the sourcing audit, the Roman-White gap diagnostic
and the oil comparator audit — each open with a banner that is
generated, not hand-written: `src/banners.py` renders it from the lock constants, and the run
asserts every banner matches. After a re-lock, `python tools/refresh_banners.py` rewrites them;
until it is run, the build fails and says so. Hand-written banners went stale twice, which is why.

To change an assumption, edit the input workbooks rather than the code. Emission factors,
capacities, scenarios, utilisation, GWP values, FID and life bounds, and the LCA comparator
totals now live on those sheets.

**What remains in code, and why.** Unit conversions and plot styling. The 2025–2050 figure-year
window. Build-out membership (which tiers sit in committed). Assertions that lock published
digits so a drifted workbook fails the run. The Kino Aski
SI distance multipliers (×3 and ×5) and the 670 km Coastal GasLink length used only in that
sensitivity. None of those is an emission factor or a project capacity.

---

## Principal data sources

**Infrastructure**
Global Energy Monitor, Global Gas Infrastructure Tracker: LNG Terminals (September 2025) and Gas
Pipelines (November 2025); Global Oil and Gas Extraction Tracker (March 2026). Tracker data is
licensed CC BY 4.0; attribution is required.

**Government and regulatory**
- *R (Finch) v Surrey County Council* [2024] UKSC 20. https://www.supremecourt.uk/cases/uksc-2022-0064
- Department for Energy Security and Net Zero (June 2025). Environmental Impact Assessment:
  assessing effects of downstream scope 3 emissions on climate. Supplementary guidance for
  offshore oil and gas projects.
  https://assets.publishing.service.gov.uk/media/6853fa3d1203c00468ba2b15/Supplementary_guidance_-_Effects_of_Scope_3_Emissions.pdf
Canada Energy Regulator: provincial and territorial energy profiles, export licence applications,
Canada's Energy Future. Environment and Climate Change Canada: National Inventory Report. Natural
Resources Canada: Canadian LNG projects. British Columbia Environmental Assessment Office:
Coastal GasLink and LNG Canada assessments. CER and NRCan figures used in the model are cited
per cell in `Inputs/Canada_LNG_Asset_Register.xlsx` and `Inputs/Canada_LNG_Data_Inputs.xlsx`.

**Peer-reviewed literature**
- Davis, S.J., Peters, G.P. and Caldeira, K. (2011). The supply chain of CO2 emissions. *PNAS*
  108(45), 18554–18559. https://doi.org/10.1073/pnas.1107409108
- Andrew, R.M., Davis, S.J. and Peters, G.P. (2013). Climate policy and dependence on traded
  carbon. *Environmental Research Letters* 8, 034011. https://doi.org/10.1088/1748-9326/8/3/034011
- Steininger, K.W., Lininger, C., Meyer, L.H., Muñoz, P. and Schinko, T. (2016). Multiple carbon
  accounting to support just and effective climate policies. *Nature Climate Change* 6, 35–41.
  https://doi.org/10.1038/nclimate2867
Howarth (2024), *Energy Science and Engineering*. MacKay et al. (2021), *Scientific Reports*.
Johnson et al. (2023), *Communications Earth and Environment*. Balcombe et al. (2022),
*Environmental Science and Technology*. Di Lullo et al. (2020), *Journal of Natural Gas Science
and Engineering*.

**Industry**
International Gas Union, World LNG Report 2026. International Maritime Organization, Data
Collection System annual report. Intergovernmental Panel on Climate Change, AR6 and the 2006
Guidelines.

---

## Citation

> Toronto Climate Observatory (2026). *The Cumulative Climate Impact of Canada's LNG Expansion:
> first results.* Toronto, ON.

---

## Contributing and corrections

Corrections are welcome, particularly on the asset register. If a capacity, status, licence term or
start year is wrong, please open an issue with the source that supports the correction. The
register records where each value came from, so a disagreement can usually be resolved by comparing
sources directly.
