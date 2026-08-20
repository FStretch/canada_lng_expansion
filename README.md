# Canada LNG Expansion: Lifecycle Emissions Model

An open, reproducible model of the greenhouse gas emissions caused by Canada's liquefied natural
gas industry, covering every LNG asset in the country: operating, under construction and proposed.

---

## What this produces

At full buildout across all Canadian LNG assets:

| | |
|---|---|
| Annual emissions | **259.2 MtCO2e/yr** |
| Lifetime emissions | **10,193.7 MtCO2e** |
| Export capacity | 95.1 mtpa across ten projects |
| Scope 1 and 2 | 46.7 Mt/yr, 18.0% |
| Scope 3 | 212.5 Mt/yr, 82.0% |

Split by where the emissions are counted: **18.5% Canada, 5.7% international marine bunkers,
75.8% foreign**.

Annual figures are averaged across each facility's operating life, which includes years of reduced
output during start-up. Peak annual emissions once all facilities reach steady state are higher, at
approximately 295 MtCO2e.

---

## Repository structure

```
Inputs/
  Canada_LNG_Asset_Register.xlsx    facts about physical assets, one row per terminal or unit
  Canada_LNG_Data_Inputs.xlsx       emission factors, parameters, scenarios and chain definitions
src/
  inputs.py                         loads and validates both workbooks, exposes typed frames
  model.py                          the lifecycle calculation and aggregation
build_results.py                    orchestrates a run and writes the outputs
Outputs/
  Canada_LNG_Emissions_Results.xlsx results by project, chain, stage, group and scenario
  RESULTS_SUMMARY.md                a review summary of the current run
  figures/                          the figures used in the report and deck
```

The two input workbooks are the only source of truth. The model reads them and never writes to
them. Where the model needs a value the inputs do not provide, it raises an error rather than
substituting a default.

---

## Method

### The asset register

Fifteen assets in scope, drawn from Global Energy Monitor's Global Gas Infrastructure Tracker
(LNG Terminals, September 2025), Natural Resources Canada's project list, and Canada Energy
Regulator export licence records. Kanata LNG (June 2026) is added from proponent sources and is
not in GEM. Discovery LNG is in GEM but was moved from inactive to early_proposed pending
verification. Port of Hamilton has no published capacity and is excluded from totals rather than
estimated.

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

### Emission factors

Each stage carries a single central value in tonnes of CO2 equivalent per tonne of LNG. Low and
high figures are recorded for reference but are not used to construct scenarios, because the stages
are not correlated.

| Stage | Central | Basis |
|---|---|---|
| Upstream production | 0.25 | Canada Energy Regulator British Columbia oil and gas emissions, corrected for measured methane |
| Pipeline transport | 0.10 | Literature band, validated against the BC assessment of Coastal GasLink |
| Liquefaction | 0.29 | Gas turbine drive, applied to every terminal for its whole operating life. 0.12 is retained as the low bound and applies only if electrification is contracted and delivered |
| Shipping | 0.12 | Howarth (2024), validated against IMO carrier data |
| Regasification | 0.04 | RMI Oil Climate Index |
| Combustion | 2.75 | IPCC 2006 Guidelines, default factor for natural gas |

**Canadian sources are used wherever the stage occurs in Canada.** Upstream, pipeline and
liquefaction all happen here and draw on Canadian regulatory and inventory data. Shipping,
regasification and combustion occur elsewhere and use international sources. That boundary matches
the scope 1 and 2 versus scope 3 split.

**Electric drive is not assumed for any terminal.** Of the projects claiming electrification, only
Cedar and Woodfibre have interconnection works under construction; the remainder rest on memoranda
of understanding, aspirations conditional on transmission that has not been built, or statements
with no firm date. Ksi Lisims holds an MOU with BC Hydro for up to 600 MW conditional on the North
Coast Transmission Line expansion, which is not built. LNG Canada Phase 2 states an intention to
transition to electric motors as more renewable power becomes available, with no date and no
contracted supply. A commitment contingent on infrastructure that does not exist is not a basis for
lowering the emissions factor. Previous drive classifications are retained in
`liquefaction_drive_note`. Where electrification is later contracted and built, this assumption
should be revisited.

**Upstream is derived rather than adopted.** The CER reports British Columbia oil and gas
production, processing and transmission emissions of 14.6 MtCO2e for 2022, against roughly 63
billion cubic metres of marketable gas. Net of pipeline transport, which is counted separately,
that gives 0.22 tCO2e per tonne of LNG. Peer-reviewed measurement studies consistently find
Canadian inventories understate upstream methane by 1.5 to 1.7 times. Applied to the methane
portion only, at an assumed 30 per cent methane share, that gives a central value of 0.25.

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
| Delay where no FID | 5 years | Planning assumption, tested across 3 to 7 years |
| Operating life | 40 years | CER export licence terms, not an assumption |
| Methane GWP100 / GWP20 | 29.8 / 82.5 | IPCC AR6 Working Group I, fossil methane |

