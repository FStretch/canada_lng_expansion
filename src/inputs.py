"""Load and validate both workbooks. Only module that reads the xlsx inputs."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

DEFAULT_SCENARIO = "measurement_central"
INTENSITY_SCENARIOS = (
    "inventory_as_reported",
    "measurement_central",
    "measurement_high",
    "near_term_methane_gwp20",
    "howarth_high",
)
DRIVE_PARAM = {
    "gas_turbine": "liquefaction_gas_turbine",
    "electric_committed": "liquefaction_electric",
    "electric_planned": "liquefaction_electric",
}
ALL_STAGES = (
    "upstream_production",
    "pipeline_transport",
    "liquefaction",
    "shipping",
    "regasification",
    "combustion",
)
SCOPE_1_2_STAGES = {"upstream_production", "pipeline_transport", "liquefaction"}
SCOPE_3_STAGES = {"shipping", "regasification", "combustion"}
TERRITORIES = ("CAN", "BUNK", "FOR")
EXPECTED_CHAIN_LENGTHS = {
    "export": 6,
    "bunkering": 4,
    "domestic": 5,
    "import": 2,
}
VALID_CHAINS = {"export", "bunkering", "domestic", "import"}
# watch is a tier, not a calc_group used in totals (Saint John is operating).
VALID_CALC_GROUPS = {
    "operating",
    "under_construction",
    "proposed",
}
CALC_GROUPS = (
    "operating",
    "under_construction",
    "proposed",
)
REQUIRED_PARAMS = (
    "liquefaction_gas_turbine",
    "liquefaction_electric",
    "liquefaction_drive_default",
    "upstream_ch4_share",
    "upstream_measurement_correction",
    "gwp100_ch4",
    "gwp20_ch4",
    "year_1_utilisation",
    "year_2_utilisation",
    "steady_state_utilisation",
    "ramp_years",
    "fid_delay_mid",
    "lifecycle_years_default",
    "mtpa_to_tonnes",
    "saint_john_utilisation",
    "lng_canada_ph1_year_1_utilisation",
    "lng_canada_ph1_year_2_utilisation",
    "lng_canada_ph1_steady_state_utilisation",
    "canada_national_emissions",
    "canada_2030_target_low",
    "canada_2030_target_high",
    "canada_2030_overshoot_gap",
    "lng_export_licence_max_term",
    "lng_energy_content",
)


class MissingInputError(KeyError):
    pass


def _read_excel_readonly(path: Path, sheet: str) -> pd.DataFrame:
    """Open workbook bytes read-only. If the file is locked (e.g. open in Excel),
    copy via the shell to a temp path — never opens Inputs/ for write."""
    import subprocess
    import tempfile

    path = Path(path)
    tmp = Path(tempfile.gettempdir()) / f"_canada_lng_ro_{path.name}"

    def _load(p: Path) -> pd.DataFrame:
        with open(p, "rb") as fh:
            return pd.read_excel(fh, sheet_name=sheet)

    try:
        return _load(path)
    except PermissionError:
        # PowerShell Copy-Item can read files Excel has open; Python open() cannot.
        subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                f"Copy-Item -LiteralPath '{path}' -Destination '{tmp}' -Force",
            ],
            check=True,
            capture_output=True,
        )
        return _load(tmp)


def get_param(params: dict, name: str):
    if name not in params:
        raise MissingInputError(
            f"Missing parameter '{name}' on sheet 'Parameters'. "
            f"Add it to Inputs/Canada_LNG_Data_Inputs.xlsx."
        )
    value = params[name]
    if value is None or (isinstance(value, float) and pd.isna(value)):
        raise MissingInputError(
            f"Parameter '{name}' on sheet 'Parameters' is blank. "
            f"A missing value must not be treated as zero."
        )
    return value


def parse_chains(chains_df: pd.DataFrame) -> dict[str, list[tuple[str, str]]]:
    required = {"chain", "stage_1", "where_1"}
    if not required.issubset(chains_df.columns):
        raise MissingInputError(
            f"Chains sheet missing columns: {sorted(required - set(chains_df.columns))}"
        )
    out: dict[str, list[tuple[str, str]]] = {}
    for _, row in chains_df.iterrows():
        name = row.get("chain")
        if pd.isna(name):
            continue
        name = str(name).strip()
        stages: list[tuple[str, str]] = []
        for i in range(1, 7):
            stage = row.get(f"stage_{i}")
            where = row.get(f"where_{i}")
            if pd.isna(stage) or str(stage).strip().lower() in {"", "not applicable"}:
                continue
            stage_s = str(stage).strip()
            if pd.isna(where) or str(where).strip() == "":
                raise MissingInputError(
                    f"Chains sheet: chain '{name}' stage '{stage_s}' has blank where_{i}."
                )
            where_s = str(where).strip().upper()
            if where_s not in TERRITORIES:
                raise MissingInputError(
                    f"Chains sheet: chain '{name}' has unknown location '{where_s}'."
                )
            if stage_s not in ALL_STAGES:
                raise MissingInputError(
                    f"Chains sheet: chain '{name}' has unknown stage '{stage_s}'."
                )
            stages.append((stage_s, where_s))
        out[name] = stages
    for chain, expected in EXPECTED_CHAIN_LENGTHS.items():
        if chain not in out:
            raise MissingInputError(f"Chains sheet is missing chain '{chain}'.")
        if len(out[chain]) != expected:
            raise MissingInputError(
                f"Chains sheet: chain '{chain}' has {len(out[chain])} stages, "
                f"expected {expected}."
            )
    return out


def load_inputs(register_path: str | Path, inputs_path: str | Path) -> dict:
    register_path, inputs_path = Path(register_path), Path(inputs_path)
    assets_raw = _read_excel_readonly(register_path, "Asset Register")
    factors = _read_excel_readonly(inputs_path, "Emission Factors")
    params_df = _read_excel_readonly(inputs_path, "Parameters")
    scenarios = _read_excel_readonly(inputs_path, "Scenarios")
    chains_df = _read_excel_readonly(inputs_path, "Chains")

    for col in (
        "project_id",
        "project_name",
        "tier",
        "calc_group",
        "end_use",
        "chain",
        "capacity_mtpa",
        "fid_confirmed",
        "project_life_years",
        "authorised_export_term_years",
        "liquefaction_drive",
        "first_export_year",
    ):
        if col not in assets_raw.columns:
            raise MissingInputError(f"Asset Register missing column '{col}'.")

    findings: list[str] = []
    for col in ("stage", "scope", "unit", "central"):
        if col not in factors.columns:
            raise MissingInputError(f"Emission Factors missing column '{col}'.")

    factors = factors.set_index("stage", drop=False)
    for stage in ALL_STAGES:
        if stage not in factors.index:
            raise MissingInputError(f"Emission Factors sheet is missing stage '{stage}'.")
        if stage != "liquefaction" and pd.isna(factors.loc[stage, "central"]):
            raise MissingInputError(
                f"Emission Factors: stage '{stage}' has a blank central value on "
                f"sheet 'Emission Factors'."
            )
    if not pd.isna(factors.loc["liquefaction", "central"]):
        raise MissingInputError(
            "Emission Factors: liquefaction 'central' must be empty. "
            "Use liquefaction_gas_turbine / liquefaction_electric from Parameters."
        )

    params, meta_rows = {}, []
    for _, row in params_df.iterrows():
        if pd.isna(row.get("parameter")):
            continue
        name = str(row["parameter"]).strip()
        params[name] = row["value"]
        meta_rows.append(row)
    for name in REQUIRED_PARAMS:
        get_param(params, name)

    upstream = {}
    for _, row in scenarios.iterrows():
        name = row.get("name")
        if pd.isna(name) or str(name).strip() not in INTENSITY_SCENARIOS:
            continue
        m = re.search(r"upstream\s+([0-9]*\.?[0-9]+)", str(row.get("projects_or_band")), re.I)
        if not m:
            raise MissingInputError(
                f"Scenarios sheet: '{name}' has no 'upstream <value>' in projects_or_band."
            )
        upstream[str(name).strip()] = float(m.group(1))
    missing = [s for s in INTENSITY_SCENARIOS if s not in upstream]
    if missing:
        raise MissingInputError(f"Scenarios sheet is missing intensity scenarios: {missing}")

    chains = parse_chains(chains_df)

    # inactive / watch calc_groups are out of the calculation entirely.
    rows = []
    excluded_none = []
    excluded_watch = []

    for _, row in assets_raw.iterrows():
        pid = row["project_id"]
        cg_raw = row["calc_group"]
        if pd.isna(cg_raw) or str(cg_raw).strip() == "":
            raise MissingInputError(
                f"Project '{pid}' has no calc_group on sheet 'Asset Register'."
            )
        calc_group = str(cg_raw).strip().lower()
        if calc_group == "inactive":
            continue
        if calc_group == "watch":
            excluded_watch.append(pid)
            continue
        if calc_group not in VALID_CALC_GROUPS:
            raise MissingInputError(
                f"Project '{pid}' has unknown calc_group {cg_raw!r} on Asset Register. "
                f"Expected one of {sorted(VALID_CALC_GROUPS)}, watch, or inactive."
            )

        raw_chain = row["chain"]
        blank_chain = pd.isna(raw_chain) or str(raw_chain).strip() == ""
        if blank_chain:
            if pd.notna(row["capacity_mtpa"]):
                raise MissingInputError(
                    f"Project '{pid}' has capacity but no chain on sheet "
                    f"'Asset Register'. Expected export, bunkering, domestic, "
                    f"import, or none."
                )
            excluded_none.append(pid)
            findings.append(
                f"{pid}: chain blank on Asset Register (no capacity); "
                f"excluded like chain=none — not zeroed."
            )
            continue
        chain = str(raw_chain).strip().lower()
        if chain == "none":
            excluded_none.append(pid)
            findings.append(
                f"{pid}: chain=none — no lifecycle applies; excluded (not zeroed)."
            )
            continue
        if chain not in VALID_CHAINS:
            raise MissingInputError(
                f"Project '{pid}' has unknown chain {raw_chain!r} on Asset Register."
            )

        rec = row.copy()
        rec["chain"] = chain
        rec["calc_group"] = calc_group
        rec["group"] = calc_group  # grouping key for aggregation
        rows.append(rec)

    if not rows:
        raise MissingInputError("No in-scope assets after reading calc_group and chain.")
    assets = pd.DataFrame(rows).reset_index(drop=True)

    flags = []
    for _, r in assets.iterrows():
        if pd.isna(r["capacity_mtpa"]):
            flags.append(
                {"project_id": r["project_id"], "field": "capacity_mtpa", "issue": "missing"}
            )
        needs_liq = any(s == "liquefaction" for s, _ in chains[r["chain"]])
        drive = r["liquefaction_drive"]
        drive_s = None if pd.isna(drive) else str(drive).strip()
        if needs_liq and r["chain"] == "export":
            if drive_s is None or drive_s == "" or drive_s == "not_published":
                if pd.notna(r["capacity_mtpa"]):
                    raise MissingInputError(
                        f"Project '{r['project_id']}' is an export asset and must carry an "
                        f"explicit liquefaction_drive on sheet 'Asset Register' "
                        f"(got {drive!r})."
                    )
                flags.append(
                    {
                        "project_id": r["project_id"],
                        "field": "liquefaction_drive",
                        "issue": "missing",
                    }
                )

    default_drive = str(get_param(params, "liquefaction_drive_default")).strip()
    if default_drive not in DRIVE_PARAM:
        raise MissingInputError(
            f"Parameter 'liquefaction_drive_default' on sheet 'Parameters' is "
            f"{default_drive!r}; expected one of {list(DRIVE_PARAM)}."
        )

    return {
        "assets": assets,
        "factors": factors,
        "params": params,
        "params_meta": pd.DataFrame(meta_rows),
        "upstream_by_scenario": upstream,
        "chains": chains,
        "chains_df": chains_df,
        "register_path": register_path,
        "inputs_path": inputs_path,
        "flags": flags,
        "findings": findings,
        "excluded_none": excluded_none,
        "excluded_watch": excluded_watch,
        "liquefaction_drive_default": default_drive,
        "calc_group_source": "Asset Register:calc_group",
    }
