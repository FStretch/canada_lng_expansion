"""Task 7: add `feedgas_basin` and `feedgas_basin_note` to the Asset Register.

One row per in-scope asset, with a matching Asset Sources cell for every row,
Field Definitions entries for both new columns, and Data Gaps rows for what
could not be sourced.

A note on what is and is not asserted here. The task brief expected "Montney"
for the Kitimat cluster. The sources already cited in those rows do not say
that. TC Energy's own Coastal GasLink page and the Province of British
Columbia's Coastal GasLink page both describe the supply only as
"northeastern British Columbia"; the CER market snapshot cited in the LNG
Canada row names no basin; the GEM wiki page gives Dawson Creek as the pipeline
origin and no formation. Northeast BC gas production is overwhelmingly Montney,
but that is an inference, not a citation, so the basin field carries what the
sources support - Western Canada Sedimentary Basin, northeast British Columbia -
and the note records both the delivering pipeline and the fact that no located
source names a producing formation. Blank beats wrong.

Fermeuse is the one asset with a named basin from a proponent statement: the
capacity derivation already cited in its row rests on 9.7 Tcf of offshore
associated gas in the Jeanne d'Arc Basin.

No emission factor, parameter or capacity changes. Run once, from the
repository root:

    python tools/add_feedgas_basin.py
"""

from __future__ import annotations

from pathlib import Path

import openpyxl

BOOK = Path(__file__).resolve().parents[1] / "Inputs" / "Canada_LNG_Asset_Register.xlsx"

NEW_COLUMNS = ("feedgas_basin", "feedgas_basin_note")

WCSB = "Western Canada Sedimentary Basin (northeast British Columbia)"
NA = "not available"

CGL_SOURCE = (
    "TC Energy, Coastal GasLink: "
    "https://www.tcenergy.com/operations/natural-gas/coastal-gaslink/ - "
    "\"delivers 2.1 Bcf/d of natural gas from northeastern British Columbia to "
    "the LNG Canada facility\". Province of British Columbia, Coastal GasLink: "
    "https://www2.gov.bc.ca/gov/content/industry/natural-gas-oil/lng/"
    "connecting-natural-gas-pipelines/coastal-gaslink - \"supply LNG Canada "
    "with natural gas from northeastern British Columbia\". GEM wiki, Coastal "
    "GasLink Pipeline: https://www.gem.wiki/Coastal_GasLink_Pipeline - runs "
    "from Dawson Creek to Kitimat. None of these names a producing formation, "
    "so the basin field stops at the WCSB and the note says so."
)
PRGT_SOURCE = (
    "GEM wiki, Prince Rupert Gas Transmission Pipeline: "
    "https://www.gem.wiki/Prince_Rupert_Gas_Transmission_Pipeline, and the "
    "Supporting Infrastructure sheet of this register (prince_rupert_gas_"
    "transmission, 750 km, under construction, serves Ksi Lisims FLNG). The "
    "line originates in northeast British Columbia. No located source names a "
    "producing formation."
)
FORTIS_SOURCE = (
    "GEM wiki, FortisBC Pipeline: https://www.gem.wiki/FortisBC_Pipeline, and "
    "the Supporting Infrastructure sheet of this register (fortisbc_eagle_"
    "mountain, 47 km, serves Woodfibre LNG). Feedgas reaches the FortisBC "
    "system from northeast British Columbia. No located source names a "
    "producing formation."
)
FERMEUSE_SOURCE = (
    "Fermeuse Energy news release, 2 September 2025, as already cited in this "
    "row's capacity_basis: the project would develop 9.7 trillion cubic feet "
    "of offshore associated gas in the Jeanne d'Arc Basin. Corroborated by "
    "CBC, 10 February 2026: "
    "https://www.cbc.ca/news/canada/newfoundland-labrador/"
    "fermeuse-lng-proposed-project-9.7082941"
)
KINO_SOURCE = (
    "not available. Kino Aski Inc. news release, 17 August 2026, "
    "https://www.newswire.ca/news-releases/first-nations-lead-kino-aski-lng-a-"
    "major-canadian-energy-project-800865754.html states no feedgas route or "
    "supply basin. No regulatory process has begun."
)

