"""Apply the sourcing-audit fixes to both input workbooks.

One-off. The model never writes Inputs/; this script does, once.

Fixes:
1. near_term_methane_gwp20 recalculated on the methane portion only.
2. Homepage citations replaced, or marked assumption, declared.
3. Discovery LNG returned to cancelled (GEM; no post-2025 activity).
4. Oil components sourced or declared; TMX 890,000 URL replaced.
5. New Parameters rows for values that had been living in Python.

Run from the repository root:

    python tools/fix_audit_findings.py
"""

from __future__ import annotations

from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Inputs" / "Canada_LNG_Data_Inputs.xlsx"
REGISTER = ROOT / "Inputs" / "Canada_LNG_Asset_Register.xlsx"

GWP20_FACTOR = 0.22 * (1.0 - 0.30) + 0.22 * 0.30 * 1.5 * (82.5 / 29.8)
# 0.428077... stored as 0.428


def _headers(ws) -> dict[str, int]:
    return {
        str(ws.cell(row=1, column=c).value).strip(): c
        for c in range(1, ws.max_column + 1)
        if ws.cell(row=1, column=c).value is not None
    }


def _find_param(ws, headers: dict[str, int], name: str) -> int | None:
    col = headers["parameter"]
    for r in range(2, ws.max_row + 1):
        val = ws.cell(row=r, column=col).value
        if val is not None and str(val).strip() == name:
            return r
    return None


def _set(ws, headers: dict[str, int], row: int, **fields) -> None:
    for key, value in fields.items():
        if key not in headers:
            raise KeyError(f"No column {key!r}")
        ws.cell(row=row, column=headers[key], value=value)


def _upsert_param(ws, headers: dict[str, int], spec: dict) -> None:
    row = _find_param(ws, headers, spec["parameter"])
    if row is None:
        row = ws.max_row + 1
    _set(ws, headers, row, **spec)


def _find_asset(ws, headers: dict[str, int], pid: str) -> int:
    col = headers["project_id"]
    for r in range(2, ws.max_row + 1):
        val = ws.cell(row=r, column=col).value
        if val is not None and str(val).strip() == pid:
            return r
    raise KeyError(f"No asset {pid}")


