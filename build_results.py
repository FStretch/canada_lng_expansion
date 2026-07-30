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
from src.model import (
    CHAINS,
    GROUPS,
    assert_no_cross_chain_capacity_sum,
    assumptions_used,
    by_stage,
    compute_by_project,
    summarise,
    summarise_by_chain,
    territorial_table,
)

ROOT = Path(__file__).resolve().parent
REGISTER = ROOT / "Inputs" / "Canada_LNG_Asset_Register.xlsx"
INPUTS = ROOT / "Inputs" / "Canada_LNG_Data_Inputs.xlsx"
OUT = ROOT / "Outputs"
RESULTS = OUT / "Canada_LNG_Emissions_Results.xlsx"
SUMMARY_MD = OUT / "RESULTS_SUMMARY.md"
FIGURE = OUT / "figures" / "operating_vs_proposed.png"
FIGURE_DIR = OUT / "figures"
FIGURE_DATA = OUT / "figure_data"

EXPECTED_ANNUAL_BY_GROUP = {
    "operating": 43.3,
    "under_construction": 15.0,
    "proposed": 100.9,
}
EXPECTED_HEADLINE_ANNUAL = 159.2
EXPECTED_EXPORT_BY_CALC = {
    "operating": 14.0,
    "under_construction": 5.4,
    "proposed": 38.7,
}
EXPECTED_EXPORT_TOTAL = 58.1


