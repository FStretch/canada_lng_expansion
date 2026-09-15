"""Every external comparison this model holds, in one table.

The comparisons were scattered across `range_sources` cells on the Emission
Factors sheet and inside figure 10, so a reviewer had to assemble them. This
builds the assembled version: one row per comparison, each carrying **both**
boundaries, so the like-for-like question is answered on the row rather than
in a footnote.

Values are read from the workbooks and from `src.lca_comparison`, so the table
cannot drift from the factors it compares.
"""

from __future__ import annotations

import pandas as pd

from src.inputs import get_param
from src.lca_comparison import build_lca_comparison, export_stage_intensity

# Conversion used for every gCO2e/MJ figure below. The IEA states 55 MJ/kg as
# its own basis (footnote 2, p. 7 of the 2025 LNG supply report); this model's
# lng_energy_content of 52 MMBtu/t is 54.863 GJ/t, within 0.25%.
IEA_MJ_PER_KG = 55.0

IEA = (
    "IEA (2025), Assessing Emissions from LNG Supply and Abatement Options, "
    "IEA, Paris, CC BY 4.0"
)
IEA_URL = (
    "https://iea.blob.core.windows.net/assets/df9b1bed-4e16-4db8-bec5-a5fa117a9130/"
    "AssessingemissionsfromLNGsupplyandabatementoptions.pdf"
)


def _g_per_mj_to_t_per_t(g: float) -> float:
    return g * IEA_MJ_PER_KG / 1000.0


