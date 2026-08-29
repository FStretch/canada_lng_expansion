"""Lifecycle calculation, territorial tagging, and aggregation."""

from __future__ import annotations

from datetime import datetime

import numpy as np
import pandas as pd

from src.inputs import (
    ALL_STAGES,
    CALC_GROUPS,
    DEFAULT_SCENARIO,
    DRIVE_PARAM,
    REQUIRED_PARAMS,
    SCOPE_1_2_STAGES,
    SCOPE_3_STAGES,
    TERRITORIES,
    VALID_CHAINS,
    MissingInputError,
    get_param,
)
from src.scope import headline_scope_sets, scope_mask

GROUPS = CALC_GROUPS
CHAINS = ("export", "bunkering", "domestic", "import")


def _licence_end_year(row) -> int | None:
    """Inclusive last authorised calendar year, or None if the register field is blank."""
    val = row.get("authorised_export_end_year")
    if val is None or (isinstance(val, float) and pd.isna(val)) or pd.isna(val):
        return None
    return int(val)


def _lifespan(row, params) -> tuple[int, str]:
    if pd.notna(row["authorised_export_term_years"]):
        life = int(row["authorised_export_term_years"])
        src = "Asset Register:authorised_export_term_years"
    elif pd.notna(row["project_life_years"]):
        life = int(row["project_life_years"])
        src = "Asset Register:project_life_years"
    else:
        life = int(get_param(params, "lifecycle_years_default"))
        src = "Parameters:lifecycle_years_default"

    licence_end = _licence_end_year(row)
    start = row.get("first_export_year")
    if licence_end is not None and pd.notna(start):
        capped = licence_end - int(start) + 1
        if capped < 1:
            raise MissingInputError(
                f"{row['project_id']}: authorised_export_end_year={licence_end} "
                f"is before first_export_year={int(start)}."
            )
        if capped < life:
            return (
                capped,
                f"Asset Register:authorised_export_end_year={licence_end} "
                f"(hard stop; cuts {life - capped}y from {src})",
            )
    return life, src


def _fid_ok(row) -> bool:
    val = row["fid_confirmed"]
    if val is True or val in (1, 1.0):
        return True
    if val is False or val in (0, 0.0):
        return False
    return str(row.get("calc_group", row["tier"])) == "operating"


def _is_legacy(row, lifespan: int, current_year: int | None = None) -> bool:
    """True when first_export_year + lifespan is already in the past.

    Kept so the full-register panel does not invent a remaining life for
    1971/1976 peak-shaving plants. Headline membership is the named
    chain/calc_group filter (src.scope), not this flag. After that filter
    these plants are already out (domestic, not export).
    """
    current_year = current_year or datetime.now().year
    start = row.get("first_export_year")
    if pd.isna(start):
        return False
    return int(start) + int(lifespan) < int(current_year)


def _steady_rate(row, params) -> float:
    pid = str(row["project_id"])
    if pid == "saint_john_import_facility":
        return float(get_param(params, "saint_john_utilisation"))
    if pid == "lng_canada_phase_1":
        return float(get_param(params, "lng_canada_ph1_steady_state_utilisation"))
    return float(get_param(params, "steady_state_utilisation"))


def utilisation_for_project(
    row, lifespan: int, params, legacy: bool = False
) -> tuple[float, str, float]:
    """Return (util_sum_or_rate, source, effective_util_fraction for annual).

    For normal projects effective_util = util_sum / lifespan.
    For legacy projects effective_util = steady-state (current annual), util_sum unused.
    """
    pid = str(row["project_id"])
    steady = _steady_rate(row, params)

    if legacy:
        return (
            steady,
            (
                f"legacy: first_export_year+lifespan before current year; "
                f"steady-state util={steady} for current annual only"
            ),
            steady,
        )

    fid_ok = _fid_ok(row)
    if pid == "saint_john_import_facility":
        rate = float(get_param(params, "saint_john_utilisation"))
        return rate * lifespan, "parameter:saint_john_utilisation (flat)", rate

    if pid == "lng_canada_phase_1":
        y1 = float(get_param(params, "lng_canada_ph1_year_1_utilisation"))
        y2 = float(get_param(params, "lng_canada_ph1_year_2_utilisation"))
        ramp = int(get_param(params, "ramp_years"))
        source = "parameters:lng_canada_ph1_year_1/year_2/steady_state_utilisation"
    else:
        y1 = float(get_param(params, "year_1_utilisation"))
        y2 = float(get_param(params, "year_2_utilisation"))
        ramp = int(get_param(params, "ramp_years"))
        source = "parameters:year_1/year_2/steady_state_utilisation (default ramp)"

    delay = 0 if fid_ok else int(get_param(params, "fid_delay_mid"))
    total = op = 0
    for year in range(lifespan):
        if year < delay:
            continue
        op += 1
        total += y1 if op == 1 and ramp >= 1 else y2 if op == 2 and ramp >= 2 else steady
    if delay:
        source += f"; fid_delay_mid={delay}y inside lifespan"
    util_sum = float(total)
    return util_sum, source, util_sum / lifespan


