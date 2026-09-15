"""Re-derive the upstream factor on the current pipeline value (0.074).

One-off. The model never writes Inputs/; this script does, once.

WHY. The upstream basis cell said "net of pipeline transport that gives 0.22".
That netted the RETIRED pipeline value of 0.10 from the CER anchor of about
0.32 tCO2e/t. Pipeline moved to 0.074 on 3 September 2026 and the cell's
arithmetic stopped closing: 0.320 - 0.074 is not 0.22. The chain was quietly
dropping about 0.026 tCO2e/t relative to its own anchor (academic review, B6).

WHAT. The same CER anchor, the same conversion, the CURRENT pipeline value
netted, the same methane share and correction. Every step is computed here and
written into the basis cell so a reader can reproduce the number from the cell
alone. The four Scenarios rows that hang off the inventory value are rescaled
from the same base. Values are stored to three decimals; the previous
two-decimal storage hid the fact that the stored central depends on the
methane share.

Run from the repository root:

    python tools/rederive_upstream_on_pipeline.py
"""

from __future__ import annotations

from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Inputs" / "Canada_LNG_Data_Inputs.xlsx"

# The anchor and the conversions, exactly as the workbook already records them.
CER_BC_UPSTREAM_MT = 14.6        # MtCO2e, BC production + processing + transmission, 2022
CER_BC_MARKETABLE_BCM = 63.0     # bcm/y marketable gas
BCM_PER_MTPA = 1.38              # lng_to_gas_bcm_per_mtpa
CER_URL = (
    "https://www.cer-rec.gc.ca/en/data-analysis/energy-markets/"
    "provincial-territorial-energy-profiles/provincial-territorial-energy-profiles-british-columbia.html"
)


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


def _param(ws, headers, name) -> float:
    return float(ws.cell(row=_row_of(ws, headers, "parameter", name), column=headers["value"]).value)