ROWS = {
    "lng_canada_phase_1": (
        WCSB,
        "Delivered by Coastal GasLink (670 km, Dawson Creek to Kitimat), per "
        "the Supporting Infrastructure sheet. TC Energy and the Province of "
        "British Columbia describe the supply only as northeastern British "
        "Columbia and name no producing formation; the Montney is the dominant "
        "play in that area but no located source ties it to this pipeline, so "
        "the formation is not asserted.",
        CGL_SOURCE,
    ),
    "lng_canada_phase_2": (
        WCSB,
        "Same feedgas route as Phase 1: Coastal GasLink, requiring the proposed "
        "expansion recorded on the Supporting Infrastructure sheet. Formation "
        "not named by any located source.",
        CGL_SOURCE,
    ),
    "cedar_lng": (
        WCSB,
        "Draws on Coastal GasLink via the 8 km Cedar LNG Pipeline connector, "
        "per the Supporting Infrastructure sheet. Formation not named by any "
        "located source.",
        CGL_SOURCE,
    ),
    "ksi_lisims_lng": (
        WCSB,
        "Delivered by Prince Rupert Gas Transmission (750 km, under "
        "construction), per the Supporting Infrastructure sheet. Formation not "
        "named by any located source.",
        PRGT_SOURCE,
    ),
    "woodfibre_lng": (
        WCSB,
        "Delivered by the FortisBC Eagle Mountain line (47 km), per the "
        "Supporting Infrastructure sheet, which draws on the FortisBC "
        "transmission system. Formation not named by any located source.",
        FORTIS_SOURCE,
    ),
    "summit_lake_pg_lng": (
        WCSB,
        "Prince George, British Columbia. No dedicated feedgas pipeline is "
        "identified in the register; supply would come off the existing "
        "British Columbia transmission system. Formation not named by any "
        "located source.",
        "not available - no proponent or regulator statement of feedgas supply "
        "was located. The assessment the proponent asked to suspend is at "
        "https://projects.eao.gov.bc.ca/p/65c661a8399db00022d48849/"
        "project-details",
    ),
    "discovery_t1t4": (
        NA,
        "Campbell River, British Columbia. No feedgas pipeline is identified "
        "for this project in GEM or in any located filing. This is the least "
        "verified asset in the register.",
        "not available",
    ),
    "kanata_lng": (
        NA,
        "Prince Rupert, British Columbia. The project is at memorandum of "
        "understanding stage and no feedgas route or supply basin has been "
        "stated.",
        "not available",
    ),
    "marinvest_baie_comeau": (
        NA,
        "The feedgas route is undefined. The two candidate supplies are "
        "Western Canadian gas reaching the Quebec north shore via the TC "
        "Energy Canadian Mainline, and United States Appalachian gas. Neither "
        "is stated by the proponent. This distinction is the subject of the "
        "Kino Aski feedgas sensitivity, because it decides both the pipeline "
        "transport distance and whether upstream and pipeline emissions are "
        "Canada territorial or foreign.",
        KINO_SOURCE,
    ),
    "fermeuse_energy_flng": (
        "Jeanne d'Arc Basin (offshore Newfoundland)",
        "Offshore associated gas, not Western Canadian pipeline gas. From the "
        "proponent statement already cited for this row's capacity: 9.7 "
        "trillion cubic feet of offshore associated gas in the Jeanne d'Arc "
        "Basin. The model nonetheless applies the Western Canadian upstream "
        "and pipeline factors to this asset; see the limitations section of "
        "RESULTS_SUMMARY.",
        FERMEUSE_SOURCE,
    ),
}

FIELD_DEFS = [
    (
        "feedgas_basin",
        "Asset Register",
        "The producing basin the terminal's feedgas comes from, as far as "
        "cited sources support. Blank or 'not available' where no source "
        "states it.",
        "-",
        "sourced",
        None,
    ),
    (
        "feedgas_basin_note",
        "Asset Register",
        "How the feedgas reaches the terminal, and what the cited sources do "
        "and do not say about the producing formation.",
        "-",
        "sourced",
        None,
    ),
]

