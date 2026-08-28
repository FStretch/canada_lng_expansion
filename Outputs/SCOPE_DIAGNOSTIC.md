# Task A diagnostic: legacy and non-export assets

Diagnostic only. No scope change and no emission-factor change. Liquefaction remains 0.29.

## A1. Peak and lifetime use the same asset set

**They do.** The 309.1 Mt peak (2037) and the 9,558.2 Mt lifetime are both sums of the calendar panel. `build_emissions_panel` omits legacy assets (`if _is_legacy: continue`). `panel_peak` and `panel_lifetime_mt` then sum that same frame.

| Asset | Chain | In 268.1 life-average? | In 9,558.2 lifetime? | In 309.1 peak (2037)? |
|---|---|---|---|---|
| `tilbury_original` (1971, 0.03 mtpa) | domestic | **yes** (0.086 Mt/yr) | **no** | **no** |
| `energir_montreal_lng` (1976, 0.21 mtpa) | domestic | **yes** (0.604 Mt/yr) | **no** | **no** |

Peak-year membership equals lifetime membership: 16 assets. Empty symmetric difference.

The 18 in-total `by_project` rows (Hamilton already excluded for missing capacity) include the two legacy plants. Those two feed **only** `life_average_annual_mt` (0.69 Mt/yr combined, 0.26% of 268.1). They do not reopen the Task 1 peak-vs-lifetime reconciliation. Task 1 closed that by moving the headline annual onto the panel.

### Other special-case treatment

| Asset | Treatment | In peak? | In lifetime? |
|---|---|---|---|
| `port_of_hamilton_lng` | no capacity → `excluded_from_totals` | no | no |
| `saint_john_import_facility` | import chain; `saint_john_utilisation=0.025` (not nameplate) | yes (0.52 Mt) | yes (12.6 Mt, 0.13%) |
| `mt_hayes_lng`, `tamaska_fort_nelson_lng` | domestic operating, **not** legacy (starts 2011 / 2021) | yes | yes (4.5 + 1.7 Mt) |
| `tilbury_phase_1a/1b/2` | bunkering, not legacy | yes | yes (224.2 Mt, 2.3%) |

`_is_legacy` is first_export_year + lifespan < current year. It is not an export/domestic flag. Mt Hayes and Tamaska are domestic but in the panel.

## A2. Every in-total asset (measurement_central)

Lifetime and peak-year Mt are from the calendar panel. Legacy lifetime/peak are 0 because they are omitted from the panel. Shares are of 9,558.2 Mt.

| project_id | chain | calc_group | start | mtpa | lifetime Mt | peak 2037 Mt | share |
|---|---|---|---:|---:|---:|---:|---:|
| lng_canada_phase_1 | export | operating | 2025 | 14.0 | 1,309.6 | 42.2 | 13.7% |
| cedar_lng | export | under_construction | 2028 | 3.3 | 376.6 | 9.8 | 3.9% |
| woodfibre_lng | export | under_construction | 2028 | 2.1 | 183.3 | 6.3 | 1.9% |
| discovery_t1t4 | export | proposed | — | 20.0 | 2,043.9 | 59.6 | 21.4% |
| marinvest_baie_comeau | export | proposed | — | 15.0 | 1,532.9 | 44.7 | 16.0% |
| kanata_lng | export | proposed | — | 12.0 | 1,226.3 | 35.7 | 12.8% |
| ksi_lisims_lng | export | proposed | 2029 | 12.0 | 1,047.6 | 35.7 | 11.0% |
| lng_canada_phase_2 | export | proposed | 2030 | 14.0 | 888.6 | 41.7 | 9.3% |
| fermeuse_energy_flng | export | proposed | — | 5.0 | 511.0 | 14.9 | 5.3% |
| summit_lake_pg_lng | export | proposed | — | 2.7 | 195.5 | 8.0 | 2.0% |
| tilbury_phase_2 | bunkering | proposed | — | 2.5 | 137.3 | 7.1 | 1.4% |
| tilbury_phase_1b | bunkering | proposed | 2028 | 0.65 | 63.4 | 1.8 | 0.7% |
| tilbury_phase_1a | bunkering | operating | 2018 | 0.25 | 23.5 | 0.7 | 0.2% |
| saint_john_import_facility | import | operating | 2009 | 7.5 | 12.6 | 0.5 | 0.1% |
| mt_hayes_lng | domestic | operating | 2011 | 0.06 | 4.5 | 0.2 | 0.05% |
| tamaska_fort_nelson_lng | domestic | operating | 2021 | 0.02 | 1.7 | 0.05 | 0.02% |
| energir_montreal_lng | domestic | operating | 1976 | 0.21 | 0 | 0 | 0 |
| tilbury_original | domestic | operating | 1971 | 0.03 | 0 | 0 | 0 |

### By chain

| chain | n | mtpa | lifetime Mt | share of 9,558.2 | peak 2037 Mt |
|---|---:|---:|---:|---:|---:|
| **export** | **10** | **100.1** | **9,315.3** | **97.5%** | **298.7** |
| bunkering | 3 | 3.4 | 224.2 | 2.3% | 9.7 |
| import | 1 | 7.5 | 12.6 | 0.1% | 0.5 |
| domestic | 4 | 0.3 | 6.1 | 0.1% | 0.2 |
| **non-export** | **8** | **11.2** | **242.9** | **2.5%** | **10.4** |

Export-only peak year is still 2037 (298.7 Mt). Committed (operating + under construction) export lifetime is 1,869.5 Mt vs all-chain committed MC median 1,945.

## Implication for Task B

A1 does **not** block the export-scope decision. Peak and lifetime are already the same 16-asset panel. Narrowing to `chain == export` (all calc_groups) drops 242.9 Mt (2.5%) and 10.4 Mt from the peak year. Nothing unexpected in the sense of a hidden peak/lifetime mismatch. Bunkering is the material non-export piece (224.2 Mt), not the two 1970s plants.

No factor change. No scope change in this commit.
