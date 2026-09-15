"""Text and consistency fixes from the academic review, sections B and C.

One-off. No value changes anywhere. The model never writes Inputs/; this
script does, once.

1. Chains sheet, bunkering `applies_to`: read "0.90 mtpa (Tilbury Phase 1a and
   1b)" while Tilbury Phase 2 (2.5 mtpa) is on the bunkering chain. Now 3.40
   mtpa with all three units listed.
2. Emission Factors, combustion basis: opened "IPCC default combustion factor
   ... not contestable" while the README grounds 2.75 as methane stoichiometry
   (the IPCC natural-gas central is 2.693, pipeline gas). Cell now matches.
3. Emission Factors, pipeline basis: the retired Coastal GasLink "1.47 vs 1.48"
   scaling check is replaced with the current statement, and the three
   evidence points (CGL assessment ~0.094, retired 0.10, adopted 0.074) are
   reconciled in one sentence instead of left for a reviewer to find.
4. Asset Register, Summit Lake `commercial_note`: records that the
   containerised rail-to-port concept is modelled with the LNG-carrier
   shipping factor, immaterial at 2.7 mtpa.

Run from the repository root:

    python tools/review_text_fixes.py
"""

from __future__ import annotations

from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Inputs" / "Canada_LNG_Data_Inputs.xlsx"
REGISTER = ROOT / "Inputs" / "Canada_LNG_Asset_Register.xlsx"


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


COMBUSTION_BASIS = (
    "2.75 tCO2 per tonne of LNG is the STOICHIOMETRIC value for pure methane (44/16): one "
    "tonne of CH4 burned completely yields 2.75 tonnes of CO2. It is the right central for LNG "
    "because liquefaction strips inerts (N2, CO2) and most heavier fractions, so delivered LNG "
    "is closer to pure methane than pipeline gas. The IPCC 2006 Guidelines default for natural "
    "gas is 2.693 tCO2/t (Table 2.2, 56,100 kgCO2/TJ x Table 1.2 NCV 48.0 TJ/Gg), which is a "
    "PIPELINE-gas figure carrying a heavier average composition; it is used here only for the "
    "uncertainty band in range_sources, applied as a relative interval to the 2.75 central. "
    "Determined by the carbon content of the fuel, so not location specific. "
    "https://www.ipcc-nggip.iges.or.jp/public/2006gl/ . Cell rewritten 3 September 2026 to "
    "match the README; it previously opened 'IPCC default combustion factor for natural gas', "
    "which was not what the 2.75 is."
)

CGL_OLD = (
    "The Coastal GasLink check (model 1.47 against 1.48 MtCO2e/yr implied by the 2014 BC EAO "
    "assessment) confirms the arithmetic of scaling a factor with throughput; it is not an "
    "independent measurement of the factor."
)
CGL_NEW = (
    "THREE EVIDENCE POINTS, RECONCILED. (i) The 2014 BC Environmental Assessment Office "
    "assessment of Coastal GasLink puts operations at 3.517 MtCO2e/yr at the line's full "
    "5 Bcf/d design capacity (51.7 bcm/y, 37.4 Mt LNG-equivalent at 1.38 bcm per Mt), which "
    "implies about 0.094 tCO2e per t LNG - a BRITISH COLUMBIA figure for an in-scope line. "
    "(ii) The retired 0.10 was an assumption that the CGL figure happened to sit near; the "
    "old '1.47 vs 1.48 MtCO2e/yr' check confirmed only the arithmetic of scaling an assumed "
    "factor with throughput and is withdrawn. (iii) The adopted 0.074 comes from an Alberta "
    "line (Liu et al. 2021) and a national average (CER/ECCC), not from British Columbia. "
    "This model's stated principle is that Canadian sources are used wherever the stage "
    "occurs in Canada, and here BC-specific evidence exists and was not adopted. The reason: "
    "the CGL figure is a PRE-OPERATION PROJECTION from an environmental assessment, whereas "
    "Liu et al. is peer-reviewed and measurement-informed and the CER route is an observed "
    "national inventory, and the two independent routes agreeing to 1.2 per cent is the "
    "stronger evidence. The CGL projection is 27 per cent above the adopted value; if the "
    "line operates at its assessed intensity the factor is low for the LNG Canada / Cedar "
    "share of throughput by about that margin, worth roughly 1 MtCO2e/yr at 14 mtpa. That "
    "is recorded as a limitation rather than corrected, and the 0.037-0.133 sampled band "
    "covers it."
)

SUMMIT_NOTE = (
    "Rail leg has no analogue in the other projects and is not modelled. SHIPPING MODE: the "
    "proponent's concept is LNG in ISO containers railed to Prince Rupert and shipped in "
    "container vessels, not LNG carriers. The model applies the LNG-carrier shipping factor "
    "(0.12 tCO2e/t on the 3,800 nm basis) to this asset like every other export terminal. "
    "At 2.7 mtpa the shipping stage is about 0.3 MtCO2e/yr, so any difference between "
    "containerised and carrier shipping intensity is immaterial to every published figure; "
    "recorded 3 September 2026 so the substitution is visible rather than silent."
)


def main() -> None:
    wb = openpyxl.load_workbook(DATA)

    ch = wb["Chains"]
    chh = _headers(ch)
    r = _row_of(ch, chh, "chain", "bunkering")
    old = ch.cell(row=r, column=chh["applies_to"]).value
    assert old == "0.90 mtpa (Tilbury Phase 1a and 1b)", old
    ch.cell(row=r, column=chh["applies_to"],
            value="3.40 mtpa (Tilbury Phase 1a 0.25 operating; Tilbury Phase 1b 0.65 and Tilbury Phase 2 2.50 proposed)")
    print(f"Chains bunkering applies_to: {old} -> 3.40 mtpa, three units")

    ef = wb["Emission Factors"]
    eh = _headers(ef)
    r = _row_of(ef, eh, "stage", "combustion")
    old = ef.cell(row=r, column=eh["basis_for_central"]).value
    assert old.startswith("IPCC default combustion factor"), old[:60]
    ef.cell(row=r, column=eh["basis_for_central"], value=COMBUSTION_BASIS)
    print("combustion basis_for_central: rewritten as methane stoichiometry")

    r = _row_of(ef, eh, "stage", "pipeline_transport")
    basis = ef.cell(row=r, column=eh["basis_for_central"]).value
    assert CGL_OLD in basis, "pipeline basis text has changed; check before patching"
    ef.cell(row=r, column=eh["basis_for_central"], value=basis.replace(CGL_OLD, CGL_NEW))
    print("pipeline basis_for_central: CGL check replaced with the three-point reconciliation")

    wb.save(DATA)

    reg = openpyxl.load_workbook(REGISTER)
    ar = reg["Asset Register"]
    ah = _headers(ar)
    r = _row_of(ar, ah, "project_id", "summit_lake_pg_lng")
    old = ar.cell(row=r, column=ah["commercial_note"]).value
    ar.cell(row=r, column=ah["commercial_note"], value=SUMMIT_NOTE)
    print(f"Summit Lake commercial_note: {old!r} -> shipping-mode note")
    src = reg["Asset Sources"]
    sh = _headers(src)
    r = _row_of(src, sh, "project_id", "summit_lake_pg_lng")
    src.cell(row=r, column=sh["commercial_note"],
             value="Compiled by us; shipping mode from the export_route already sourced in this row (BC EAO project description)")
    reg.save(REGISTER)
    print("saved")


if __name__ == "__main__":
    main()
