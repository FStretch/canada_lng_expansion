"""Placeholder first-export-year sensitivity (Parameters sheet).

Four headline-scope export assets have a blank Asset Register
first_export_year. The named parameter assumed_first_export_year_if_missing
fills that gap. With licence-end stops on the licensed terminals, the
panel tail is entirely this placeholder.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.inputs import DEFAULT_SCENARIO, get_param
from src.loss_damage import LD_EMISSION_SCENARIOS, compute_loss_damage
from src.scope import filter_panel
from src.trajectories import (
    build_emissions_panel,
    panel_by_project,
    panel_lifetime_mt,
    panel_n_emitting,
    panel_peak,
)


def _placeholder_years(params: dict) -> tuple[int, ...]:
    """Central year plus the sensitivity years from Parameters."""
    named = int(get_param(params, "assumed_first_export_year_if_missing"))
    raw = str(get_param(params, "placeholder_sensitivity_years"))
    extra = tuple(int(x.strip()) for x in raw.split(",") if x.strip())
    years = (named,) + extra
    for y in extra:
        if y <= named:
            raise ValueError(
                f"placeholder_sensitivity_years {raw} must all be after "
                f"assumed_first_export_year_if_missing ({named})."
            )
    return years


def placeholder_contribution(
    panel: pd.DataFrame,
    assets: pd.DataFrame,
    scenario: str = DEFAULT_SCENARIO,
) -> pd.DataFrame:
    """Lifetime MtCO2e from assets whose start year was the placeholder."""
    proj = panel_by_project(panel)
    sl = proj.loc[
        (proj["scenario"] == scenario) & (proj["start_was_placeholder"])
    ].copy()
    cap = assets[["project_id", "capacity_mtpa"]].drop_duplicates("project_id")
    sl = sl.merge(cap, on="project_id", how="left")
    total = panel_lifetime_mt(panel, scenario)
    sl["share_of_lifetime_pct"] = 100.0 * sl["lifetime_mtco2e"] / total
    sl["last_emitting_year"] = [
        int(
            panel.loc[
                (panel["scenario"] == scenario)
                & (panel["project_id"] == pid)
                & (panel["emissions_mtco2e"] > 0),
                "year",
            ].max()
        )
        for pid in sl["project_id"]
    ]
    sl = sl.sort_values("lifetime_mtco2e", ascending=False)
    return sl


def run_placeholder_start_sensitivity(
    inputs: dict,
    inputs_dir: Path,
    central_panel: pd.DataFrame,
    central_ld: dict,
) -> dict:
    """2030 / 2033 / 2035 start-year cases. 2030 must match the published run."""
    named = int(get_param(inputs["params"], "assumed_first_export_year_if_missing"))
    if named != 2030:
        raise AssertionError(
            f"Central assumed_first_export_year_if_missing is {named}, not 2030."
        )
    years = _placeholder_years(inputs["params"])

    contrib = placeholder_contribution(central_panel, inputs["assets"])
    lifetime_central = panel_lifetime_mt(central_panel, DEFAULT_SCENARIO)
    placeholder_mt = float(contrib["lifetime_mtco2e"].sum())
    placeholder_pct = 100.0 * placeholder_mt / lifetime_central

    rows = []
    for start in years:
        if start == named:
            panel_s = central_panel
            ld_s = central_ld
        else:
            panel_s = build_emissions_panel(
                inputs,
                scenarios=LD_EMISSION_SCENARIOS,
                assumed_start=start,
            )
            panel_s = filter_panel(panel_s, inputs)
            ld_s = compute_loss_damage(
                inputs, inputs_dir, panel=panel_s, assumed_start=start
            )
        peak_year, peak_mt = panel_peak(panel_s, DEFAULT_SCENARIO)
        last_year = int(
            panel_s.loc[
                (panel_s["scenario"] == DEFAULT_SCENARIO)
                & (panel_s["emissions_mtco2e"] > 0),
                "year",
            ].max()
        )
        rows.append(
            {
                "assumed_first_export_year_if_missing": start,
                "is_central": start == named,
                "lifetime_mtco2e": panel_lifetime_mt(panel_s, DEFAULT_SCENARIO),
                "peak_year": peak_year,
                "peak_mtco2e_yr": peak_mt,
                "peak_n_assets": panel_n_emitting(panel_s, peak_year, DEFAULT_SCENARIO),
                "last_emitting_year": last_year,
                "central_damage_cad_billion": float(
                    ld_s["published"]["total_cad_billion"]
                ),
            }
        )

    cases = pd.DataFrame(rows)
    central_row = cases.loc[cases["is_central"]].iloc[0]
    if abs(float(central_row["lifetime_mtco2e"]) - lifetime_central) > 1e-6:
        raise AssertionError("2030 sensitivity case drifted from the published panel.")
    if abs(float(central_row["central_damage_cad_billion"])
           - float(central_ld["published"]["total_cad_billion"])) > 1e-6:
        raise AssertionError("2030 sensitivity damages drifted from the published total.")

    return {
        "cases": cases,
        "by_asset": contrib,
        "placeholder_mt": placeholder_mt,
        "placeholder_pct": placeholder_pct,
        "lifetime_central": lifetime_central,
        "named_start": named,
    }


def format_placeholder_markdown(sens: dict) -> list[str]:
    cases = sens["cases"]
    by_asset = sens["by_asset"]
    lines = []
    lines.append("## Placeholder start-year sensitivity")
    lines.append("")
    lines.append(
        f"Parameter `assumed_first_export_year_if_missing` = **{sens['named_start']}** "
        f"(Parameters sheet). {len(by_asset)} headline-scope assets have a blank "
        f"`first_export_year`. "
        "With licence-end stops on licensed terminals, every dated end year is "
        "2056–2066; the panel tail is entirely this placeholder."
    )
    lines.append("")
    lines.append(
        f"Placeholder-start assets account for **{sens['placeholder_mt']:.1f} MtCO2e** "
        f"({sens['placeholder_pct']:.1f}% of the {sens['lifetime_central']:.1f} Mt "
        "lifetime total)."
    )
    lines.append("")
    lines.append(
        "| project | mtpa | lifetime Mt | share of lifetime | last year |"
    )
    lines.append("|---|---|---|---|---|")
    for r in by_asset.itertuples():
        lines.append(
            f"| {r.project_id} | {r.capacity_mtpa:.1f} | "
            f"{r.lifetime_mtco2e:.1f} | {r.share_of_lifetime_pct:.1f}% | "
            f"{r.last_emitting_year} |"
        )
    lines.append("")
    lines.append(
        "| start year | lifetime Mt | peak year | peak Mt | last year | "
        "central damage CAD bn |"
    )
    lines.append("|---|---|---|---|---|---|")
    for r in cases.itertuples():
        mark = " (central)" if r.is_central else ""
        lines.append(
            f"| {int(r.assumed_first_export_year_if_missing)}{mark} | "
            f"{r.lifetime_mtco2e:.1f} | {int(r.peak_year)} | "
            f"{r.peak_mtco2e_yr:.1f} | {int(r.last_emitting_year)} | "
            f"{r.central_damage_cad_billion:.0f} |"
        )
    lines.append("")
    return lines
