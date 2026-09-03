"""upstream_ch4_share 0.30 -> 0.25, on the Johnson et al. (2023) bracket.

One-off. The model never writes Inputs/; this script does, once.

Johnson, M.R., Conrad, B.M., Tyner, D.R. (2023), "Creating measurement-based
oil and gas sector methane inventories using source-resolved aerial surveys",
Communications Earth & Environment 4, doi 10.1038/s43247-023-00769-7, brackets
the British Columbia upstream methane share at roughly 18-34%, centring near
25%. The retired 0.30 sat high in that bracket without a reason for sitting
high.

Also updates near_term_methane_gwp20, which is derived FROM the share and
must move with it: the methane portion of the inventory factor, corrected by
1.5 and re-weighted at GWP20/GWP100, over an unchanged non-methane portion.

Run from the repository root:

    python tools/update_ch4_share.py
"""

from __future__ import annotations

from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Inputs" / "Canada_LNG_Data_Inputs.xlsx"

JOHNSON = "https://doi.org/10.1038/s43247-023-00769-7"

SHARE = 0.25
INV = 0.22
CORRECTION = 1.5
GWP20, GWP100 = 82.5, 29.8

# 0.22 x 0.75 + 0.22 x 0.25 x 1.5 x (82.5/29.8)
GWP20_FACTOR = INV * (1 - SHARE) + INV * SHARE * CORRECTION * (GWP20 / GWP100)

SOURCE = (
    "Share of upstream oil and gas emissions that is methane rather than "
    "carbon dioxide. Required to apply the measurement correction and the "
    "GWP20 uplift to the methane portion only. DERIVED, 3 September 2026, "
    "from Johnson, Conrad & Tyner (2023), Communications Earth & Environment, "
    + JOHNSON
    + " , which reports for British Columbia in 2021: total measurement-based "
    "upstream oil and gas methane of 144.5 kt/y; an upstream methane intensity "
    "of marketed natural gas of 0.38% (95% CI 0.33-0.44%, SI section S3); and "
    "that this measurement-based inventory is nominally 1.7 times the official "
    "ECCC bottom-up figure (range 1.5-2.0). "
    "ROUTE A, intensity: 0.38% / 1.7 = 0.224% official-basis intensity; per "
    "tonne of marketed gas that is 0.00224 t CH4, which at GWP100 29.8 is "
    "0.0666 tCO2e, or 30.3% of the 0.22 inventory_as_reported upstream factor. "
    "ROUTE B, absolute: 144.5 / 1.7 = 85.0 kt CH4 official basis = 2.53 "
    "MtCO2e at 29.8; the 0.22 factor over 63 bcm (45.7 Mt LNG-equivalent at "
    "1.38 bcm per mtpa) implies 10.04 MtCO2e of upstream emissions net of "
    "transmission, so the share is 25.2%. "
    "BRACKET: across the 1.5-2.0 correction range and AR5 (25) versus AR6 "
    "(29.8) methane GWP vintages the two routes span roughly 18% to 34% and "
    "centre near 25%. 0.25 is adopted as the centre of that bracket, "
    "replacing an assumed 0.30 which sat high in it without a stated reason. "
    "Still a judgement within a bracket rather than a single reported figure, "
    "so the type stays assumption."
)

