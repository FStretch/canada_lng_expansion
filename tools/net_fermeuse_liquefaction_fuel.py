"""Fermeuse capacity: net the liquefaction fuel share out of the derivation.

One-off. The model never writes Inputs/; this script does, once.

WHY. The register derived Fermeuse at 5.0 mtpa by dividing the proponent's
9.7 Tcf (275 bcm) resource by 1.38 bcm per mtpa over 40 years. But 1.38 bcm per
mtpa is the gas-equivalent of the LNG OUTPUT, not the feedgas needed to make
it: liquefaction burns a share of throughput as fuel, and the derivation
ignored that (academic review, E).

WHAT. The fuel share is taken from the model's own factors rather than a
literature percentage, so the derivation is internally consistent: the
liquefaction stage emits 0.29 tCO2e per t LNG, and burning gas releases 2.75
tCO2 per tonne (the combustion central), so the gas burned to liquefy one tonne
of LNG is 0.29 / 2.75 = 0.1055 t per t. Feedgas per tonne of LNG is therefore
1.1055 t, and the same resource supports 5.0 / 1.1055 = 4.5 mtpa. That treats
the whole liquefaction factor as fuel combustion; the small non-combustion part
(flaring, venting) makes 4.5 slightly low, but the effect is inside the
rounding.

The description "the lowest defensible derivation" is removed. It assumed full
recovery of a proponent-stated resource on a flat 40-year profile for an
associated-gas play; every one of those choices pushes the figure up.

Run from the repository root:

    python tools/net_fermeuse_liquefaction_fuel.py
"""

from __future__ import annotations

from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "Inputs" / "Canada_LNG_Asset_Register.xlsx"
DATA = ROOT / "Inputs" / "Canada_LNG_Data_Inputs.xlsx"

PROJECT_ID = "fermeuse_energy_flng"
RESOURCE_TCF = 9.7
RESOURCE_BCM = 275.0
BCM_PER_MTPA = 1.38
LIFE_YEARS = 40


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


