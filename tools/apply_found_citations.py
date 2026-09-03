"""Apply the citations returned against CITATIONS_WANTED.md, 3 September 2026.

One-off. The model never writes Inputs/; this script does, once.

1. Combustion range 2.50 / 3.00 -> 2.58 / 3.00, derived from the IPCC 2006
   uncertainty ranges and cited to them. Central 2.75 unchanged.
2. Regasification central 0.04 -> 0.021 (Gan et al. 2024), range 0.02 / 0.06 ->
   0.011 / 0.0275 (IEA 2025). The row was entirely uncited; it is now fully
   cited. This moves the headline.
3. liquefaction range_low and Parameters liquefaction_electric 0.12 -> 0.15,
   a published Pembina figure. 0.12 appears to have been a misreading of
   Pembina's 0.11 tCO2e/t *reduction* as an absolute level.
4. lng_energy_content and lng_to_gas_bcm_per_mtpa: sources recorded, values
   unchanged.
5. Figure 7 retired, so its seven oil parameters are deleted from the sheet.

Run from the repository root:

    python tools/apply_found_citations.py
"""

from __future__ import annotations

from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Inputs" / "Canada_LNG_Data_Inputs.xlsx"

IPCC_URL = (
    "https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/2_Volume2/"
    "V2_1_Ch1_Introduction.pdf"
)
IEA_URL = (
    "https://iea.blob.core.windows.net/assets/df9b1bed-4e16-4db8-bec5-a5fa117a9130/"
    "AssessingemissionsfromLNGsupplyandabatementoptions.pdf"
)
GAN_URL = "https://doi.org/10.1038/s43247-024-01988-2"
PEMBINA_URL = (
    "https://www.pembina.org/reports/squaring-the-circle-state-of-lng-2023.pdf"
)

# --- Emission Factors -------------------------------------------------------

COMBUSTION_RANGE_SOURCES = (
    "Derived from the IPCC 2006 Guidelines Volume 2 Chapter 1 uncertainty "
    "ranges, "
    + IPCC_URL
    + " . Table 1.2 natural gas NCV 48.0 TJ/Gg (lower 46.5, upper 50.4) and "
    "Table 1.3 carbon content 15.3 kgC/GJ (lower 14.8, upper 15.9), both 95% "
    "confidence intervals. NCV x carbon content x 44/12 gives 2.523 / 2.693 / "
    "2.938 tCO2 per tonne. Cross-check: Table 2.2 gives 56,100 kgCO2/TJ, which "
    "x 48.0 TJ/Gg = 2.693, consistent. The IPCC central is pipeline natural "
    "gas at 2.693; this model's central is 2.75, the stoichiometric value for "
    "pure methane (44/16), which is the right central for LNG because "
    "liquefaction strips inerts and heavier fractions. The IPCC RELATIVE "
    "uncertainty (0.937 / 1.091) applied to 2.75 gives 2.58 / 3.00. The two "
    "uncertainty ranges are combined multiplicatively, which is conservative "
    "(it treats NCV and carbon content as perfectly correlated). Previous "
    "range_low was 2.50, wider than the IPCC interval supports and uncited."
)