NOTES = (
    "DO NOT substitute the national fugitives share. ECCC's 2026 executive "
    "summary reports 46 MtCO2e of oil and gas fugitive methane within roughly "
    "66 MtCO2e of total Fugitive Sources, a share near 70%. This model's "
    "upstream stage covers production and processing in total, INCLUDING "
    "stationary combustion and flaring, which are nearly all CO2. Applying a "
    "fugitives-only share here would overstate methane by roughly a factor of "
    "two. Canada's NIR gives about 20% for the oil and gas sector nationally, "
    "but that includes oil sands, which are far more CO2-intensive than gas "
    "production. "
    "WHAT THIS VALUE DRIVES: the CO2 floor in the per-gas split "
    "(inventory_as_reported x (1 - share) = 0.165 at 0.25, was 0.154 at 0.30), "
    "and through it lifetime_co2_only_mt, lifetime_ch4_kt and the SC-CH4 "
    "damages line; and the near_term_methane_gwp20 scenario factor. It does "
    "NOT drive the measurement_central 0.25 or measurement_high 0.26 upstream "
    "factors, which are stored values on the Scenarios sheet: 0.22 x "
    "(1 - s + 1.5s) is 0.2530 at s=0.30 and 0.2475 at s=0.25, both rounding "
    "to the stored 0.25. The headline lifetime, peak and territorial split are "
    "therefore unchanged by this move. "
    "OTHER ROUTES ATTEMPTED 3 September 2026 and not closed: the ECCC National "
    "Inventory Report Part 3 provincial tables (category 1.B.2 for British "
    "Columbia) exist but are served through a JavaScript data-mart portal "
    "rather than a direct download; the UNFCCC Common Reporting Tables for "
    "Canada are the route that would work. The BC Provincial Inventory "
    "methodology report confirms upstream fugitives are Tier 3 bottom-up "
    "facility by facility, so the underlying data distinguishes gases even "
    "though the published provincial tables are CO2e only."
)

GWP20_BAND = f"upstream {GWP20_FACTOR:.3f}"
GWP20_RAMP = (
    "x1.5 on the methane portion of the inventory, then GWP20/GWP100 "
    "(82.5/29.8) on that methane portion only"
)
GWP20_NOTES_A = (
    "Non-methane portion of inventory_as_reported (0.22 x 0.75 = 0.165) is "
    "unchanged. Methane portion is inventory x upstream_ch4_share x "
    "upstream_measurement_correction x (gwp20_ch4 / gwp100_ch4). Depends on "
    "the methane share of 0.25. Was 0.428 at a share of 0.30, and 0.33 before "
    "that (= 0.22 x 1.5 on the whole factor, which treated all upstream as "
    "methane)."
)
GWP20_NOTES_B = (
    f"Result {GWP20_FACTOR:.3f} depends on upstream_ch4_share = 0.25, itself "
    "the centre of the 18-34% Johnson et al. bracket. Pipeline methane is not "
    "re-weighted: no pipeline methane share exists."
)


def _headers(ws) -> dict[str, int]:
    return {
        str(ws.cell(row=1, column=c).value).strip(): c
        for c in range(1, ws.max_column + 1)
        if ws.cell(row=1, column=c).value is not None
    }


def main() -> None:
    wb = openpyxl.load_workbook(DATA)

    ps = wb["Parameters"]
    ph = _headers(ps)
    row = None
    for r in range(2, ps.max_row + 1):
        if str(ps.cell(row=r, column=ph["parameter"]).value).strip() == "upstream_ch4_share":
            row = r
            break
    if row is None:
        raise KeyError("upstream_ch4_share not found")
    old = ps.cell(row=row, column=ph["value"]).value
    ps.cell(row=row, column=ph["value"], value=SHARE)
    ps.cell(row=row, column=ph["source"], value=SOURCE)
    ps.cell(row=row, column=ph["source_url"], value=JOHNSON)
    ps.cell(row=row, column=ph["notes"], value=NOTES)
    print(f"upstream_ch4_share {old} -> {SHARE}")

    sc = wb["Scenarios"]
    sh = _headers(sc)
    srow = None
    for r in range(2, sc.max_row + 1):
        v = sc.cell(row=r, column=sh["name"]).value
        if v is not None and str(v).strip() == "near_term_methane_gwp20":
            srow = r
            break
    if srow is None:
        raise KeyError("near_term_methane_gwp20 not found")
    old_band = sc.cell(row=srow, column=sh["projects_or_band"]).value
    sc.cell(row=srow, column=sh["projects_or_band"], value=GWP20_BAND)
    sc.cell(row=srow, column=sh["ramp_or_multiplier"], value=GWP20_RAMP)
    sc.cell(row=srow, column=sh["notes_or_electrification"], value=GWP20_NOTES_A)
    sc.cell(row=srow, column=sh["notes"], value=GWP20_NOTES_B)
    print(f"near_term_methane_gwp20 {old_band!r} -> {GWP20_BAND!r}")

    wb.save(DATA)
    print("saved")


if __name__ == "__main__":
    main()
