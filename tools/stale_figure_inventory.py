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
    (r"10[,.]?704\.7", "10,704.7 Mt lifetime", "7,254.2 Mt", "superseded before this task sequence"),
    (r"\b272\.0\b", "272.0 Mt peak", "238.6 Mt in 2037", "superseded before this task sequence"),
    # Discovery LNG returned to cancelled, 1 September 2026.
    (r"9[,.]?298\.1", "9,298.1 Mt lifetime (Discovery counted as early_proposed)", "7,254.2 Mt", "Discovery returned to cancelled"),
    (r"\b298\.2\b", "298.2 Mt peak (Discovery in)", "238.6 Mt in 2037", "Discovery returned to cancelled"),
    (r"8[,.]?955\.2", "8,955.2 Mt CO2-only (Discovery in)", "6,987.7 Mt", "Discovery returned to cancelled"),
    (r"18\.1\s*[/-]\s*3\.2\s*[/-]\s*78\.7", "18.1 / 3.2 / 78.7 territorial", "18.1 / 3.2 / 78.8", "Discovery returned to cancelled"),
    (r"\b4[,.]?073\b", "C$4,073bn ECCC 2% damages (Discovery in)", "C$3,143bn", "Discovery returned to cancelled"),
    (r"\b258\.5\b", "258.5 Mt/yr life-average (Discovery in)", "207.4 Mt/yr", "Discovery returned to cancelled"),
    (r"\b100\.1\b", "100.1 mtpa export capacity (ten projects)", "80.1 mtpa (nine projects)", "Discovery returned to cancelled"),
    (r"11[,.]?505", "11,505 kt CH4 (Discovery in)", "8,942 kt", "Discovery returned to cancelled"),
    # GWP20 scenario recomputed on the methane portion only.
    (r"upstream 0\.33\b", "upstream 0.33 GWP20 (whole factor x1.5)", "0.428 (methane portion only)", "GWP20 recomputed on the methane portion"),
    # Regasification and combustion range moved onto cited values, 3 September 2026.
    (r"7[,.]?254\.2", "7,254.2 Mt lifetime (regasification 0.04)", "7,215.3 Mt", "regasification 0.04 -> 0.021"),
    (r"\b238\.6\b", "238.6 Mt peak (regasification 0.04)", "237.3 Mt in 2037", "regasification 0.04 -> 0.021"),
    (r"6[,.]?987\.7", "6,987.7 Mt CO2-only (regasification 0.04)", "6,948.8 Mt", "regasification 0.04 -> 0.021"),
    (r"18\.1\s*[/-]\s*3\.2\s*[/-]\s*78\.8", "18.1 / 3.2 / 78.8 territorial", "18.2 / 3.2 / 78.6", "regasification 0.04 -> 0.021 (regas is FOR-tagged)"),
    (r"\b3[,.]?143\b", "C$3,143bn ECCC 2% damages (regasification 0.04)", "C$3,126bn", "regasification 0.04 -> 0.021"),
    (r"\b207\.4\b", "207.4 Mt/yr life-average (regasification 0.04)", "206.3 Mt/yr", "regasification 0.04 -> 0.021"),
    (r"regasification 0\.04|regas 0\.04", "regasification central 0.04 (uncited)", "0.021 (Gan et al. 2024)", "moved onto a cited value"),
    (r"combustion (?:range )?2\.50|2\.50\s*/\s*3\.00", "combustion range low 2.50 (uncited)", "2.58 (IPCC 2006 uncertainty band)", "moved onto a cited derivation"),
    # Pipeline moved onto two converging cited routes, 3 September 2026.
    (r"7[,.]?215\.3", "7,215.3 Mt lifetime (pipeline 0.10)", "7,162.0 Mt", "pipeline 0.10 -> 0.074"),
    (r"237\.3", "237.3 Mt peak (pipeline 0.10)", "235.6 Mt in 2037", "pipeline 0.10 -> 0.074"),
    (r"6[,.]?948\.8", "6,948.8 Mt CO2-only (pipeline 0.10)", "6,895.6 Mt", "pipeline 0.10 -> 0.074"),
    (r"18\.2\s*[/-]\s*3\.2\s*[/-]\s*78\.6", "18.2 / 3.2 / 78.6 territorial", "17.6 / 3.2 / 79.2", "pipeline 0.10 -> 0.074 (pipeline is CAN-tagged)"),
    (r"3[,.]?126", "C$3,126bn ECCC 2% damages (pipeline 0.10)", "C$3,103bn", "pipeline 0.10 -> 0.074"),
    (r"206\.3", "206.3 Mt/yr life-average (pipeline 0.10)", "204.7 Mt/yr", "pipeline 0.10 -> 0.074"),
    (r"pipeline (?:transport )?(?:central )?0\.10", "pipeline central 0.10 (assumed)", "0.074 (Liu 2021 / CER 2022)", "moved onto two converging cited routes"),
]

