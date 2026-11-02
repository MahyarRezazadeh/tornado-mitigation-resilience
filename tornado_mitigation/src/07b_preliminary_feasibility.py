"""Section 62 pilot: FEMA treatment x NOAA tornado feasibility counts before heavy downloads.

Output: output/final/preliminary_feasibility.md (+ csv tables in output/tables/)
"""
from __future__ import annotations

import pandas as pd

from utils import FINAL, INTER, PROC, TABLES, XWALK, get_logger

log = get_logger(__file__)
END = pd.Timestamp("2025-12-31")
ANALYSIS_START = 1990


def counts(ct: pd.DataFrame, tor: pd.DataFrame, ever_ctrl: set) -> dict:
    m = tor.merge(ct[["county_fips", "first_treat_date"]], on="county_fips")
    post = m[m["date"] > m["first_treat_date"]]
    r = {"Treated counties": ct.county_fips.nunique(),
         "Treated states": ct.state_fips.nunique(),
         "Median treatment year": int(ct.first_treat_date.dt.year.median()),
         "Post-treatment tornado counties": post.county_fips.nunique(),
         "Post-trt EF1+ counties": post[post.ef >= 1].county_fips.nunique(),
         "Post-trt EF2+ counties": post[post.ef >= 2].county_fips.nunique(),
         "Post-trt EF3+ counties": post[post.ef >= 3].county_fips.nunique(),
         "Any tornado events": len(post), "EF1+ events": int((post.ef >= 1).sum()),
         "EF2+ events": int((post.ef >= 2).sum()), "EF3+ events": int((post.ef >= 3).sum()),
         "Post-trt EF1+ county-quarters": post[post.ef >= 1].groupby(["county_fips", "yq"]).ngroups,
         "Untreated EF1+ control counties": len(ever_ctrl - set(ct.county_fips))}
    return r


def assess(r: dict) -> str:
    if r["Post-trt EF1+ counties"] >= 100 and r["EF1+ events"] >= 200:
        return "ADEQUATE event count for county-level design"
    if r["Post-trt EF1+ counties"] >= 30:
        return "MARGINAL - power risk"
    return "LOW POWER RISK"


def main() -> None:
    ct = pd.read_parquet(PROC / "county_treatment.parquet")
    tor = pd.read_parquet(INTER / "tornadoes_clean.parquet")
    tor = tor[(tor.year >= ANALYSIS_START) & (tor.date <= END)]
    proj = pd.read_parquet(INTER / "fema_treatment_projects.parquet")
    cty = pd.read_parquet(XWALK / "counties_2020.parquet")[["county_fips", "STUSPS"]]
    ever_ctrl = set(tor[tor.ef >= 1].county_fips)

    rows = []
    for d in ["strict", "moderate", "broad"]:
        for tm in ["t_primary", "t_closeout", "t_obligation_L0", "t_approval_L0", "t_obligation_L3"]:
            c = ct[(ct.definition == d) & (ct.timing == tm) & (ct.first_treat_date <= END)]
            c = c[c.county_fips.isin(cty.county_fips)]
            r = counts(c, tor, ever_ctrl)
            r = {"Treatment definition": d, "Timing": tm, **r}
            r["Assessment"] = assess(r)
            rows.append(r)
    tab = pd.DataFrame(rows)
    tab.to_csv(TABLES / "preliminary_feasibility_full.csv", index=False)

    p = proj[proj.county_fips.notna() & proj.county_fips.isin(cty.county_fips)].merge(cty, on="county_fips")
    by_state = p[p.treat_strict == 1].groupby("STUSPS").agg(projects=("projectIdentifier", "nunique"),
                                                            counties=("county_fips", "nunique"),
                                                            federal_share=("federal_share", "sum")) \
        .sort_values("projects", ascending=False)
    by_type = p.groupby(["mitigation_type"]).agg(projects=("projectIdentifier", "nunique"),
                                                 counties=("county_fips", "nunique"))
    by_fac = p[p.treat_strict == 1].facility_type.value_counts()
    by_state.to_csv(TABLES / "preliminary_strict_by_state.csv")

    main_cols = ["Treatment definition", "Treated counties", "Post-treatment tornado counties", "Any tornado events",
                 "EF1+ events", "EF2+ events", "EF3+ events", "Assessment"]
    prim = tab[tab.Timing == "t_primary"]
    top_share = by_state.counties.head(1).iloc[0] / by_state.counties.sum()
    n_all = len(proj)
    md = [
        "# Preliminary Feasibility (Section 62 pilot)", "",
        f"Generated {pd.Timestamp.now():%Y-%m-%d %H:%M}. Analysis window for tornadoes: {ANALYSIS_START}-2025 (NOAA Storm Events, contiguous US).",
        "Treatment = funded OpenFEMA HMA projects (status Closed/Approved/Obligated/Awarded/Completed) with an identified primary county.",
        "Primary timing = obligation date + 2 years (fallback approval + 2y, then closeout). **OpenFEMA publishes no physical completion date.**",
        "", "## Main table (primary timing)", "", prim[main_cols].to_markdown(index=False), "",
        "## Treated counties and post-treatment events under alternative timings", "",
        tab[["Treatment definition", "Timing", "Treated counties", "Median treatment year",
             "Post-trt EF1+ counties", "Post-trt EF2+ counties", "Post-trt EF3+ counties", "EF1+ events",
             "Post-trt EF1+ county-quarters", "Untreated EF1+ control counties"]].to_markdown(index=False), "",
        "## Treatment counts", "",
        f"- Funded wind/tornado-classified projects (broad, any geography): {n_all:,}",
        f"- Strict projects with county FIPS in contiguous US: {p[p.treat_strict == 1].projectIdentifier.nunique():,}",
        f"- Treated states (strict): {by_state.shape[0]}",
        f"- Largest state's share of strict treated counties: {top_share:.1%} ({by_state.index[0]})", "",
        "### Projects by mitigation type", "", by_type.to_markdown(), "",
        "### Strict projects by protected facility type (text-based, approximate)", "", by_fac.to_frame("projects").to_markdown(), "",
        "### Top 15 states (strict)", "", by_state.head(15).assign(federal_share=lambda x: (x.federal_share / 1e6).round(1))
        .rename(columns={"federal_share": "federal_share_$M"}).to_markdown(), "",
    ]
    (FINAL / "preliminary_feasibility.md").write_text("\n".join(md), encoding="utf-8")
    log.info("\n%s", prim[main_cols].to_string(index=False))


if __name__ == "__main__":
    main()
