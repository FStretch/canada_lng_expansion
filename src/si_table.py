"""Supplementary information: one row per headline-scope asset.

Everything a reader needs to check an individual project against the register,
in one place: what it is, how big, when it starts and on what basis, how long
it runs and why, what it emits over its life and where those emissions land,
and what Global Energy Monitor says about it.
"""

from __future__ import annotations

import pandas as pd

from src.inputs import DEFAULT_SCENARIO
from src.model import _fid_ok, _lifespan
from src.scope import headline_scope_sets, row_in_headline_scope
from src.trajectories import _chain_intensity_split, _start_year, panel_lifetime_mt

# Province to coast. Only provinces that appear on headline-scope rows.
COAST = {
    "British Columbia": "Pacific",
    "Quebec": "Atlantic",
    "Newfoundland and Labrador": "Atlantic",
    "New Brunswick": "Atlantic",
    "Nova Scotia": "Atlantic",
}


def _blank(value) -> bool:
    return value is None or (isinstance(value, float) and pd.isna(value)) or pd.isna(value)


def _life_basis(source: str) -> str:
    s = str(source)
    if "authorised_export_end_year" in s:
        return "licence end"
    if "authorised_export_term_years" in s:
        return "licence term"
    if "project_life_years" in s:
        return "proponent"
    if "lifecycle_years_default" in s:
        return "parameters default"
    return s


def build_si_asset_table(inputs: dict, panel: pd.DataFrame) -> pd.DataFrame:
    """One row per headline-scope asset, sorted by lifetime emissions."""
    chains, groups = headline_scope_sets(inputs)
    params = inputs["params"]
    assumed = int(
        pd.to_numeric(params["assumed_first_export_year_if_missing"])
    )
    headline_life = panel_lifetime_mt(panel, DEFAULT_SCENARIO)

    rows = []
    for _, row in inputs["assets"].iterrows():
        if _blank(row["capacity_mtpa"]):
            continue
        if not row_in_headline_scope(row, chains, groups):
            continue
        pid = str(row["project_id"])
        life_years, life_src = _lifespan(row, params)
        start, placeholder = _start_year(row, assumed)
        lifetime = panel_lifetime_mt(panel, DEFAULT_SCENARIO, project_id=pid)

        total_i, _c, _h = _chain_intensity_split(
            row, DEFAULT_SCENARIO, inputs, canada_only=False
        )
        can_i, _c2, _h2 = _chain_intensity_split(
            row, DEFAULT_SCENARIO, inputs, canada_only=True
        )
        bunk_i = 0.0
        for stage, where in inputs["chains"][row["chain"]]:
            if where != "BUNK":
                continue
            from src.model import _stage_intensity

            bunk_i += _stage_intensity(stage, row, DEFAULT_SCENARIO, inputs)[0]
        for_i = total_i - can_i - bunk_i

        # Emitting years, so per-year figures are over the operating window
        # rather than the whole panel.
        emitting = panel.loc[
            (panel["scenario"] == DEFAULT_SCENARIO)
            & (panel["project_id"] == pid)
            & (panel["emissions_mtco2e"] > 0)
        ]
        n_years = int(emitting["year"].nunique()) or 1
        province = "" if _blank(row.get("province")) else str(row["province"]).strip()

        rows.append({
            "project": str(row["project_name"]),
            "project_id": pid,
            "province": province,
            "coast": COAST.get(province, "not available"),
            "tier": "" if _blank(row["tier"]) else str(row["tier"]).strip(),
            "calc_group": str(row["calc_group"]),
            "capacity_mtpa": float(row["capacity_mtpa"]),
            "capacity_basis": (
                "not available" if _blank(row.get("capacity_basis"))
                else str(row["capacity_basis"])
            ),
            "first_export_year": start,
            "first_export_year_is_placeholder": bool(placeholder),
            "first_export_year_note": (
                f"placeholder: assumed_first_export_year_if_missing={assumed}"
                if placeholder
                else "Asset Register:first_export_year"
            ),
            "life_years": int(life_years),
            "life_basis": _life_basis(life_src),
            "life_source": life_src,
            "lifetime_mtco2e": lifetime,
            "share_of_full_buildout_pct": (
                100.0 * lifetime / headline_life if headline_life else float("nan")
            ),
            "emitting_years": n_years,
            "canada_territorial_mtco2e_per_year": lifetime * can_i / total_i / n_years,
            "international_bunkers_mtco2e_per_year": (
                lifetime * bunk_i / total_i / n_years
            ),
            "foreign_territorial_mtco2e_per_year": (
                lifetime * for_i / total_i / n_years
            ),
            "fid_confirmed": bool(_fid_ok(row)),
            "gem_status_verbatim": (
                "not available" if _blank(row.get("gem_status_verbatim"))
                else str(row["gem_status_verbatim"])
            ),
            "gem_status_date": (
                "not available" if _blank(row.get("gem_status_date"))
                else str(row["gem_status_date"])
            ),
            "gem_wiki_url": (
                "not available" if _blank(row.get("gem_wiki_url"))
                else str(row["gem_wiki_url"])
            ),
            "register_status": (
                "not available" if _blank(row.get("status")) else str(row["status"])
            ),
            "feedgas_basin": (
                "not available" if _blank(row.get("feedgas_basin"))
                else str(row["feedgas_basin"])
            ),
            "route_distance_nm": (
                None if _blank(row.get("route_distance_nm"))
                else float(row["route_distance_nm"])
            ),
        })

    table = pd.DataFrame(rows).sort_values(
        "lifetime_mtco2e", ascending=False
    ).reset_index(drop=True)
    table["gem_disagrees_with_register"] = [
        g not in ("not available", r)
        for g, r in zip(table["gem_status_verbatim"], table["register_status"])
    ]
    return table


