"""Eight report figures (PNG @ 200 dpi) plus CSV series under Outputs/figure_data/.

Figures 1–7 are the main set. Figure 8 is the appendix electrification
comparator for Canada-territorial emissions.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from src.inputs import ALL_STAGES, DEFAULT_SCENARIO
from src.model import GROUPS, electrification_counterfactual
from src.scope import BUILD_OUTS, build_out_project_ids, headline_sample
from src.trajectories import (
    annual_series,
    canada_pathway_series,
    panel_lifetime_mt,
)

DPI = 200

# Deck brand palette (sage / forest, gold for emphasis only).
# Same colour always means the same thing across figures.
INK = "#1A1A1A"
MUTED = "#6B7975"
GRID = "#DDE2DC"
FOREST = "#344745"
SAGE = "#8A9B9A"
FOG = "#C2C9BF"
MIST = "#DDE2DC"
LEAF = "#A6B0A1"
GOLD = "#C89A3C"

C = {
    "black": INK,
    "navy": FOREST,
    "blue": FOREST,
    "sky": SAGE,
    "pale": FOG,
    "orange": SAGE,
    "gold": GOLD,
    "green": MUTED,
    "darkgreen": FOREST,
    "red": MUTED,
    "brown": SAGE,
    "grey": MUTED,
    "grid": GRID,
    "text": MUTED,
    "vermillion": SAGE,
    "purple": LEAF,
    "yellow": LEAF,
}

SCENARIO_COLOR = {
    "committed": FOG,
    "committed_plus_advanced": SAGE,
    "full": FOREST,
}
SCENARIO_LABEL = {
    "committed": "Committed",
    "committed_plus_advanced": "Committed plus advanced",
    "full": "Full build-out",
}
STAGE_LABEL = {
    "upstream_production": "Upstream production",
    "pipeline_transport": "Pipeline transport",
    "liquefaction": "Liquefaction",
    "shipping": "Shipping",
    "regasification": "Regasification",
    "combustion": "Combustion",
}
STAGE_COLOR = {
    "upstream_production": MUTED,
    "pipeline_transport": FOG,
    "liquefaction": SAGE,
    "shipping": LEAF,
    "regasification": MIST,
    "combustion": FOREST,
}
TERRITORY_LABEL = {
    "CAN": "Canada",
    "BUNK": "International marine bunkers",
    "FOR": "Importing countries",
}
TERRITORY_COLOR = {
    "CAN": FOREST,
    "BUNK": GOLD,
    "FOR": SAGE,
}
LOCKED_STAGE_SHARE_PCT = {
    "combustion": 78.0,
    "liquefaction": 8.2,
    "upstream_production": 7.9,
    "shipping": 3.2,
    "pipeline_transport": 2.1,
    "regasification": 0.6,
}
LOCKED_TERRITORY_SHARE_PCT = {"CAN": 18.2, "BUNK": 3.2, "FOR": 78.6}

LINE_STYLES = {
    "solid": "-",
    "dashed": "--",
    "dashdot": "-.",
    "dotted": ":",
}


def _setup_style() -> None:
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Liberation Sans", "DejaVu Sans"],
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "text.color": INK,
        "axes.labelcolor": INK,
        "axes.titlecolor": INK,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": INK,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.grid": False,
    })


def _ygrid(ax) -> None:
    ax.yaxis.grid(True, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def _label_on(fill: str) -> str:
    """White on forest bars; ink on pale fills."""
    return "#FFFFFF" if fill.upper() == FOREST.upper() else INK


def tint_hex(hex_color: str, amount: float = 0.45) -> str:
    """Mix a hex colour with white. Same hue, lighter tint (NPV bars)."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r = round(r + (255 - r) * amount)
    g = round(g + (255 - g) * amount)
    b = round(b + (255 - b) * amount)
    return f"#{r:02X}{g:02X}{b:02X}"


def build_out_annual_series(panel: pd.DataFrame, inputs: dict) -> pd.DataFrame:
    """Calendar-year emissions by build-out, 2025–2069. Data selection only."""
    ids = build_out_project_ids(inputs)
    sl = panel.loc[panel["scenario"] == DEFAULT_SCENARIO]
    years = list(range(2025, 2070))
    rows = []
    for year in years:
        ysl = sl.loc[sl["year"] == year]
        rec = {"year": int(year)}
        for name in BUILD_OUTS:
            rec[name] = float(
                ysl.loc[ysl["project_id"].isin(ids[name]), "emissions_mtco2e"].sum()
            )
        rows.append(rec)
    return pd.DataFrame(rows)


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
# Figure 1 — lifetime share by lifecycle stage (manuscript Figure 2(a))
# ---------------------------------------------------------------------------