def _resolve_drive(row, inputs: dict) -> tuple[str, str]:
    drive = row["liquefaction_drive"]
    drive_s = None if pd.isna(drive) else str(drive).strip()
    if drive_s == "not_published":
        default = inputs["liquefaction_drive_default"]
        return default, "parameter:liquefaction_drive_default (register=not_published)"
    if drive_s in DRIVE_PARAM:
        return drive_s, f"Asset Register:liquefaction_drive={drive_s}"
    if row["chain"] == "export":
        raise MissingInputError(
            f"Project '{row['project_id']}' is an export asset and must carry an "
            f"explicit liquefaction_drive on sheet 'Asset Register' (got {drive!r})."
        )
    raise MissingInputError(
        f"Project '{row['project_id']}' has liquefaction_drive={drive!r} on "
        f"Asset Register; expected a drive key or not_published."
    )


def _stage_intensity(stage: str, row, scenario: str, inputs: dict) -> tuple[float, str]:
    params, factors = inputs["params"], inputs["factors"]
    if stage == "upstream_production":
        return float(inputs["upstream_by_scenario"][scenario]), f"scenario:{scenario}"
    if stage == "liquefaction":
        drive_key, drive_src = _resolve_drive(row, inputs)
        if drive_key in {"electric_committed", "electric_planned"}:
            raise MissingInputError(
                f"Project '{row['project_id']}' still carries liquefaction_drive="
                f"{drive_key!r}. Electric drive is not assumed; set the register "
                f"drive to gas_turbine and keep the previous classification in "
                f"liquefaction_drive_note."
            )
        val = factors.loc["liquefaction", "central"]
        if pd.isna(val):
            raise MissingInputError(
                "Emission Factors: stage 'liquefaction' has a blank central value on "
                "sheet 'Emission Factors'."
            )
        return (
            float(val),
            f"Emission Factors:central:liquefaction (drive={drive_key} via {drive_src})",
        )
    val = factors.loc[stage, "central"]
    if pd.isna(val):
        raise MissingInputError(
            f"Emission Factors: stage '{stage}' has a blank central value on "
            f"sheet 'Emission Factors'."
        )
    if stage == "shipping":
        scaled, note = scale_shipping_to_route(float(val), row, params)
        return scaled, f"Emission Factors:central:shipping x {note}"
    return float(val), f"Emission Factors:central:{stage}"


def route_scale_factor(row, params) -> tuple[float, str]:
    """Per-asset shipping distance multiplier against the BC basis.

    The shipping factor on the Emission Factors sheet is derived on the
    British Columbia to north-east Asia route (`route_bc_to_northeast_asia_nm`,
    3,800 nm). An asset shipping a shorter distance burns less. The multiplier
    is `route_distance_nm / route_bc_to_northeast_asia_nm`.

    Raises rather than defaulting when `route_distance_nm` is blank. Callers
    only reach this for assets whose chain includes the shipping stage;
    bunkering has no shipping stage and never gets here.
    """
    basis = float(get_param(params, "route_bc_to_northeast_asia_nm"))
    if basis <= 0:
        raise MissingInputError(
            f"Parameter 'route_bc_to_northeast_asia_nm' must be positive; got {basis}."
        )
    dist = row.get("route_distance_nm")
    if dist is None or pd.isna(dist) or str(dist).strip() == "":
        raise MissingInputError(
            f"Project '{row['project_id']}' is on a chain that includes the "
            f"shipping stage but has a blank route_distance_nm on sheet "
            f"'Asset Register'. Shipping is scaled by route distance; a "
            f"missing distance must not be treated as the BC basis."
        )
    dist = float(dist)
    if dist <= 0:
        raise MissingInputError(
            f"Project '{row['project_id']}' has route_distance_nm={dist}; "
            f"expected a positive one-way marine distance."
        )
    return dist / basis, f"route {dist:g}nm / basis {basis:g}nm"