CURRENT = {
    "lifetime CO2e": "7,162.0 Mt",
    "lifetime CO2 only": "6,895.6 Mt (plus 8,942 kt CH4)",
    "peak": "235.6 Mt in 2037",
    "territorial CAN / BUNK / FOR": "17.6 / 3.2 / 79.2 %",
    "ECCC 2% damages": "C$3,103 bn",
    "committed": "1,845.8 Mt, C$739 bn",
    "committed plus advanced": "3,757.5 Mt, C$1,559 bn",
    "export capacity": "80.1 mtpa across nine projects",
}

TEXT_SUFFIXES = {".md", ".py", ".txt", ".cff", ".yml", ".yaml"}
DATA_SUFFIXES = {".csv"}
SKIP_DIRS = {".git", "__pycache__", "figures"}
# Deliberate records of superseded values, not text to fix.
ALLOWED = {
    "tools/stale_figure_inventory.py",
    # Names the exact README string it replaced, so it must quote the old split.
    "tools/update_data_inputs_readme_task4.py",
    # Record what they changed, so they must quote the values they moved away from.
    "tools/fix_audit_findings.py",
    "tools/update_chains_applies_to.py",
    "tools/apply_found_citations.py",
    "tools/update_pipeline_factor.py",
    "tools/record_ch4_share_derivation.py",
    "build_results.py",
    "Outputs/STALE_FIGURE_INVENTORY.md",
    # Dated diagnostics and audits, each carrying a superseded-snapshot banner.
    "Outputs/SCOPE_DIAGNOSTIC.md",
    "Outputs/OIL_COMPARATOR_AUDIT.md",
    "Outputs/SOURCING_AUDIT.md",
    "Outputs/DECK_RECONCILIATION.md",
    "Outputs/CITATIONS_WANTED.md",
}
ALLOWED_PREFIXES = ("Outputs/BASELINE_", "Outputs/CHANGE_REPORT_")

# A file may quote one specific superseded value on purpose without being
# exempted from every other check. Keyed (path, superseded label).
ALLOWED_PAIRS = {
    # One deliberate before/after sentence about the Discovery removal.
    ("README.md", "9,298.1 Mt lifetime (Discovery counted as early_proposed)"),
    ("README.md", "100.1 mtpa export capacity (ten projects)"),
    # The scenarios section explains what 0.33 was and why it moved.
    ("README.md", "upstream 0.33 GWP20 (whole factor x1.5)"),
    # The emission-factor section explains both 3 September moves.
    ("README.md", "regasification central 0.04 (uncited)"),
    ("README.md", "combustion range low 2.50 (uncited)"),
    ("Outputs/CITATIONS_WANTED.md", "regasification central 0.04 (uncited)"),
    ("Outputs/CITATIONS_WANTED.md", "combustion range low 2.50 (uncited)"),
    ("README.md", "pipeline central 0.10 (assumed)"),
    ("Outputs/CITATIONS_WANTED.md", "pipeline central 0.10 (assumed)"),
    ("src/benchmark_table.py", "pipeline central 0.10 (assumed)"),
}


def _allowed(rel: str, label: str | None = None) -> bool:
    if rel in ALLOWED or rel.startswith(ALLOWED_PREFIXES):
        return True
    return label is not None and (rel, label) in ALLOWED_PAIRS


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
                findings[label].append((rel, kind, _allowed(rel, label)))

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
        "Generated, not hand-written. An earlier hand-written version of this "
        "file went stale itself, twice: it treated 9,558.2 Mt and 309.1 Mt as "
        "current after they had been superseded, and a later generated run "
        "still listed 9,298.1 Mt as current after Discovery LNG was returned "
        "to cancelled. Re-run this script after every re-lock; that is the "
        "only thing that keeps it honest."
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
