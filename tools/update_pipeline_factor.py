"""Pipeline transport 0.10 -> 0.074 tCO2e/t LNG, on two independent routes.

One-off. The model never writes Inputs/; this script does, once.

Route A (central). Liu et al. (2021), ES&T 55(14): 9711-9720, doi
10.1021/acs.est.0c06353, Results p. 9713: "The company emissions intensities
using both mass and energy allocation are 4.2 gCO2e/MJ NG at transmission
pipeline outlet". Modern West Advisory for Emissions Reduction Alberta (2022),
Life-Cycle Analysis of Canadian Natural Gas: A Pilot Study, section 5.3 p. 43,
restates the same study at the plant-exit boundary: "If the transmission
emissions are excluded to make the boundaries consistent with the present
report, the estimated emission intensity at NG plant exit is approximately
2.86 gCO2e/MJ NG." The difference is the transmission stage:
4.20 - 2.86 = 1.34 gCO2e/MJ, which at 54.863 GJ/t is 0.0735 tCO2e/t.

Route B (cross-check, not the central). CER Market Snapshot, "Greening
Canada's pipeline infrastructure" (2022): "In 2019, emissions resulting from
pipeline transport, primarily emissions related to combustion at compressor
stations, accounted for 8.3 MT CO2e", attributed to ECCC NIR 1990-2019 Part 1
Table 2-5. Over roughly 170 bcm of Canadian marketable gas at 36 PJ/bcm that
is 1.356 gCO2e/MJ, or 0.0744 tCO2e/t.

Both figures were read from the primary documents on 3 September 2026.

Run from the repository root:

    python tools/update_pipeline_factor.py
"""

from __future__ import annotations

from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Inputs" / "Canada_LNG_Data_Inputs.xlsx"

LIU_URL = "https://doi.org/10.1021/acs.est.0c06353"
LIU_PDF = "https://ngi.stanford.edu/sites/ngi/files/media/file/acs.est_.0c06353.pdf"
ERA_URL = (
    "https://www.eralberta.ca/wp-content/uploads/2022/04/"
    "Modern-West-Advisory-Final-Outcomes-Report-Non-Confidential.pdf"
)
CER_URL = (
    "https://www.cer-rec.gc.ca/en/data-analysis/energy-markets/market-snapshots/"
    "2022/market-snapshot-greening-canadas-pipeline-infrastructure.html"
)

CENTRAL = 0.074
RANGE_LOW = 0.037
RANGE_HIGH = 0.133

BASIS = (
    "0.074 tCO2e per t LNG, from two independent routes that converge. "
    "ROUTE A (central): Liu, R.E., Ravikumar, A.P., Bi, X.T., Zhang, S., Nie, "
    "Y., Brandt, A., Bergerson, J.A. (2021), 'Greenhouse Gas Emissions of "
    "Western Canadian Natural Gas: Proposed Emissions Tracking for Life Cycle "
    "Modeling', Environmental Science & Technology 55(14): 9711-9720, "
    + LIU_URL
    + " (open PDF " + LIU_PDF + "). Results, p. 9713: 'The company emissions "
    "intensities using both mass and energy allocation are 4.2 gCO2e/MJ NG at "
    "transmission pipeline outlet.' Modern West Advisory for Emissions "
    "Reduction Alberta (2022), Life-Cycle Analysis of Canadian Natural Gas: A "
    "Pilot Study, section 5.3 p. 43, " + ERA_URL + " , restates that same "
    "study on the plant-exit boundary: 'If the transmission emissions are "
    "excluded to make the boundaries consistent with the present report, the "
    "estimated emission intensity at NG plant exit is approximately 2.86 "
    "gCO2e/MJ NG.' The difference is the transmission stage: 4.20 - 2.86 = "
    "1.34 gCO2e/MJ. At lng_energy_content 52 MMBtu/t = 54.863 GJ/t that is "
    "0.0735 tCO2e per t LNG. ROUTE B (independent cross-check, not the "
    "central): CER Market Snapshot, 'Greening Canada's pipeline "
    "infrastructure' (2022), " + CER_URL + " : 'In 2019, emissions resulting "
    "from pipeline transport, primarily emissions related to combustion at "
    "compressor stations, accounted for 8.3 MT CO2e', attributed to ECCC "
    "National Inventory Report 1990-2019 Part 1 Table 2-5. Over roughly 170 "
    "bcm of Canadian marketable gas at 36 PJ/bcm: 8.3 Mt / 6,120 PJ = 1.356 "
    "gCO2e/MJ = 0.0744 tCO2e/t. The two routes agree to within 1.2 per cent. "
    "Stored as 0.074. Replaces an assumed 0.10 (3 September 2026), which was "
    "about 35 per cent above both routes and which no ICF or Sphera document "
    "supported."
)