def scale_shipping_to_route(central: float, row, params) -> tuple[float, str]:
    scale, note = route_scale_factor(row, params)
    return central * scale, note


def stage_ch4_co2e_intensity(
    stage: str,
    intensity: float,
    inputs: dict,
) -> float:
    """CH4-derived part of one stage's CO2e intensity, tCO2e per t LNG.

    Two stages carry an identified methane portion, both from parameters
    already on the workbook:

    - `upstream_production`: the scenario factor less the part of the official
      inventory that is CO2, i.e. `inventory_as_reported x (1 - upstream_ch4_share)`
      (0.154 at default parameters). Any excess is CH4-derived CO2e. This is
      the construction the upstream factor is built from, so the split is not
      an extra assumption.
    - `shipping`: the 1.44 carrier uplift is entirely measured methane slip,
      so `1 - 1/1.44` = 0.306 of the shipping CO2e is CH4-derived.

    Pipeline transport, liquefaction, regasification and combustion are treated
    as CO2. **Pipeline fugitive methane is not split**: the workbook carries a
    single pipeline factor with no methane share behind it, so there is nothing
    to split it on. Blank beats wrong.
    """
    if stage == "upstream_production":
        params = inputs["params"]
        share = float(get_param(params, "upstream_ch4_share"))
        inv = float(inputs["upstream_by_scenario"]["inventory_as_reported"])
        floor = inv * (1.0 - share)
        if isinstance(intensity, np.ndarray):
            return np.maximum(intensity - floor, 0.0)
        return max(float(intensity) - floor, 0.0)
    if stage == "shipping":
        uplift = float(get_param(inputs["params"], "lng_carrier_methane_slip_uplift"))
        if uplift <= 0:
            raise MissingInputError(
                "Parameter 'lng_carrier_methane_slip_uplift' must be positive; "
                f"got {uplift}."
            )
        slip = 1.0 - 1.0 / uplift
        if isinstance(intensity, np.ndarray):
            return intensity * slip
        return float(intensity) * slip
    return 0.0


def previously_classified_electric(note) -> bool:
    """True when liquefaction_drive_note records a prior electric classification."""
    if note is None or (isinstance(note, float) and pd.isna(note)):
        return False
    return "previously classified as electric_" in str(note).lower()


