"""Calendar-year emission panel and figure trajectories.

The per-asset, per-calendar-year panel (build_emissions_panel) is the
published source of lifetime totals. compute_by_project still produces a
life-average annual figure; that average is not integrated to a lifetime.

Figure trajectories (TRAJECTORY_YEARS) remain 2025–2050 for plots only.
They do not cut the panel.
"""

from __future__ import annotations

from typing import Iterable

import pandas as pd

from src.inputs import DEFAULT_SCENARIO, INTENSITY_SCENARIOS, get_param
from src.model import (
    _fid_ok,
    _is_legacy,
    _licence_end_year,
    _lifespan,
    _stage_intensity,
    previously_classified_electric,
    stage_ch4_co2e_intensity,
)
from src.scope import headline_scope_sets, row_in_headline_scope

TRAJECTORY_YEARS = tuple(range(2025, 2051))
# Scenarios whose CO2e is on a GWP100 basis, so CH4 mass = CH4-derived CO2e /
# gwp100_ch4. near_term_methane_gwp20 is excluded: its 0.33 upstream factor is
# the inventory factor scaled whole (0.22 x 1.5), not a GWP100 CO2e figure that
# can be divided back to a mass. Its ch4_mass_kt is left blank rather than wrong.
GWP100_SCENARIOS = (
    "inventory_as_reported",
    "measurement_central",
    "measurement_high",
    "howarth_high",
)
# First calendar year of the published panel (remaining life from this year).
PANEL_START_YEAR = 2025
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


def _chain_intensity_split(
    row,
    scenario: str,
    inputs: dict,
    *,
    canada_only: bool,
    liquefaction_mode: str | None = None,
) -> tuple[float, float, float]:
    """(total, CO2, CH4-derived CO2e) chain intensity in tCO2e per t LNG.

    total == co2 + ch4_co2e exactly. See `stage_ch4_co2e_intensity` for which
    stages carry an identified methane portion; pipeline fugitives are not split.
    """
    total = 0.0
    ch4 = 0.0
    override = _liquefaction_intensity_for_mode(row, inputs, liquefaction_mode)
    for stage, where in inputs["chains"][row["chain"]]:
        if canada_only and where != "CAN":
            continue
        if stage == "liquefaction" and override is not None:
            total += override
            continue
        intensity, _ = _stage_intensity(stage, row, scenario, inputs)
        total += intensity
        ch4 += stage_ch4_co2e_intensity(stage, intensity, inputs)
    return total, total - ch4, ch4


def _chain_intensity(
    row,
    scenario: str,
    inputs: dict,
    *,
    canada_only: bool,
    liquefaction_mode: str | None = None,
) -> float:
    total, _co2, _ch4 = _chain_intensity_split(
        row,
        scenario,
        inputs,
        canada_only=canada_only,
        liquefaction_mode=liquefaction_mode,
    )
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
    licence_end = _licence_end_year(row)
    if licence_end is not None and year > licence_end:
        return 0.0
    idx = year - start
    if idx < 0 or idx >= lifespan:
        return 0.0
    return sched[idx]


def project_annual_split_mt(
    row,
    year: int,
    inputs: dict,
    scenario: str,
    assumed_start: int,
    *,
    canada_only: bool = False,
    liquefaction_mode: str | None = None,
) -> tuple[float, float, float] | None:
    """(MtCO2e, MtCO2, Mt CH4-derived CO2e) for one asset-year, or None if excluded."""
    if pd.isna(row["capacity_mtpa"]):
        return None
    params = inputs["params"]
    life, _ = _lifespan(row, params)
    legacy = _is_legacy(row, life)
    start, _ = _start_year(row, assumed_start)
    sched = _util_schedule(row, life, params)
    util = util_in_calendar_year(row, year, life, sched, start, legacy)
    if util == 0.0:
        return 0.0, 0.0, 0.0
    mtpa_to_t = float(get_param(params, "mtpa_to_tonnes"))
    total_i, co2_i, ch4_i = _chain_intensity_split(
        row,
        scenario,
        inputs,
        canada_only=canada_only,
        liquefaction_mode=liquefaction_mode,
    )
    scale = float(row["capacity_mtpa"]) * mtpa_to_t * util / 1e6
    return scale * total_i, scale * co2_i, scale * ch4_i


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
    split = project_annual_split_mt(
        row,
        year,
        inputs,
        scenario,
        assumed_start,
        canada_only=canada_only,
        liquefaction_mode=liquefaction_mode,
    )
    return None if split is None else split[0]


