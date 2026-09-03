"""Lifecycle intensity comparison against published LNG studies.

This model's export-chain intensity is the sum of Emission Factors centrals.
Comparators are included only when the system boundary can be read from the
source. Where a comparator omits combustion or stops at the terminal, this
model is recomputed on that same stage set. GWP20 and GWP100 are never placed
on the same axis. Ranges are shown as published; arithmetic midpoints are not
substituted.

MacKay (2021) and Johnson (2023) are methane-measurement papers, not LNG LCAs.
Di Lullo's published work used around this model is a pipeline construction/
operation LCA or crude WTT — not an LNG lifecycle total. Those three are
recorded as excluded, not guessed onto the chart.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.figures_report import C, _save, _setup_style, _write_csv
from src.inputs import ALL_STAGES, get_param


def _lca_comparators(params: dict) -> dict:
    """Howarth / Roman-White / Balcombe comparators from the Parameters sheet."""
    return {
        "howarth": (
            float(get_param(params, "lca_howarth_gwp20_low")),
            float(get_param(params, "lca_howarth_gwp20_high")),
        ),
        "roman_white": (
            float(get_param(params, "lca_roman_white_w2r_p025")),
            float(get_param(params, "lca_roman_white_w2r_expected")),
            float(get_param(params, "lca_roman_white_w2r_p975")),
        ),
        "balcombe_g": (
            float(get_param(params, "lca_balcombe_lng_stages_low_g_per_mj_hhv")),
            float(get_param(params, "lca_balcombe_lng_stages_high_g_per_mj_hhv")),
        ),
        "hhv": float(get_param(params, "lca_hhv_mj_per_kg")),
    }


def export_stage_intensity(inputs: dict) -> dict[str, float]:
    """Central stage intensities on the **British Columbia shipping basis**.

    The headline model scales shipping per asset by `route_distance_nm /
    route_bc_to_northeast_asia_nm`. This comparison deliberately does not: the
    published studies are single-route figures, so comparing them against a
    fleet-average of Pacific and Atlantic routes would not be like for like.
    Shipping here is the unscaled 0.12 BC-to-north-east-Asia factor.
    """
    factors = inputs["factors"]
    return {stage: float(factors.loc[stage, "central"]) for stage in ALL_STAGES}


def intensity_on_stages(stage_i: dict[str, float], stages: tuple[str, ...]) -> float:
    return float(sum(stage_i[s] for s in stages))


def build_lca_comparison(inputs: dict) -> dict[str, pd.DataFrame]:
    si = export_stage_intensity(inputs)
    liq_param = float(get_param(inputs["params"], "liquefaction_gas_turbine"))
    if abs(si["liquefaction"] - liq_param) > 1e-12:
        raise AssertionError(
            f"Liquefaction central is {si['liquefaction']}, not {liq_param}."
        )
    cmp = _lca_comparators(inputs["params"])
    howarth = cmp["howarth"]
    roman_white = cmp["roman_white"]
    hhv = cmp["hhv"]
    w2r_stages = (
        "upstream_production",
        "pipeline_transport",
        "liquefaction",
        "shipping",
        "regasification",
    )
    lng_only = ("liquefaction", "shipping", "regasification")
    model_full = intensity_on_stages(si, ALL_STAGES)
    model_w2r = intensity_on_stages(si, w2r_stages)
    model_lng = intensity_on_stages(si, lng_only)
    balcombe_t = tuple(g * hhv / 1000.0 for g in cmp["balcombe_g"])

    included = pd.DataFrame(
        [
            {
                "study": "This model (export chain)",
                "display_label": "This model",
                "year": 2026,
                "geography": "Canada",
                "system_boundary": "Well → combustion (GWP100)",
                "upstream_tCO2e_per_t": si["upstream_production"],
                "combustion_included": True,
                "shipping_included": True,
                "total_low": model_full,
                "total_central": model_full,
                "total_high": model_full,
                "gwp": "GWP100",
                "axis_group": "full_gwp100",
                "is_this_model": True,
                "source": "Emission Factors centrals; export chain",
                "alignment_note": (
                    "Headline export-chain intensity. Combustion 2.75 t/t. "
                    "No destination-city distribution leak."
                ),
            },
            {
                "study": "This model, aligned to Roman-White 2021",
                "display_label": "This model (aligned)",
                "year": 2026,
                "geography": "Canada",
                "system_boundary": "Well → regasification (no combustion, GWP100)",
                "upstream_tCO2e_per_t": si["upstream_production"],
                "combustion_included": False,
                "shipping_included": True,
                "total_low": model_w2r,
                "total_central": model_w2r,
                "total_high": model_w2r,
                "gwp": "GWP100",
                "axis_group": "w2r_gwp100",
                "is_this_model": True,
                "source": "Same factors; combustion dropped",
                "alignment_note": (
                    "Same stages as Roman-White Table 1 cradle→regas. "
                    "This model's shipping 0.12 is shorter than China-bound."
                ),
            },
            {
                "study": "Roman-White et al. 2021 (Balcombe co-author)",
                "display_label": "Roman-White 2021",
                "year": 2021,
                "geography": "US Gulf Coast → China (Cheniere SPL)",
                "system_boundary": "Well → regasification (no combustion, GWP100)",
                "upstream_tCO2e_per_t": np.nan,
                "combustion_included": False,
                "shipping_included": True,
                "total_low": roman_white[0],
                "total_central": roman_white[1],
                "total_high": roman_white[2],
                "gwp": "GWP100",
                "axis_group": "w2r_gwp100",
                "is_this_model": False,
                "source": (
                    "ACS Sustainable Chem. Eng. 9:10857; Table 1 China; "
                    "P2.5 / expected / P97.5"
                ),
                "alignment_note": (
                    "Supplier-specific Cheniere SPL to China. "
                    "Expected is their published statistic, not a midpoint. "
                    "Combustion only appears on the kg/MWh power-plant boundary, "
                    "which is a different functional unit and is not plotted."
                ),
            },
            {
                "study": "This model, aligned to Balcombe 2016 LNG stages",
                "display_label": "This model (aligned)",
                "year": 2026,
                "geography": "Canada",
                "system_boundary": "Liquefaction + shipping + regasification (GWP100)",
                "upstream_tCO2e_per_t": np.nan,
                "combustion_included": False,
                "shipping_included": True,
                "total_low": model_lng,
                "total_central": model_lng,
                "total_high": model_lng,
                "gwp": "GWP100",
                "axis_group": "lng_stages_gwp100",
                "is_this_model": True,
                "source": "Same factors; upstream and pipeline dropped",
                "alignment_note": "Matches the Balcombe 2016 LNG-stage compilation boundary.",
            },
            {
                "study": "Balcombe et al. 2016 (LNG-stage literature range)",
                "display_label": "Balcombe 2016 compilation",
                "year": 2016,
                "geography": "Global compilation",
                "system_boundary": "Liquefaction + tanker + regasification (not upstream)",
                "upstream_tCO2e_per_t": np.nan,
                "combustion_included": False,
                "shipping_included": True,
                "total_low": balcombe_t[0],
                "total_central": np.nan,
                "total_high": balcombe_t[1],
                "gwp": "GWP100",
                "axis_group": "lng_stages_gwp100",
                "is_this_model": False,
                "source": (
                    f"ACS Sustainable Chem. Eng.; {cmp['balcombe_g'][0]:g}–"
                    f"{cmp['balcombe_g'][1]:g} gCO2e/MJ HHV × "
                    f"{hhv:g} MJ/kg HHV. Not Balcombe's own single-chain LCA."
                ),
                "alignment_note": (
                    "Range of other studies' LNG stages. Converted from HHV with "
                    f"{hhv:g} MJ/kg. No midpoint plotted. "
                    "Roman-White 2021 is the Balcombe-coauthored single-chain LCA."
                ),
            },
            {
                "study": "Howarth 2024",
                "display_label": "Howarth 2024",
                "year": 2024,
                "geography": "US shale LNG exports",
                "system_boundary": "Well → combustion, GWP20 (not GWP100)",
                "upstream_tCO2e_per_t": np.nan,
                "combustion_included": True,
                "shipping_included": True,
                "total_low": howarth[0],
                "total_central": np.nan,
                "total_high": howarth[1],
                "gwp": "GWP20",
                "axis_group": "full_gwp20",
                "is_this_model": False,
                "source": (
                    "Energy Sci. Eng. 12:4843; Table 3 average 38-day voyage; "
                    "7,370–8,028 gCO2e/kg LNG. GWP20=82.5."
                ),
                "alignment_note": (
                    "Includes destination transmission methane (0.32% leak; "
                    "264 gCO2e/kg GWP20) that this model does not. "
                    "GWP100 totals are only in supplemental figures; not tabulated, "
                    "so not converted here. Combustion 2.75 t/t matches this model."
                ),
            },
        ]
    )

    excluded = pd.DataFrame(
        [
            {
                "study": "MacKay et al. 2021",
                "reason": (
                    "6,650-site methane measurements in western Canada. "
                    "No LNG system boundary and no lifecycle total."
                ),
            },
            {
                "study": "Johnson et al. 2023",
                "reason": (
                    "Alberta measurement inventory of oil and gas methane. "
                    "No LNG system boundary and no lifecycle total."
                ),
            },
            {
                "study": "Di Lullo et al.",
                "reason": (
                    "Published work is a transmission-pipeline LCA "
                    "(construction/operation/decommissioning) and crude WTT studies. "
                    "No LNG well-to-wire or well-to-combustion total with a readable boundary."
                ),
            },
        ]
    )
    return {
        "included": included,
        "excluded": excluded,
        "stage_intensity": si,
        "model_full": model_full,
        "model_w2r": model_w2r,
        "model_lng": model_lng,
    }


def _range_panel(ax, sl: pd.DataFrame, title: str, xlabel: str) -> None:
    sl = sl.reset_index(drop=True)
    y = np.arange(len(sl))
    xmax = 0.0
    for i, r in sl.iterrows():
        color = C["blue"] if r["is_this_model"] else C["vermillion"]
        lo = float(r["total_low"])
        hi = float(r["total_high"])
        mid = r["total_central"]
        ax.hlines(i, lo, hi, color=color, linewidth=5, zorder=2)
        ax.plot(lo, i, "o", color=color, markersize=6, zorder=3)
        ax.plot(hi, i, "o", color=color, markersize=6, zorder=3)
        if pd.notna(mid):
            ax.plot(float(mid), i, "D", color=C["black"], markersize=7, zorder=4)
        label = f"{lo:.2f}" if abs(hi - lo) < 1e-9 else f"{lo:.2f}–{hi:.2f}"
        ax.text(hi + 0.02, i, label, va="center", fontsize=8, color=C["grey"])
        xmax = max(xmax, hi)
    ax.set_yticks(y, sl["display_label"])
    ax.invert_yaxis()
    ax.set_title(title, loc="left", fontsize=10)
    ax.set_xlabel(xlabel)
    ax.set_xlim(0, xmax * 1.28)
    ax.axvline(0, color=C["grey"], linewidth=0.6)


def figure_10_lca_comparison(
    inputs: dict,
    fig_dir: Path,
    data_dir: Path,
) -> dict:
    tables = build_lca_comparison(inputs)
    inc = tables["included"]
    _write_csv(inc, data_dir / "fig10_lca_comparison.csv")
    _write_csv(tables["excluded"], data_dir / "fig10_lca_excluded.csv")

    _setup_style()
    fig, axes = plt.subplots(2, 2, figsize=(10.4, 7.0))

    _range_panel(
        axes[0, 0],
        inc.loc[inc["axis_group"] == "w2r_gwp100"],
        "Well → regasification · GWP100",
        "tCO₂e per t LNG",
    )
    _range_panel(
        axes[0, 1],
        inc.loc[inc["axis_group"] == "lng_stages_gwp100"],
        "Liquefaction + shipping + regas · GWP100",
        "tCO₂e per t LNG",
    )
    _range_panel(
        axes[1, 0],
        inc.loc[inc["axis_group"] == "full_gwp100"],
        "Full chain with combustion · GWP100",
        "tCO₂e per t LNG",
    )
    _range_panel(
        axes[1, 1],
        inc.loc[inc["axis_group"] == "full_gwp20"],
        "Full chain with combustion · GWP20 (not GWP100)",
        "tCO₂e per t LNG",
    )

    handles = [
        plt.Line2D([0], [0], color=C["blue"], lw=5, label="This model"),
        plt.Line2D([0], [0], color=C["vermillion"], lw=5, label="Published study"),
        plt.Line2D(
            [0], [0], marker="D", color=C["black"], lw=0, markersize=7,
            label="Point / published expected",
        ),
    ]
    fig.legend(handles=handles, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.02))
    fig.text(
        0.5,
        0.01,
        "Figure 10 · Bars are published ranges (no invented midpoints). Diamonds are this "
        "model's intensity or Roman-White's published expected value. Howarth is GWP20 and "
        "is not ranked against this model's 3.55 t/t GWP100. MacKay, Johnson and Di Lullo "
        "are excluded (fig10_lca_excluded.csv).",
        ha="center",
        va="bottom",
        fontsize=8,
        color=C["grey"],
    )
    fig.tight_layout(rect=(0, 0.06, 1, 0.96))
    out = fig_dir / "fig10_lca_comparison.png"
    _save(fig, out)
    return {
        "path": out,
        "csv": data_dir / "fig10_lca_comparison.csv",
        "key": {
            "model_full_t_per_t": round(tables["model_full"], 2),
            "model_well_to_regas_t_per_t": round(tables["model_w2r"], 2),
            "model_lng_stages_t_per_t": round(tables["model_lng"], 2),
            "roman_white_w2r": "0.94–1.51 (expected 1.19)",
            "howarth_gwp20": "7.37–8.03",
        },
        "tables": tables,
    }


def format_lca_markdown(tables: dict) -> list[str]:
    inc = tables["included"]
    exc = tables["excluded"]
    lines = [
        "## Lifecycle intensity comparison",
        "",
        "tCO2e per tonne LNG. This model is recomputed on each comparator's boundary. "
        "Ranges are shown as published; midpoints are not substituted. "
        "GWP20 is not mixed with GWP100.",
        "",
        "| study | year | geography | boundary | combustion | shipping | total tCO2e/t |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in inc.itertuples():
        if pd.notna(r.total_central) and abs(float(r.total_low) - float(r.total_high)) < 1e-9:
            tot = f"{float(r.total_central):.2f}"
        else:
            tot = f"{float(r.total_low):.2f}–{float(r.total_high):.2f}"
            if pd.notna(r.total_central):
                tot += f" (expected {float(r.total_central):.2f})"
        lines.append(
            f"| {r.study} | {int(r.year)} | {r.geography} | {r.system_boundary} | "
            f"{'yes' if r.combustion_included else 'no'} | "
            f"{'yes' if r.shipping_included else 'no'} | {tot} |"
        )
    lines.append("")
    lines.append(
        "This model's export-chain GWP100 is "
        f"{tables['model_full']:.2f} t/t "
        f"(well-to-regas {tables['model_w2r']:.2f}; "
        f"liquefaction+shipping+regas {tables['model_lng']:.2f}). "
        "**Shipping here is the unscaled 0.12 British Columbia to "
        "north-east Asia factor**, not the per-asset route-scaled figure the "
        "headline model uses, because the comparator studies are single-route. "
        "Liquefaction remains 0.29. Howarth's GWP100 totals are only in "
        "supplemental figures and are not converted here. Howarth also includes "
        "destination transmission methane that this model does not."
    )
    lines.append("")
    lines.append("Excluded (boundary not an LNG lifecycle, or not determined):")
    lines.append("")
    for r in exc.itertuples():
        lines.append(f"- **{r.study}:** {r.reason}")
    lines.append("")
    lines.append("Figure: `Outputs/figures/fig10_lca_comparison.png`.")
    lines.append("")
    return lines