def electrification_counterfactual(
    inputs: dict,
    by_project: pd.DataFrame,
    scenario: str = DEFAULT_SCENARIO,
) -> dict:
    """Canada-territorial LNG if liquefaction ran electric (0.12) versus gas (0.29).

    Does not change the headline case. Liquefaction is CAN-tagged on every chain
    that includes it, so the intensity delta lands entirely in Canada territorial.
    """
    params = inputs["params"]
    gas_i = float(get_param(params, "liquefaction_gas_turbine"))
    elec_i = float(get_param(params, "liquefaction_electric"))
    delta_i = gas_i - elec_i
    national = float(get_param(params, "canada_national_emissions"))
    t_low = float(get_param(params, "canada_2030_target_low"))
    t_high = float(get_param(params, "canada_2030_target_high"))

    sample = _totals_frame(by_project)
    sample = sample.loc[sample["scenario"] == scenario].copy()
    notes = inputs["assets"][["project_id", "liquefaction_drive_note"]].drop_duplicates(
        "project_id"
    )
    sample = sample.merge(notes, on="project_id", how="left")
    sample["claimed_electric"] = sample["liquefaction_drive_note"].map(
        previously_classified_electric
    )
    has_liq = sample["annual_liquefaction"].notna()
    sample["liq_delta_tco2e_yr"] = 0.0
    sample.loc[has_liq, "liq_delta_tco2e_yr"] = (
        sample.loc[has_liq, "effective_tonnes"] * delta_i
    )
    sample["liq_delta_claimed_tco2e_yr"] = sample["liq_delta_tco2e_yr"].where(
        sample["claimed_electric"], 0.0
    )
    sample["can_gas_tco2e_yr"] = sample["canada_territorial"]
    sample["can_all_electric_tco2e_yr"] = (
        sample["canada_territorial"] - sample["liq_delta_tco2e_yr"]
    )
    sample["can_claimed_electric_tco2e_yr"] = (
        sample["canada_territorial"] - sample["liq_delta_claimed_tco2e_yr"]
    )

    def _pack(g: pd.DataFrame, key: str) -> dict:
        gas = float(g["can_gas_tco2e_yr"].sum()) / 1e6
        claimed = float(g["can_claimed_electric_tco2e_yr"].sum()) / 1e6
        alle = float(g["can_all_electric_tco2e_yr"].sum()) / 1e6
        claimed_mtpa = float(
            g.loc[g["claimed_electric"] & (g["chain"] == "export"), "capacity_mtpa"].sum()
        )
        liq_gas = float(g["annual_liquefaction"].sum()) / 1e6
        return {
            "slice": key,
            "canada_territorial_gas_mtco2e_yr": gas,
            "canada_territorial_claimed_electric_mtco2e_yr": claimed,
            "canada_territorial_all_electric_mtco2e_yr": alle,
            "delta_claimed_vs_gas_mtco2e_yr": claimed - gas,
            "delta_all_electric_vs_gas_mtco2e_yr": alle - gas,
            "liquefaction_gas_mtco2e_yr": liq_gas,
            "claimed_electric_export_mtpa": claimed_mtpa,
            "share_of_national_inventory_gas": gas / national,
            "share_of_national_inventory_all_electric": alle / national,
            "share_of_2030_target_low_gas": gas / t_low,
            "share_of_2030_target_low_all_electric": alle / t_low,
            "share_of_2030_target_high_gas": gas / t_high,
            "share_of_2030_target_high_all_electric": alle / t_high,
        }

    rows = [_pack(sample, "headline")]
    for group in GROUPS:
        rows.append(_pack(sample.loc[sample["group"] == group], group))
    summary = pd.DataFrame(rows)
    claimed_ids = sorted(
        sample.loc[sample["claimed_electric"], "project_id"].unique().tolist()
    )
    return {
        "summary": summary,
        "by_project": sample,
        "gas_intensity": gas_i,
        "electric_intensity": elec_i,
        "claimed_project_ids": claimed_ids,
        "national": national,
        "target_low": t_low,
        "target_high": t_high,
    }


