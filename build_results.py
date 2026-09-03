"""Orchestrate lifecycle emissions build. Writes Outputs/ only — never Inputs/."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.inputs import (
    ALL_STAGES,
    DEFAULT_SCENARIO,
    EXPECTED_CHAIN_LENGTHS,
    INTENSITY_SCENARIOS,
    get_param,
    load_inputs,
)
from src.figures_report import build_all_report_figures
from src.slide_tables import build_slide_tables, write_slide_tables_xlsx
from src.benchmark_table import build_benchmark_table, format_benchmark_markdown
from src.si_table import build_si_asset_table, format_si_table_markdown
from src.drive_sensitivity import (
    format_drive_markdown,
    run_drive_sensitivity,
)
from src.feedgas_sensitivity import (
    format_feedgas_markdown,
    run_kino_aski_feedgas_sensitivity,
)
from src.lifespan_sensitivity import (
    format_uniform_life_markdown,
    run_uniform_life_sensitivity,
)
from src.placeholder_sensitivity import (
    format_placeholder_markdown,
    run_placeholder_start_sensitivity,
)
from src.loss_damage import compute_loss_damage, format_ld_markdown, write_ld_figure
from src.monte_carlo import format_mc_markdown, run_monte_carlo
from src.lca_comparison import figure_10_lca_comparison, format_lca_markdown
from src.scope import (
    BUILD_OUT_LABEL,
    BUILD_OUTS,
    SCOPE_RULE_ONE_LINE,
    build_out_project_ids,
    exclusion_report,
    filter_panel,
    headline_sample,
    headline_scope_sets,
)
from src.trajectories import (
    PANEL_START_YEAR,
    build_emissions_panel,
    gwp20_reconciliation,
    panel_by_project,
    panel_gas_totals,
    panel_lifetime_mt,
    panel_n_emitting,
    panel_peak,
)
from src.banners import stale_banners
from src.model import (
    CHAINS,
    GROUPS,
    _licence_end_year,
    _lifespan,
    assert_no_cross_chain_capacity_sum,
    assumptions_used,
    by_stage,
    carbon_budget_shares,
    compute_by_project,
    electrification_counterfactual,
    summarise,
    summarise_by_chain,
    territorial_table,
)

ROOT = Path(__file__).resolve().parent
REGISTER = ROOT / "Inputs" / "Canada_LNG_Asset_Register.xlsx"
INPUTS = ROOT / "Inputs" / "Canada_LNG_Data_Inputs.xlsx"
INPUTS_DIR = ROOT / "Inputs"
OUT = ROOT / "Outputs"
RESULTS = OUT / "Canada_LNG_Emissions_Results.xlsx"
SLIDE_TABLES = OUT / "SLIDE_TABLES.xlsx"
SI_TABLE_CSV = OUT / "si_table_assets.csv"
BENCHMARK_CSV = OUT / "benchmark_comparison.csv"
SUMMARY_MD = OUT / "RESULTS_SUMMARY.md"
FIGURE_DIR = OUT / "figures"
FIGURE_DATA = OUT / "figure_data"
PAPER_SET_CSV = OUT / "figure_data" / "paper_set.csv"
# Canonical, rounded copy of the paper set. Its SHA-256 is asserted below, so
# a re-run that moves any published digit fails loudly instead of quietly
# republishing. Rounded to the published precision on purpose: the hash should
# track paper numbers, not float noise in the last bits.
PAPER_SET_LOCKED_CSV = OUT / "paper_set_locked.csv"

# Snapshot before the August 2026 register/electrification revision.
BEFORE = {
    "annual_mt": 159.2,
    "lifecycle_mt": 6196.7,
    "export_mtpa": 58.1,
    "liquefaction_mt": 8.0,
    "early_export_mtpa": 12.7,
    "group_annual": {
        "operating": 43.3,
        "under_construction": 15.0,
        "proposed": 100.9,
    },
    "chain_annual": {
        "export": 150.0,
        "bunkering": 7.8,
        "domestic": 0.9,
        "import": 0.5,
    },
}
EXPECTED_EXPORT_BY_CALC = {
    "operating": 14.0,
    "under_construction": 5.4,
    "proposed": 60.7,
}
EXPECTED_EXPORT_TOTAL = 80.1
EXPECTED_EARLY_EXPORT = 34.7
EXPECTED_ADVANCED_EXPORT = 26.0
# Life-average territorial shares, one decimal. Tied to the Data Inputs README
# and the repo README so those documents cannot drift from the model.
# Lock history:
#   all assets:          CAN 18.5 / BUNK 5.6 / FOR 75.9; lifetime 9558.2; peak 309.1 (2037)
#   export-scope filter: CAN 18.0 / BUNK 3.4 / FOR 78.6; lifetime 9315.3; peak 298.7 (2037)
#   route-scaled shipping: CAN 18.1 / BUNK 3.2 / FOR 78.7; lifetime 9298.1; peak 298.2 (2037)
#   Discovery returned to cancelled (1 Sep 2026): CAN 18.1 / BUNK 3.2 / FOR 78.8;
#   lifetime 7254.2; peak 238.6 (2037). Discovery was 20 mtpa / 2,043.9 Mt.
#   Regasification 0.04 -> 0.021 (3 Sep 2026): CAN 18.2 / BUNK 3.2 / FOR 78.6;
#   lifetime 7215.3; peak 237.3 (2037).
#   Pipeline 0.10 -> 0.074 (3 Sep 2026): CAN 17.6 / BUNK 3.2 / FOR 79.2;
#   lifetime 7162.0; peak 235.6 (2037).
#   upstream_ch4_share 0.30 -> 0.25 (3 Sep 2026): lifetime, peak and the
#   territorial split are ALL UNCHANGED - the share only moves the CO2/CH4
#   split and the SC-CH4 damages line. Values below. The old 0.10 was assumed
#   and about 35% above two independent cited routes (Liu et al. 2021 via the
#   ERA restatement, 0.0735; CER/NIR 2019 pipeline transport, 0.0744). Pipeline
#   is CAN-tagged, so cutting it moves weight from CAN to FOR.
EXPECTED_TERRITORIAL_SHARE_PCT = {"CAN": 17.6, "BUNK": 3.2, "FOR": 79.2}
EXPECTED_LIFETIME_MT = 7162.0
EXPECTED_PEAK_YEAR = 2037
EXPECTED_PEAK_MT = 235.6

# The paper set, locked 3 September 2026 (Discovery cancelled; GWP20 methane-
# only; Monte Carlo triangles read from the workbooks; regasification and the
# combustion range bounds moved onto cited values; pipeline moved onto two
# converging cited routes). The paper reports the central
# case — the point estimate from the central factor values — with the Monte
# Carlo 5th to 95th percentile as its interval. The MC median is stated once,
# with the reason it sits above the central: the stage triangles are
# right-skewed, shipping 0.05 / 0.12 / 0.31 especially.
#
# One decimal on Mt, whole CAD bn. `full` duplicates EXPECTED_LIFETIME_MT /
# EXPECTED_PEAK_MT / EXPECTED_PEAK_YEAR on purpose: the two locks must agree.
# SHA-256 of Outputs/paper_set_locked.csv, the rounded canonical copy of the
# paper set. Re-lock it in the same commit as EXPECTED_BUILD_OUT, never alone.
EXPECTED_PAPER_SET_SHA256 = (
    "fd506c3a1cd8187d546a3a551719834f965d3167c4c55c4d7e0ca6bd0b0bbae6"
)

# Figure 10's model well-to-regasification intensity, GWP100, two decimals.
# Locked 3 September 2026 so the Roman-White gap document's generated banner
# rests on an asserted value, not a figure key nobody checks.
EXPECTED_WELL_TO_REGAS_T_PER_T = 0.76

EXPECTED_BUILD_OUT = {
    "committed": {
        "lifetime_mt": 1845.8,
        "lifetime_co2_only_mt": 1781.7,
        "peak_year": 2030,
        "peak_mt": 57.6,
        "damages_cad_bn": 741,
    },
    "committed_plus_advanced": {
        "lifetime_mt": 3757.5,
        "lifetime_co2_only_mt": 3627.1,
        "peak_year": 2037,
        "peak_mt": 134.0,
        "damages_cad_bn": 1561,
    },
    "full": {
        "lifetime_mt": 7162.0,
        "lifetime_co2_only_mt": 6918.1,
        "peak_year": 2037,
        "peak_mt": 235.6,
        "damages_cad_bn": 3108,
    },
}


def current_lock() -> dict:
    """The locked values as one dict, for the generated banners on the dated
    documents (src/banners.py). Built from the EXPECTED_* constants above so a
    banner can only ever say what the run asserts."""
    return {
        "lifetime_mt": EXPECTED_LIFETIME_MT,
        "peak_mt": EXPECTED_PEAK_MT,
        "peak_year": EXPECTED_PEAK_YEAR,
        "territorial_pct": dict(EXPECTED_TERRITORIAL_SHARE_PCT),
        "damages_cad_bn": EXPECTED_BUILD_OUT["full"]["damages_cad_bn"],
        "export_mtpa": EXPECTED_EXPORT_TOTAL,
        "well_to_regas_t_per_t": EXPECTED_WELL_TO_REGAS_T_PER_T,
    }


def gas_split_table(panel: pd.DataFrame, inputs: dict) -> pd.DataFrame:
    """Lifetime CO2e, CO2-only and CH4 mass by build-out and by calc_group."""
    ids = build_out_project_ids(inputs)
    rows = []
    for name in BUILD_OUTS:
        rows.append({
            "slice": "build_out",
            "key": name,
            "membership": BUILD_OUT_LABEL[name],
            "n_assets": len(ids[name]),
            **panel_gas_totals(panel, DEFAULT_SCENARIO, project_ids=ids[name]),
        })
    for group in GROUPS:
        sl = panel.loc[
            (panel["scenario"] == DEFAULT_SCENARIO) & (panel["calc_group"] == group)
        ]
        rows.append({
            "slice": "calc_group",
            "key": group,
            "membership": f"calc_group={group}",
            "n_assets": int(sl["project_id"].nunique()),
            **panel_gas_totals(panel, DEFAULT_SCENARIO, calc_group=group),
        })
    df = pd.DataFrame(rows)
    df["ch4_share_of_co2e_pct"] = (
        100.0 * df["lifetime_ch4_derived_co2e_mt"] / df["lifetime_mtco2e"]
    )
    df["scenario"] = DEFAULT_SCENARIO
    df["split_note"] = (
        "CH4-derived CO2e is upstream (scenario factor less inventory CO2) plus "
        "shipping methane slip (1 - 1/1.44). Pipeline fugitives are not split; "
        "liquefaction, regasification and combustion are treated as CO2."
    )
    return df


PAPER_SET_LOCKED_COLUMNS = (
    ("build_out", None),
    ("n_assets", None),
    ("lifetime_mtco2e", 1),
    ("lifetime_mtco2e_p05", 1),
    ("lifetime_mtco2e_p95", 1),
    ("lifetime_mtco2e_mc_median", 1),
    ("lifetime_co2_only_mt", 1),
    ("lifetime_co2_only_mt_p05", 1),
    ("lifetime_co2_only_mt_p95", 1),
    ("lifetime_ch4_kt", 0),
    ("peak_year", None),
    ("peak_mtco2e_yr", 1),
    ("peak_mtco2e_yr_p05", 1),
    ("peak_mtco2e_yr_p95", 1),
    ("eccc_2pct_damages_cad_bn", 0),
    ("eccc_2pct_damages_cad_bn_p05", 0),
    ("eccc_2pct_damages_cad_bn_p95", 0),
    ("canada_territorial_pct", 1),
    ("international_bunkers_pct", 1),
    ("foreign_territorial_pct", 1),
    ("share_of_remaining_15c_budget_pct", 2),
    ("share_of_remaining_17c_budget_pct", 2),
    ("share_of_remaining_2c_budget_pct", 2),
)


def write_paper_set_locked(paper_set: pd.DataFrame, path: Path) -> str:
    """Write the rounded paper set and return its SHA-256."""
    out = pd.DataFrame()
    for col, places in PAPER_SET_LOCKED_COLUMNS:
        series = paper_set[col]
        out[col] = series if places is None else series.astype(float).round(places)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = out.to_csv(index=False, lineterminator=chr(10))
    path.write_text(text, encoding="utf-8", newline="")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def paper_set_table(
    panel: pd.DataFrame,
    ld: dict,
    mc: dict,
    inputs: dict,
    by_project: pd.DataFrame,
) -> pd.DataFrame:
    """The paper set: central case per build-out, with the MC interval beside it.

    Central is the point estimate from the central factor values. The interval
    is the Monte Carlo 5th to 95th percentile. The MC median is carried in its
    own column and is not the reported figure.
    """
    ids = build_out_project_ids(inputs)
    summ = mc["summary"]
    bp = ld["by_project"]
    eccc = bp.loc[
        (bp["price_family"] == "eccc")
        & (bp["discount_rate_pct"] == ld["eccc_r"])
    ]
    sample = headline_sample(by_project, DEFAULT_SCENARIO)
    params = inputs["params"]

    def _mc(name: str, metric: str) -> tuple[float, float, float]:
        r = summ.loc[(summ["build_out"] == name) & (summ["metric"] == metric)]
        if not len(r):
            return (float("nan"),) * 3
        r = r.iloc[0]
        return float(r["median"]), float(r["p05"]), float(r["p95"])

    rows = []
    for name in BUILD_OUTS:
        members = ids[name]
        gas = panel_gas_totals(panel, DEFAULT_SCENARIO, project_ids=members)
        slice_panel = panel.loc[panel["project_id"].isin(members)]
        peak_year, peak_mt = panel_peak(slice_panel, DEFAULT_SCENARIO)
        damages_bn = float(
            eccc.loc[eccc["project_id"].isin(members), "hatton_sum_cad"].sum()
        ) / 1e9
        sl = sample.loc[sample["project_id"].isin(members)]
        terr_total = float(sl["annual_total"].sum())
        budgets = carbon_budget_shares(
            gas["lifetime_mtco2e"], params, gas["lifetime_co2_only_mt"]
        )
        life_med, life_lo, life_hi = _mc(name, "lifetime_mtco2e")
        co2_med, co2_lo, co2_hi = _mc(name, "lifetime_co2_only_mt")
        peak_med, peak_lo, peak_hi = _mc(name, "peak_mtco2e_yr")
        dmg_med, dmg_lo, dmg_hi = _mc(name, "central_damage_cad_billion")
        rows.append({
            "build_out": name,
            "membership": BUILD_OUT_LABEL[name],
            "n_assets": len(members),
            "lifetime_mtco2e": gas["lifetime_mtco2e"],
            "lifetime_mtco2e_p05": life_lo,
            "lifetime_mtco2e_p95": life_hi,
            "lifetime_mtco2e_mc_median": life_med,
            "lifetime_co2_only_mt": gas["lifetime_co2_only_mt"],
            "lifetime_co2_only_mt_p05": co2_lo,
            "lifetime_co2_only_mt_p95": co2_hi,
            "lifetime_co2_only_mt_mc_median": co2_med,
            "lifetime_ch4_kt": gas["lifetime_ch4_kt"],
            "peak_year": int(peak_year),
            "peak_mtco2e_yr": peak_mt,
            "peak_mtco2e_yr_p05": peak_lo,
            "peak_mtco2e_yr_p95": peak_hi,
            "peak_mtco2e_yr_mc_median": peak_med,
            "eccc_2pct_damages_cad_bn": damages_bn,
            "eccc_2pct_damages_cad_bn_p05": dmg_lo,
            "eccc_2pct_damages_cad_bn_p95": dmg_hi,
            "eccc_2pct_damages_cad_bn_mc_median": dmg_med,
            "canada_territorial_pct": (
                100.0 * float(sl["canada_territorial"].sum()) / terr_total
                if terr_total else float("nan")
            ),
            "international_bunkers_pct": (
                100.0 * float(sl["international_bunkers"].sum()) / terr_total
                if terr_total else float("nan")
            ),
            "foreign_territorial_pct": (
                100.0 * float(sl["foreign_territorial"].sum()) / terr_total
                if terr_total else float("nan")
            ),
            **{
                f"share_of_{r.parameter}_pct": r.share_pct
                for r in budgets.itertuples()
            },
            "central_basis": "point estimate from central factor values",
            "interval_basis": (
                f"Monte Carlo p5-p95, {mc['n_draws']} draws, seed {mc['seed']}"
            ),
        })
    return pd.DataFrame(rows)


def write_review_summary(
    path: Path,
    inputs: dict,
    by_project: pd.DataFrame,
    summary: pd.DataFrame,
    by_chain: pd.DataFrame,
    stages: pd.DataFrame,
    panel: pd.DataFrame,
    ld: dict | None = None,
    placeholder_sens: dict | None = None,
    mc: dict | None = None,
    lca: dict | None = None,
    exclusion: dict | None = None,
    gas_split: pd.DataFrame | None = None,
    gwp20_rec: dict | None = None,
    paper_set: pd.DataFrame | None = None,
    uniform_life: dict | None = None,
    feedgas: dict | None = None,
    drive_sens: dict | None = None,
    si_assets: pd.DataFrame | None = None,
    benchmark: pd.DataFrame | None = None,
) -> None:
    sample = headline_sample(by_project, DEFAULT_SCENARIO)
    params = inputs["params"]
    national = float(get_param(params, "canada_national_emissions"))
    t_low = float(get_param(params, "canada_2030_target_low"))
    t_high = float(get_param(params, "canada_2030_target_high"))
    gap = float(get_param(params, "canada_2030_overshoot_gap"))

    annual = float(sample["annual_total"].sum()) / 1e6
    lifecycle = panel_lifetime_mt(panel, DEFAULT_SCENARIO)
    peak_year, peak_mt = panel_peak(panel, DEFAULT_SCENARIO)
    panel_year0 = int(panel.loc[panel["scenario"] == DEFAULT_SCENARIO, "year"].min())
    panel_year1 = int(panel.loc[panel["scenario"] == DEFAULT_SCENARIO, "year"].max())
    project_life = panel_by_project(panel)
    project_life_def = project_life.loc[project_life["scenario"] == DEFAULT_SCENARIO]
    s12 = float(sample["scope_1_2"].sum()) / 1e6
    s3 = float(sample["scope_3"].sum()) / 1e6
    can = float(sample["canada_territorial"].sum()) / 1e6
    bunk = float(sample["international_bunkers"].sum()) / 1e6
    foreign = float(sample["foreign_territorial"].sum()) / 1e6
    export_cap = float(sample.loc[sample["chain"] == "export", "capacity_mtpa"].sum())

    lines = []
    lines.append("# Canada LNG lifecycle emissions — review summary")
    lines.append("")
    lines.append(
        f"Default scenario: `{DEFAULT_SCENARIO}`. "
        f"Run at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}. "
        "Numbers to one decimal. Inputs read-only. "
        f"`calc_group` from `{inputs['calc_group_source']}`."
    )
    lines.append("")
    lines.append(
        "Deck-facing tables (one sheet per table, 1-decimal): "
        "`Outputs/SLIDE_TABLES.xlsx`. Send that workbook to the PPT chat."
    )
    lines.append("")

    # 0 Paper set
    if paper_set is not None:
        lines.append("## Paper set")
        lines.append("")
        lines.append(
            "Decision taken 29 August 2026. The paper reports the **central "
            "case** — the point estimate from the central factor values — with "
            "the Monte Carlo **5th to 95th percentile** as its interval. The "
            "Monte Carlo median is stated once, in its own column, and is not "
            "the reported figure."
        )
        lines.append("")
        lines.append(
            "| build-out | lifetime CO2e Mt | lifetime CO2-only Mt | "
            "peak | ECCC 2% damages CAD bn | MC median (lifetime / peak / "
            "damages)\u00b9 |"
        )
        lines.append("|---|---|---|---|---|---|")
        for _, r in paper_set.iterrows():
            lines.append(
                f"| {r['build_out']} | "
                f"**{r['lifetime_mtco2e']:,.1f}** "
                f"[{r['lifetime_mtco2e_p05']:,.1f}, "
                f"{r['lifetime_mtco2e_p95']:,.1f}] | "
                f"**{r['lifetime_co2_only_mt']:,.1f}** "
                f"[{r['lifetime_co2_only_mt_p05']:,.1f}, "
                f"{r['lifetime_co2_only_mt_p95']:,.1f}] | "
                f"**{r['peak_mtco2e_yr']:,.1f}** in {int(r['peak_year'])} "
                f"[{r['peak_mtco2e_yr_p05']:,.1f}, "
                f"{r['peak_mtco2e_yr_p95']:,.1f}] | "
                f"**{r['eccc_2pct_damages_cad_bn']:,.0f}** "
                f"[{r['eccc_2pct_damages_cad_bn_p05']:,.0f}, "
                f"{r['eccc_2pct_damages_cad_bn_p95']:,.0f}] | "
                f"{r['lifetime_mtco2e_mc_median']:,.1f} / "
                f"{r['peak_mtco2e_yr_mc_median']:,.1f} / "
                f"{r['eccc_2pct_damages_cad_bn_mc_median']:,.0f} |"
            )
        lines.append("")
        full_ps = paper_set.loc[paper_set["build_out"] == "full"].iloc[0]
        lines.append(
            f"\u00b9 The Monte Carlo median sits **above** the central case "
            f"({full_ps['lifetime_mtco2e_mc_median']:,.1f} against "
            f"{full_ps['lifetime_mtco2e']:,.1f} Mt at full buildout) because "
            f"the sampled stage triangles are right-skewed — shipping "
            f"0.05 / 0.12 / 0.31 especially, where the central 0.12 sits well "
            f"below the midpoint of the range. The median of a right-skewed "
            f"draw is not the point estimate from central values. Both are "
            f"reported; only the central case is the paper's number."
        )
        lines.append("")
        lines.append(
            "Membership: "
            + "; ".join(
                f"**{r['build_out']}** = {r['membership']} ({int(r['n_assets'])} assets)"
                for _, r in paper_set.iterrows()
            )
            + ". Interval basis: "
            + str(paper_set.iloc[0]["interval_basis"])
            + "."
        )
        lines.append("")
        lines.append("### Territorial split and carbon-budget shares")
        lines.append("")
        lines.append(
            "Territorial shares are the life-average split. Budget shares are "
            "the **CO2-only** lifetime against the GCB 2025 remaining CO2 "
            "budgets from the start of 2026, like for like."
        )
        lines.append("")
        lines.append(
            "| build-out | CAN % | BUNK % | FOR % | 1.5\u00b0C (170 GtCO2) | "
            "1.7\u00b0C (525) | 2.0\u00b0C (1,055) |"
        )
        lines.append("|---|---|---|---|---|---|---|")
        for _, r in paper_set.iterrows():
            lines.append(
                f"| {r['build_out']} | {r['canada_territorial_pct']:.1f} | "
                f"{r['international_bunkers_pct']:.1f} | "
                f"{r['foreign_territorial_pct']:.1f} | "
                f"{r['share_of_remaining_15c_budget_pct']:.2f}% | "
                f"{r['share_of_remaining_17c_budget_pct']:.2f}% | "
                f"{r['share_of_remaining_2c_budget_pct']:.2f}% |"
            )
        lines.append("")
        lines.append(
            "Locked in `build_results.py` as `EXPECTED_BUILD_OUT`; the run "
            "asserts every cell of the central column. Machine-readable copy: "
            "`Outputs/figure_data/paper_set.csv`."
        )
        lines.append("")

    # 1 Headline
    lines.append("## 1. Headline")
    lines.append("")
    peak_n = panel_n_emitting(panel, peak_year, DEFAULT_SCENARIO)
    lines.append(
        f"- **Annual total (panel peak):** {peak_mt:.1f} MtCO2e in {peak_year} "
        f"({peak_n} assets emitting that year)"
    )
    lines.append(
        f"- **life_average_annual_mt:** {annual:.1f} MtCO2e/yr "
        "(mean utilisation over each asset's operating window; not a calendar year)"
    )
    lines.append(
        f"- **Lifetime total (calendar panel {panel_year0}–{panel_year1}):** "
        f"{lifecycle:.1f} MtCO2e (headline scope; remaining years from "
        f"{PANEL_START_YEAR}, not duration × life-average)"
    )
    lines.append(
        f"- **Headline capacity (export chain only):** {export_cap:.1f} mtpa "
        "(liquefaction; not summed with import regasification or other chains)"
    )
    if exclusion is not None:
        lines.append(
            f"- **Scope:** {SCOPE_RULE_ONE_LINE} "
            f"Excluded {exclusion['n_excluded']} in-total non-export assets totalling "
            f"{exclusion['lifetime_mt']:.1f} MtCO2e on the full-register panel "
            f"({exclusion['share_of_all_assets_pct']:.1f}% of the all-assets "
            f"{exclusion['all_assets_lifetime_mt']:.1f} Mt). "
            "They remain in the register."
        )
    lines.append("")
    lines.append("| chain | mtpa |")
    lines.append("|---|---|")
    for chain in CHAINS:
        cap = float(sample.loc[sample["chain"] == chain, "capacity_mtpa"].sum())
        if cap == 0:
            continue
        lines.append(f"| {chain} | {cap:.1f} |")
    lines.append("")
    lines.append(
        f"- **Scope 1+2:** {s12:.1f} MtCO2e/yr ({s12/annual*100:.1f}%)  |  "
        f"**Scope 3:** {s3:.1f} MtCO2e/yr ({s3/annual*100:.1f}%)"
    )
    lines.append(
        f"- **Territorial:** CAN {can:.1f} ({can/annual*100:.1f}%)  |  "
        f"BUNK {bunk:.1f} ({bunk/annual*100:.1f}%)  |  "
        f"FOR {foreign:.1f} ({foreign/annual*100:.1f}%)"
    )
    lifetime_co2_only = panel_gas_totals(panel, DEFAULT_SCENARIO)[
        "lifetime_co2_only_mt"
    ]
    budgets = carbon_budget_shares(lifecycle, params, lifetime_co2_only)
    lines.append(
        f"- **Share of remaining carbon budget (GCB 2025, from start of 2026), "
        f"on the CO2-only lifetime of {lifetime_co2_only:,.1f} MtCO2:** "
        + "  |  ".join(
            f"{r.label} {r.share_pct:.1f}% of {r.budget_gtco2:g} GtCO2"
            for r in budgets.itertuples()
        )
        + f". This is **like for like**: CO2 against a CO2 budget. "
        f"Residual caveats: pipeline fugitive methane is not split out of the "
        f"CO2 total, and non-CO2 gases other than CH4 are not counted. "
        f"On the older GWP100 CO2e basis the same shares are "
        + "  |  ".join(
            f"{r.share_co2e_pct:.1f}%" for r in budgets.itertuples()
        )
        + "."
    )
    lines.append("")

    # 2 By group
    lines.append("## 2. By group")
    lines.append("")
    lines.append(
        "| calc_group | export mtpa | life_average_annual_mt | Lifecycle Mt | "
        "CAN / BUNK / FOR Mt/yr |"
    )
    lines.append("|---|---|---|---|---|")
    sdef = summary.loc[summary["scenario"] == DEFAULT_SCENARIO]
    for g in GROUPS:
        r = sdef.loc[sdef["group"] == g]
        if not len(r):
            continue
        r = r.iloc[0]
        if r["annual_total_mtco2e_yr"] == 0 and r["capacity_export_headline_mtpa"] == 0:
            continue
        glife = panel_lifetime_mt(panel, DEFAULT_SCENARIO, calc_group=g)
        lines.append(
            f"| {g} | {r['capacity_export_headline_mtpa']:.1f} | "
            f"{r['annual_total_mtco2e_yr']:.1f} | {glife:.1f} | "
            f"{r['canada_territorial_mtco2e_yr']:.1f} / "
            f"{r['international_bunkers_mtco2e_yr']:.1f} / "
            f"{r['foreign_territorial_mtco2e_yr']:.1f} |"
        )
    lines.append("")
    lines.append("Capacity by chain within each calc_group (not summed across chains):")
    lines.append("")
    lines.append("| calc_group | export | bunkering | domestic | import |")
    lines.append("|---|---|---|---|---|")
    for g in GROUPS:
        r = sdef.loc[sdef["group"] == g]
        if not len(r):
            continue
        r = r.iloc[0]
        lines.append(
            f"| {g} | {r['capacity_export_mtpa']:.1f} | "
            f"{r['capacity_bunkering_mtpa']:.1f} | "
            f"{r['capacity_domestic_mtpa']:.1f} | "
            f"{r['capacity_import_mtpa']:.1f} |"
        )
    lines.append("")
    lines.append("### Proposed: advanced vs early (tier split)")
    lines.append("")
    lines.append(
        "| tier | chain scope | mtpa | life_average_annual_mt | CAN / BUNK / FOR |"
    )
    lines.append("|---|---|---|---|---|")
    prop = sample.loc[sample["calc_group"] == "proposed"]
    for tier in ("advanced_proposed", "early_proposed"):
        g = prop.loc[prop["tier"] == tier]
        if not len(g):
            continue
        # Emissions for all chains in the tier; capacity reported per chain only.
        for chain in CHAINS:
            gc = g.loc[g["chain"] == chain]
            if not len(gc):
                continue
            lines.append(
                f"| {tier} | {chain} | {float(gc['capacity_mtpa'].sum()):.1f} | "
                f"{float(gc['annual_total'].sum())/1e6:.1f} | "
                f"{float(gc['canada_territorial'].sum())/1e6:.1f} / "
                f"{float(gc['international_bunkers'].sum())/1e6:.1f} / "
                f"{float(gc['foreign_territorial'].sum())/1e6:.1f} |"
            )
    lines.append("")

    # 3 By chain
    lines.append("## 3. By chain")
    lines.append("")
    chain_stages = {
        c: " → ".join(f"{s}@{w}" for s, w in inputs["chains"][c])
        for c in CHAINS
    }
    lines.append(
        "| chain | stages | mtpa | life_average_annual_mt | Lifecycle Mt | CAN / BUNK / FOR |"
    )
    lines.append("|---|---|---|---|---|---|")
    cdef = by_chain.loc[by_chain["scenario"] == DEFAULT_SCENARIO]
    for chain in CHAINS:
        r = cdef.loc[cdef["chain"] == chain].iloc[0]
        if float(r["capacity_mtpa"]) == 0 and float(r["annual_total_mtco2e_yr"]) == 0:
            continue
        clife = panel_lifetime_mt(panel, DEFAULT_SCENARIO, chain=chain)
        lines.append(
            f"| {chain} | {chain_stages[chain]} | {r['capacity_mtpa']:.1f} | "
            f"{r['annual_total_mtco2e_yr']:.1f} | {clife:.1f} | "
            f"{r['canada_territorial_mtco2e_yr']:.1f} / "
            f"{r['international_bunkers_mtco2e_yr']:.1f} / "
            f"{r['foreign_territorial_mtco2e_yr']:.1f} |"
        )
    lines.append("")

    # 4 By project
    lines.append("## 4. By project")
    lines.append("")
    lines.append(
        "| project | mtpa | chain | calc_group | tier | drive | life (source) | "
        "effective Mt/yr | annual Mt/yr | lifecycle Mt | CAN / BUNK / FOR | notes |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for _, r in sample.sort_values(["calc_group", "chain", "project_id"]).iterrows():
        drive = r["liquefaction_drive"] if pd.notna(r["liquefaction_drive"]) else "—"
        pl = project_life_def.loc[project_life_def["project_id"] == r["project_id"]]
        if r["is_legacy"] or not len(pl):
            life_tot = "—"
        else:
            life_tot = f"{float(pl.iloc[0]['lifetime_mtco2e']):.1f}"
        note = (
            "legacy: outlived nominal design life; steady-state util; annual only"
            if r["is_legacy"]
            else ""
        )
        lines.append(
            f"| {r['project_id']} | {r['capacity_mtpa']:.1f} | {r['chain']} | "
            f"{r['calc_group']} | {r['tier']} | {drive} | "
            f"{int(r['lifespan_years'])} ({r['lifespan_source']}) | "
            f"{r['effective_tonnes']/1e6:.2f} | {r['annual_total']/1e6:.1f} | "
            f"{life_tot} | "
            f"{r['canada_territorial']/1e6:.1f} / "
            f"{r['international_bunkers']/1e6:.1f} / "
            f"{r['foreign_territorial']/1e6:.1f} | {note} |"
        )
    lines.append("")

    if exclusion is not None:
        lines.append("## Headline exclusion (retained in the register)")
        lines.append("")
        lines.append(
            f"{SCOPE_RULE_ONE_LINE} Combined excluded tonnage: "
            f"**{exclusion['lifetime_mt']:.1f} MtCO2e** "
            f"({exclusion['n_excluded']} in-total assets; "
            f"{exclusion['peak_mt']:.1f} Mt in the all-assets peak year "
            f"{exclusion['peak_year']}). Already out of totals: "
            f"{exclusion['already_out_of_totals'] or 'none'}."
        )
        lines.append("")
        lines.append(
            "| project | chain | calc_group | start | mtpa | lifetime Mt | "
            "legacy |"
        )
        lines.append("|---|---|---|---:|---:|---:|---|")
        for _, r in exclusion["table"].iterrows():
            start = (
                "—"
                if pd.isna(r["first_export_year"])
                else str(int(r["first_export_year"]))
            )
            lines.append(
                f"| {r['project_id']} | {r['chain']} | {r['calc_group']} | "
                f"{start} | {r['capacity_mtpa']:.2f} | "
                f"{r['lifetime_mtco2e']:.1f} | "
                f"{'yes' if r['is_legacy'] else ''} |"
            )
        lines.append("")
        lines.append("| chain | n | mtpa | lifetime Mt |")
        lines.append("|---|---:|---:|---:|")
        for _, r in exclusion["by_chain"].iterrows():
            lines.append(
                f"| {r['chain']} | {int(r['n'])} | {r['capacity_mtpa']:.1f} | "
                f"{r['lifetime_mtco2e']:.1f} |"
            )
        lines.append("")

    # 5 By stage
    lines.append("## 5. By stage")
    lines.append("")
    lines.append("| stage | destination | life_average_annual_mt | share |")
    lines.append("|---|---|---|---|")
    for _, r in stages.iterrows():
        share = r["share_of_total"] * 100 if r["share_of_total"] is not None else 0
        lines.append(
            f"| {r['stage']} | {r['territorial_destination']} | "
            f"{r['annual_mtco2e_yr']:.1f} | {share:.1f}% |"
        )
    lines.append("")

    # 5a CO2 / CH4 split
    if gas_split is not None:
        lines.append("## 5a. Carbon dioxide and methane split")
        lines.append("")
        lines.append(
            "Every asset-year in the panel now carries `co2_mt`, "
            "`ch4_derived_co2e_mt` and `ch4_mass_kt`, with "
            "`emissions_mtco2e = co2_mt + ch4_derived_co2e_mt` exactly. "
            "The split uses only parameters already on the workbook. "
            "**Upstream:** CH4-derived CO2e per tonne LNG is the scenario "
            "upstream factor less the CO2 part of the official inventory "
            "(`inventory_as_reported x (1 - upstream_ch4_share)` = 0.154), i.e. "
            "0.096 tCO2e/t at central. **Shipping:** the 1.44 carrier uplift is "
            "entirely measured methane slip, so `1 - 1/1.44` = 0.306 of the "
            "shipping CO2e is CH4-derived (0.037 tCO2e/t). **Pipeline "
            "transport, liquefaction, regasification and combustion are treated "
            "as CO2; pipeline fugitive methane is not split**, because the "
            "workbook carries a single pipeline factor with no methane share "
            "behind it. CO2e totals are unchanged by this task."
        )
        lines.append("")
        lines.append(
            "| slice | lifetime CO2e Mt | lifetime CO2-only Mt | "
            "CH4-derived CO2e Mt | CH4 mass kt | CH4 share of CO2e |"
        )
        lines.append("|---|---|---|---|---|---|")
        for _, r in gas_split.iterrows():
            lines.append(
                f"| {r['key']} ({r['slice']}) | {r['lifetime_mtco2e']:,.1f} | "
                f"{r['lifetime_co2_only_mt']:,.1f} | "
                f"{r['lifetime_ch4_derived_co2e_mt']:,.1f} | "
                f"{r['lifetime_ch4_kt']:,.0f} | "
                f"{r['ch4_share_of_co2e_pct']:.1f}% |"
            )
        lines.append("")
        lines.append(
            "CH4 mass is CH4-derived CO2e divided by `gwp100_ch4` = 29.8. It is "
            "left blank for the `near_term_methane_gwp20` scenario, whose "
            "upstream factor is not a GWP100 CO2e figure (see below)."
        )
        lines.append("")
    if gwp20_rec is not None:
        lines.append("### Reconciliation with `near_term_methane_gwp20`")
        lines.append("")
        lines.append(
            f"That scenario's lifetime is "
            f"**{gwp20_rec['scenario_route_mt']:,.1f} Mt** with upstream at "
            f"{gwp20_rec['scenario_upstream_factor']:.3f} and every other stage "
            f"central. The workbook now re-weights only the methane portion of "
            f"upstream: non-methane inventory stays at "
            f"{gwp20_rec['inventory_upstream_factor']:.2f} × (1 − "
            f"upstream_ch4_share), and the methane portion is multiplied by 1.5 "
            f"then by gwp20/gwp100 (82.5/29.8). Rebuilding from the Task 1 CH4 "
            f"mass (`co2_mt + ch4_mass_kt/1000 x gwp20_ch4`, "
            f"gwp20 = {gwp20_rec['gwp20_ch4']:g}) gives "
            f"**{gwp20_rec['ch4_mass_route_mt']:,.1f} Mt**, "
            f"**{gwp20_rec['difference_pct']:+.1f}%** apart. The remaining gap "
            f"is shipping methane slip, which the named scenario does not "
            f"re-weight ({gwp20_rec['shipping_uplift_mt']:,.1f} Mt). The two "
            f"routes are reported rather than forced together."
        )
        lines.append("")
        lines.append(
            "The CH4-mass route's implied methane-only GWP20 upstream factor is "
            f"{gwp20_rec['mass_route_upstream_factor']:.3f}, against the workbook's "
            f"{gwp20_rec['scenario_upstream_factor']:.3f}. They differ because the "
            "workbook starts from the inventory factor and an assumed 30% methane "
            "share, while the mass route starts from the central-case CH4 mass "
            "(inventory CO2 plus the 1.5× methane correction already in "
            "`measurement_central`). **No pipeline methane portion is defined "
            "anywhere in the workbook**, so pipeline is not re-weighted. "
            "`near_term_methane_gwp20` remains a named scenario as the workbook "
            "defines it; the CH4-mass route is not substituted for it."
        )
        lines.append("")

    # 6 Scenario range
    lines.append("## 6. Scenario range")
    lines.append("")
    lines.append("| scenario | upstream | life_average_annual_mt | Lifecycle Mt | CAN Mt/yr |")
    lines.append("|---|---|---|---|---|")
    for scen in INTENSITY_SCENARIOS:
        s = headline_sample(by_project, scen)
        up = inputs["upstream_by_scenario"][scen]
        life = panel_lifetime_mt(panel, scen)
        lines.append(
            f"| {scen} | {up:.3f} | {float(s['annual_total'].sum())/1e6:.1f} | "
            f"{life:.1f} | "
            f"{float(s['canada_territorial'].sum())/1e6:.1f} |"
        )
    lines.append("")

    # 7 Context
    lines.append("## 7. Context")
    lines.append("")
    lines.append(
        f"Canada territorial under `{DEFAULT_SCENARIO}` is **{can:.1f} MtCO2e/yr**."
    )
    lines.append("")
    lines.append(
        f"- **{can/national*100:.1f}%** of national inventory "
        f"({national:.0f} Mt, inventory basis — excludes LULUCF)."
    )
    lines.append(
        f"- **{can/t_low*100:.1f}% to {can/t_high*100:.1f}%** of the 2030 target range "
        f"({t_low:.0f}–{t_high:.0f} Mt). Targets include land-use accounting; "
        f"the {national:.0f} inventory figure does not."
    )
    lines.append(
        f"- **{can/gap*100:.1f}%** of the 2030 overshoot gap "
        f"({gap:.0f} Mt, projected emissions minus the target path)."
    )
    lines.append("")

    # 8 Sensitivities
    lines.append("## 8. Assumptions that move the number most")
    lines.append("")
    base_annual = annual
    howarth = float(
        headline_sample(by_project, "howarth_high")["annual_total"].sum()
    ) / 1e6
    inventory = float(
        headline_sample(by_project, "inventory_as_reported")["annual_total"].sum()
    ) / 1e6
    lines.append(
        f"- **Upstream factor** (central 0.25): inventory_as_reported (0.22) → "
        f"{inventory:.1f} Mt/yr ({inventory-base_annual:+.1f}); "
        f"howarth_high (0.55) → {howarth:.1f} Mt/yr ({howarth-base_annual:+.1f})."
    )

    life_low = (
        float(params["lifespan_sensitivity_low"])
        if "lifespan_sensitivity_low" in params
        else 30.0
    )
    life_high = (
        float(params["lifespan_sensitivity_high"])
        if "lifespan_sensitivity_high" in params
        else 50.0
    )
    lines.append(
        f"- **Lifespan** (default mostly 40 yr licence / Parameters default): "
        f"sensitivity bounds in Parameters are {life_low:.0f} and {life_high:.0f} yr. "
        f"Lifecycle total scales roughly with lifespan "
        f"(~{(life_low/40-1)*100:+.0f}% at {life_low:.0f} yr, "
        f"~{(life_high/40-1)*100:+.0f}% at {life_high:.0f} yr on a pure scale basis). "
        f"Annual changes only via the util_sum/life ratio and FID-delay share of the window. "
        f"Legacy facilities (outlived design life) use steady-state util and report annual only."
    )

    delayed = sample.loc[sample["utilisation_source"].astype(str).str.contains("fid_delay")]
    delay_cap_export = (
        float(delayed.loc[delayed["chain"] == "export", "capacity_mtpa"].sum())
        if len(delayed)
        else 0.0
    )
    delay_ann = float(delayed["annual_total"].sum()) / 1e6 if len(delayed) else 0.0
    lines.append(
        f"- **FID delay** (`fid_delay_mid`={get_param(params,'fid_delay_mid')} yr inside lifespan): "
        f"applies to {len(delayed)} projects ({delay_cap_export:.1f} mtpa export), "
        f"currently {delay_ann:.1f} Mt/yr. Removing the delay would raise their annual "
        f"emissions by roughly the ratio of lost ramp years "
        f"(order-of-magnitude: several Mt/yr on the proposed export slate)."
    )

    util_ss = float(get_param(params, "steady_state_utilisation"))
    lines.append(
        f"- **Utilisation** (default steady-state {util_ss:.3f}; Phase 1 override "
        f"{get_param(params,'lng_canada_ph1_steady_state_utilisation')}; "
        f"Saint John flat {get_param(params,'saint_john_utilisation')}): "
        f"annual emissions scale almost linearly with effective util. "
        f"A +10% relative move in steady-state util moves the headline by about "
        f"{base_annual*0.10:.1f} Mt/yr if applied uniformly."
    )

    liq_central = float(inputs["factors"].loc["liquefaction", "central"])
    lines.append(
        f"- **Liquefaction** (central {liq_central:.2f} tCO2e/t, gas turbine for "
        f"every terminal): electrification is not assumed "
        f"(`liquefaction_electrification_assumed`="
        f"{get_param(params, 'liquefaction_electrification_assumed')}). "
        f"0.12 is retained as range_low and applies only if electrification is "
        f"contracted and delivered. Previous drive classifications are in "
        f"`liquefaction_drive_note`."
    )
    if placeholder_sens is not None:
        lines.append(
            f"- **Placeholder start year** (`assumed_first_export_year_if_missing`="
            f"{placeholder_sens['named_start']}): "
            f"{placeholder_sens['placeholder_mt']:.1f} MtCO2e "
            f"({placeholder_sens['placeholder_pct']:.1f}% of lifetime) from "
            f"{len(placeholder_sens['by_asset'])} "
            "assets with a blank `first_export_year`. The 2069 tail is entirely "
            "this fill. Sensitivity at 2033 and 2035 is tabulated below."
        )
    lines.append(
        f"- **Liquefaction drive default** for remaining `not_published` "
        f"(domestic) rows: `{inputs['liquefaction_drive_default']}` → "
        f"intensity {liq_central:.2f} tCO2e/t from Emission Factors central."
    )
    lines.append("")

    # 9 Appendix comparator
    cf = electrification_counterfactual(inputs, by_project)
    head = cf["summary"].loc[cf["summary"]["slice"] == "headline"].iloc[0]
    lines.append("## 9. Appendix · electrification counterfactual (Canada territorial)")
    lines.append("")
    lines.append(
        "Headline case is gas turbine for every terminal. The rows below ask what "
        "Canada-territorial LNG would be if liquefaction ran at the electric factor "
        f"({cf['electric_intensity']:.2f} instead of {cf['gas_intensity']:.2f} tCO2e/t). "
        "Liquefaction is tagged CAN, so the whole delta is territorial. "
        "This does not change the headline totals."
    )
    lines.append("")
    lines.append(
        f"| case | CAN Mt/yr | vs gas | share of {cf['national']:.0f} Mt inventory | share of 2030 target low |"
    )
    lines.append("|---|---|---|---|---|")
    gas = float(head["canada_territorial_gas_mtco2e_yr"])
    claimed = float(head["canada_territorial_claimed_electric_mtco2e_yr"])
    alle = float(head["canada_territorial_all_electric_mtco2e_yr"])
    lines.append(
        f"| Gas turbine (current) | {gas:.1f} | — | "
        f"{float(head['share_of_national_inventory_gas'])*100:.1f}% | "
        f"{float(head['share_of_2030_target_low_gas'])*100:.1f}% |"
    )
    lines.append(
        f"| Claimed electric delivered | {claimed:.1f} | {claimed-gas:+.1f} | "
        f"{claimed/cf['national']*100:.1f}% | "
        f"{claimed/cf['target_low']*100:.1f}% |"
    )
    lines.append(
        f"| All terminals electric | {alle:.1f} | {alle-gas:+.1f} | "
        f"{float(head['share_of_national_inventory_all_electric'])*100:.1f}% | "
        f"{float(head['share_of_2030_target_low_all_electric'])*100:.1f}% |"
    )
    lines.append("")
    lines.append(
        "Claimed-electric assets (previous `electric_committed` / `electric_planned`): "
        + ", ".join(cf["claimed_project_ids"])
        + "."
    )
    lines.append("")
    lines.append("| calc_group | gas | claimed electric | all electric |")
    lines.append("|---|---|---|---|")
    for g in GROUPS:
        r = cf["summary"].loc[cf["summary"]["slice"] == g].iloc[0]
        lines.append(
            f"| {g} | {r['canada_territorial_gas_mtco2e_yr']:.1f} | "
            f"{r['canada_territorial_claimed_electric_mtco2e_yr']:.1f} | "
            f"{r['canada_territorial_all_electric_mtco2e_yr']:.1f} |"
        )
    lines.append("")
    lines.append(
        "Figure: `Outputs/figures/fig08_electrification_canada_territorial.png`."
    )
    lines.append("")

    # 10 Anything wrong
    lines.append("## 10. Anything that looks wrong")
    lines.append("")
    if inputs["findings"]:
        for f in inputs["findings"]:
            lines.append(f"- FINDING: {f}")
    else:
        lines.append("- No load-time findings.")
    for f in inputs["flags"]:
        lines.append(f"- Flag: {f['project_id']}.{f['field']}={f['issue']}")
    if inputs.get("excluded_none"):
        lines.append(
            f"- Excluded (chain=none or blank, not zeroed): {inputs['excluded_none']}"
        )
    if inputs.get("excluded_watch"):
        lines.append(
            f"- Excluded calc_group=watch (not in calculation): {inputs['excluded_watch']}"
        )
    legacy = sample.loc[sample["is_legacy"]]
    if len(legacy):
        names = ", ".join(
            f"{r.project_id} (first_export_year={r.first_export_year})"
            for r in legacy.itertuples()
        )
        lines.append(
            f"- Legacy facilities (outlived nominal design life; annual only, "
            f"no lifecycle total): {names}."
        )
    lines.append(
        "- Remaining carbon budgets (GCB 2025) are CO2 from the start of 2026. "
        "The paper's share-of-budget figures are now the **CO2-only** lifetime "
        "against those budgets, from the Task 1 per-gas split. Residual "
        "caveats: pipeline fugitive methane is not split out of the CO2 total, "
        "so a small amount of methane sits inside it; and non-CO2 gases other "
        "than CH4 (N2O, refrigerants) are not counted anywhere in the model."
    )
    lines.append(
        "- Reconciliations close within floating-point tolerance (1e-6 to 1e-3); "
        "no material rounding residuals."
    )
    lines.append(
        "- Saint John at ~0.5 Mt/yr depends entirely on `saint_john_utilisation=0.025`; "
        "nameplate at default util would be ~17 Mt/yr. "
        "tier=watch but calc_group=operating (operating import terminal)."
    )
    lines.append(
        "- Tilbury Phase 2 (2.5 mtpa) sits on bunkering by register judgement "
        "(`chain_note`); NRCan lists it as export — classification is a stated judgement, "
        "not re-derived in code."
    )
    lines.append(
        "- Loss and damage central case is ECCC SC-CO2 at 2%, applied per "
        "calendar year to the full GWP100 CO2e total "
        "(`central_price_family=eccc`). That overstates methane (CH4-derived "
        "CO2e is charged at SC-CO2 rather than SC-CH4). Burke is an "
        "upper-bracket sensitivity (g = 0). Damages after 2100, sea-level "
        "rise, extremes and mortality outside GDP are omitted. The "
        "Conference Board denominator is Table 1 GDP in 2020 CAD, inflated "
        "to 2025 CAD."
    )
    lines.append("")

    if ld is not None:
        lines.extend(format_ld_markdown(ld))
    if placeholder_sens is not None:
        lines.extend(format_placeholder_markdown(placeholder_sens))
    if uniform_life is not None:
        lines.extend(format_uniform_life_markdown(uniform_life))
    if feedgas is not None:
        lines.extend(format_feedgas_markdown(feedgas, inputs))
    if drive_sens is not None:
        lines.extend(format_drive_markdown(drive_sens))
    if benchmark is not None:
        lines.extend(format_benchmark_markdown(benchmark))
    if si_assets is not None:
        lines.extend(format_si_table_markdown(si_assets))
    if mc is not None:
        published_vs_mc = None
        if ld is not None:
            h = ld["headline"].set_index("case")
            published_vs_mc = {
                "lifetime_mt": lifecycle,
                "peak_year": peak_year,
                "peak_mt": peak_mt,
                "damage_cad_bn": float(h.loc["published_central", "total_cad_billion"]),
            }
        lines.extend(format_mc_markdown(mc, published=published_vs_mc))
    if lca is not None:
        lines.extend(format_lca_markdown(lca["tables"]))

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote review summary: {path}")


def _validate_licence_end(
    inputs: dict, panel: pd.DataFrame, sample: pd.DataFrame
) -> None:
    """No asset emits after authorised_export_end_year where that field is set."""
    assets = inputs["assets"].set_index("project_id")
    pdef = panel.loc[panel["scenario"] == DEFAULT_SCENARIO]
    n = 0
    for pid, arow in assets.iterrows():
        end = _licence_end_year(arow)
        if end is None:
            continue
        n += 1
        years = pdef.loc[pdef["project_id"] == pid, "year"]
        last = int(years.max()) if len(years) else None
        if last is not None:
            assert last <= end, (pid, last, end)
        prow = sample.loc[sample["project_id"] == pid]
        if not len(prow):
            continue
        life = int(prow.iloc[0]["lifespan_years"])
        src = str(prow.iloc[0]["lifespan_source"])
        derived = None
        if pd.notna(arow.get("authorised_export_term_years")):
            derived = int(arow["authorised_export_term_years"])
        cut = (derived - life) if derived is not None else None
        print(
            f"  licence stop {pid}: last_year={last} end={end} "
            f"life={life}"
            + (f" (cut {cut}y from term {derived})" if cut else "")
            + f" src={src}"
        )
    assert n > 0
    print(
        f"[validate] no asset emits past authorised_export_end_year "
        f"(n={n} licenced) PASS"
    )


def _validate_loss_damage(sample: pd.DataFrame, ld: dict, panel: pd.DataFrame) -> None:
    """L&D remaining tonnes must equal the published panel; ECCC is central."""
    assert ld["central_price_family"] == "eccc"
    assert ld["central_aggregation"] == "calendar_year"
    assert ld["eccc_r"] == 2.0
    assert ld["burke_r"] == 2.0
    assert ld["central_g"] == 0.0
    h = ld["headline"].set_index("case")
    published = h.loc["published_central"]
    assert published["price_family"] == "eccc"
    assert published["aggregation"] == "calendar_year"
    eccc_npv = h.loc["eccc_central_npv_2025"]
    assert published["proposed_cad_billion"] > published["operating_cad_billion"] > 0
    assert published["total_cad_billion"] > eccc_npv["total_cad_billion"] > 0
    egrid = ld["eccc_grid"].set_index("discount_rate_pct")
    assert (
        float(egrid.loc[1.5, "calendar_year_total_cad_billion"])
        > float(egrid.loc[2.0, "calendar_year_total_cad_billion"])
        > float(egrid.loc[2.5, "calendar_year_total_cad_billion"])
    )
    hb = ld["h_burke"]
    assert float(hb["total_cad_billion"]) > float(published["total_cad_billion"])
    share = ld["canada_share"]
    # Task 11: NOT relaxed. The Burke replication package (GitHub
    # echolab-stanford/loss_damage; Zenodo 10.5281/zenodo.18199013, v1.1)
    # ships no country-level damages table by pulse year, so no 2020-pulse
    # share can be computed and this 1990-pulse bound still stands.
    assert 0.0015 < share < 0.0020, share
    assert ld["burke_country_share_pulse_year"] == 1990
    assert 0.0 < ld["canada_p_dam_fd"] < 1.0, ld["canada_p_dam_fd"]
    assert abs(ld["canada_p_dam_fd"] - 0.41) < 0.005, ld["canada_p_dam_fd"]
    assert abs(ld["canada_p_dam_hd"] - 0.33) < 0.005, ld["canada_p_dam_hd"]
    assert hb["externality_ratio_proposed"] > 10
    assert hb["national_value_over_borne"] > 1
    assert abs(hb["externalisation_share"] - (1 - share)) < 1e-12
    assert abs(
        float(hb["proposed_cad_billion"]) - float(hb["proposed_gwp_cad_billion"])
    ) < 1e-6
    # Task 3: ECCC damages are priced per gas. The old methane_overstatement
    # bound no longer applies as written; it survives only as a one-line
    # reconciliation with the retired whole-CO2e-at-SC-CO2 treatment.
    assert 0.01 < ld["methane_share_of_co2e"] < 0.08, ld["methane_share_of_co2e"]
    py = ld["price_by_year"]
    gas_sum = float(py["co2_damage_cad"].sum()) + float(py["ch4_damage_cad"].sum())
    assert abs(gas_sum - float(published["total_cad"])) < 1.0, (
        gas_sum,
        float(published["total_cad"]),
    )
    assert 0.0 < ld["eccc_ch4_damage_share"] < 0.05, ld["eccc_ch4_damage_share"]
    # Pricing CH4 at SC-CH4 must cost less than charging the same CH4-derived
    # CO2e at SC-CO2, because SC-CH4/SC-CO2 stays below GWP100 on the schedule.
    assert ld["old_treatment_cad"] > float(published["total_cad"]), (
        ld["old_treatment_cad"],
        float(published["total_cad"]),
    )
    assert 0.0 < ld["old_treatment_delta_pct"] < 0.10, ld["old_treatment_delta_pct"]
    tonnes = float(py["emissions_mtco2e"].sum()) * 1e6
    wavg = float(published["total_cad"]) / tonnes
    assert abs(wavg - ld["weighted_sc_cad2025"]) < 1e-6, (wavg, ld["weighted_sc_cad2025"])
    y2025 = py.loc[py["year"] == 2025].iloc[0]
    assert int(y2025["sc_cad2021_per_t"]) == 271
    assert int(y2025["sc_ch4_cad2021_per_t"]) > 0
    factor = ld["cad2021_to_2025_factor"]
    # Inflation applied once: CAD 2025 = CAD 2021 × deflator, not × deflator².
    assert abs(float(y2025["sc_cad2025_per_t"]) - 271.0 * factor) < 1e-6
    assert abs(float(y2025["sc_cad2025_per_t"]) - 271.0 * factor * factor) > 1.0
    assert abs(
        float(y2025["sc_ch4_cad2025_per_t"])
        - float(y2025["sc_ch4_cad2021_per_t"]) * factor
    ) < 1e-6
    assert int(py["year"].min()) == 2025
    assert ld["gva"] > ld["gva_proposed_as_published"]
    assert not ld["fig4"]["canada_in_recipient_panel"]
    assert abs(ld["fig4"]["usa_owing_usd"] / 1e12 - 10.18) < 0.15
    assert ld["gva_proposed_30yr"] < ld["gva"]
    grid = ld["burke_grid"]
    lo = float(
        grid.loc[
            (grid["discount_rate_pct"] == 5.0) & (grid["growth_rate"] == 0.0),
            "total_cad_billion",
        ].iloc[0]
    )
    hi = float(
        grid.loc[
            (grid["discount_rate_pct"] == 1.5) & (grid["growth_rate"] == 0.02),
            "total_cad_billion",
        ].iloc[0]
    )
    assert hi > lo, (hi, lo)
    assert not bool(grid["is_central"].any())

    rem = (
        ld["by_year"]
        .loc[ld["by_year"]["price_family"] == "burke"]
        .drop_duplicates(["project_id", "year"])
        .groupby("project_id")["emissions_mtco2e"]
        .sum()
    )
    pub = (
        panel.loc[panel["scenario"] == DEFAULT_SCENARIO]
        .groupby("project_id")["emissions_mtco2e"]
        .sum()
    )
    merged = pub.rename("panel_mt").to_frame().join(rem.rename("ld_mt"), how="outer")
    merged = merged.fillna(0.0)
    delta = (merged["panel_mt"] - merged["ld_mt"]).abs()
    assert delta.max() < 0.05, merged.loc[delta >= 0.05]
    panel_sum = float(pub.sum())
    ld_sum = float(rem.sum())
    assert abs(panel_sum - ld_sum) < 0.05, (panel_sum, ld_sum)
    legacy_ids = set(sample.loc[sample["is_legacy"], "project_id"])
    ld_ids = set(ld["by_project"]["project_id"])
    assert not (ld_ids & legacy_ids), ld_ids & legacy_ids
    print(
        f"[validate] L&D remaining = panel lifetime "
        f"{panel_sum:.2f} Mt PASS"
    )


def main() -> None:
    try:
        reg_m, inp_m = REGISTER.stat().st_mtime, INPUTS.stat().st_mtime
    except OSError:
        reg_m = inp_m = None
    inputs = load_inputs(REGISTER, INPUTS)
    print(f"In-scope assets: {len(inputs['assets'])}")
    print(f"calc_group source: {inputs['calc_group_source']}")
    for finding in inputs["findings"]:
        print(f"  FINDING: {finding}")
    for f in inputs["flags"]:
        print(f"  flag: {f['project_id']}.{f['field']}={f['issue']}")

    # calc_group must be read from register, never derived
    assert inputs["calc_group_source"] == "Asset Register:calc_group"
    print("[validate] calc_group read from Asset Register (not derived) PASS")
    assert abs(float(get_param(inputs["params"], "remaining_15c_budget")) - 170) < 1e-9
    assert abs(float(get_param(inputs["params"], "remaining_17c_budget")) - 525) < 1e-9
    assert abs(float(get_param(inputs["params"], "remaining_2c_budget")) - 1055) < 1e-9
    print("[validate] GCB 2025 carbon budgets 170 / 525 / 1055 GtCO2 PASS")

    for chain, n in EXPECTED_CHAIN_LENGTHS.items():
        assert len(inputs["chains"][chain]) == n
    print("[validate] chain stage counts PASS")

    by_project = compute_by_project(inputs)
    panel_all = build_emissions_panel(inputs)
    exclusion = exclusion_report(by_project, panel_all, inputs)
    panel = filter_panel(panel_all, inputs)
    summary = summarise(by_project)
    by_chain = summarise_by_chain(by_project)
    stages = by_stage(by_project)
    territorial = territorial_table(by_project, inputs["params"])
    assumptions = assumptions_used(inputs, by_project)

    sample = headline_sample(by_project, DEFAULT_SCENARIO)
    full_in_total = by_project.loc[
        (~by_project["excluded_from_totals"])
        & (by_project["scenario"] == DEFAULT_SCENARIO)
    ]
    scope_chains, scope_groups = headline_scope_sets(inputs)
    print(
        f"[scope] {SCOPE_RULE_ONE_LINE} "
        f"n_headline={sample['project_id'].nunique()} "
        f"n_excluded={exclusion['n_excluded']} "
        f"excluded_mt={exclusion['lifetime_mt']:.1f}"
    )

    assert set(sample["chain"].unique()) == {"export"}
    assert int(sample["project_id"].nunique()) == 9, sample["project_id"].unique()
    print("[validate] headline sample is 9 export assets PASS")

    # No watch group in calculation
    assert "watch" not in set(sample["calc_group"].unique()), sample["calc_group"].unique()
    assert "watch" not in set(summary["group"].unique())
    assert not inputs["excluded_watch"] or all(
        pid not in set(sample["project_id"]) for pid in inputs["excluded_watch"]
    )
    # Saint John stays in the register as operating/watch; out of headline (import).
    sj_row = full_in_total.loc[full_in_total["project_id"] == "saint_john_import_facility"]
    assert len(sj_row) == 1 and sj_row.iloc[0]["calc_group"] == "operating"
    assert sj_row.iloc[0]["tier"] == "watch"
    assert not bool(sj_row.iloc[0]["in_headline_scope"])
    print(
        "[validate] no watch calc_group in headline; "
        "Saint John=operating in register, out of headline scope PASS"
    )

    assert_no_cross_chain_capacity_sum(
        {"summary": summary, "by_chain": by_chain, "by_project": by_project}
    )

    # Export capacity by calc_group (headline comparable figure)
    for cg, exp in EXPECTED_EXPORT_BY_CALC.items():
        cap = float(
            sample.loc[
                (sample["chain"] == "export") & (sample["calc_group"] == cg),
                "capacity_mtpa",
            ].sum()
        )
        assert abs(cap - exp) < 1e-6, (cg, cap, exp)
        s_cap = float(
            summary.loc[
                (summary["scenario"] == DEFAULT_SCENARIO) & (summary["group"] == cg),
                "capacity_export_headline_mtpa",
            ].iloc[0]
        )
        assert abs(s_cap - exp) < 1e-6, (cg, s_cap, exp)
    export_total = float(sample.loc[sample["chain"] == "export", "capacity_mtpa"].sum())
    assert abs(export_total - EXPECTED_EXPORT_TOTAL) < 1e-6, export_total
    print(
        f"[validate] export capacity by calc_group "
        f"(total {export_total:.1f} mtpa) PASS"
    )

    # Proposed export: 26 advanced + 34.7 early (Kino Aski 15 mtpa)
    prop_exp = sample.loc[
        (sample["chain"] == "export") & (sample["calc_group"] == "proposed")
    ]
    adv = float(prop_exp.loc[prop_exp["tier"] == "advanced_proposed", "capacity_mtpa"].sum())
    early = float(prop_exp.loc[prop_exp["tier"] == "early_proposed", "capacity_mtpa"].sum())
    assert abs(adv - EXPECTED_ADVANCED_EXPORT) < 1e-6, adv
    assert abs(early - EXPECTED_EARLY_EXPORT) < 1e-6, (early, EXPECTED_EARLY_EXPORT)
    print(f"[validate] proposed export split advanced={adv:.1f} early={early:.1f} PASS")

    electric_left = sample.loc[
        sample["liquefaction_drive"].isin(["electric_committed", "electric_planned"])
    ]
    assert len(electric_left) == 0, electric_left["project_id"].tolist()
    print("[validate] no electric_committed or electric_planned active drive PASS")

    liq_rows = full_in_total.loc[full_in_total["chain"].isin(["export", "bunkering"])]
    liq_delta = (liq_rows["intensity_liquefaction"].astype(float) - 0.29).abs()
    assert len(liq_rows) and liq_delta.max() < 1e-9, liq_delta.max()
    print("[validate] liquefaction intensity=0.29 for all export and bunkering PASS")

    # Off-chain null
    for _, r in sample.iterrows():
        on = {s for s, _ in inputs["chains"][r["chain"]]}
        for stage_name in ALL_STAGES:
            if stage_name not in on:
                assert pd.isna(r[f"annual_{stage_name}"]), (r["project_id"], stage_name)
    print("[validate] no off-chain stages computed PASS")

    terr_delta = (
        sample["canada_territorial"]
        + sample["international_bunkers"]
        + sample["foreign_territorial"]
        - sample["annual_total"]
    ).abs()
    assert terr_delta.max() < 1e-6
    print("[validate] CAN + BUNK + FOR = total PASS")
    terr_total = float(sample["annual_total"].sum())
    terr_share = {
        "CAN": round(100 * float(sample["canada_territorial"].sum()) / terr_total, 1),
        "BUNK": round(
            100 * float(sample["international_bunkers"].sum()) / terr_total, 1
        ),
        "FOR": round(100 * float(sample["foreign_territorial"].sum()) / terr_total, 1),
    }
    for code, exp in EXPECTED_TERRITORIAL_SHARE_PCT.items():
        assert terr_share[code] == exp, (code, terr_share, EXPECTED_TERRITORIAL_SHARE_PCT)
    print(
        f"[validate] territorial split CAN {terr_share['CAN']}% / "
        f"BUNK {terr_share['BUNK']}% / FOR {terr_share['FOR']}% "
        "matches documented shares PASS"
    )
    scope_delta = (
        sample["scope_1_2"] + sample["scope_3"] - sample["annual_total"]
    ).abs()
    assert scope_delta.max() < 1e-6
    print("[validate] scope 1+2 + scope 3 = total PASS")

    sj = full_in_total.loc[full_in_total["project_id"] == "saint_john_import_facility"].iloc[0]
    sj_mt = float(sj["annual_total"]) / 1e6
    assert abs(sj_mt - 0.5) < 0.15 and sj_mt < 5
    print(f"[validate] Saint John={sj_mt:.3f} MtCO2e/yr (register, out of headline) PASS")

    p1 = sample.loc[sample["project_id"] == "lng_canada_phase_1"].iloc[0]
    nameplate_liq = float(p1["capacity_mtpa"]) * float(p1["intensity_liquefaction"])
    assert abs(nameplate_liq - 4.06) < 0.02
    print(f"[validate] Phase 1 liquefaction nameplate={nameplate_liq:.3f} PASS")

    # Legacy facilities remain in the register; they are out of headline (domestic).
    legacy = full_in_total.loc[full_in_total["is_legacy"]]
    legacy_ids = sorted(legacy["project_id"].unique())
    assert "tilbury_original" in legacy_ids
    assert "energir_montreal_lng" in legacy_ids
    assert set(legacy_ids).isdisjoint(set(sample["project_id"]))
    for _, r in legacy.iterrows():
        assert pd.isna(r["lifecycle_total"]), r["project_id"]
        assert "legacy" in str(r["utilisation_source"]).lower()
        assert abs(float(r["effective_util"]) - float(get_param(inputs["params"], "steady_state_utilisation"))) < 1e-9
        assert not bool(r["in_headline_scope"])
    print(
        f"[validate] legacy facilities annual-only, out of headline scope: "
        f"{legacy_ids} PASS"
    )

    _validate_licence_end(inputs, panel, sample)

    ld = compute_loss_damage(inputs, INPUTS_DIR, panel=panel)
    _validate_loss_damage(sample, ld, panel)
    print(
        f"[validate] Burke country share is the {ld['burke_country_share_pulse_year']} "
        f"pulse only (no by-pulse country table in the replication package); "
        f"Canada share {100*ld['canada_share']:.2f}% with "
        f"P_dam_FD={ld['canada_p_dam_fd']:.2f}, "
        f"P_dam_HD={ld['canada_p_dam_hd']:.2f}; "
        f"0.0015 < share < 0.0020 assertion NOT relaxed PASS"
    )
    print(
        f"[validate] loss and damage central "
        f"${ld['published']['total_cad_billion']:.0f} bn "
        f"CAD 2025 (ECCC 2% calendar year) PASS"
    )
    print(
        f"[validate] emissions-weighted SC-CO2 "
        f"${ld['weighted_sc_cad2025']:.0f}/t CAD 2025 "
        f"(simple mean ${ld['simple_sc_cad2025']:.0f}; "
        f"CAD 2021 weighted ${ld['weighted_sc_cad2021']:.0f}; "
        f"deflator {ld['cad2021_to_2025_factor']:.4f} applied once) PASS"
    )

    # Group and headline annuals — printed against the pre-revision snapshot
    sdef = summary.loc[summary["scenario"] == DEFAULT_SCENARIO]
    annual = float(sample["annual_total"].sum())
    annual_mt = annual / 1e6
    liq_mt = float(sample["annual_liquefaction"].sum()) / 1e6
    print(
        f"[validate] life_average_annual_mt {annual_mt:.1f} Mt/yr "
        f"(was {BEFORE['annual_mt']:.1f}); "
        f"liquefaction {liq_mt:.1f} Mt/yr (was {BEFORE['liquefaction_mt']:.1f})"
    )

    can = float(sample["canada_territorial"].sum())
    bunk = float(sample["international_bunkers"].sum())
    foreign = float(sample["foreign_territorial"].sum())

    panel_life_mt = panel_lifetime_mt(panel, DEFAULT_SCENARIO)
    peak_year, peak_mt = panel_peak(panel, DEFAULT_SCENARIO)
    duration_life = float(sample["lifecycle_total"].sum(min_count=1)) / 1e6
    if pd.isna(duration_life):
        duration_life = 0.0
    print(
        f"[validate] published lifetime is calendar panel "
        f"{panel_life_mt:.1f} Mt (duration×average was {duration_life:.1f}; "
        f"delta {panel_life_mt - duration_life:+.1f})"
    )
    print(
        f"[validate] headline annual is panel peak {peak_mt:.1f} Mt in {peak_year} "
        f"({panel_n_emitting(panel, peak_year, DEFAULT_SCENARIO)} assets); "
        f"life_average_annual_mt {annual_mt:.1f}"
    )
    assert abs(round(panel_life_mt, 1) - EXPECTED_LIFETIME_MT) < 1e-9, (
        panel_life_mt,
        EXPECTED_LIFETIME_MT,
    )
    assert peak_year == EXPECTED_PEAK_YEAR, (peak_year, EXPECTED_PEAK_YEAR)
    assert abs(round(peak_mt, 1) - EXPECTED_PEAK_MT) < 1e-9, (
        peak_mt,
        EXPECTED_PEAK_MT,
    )
    print(
        f"[validate] lifetime {EXPECTED_LIFETIME_MT} Mt and peak "
        f"{EXPECTED_PEAK_MT} Mt in {EXPECTED_PEAK_YEAR} match locked values PASS"
    )
    placeholder_sens = run_placeholder_start_sensitivity(
        inputs, INPUTS_DIR, panel, ld
    )
    print(
        f"[validate] placeholder-start assets "
        f"{placeholder_sens['placeholder_mt']:.1f} Mt "
        f"({placeholder_sens['placeholder_pct']:.1f}% of lifetime) PASS"
    )
    uniform_life = run_uniform_life_sensitivity(inputs, INPUTS_DIR, panel, ld)
    central_full = float(
        uniform_life["cases"].loc[
            (uniform_life["cases"]["case"] == "central")
            & (uniform_life["cases"]["build_out"] == "full"),
            "lifetime_mtco2e",
        ].iloc[0]
    )
    assert abs(central_full - panel_life_mt) < 1e-9, (central_full, panel_life_mt)
    print(
        f"[validate] uniform 40-year life sensitivity "
        f"{uniform_life['delta_pct_full']:+.1f}% on full buildout; "
        f"central case unchanged PASS"
    )

    feedgas = run_kino_aski_feedgas_sensitivity(inputs, panel)
    fg_central = feedgas["cases"].loc[feedgas["cases"]["case"] == "central"].iloc[0]
    assert abs(float(fg_central["headline_lifetime_mtco2e"]) - panel_life_mt) < 1e-6
    assert abs(round(float(fg_central["headline_canada_pct"]), 1)
               - EXPECTED_TERRITORIAL_SHARE_PCT["CAN"]) < 0.05, (
        fg_central["headline_canada_pct"],
        EXPECTED_TERRITORIAL_SHARE_PCT["CAN"],
    )
    print(
        "[validate] Kino Aski feedgas sensitivity: Canada share "
        + " / ".join(
            f"{r['case']} {r['headline_canada_pct']:.1f}%"
            for _, r in feedgas["cases"].iterrows()
        )
        + " PASS"
    )

    drive_sens = run_drive_sensitivity(inputs, panel)
    dcen = drive_sens["cases"].loc[drive_sens["cases"]["case"] == "central"].iloc[0]
    assert abs(float(dcen["headline_lifetime_mtco2e"]) - panel_life_mt) < 1e-6
    print(
        "[validate] liquefaction drive sensitivity (central 0.29 unchanged): "
        + "; ".join(
            f"{r['case']} {r['headline_delta_mtco2e']:+.1f} Mt total and CAN"
            for _, r in drive_sens["cases"].iterrows()
            if r["case"] != "central"
        )
        + " PASS"
    )

    benchmark = build_benchmark_table(inputs)
    assert len(benchmark) == 6, len(benchmark)
    print(
        f"[validate] benchmark comparison table {len(benchmark)} rows "
        f"(liquefaction, shipping, pipeline, regasification, well-to-regas, "
        f"LNG stages) PASS"
    )

    si_assets = build_si_asset_table(inputs, panel)
    assert len(si_assets) == int(sample["project_id"].nunique()), len(si_assets)
    assert abs(float(si_assets["lifetime_mtco2e"].sum()) - panel_life_mt) < 1e-6
    assert abs(float(si_assets["share_of_full_buildout_pct"].sum()) - 100.0) < 1e-6
    gem_dis = si_assets.loc[si_assets["gem_disagrees_with_register"]]
    print(
        f"[validate] SI asset table {len(si_assets)} rows, shares sum to 100% "
        f"PASS"
    )
    for _, r in gem_dis.iterrows():
        print(
            f"  FINDING: GEM has {r['project_id']} as "
            f"{r['gem_status_verbatim']!r} ({r['gem_status_date']}); register "
            f"has {r['register_status']!r}. "
            f"{r['lifetime_mtco2e']:.1f} Mt, "
            f"{r['share_of_full_buildout_pct']:.1f}% of lifetime. "
            f"Recorded, not resolved."
        )

    mc = run_monte_carlo(inputs, INPUTS_DIR, panel)
    print(
        f"[validate] Monte Carlo {mc['n_draws']} draws seed {mc['seed']} "
        f"physics {mc['physics_seconds']:.2f}s price {mc['price_seconds']:.2f}s "
        f"kernel max abs {mc['kernel_panel_max_abs_mt']:.1e} Mt PASS"
    )
    gas_split = gas_split_table(panel, inputs)
    gwp20_rec = gwp20_reconciliation(panel, inputs)
    full_split = gas_split.loc[
        (gas_split["slice"] == "build_out") & (gas_split["key"] == "full")
    ].iloc[0]
    resid = abs(
        float(full_split["lifetime_co2_only_mt"])
        + float(full_split["lifetime_ch4_derived_co2e_mt"])
        - float(full_split["lifetime_mtco2e"])
    )
    assert resid < 1e-6, resid
    assert abs(float(full_split["lifetime_mtco2e"]) - panel_life_mt) < 1e-9
    print(
        f"[validate] gas split CO2 {full_split['lifetime_co2_only_mt']:.1f} Mt + "
        f"CH4-derived {full_split['lifetime_ch4_derived_co2e_mt']:.1f} MtCO2e "
        f"= CO2e {full_split['lifetime_mtco2e']:.1f} Mt exactly; "
        f"CH4 mass {full_split['lifetime_ch4_kt']:,.0f} kt PASS"
    )
    print(
        f"[reconcile] GWP20 scenario route {gwp20_rec['scenario_route_mt']:.1f} Mt vs "
        f"CH4-mass route {gwp20_rec['ch4_mass_route_mt']:.1f} Mt "
        f"({gwp20_rec['difference_pct']:+.2f}%) - reported, not forced"
    )

    paper_set = paper_set_table(panel, ld, mc, inputs, by_project)
    for _, r in paper_set.iterrows():
        exp = EXPECTED_BUILD_OUT[r["build_out"]]
        got = {
            "lifetime_mt": round(float(r["lifetime_mtco2e"]), 1),
            "lifetime_co2_only_mt": round(float(r["lifetime_co2_only_mt"]), 1),
            "peak_year": int(r["peak_year"]),
            "peak_mt": round(float(r["peak_mtco2e_yr"]), 1),
            "damages_cad_bn": round(float(r["eccc_2pct_damages_cad_bn"])),
        }
        assert got == exp, (r["build_out"], got, exp)
        assert (
            r["lifetime_mtco2e_p05"]
            <= r["lifetime_mtco2e_mc_median"]
            <= r["lifetime_mtco2e_p95"]
        ), r["build_out"]
    paper_set_sha = write_paper_set_locked(paper_set, PAPER_SET_LOCKED_CSV)
    assert paper_set_sha == EXPECTED_PAPER_SET_SHA256, (
        "The locked paper-set table has changed. "
        f"expected SHA-256 {EXPECTED_PAPER_SET_SHA256}; "
        f"got {paper_set_sha}; "
        f"file {PAPER_SET_LOCKED_CSV}. "
        "Every published paper number is in that file. If the change is "
        "deliberate, update EXPECTED_PAPER_SET_SHA256 and EXPECTED_BUILD_OUT "
        "in the same commit and put the old and new values in the message."
    )
    print(f"[validate] paper-set SHA-256 {paper_set_sha[:16]}... matches lock PASS")

    full_row = paper_set.loc[paper_set["build_out"] == "full"].iloc[0]
    assert round(float(full_row["lifetime_mtco2e"]), 1) == EXPECTED_LIFETIME_MT
    assert int(full_row["peak_year"]) == EXPECTED_PEAK_YEAR
    assert round(float(full_row["peak_mtco2e_yr"]), 1) == EXPECTED_PEAK_MT
    print(
        "[validate] paper set locked for all three build-outs "
        + "; ".join(
            f"{r['build_out']} {r['lifetime_mtco2e']:.1f} Mt / "
            f"{r['eccc_2pct_damages_cad_bn']:.0f} bn"
            for _, r in paper_set.iterrows()
        )
        + " PASS"
    )

    budgets = carbon_budget_shares(
        panel_life_mt,
        inputs["params"],
        float(full_split["lifetime_co2_only_mt"]),
    )
    b15 = budgets.loc[budgets["parameter"] == "remaining_15c_budget"].iloc[0]
    print(
        f"[validate] lifetime {b15['lifetime_gtco2']:.2f} GtCO2 (CO2 only) is "
        f"{b15['share_pct']:.1f}% of 1.5C budget {b15['budget_gtco2']:g} GtCO2 "
        f"like for like (CO2e basis would be {b15['share_co2e_pct']:.1f}%) PASS"
    )

    summary = summary.copy()
    summary["lifecycle_total_mtco2e"] = [
        panel_lifetime_mt(panel, r["scenario"], calc_group=r["group"])
        for _, r in summary.iterrows()
    ]
    by_chain = by_chain.copy()
    by_chain["lifecycle_total_mtco2e"] = [
        panel_lifetime_mt(panel, r["scenario"], chain=r["chain"])
        for _, r in by_chain.iterrows()
    ]
    proj_life = panel_by_project(panel)
    by_project = by_project.merge(
        proj_life[["scenario", "project_id", "lifetime_mtco2e"]].rename(
            columns={"lifetime_mtco2e": "panel_lifetime_mtco2e"}
        ),
        on=["scenario", "project_id"],
        how="left",
    )

    readme = pd.DataFrame(
        [
            ("title", "Canada LNG lifecycle emissions — calc_group grouping"),
            ("run_at_utc", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")),
            ("asset_register", REGISTER.name),
            ("data_inputs", INPUTS.name),
            ("headline_scenario", DEFAULT_SCENARIO),
            ("calc_group_source", inputs["calc_group_source"]),
            (
                "headline_note",
                "Lifetime is the sum of the per-asset calendar panel "
                f"({PANEL_START_YEAR} to last emitting year). "
                "Headline annual is the panel peak calendar year. "
                "life_average_annual_mt is utilisation over each asset window. "
                "Headline includes calc_groups in headline_scope_calc_groups "
                "on chains in headline_scope_chains (export operating / "
                "under construction / proposed). "
                "Capacity is per chain; headline capacity is export liquefaction only. "
                "Non-export assets stay in the register as a stated exclusion.",
            ),
            ("annual_total_mtco2e_yr", peak_mt),
            ("annual_basis", "panel peak calendar year"),
            ("panel_peak_year", peak_year),
            ("panel_peak_mtco2e_yr", peak_mt),
            ("panel_peak_n_assets", panel_n_emitting(panel, peak_year, DEFAULT_SCENARIO)),
            ("life_average_annual_mt", annual_mt),
            ("life_average_basis", "life-average utilisation over each asset window"),
            ("lifetime_total_mtco2e", panel_life_mt),
            ("lifetime_basis", "sum of calendar panel; headline scope (export chain)"),
            ("headline_scope_rule", SCOPE_RULE_ONE_LINE),
            ("headline_scope_chains", ",".join(sorted(scope_chains))),
            ("headline_scope_calc_groups", ",".join(sorted(scope_groups))),
            ("headline_n_assets", int(sample["project_id"].nunique())),
            ("excluded_n_assets", exclusion["n_excluded"]),
            ("excluded_lifetime_mtco2e", exclusion["lifetime_mt"]),
            (
                "assumed_first_export_year_if_missing",
                int(get_param(inputs["params"], "assumed_first_export_year_if_missing")),
            ),
            ("placeholder_lifetime_mtco2e", placeholder_sens["placeholder_mt"]),
            ("placeholder_share_of_lifetime_pct", placeholder_sens["placeholder_pct"]),
            ("monte_carlo_seed", mc["seed"]),
            ("monte_carlo_n_draws", mc["n_draws"]),
            ("monte_carlo_physics_seconds", round(mc["physics_seconds"], 3)),
            ("monte_carlo_price_seconds", round(mc["price_seconds"], 3)),
            ("lifetime_co2_only_mt", float(full_split["lifetime_co2_only_mt"])),
            ("lifetime_ch4_kt", float(full_split["lifetime_ch4_kt"])),
            (
                "carbon_budget_units_note",
                "Share-of-budget is the CO2-only lifetime against the CO2 "
                "budgets (like for like). Residual: pipeline fugitive methane "
                "is not split out of the CO2 total, and non-CO2 gases other "
                "than CH4 are not counted.",
            ),
            ("lifetime_share_of_15c_budget_co2e_basis_pct", float(b15["share_co2e_pct"])),
            ("duration_x_average_mtco2e", duration_life),
            ("export_capacity_mtpa", export_total),
            ("canada_territorial_mtco2e_yr", can / 1e6),
            ("international_bunkers_mtco2e_yr", bunk / 1e6),
            ("foreign_territorial_mtco2e_yr", foreign / 1e6),
            ("legacy_projects", ", ".join(legacy_ids)),
            ("gcb_2025_15c_gtco2", float(b15["budget_gtco2"])),
            ("lifetime_share_of_15c_budget_pct", float(b15["share_pct"])),
            ("inputs_guard", "Inputs opened read-only (rb); writes only under Outputs/."),
            (
                "slide_tables",
                "Outputs/SLIDE_TABLES.xlsx — send this file to the PPT chat "
                "(one table per sheet, 1-decimal, project names).",
            ),
            ("findings", "; ".join(inputs["findings"]) if inputs["findings"] else "none"),
        ],
        columns=["field", "value"],
    )

    OUT.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(RESULTS, engine="openpyxl") as writer:
        readme.to_excel(writer, sheet_name="README", index=False)
        summary[
            [
                "group",
                "scenario",
                "project_count",
                "capacity_export_headline_mtpa",
                "capacity_export_mtpa",
                "capacity_bunkering_mtpa",
                "capacity_domestic_mtpa",
                "capacity_import_mtpa",
                "scope_1_2_mtco2e_yr",
                "scope_3_mtco2e_yr",
                "canada_territorial_mtco2e_yr",
                "international_bunkers_mtco2e_yr",
                "foreign_territorial_mtco2e_yr",
                "annual_total_mtco2e_yr",
                "lifecycle_total_mtco2e",
            ]
        ].to_excel(writer, sheet_name="Summary", index=False)
        by_project.to_excel(writer, sheet_name="By Project", index=False)
        stages.to_excel(writer, sheet_name="By Stage", index=False)
        territorial.to_excel(writer, sheet_name="Territorial", index=False)
        assumptions.to_excel(writer, sheet_name="Assumptions", index=False)
        budgets.to_excel(writer, sheet_name="Carbon Budgets", index=False)
        gas_split.to_excel(writer, sheet_name="Gas Split", index=False)
        paper_set.to_excel(writer, sheet_name="Paper Set", index=False)
        si_assets.to_excel(writer, sheet_name="SI Assets", index=False)
        benchmark.to_excel(writer, sheet_name="Benchmark", index=False)
        by_chain.to_excel(writer, sheet_name="By Chain", index=False)
        exclusion["table"].to_excel(writer, sheet_name="Headline Exclusion", index=False)
        panel.to_excel(writer, sheet_name="Calendar Panel", index=False)
        panel_by_project(panel).to_excel(
            writer, sheet_name="Panel Lifetime By Project", index=False
        )
        elec_cf = electrification_counterfactual(inputs, by_project)
        elec_cf["summary"].to_excel(writer, sheet_name="Electrification CAN", index=False)
        ld["headline"].to_excel(writer, sheet_name="LD Headline", index=False)
        ld["by_project"].to_excel(writer, sheet_name="LD By Project", index=False)
        ld["burke_grid"].to_excel(writer, sheet_name="LD Burke Grid", index=False)
        ld["eccc_grid"].to_excel(writer, sheet_name="LD ECCC Grid", index=False)
        ld["physical_scenarios"].to_excel(writer, sheet_name="LD Physical Scenarios", index=False)
        ld["sc_table"].to_excel(writer, sheet_name="LD SC-CO2", index=False)
        ld["horizon_table"].to_excel(writer, sheet_name="LD Horizons", index=False)
        ld["params_meta"].to_excel(writer, sheet_name="LD Assumptions", index=False)
        mc["summary"].to_excel(writer, sheet_name="MC Summary", index=False)
        mc["howarth"].to_excel(writer, sheet_name="MC Howarth", index=False)
        mc["parameters"].to_excel(writer, sheet_name="MC Parameters", index=False)

    fig10 = figure_10_lca_comparison(inputs, FIGURE_DIR, FIGURE_DATA)
    w2r = fig10["key"]["model_well_to_regas_t_per_t"]
    assert abs(w2r - EXPECTED_WELL_TO_REGAS_T_PER_T) < 1e-9, (
        f"well-to-regasification {w2r} t/t; locked "
        f"{EXPECTED_WELL_TO_REGAS_T_PER_T}. If deliberate, re-lock "
        "EXPECTED_WELL_TO_REGAS_T_PER_T and run tools/refresh_banners.py."
    )
    print(f"[validate] well-to-regasification {w2r} t/t = lock PASS")
    stale = stale_banners(ROOT, current_lock())
    assert not stale, (
        "dated-document banners do not match the lock: " + "; ".join(stale)
        + ". Run python tools/refresh_banners.py and commit the result."
    )
    print("[validate] dated-document banners match the lock PASS")
    write_review_summary(
        SUMMARY_MD,
        inputs,
        by_project,
        summary,
        by_chain,
        stages,
        panel,
        ld=ld,
        placeholder_sens=placeholder_sens,
        mc=mc,
        lca=fig10,
        exclusion=exclusion,
        gas_split=gas_split,
        gwp20_rec=gwp20_rec,
        paper_set=paper_set,
        uniform_life=uniform_life,
        feedgas=feedgas,
        drive_sens=drive_sens,
        si_assets=si_assets,
        benchmark=benchmark,
    )
    fig_results = build_all_report_figures(
        inputs, by_project, stages, FIGURE_DIR, FIGURE_DATA, panel=panel
    )
    fig09 = FIGURE_DIR / "fig09_loss_damage_by_group.png"
    write_ld_figure(ld["published"], fig09)
    ld_csv = FIGURE_DATA / "fig09_loss_damage_by_group.csv"
    FIGURE_DATA.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "calc_group": g,
                "cad_trillion_2025": float(ld["published"][f"{g}_cad_billion"]) / 1000.0,
                "price_family": "eccc",
                "discount_rate_pct": ld["eccc_r"],
                "aggregation": "calendar_year",
            }
            for g in GROUPS
        ]
    ).to_csv(ld_csv, index=False)
    ld["headline"].to_csv(FIGURE_DATA / "ld_headline.csv", index=False)
    ld["burke_grid"].to_csv(FIGURE_DATA / "ld_burke_grid.csv", index=False)
    ld["eccc_grid"].to_csv(FIGURE_DATA / "ld_eccc_grid.csv", index=False)
    ld["price_by_year"].to_csv(FIGURE_DATA / "ld_price_by_year.csv", index=False)
    pd.DataFrame(
        [
            {
                "item": "canada_share_of_1gt_pulse_future_window",
                "value": ld["canada_share"],
                "unit": "fraction",
                "pulse_year": ld["burke_country_share_pulse_year"],
                "note": "share_FD_% / 100 from burke_country_damage_shares.csv",
            },
            {
                "item": "canada_P_dam_FD",
                "value": ld["canada_p_dam_fd"],
                "unit": "fraction of Burke draws",
                "pulse_year": ld["burke_country_share_pulse_year"],
                "note": (
                    "share of Burke draws in which Canada's damage from that "
                    "pulse is positive, future window. Report with the 0.17%."
                ),
            },
            {
                "item": "canada_P_dam_HD",
                "value": ld["canada_p_dam_hd"],
                "unit": "fraction of Burke draws",
                "pulse_year": ld["burke_country_share_pulse_year"],
                "note": "same, historical window",
            },
            {
                "item": "canada_share_of_1gt_pulse_historical_window",
                "value": ld["canada_share_hd"],
                "unit": "fraction",
                "pulse_year": ld["burke_country_share_pulse_year"],
                "note": "share_HD_% / 100",
            },
            {
                "item": "pulse_year_availability",
                "value": None,
                "unit": "-",
                "pulse_year": ld["burke_country_share_pulse_year"],
                "note": ld["burke_country_share_availability"],
            },
        ]
    ).to_csv(FIGURE_DATA / "burke_canada_share.csv", index=False)
    placeholder_sens["cases"].to_csv(
        FIGURE_DATA / "placeholder_start_sensitivity.csv", index=False
    )
    placeholder_sens["by_asset"].to_csv(
        FIGURE_DATA / "placeholder_start_by_asset.csv", index=False
    )
    mc["summary"].to_csv(FIGURE_DATA / "mc_summary.csv", index=False)
    mc["howarth"].to_csv(FIGURE_DATA / "mc_howarth_sensitivity.csv", index=False)
    mc["parameters"].to_csv(FIGURE_DATA / "mc_parameters.csv", index=False)
    mc["draws"].to_csv(FIGURE_DATA / "mc_draws.csv", index=False)
    panel.to_csv(FIGURE_DATA / "emissions_panel.csv", index=False)
    gas_split.to_csv(FIGURE_DATA / "gas_split.csv", index=False)
    paper_set.to_csv(PAPER_SET_CSV, index=False)
    uniform_life["cases"].to_csv(
        FIGURE_DATA / "sens_uniform_life.csv", index=False
    )
    uniform_life["by_asset"].to_csv(
        FIGURE_DATA / "sens_uniform_life_by_asset.csv", index=False
    )
    feedgas["cases"].to_csv(
        FIGURE_DATA / "sens_kino_aski_feedgas.csv", index=False
    )
    drive_sens["cases"].to_csv(
        FIGURE_DATA / "sens_liquefaction_drive.csv", index=False
    )
    drive_sens["by_asset"].to_csv(
        FIGURE_DATA / "sens_liquefaction_drive_by_asset.csv", index=False
    )
    si_assets.to_csv(SI_TABLE_CSV, index=False)
    benchmark.to_csv(BENCHMARK_CSV, index=False)
    slide_tables = build_slide_tables(
        inputs, by_project, summary, by_chain, stages, panel, ld=ld, mc=mc
    )
    write_slide_tables_xlsx(slide_tables, SLIDE_TABLES, FIGURE_DATA)

    if reg_m is not None and inp_m is not None:
        assert REGISTER.stat().st_mtime == reg_m and INPUTS.stat().st_mtime == inp_m

    print("\n========== COMPLETION ==========")
    print("BEFORE (July 2026 run, measurement_central):")
    print(
        f"  annual={BEFORE['annual_mt']:.1f} Mt/yr  "
        f"lifecycle={BEFORE['lifecycle_mt']:.1f} Mt  "
        f"export={BEFORE['export_mtpa']:.1f} mtpa  "
        f"liquefaction={BEFORE['liquefaction_mt']:.1f} Mt/yr  "
        f"early_export={BEFORE['early_export_mtpa']:.1f} mtpa"
    )
    for g, val in BEFORE["group_annual"].items():
        print(f"  group {g:20s}  annual={val:6.1f} Mt/yr")
    for c, val in BEFORE["chain_annual"].items():
        print(f"  chain {c:20s}  annual={val:6.1f} Mt/yr")
    print("AFTER:")
    print(
        f"Headline annual (panel peak): {peak_mt:.1f} MtCO2e in {peak_year} "
        f"({panel_n_emitting(panel, peak_year, DEFAULT_SCENARIO)} assets emitting)"
    )
    print(f"life_average_annual_mt: {annual_mt:.1f} MtCO2e/yr")
    print("Group annual totals (measurement_central, life-average):")
    for g in GROUPS:
        r = sdef.loc[sdef["group"] == g].iloc[0]
        before_g = BEFORE["group_annual"][g]
        print(
            f"  {g:20s}  annual={r['annual_total_mtco2e_yr']:6.1f} Mt/yr "
            f"(was {before_g:.1f})  "
            f"export_cap={r['capacity_export_headline_mtpa']:5.1f} mtpa"
        )
    print(
        f"  {'TOTAL':20s}  life_average={annual_mt:6.1f} Mt/yr "
        f"(was {BEFORE['annual_mt']:.1f})"
    )
    print(
        f"Published lifetime (calendar panel): {panel_life_mt:.1f} Mt  "
        f"(duration×average was {duration_life:.1f})"
    )
    print(f"Panel peak: {peak_mt:.1f} MtCO2e in {peak_year}")
    print(
        f"Liquefaction stage: {liq_mt:.1f} Mt/yr "
        f"(was {BEFORE['liquefaction_mt']:.1f})"
    )
    print(
        f"Early-stage export capacity: {early:.1f} mtpa "
        f"(was {BEFORE['early_export_mtpa']:.1f})"
    )
    print(
        f"Headline export capacity: {export_total:.1f} mtpa "
        f"(was {BEFORE['export_mtpa']:.1f})"
    )
    print("By chain:")
    cdef = by_chain.loc[by_chain["scenario"] == DEFAULT_SCENARIO]
    for chain in CHAINS:
        r = cdef.loc[cdef["chain"] == chain].iloc[0]
        before_c = BEFORE["chain_annual"][chain]
        print(
            f"  {chain:20s}  annual={r['annual_total_mtco2e_yr']:6.1f} Mt/yr "
            f"(was {before_c:.1f})  cap={r['capacity_mtpa']:5.1f} mtpa"
        )
    print(
        f"Territorial (average): CAN={can/1e6:.1f}  BUNK={bunk/1e6:.1f}  "
        f"FOR={foreign/1e6:.1f}"
    )
    print(
        "Validations: capacity+tier have chain/calc_group; no electric drive; "
        "liquefaction=0.29 export/bunkering; Saint John ~0.5; Phase 1 liq ~4.06; "
        "scope and territorial splits sum to total — all PASS"
    )
    print("\nReport figures written:")
    for key in ("fig1", "fig2", "fig3", "fig4", "fig5", "fig6", "fig8"):
        r = fig_results[key]
        print(f"  {r['path'].name}")
        print(f"    csv: {r['csv'].name}")
        print(f"    key: {r['key']}")
    print(f"  {fig09.name}")
    print(f"    csv: {ld_csv.name}")
    print(f"  {fig10['path'].name}")
    print(f"    csv: {fig10['csv'].name}")
    print(f"    key: {fig10['key']}")
    print(
        "\nFigure validations: stage sum=headline, territorial sum=headline, "
        "fig3 plateau=fig6 plateau, fig5 central=fig4, CSVs present — all PASS"
    )
    print(f"\nSlide tables (send this to the PPT chat): {SLIDE_TABLES.name}")
    print("No input file was modified during the run.")
    print("================================")


if __name__ == "__main__":
    main()