def main() -> None:
    data = openpyxl.load_workbook(DATA, read_only=True, data_only=True)
    ef = data["Emission Factors"]
    rows = list(ef.iter_rows(values_only=True))
    hdr = [str(c).strip() for c in rows[0]]
    fac = {r[hdr.index("stage")]: float(r[hdr.index("central")]) for r in rows[1:] if r[0]}
    data.close()
    liq, comb = fac["liquefaction"], fac["combustion"]

    fuel_share = liq / comb                      # t gas burned per t LNG
    feedgas_per_t = 1.0 + fuel_share
    output_gross = RESOURCE_BCM / BCM_PER_MTPA / LIFE_YEARS
    output_net = output_gross / feedgas_per_t
    cap = round(output_net, 1)
    print(f"fuel share   {liq} / {comb} = {fuel_share:.4f} t per t LNG")
    print(f"gross        {RESOURCE_BCM} / {BCM_PER_MTPA} / {LIFE_YEARS} = {output_gross:.3f} mtpa")
    print(f"net          {output_gross:.3f} / {feedgas_per_t:.4f} = {output_net:.3f} -> {cap} mtpa")

    basis = (
        "Derived, not published, and conditional on the proponent's own resource claim. The "
        "proponent has not stated a liquefaction capacity. Fermeuse Energy states the project "
        f"would develop {RESOURCE_TCF} trillion cubic feet of offshore associated gas in the "
        f"Jeanne d'Arc Basin, which is {RESOURCE_BCM:.0f} billion cubic metres. DERIVATION: "
        f"{RESOURCE_BCM:.0f} bcm / {BCM_PER_MTPA} bcm per mtpa (lng_to_gas_bcm_per_mtpa, the "
        f"gas-equivalent of LNG OUTPUT) / {LIFE_YEARS} years = {output_gross:.2f} mtpa of "
        "output if every molecule became LNG. It does not: liquefaction burns part of the "
        "throughput as fuel. Using the model's own factors so the derivation is internally "
        f"consistent, the liquefaction stage emits {liq} tCO2e per t LNG and burning gas "
        f"releases {comb} tCO2 per t (combustion central), so fuel is {liq} / {comb} = "
        f"{fuel_share:.4f} t per t LNG and feedgas per tonne of LNG is {feedgas_per_t:.4f} t. "
        f"Output is therefore {output_gross:.2f} / {feedgas_per_t:.4f} = {output_net:.2f}, "
        f"recorded as {cap} mtpa. That treats the whole liquefaction factor as fuel "
        "combustion; the small non-combustion part (flaring, venting) makes the fuel share "
        "slightly high and the capacity slightly low, inside the rounding. WHAT PUSHES THIS "
        "FIGURE UP, and why it is not a lower bound: it assumes (a) 100 per cent recovery of "
        "a resource stated by the proponent, not a regulator or an independent estimate; "
        "(b) a flat 40-year production profile, whereas associated gas follows the oil "
        "decline and would front-load output; and (c) no reservation of gas for platform "
        "fuel, reinjection or domestic supply. Each choice raises the capacity, so the "
        "figure is closer to an upper bound on the proponent's claim than to a conservative "
        "one. Two other approaches give higher figures and were not used: the same resource "
        "over a 25-year life gives about 8 mtpa net of fuel, and benchmarking the stated "
        "US$12 to 15 billion capital cost against Ksi Lisims and Cedar gives 9 to 12 mtpa. "
        "An unsourced third-party table circulates a figure of 10 mtpa. HISTORY: 5.0 mtpa "
        "until 3 September 2026, from the same resource without netting the fuel share, "
        "and described as 'the lowest defensible derivation', which it was not."
    )

    wb = openpyxl.load_workbook(REGISTER)
    ar = wb["Asset Register"]
    ah = _headers(ar)
    r = _row_of(ar, ah, "project_id", PROJECT_ID)
    before = ar.cell(row=r, column=ah["capacity_mtpa"]).value
    ar.cell(row=r, column=ah["capacity_mtpa"], value=cap)
    ar.cell(row=r, column=ah["capacity_basis"], value=basis)
    print(f"Asset Register {PROJECT_ID}: capacity_mtpa {before} -> {cap}")

    src = wb["Asset Sources"]
    sh = _headers(src)
    r = _row_of(src, sh, "project_id", PROJECT_ID)
    src.cell(row=r, column=sh["capacity_mtpa"], value=(
        f"Derived from proponent-stated {RESOURCE_TCF} Tcf Jeanne d'Arc resource over {LIFE_YEARS} "
        "years, net of liquefaction fuel at the model's own liquefaction and combustion factors; "
        "not a published nameplate. Fermeuse Energy news release, 2 September 2025."))
    src.cell(row=r, column=sh["capacity_basis"], value="Compiled by us; derivation recorded step by step in capacity_basis")

    rd = wb["README"]
    for i in range(1, rd.max_row + 1):
        if rd.cell(row=i, column=1).value == "Fermeuse capacity is derived":
            rd.cell(row=i, column=2, value=(
                f"Fermeuse Energy has not published a liquefaction capacity. The register records {cap} mtpa, "
                f"derived from the stated {RESOURCE_TCF} Tcf Jeanne d'Arc resource over a 40-year life, net of the "
                "gas liquefaction burns as fuel. The derivation is conditional on the proponent's resource claim "
                "and assumes full recovery on a flat profile, both of which push it up; it is not a lower bound. "
                "This is an exception to the nameplate convention and is flagged in capacity_basis."))
            print("Register README: Fermeuse row restated")

    dg = wb["Data Gaps"]
    dh = _headers(dg)
    for i in range(2, dg.max_row + 1):
        if (dg.cell(row=i, column=dh["field"]).value == "capacity_mtpa"
                and "Fermeuse" in str(dg.cell(row=i, column=dh["rows_affected"]).value)):
            dg.cell(row=i, column=dh["current_state"], value=f"Derived {cap} mtpa")
            dg.cell(row=i, column=dh["why"], value=(
                f"Proponent has not published a liquefaction capacity. {cap} mtpa is derived from the stated "
                f"{RESOURCE_TCF} Tcf Jeanne d'Arc resource over a 40-year life at {BCM_PER_MTPA} bcm per mtpa, net of "
                "liquefaction fuel at the model's own factors (was 5.0 before netting fuel, 3 September 2026). "
                "Conditional on the proponent's resource claim; full recovery on a flat profile pushes it up. "
                "Higher figures (about 8 from a 25-year life; 9-12 from capital-cost benchmarking; an unsourced "
                "10 mtpa) were not used."))
            print("Data Gaps: Fermeuse capacity row restated")

    si = wb["Supporting Infrastructure"]
    ih = _headers(si)
    for i in range(2, si.max_row + 1):
        if "ermeuse" in str(si.cell(row=i, column=ih["serves_terminals"]).value or ""):
            print("Supporting Infrastructure row mentions Fermeuse; check terminal_capacity_mtpa by hand:",
                  si.cell(row=i, column=ih["terminal_capacity_mtpa"]).value)
    wb.save(REGISTER)

    # The lng_to_gas_bcm_per_mtpa note quoted the un-netted 4.98 / 5.05 pair.
    wb2 = openpyxl.load_workbook(DATA)
    ps = wb2["Parameters"]
    ph = _headers(ps)
    r = _row_of(ps, ph, "parameter", "lng_to_gas_bcm_per_mtpa")
    s = ps.cell(row=r, column=ph["source"]).value
    old = "At 1.36 the Fermeuse derivation gives 5.05 mtpa rather than 4.98, so it rounds to 5.0 either way and no published figure moves."
    assert old in s
    alt = RESOURCE_BCM / 1.36 / LIFE_YEARS / feedgas_per_t
    ps.cell(row=r, column=ph["source"], value=s.replace(old, (
        f"At 1.36 the Fermeuse derivation gives {alt:.2f} mtpa rather than {output_net:.2f} (both net of liquefaction "
        f"fuel), so it rounds to {cap} either way and no published figure moves.")))
    # Chains sheet: the export applies_to string carries the capacity totals.
    ch = wb2["Chains"]
    chh = _headers(ch)
    r = _row_of(ch, chh, "chain", "export")
    old_cap = ch.cell(row=r, column=chh["applies_to"]).value
    assert old_cap == "80.1 mtpa (14.0 operating, 5.4 under construction, 60.7 proposed)", old_cap
    delta = round(5.0 - cap, 1)
    ch.cell(row=r, column=chh["applies_to"], value=(
        f"{80.1 - delta:.1f} mtpa (14.0 operating, 5.4 under construction, {60.7 - delta:.1f} proposed)"))
    print(f"Chains export applies_to: {old_cap} -> {ch.cell(row=r, column=chh['applies_to']).value}")
    wb2.save(DATA)
    print("Data Inputs: lng_to_gas_bcm_per_mtpa note restated")
    print("saved")


if __name__ == "__main__":
    main()
