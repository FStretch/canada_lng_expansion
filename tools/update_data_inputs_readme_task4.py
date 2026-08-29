"""Task 4: bring the Data Inputs README into line with route-scaled shipping.

Two rows on the `README` sheet of Canada_LNG_Data_Inputs.xlsx:

- "The result": the asserted territorial shares move from 18.0 / 3.4 / 78.6 to
  18.1 / 3.2 / 78.7 now that shipping is scaled by route distance per asset.
- "Result" (SHIPPING block): the sheet already claimed east-coast projects carry
  lower shipping emissions than west-coast ones. The code applied a flat 0.12 to
  every asset, so the claim and the code disagreed. The code now implements it;
  this row says so.

No emission factor or parameter changes. Run once, from the repository root:

    python tools/update_data_inputs_readme_task4.py
"""

from __future__ import annotations

from pathlib import Path

import openpyxl

BOOK = Path(__file__).resolve().parents[1] / "Inputs" / "Canada_LNG_Data_Inputs.xlsx"

REPLACEMENTS = [
    (
        "18.0 per cent of emissions are Canada territorial",
        "Across the export-chain headline (headline_scope_chains=export; "
        "headline_scope_calc_groups=operating,under_construction,proposed), "
        "18.1 per cent of emissions are Canada territorial, 3.2 per cent are "
        "international bunkers, and 78.7 per cent are foreign territorial. LNG "
        "carrier shipping is itself an international bunker, so it lands "
        "nowhere. These shares are the life-average split; the model asserts "
        "them every run. Shipping is scaled per asset by route_distance_nm / "
        "route_bc_to_northeast_asia_nm, which is what moved the bunkers share "
        "down from 3.4 per cent. Eight non-export assets totalling 242.9 "
        "MtCO2e stay in the register.",
    ),
    (
        "East coast projects therefore carry lower shipping emissions",
        "Baie-Comeau to Rotterdam is about 2,980 nautical miles and Fermeuse "
        "about 2,470, against 3,800 from British Columbia to Asia. East coast "
        "projects therefore carry lower shipping emissions than west coast "
        "ones, and the model implements this: shipping intensity for each "
        "asset is the 0.12 central factor times route_distance_nm / "
        "route_bc_to_northeast_asia_nm. An asset on a chain that includes the "
        "shipping stage with a blank route_distance_nm raises rather than "
        "defaulting to the BC basis. Bunkering has no shipping stage. The "
        "routing factor is not applied to Pacific routes, where the cited "
        "figure is used. The lifecycle comparison in src/lca_comparison.py "
        "deliberately stays on the unscaled BC basis, because the comparator "
        "studies are single-route.",
    ),
]


def main() -> None:
    wb = openpyxl.load_workbook(BOOK)
    ws = wb["README"]
    changed = 0
    for needle, new_text in REPLACEMENTS:
        hit = None
        for row in range(1, ws.max_row + 1):
            cell = ws.cell(row=row, column=2)
            if cell.value and needle in str(cell.value):
                hit = cell
                break
        if hit is None:
            print(f"skip (not found, may already be updated): {needle[:50]}...")
            continue
        hit.value = new_text
        changed += 1
    if changed:
        wb.save(BOOK)
    print(f"updated {changed} README row(s)")


if __name__ == "__main__":
    main()