The FID delay sits inside the lifespan window rather than extending it, so a delayed project has
fewer operating years. It is the least evidenced parameter in the model and is worth approximately
13 MtCO2e a year.

Lifespan comes from each project's CER export licence term where one exists. Where a proponent
states a different operating life, that is used instead: Summit Lake PG LNG states 30 years.

### Scenarios

Five scenarios vary the upstream factor, each named for its basis rather than described as a
percentage.

| Scenario | Upstream | Basis |
|---|---|---|
| `inventory_as_reported` | 0.22 | Official Canadian inventory at face value |
| `measurement_central` | 0.25 | Default. Three measurement studies agree on a 1.5x correction |
| `measurement_high` | 0.26 | 1.7x, from a British Columbia aircraft survey |
| `near_term_methane_gwp20` | 0.33 | Methane weighted over 20 years rather than 100 |
| `howarth_high` | 0.55 | United States focused study, high leakage assumptions |

The 20-year warming uplift is applied to the methane portion of upstream and pipeline emissions
only. Applying it to the whole factor would assume all upstream emissions are methane and overstate
the result by roughly 1.8 times.

---

## Validation

Two stages were checked against independent sources:

**Pipeline transport.** The model produces 1.47 MtCO2e a year for LNG Canada Phase 1, against 1.48
implied by the British Columbia Environmental Assessment Office's assessment of Coastal GasLink.
A difference of 0.6 per cent.

**Shipping.** The 0.12 factor was reconstructed from the International Maritime Organization's 2023
LNG carrier fleet average of 8.50 gCO2 per deadweight tonne per nautical mile, applied over a round
trip and uplifted for measured methane slip, giving 0.110. Within 8 per cent.

**Liquefaction.** LNG Canada Phase 1 produces 4.06 MtCO2e a year on a nameplate basis, against the
approximately 4 Mt in the facility's own environmental assessment.

Every run also asserts that capacity totals tie to the register, that scope and territorial splits
sum to the total, and that no stage is computed for a chain that does not include it.

---

## Limitations

**Construction emissions are excluded.** Literature suggests these would add roughly 50 to 150
MtCO2e, about 1 to 2 per cent of the lifecycle total. All figures are conservative in this respect.

**Abandoned well methane is not counted.** Measured diffusive flux from abandoned shale wells
reaches 20,000 cubic metres per well per day. The buildout requires 12,558 to 32,000 new wells, all
of which are eventually abandoned.

**The methane share of upstream emissions is assumed.** British Columbia does not publish the
carbon dioxide and methane split separately. The 30 per cent figure is tested across 20 to 40 per
cent, but it is an assumption rather than a derivation.

**Two projects rest on weak capacity figures.** Baie-Comeau's 10 mtpa is a figure the company gave
journalists, with no project description filed. Summit Lake's 2.7 mtpa is an upper bound from an
assessment the proponent asked to suspend. Both are identified by tier and can be removed from any
total.

**Discovery LNG is the least verified asset in the register.** It was moved from inactive to
early_proposed pending verification. Capacity is Global Energy Monitor's 20 mtpa nameplate. No
current filing or proponent activity was located in a review of news and regulatory sources in
August 2026, and this classification should be revisited.

**Fermeuse's 5.0 mtpa is derived, not published.** The proponent has not stated a liquefaction
capacity. The figure is the lowest defensible derivation from the stated 9.7 Tcf Jeanne d'Arc
reserve over a 40-year life.

**Tilbury Phase 2's classification is a judgement.** FortisBC describes the expansion as serving
Lower Mainland resilience and marine fuelling; NRCan lists it as an export project. This analysis
places it on the bunkering chain and records the disagreement rather than resolving it.

**Capacity is never summed across chains.** Export and bunkering capacity is liquefaction; import
capacity is regasification. They measure opposite operations.

**Annual figures come in two forms.** The headline of 259.2 MtCO2e a year is averaged across each
facility's operating life. Time-series figures show actual annual values, which peak higher at
approximately 295 MtCO2e. Both are stated wherever used.

---

## Reproducing a run

```bash
python build_results.py
```

Reads both workbooks from `Inputs/`, runs all five scenarios, and writes the results workbook, the
summary and the figures to `Outputs/`. The inputs are opened read-only and the run asserts they are
unmodified on completion.

To change an assumption, edit the input workbooks rather than the code. The model has no
hardcoded emission factors, capacities or parameters.

---

## Principal data sources

**Infrastructure**
Global Energy Monitor, Global Gas Infrastructure Tracker: LNG Terminals (September 2025) and Gas
Pipelines (November 2025); Global Oil and Gas Extraction Tracker (March 2026).

**Government and regulatory**
Canada Energy Regulator: provincial and territorial energy profiles, export licence applications,
Canada's Energy Future. Environment and Climate Change Canada: National Inventory Report. Natural
Resources Canada: Canadian LNG projects. British Columbia Environmental Assessment Office:
Coastal GasLink and LNG Canada assessments.

**Peer-reviewed literature**
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
