"""Report-only parameters not yet on the Data Inputs Parameters sheet.

Inputs remain read-only. Values here are used for figures when the workbook
does not already define the same parameter name. Prefer workbook values when
present. Every key used is written to Outputs/figure_data/ for audit.
"""

from __future__ import annotations

# Defaults for figure construction. Sources are recorded alongside values.
REPORT_PARAM_DEFAULTS: dict[str, dict] = {
    "assumed_first_export_year_if_missing": {
        "value": 2030,
        "unit": "year",
        "source": (
            "Report assumption for trajectory figures when Asset Register "
            "first_export_year is blank (tilbury_phase_2, marinvest_baie_comeau, "
            "summit_lake_pg_lng). Not used in the 40-year average calculation."
        ),
    },
    "tmx_expansion_bpd": {
        "value": 590_000,
        "unit": "bpd",
        "source": (
            "TMX expansion increment commonly cited as 590,000 bpd above the "
            "pre-expansion system; used with tmx_oil_lifecycle_per_barrel for "
            "figure 7. Add to Parameters sheet to override."
        ),
    },
    "alberta_bc_bitumen_pipeline_bpd": {
        "value": 1_000_000,
        "unit": "bpd",
        "source": (
            "Proposed Alberta–BC bitumen pipeline, capacity over 1 million bpd; "
            "formally submitted to the Major Projects Office on 2 July 2026 "
            "(Bruderheim to Delta BC, ~1,200 km, completion targeted 2032–2034). "
            "Floor of 1,000,000 bpd used until a firmer published capacity is "
            "entered on the Parameters sheet. UNVALIDATED."
        ),
        "unvalidated": True,
    },
    "alberta_bc_bitumen_pipeline_label": {
        "value": "Proposed Alberta–BC bitumen pipeline (≥1 Mbpd)",
        "unit": "label",
        "source": "Report label for figure 7.",
        "unvalidated": True,
    },
}


def resolve_report_params(workbook_params: dict) -> tuple[dict, list[dict]]:
    """Merge workbook Parameters over report defaults.

    Returns (resolved_values, audit_rows).
    """
    resolved: dict = {}
    audit: list[dict] = []
    for name, meta in REPORT_PARAM_DEFAULTS.items():
        if name in workbook_params and workbook_params[name] is not None:
            val = workbook_params[name]
            origin = "Parameters sheet"
        else:
            val = meta["value"]
            origin = "report_params default (Inputs unchanged)"
        resolved[name] = val
        audit.append({
            "parameter": name,
            "value": val,
            "unit": meta.get("unit"),
            "source": meta.get("source"),
            "origin": origin,
            "unvalidated": bool(meta.get("unvalidated", False)),
        })
    return resolved, audit