def main() -> None:
    wb = openpyxl.load_workbook(DATA)
    ef, ps, sc = wb["Emission Factors"], wb["Parameters"], wb["Scenarios"]
    eh, ph = _headers(ef), _headers(ps)

    pipeline = float(ef.cell(row=_row_of(ef, eh, "stage", "pipeline_transport"), column=eh["central"]).value)
    share = _param(ps, ph, "upstream_ch4_share")
    corr = _param(ps, ph, "upstream_measurement_correction")
    gwp100 = _param(ps, ph, "gwp100_ch4")
    gwp20 = _param(ps, ph, "gwp20_ch4")
    assert pipeline == 0.074, pipeline

    # ---- the derivation, every step ------------------------------------
    lng_mt_equiv = CER_BC_MARKETABLE_BCM / BCM_PER_MTPA          # Mt LNG-equivalent per year
    anchor = CER_BC_UPSTREAM_MT / lng_mt_equiv                    # t/t, incl. transmission
    inventory = anchor - pipeline                                 # t/t, net of pipeline
    central = inventory * (1 - share + corr * share)              # 1.5x on the methane portion
    high = inventory * (1 - share + 1.7 * share)                  # 1.7x, BC aircraft survey
    co2_floor = inventory * (1 - share)
    gwp20_factor = co2_floor + inventory * share * corr * (gwp20 / gwp100)

    r3 = lambda x: round(x, 3)
    inv3, cen3, high3, g20_3 = r3(inventory), r3(central), r3(high), r3(gwp20_factor)
    print(f"anchor      {CER_BC_UPSTREAM_MT} / ({CER_BC_MARKETABLE_BCM} / {BCM_PER_MTPA}) = {CER_BC_UPSTREAM_MT} / {lng_mt_equiv:.3f} = {anchor:.4f} t/t")
    print(f"inventory   {anchor:.4f} - {pipeline} = {inventory:.4f} -> {inv3}")
    print(f"central     {inventory:.4f} x (1 - {share} + {corr} x {share}) = {central:.4f} -> {cen3}")
    print(f"high        {inventory:.4f} x (1 - {share} + 1.7 x {share}) = {high:.4f} -> {high3}")
    print(f"co2 floor   {inventory:.4f} x (1 - {share}) = {co2_floor:.4f}")
    print(f"gwp20       {co2_floor:.4f} + {inventory:.4f} x {share} x {corr} x ({gwp20}/{gwp100}) = {gwp20_factor:.4f} -> {g20_3}")

    basis = (
        f"DERIVED, every step shown; re-derived 3 September 2026 on the current pipeline "
        f"factor. (1) ANCHOR: the Canada Energy Regulator reports British Columbia oil and "
        f"gas production, processing AND transmission emissions of {CER_BC_UPSTREAM_MT} MtCO2e "
        f"for 2022 against roughly {CER_BC_MARKETABLE_BCM:.0f} bcm/y of marketable gas "
        f"({CER_URL}). (2) CONVERSION: {CER_BC_MARKETABLE_BCM:.0f} bcm / {BCM_PER_MTPA} bcm "
        f"per Mt LNG (lng_to_gas_bcm_per_mtpa) = {lng_mt_equiv:.2f} Mt LNG-equivalent, so the "
        f"anchor is {CER_BC_UPSTREAM_MT} / {lng_mt_equiv:.2f} = {anchor:.4f} tCO2e per t LNG "
        f"INCLUDING transmission. (3) NET OF PIPELINE: transmission is this model's separate "
        f"pipeline_transport stage, so its current central of {pipeline} is removed: "
        f"{anchor:.4f} - {pipeline} = {inventory:.4f}, stored as {inv3}. This is the official "
        f"inventory upstream factor and the inventory_as_reported scenario. (4) METHANE SHARE: "
        f"upstream_ch4_share = {share}, the centre of the Johnson et al. (2023) bracket. "
        f"(5) CORRECTION: peer-reviewed measurement studies find Canadian inventories understate "
        f"upstream methane by 1.5 to 1.7 times; upstream_measurement_correction = {corr} is "
        f"applied to the methane portion only. (6) RESULT: {inv3} x (1 - {share} + {corr} x "
        f"{share}) = {inv3} x {1 - share + corr * share:.3f} = {central:.4f}, stored as {cen3}. "
        f"HISTORY: until 3 September 2026 the cell read 'net of pipeline transport that gives "
        f"0.22', which had netted the RETIRED pipeline value of 0.10 ({anchor:.3f} - 0.10 = "
        f"0.220); when pipeline moved to 0.074 that arithmetic stopped closing and the chain "
        f"dropped about {anchor - 0.10 - inventory:+.3f} t/t against its own anchor. Central "
        f"was 0.25 (0.2475 at two decimals). Values are now stored to three decimals because "
        f"at two the stored central did not visibly depend on the methane share; at three it "
        f"does: {inv3} x (1 + 0.5 x 0.30) = {inv3 * 1.15:.3f} at a share of 0.30. The "
        f"measurement_high (1.7x) and near_term_methane_gwp20 scenarios are rescaled from the "
        f"same {inv3} base on the Scenarios sheet."
    )
    key = (
        "The largest uncertainty in the model. BC does not publish the CO2 and methane split "
        "for upstream emissions, so the methane share is a bracketed judgement "
        f"(upstream_ch4_share = {share}, from Johnson et al. 2023; tested across 0.20 to 0.40). "
        "The national oil and gas figure is 20 per cent methane, but that includes oil sands, "
        "which are far more carbon dioxide intensive than gas production. Measurement studies "
        "also find Montney intensity is among the lowest in North America, while BC reports a "
        "51 per cent methane reduction by 2023, both of which argue against the high case."
    )
    r = _row_of(ef, eh, "stage", "upstream_production")
    before = (ef.cell(row=r, column=eh["central"]).value, ef.cell(row=r, column=eh["range_low"]).value)
    ef.cell(row=r, column=eh["central"], value=cen3)
    ef.cell(row=r, column=eh["range_low"], value=inv3)
    ef.cell(row=r, column=eh["basis_for_central"], value=basis)
    ef.cell(row=r, column=eh["key_uncertainty"], value=key)
    print(f"Emission Factors upstream_production: central {before[0]} -> {cen3}, range_low {before[1]} -> {inv3}")

    # ---- Scenarios sheet -------------------------------------------------
    sh = {str(c.value).strip(): c.column for c in sc[1] if c.value is not None}
    rows = {sc.cell(row=i, column=sh["name"]).value: i for i in range(2, sc.max_row + 1)}
    band = sh["projects_or_band"]
    sc.cell(row=rows["inventory_as_reported"], column=band, value=f"upstream {inv3}")
    sc.cell(row=rows["inventory_as_reported"], column=sh["notes"],
            value=f"Lower bound. Was 0.22 until 3 September 2026 (netted the retired pipeline 0.10); {inv3} nets the current 0.074. Derivation in the Emission Factors basis cell.")
    sc.cell(row=rows["measurement_central"], column=band, value=f"upstream {cen3}")
    sc.cell(row=rows["measurement_central"], column=sh["notes"],
            value=f"Was 0.25 (0.2475 at two decimals) until 3 September 2026. = {inv3} x (1 - {share} + {corr} x {share}).")
    sc.cell(row=rows["measurement_high"], column=band, value=f"upstream {high3}")
    sc.cell(row=rows["measurement_high"], column=sh["notes"],
            value=f"Was 0.26 until 3 September 2026. = {inv3} x (1 - {share} + 1.7 x {share}).")
    sc.cell(row=rows["near_term_methane_gwp20"], column=band, value=f"upstream {g20_3}")
    sc.cell(row=rows["near_term_methane_gwp20"], column=sh["notes_or_electrification"],
            value=(f"Non-methane portion of inventory_as_reported ({inv3} x {1 - share} = {co2_floor:.4f}) is unchanged. "
                   f"Methane portion is inventory x upstream_ch4_share x upstream_measurement_correction x (gwp20_ch4 / gwp100_ch4) "
                   f"= {inv3} x {share} x {corr} x ({gwp20} / {gwp100}) = {gwp20_factor - co2_floor:.4f}. Total {gwp20_factor:.4f}, stored {g20_3}. "
                   f"Was 0.393 on the 0.22 base, 0.428 at a share of 0.30, and 0.33 before that (= 0.22 x 1.5 on the whole factor)."))
    sc.cell(row=rows["near_term_methane_gwp20"], column=sh["notes"],
            value=f"Result {g20_3} depends on upstream_ch4_share = {share} and on the {inv3} inventory base. Pipeline methane is not re-weighted: no pipeline methane share exists.")
    print(f"Scenarios: inventory {inv3}, central {cen3}, high {high3}, gwp20 {g20_3}")

    # ---- upstream_ch4_share cell: the two routes were expressed against 0.22 ----
    r = _row_of(ps, ph, "parameter", "upstream_ch4_share")
    src = ps.cell(row=r, column=ph["source"]).value
    route_a_pct = 0.0666 / inventory * 100
    upstream_mt = inventory * lng_mt_equiv
    route_b_pct = 2.53 / upstream_mt * 100
    old_a = "or 30.3% of the 0.22 inventory_as_reported upstream factor"
    new_a = f"or {route_a_pct:.1f}% of the {inv3} inventory_as_reported upstream factor (30.3% of the pre-3-September 0.22)"
    old_b = ("the 0.22 factor over 63 bcm (45.7 Mt LNG-equivalent at 1.38 bcm per mtpa) implies 10.04 MtCO2e "
             "of upstream emissions net of transmission, so the share is 25.2%")
    new_b = (f"the {inv3} factor over 63 bcm ({lng_mt_equiv:.1f} Mt LNG-equivalent at 1.38 bcm per mtpa) implies "
             f"{upstream_mt:.2f} MtCO2e of upstream emissions net of transmission, so the share is {route_b_pct:.1f}% "
             f"(25.2% on the pre-3-September 0.22 base)")
    assert old_a in src and old_b in src, "upstream_ch4_share source text has changed; check before patching"
    src = src.replace(old_a, new_a).replace(old_b, new_b)
    src = src.replace(
        "0.25 is adopted as the centre of that bracket,",
        f"On the re-derived {inv3} base (3 September 2026) the two routes give {route_a_pct:.1f}% and {route_b_pct:.1f}%, "
        "which still straddle 25; the bracket and the adopted value are unchanged. 0.25 is adopted as the centre of that bracket,",
    )
    ps.cell(row=r, column=ph["source"], value=src)
    notes = ps.cell(row=r, column=ph["notes"]).value
    old_n = "WHAT THIS VALUE DRIVES: the CO2 floor in the per-gas split (inventory_as_reported x (1 - share) = 0.165 at 0.25, was 0.154 at 0.30)"
    new_n = f"WHAT THIS VALUE DRIVES: the CO2 floor in the per-gas split (inventory_as_reported x (1 - share) = {co2_floor:.4f} at 0.25 on the {inv3} base; 0.165 on the old 0.22 base, 0.154 at a share of 0.30)"
    old_n2 = ("It does NOT drive the measurement_central 0.25 or measurement_high 0.26 upstream factors, which are stored values on the Scenarios sheet: "
              "0.22 x (1 - s + 1.5s) is 0.2530 at s=0.30 and 0.2475 at s=0.25, both rounding to the stored 0.25. "
              "The headline lifetime, peak and territorial split are therefore unchanged by this move.")
    new_n2 = (f"SINCE 3 September 2026 it DOES visibly drive the stored measurement_central and measurement_high factors, which are now stored to three "
              f"decimals: {inv3} x (1 - s + 1.5s) is {inv3 * 1.15:.3f} at s=0.30 and {cen3} at s=0.25. Under the previous two-decimal storage both "
              "rounded to 0.25 and the headline was insensitive to the share; that insensitivity was a rounding artefact, not a property of the model.")
    assert old_n in notes and old_n2 in notes, "upstream_ch4_share notes text has changed; check before patching"
    ps.cell(row=r, column=ph["notes"], value=notes.replace(old_n, new_n).replace(old_n2, new_n2))
    print(f"upstream_ch4_share: routes restated on the {inv3} base -> A {route_a_pct:.1f}%, B {route_b_pct:.1f}%; value unchanged at {share}")

    # ---- Derived Fields and README sheet cells that quoted the old numbers ----
    df = wb["Derived Fields"]
    for i in range(1, df.max_row + 1):
        for j in range(1, df.max_column + 1):
            v = df.cell(row=i, column=j).value
            if isinstance(v, str) and "At measurement_central: 0.25 - 0.22 x 0.7 = 0.096." in v:
                df.cell(row=i, column=j, value=v.replace(
                    "At measurement_central: 0.25 - 0.22 x 0.7 = 0.096.",
                    f"At measurement_central: {cen3} - {inv3} x {1 - share} = {central - co2_floor:.4f} (was 0.25 - 0.22 x 0.7 = 0.096 before 3 September 2026)."))
                print("Derived Fields: upstream_ch4_derived_co2e example restated")
            if isinstance(v, str) and "whose upstream factor (0.22 x 1.5) is not a GWP100" in v:
                df.cell(row=i, column=j, value=v.replace("whose upstream factor (0.22 x 1.5) is not a GWP100",
                                                         "whose upstream factor (GWP20-weighted methane portion) is not a GWP100"))
                print("Derived Fields: ch4_mass_kt note restated")
    rd = wb["README"]
    for i in range(1, rd.max_row + 1):
        v = rd.cell(row=i, column=2).value
        if isinstance(v, str) and "Net of pipeline transport this gives 0.22" in v:
            rd.cell(row=i, column=2, value=(
                f"CER reports British Columbia oil and gas production, processing and transmission emissions of {CER_BC_UPSTREAM_MT} MtCO2e for 2022, "
                f"against roughly {CER_BC_MARKETABLE_BCM:.0f} bcm/y of marketable gas: {anchor:.3f} tCO2e per tonne of LNG including transmission. "
                f"Net of the model's own pipeline_transport central ({pipeline}) this gives {inv3}. Peer-reviewed measurement studies find Canadian "
                f"inventories understate upstream methane by 1.5 to 1.7 times; applied to a {share} methane share that gives a central of {cen3}. "
                f"Every step is in the Emission Factors basis cell. Re-derived 3 September 2026; the earlier 0.22 had netted the retired pipeline 0.10."))
            print("README sheet: upstream basis row restated")

    wb.save(DATA)
    print("saved")


if __name__ == "__main__":
    main()
