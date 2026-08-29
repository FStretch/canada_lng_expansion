"""Global climate loss and damage from modelled LNG emissions.

Physical tonnes come from the existing lifecycle model (full chain, GWP100
CO2e). This module does not change those calculations.

The published central case is named in Inputs/loss_damage/parameters.csv
(`central_price_family`, `central_aggregation`, `eccc_central_discount_rate_pct`).
Default: ECCC official SC-CO2 at 2%, applied per calendar year of emissions
to the full GWP100 CO2e total (year t tonnes × year t SC, summed in 2025 CAD).
This overstates methane (CH4-derived CO2e is charged at SC-CO2 rather than
SC-CH4); that bound is reported. There is no native per-gas split.

Burke et al. (2026) is an upper-bracket sensitivity across discount rates
and Figure 2e horizons. Burke default is g = 0; Hatton's +2% is not used
as a Burke default. The SC already discounts the damage stream.

    SC_t = SC_2020_CAD2025 * (1 + g) ** (t - 2020)
    L&D  = sum_t SC_t * E_t

ECCC path: official SC-CO2 schedule (C$2021) inflated to C$2025, applied to
the full GWP100 CO2e total. This overstates the methane contribution: CH4-
derived CO2e is charged at SC-CO2 rather than at SC-CH4. That bound is
reported; there is no native per-gas split.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.inputs import DEFAULT_SCENARIO, INTENSITY_SCENARIOS, MissingInputError, get_param
from src.model import GROUPS, _stage_intensity
from src.scope import filter_panel
from src.trajectories import (
    _chain_intensity_split,
    build_emissions_panel,
    calendar_bounds,
    project_annual_mt,
)

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
        "central_price_family",
        "central_aggregation",
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


def methane_co2e_fraction_from_upstream(row, scenario: str, inputs: dict) -> float:
    """CH4-derived share of this asset's chain CO2e.

    Thin wrapper over the physics split (`src.trajectories._chain_intensity_split`,
    built on `src.model.stage_ch4_co2e_intensity`), kept so the old call sites
    read unchanged. The split now covers upstream **and** shipping methane
    slip; pipeline fugitives are still not split.
    """
    chain = row["chain"]
    if chain not in inputs["chains"]:
        return 0.0
    total, _co2, ch4 = _chain_intensity_split(
        row, scenario, inputs, canada_only=False
    )
    if total <= 0:
        return 0.0
    return ch4 / total


def usd2020_to_cad2025(usd_2020: float, params: dict) -> float:
    us0 = float(_required(params, "us_gdp_deflator_2020"))
    us1 = float(_required(params, "us_gdp_deflator_2025"))
    fx = float(_required(params, "usd_cad_2025"))
    return usd_2020 * (us1 / us0) * fx


def cad2021_to_cad2025(cad_2021: float, params: dict) -> float:
    """Inflate official ECCC CAD 2021 prices to CAD 2025. Applied once."""
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
    assumed_start: int | None = None,
) -> dict:
    ld = load_ld_params(inputs_dir)
    p = ld["params"]
    burke_usd = load_burke_sc_2020(inputs_dir, p)
    horizons = load_horizons(inputs_dir, p)
    canada_share, uk_fd_share, can_row = load_canada_fd_share(inputs_dir, p)
    eccc = load_eccc_schedule(inputs_dir, p)
    eccc_ch4 = load_eccc_ch4(inputs_dir, p)
    fig4 = load_fig4_canada(inputs_dir, p)
    if assumed_start is None:
        assumed_start = int(
            get_param(inputs["params"], "assumed_first_export_year_if_missing")
        )
    year0, year1 = calendar_bounds(inputs, assumed_start)
    horizon = int(float(_required(p, "damages_horizon_year")))
    analysis = int(float(_required(p, "analysis_year")))
    central_price_family = str(_required(p, "central_price_family")).strip().lower()
    central_aggregation = str(_required(p, "central_aggregation")).strip().lower()
    if central_price_family != "eccc":
        raise MissingInputError(
            f"central_price_family={central_price_family!r}; paper central is ECCC. "
            "Burke is an upper-bracket sensitivity, not a selectable central."
        )
    if central_aggregation != "calendar_year":
        raise MissingInputError(
            f"central_aggregation={central_aggregation!r}; "
            "paper central applies ECCC SC per calendar year."
        )
    burke_r = float(_required(p, "central_discount_rate_pct"))
    burke_g = float(_required(p, "central_growth_rate"))
    if burke_g != 0.0:
        raise MissingInputError(
            f"Burke default growth_rate is 0; got {burke_g}. Do not use Hatton +2%."
        )
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

    gwp = float(get_param(inputs["params"], "gwp100_ch4"))
    inv_up = float(inputs["upstream_by_scenario"]["inventory_as_reported"])
    ch4_share_param = float(get_param(inputs["params"], "upstream_ch4_share"))
    inventory_co2_upstream = inv_up * (1.0 - ch4_share_param)
    frac_cache: dict[tuple, float] = {}

    def _methane_frac(asset_row, scen: str) -> float:
        key = (asset_row["project_id"], scen)
        if key not in frac_cache:
            frac_cache[key] = methane_co2e_fraction_from_upstream(
                asset_row, scen, inputs
            )
        return frac_cache[key]

    if panel is None:
        panel = build_emissions_panel(
            inputs,
            scenarios=LD_EMISSION_SCENARIOS,
            assumed_start=assumed_start,
        )
        panel = filter_panel(panel, inputs)
    else:
        panel = panel.loc[panel["scenario"].isin(LD_EMISSION_SCENARIOS)].copy()
        if not len(panel):
            raise MissingInputError("Emissions panel has no L&D scenarios.")
    assets_by_id = {r["project_id"]: r for _, r in inputs["assets"].iterrows()}

    year_rows = []
    methane_overstatement_cad = 0.0
    methane_co2e_tonnes_central = 0.0
    co2e_tonnes_central = 0.0
    for _, prec in panel.iterrows():
        row = assets_by_id[prec["project_id"]]
        scenario = prec["scenario"]
        year = int(prec["year"])
        mt = float(prec["emissions_mtco2e"])
        tonnes_co2e = mt * 1e6
        methane_frac = _methane_frac(row, scenario)
        # Published damages price the full GWP100 CO2e total at SC-CO2.
        # That overstates methane: CH4-derived CO2e is charged at SC-CO2
        # rather than at SC-CH4. Do not treat this as conservative.
        for rate in BURKE_RATES:
            for g in GROWTH_RATES:
                sc = burke_sc_cad2025(year, rate, g, burke_cad[rate], p)
                hatton = sc * tonnes_co2e
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
                    "discount_rate_pct": rate,
                    "growth_rate": g,
                    "sc_cad2021_per_t": None,
                    "sc_cad2025_per_t": sc,
                    "hatton_sum_cad": hatton,
                    "npv_analysis_year_cad": npv,
                })
        for rate in ECCC_RATES:
            try:
                sc21 = float(eccc_idx.loc[(rate, year)])
            except KeyError as exc:
                raise MissingInputError(
                    f"ECCC schedule has no SC-CO2 for rate {rate}% year {year}."
                ) from exc
            sc = cad2021_to_cad2025(sc21, p)
            undisc = sc * tonnes_co2e
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
                "discount_rate_pct": rate,
                "growth_rate": None,
                "sc_cad2021_per_t": sc21,
                "sc_cad2025_per_t": sc,
                "hatton_sum_cad": undisc,
                "npv_analysis_year_cad": npv,
            })
            if scenario == DEFAULT_SCENARIO and rate == eccc_r:
                try:
                    ratio_yr = float(eccc_ch4_idx.loc[(rate, year)]) / float(
                        eccc_idx.loc[(rate, year)]
                    )
                except KeyError as exc:
                    raise MissingInputError(
                        f"ECCC CH4/CO2 ratio missing for {rate}% year {year}."
                    ) from exc
                methane_t = tonnes_co2e * methane_frac
                # Priced as CO2: methane_t × SC-CO2.
                # Priced as CH4: (methane_t / GWP100) × SC-CH4
                #              = methane_t × SC-CO2 × (ratio / GWP100).
                methane_overstatement_cad += (
                    methane_t * sc * (1.0 - ratio_yr / gwp)
                )
                methane_co2e_tonnes_central += methane_t
                co2e_tonnes_central += tonnes_co2e


    by_year = pd.DataFrame(year_rows)
    if not len(by_year):
        raise MissingInputError("Loss-and-damage produced no emission years.")

    def _aggregate(df: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
        em = (
            df.drop_duplicates(keys + ["project_id", "year"])
            .groupby(keys, dropna=False, sort=False)[
                ["emissions_mtco2e"]
            ]
            .sum()
        )
        money = df.groupby(keys, dropna=False, sort=False).agg(
            hatton_sum_cad=("hatton_sum_cad", "sum"),
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

    burke_default = _slice("burke", DEFAULT_SCENARIO, burke_r, burke_g)
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
            & (by_year["discount_rate_pct"] == burke_r)
            & (by_year["growth_rate"] == burke_g)
        ]
        .drop_duplicates(["project_id", "year"])
    )
    tonnes_by_group = phys_years.groupby("calc_group")["emissions_mtco2e"].sum()
    tonnes_all = float(tonnes_by_group.sum())
    tonnes_proposed = float(tonnes_by_group.get("proposed", 0.0))

    horizon_rows = []
    for _, hr in horizons.iterrows():
        sc_cad = usd2020_to_cad2025(float(hr["sc_co2_usd2020_per_t"]), p)
        total = tonnes_all * 1e6 * sc_cad
        proposed = tonnes_proposed * 1e6 * sc_cad
        operating = float(tonnes_by_group.get("operating", 0.0)) * 1e6 * sc_cad
        uc = float(tonnes_by_group.get("under_construction", 0.0)) * 1e6 * sc_cad
        canada_borne_prop = proposed * canada_share
        ratio = None if v_proposed == 0 else proposed / v_proposed
        nat = None if canada_borne_prop == 0 else v_proposed / canada_borne_prop
        horizon_rows.append({
            "horizon": hr["horizon"],
            "discounting": hr["discounting"],
            "sc_co2_usd2020_per_t": float(hr["sc_co2_usd2020_per_t"]),
            "sc_co2_cad2025_per_t": sc_cad,
            "is_burke_default": (
                str(hr["horizon"]) == central_horizon
                and str(hr["discounting"]) == central_h_disc
            ),
            "is_central": False,
            "total_cad_billion": total / 1e9,
            "proposed_cad_billion": proposed / 1e9,
            "proposed_gwp_cad_billion": proposed / 1e9,
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
    h_burke = horizon_table.loc[horizon_table["is_burke_default"]]
    if len(h_burke) != 1:
        raise MissingInputError(
            f"Burke default horizon={central_horizon!r} discounting={central_h_disc!r} "
            f"matched {len(h_burke)} horizon rows."
        )
    h_burke = h_burke.iloc[0]

    headline_specs = [
        ("published_central", eccc_central, "eccc", "hatton_sum"),
        ("eccc_central_npv_2025", eccc_central, "eccc", "npv_analysis_year"),
        ("burke_default_hatton", burke_default, "burke", "hatton_sum"),
        ("burke_default_npv_2025", burke_default, "burke", "npv_analysis_year"),
    ]
    for rate in ECCC_RATES:
        if rate == eccc_r:
            continue
        headline_specs.append(
            (
                f"eccc_{rate:g}pct_calendar",
                _slice("eccc", DEFAULT_SCENARIO, rate, None),
                "eccc",
                "hatton_sum",
            )
        )
    headline_rows = []
    for label, df, family, method in headline_specs:
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
        agg_label = (
            "calendar_year" if family == "eccc" and method == "hatton_sum" else method
        )
        headline_rows.append({
            "case": label,
            "price_family": family,
            "aggregation": agg_label,
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
    published = headline.loc[headline["case"] == "published_central"].iloc[0]
    methane_share = (
        methane_co2e_tonnes_central / co2e_tonnes_central
        if co2e_tonnes_central else 0.0
    )
    published_cad = float(published["total_cad"])
    methane_overstatement_pct = (
        methane_overstatement_cad / published_cad if published_cad else 0.0
    )

    def _eccc_ratio(year: int) -> float:
        return float(eccc_ch4_idx.loc[(eccc_r, year)]) / float(
            eccc_idx.loc[(eccc_r, year)]
        )

    ch4_co2_ratio_2025 = _eccc_ratio(analysis)
    ch4_co2_ratio_2080 = _eccc_ratio(int(eccc["year"].max()))
    central_up = float(inputs["upstream_by_scenario"][DEFAULT_SCENARIO])
    methane_co2e_per_t_lng = max(central_up - inventory_co2_upstream, 0.0)

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
                "is_burke_default": rate == burke_r and g == burke_g,
                "is_central": False,
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
            "calendar_year_total_cad_billion": float(sl["hatton_sum_cad"].sum()) / 1e9,
            "calendar_year_proposed_cad_billion": float(
                sl.loc[sl["calc_group"] == "proposed", "hatton_sum_cad"].sum()
            ) / 1e9,
            "npv_2025_total_cad_billion": float(sl["npv_analysis_year_cad"].sum()) / 1e9,
            "npv_2025_proposed_cad_billion": float(
                sl.loc[sl["calc_group"] == "proposed", "npv_analysis_year_cad"].sum()
            ) / 1e9,
            "is_central": rate == eccc_r,
            "is_sensitivity_range": rate != eccc_r,
        })
    eccc_grid = pd.DataFrame(eccc_sens)

    phys = []
    for scenario in LD_EMISSION_SCENARIOS:
        sl = by_group.loc[
            (by_group["price_family"] == "eccc")
            & (by_group["scenario"] == scenario)
            & (by_group["discount_rate_pct"] == eccc_r)
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
            "sc_analysis_year_cad2025_g0": burke_sc_cad2025(
                analysis, rate, burke_g, cad, p
            ) if rate == burke_r else None,
        })
    sc_table = pd.DataFrame(sc_audit)

    # Keep by_year manageable: central Burke + central ECCC, default scenario only
    by_year_central = by_year.loc[
        (by_year["scenario"] == DEFAULT_SCENARIO)
        & (
            (
                (by_year["price_family"] == "burke")
                & (by_year["discount_rate_pct"] == burke_r)
                & (by_year["growth_rate"] == burke_g)
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
                & (by_project["discount_rate_pct"] == burke_r)
                & (by_project["growth_rate"] == burke_g)
            )
            | (
                (by_project["price_family"] == "eccc")
                & (by_project["discount_rate_pct"] == eccc_r)
            )
        )
    ].copy()

    cad2021_to_2025_factor = float(_required(p, "canada_gdp_deflator_2025")) / float(
        _required(p, "canada_gdp_deflator_2021")
    )
    eccc_yr = by_year_central.loc[by_year_central["price_family"] == "eccc"]
    price_by_year = (
        eccc_yr.groupby("year", sort=True)
        .agg(
            emissions_mtco2e=("emissions_mtco2e", "sum"),
            sc_cad2021_per_t=("sc_cad2021_per_t", "first"),
            sc_cad2025_per_t=("sc_cad2025_per_t", "first"),
            damage_cad=("hatton_sum_cad", "sum"),
        )
        .reset_index()
    )
    price_by_year["damage_cad_billion"] = price_by_year["damage_cad"] / 1e9
    tonnes = float(price_by_year["emissions_mtco2e"].sum()) * 1e6
    damages = float(price_by_year["damage_cad"].sum())
    weighted_sc_cad2025 = damages / tonnes if tonnes else 0.0
    simple_sc_cad2025 = float(price_by_year["sc_cad2025_per_t"].mean())
    weighted_sc_cad2021 = (
        float(
            (
                price_by_year["emissions_mtco2e"] * price_by_year["sc_cad2021_per_t"]
            ).sum()
        )
        / float(price_by_year["emissions_mtco2e"].sum())
        if tonnes
        else 0.0
    )
    simple_sc_cad2021 = float(price_by_year["sc_cad2021_per_t"].mean())

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
        "methane_share_of_co2e": methane_share,
        "methane_co2e_mt": methane_co2e_tonnes_central / 1e6,
        "methane_co2e_per_t_lng": methane_co2e_per_t_lng,
        "inventory_co2_upstream": inventory_co2_upstream,
        "methane_overstatement_cad": methane_overstatement_cad,
        "methane_overstatement_pct": methane_overstatement_pct,
        "ch4_co2_ratio_2020": ch4_co2_ratio_2020,
        "ch4_co2_ratio_2025": ch4_co2_ratio_2025,
        "ch4_co2_ratio_2080": ch4_co2_ratio_2080,
        "gwp100_ch4": gwp,
        "central_price_family": central_price_family,
        "central_aggregation": central_aggregation,
        "central_r": eccc_r,
        "burke_r": burke_r,
        "central_g": burke_g,
        "central_horizon": central_horizon,
        "eccc_r": eccc_r,
        "burke_usd": burke_usd,
        "burke_cad": burke_cad,
        "by_group_all": by_group,
        "published": published,
        "h_burke": h_burke,
        "price_by_year": price_by_year,
        "cad2021_to_2025_factor": cad2021_to_2025_factor,
        "weighted_sc_cad2025": weighted_sc_cad2025,
        "simple_sc_cad2025": simple_sc_cad2025,
        "weighted_sc_cad2021": weighted_sc_cad2021,
        "simple_sc_cad2021": simple_sc_cad2021,
    }


def write_ld_figure(h_row, path: Path) -> None:
    """Bar: published central (ECCC 2% calendar year) L&D by calc_group."""
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
        "Central case: ECCC SC-CO2 at 2%, applied per calendar year of emissions "
        "(2025 CAD). ECCC 1.5% and 2.5% are the sensitivity range. "
        "Burke is an upper-bracket sensitivity, not shown here. Global damages.",
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
    published = ld["published"]
    h = ld["headline"].set_index("case")
    eccc_npv = h.loc["eccc_central_npv_2025"]
    egrid = ld["eccc_grid"].set_index("discount_rate_pct")
    eccc_lo = egrid.loc[2.5]
    eccc_hi = egrid.loc[1.5]
    burke = ld["h_burke"]
    share_pct = 100 * ld["canada_share"]
    lines = []
    lines.append("## 11. Climate loss and damage (global)")
    lines.append("")
    lines.append(
        "Monetised economic damages from the modelled lifecycle emissions. "
        "The **central case** is ECCC official SC-CO2 at the **2%** discount "
        "rate, applied per calendar year of emissions, in 2025 CAD "
        f"(named parameters `central_price_family={ld['central_price_family']}`, "
        f"`central_aggregation={ld['central_aggregation']}`). "
        "ECCC 1.5% and 2.5% are the central case's sensitivity range. "
        "Burke et al. (2026) is an **upper-bracket sensitivity** across discount "
        "rates and Figure 2e horizons (default g = 0; Hatton +2% is not used). "
        "Damages are **global**. They are not a legal bill. "
        "ECCC SC-CO2 is applied to the full GWP100 CO2e total. That "
        "**overstates** the methane contribution (CH4-derived CO2e is charged "
        "at SC-CO2 rather than at SC-CH4) and is not conservative in that "
        "direction. Construction, sea-level rise, extremes, and mortality "
        "outside GDP are omitted."
    )
    lines.append("")
    share_ch4 = 100 * ld["methane_share_of_co2e"]
    over_pct = 100 * ld["methane_overstatement_pct"]
    total_mt = (
        ld["methane_co2e_mt"] / ld["methane_share_of_co2e"]
        if ld["methane_share_of_co2e"] else 0.0
    )
    up_central = ld["inventory_co2_upstream"] + ld["methane_co2e_per_t_lng"]
    lines.append(
        f"Methane share of the CO2e total is **{share_ch4:.1f}%** "
        f"({ld['methane_co2e_mt']:,.0f} of {total_mt:,.0f} MtCO2e). "
        f"That is the excess of the central upstream factor ({up_central:.2f}) "
        f"over inventory CO2 ({ld['inventory_co2_upstream']:.3f}), i.e. "
        f"{ld['methane_co2e_per_t_lng']:.3f} tCO2e per t LNG, as a share of "
        f"the chain total. Pipeline and shipping methane stay inside CO2e as "
        f"CO2 and are not in this share. GWP100 = {ld['gwp100_ch4']:.1f}; "
        f"ECCC SC-CH4/SC-CO2 is {ld['ch4_co2_ratio_2025']:.1f} in 2025 and "
        f"{ld['ch4_co2_ratio_2080']:.1f} by 2080. Pricing that methane CO2e "
        f"as CO2 therefore charges it at roughly "
        f"{ld['gwp100_ch4']/ld['ch4_co2_ratio_2025']:.1f}× the ECCC CH4 price "
        f"in 2025. The resulting overstatement is **{over_pct:.1f}%** of the "
        f"central damage bill. This treatment overstates methane and is not "
        f"conservative in that direction."
    )
    lines.append("")
    py = ld["price_by_year"]
    e_after = float(py.loc[py["year"] > 2050, "emissions_mtco2e"].sum())
    e_all = float(py["emissions_mtco2e"].sum())
    lines.append(
        f"Implied average price is **${ld['weighted_sc_cad2025']:,.0f}/t** "
        f"CAD 2025 (total damages / lifetime tonnes). That is the "
        f"emissions-weighted mean of the ECCC 2% schedule after a **single** "
        f"CAD 2021→2025 inflation of {ld['cad2021_to_2025_factor']:.4f} "
        f"(deflators {ld['params']['canada_gdp_deflator_2021']} / "
        f"{ld['params']['canada_gdp_deflator_2025']}). "
        f"The unweighted mean of the same series over panel years is "
        f"${ld['simple_sc_cad2025']:,.0f}/t. In CAD 2021 the weighted mean is "
        f"${ld['weighted_sc_cad2021']:,.0f}/t (2025 official schedule value "
        f"is $271/t). Prices are looked up on the **calendar year of emission**. "
        f"{100*e_after/e_all:.0f}% of lifetime tonnes are after 2050, so the "
        f"weighted mean sits above the 2037 peak-year price. "
        f"Year table: `Outputs/figure_data/ld_price_by_year.csv`."
    )
    lines.append("")
    lines.append(
        f"- **Central (ECCC 2%, calendar year), all in-scope:** "
        f"**{_money_cad(published['total_cad_billion'])}** "
        f"(operating {_money_cad(published['operating_cad_billion'])}  |  "
        f"under construction {_money_cad(published['under_construction_cad_billion'])}  |  "
        f"proposed {_money_cad(published['proposed_cad_billion'])})"
    )
    lines.append(
        f"- **Central sensitivity (ECCC 1.5%–2.5%, calendar year):** "
        f"{_money_cad(eccc_lo['calendar_year_total_cad_billion'])} "
        f"to {_money_cad(eccc_hi['calendar_year_total_cad_billion'])}"
    )
    lines.append(
        f"- **ECCC 2% NPV to 2025 (sensitivity, not central):** "
        f"{_money_cad(eccc_npv['total_cad_billion'])} "
        f"(proposed {_money_cad(eccc_npv['proposed_cad_billion'])})"
    )
    bgrid = ld["burke_grid"]
    burke_g0 = bgrid.loc[bgrid["growth_rate"] == 0.0]
    burke_min = float(burke_g0["total_cad_billion"].min())
    burke_max = float(burke_g0["total_cad_billion"].max())
    lines.append(
        f"- **Burke upper bracket (g = 0, year-by-year 2100 path, 1.5%–5%):** "
        f"{_money_cad(burke_min)} to {_money_cad(burke_max)}; "
        f"Figure 2e through-2300 at 2% fixed: "
        f"**{_money_cad(burke['total_cad_billion'])}** "
        f"(proposed {_money_cad(burke['proposed_cad_billion'])})"
    )
    v_prop = float(burke["canada_value_proposed_cad_billion"])
    lines.append(
        f"- **Canadian value (proposed, CBoC scaled, 40 yr, 2025 CAD):** "
        f"**{_money_cad(v_prop)}**"
    )
    eccc_ratio = (
        published["proposed_cad_billion"] / v_prop if v_prop else None
    )
    lines.append(
        f"- **Externality ratio, ECCC central (proposed):** "
        f"**{eccc_ratio:.1f}x** global damages / Canadian value "
        f"(Hatton UK range was 5.9x–16.8x; Burke through-2300 is "
        f"{burke['externality_ratio_proposed']:.0f}x)"
    )
    lines.append(
        f"- **Canada Burke-channel victim share (sensitivity, not central):** "
        f"**{share_pct:.2f}%** of a 1990 1 Gt pulse, so it externalises "
        f"{100*(1-ld['canada_share']):.1f}% "
        f"({_money_cad(burke['canada_borne_proposed_cad_billion'])} borne at "
        f"the through-2300 2% price)"
    )
    lines.append(
        f"- **National test, Burke channel only (not the headline):** "
        f"Canadian value is {burke['national_value_over_borne']:.1f}x the damages "
        f"Canada itself bears. Reported as indeterminate."
    )
    v30 = ld["gva_proposed_30yr"] / 1e9
    ratio30 = published["proposed_cad_billion"] / v30 if v30 else None
    lines.append(
        f"- **30-year denominator sensitivity (ECCC central, proposed):** "
        f"{_money_cad(v30)} Canadian value, ratio "
        f"**{ratio30:.0f}x** (research sketch used 30 years; central uses 40)."
    )
    v_com = ld["gva_committed"] / 1e9
    d_com = (
        published["operating_cad_billion"]
        + published["under_construction_cad_billion"]
    )
    ratio_com = d_com / v_com if v_com else None
    lines.append(
        f"- **Operating + under construction only (ECCC central):** "
        f"{_money_cad(d_com)} global L&D / {_money_cad(v_com)} value = "
        f"**{ratio_com:.0f}x** ({ld['committed_export_mtpa']:.1f} mtpa export)."
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
        "Burke horizon rows (g = 0, proposed slate; upper bracket, not central). "
        "Global L&D and value in trillion 2025 CAD; Canada-borne in billion 2025 CAD. "
        "Bold is the Burke default horizon, not the paper central."
    )
    lines.append("")
    lines.append(
        "| horizon | discounting | SC USD2020/t | global L&D (tn) | "
        "value (tn) | ratio | Canada-borne (bn) |"
    )
    lines.append("|---|---|---|---|---|---|---|")
    for _, r in ld["horizon_table"].iterrows():
        mark = "**" if r["is_burke_default"] else ""
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
        "Burke through-2100 year-by-year path, g bracket "
        "(trillion 2025 CAD, all / proposed). Burke default g = 0; "
        "+2% is Hatton's headline and is not used."
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
            mark = "**" if r["is_burke_default"] else ""
            cells.append(
                f"{mark}{r['total_cad_billion']/1000:,.1f} / "
                f"{r['proposed_cad_billion']/1000:,.1f}{mark}"
            )
        lines.append(f"| {rate:g}% | {cells[0]} | {cells[1]} | {cells[2]} |")
    lines.append("")
    lines.append("Figure: `Outputs/figures/fig09_loss_damage_by_group.png`.")
    lines.append("")
    return lines
