"""Eight report figures (PNG @ 200 dpi) plus CSV series under Outputs/figure_data/.

Figures 1–7 are the main set. Figure 8 is the appendix electrification
comparator for Canada-territorial emissions.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

from src.inputs import DEFAULT_SCENARIO, get_param
from src.model import GROUPS, electrification_counterfactual
from src.report_params import resolve_report_params
from src.trajectories import (
    annual_series,
    canada_pathway_series,
    cumulative_case_series,
    oil_lifecycle_gt,
    panel_lifetime_mt,
)

DPI = 200

# Okabe–Ito colourblind-safe palette
C = {
    "black": "#000000",
    "orange": "#E69F00",
    "sky": "#56B4E9",
    "green": "#009E73",
    "yellow": "#F0E442",
    "blue": "#0072B2",
    "vermillion": "#D55E00",
    "purple": "#CC79A7",
    "grey": "#666666",
}

LINE_STYLES = {
    "solid": "-",
    "dashed": "--",
    "dashdot": "-.",
    "dotted": ":",
}


def _setup_style() -> None:
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Arial"],
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.grid": False,
    })


def _caption(fig, text: str) -> None:
    fig.text(0.5, 0.01, text, ha="center", va="bottom", fontsize=8, color=C["grey"], wrap=True)
    fig.subplots_adjust(bottom=0.14)


def _save(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def _write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


# ---------------------------------------------------------------------------
# Figure 1 — stage breakdown (life-average annual)
# ---------------------------------------------------------------------------

def figure_1_stage_breakdown(
    stages: pd.DataFrame,
    headline_mt: float,
    fig_dir: Path,
    data_dir: Path,
) -> dict:
    df = stages.copy()
    df = df.sort_values("annual_mtco2e_yr", ascending=True)
    df["share_pct"] = df["share_of_total"] * 100
    df["value_kind"] = "life_average_annual_mt"
    df["scenario"] = DEFAULT_SCENARIO
    _write_csv(
        df[[
            "stage",
            "territorial_destination",
            "annual_mtco2e_yr",
            "share_pct",
            "value_kind",
            "scenario",
        ]],
        data_dir / "fig01_stage_breakdown.csv",
    )

    _setup_style()
    fig, ax = plt.subplots(figsize=(9.0, 5.2))
    colors = [C["vermillion"], C["blue"], C["orange"], C["sky"], C["green"], C["purple"]]
    # map by stage after sort
    bar_colors = colors[: len(df)]
    y = np.arange(len(df))
    ax.barh(y, df["annual_mtco2e_yr"], color=bar_colors, height=0.65)
    ax.set_yticks(y, df["stage"].str.replace("_", " "))
    ax.set_xlabel("Life-average annual emissions (MtCO₂e/yr)")
    ax.set_title("Lifecycle emissions by stage")
    for i, r in enumerate(df.itertuples()):
        dest = r.territorial_destination or "—"
        ax.text(
            r.annual_mtco2e_yr + headline_mt * 0.01,
            i,
            f"{r.annual_mtco2e_yr:.1f}  ({r.share_pct:.1f}%)  ·  {dest}",
            va="center",
            fontsize=8,
        )
    ax.set_xlim(0, df["annual_mtco2e_yr"].max() * 1.38)
    _caption(
        fig,
        f"Figure 1 · Scenario: {DEFAULT_SCENARIO}. Values are life_average_annual_mt "
        f"({headline_mt:.1f} MtCO₂e/yr), not the panel-peak headline. "
        "Destination tags from the Chains sheet (CAN / BUNK / FOR).",
    )
    out = fig_dir / "fig01_stage_breakdown.png"
    _save(fig, out)
    stage_sum = float(df["annual_mtco2e_yr"].sum())
    return {
        "path": out,
        "csv": data_dir / "fig01_stage_breakdown.csv",
        "key": {r.stage: round(r.annual_mtco2e_yr, 1) for r in df.itertuples()},
        "stage_sum": stage_sum,
        "headline": headline_mt,
    }


# ---------------------------------------------------------------------------
# Figure 2 — territorial split (life-average annual)
# ---------------------------------------------------------------------------

def figure_2_territorial_split(
    can: float,
    bunk: float,
    foreign: float,
    headline_mt: float,
    fig_dir: Path,
    data_dir: Path,
) -> dict:
    rows = pd.DataFrame([
        {
            "category": "Canada territorial",
            "code": "CAN",
            "annual_mtco2e_yr": can,
            "note": "Counted in Canada's inventory",
        },
        {
            "category": "International bunkers",
            "code": "BUNK",
            "annual_mtco2e_yr": bunk,
            "note": "Attributed to no country under UNFCCC accounting",
        },
        {
            "category": "Foreign territorial",
            "code": "FOR",
            "annual_mtco2e_yr": foreign,
            "note": "Counted in destination countries",
        },
    ])
    rows["share_pct"] = rows["annual_mtco2e_yr"] / headline_mt * 100
    rows["value_kind"] = "life_average_annual_mt"
    rows["scenario"] = DEFAULT_SCENARIO
    _write_csv(rows, data_dir / "fig02_territorial_split.csv")

    _setup_style()
    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    colors = [C["blue"], C["orange"], C["vermillion"]]
    # Single stacked horizontal bar — clearest at three unequal categories
    left = 0.0
    for i, r in enumerate(rows.itertuples()):
        ax.barh(
            0,
            r.annual_mtco2e_yr,
            left=left,
            height=0.55,
            color=colors[i],
            label=f"{r.category} ({r.code})",
        )
        mid = left + r.annual_mtco2e_yr / 2
        if r.annual_mtco2e_yr / headline_mt > 0.08:
            ax.text(
                mid,
                0,
                f"{r.code}\n{r.annual_mtco2e_yr:.1f}",
                ha="center",
                va="center",
                color="white",
                fontsize=9,
                fontweight="bold",
            )
        left += r.annual_mtco2e_yr
    ax.set_yticks([])
    ax.set_xlabel("Life-average annual emissions (MtCO₂e/yr)")
    ax.set_title("Territorial attribution of lifecycle emissions")
    ax.set_xlim(0, headline_mt * 1.02)
    # Legend with hatch-free labels; bunkers note in caption + legend entry
    handles = [
        plt.Rectangle((0, 0), 1, 1, color=colors[i])
        for i in range(3)
    ]
    ax.legend(
        handles,
        [
            f"Canada (CAN) — {can:.1f}",
            f"International bunkers (BUNK) — {bunk:.1f}\n(no country under UNFCCC)",
            f"Foreign (FOR) — {foreign:.1f}",
        ],
        loc="upper center",
        bbox_to_anchor=(0.5, -0.18),
        ncol=3,
        frameon=False,
        fontsize=8,
    )
    fig.subplots_adjust(bottom=0.32)
    fig.text(
        0.5,
        0.02,
        f"Figure 2 · Scenario: {DEFAULT_SCENARIO}. Values are life_average_annual_mt "
        f"({headline_mt:.1f} MtCO₂e/yr), not the panel-peak headline. International bunkers are attributed "
        "to no country under UNFCCC accounting.",
        ha="center",
        va="bottom",
        fontsize=8,
        color=C["grey"],
    )
    out = fig_dir / "fig02_territorial_split.png"
    _save(fig, out)
    return {
        "path": out,
        "csv": data_dir / "fig02_territorial_split.csv",
        "key": {"CAN": round(can, 1), "BUNK": round(bunk, 1), "FOR": round(foreign, 1)},
        "sum": can + bunk + foreign,
        "headline": headline_mt,
    }


# ---------------------------------------------------------------------------
# Figure 3 — three cumulative trajectories
# ---------------------------------------------------------------------------

def figure_3_three_trajectories(
    inputs: dict,
    fig_dir: Path,
    data_dir: Path,
) -> dict:
    df = cumulative_case_series(inputs, DEFAULT_SCENARIO, canada_only=False)
    df["value_kind"] = "calendar-year annual"
    _write_csv(df, data_dir / "fig03_three_trajectories.csv")

    _setup_style()
    fig, ax = plt.subplots(figsize=(9.0, 5.4))
    series = [
        ("operating", "Operating only", C["blue"], LINE_STYLES["solid"], "o"),
        ("plus_under_construction", "Operating + under construction", C["green"], LINE_STYLES["dashed"], "s"),
        ("plus_proposed", "All calc_groups (+ proposed)", C["vermillion"], LINE_STYLES["dashdot"], "^"),
    ]
    for col, label, color, ls, marker in series:
        ax.plot(
            df["year"],
            df[col],
            color=color,
            linestyle=ls,
            linewidth=2.0,
            marker=marker,
            markevery=3,
            markersize=5,
            label=label,
        )
    ax.set_xlabel("Year")
    ax.set_ylabel("Annual emissions (MtCO₂e/yr)")
    ax.set_title("Canada LNG emissions trajectories to 2050")
    ax.set_xlim(2025, 2050)
    ax.legend(frameon=False, loc="upper left")
    plateaus = {col: float(df[col].max()) for col, *_ in series}
    _caption(
        fig,
        f"Figure 3 · Scenario: {DEFAULT_SCENARIO}. Calendar-year annual values "
        "(not the life-average). Membership from calc_group. "
        f"Plateaus ≈ {plateaus['operating']:.0f} / "
        f"{plateaus['plus_under_construction']:.0f} / "
        f"{plateaus['plus_proposed']:.0f} MtCO₂e/yr.",
    )
    out = fig_dir / "fig03_three_trajectories.png"
    _save(fig, out)
    return {
        "path": out,
        "csv": data_dir / "fig03_three_trajectories.csv",
        "key": {k: round(v, 1) for k, v in plateaus.items()},
        "series": df,
        "plateau_all": plateaus["plus_proposed"],
    }


# ---------------------------------------------------------------------------
# Figures 4–6 — pathway overlays
# ---------------------------------------------------------------------------

def _pathway_figure(
    *,
    lng_lines: list[tuple[str, pd.Series, str, str, str]],
    pathway: pd.DataFrame,
    title: str,
    caption: str,
    out_name: str,
    fig_dir: Path,
    data_dir: Path,
    csv_df: pd.DataFrame,
) -> Path:
    _write_csv(csv_df, data_dir / f"{out_name}.csv")
    _setup_style()
    fig, ax = plt.subplots(figsize=(9.0, 5.4))
    ax.plot(
        pathway["year"],
        pathway["canada_pathway_mtco2e_yr"],
        color=C["black"],
        linestyle=LINE_STYLES["solid"],
        linewidth=2.2,
        label="Canada legislated pathway",
    )
    for label, series, color, ls, marker in lng_lines:
        ax.plot(
            series.index,
            series.values,
            color=color,
            linestyle=ls,
            linewidth=2.0,
            marker=marker,
            markevery=3,
            markersize=5,
            label=label,
        )
    ax.set_xlabel("Year")
    ax.set_ylabel("Annual emissions (MtCO₂e/yr)")
    ax.set_title(title)
    ax.set_xlim(2025, 2050)
    ax.set_ylim(bottom=0)
    ax.legend(frameon=False, loc="upper right")
    _caption(fig, caption)
    out = fig_dir / f"{out_name}.png"
    _save(fig, out)
    return out


def figure_4_pathway_vs_territorial(
    inputs: dict,
    fig_dir: Path,
    data_dir: Path,
) -> dict:
    pathway = canada_pathway_series(inputs["params"])
    lng = annual_series(
        inputs,
        DEFAULT_SCENARIO,
        calc_groups=GROUPS,
        canada_only=True,
    ).set_index("year")["annual_mtco2e_yr"]
    csv = pathway.merge(
        lng.rename("canada_territorial_lng_mtco2e_yr"),
        left_on="year",
        right_index=True,
    )
    csv["scenario"] = DEFAULT_SCENARIO
    csv["value_kind"] = "calendar-year annual"
    path = _pathway_figure(
        lng_lines=[
            (
                "Canada-territorial LNG (CAN stages)",
                lng,
                C["blue"],
                LINE_STYLES["dashed"],
                "o",
            )
        ],
        pathway=pathway,
        title="Canada's pathway versus territorial LNG emissions",
        caption=(
            f"Figure 4 · Scenario: {DEFAULT_SCENARIO}. Calendar-year annual values "
            "(not the life-average). LNG line is stages tagged CAN only. "
            "Pathway interpolated from Parameters milestones "
            "(694 / 607 / 455 / 417 / 0)."
        ),
        out_name="fig04_pathway_vs_territorial_lng",
        fig_dir=fig_dir,
        data_dir=data_dir,
        csv_df=csv,
    )
    return {
        "path": path,
        "csv": data_dir / "fig04_pathway_vs_territorial_lng.csv",
        "key": {"lng_plateau": round(float(lng.max()), 1)},
        "lng_series": lng,
    }


def figure_5_pathway_three_upstream(
    inputs: dict,
    fig_dir: Path,
    data_dir: Path,
    fig4_lng: pd.Series,
) -> dict:
    pathway = canada_pathway_series(inputs["params"])
    scenarios = [
        ("measurement_central", "measurement_central", C["blue"], LINE_STYLES["dashed"], "o"),
        ("near_term_methane_gwp20", "near_term_methane_gwp20", C["orange"], LINE_STYLES["dashdot"], "s"),
        ("howarth_high", "howarth_high", C["vermillion"], LINE_STYLES["dotted"], "^"),
    ]
    csv = pathway.copy()
    lng_lines = []
    plateaus = {}
    for scen, label, color, ls, marker in scenarios:
        s = annual_series(
            inputs, scen, calc_groups=GROUPS, canada_only=True
        ).set_index("year")["annual_mtco2e_yr"]
        csv[f"lng_can_{scen}"] = csv["year"].map(s)
        lng_lines.append((label, s, color, ls, marker))
        plateaus[scen] = float(s.max())
    csv["value_kind"] = "calendar-year annual"
    path = _pathway_figure(
        lng_lines=lng_lines,
        pathway=pathway,
        title="Canada's pathway versus territorial LNG — upstream cases",
        caption=(
            "Figure 5 · Calendar-year annual values (not the life-average). "
            "Canada pathway unchanged; LNG (CAN stages) under three upstream scenarios. "
            f"Territorial plateaus ≈ {plateaus['measurement_central']:.0f} / "
            f"{plateaus['near_term_methane_gwp20']:.0f} / "
            f"{plateaus['howarth_high']:.0f} MtCO₂e/yr."
        ),
        out_name="fig05_pathway_three_upstream",
        fig_dir=fig_dir,
        data_dir=data_dir,
        csv_df=csv,
    )
    central = annual_series(
        inputs, DEFAULT_SCENARIO, calc_groups=GROUPS, canada_only=True
    ).set_index("year")["annual_mtco2e_yr"]
    return {
        "path": path,
        "csv": data_dir / "fig05_pathway_three_upstream.csv",
        "key": {k: round(v, 1) for k, v in plateaus.items()},
        "central_series": central,
        "fig4_match_max_abs": float((central - fig4_lng).abs().max()),
    }


def figure_6_pathway_vs_total(
    inputs: dict,
    fig_dir: Path,
    data_dir: Path,
) -> dict:
    pathway = canada_pathway_series(inputs["params"])
    lng = annual_series(
        inputs,
        DEFAULT_SCENARIO,
        calc_groups=GROUPS,
        canada_only=False,
    ).set_index("year")["annual_mtco2e_yr"]
    csv = pathway.merge(
        lng.rename("total_lng_mtco2e_yr"),
        left_on="year",
        right_index=True,
    )
    csv["scenario"] = DEFAULT_SCENARIO
    csv["value_kind"] = "calendar-year annual"
    path = _pathway_figure(
        lng_lines=[
            (
                "Total LNG (all territories)",
                lng,
                C["vermillion"],
                LINE_STYLES["dashdot"],
                "^",
            )
        ],
        pathway=pathway,
        title="Canada's pathway versus total LNG emissions",
        caption=(
            f"Figure 6 · Scenario: {DEFAULT_SCENARIO}. Calendar-year annual values "
            "(not the life-average). Total includes CAN, BUNK and FOR stages. "
            f"Plateau ≈ {float(lng.max()):.0f} MtCO₂e/yr."
        ),
        out_name="fig06_pathway_vs_total_lng",
        fig_dir=fig_dir,
        data_dir=data_dir,
        csv_df=csv,
    )
    return {
        "path": path,
        "csv": data_dir / "fig06_pathway_vs_total_lng.csv",
        "key": {"lng_plateau": round(float(lng.max()), 1)},
        "plateau": float(lng.max()),
    }


# ---------------------------------------------------------------------------
# Figure 7 — oil infrastructure comparison (lifecycle Gt, calendar panel)
# ---------------------------------------------------------------------------

def figure_7_oil_comparison(
    by_project: pd.DataFrame,
    inputs: dict,
    fig_dir: Path,
    data_dir: Path,
    panel: pd.DataFrame | None = None,
) -> dict:
    sample = by_project.loc[
        (~by_project["excluded_from_totals"])
        & (by_project["scenario"] == DEFAULT_SCENARIO)
    ]
    if panel is not None:
        lng_all = panel_lifetime_mt(panel, DEFAULT_SCENARIO) / 1e3
        lng_prop = panel_lifetime_mt(
            panel, DEFAULT_SCENARIO, calc_group="proposed"
        ) / 1e3
        method_note = "calendar panel sum (excludes legacy)"
    else:
        lng_all = float(sample["lifecycle_total"].sum(min_count=1)) / 1e9
        if pd.isna(lng_all):
            lng_all = 0.0
        lng_prop = float(
            sample.loc[sample["calc_group"] == "proposed", "lifecycle_total"].sum(
                min_count=1
            )
        ) / 1e9
        if pd.isna(lng_prop):
            lng_prop = 0.0
        method_note = "model lifecycle total (excludes legacy nulls)"

    params = inputs["params"]
    report, audit = resolve_report_params(params)
    audit = [
        {
            "parameter": "assumed_first_export_year_if_missing",
            "value": int(get_param(params, "assumed_first_export_year_if_missing")),
            "unit": "year",
            "source": (
                "Parameters sheet. Fills blank Asset Register first_export_year "
                "for six in-scope assets. The published panel tail is this placeholder."
            ),
            "origin": "Parameters sheet",
            "unvalidated": False,
        }
    ] + audit
    tmx_full_bpd = float(get_param(params, "tmx_total_system_bpd"))
    tmx_exp_bpd = float(report["tmx_expansion_bpd"])
    ab_bc_bpd = float(report["alberta_bc_bitumen_pipeline_bpd"])
    ab_label = str(report["alberta_bc_bitumen_pipeline_label"])

    tmx_full = oil_lifecycle_gt(tmx_full_bpd, params)
    tmx_exp = oil_lifecycle_gt(tmx_exp_bpd, params)
    ab_bc = oil_lifecycle_gt(ab_bc_bpd, params)

    rows = pd.DataFrame([
        {
            "item": "Canadian LNG, all assets",
            "lifecycle_gtco2e": lng_all,
            "method": method_note,
            "unvalidated": False,
            "capacity_note": "export headline capacity separate; emissions all chains",
        },
        {
            "item": "Canadian LNG, proposed only",
            "lifecycle_gtco2e": lng_prop,
            "method": method_note + ", calc_group=proposed",
            "unvalidated": False,
            "capacity_note": "",
        },
        {
            "item": f"TMX full system ({tmx_full_bpd:,.0f} bpd)",
            "lifecycle_gtco2e": tmx_full,
            "method": "bpd × tmx_oil_lifecycle_per_barrel × 365 × lifecycle_years_default",
            "unvalidated": False,
            "capacity_note": f"tmx_total_system_bpd={tmx_full_bpd}",
        },
        {
            "item": f"TMX expansion only ({tmx_exp_bpd:,.0f} bpd)",
            "lifecycle_gtco2e": tmx_exp,
            "method": "same oil method; tmx_expansion_bpd",
            "unvalidated": False,
            "capacity_note": f"tmx_expansion_bpd={tmx_exp_bpd}",
        },
        {
            "item": ab_label,
            "lifecycle_gtco2e": ab_bc,
            "method": "same oil method; alberta_bc_bitumen_pipeline_bpd — NEW, UNVALIDATED",
            "unvalidated": True,
            "capacity_note": (
                f"alberta_bc_bitumen_pipeline_bpd={ab_bc_bpd}; "
                "MPO submission 2 July 2026; Bruderheim–Delta BC"
            ),
        },
    ])
    rows["value_kind"] = "lifecycle total (GtCO₂e)"
    rows["scenario"] = DEFAULT_SCENARIO
    _write_csv(rows, data_dir / "fig07_oil_infrastructure_comparison.csv")
    _write_csv(pd.DataFrame(audit), data_dir / "fig07_report_parameters_used.csv")

    _setup_style()
    fig, ax = plt.subplots(figsize=(9.2, 5.0))
    plot_df = rows.iloc[::-1].reset_index(drop=True)
    colors = []
    for u in plot_df["unvalidated"]:
        colors.append(C["orange"] if u else C["blue"])
    y = np.arange(len(plot_df))
    ax.barh(y, plot_df["lifecycle_gtco2e"], color=colors, height=0.62)
    # hatch the unvalidated bar so colour is not the only cue
    for i, r in enumerate(plot_df.itertuples()):
        if r.unvalidated:
            ax.barh(
                i,
                r.lifecycle_gtco2e,
                height=0.62,
                facecolor="none",
                edgecolor=C["black"],
                hatch="///",
                linewidth=0.8,
            )
        ax.text(
            r.lifecycle_gtco2e + 0.08,
            i,
            f"{r.lifecycle_gtco2e:.2f} Gt",
            va="center",
            fontsize=9,
        )
    ax.set_yticks(y, plot_df["item"])
    ax.set_xlabel("Lifecycle emissions (GtCO₂e)")
    ax.set_title("Lifecycle comparison: Canadian LNG and oil pipeline infrastructure")
    ax.set_xlim(0, plot_df["lifecycle_gtco2e"].max() * 1.18)
    legend_elems = [
        Line2D([0], [0], color=C["blue"], lw=8, label="Published / model basis"),
        Line2D(
            [0], [0], color=C["orange"], lw=8, label="New — unvalidated (hatched)"
        ),
    ]
    ax.legend(handles=legend_elems, frameon=False, loc="lower right")
    _caption(
        fig,
        f"Figure 7 · Scenario: {DEFAULT_SCENARIO}. Lifecycle totals (GtCO₂e), not "
        "calendar-year trajectories. LNG from the calendar-panel lifetime sum "
        "(legacy facilities contribute annual only and are excluded from Gt). "
        "Oil rows use Parameters tmx_oil_lifecycle_per_barrel. "
        "Alberta–BC bitumen pipeline is NEW and UNVALIDATED.",
    )
    out = fig_dir / "fig07_oil_infrastructure_comparison.png"
    _save(fig, out)
    return {
        "path": out,
        "csv": data_dir / "fig07_oil_infrastructure_comparison.csv",
        "key": {
            "lng_all_gt": round(lng_all, 2),
            "lng_proposed_gt": round(lng_prop, 2),
            "tmx_full_gt": round(tmx_full, 2),
            "tmx_expansion_gt": round(tmx_exp, 2),
            "alberta_bc_gt": round(ab_bc, 2),
            "alberta_bc_unvalidated": True,
        },
    }


# ---------------------------------------------------------------------------
# Figure 8 — appendix: gas vs electric, Canada territorial
# ---------------------------------------------------------------------------

def figure_8_electrification_appendix(
    inputs: dict,
    by_project: pd.DataFrame,
    fig_dir: Path,
    data_dir: Path,
) -> dict:
    cf = electrification_counterfactual(inputs, by_project)
    head = cf["summary"].loc[cf["summary"]["slice"] == "headline"].iloc[0]
    gas = float(head["canada_territorial_gas_mtco2e_yr"])
    claimed = float(head["canada_territorial_claimed_electric_mtco2e_yr"])
    alle = float(head["canada_territorial_all_electric_mtco2e_yr"])
    gas_i = cf["gas_intensity"]
    elec_i = cf["electric_intensity"]

    group_rows = []
    for g in GROUPS:
        r = cf["summary"].loc[cf["summary"]["slice"] == g].iloc[0]
        group_rows.append({
            "calc_group": g,
            "canada_territorial_gas_mtco2e_yr": float(r["canada_territorial_gas_mtco2e_yr"]),
            "canada_territorial_claimed_electric_mtco2e_yr": float(
                r["canada_territorial_claimed_electric_mtco2e_yr"]
            ),
            "canada_territorial_all_electric_mtco2e_yr": float(
                r["canada_territorial_all_electric_mtco2e_yr"]
            ),
        })
    groups_df = pd.DataFrame(group_rows)

    pathway = canada_pathway_series(inputs["params"])
    gas_s = annual_series(
        inputs, DEFAULT_SCENARIO, calc_groups=GROUPS, canada_only=True, liquefaction_mode="gas"
    ).set_index("year")["annual_mtco2e_yr"]
    claimed_s = annual_series(
        inputs,
        DEFAULT_SCENARIO,
        calc_groups=GROUPS,
        canada_only=True,
        liquefaction_mode="claimed_electric",
    ).set_index("year")["annual_mtco2e_yr"]
    elec_s = annual_series(
        inputs,
        DEFAULT_SCENARIO,
        calc_groups=GROUPS,
        canada_only=True,
        liquefaction_mode="all_electric",
    ).set_index("year")["annual_mtco2e_yr"]
    traj = pathway.merge(gas_s.rename("can_gas_mtco2e_yr"), left_on="year", right_index=True)
    traj = traj.merge(
        claimed_s.rename("can_claimed_electric_mtco2e_yr"), left_on="year", right_index=True
    )
    traj = traj.merge(
        elec_s.rename("can_all_electric_mtco2e_yr"), left_on="year", right_index=True
    )
    traj["scenario"] = DEFAULT_SCENARIO
    traj["value_kind"] = "calendar-year annual, Canada territorial only"
    _write_csv(traj, data_dir / "fig08_electrification_can_trajectories.csv")

    avg_rows = pd.DataFrame([
        {
            "case": "gas_turbine_current",
            "label": "Gas turbine (current)",
            "canada_territorial_mtco2e_yr": gas,
            "share_of_national_inventory": float(head["share_of_national_inventory_gas"]),
            "note": f"Headline. Liquefaction {gas_i:.2f} tCO2e/t for every terminal.",
        },
        {
            "case": "claimed_electric_delivered",
            "label": "If claimed electric drive is delivered",
            "canada_territorial_mtco2e_yr": claimed,
            "share_of_national_inventory": claimed / cf["national"],
            "note": (
                "0.12 only for assets previously classified electric_committed or "
                f"electric_planned: {', '.join(cf['claimed_project_ids'])}."
            ),
        },
        {
            "case": "all_terminals_electric",
            "label": "If every terminal ran electric",
            "canada_territorial_mtco2e_yr": alle,
            "share_of_national_inventory": float(
                head["share_of_national_inventory_all_electric"]
            ),
            "note": f"Liquefaction {elec_i:.2f} tCO2e/t on every chain that includes it.",
        },
    ])
    avg_rows["delta_vs_gas_mtco2e_yr"] = avg_rows["canada_territorial_mtco2e_yr"] - gas
    avg_rows["value_kind"] = "life_average_annual_mt"
    avg_rows["scenario"] = DEFAULT_SCENARIO
    _write_csv(avg_rows, data_dir / "fig08_electrification_can_average.csv")
    _write_csv(groups_df, data_dir / "fig08_electrification_can_by_group.csv")

    _setup_style()
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(13.2, 6.2), gridspec_kw={"width_ratios": [1.05, 1.25]}
    )
    cases = [
        ("Gas turbine\n(current)", gas, C["vermillion"]),
        ("Claimed electric\ndelivered", claimed, C["orange"]),
        ("All terminals\nelectric", alle, C["blue"]),
    ]
    x = np.arange(len(cases))
    ax1.bar(x, [c[1] for c in cases], color=[c[2] for c in cases], width=0.62)
    ax1.set_xticks(x, [c[0] for c in cases])
    ax1.set_ylabel("Canada-territorial LNG (MtCO₂e/yr)")
    ax1.set_title("Life-average")
    ymax = max(c[1] for c in cases)
    ax1.set_ylim(0, ymax * 1.22)
    for i, (label, val, _col) in enumerate(cases):
        delta = val - gas
        extra = "" if i == 0 else f"\n({delta:+.1f})"
        ax1.text(i, val + ymax * 0.03, f"{val:.1f}{extra}", ha="center", va="bottom", fontsize=9)
    ax1.axhline(gas, color=C["grey"], linewidth=0.6, linestyle=":")

    ax2.plot(
        traj["year"],
        traj["canada_pathway_mtco2e_yr"],
        color=C["black"],
        linestyle=LINE_STYLES["solid"],
        linewidth=1.6,
        label="Canada legislated pathway",
    )
    ax2.plot(
        traj["year"],
        traj["can_gas_mtco2e_yr"],
        color=C["vermillion"],
        linestyle=LINE_STYLES["solid"],
        linewidth=2.0,
        label="CAN LNG, gas turbine",
    )
    ax2.plot(
        traj["year"],
        traj["can_claimed_electric_mtco2e_yr"],
        color=C["orange"],
        linestyle=LINE_STYLES["dashed"],
        linewidth=2.0,
        label="CAN LNG, claimed electric",
    )
    ax2.plot(
        traj["year"],
        traj["can_all_electric_mtco2e_yr"],
        color=C["blue"],
        linestyle=LINE_STYLES["dashdot"],
        linewidth=2.0,
        label="CAN LNG, all electric",
    )
    ax2.set_xlim(2025, 2050)
    ax2.set_ylim(bottom=0)
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Annual emissions (MtCO₂e/yr)")
    ax2.set_title("Calendar-year territorial LNG")
    ax2.legend(frameon=False, loc="upper right", fontsize=8)

    fig.suptitle(
        "Appendix · Canada-territorial LNG if liquefaction ran electric versus gas",
        fontsize=13,
        y=0.98,
    )
    fig.text(
        0.5,
        0.01,
        (
            f"Appendix figure · Scenario: {DEFAULT_SCENARIO}. Liquefaction is tagged CAN, "
            f"so the {gas_i:.2f}→{elec_i:.2f} tCO2e/t switch lands entirely in Canada. "
            f"Headline case is gas turbine for every terminal. Claimed-electric restores "
            f"0.12 only where the register previously recorded electric_committed or "
            f"electric_planned ({len(cf['claimed_project_ids'])} assets). "
            "Electrification is not assumed in the main results."
        ),
        ha="center",
        va="bottom",
        fontsize=8,
        color=C["grey"],
        wrap=True,
    )
    fig.subplots_adjust(bottom=0.16, top=0.86, wspace=0.28)
    out = fig_dir / "fig08_electrification_canada_territorial.png"
    _save(fig, out)

    plateau_gas = float(gas_s.max())
    plateau_elec = float(elec_s.max())
    assert alle < gas - 0.05
    assert claimed <= gas + 1e-9
    assert claimed >= alle - 1e-9
    print("[validate] fig8 electric CAN < gas CAN PASS")

    return {
        "path": out,
        "csv": data_dir / "fig08_electrification_can_average.csv",
        "key": {
            "can_gas": round(gas, 1),
            "can_claimed_electric": round(claimed, 1),
            "can_all_electric": round(alle, 1),
            "delta_all_electric": round(alle - gas, 1),
            "plateau_gas": round(plateau_gas, 1),
            "plateau_all_electric": round(plateau_elec, 1),
            "claimed_assets": len(cf["claimed_project_ids"]),
        },
        "counterfactual": cf,
        "traj": traj,
    }


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def build_all_report_figures(
    inputs: dict,
    by_project: pd.DataFrame,
    stages: pd.DataFrame,
    fig_dir: Path,
    data_dir: Path,
    panel: pd.DataFrame | None = None,
) -> dict:
    fig_dir = Path(fig_dir)
    data_dir = Path(data_dir)
    fig_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    sample = by_project.loc[
        (~by_project["excluded_from_totals"])
        & (by_project["scenario"] == DEFAULT_SCENARIO)
    ]
    headline = float(sample["annual_total"].sum()) / 1e6
    can = float(sample["canada_territorial"].sum()) / 1e6
    bunk = float(sample["international_bunkers"].sum()) / 1e6
    foreign = float(sample["foreign_territorial"].sum()) / 1e6

    results = {}
    results["fig1"] = figure_1_stage_breakdown(stages, headline, fig_dir, data_dir)
    results["fig2"] = figure_2_territorial_split(
        can, bunk, foreign, headline, fig_dir, data_dir
    )
    results["fig3"] = figure_3_three_trajectories(inputs, fig_dir, data_dir)
    results["fig4"] = figure_4_pathway_vs_territorial(inputs, fig_dir, data_dir)
    results["fig5"] = figure_5_pathway_three_upstream(
        inputs, fig_dir, data_dir, results["fig4"]["lng_series"]
    )
    results["fig6"] = figure_6_pathway_vs_total(inputs, fig_dir, data_dir)
    results["fig7"] = figure_7_oil_comparison(
        by_project, inputs, fig_dir, data_dir, panel=panel
    )
    results["fig8"] = figure_8_electrification_appendix(
        inputs, by_project, fig_dir, data_dir
    )

    # Validations
    assert abs(results["fig1"]["stage_sum"] - headline) < 0.05, (
        results["fig1"]["stage_sum"],
        headline,
    )
    print("[validate] fig1 stage totals = headline PASS")

    assert abs(results["fig2"]["sum"] - headline) < 0.05, (
        results["fig2"]["sum"],
        headline,
    )
    print("[validate] fig2 territorial sum = headline PASS")

    assert abs(results["fig3"]["plateau_all"] - results["fig6"]["plateau"]) < 0.05, (
        results["fig3"]["plateau_all"],
        results["fig6"]["plateau"],
    )
    print("[validate] fig3 third plateau = fig6 plateau PASS")

    assert results["fig5"]["fig4_match_max_abs"] < 1e-9, results["fig5"]["fig4_match_max_abs"]
    print("[validate] fig5 central line = fig4 PASS")

    expected_csv = [
        "fig01_stage_breakdown.csv",
        "fig02_territorial_split.csv",
        "fig03_three_trajectories.csv",
        "fig04_pathway_vs_territorial_lng.csv",
        "fig05_pathway_three_upstream.csv",
        "fig06_pathway_vs_total_lng.csv",
        "fig07_oil_infrastructure_comparison.csv",
        "fig08_electrification_can_average.csv",
        "fig08_electrification_can_by_group.csv",
        "fig08_electrification_can_trajectories.csv",
    ]
    for name in expected_csv:
        assert (data_dir / name).is_file(), name
    print("[validate] all figure CSVs present PASS")

    results["headline_average_mt"] = headline
    return results
