"""Decoupled Monte Carlo: sample physics, then price with a frozen ECCC vector.

Liquefaction is held at 0.29 (electric 0.12 is a discrete counterfactual).
Howarth 0.55 is a named point sensitivity, not a draw. upstream_ch4_share
is held at 0.30 so the 0.22 × 1.5 construction is not double-counted.
Utilisation ramp rates are held: no published range.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd

from src.inputs import DEFAULT_SCENARIO, get_param
from src.loss_damage import (
    cad2021_to_cad2025,
    load_eccc_ch4,
    load_eccc_schedule,
    load_ld_params,
)
from src.model import (
    _fid_ok,
    _is_legacy,
    _licence_end_year,
    _lifespan,
    stage_ch4_co2e_intensity,
)
from src.scope import headline_scope_sets, row_in_headline_scope
from src.trajectories import PANEL_START_YEAR, _start_year

MC_SEED_PARAM = "monte_carlo_seed"
MC_DRAWS_PARAM = "monte_carlo_n_draws"
ECCC_RATE = 2.0
HOWARTH_SCENARIO = "howarth_high"

# Upstream triangle is inventory / central / GWP20-equivalent factor.
# Howarth 0.55 is excluded (different method).
UPSTREAM_TRI = (0.22, 0.25, 0.33)
FID_TRI = (3.0, 5.0, 7.0)
LIFE_TRI = (30.0, 40.0, 50.0)
LIQUEFACTION_FIXED = 0.29

BUILD_OUTS = (
    "committed",
    "committed_plus_advanced",
    "full",
)

SAMPLED_STAGES = (
    "pipeline_transport",
    "shipping",
    "regasification",
    "combustion",
)


@dataclass(frozen=True)
class AssetSpec:
    project_id: str
    capacity_mtpa: float
    calc_group: str
    tier: str
    chain: str
    start: int
    life_central: int
    life_sampled: bool
    licence_end: int | None
    fid_ok: bool
    y1: float
    y2: float
    steady: float
    ramp: int
    stages: tuple[str, ...]
    committed: bool
    committed_plus_advanced: bool
    full: bool


def _tri(factors: pd.DataFrame, stage: str) -> tuple[float, float, float]:
    low = float(factors.loc[stage, "range_low"])
    mode = float(factors.loc[stage, "central"])
    high = float(factors.loc[stage, "range_high"])
    if not (low <= mode <= high):
        raise ValueError(f"{stage} triangle {low}, {mode}, {high} is not ordered.")
    return low, mode, high


def _compile_assets(inputs: dict) -> list[AssetSpec]:
    params = inputs["params"]
    assumed = int(get_param(params, "assumed_first_export_year_if_missing"))
    y1 = float(get_param(params, "year_1_utilisation"))
    y2 = float(get_param(params, "year_2_utilisation"))
    steady = float(get_param(params, "steady_state_utilisation"))
    ramp = int(get_param(params, "ramp_years"))
    ph1_y1 = float(get_param(params, "lng_canada_ph1_year_1_utilisation"))
    ph1_y2 = float(get_param(params, "lng_canada_ph1_year_2_utilisation"))
    ph1_ss = float(get_param(params, "lng_canada_ph1_steady_state_utilisation"))
    sj = float(get_param(params, "saint_john_utilisation"))
    specs = []
    scope_chains, scope_groups = headline_scope_sets(inputs)
    for _, row in inputs["assets"].iterrows():
        if pd.isna(row["capacity_mtpa"]):
            continue
        chain = row["chain"]
        if chain not in inputs["chains"]:
            continue
        if not row_in_headline_scope(row, scope_chains, scope_groups):
            continue
        life, src = _lifespan(row, params)
        if _is_legacy(row, life):
            continue
        start, _ = _start_year(row, assumed)
        pid = str(row["project_id"])
        term = row.get("authorised_export_term_years")
        stated = row.get("project_life_years")
        licence_end = _licence_end_year(row)
        has_term = pd.notna(term)
        has_stated = pd.notna(stated)
        # Sample only the Parameters default. Licence terms, licence end years
        # and stated project lives stay put.
        life_sampled = (not has_term) and (licence_end is None) and (not has_stated)
        if pid == "saint_john_import_facility":
            a, b, c = sj, sj, sj
        elif pid == "lng_canada_phase_1":
            a, b, c = ph1_y1, ph1_y2, ph1_ss
        else:
            a, b, c = y1, y2, steady
        cg = str(row["calc_group"])
        tier = "" if pd.isna(row["tier"]) else str(row["tier"]).strip()
        committed = cg in ("operating", "under_construction")
        advanced = committed or tier == "advanced_proposed"
        specs.append(
            AssetSpec(
                project_id=pid,
                capacity_mtpa=float(row["capacity_mtpa"]),
                calc_group=cg,
                tier=tier,
                chain=str(chain),
                start=start,
                life_central=int(life),
                life_sampled=life_sampled,
                licence_end=licence_end,
                fid_ok=_fid_ok(row),
                y1=a,
                y2=b,
                steady=c,
                ramp=ramp,
                stages=tuple(s for s, _ in inputs["chains"][chain]),
                committed=committed,
                committed_plus_advanced=advanced,
                full=True,
            )
        )
    if not specs:
        raise ValueError("Monte Carlo has no in-scope assets.")
    return specs


def _util_matrix(
    years: np.ndarray,
    start: int,
    life: np.ndarray,
    delay: np.ndarray,
    y1: float,
    y2: float,
    steady: float,
    ramp: int,
    licence_end: int | None,
) -> np.ndarray:
    """n_draws × n_years utilisation. Delay sits inside the lifespan."""
    idx = years[None, :] - start
    life_c = life[:, None]
    delay_c = delay[:, None]
    operating = (idx >= 0) & (idx < life_c)
    if licence_end is not None:
        operating = operating & (years[None, :] <= licence_end)
    after_delay = idx >= delay_c
    op_year = idx - delay_c + 1
    if ramp < 1:
        u = np.full(idx.shape, steady, dtype=float)
    else:
        u = np.where(op_year == 1, y1, np.where((op_year == 2) & (ramp >= 2), y2, steady))
    return np.where(operating & after_delay, u, 0.0)


def _intensity_by_draw(
    specs: list[AssetSpec],
    upstream: np.ndarray,
    stage_draws: dict[str, np.ndarray],
    liquefaction: float,
    inputs: dict,
) -> tuple[np.ndarray, np.ndarray]:
    """(total, CH4-derived) n_draws × n_assets chain intensity, tCO2e / t LNG.

    The CH4 part uses the same construction as the central case
    (`src.model.stage_ch4_co2e_intensity`), applied draw by draw: each draw
    carries its own upstream and shipping factor, so the methane it implies
    moves with it.
    """
    n_draws = len(upstream)
    n_assets = len(specs)
    out = np.zeros((n_draws, n_assets))
    ch4_out = np.zeros((n_draws, n_assets))
    for j, spec in enumerate(specs):
        tot = np.zeros(n_draws)
        ch4 = np.zeros(n_draws)
        for stage in spec.stages:
            if stage == "upstream_production":
                draw = upstream
            elif stage == "liquefaction":
                draw = np.full(n_draws, liquefaction)
            elif stage in stage_draws:
                draw = stage_draws[stage]
            else:
                raise ValueError(f"Unpriced stage {stage} on {spec.project_id}.")
            tot += draw
            ch4 += stage_ch4_co2e_intensity(stage, draw, inputs)
        out[:, j] = tot
        ch4_out[:, j] = ch4
    return out, ch4_out


def _eccc_price_cad2025(
    inputs_dir: Path, years: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """(SC-CO2 per tCO2, SC-CH4 per tCH4) in CAD 2025, one entry per year."""
    ld = load_ld_params(inputs_dir)
    p = ld["params"]
    eccc = load_eccc_schedule(inputs_dir, p)
    eccc_ch4 = load_eccc_ch4(inputs_dir, p)
    idx = eccc.set_index(["discount_rate_pct", "year"])["sc_co2_cad2021"]
    ch4_idx = eccc_ch4.set_index(["discount_rate_pct", "year"])["sc_ch4_cad2021"]
    out = np.empty(len(years), dtype=float)
    out_ch4 = np.empty(len(years), dtype=float)
    for i, year in enumerate(years):
        try:
            cad2021 = float(idx.loc[(ECCC_RATE, int(year))])
        except KeyError as exc:
            raise KeyError(
                f"ECCC SC-CO2 at {ECCC_RATE}% has no year {int(year)}."
            ) from exc
        try:
            ch4_cad2021 = float(ch4_idx.loc[(ECCC_RATE, int(year))])
        except KeyError as exc:
            raise KeyError(
                f"ECCC SC-CH4 at {ECCC_RATE}% has no year {int(year)}. "
                f"Do not extrapolate and do not fall back to SC-CO2."
            ) from exc
        out[i] = cad2021_to_cad2025(cad2021, p)
        out_ch4[i] = cad2021_to_cad2025(ch4_cad2021, p)
    return out, out_ch4


def _membership(specs: list[AssetSpec], name: str) -> np.ndarray:
    if name == "committed":
        return np.array([s.committed for s in specs], dtype=bool)
    if name == "committed_plus_advanced":
        return np.array([s.committed_plus_advanced for s in specs], dtype=bool)
    if name == "full":
        return np.array([s.full for s in specs], dtype=bool)
    raise ValueError(name)


def _summarise_yearly(
    yearly: np.ndarray,
    yearly_co2: np.ndarray,
    yearly_ch4_kt: np.ndarray,
    years: np.ndarray,
    prices: np.ndarray,
    prices_ch4: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """lifetime Mt, peak Mt, peak year, damage CAD billion, lifetime CO2-only Mt.

    Damages are per gas, as in the central case: CO2 at SC-CO2 and CH4 mass
    at SC-CH4, both at 2%, both already in CAD 2025.
    """
    lifetime = yearly.sum(axis=1)
    peak_idx = yearly.argmax(axis=1)
    peak_mt = yearly[np.arange(len(yearly)), peak_idx]
    peak_year = years[peak_idx]
    damage_bn = (
        (yearly_co2 * (prices * 1e6)[None, :]).sum(axis=1)
        + (yearly_ch4_kt * (prices_ch4 * 1e3)[None, :]).sum(axis=1)
    ) / 1e9
    return lifetime, peak_mt, peak_year, damage_bn, yearly_co2.sum(axis=1)


def _ci90(x: np.ndarray) -> tuple[float, float, float]:
    return (
        float(np.median(x)),
        float(np.percentile(x, 5)),
        float(np.percentile(x, 95)),
    )


def _simulate(
    specs: list[AssetSpec],
    years: np.ndarray,
    mtpa_to_t: float,
    liquefaction: float,
    upstream: np.ndarray,
    stage_draws: dict[str, np.ndarray],
    life_draw: np.ndarray,
    delay_draw: np.ndarray,
    inputs: dict,
    gwp100: float,
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray], dict[str, np.ndarray]]:
    """(CO2e Mt, CO2 Mt, CH4 kt) per build-out, n_draws x n_years."""
    n_draws = len(upstream)
    intensity, ch4_intensity = _intensity_by_draw(
        specs, upstream, stage_draws, liquefaction, inputs
    )
    yearly = {name: np.zeros((n_draws, len(years))) for name in BUILD_OUTS}
    yearly_co2 = {name: np.zeros((n_draws, len(years))) for name in BUILD_OUTS}
    yearly_ch4 = {name: np.zeros((n_draws, len(years))) for name in BUILD_OUTS}
    for j, spec in enumerate(specs):
        if spec.life_sampled:
            life = life_draw
        else:
            life = np.full(n_draws, spec.life_central, dtype=int)
        if spec.fid_ok:
            delay = np.zeros(n_draws, dtype=int)
        else:
            delay = delay_draw
        util = _util_matrix(
            years,
            spec.start,
            life,
            delay,
            spec.y1,
            spec.y2,
            spec.steady,
            spec.ramp,
            spec.licence_end,
        )
        base = spec.capacity_mtpa * mtpa_to_t * util / 1e6
        mt = base * intensity[:, [j]]
        ch4_co2e_mt = base * ch4_intensity[:, [j]]
        co2_mt = mt - ch4_co2e_mt
        ch4_kt = ch4_co2e_mt / gwp100 * 1000.0
        for name in BUILD_OUTS:
            if getattr(spec, name):
                yearly[name] += mt
                yearly_co2[name] += co2_mt
                yearly_ch4[name] += ch4_kt
    return yearly, yearly_co2, yearly_ch4


def _howarth_from_panel(
    panel: pd.DataFrame,
    assets: pd.DataFrame,
    years: np.ndarray,
    prices: np.ndarray,
    prices_ch4: np.ndarray,
) -> pd.DataFrame:
    sl = panel.loc[panel["scenario"] == HOWARTH_SCENARIO].copy()
    meta = assets[["project_id", "tier"]].drop_duplicates("project_id")
    sl = sl.merge(meta, on="project_id", how="left")
    sl["committed"] = sl["calc_group"].isin(("operating", "under_construction"))
    sl["committed_plus_advanced"] = sl["committed"] | (
        sl["tier"].astype(str) == "advanced_proposed"
    )
    sl["full"] = True
    rows = []
    cols = ["emissions_mtco2e", "co2_mt", "ch4_mass_kt"]
    for name in BUILD_OUTS:
        sub = sl.loc[sl[name]]
        grouped = sub.groupby("year")[cols].sum().reindex(years, fill_value=0.0)
        yearly = grouped["emissions_mtco2e"].to_numpy(dtype=float)
        yearly_co2 = grouped["co2_mt"].to_numpy(dtype=float)
        yearly_ch4 = grouped["ch4_mass_kt"].to_numpy(dtype=float)
        lifetime = float(yearly.sum())
        peak_i = int(yearly.argmax())
        rows.append(
            {
                "build_out": name,
                "upstream": 0.55,
                "lifetime_mtco2e": lifetime,
                "lifetime_co2_only_mt": float(yearly_co2.sum()),
                "lifetime_ch4_kt": float(yearly_ch4.sum()),
                "peak_year": int(years[peak_i]),
                "peak_mtco2e_yr": float(yearly[peak_i]),
                "central_damage_cad_billion": float(
                    (
                        (yearly_co2 * prices * 1e6).sum()
                        + (yearly_ch4 * prices_ch4 * 1e3).sum()
                    )
                    / 1e9
                ),
            }
        )
    return pd.DataFrame(rows)


def run_monte_carlo(
    inputs: dict,
    inputs_dir: Path,
    panel: pd.DataFrame,
) -> dict:
    params = inputs["params"]
    factors = inputs["factors"]
    liq = float(factors.loc["liquefaction", "central"])
    if abs(liq - LIQUEFACTION_FIXED) > 1e-12:
        raise AssertionError(
            f"Liquefaction central is {liq}, not {LIQUEFACTION_FIXED}. "
            "Monte Carlo will not run if the headline factor has moved."
        )
    seed = int(get_param(params, MC_SEED_PARAM))
    n_draws = int(get_param(params, MC_DRAWS_PARAM))
    mtpa_to_t = float(get_param(params, "mtpa_to_tonnes"))
    specs = _compile_assets(inputs)
    year0 = PANEL_START_YEAR
    year1 = max(s.start + 50 - 1 for s in specs)
    years = np.arange(year0, year1 + 1)
    prices, prices_ch4 = _eccc_price_cad2025(inputs_dir, years)
    gwp100 = float(get_param(params, "gwp100_ch4"))

    stage_bounds = {stage: _tri(factors, stage) for stage in SAMPLED_STAGES}

    # Central-point check: kernel at published values must match the panel.
    n1 = 1
    up_c = np.full(n1, float(inputs["upstream_by_scenario"][DEFAULT_SCENARIO]))
    st_c = {
        stage: np.full(n1, float(factors.loc[stage, "central"]))
        for stage in SAMPLED_STAGES
    }
    life_c = np.full(n1, int(get_param(params, "lifecycle_years_default")), dtype=int)
    delay_c = np.full(n1, int(get_param(params, "fid_delay_mid")), dtype=int)
    central_yearly, central_co2, _central_ch4 = _simulate(
        specs, years, mtpa_to_t, liq, up_c, st_c, life_c, delay_c, inputs, gwp100
    )
    published = (
        panel.loc[panel["scenario"] == DEFAULT_SCENARIO]
        .groupby("year")["emissions_mtco2e"]
        .sum()
        .reindex(years, fill_value=0.0)
        .to_numpy(dtype=float)
    )
    kernel_full = central_yearly["full"][0]
    max_abs = float(np.max(np.abs(kernel_full - published)))
    if max_abs > 1e-6:
        raise AssertionError(
            f"Monte Carlo kernel diverges from the published panel "
            f"(max abs {max_abs} Mt in a year)."
        )
    published_co2 = (
        panel.loc[panel["scenario"] == DEFAULT_SCENARIO]
        .groupby("year")["co2_mt"]
        .sum()
        .reindex(years, fill_value=0.0)
        .to_numpy(dtype=float)
    )
    max_abs_co2 = float(np.max(np.abs(central_co2["full"][0] - published_co2)))
    if max_abs_co2 > 1e-6:
        raise AssertionError(
            f"Monte Carlo CO2-only kernel diverges from the published panel "
            f"(max abs {max_abs_co2} Mt in a year)."
        )

    rng = np.random.default_rng(seed)
    t0 = perf_counter()
    upstream = rng.triangular(*UPSTREAM_TRI, size=n_draws)
    stage_draws = {
        stage: rng.triangular(*stage_bounds[stage], size=n_draws)
        for stage in SAMPLED_STAGES
    }
    life_draw = np.rint(rng.triangular(*LIFE_TRI, size=n_draws)).astype(int)
    delay_draw = np.rint(rng.triangular(*FID_TRI, size=n_draws)).astype(int)
    yearly, yearly_co2, yearly_ch4 = _simulate(
        specs,
        years,
        mtpa_to_t,
        liq,
        upstream,
        stage_draws,
        life_draw,
        delay_draw,
        inputs,
        gwp100,
    )
    physics_s = perf_counter() - t0
    t1 = perf_counter()
    draw_rows = []
    summary_rows = []
    for name in BUILD_OUTS:
        life, peak_mt, peak_year, damage, life_co2 = _summarise_yearly(
            yearly[name],
            yearly_co2[name],
            yearly_ch4[name],
            years,
            prices,
            prices_ch4,
        )
        life_ch4 = yearly_ch4[name].sum(axis=1)
        for i in range(n_draws):
            draw_rows.append(
                {
                    "draw": i,
                    "build_out": name,
                    "lifetime_mtco2e": float(life[i]),
                    "lifetime_co2_only_mt": float(life_co2[i]),
                    "lifetime_ch4_kt": float(life_ch4[i]),
                    "peak_mtco2e_yr": float(peak_mt[i]),
                    "peak_year": int(peak_year[i]),
                    "central_damage_cad_billion": float(damage[i]),
                    "upstream_tCO2e_per_t": float(upstream[i]),
                }
            )
        for metric, arr in (
            ("lifetime_mtco2e", life),
            ("lifetime_co2_only_mt", life_co2),
            ("lifetime_ch4_kt", life_ch4),
            ("peak_mtco2e_yr", peak_mt),
            ("central_damage_cad_billion", damage),
        ):
            med, lo, hi = _ci90(arr)
            summary_rows.append(
                {
                    "build_out": name,
                    "metric": metric,
                    "median": med,
                    "p05": lo,
                    "p95": hi,
                    "n_draws": n_draws,
                    "seed": seed,
                }
            )
    price_s = perf_counter() - t1
    draws = pd.DataFrame(draw_rows)
    summary = pd.DataFrame(summary_rows)
    howarth = _howarth_from_panel(
        panel, inputs["assets"], years, prices, prices_ch4
    )

    sampled_life_ids = [s.project_id for s in specs if s.life_sampled]
    sampled_fid_ids = [s.project_id for s in specs if not s.fid_ok]
    param_rows = [
        {
            "parameter": "upstream_production",
            "distribution": f"triangular{UPSTREAM_TRI}",
            "source": "inventory 0.22 / central 0.25 / GWP20-equivalent 0.33; Howarth 0.55 excluded",
            "sampled": True,
        },
        {
            "parameter": "liquefaction",
            "distribution": "fixed 0.29",
            "source": "Emission Factors central; 0.12 is electric, not an uncertainty band",
            "sampled": False,
        },
        *[
            {
                "parameter": stage,
                "distribution": f"triangular{_tri(factors, stage)}",
                "source": "Emission Factors range_low / central / range_high",
                "sampled": True,
            }
            for stage in SAMPLED_STAGES
        ],
        {
            "parameter": "fid_delay_mid",
            "distribution": f"triangular{FID_TRI}, rounded to int",
            "source": "Parameters fid_delay_low / mid / high; applied to non-FID assets",
            "sampled": True,
        },
        {
            "parameter": "lifecycle_years_default",
            "distribution": f"triangular{LIFE_TRI}, rounded to int",
            "source": (
                "Parameters lifespan_sensitivity_low / default / high. "
                f"Sampled for: {', '.join(sampled_life_ids) or 'none'}. "
                "Licence terms and stated project lives held."
            ),
            "sampled": True,
        },
        {
            "parameter": "utilisation ramp",
            "distribution": "fixed (year_1=0.4, year_2=0.7, steady=0.839, ramp=2)",
            "source": "No published range; IGU 83.9% is a point",
            "sampled": False,
        },
        {
            "parameter": "upstream_ch4_share",
            "distribution": "fixed 0.30",
            "source": "Not independent of the 0.22 × 1.5 upstream construction",
            "sampled": False,
        },
        {
            "parameter": "howarth_high",
            "distribution": "named point, upstream 0.55, other stages central",
            "source": "Scenarios sheet; excluded from the sampling distribution",
            "sampled": False,
        },
        {
            "parameter": MC_SEED_PARAM,
            "distribution": str(seed),
            "source": "Parameters sheet",
            "sampled": False,
        },
        {
            "parameter": MC_DRAWS_PARAM,
            "distribution": str(n_draws),
            "source": "Parameters sheet",
            "sampled": False,
        },
    ]
    return {
        "summary": summary,
        "draws": draws,
        "howarth": howarth,
        "parameters": pd.DataFrame(param_rows),
        "n_draws": n_draws,
        "seed": seed,
        "physics_seconds": physics_s,
        "price_seconds": price_s,
        "kernel_panel_max_abs_mt": max_abs,
        "kernel_panel_max_abs_co2_mt": max_abs_co2,
        "sampled_life_ids": sampled_life_ids,
        "sampled_fid_ids": sampled_fid_ids,
        "n_assets": len(specs),
        "years": (int(years[0]), int(years[-1])),
    }


def format_mc_markdown(mc: dict, published: dict | None = None) -> list[str]:
    lines = []
    lines.append(
        "## Monte Carlo (physics sampled, ECCC 2% per gas applied after)"
    )
    lines.append("")
    lines.append(
        f"{mc['n_draws']:,} draws, seed `{mc['seed']}`. "
        f"Physics {mc['physics_seconds']:.2f}s; pricing {mc['price_seconds']:.2f}s. "
        f"Kernel vs published panel max abs {mc['kernel_panel_max_abs_mt']:.1e} Mt. "
        "Liquefaction held at 0.29. Howarth 0.55 is a named point, not a draw. "
        "Draws are on the headline scope (export chain). "
        "Each draw carries its own upstream and shipping factor, so its CH4 "
        "mass moves with it; damages are CO2 at SC-CO2 plus CH4 mass at "
        "SC-CH4, the same per-gas treatment as the central case."
    )
    lines.append("")
    lines.append(
        "| build-out | lifetime median [p5, p95] Mt | "
        "peak-year median [p5, p95] Mt | "
        "ECCC 2% damage median [p5, p95] CAD bn |"
    )
    lines.append("|---|---|---|---|")
    summ = mc["summary"]
    for name in BUILD_OUTS:
        def _cell(metric: str) -> str:
            r = summ.loc[
                (summ["build_out"] == name) & (summ["metric"] == metric)
            ].iloc[0]
            if metric == "central_damage_cad_billion":
                return f"{r['median']:.0f} [{r['p05']:.0f}, {r['p95']:.0f}]"
            return f"{r['median']:.1f} [{r['p05']:.1f}, {r['p95']:.1f}]"

        lines.append(
            f"| {name} | {_cell('lifetime_mtco2e')} | "
            f"{_cell('peak_mtco2e_yr')} | "
            f"{_cell('central_damage_cad_billion')} |"
        )
    lines.append("")
    lines.append("Howarth 0.55 (other stages central, not inside the interval):")
    lines.append("")
    lines.append("| build-out | lifetime Mt | peak year / Mt | ECCC 2% CAD bn |")
    lines.append("|---|---|---|---|")
    for r in mc["howarth"].itertuples():
        lines.append(
            f"| {r.build_out} | {r.lifetime_mtco2e:.1f} | "
            f"{int(r.peak_year)} / {r.peak_mtco2e_yr:.1f} | "
            f"{r.central_damage_cad_billion:.0f} |"
        )
    lines.append("")
    if published is not None:
        def _full(metric: str) -> pd.Series:
            return summ.loc[
                (summ["build_out"] == "full") & (summ["metric"] == metric)
            ].iloc[0]

        life = _full("lifetime_mtco2e")
        peak = _full("peak_mtco2e_yr")
        dmg = _full("central_damage_cad_billion")
        lines.append("Central case versus Monte Carlo median (full build-out):")
        lines.append("")
        lines.append("| quantity | central case | Monte Carlo median [p5, p95] |")
        lines.append("|---|---|---|")
        lines.append(
            f"| Lifetime (Mt) | {published['lifetime_mt']:.1f} | "
            f"{life['median']:.1f} [{life['p05']:.1f}, {life['p95']:.1f}] |"
        )
        lines.append(
            f"| Peak-year (Mt) | {published['peak_mt']:.1f} in {int(published['peak_year'])} | "
            f"{peak['median']:.1f} [{peak['p05']:.1f}, {peak['p95']:.1f}] |"
        )
        lines.append(
            f"| ECCC 2% damage (CAD bn) | {published['damage_cad_bn']:.0f} | "
            f"{dmg['median']:.0f} [{dmg['p05']:.0f}, {dmg['p95']:.0f}] |"
        )
        lines.append("")
        lines.append(
            "They differ because the stage triangles are right-skewed "
            "(shipping 0.05 / 0.12 / 0.31 especially): the Monte Carlo median is "
            "not the point estimate from central factor values."
        )
        lines.append("")
        lines.append(
            "Which of the two should be the paper's headline number is not chosen here."
        )
        lines.append("")
    return lines