REGAS_BASIS = (
    "0.021 tCO2e per t LNG. Gan et al. (2024), Communications Earth & "
    "Environment, " + GAN_URL + " : peer-reviewed US LNG lifecycle assessment "
    "placing regasification at 0.021 tCO2e/t. Adopted 3 September 2026, "
    "replacing an uncited 0.04 that sat above the top of the IEA range below. "
    "The previous 0.04 was labelled RMI Oil Climate Index; no OCI+ table or "
    "page states 0.04 t/t."
)
REGAS_RANGE_SOURCES = (
    "IEA (2025), Assessing Emissions from LNG Supply and Abatement Options, "
    "IEA, Paris, CC BY 4.0, page 16: \"Total GHG emissions from regasification "
    "are around 0.2-0.5 g CO2-eq/MJ of gas regasified.\" " + IEA_URL + " . "
    "Converted at the report's own stated basis of 55 MJ per kg of methane "
    "(footnote 2, page 7): 0.2 g/MJ = 0.011 and 0.5 g/MJ = 0.0275 tCO2e per "
    "tonne. IEA takes 1 t methane as 30 t CO2 on a 100-year GWP, against this "
    "model's 29.8. The Gan et al. central of 0.021 sits inside this range."
)
REGAS_KEY_UNCERTAINTY = (
    "Smallest stage, about 0.6 per cent of the lifecycle total after the move "
    "to 0.021. Varies with the destination terminal's technology: open-rack "
    "vaporisers (about 90 per cent of world plants) draw power for pumps and "
    "boil-off compressors, while submerged combustion vaporisers burn gas "
    "directly. IEA reports regasification energy demand at 0.3-0.5 per cent of "
    "the LNG imported."
)

LIQ_RANGE_SOURCES = (
    "range_low 0.15 tCO2e per t LNG: Pembina Institute, Squaring the Circle: "
    "State of LNG 2023, " + PEMBINA_URL + " , reported figure for LNG Canada "
    "Phase 1 under electric drive. Adopted 3 September 2026, replacing 0.12, "
    "which no Pembina document states and which appears to have been a "
    "misreading of the 0.11 tCO2e/t REDUCTION reported in Wellhead to "
    "Waterline (2014) as an absolute intensity. The same Pembina report gives "
    "0.059 for LNG Canada Phase 2 and 0.04 for Woodfibre; those are "
    "facility-specific and are not used. range_low is a counterfactual for "
    "the figure-8 appendix only and is not used in the central case. "
    "range_high 0.36 remains an uncited literature upper bound for gas-turbine "
    "plants. Corroboration on the central: IEA (2025), page 13, gives a global "
    "average liquefaction intensity of about 6 g CO2-eq/MJ of LNG, which at "
    "55 MJ/kg is 0.33 tCO2e/t - above this model's 0.29, so 0.29 is not a "
    "high-side choice. " + IEA_URL
)

# --- Parameters -------------------------------------------------------------

PARAM_UPDATES = {
    "liquefaction_electric": {
        "value": 0.15,
        "type": "cited",
        "source": (
            "Pembina Institute, Squaring the Circle: State of LNG 2023, "
            "reported intensity for LNG Canada Phase 1 under electric drive. "
            "Replaces 0.12 (3 September 2026), which no Pembina document "
            "states; 0.12 appears to have been a misreading of the 0.11 "
            "tCO2e/t reduction in Wellhead to Waterline (2014) as an absolute "
            "level. The same report gives 0.059 for Phase 2 and 0.04 for "
            "Woodfibre."
        ),
        "source_url": PEMBINA_URL,
        "notes": (
            "Figure-8 appendix counterfactual and Emission Factors range_low. "
            "NOT used in the central case, which is gas turbine 0.29 for every "
            "terminal. BC EAO 0.021 grid / 0.156 gas-barge are a separate SI "
            "sensitivity on a facility-total boundary."
        ),
    },
    "lng_energy_content": {
        "type": "cited",
        "source": (
            "Standard LNG higher heating value, 52 MMBtu per tonne. Equivalent "
            "to 54.86 GJ/t (x 1.05506 GJ per MMBtu), which agrees within 0.25% "
            "with the 55 MJ/kg HHV used by Balcombe et al. for the figure-10 "
            "comparison and by the IEA (2025) LNG supply report. The two "
            "figures in this repository are therefore consistent, not "
            "conflicting."
        ),
        "source_url": IEA_URL,
        "notes": (
            "Used to convert Saint John's reported throughput in TBtu into "
            "tonnes. Recorded 3 September 2026; previously an uncited method "
            "constant."
        ),
    },
    "lng_to_gas_bcm_per_mtpa": {
        "source": (
            "Volume of natural gas from one Mt of LNG, used for feedgas "
            "headroom against pipeline capacity and the Fermeuse capacity "
            "derivation. Basis: LNG density about 450 kg/m3 and a "
            "liquid-to-gas expansion ratio near 600:1 at 15 degrees C and "
            "101.325 kPa. The Energy Institute Statistical Review conversion "
            "gives 1.36 bcm per Mt on its own density and reference "
            "conditions; 1.38 is 1.5% higher and is retained. At 1.36 the "
            "Fermeuse derivation gives 5.05 mtpa rather than 4.98, so it "
            "rounds to 5.0 either way and no published figure moves."
        ),
        "notes": (
            "Read by no module; it backs the stored feedgas_demand_bcm_y and "
            "headroom_bcm_y columns on the register's Supporting "
            "Infrastructure sheet. Basis recorded 3 September 2026; "
            "previously an uncited method constant."
        ),
    },
}

