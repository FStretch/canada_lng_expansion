"""Generated lock banners for the dated documents under Outputs/.

Three documents record the model at a past state: the sourcing audit, the
Roman-White gap diagnostic and the oil comparator audit.
Each needs a banner that says what it was written against and what the current
lock is. Hand-written banners went stale twice — they claimed values as
"current" one to three re-locks after they had moved, and the stale-figure
inventory could not see it because those files were exempt whole.

So the banner is generated. `render_banner` builds it from the lock that
`build_results.py` asserts; `tools/refresh_banners.py` writes it between the
markers; `build_results.py` asserts on every run that what is in each file is
exactly what the lock would render. A re-lock that forgets the banners fails
the run rather than publishing a stale claim.

Everything between the markers is generated. Everything outside them is the
document's own text and is never touched.
"""

from __future__ import annotations

from pathlib import Path

START = "<!-- lock-banner:start -->"
END = "<!-- lock-banner:end -->"

# What each dated document was written against. Historical facts; they do not
# change when the lock does. The current values come from `lock` at render time.
DATED_DOCUMENTS: dict[str, dict[str, str]] = {
    "Outputs/SOURCING_AUDIT.md": {
        "what": "Sourcing audit of every number in the model, 1 September 2026.",
        "written_against": (
            "the pre-Discovery lock: 9,298.1 Mt lifetime, 298.2 Mt peak, "
            "C$4,073 bn damages, 100.1 mtpa across ten projects"
        ),
        "since": (
            "Its own findings were then applied (`tools/fix_audit_findings.py`): "
            "Discovery LNG returned to cancelled and the GWP20 scenario was "
            "recomputed on the methane portion only. Regasification, the "
            "combustion range, pipeline transport, the methane share and the "
            "FID band have all moved onto cited values since; each move is a "
            "commit in the git history. The verdicts below stand; the headline "
            "figures they were measured against do not."
        ),
    },
    "Outputs/LCA_ROMAN_WHITE_GAP.md": {
        "what": (
            "Diagnostic of the gap to Roman-White et al. (2021) on the aligned "
            "well-to-regasification boundary, 28 August 2026."
        ),
        "written_against": (
            "a model well-to-regasification intensity of 0.80 tCO2e/t LNG, "
            "before regasification moved from 0.04 to 0.021 and pipeline "
            "transport from 0.10 to 0.074"
        ),
        "since": (
            "The stage mapping and the reasoning below stand; the model side of "
            "the comparison has moved. The current figure is in "
            "`Outputs/figure_data/fig10_lca_comparison.csv` and the six-row "
            "boundary-aligned comparison in `Outputs/benchmark_comparison.csv`."
        ),
    },
    "Outputs/OIL_COMPARATOR_AUDIT.md": {
        "what": "Audit of the oil-pipeline comparator behind figure 7, 25 August 2026.",
        "written_against": (
            "a model that still carried figure 7, `src/report_params.py` and "
            "the `tmx_*` and bitumen-pipeline parameters"
        ),
        "since": (
            "**The analysis this document audits has been retired.** Figure 7, "
            "`src/report_params.py`, `oil_lifecycle_gt` and the oil comparator "
            "parameters were removed on 3 September 2026 (commit 056e999) because of the "
            "findings below: the factor had no citation, no URL and no vintage, "
            "and the bitumen-pipeline bar was an unvalidated first pass. This "
            "file is kept as the working behind that decision, not as a "
            "description of anything now in the model."
        ),
    },
}


def render_banner(rel_path: str, lock: dict) -> str:
    """The exact banner block for one dated document at the given lock."""
    meta = DATED_DOCUMENTS[rel_path]
    terr = lock["territorial_pct"]
    current = (
        f"**{lock['lifetime_mt']:,.1f} Mt** lifetime CO2e, "
        f"**{lock['peak_mt']:,.1f} Mt** peak in {lock['peak_year']}, "
        f"**{terr['CAN']:.1f} / {terr['BUNK']:.1f} / {terr['FOR']:.1f}** "
        f"CAN / BUNK / FOR, **C${lock['damages_cad_bn']:,} bn** ECCC 2% damages valued "
        f"when caused (**C${lock['damages_npv_cad_bn']:,} bn** discounted to 2025), "
        f"**{lock['export_mtpa']:.1f} mtpa** of export capacity"
    )
    if rel_path == "Outputs/LCA_ROMAN_WHITE_GAP.md":
        current += (
            f"; well-to-regasification "
            f"**{lock['well_to_regas_t_per_t']:.2f} tCO2e/t LNG**"
        )
    lines = [
        START,
        f"> **Dated document.** {meta['what']}",
        f"> Written against {meta['written_against']}.",
        f"> {meta['since']}",
        f"> **Current lock:** {current}.",
        "> This banner is generated from the lock in `build_results.py` and "
        "asserted on every run; edit nothing between the markers.",
        END,
    ]
    return "\n".join(lines)


def _split(text: str) -> tuple[str, str | None, str]:
    """(before, banner-or-None, after) for a document's text."""
    if START not in text:
        return text, None, ""
    head, rest = text.split(START, 1)
    if END not in rest:
        raise ValueError("lock-banner start marker without end marker")
    banner, tail = rest.split(END, 1)
    return head, START + banner + END, tail


def banner_of(text: str) -> str | None:
    """The banner block in a document's text, or None if it has none."""
    return _split(text)[1]


def stale_banners(root: Path, lock: dict) -> list[str]:
    """Documents whose banner is missing or differs from the rendered one."""
    problems = []
    for rel in DATED_DOCUMENTS:
        path = root / rel
        if not path.exists():
            problems.append(f"{rel}: file missing")
            continue
        found = banner_of(path.read_text(encoding="utf-8"))
        want = render_banner(rel, lock)
        if found is None:
            problems.append(f"{rel}: no lock banner")
        elif found.replace("\r\n", "\n") != want:
            problems.append(f"{rel}: banner does not match the current lock")
    return problems


def write_banners(root: Path, lock: dict) -> list[str]:
    """Write or replace the banner in each dated document. Returns those changed.

    A document with no banner yet gets it inserted after its H1 title line.
    """
    changed = []
    for rel in DATED_DOCUMENTS:
        path = root / rel
        text = path.read_text(encoding="utf-8")
        want = render_banner(rel, lock)
        head, found, tail = _split(text)
        if found is None:
            lines = text.split("\n")
            assert lines[0].startswith("# "), f"{rel}: expected an H1 on line 1"
            body = lines[1:]
            if body and body[0].strip() == "":
                body = body[1:]
            new_text = "\n".join([lines[0], "", want, ""] + body)
        else:
            if found.replace("\r\n", "\n") == want:
                continue
            new_text = head + want + tail
        path.write_text(new_text, encoding="utf-8", newline="")
        changed.append(rel)
    return changed