def build_benchmark_table(inputs: dict) -> pd.DataFrame:
    si = export_stage_intensity(inputs)
    lca = build_lca_comparison(inputs)
    params = inputs["params"]
    rows = []

    rows.append({
        "comparison": "Liquefaction",
        "our_value_tco2e_per_t": si["liquefaction"],
        "our_boundary": "Liquefaction stage only, gas turbine drive, every terminal",
        "external_low": None,
        "external_central": _g_per_mj_to_t_per_t(6.0),
        "external_high": None,
        "external_as_published": "about 6 gCO2e/MJ of LNG",
        "external_source": f"{IEA}, p. 13. {IEA_URL}",
        "external_boundary": (
            "Global average across 45 liquefaction terminals, 2024. "
            "Liquefaction stage. CO2 plus methane at 1 t CH4 = 30 t CO2."
        ),
        "like_for_like": "Close. Same stage; IEA is a global fleet average, ours is a single gas-turbine assumption applied to every terminal.",
        "direction": "ours LOWER than the world average",
        "note": (
            "0.29 is not a high-side choice: the IEA global average is 14% "
            "above it. Held at 0.29 by the paper's ground rules."
        ),
    })

    rows.append({
        "comparison": "Shipping",
        "our_value_tco2e_per_t": si["shipping"],
        "our_boundary": (
            "British Columbia to north-east Asia basis, 3,800 nm one way "
            "(7,600 nm / 14,075 km round trip), then scaled per asset by "
            "route_distance_nm / 3,800"
        ),
        "external_low": _g_per_mj_to_t_per_t(2.5),
        "external_central": _g_per_mj_to_t_per_t(3.3),
        "external_high": _g_per_mj_to_t_per_t(3.5),
        "external_as_published": (
            "3.5 gCO2e/MJ global average; 3.3 to China; 2.5 to the EU"
        ),
        "external_source": f"{IEA}, p. 15. {IEA_URL}",
        "external_boundary": (
            "Fleet average over about 7,000 round trips in 2024, average "
            "round trip 10,000 km. Includes methane slip at 1 t CH4 = 30 t CO2."
        ),
        "like_for_like": (
            "NO. The IEA average round trip is 10,000 km against our 14,075 km "
            "BC-basis voyage, and the IEA figure is an origin-blended average "
            "to a destination, not a route. Ours would have to be scaled up, "
            "not down, to compare."
        ),
        "direction": "ours LOWER, on a LONGER voyage",
        "note": (
            "The most likely understatement in the model. Per km the IEA "
            "implies roughly 2.3x our intensity. Not acted on: the boundaries "
            "differ and no like-for-like BC-to-Asia figure was located."
        ),
    })

    rows.append({
        "comparison": "Pipeline transport",
        "our_value_tco2e_per_t": si["pipeline_transport"],
        "our_boundary": (
            "Feedgas transmission from processing to the terminal. Flat, "
            "NOT scaled by distance. In-scope lines are 670 km (Coastal "
            "GasLink), 750 km (PRGT) and 47 km (FortisBC Eagle Mountain)."
        ),
        "external_low": 0.0735,
        "external_central": 0.074,
        "external_high": 0.0744,
        "external_as_published": (
            "Route A 1.34 gCO2e/MJ (4.20 at transmission pipeline outlet less "
            "2.86 at plant exit) = 0.0735; Route B 8.3 MtCO2e over ~170 bcm "
            "= 1.356 gCO2e/MJ = 0.0744"
        ),
        "external_source": (
            "Liu et al. (2021), ES&T 55(14):9711-9720, doi "
            "10.1021/acs.est.0c06353, Results p. 9713, restated at plant exit "
            "by Modern West Advisory for Emissions Reduction Alberta (2022), "
            "section 5.3 p. 43. Cross-check: CER Market Snapshot, Greening "
            "Canada's pipeline infrastructure (2022), citing ECCC NIR "
            "1990-2019 Part 1 Table 2-5."
        ),
        "external_boundary": (
            "Route A: one Alberta operator (Seven Generations, Kakwa), "
            "1,100 km modelled transmission line, mass and energy allocation. "
            "Route B: Canadian national total for pipeline transport, "
            "primarily compressor-station combustion, over national marketable "
            "gas."
        ),
        "like_for_like": (
            "Partly. Both are Canadian gas transmission. Neither is calibrated "
            "to the in-scope line lengths, and this model does not scale "
            "pipeline by distance."
        ),
        "direction": "ADOPTED as the central, 3 September 2026",
        "note": (
            "The two routes converge to within 1.2%. The retired 0.10 was "
            "assumed and about 35% above both. Because the sources sit at "
            "1,100 km and a national average haul while the in-scope lines are "
            "shorter, 0.074 is more likely high than low for these assets."
        ),
    })

    rows.append({
        "comparison": "Regasification",
        "our_value_tco2e_per_t": si["regasification"],
        "our_boundary": "Regasification at the destination import terminal",
        "external_low": _g_per_mj_to_t_per_t(0.2),
        "external_central": 0.021,
        "external_high": _g_per_mj_to_t_per_t(0.5),
        "external_as_published": (
            "Mukherjee et al. 0.021 tCO2e/t; IEA 0.2-0.5 gCO2e/MJ of gas regasified"
        ),
        "external_source": (
            "Mukherjee et al. (2025), Communications Earth & Environment 6:16, doi "
            f"10.1038/s43247-024-01988-2. Range: {IEA}, p. 16. {IEA_URL}"
        ),
        "external_boundary": (
            "Mukherjee: US LNG lifecycle assessment, regasification stage. IEA: "
            "global average across 220 regasification terminals, mostly "
            "open-rack vaporisers."
        ),
        "like_for_like": "Yes. Same stage, and the Mukherjee central sits inside the IEA band.",
        "direction": "ADOPTED as the central, 3 September 2026",
        "note": (
            "The retired 0.04 was uncited and sat above the top of the IEA "
            "band."
        ),
    })

    rows.append({
        "comparison": "Well to regasification (no combustion)",
        "our_value_tco2e_per_t": lca["model_w2r"],
        "our_boundary": (
            "Upstream + pipeline + liquefaction + shipping + regasification, "
            "GWP100, no combustion. Shipping on the unscaled BC basis."
        ),
        "external_low": 0.94,
        "external_central": float(get_param(params, "lca_roman_white_w2r_expected")),
        "external_high": 1.51,
        "external_as_published": "0.94 / 1.19 expected / 1.51 tCO2e per t LNG",
        "external_source": (
            "Roman-White et al. (2021), ACS Sustainable Chemistry & "
            "Engineering, doi 10.1021/acssuschemeng.1c03307, Table 1, "
            "US Gulf Coast to China"
        ),
        "external_boundary": (
            "Cradle to regasification, GWP100. US supply chain, US Gulf to "
            "China, a much longer voyage than BC to north-east Asia."
        ),
        "like_for_like": (
            "NO on geography. Same boundary, but US upstream methane "
            "intensities are materially higher than Western Canadian ones and "
            "the US Gulf voyage is roughly 2.4x the BC one."
        ),
        "direction": "ours LOWER, and expected to be",
        "note": (
            "Our 0.755 sits below their 2.5th percentile. Most of the gap is "
            "upstream methane and voyage length, both of which genuinely "
            "differ; but it is the comparison a reviewer will press hardest."
        ),
    })

    rows.append({
        "comparison": "LNG stages only (liquefaction + shipping + regasification)",
        "our_value_tco2e_per_t": lca["model_lng"],
        "our_boundary": (
            "Liquefaction + shipping + regasification, GWP100. Excludes "
            "upstream, pipeline and combustion. Shipping on the unscaled BC basis."
        ),
        "external_low": (
            float(get_param(params, "lca_balcombe_lng_stages_low_g_per_mj_hhv"))
            * float(get_param(params, "lca_hhv_mj_per_kg")) / 1000.0
        ),
        "external_central": None,
        "external_high": (
            float(get_param(params, "lca_balcombe_lng_stages_high_g_per_mj_hhv"))
            * float(get_param(params, "lca_hhv_mj_per_kg")) / 1000.0
        ),
        "external_as_published": "11.2 to 31.1 gCO2e/MJ HHV",
        "external_source": (
            "Balcombe et al. (2016), literature compilation for liquefaction, "
            "tanker and regasification. Converted at "
            f"{float(get_param(params, 'lca_hhv_mj_per_kg')):g} MJ/kg HHV."
        ),
        "external_boundary": (
            "Same three stages. A compilation across many studies, routes and "
            "vintages, so the spread is between-study variation rather than "
            "an uncertainty interval on one system."
        ),
        "like_for_like": (
            "Boundary yes, vintage no. The compilation predates both the "
            "current LNG carrier fleet and modern liquefaction trains."
        ),
        "direction": "ours LOWER than the bottom of the range",
        "note": (
            "Our 0.431 is below their 0.62 low. Driven by shipping on the "
            "short BC route and by regasification at the cited 0.021."
        ),
    })

    df = pd.DataFrame(rows)
    df["our_vs_external_central_pct"] = [
        (
            100.0 * (r["our_value_tco2e_per_t"] / r["external_central"] - 1.0)
            if r["external_central"]
            else None
        )
        for _, r in df.iterrows()
    ]
    df["scenario_note"] = (
        "Our values are the central case. Every external figure is quoted on "
        "its own boundary, given in external_boundary."
    )
    return df


