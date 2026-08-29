"""Liquefaction drive-type sensitivity (supplementary information only).

The central case runs gas turbine drive at 0.29 tCO2e per tonne LNG for every
terminal, for its whole operating life, and that does not change here. The
0.29 assertion in build_results.py stays. The existing electrification
appendix (`src.model.electrification_counterfactual`, figure 8, 0.12 versus
0.29) is left exactly as it is; this is a separate, differently sourced case.

Two figures come from the British Columbia Environmental Assessment Office's
assessment of Ksi Lisims LNG:

    liquefaction_electric_drive_gas_generation = 0.156   Alternative Case,
                                                         gas-fired power barges
    liquefaction_electric_drive_grid           = 0.021   Base Case, grid supply

**Boundary caveat, carried into every output.** Both are the facility's total
intensity **including marine sources**, not the liquefaction stage alone. The
0.29 they are compared against is a liquefaction-stage factor. The comparison
is therefore approximate and is labelled as such.

Scope: Ksi Lisims, where the figures are sourced, and Cedar, on the stated
**assumption** that it belongs to the same floating-LNG electric-drive class.
No other terminal is touched.
"""

from __future__ import annotations

import pandas as pd

from src.inputs import DEFAULT_SCENARIO, get_param
from src.trajectories import _chain_intensity_split, panel_lifetime_mt

SOURCED_ID = "ksi_lisims_lng"
ASSUMED_ID = "cedar_lng"
CASES = (
    (
        "electric_drive_gas_generation",
        "liquefaction_electric_drive_gas_generation",
        "Alternative Case, gas-fired power barges (BC EAO Ksi Lisims)",
    ),
    (
        "electric_drive_grid",
        "liquefaction_electric_drive_grid",
        "Base Case, grid supply (BC EAO Ksi Lisims)",
    ),
)
BOUNDARY_NOTE = (
    "The two drive figures are facility total intensity including marine "
    "sources, not the liquefaction stage alone; 0.29 is a liquefaction-stage "
    "factor. The comparison is approximate."
)


def _row(inputs: dict, project_id: str):
    sl = inputs["assets"].loc[inputs["assets"]["project_id"] == project_id]
    if len(sl) != 1:
        raise KeyError(f"Expected exactly one register row for {project_id!r}.")
    return sl.iloc[0]


def run_drive_sensitivity(inputs: dict, panel: pd.DataFrame) -> dict:
    """Ksi Lisims (sourced) and Cedar (assumed) at each electric-drive figure."""
    params = inputs["params"]
    gas_i = float(inputs["factors"].loc["liquefaction", "central"])
    if abs(gas_i - 0.29) > 1e-12:
        raise AssertionError(
            f"Liquefaction central is {gas_i}, not 0.29. The drive sensitivity "
            "is defined against the 0.29 central and will not run if it moves."
        )
    headline_life = panel_lifetime_mt(panel, DEFAULT_SCENARIO)

    targets = [
        (SOURCED_ID, "sourced (BC EAO assessment is for this facility)"),
        (
            ASSUMED_ID,
            "assumption: same floating-LNG electric-drive class as Ksi Lisims; "
            "no Cedar-specific figure was located",
        ),
    ]

    # Lifetime tonnes of LNG behind each asset's panel total, so an intensity
    # change can be applied without re-running the panel.
    meta = {}
    headline_can = 0.0
    for pid in panel.loc[panel["scenario"] == DEFAULT_SCENARIO, "project_id"].unique():
        row = _row(inputs, pid)
        total_i, _c, _h = _chain_intensity_split(
            row, DEFAULT_SCENARIO, inputs, canada_only=False
        )
        can_i, _c2, _h2 = _chain_intensity_split(
            row, DEFAULT_SCENARIO, inputs, canada_only=True
        )
        life = panel_lifetime_mt(panel, DEFAULT_SCENARIO, project_id=pid)
        meta[pid] = {"total_i": total_i, "can_i": can_i, "lng_mt": life / total_i}
        headline_can += life * can_i / total_i

    rows = [{
        "case": "central",
        "label": "Central: gas turbine 0.29 for every terminal",
        "liquefaction_intensity": gas_i,
        "parameter": "Emission Factors:central:liquefaction",
        "applies_to": "all terminals",
        "basis": "central case, unchanged",
        "headline_lifetime_mtco2e": headline_life,
        "headline_delta_mtco2e": 0.0,
        "headline_canada_mtco2e": headline_can,
        "headline_canada_delta_mtco2e": 0.0,
        "boundary_note": "liquefaction stage only",
    }]

    for case, param_name, basis in CASES:
        value = float(get_param(params, param_name))
        delta_i = value - gas_i
        total_delta = 0.0
        for pid, _why in targets:
            total_delta += meta[pid]["lng_mt"] * delta_i
        rows.append({
            "case": case,
            "label": f"{basis}, applied to Ksi Lisims and Cedar",
            "liquefaction_intensity": value,
            "parameter": f"Parameters:{param_name}",
            "applies_to": (
                f"{SOURCED_ID} (sourced); {ASSUMED_ID} (assumption: same FLNG "
                f"electric-drive class)"
            ),
            "basis": basis,
            "headline_lifetime_mtco2e": headline_life + total_delta,
            "headline_delta_mtco2e": total_delta,
            # Liquefaction is CAN-tagged on every chain that includes it, so
            # the whole delta lands in Canada territorial.
            "headline_canada_mtco2e": headline_can + total_delta,
            "headline_canada_delta_mtco2e": total_delta,
            "boundary_note": BOUNDARY_NOTE,
        })

    per_asset = []
    for case, param_name, basis in CASES:
        value = float(get_param(params, param_name))
        for pid, why in targets:
            per_asset.append({
                "case": case,
                "project_id": pid,
                "evidence": why,
                "liquefaction_intensity": value,
                "lifetime_delta_mtco2e": meta[pid]["lng_mt"] * (value - gas_i),
                "canada_delta_mtco2e": meta[pid]["lng_mt"] * (value - gas_i),
            })

    return {
        "cases": pd.DataFrame(rows),
        "by_asset": pd.DataFrame(per_asset),
        "gas_intensity": gas_i,
        "headline_lifetime_central": headline_life,
        "headline_canada_central": headline_can,
    }