def calendar_bounds(inputs: dict, assumed_start: int) -> tuple[int, int]:
    """Inclusive (first, last) calendar year of the published emissions panel."""
    last = PANEL_START_YEAR
    params = inputs["params"]
    for _, row in inputs["assets"].iterrows():
        if pd.isna(row["capacity_mtpa"]):
            continue
        life, _ = _lifespan(row, params)
        if _is_legacy(row, life):
            continue
        start, _ = _start_year(row, assumed_start)
        last = max(last, start + life - 1)
    return PANEL_START_YEAR, last


def build_emissions_panel(
    inputs: dict,
    *,
    scenarios: Iterable[str] | None = None,
    assumed_start: int | None = None,
    canada_only: bool = False,
    liquefaction_mode: str | None = None,
) -> pd.DataFrame:
    """Per-asset, per-calendar-year MtCO2e. Primary emissions object.

    Legacy assets (outlived design life) are omitted here so the full
    register panel does not invent a remaining life for plants
    commissioned in 1971 and 1976. Headline membership is the named
    chain/calc_group filter in src.scope, applied after this frame is
    built. Years with zero output are omitted. Lifetime totals are the
    sum of the (optionally scoped) frame.
    """
    if assumed_start is None:
        assumed_start = int(get_param(inputs["params"], "assumed_first_export_year_if_missing"))
    scen_list = tuple(scenarios) if scenarios is not None else INTENSITY_SCENARIOS
    year0, year1 = calendar_bounds(inputs, assumed_start)
    years = range(year0, year1 + 1)
    gwp100 = float(get_param(inputs["params"], "gwp100_ch4"))
    rows = []
    for scenario in scen_list:
        on_gwp100 = scenario in GWP100_SCENARIOS
        for _, row in inputs["assets"].iterrows():
            if pd.isna(row["capacity_mtpa"]):
                continue
            life, life_src = _lifespan(row, inputs["params"])
            if _is_legacy(row, life):
                continue
            start, placeholder = _start_year(row, assumed_start)
            for year in years:
                split = project_annual_split_mt(
                    row,
                    year,
                    inputs,
                    scenario,
                    assumed_start,
                    canada_only=canada_only,
                    liquefaction_mode=liquefaction_mode,
                )
                if split is None:
                    continue
                mt, co2_mt, ch4_mt = split
                if mt == 0.0:
                    continue
                rows.append({
                    "year": year,
                    "scenario": scenario,
                    "project_id": row["project_id"],
                    "project_name": row["project_name"],
                    "calc_group": row["calc_group"],
                    "chain": row["chain"],
                    "emissions_mtco2e": float(mt),
                    "co2_mt": float(co2_mt),
                    "ch4_derived_co2e_mt": float(ch4_mt),
                    "ch4_mass_kt": (
                        float(ch4_mt) / gwp100 * 1000.0 if on_gwp100 else float("nan")
                    ),
                    "ch4_gwp_basis": gwp100 if on_gwp100 else float("nan"),
                    "start_year": start,
                    "lifespan_years": life,
                    "lifespan_source": life_src,
                    "start_was_placeholder": placeholder,
                    "canada_only": canada_only,
                })
    panel = pd.DataFrame(rows)
    if not len(panel):
        raise ValueError("Emissions panel is empty.")
    resid = (
        panel["emissions_mtco2e"] - panel["co2_mt"] - panel["ch4_derived_co2e_mt"]
    ).abs().max()
    if resid > 1e-9:
        raise AssertionError(
            f"Panel CO2 + CH4-derived CO2e does not reconstruct CO2e "
            f"(max residual {resid} Mt)."
        )
    return panel


