"""Task 9: add `gem_status_verbatim` and `gem_status_date` to the Asset Register.

Each value is read from that row's own `gem_wiki_url` and recorded verbatim.
`gem_status_date` is the GEM page's last-modified date, which is what the page
offers; it is not a GEM-asserted "as of" date and the Field Definitions row
says so.

Assets with no `gem_wiki_url` get "not available": Kanata LNG (added from
proponent sources, not in GEM), Kino Aski LNG, and Summit Lake PG LNG. Assets
outside the headline export scope were not researched and are left blank with
"not available" rather than guessed.

FINDING recorded rather than acted on: GEM's Discovery LNG Terminal page reads
"cancelled (inferred 4 y)". The register classes Discovery as
proposed / early_proposed, and it is 2,043.9 MtCO2e, about 22 per cent of the
headline lifetime total. This script records the verbatim status and adds a
Data Gaps row. It does **not** change calc_group or tier: that is a scope
decision for the authors, not a side effect of a data-capture task.

Run once, from the repository root:

    python tools/add_gem_status_verbatim.py
"""

from __future__ import annotations

from pathlib import Path

import openpyxl

BOOK = Path(__file__).resolve().parents[1] / "Inputs" / "Canada_LNG_Asset_Register.xlsx"

NEW_COLUMNS = ("gem_status_verbatim", "gem_status_date")

# (verbatim status, page last-modified date, page url)
READ = {
    "lng_canada_phase_1": (
        "operating",
        "2026-08-28",
        "https://www.gem.wiki/LNG_Canada_Terminal",
    ),
    "lng_canada_phase_2": (
        "proposed",
        "2026-08-28",
        "https://www.gem.wiki/LNG_Canada_Terminal",
    ),
    "cedar_lng": (
        "construction",
        "2026-08-28",
        "https://www.gem.wiki/Cedar_FLNG_Terminal",
    ),
    "woodfibre_lng": (
        "construction",
        "2026-08-28",
        "https://www.gem.wiki/Woodfibre_LNG_Terminal",
    ),
    "ksi_lisims_lng": (
        "proposed",
        "2026-08-28",
        "https://www.gem.wiki/Ksi_Lisims_FLNG_Terminal",
    ),
    "fermeuse_energy_flng": (
        "proposed",
        "2026-08-28",
        "https://www.gem.wiki/Fermeuse_Energy_FLNG_Terminal",
    ),
    "discovery_t1t4": (
        "cancelled (inferred 4 y)",
        "2026-08-29",
        "https://www.gem.wiki/Discovery_LNG_Terminal",
    ),
}

NOT_IN_GEM = {
    "marinvest_baie_comeau": (
        "not available - Kino Aski LNG has no GEM entry; the register carries "
        "no gem_wiki_url for it"
    ),
    "kanata_lng": (
        "not available - Kanata LNG was added from proponent sources in June "
        "2026 and is not in GEM"
    ),
    "summit_lake_pg_lng": (
        "not available - no gem_wiki_url in the register; the project is "
        "tracked through NRCan, IAAC and the BC EAO instead"
    ),
}

OUT_OF_SCOPE_NOTE = (
    "not available - outside the headline export scope; the GEM page was not "
    "read for this row"
)

FIELD_DEFS = [
    (
        "gem_status_verbatim",
        "Asset Register",
        "The status string on this row's GEM wiki page, quoted exactly as "
        "written. Not normalised and not reconciled with the register's own "
        "status, tier or calc_group; where the two disagree that is a finding, "
        "not an error to be smoothed over.",
        "-",
        "sourced",
        None,
    ),
    (
        "gem_status_date",
        "Asset Register",
        "The GEM page's last-modified date when the status was read. It is the "
        "page's edit date, not a GEM-asserted 'status as of' date.",
        "date",
        "sourced",
        None,
    ),
]

DATA_GAPS = [
    (
        "gem_status_verbatim",
        "Discovery LNG",
        "DISAGREEMENT - GEM says cancelled",
        "GEM's Discovery LNG Terminal page reads \"cancelled (inferred 4 y)\" "
        "as of its 29 August 2026 edit. This register classes Discovery as "
        "proposed / early_proposed, having moved it from inactive pending "
        "verification, and it contributes 2,043.9 MtCO2e, about 22 per cent of "
        "the headline lifetime total. No current filing or proponent activity "
        "was located in the August 2026 review. The verbatim GEM status is now "
        "recorded; the classification is not changed here.",
        "A proponent statement or regulatory filing either confirming the "
        "project is live or confirming it is cancelled. Either resolves it.",
        "high - 22 per cent of the headline total rests on a classification "
        "GEM now contradicts",
    ),
    (
        "gem_status_verbatim",
        "Kino Aski LNG, Kanata LNG, Summit Lake PG LNG",
        "not available",
        "None of the three has a GEM entry. Kanata was added from proponent "
        "sources in June 2026; Kino Aski has begun no regulatory process; "
        "Summit Lake is tracked through NRCan, IAAC and the BC EAO.",
        "A GEM Global Gas Infrastructure Tracker entry for any of the three.",
        "low - the register does not depend on GEM for these rows",
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


def main() -> None:
    wb = openpyxl.load_workbook(BOOK)
    reg, src = wb["Asset Register"], wb["Asset Sources"]
    reg_cols = {n: _col(reg, n, create=True) for n in NEW_COLUMNS}
    src_cols = {n: _col(src, n, create=True) for n in NEW_COLUMNS}
    pid_col = _col(reg, "project_id")
    src_pid_col = _col(src, "project_id")

    src_rows = {}
    for r in range(2, src.max_row + 1):
        pid = src.cell(row=r, column=src_pid_col).value
        if pid is not None:
            src_rows[str(pid).strip()] = r

    n_read = 0
    for r in range(2, reg.max_row + 1):
        pid = reg.cell(row=r, column=pid_col).value
        if pid is None:
            continue
        pid = str(pid).strip()
        if pid in READ:
            status, date, url = READ[pid]
            reg.cell(row=r, column=reg_cols["gem_status_verbatim"], value=status)
            reg.cell(row=r, column=reg_cols["gem_status_date"], value=date)
            source = (
                f"GEM wiki, read {date}: {url} - status field quoted verbatim. "
                f"gem_status_date is the page's last-modified date."
            )
            n_read += 1
        elif pid in NOT_IN_GEM:
            source = NOT_IN_GEM[pid]
        else:
            source = OUT_OF_SCOPE_NOTE
        sr = src_rows.get(pid)
        if sr is None:
            continue
        src.cell(row=sr, column=src_cols["gem_status_verbatim"], value=source)
        src.cell(row=sr, column=src_cols["gem_status_date"], value=source)

    fd = wb["Field Definitions"]
    have = {str(fd.cell(row=r, column=1).value).strip() for r in range(2, fd.max_row + 1)}
    row = fd.max_row + 1
    for values in FIELD_DEFS:
        if values[0] in have:
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
    print(f"read {n_read} GEM pages; {len(NOT_IN_GEM)} rows marked not available")
    print("FINDING: GEM lists Discovery LNG as 'cancelled (inferred 4 y)'")


if __name__ == "__main__":
    main()