def format_drive_markdown(sens: dict) -> list[str]:
    cases = sens["cases"]
    lines = []
    lines.append("## Liquefaction drive-type sensitivity (SI only)")
    lines.append("")
    lines.append(
        f"Central liquefaction stays **{sens['gas_intensity']:.2f}** tCO2e per "
        f"tonne LNG (gas turbine drive) for every terminal, and the run still "
        f"asserts it. Two electric-drive figures from the British Columbia "
        f"Environmental Assessment Office's assessment of Ksi Lisims LNG "
        f"(7 August 2025, Canadian Impact Assessment Registry document "
        f"163192E, pages 847 to 848) are applied as a sensitivity: **0.156** "
        f"for the Alternative Case with gas-fired power barges, and **0.021** "
        f"for the Base Case on grid supply."
    )
    lines.append("")
    lines.append(
        f"**Boundary caveat.** {BOUNDARY_NOTE} Both parameter rows on the "
        f"Parameters sheet carry the same note."
    )
    lines.append("")
    lines.append(
        "Scope: **Ksi Lisims**, where the figures are sourced, and **Cedar**, "
        "on the stated **assumption** that it belongs to the same floating-LNG "
        "electric-drive class - no Cedar-specific figure was located. No other "
        "terminal is touched. The existing electrification appendix (0.12 "
        "versus 0.29, figure 8) is unchanged and is a separate comparator."
    )
    lines.append("")
    lines.append(
        "| case | liquefaction tCO2e/t | headline lifetime Mt | delta Mt | "
        "headline Canada-territorial Mt | Canada delta Mt |"
    )
    lines.append("|---|---|---|---|---|---|")
    for _, r in cases.iterrows():
        lines.append(
            f"| {r['label']} | {r['liquefaction_intensity']:.3f} | "
            f"{r['headline_lifetime_mtco2e']:,.1f} | "
            f"{r['headline_delta_mtco2e']:+,.1f} | "
            f"{r['headline_canada_mtco2e']:,.1f} | "
            f"{r['headline_canada_delta_mtco2e']:+,.1f} |"
        )
    lines.append("")
    lines.append(
        "Liquefaction is CAN-tagged on every chain that includes it, so the "
        "whole delta lands in the Canada-territorial column: the total and the "
        "Canada figure move by the same amount. Per-asset split: "
        "`Outputs/figure_data/sens_liquefaction_drive.csv`."
    )
    lines.append("")
    return lines