DATA_GAPS = [
    (
        "feedgas_basin",
        "All six British Columbia export assets",
        "Filled at basin level only",
        "TC Energy, the Province of British Columbia, the CER market snapshot "
        "and GEM all describe west coast LNG feedgas as coming from "
        "northeastern British Columbia and none names a producing formation. "
        "Northeast BC production is overwhelmingly Montney, but that inference "
        "is not written into the register.",
        "A proponent, CER or BC Energy Regulator statement naming the "
        "producing formation for a specific feedgas pipeline.",
        "low - the upstream factor is derived from provincial BC totals, not "
        "from a formation-specific figure, so the model does not depend on it",
    ),
    (
        "feedgas_basin",
        "Kino Aski LNG (Baie-Comeau)",
        "not available",
        "The proponent has stated no feedgas route or supply basin and no "
        "regulatory process has begun. The two candidates - Western Canadian "
        "gas via the TC Energy Mainline, and United States Appalachian gas - "
        "differ both in pipeline transport distance and in whether upstream "
        "and pipeline emissions are Canada territorial.",
        "A filed project description or regulatory application stating the "
        "feedgas source and route.",
        "high - decides 15 mtpa of territorial attribution; run as an explicit "
        "sensitivity in the meantime",
    ),
    (
        "pipeline route distance",
        "Kino Aski LNG (Baie-Comeau), Western Canadian supply case",
        "Illustrative multiplier band, not a distance",
        "No published route distance exists for Western Canadian gas to the "
        "Quebec north shore, because no such route is defined. The CER "
        "pipeline profile for the TransCanada Canadian Mainline publishes only "
        "a total regulated system length of 14,123 km covering all segments "
        "including deactivated and abandoned ones "
        "(https://apps.cer-rec.gc.ca/PPS/en/pipeline-profiles/"
        "transcanada-canadian-mainline-tc), which is not a route distance, and "
        "Baie-Comeau is not on the Mainline in any case.",
        "A filed route for the feedgas pipeline, or a published Alberta-border "
        "to Quebec-north-shore sailing of the Mainline corridor.",
        "high - the sensitivity uses an explicit x3 and x5 band against the "
        "670 km Coastal GasLink calibration, labelled illustrative",
    ),
]


def _col(ws, name: str, create: bool = False) -> int:
    for c in range(1, ws.max_column + 1):
        if str(ws.cell(row=1, column=c).value).strip() == name:
            return c
    if not create:
        raise KeyError(f"Column '{name}' not found on '{ws.title}'.")
    c = ws.max_column + 1
    ws.cell(row=1, column=c, value=name)
    return c


def _row(ws, pid: str) -> int:
    pid_col = _col(ws, "project_id")
    for r in range(2, ws.max_row + 1):
        if str(ws.cell(row=r, column=pid_col).value).strip() == pid:
            return r
    raise KeyError(f"project_id '{pid}' not found on '{ws.title}'.")


def main() -> None:
    wb = openpyxl.load_workbook(BOOK)
    reg, src = wb["Asset Register"], wb["Asset Sources"]

    reg_cols = {n: _col(reg, n, create=True) for n in NEW_COLUMNS}
    src_cols = {n: _col(src, n, create=True) for n in NEW_COLUMNS}

    # Every register row gets a source cell, not just the populated ones.
    pid_col = _col(reg, "project_id")
    src_pid_col = _col(src, "project_id")
    for r in range(2, reg.max_row + 1):
        pid = reg.cell(row=r, column=pid_col).value
        if pid is None:
            continue
        pid = str(pid).strip()
        basin, note, source = ROWS.get(
            pid,
            (
                None,
                None,
                "not available - asset is inactive or carries no lifecycle "
                "chain, so no feedgas basin was researched",
            ),
        )
        if basin is not None:
            reg.cell(row=r, column=reg_cols["feedgas_basin"], value=basin)
            reg.cell(row=r, column=reg_cols["feedgas_basin_note"], value=note)
        sr = None
        for rr in range(2, src.max_row + 1):
            if str(src.cell(row=rr, column=src_pid_col).value).strip() == pid:
                sr = rr
                break
        if sr is None:
            continue
        src.cell(row=sr, column=src_cols["feedgas_basin"], value=source)
        src.cell(
            row=sr,
            column=src_cols["feedgas_basin_note"],
            value=source if basin is not None else "not available",
        )

    fd = wb["Field Definitions"]
    have_fd = {
        str(fd.cell(row=r, column=1).value).strip() for r in range(2, fd.max_row + 1)
    }
    row = fd.max_row + 1
    for values in FIELD_DEFS:
        if values[0] in have_fd:
            continue
        for col, value in enumerate(values, start=1):
            if value is not None:
                fd.cell(row=row, column=col, value=value)
        row += 1

    gaps = wb["Data Gaps"]
    have_gaps = {
        (
            str(gaps.cell(row=r, column=1).value).strip(),
            str(gaps.cell(row=r, column=2).value).strip(),
        )
        for r in range(2, gaps.max_row + 1)
    }
    row = gaps.max_row + 1
    for values in DATA_GAPS:
        if (values[0], values[1]) in have_gaps:
            continue
        for col, value in enumerate(values, start=1):
            gaps.cell(row=row, column=col, value=value)
        row += 1

    wb.save(BOOK)
    print(f"added {NEW_COLUMNS} to Asset Register and Asset Sources")
    print(f"populated {len(ROWS)} in-scope rows; Field Definitions and Data Gaps updated")


if __name__ == "__main__":
    main()
