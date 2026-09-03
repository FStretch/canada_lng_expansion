"""Report-only parameters not yet on the Data Inputs Parameters sheet.

The placeholder first-export year now lives on the Parameters sheet
(`assumed_first_export_year_if_missing`). Remaining keys here are figure
comparators (TMX expansion, Alberta–BC bitumen). Prefer workbook values
when present. Every key used is written to Outputs/figure_data/ for audit.
"""

from __future__ import annotations

# Defaults for figure construction. Sources are recorded alongside values.
REPORT_PARAM_DEFAULTS: dict[str, dict] = {
    "tmx_expansion_bpd": {
        "value": 590_000,
        "unit": "bpd",
            "source": (
                "TMX expansion increment: expanded-system 890,000 bpd less the "
                "pre-expansion ~300,000 bpd. Prefer the Parameters-sheet value."
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