def compute_by_project(inputs: dict) -> pd.DataFrame:
    params = inputs["params"]
    chains = inputs["chains"]
    mtpa_to_t = float(get_param(params, "mtpa_to_tonnes"))
    rows = []

    for scenario in inputs["upstream_by_scenario"]:
        for _, row in inputs["assets"].iterrows():
            chain_name = row["chain"]
            chain_stages = chains[chain_name]
            capacity = row["capacity_mtpa"]
            base = {
                "project_id": row["project_id"],
                "project_name": row["project_name"],
                "unit_name": row.get("unit_name"),
                "tier": row["tier"],
                "calc_group": row["calc_group"],
                "end_use": row["end_use"],
                "chain": chain_name,
                "group": row["calc_group"],
                "scenario": scenario,
                "liquefaction_drive": row["liquefaction_drive"],
                "n_stages": len(chain_stages),
            }

            stage_annual = {s: None for s in ALL_STAGES}
            stage_intensity = {s: None for s in ALL_STAGES}
            stage_where = {s: None for s in ALL_STAGES}

            if pd.isna(capacity):
                rows.append({
                    **base,
                    "capacity_mtpa": None,
                    "excluded_from_totals": True,
                    "is_legacy": False,
                    "util_sum": None,
                    "effective_util": None,
                    "utilisation_source": None,
                    "lifespan_years": None,
                    "lifespan_source": None,
                    "first_export_year": row.get("first_export_year"),
                    "effective_tonnes": None,
                    "scope_1_2": None,
                    "scope_3": None,
                    "annual_total": None,
                    "lifecycle_total": None,
                    "canada_territorial": None,
                    "international_bunkers": None,
                    "foreign_territorial": None,
                    **{f"annual_{s}": None for s in ALL_STAGES},
                    **{f"intensity_{s}": None for s in ALL_STAGES},
                    **{f"where_{s}": None for s in ALL_STAGES},
                })
                continue

            life, life_src = _lifespan(row, params)
            legacy = _is_legacy(row, life)
            util_sum, util_source, effective_util = utilisation_for_project(
                row, life, params, legacy=legacy
            )
            # Annual uses effective util (lifecycle-average, or steady-state if legacy).
            effective = float(capacity) * mtpa_to_t * effective_util

            terr_acc = {t: 0.0 for t in TERRITORIES}
            scope_1_2 = scope_3 = 0.0
            for stage, where in chain_stages:
                intensity, _src = _stage_intensity(stage, row, scenario, inputs)
                value = effective * intensity
                stage_annual[stage] = value
                stage_intensity[stage] = intensity
                stage_where[stage] = where
                terr_acc[where] += value
                if stage in SCOPE_1_2_STAGES:
                    scope_1_2 += value
                elif stage in SCOPE_3_STAGES:
                    scope_3 += value
                else:
                    raise MissingInputError(f"Stage '{stage}' has no scope mapping.")

            annual_total = scope_1_2 + scope_3
            on_chain = {s for s, _ in chain_stages}
            for s in ALL_STAGES:
                if s not in on_chain:
                    assert stage_annual[s] is None, f"off-chain stage computed: {s}"

            # Duration × life-average. Not the published lifetime (that is
            # the calendar panel sum). Kept for diagnostics and util identity.
            # Legacy: current annual only — no duration product.
            lifecycle_total = None if legacy else annual_total * life

            rows.append({
                **base,
                "capacity_mtpa": float(capacity),
                "lifespan_years": life,
                "lifespan_source": life_src,
                "first_export_year": (
                    None if pd.isna(row.get("first_export_year"))
                    else int(row["first_export_year"])
                ),
                "is_legacy": legacy,
                "fid_confirmed": _fid_ok(row),
                "liquefaction_drive": (
                    None
                    if pd.isna(row["liquefaction_drive"])
                    else str(row["liquefaction_drive"]).strip()
                ),
                "util_sum": util_sum,
                "effective_util": effective_util,
                "utilisation_source": util_source,
                "effective_tonnes": effective,
                **{f"intensity_{s}": stage_intensity[s] for s in ALL_STAGES},
                **{f"annual_{s}": stage_annual[s] for s in ALL_STAGES},
                **{f"where_{s}": stage_where[s] for s in ALL_STAGES},
                "scope_1_2": scope_1_2,
                "scope_3": scope_3,
                "annual_total": annual_total,
                "lifecycle_total": lifecycle_total,
                "canada_territorial": terr_acc["CAN"],
                "international_bunkers": terr_acc["BUNK"],
                "foreign_territorial": terr_acc["FOR"],
                "excluded_from_totals": False,
            })

    result = pd.DataFrame(rows)
    chains, groups = headline_scope_sets(inputs)
    if len(result):
        result["in_headline_scope"] = (
            ~result["excluded_from_totals"].astype(bool)
            & scope_mask(result, chains, groups)
        )
    else:
        result["in_headline_scope"] = pd.Series(dtype=bool)
    active = result.loc[~result["excluded_from_totals"]]
    if len(active):
        terr_sum = (
            active["canada_territorial"]
            + active["international_bunkers"]
            + active["foreign_territorial"]
        )
        assert (terr_sum - active["annual_total"]).abs().max() < 1e-6
        assert (
            active["scope_1_2"] + active["scope_3"] - active["annual_total"]
        ).abs().max() < 1e-6
        print(f"[reconcile] territory+scope identity OK (n={len(active)})")
    n_head = int(result.loc[result["in_headline_scope"], "project_id"].nunique())
    print(
        f"[scope] headline = chain in {sorted(chains)} and calc_group in "
        f"{sorted(groups)} (n={n_head})"
    )
    return result


