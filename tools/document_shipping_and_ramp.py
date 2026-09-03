"""Documentation only: the IEA shipping comparison, and the observed Phase 1 ramp.

One-off. No value changes. The model never writes Inputs/; this script does, once.

1. Shipping 0.12 is held. The IEA 2025 figure of 0.18 tCO2e/t is not
   like-for-like and the range_sources cell now says exactly why, so a reviewer
   meeting the IEA number is answered before they ask.

2. The LNG Canada Phase 1 ramp of 0.25 / 0.60 / 0.85 is held, but observed
   throughput data now exists and is recorded against it, so the assumption is
   visibly testable rather than merely asserted.

Run from the repository root:

    python tools/document_shipping_and_ramp.py
"""

from __future__ import annotations

from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Inputs" / "Canada_LNG_Data_Inputs.xlsx"

IEA_URL = (
    "https://iea.blob.core.windows.net/assets/df9b1bed-4e16-4db8-bec5-a5fa117a9130/"
    "AssessingemissionsfromLNGsupplyandabatementoptions.pdf"
)
GLOBE_URL = (
    "https://www.theglobeandmail.com/business/article-"
    "lng-canada-exports-asia-natural-gas-strait-of-hormuz/"
)
GEM_URL = "https://www.gem.wiki/LNG_Canada_Terminal"

SHIPPING_RANGE_SOURCES = (
    "Route-specific range from a peer-reviewed supplier-specific lifecycle "
    "assessment: ocean transport runs 0.05 tCO2e/t on short routes to 0.31 on "
    "long ones, https://pubs.acs.org/doi/10.1021/acssuschemeng.1c03307 . "
    "Methane slip measurement: "
    "https://pubs.acs.org/doi/10.1021/acs.est.2c01383 . "
    "WHY THIS MODEL HOLDS 0.12 AGAINST THE IEA'S 0.18. IEA (2025), Assessing "
    "Emissions from LNG Supply and Abatement Options, p. 15, gives about "
    "3.5 gCO2e/MJ globally and 3.3 gCO2e/MJ for LNG delivered to China, which "
    "at 55 MJ/kg is 0.19 and 0.18 tCO2e/t (" + IEA_URL + "). That is higher "
    "than this model's 0.12, and a reviewer will meet it. Four reasons it is "
    "NOT like-for-like: "
    "(1) DISTANCE - the IEA average round trip is 10,000 km, against the "
    "14,075 km round trip (7,600 nm) this model uses for the British Columbia "
    "to north-east Asia basis, so the IEA figure is for a SHORTER voyage; "
    "(2) FLEET AVERAGE, NOT ROUTE - it averages about 7,000 round trips in "
    "2024 across the world fleet, including Arctic ice-class voyages such as "
    "Yamal to China, rather than describing any single route; "
    "(3) GWP BASIS - the IEA takes 1 t methane as 30 t CO2, against this "
    "model's 29.8, and its methane-slip treatment is fleet-wide rather than "
    "the measured 1.44 uplift used here; "
    "(4) ORIGIN-BLENDED - 'to China' blends US Gulf, Qatari, Australian and "
    "Russian origins, so it carries voyages this model does not run. "
    "THE HONEST STATEMENT OF THE GAP: per kilometre the IEA implies roughly "
    "2.3 times this model's intensity. That is the real disagreement and it is "
    "not resolved by the boundary differences above. The 0.12 is retained "
    "because it is Howarth's figure independently reconstructed from IMO Data "
    "Collection System fleet data on the voyage this model actually runs - "
    "8.50 gCO2 per DWT per nautical mile over a 7,600 nm round trip, converted "
    "to cargo tonnes and uplifted 44 per cent for measured methane slip, "
    "giving 0.110 against the stored 0.120. A route-specific derivation on our "
    "own voyage is preferred to a fleet average on a different one. Recorded "
    "3 September 2026; see also Outputs/benchmark_comparison.csv."
)

RAMP_OBSERVED = (
    "OBSERVED DATA AS AT JUNE 2026, recorded 3 September 2026 so this "
    "assumption is testable rather than merely asserted. The model still uses "
    "the assumed ramp; nothing below has been fed back into it. "
    "First cargo 30 June 2025 from Train 1; Train 2 entered production "
    "November 2025 (GEM, LNG Canada Terminal page, last edited 18 August 2026, "
    + GEM_URL + " ; Norton Rose Fulbright, Canadian LNG industry: 2026 "
    "outlook). Vessel departures 4 in December 2025, 10 in January 2026 and 11 "
    "in February 2026 (Kpler, via Globe and Mail, 18 March 2026, "
    + GLOBE_URL + " ). Approximately 4.6 Mt exported between June 2025 and "
    "mid-March 2026 (RBC Capital Markets, Michael Harvey, same article). "
    "60th cargo mid-March 2026 and approximately 80 cargoes by early May 2026 "
    "(EnergyNow, June 2026). April 2026 was the first month above 1 Mt, and "
    "production reached 1.2 Mt per month by May 2026. "
    "WHAT THE DATA SAYS ABOUT THE ASSUMPTION: against 14 mtpa nameplate, "
    "calendar 2025 ran at roughly 11 per cent of a full year against the "
    "assumed year-one 25 per cent, while April and May 2026 ran at about 86 "
    "and 103 per cent of nameplate against the assumed year-two 60 per cent. "
    "THE AVERAGE IS ABOUT RIGHT; THE SHAPE IS NOT. The model starts too high "
    "and ramps too slowly, and the two errors largely offset over the life. "
    "Retained as a known limitation rather than corrected, because a "
    "single-facility observed profile is not a basis for the generic ramp "
    "applied to every other asset."
)


def _headers(ws) -> dict[str, int]:
    return {
        str(ws.cell(row=1, column=c).value).strip(): c
        for c in range(1, ws.max_column + 1)
        if ws.cell(row=1, column=c).value is not None
    }


def _row_of(ws, headers, key_col, name):
    col = headers[key_col]
    for r in range(2, ws.max_row + 1):
        v = ws.cell(row=r, column=col).value
        if v is not None and str(v).strip() == name:
            return r
    raise KeyError(name)


def main() -> None:
    wb = openpyxl.load_workbook(DATA)

    ef = wb["Emission Factors"]
    eh = _headers(ef)
    r = _row_of(ef, eh, "stage", "shipping")
    ef.cell(row=r, column=eh["range_sources"], value=SHIPPING_RANGE_SOURCES)
    print("shipping range_sources: IEA comparison recorded, value unchanged at 0.12")

    ps = wb["Parameters"]
    ph = _headers(ps)
    for name in (
        "lng_canada_ph1_year_1_utilisation",
        "lng_canada_ph1_year_2_utilisation",
        "lng_canada_ph1_steady_state_utilisation",
    ):
        row = _row_of(ps, ph, "parameter", name)
        ps.cell(row=row, column=ph["notes"], value=RAMP_OBSERVED)
        ps.cell(row=row, column=ph["source_url"], value=GLOBE_URL)
        print(f"{name}: observed data recorded, value unchanged")

    wb.save(DATA)
    print("saved")


if __name__ == "__main__":
    main()
