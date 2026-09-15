"""Deck-facing Excel tables. Regenerated every run. Send SLIDE_TABLES.xlsx."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.inputs import DEFAULT_SCENARIO, INTENSITY_SCENARIOS, get_param
from src.model import CHAINS, GROUPS, carbon_budget_shares, electrification_counterfactual
from src.lca_comparison import build_lca_comparison
from src.scope import headline_sample
from src.trajectories import (
    annual_series,
    canada_pathway_series,
    cumulative_case_series,
    panel_gas_totals,
    panel_lifetime_mt,
    panel_n_emitting,
    panel_peak,
)

KEY_YEARS = (2025, 2028, 2030, 2035, 2040, 2050)


def _r1(val) -> float:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return val
    return round(float(val), 1)


def _r2(val) -> float:
    return round(float(val), 2)


def build_slide_tables(
    inputs: dict,
    by_project: pd.DataFrame,
    summary: pd.DataFrame,
    by_chain: pd.DataFrame,
    stages: pd.DataFrame,
    panel: pd.DataFrame,
    ld: dict | None = None,
    mc: dict | None = None,
) -> dict[str, pd.DataFrame]:
    sample = headline_sample(by_project, DEFAULT_SCENARIO)
    params = inputs["params"]
    national = float(get_param(params, "canada_national_emissions"))
    t_low = float(get_param(params, "canada_2030_target_low"))
    t_high = float(get_param(params, "canada_2030_target_high"))
    gap = float(get_param(params, "canada_2030_overshoot_gap"))
    sdef = summary.loc[summary["scenario"] == DEFAULT_SCENARIO]
    cdef = by_chain.loc[by_chain["scenario"] == DEFAULT_SCENARIO]
    cf = electrification_counterfactual(inputs, by_project)
    head = cf["summary"].loc[cf["summary"]["slice"] == "headline"].iloc[0]

    annual = float(sample["annual_total"].sum()) / 1e6
    lifecycle = panel_lifetime_mt(panel, DEFAULT_SCENARIO)
    peak_year, peak_mt = panel_peak(panel, DEFAULT_SCENARIO)
    peak_n = panel_n_emitting(panel, peak_year, DEFAULT_SCENARIO)
    s12 = float(sample["scope_1_2"].sum()) / 1e6
    s3 = float(sample["scope_3"].sum()) / 1e6
    can = float(sample["canada_territorial"].sum()) / 1e6
    bunk = float(sample["international_bunkers"].sum()) / 1e6
    foreign = float(sample["foreign_territorial"].sum()) / 1e6
    export_cap = float(sample.loc[sample["chain"] == "export", "capacity_mtpa"].sum())

    tables: dict[str, pd.DataFrame] = {}

    tables["00_Index"] = pd.DataFrame(
        [
            ("01_Headline", "Panel-peak annual (headline) plus life_average_annual_mt", "MtCO2e/yr, mtpa, Mt"),
            ("02_Scope_territory", "Scope 1+2 vs 3 and CAN / BUNK / FOR split", "MtCO2e/yr and %"),
            ("03_By_group", "Operating / under construction / proposed", "mtpa and MtCO2e"),
            ("04_Capacity_by_chain", "Capacity within each group, never summed across chains", "mtpa"),
            ("05_Advanced_vs_early", "Proposed tier split by chain", "mtpa and MtCO2e"),
            ("06_By_chain", "Export, bunkering, domestic, import", "mtpa and MtCO2e"),
            ("07_By_project", "Every in-scope project, one row", "mtpa and MtCO2e"),
            ("08_By_stage", "Lifecycle stage breakdown", "MtCO2e/yr and %"),
            ("09_Scenarios", "Five upstream scenarios", "MtCO2e"),
            ("10_Canada_context", "CAN LNG vs inventory, 2030 target, overshoot gap", "% and Mt"),
            ("11_Electrification", "Appendix: gas vs electric, Canada territorial", "MtCO2e/yr"),
            ("12_Elec_by_group", "Appendix electrification by calc_group", "MtCO2e/yr"),
            ("13_Trajectories", "Calendar-year totals at key years (fig 3)", "MtCO2e/yr"),
            ("14_CAN_trajectories", "Canada-territorial LNG vs pathway; gas vs electric", "MtCO2e/yr"),
            ("15_Oil_comparison", "Lifecycle Gt vs TMX and Alberta–BC bitumen (fig 7)", "GtCO2e"),
            ("16_Notes", "Units, scenario, what not to sum", "—"),
            ("17_Loss_damage", "Global L&D, ECCC central + Burke upper bracket", "2025 CAD tn"),
            ("18_Carbon_budget", "Lifetime CO2e vs GCB 2025 remaining CO2 budgets", "% of GtCO2"),
            ("19_LCA_comparison", "This model vs published LNG LCAs on aligned boundaries", "tCO2e/t"),
            ("19_LCA_excluded", "Named sources that are not LNG LCAs", "—"),
            ("20_Central_vs_MC", "Central-case point estimate vs Monte Carlo median (full build-out)", "Mt and CAD bn"),
        ],
        columns=["sheet", "contents", "units"],
    )

    tables["01_Headline"] = pd.DataFrame(
        [
            (
                "Annual emissions (panel peak)",
                _r1(peak_mt),
                "MtCO2e/yr",
                f"Calendar year {peak_year}; {peak_n} assets emitting",
            ),
            (
                "life_average_annual_mt",
                _r1(annual),
                "MtCO2e/yr",
                "Life-average util over each asset window; not a calendar year",
            ),
            ("Lifecycle emissions", _r1(lifecycle), "MtCO2e", "Central case: calendar-panel sum; export-chain headline scope. Not the Monte Carlo median."),
            ("Export capacity", _r1(export_cap), "mtpa", "Export chain only; liquefaction nameplate"),
            ("Canada territorial", _r1(can), "MtCO2e/yr", "Stages tagged CAN (life-average)"),
            ("International bunkers", _r1(bunk), "MtCO2e/yr", "UNFCCC bunkers, no country (life-average)"),
            ("Foreign territorial", _r1(foreign), "MtCO2e/yr", "Importing-country inventory (life-average)"),
            ("Scope 1 and 2", _r1(s12), "MtCO2e/yr", "Upstream, pipeline, liquefaction (life-average)"),
            ("Scope 3", _r1(s3), "MtCO2e/yr", "Shipping, regasification, combustion (life-average)"),
            ("Scenario", DEFAULT_SCENARIO, "—", "Default headline scenario"),
        ],
        columns=["item", "value", "unit", "note"],
    )

    tables["02_Scope_territory"] = pd.DataFrame(
        [
            ("Scope 1+2", _r1(s12), _r1(100 * s12 / annual)),
            ("Scope 3", _r1(s3), _r1(100 * s3 / annual)),
            ("Canada territorial (CAN)", _r1(can), _r1(100 * can / annual)),
            ("International bunkers (BUNK)", _r1(bunk), _r1(100 * bunk / annual)),
            ("Foreign territorial (FOR)", _r1(foreign), _r1(100 * foreign / annual)),
            ("Total", _r1(annual), 100.0),
        ],
        columns=["slice", "MtCO2e_yr", "share_pct"],
    )

    group_rows = []
    for g in GROUPS:
        r = sdef.loc[sdef["group"] == g].iloc[0]
        group_rows.append(
            {
                "calc_group": g,
                "export_mtpa": _r1(r["capacity_export_headline_mtpa"]),
                "life_average_annual_mt": _r1(r["annual_total_mtco2e_yr"]),
                "lifecycle_MtCO2e": _r1(r["lifecycle_total_mtco2e"]),
                "CAN_MtCO2e_yr": _r1(r["canada_territorial_mtco2e_yr"]),
                "BUNK_MtCO2e_yr": _r1(r["international_bunkers_mtco2e_yr"]),
                "FOR_MtCO2e_yr": _r1(r["foreign_territorial_mtco2e_yr"]),
                "scope_1_2_MtCO2e_yr": _r1(r["scope_1_2_mtco2e_yr"]),
                "scope_3_MtCO2e_yr": _r1(r["scope_3_mtco2e_yr"]),
            }
        )
    group_rows.append(
        {
            "calc_group": "TOTAL",
            "export_mtpa": _r1(export_cap),
            "life_average_annual_mt": _r1(annual),
            "lifecycle_MtCO2e": _r1(lifecycle),
            "CAN_MtCO2e_yr": _r1(can),
            "BUNK_MtCO2e_yr": _r1(bunk),
            "FOR_MtCO2e_yr": _r1(foreign),
            "scope_1_2_MtCO2e_yr": _r1(s12),
            "scope_3_MtCO2e_yr": _r1(s3),
        }
    )
    tables["03_By_group"] = pd.DataFrame(group_rows)

    cap_rows = []
    for g in GROUPS:
        r = sdef.loc[sdef["group"] == g].iloc[0]
        cap_rows.append(
            {
                "calc_group": g,
                "export_mtpa": _r1(r["capacity_export_mtpa"]),
                "bunkering_mtpa": _r1(r["capacity_bunkering_mtpa"]),
                "domestic_mtpa": _r1(r["capacity_domestic_mtpa"]),
                "import_mtpa": _r1(r["capacity_import_mtpa"]),
            }
        )
    tables["04_Capacity_by_chain"] = pd.DataFrame(cap_rows)

    prop = sample.loc[sample["calc_group"] == "proposed"]
    adv_early = []
    for tier in ("advanced_proposed", "early_proposed"):
        g = prop.loc[prop["tier"] == tier]
        for chain in CHAINS:
            gc = g.loc[g["chain"] == chain]
            if not len(gc):
                continue
            adv_early.append(
                {
                    "tier": tier,
                    "chain": chain,
                    "mtpa": _r1(gc["capacity_mtpa"].sum()),
                    "life_average_annual_mt": _r1(gc["annual_total"].sum() / 1e6),
                    "CAN_MtCO2e_yr": _r1(gc["canada_territorial"].sum() / 1e6),
                    "BUNK_MtCO2e_yr": _r1(gc["international_bunkers"].sum() / 1e6),
                    "FOR_MtCO2e_yr": _r1(gc["foreign_territorial"].sum() / 1e6),
                }
            )
    tables["05_Advanced_vs_early"] = pd.DataFrame(adv_early)

    chain_rows = []
    for chain in CHAINS:
        r = cdef.loc[cdef["chain"] == chain].iloc[0]
        stages_s = " > ".join(f"{s}@{w}" for s, w in inputs["chains"][chain])
        chain_rows.append(
            {
                "chain": chain,
                "stages": stages_s,
                "mtpa": _r1(r["capacity_mtpa"]),
                "life_average_annual_mt": _r1(r["annual_total_mtco2e_yr"]),
                "lifecycle_MtCO2e": _r1(r["lifecycle_total_mtco2e"]),
                "CAN_MtCO2e_yr": _r1(r["canada_territorial_mtco2e_yr"]),
                "BUNK_MtCO2e_yr": _r1(r["international_bunkers_mtco2e_yr"]),
                "FOR_MtCO2e_yr": _r1(r["foreign_territorial_mtco2e_yr"]),
            }
        )
    tables["06_By_chain"] = pd.DataFrame(chain_rows)

    proj = []
    for _, r in sample.sort_values(["calc_group", "chain", "project_name"]).iterrows():
        life_tot = r.get("panel_lifetime_mtco2e")
        proj.append(
            {
                "project_id": r["project_id"],
                "project_name": r["project_name"],
                "mtpa": _r1(r["capacity_mtpa"]),
                "chain": r["chain"],
                "calc_group": r["calc_group"],
                "tier": r["tier"],
                "drive": (
                    r["liquefaction_drive"] if pd.notna(r["liquefaction_drive"]) else "—"
                ),
                "life_years": int(r["lifespan_years"]),
                "effective_Mt_LNG_yr": _r2(r["effective_tonnes"] / 1e6),
                "life_average_annual_mt": _r1(r["annual_total"] / 1e6),
                "lifecycle_MtCO2e": (
                    "—" if r["is_legacy"] or pd.isna(life_tot) else _r1(life_tot)
                ),
                "CAN_MtCO2e_yr": _r1(r["canada_territorial"] / 1e6),
                "BUNK_MtCO2e_yr": _r1(r["international_bunkers"] / 1e6),
                "FOR_MtCO2e_yr": _r1(r["foreign_territorial"] / 1e6),
                "legacy": bool(r["is_legacy"]),
            }
        )
    tables["07_By_project"] = pd.DataFrame(proj)

    stage_rows = []
    for _, r in stages.iterrows():
        stage_rows.append(
            {
                "stage": r["stage"],
                "territorial_destination": r["territorial_destination"],
                "life_average_annual_mt": _r1(r["annual_mtco2e_yr"]),
                "share_pct": _r1(100 * r["share_of_total"] if r["share_of_total"] else 0),
            }
        )
    tables["08_By_stage"] = pd.DataFrame(stage_rows)

    scen_rows = []
    for scen in INTENSITY_SCENARIOS:
        s = headline_sample(by_project, scen)
        life = panel_lifetime_mt(panel, scen)
        scen_rows.append(
            {
                "scenario": scen,
                "upstream_tCO2e_per_t": inputs["upstream_by_scenario"][scen],
                "life_average_annual_mt": _r1(s["annual_total"].sum() / 1e6),
                "lifecycle_MtCO2e": _r1(life),
                "CAN_MtCO2e_yr": _r1(s["canada_territorial"].sum() / 1e6),
            }
        )
    tables["09_Scenarios"] = pd.DataFrame(scen_rows)

    tables["10_Canada_context"] = pd.DataFrame(
        [
            ("Canada territorial LNG", _r1(can), "MtCO2e/yr"),
            ("National inventory 2023 (ex LULUCF)", _r1(national), "MtCO2e"),
            ("Share of national inventory", _r1(100 * can / national), "%"),
            ("2030 target low", _r1(t_low), "MtCO2e"),
            ("2030 target high", _r1(t_high), "MtCO2e"),
            ("Share of 2030 target low", _r1(100 * can / t_low), "%"),
            ("Share of 2030 target high", _r1(100 * can / t_high), "%"),
            ("2030 overshoot gap", _r1(gap), "MtCO2e"),
            ("Share of 2030 overshoot gap", _r1(100 * can / gap), "%"),
        ],
        columns=["item", "value", "unit"],
    )

    lifetime_co2_only = panel_gas_totals(panel, DEFAULT_SCENARIO)[
        "lifetime_co2_only_mt"
    ]
    budgets = carbon_budget_shares(lifecycle, inputs["params"], lifetime_co2_only)
    budget_rows = []
    for r in budgets.itertuples():
        budget_rows.append(
            {
                "item": f"Share of {r.label} budget",
                "value": _r1(r.share_pct),
                "unit": "%",
                "budget_GtCO2": r.budget_gtco2,
                "lifetime_GtCO2_co2_only": round(r.lifetime_gtco2, 2),
                "lifetime_GtCO2e": round(r.lifetime_gtco2e, 2),
                "share_on_co2e_basis_pct": _r1(r.share_co2e_pct),
                "note": r.units_note,
            }
        )
    tables["18_Carbon_budget"] = pd.DataFrame(budget_rows)

    lca = build_lca_comparison(inputs)
    inc = lca["included"].copy()
    inc["total_tCO2e_per_t"] = inc.apply(
        lambda r: (
            f"{r['total_central']:.2f}"
            if pd.notna(r["total_central"])
            and abs(float(r["total_low"]) - float(r["total_high"])) < 1e-9
            else (
                f"{r['total_low']:.2f}–{r['total_high']:.2f}"
                + (
                    f" (expected {r['total_central']:.2f})"
                    if pd.notna(r["total_central"])
                    else ""
                )
            )
        ),
        axis=1,
    )
    tables["19_LCA_comparison"] = inc[
        [
            "study",
            "year",
            "geography",
            "system_boundary",
            "combustion_included",
            "shipping_included",
            "gwp",
            "total_tCO2e_per_t",
            "alignment_note",
        ]
    ]
    tables["19_LCA_excluded"] = lca["excluded"]

    if mc is not None and ld is not None:
        summ = mc["summary"]

        def _mc_row(metric: str) -> pd.Series:
            return summ.loc[
                (summ["build_out"] == "full") & (summ["metric"] == metric)
            ].iloc[0]

        h = ld["headline"].set_index("case")
        damage = float(h.loc["published_central", "total_cad_billion"])
        damage_npv = float(h.loc["eccc_central_npv_2025", "total_cad_billion"])
        life = _mc_row("lifetime_mtco2e")
        peak = _mc_row("peak_mtco2e_yr")
        dmg = _mc_row("central_damage_cad_billion")
        tables["20_Central_vs_MC"] = pd.DataFrame(
            [
                {
                    "quantity": "Lifetime",
                    "central_case": _r1(lifecycle),
                    "mc_median": _r1(life["median"]),
                    "mc_p05": _r1(life["p05"]),
                    "mc_p95": _r1(life["p95"]),
                    "unit": "MtCO2e",
                    "note": "Central case is the point estimate from central factors.",
                },
                {
                    "quantity": "Peak-year emissions",
                    "central_case": _r1(peak_mt),
                    "mc_median": _r1(peak["median"]),
                    "mc_p05": _r1(peak["p05"]),
                    "mc_p95": _r1(peak["p95"]),
                    "unit": "MtCO2e/yr",
                    "note": f"Central peak year {peak_year}.",
                },
                {
                    "quantity": "ECCC 2% damage",
                    "central_case": round(damage, 0),
                    "mc_median": round(float(dmg["median"]), 0),
                    "mc_p05": round(float(dmg["p05"]), 0),
                    "mc_p95": round(float(dmg["p95"]), 0),
                    "unit": "CAD bn 2025",
                    "note": "Calendar-year ECCC 2%: damage valued when caused (loss-and-damage figure).",
                },
                {
                    "quantity": "ECCC 2% damage, NPV to 2025",
                    "central_case": round(damage_npv, 0),
                    "mc_median": None,
                    "mc_p05": None,
                    "mc_p95": None,
                    "unit": "CAD bn 2025",
                    "note": "Same stream discounted to 2025 at 2% (cost-benefit figure). Carried with the central, not a sensitivity on it.",
                },
            ]
        )

    elec = float(cf["electric_intensity"])
    gas = float(head["canada_territorial_gas_mtco2e_yr"])
    claimed = float(head["canada_territorial_claimed_electric_mtco2e_yr"])
    alle = float(head["canada_territorial_all_electric_mtco2e_yr"])
    tables["11_Electrification"] = pd.DataFrame(
        [
            {
                "case": "Gas turbine (current headline)",
                "CAN_MtCO2e_yr": _r1(gas),
                "vs_gas_MtCO2e_yr": 0.0,
                "share_of_inventory_pct": _r1(100 * gas / national),
                "share_of_2030_target_low_pct": _r1(100 * gas / t_low),
                "note": "Liquefaction 0.29 tCO2e/t every terminal",
            },
            {
                "case": "Claimed electric delivered",
                "CAN_MtCO2e_yr": _r1(claimed),
                "vs_gas_MtCO2e_yr": _r1(claimed - gas),
                "share_of_inventory_pct": _r1(100 * claimed / national),
                "share_of_2030_target_low_pct": _r1(100 * claimed / t_low),
                "note": f"{elec:g} only for previously electric_committed/planned: "
                + ", ".join(cf["claimed_project_ids"]),
            },
            {
                "case": "All terminals electric",
                "CAN_MtCO2e_yr": _r1(alle),
                "vs_gas_MtCO2e_yr": _r1(alle - gas),
                "share_of_inventory_pct": _r1(100 * alle / national),
                "share_of_2030_target_low_pct": _r1(100 * alle / t_low),
                "note": f"Liquefaction {elec:g} tCO2e/t on every chain that includes it",
            },
        ]
    )

    elec_g = []
    for g in GROUPS:
        r = cf["summary"].loc[cf["summary"]["slice"] == g].iloc[0]
        elec_g.append(
            {
                "calc_group": g,
                "gas_CAN_MtCO2e_yr": _r1(r["canada_territorial_gas_mtco2e_yr"]),
                "claimed_electric_CAN_MtCO2e_yr": _r1(
                    r["canada_territorial_claimed_electric_mtco2e_yr"]
                ),
                "all_electric_CAN_MtCO2e_yr": _r1(
                    r["canada_territorial_all_electric_mtco2e_yr"]
                ),
            }
        )
    tables["12_Elec_by_group"] = pd.DataFrame(elec_g)

    traj = cumulative_case_series(inputs, DEFAULT_SCENARIO, canada_only=False)
    traj_rows = []
    for y in KEY_YEARS:
        row = traj.loc[traj["year"] == y].iloc[0]
        traj_rows.append(
            {
                "year": int(y),
                "operating_MtCO2e_yr": _r1(row["operating"]),
                "plus_under_construction_MtCO2e_yr": _r1(row["plus_under_construction"]),
                "all_calc_groups_MtCO2e_yr": _r1(row["plus_proposed"]),
            }
        )
    peak = float(traj["plus_proposed"].max())
    peak_year = int(traj.loc[traj["plus_proposed"].idxmax(), "year"])
    traj_rows.append(
        {
            "year": f"peak ({peak_year})",
            "operating_MtCO2e_yr": _r1(traj["operating"].max()),
            "plus_under_construction_MtCO2e_yr": _r1(
                traj["plus_under_construction"].max()
            ),
            "all_calc_groups_MtCO2e_yr": _r1(peak),
        }
    )
    tables["13_Trajectories"] = pd.DataFrame(traj_rows)

    pathway = canada_pathway_series(inputs["params"])
    gas_s = annual_series(
        inputs, DEFAULT_SCENARIO, calc_groups=GROUPS, canada_only=True, liquefaction_mode="gas"
    )
    claimed_s = annual_series(
        inputs,
        DEFAULT_SCENARIO,
        calc_groups=GROUPS,
        canada_only=True,
        liquefaction_mode="claimed_electric",
    )
    elec_s = annual_series(
        inputs,
        DEFAULT_SCENARIO,
        calc_groups=GROUPS,
        canada_only=True,
        liquefaction_mode="all_electric",
    )
    can_rows = []
    for y in KEY_YEARS:
        pw = float(pathway.loc[pathway["year"] == y, "canada_pathway_mtco2e_yr"].iloc[0])
        g = float(gas_s.loc[gas_s["year"] == y, "annual_mtco2e_yr"].iloc[0])
        c = float(claimed_s.loc[claimed_s["year"] == y, "annual_mtco2e_yr"].iloc[0])
        e = float(elec_s.loc[elec_s["year"] == y, "annual_mtco2e_yr"].iloc[0])
        can_rows.append(
            {
                "year": int(y),
                "canada_pathway_MtCO2e_yr": _r1(pw),
                "CAN_LNG_gas_MtCO2e_yr": _r1(g),
                "CAN_LNG_claimed_electric_MtCO2e_yr": _r1(c),
                "CAN_LNG_all_electric_MtCO2e_yr": _r1(e),
            }
        )
    tables["14_CAN_trajectories"] = pd.DataFrame(can_rows)

    tables["16_Notes"] = pd.DataFrame(
        [
            ("scenario", DEFAULT_SCENARIO),
            ("run_at_utc", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")),
            (
                "headline_scope",
                "Headline is chain in headline_scope_chains and calc_group in "
                "headline_scope_calc_groups (export / operating, under construction, "
                "proposed). Non-export assets stay in the register as a stated exclusion.",
            ),
            (
                "annual_basis",
                "Headline annual is the panel peak calendar year. "
                "life_average_annual_mt is utilisation-weighted over each asset window. "
                "Trajectory sheets are calendar years.",
            ),
            (
                "capacity_rule",
                "Never sum export + bunkering + import. Export is liquefaction; import is regasification.",
            ),
            (
                "electrification",
                "Headline assumes gas turbine 0.29 for every terminal. 11 and 12 are appendix only.",
            ),
            (
                "oil_comparator",
                "RETIRED 3 September 2026. The Trans Mountain comparison was "
                "dropped from the deck, so figure 7, slide table 15 and the "
                "tmx_oil_* parameters were removed from the model rather than "
                "left generating an unpublished figure on unsourced addends.",
            ),
            ("rounding", "One decimal throughout."),
            (
                "carbon_budget_units",
                "GCB 2025 remaining budgets are CO2; lifetime totals are GWP100 CO2e. "
                "Sheet 18 compares CO2e to a CO2 budget (approximation).",
            ),
            (
                "send_this_file",
                "Outputs/SLIDE_TABLES.xlsx — one table per sheet, for the PPT Claude chat.",
            ),
            (
                "central_vs_mc",
                "Central case (sheet 01, 20) is the point estimate from central factor values. "
                "Monte Carlo median (sheet 20) is higher because the stage triangles are "
                "right-skewed (shipping 0.05/0.12/0.31). They are different quantities. "
                "Paper reports the central case with the MC p5-p95 as its "
                "interval (decision of 29 August 2026); the MC median is "
                "stated once, with the skew as the reason.",
            ),
        ],
        columns=["item", "value"],
    )

    if ld is not None:
        egrid = ld["eccc_grid"].set_index("discount_rate_pct")
        published = ld["published"]
        hz = ld["horizon_table"].set_index(["horizon", "discounting"])
        b2300 = hz.loc[("through_2300", "2pct_fixed")]
        b2100 = hz.loc[("through_2100", "2pct_fixed")]
        tables["17_Loss_damage"] = pd.DataFrame(
            [
                (
                    "Central, ECCC 2% calendar year (damage valued when caused)",
                    round(float(published["total_cad_billion"]) / 1000, 2),
                    "trillion 2025 CAD",
                    "CO2 x SC-CO2 + CH4 mass x SC-CH4, per calendar year; the loss-and-damage figure",
                ),
                (
                    "Central, ECCC 2% NPV to 2025 (cost-benefit framing)",
                    round(float(ld["headline"].set_index("case").loc["eccc_central_npv_2025", "total_cad_billion"]) / 1000, 2),
                    "trillion 2025 CAD",
                    "Same stream discounted to 2025 at 2%; carried with the central, not a sensitivity on it",
                ),
                (
                    "Methane share of CO2e total",
                    round(100 * float(ld["methane_share_of_co2e"]), 1),
                    "%",
                    "Upstream excess over inventory CO2 plus shipping methane slip",
                ),
                (
                    "Methane share of the damage bill",
                    round(100 * float(ld["eccc_ch4_damage_share"]), 1),
                    "% of damage bill",
                    "CH4 mass priced at ECCC SC-CH4",
                ),
                (
                    "Retired treatment (whole CO2e at SC-CO2)",
                    round(float(ld["old_treatment_cad"]) / 1e12, 2),
                    "trillion 2025 CAD",
                    "Reconciliation only: "
                    f"{100*float(ld['old_treatment_delta_pct']):+.1f}% vs per-gas",
                ),
                (
                    "ECCC 1.5% calendar year",
                    round(float(egrid.loc[1.5, "calendar_year_total_cad_billion"]) / 1000, 2),
                    "trillion 2025 CAD",
                    "Central-case sensitivity (higher damages)",
                ),
                (
                    "ECCC 2.5% calendar year",
                    round(float(egrid.loc[2.5, "calendar_year_total_cad_billion"]) / 1000, 2),
                    "trillion 2025 CAD",
                    "Central-case sensitivity (lower damages)",
                ),
                (
                    "Proposed only, ECCC 2%",
                    round(float(published["proposed_cad_billion"]) / 1000, 2),
                    "trillion 2025 CAD",
                    "Same central price, proposed slate",
                ),
                (
                    "Burke through-2300 2% g=0 (upper bracket)",
                    round(float(b2300["total_cad_billion"]) / 1000, 1),
                    "trillion 2025 CAD",
                    "Figure 2e; not the paper central",
                ),
                (
                    "Burke through-2100 2% g=0",
                    round(float(b2100["total_cad_billion"]) / 1000, 1),
                    "trillion 2025 CAD",
                    "Hatton-comparable horizon",
                ),
                (
                    "Canadian value, proposed",
                    round(float(b2300["canada_value_proposed_cad_billion"]), 0),
                    "billion 2025 CAD",
                    "CBoC Table 1 $11.153bn/yr (2020 CAD) at 56 mtpa, scaled, 40 yr, inflated",
                ),
                (
                    "Canada Burke-channel share (FD)",
                    round(100 * float(b2300["canada_share_fd"]), 2),
                    "%",
                    "1990 1 Gt pulse, 2021-2100; UK HD validates at 1.61%",
                ),
                (
                    "Canada 1990-2020 emitter total (Fig 4)",
                    round(ld["fig4"]["canada_owing_usd"] / 1e12, 2),
                    "trillion 2020 USD",
                    "All Canadian emissions, not LNG; Canada absent from recipient panel",
                ),
            ],
            columns=["item", "value", "unit", "note"],
        )

    return tables


FIGURE_SHEET_NAMES = {
    "fig01_stage_breakdown.csv": "fig01_stage",
    "fig02_territorial_split.csv": "fig02_territory",
    "fig03_three_trajectories.csv": "fig03_trajectories",
    "fig04_pathway_vs_territorial_lng.csv": "fig04_pathway_CAN",
    "fig05_pathway_three_upstream.csv": "fig05_pathway_scenarios",
    "fig06_pathway_vs_total_lng.csv": "fig06_pathway_total",
    "fig08_electrification_can_average.csv": "fig08_elec_average",
    "fig08_electrification_can_by_group.csv": "fig08_elec_by_group",
    "fig08_electrification_can_trajectories.csv": "fig08_elec_traj",
    "fig09_loss_damage_by_group.csv": "fig09_loss_damage",
    "ld_headline.csv": "ld_headline",
    "ld_burke_grid.csv": "ld_burke_grid",
    "ld_eccc_grid.csv": "ld_eccc_grid",
    "ld_price_by_year.csv": "ld_price_by_year",
    "placeholder_start_sensitivity.csv": "placeholder_start_sens",
    "placeholder_start_by_asset.csv": "placeholder_start_assets",
    "mc_summary.csv": "mc_summary",
    "mc_howarth_sensitivity.csv": "mc_howarth",
    "mc_parameters.csv": "mc_parameters",
    "fig10_lca_comparison.csv": "fig10_lca",
    "fig10_lca_excluded.csv": "fig10_lca_excluded",
}


def write_slide_tables_xlsx(
    tables: dict[str, pd.DataFrame],
    path: Path,
    figure_data_dir: Path | None = None,
) -> None:
    """Write the send-to-PPT workbook. Optionally attach figure CSV series."""
    out = dict(tables)
    if figure_data_dir and figure_data_dir.exists():
        extra_index = []
        for csv_path in sorted(figure_data_dir.glob("*.csv")):
            sheet = FIGURE_SHEET_NAMES.get(csv_path.name, csv_path.stem[:31])
            out[sheet] = pd.read_csv(csv_path)
            extra_index.append(
                (sheet, f"Chart series from {csv_path.name}", "as in figure")
            )
        if extra_index and "00_Index" in out:
            extra = pd.DataFrame(extra_index, columns=["sheet", "contents", "units"])
            out["00_Index"] = pd.concat([out["00_Index"], extra], ignore_index=True)

    path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for name, df in out.items():
            df.to_excel(writer, sheet_name=name[:31], index=False)
    print(f"Wrote slide tables: {path}")