def write_figure(by_project: pd.DataFrame, path: Path) -> None:
    """Export-chain operating / under construction / proposed (early inside proposed)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    sample = by_project.loc[
        (~by_project["excluded_from_totals"])
        & (by_project["scenario"] == DEFAULT_SCENARIO)
        & (by_project["chain"] == "export")
    ]
    buckets = [
        ("operating", "Operating now", 14.0),
        ("under_construction", "Under construction", 5.4),
        ("proposed", "Proposed", 38.7),
    ]
    labels, s12, s3, caps = [], [], [], []
    for cg, label, exp in buckets:
        g = sample.loc[sample["calc_group"] == cg]
        cap = float(g["capacity_mtpa"].sum())
        assert abs(cap - exp) < 1e-6, (cg, cap, exp)
        labels.append(label)
        s12.append(float(g["scope_1_2"].sum()) / 1e6)
        s3.append(float(g["scope_3"].sum()) / 1e6)
        caps.append(exp)
    x = np.arange(3)
    fig, ax = plt.subplots(figsize=(9.5, 6.2))
    ax.bar(x, s12, 0.55, label="Scope 1+2", color="#1f4e5f")
    ax.bar(x, s3, 0.55, bottom=s12, label="Scope 3", color="#c47b3a")
    ax.set_ylabel("Annual emissions (MtCO2e / year)")
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
    lifecycle = float(sample["lifecycle_total"].sum(min_count=1)) / 1e6
    if pd.isna(lifecycle):
        lifecycle = 0.0
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

    # 1 Headline
    lines.append("## 1. Headline")
    lines.append("")
    lines.append(f"- **Annual total:** {annual:.1f} MtCO2e/yr")
    lines.append(f"- **Lifecycle total:** {lifecycle:.1f} MtCO2e (excludes legacy facilities)")
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
    lines.append("")

    # 2 By group
    lines.append("## 2. By group")
    lines.append("")
    lines.append(
        "| calc_group | export mtpa | Annual Mt/yr | Lifecycle Mt | "
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
        lines.append(
            f"| {g} | {r['capacity_export_headline_mtpa']:.1f} | "
            f"{r['annual_total_mtco2e_yr']:.1f} | {r['lifecycle_total_mtco2e']:.1f} | "
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
        "| tier | chain scope | mtpa | Annual Mt/yr | CAN / BUNK / FOR |"
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
        "| chain | stages | mtpa | Annual Mt/yr | Lifecycle Mt | CAN / BUNK / FOR |"
    )
    lines.append("|---|---|---|---|---|---|")
    cdef = by_chain.loc[by_chain["scenario"] == DEFAULT_SCENARIO]
    for chain in CHAINS:
        r = cdef.loc[cdef["chain"] == chain].iloc[0]
        lines.append(
            f"| {chain} | {chain_stages[chain]} | {r['capacity_mtpa']:.1f} | "
            f"{r['annual_total_mtco2e_yr']:.1f} | {r['lifecycle_total_mtco2e']:.1f} | "
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
        life_tot = (
            "—"
            if r["is_legacy"] or pd.isna(r["lifecycle_total"])
            else f"{r['lifecycle_total']/1e6:.1f}"
        )
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
    lines.append("| stage | destination | Annual Mt/yr | share |")
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
    lines.append("| scenario | upstream | Annual Mt/yr | Lifecycle Mt | CAN Mt/yr |")
    lines.append("|---|---|---|---|---|")
    for scen in INTENSITY_SCENARIOS:
        s = by_project.loc[
            (~by_project["excluded_from_totals"]) & (by_project["scenario"] == scen)
        ]
        up = inputs["upstream_by_scenario"][scen]
        life = float(s["lifecycle_total"].sum(min_count=1)) / 1e6
        if pd.isna(life):
            life = 0.0
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

    elec = sample.loc[
        sample["liquefaction_drive"].isin(["electric_committed", "electric_planned"])
    ]
    if len(elec):
        delta = 0.17 * float(elec["effective_tonnes"].sum()) / 1e6
        elec_export = float(elec.loc[elec["chain"] == "export", "capacity_mtpa"].sum())
        lines.append(
            f"- **Liquefaction drive** (gas_turbine 0.29 vs electric 0.12): "
            f"{elec_export:.1f} mtpa export currently electric. "
            f"Switching them all to gas_turbine would add about **{delta:.1f} Mt/yr**; "
            f"the reverse (all gas to electric) is not applicable to Phase 1."
        )
    lines.append(
        f"- **Liquefaction drive default** for `not_published` rows: "
        f"`{inputs['liquefaction_drive_default']}` → "
        f"intensity {get_param(params, 'liquefaction_gas_turbine')} tCO2e/t."
    )
    lines.append("")

    # 9 Anything wrong
    lines.append("## 9. Anything that looks wrong")
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
        "- Capacity is never summed across chains (liquefaction ≠ regasification). "
        "Headline capacity is export-chain only."
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
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote review summary: {path}")


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

    for chain, n in EXPECTED_CHAIN_LENGTHS.items():
        assert len(inputs["chains"][chain]) == n
    print("[validate] chain stage counts PASS")

    by_project = compute_by_project(inputs)
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

    # Proposed export: 26 advanced + 12.7 early
    prop_exp = sample.loc[
        (sample["chain"] == "export") & (sample["calc_group"] == "proposed")
    ]
    adv = float(prop_exp.loc[prop_exp["tier"] == "advanced_proposed", "capacity_mtpa"].sum())
    early = float(prop_exp.loc[prop_exp["tier"] == "early_proposed", "capacity_mtpa"].sum())
    assert abs(adv - 26.0) < 1e-6 and abs(early - 12.7) < 1e-6, (adv, early)
    print(f"[validate] proposed export split advanced={adv:.1f} early={early:.1f} PASS")

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

    sj = sample.loc[sample["project_id"] == "saint_john_import_facility"].iloc[0]
    sj_mt = float(sj["annual_total"]) / 1e6
    assert abs(sj_mt - 0.5) < 0.15 and sj_mt < 5
    print(f"[validate] Saint John={sj_mt:.3f} MtCO2e/yr PASS")

    p1 = sample.loc[sample["project_id"] == "lng_canada_phase_1"].iloc[0]
    nameplate_liq = float(p1["capacity_mtpa"]) * float(p1["intensity_liquefaction"])
    assert abs(nameplate_liq - 4.0) <= 0.15
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

    # Group annual totals and headline 159.2
    sdef = summary.loc[summary["scenario"] == DEFAULT_SCENARIO]
    for cg, exp in EXPECTED_ANNUAL_BY_GROUP.items():
        got = float(sdef.loc[sdef["group"] == cg, "annual_total_mtco2e_yr"].iloc[0])
        assert abs(got - exp) < 0.05, (cg, got, exp)
    annual = float(sample["annual_total"].sum())
    annual_mt = annual / 1e6
    assert abs(annual_mt - EXPECTED_HEADLINE_ANNUAL) < 0.05, annual_mt
    print(
        f"[validate] group annuals + headline {annual_mt:.1f} Mt/yr "
        f"(expected {EXPECTED_HEADLINE_ANNUAL}) PASS"
    )

    can = float(sample["canada_territorial"].sum())
    bunk = float(sample["international_bunkers"].sum())
    foreign = float(sample["foreign_territorial"].sum())

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
                "Headline includes all calc_groups (proposed = advanced + early). "
                "Grouped by calc_group, not tier. Capacity is per chain; "
                "headline capacity is export liquefaction only.",
            ),
            ("annual_total_mtco2e_yr", annual_mt),
            ("export_capacity_mtpa", export_total),
            ("canada_territorial_mtco2e_yr", can / 1e6),
            ("international_bunkers_mtco2e_yr", bunk / 1e6),
            ("foreign_territorial_mtco2e_yr", foreign / 1e6),
            ("legacy_projects", ", ".join(legacy_ids)),
            ("inputs_guard", "Inputs opened read-only (rb); writes only under Outputs/."),
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
        by_chain.to_excel(writer, sheet_name="By Chain", index=False)

    write_figure(by_project, FIGURE)
    write_review_summary(SUMMARY_MD, inputs, by_project, summary, by_chain, stages)
    fig_results = build_all_report_figures(
        inputs, by_project, stages, FIGURE_DIR, FIGURE_DATA
    )

    if reg_m is not None and inp_m is not None:
        assert REGISTER.stat().st_mtime == reg_m and INPUTS.stat().st_mtime == inp_m

    print("\n========== COMPLETION ==========")
    print("Group annual totals (measurement_central, 40-year average):")
    for g in GROUPS:
        r = sdef.loc[sdef["group"] == g].iloc[0]
        print(
            f"  {g:20s}  annual={r['annual_total_mtco2e_yr']:6.1f} Mt/yr  "
            f"export_cap={r['capacity_export_headline_mtpa']:5.1f} mtpa"
        )
    print(f"  {'TOTAL':20s}  annual={annual_mt:6.1f} Mt/yr")
    print(
        f"Territorial (average): CAN={can/1e6:.1f}  BUNK={bunk/1e6:.1f}  "
        f"FOR={foreign/1e6:.1f}"
    )
    print("\nReport figures written:")
    for key in ("fig1", "fig2", "fig3", "fig4", "fig5", "fig6", "fig7"):
        r = fig_results[key]
        print(f"  {r['path'].name}")
        print(f"    csv: {r['csv'].name}")
        print(f"    key: {r['key']}")
    print(
        "\nFigure validations: stage sum=headline, territorial sum=headline, "
        "fig3 plateau=fig6 plateau, fig5 central=fig4, CSVs present — all PASS"
    )
    print("No input file was modified.")
    print("================================")


if __name__ == "__main__":
    main()