def patch_data_inputs() -> None:
    wb = openpyxl.load_workbook(DATA)

    # --- Scenarios: GWP20 on methane portion only ---
    sc = wb["Scenarios"]
    sh = _headers(sc)
    name_col = sh["name"]
    for r in range(2, sc.max_row + 1):
        name = sc.cell(row=r, column=name_col).value
        if name is None or str(name).strip() != "near_term_methane_gwp20":
            continue
        _set(
            sc,
            sh,
            r,
            projects_or_band=f"upstream {GWP20_FACTOR:.3f}",
            ramp_or_multiplier=(
                "x1.5 on the methane portion of the inventory, then GWP20/GWP100 "
                "(82.5/29.8) on that methane portion only"
            ),
            delay_or_gwp="GWP20 (82.5)",
            notes_or_electrification=(
                "Non-methane portion of inventory_as_reported (0.22 x 0.70 = 0.154) "
                "is unchanged. Methane portion is inventory x upstream_ch4_share x "
                "upstream_measurement_correction x (gwp20_ch4 / gwp100_ch4). "
                "Depends on the assumed methane share of 0.30. Was 0.33 "
                "(= 0.22 x 1.5 on the whole factor); that treated all upstream as methane."
            ),
            notes=(
                "Result 0.428 depends on upstream_ch4_share = 0.30. "
                "Pipeline methane is not re-weighted: no pipeline methane share exists."
            ),
        )
        break
    else:
        raise KeyError("Scenarios sheet has no near_term_methane_gwp20 row")

    # --- Emission Factors ---
    ef = wb["Emission Factors"]
    efh = _headers(ef)
    stage_col = efh["stage"]
    for r in range(2, ef.max_row + 1):
        stage = ef.cell(row=r, column=stage_col).value
        if stage is None:
            continue
        stage = str(stage).strip()
        if stage == "pipeline_transport":
            _set(
                ef,
                efh,
                r,
                basis_for_central=(
                    "Assumed 0.10 tCO2e per t LNG. No ICF or Sphera document stating "
                    "this figure was located. The BC Environmental Assessment Office "
                    "Coastal GasLink assessment (October 2014) reports 3.517 MtCO2e/yr "
                    "at 5 Bcf/d design capacity. Scaled to the 2.1 Bcf/d serving LNG "
                    "Canada Phase 1 that implies 1.48 MtCO2e/yr against this model's "
                    "1.47 at 0.10 t/t. That check confirms the arithmetic of scaling the "
                    "assumed factor, not an independent measurement of 0.10."
                ),
                range_sources=(
                    "Range 0.05-0.18 is an assumed literature band, not a cited "
                    "interval. Consistency check: BC EAO 2014 Coastal GasLink "
                    "Assessment Report, "
                    "https://projects.eao.gov.bc.ca/api/document/58868fd3e036fb0105768772/fetch/Assessment%20Report%20and%20Appendices%20for%20the%20CGL%20Project%20dated%20October%202014..pdf"
                ),
            )
        elif stage == "regasification":
            _set(
                ef,
                efh,
                r,
                basis_for_central=(
                    "Assumed 0.04 tCO2e per t LNG. Previously labelled RMI Oil "
                    "Climate Index; no OCI+ table or page states 0.04 t/t. "
                    "A peer-reviewed US LNG LCA (Gan et al. 2024, "
                    "Communications Earth & Environment) places regasification at "
                    "0.021 tCO2e/t, which sits at this row's range_low. The central "
                    "0.04 is a judgement in the middle of the 0.02-0.06 assumed range."
                ),
                range_sources=(
                    "Range is an assumed band. Corroboration at the low end: "
                    "Gan et al. 2024 https://doi.org/10.1038/s43247-024-01988-2 "
                    "(0.021 tCO2e/t). RMI OCI+ (https://ociplus.rmi.org/total-emissions) "
                    "does not publish a 0.04 t/t LNG regasification factor."
                ),
            )
        elif stage == "liquefaction":
            _set(
                ef,
                efh,
                r,
                range_sources=(
                    "range_low 0.12 is a declared assumption previously attributed to "
                    "a Pembina Institute electrified-LNG scenario. No Pembina document "
                    "stating 0.12 tCO2e/t was located (Squaring the Circle 2023 uses "
                    "0.15 / 0.059 / 0.04 for specific BC terminals; Wellhead to Waterline "
                    "2014 reports a 0.11 t/t reduction from electrification, not a 0.12 "
                    "absolute intensity). It is not used in the central case. "
                    "range_high 0.36 remains an assumed literature upper bound. "
                    "BC GGIRCA benchmark 0.16 is recorded on the Parameters sheet and "
                    "is not this row's central."
                ),
            )

    # --- Parameters ---
    ps = wb["Parameters"]
    ph = _headers(ps)

    _set(
        ps,
        ph,
        _find_param(ps, ph, "steady_state_utilisation"),
        source=(
            "IGU World LNG Report 2026: global average liquefaction utilisation "
            "83.9% in 2025 (decline from 86.5% in 2024)."
        ),
        source_url="https://www.igu.org/advocacy/graphics-data/2026-world-lng-report-03",
        notes=(
            "Figure also in the report PDF "
            "https://www.datocms-assets.com/146580/1783403747-igu-world-lng-report-2026.pdf "
            "(liquefaction capacity chapter). Nameplate utilisation, not available-capacity."
        ),
    )
    _set(
        ps,
        ph,
        _find_param(ps, ph, "tmx_total_system_bpd"),
        source=(
            "Trans Mountain Corporation, Management's Discussion and Analysis, "
            "31 March 2025: mechanical completion and commercial commencement of "
            "TMEP in Q2 2024 expanded the system to a combined nominal capacity of "
            "890,000 bpd."
        ),
        source_url=(
            "https://docs.transmountain.com/Corporate-Reports/"
            "TMC-03.31.25-Management-Report-Final.pdf"
        ),
        vintage="2025",
        notes="Nominal / nameplate capacity. Actual throughput runs below this.",
    )
    _set(
        ps,
        ph,
        _find_param(ps, ph, "liquefaction_electric"),
        type="assumption",
        source=(
            "Declared assumption. Previously cited as Pembina Institute electrified "
            "LNG; no Pembina document stating 0.12 tCO2e/t was located. Retained as "
            "the figure-8 counterfactual and Emission Factors range_low. Not used in "
            "the central case. EAO 0.021 / 0.156 are a separate SI."
        ),
        source_url="Not available",
        notes=(
            "Pembina Squaring the Circle (2023) uses 0.15 (LNG Canada Phase 1), "
            "0.059 (Phase 2) and 0.04 (Woodfibre), not 0.12. "
            "https://www.pembina.org/reports/squaring-the-circle-state-of-lng-2023.pdf"
        ),
    )
    _set(
        ps,
        ph,
        _find_param(ps, ph, "tmx_oil_lifecycle_per_barrel"),
        type="derived",
        source=(
            "Sum of tmx_oil_upstream_per_barrel (0.075) + "
            "tmx_oil_transport_per_barrel (0.008) + "
            "tmx_oil_combustion_per_barrel (0.43). See those rows for sources."
        ),
        source_url="Not available",
        notes=(
            "Derived identity. Oil runs at nameplate x 365 x 40 years, unlike LNG. "
            "Figure 7 states the utilisation asymmetry. Alberta bitumen is not "
            "given its own heavier upstream factor."
        ),
    )
    _set(
        ps,
        ph,
        _find_param(ps, ph, "canada_2030_overshoot_gap"),
        type="assumption",
        source=(
            "Round figure in the neighbourhood of projected 2030 emissions "
            "(646 Mt) minus the 417-455 Mt target range (arithmetic interval 191-229). "
            "200 is a judgement, not the difference of two cells."
        ),
        notes="Typed assumption. The interval is 191 to 229 Mt.",
    )
    _set(
        ps,
        ph,
        _find_param(ps, ph, "lifecycle_years_default"),
        source_url=(
            "https://www.cer-rec.gc.ca/en/applications-hearings/"
            "view-applications-projects/export-licence-applications/"
        ),
        notes=(
            "Fallback only. Licensed assets use authorised_export_end_year, "
            "sourced to the licence filing on Asset Sources (GL-330, GL-340, "
            "GL-346, GL-349), not this index page."
        ),
    )

    new_params = [
        {
            "parameter": "tmx_oil_upstream_per_barrel",
            "value": 0.075,
            "unit": "tCO2e/bbl",
            "type": "cited",
            "source": (
                "Natural Resources Canada, Roadmap for the Decarbonization of "
                "Canada's Oil and Gas Sector: 2021 oil sands production intensity "
                "approximately 75 kg CO2e/barrel. Slate: Canadian oil sands average, "
                "not a TMX ticket-by-ticket mix. TMX also carries conventional crude "
                "(NRCan ~48-49 kg/bbl), so 0.075 is oil-sands-heavy for the TMX mix."
            ),
            "source_url": (
                "https://natural-resources.canada.ca/climate-change/"
                "roadmap-decarbonization-canada-s-oil-gas-sector"
            ),
            "vintage": "2021",
            "notes": "Upstream production only. Not well-to-tank.",
        },
        {
            "parameter": "tmx_oil_transport_per_barrel",
            "value": 0.008,
            "unit": "tCO2e/bbl",
            "type": "assumption",
            "source": (
                "Declared assumption. 8 kgCO2e/bbl for pipeline transport. No document "
                "stating this figure for TMX was located."
            ),
            "source_url": "Not available",
            "vintage": None,
            "notes": "Not a cited TMX intensity.",
        },
        {
            "parameter": "tmx_oil_combustion_per_barrel",
            "value": 0.43,
            "unit": "tCO2e/bbl",
            "type": "cited",
            "source": (
                "IPCC 2006 Guidelines, Volume 2, Chapter 1: crude oil default "
                "NCV 42.3 TJ/Gg (Table 1.2) and carbon content 20.0 kg C/GJ "
                "(Table 1.3) give 0.423 tCO2/bbl at 100% oxidation; stored as 0.43. "
                "Slate: IPCC generic crude, not a WCSB or TMX assay."
            ),
            "source_url": (
                "https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/2_Volume2/"
                "V2_1_Ch1_Introduction.pdf"
            ),
            "vintage": "2006",
            "notes": "Combustion CO2 only. Rounding 0.423 to 0.43 is undeclared at the third decimal.",
        },
        {
            "parameter": "tmx_expansion_bpd",
            "value": 590000,
            "unit": "barrels per day",
            "type": "derived",
            "source": (
                "Increment implied by the expanded-system 890,000 bpd less the "
                "pre-expansion ~300,000 bpd, both stated in Trans Mountain's "
                "description of the May 2024 expansion."
            ),
            "source_url": (
                "https://www.transmountain.com/news/"
                "trans-mountain-pipeline-system-a-strategic-canadian-asset"
            ),
            "vintage": "2024",
            "notes": "890,000 - 300,000 = 590,000. Figure 7 expansion-only bar.",
        },
        {
            "parameter": "days_per_year",
            "value": 365,
            "unit": "days",
            "type": "method constant",
            "source": (
                "Civil year used to convert barrels per day to an annual total "
                "for the oil comparator. Not a leap-year correction."
            ),
            "source_url": "Not available",
            "vintage": None,
            "notes": "Structural method constant. LNG utilisation is a fraction of nameplate, not a day count.",
        },
        {
            "parameter": "lca_howarth_gwp20_low",
            "value": 7.37,
            "unit": "tCO2e per t LNG",
            "type": "cited",
            "source": "Howarth 2024, Energy Science & Engineering, Table 3, GWP20, average 38-day voyage.",
            "source_url": "https://doi.org/10.1002/ese3.1934",
            "vintage": "2024",
            "notes": "Figure 10 only. Not mixed with this model's GWP100 totals.",
        },
        {
            "parameter": "lca_howarth_gwp20_high",
            "value": 8.03,
            "unit": "tCO2e per t LNG",
            "type": "cited",
            "source": "Howarth 2024 Table 3, GWP20 upper end of the four tanker types.",
            "source_url": "https://doi.org/10.1002/ese3.1934",
            "vintage": "2024",
            "notes": "Figure 10 only.",
        },
        {
            "parameter": "lca_roman_white_w2r_p025",
            "value": 0.94,
            "unit": "tCO2e per t LNG",
            "type": "cited",
            "source": "Roman-White et al. 2021, ACS Sustainable Chemistry & Engineering, Table 1, China, GWP100, cradle to regasification, P2.5.",
            "source_url": "https://doi.org/10.1021/acssuschemeng.1c03307",
            "vintage": "2021",
            "notes": "Figure 10 only.",
        },
        {
            "parameter": "lca_roman_white_w2r_expected",
            "value": 1.19,
            "unit": "tCO2e per t LNG",
            "type": "cited",
            "source": "Roman-White et al. 2021 Table 1 expected value, not an arithmetic midpoint.",
            "source_url": "https://doi.org/10.1021/acssuschemeng.1c03307",
            "vintage": "2021",
            "notes": "Figure 10 only.",
        },
        {
            "parameter": "lca_roman_white_w2r_p975",
            "value": 1.51,
            "unit": "tCO2e per t LNG",
            "type": "cited",
            "source": "Roman-White et al. 2021 Table 1, P97.5.",
            "source_url": "https://doi.org/10.1021/acssuschemeng.1c03307",
            "vintage": "2021",
            "notes": "Figure 10 only.",
        },
        {
            "parameter": "lca_balcombe_lng_stages_low_g_per_mj_hhv",
            "value": 11.2,
            "unit": "gCO2e per MJ HHV",
            "type": "cited",
            "source": "Balcombe et al. 2016 literature range, liquefaction + tanker + regasification.",
            "source_url": "https://doi.org/10.1002/ese3.161",
            "vintage": "2016",
            "notes": "Figure 10. Converted with lca_hhv_mj_per_kg.",
        },
        {
            "parameter": "lca_balcombe_lng_stages_high_g_per_mj_hhv",
            "value": 31.1,
            "unit": "gCO2e per MJ HHV",
            "type": "cited",
            "source": "Balcombe et al. 2016 literature range, upper end.",
            "source_url": "https://doi.org/10.1002/ese3.161",
            "vintage": "2016",
            "notes": "Figure 10.",
        },
        {
            "parameter": "lca_hhv_mj_per_kg",
            "value": 55.0,
            "unit": "MJ per kg",
            "type": "cited",
            "source": (
                "Higher heating value used by Balcombe et al. to report LNG-stage "
                "intensities. Not this model's lng_energy_content (52)."
            ),
            "source_url": "https://doi.org/10.1002/ese3.161",
            "vintage": "2016",
            "notes": "Figure 10 conversion only.",
        },
        {
            "parameter": "placeholder_sensitivity_years",
            "value": "2033,2035",
            "unit": "years",
            "type": "assumption",
            "source": (
                "Sensitivity start years for assets with a blank first_export_year. "
                "Central remains assumed_first_export_year_if_missing (2030). "
                "These years are not filed dates."
            ),
            "source_url": "Not available",
            "vintage": "2026",
            "notes": "SI only. Do not treat as filed first-export years.",
        },
    ]
    for spec in new_params:
        _upsert_param(ps, ph, spec)

    # --- Data Gaps ---
    dg = wb["Data Gaps"]
    dh = _headers(dg)
    existing_fields = {
        str(dg.cell(row=r, column=dh["field"]).value)
        for r in range(2, dg.max_row + 1)
    }
    gap_rows = [
        {
            "field": "pipeline_transport central 0.10",
            "rows_affected": "Emission Factors:pipeline_transport",
            "current_state": "assumption, declared",
            "why": (
                "No ICF or Sphera document stating 0.10 tCO2e/t was located. "
                "The CGL 1.47 vs 1.48 check confirms scaling of the assumed factor, "
                "not an independent measurement."
            ),
            "what_would_fill_it": "A cited pipeline LCA or inventory intensity for BC gas transmission.",
            "priority": "medium - about 3% of the lifecycle total",
        },
        {
            "field": "regasification central 0.04",
            "rows_affected": "Emission Factors:regasification",
            "current_state": "assumption, declared",
            "why": "Previously labelled RMI Oil Climate Index; OCI+ does not publish 0.04 t/t.",
            "what_would_fill_it": "A named OCI+ or peer-reviewed regasification intensity used as central.",
            "priority": "low - about 1% of the lifecycle total",
        },
        {
            "field": "liquefaction_electric 0.12",
            "rows_affected": "Parameters:liquefaction_electric; Emission Factors range_low",
            "current_state": "assumption, declared",
            "why": "No Pembina document stating 0.12 tCO2e/t was located.",
            "what_would_fill_it": "A Pembina table, or replacement by the EAO 0.021/0.156 pair as the electric counterfactual.",
            "priority": "low - not used in the central case",
        },
        {
            "field": "tmx_oil_transport_per_barrel",
            "rows_affected": "Parameters:tmx_oil_transport_per_barrel",
            "current_state": "assumption, declared, 0.008 tCO2e/bbl",
            "why": "No TMX or CER document stating 8 kgCO2e/bbl was located.",
            "what_would_fill_it": "A TMX or OPGEE/GHGenius transport intensity for the Edmonton-Burnaby haul.",
            "priority": "low - figure 7 only",
        },
    ]
    row = dg.max_row + 1
    for spec in gap_rows:
        if spec["field"] in existing_fields:
            continue
        for key, value in spec.items():
            if key in dh:
                dg.cell(row=row, column=dh[key], value=value)
        row += 1

    wb.save(DATA)
    print(f"wrote {DATA}")
    print(f"GWP20 factor stored as {GWP20_FACTOR:.3f} (exact {GWP20_FACTOR:.6f})")


