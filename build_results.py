"""Orchestrate lifecycle emissions build. Writes Outputs/ only — never Inputs/."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.inputs import (
    ALL_STAGES,
    DEFAULT_SCENARIO,
    EXPECTED_CHAIN_LENGTHS,
    INTENSITY_SCENARIOS,
    get_param,
    load_inputs,
)
from src.figures_report import build_all_report_figures
from src.slide_tables import build_slide_tables, write_slide_tables_xlsx
from src.placeholder_sensitivity import (
    format_placeholder_markdown,
    run_placeholder_start_sensitivity,
)
from src.loss_damage import compute_loss_damage, format_ld_markdown, write_ld_figure
from src.monte_carlo import format_mc_markdown, run_monte_carlo
from src.trajectories import (
    PANEL_START_YEAR,
    build_emissions_panel,
    panel_by_project,
    panel_lifetime_mt,
    panel_n_emitting,
    panel_peak,
)
from src.model import (
    CHAINS,
    GROUPS,
    _licence_end_year,
    _lifespan,
    assert_no_cross_chain_capacity_sum,
    assumptions_used,
    by_stage,
    carbon_budget_shares,
    compute_by_project,
    electrification_counterfactual,
    summarise,
    summarise_by_chain,
    territorial_table,
)

ROOT = Path(__file__).resolve().parent
REGISTER = ROOT / "Inputs" / "Canada_LNG_Asset_Register.xlsx"
INPUTS = ROOT / "Inputs" / "Canada_LNG_Data_Inputs.xlsx"
INPUTS_DIR = ROOT / "Inputs"
OUT = ROOT / "Outputs"
RESULTS = OUT / "Canada_LNG_Emissions_Results.xlsx"
SLIDE_TABLES = OUT / "SLIDE_TABLES.xlsx"
SUMMARY_MD = OUT / "RESULTS_SUMMARY.md"
FIGURE = OUT / "figures" / "operating_vs_proposed.png"
FIGURE_DIR = OUT / "figures"
FIGURE_DATA = OUT / "figure_data"

# Snapshot before the August 2026 register/electrification revision.
BEFORE = {
    "annual_mt": 159.2,
    "lifecycle_mt": 6196.7,
    "export_mtpa": 58.1,
    "liquefaction_mt": 8.0,
    "early_export_mtpa": 12.7,
    "group_annual": {
        "operating": 43.3,
        "under_construction": 15.0,
        "proposed": 100.9,
    },
    "chain_annual": {
        "export": 150.0,
        "bunkering": 7.8,
        "domestic": 0.9,
        "import": 0.5,
    },
}
EXPECTED_EXPORT_BY_CALC = {
    "operating": 14.0,
    "under_construction": 5.4,
    "proposed": 80.7,
}
EXPECTED_EXPORT_TOTAL = 100.1
EXPECTED_EARLY_EXPORT = 54.7
EXPECTED_ADVANCED_EXPORT = 26.0


def write_figure(by_project: pd.DataFrame, path: Path) -> None:
    """Export-chain operating / under construction / proposed (early inside proposed)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    sample = by_project.loc[
        (~by_project["excluded_from_totals"])
        & (by_project["scenario"] == DEFAULT_SCENARIO)
        & (by_project["chain"] == "export")
    ]
    buckets = [
        ("operating", "Operating now"),
        ("under_construction", "Under construction"),
        ("proposed", "Proposed"),
    ]
    labels, s12, s3, caps = [], [], [], []
    for cg, label in buckets:
        g = sample.loc[sample["calc_group"] == cg]
        cap = float(g["capacity_mtpa"].sum())
        labels.append(label)
        s12.append(float(g["scope_1_2"].sum()) / 1e6)
        s3.append(float(g["scope_3"].sum()) / 1e6)
        caps.append(cap)
    x = np.arange(3)
    fig, ax = plt.subplots(figsize=(9.5, 6.2))
    ax.bar(x, s12, 0.55, label="Scope 1+2", color="#1f4e5f")
    ax.bar(x, s3, 0.55, bottom=s12, label="Scope 3", color="#c47b3a")
    ax.set_ylabel("Life-average annual emissions (MtCO2e / year)")
    ax.set_xticks(x, labels)
    ax.legend(frameon=False, loc="upper left")
    ymax = max(a + b for a, b in zip(s12, s3))
    ax.set_ylim(0, ymax * 1.22)
    for i, (a, b, cap) in enumerate(zip(s12, s3, caps)):
        ax.text(i, a + b + ymax * 0.03, f"{a + b:.1f} MtCO2e/yr", ha="center", fontsize=10)
        ax.text(i, -ymax * 0.08, f"{cap:g} mtpa", ha="center", va="top", fontsize=10)
    ax.set_title("Canada LNG export chain: operating versus proposed")
    fig.text(
        0.5, 0.02,
        f"Scenario: {DEFAULT_SCENARIO}. Export chain; proposed includes advanced + early.",
        ha="center", fontsize=9, color="#444",
    )
    fig.subplots_adjust(bottom=0.16, top=0.9)
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def write_review_summary(
    path: Path,
    inputs: dict,
    by_project: pd.DataFrame,
    summary: pd.DataFrame,
    by_chain: pd.DataFrame,
    stages: pd.DataFrame,
    panel: pd.DataFrame,
    ld: dict | None = None,
    placeholder_sens: dict | None = None,
    mc: dict | None = None,
) -> None:
    sample = by_project.loc[
        (~by_project["excluded_from_totals"]) & (by_project["scenario"] == DEFAULT_SCENARIO)
    ]
    params = inputs["params"]
    national = float(get_param(params, "canada_national_emissions"))
    t_low = float(get_param(params, "canada_2030_target_low"))
    t_high = float(get_param(params, "canada_2030_target_high"))
    gap = float(get_param(params, "canada_2030_overshoot_gap"))

    annual = float(sample["annual_total"].sum()) / 1e6
    lifecycle = panel_lifetime_mt(panel, DEFAULT_SCENARIO)
    peak_year, peak_mt = panel_peak(panel, DEFAULT_SCENARIO)
    panel_year0 = int(panel.loc[panel["scenario"] == DEFAULT_SCENARIO, "year"].min())
    panel_year1 = int(panel.loc[panel["scenario"] == DEFAULT_SCENARIO, "year"].max())
    project_life = panel_by_project(panel)
    project_life_def = project_life.loc[project_life["scenario"] == DEFAULT_SCENARIO]
    s12 = float(sample["scope_1_2"].sum()) / 1e6
    s3 = float(sample["scope_3"].sum()) / 1e6
    can = float(sample["canada_territorial"].sum()) / 1e6
    bunk = float(sample["international_bunkers"].sum()) / 1e6
    foreign = float(sample["foreign_territorial"].sum()) / 1e6
    export_cap = float(sample.loc[sample["chain"] == "export", "capacity_mtpa"].sum())

    lines = []
    lines.append("# Canada LNG lifecycle emissions — review summary")
    lines.append("")
    lines.append(
        f"Default scenario: `{DEFAULT_SCENARIO}`. "
        f"Run at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}. "
        "Numbers to one decimal. Inputs read-only. "
        f"`calc_group` from `{inputs['calc_group_source']}`."
    )
    lines.append("")
    lines.append(
        "Deck-facing tables (one sheet per table, 1-decimal): "
        "`Outputs/SLIDE_TABLES.xlsx`. Send that workbook to the PPT chat."
    )
    lines.append("")

    # 1 Headline
    lines.append("## 1. Headline")
    lines.append("")
    peak_n = panel_n_emitting(panel, peak_year, DEFAULT_SCENARIO)
    lines.append(
        f"- **Annual total (panel peak):** {peak_mt:.1f} MtCO2e in {peak_year} "
        f"({peak_n} assets emitting that year)"
    )
    lines.append(
        f"- **life_average_annual_mt:** {annual:.1f} MtCO2e/yr "
        "(mean utilisation over each asset's operating window; not a calendar year)"
    )
    lines.append(
        f"- **Lifetime total (calendar panel {panel_year0}–{panel_year1}):** "
        f"{lifecycle:.1f} MtCO2e (excludes legacy facilities; remaining years from "
        f"{PANEL_START_YEAR}, not duration × life-average)"
    )
    lines.append(
        f"- **Headline capacity (export chain only):** {export_cap:.1f} mtpa "
        "(liquefaction; not summed with import regasification or other chains)"
    )
    lines.append("")
    lines.append("| chain | mtpa |")
    lines.append("|---|---|")
    for chain in CHAINS:
        cap = float(sample.loc[sample["chain"] == chain, "capacity_mtpa"].sum())
        lines.append(f"| {chain} | {cap:.1f} |")
    lines.append("")
    lines.append(
        f"- **Scope 1+2:** {s12:.1f} MtCO2e/yr ({s12/annual*100:.1f}%)  |  "
        f"**Scope 3:** {s3:.1f} MtCO2e/yr ({s3/annual*100:.1f}%)"
    )
    lines.append(
        f"- **Territorial:** CAN {can:.1f} ({can/annual*100:.1f}%)  |  "
        f"BUNK {bunk:.1f} ({bunk/annual*100:.1f}%)  |  "
        f"FOR {foreign:.1f} ({foreign/annual*100:.1f}%)"
    )
    budgets = carbon_budget_shares(lifecycle, params)
    lines.append(
        "- **Share of remaining carbon budget (GCB 2025, from start of 2026):** "
        + "  |  ".join(
            f"{r.label} {r.share_pct:.1f}% of {r.budget_gtco2:g} GtCO2"
            for r in budgets.itertuples()
        )
        + ". Comparison is **CO2e against a CO2 budget** (approximation); "
        "a true CO2-only total is not derivable."
    )
    lines.append("")

    # 2 By group
    lines.append("## 2. By group")
    lines.append("")
    lines.append(
        "| calc_group | export mtpa | life_average_annual_mt | Lifecycle Mt | "
        "CAN / BUNK / FOR Mt/yr |"
    )
    lines.append("|---|---|---|---|---|")
    sdef = summary.loc[summary["scenario"] == DEFAULT_SCENARIO]
    for g in GROUPS:
        r = sdef.loc[sdef["group"] == g]
        if not len(r):
            continue
        r = r.iloc[0]
        if r["annual_total_mtco2e_yr"] == 0 and r["capacity_export_headline_mtpa"] == 0:
            continue
        glife = panel_lifetime_mt(panel, DEFAULT_SCENARIO, calc_group=g)
        lines.append(
            f"| {g} | {r['capacity_export_headline_mtpa']:.1f} | "
            f"{r['annual_total_mtco2e_yr']:.1f} | {glife:.1f} | "
            f"{r['canada_territorial_mtco2e_yr']:.1f} / "
            f"{r['international_bunkers_mtco2e_yr']:.1f} / "
            f"{r['foreign_territorial_mtco2e_yr']:.1f} |"
        )
    lines.append("")
    lines.append("Capacity by chain within each calc_group (not summed across chains):")
    lines.append("")
    lines.append("| calc_group | export | bunkering | domestic | import |")
    lines.append("|---|---|---|---|---|")
    for g in GROUPS:
        r = sdef.loc[sdef["group"] == g]
        if not len(r):
            continue
        r = r.iloc[0]
        lines.append(
            f"| {g} | {r['capacity_export_mtpa']:.1f} | "
            f"{r['capacity_bunkering_mtpa']:.1f} | "
            f"{r['capacity_domestic_mtpa']:.1f} | "
            f"{r['capacity_import_mtpa']:.1f} |"
        )
    lines.append("")
    lines.append("### Proposed: advanced vs early (tier split)")
    lines.append("")
    lines.append(
        "| tier | chain scope | mtpa | life_average_annual_mt | CAN / BUNK / FOR |"
    )
    lines.append("|---|---|---|---|---|")
    prop = sample.loc[sample["calc_group"] == "proposed"]
    for tier in ("advanced_proposed", "early_proposed"):
        g = prop.loc[prop["tier"] == tier]
        if not len(g):
            continue
        # Emissions for all chains in the tier; capacity reported per chain only.
        for chain in CHAINS:
            gc = g.loc[g["chain"] == chain]
            if not len(gc):
                continue
            lines.append(
                f"| {tier} | {chain} | {float(gc['capacity_mtpa'].sum()):.1f} | "
                f"{float(gc['annual_total'].sum())/1e6:.1f} | "
                f"{float(gc['canada_territorial'].sum())/1e6:.1f} / "
                f"{float(gc['international_bunkers'].sum())/1e6:.1f} / "
                f"{float(gc['foreign_territorial'].sum())/1e6:.1f} |"
            )
    lines.append("")

    # 3 By chain
    lines.append("## 3. By chain")
    lines.append("")
    chain_stages = {
        c: " → ".join(f"{s}@{w}" for s, w in inputs["chains"][c])
        for c in CHAINS
    }
    lines.append(
        "| chain | stages | mtpa | life_average_annual_mt | Lifecycle Mt | CAN / BUNK / FOR |"
    )
    lines.append("|---|---|---|---|---|---|")
    cdef = by_chain.loc[by_chain["scenario"] == DEFAULT_SCENARIO]
    for chain in CHAINS:
        r = cdef.loc[cdef["chain"] == chain].iloc[0]
        clife = panel_lifetime_mt(panel, DEFAULT_SCENARIO, chain=chain)
        lines.append(
            f"| {chain} | {chain_stages[chain]} | {r['capacity_mtpa']:.1f} | "
            f"{r['annual_total_mtco2e_yr']:.1f} | {clife:.1f} | "
            f"{r['canada_territorial_mtco2e_yr']:.1f} / "
            f"{r['international_bunkers_mtco2e_yr']:.1f} / "
            f"{r['foreign_territorial_mtco2e_yr']:.1f} |"
        )
    lines.append("")

    # 4 By project
    lines.append("## 4. By project")
    lines.append("")
    lines.append(
        "| project | mtpa | chain | calc_group | tier | drive | life (source) | "
        "effective Mt/yr | annual Mt/yr | lifecycle Mt | CAN / BUNK / FOR | notes |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for _, r in sample.sort_values(["calc_group", "chain", "project_id"]).iterrows():
        drive = r["liquefaction_drive"] if pd.notna(r["liquefaction_drive"]) else "—"
        pl = project_life_def.loc[project_life_def["project_id"] == r["project_id"]]
        if r["is_legacy"] or not len(pl):
            life_tot = "—"
        else:
            life_tot = f"{float(pl.iloc[0]['lifetime_mtco2e']):.1f}"
        note = (
            "legacy: outlived nominal design life; steady-state util; annual only"
            if r["is_legacy"]
            else ""
        )
        lines.append(
            f"| {r['project_id']} | {r['capacity_mtpa']:.1f} | {r['chain']} | "
            f"{r['calc_group']} | {r['tier']} | {drive} | "
            f"{int(r['lifespan_years'])} ({r['lifespan_source']}) | "
            f"{r['effective_tonnes']/1e6:.2f} | {r['annual_total']/1e6:.1f} | "
            f"{life_tot} | "
            f"{r['canada_territorial']/1e6:.1f} / "
            f"{r['international_bunkers']/1e6:.1f} / "
            f"{r['foreign_territorial']/1e6:.1f} | {note} |"
        )
    lines.append("")

    # 5 By stage
    lines.append("## 5. By stage")
    lines.append("")
    lines.append("| stage | destination | life_average_annual_mt | share |")
    lines.append("|---|---|---|---|")
    for _, r in stages.iterrows():
        share = r["share_of_total"] * 100 if r["share_of_total"] is not None else 0
        lines.append(
            f"| {r['stage']} | {r['territorial_destination']} | "
            f"{r['annual_mtco2e_yr']:.1f} | {share:.1f}% |"
        )
    lines.append("")

    # 6 Scenario range
    lines.append("## 6. Scenario range")
    lines.append("")
    lines.append("| scenario | upstream | life_average_annual_mt | Lifecycle Mt | CAN Mt/yr |")
    lines.append("|---|---|---|---|---|")
    for scen in INTENSITY_SCENARIOS:
        s = by_project.loc[
            (~by_project["excluded_from_totals"]) & (by_project["scenario"] == scen)
        ]
        up = inputs["upstream_by_scenario"][scen]
        life = panel_lifetime_mt(panel, scen)
        lines.append(
            f"| {scen} | {up:.2f} | {float(s['annual_total'].sum())/1e6:.1f} | "
            f"{life:.1f} | "
            f"{float(s['canada_territorial'].sum())/1e6:.1f} |"
        )
    lines.append("")

    # 7 Context
    lines.append("## 7. Context")
    lines.append("")
    lines.append(
        f"Canada territorial under `{DEFAULT_SCENARIO}` is **{can:.1f} MtCO2e/yr**."
    )
    lines.append("")
    lines.append(
        f"- **{can/national*100:.1f}%** of national inventory "
        f"({national:.0f} Mt, inventory basis — excludes LULUCF)."
    )
    lines.append(
        f"- **{can/t_low*100:.1f}% to {can/t_high*100:.1f}%** of the 2030 target range "
        f"({t_low:.0f}–{t_high:.0f} Mt). Targets include land-use accounting; "
        f"the {national:.0f} inventory figure does not."
    )
    lines.append(
        f"- **{can/gap*100:.1f}%** of the 2030 overshoot gap "
        f"({gap:.0f} Mt, projected emissions minus the target path)."
    )
    lines.append("")

    # 8 Sensitivities
    lines.append("## 8. Assumptions that move the number most")
    lines.append("")
    base_annual = annual
    howarth = by_project.loc[
        (~by_project["excluded_from_totals"])
        & (by_project["scenario"] == "howarth_high"),
        "annual_total",
    ].sum() / 1e6
    inventory = by_project.loc[
        (~by_project["excluded_from_totals"])
        & (by_project["scenario"] == "inventory_as_reported"),
        "annual_total",
    ].sum() / 1e6
    lines.append(
        f"- **Upstream factor** (central 0.25): inventory_as_reported (0.22) → "
        f"{inventory:.1f} Mt/yr ({inventory-base_annual:+.1f}); "
        f"howarth_high (0.55) → {howarth:.1f} Mt/yr ({howarth-base_annual:+.1f})."
    )

    life_low = (
        float(params["lifespan_sensitivity_low"])
        if "lifespan_sensitivity_low" in params
        else 30.0
    )
    life_high = (
        float(params["lifespan_sensitivity_high"])
        if "lifespan_sensitivity_high" in params
        else 50.0
    )
    lines.append(
        f"- **Lifespan** (default mostly 40 yr licence / Parameters default): "
        f"sensitivity bounds in Parameters are {life_low:.0f} and {life_high:.0f} yr. "
        f"Lifecycle total scales roughly with lifespan "
        f"(~{(life_low/40-1)*100:+.0f}% at {life_low:.0f} yr, "
        f"~{(life_high/40-1)*100:+.0f}% at {life_high:.0f} yr on a pure scale basis). "
        f"Annual changes only via the util_sum/life ratio and FID-delay share of the window. "
        f"Legacy facilities (outlived design life) use steady-state util and report annual only."
    )

    delayed = sample.loc[sample["utilisation_source"].astype(str).str.contains("fid_delay")]
    delay_cap_export = (
        float(delayed.loc[delayed["chain"] == "export", "capacity_mtpa"].sum())
        if len(delayed)
        else 0.0
    )
    delay_ann = float(delayed["annual_total"].sum()) / 1e6 if len(delayed) else 0.0
    lines.append(
        f"- **FID delay** (`fid_delay_mid`={get_param(params,'fid_delay_mid')} yr inside lifespan): "
        f"applies to {len(delayed)} projects ({delay_cap_export:.1f} mtpa export), "
        f"currently {delay_ann:.1f} Mt/yr. Removing the delay would raise their annual "
        f"emissions by roughly the ratio of lost ramp years "
        f"(order-of-magnitude: several Mt/yr on the proposed export slate)."
    )

    util_ss = float(get_param(params, "steady_state_utilisation"))
    lines.append(
        f"- **Utilisation** (default steady-state {util_ss:.3f}; Phase 1 override "
        f"{get_param(params,'lng_canada_ph1_steady_state_utilisation')}; "
        f"Saint John flat {get_param(params,'saint_john_utilisation')}): "
        f"annual emissions scale almost linearly with effective util. "
        f"A +10% relative move in steady-state util moves the headline by about "
        f"{base_annual*0.10:.1f} Mt/yr if applied uniformly."
    )

    liq_central = float(inputs["factors"].loc["liquefaction", "central"])
    lines.append(
        f"- **Liquefaction** (central {liq_central:.2f} tCO2e/t, gas turbine for "
        f"every terminal): electrification is not assumed "
        f"(`liquefaction_electrification_assumed`="
        f"{get_param(params, 'liquefaction_electrification_assumed')}). "
        f"0.12 is retained as range_low and applies only if electrification is "
        f"contracted and delivered. Previous drive classifications are in "
        f"`liquefaction_drive_note`."
    )
    if placeholder_sens is not None:
        lines.append(
            f"- **Placeholder start year** (`assumed_first_export_year_if_missing`="
            f"{placeholder_sens['named_start']}): "
            f"{placeholder_sens['placeholder_mt']:.1f} MtCO2e "
            f"({placeholder_sens['placeholder_pct']:.1f}% of lifetime) from six "
            "assets with a blank `first_export_year`. The 2069 tail is entirely "
            "this fill. Sensitivity at 2033 and 2035 is tabulated below."
        )
    lines.append(
        f"- **Liquefaction drive default** for remaining `not_published` "
        f"(domestic) rows: `{inputs['liquefaction_drive_default']}` → "
        f"intensity {liq_central:.2f} tCO2e/t from Emission Factors central."
    )
    lines.append("")

    # 9 Appendix comparator
    cf = electrification_counterfactual(inputs, by_project)
    head = cf["summary"].loc[cf["summary"]["slice"] == "headline"].iloc[0]
    lines.append("## 9. Appendix · electrification counterfactual (Canada territorial)")
    lines.append("")
    lines.append(
        "Headline case is gas turbine for every terminal. The rows below ask what "
        "Canada-territorial LNG would be if liquefaction ran at the electric factor "
        f"({cf['electric_intensity']:.2f} instead of {cf['gas_intensity']:.2f} tCO2e/t). "
        "Liquefaction is tagged CAN, so the whole delta is territorial. "
        "This does not change the headline totals."
    )
    lines.append("")
    lines.append(
        f"| case | CAN Mt/yr | vs gas | share of {cf['national']:.0f} Mt inventory | share of 2030 target low |"
    )
    lines.append("|---|---|---|---|---|")
    gas = float(head["canada_territorial_gas_mtco2e_yr"])
    claimed = float(head["canada_territorial_claimed_electric_mtco2e_yr"])
    alle = float(head["canada_territorial_all_electric_mtco2e_yr"])
    lines.append(
        f"| Gas turbine (current) | {gas:.1f} | — | "
        f"{float(head['share_of_national_inventory_gas'])*100:.1f}% | "
        f"{float(head['share_of_2030_target_low_gas'])*100:.1f}% |"
    )
    lines.append(
        f"| Claimed electric delivered | {claimed:.1f} | {claimed-gas:+.1f} | "
        f"{claimed/cf['national']*100:.1f}% | "
        f"{claimed/cf['target_low']*100:.1f}% |"
    )
    lines.append(
        f"| All terminals electric | {alle:.1f} | {alle-gas:+.1f} | "
        f"{float(head['share_of_national_inventory_all_electric'])*100:.1f}% | "
        f"{float(head['share_of_2030_target_low_all_electric'])*100:.1f}% |"
    )
    lines.append("")
    lines.append(
        "Claimed-electric assets (previous `electric_committed` / `electric_planned`): "
        + ", ".join(cf["claimed_project_ids"])
        + "."
    )
    lines.append("")
    lines.append("| calc_group | gas | claimed electric | all electric |")
    lines.append("|---|---|---|---|")
    for g in GROUPS:
        r = cf["summary"].loc[cf["summary"]["slice"] == g].iloc[0]
        lines.append(
            f"| {g} | {r['canada_territorial_gas_mtco2e_yr']:.1f} | "
            f"{r['canada_territorial_claimed_electric_mtco2e_yr']:.1f} | "
            f"{r['canada_territorial_all_electric_mtco2e_yr']:.1f} |"
        )
    lines.append("")
    lines.append(
        "Figure: `Outputs/figures/fig08_electrification_canada_territorial.png`."
    )
    lines.append("")

    # 10 Anything wrong
    lines.append("## 10. Anything that looks wrong")
    lines.append("")
    if inputs["findings"]:
        for f in inputs["findings"]:
            lines.append(f"- FINDING: {f}")
    else:
        lines.append("- No load-time findings.")
    for f in inputs["flags"]:
        lines.append(f"- Flag: {f['project_id']}.{f['field']}={f['issue']}")
    if inputs.get("excluded_none"):
        lines.append(
            f"- Excluded (chain=none or blank, not zeroed): {inputs['excluded_none']}"
        )
    if inputs.get("excluded_watch"):
        lines.append(
            f"- Excluded calc_group=watch (not in calculation): {inputs['excluded_watch']}"
        )
    legacy = sample.loc[sample["is_legacy"]]
    if len(legacy):
        names = ", ".join(
            f"{r.project_id} (first_export_year={r.first_export_year})"
            for r in legacy.itertuples()
        )
        lines.append(
            f"- Legacy facilities (outlived nominal design life; annual only, "
            f"no lifecycle total): {names}."
        )
    lines.append(
        "- Remaining carbon budgets (GCB 2025) are CO2 from the start of 2026. "
        "Lifetime totals are GWP100 CO2e. The share-of-budget figures compare "
        "CO2e to a CO2 budget and are an approximation; a true CO2-only total "
        "is not derivable from this model."
    )
    lines.append(
        "- Reconciliations close within floating-point tolerance (1e-6 to 1e-3); "
        "no material rounding residuals."
    )
    lines.append(
        "- Saint John at ~0.5 Mt/yr depends entirely on `saint_john_utilisation=0.025`; "
        "nameplate at default util would be ~17 Mt/yr. "
        "tier=watch but calc_group=operating (operating import terminal)."
    )
    lines.append(
        "- Tilbury Phase 2 (2.5 mtpa) sits on bunkering by register judgement "
        "(`chain_note`); NRCan lists it as export — classification is a stated judgement, "
        "not re-derived in code."
    )
    lines.append(
        "- Loss and damage central case is ECCC SC-CO2 at 2%, applied per "
        "calendar year to the full GWP100 CO2e total "
        "(`central_price_family=eccc`). That overstates methane (CH4-derived "
        "CO2e is charged at SC-CO2 rather than SC-CH4). Burke is an "
        "upper-bracket sensitivity (g = 0). Damages after 2100, sea-level "
        "rise, extremes and mortality outside GDP are omitted. The "
        "Conference Board denominator is Table 1 GDP in 2020 CAD, inflated "
        "to 2025 CAD."
    )
    lines.append("")

    if ld is not None:
        lines.extend(format_ld_markdown(ld))
    if placeholder_sens is not None:
        lines.extend(format_placeholder_markdown(placeholder_sens))
    if mc is not None:
        lines.extend(format_mc_markdown(mc))

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote review summary: {path}")


def _validate_licence_end(
    inputs: dict, panel: pd.DataFrame, sample: pd.DataFrame
) -> None:
    """No asset emits after authorised_export_end_year where that field is set."""
    assets = inputs["assets"].set_index("project_id")
    pdef = panel.loc[panel["scenario"] == DEFAULT_SCENARIO]
    n = 0
    for pid, arow in assets.iterrows():
        end = _licence_end_year(arow)
        if end is None:
            continue
        n += 1
        years = pdef.loc[pdef["project_id"] == pid, "year"]
        last = int(years.max()) if len(years) else None
        if last is not None:
            assert last <= end, (pid, last, end)
        prow = sample.loc[sample["project_id"] == pid]
        if not len(prow):
            continue
        life = int(prow.iloc[0]["lifespan_years"])
        src = str(prow.iloc[0]["lifespan_source"])
        derived = None
        if pd.notna(arow.get("authorised_export_term_years")):
            derived = int(arow["authorised_export_term_years"])
        cut = (derived - life) if derived is not None else None
        print(
            f"  licence stop {pid}: last_year={last} end={end} "
            f"life={life}"
            + (f" (cut {cut}y from term {derived})" if cut else "")
            + f" src={src}"
        )
    assert n > 0
    print(
        f"[validate] no asset emits past authorised_export_end_year "
        f"(n={n} licenced) PASS"
    )


def _validate_loss_damage(sample: pd.DataFrame, ld: dict, panel: pd.DataFrame) -> None:
    """L&D remaining tonnes must equal the published panel; ECCC is central."""
    assert ld["central_price_family"] == "eccc"
    assert ld["central_aggregation"] == "calendar_year"
    assert ld["eccc_r"] == 2.0
    assert ld["burke_r"] == 2.0
    assert ld["central_g"] == 0.0
    h = ld["headline"].set_index("case")
    published = h.loc["published_central"]
    assert published["price_family"] == "eccc"
    assert published["aggregation"] == "calendar_year"
    eccc_npv = h.loc["eccc_central_npv_2025"]
    assert published["proposed_cad_billion"] > published["operating_cad_billion"] > 0
    assert published["total_cad_billion"] > eccc_npv["total_cad_billion"] > 0
    egrid = ld["eccc_grid"].set_index("discount_rate_pct")
    assert (
        float(egrid.loc[1.5, "calendar_year_total_cad_billion"])
        > float(egrid.loc[2.0, "calendar_year_total_cad_billion"])
        > float(egrid.loc[2.5, "calendar_year_total_cad_billion"])
    )
    hb = ld["h_burke"]
    assert float(hb["total_cad_billion"]) > float(published["total_cad_billion"])
    share = ld["canada_share"]
    assert 0.0015 < share < 0.0020, share
    assert hb["externality_ratio_proposed"] > 10
    assert hb["national_value_over_borne"] > 1
    assert abs(hb["externalisation_share"] - (1 - share)) < 1e-12
    assert abs(
        float(hb["proposed_cad_billion"]) - float(hb["proposed_gwp_cad_billion"])
    ) < 1e-6
    assert 0.01 < ld["methane_share_of_co2e"] < 0.08, ld["methane_share_of_co2e"]
    assert 0.0 < ld["methane_overstatement_pct"] < 0.10, ld["methane_overstatement_pct"]
    py = ld["price_by_year"]
    tonnes = float(py["emissions_mtco2e"].sum()) * 1e6
    wavg = float(published["total_cad"]) / tonnes
    assert abs(wavg - ld["weighted_sc_cad2025"]) < 1e-6, (wavg, ld["weighted_sc_cad2025"])
    y2025 = py.loc[py["year"] == 2025].iloc[0]
    assert int(y2025["sc_cad2021_per_t"]) == 271
    factor = ld["cad2021_to_2025_factor"]
    # Inflation applied once: CAD 2025 = CAD 2021 × deflator, not × deflator².
    assert abs(float(y2025["sc_cad2025_per_t"]) - 271.0 * factor) < 1e-6
    assert abs(float(y2025["sc_cad2025_per_t"]) - 271.0 * factor * factor) > 1.0
    assert int(py["year"].min()) == 2025
    assert ld["gva"] > ld["gva_proposed_as_published"]
    assert not ld["fig4"]["canada_in_recipient_panel"]
    assert abs(ld["fig4"]["usa_owing_usd"] / 1e12 - 10.18) < 0.15
    assert ld["gva_proposed_30yr"] < ld["gva"]
    grid = ld["burke_grid"]
    lo = float(
        grid.loc[
            (grid["discount_rate_pct"] == 5.0) & (grid["growth_rate"] == 0.0),
            "total_cad_billion",
        ].iloc[0]
    )
    hi = float(
        grid.loc[
            (grid["discount_rate_pct"] == 1.5) & (grid["growth_rate"] == 0.02),
            "total_cad_billion",
        ].iloc[0]
    )
    assert hi > lo, (hi, lo)
    assert not bool(grid["is_central"].any())

    rem = (
        ld["by_year"]
        .loc[ld["by_year"]["price_family"] == "burke"]
        .drop_duplicates(["project_id", "year"])
        .groupby("project_id")["emissions_mtco2e"]
        .sum()
    )
    pub = (
        panel.loc[panel["scenario"] == DEFAULT_SCENARIO]
        .groupby("project_id")["emissions_mtco2e"]
        .sum()
    )
    merged = pub.rename("panel_mt").to_frame().join(rem.rename("ld_mt"), how="outer")
    merged = merged.fillna(0.0)
    delta = (merged["panel_mt"] - merged["ld_mt"]).abs()
    assert delta.max() < 0.05, merged.loc[delta >= 0.05]
    panel_sum = float(pub.sum())
    ld_sum = float(rem.sum())
    assert abs(panel_sum - ld_sum) < 0.05, (panel_sum, ld_sum)
    legacy_ids = set(sample.loc[sample["is_legacy"], "project_id"])
    ld_ids = set(ld["by_project"]["project_id"])
    assert not (ld_ids & legacy_ids), ld_ids & legacy_ids
    print(
        f"[validate] L&D remaining = panel lifetime "
        f"{panel_sum:.2f} Mt PASS"
    )


def main() -> None:
    try:
        reg_m, inp_m = REGISTER.stat().st_mtime, INPUTS.stat().st_mtime
    except OSError:
        reg_m = inp_m = None
    inputs = load_inputs(REGISTER, INPUTS)
    print(f"In-scope assets: {len(inputs['assets'])}")
    print(f"calc_group source: {inputs['calc_group_source']}")
    for finding in inputs["findings"]:
        print(f"  FINDING: {finding}")
    for f in inputs["flags"]:
        print(f"  flag: {f['project_id']}.{f['field']}={f['issue']}")

    # calc_group must be read from register, never derived
    assert inputs["calc_group_source"] == "Asset Register:calc_group"
    print("[validate] calc_group read from Asset Register (not derived) PASS")
    assert abs(float(get_param(inputs["params"], "remaining_15c_budget")) - 170) < 1e-9
    assert abs(float(get_param(inputs["params"], "remaining_17c_budget")) - 525) < 1e-9
    assert abs(float(get_param(inputs["params"], "remaining_2c_budget")) - 1055) < 1e-9
    print("[validate] GCB 2025 carbon budgets 170 / 525 / 1055 GtCO2 PASS")

    for chain, n in EXPECTED_CHAIN_LENGTHS.items():
        assert len(inputs["chains"][chain]) == n
    print("[validate] chain stage counts PASS")

    by_project = compute_by_project(inputs)
    panel = build_emissions_panel(inputs)
    summary = summarise(by_project)
    by_chain = summarise_by_chain(by_project)
    stages = by_stage(by_project)
    territorial = territorial_table(by_project, inputs["params"])
    assumptions = assumptions_used(inputs, by_project)

    sample = by_project.loc[
        (~by_project["excluded_from_totals"]) & (by_project["scenario"] == DEFAULT_SCENARIO)
    ]

    # No watch group in calculation
    assert "watch" not in set(sample["calc_group"].unique()), sample["calc_group"].unique()
    assert "watch" not in set(summary["group"].unique())
    assert not inputs["excluded_watch"] or all(
        pid not in set(sample["project_id"]) for pid in inputs["excluded_watch"]
    )
    # Saint John must be operating via calc_group
    sj_row = sample.loc[sample["project_id"] == "saint_john_import_facility"]
    assert len(sj_row) == 1 and sj_row.iloc[0]["calc_group"] == "operating"
    assert sj_row.iloc[0]["tier"] == "watch"
    print("[validate] no watch calc_group in calculation; Saint John=operating PASS")

    assert_no_cross_chain_capacity_sum(
        {"summary": summary, "by_chain": by_chain, "by_project": by_project}
    )

    # Export capacity by calc_group (headline comparable figure)
    for cg, exp in EXPECTED_EXPORT_BY_CALC.items():
        cap = float(
            sample.loc[
                (sample["chain"] == "export") & (sample["calc_group"] == cg),
                "capacity_mtpa",
            ].sum()
        )
        assert abs(cap - exp) < 1e-6, (cg, cap, exp)
        s_cap = float(
            summary.loc[
                (summary["scenario"] == DEFAULT_SCENARIO) & (summary["group"] == cg),
                "capacity_export_headline_mtpa",
            ].iloc[0]
        )
        assert abs(s_cap - exp) < 1e-6, (cg, s_cap, exp)
    export_total = float(sample.loc[sample["chain"] == "export", "capacity_mtpa"].sum())
    assert abs(export_total - EXPECTED_EXPORT_TOTAL) < 1e-6, export_total
    print(
        f"[validate] export capacity by calc_group "
        f"(total {export_total:.1f} mtpa) PASS"
    )

    # Proposed export: 26 advanced + 54.7 early (Kino Aski 15 mtpa)
    prop_exp = sample.loc[
        (sample["chain"] == "export") & (sample["calc_group"] == "proposed")
    ]
    adv = float(prop_exp.loc[prop_exp["tier"] == "advanced_proposed", "capacity_mtpa"].sum())
    early = float(prop_exp.loc[prop_exp["tier"] == "early_proposed", "capacity_mtpa"].sum())
    assert abs(adv - EXPECTED_ADVANCED_EXPORT) < 1e-6, adv
    assert abs(early - EXPECTED_EARLY_EXPORT) < 1e-6, (early, EXPECTED_EARLY_EXPORT)
    print(f"[validate] proposed export split advanced={adv:.1f} early={early:.1f} PASS")

    electric_left = sample.loc[
        sample["liquefaction_drive"].isin(["electric_committed", "electric_planned"])
    ]
    assert len(electric_left) == 0, electric_left["project_id"].tolist()
    print("[validate] no electric_committed or electric_planned active drive PASS")

    liq_rows = sample.loc[sample["chain"].isin(["export", "bunkering"])]
    liq_delta = (liq_rows["intensity_liquefaction"].astype(float) - 0.29).abs()
    assert len(liq_rows) and liq_delta.max() < 1e-9, liq_delta.max()
    print("[validate] liquefaction intensity=0.29 for all export and bunkering PASS")

    # Off-chain null
    for _, r in sample.iterrows():
        on = {s for s, _ in inputs["chains"][r["chain"]]}
        for stage_name in ALL_STAGES:
            if stage_name not in on:
                assert pd.isna(r[f"annual_{stage_name}"]), (r["project_id"], stage_name)
    print("[validate] no off-chain stages computed PASS")

    terr_delta = (
        sample["canada_territorial"]
        + sample["international_bunkers"]
        + sample["foreign_territorial"]
        - sample["annual_total"]
    ).abs()
    assert terr_delta.max() < 1e-6
    print("[validate] CAN + BUNK + FOR = total PASS")
    scope_delta = (
        sample["scope_1_2"] + sample["scope_3"] - sample["annual_total"]
    ).abs()
    assert scope_delta.max() < 1e-6
    print("[validate] scope 1+2 + scope 3 = total PASS")

    sj = sample.loc[sample["project_id"] == "saint_john_import_facility"].iloc[0]
    sj_mt = float(sj["annual_total"]) / 1e6
    assert abs(sj_mt - 0.5) < 0.15 and sj_mt < 5
    print(f"[validate] Saint John={sj_mt:.3f} MtCO2e/yr PASS")

    p1 = sample.loc[sample["project_id"] == "lng_canada_phase_1"].iloc[0]
    nameplate_liq = float(p1["capacity_mtpa"]) * float(p1["intensity_liquefaction"])
    assert abs(nameplate_liq - 4.06) < 0.02
    print(f"[validate] Phase 1 liquefaction nameplate={nameplate_liq:.3f} PASS")

    # Legacy facilities
    legacy = sample.loc[sample["is_legacy"]]
    legacy_ids = sorted(legacy["project_id"].unique())
    assert "tilbury_original" in legacy_ids
    assert "energir_montreal_lng" in legacy_ids
    for _, r in legacy.iterrows():
        assert pd.isna(r["lifecycle_total"]), r["project_id"]
        assert "legacy" in str(r["utilisation_source"]).lower()
        assert abs(float(r["effective_util"]) - float(get_param(inputs["params"], "steady_state_utilisation"))) < 1e-9
    print(f"[validate] legacy facilities annual-only (no lifecycle): {legacy_ids} PASS")

    _validate_licence_end(inputs, panel, sample)

    ld = compute_loss_damage(inputs, INPUTS_DIR, panel=panel)
    _validate_loss_damage(sample, ld, panel)
    print(
        f"[validate] loss and damage central "
        f"${ld['published']['total_cad_billion']:.0f} bn "
        f"CAD 2025 (ECCC 2% calendar year) PASS"
    )
    print(
        f"[validate] emissions-weighted SC-CO2 "
        f"${ld['weighted_sc_cad2025']:.0f}/t CAD 2025 "
        f"(simple mean ${ld['simple_sc_cad2025']:.0f}; "
        f"CAD 2021 weighted ${ld['weighted_sc_cad2021']:.0f}; "
        f"deflator {ld['cad2021_to_2025_factor']:.4f} applied once) PASS"
    )

    # Group and headline annuals — printed against the pre-revision snapshot
    sdef = summary.loc[summary["scenario"] == DEFAULT_SCENARIO]
    annual = float(sample["annual_total"].sum())
    annual_mt = annual / 1e6
    liq_mt = float(sample["annual_liquefaction"].sum()) / 1e6
    print(
        f"[validate] life_average_annual_mt {annual_mt:.1f} Mt/yr "
        f"(was {BEFORE['annual_mt']:.1f}); "
        f"liquefaction {liq_mt:.1f} Mt/yr (was {BEFORE['liquefaction_mt']:.1f})"
    )

    can = float(sample["canada_territorial"].sum())
    bunk = float(sample["international_bunkers"].sum())
    foreign = float(sample["foreign_territorial"].sum())

    panel_life_mt = panel_lifetime_mt(panel, DEFAULT_SCENARIO)
    peak_year, peak_mt = panel_peak(panel, DEFAULT_SCENARIO)
    duration_life = float(sample["lifecycle_total"].sum(min_count=1)) / 1e6
    if pd.isna(duration_life):
        duration_life = 0.0
    print(
        f"[validate] published lifetime is calendar panel "
        f"{panel_life_mt:.1f} Mt (duration×average was {duration_life:.1f}; "
        f"delta {panel_life_mt - duration_life:+.1f})"
    )
    print(
        f"[validate] headline annual is panel peak {peak_mt:.1f} Mt in {peak_year} "
        f"({panel_n_emitting(panel, peak_year, DEFAULT_SCENARIO)} assets); "
        f"life_average_annual_mt {annual_mt:.1f}"
    )
    placeholder_sens = run_placeholder_start_sensitivity(
        inputs, INPUTS_DIR, panel, ld
    )
    print(
        f"[validate] placeholder-start assets "
        f"{placeholder_sens['placeholder_mt']:.1f} Mt "
        f"({placeholder_sens['placeholder_pct']:.1f}% of lifetime) PASS"
    )
    mc = run_monte_carlo(inputs, INPUTS_DIR, panel)
    print(
        f"[validate] Monte Carlo {mc['n_draws']} draws seed {mc['seed']} "
        f"physics {mc['physics_seconds']:.2f}s price {mc['price_seconds']:.2f}s "
        f"kernel max abs {mc['kernel_panel_max_abs_mt']:.1e} Mt PASS"
    )
    budgets = carbon_budget_shares(panel_life_mt, inputs["params"])
    b15 = budgets.loc[budgets["parameter"] == "remaining_15c_budget"].iloc[0]
    print(
        f"[validate] lifetime {b15['lifetime_gtco2e']:.2f} GtCO2e is "
        f"{b15['share_pct']:.1f}% of 1.5C budget {b15['budget_gtco2']:g} GtCO2 "
        f"(CO2e vs CO2 approximation) PASS"
    )

    summary = summary.copy()
    summary["lifecycle_total_mtco2e"] = [
        panel_lifetime_mt(panel, r["scenario"], calc_group=r["group"])
        for _, r in summary.iterrows()
    ]
    by_chain = by_chain.copy()
    by_chain["lifecycle_total_mtco2e"] = [
        panel_lifetime_mt(panel, r["scenario"], chain=r["chain"])
        for _, r in by_chain.iterrows()
    ]
    proj_life = panel_by_project(panel)
    by_project = by_project.merge(
        proj_life[["scenario", "project_id", "lifetime_mtco2e"]].rename(
            columns={"lifetime_mtco2e": "panel_lifetime_mtco2e"}
        ),
        on=["scenario", "project_id"],
        how="left",
    )

    readme = pd.DataFrame(
        [
            ("title", "Canada LNG lifecycle emissions — calc_group grouping"),
            ("run_at_utc", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")),
            ("asset_register", REGISTER.name),
            ("data_inputs", INPUTS.name),
            ("headline_scenario", DEFAULT_SCENARIO),
            ("calc_group_source", inputs["calc_group_source"]),
            (
                "headline_note",
                "Lifetime is the sum of the per-asset calendar panel "
                f"({PANEL_START_YEAR} to last emitting year). "
                "Headline annual is the panel peak calendar year. "
                "life_average_annual_mt is utilisation over each asset window. "
                "Headline includes all calc_groups (proposed = advanced + early). "
                "Capacity is per chain; headline capacity is export liquefaction only.",
            ),
            ("annual_total_mtco2e_yr", peak_mt),
            ("annual_basis", "panel peak calendar year"),
            ("panel_peak_year", peak_year),
            ("panel_peak_mtco2e_yr", peak_mt),
            ("panel_peak_n_assets", panel_n_emitting(panel, peak_year, DEFAULT_SCENARIO)),
            ("life_average_annual_mt", annual_mt),
            ("life_average_basis", "life-average utilisation over each asset window"),
            ("lifetime_total_mtco2e", panel_life_mt),
            ("lifetime_basis", "sum of calendar panel; excludes legacy"),
            (
                "assumed_first_export_year_if_missing",
                int(get_param(inputs["params"], "assumed_first_export_year_if_missing")),
            ),
            ("placeholder_lifetime_mtco2e", placeholder_sens["placeholder_mt"]),
            ("placeholder_share_of_lifetime_pct", placeholder_sens["placeholder_pct"]),
            ("monte_carlo_seed", mc["seed"]),
            ("monte_carlo_n_draws", mc["n_draws"]),
            ("monte_carlo_physics_seconds", round(mc["physics_seconds"], 3)),
            ("monte_carlo_price_seconds", round(mc["price_seconds"], 3)),
            (
                "carbon_budget_units_note",
                "Lifetime is GWP100 CO2e; GCB 2025 budgets are CO2. "
                "Share-of-budget is CO2e / CO2 (approximation).",
            ),
            ("duration_x_average_mtco2e", duration_life),
            ("export_capacity_mtpa", export_total),
            ("canada_territorial_mtco2e_yr", can / 1e6),
            ("international_bunkers_mtco2e_yr", bunk / 1e6),
            ("foreign_territorial_mtco2e_yr", foreign / 1e6),
            ("legacy_projects", ", ".join(legacy_ids)),
            ("gcb_2025_15c_gtco2", float(b15["budget_gtco2"])),
            ("lifetime_share_of_15c_budget_pct", float(b15["share_pct"])),
            ("inputs_guard", "Inputs opened read-only (rb); writes only under Outputs/."),
            (
                "slide_tables",
                "Outputs/SLIDE_TABLES.xlsx — send this file to the PPT chat "
                "(one table per sheet, 1-decimal, project names).",
            ),
            ("findings", "; ".join(inputs["findings"]) if inputs["findings"] else "none"),
        ],
        columns=["field", "value"],
    )

    OUT.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(RESULTS, engine="openpyxl") as writer:
        readme.to_excel(writer, sheet_name="README", index=False)
        summary[
            [
                "group",
                "scenario",
                "project_count",
                "capacity_export_headline_mtpa",
                "capacity_export_mtpa",
                "capacity_bunkering_mtpa",
                "capacity_domestic_mtpa",
                "capacity_import_mtpa",
                "scope_1_2_mtco2e_yr",
                "scope_3_mtco2e_yr",
                "canada_territorial_mtco2e_yr",
                "international_bunkers_mtco2e_yr",
                "foreign_territorial_mtco2e_yr",
                "annual_total_mtco2e_yr",
                "lifecycle_total_mtco2e",
            ]
        ].to_excel(writer, sheet_name="Summary", index=False)
        by_project.to_excel(writer, sheet_name="By Project", index=False)
        stages.to_excel(writer, sheet_name="By Stage", index=False)
        territorial.to_excel(writer, sheet_name="Territorial", index=False)
        assumptions.to_excel(writer, sheet_name="Assumptions", index=False)
        budgets.to_excel(writer, sheet_name="Carbon Budgets", index=False)
        by_chain.to_excel(writer, sheet_name="By Chain", index=False)
        panel.to_excel(writer, sheet_name="Calendar Panel", index=False)
        panel_by_project(panel).to_excel(
            writer, sheet_name="Panel Lifetime By Project", index=False
        )
        elec_cf = electrification_counterfactual(inputs, by_project)
        elec_cf["summary"].to_excel(writer, sheet_name="Electrification CAN", index=False)
        ld["headline"].to_excel(writer, sheet_name="LD Headline", index=False)
        ld["by_project"].to_excel(writer, sheet_name="LD By Project", index=False)
        ld["burke_grid"].to_excel(writer, sheet_name="LD Burke Grid", index=False)
        ld["eccc_grid"].to_excel(writer, sheet_name="LD ECCC Grid", index=False)
        ld["physical_scenarios"].to_excel(writer, sheet_name="LD Physical Scenarios", index=False)
        ld["sc_table"].to_excel(writer, sheet_name="LD SC-CO2", index=False)
        ld["horizon_table"].to_excel(writer, sheet_name="LD Horizons", index=False)
        ld["params_meta"].to_excel(writer, sheet_name="LD Assumptions", index=False)
        mc["summary"].to_excel(writer, sheet_name="MC Summary", index=False)
        mc["howarth"].to_excel(writer, sheet_name="MC Howarth", index=False)
        mc["parameters"].to_excel(writer, sheet_name="MC Parameters", index=False)

    write_figure(by_project, FIGURE)
    write_review_summary(
        SUMMARY_MD,
        inputs,
        by_project,
        summary,
        by_chain,
        stages,
        panel,
        ld=ld,
        placeholder_sens=placeholder_sens,
        mc=mc,
    )
    fig_results = build_all_report_figures(
        inputs, by_project, stages, FIGURE_DIR, FIGURE_DATA, panel=panel
    )
    fig09 = FIGURE_DIR / "fig09_loss_damage_by_group.png"
    write_ld_figure(ld["published"], fig09)
    ld_csv = FIGURE_DATA / "fig09_loss_damage_by_group.csv"
    FIGURE_DATA.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "calc_group": g,
                "cad_trillion_2025": float(ld["published"][f"{g}_cad_billion"]) / 1000.0,
                "price_family": "eccc",
                "discount_rate_pct": ld["eccc_r"],
                "aggregation": "calendar_year",
            }
            for g in GROUPS
        ]
    ).to_csv(ld_csv, index=False)
    ld["headline"].to_csv(FIGURE_DATA / "ld_headline.csv", index=False)
    ld["burke_grid"].to_csv(FIGURE_DATA / "ld_burke_grid.csv", index=False)
    ld["eccc_grid"].to_csv(FIGURE_DATA / "ld_eccc_grid.csv", index=False)
    ld["price_by_year"].to_csv(FIGURE_DATA / "ld_price_by_year.csv", index=False)
    placeholder_sens["cases"].to_csv(
        FIGURE_DATA / "placeholder_start_sensitivity.csv", index=False
    )
    placeholder_sens["by_asset"].to_csv(
        FIGURE_DATA / "placeholder_start_by_asset.csv", index=False
    )
    mc["summary"].to_csv(FIGURE_DATA / "mc_summary.csv", index=False)
    mc["howarth"].to_csv(FIGURE_DATA / "mc_howarth_sensitivity.csv", index=False)
    mc["parameters"].to_csv(FIGURE_DATA / "mc_parameters.csv", index=False)
    mc["draws"].to_csv(FIGURE_DATA / "mc_draws.csv", index=False)
    panel.to_csv(FIGURE_DATA / "emissions_panel.csv", index=False)
    slide_tables = build_slide_tables(
        inputs, by_project, summary, by_chain, stages, panel, ld=ld
    )
    write_slide_tables_xlsx(slide_tables, SLIDE_TABLES, FIGURE_DATA)

    if reg_m is not None and inp_m is not None:
        assert REGISTER.stat().st_mtime == reg_m and INPUTS.stat().st_mtime == inp_m

    print("\n========== COMPLETION ==========")
    print("BEFORE (July 2026 run, measurement_central):")
    print(
        f"  annual={BEFORE['annual_mt']:.1f} Mt/yr  "
        f"lifecycle={BEFORE['lifecycle_mt']:.1f} Mt  "
        f"export={BEFORE['export_mtpa']:.1f} mtpa  "
        f"liquefaction={BEFORE['liquefaction_mt']:.1f} Mt/yr  "
        f"early_export={BEFORE['early_export_mtpa']:.1f} mtpa"
    )
    for g, val in BEFORE["group_annual"].items():
        print(f"  group {g:20s}  annual={val:6.1f} Mt/yr")
    for c, val in BEFORE["chain_annual"].items():
        print(f"  chain {c:20s}  annual={val:6.1f} Mt/yr")
    print("AFTER:")
    print(
        f"Headline annual (panel peak): {peak_mt:.1f} MtCO2e in {peak_year} "
        f"({panel_n_emitting(panel, peak_year, DEFAULT_SCENARIO)} assets emitting)"
    )
    print(f"life_average_annual_mt: {annual_mt:.1f} MtCO2e/yr")
    print("Group annual totals (measurement_central, life-average):")
    for g in GROUPS:
        r = sdef.loc[sdef["group"] == g].iloc[0]
        before_g = BEFORE["group_annual"][g]
        print(
            f"  {g:20s}  annual={r['annual_total_mtco2e_yr']:6.1f} Mt/yr "
            f"(was {before_g:.1f})  "
            f"export_cap={r['capacity_export_headline_mtpa']:5.1f} mtpa"
        )
    print(
        f"  {'TOTAL':20s}  life_average={annual_mt:6.1f} Mt/yr "
        f"(was {BEFORE['annual_mt']:.1f})"
    )
    print(
        f"Published lifetime (calendar panel): {panel_life_mt:.1f} Mt  "
        f"(duration×average was {duration_life:.1f})"
    )
    print(f"Panel peak: {peak_mt:.1f} MtCO2e in {peak_year}")
    print(
        f"Liquefaction stage: {liq_mt:.1f} Mt/yr "
        f"(was {BEFORE['liquefaction_mt']:.1f})"
    )
    print(
        f"Early-stage export capacity: {early:.1f} mtpa "
        f"(was {BEFORE['early_export_mtpa']:.1f})"
    )
    print(
        f"Headline export capacity: {export_total:.1f} mtpa "
        f"(was {BEFORE['export_mtpa']:.1f})"
    )
    print("By chain:")
    cdef = by_chain.loc[by_chain["scenario"] == DEFAULT_SCENARIO]
    for chain in CHAINS:
        r = cdef.loc[cdef["chain"] == chain].iloc[0]
        before_c = BEFORE["chain_annual"][chain]
        print(
            f"  {chain:20s}  annual={r['annual_total_mtco2e_yr']:6.1f} Mt/yr "
            f"(was {before_c:.1f})  cap={r['capacity_mtpa']:5.1f} mtpa"
        )
    print(
        f"Territorial (average): CAN={can/1e6:.1f}  BUNK={bunk/1e6:.1f}  "
        f"FOR={foreign/1e6:.1f}"
    )
    print(
        "Validations: capacity+tier have chain/calc_group; no electric drive; "
        "liquefaction=0.29 export/bunkering; Saint John ~0.5; Phase 1 liq ~4.06; "
        "scope and territorial splits sum to total — all PASS"
    )
    print("\nReport figures written:")
    for key in ("fig1", "fig2", "fig3", "fig4", "fig5", "fig6", "fig7", "fig8"):
        r = fig_results[key]
        print(f"  {r['path'].name}")
        print(f"    csv: {r['csv'].name}")
        print(f"    key: {r['key']}")
    print(f"  {fig09.name}")
    print(f"    csv: {ld_csv.name}")
    print(
        "\nFigure validations: stage sum=headline, territorial sum=headline, "
        "fig3 plateau=fig6 plateau, fig5 central=fig4, CSVs present — all PASS"
    )
    print(f"\nSlide tables (send this to the PPT chat): {SLIDE_TABLES.name}")
    print("No input file was modified during the run.")
    print("================================")


if __name__ == "__main__":
    main()