def format_si_table_markdown(table: pd.DataFrame) -> list[str]:
    lines = []
    lines.append("## SI table: per-asset detail")
    lines.append("")
    lines.append(
        "One row per headline-scope asset. Full machine-readable version, with "
        "capacity_basis and life_source in full, at "
        "`Outputs/si_table_assets.csv` and on the `SI Assets` sheet of the "
        "results workbook."
    )
    lines.append("")
    lines.append(
        "| project | coast | tier | calc_group | mtpa | first export | life (basis) | "
        "lifetime Mt | share | CAN / BUNK / FOR Mt per year | FID | GEM status (date) |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for _, r in table.iterrows():
        start = f"{r['first_export_year']}"
        if r["first_export_year_is_placeholder"]:
            start += " *"
        lines.append(
            f"| {r['project']} | {r['coast']} | {r['tier']} | {r['calc_group']} | "
            f"{r['capacity_mtpa']:g} | {start} | "
            f"{r['life_years']} ({r['life_basis']}) | "
            f"{r['lifetime_mtco2e']:,.1f} | "
            f"{r['share_of_full_buildout_pct']:.1f}% | "
            f"{r['canada_territorial_mtco2e_per_year']:.1f} / "
            f"{r['international_bunkers_mtco2e_per_year']:.1f} / "
            f"{r['foreign_territorial_mtco2e_per_year']:.1f} | "
            f"{'yes' if r['fid_confirmed'] else 'no'} | "
            f"{r['gem_status_verbatim']} ({r['gem_status_date']}) |"
        )
    lines.append("")
    n_ph = int(table["first_export_year_is_placeholder"].sum())
    lines.append(
        f"\\* first export year is the `assumed_first_export_year_if_missing` "
        f"placeholder, not a register value ({n_ph} of {len(table)} assets). "
        f"Per-year territorial figures are the asset's lifetime split over its "
        f"own emitting years, not calendar-panel years."
    )
    lines.append("")
    dis = table.loc[table["gem_disagrees_with_register"]]
    if len(dis):
        lines.append(
            "**GEM disagrees with the register on "
            + ", ".join(dis["project"].tolist())
            + ".** "
            + " ".join(
                f"GEM has {r['project']} as \"{r['gem_status_verbatim']}\" "
                f"({r['gem_status_date']}); the register has "
                f"\"{r['register_status']}\", worth "
                f"{r['lifetime_mtco2e']:,.1f} MtCO2e "
                f"({r['share_of_full_buildout_pct']:.1f}% of the headline "
                f"lifetime)."
                for _, r in dis.iterrows()
            )
            + " The verbatim status is recorded and a Data Gaps row is open; "
            "the classification has not been changed, because that is a scope "
            "decision rather than a data-capture one. It should be resolved "
            "before publication."
        )
        lines.append("")
    return lines
