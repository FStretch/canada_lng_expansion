"""fid_delay band 3 / 5 / 7 -> 4 / 5 / 8, and connect post_fid_to_completion.

One-off. The model never writes Inputs/; this script does, once.

The mid of 5 is unchanged and now carries two independent citations:

  IEA, Global LNG Capacity Tracker: "the long time lag of 4 to 5 years, on
  average, between project FID and completion."
  https://www.iea.org/data-and-statistics/data-tools/global-lng-capacity-tracker

  Rogers, H. (2017), The Forthcoming LNG Supply Wave: A Case of 'Crying Wolf'?,
  Oxford Institute for Energy Studies, Energy Insight 4, February 2017, page 1:
  "Note that the time from FID to project completion is typically 5 years,
  before unforeseen slippage."
  https://www.oxfordenergy.org/wpcms/wp-content/uploads/2017/02/
  The-Forthcoming-LNG-Supply-Wave-OIES-Energy-Insight.pdf

Both quotations were read from the primary sources on 3 September 2026. The
OIES sentence sits on page 1, in a list of factors explaining why LNG capacity
forecasts from 2004-2009 overshot what was actually delivered.

The band becomes asymmetric because slippage does. "Before unforeseen
slippage" means 5 years is a floor-ish central, not a midpoint: LNG projects
run late, not early. A symmetric 3/5/7 implied a project was as likely to be
two years early as two years late, which neither source supports.

post_fid_to_completion = 4.5 rests on the same IEA statement and is read by no
module. It is marked reference-only here rather than left as a second,
disconnected version of the same fact.

Run from the repository root:

    python tools/update_fid_delay_band.py
"""

from __future__ import annotations

from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Inputs" / "Canada_LNG_Data_Inputs.xlsx"

IEA_URL = "https://www.iea.org/data-and-statistics/data-tools/global-lng-capacity-tracker"
OIES_URL = (
    "https://www.oxfordenergy.org/wpcms/wp-content/uploads/2017/02/"
    "The-Forthcoming-LNG-Supply-Wave-OIES-Energy-Insight.pdf"
)

CITATIONS = (
    "IEA, Global LNG Capacity Tracker: 'the long time lag of 4 to 5 years, on "
    "average, between project FID and completion' (" + IEA_URL + "). Rogers, "
    "H. (2017), The Forthcoming LNG Supply Wave: A Case of 'Crying Wolf'?, "
    "Oxford Institute for Energy Studies, Energy Insight 4, February 2017, "
    "page 1: 'Note that the time from FID to project completion is typically 5 "
    "years, before unforeseen slippage' (" + OIES_URL + ")."
)

ASYMMETRY = (
    "THE BAND IS ASYMMETRIC ON PURPOSE. 'Before unforeseen slippage' makes 5 "
    "years a central that slippage moves in one direction only: LNG projects "
    "run late, not early. The OIES sentence appears in a list of factors "
    "explaining why 2004-2009 LNG capacity forecasts overshot what was "
    "delivered. The retired symmetric 3/5/7 implied a project was as likely to "
    "be two years early as two years late, which neither source supports and "
    "which the Australian and US project record contradicts. 4/5/8 keeps the "
    "cited mid, pulls the optimistic tail in to the bottom of the IEA's own "
    "4-to-5 range, and lets the pessimistic tail run a year further."
)

UPDATES = {
    "fid_delay_low": {
        "value": 4,
        "source": (
            "Lower bound of the FID-delay triangle. Set to 4 years, the bottom "
            "of the IEA's stated 4-to-5 year FID-to-completion range: a "
            "project is not credibly faster than the fastest observed average. "
            + CITATIONS + " " + ASYMMETRY
        ),
        "source_url": IEA_URL,
        "notes": "Was 3 (assumed). Raised 3 September 2026.",
    },
    "fid_delay_mid": {
        "value": 5,
        "source": (
            "Delay applied to assets without a confirmed FID, sitting inside "
            "the lifespan window rather than extending it. Value unchanged; "
            "now carries two independent citations. " + CITATIONS + " "
            + ASYMMETRY
        ),
        "source_url": OIES_URL,
        "notes": (
            "Unchanged at 5, so the central case is untouched by the 3 "
            "September 2026 band change. Applied to the seven proposed assets "
            "without FID. post_fid_to_completion = 4.5 rests on the same IEA "
            "statement and is reference-only; this row is the one the model "
            "reads."
        ),
    },
    "fid_delay_high": {
        "value": 8,
        "source": (
            "Upper bound of the FID-delay triangle. Set to 8 years, three "
            "years beyond the cited typical 5, to carry the 'unforeseen "
            "slippage' the OIES source names explicitly. " + CITATIONS + " "
            + ASYMMETRY
        ),
        "source_url": OIES_URL,
        "notes": "Was 7 (assumed, symmetric). Raised 3 September 2026.",
    },
    "post_fid_to_completion": {
        "source": (
            "REFERENCE ONLY - read by no module. Retained because it records "
            "the same IEA statement that supports fid_delay_mid: 'the long "
            "time lag of 4 to 5 years, on average, between project FID and "
            "completion' (" + IEA_URL + "). The model applies fid_delay_mid = "
            "5 rather than this row; the two are not independent facts and "
            "must not be cited as if they were."
        ),
        "source_url": IEA_URL,
        "notes": (
            "Marked reference-only 3 September 2026 so the workbook does not "
            "carry two disconnected versions of one fact. Do not wire this "
            "into the utilisation calculation without retiring fid_delay_mid."
        ),
    },
}


def _headers(ws) -> dict[str, int]:
    return {
        str(ws.cell(row=1, column=c).value).strip(): c
        for c in range(1, ws.max_column + 1)
        if ws.cell(row=1, column=c).value is not None
    }


def main() -> None:
    wb = openpyxl.load_workbook(DATA)
    ws = wb["Parameters"]
    h = _headers(ws)
    for name, fields in UPDATES.items():
        row = None
        for r in range(2, ws.max_row + 1):
            if str(ws.cell(row=r, column=h["parameter"]).value).strip() == name:
                row = r
                break
        if row is None:
            raise KeyError(f"{name} not found")
        old = ws.cell(row=row, column=h["value"]).value
        for key, value in fields.items():
            ws.cell(row=row, column=h[key], value=value)
        new = ws.cell(row=row, column=h["value"]).value
        note = f"{old} -> {new}" if old != new else f"{old} (unchanged)"
        print(f"{name}: {note}")
    wb.save(DATA)
    print("saved")


if __name__ == "__main__":
    main()
