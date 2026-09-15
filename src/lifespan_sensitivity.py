"""Uniform-life sensitivity (supplementary information only).

The central case takes each project's operating life from its CER export
licence term where one exists, cut at `authorised_export_end_year` when that
field is populated, and falls back to a proponent-stated life or the
Parameters default. That produces lives from 27 to 40 years across the ten
headline assets and, because the licence-end stops bite hardest on the two
LNG Canada trains and Ksi Lisims, it shortens exactly the assets that are
furthest along.

This module runs the counterfactual the reviewer would ask for: **every
in-scope asset at 40 years from its first export year, with no
`authorised_export_end_year` stop**. It does not change the central case.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.inputs import DEFAULT_SCENARIO, get_param
from src.loss_damage import LD_EMISSION_SCENARIOS, compute_loss_damage
from src.scope import BUILD_OUT_LABEL, BUILD_OUTS, build_out_project_ids, filter_panel
from src.trajectories import build_emissions_panel, panel_gas_totals, panel_peak

CASES = (
    ("central", None, False),
    ("uniform_40yr_no_licence_stop", 40, True),
)


def _slice_metrics(
    panel: pd.DataFrame,
    ld: dict,
    ids: list[str],
) -> dict:
    gas = panel_gas_totals(panel, DEFAULT_SCENARIO, project_ids=ids)
    sl = panel.loc[panel["project_id"].isin(ids)]
    peak_year, peak_mt = panel_peak(sl, DEFAULT_SCENARIO)
    bp = ld["by_project"]
    eccc = bp.loc[
        (bp["price_family"] == "eccc")
        & (bp["discount_rate_pct"] == ld["eccc_r"])
        & (bp["project_id"].isin(ids))
    ]
    return {
        "lifetime_mtco2e": gas["lifetime_mtco2e"],
        "lifetime_co2_only_mt": gas["lifetime_co2_only_mt"],
        "lifetime_ch4_kt": gas["lifetime_ch4_kt"],
        "peak_year": int(peak_year),
        "peak_mtco2e_yr": peak_mt,
        "eccc_2pct_damages_cad_bn": float(eccc["hatton_sum_cad"].sum()) / 1e9,
    }


def run_uniform_life_sensitivity(
    inputs: dict,
    inputs_dir: Path,
    central_panel: pd.DataFrame,
    central_ld: dict,
) -> dict:
    """Central versus every asset at 40 years with no licence-end stop."""
    default_life = int(get_param(inputs["params"], "lifecycle_years_default"))
    ids = build_out_project_ids(inputs)
    rows = []
    life_rows = []
    for case, override, ignore_end in CASES:
        if override is None and not ignore_end:
            panel_c, ld_c = central_panel, central_ld
        else:
            panel_c = filter_panel(
                build_emissions_panel(
                    inputs,
                    scenarios=LD_EMISSION_SCENARIOS,
                    lifespan_override_years=override,
                    ignore_licence_end=ignore_end,
                ),
                inputs,
            )
            ld_c = compute_loss_damage(inputs, inputs_dir, panel=panel_c)
        for name in BUILD_OUTS:
            rows.append({
                "case": case,
                "lifespan_override_years": override,
                "ignore_licence_end": ignore_end,
                "build_out": name,
                "membership": BUILD_OUT_LABEL[name],
                **_slice_metrics(panel_c, ld_c, ids[name]),
            })
        by_asset = (
            panel_c.loc[panel_c["scenario"] == DEFAULT_SCENARIO]
            .groupby(["project_id", "lifespan_years"], sort=False)["emissions_mtco2e"]
            .sum()
            .reset_index()
        )
        by_asset["case"] = case
        life_rows.append(by_asset)

    cases = pd.DataFrame(rows)
    wide = cases.pivot(index="build_out", columns="case")

    def _val(build_out: str, case: str, col: str) -> float:
        return float(
            cases.loc[
                (cases["build_out"] == build_out) & (cases["case"] == case), col
            ].iloc[0]
        )

    ratios = []
    for case, _o, _i in CASES:
        full = _val("full", case, "lifetime_mtco2e")
        committed = _val("committed", case, "lifetime_mtco2e")
        ratios.append({
            "case": case,
            "committed_mtco2e": committed,
            "full_mtco2e": full,
            "full_over_committed": full / committed if committed else float("nan"),
            "committed_over_full_pct": (
                100.0 * committed / full if full else float("nan")
            ),
        })

    central_full = _val("full", "central", "lifetime_mtco2e")
    uniform_full = _val("full", "uniform_40yr_no_licence_stop", "lifetime_mtco2e")
    return {
        "cases": cases,
        "wide": wide,
        "ratios": pd.DataFrame(ratios),
        "by_asset": pd.concat(life_rows, ignore_index=True),
        "default_life": default_life,
        "delta_pct_full": 100.0 * (uniform_full - central_full) / central_full,
    }


def format_uniform_life_markdown(sens: dict) -> list[str]:
    cases = sens["cases"]
    ratios = sens["ratios"].set_index("case")
    lines = []
    lines.append("## Uniform 40-year life sensitivity (SI only)")
    lines.append("")
    lines.append(
        f"Every in-scope asset run at **{sens['default_life']} years from its "
        f"first export year with no `authorised_export_end_year` stop** "
        f"(`lifespan_override_years=40`, `ignore_licence_end=True` on the panel "
        f"builder). The central case is unchanged and stays the paper's number; "
        f"this is supplementary information. Lives in the central case run from "
        f"27 to 40 years, and the licence-end stops bite hardest on the two LNG "
        f"Canada trains and Ksi Lisims — the assets furthest along — so the "
        f"central case is not simply a shorter version of this one."
    )
    lines.append("")
    lines.append(
        "| build-out | case | lifetime CO2e Mt | lifetime CO2-only Mt | "
        "peak Mt (year) | ECCC 2% damages CAD bn, calendar-year sum (valued when "
        "caused; the NPV-to-2025 figure is carried in the paper set) |"
    )
    lines.append("|---|---|---|---|---|---|")
    for build_out in cases["build_out"].unique():
        for _, r in cases.loc[cases["build_out"] == build_out].iterrows():
            lines.append(
                f"| {build_out} | {r['case']} | {r['lifetime_mtco2e']:,.1f} | "
                f"{r['lifetime_co2_only_mt']:,.1f} | "
                f"{r['peak_mtco2e_yr']:,.1f} ({int(r['peak_year'])}) | "
                f"{r['eccc_2pct_damages_cad_bn']:,.0f} |"
            )
    lines.append("")
    lines.append(
        f"Full buildout moves **{sens['delta_pct_full']:+.1f}%** on the uniform "
        f"life. Committed-to-full ratio, both ways:"
    )
    lines.append("")
    lines.append("| case | full / committed | committed as % of full |")
    lines.append("|---|---|---|")
    for case in ratios.index:
        r = ratios.loc[case]
        lines.append(
            f"| {case} | {r['full_over_committed']:.2f} | "
            f"{r['committed_over_full_pct']:.1f}% |"
        )
    lines.append("")
    lines.append(
        "Series: `Outputs/figure_data/sens_uniform_life.csv`. No locked value "
        "changes: the central case is untouched."
    )
    lines.append("")
    return lines
