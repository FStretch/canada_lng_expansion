"""Headline results scope: export-chain assets in named calc_groups.

Rationale: domestic peak-shaving and distribution assets are not export
capacity and not expansion. The paper's subject is export buildout.
Retaining the 1971/1976 plants in the headline would require inventing a
retirement date that no available source supports.

Rule: an asset is in headline scope iff its chain is listed in
headline_scope_chains and its calc_group is listed in
headline_scope_calc_groups. Both are Parameters-sheet comma-separated
class lists, not an asset-id list.
"""

from __future__ import annotations

import pandas as pd

from src.inputs import DEFAULT_SCENARIO, get_param


SCOPE_RULE_ONE_LINE = (
    "Headline results include assets whose chain is in headline_scope_chains "
    "and whose calc_group is in headline_scope_calc_groups "
    "(export / operating,under_construction,proposed)."
)


def parse_scope_list(params: dict, name: str) -> frozenset[str]:
    raw = str(get_param(params, name))
    items = [p.strip().lower() for p in raw.split(",") if p.strip()]
    if not items:
        raise ValueError(f"Parameter '{name}' is empty.")
    return frozenset(items)


def headline_scope_sets(inputs: dict) -> tuple[frozenset[str], frozenset[str]]:
    params = inputs["params"]
    return (
        parse_scope_list(params, "headline_scope_chains"),
        parse_scope_list(params, "headline_scope_calc_groups"),
    )


def scope_mask(df: pd.DataFrame, chains: frozenset[str], groups: frozenset[str]) -> pd.Series:
    chain = df["chain"].astype(str).str.strip().str.lower()
    cg = df["calc_group"].astype(str).str.strip().str.lower()
    return chain.isin(chains) & cg.isin(groups)


def row_in_headline_scope(row, chains: frozenset[str], groups: frozenset[str]) -> bool:
    chain = row.get("chain")
    cg = row.get("calc_group")
    if chain is None or cg is None or (isinstance(chain, float) and pd.isna(chain)):
        return False
    if isinstance(cg, float) and pd.isna(cg):
        return False
    return str(chain).strip().lower() in chains and str(cg).strip().lower() in groups


def filter_panel(panel: pd.DataFrame, inputs: dict) -> pd.DataFrame:
    chains, groups = headline_scope_sets(inputs)
    out = panel.loc[scope_mask(panel, chains, groups)].copy()
    if not len(out):
        raise ValueError("Headline-scope emissions panel is empty.")
    return out


def headline_sample(
    by_project: pd.DataFrame,
    scenario: str = DEFAULT_SCENARIO,
) -> pd.DataFrame:
    if "in_headline_scope" not in by_project.columns:
        raise KeyError("by_project is missing in_headline_scope.")
    return by_project.loc[
        by_project["in_headline_scope"] & (by_project["scenario"] == scenario)
    ].copy()


BUILD_OUTS = ("committed", "committed_plus_advanced", "full")
BUILD_OUT_LABEL = {
    "committed": "committed (operating + under construction)",
    "committed_plus_advanced": "committed plus advanced (+ tier advanced_proposed)",
    "full": "full (every headline-scope asset)",
}


def build_out_project_ids(inputs: dict) -> dict[str, list[str]]:
    """Headline-scope project ids for each build-out.

    Same membership as `src.monte_carlo.BUILD_OUTS`, kept here so the
    central case and the Monte Carlo cannot drift apart.
    """
    chains, groups = headline_scope_sets(inputs)
    committed, advanced, full = [], [], []
    for _, row in inputs["assets"].iterrows():
        if pd.isna(row["capacity_mtpa"]):
            continue
        if not row_in_headline_scope(row, chains, groups):
            continue
        pid = str(row["project_id"])
        cg = str(row["calc_group"]).strip().lower()
        tier = "" if pd.isna(row["tier"]) else str(row["tier"]).strip()
        full.append(pid)
        if cg in ("operating", "under_construction"):
            committed.append(pid)
            advanced.append(pid)
        elif tier == "advanced_proposed":
            advanced.append(pid)
    return {
        "committed": committed,
        "committed_plus_advanced": advanced,
        "full": full,
    }


def exclusion_report(
    by_project: pd.DataFrame,
    panel_all: pd.DataFrame,
    inputs: dict,
    scenario: str = DEFAULT_SCENARIO,
) -> dict:
    """Stated exclusion: in-total assets outside the headline class filter."""
    from src.trajectories import panel_by_project, panel_lifetime_mt, panel_peak

    chains, groups = headline_scope_sets(inputs)
    full = by_project.loc[
        (~by_project["excluded_from_totals"]) & (by_project["scenario"] == scenario)
    ].copy()
    full["in_headline_scope"] = scope_mask(full, chains, groups)
    excluded = full.loc[~full["in_headline_scope"]].copy()
    proj_life = panel_by_project(panel_all)
    life_def = proj_life.loc[proj_life["scenario"] == scenario][
        ["project_id", "lifetime_mtco2e"]
    ]
    excluded = excluded.merge(life_def, on="project_id", how="left")
    excluded["lifetime_mtco2e"] = excluded["lifetime_mtco2e"].fillna(0.0)
    peak_year, _ = panel_peak(panel_all, scenario)
    peak_slice = panel_all.loc[
        (panel_all["scenario"] == scenario) & (panel_all["year"] == peak_year)
    ]
    peak_by = peak_slice.groupby("project_id")["emissions_mtco2e"].sum()
    excluded["peak_year_mtco2e"] = excluded["project_id"].map(peak_by).fillna(0.0)
    all_life = panel_lifetime_mt(panel_all, scenario)
    excluded_life = float(excluded["lifetime_mtco2e"].sum())
    table = excluded[
        [
            "project_id",
            "project_name",
            "chain",
            "calc_group",
            "first_export_year",
            "capacity_mtpa",
            "is_legacy",
            "lifetime_mtco2e",
            "peak_year_mtco2e",
        ]
    ].sort_values("lifetime_mtco2e", ascending=False)
    by_chain = (
        excluded.groupby("chain", sort=False)
        .agg(
            n=("project_id", "nunique"),
            capacity_mtpa=("capacity_mtpa", "sum"),
            lifetime_mtco2e=("lifetime_mtco2e", "sum"),
            peak_year_mtco2e=("peak_year_mtco2e", "sum"),
        )
        .reset_index()
    )
    already_out = by_project.loc[
        by_project["excluded_from_totals"] & (by_project["scenario"] == scenario),
        "project_id",
    ].unique().tolist()
    return {
        "rule": SCOPE_RULE_ONE_LINE,
        "chains": ",".join(sorted(chains)),
        "calc_groups": ",".join(sorted(groups)),
        "n_excluded": int(excluded["project_id"].nunique()),
        "lifetime_mt": excluded_life,
        "share_of_all_assets_pct": (
            100.0 * excluded_life / all_life if all_life else 0.0
        ),
        "peak_year": int(peak_year),
        "peak_mt": float(excluded["peak_year_mtco2e"].sum()),
        "table": table,
        "by_chain": by_chain,
        "already_out_of_totals": already_out,
        "all_assets_lifetime_mt": all_life,
    }