CER_LICENCE_URLS = {
    "lng_canada_phase_1": (
        "https://apps.cer-rec.gc.ca/REGDOCS/Item/Filing/A77188",
        "NEB licence GL-330, 27 May 2016 (Filing A77188). 40-year term. "
        "End year 2056 is issued year + term, a conservative reading; the term "
        "may instead run from first export.",
    ),
    "lng_canada_phase_2": (
        "https://apps.cer-rec.gc.ca/REGDOCS/Item/Filing/A77188",
        "Same GL-330 as Phase 1 (Filing A77188). End year 2056 is issued year + 40.",
    ),
    "woodfibre_lng": (
        "https://apps.cer-rec.gc.ca/REGDOCS/Item/Filing/A84304",
        "NEB licence GL-340, 9 June 2017 (Filing A84304), 40-year term; "
        "amended AO-001-GL-340 (Filing C22887). End year 2057 is issued year + term.",
    ),
    "ksi_lisims_lng": (
        "https://apps.cer-rec.gc.ca/REGDOCS/Item/Filing/C23652",
        "CER licence GL-346, 15 March 2023 (Filing C23652). 40-year term. "
        "End year 2063 is issued year + term.",
    ),
    "cedar_lng": (
        "https://apps.cer-rec.gc.ca/REGDOCS/Item/Filing/C37882",
        "CER licence GL-349, 14 January 2026 (Filing C37882). 40-year term. "
        "End year 2066 is issued year + term.",
    ),
}