def figure_1_stage_breakdown(
    stages: pd.DataFrame,
    lifetime_mt: float,
    fig_dir: Path,
    data_dir: Path,
) -> dict:
    df = stages.set_index("stage").loc[list(ALL_STAGES)].reset_index()
    df["share_pct"] = df["share_of_total"] * 100
    df["lifetime_mtco2e"] = df["share_of_total"] * lifetime_mt
    df["stage_label"] = df["stage"].map(STAGE_LABEL)
    export = df[[
        "stage",
        "stage_label",
        "lifetime_mtco2e",
        "share_pct",
    ]].copy()
    _write_csv(export, data_dir / "fig01_stage_breakdown.csv")

    plot = df.iloc[::-1].reset_index(drop=True)
    _setup_style()
    fig, ax = plt.subplots(figsize=(9.0, 5.2))
    y = np.arange(len(plot))
    colors = [STAGE_COLOR[s] for s in plot["stage"]]
    ax.barh(y, plot["share_pct"], color=colors, height=0.65)
    ax.set_yticks(y, plot["stage_label"])
    ax.set_xlabel("Share of lifetime emissions (%)")
    ax.set_title("Full build-out lifetime emissions by lifecycle stage")
    _ygrid(ax)
    for i, r in enumerate(plot.itertuples()):
        ax.text(
            r.share_pct + 1.2,
            i,
            f"{r.lifetime_mtco2e:,.0f} MtCO2e",
            va="center",
            fontsize=9,
            color=INK,
        )
    ax.set_xlim(0, max(plot["share_pct"].max() * 1.28, 100))
    out = fig_dir / "fig01_stage_breakdown.png"
    _save(fig, out)
    share_sum = float(df["share_pct"].sum())
    lifetime_sum = float(df["lifetime_mtco2e"].sum())
    rounded = {r.stage: round(r.share_pct, 1) for r in df.itertuples()}
    return {
        "path": out,
        "csv": data_dir / "fig01_stage_breakdown.csv",
        "key": {
            r.stage_label: f"{r.share_pct:.1f}% ({r.lifetime_mtco2e:,.0f} MtCO2e)"
            for r in df.itertuples()
        },
        "share_sum": share_sum,
        "lifetime_sum": lifetime_sum,
        "rounded_shares": rounded,
        "lifetime_mt": lifetime_mt,
    }


# ---------------------------------------------------------------------------
# Figure 2 — territorial attribution of lifetime emissions (manuscript Figure 2(b))
# ---------------------------------------------------------------------------