CAVEATS = (
    "CAVEATS ON ROUTE A. Liu et al. is a case study of Seven Generations "
    "Energy's Kakwa operations in Alberta - one operator running relatively "
    "new facilities, so plausibly better than the Western Canadian average; "
    "the paper's own comparison puts BC estimates at 6.2-12 gCO2e/MJ upstream "
    "against its 4.2. The paper's Table 1 Section D gives the modelled "
    "transmission pipeline length as 1,100 km (company data; US default 971 "
    "km). NOTE THE ABSTRACT SAYS 3.1-4.0 gCO2e/MJ while the Results text says "
    "4.2 for mass and energy allocation and 3.1 / 3.3 for financial and "
    "condensate-displacement allocation; the 4.2 used here is the Results "
    "figure on the allocation basis this model uses. "
    "DISTANCE. This model applies the pipeline factor FLAT, with no "
    "distance scaling, unlike shipping. Route A is calibrated on 1,100 km and "
    "Route B is a national average haul, while the in-scope feedgas lines are "
    "Coastal GasLink 670 km, Prince Rupert Gas Transmission 750 km and "
    "FortisBC Eagle Mountain 47 km. If transmission emissions scale with "
    "distance, 0.074 is high for every one of them - Woodfibre most of all. "
    "That is a stated limitation, not a correction applied here. "
    "The Coastal GasLink check (model 1.47 against 1.48 MtCO2e/yr implied by "
    "the 2014 BC EAO assessment) confirms the arithmetic of scaling a factor "
    "with throughput; it is not an independent measurement of the factor."
)

RANGE_SOURCES = (
    "ASSUMPTION, DECLARED. The 0.037-0.133 band is not cited. It preserves "
    "the relative width of the retired 0.05-0.18 band (x0.5 / x1.8) around the "
    "new 0.074 central, because no published uncertainty interval for Canadian "
    "gas transmission intensity was located. 'Regional greenhouse gas analysis "
    "of compressor drivers in natural gas transmission systems in Canada', "
    "Journal of Cleaner Production (2023), doi 10.1016/j.jclepro.2023.137150, "
    "was the candidate for a structured band but is paywalled and could not be "
    "read. The two central routes agreeing to 1.2 per cent (0.0735 and 0.0744) "
    "is convergence on the CENTRAL and must not be read as the uncertainty: "
    "the real spread is driven by route length and compressor drive type, "
    "neither of which this model varies. Do not narrow the Monte Carlo band to "
    "the gap between the two routes; that would assert a precision the "
    "evidence does not support."
)

KEY_UNCERTAINTY = (
    "About 2 per cent of the lifecycle total after the move to 0.074. Modelled "
    "proportional to throughput and flat in distance, whereas compressor "
    "stations have a fixed operating baseline and their fuel burn scales with "
    "haul length. The in-scope lines are shorter than the 1,100 km behind "
    "Route A, so the factor is more likely high than low for these assets."
)


def _headers(ws) -> dict[str, int]:
    return {
        str(ws.cell(row=1, column=c).value).strip(): c
        for c in range(1, ws.max_column + 1)
        if ws.cell(row=1, column=c).value is not None
    }


def main() -> None:
    wb = openpyxl.load_workbook(DATA)
    ws = wb["Emission Factors"]
    h = _headers(ws)
    row = None
    for r in range(2, ws.max_row + 1):
        if str(ws.cell(row=r, column=h["stage"]).value).strip() == "pipeline_transport":
            row = r
            break
    if row is None:
        raise KeyError("pipeline_transport row not found")

    old = ws.cell(row=row, column=h["central"]).value
    ws.cell(row=row, column=h["central"], value=CENTRAL)
    ws.cell(row=row, column=h["range_low"], value=RANGE_LOW)
    ws.cell(row=row, column=h["range_high"], value=RANGE_HIGH)
    ws.cell(row=row, column=h["basis_for_central"], value=BASIS + " " + CAVEATS)
    ws.cell(row=row, column=h["range_sources"], value=RANGE_SOURCES)
    ws.cell(row=row, column=h["key_uncertainty"], value=KEY_UNCERTAINTY)

    wb.save(DATA)
    print(f"pipeline_transport central {old} -> {CENTRAL}")
    print(f"pipeline_transport range 0.05/0.18 -> {RANGE_LOW}/{RANGE_HIGH} (declared assumption)")


if __name__ == "__main__":
    main()
