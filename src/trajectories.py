"""Calendar-year emission trajectories (2025–2050).

Uses the same intensities, util ramps, and FID-delay rules as the average
model, but reports year-by-year values rather than the 40-year average.
Does not alter the average calculation.
"""

from __future__ import annotations

from typing import Iterable

import pandas as pd

from src.inputs import DEFAULT_SCENARIO, get_param
from src.model import _fid_ok, _is_legacy, _lifespan, _stage_intensity, previously_classified_electric

TRAJECTORY_YEARS = tuple(range(2025, 2051))
CUMULATIVE_CASES = (
    ("operating", ("operating",)),
    ("plus_under_construction", ("operating", "under_construction")),
    ("plus_proposed", ("operating", "under_construction", "proposed")),
)


def _util_schedule(row, lifespan: int, params: dict) -> list[float]:
    pid = str(row["project_id"])
    if pid == "saint_john_import_facility":
        rate = float(get_param(params, "saint_john_utilisation"))
        return [rate] * lifespan

    if pid == "lng_canada_phase_1":
        y1 = float(get_param(params, "lng_canada_ph1_year_1_utilisation"))
        y2 = float(get_param(params, "lng_canada_ph1_year_2_utilisation"))
        steady = float(get_param(params, "lng_canada_ph1_steady_state_utilisation"))
    else:
        y1 = float(get_param(params, "year_1_utilisation"))
        y2 = float(get_param(params, "year_2_utilisation"))
        steady = float(get_param(params, "steady_state_utilisation"))

    ramp = int(get_param(params, "ramp_years"))
    delay = 0 if _fid_ok(row) else int(get_param(params, "fid_delay_mid"))
    sched: list[float] = []
    op = 0
    for year in range(lifespan):
        if year < delay:
            sched.append(0.0)
            continue
        op += 1
        if op == 1 and ramp >= 1:
            sched.append(y1)
        elif op == 2 and ramp >= 2:
            sched.append(y2)
        else:
            sched.append(steady)
    return sched


def _steady_from_schedule(sched: list[float]) -> float:
    for v in reversed(sched):
        if v > 0:
            return v
    return 0.0


def _start_year(row, assumed_if_missing: int) -> tuple[int, bool]:
    start = row.get("first_export_year")
    if pd.isna(start):
        return int(assumed_if_missing), True
    return int(start), False


def _liquefaction_intensity_for_mode(row, inputs: dict, mode: str | None) -> float | None:
    """None means use the modelled (gas turbine) factor."""
    if mode in (None, "gas"):
        return None
    elec = float(get_param(inputs["params"], "liquefaction_electric"))
    gas = float(get_param(inputs["params"], "liquefaction_gas_turbine"))
    if mode == "all_electric":
        return elec
    if mode == "claimed_electric":
        return (
            elec
            if previously_classified_electric(row.get("liquefaction_drive_note"))
            else gas
        )
    raise ValueError(f"Unknown liquefaction mode {mode!r}")


def _chain_intensity(
    row,
    scenario: str,
    inputs: dict,
    *,
    canada_only: bool,
    liquefaction_mode: str | None = None,
) -> float:
    total = 0.0
    override = _liquefaction_intensity_for_mode(row, inputs, liquefaction_mode)
    for stage, where in inputs["chains"][row["chain"]]:
        if canada_only and where != "CAN":
            continue
        if stage == "liquefaction" and override is not None:
            total += override
            continue
        intensity, _ = _stage_intensity(stage, row, scenario, inputs)
        total += intensity
    return total


def util_in_calendar_year(
    row,
    year: int,
    lifespan: int,
    sched: list[float],
    start: int,
    legacy: bool,
) -> float:
    if legacy:
        return _steady_from_schedule(sched)
    idx = year - start
    if idx < 0 or idx >= lifespan:
        return 0.0
    return sched[idx]


def project_annual_mt(
    row,
    year: int,
    inputs: dict,
    scenario: str,
    assumed_start: int,
    *,
    canada_only: bool = False,
    liquefaction_mode: str | None = None,
) -> float | None:
    """MtCO2e in a calendar year for one asset, or None if excluded (no capacity)."""
    if pd.isna(row["capacity_mtpa"]):
        return None
    params = inputs["params"]
    life, _ = _lifespan(row, params)
    legacy = _is_legacy(row, life)
    start, _ = _start_year(row, assumed_start)
    sched = _util_schedule(row, life, params)
    util = util_in_calendar_year(row, year, life, sched, start, legacy)
    if util == 0.0:
        return 0.0
    mtpa_to_t = float(get_param(params, "mtpa_to_tonnes"))
    intensity = _chain_intensity(
        row,
        scenario,
        inputs,
        canada_only=canada_only,
        liquefaction_mode=liquefaction_mode,
    )
    return float(row["capacity_mtpa"]) * mtpa_to_t * util * intensity / 1e6


