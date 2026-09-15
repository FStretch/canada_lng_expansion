"""Kino Aski feedgas sensitivity (supplementary information only).

Kino Aski LNG (formerly Marinvest, Baie-Comeau) is 15 mtpa on the Quebec north
shore with no stated feedgas route. The register records the gap. Two candidate
supplies were named in the proponent coverage, and they differ in two ways that
matter to this model:

**Case A, Western Canadian supply.** Gas reaches the Quebec north shore from the
Western Canada Sedimentary Basin. The pipeline haul is far longer than the
in-scope British Columbia lines, so pipeline intensity should scale with
distance. The 670 km Coastal GasLink length is used only as the distance
yardstick for the illustrative multipliers; the 0.074 pipeline_transport
factor is not calibrated on it (it comes from Liu et al. 2021 on an 1,100 km
Alberta line and a CER national average). Territory stays CAN for both
upstream and pipeline.

**Case B, United States supply.** Appalachian gas. Intensities are unchanged -
this model has no US-specific factors and does not invent any - but upstream and
pipeline emissions occur outside Canada, so they are tagged FOR instead of CAN.

No central factor is touched and the central case is unchanged.

On Case A's distance: no published route distance exists for Western Canadian
gas to the Quebec north shore, because no such route is defined. The CER's
pipeline profile for the TransCanada Canadian Mainline publishes only a total
regulated system length of 14,123 km across all segments including deactivated
and abandoned ones, which is not a route distance, and Baie-Comeau is not on the
Mainline in any case. So Case A is run as an explicit multiplier band, x3 and
x5 against the Coastal GasLink calibration, **labelled illustrative**. The gap
is recorded on the register's Data Gaps sheet.
"""

from __future__ import annotations

import pandas as pd

from src.inputs import DEFAULT_SCENARIO
from src.scope import headline_scope_sets, row_in_headline_scope
from src.trajectories import _chain_intensity_split, panel_lifetime_mt

KINO_ASKI_ID = "marinvest_baie_comeau"
# Coastal GasLink's 670 km (Supporting Infrastructure sheet) is the distance
# yardstick for the illustrative x3 / x5 band only. The pipeline_transport
# factor is NOT calibrated on it; see the Emission Factors basis cell.
CGL_CALIBRATION_KM = 670.0
ILLUSTRATIVE_MULTIPLIERS = (3.0, 5.0)


def _asset_row(inputs: dict, project_id: str):
    sl = inputs["assets"].loc[inputs["assets"]["project_id"] == project_id]
    if len(sl) != 1:
        raise KeyError(f"Expected exactly one register row for {project_id!r}.")
    return sl.iloc[0]


def run_kino_aski_feedgas_sensitivity(
    inputs: dict,
    panel: pd.DataFrame,
) -> dict:
    """Case A (Western Canadian, distance-scaled pipeline) and Case B (US, FOR)."""
    chains, groups = headline_scope_sets(inputs)
    row = _asset_row(inputs, KINO_ASKI_ID)
    if not row_in_headline_scope(row, chains, groups):
        raise ValueError(f"{KINO_ASKI_ID} is not in headline scope.")

    pipe_i = float(inputs["factors"].loc["pipeline_transport", "central"])
    chain_stages = inputs["chains"][row["chain"]]
    total_i, _co2, _ch4 = _chain_intensity_split(
        row, DEFAULT_SCENARIO, inputs, canada_only=False
    )
    up_i = float(inputs["upstream_by_scenario"][DEFAULT_SCENARIO])

    kino_life = panel_lifetime_mt(panel, DEFAULT_SCENARIO, project_id=KINO_ASKI_ID)
    headline_life = panel_lifetime_mt(panel, DEFAULT_SCENARIO)
    # Lifetime tonnes of LNG behind that number, from the chain intensity.
    lng_mt = kino_life / total_i

    # Split this asset's chain intensity by territory, so the two cases can be
    # applied as intensity moves rather than re-running the whole panel.
    can_i, _c, _h = _chain_intensity_split(
        row, DEFAULT_SCENARIO, inputs, canada_only=True
    )
    bunk_i = sum(
        _stage_i(row, stage, inputs)
        for stage, where in chain_stages
        if where == "BUNK"
    )
    for_i = total_i - can_i - bunk_i

    rows = []

    def _pack(case: str, label: str, pipe_scale: float, us_supply: bool) -> dict:
        pipe_new = pipe_i * pipe_scale
        total_new = total_i - pipe_i + pipe_new
        life_new = lng_mt * total_new
        if us_supply:
            can_new = can_i - up_i - pipe_new
            for_new = for_i + up_i + pipe_new
        else:
            can_new = can_i - pipe_i + pipe_new
            for_new = for_i
        return {
            "case": case,
            "label": label,
            "pipeline_multiplier": pipe_scale,
            "pipeline_intensity_tco2e_per_t": pipe_new,
            "chain_intensity_tco2e_per_t": total_new,
            "kino_aski_lifetime_mtco2e": life_new,
            "kino_aski_delta_mtco2e": life_new - kino_life,
            "headline_lifetime_mtco2e": headline_life - kino_life + life_new,
            "headline_delta_mtco2e": life_new - kino_life,
            "kino_can_intensity": can_new,
            "kino_bunk_intensity": bunk_i,
            "kino_for_intensity": for_new,
            "kino_can_lifetime_mtco2e": lng_mt * can_new,
            "kino_can_delta_mtco2e": lng_mt * (can_new - can_i),
            "territory_upstream_pipeline": "FOR" if us_supply else "CAN",
            "illustrative": pipe_scale != 1.0,
        }

    rows.append(_pack("central", "Central (as published)", 1.0, False))
    for mult in ILLUSTRATIVE_MULTIPLIERS:
        rows.append(
            _pack(
                f"A_western_canada_x{mult:g}",
                (
                    f"Case A, Western Canadian supply, pipeline x{mult:g} "
                    f"(illustrative: {mult:g} x {CGL_CALIBRATION_KM:g} km "
                    f"= {mult * CGL_CALIBRATION_KM:,.0f} km, no cited route)"
                ),
                mult,
                False,
            )
        )
    rows.append(
        _pack(
            "B_us_appalachian",
            "Case B, United States supply (intensities unchanged, upstream and "
            "pipeline tagged FOR)",
            1.0,
            True,
        )
    )
    cases = pd.DataFrame(rows)

    # Canada-territorial share of the whole headline under each case.
    headline_can = _headline_can_mt(inputs, panel)
    cases["headline_canada_mtco2e"] = (
        headline_can - lng_mt * can_i + cases["kino_can_lifetime_mtco2e"]
    )
    cases["headline_canada_pct"] = (
        100.0 * cases["headline_canada_mtco2e"] / cases["headline_lifetime_mtco2e"]
    )
    return {
        "cases": cases,
        "kino_lifetime_central": kino_life,
        "headline_lifetime_central": headline_life,
        "lng_lifetime_mt": lng_mt,
        "cgl_km": CGL_CALIBRATION_KM,
        "pipeline_central": pipe_i,
    }


