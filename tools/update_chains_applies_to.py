"""Update the Chains sheet's export `applies_to` capacity after the Discovery removal.

The cell read "100.1 mtpa (14.0 operating, 5.4 under construction, 80.7
proposed)". Discovery LNG went back to cancelled on 1 September 2026, taking
20 mtpa out of proposed, so the export chain now applies to 80.1 mtpa
(14.0 operating, 5.4 under construction, 60.7 proposed). The stale-figure
inventory found this cell; nothing else in the repository still carried the
old capacity as a current figure.

No emission factor, parameter or register value changes. Run once, from the
repository root:

    python tools/update_chains_applies_to.py
"""

from __future__ import annotations

from pathlib import Path

import openpyxl

BOOK = Path(__file__).resolve().parents[1] / "Inputs" / "Canada_LNG_Data_Inputs.xlsx"

OLD = "100.1 mtpa (14.0 operating, 5.4 under construction, 80.7 proposed)"
NEW = "80.1 mtpa (14.0 operating, 5.4 under construction, 60.7 proposed)"


def main() -> None:
    wb = openpyxl.load_workbook(BOOK)
    ws = wb["Chains"]
    hits = 0
    for row in ws.iter_rows():
        for cell in row:
            if isinstance(cell.value, str) and OLD in cell.value:
                cell.value = cell.value.replace(OLD, NEW)
                hits += 1
    if hits:
        wb.save(BOOK)
        print(f"updated {hits} Chains cell(s): {OLD!r} -> {NEW!r}")
    else:
        print("nothing to update (already current)")


if __name__ == "__main__":
    main()