def figure_2_territorial_split(
    can: float,
    bunk: float,
    foreign: float,
    headline_mt: float,
    lifetime_mt: float,
    fig_dir: Path,
    data_dir: Path,
) -> dict:
    annual = {"CAN": can, "BUNK": bunk, "FOR": foreign}
    rows = pd.DataFrame([
        {
            "territory": TERRITORY_LABEL[code],
            "code": code,
            "share_pct": 100.0 * annual[code] / headline_mt,
            "lifetime_mtco2e": lifetime_mt * annual[code] / headline_mt,
        }
        for code in ("CAN", "BUNK", "FOR")
    ])
    _write_csv(rows, data_dir / "fig02_territorial_split.csv")

    _setup_style()
    fig, ax = plt.subplots(figsize=(9.2, 3.8))
    left = 0.0
    for r in rows.itertuples():
        ax.barh(
            0,
            r.share_pct,
            left=left,
            height=0.55,
            color=TERRITORY_COLOR[r.code],
        )
        mid = left + r.share_pct / 2
        if r.share_pct > 10:
            ax.text(
                mid,
                0,
                f"{r.share_pct:.1f}%\n{r.lifetime_mtco2e:,.0f} MtCO2e",
                ha="center",
                va="center",
                color=_label_on(TERRITORY_COLOR[r.code]),
                fontsize=9,
                fontweight="bold",
            )
        left += r.share_pct
    ax.set_yticks([])
    ax.set_xlabel("Share of lifetime emissions (%)")
    ax.set_title("Territorial attribution of lifetime emissions")
    ax.set_xlim(0, 100)
    handles = [
        plt.Rectangle((0, 0), 1, 1, color=TERRITORY_COLOR[code])
        for code in ("CAN", "BUNK", "FOR")
    ]
    legend_labels = [
        f"{r.territory} — {r.share_pct:.1f}% ({r.lifetime_mtco2e:,.0f} MtCO2e)"
        for r in rows.itertuples()
    ]
    ax.legend(
        handles,
        legend_labels,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.28),
        ncol=1,
        frameon=False,
        fontsize=9,
    )
    fig.subplots_adjust(bottom=0.42)
    fig.text(
        0.5,
        0.02,
        "Marine bunkers are attributed to no country under UNFCCC reporting",
        ha="center",
        va="bottom",
        fontsize=8,
        color=C["text"],
    )
    out = fig_dir / "fig02_territorial_split.png"
    _save(fig, out)
    rounded = {r.code: round(r.share_pct, 1) for r in rows.itertuples()}
    return {
        "path": out,
        "csv": data_dir / "fig02_territorial_split.csv",
        "key": {
            r.territory: f"{r.share_pct:.1f}% ({r.lifetime_mtco2e:,.0f} MtCO2e)"
            for r in rows.itertuples()
        },
        "share_sum": float(rows["share_pct"].sum()),
        "lifetime_sum": float(rows["lifetime_mtco2e"].sum()),
        "rounded_shares": rounded,
        "lifetime_mt": lifetime_mt,
    }


# ---------------------------------------------------------------------------
# Figure 3 — annual emissions by build-out scenario (manuscript Figure 1)
# ---------------------------------------------------------------------------