def format_benchmark_markdown(df: pd.DataFrame) -> list[str]:
    lines = []
    lines.append("## Benchmark comparison")
    lines.append("")
    lines.append(
        "Every external comparison the model holds, in one place. Each row "
        "carries **both** boundaries, because the like-for-like question is "
        "what makes the comparison worth anything. Machine-readable copy: "
        "`Outputs/benchmark_comparison.csv`; also a sheet in `SLIDE_TABLES.xlsx`."
    )
    lines.append("")
    lines.append(
        "| comparison | ours | external | source | like for like? | direction |"
    )
    lines.append("|---|---|---|---|---|---|")
    for _, r in df.iterrows():
        if r["external_central"] is not None and not pd.isna(r["external_central"]):
            ext = f"{r['external_central']:.3f}"
            if r["external_low"] is not None and not pd.isna(r["external_low"]):
                ext += f" [{r['external_low']:.3f}, {r['external_high']:.3f}]"
        else:
            ext = f"{r['external_low']:.2f}–{r['external_high']:.2f}"
        src = str(r["external_source"]).split(",")[0]
        lines.append(
            f"| {r['comparison']} | **{r['our_value_tco2e_per_t']:.3f}** | {ext} | "
            f"{src} | {str(r['like_for_like']).split('.')[0]} | {r['direction']} |"
        )
    lines.append("")
    lines.append(
        "All values in tCO2e per tonne LNG. **Every comparison that is not an "
        "adopted value points the same way: this model sits at or below the "
        "external figure.** The two that matter most are shipping, where the "
        "IEA implies roughly 2.3x our intensity per kilometre, and "
        "liquefaction, where the IEA global average is 14% above our 0.29. "
        "Neither is like-for-like enough to act on, and both are recorded here "
        "rather than left in a source cell."
    )
    lines.append("")
    return lines