def panel_lifetime_mt(
    panel: pd.DataFrame,
    scenario: str = DEFAULT_SCENARIO,
    *,
    calc_group: str | None = None,
    chain: str | None = None,
    project_id: str | None = None,
) -> float:
    """Sum of panel MtCO2e for the given slice."""
    q = panel["scenario"] == scenario
    if calc_group is not None:
        q = q & (panel["calc_group"] == calc_group)
    if chain is not None:
        q = q & (panel["chain"] == chain)
    if project_id is not None:
        q = q & (panel["project_id"] == project_id)
    return float(panel.loc[q, "emissions_mtco2e"].sum())


def panel_gas_totals(
    panel: pd.DataFrame,
    scenario: str = DEFAULT_SCENARIO,
    *,
    calc_group: str | None = None,
    calc_groups: Iterable[str] | None = None,
    project_ids: Iterable[str] | None = None,
) -> dict:
    """Lifetime CO2e Mt, CO2-only Mt and CH4 kt for a panel slice."""
    q = panel["scenario"] == scenario
    if calc_group is not None:
        q = q & (panel["calc_group"] == calc_group)
    if calc_groups is not None:
        q = q & panel["calc_group"].isin(list(calc_groups))
    if project_ids is not None:
        q = q & panel["project_id"].isin(list(project_ids))
    sl = panel.loc[q]
    return {
        "lifetime_mtco2e": float(sl["emissions_mtco2e"].sum()),
        "lifetime_co2_only_mt": float(sl["co2_mt"].sum()),
        "lifetime_ch4_derived_co2e_mt": float(sl["ch4_derived_co2e_mt"].sum()),
        "lifetime_ch4_kt": float(sl["ch4_mass_kt"].sum()),
    }


def gwp20_reconciliation(panel: pd.DataFrame, inputs: dict) -> dict:
    """Reconcile the `near_term_methane_gwp20` scenario against the CH4-mass route.

    Route A is the scenario as the workbook defines it: upstream 0.33, every
    other stage at its central value.

    Route B re-weights the Task 1 CH4 mass at `gwp20_ch4`:
    `co2_mt + ch4_mass_kt/1000 x gwp20`.

    The two are not expected to agree, and are not forced to. The decomposition
    below is reported instead.
    """
    gwp100 = float(get_param(inputs["params"], "gwp100_ch4"))
    gwp20 = float(get_param(inputs["params"], "gwp20_ch4"))
    inv = float(inputs["upstream_by_scenario"]["inventory_as_reported"])
    share = float(get_param(inputs["params"], "upstream_ch4_share"))
    central_up = float(inputs["upstream_by_scenario"][DEFAULT_SCENARIO])
    scen_up = float(inputs["upstream_by_scenario"]["near_term_methane_gwp20"])

    central = panel_gas_totals(panel, DEFAULT_SCENARIO)
    scen_total = panel_lifetime_mt(panel, "near_term_methane_gwp20")
    mass_route = central["lifetime_co2_only_mt"] + (
        central["lifetime_ch4_kt"] / 1000.0 * gwp20
    )

    # Split route B's uplift into the upstream and shipping parts, so the gap
    # can be attributed rather than just stated.
    ch4_up_per_t = max(central_up - inv * (1.0 - share), 0.0)
    ship_i = float(inputs["factors"].loc["shipping", "central"])
    uplift = float(get_param(inputs["params"], "lng_carrier_methane_slip_uplift"))
    ch4_ship_per_t = ship_i * (1.0 - 1.0 / uplift)
    ch4_total_per_t = ch4_up_per_t + ch4_ship_per_t
    uplift_mt = mass_route - central["lifetime_mtco2e"]
    ship_uplift_mt = (
        uplift_mt * ch4_ship_per_t / ch4_total_per_t if ch4_total_per_t else 0.0
    )
    up_uplift_mt = uplift_mt - ship_uplift_mt

    diff_pct = 100.0 * (mass_route - scen_total) / scen_total if scen_total else 0.0
    up_only_route = central["lifetime_mtco2e"] + up_uplift_mt
    up_only_diff_pct = (
        100.0 * (up_only_route - scen_total) / scen_total if scen_total else 0.0
    )
    return {
        "central_route_mt": central["lifetime_mtco2e"],
        "scenario_route_mt": scen_total,
        "ch4_mass_route_mt": mass_route,
        "difference_pct": diff_pct,
        "upstream_only_mass_route_mt": up_only_route,
        "upstream_only_difference_pct": up_only_diff_pct,
        "upstream_uplift_mt": up_uplift_mt,
        "shipping_uplift_mt": ship_uplift_mt,
        "scenario_upstream_factor": scen_up,
        "mass_route_upstream_factor": (
            inv * (1.0 - share) + ch4_up_per_t / gwp100 * gwp20
        ),
        "inventory_upstream_factor": inv,
        "gwp100_ch4": gwp100,
        "gwp20_ch4": gwp20,
        "agrees_within_0_1_pct": abs(diff_pct) <= 0.1,
    }