def figure_3_three_trajectories(
    inputs: dict,
    panel: pd.DataFrame,
    fig_dir: Path,
    data_dir: Path,
) -> dict:
    df = build_out_annual_series(panel, inputs)
    _write_csv(df, data_dir / "fig03_three_trajectories.csv")

    _setup_style()
    fig, ax = plt.subplots(figsize=(9.0, 5.4))
    markers = {"committed": "o", "committed_plus_advanced": "s", "full": "^"}
    for name in BUILD_OUTS:
        ax.plot(
            df["year"],
            df[name],
            color=SCENARIO_COLOR[name],
            linestyle=LINE_STYLES["solid"],
            linewidth=3.0,
            marker=markers[name],
            markevery=3,
            markersize=6,
            label=SCENARIO_LABEL[name],
        )
    peak_idx = int(df["full"].idxmax())
    peak_year = int(df.loc[peak_idx, "year"])
    peak_mt = float(df.loc[peak_idx, "full"])
    ax.annotate(
        f"{peak_mt:.1f} MtCO2e in {peak_year}",
        xy=(peak_year, peak_mt),
        xytext=(peak_year + 6, peak_mt + 8),
        ha="left",
        fontsize=9,
        color=GOLD,
        arrowprops=dict(arrowstyle="-", color=GOLD, lw=0.8),
    )
    ax.set_xlabel("Year")
    ax.set_ylabel("Annual emissions (MtCO2e/yr)")
    ax.set_title("Annual emissions by build-out scenario")
    ax.set_xlim(2025, 2069)
    ax.set_ylim(bottom=0)
    _ygrid(ax)
    ax.legend(frameon=False, loc="upper left")
    plateaus = {name: float(df[name].max()) for name in BUILD_OUTS}
    out = fig_dir / "fig03_three_trajectories.png"
    _save(fig, out)
    return {
        "path": out,
        "csv": data_dir / "fig03_three_trajectories.csv",
        "key": {SCENARIO_LABEL[k]: round(v, 1) for k, v in plateaus.items()},
        "series": df,
        "plateau_all": plateaus["full"],
        "peak_year": peak_year,
        "peak_mt": peak_mt,
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
        color=INK,
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
    ax.set_ylabel("Annual emissions (MtCO2e/yr)")
    ax.set_title(title)
    ax.set_xlim(2025, 2050)
    ax.set_ylim(bottom=0)
    _ygrid(ax)
    ax.legend(frameon=False, loc="upper right")
    if caption:
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
                "Canada-territorial LNG",
                lng,
                C["blue"],
                LINE_STYLES["dashed"],
                "o",
            )
        ],
        pathway=pathway,
        title="Canada's pathway versus territorial LNG emissions",
        caption="",
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
        ("measurement_central", "Central", C["blue"], LINE_STYLES["dashed"], "o"),
        ("near_term_methane_gwp20", "Near-term methane (GWP20)", C["orange"], LINE_STYLES["dashdot"], "s"),
        ("howarth_high", "Howarth high", C["red"], LINE_STYLES["dotted"], "^"),
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
        title="Canada's pathway versus territorial LNG — upstream sensitivities",
        caption="",
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
                C["navy"],
                LINE_STYLES["dashdot"],
                "^",
            )
        ],
        pathway=pathway,
        title="Canada's pathway versus total LNG emissions",
        caption="",
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
                f"{elec_i:g} only for assets previously classified "
                f"electric_committed or electric_planned: "
                f"{', '.join(cf['claimed_project_ids'])}."
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
    ax1.set_ylabel("Canada-territorial LNG (MtCO2e/yr)")
    ax1.set_title("Life-average")
    _ygrid(ax1)
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
        color=INK,
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
    ax2.set_ylabel("Annual emissions (MtCO2e/yr)")
    ax2.set_title("Calendar-year territorial LNG")
    _ygrid(ax2)
    ax2.legend(frameon=False, loc="upper right", fontsize=8)

    fig.suptitle(
        "Appendix · Canada-territorial LNG if liquefaction ran electric versus gas",
        fontsize=13,
        y=0.98,
    )
    fig.subplots_adjust(bottom=0.08, top=0.86, wspace=0.28)
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

    sample = headline_sample(by_project, DEFAULT_SCENARIO)
    headline = float(sample["annual_total"].sum()) / 1e6
    can = float(sample["canada_territorial"].sum()) / 1e6
    bunk = float(sample["international_bunkers"].sum()) / 1e6
    foreign = float(sample["foreign_territorial"].sum()) / 1e6
    if panel is None:
        raise ValueError("build_all_report_figures requires the headline-scope panel.")
    lifetime_mt = panel_lifetime_mt(panel, DEFAULT_SCENARIO)

    results = {}
    results["fig1"] = figure_1_stage_breakdown(stages, lifetime_mt, fig_dir, data_dir)
    results["fig2"] = figure_2_territorial_split(
        can, bunk, foreign, headline, lifetime_mt, fig_dir, data_dir
    )
    results["fig3"] = figure_3_three_trajectories(inputs, panel, fig_dir, data_dir)
    results["fig4"] = figure_4_pathway_vs_territorial(inputs, fig_dir, data_dir)
    results["fig5"] = figure_5_pathway_three_upstream(
        inputs, fig_dir, data_dir, results["fig4"]["lng_series"]
    )
    results["fig6"] = figure_6_pathway_vs_total(inputs, fig_dir, data_dir)
    results["fig8"] = figure_8_electrification_appendix(
        inputs, by_project, fig_dir, data_dir
    )

    # Validations
    assert abs(results["fig1"]["share_sum"] - 100.0) < 0.05, results["fig1"]["share_sum"]
    assert abs(results["fig1"]["lifetime_sum"] - lifetime_mt) < 0.05, (
        results["fig1"]["lifetime_sum"],
        lifetime_mt,
    )
    for stage, expected in LOCKED_STAGE_SHARE_PCT.items():
        got = results["fig1"]["rounded_shares"][stage]
        assert got == expected, (stage, got, expected)
    print("[validate] fig1 lifetime shares = locked manuscript shares PASS")

    assert abs(results["fig2"]["share_sum"] - 100.0) < 0.05, results["fig2"]["share_sum"]
    assert abs(results["fig2"]["lifetime_sum"] - lifetime_mt) < 0.05, (
        results["fig2"]["lifetime_sum"],
        lifetime_mt,
    )
    for code, expected in LOCKED_TERRITORY_SHARE_PCT.items():
        got = results["fig2"]["rounded_shares"][code]
        assert got == expected, (code, got, expected)
    print("[validate] fig2 territorial shares = locked manuscript shares PASS")

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
        "fig08_electrification_can_average.csv",
        "fig08_electrification_can_by_group.csv",
        "fig08_electrification_can_trajectories.csv",
    ]
    for name in expected_csv:
        assert (data_dir / name).is_file(), name
    print("[validate] all figure CSVs present PASS")

    results["headline_average_mt"] = headline
    return results