# Figure 7 retired 3 September 2026: these rows feed no published output.
PARAMS_TO_DELETE = [
    "tmx_oil_upstream_per_barrel",
    "tmx_oil_transport_per_barrel",
    "tmx_oil_combustion_per_barrel",
    "tmx_oil_lifecycle_per_barrel",
    "tmx_total_system_bpd",
    "tmx_expansion_bpd",
    "days_per_year",
]


def _headers(ws) -> dict[str, int]:
    return {
        str(ws.cell(row=1, column=c).value).strip(): c
        for c in range(1, ws.max_column + 1)
        if ws.cell(row=1, column=c).value is not None
    }


def _row_of(ws, headers: dict[str, int], key_col: str, name: str) -> int | None:
    col = headers[key_col]
    for r in range(2, ws.max_row + 1):
        val = ws.cell(row=r, column=col).value
        if val is not None and str(val).strip() == name:
            return r
    return None


def _set(ws, headers: dict[str, int], row: int, **fields) -> None:
    for key, value in fields.items():
        if key not in headers:
            raise KeyError(f"No column {key!r} on {ws.title!r}")
        ws.cell(row=row, column=headers[key], value=value)


def main() -> None:
    wb = openpyxl.load_workbook(DATA)

    ef = wb["Emission Factors"]
    eh = _headers(ef)

    r = _row_of(ef, eh, "stage", "combustion")
    _set(ef, eh, r, range_low=2.58, range_sources=COMBUSTION_RANGE_SOURCES)
    print("combustion range_low 2.50 -> 2.58, cited to IPCC 2006 Tables 1.2/1.3")

    r = _row_of(ef, eh, "stage", "regasification")
    _set(
        ef,
        eh,
        r,
        central=0.021,
        range_low=0.011,
        range_high=0.0275,
        basis_for_central=REGAS_BASIS,
        range_sources=REGAS_RANGE_SOURCES,
        key_uncertainty=REGAS_KEY_UNCERTAINTY,
    )
    print("regasification central 0.04 -> 0.021, range 0.02/0.06 -> 0.011/0.0275")

    r = _row_of(ef, eh, "stage", "liquefaction")
    _set(ef, eh, r, range_low=0.15, range_sources=LIQ_RANGE_SOURCES)
    print("liquefaction range_low 0.12 -> 0.15, cited to Pembina 2023")

    ps = wb["Parameters"]
    ph = _headers(ps)
    for name, fields in PARAM_UPDATES.items():
        row = _row_of(ps, ph, "parameter", name)
        if row is None:
            raise KeyError(f"Parameter {name!r} not found")
        _set(ps, ph, row, **fields)
        print(f"parameter updated: {name}")

    deleted = []
    for name in PARAMS_TO_DELETE:
        row = _row_of(ps, ph, "parameter", name)
        if row is None:
            continue
        ps.delete_rows(row, 1)
        deleted.append(name)
    print(f"deleted {len(deleted)} retired oil parameters: {', '.join(deleted)}")

    wb.save(DATA)
    print("saved")


if __name__ == "__main__":
    main()