def _stage_i(row, stage: str, inputs: dict) -> float:
    from src.model import _stage_intensity

    return _stage_intensity(stage, row, DEFAULT_SCENARIO, inputs)[0]


def _headline_can_mt(inputs: dict, panel: pd.DataFrame) -> float:
    """Canada-territorial lifetime MtCO2e across the headline scope."""
    total = 0.0
    by_project = (
        panel.loc[panel["scenario"] == DEFAULT_SCENARIO]
        .groupby("project_id")["emissions_mtco2e"]
        .sum()
    )
    for pid, life in by_project.items():
        row = _asset_row(inputs, pid)
        chain_i, _c, _h = _chain_intensity_split(
            row, DEFAULT_SCENARIO, inputs, canada_only=False
        )
        can_i, _c2, _h2 = _chain_intensity_split(
            row, DEFAULT_SCENARIO, inputs, canada_only=True
        )
        total += life * can_i / chain_i
    return total


def format_feedgas_markdown(sens: dict, inputs: dict) -> list[str]:
    cases = sens["cases"]
    lines = []
    lines.append("## Kino Aski feedgas sensitivity (SI only)")
    lines.append("")
    lines.append(
        f"Kino Aski LNG (15 mtpa, Baie-Comeau) has **no stated feedgas route**. "
        f"The register now carries `feedgas_basin` = \"not available\" for it, "
        f"with the two candidate supplies named in `feedgas_basin_note`: "
        f"Western Canadian gas via the TC Energy Canadian Mainline, and United "
        f"States Appalachian gas. The distinction decides both the pipeline "
        f"haul and whether upstream and pipeline emissions are Canada "
        f"territorial. Central factors are untouched and the central case is "
        f"unchanged; this is supplementary information."
    )
    lines.append("")
    lines.append(
        f"**Case A, Western Canadian supply.** Pipeline transport is scaled by "
        f"distance, expressed as multiples of the {sens['cgl_km']:.0f} km "
        f"Coastal GasLink length used only as a yardstick; the "
        f"{sens['pipeline_central']:.3f} tCO2e/t pipeline factor is not "
        f"calibrated on that line. **No cited distance is available**: no route to the "
        f"Quebec north shore is defined, and the CER's pipeline profile for the "
        f"TransCanada Canadian Mainline publishes only a 14,123 km total "
        f"regulated system length covering all segments including deactivated "
        f"and abandoned ones, which is not a route distance - and Baie-Comeau "
        f"is not on the Mainline in any case. Case A is therefore run as an "
        f"**explicit x3 and x5 multiplier band, labelled illustrative**, and "
        f"the gap is recorded on the register's Data Gaps sheet. Territory "
        f"stays CAN."
    )
    lines.append("")
    lines.append(
        "**Case B, United States supply.** Intensities are unchanged - this "
        "model has no US-specific factors and does not invent any - but "
        "upstream and pipeline emissions occur outside Canada and are tagged "
        "FOR instead of CAN."
    )
    lines.append("")
    lines.append(
        "| case | pipeline tCO2e/t | Kino Aski lifetime Mt | headline lifetime Mt | "
        "headline Canada-territorial Mt | headline Canada share |"
    )
    lines.append("|---|---|---|---|---|---|")
    for _, r in cases.iterrows():
        lines.append(
            f"| {r['label']} | {r['pipeline_intensity_tco2e_per_t']:.3f} | "
            f"{r['kino_aski_lifetime_mtco2e']:,.1f} | "
            f"{r['headline_lifetime_mtco2e']:,.1f} | "
            f"{r['headline_canada_mtco2e']:,.1f} | "
            f"{r['headline_canada_pct']:.1f}% |"
        )
    lines.append("")
    b = cases.loc[cases["case"] == "B_us_appalachian"].iloc[0]
    c = cases.loc[cases["case"] == "central"].iloc[0]
    lines.append(
        f"Case B leaves the total unchanged ({b['headline_lifetime_mtco2e']:,.1f} "
        f"Mt) and moves {abs(b['kino_can_delta_mtco2e']):,.1f} Mt out of the "
        f"Canada-territorial column, taking the Canada share from "
        f"{c['headline_canada_pct']:.1f}% to {b['headline_canada_pct']:.1f}%. "
        f"That is the larger of the two effects: which country's gas Kino Aski "
        f"burns matters more to the territorial answer than how far it travels. "
        f"Series: `Outputs/figure_data/sens_kino_aski_feedgas.csv`."
    )
    lines.append("")
    lines.append("### Limitations: feedgas basin and route")
    lines.append("")
    lines.append(
        "**All assets use Western Canadian upstream and pipeline factors.** The "
        "upstream factor is derived from Canada Energy Regulator British "
        "Columbia oil and gas production, processing and transmission "
        "emissions against BC marketable gas, corrected for measured methane. "
        f"The pipeline factor is {float(inputs['factors'].loc['pipeline_transport', 'central']):.3f} "
        "tCO2e/t, cited, from two independent routes that agree to 1.2 per "
        "cent: Liu et al. (2021) on an 1,100 km Alberta line and the CER/ECCC "
        "national pipeline-transport inventory. The British Columbia "
        "assessment of Coastal GasLink implies about 0.094 tCO2e/t at the "
        "line's design capacity; the difference is discussed in the Emission "
        "Factors basis cell and the README. The upstream factor is a British "
        "Columbia figure; the pipeline factor is not. For the seven "
        "Pacific-coast assets the upstream geography is right. "
        "For the two Atlantic projects it is a **substitution**, and the "
        "direction of bias differs:"
    )
    lines.append("")
    lines.append(
        "- **Kino Aski (Baie-Comeau, 15 mtpa).** If the feedgas is Western "
        "Canadian, the upstream factor is right but the pipeline factor is "
        "**too low**, because a haul to the Quebec north shore is several times "
        "the 670 km Coastal GasLink yardstick: the illustrative band above "
        "puts the understatement at roughly "
        f"{cases.loc[cases['case'].str.startswith('A_'), 'kino_aski_delta_mtco2e'].min():,.0f} "
        f"to "
        f"{cases.loc[cases['case'].str.startswith('A_'), 'kino_aski_delta_mtco2e'].max():,.0f} "
        "MtCO2e over the asset's life. If the feedgas is United States "
        "Appalachian, the upstream factor is the wrong jurisdiction entirely - "
        "measured Appalachian methane intensities are generally **higher** than "
        "Montney-area ones, so the factor is again likely too low - and the "
        "territorial attribution is wrong by the whole of upstream and "
        "pipeline. No US factor is substituted, because this model has none."
    )
    lines.append(
        f"- **Fermeuse (Avalon Peninsula, "
        f"{float(_asset_row(inputs, 'fermeuse_energy_flng')['capacity_mtpa']):.1f} mtpa).** "
        "The feedgas is offshore "
        "associated gas from the Jeanne d'Arc Basin, not Western Canadian "
        "pipeline gas. The bias runs the other way on pipeline transport: there "
        "is essentially no onshore transmission haul, so applying the "
        f"{float(inputs['factors'].loc['pipeline_transport', 'central']):.3f} "
        "tCO2e/t pipeline factor **overstates** that stage. Offshore associated "
        "gas production has a different emissions profile from onshore "
        "unconventional production - platform power, flaring and venting rather "
        "than well-pad and gathering methane - and no Canadian offshore factor "
        "was located, so the Western Canadian upstream factor is applied and "
        "the direction of that bias is **not determined**. No factor change is "
        "made for Fermeuse; this is limitations text only."
    )
    lines.append(
        "- **Shipping is now route-scaled** (see the emission factors section), "
        "so the Atlantic projects no longer carry a Pacific shipping distance. "
        "That correction is in the central case; the upstream and pipeline "
        "substitutions above are not."
    )
    lines.append("")
    return lines