def panel_by_project(panel: pd.DataFrame) -> pd.DataFrame:
    """One row per scenario × project: lifetime MtCO2e from the panel."""
    keys = [
        "scenario",
        "project_id",
        "project_name",
        "calc_group",
        "chain",
        "start_year",
        "lifespan_years",
        "start_was_placeholder",
    ]
    return (
        panel.groupby(keys, dropna=False, sort=False)[
            ["emissions_mtco2e", "co2_mt", "ch4_derived_co2e_mt", "ch4_mass_kt"]
        ]
        .sum()
        .reset_index()
        .rename(
            columns={
                "emissions_mtco2e": "lifetime_mtco2e",
                "co2_mt": "lifetime_co2_only_mt",
                "ch4_derived_co2e_mt": "lifetime_ch4_derived_co2e_mt",
                "ch4_mass_kt": "lifetime_ch4_kt",
            }
        )
    )


def panel_by_group(panel: pd.DataFrame) -> pd.DataFrame:
    return (
        panel.groupby(["scenario", "calc_group"], dropna=False, sort=False)[
            ["emissions_mtco2e", "co2_mt", "ch4_derived_co2e_mt", "ch4_mass_kt"]
        ]
        .sum()
        .reset_index()
        .rename(
            columns={
                "emissions_mtco2e": "lifetime_mtco2e",
                "co2_mt": "lifetime_co2_only_mt",
                "ch4_derived_co2e_mt": "lifetime_ch4_derived_co2e_mt",
                "ch4_mass_kt": "lifetime_ch4_kt",
            }
        )
    )


def panel_by_year(panel: pd.DataFrame, scenario: str = DEFAULT_SCENARIO) -> pd.DataFrame:
    sl = panel.loc[panel["scenario"] == scenario]
    return (
        sl.groupby("year", sort=True)["emissions_mtco2e"]
        .sum()
        .reset_index()
        .rename(columns={"emissions_mtco2e": "annual_mtco2e_yr"})
    )


def panel_peak(panel: pd.DataFrame, scenario: str = DEFAULT_SCENARIO) -> tuple[int, float]:
    yearly = panel_by_year(panel, scenario)
    idx = yearly["annual_mtco2e_yr"].idxmax()
    row = yearly.loc[idx]
    return int(row["year"]), float(row["annual_mtco2e_yr"])


def panel_n_emitting(
    panel: pd.DataFrame,
    year: int,
    scenario: str = DEFAULT_SCENARIO,
) -> int:
    """Count assets with positive emissions in a calendar year."""
    sl = panel.loc[
        (panel["scenario"] == scenario)
        & (panel["year"] == year)
        & (panel["emissions_mtco2e"] > 0)
    ]
    return int(sl["project_id"].nunique())


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
    if assumed_start is None:
        assumed_start = int(get_param(inputs["params"], "assumed_first_export_year_if_missing"))
    groups = set(calc_groups) if calc_groups is not None else None
    scope_chains, scope_groups = headline_scope_sets(inputs)

    rows = []
    for year in years:
        total = 0.0
        for _, row in inputs["assets"].iterrows():
            if not row_in_headline_scope(row, scope_chains, scope_groups):
                continue
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
