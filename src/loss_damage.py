"""Global climate loss and damage from modelled LNG emissions.

Physical tonnes come from the existing lifecycle model (full chain, GWP100
CO2e). This module does not change those calculations.

Burke path (headline): Hatton (2026) applied to Burke et al. (2026) SC-CO2
for a 2020 pulse, inflated to 2025 CAD, grown at a real rate g:

    SC_t = SC_2020_CAD2025 * (1 + g) ** (t - 2020)
    L&D  = sum_t SC_t * E_t

The SC already discounts the damage stream; the sum across emission years
is not further discounted to 2025 (Hatton's aggregation). A 2025 NPV using
the same r is reported alongside.

Central case (desk research 25 Aug 2026): 2% discount, g = 0, Figure 2e
through-2300 SC as the horizon-consistent price, Conference Board
whole-chain GDP as the Canada denominator. Headline metrics are the
externality ratio (global L&D / Canadian value) and the Burke-channel
externalisation share (1 − Canada's 0.17% of a 1990 pulse). The national
cost-benefit test is reported, not led with.

ECCC path: official SC-CO2 and SC-CH4 schedules (C$2021) inflated to C$2025.

Central valuation splits upstream into CO2 mass and CH4 mass (ECCC FAQ 4.2).
Burke has no SC-CH4; methane is priced at Burke SC-CO2 times the ECCC
SC-CH4/SC-CO2 ratio. GWP100-CO2e x SC-CO2 is kept as a comparison row.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.inputs import DEFAULT_SCENARIO, INTENSITY_SCENARIOS, MissingInputError, get_param
from src.model import GROUPS, _stage_intensity
from src.report_params import resolve_report_params
from src.trajectories import build_emissions_panel, calendar_bounds, project_annual_mt

BURKE_RATES = (1.5, 2.0, 3.0, 5.0)
GROWTH_RATES = (-0.02, 0.0, 0.02)
ECCC_RATES = (1.5, 2.0, 2.5)
# GWP20 is a physical-metric sensitivity, not an SC-CO2 damages case.
LD_EMISSION_SCENARIOS = tuple(
    s for s in INTENSITY_SCENARIOS if s != "near_term_methane_gwp20"
)
RATE_COL = {
    1.5: "1.5%",
    2.0: "2%",
    3.0: "3%",
    5.0: "5%",
}


def _required(params: dict, name: str):
    if name not in params:
        raise MissingInputError(
            f"Missing loss-and-damage parameter '{name}' in "
            f"Inputs/loss_damage/parameters.csv."
        )
    value = params[name]
    if value is None or (isinstance(value, float) and pd.isna(value)):
        raise MissingInputError(
            f"Loss-and-damage parameter '{name}' is blank. "
            f"A missing value must not be treated as zero."
        )
    return value


def load_ld_params(inputs_dir: Path) -> dict:
    path = inputs_dir / "loss_damage" / "parameters.csv"
    if not path.exists():
        raise MissingInputError(f"Missing {path}.")
    df = pd.read_csv(path)
    params = {}
    meta = []
    for _, row in df.iterrows():
        name = str(row["parameter"]).strip()
        params[name] = row["value"]
        meta.append(row)
    for name in (
        "pulse_year",
        "analysis_year",
        "damages_horizon_year",
        "us_gdp_deflator_2020",
        "us_gdp_deflator_2025",
        "usd_cad_2025",
        "canada_gdp_deflator_2021",
        "canada_gdp_deflator_2025",
        "central_discount_rate_pct",
        "central_growth_rate",
        "central_horizon",
        "central_horizon_discounting",
        "burke_pulse_file",
        "burke_horizons_file",
        "burke_country_shares_file",
        "eccc_schedule_file",
        "eccc_central_discount_rate_pct",
        "cboc_gdp_cad_per_year",
        "cboc_scenario_mtpa",
        "cboc_operating_years",
        "cboc_operating_years_sensitivity",
        "cboc_dollar_year",
        "eccc_ch4_schedule_file",
        "burke_fig4_canada_file",
        "canada_gdp_deflator_2020",
    ):
        _required(params, name)
    return {"params": params, "meta": pd.DataFrame(meta), "inputs_dir": inputs_dir}


def load_burke_sc_2020(inputs_dir: Path, params: dict) -> dict[float, float]:
    """2020 USD / tCO2 for a 2020 pulse, damages 2021-2100, by discount rate."""
    rel = Path(str(_required(params, "burke_pulse_file")))
    path = inputs_dir / rel
    if not path.exists():
        raise MissingInputError(f"Missing Burke pulse file {path}.")
    df = pd.read_csv(path)
    pulse = int(float(_required(params, "pulse_year")))
    out = {}
    for rate, label in RATE_COL.items():
        row = df.loc[
            (df["emitter"].astype(int) == pulse) & (df["discount_rate"] == label)
        ]
        if len(row) != 1:
            raise MissingInputError(
                f"Burke file {path} has {len(row)} rows for pulse {pulse} "
                f"discount {label}; expected 1."
            )
        out[rate] = float(row.iloc[0]["total_damages"])
    return out


def load_horizons(inputs_dir: Path, params: dict) -> pd.DataFrame:
    rel = Path(str(_required(params, "burke_horizons_file")))
    path = inputs_dir / rel
    if not path.exists():
        raise MissingInputError(f"Missing Burke horizons file {path}.")
    df = pd.read_csv(path)
    need = {"horizon", "discounting", "sc_co2_usd2020_per_t"}
    if not need.issubset(df.columns):
        raise MissingInputError(f"Horizons file missing {need - set(df.columns)}.")
    return df


def load_canada_fd_share(inputs_dir: Path, params: dict) -> tuple[float, float, pd.Series]:
    """Canada share of FD-CO2 from a 1990 1 Gt pulse (fraction, not percent).

    Validates the UK historical share against Hatton's 1.6%. Do not treat
    Canada's dam_FD per tonne as a 2020s pulse rate — apply the share.
    """
    rel = Path(str(_required(params, "burke_country_shares_file")))
    path = inputs_dir / rel
    if not path.exists():
        raise MissingInputError(f"Missing country shares file {path}.")
    df = pd.read_csv(path)
    gbr = df.loc[df["ISO3"] == "GBR"]
    can = df.loc[df["ISO3"] == "CAN"]
    if len(gbr) != 1 or len(can) != 1:
        raise MissingInputError("Country shares file must have one GBR and one CAN row.")
    gbr_hd = float(gbr.iloc[0]["share_HD_%"])
    if abs(gbr_hd - 1.6096) > 0.01:
        raise MissingInputError(
            f"UK share_HD_% is {gbr_hd}, expected ~1.6096 (Hatton/Burke check)."
        )
    share = float(can.iloc[0]["share_FD_%"]) / 100.0
    uk_fd = float(gbr.iloc[0]["share_FD_%"]) / 100.0
    return share, uk_fd, can.iloc[0]


def load_eccc_schedule(inputs_dir: Path, params: dict) -> pd.DataFrame:
    rel = Path(str(_required(params, "eccc_schedule_file")))
    path = inputs_dir / rel
    if not path.exists():
        raise MissingInputError(f"Missing ECCC schedule {path}.")
    df = pd.read_csv(path)
    need = {"year", "discount_rate_pct", "sc_co2_cad2021"}
    if not need.issubset(df.columns):
        raise MissingInputError(f"ECCC schedule missing columns {need - set(df.columns)}.")
    return df


def load_eccc_ch4(inputs_dir: Path, params: dict) -> pd.DataFrame:
    rel = Path(str(_required(params, "eccc_ch4_schedule_file")))
    path = inputs_dir / rel
    if not path.exists():
        raise MissingInputError(f"Missing ECCC SC-CH4 schedule {path}.")
    df = pd.read_csv(path)
    need = {"year", "discount_rate_pct", "sc_ch4_cad2021"}
    if not need.issubset(df.columns):
        raise MissingInputError(f"ECCC SC-CH4 missing columns {need - set(df.columns)}.")
    check = df.loc[(df["year"] == 2020) & (df["discount_rate_pct"] == 2.0)]
    if len(check) != 1 or abs(float(check.iloc[0]["sc_ch4_cad2021"]) - 2107) > 0.5:
        raise MissingInputError("ECCC SC-CH4 2020 at 2% must be 2107 (Table 1).")
    return df


def load_fig4_canada(inputs_dir: Path, params: dict) -> dict:
    rel = Path(str(_required(params, "burke_fig4_canada_file")))
    path = inputs_dir / rel
    if not path.exists():
        raise MissingInputError(f"Missing Figure 4 Canada extract {path}.")
    df = pd.read_csv(path).set_index("item")
    usa = float(df.loc["usa_owing_usd", "value"])
    if abs(usa / 1e12 - 10.18) > 0.15:
        raise MissingInputError(f"Figure 4 USA owing is {usa/1e12:.2f}T; expected ~10.18T.")
    return {
        "canada_owing_usd": float(df.loc["canada_emissions_caused_usd", "value"]),
        "canada_emitter_share": float(df.loc["canada_share_of_global_owing", "value"]),
        "global_owing_usd": float(df.loc["global_owing_usd", "value"]),
        "canada_in_recipient_panel": float(df.loc["canada_in_owed_to_panel", "value"]) == 1.0,
        "usa_owing_usd": usa,
        "china_owing_usd": float(df.loc["china_owing_usd", "value"]),
        "eu_owing_usd": float(df.loc["eu_owing_usd", "value"]),
        "uk_owing_usd": float(df.loc["uk_owing_usd", "value"]),
    }


def cad_vintage_to_cad2025(cad: float, vintage_year: int, params: dict) -> float:
    d0 = float(_required(params, f"canada_gdp_deflator_{vintage_year}"))
    d1 = float(_required(params, "canada_gdp_deflator_2025"))
    return cad * (d1 / d0)


def chain_gas_intensities(row, scenario: str, inputs: dict) -> tuple[float, float, float, float]:
    """tCO2e, tCO2, tCH4 per tonne LNG for this asset's chain.

    Upstream CO2 is the inventory CO2 portion; any excess of the scenario
    upstream factor over that portion is methane CO2e, converted at GWP100.
    Other stages are treated as CO2 (pipeline methane and shipping slip stay
    inside the CO2e total as CO2). Import chains have no upstream.
    """
    params = inputs["params"]
    gwp = float(get_param(params, "gwp100_ch4"))
    share = float(get_param(params, "upstream_ch4_share"))
    inv = float(inputs["upstream_by_scenario"]["inventory_as_reported"])
    co2_up = inv * (1.0 - share)
    tco2e = tco2 = tch4 = 0.0
    for stage, _where in inputs["chains"][row["chain"]]:
        intensity, _ = _stage_intensity(stage, row, scenario, inputs)
        tco2e += intensity
        if stage == "upstream_production":
            ch4_co2e = max(intensity - co2_up, 0.0)
            tco2 += min(intensity, co2_up)
            tch4 += ch4_co2e / gwp
        else:
            tco2 += intensity
    return tco2e, tco2, tch4, gwp


def usd2020_to_cad2025(usd_2020: float, params: dict) -> float:
    us0 = float(_required(params, "us_gdp_deflator_2020"))
    us1 = float(_required(params, "us_gdp_deflator_2025"))
    fx = float(_required(params, "usd_cad_2025"))
    return usd_2020 * (us1 / us0) * fx


def cad2021_to_cad2025(cad_2021: float, params: dict) -> float:
    c0 = float(_required(params, "canada_gdp_deflator_2021"))
    c1 = float(_required(params, "canada_gdp_deflator_2025"))
    return cad_2021 * (c1 / c0)


def burke_sc_cad2025(year: int, rate: float, growth: float, sc2020_cad: float, params: dict) -> float:
    pulse = int(float(_required(params, "pulse_year")))
    return sc2020_cad * (1.0 + growth) ** (year - pulse)


def project_full_life_mt(
    row,
    inputs: dict,
    scenario: str,
    assumed_start: int,
    years: range,
) -> list[tuple[int, float]]:
    """(year, MtCO2e) for years with any modelled output. Legacy -> empty."""
    from src.model import _is_legacy, _lifespan

    if pd.isna(row["capacity_mtpa"]):
        return []
    life, _ = _lifespan(row, inputs["params"])
    if _is_legacy(row, life):
        return []
    out = []
    for year in years:
        mt = project_annual_mt(row, year, inputs, scenario, assumed_start)
        if mt is None:
            return []
        if mt != 0.0:
            out.append((year, float(mt)))
    return out


def compute_loss_damage(
    inputs: dict,
    inputs_dir: Path,
    panel: pd.DataFrame | None = None,
) -> dict:
    ld = load_ld_params(inputs_dir)
    p = ld["params"]
    burke_usd = load_burke_sc_2020(inputs_dir, p)
    horizons = load_horizons(inputs_dir, p)
    canada_share, uk_fd_share, can_row = load_canada_fd_share(inputs_dir, p)
    eccc = load_eccc_schedule(inputs_dir, p)
    eccc_ch4 = load_eccc_ch4(inputs_dir, p)
    fig4 = load_fig4_canada(inputs_dir, p)
    report, _ = resolve_report_params(inputs["params"])
    assumed_start = int(report["assumed_first_export_year_if_missing"])
    year0, year1 = calendar_bounds(inputs, assumed_start)
    horizon = int(float(_required(p, "damages_horizon_year")))
    analysis = int(float(_required(p, "analysis_year")))
    central_r = float(_required(p, "central_discount_rate_pct"))
    central_g = float(_required(p, "central_growth_rate"))
    central_horizon = str(_required(p, "central_horizon")).strip()
    central_h_disc = str(_required(p, "central_horizon_discounting")).strip()
    eccc_r = float(_required(p, "eccc_central_discount_rate_pct"))
    cboc_gdp = float(_required(p, "cboc_gdp_cad_per_year"))
    cboc_mtpa = float(_required(p, "cboc_scenario_mtpa"))
    cboc_years = int(float(_required(p, "cboc_operating_years")))
    cboc_years_lo = int(float(_required(p, "cboc_operating_years_sensitivity")))
    cboc_dollar_year = int(float(_required(p, "cboc_dollar_year")))

    eccc_idx = eccc.set_index(["discount_rate_pct", "year"])["sc_co2_cad2021"]
    eccc_ch4_idx = eccc_ch4.set_index(["discount_rate_pct", "year"])["sc_ch4_cad2021"]
    eccc_max_year = int(eccc["year"].max())
    if year1 > eccc_max_year:
        raise MissingInputError(
            f"Full-life emissions run to {year1} but ECCC SC-CO2 ends in "
            f"{eccc_max_year}. Do not extrapolate."
        )
    ch4_max_year = int(eccc_ch4["year"].max())
    if year1 > ch4_max_year:
        raise MissingInputError(
            f"Full-life emissions run to {year1} but ECCC SC-CH4 ends in "
            f"{ch4_max_year}. Do not extrapolate."
        )
    if year1 > horizon:
        raise MissingInputError(
            f"Full-life emissions run to {year1} past damages horizon {horizon}."
        )

    burke_cad = {rate: usd2020_to_cad2025(usd, p) for rate, usd in burke_usd.items()}
    try:
        eccc_ch4_2020 = float(eccc_ch4_idx.loc[(2.0, 2020)])
        eccc_co2_2020 = float(eccc_idx.loc[(2.0, 2020)])
    except KeyError as exc:
        raise MissingInputError("ECCC schedules need 2020 at 2% for the CH4/CO2 ratio.") from exc
    ch4_co2_ratio_2020 = eccc_ch4_2020 / eccc_co2_2020

    split_cache: dict[tuple, tuple[float, float, float, float]] = {}

    def _split_for(asset_row, scen: str):
        key = (asset_row["project_id"], scen)
        if key not in split_cache:
            split_cache[key] = chain_gas_intensities(asset_row, scen, inputs)
        return split_cache[key]

    if panel is None:
        panel = build_emissions_panel(
            inputs,
            scenarios=LD_EMISSION_SCENARIOS,
            assumed_start=assumed_start,
        )
    else:
        panel = panel.loc[panel["scenario"].isin(LD_EMISSION_SCENARIOS)].copy()
        if not len(panel):
            raise MissingInputError("Emissions panel has no L&D scenarios.")
    assets_by_id = {r["project_id"]: r for _, r in inputs["assets"].iterrows()}

    year_rows = []
    for _, prec in panel.iterrows():
        row = assets_by_id[prec["project_id"]]
        scenario = prec["scenario"]
        year = int(prec["year"])
        mt = float(prec["emissions_mtco2e"])
        tco2e_i, tco2_i, tch4_i, _gwp = _split_for(row, scenario)
        tonnes_co2e = mt * 1e6
        if tco2e_i <= 0:
            tonnes_co2 = tonnes_co2e
            tonnes_ch4 = 0.0
        else:
            tonnes_co2 = tonnes_co2e * (tco2_i / tco2e_i)
            tonnes_ch4 = tonnes_co2e * (tch4_i / tco2e_i)
        try:
            ratio_yr = float(eccc_ch4_idx.loc[(2.0, year)]) / float(
                eccc_idx.loc[(2.0, year)]
            )
        except KeyError as exc:
            raise MissingInputError(
                f"ECCC CH4/CO2 ratio missing for 2% year {year}."
            ) from exc
        for rate in BURKE_RATES:
            for g in GROWTH_RATES:
                sc = burke_sc_cad2025(year, rate, g, burke_cad[rate], p)
                hatton_gwp = sc * tonnes_co2e
                hatton = sc * tonnes_co2 + (sc * ratio_yr) * tonnes_ch4
                npv = hatton / ((1.0 + rate / 100.0) ** (year - analysis))
                year_rows.append({
                    "price_family": "burke",
                    "scenario": scenario,
                    "project_id": row["project_id"],
                    "project_name": row["project_name"],
                    "calc_group": row["calc_group"],
                    "chain": row["chain"],
                    "year": year,
                    "emissions_mtco2e": mt,
                    "emissions_mtco2": tonnes_co2 / 1e6,
                    "emissions_mtch4": tonnes_ch4 / 1e6,
                    "discount_rate_pct": rate,
                    "growth_rate": g,
                    "sc_cad2025_per_t": sc,
                    "hatton_sum_cad": hatton,
                    "hatton_gwp_cad": hatton_gwp,
                    "npv_analysis_year_cad": npv,
                })
        for rate in ECCC_RATES:
            try:
                sc21 = float(eccc_idx.loc[(rate, year)])
                sc21_ch4 = float(eccc_ch4_idx.loc[(rate, year)])
            except KeyError as exc:
                raise MissingInputError(
                    f"ECCC schedule has no SC-CO2/SC-CH4 for rate {rate}% year {year}."
                ) from exc
            sc = cad2021_to_cad2025(sc21, p)
            sc_ch4 = cad2021_to_cad2025(sc21_ch4, p)
            undisc_gwp = sc * tonnes_co2e
            undisc = sc * tonnes_co2 + sc_ch4 * tonnes_ch4
            npv = undisc / ((1.0 + rate / 100.0) ** (year - analysis))
            year_rows.append({
                "price_family": "eccc",
                "scenario": scenario,
                "project_id": row["project_id"],
                "project_name": row["project_name"],
                "calc_group": row["calc_group"],
                "chain": row["chain"],
                "year": year,
                "emissions_mtco2e": mt,
                "emissions_mtco2": tonnes_co2 / 1e6,
                "emissions_mtch4": tonnes_ch4 / 1e6,
                "discount_rate_pct": rate,
                "growth_rate": None,
                "sc_cad2025_per_t": sc,
                "hatton_sum_cad": undisc,
                "hatton_gwp_cad": undisc_gwp,
                "npv_analysis_year_cad": npv,
            })


    by_year = pd.DataFrame(year_rows)
    if not len(by_year):
        raise MissingInputError("Loss-and-damage produced no emission years.")

    def _aggregate(df: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
        em = (
            df.drop_duplicates(keys + ["project_id", "year"])
            .groupby(keys, dropna=False, sort=False)[
                ["emissions_mtco2e", "emissions_mtco2", "emissions_mtch4"]
            ]
            .sum()
        )
        money = df.groupby(keys, dropna=False, sort=False).agg(
            hatton_sum_cad=("hatton_sum_cad", "sum"),
            hatton_gwp_cad=("hatton_gwp_cad", "sum"),
            npv_analysis_year_cad=("npv_analysis_year_cad", "sum"),
        )
        return money.join(em).reset_index()

    project_keys = [
        "price_family",
        "scenario",
        "project_id",
        "project_name",
        "calc_group",
        "chain",
        "discount_rate_pct",
        "growth_rate",
    ]
    group_keys = [
        "price_family",
        "scenario",
        "calc_group",
        "discount_rate_pct",
        "growth_rate",
    ]
    by_project = _aggregate(by_year, project_keys)
    by_group = _aggregate(by_year, group_keys)

    def _slice(family, scenario, rate, growth):
        q = (
            (by_group["price_family"] == family)
            & (by_group["scenario"] == scenario)
            & (by_group["discount_rate_pct"] == rate)
        )
        if growth is None:
            q = q & by_group["growth_rate"].isna()
        else:
            q = q & (by_group["growth_rate"] == growth)
        return by_group.loc[q].copy()

    central = _slice("burke", DEFAULT_SCENARIO, central_r, central_g)
    eccc_central = _slice("eccc", DEFAULT_SCENARIO, eccc_r, None)

    def _total(df: pd.DataFrame) -> float:
        return float(df["hatton_sum_cad"].sum()) if len(df) else 0.0

    def _npv(df: pd.DataFrame) -> float:
        return float(df["npv_analysis_year_cad"].sum()) if len(df) else 0.0

    proposed_export_mtpa = float(
        inputs["assets"].loc[
            (inputs["assets"]["calc_group"] == "proposed")
            & (inputs["assets"]["chain"] == "export")
            & inputs["assets"]["capacity_mtpa"].notna(),
            "capacity_mtpa",
        ].sum()
    )
    committed_export_mtpa = float(
        inputs["assets"].loc[
            (inputs["assets"]["calc_group"].isin(["operating", "under_construction"]))
            & (inputs["assets"]["chain"] == "export")
            & inputs["assets"]["capacity_mtpa"].notna(),
            "capacity_mtpa",
        ].sum()
    )
    gdp_per_mtpa = cboc_gdp / cboc_mtpa
    v_published = gdp_per_mtpa * proposed_export_mtpa * cboc_years
    v_proposed = cad_vintage_to_cad2025(v_published, cboc_dollar_year, p)
    v_proposed_30 = cad_vintage_to_cad2025(
        gdp_per_mtpa * proposed_export_mtpa * cboc_years_lo, cboc_dollar_year, p
    )
    v_committed = cad_vintage_to_cad2025(
        gdp_per_mtpa * committed_export_mtpa * cboc_years, cboc_dollar_year, p
    )
    v_published_30 = gdp_per_mtpa * proposed_export_mtpa * cboc_years_lo

    phys_years = (
        by_year.loc[
            (by_year["price_family"] == "burke")
            & (by_year["scenario"] == DEFAULT_SCENARIO)
            & (by_year["discount_rate_pct"] == central_r)
            & (by_year["growth_rate"] == central_g)
        ]
        .drop_duplicates(["project_id", "year"])
    )
    tonnes_by_group = phys_years.groupby("calc_group")["emissions_mtco2e"].sum()
    tonnes_co2_by_group = phys_years.groupby("calc_group")["emissions_mtco2"].sum()
    tonnes_ch4_by_group = phys_years.groupby("calc_group")["emissions_mtch4"].sum()
    tonnes_all = float(tonnes_by_group.sum())
    tonnes_proposed = float(tonnes_by_group.get("proposed", 0.0))
    tonnes_co2_all = float(tonnes_co2_by_group.sum())
    tonnes_ch4_all = float(tonnes_ch4_by_group.sum())
    tonnes_co2_proposed = float(tonnes_co2_by_group.get("proposed", 0.0))
    tonnes_ch4_proposed = float(tonnes_ch4_by_group.get("proposed", 0.0))

    def _gas_damages(sc_cad: float, t_co2: float, t_ch4: float) -> float:
        return t_co2 * 1e6 * sc_cad + t_ch4 * 1e6 * sc_cad * ch4_co2_ratio_2020

    horizon_rows = []
    for _, hr in horizons.iterrows():
        sc_cad = usd2020_to_cad2025(float(hr["sc_co2_usd2020_per_t"]), p)
        total = _gas_damages(sc_cad, tonnes_co2_all, tonnes_ch4_all)
        proposed = _gas_damages(sc_cad, tonnes_co2_proposed, tonnes_ch4_proposed)
        operating = _gas_damages(
            sc_cad,
            float(tonnes_co2_by_group.get("operating", 0.0)),
            float(tonnes_ch4_by_group.get("operating", 0.0)),
        )
        uc = _gas_damages(
            sc_cad,
            float(tonnes_co2_by_group.get("under_construction", 0.0)),
            float(tonnes_ch4_by_group.get("under_construction", 0.0)),
        )
        proposed_gwp = tonnes_proposed * 1e6 * sc_cad
        canada_borne_prop = proposed * canada_share
        ratio = None if v_proposed == 0 else proposed / v_proposed
        nat = None if canada_borne_prop == 0 else v_proposed / canada_borne_prop
        horizon_rows.append({
            "horizon": hr["horizon"],
            "discounting": hr["discounting"],
            "sc_co2_usd2020_per_t": float(hr["sc_co2_usd2020_per_t"]),
            "sc_co2_cad2025_per_t": sc_cad,
            "is_central": (
                str(hr["horizon"]) == central_horizon
                and str(hr["discounting"]) == central_h_disc
            ),
            "total_cad_billion": total / 1e9,
            "proposed_cad_billion": proposed / 1e9,
            "proposed_gwp_cad_billion": proposed_gwp / 1e9,
            "operating_cad_billion": operating / 1e9,
            "under_construction_cad_billion": uc / 1e9,
            "canada_share_fd": canada_share,
            "canada_borne_proposed_cad_billion": canada_borne_prop / 1e9,
            "externalisation_share": 1.0 - canada_share,
            "canada_value_proposed_cad_billion": v_proposed / 1e9,
            "canada_value_proposed_as_published_cad_billion": v_published / 1e9,
            "externality_ratio_proposed": ratio,
            "national_value_over_borne": nat,
            "breakeven_share_proposed": None if proposed == 0 else v_proposed / proposed,
        })
    horizon_table = pd.DataFrame(horizon_rows)
    h_central = horizon_table.loc[horizon_table["is_central"]]
    if len(h_central) != 1:
        raise MissingInputError(
            f"central_horizon={central_horizon!r} discounting={central_h_disc!r} "
            f"matched {len(h_central)} horizon rows."
        )
    h_central = h_central.iloc[0]

    headline_rows = []
    for label, df, family, method in (
        ("burke_central_hatton", central, "burke", "hatton_sum"),
        ("burke_central_npv_2025", central, "burke", "npv_analysis_year"),
        ("eccc_central_npv_2025", eccc_central, "eccc", "npv_analysis_year"),
        ("eccc_central_undiscounted_across_years", eccc_central, "eccc", "hatton_sum"),
    ):
        total = _total(df) if method == "hatton_sum" else _npv(df)
        by_g = {
            g: (
                float(df.loc[df["calc_group"] == g, "hatton_sum_cad"].sum())
                if method == "hatton_sum"
                else float(df.loc[df["calc_group"] == g, "npv_analysis_year_cad"].sum())
            )
            for g in GROUPS
        }
        proposed = by_g["proposed"]
        committed = by_g["operating"] + by_g["under_construction"]
        inv = None if v_proposed == 0 or total == 0 else v_proposed / total
        inv_prop = None if v_proposed == 0 or proposed == 0 else v_proposed / proposed
        headline_rows.append({
            "case": label,
            "price_family": family,
            "aggregation": method,
            "scenario": DEFAULT_SCENARIO,
            "currency": "CAD 2025",
            "total_cad": total,
            "total_cad_billion": total / 1e9,
            "operating_cad_billion": by_g["operating"] / 1e9,
            "under_construction_cad_billion": by_g["under_construction"] / 1e9,
            "proposed_cad_billion": proposed / 1e9,
            "committed_cad_billion": committed / 1e9,
            "canada_economic_value_proposed_cad": v_proposed,
            "breakeven_canada_share_all": inv,
            "breakeven_canada_share_proposed": inv_prop,
            "breakeven_note": "technique only; not the headline (actual Burke share is known)",
        })
    headline = pd.DataFrame(headline_rows)

    # Sensitivity grid: Burke rate × g, measurement_central, Hatton sum, all groups
    sens = by_group.loc[
        (by_group["price_family"] == "burke")
        & (by_group["scenario"] == DEFAULT_SCENARIO)
    ].copy()
    grid_rows = []
    for rate in BURKE_RATES:
        for g in GROWTH_RATES:
            sl = sens.loc[
                (sens["discount_rate_pct"] == rate) & (sens["growth_rate"] == g)
            ]
            grid_rows.append({
                "discount_rate_pct": rate,
                "growth_rate": g,
                "total_cad_billion": float(sl["hatton_sum_cad"].sum()) / 1e9,
                "proposed_cad_billion": float(
                    sl.loc[sl["calc_group"] == "proposed", "hatton_sum_cad"].sum()
                ) / 1e9,
                "is_central": rate == central_r and g == central_g,
            })
    burke_grid = pd.DataFrame(grid_rows)

    eccc_sens = []
    for rate in ECCC_RATES:
        sl = by_group.loc[
            (by_group["price_family"] == "eccc")
            & (by_group["scenario"] == DEFAULT_SCENARIO)
            & (by_group["discount_rate_pct"] == rate)
        ]
        eccc_sens.append({
            "discount_rate_pct": rate,
            "npv_2025_total_cad_billion": float(sl["npv_analysis_year_cad"].sum()) / 1e9,
            "npv_2025_proposed_cad_billion": float(
                sl.loc[sl["calc_group"] == "proposed", "npv_analysis_year_cad"].sum()
            ) / 1e9,
            "is_central": rate == eccc_r,
        })
    eccc_grid = pd.DataFrame(eccc_sens)

    phys = []
    for scenario in LD_EMISSION_SCENARIOS:
        sl = by_group.loc[
            (by_group["price_family"] == "burke")
            & (by_group["scenario"] == scenario)
            & (by_group["discount_rate_pct"] == central_r)
            & (by_group["growth_rate"] == central_g)
        ]
        phys.append({
            "scenario": scenario,
            "total_cad_billion": float(sl["hatton_sum_cad"].sum()) / 1e9,
            "proposed_cad_billion": float(
                sl.loc[sl["calc_group"] == "proposed", "hatton_sum_cad"].sum()
            ) / 1e9,
        })
    physical_scenarios = pd.DataFrame(phys)

    sc_audit = []
    for rate, usd in burke_usd.items():
        cad = burke_cad[rate]
        sc_audit.append({
            "price_family": "burke",
            "discount_rate_pct": rate,
            "sc_pulse_year_usd2020": usd,
            "sc_pulse_year_cad2025": cad,
            "sc_analysis_year_cad2025_g_central": burke_sc_cad2025(
                analysis, rate, central_g, cad, p
            ) if rate == central_r else None,
        })
    sc_table = pd.DataFrame(sc_audit)

    # Keep by_year manageable: central Burke + central ECCC, default scenario only
    by_year_central = by_year.loc[
        (by_year["scenario"] == DEFAULT_SCENARIO)
        & (
            (
                (by_year["price_family"] == "burke")
                & (by_year["discount_rate_pct"] == central_r)
                & (by_year["growth_rate"] == central_g)
            )
            | (
                (by_year["price_family"] == "eccc")
                & (by_year["discount_rate_pct"] == eccc_r)
            )
        )
    ].copy()

    by_project_central = by_project.loc[
        (by_project["scenario"] == DEFAULT_SCENARIO)
        & (
            (
                (by_project["price_family"] == "burke")
                & (by_project["discount_rate_pct"] == central_r)
                & (by_project["growth_rate"] == central_g)
            )
            | (
                (by_project["price_family"] == "eccc")
                & (by_project["discount_rate_pct"] == eccc_r)
            )
        )
    ].copy()

    return {
        "params": p,
        "params_meta": ld["meta"],
        "assumed_start": assumed_start,
        "year_start": year0,
        "year_end": year1,
        "panel": panel,
        "headline": headline,
        "by_group": by_group,
        "by_project": by_project_central,
        "by_year": by_year_central,
        "burke_grid": burke_grid,
        "eccc_grid": eccc_grid,
        "physical_scenarios": physical_scenarios,
        "sc_table": sc_table,
        "horizon_table": horizon_table,
        "gva": v_proposed,
        "gva_proposed_as_published": v_published,
        "gva_proposed_30yr": v_proposed_30,
        "gva_proposed_30yr_as_published": v_published_30,
        "gva_committed": v_committed,
        "cboc_dollar_year": cboc_dollar_year,
        "proposed_export_mtpa": proposed_export_mtpa,
        "committed_export_mtpa": committed_export_mtpa,
        "canada_share": canada_share,
        "uk_fd_share": uk_fd_share,
        "canada_row": can_row,
        "fig4": fig4,
        "tonnes_proposed_mtco2e": tonnes_proposed,
        "tonnes_proposed_mtco2": tonnes_co2_proposed,
        "tonnes_proposed_mtch4": tonnes_ch4_proposed,
        "ch4_co2_ratio_2020": ch4_co2_ratio_2020,
        "central_r": central_r,
        "central_g": central_g,
        "central_horizon": central_horizon,
        "eccc_r": eccc_r,
        "burke_usd": burke_usd,
        "burke_cad": burke_cad,
        "by_group_all": by_group,
        "h_central": h_central,
    }


def write_ld_figure(h_row, path: Path) -> None:
    """Bar: central horizon global L&D by calc_group, trillion 2025 CAD."""
    path.parent.mkdir(parents=True, exist_ok=True)
    labels = ["Operating", "Under construction", "Proposed"]
    vals = [
        float(h_row["operating_cad_billion"]) / 1000.0,
        float(h_row["under_construction_cad_billion"]) / 1000.0,
        float(h_row["proposed_cad_billion"]) / 1000.0,
    ]
    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    colours = ["#0072B2", "#56B4E9", "#D55E00"]
    ax.bar(range(3), vals, 0.55, color=colours)
    ax.set_xticks(range(3), labels)
    ax.set_ylabel("Global loss and damage (trillion 2025 CAD)")
    ax.set_title("Climate loss and damage from Canadian LNG lifecycle emissions")
    ymax = max(vals) if vals else 1
    ax.set_ylim(0, ymax * 1.18)
    for i, v in enumerate(vals):
        ax.text(i, v + ymax * 0.03, f"{v:.1f}", ha="center", fontsize=10)
    fig.text(
        0.5, 0.02,
        "Burke et al. 2026 SC-CO2, 2% discount, g=0, through-2300 (Figure 2e). "
        "CO2/CH4 split (ECCC FAQ 4.2). Global damages, not Canada-only. "
        f"Canada Burke-channel share {100*float(h_row['canada_share_fd']):.2f}%.",
        ha="center", fontsize=8, color="#444",
    )
    fig.subplots_adjust(bottom=0.16, top=0.9)
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def _money_cad(billion: float) -> str:
    if abs(billion) >= 1000:
        return f"${billion / 1000:,.1f} trillion"
    return f"${billion:,.0f} billion"


def format_ld_markdown(ld: dict) -> list[str]:
    h = ld["h_central"]
    eccc = ld["headline"].set_index("case").loc["eccc_central_npv_2025"]
    share_pct = 100 * ld["canada_share"]
    lines = []
    lines.append("## 11. Climate loss and damage (global)")
    lines.append("")
    lines.append(
        "Monetised economic damages from the modelled lifecycle emissions. "
        "Central price is Burke et al. (2026) Figure 2e **through 2300**, "
        "2% fixed, g = 0, in 2025 CAD. Through-2100 is shown for comparability "
        "with Hatton (2026). Damages are **global**. They are not a legal bill. "
        "Upstream is split into CO2 mass and CH4 mass; methane is priced at "
        "Burke SC-CO2 times the ECCC SC-CH4/SC-CO2 ratio (FAQ 4.2). Pipeline "
        "and shipping methane remain inside the CO2e total as CO2. Construction, "
        "sea-level rise, extremes, and mortality outside GDP are omitted."
    )
    lines.append("")
    ch4_mt = ld["tonnes_proposed_mtch4"]
    co2_mt = ld["tonnes_proposed_mtco2"]
    co2e_mt = ld["tonnes_proposed_mtco2e"]
    gwp_bn = float(h["proposed_gwp_cad_billion"])
    split_bn = float(h["proposed_cad_billion"])
    lines.append(
        f"Proposed remaining gases: {co2e_mt:,.0f} MtCO2e = {co2_mt:,.0f} MtCO2 + "
        f"{ch4_mt:,.1f} MtCH4. Split damages "
        f"{_money_cad(split_bn)} vs GWP100×SC-CO2 {_money_cad(gwp_bn)} "
        f"(ECCC 2020 2% SC-CH4/SC-CO2 = {ld['ch4_co2_ratio_2020']:.2f}, "
        f"GWP100 = 29.8)."
    )
    lines.append("")
    lines.append(
        f"Canada's Burke-channel **victim** share of a 1990 1 Gt pulse, future "
        f"window: **{share_pct:.2f}%** (UK historical share in the same file is "
        f"1.61%, matching Hatton). That share is applied to later pulses; the "
        f"$3.13/t Canada FD rate is not. Probability of net Canada damage on "
        f"this channel rises from 0.33 (1990–2020) to 0.41 (2021–2100)."
    )
    lines.append("")
    f4 = ld["fig4"]
    lines.append(
        f"Burke Figure 4 sankey (`damages_and_benefits_k90.rds`) is emitter/"
        f"recipient flows for 1990–2020 **all** emissions, not LNG. Canada as "
        f"emitter caused **${f4['canada_owing_usd']/1e12:.2f} trillion** "
        f"({100*f4['canada_emitter_share']:.2f}% of global owing; USA "
        f"${f4['usa_owing_usd']/1e12:.2f}T validates against the paper's "
        f"$10.2T). Canada is **not** a plotted recipient, so CAN-on-CAN "
        f"cannot be read from this file. Victim share stays 0.17% from the "
        f"1 Gt pulse."
    )
    lines.append("")
    pub = ld["gva_proposed_as_published"] / 1e9
    lines.append(
        f"Canada denominator: Conference Board *A Rising Tide* Table 1, "
        f"Canada GDP at market prices **C$11.153bn/yr (2020 CAD)** at 56 mtpa, "
        f"scaled linearly on proposed export nameplate "
        f"({ld['proposed_export_mtpa']:.1f} mtpa) over 40 years (Appendix A "
        f"operating life). Whole-chain including upstream (76% of the GDP). "
        f"Industry-commissioned. Inflated to 2025 CAD with FRED NGDPDIXCAA. "
        f"Uninflated 2020 CAD value is {_money_cad(pub)}."
    )
    lines.append("")
    lines.append(
        f"- **Proposed global L&D (through 2300, 2%):** "
        f"**{_money_cad(h['proposed_cad_billion'])}**"
    )
    lines.append(
        f"- **Canadian value (proposed, CBoC scaled, 40 yr, 2025 CAD):** "
        f"**{_money_cad(h['canada_value_proposed_cad_billion'])}**"
    )
    lines.append(
        f"- **Externality ratio (global damages / Canadian value):** "
        f"**{h['externality_ratio_proposed']:.0f}x** "
        f"(Hatton UK range was 5.9x–16.8x)"
    )
    lines.append(
        f"- **Canada bears {share_pct:.2f}% of the damage it causes, so it "
        f"externalises {100*(1-ld['canada_share']):.1f}%** "
        f"(Burke-channel; {_money_cad(h['canada_borne_proposed_cad_billion'])} borne)"
    )
    lines.append(
        f"- **National test, Burke channel only (not the headline):** "
        f"Canadian value is {h['national_value_over_borne']:.1f}x the damages "
        f"Canada itself bears. Omitted channels would need a "
        f"{h['national_value_over_borne']:.1f}x uplift to flip the sign. "
        "Reported as indeterminate."
    )
    lines.append(
        f"- **All in-scope, same price:** {_money_cad(h['total_cad_billion'])}  |  "
        f"operating {_money_cad(h['operating_cad_billion'])}  |  "
        f"under construction {_money_cad(h['under_construction_cad_billion'])}"
    )
    lines.append(
        f"- **ECCC SC-CO2 + SC-CH4 (2% Ramsey, NPV to 2025), all groups:** "
        f"{_money_cad(eccc['total_cad_billion'])} "
        f"(proposed {_money_cad(eccc['proposed_cad_billion'])})"
    )
    v30 = ld["gva_proposed_30yr"] / 1e9
    ratio30 = h["proposed_cad_billion"] / v30 if v30 else None
    lines.append(
        f"- **30-year denominator sensitivity:** "
        f"{_money_cad(v30)} Canadian value, ratio "
        f"**{ratio30:.0f}x** (research sketch used 30 years; central uses 40)."
    )
    v_com = ld["gva_committed"] / 1e9
    d_com = h["operating_cad_billion"] + h["under_construction_cad_billion"]
    ratio_com = d_com / v_com if v_com else None
    lines.append(
        f"- **Operating + under construction only:** "
        f"{_money_cad(d_com)} global L&D / {_money_cad(v_com)} value = "
        f"**{ratio_com:.0f}x** ({ld['committed_export_mtpa']:.1f} mtpa export)."
    )
    lines.append("")
    lines.append(
        "Burke horizon rows (g = 0, proposed slate). Global L&D and value "
        "in trillion 2025 CAD; Canada-borne in billion 2025 CAD."
    )
    lines.append("")
    lines.append(
        "| horizon | discounting | SC USD2020/t | global L&D (tn) | "
        "value (tn) | ratio | Canada-borne (bn) |"
    )
    lines.append("|---|---|---|---|---|---|---|")
    for _, r in ld["horizon_table"].iterrows():
        mark = "**" if r["is_central"] else ""
        lines.append(
            f"| {mark}{r['horizon']}{mark} | {r['discounting']} | "
            f"{r['sc_co2_usd2020_per_t']:,.0f} | "
            f"{mark}{r['proposed_cad_billion']/1000:,.1f}{mark} | "
            f"{r['canada_value_proposed_cad_billion']/1000:,.2f} | "
            f"{mark}{r['externality_ratio_proposed']:.0f}x{mark} | "
            f"{r['canada_borne_proposed_cad_billion']:.1f} |"
        )
    lines.append("")
    lines.append(
        "Through-2100 year-by-year path, g bracket (trillion 2025 CAD, all / proposed). "
        "Central g = 0; +2% is Hatton's headline and is not ours."
    )
    lines.append("")
    lines.append("| discount | g=−2% | g=0% | g=+2% |")
    lines.append("|---|---|---|---|")
    grid = ld["burke_grid"]
    for rate in BURKE_RATES:
        cells = []
        for g in GROWTH_RATES:
            r = grid.loc[
                (grid["discount_rate_pct"] == rate) & (grid["growth_rate"] == g)
            ].iloc[0]
            mark = "**" if r["is_central"] else ""
            cells.append(
                f"{mark}{r['total_cad_billion']/1000:,.1f} / "
                f"{r['proposed_cad_billion']/1000:,.1f}{mark}"
            )
        lines.append(f"| {rate:g}% | {cells[0]} | {cells[1]} | {cells[2]} |")
    lines.append("")
    lines.append("Figure: `Outputs/figures/fig09_loss_damage_by_group.png`.")
    lines.append("")
    return lines