def annual_series(
    inputs: dict,
    scenario: str = DEFAULT_SCENARIO,
    *,
    calc_groups: Iterable[str] | None = None,
    canada_only: bool = False,
    assumed_start: int | None = None,
    years: tuple[int, ...] = TRAJECTORY_YEARS,
    liquefaction_mode: str | None = None,
) -> pd.DataFrame:
    """One row per year: annual_mtco2e_yr for the selected calc_groups."""
    from src.report_params import resolve_report_params

    report, _ = resolve_report_params(inputs["params"])
    if assumed_start is None:
        assumed_start = int(report["assumed_first_export_year_if_missing"])
    groups = set(calc_groups) if calc_groups is not None else None

    rows = []
    for year in years:
        total = 0.0
        for _, row in inputs["assets"].iterrows():
            if groups is not None and row["calc_group"] not in groups:
                continue
            val = project_annual_mt(
                row,
                year,
                inputs,
                scenario,
                assumed_start,
                canada_only=canada_only,
                liquefaction_mode=liquefaction_mode,
            )
            if val is None:
                continue
            total += val
        rows.append({
            "year": year,
            "scenario": scenario,
            "canada_only": canada_only,
            "calc_groups": (
                ",".join(sorted(groups)) if groups is not None else "all_in_scope"
            ),
            "annual_mtco2e_yr": total,
        })
    return pd.DataFrame(rows)


def cumulative_case_series(
    inputs: dict,
    scenario: str = DEFAULT_SCENARIO,
    *,
    canada_only: bool = False,
) -> pd.DataFrame:
    """Three cumulative membership cases derived from calc_group."""
    frames = []
    for case_name, groups in CUMULATIVE_CASES:
        df = annual_series(
            inputs,
            scenario,
            calc_groups=groups,
            canada_only=canada_only,
        )
        df = df.rename(columns={"annual_mtco2e_yr": case_name})
        frames.append(df[["year", case_name]])
    out = frames[0]
    for f in frames[1:]:
        out = out.merge(f, on="year")
    out["scenario"] = scenario
    out["canada_only"] = canada_only
    return out


def canada_pathway_series(
    params: dict,
    years: tuple[int, ...] = TRAJECTORY_YEARS,
) -> pd.DataFrame:
    """Interpolate Canada's legislated pathway between Parameter milestones."""
    milestones = {
        2023: float(get_param(params, "canada_national_emissions")),
        2026: float(get_param(params, "canada_2026_interim_objective")),
        2030: float(get_param(params, "canada_2030_target_high")),
        2035: float(get_param(params, "canada_2035_target_high")),
        int(get_param(params, "canada_net_zero_year")): 0.0,
    }
    ms_years = sorted(milestones)
    ms_vals = [milestones[y] for y in ms_years]
    rows = []
    for y in years:
        # piecewise linear between milestones
        if y <= ms_years[0]:
            val = ms_vals[0]
        elif y >= ms_years[-1]:
            val = ms_vals[-1]
        else:
            for i in range(len(ms_years) - 1):
                y0, y1 = ms_years[i], ms_years[i + 1]
                if y0 <= y <= y1:
                    t = (y - y0) / (y1 - y0)
                    val = ms_vals[i] + t * (ms_vals[i + 1] - ms_vals[i])
                    break
        rows.append({
            "year": y,
            "canada_pathway_mtco2e_yr": val,
            "milestone_years": ",".join(str(x) for x in ms_years),
        })
    return pd.DataFrame(rows)


def oil_lifecycle_gt(bpd: float, params: dict) -> float:
    """Same method as TMX: bpd × tCO2e/bbl × 365 × lifecycle_years / 1e9."""
    per_bbl = float(get_param(params, "tmx_oil_lifecycle_per_barrel"))
    life = float(get_param(params, "lifecycle_years_default"))
    return float(bpd) * per_bbl * 365.0 * life / 1e9