def _agg_emissions(g: pd.DataFrame) -> dict:
    """Aggregate emissions only — never capacity (capacity is chain-specific)."""
    s12 = float(g["scope_1_2"].sum())
    s3 = float(g["scope_3"].sum())
    annual = float(g["annual_total"].sum())
    can = float(g["canada_territorial"].sum())
    bunk = float(g["international_bunkers"].sum())
    foreign = float(g["foreign_territorial"].sum())
    assert abs(s12 + s3 - annual) < 1e-4
    assert abs(can + bunk + foreign - annual) < 1e-4
    # Legacy rows have null lifecycle_total; sum only non-null.
    life = float(g["lifecycle_total"].sum(min_count=1)) if len(g) else 0.0
    if pd.isna(life):
        life = 0.0
    return {
        "project_count": int(len(g)),
        "scope_1_2_mtco2e_yr": s12 / 1e6,
        "scope_3_mtco2e_yr": s3 / 1e6,
        "canada_territorial_mtco2e_yr": can / 1e6,
        "international_bunkers_mtco2e_yr": bunk / 1e6,
        "foreign_territorial_mtco2e_yr": foreign / 1e6,
        "annual_total_mtco2e_yr": annual / 1e6,
        "lifecycle_total_mtco2e": life / 1e6,
        "scope_1_2_tco2e_yr": s12,
        "scope_3_tco2e_yr": s3,
        "canada_territorial_tco2e_yr": can,
        "international_bunkers_tco2e_yr": bunk,
        "foreign_territorial_tco2e_yr": foreign,
        "annual_total_tco2e_yr": annual,
        "lifecycle_total_tco2e": life,
    }


def _capacity_by_chain(g: pd.DataFrame) -> dict:
    """Capacity reported per chain only — never summed across chains."""
    out = {f"capacity_{c}_mtpa": 0.0 for c in CHAINS}
    for chain in CHAINS:
        out[f"capacity_{chain}_mtpa"] = float(
            g.loc[g["chain"] == chain, "capacity_mtpa"].sum()
        )
    # Headline capacity = export liquefaction (comparable to published Canadian LNG).
    out["capacity_export_headline_mtpa"] = out["capacity_export_mtpa"]
    return out


def _totals_frame(by_project: pd.DataFrame) -> pd.DataFrame:
    """Rows that enter published totals: headline scope when the flag exists."""
    if "in_headline_scope" in by_project.columns:
        return by_project.loc[by_project["in_headline_scope"]]
    return by_project.loc[~by_project["excluded_from_totals"]]


def summarise(by_project: pd.DataFrame) -> pd.DataFrame:
    """One row per calc_group per scenario. Early-stage is inside proposed.

    Capacity is reported per chain; headline capacity is export only.
    """
    active = _totals_frame(by_project)
    rows = []
    for scenario, s_df in active.groupby("scenario", sort=False):
        for group in GROUPS:
            g = s_df.loc[s_df["group"] == group]
            block = _agg_emissions(g)
            caps = _capacity_by_chain(g)
            rows.append({"group": group, "scenario": scenario, **caps, **block})
    summary = pd.DataFrame(rows)
    print("[reconcile] calc_group scope+territory sums OK")
    return summary


def summarise_by_chain(by_project: pd.DataFrame) -> pd.DataFrame:
    """One row per chain per scenario. Capacity is within-chain only."""
    active = _totals_frame(by_project)
    rows = []
    for scenario, s_df in active.groupby("scenario", sort=False):
        for chain in CHAINS:
            g = s_df.loc[s_df["chain"] == chain]
            block = _agg_emissions(g)
            cap = float(g["capacity_mtpa"].sum()) if len(g) else 0.0
            rows.append({
                "chain": chain,
                "scenario": scenario,
                "capacity_mtpa": cap,
                **block,
            })
    return pd.DataFrame(rows)


def assert_no_cross_chain_capacity_sum(outputs: dict) -> None:
    """Raise if any aggregated output mixes liquefaction and regasification capacity."""
    summary = outputs["summary"]
    # Group summary must not carry a single mixed capacity_mtpa column.
    if "capacity_mtpa" in summary.columns:
        raise AssertionError(
            "Summary has capacity_mtpa — that would sum across chains. "
            "Use capacity_<chain>_mtpa / capacity_export_headline_mtpa."
        )
    by_chain = outputs["by_chain"]
    # Within-chain capacity is fine; verify chains are not then re-summed elsewhere
    # by checking By Project is the only place with mixed-chain capacity rows.
    sample = _totals_frame(outputs["by_project"])
    sample = sample.loc[sample["scenario"] == DEFAULT_SCENARIO]
    mixed = sample.groupby("calc_group")["chain"].nunique()
    # Groups can contain multiple chains — that is OK at project grain.
    # Forbidden: a rolled-up number that adds those capacities.
    for col in summary.columns:
        if col.startswith("capacity_") and col.endswith("_mtpa"):
            continue
    # Sanity: export headline equals export column
    assert (
        summary["capacity_export_headline_mtpa"] - summary["capacity_export_mtpa"]
    ).abs().max() < 1e-9
    # by_chain capacity must equal per-chain slice of projects
    for chain in CHAINS:
        exp = float(sample.loc[sample["chain"] == chain, "capacity_mtpa"].sum())
        got = float(
            by_chain.loc[
                (by_chain["scenario"] == DEFAULT_SCENARIO) & (by_chain["chain"] == chain),
                "capacity_mtpa",
            ].iloc[0]
        )
        assert abs(exp - got) < 1e-9, (chain, exp, got)
    _ = mixed  # groups may span chains; capacity columns stay per-chain
    print("[validate] no capacity summed across chains PASS")