def patch_register() -> None:
    wb = openpyxl.load_workbook(REGISTER)
    ar = wb["Asset Register"]
    ah = _headers(ar)
    drow = _find_asset(ar, ah, "discovery_t1t4")
    _set(
        ar,
        ah,
        drow,
        status="cancelled",
        calc_group="inactive",
        tier="inactive",
        tier_reason=(
            "Returned to cancelled 1 September 2026 to match GEM. GEM records "
            "cancelled (inferred 4 y). No regulatory filing, proponent statement "
            "or news report of current activity was found after GEM's September "
            "2025 snapshot. Rockyview Resources was struck off the Alberta "
            "corporate registry in 2017. The third-party table that had prompted "
            "the early_proposed classification was wrong about Grassy Point, "
            "Bear Head and Goldboro, all confirmed cancelled. Discovery is not on "
            "NRCan's proposed-and-under-construction list."
        ),
    )

    xs = wb["Asset Sources"]
    xh = _headers(xs)
    srow = _find_asset(xs, xh, "discovery_t1t4")
    _set(
        xs,
        xh,
        srow,
        status=(
            "GEM GGIT LNG Terminals (Sep 2025) Status = cancelled (inferred 4 y). "
            "Register now matches. Previously assigned proposed pending verification "
            "August 2026; reversed 1 September 2026 after a search found no "
            "post-2025 activity and the reclassification table was wrong on three "
            "other projects."
        ),
        calc_group="Same source as status. Inactive / cancelled, matching GEM.",
        tier=(
            "GEM cancelled. We differ no longer. GEM wiki: "
            "https://www.gem.wiki/Discovery_LNG_Terminal"
        ),
        gem_status_verbatim=(
            "GEM GGIT / wiki: cancelled (inferred 4 y), last edited on the wiki "
            "4 December 2024; tracker snapshot September 2025."
        ),
    )

    for pid, (url, note) in CER_LICENCE_URLS.items():
        row = _find_asset(xs, xh, pid)
        _set(
            xs,
            xh,
            row,
            cer_licence_url=url,
            authorised_export_end_year=note,
            export_term_note=(
                "40-year term from the licence filing. End year = licence_issued_year "
                "+ authorised_export_term_years, conservative (term may run from "
                "first export instead)."
            ),
        )

    dg = wb["Data Gaps"]
    dh = _headers(dg)
    existing_fields = {
        str(dg.cell(row=r, column=dh["field"]).value)
        for r in range(2, dg.max_row + 1)
    }
    disc_gap = {
        "field": "discovery_t1t4 status / calc_group / tier",
        "rows_affected": "discovery_t1t4",
        "current_state": "cancelled / inactive (matches GEM as of 1 Sep 2026)",
        "why": (
            "Returned to cancelled. GEM snapshot September 2025: cancelled "
            "(inferred 4 y). No post-2025 filing, proponent statement or news of "
            "current activity. Rockyview Resources struck off Alberta registry 2017. "
            "The third-party table that had classified it early_proposed was wrong "
            "about Grassy Point, Bear Head and Goldboro."
        ),
        "what_would_fill_it": "A current CER/IAAC filing or proponent statement of activity.",
        "priority": "closed - register now matches GEM",
    }
    if disc_gap["field"] not in existing_fields:
        row = dg.max_row + 1
        for key, value in disc_gap.items():
            if key in dh:
                dg.cell(row=row, column=dh[key], value=value)

    wb.save(REGISTER)
    print(f"wrote {REGISTER}")
    print("Discovery LNG: status/calc_group/tier -> cancelled / inactive / inactive")


if __name__ == "__main__":
    print(f"GWP20 exact {GWP20_FACTOR:.6f}")
    patch_data_inputs()
    patch_register()
