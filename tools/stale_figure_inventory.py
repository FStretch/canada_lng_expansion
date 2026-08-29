"""Regenerate Outputs/STALE_FIGURE_INVENTORY.md against the current lock.

The previous inventory was a hand-written snapshot taken before an earlier
round of edits. It went stale itself: it treated 9,558.2 Mt, 309.1 Mt and
18.5 / 5.6 / 75.9 as current, and by the time anyone read it those were two
scope changes out of date. A hand-written inventory of stale numbers is the
one document guaranteed to go stale.

This script greps the repository for every superseded headline value and
writes the inventory from what it finds, so it can be re-run after any
re-lock. Values live in SUPERSEDED below; add a row when a lock moves.

    python tools/stale_figure_inventory.py

Hits inside ALLOWED paths are reported as deliberate history (the lock-history
comment in build_results.py, this script, the baseline record, the change
report) rather than as stale text to fix.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Outputs" / "STALE_FIGURE_INVENTORY.md"

# (pattern, what it was, what replaced it, when it moved)
SUPERSEDED = [
    (r"9[,.]?558\.2", "9,558.2 Mt lifetime (all assets)", "9,298.1 Mt", "export-scope filter, then route-scaled shipping"),
    (r"\b309\.1\b", "309.1 Mt peak (all assets)", "298.2 Mt in 2037", "export-scope filter, then route-scaled shipping"),
    (r"18\.5\s*[/-]\s*5\.6\s*[/-]\s*75\.9", "18.5 / 5.6 / 75.9 territorial", "18.1 / 3.2 / 78.7", "export-scope filter, then route-scaled shipping"),
    (r"9[,.]?315\.3", "9,315.3 Mt lifetime (export scope, flat shipping)", "9,298.1 Mt", "Task 4, route-scaled shipping"),
    (r"\b298\.7\b", "298.7 Mt peak (flat shipping)", "298.2 Mt in 2037", "Task 4, route-scaled shipping"),
    (r"18\.0\s*[/-]\s*3\.4\s*[/-]\s*78\.6", "18.0 / 3.4 / 78.6 territorial", "18.1 / 3.2 / 78.7", "Task 4, route-scaled shipping"),
    (r"\b4[,.]?164\b", "C$4,164bn ECCC 2% damages (whole CO2e at SC-CO2)", "C$4,073bn", "Task 3 per-gas pricing, then Task 4"),
    (r"\b258\.9\b", "258.9 Mt/yr life-average", "258.5 Mt/yr", "Task 4, route-scaled shipping"),
    (r"10[,.]?704\.7", "10,704.7 Mt lifetime", "9,298.1 Mt", "superseded before this task sequence"),
    (r"\b272\.0\b", "272.0 Mt peak", "298.2 Mt in 2037", "superseded before this task sequence"),
]

CURRENT = {
    "lifetime CO2e": "9,298.1 Mt",
    "lifetime CO2 only": "8,955.2 Mt (plus 11,505 kt CH4)",
    "peak": "298.2 Mt in 2037",
    "territorial CAN / BUNK / FOR": "18.1 / 3.2 / 78.7 %",
    "ECCC 2% damages": "C$4,073 bn",
    "committed": "1,869.5 Mt, C$749 bn",
    "committed plus advanced": "3,805.7 Mt, C$1,579 bn",
}

TEXT_SUFFIXES = {".md", ".py", ".txt", ".cff", ".yml", ".yaml"}
DATA_SUFFIXES = {".csv"}
SKIP_DIRS = {".git", "__pycache__", "figures"}
# Deliberate records of superseded values, not text to fix.
ALLOWED = {
    "tools/stale_figure_inventory.py",
    # Names the exact README string it replaced, so it must quote the old split.
    "tools/update_data_inputs_readme_task4.py",
    "build_results.py",
    "Outputs/STALE_FIGURE_INVENTORY.md",
    # Dated diagnostics, each carrying a superseded-snapshot banner.
    "Outputs/SCOPE_DIAGNOSTIC.md",
    "Outputs/OIL_COMPARATOR_AUDIT.md",
}
ALLOWED_PREFIXES = ("Outputs/BASELINE_", "Outputs/CHANGE_REPORT_")


def _allowed(rel: str) -> bool:
    return rel in ALLOWED or rel.startswith(ALLOWED_PREFIXES)


def _iter_files():
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES:
            yield path, "text"
        elif path.suffix.lower() in DATA_SUFFIXES:
            yield path, "data"
        elif path.suffix.lower() == ".xlsx":
            yield path, "workbook"


def _workbook_text(path: Path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        for ws in wb.worksheets:
            for row in ws.iter_rows(values_only=True):
                for value in row:
                    if isinstance(value, str):
                        yield ws.title, value
    finally:
        wb.close()


def main() -> None:
    findings = {label: [] for _p, label, _c, _w in SUPERSEDED}
    for path, kind in _iter_files():
        rel = path.relative_to(ROOT).as_posix()
        if kind == "workbook":
            try:
                cells = list(_workbook_text(path))
            except Exception as exc:  # noqa: BLE001 - report, do not crash
                print(f"  could not read {rel}: {exc}")
                continue
            for pattern, label, _cur, _when in SUPERSEDED:
                rx = re.compile(pattern)
                for sheet, value in cells:
                    if rx.search(value):
                        findings[label].append((f"{rel} [{sheet}]", kind, False))
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for pattern, label, _cur, _when in SUPERSEDED:
            if re.search(pattern, text):
                findings[label].append((rel, kind, _allowed(rel)))

    lines = []
    lines.append("# Stale figure inventory")
    lines.append("")
    lines.append(
        f"Regenerated {date.today().isoformat()} by "
        "`python tools/stale_figure_inventory.py`, against the paper set locked "
        "as `EXPECTED_BUILD_OUT` in `build_results.py`."
    )
    lines.append("")
    lines.append(
        "The previous version of this file was a hand-written snapshot and had "
        "itself gone stale: it treated 9,558.2 Mt, 309.1 Mt and "
        "18.5 / 5.6 / 75.9 as current, two scope changes after they stopped "
        "being so. This one is generated, so it can be re-run after any "
        "re-lock."
    )
    lines.append("")
    lines.append("## Current locked values")
    lines.append("")
    lines.append("| quantity | value |")
    lines.append("|---|---|")
    for key, value in CURRENT.items():
        lines.append(f"| {key} | **{value}** |")
    lines.append("")
    lines.append("## Superseded values, and where they still appear")
    lines.append("")
    lines.append("| superseded | replaced by | when it moved | live hits | deliberate records |")
    lines.append("|---|---|---|---|---|")
    live_total = 0
    for _pattern, label, current, when in SUPERSEDED:
        hits = findings[label]
        live = [h for h in hits if not h[2] and h[1] != "data"]
        keep = [h for h in hits if h[2]]
        data = [h for h in hits if h[1] == "data" and not h[2]]
        live_total += len(live)
        live_txt = (
            ", ".join(f"`{p}`" for p, _k, _a in live) if live else "**none**"
        )
        keep_txt = ", ".join(f"`{p}`" for p, _k, _a in keep) or "-"
        if data:
            keep_txt += " · data series (not published text): " + ", ".join(
                f"`{p}`" for p, _k, _a in data
            )
        lines.append(
            f"| {label} | {current} | {when} | {live_txt} | {keep_txt} |"
        )
    lines.append("")
    if live_total:
        lines.append(
            f"**{live_total} live hit(s) to fix.** Anything in the last column "
            "is a deliberate record of what a number used to be - the lock "
            "history comment in `build_results.py`, the baseline record, a "
            "change report, or this script's own value table - and is not "
            "stale text."
        )
    else:
        lines.append(
            "**No live hits.** Every remaining occurrence is a deliberate "
            "record of what a number used to be: the lock history comment in "
            "`build_results.py`, the baseline record, the change report, or "
            "this script's own value table. Monte Carlo draw files may contain "
            "coincidental samples near a superseded figure; those are data, "
            "not published text."
        )
    lines.append("")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({live_total} live hit(s))")


if __name__ == "__main__":
    main()