def by_stage(by_project: pd.DataFrame, scenario: str = DEFAULT_SCENARIO) -> pd.DataFrame:
    """Stage totals for full headline (all calc_groups)."""
    head = _totals_frame(by_project)
    head = head.loc[head["scenario"] == scenario]
    total = float(head["annual_total"].sum())
    rows, running = [], 0.0
    for stage in ALL_STAGES:
        series = head[f"annual_{stage}"].dropna()
        value = float(series.sum()) if len(series) else 0.0
        wheres = head.loc[head[f"annual_{stage}"].notna(), f"where_{stage}"].dropna().unique()
        running += value
        rows.append({
            "scenario": scenario,
            "coverage": "headline_all_calc_groups",
            "stage": stage,
            "territorial_destination": ",".join(sorted(set(wheres))) if len(wheres) else None,
            "projects_with_stage": int(series.shape[0]),
            "annual_tco2e_yr": value,
            "annual_mtco2e_yr": value / 1e6,
            "share_of_total": value / total if total else None,
        })
    assert abs(running - total) < 1e-3
    print(f"[reconcile] by-stage -> headline OK ({total/1e6:.2f} Mt)")
    return pd.DataFrame(rows)


def territorial_table(
    by_project: pd.DataFrame,
    params: dict,
    scenario: str = DEFAULT_SCENARIO,
) -> pd.DataFrame:
    active = _totals_frame(by_project)
    active = active.loc[active["scenario"] == scenario]
    national = float(get_param(params, "canada_national_emissions"))
    t_low = float(get_param(params, "canada_2030_target_low"))
    t_high = float(get_param(params, "canada_2030_target_high"))
    gap = float(get_param(params, "canada_2030_overshoot_gap"))

    rows = []
    for loc, col in (
        ("CAN", "canada_territorial"),
        ("BUNK", "international_bunkers"),
        ("FOR", "foreign_territorial"),
    ):
        value = float(active[col].sum()) / 1e6
        rows.append({
            "slice": "location_headline",
            "key": loc,
            "annual_mtco2e_yr": value,
            "share_of_slice_total": None,
            "share_of_national_inventory": value / national if loc == "CAN" else None,
            "share_of_2030_target_low": value / t_low if loc == "CAN" else None,
            "share_of_2030_target_high": value / t_high if loc == "CAN" else None,
            "share_of_2030_overshoot_gap": value / gap if loc == "CAN" else None,
        })
    loc_total = sum(r["annual_mtco2e_yr"] for r in rows)
    for r in rows:
        r["share_of_slice_total"] = r["annual_mtco2e_yr"] / loc_total if loc_total else None

    for group in GROUPS:
        g = active.loc[active["group"] == group]
        can = float(g["canada_territorial"].sum()) / 1e6
        bunk = float(g["international_bunkers"].sum()) / 1e6
        foreign = float(g["foreign_territorial"].sum()) / 1e6
        rows.append({
            "slice": "calc_group",
            "key": group,
            "annual_mtco2e_yr": can + bunk + foreign,
            "canada_territorial_mtco2e_yr": can,
            "international_bunkers_mtco2e_yr": bunk,
            "foreign_territorial_mtco2e_yr": foreign,
            "share_of_slice_total": None,
            "share_of_national_inventory": can / national,
            "share_of_2030_target_low": can / t_low,
            "share_of_2030_target_high": can / t_high,
            "share_of_2030_overshoot_gap": can / gap,
        })
    return pd.DataFrame(rows)


def assumptions_used(inputs: dict, by_project: pd.DataFrame) -> pd.DataFrame:
    meta = inputs["params_meta"].set_index("parameter")
    rows = [
        {
            "item": n,
            "kind": "parameter",
            "value": meta.loc[n, "value"],
            "unit": meta.loc[n].get("unit"),
            "source": meta.loc[n].get("source"),
            "sheet": "Parameters",
        }
        for n in REQUIRED_PARAMS
    ]
    for stage in ALL_STAGES:
        f = inputs["factors"].loc[stage]
        rows.append({
            "item": f"central_{stage}",
            "kind": "emission_factor",
            "value": f["central"],
            "unit": f.get("unit"),
            "source": f.get("basis_for_central"),
            "sheet": "Emission Factors",
        })
    for name, val in inputs["upstream_by_scenario"].items():
        rows.append({
            "item": f"upstream_{name}",
            "kind": "scenario",
            "value": val,
            "unit": "tCO2e per t LNG",
            "source": "Scenarios.projects_or_band",
            "sheet": "Scenarios",
        })
    for chain, stages in inputs["chains"].items():
        rows.append({
            "item": f"chain_{chain}",
            "kind": "chain",
            "value": " > ".join(f"{s}@{w}" for s, w in stages),
            "unit": f"{len(stages)} stages",
            "source": "Chains tab",
            "sheet": "Chains",
        })
    sample = by_project.loc[
        (~by_project["excluded_from_totals"])
        & (by_project["scenario"] == DEFAULT_SCENARIO)
    ]
    for _, r in sample.iterrows():
        unit = (
            "steady-state util (legacy annual only)"
            if r.get("is_legacy")
            else "util_sum over lifespan"
        )
        rows.append({
            "item": f"utilisation_{r['project_id']}",
            "kind": "utilisation_source",
            "value": r["util_sum"],
            "unit": unit,
            "source": r["utilisation_source"],
            "sheet": "Parameters",
        })
        life_note = r["lifespan_source"]
        if r.get("is_legacy"):
            start = r.get("first_export_year")
            life_note = (
                f"{life_note}; LEGACY: first_export_year={start} + "
                f"{int(r['lifespan_years'])}yr before current year — "
                f"annual only, no lifecycle total"
            )
        rows.append({
            "item": f"lifespan_{r['project_id']}",
            "kind": "lifespan_source",
            "value": r["lifespan_years"],
            "unit": "years",
            "source": life_note,
            "sheet": "Asset Register / Parameters",
        })
    return pd.DataFrame(rows)


CARBON_BUDGET_PARAMS = (
    ("remaining_15c_budget", "1.5°C, 50% from start of 2026"),
    ("remaining_17c_budget", "1.7°C, 50% from start of 2026"),
    ("remaining_2c_budget", "2.0°C, 50% from start of 2026"),
)


CO2_ONLY_BUDGET_CAVEAT = (
    "Like for like: CO2-only lifetime against a CO2 budget. Residual caveats: "
    "pipeline fugitive methane is not split out of the CO2 total, and non-CO2 "
    "gases other than CH4 (N2O, refrigerants) are not counted at all."
)


def carbon_budget_shares(
    lifetime_mtco2e: float,
    params,
    lifetime_co2_only_mt: float | None = None,
) -> pd.DataFrame:
    """Lifetime against the GCB 2025 remaining CO2 budgets, both bases.

    `share_pct` is the **paper value**: the CO2-only lifetime against a CO2
    budget. `share_co2e_pct` is the older CO2e-against-CO2 comparison, kept
    for continuity and labelled as an approximation.
    """
    gt = float(lifetime_mtco2e) / 1000.0
    if lifetime_co2_only_mt is None:
        raise MissingInputError(
            "carbon_budget_shares needs lifetime_co2_only_mt. The paper value "
            "is the CO2-only share; pass it from the panel gas split."
        )
    gt_co2 = float(lifetime_co2_only_mt) / 1000.0
    rows = []
    for name, label in CARBON_BUDGET_PARAMS:
        budget = float(get_param(params, name))
        rows.append({
            "parameter": name,
            "label": label,
            "budget_gtco2": budget,
            "lifetime_gtco2": gt_co2,
            "lifetime_gtco2e": gt,
            "share_pct": 100.0 * gt_co2 / budget,
            "share_basis": "CO2-only lifetime vs CO2 budget (paper value)",
            "share_co2e_pct": 100.0 * gt / budget,
            "share_co2e_basis": "GWP100 CO2e vs CO2 budget (approximation)",
            "units_note": CO2_ONLY_BUDGET_CAVEAT,
        })
    return pd.DataFrame(rows)
