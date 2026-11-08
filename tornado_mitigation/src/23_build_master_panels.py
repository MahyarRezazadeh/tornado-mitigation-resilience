"""Build master panels (contiguous US counties, harmonized 2020 geography).

  county_quarter_panel.parquet           1990Q1-2025Q4: tornado exposure, QWI, QCEW totals, treatment, controls
  county_year_panel.parquet              1990-2025: calendar + March-aligned tornado exposure, BDS, CBP, IRS, BPS
  county_industry_quarter_panel.parquet  QWI industry groups (+ QCEW 2014+)
  county_industry_year_panel.parquet     CBP industry groups
  county_demographic_quarter_panel.parquet QWI sex/age/education/race/ethnicity/firm-size cells
  county_treatment_wide.parquet          first-treatment quarter for every definition x timing

Alignment: BDS/CBP measure March 12 of year t; IRS pair (t-1,t) measures spring-to-spring moves.
For those, annual tornado exposure is March-aligned: Q2..Q4 of t-1 plus Q1 of t ('mar_' prefix),
and Mitigated_ct requires treatment on/before the window start (operational before the storm).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from utils import DIAG, INTER, PROC, XWALK, get_logger, log_frame

log = get_logger(__file__)
Y0, Y1 = 1990, 2025
EXPO = ["any_tornado", "tornado_count", "EF0_count", "EF1_plus_count", "EF2_plus_count", "EF3_plus_count",
        "EF1_plus", "EF2_plus", "EF3_plus", "max_tornado_intensity", "total_injuries", "total_fatalities",
        "reported_property_damage", "reported_crop_damage", "EFU_count"]


def yq_of(ts: pd.Series) -> pd.Series:
    return (ts.dt.year * 10 + ts.dt.quarter).astype("Int64")


def treatment_wide(cty: pd.DataFrame) -> pd.DataFrame:
    ct = pd.read_parquet(PROC / "county_treatment.parquet")
    ct["ft_yq"] = yq_of(ct["first_treat_date"])
    w = ct.pivot_table(index="county_fips", columns=["definition", "timing"], values="ft_yq", aggfunc="min")
    w.columns = [f"ft_{d}_{t.removeprefix('t_')}" for d, t in w.columns]
    w = cty[["county_fips"]].merge(w.reset_index(), how="left")
    prim = ct[ct.timing == "t_primary"].pivot_table(index="county_fips", columns="definition",
                                                    values=["n_projects", "federal_share", "total_cost",
                                                            "n_safe_room", "n_wind_retrofit"], aggfunc="sum")
    prim.columns = [f"{v}_{d}" for v, d in prim.columns]
    w = w.merge(prim.reset_index(), how="left")
    conf = ct[(ct.timing == "t_primary") & (ct.definition == "strict")][["county_fips", "min_confidence"]]
    w = w.merge(conf, how="left")
    return w


def cumulative_intensity(cty_list) -> pd.DataFrame:
    """Cumulative strict federal share and project count by county x quarter (primary timing)."""
    p = pd.read_parquet(INTER / "fema_treatment_projects.parquet")
    p = p[(p.treat_strict == 1) & p.county_fips.isin(cty_list) & p.t_primary.notna()].copy()
    p["yq"] = yq_of(p["t_primary"])
    g = p.groupby(["county_fips", "yq"]).agg(fed=("federal_share", "sum"), nproj=("projectIdentifier", "nunique"))
    return g.reset_index()


def to_index(yq: pd.Series) -> pd.Series:
    return (yq // 10 - Y0) * 4 + (yq % 10) - 1


def main() -> None:
    cty = pd.read_parquet(XWALK / "counties_2020.parquet")
    risk = pd.read_parquet(PROC / "historical_tornado_risk.parquet")
    metro = pd.read_parquet(PROC / "county_metro.parquet")[["county_fips", "metro"]]
    pop = pd.read_parquet(PROC / "county_population.parquet")
    tw = treatment_wide(cty)
    tw.to_parquet(PROC / "county_treatment_wide.parquet", index=False)

    base = cty[["county_fips", "state_fips", "STUSPS", "land_area_km2", "lat", "lon"]].merge(risk.drop(
        columns="land_area_km2"), how="left").merge(metro, how="left")
    base["metro"] = base["metro"].fillna(0).astype(int)
    bp = pop[pop.year == 2000][["county_fips", "population"]].rename(columns={"population": "baseline_pop"})
    base = base.merge(bp, how="left")
    bds = pd.read_parquet(INTER / "bds_county_year.parquet")
    be = bds[bds.year.between(1995, 1999)].groupby("county_fips").agg(baseline_emp=("emp", "mean"),
                                                                       baseline_estabs=("estabs", "mean"))
    base = base.merge(be.reset_index(), how="left")
    base = base.merge(tw[["county_fips", "ft_strict_primary", "ft_moderate_primary", "ft_broad_primary",
                          "min_confidence"]], how="left")
    regions = {"Northeast": ["09", "23", "25", "33", "44", "50", "34", "36", "42"],
               "Midwest": ["17", "18", "26", "39", "55", "19", "20", "27", "29", "31", "38", "46"],
               "South": ["10", "11", "12", "13", "24", "37", "45", "51", "54", "01", "21", "28", "47", "05", "22",
                         "40", "48"]}
    base["region"] = "West"
    for r, sts in regions.items():
        base.loc[base.state_fips.isin(sts), "region"] = r

    # ---------------- county-quarter ----------------
    yqs = [y * 10 + q for y in range(Y0, Y1 + 1) for q in range(1, 5)]
    cq = pd.MultiIndex.from_product([cty.county_fips, yqs], names=["county_fips", "yq"]).to_frame(index=False)
    ex = pd.read_parquet(PROC / "tornado_exposure_cq.parquet")
    cq = cq.merge(ex.drop(columns=["year", "quarter"]), how="left", on=["county_fips", "yq"])
    oh = pd.read_parquet(PROC / "other_hazards_cq.parquet")
    cq = cq.merge(oh, how="left", on=["county_fips", "yq"])
    for c in ["hurricane_events", "flood_events", "severe_storm_events"]:
        cq[c] = cq[c].fillna(0)
    q = pd.read_parquet(INTER / "qwi_county_quarter.parquet").drop(columns=["year", "quarter"])
    cq = cq.merge(q, how="left", on=["county_fips", "yq"])
    qc = INTER / "qcew_county_quarter.parquet"
    if qc.exists():
        cq = cq.merge(pd.read_parquet(qc).query("industry_group == 'Total'").drop(columns="industry_group"),
                      how="left", on=["county_fips", "yq"])
    ci = cumulative_intensity(cty.county_fips)
    cq = cq.merge(ci, how="left", on=["county_fips", "yq"])
    cq[["fed", "nproj"]] = cq[["fed", "nproj"]].fillna(0)
    cq = cq.sort_values(["county_fips", "yq"])
    cq["cum_fed_share_strict"] = cq.groupby("county_fips")["fed"].cumsum()
    cq["cum_projects_strict"] = cq.groupby("county_fips")["nproj"].cumsum()
    cq = cq.drop(columns=["fed", "nproj"])
    cq["year"] = cq.yq // 10
    cq["quarter"] = cq.yq % 10
    cq["t"] = to_index(cq.yq)
    cq = cq.merge(base, how="left", on="county_fips")
    cq = cq.merge(pop.rename(columns={"population": "pop_year"}), how="left", on=["county_fips", "year"])
    cq["cum_fed_pc_strict"] = cq["cum_fed_share_strict"] / cq["baseline_pop"]
    cq["state_yq"] = cq["state_fips"] + "_" + cq["yq"].astype(str)
    cq["region_yq"] = cq["region"] + "_" + cq["yq"].astype(str)
    assert not cq.duplicated(["county_fips", "yq"]).any(), "duplicate county-quarter keys"
    cq.to_parquet(PROC / "county_quarter_panel.parquet", index=False)
    log_frame(log, cq, "county_quarter_panel")

    # ---------------- county-year ----------------
    yrs = list(range(Y0, Y1 + 1))
    cy = pd.MultiIndex.from_product([cty.county_fips, yrs], names=["county_fips", "year"]).to_frame(index=False)
    ey = pd.read_parquet(PROC / "tornado_exposure_cy.parquet")
    cy = cy.merge(ey, how="left", on=["county_fips", "year"])
    # March-aligned exposure: Q2-Q4 of t-1 + Q1 of t
    e = ex.copy()
    e["mar_year"] = np.where(e.quarter == 1, e.year, e.year + 1)
    agg = {c: "sum" for c in EXPO if c in e}
    agg["max_tornado_intensity"] = "max"
    m = e.groupby(["county_fips", "mar_year"]).agg(agg).reset_index().rename(columns={"mar_year": "year"})
    for k in ["any_tornado", "EF1_plus", "EF2_plus", "EF3_plus"]:
        m[k] = (m[k] > 0).astype(int)
    m = m.rename(columns={c: "mar_" + c for c in m.columns if c not in ["county_fips", "year"]})
    cy = cy.merge(m, how="left", on=["county_fips", "year"])
    ohy = pd.read_parquet(PROC / "other_hazards_cy.parquet")
    cy = cy.merge(ohy, how="left", on=["county_fips", "year"])
    for c in ["hurricane_events", "flood_events", "severe_storm_events"]:
        cy[c] = cy[c].fillna(0)
    cy = cy.merge(bds.drop(columns=[c for c in ["st", "cty"] if c in bds]), how="left", on=["county_fips", "year"])
    for f in ["cbp_county_year", "irs_county_year", "bps_county_year"]:
        cy = cy.merge(pd.read_parquet(INTER / f"{f}.parquet"), how="left", on=["county_fips", "year"])
    # BDS small-business: firm size 1-19 deaths & JD
    fz = pd.read_parquet(INTER / "bds_county_year_fsize.parquet")
    sm = fz[fz.fsizecoarse == "a) 1 to 19"][["county_fips", "year", "estab_deaths", "establishment_death_rate",
                                             "job_destruction_rate", "estabs"]]
    sm.columns = ["county_fips", "year", "small_estab_deaths", "small_estab_death_rate", "small_jd_rate", "small_estabs_bds"]
    cy = cy.merge(sm, how="left", on=["county_fips", "year"])
    fa = pd.read_parquet(INTER / "bds_county_year_fage.parquet")
    st = fa[fa.fagecoarse == "a) 0"][["county_fips", "year", "estabs", "job_creation"]]
    st.columns = ["county_fips", "year", "startup_estabs", "startup_job_creation"]
    cy = cy.merge(st, how="left", on=["county_fips", "year"])
    cy["startup_rate"] = 100 * cy["startup_estabs"] / cy["estabs"]
    cy = cy.merge(base, how="left", on="county_fips")
    cy = cy.merge(pop.rename(columns={"population": "pop_year"}), how="left", on=["county_fips", "year"])
    ciy = cq.groupby(["county_fips", "year"])[["cum_fed_share_strict", "cum_projects_strict"]].max().reset_index()
    cy = cy.merge(ciy, how="left", on=["county_fips", "year"])
    cy["cum_fed_pc_strict"] = cy["cum_fed_share_strict"] / cy["baseline_pop"]
    cy["state_year"] = cy["state_fips"] + "_" + cy["year"].astype(str)
    cy["region_year"] = cy["region"] + "_" + cy["year"].astype(str)
    cy["log_estabs_bds"] = np.log(cy.estabs.where(cy.estabs > 0))
    cy["log_emp_bds"] = np.log(cy.emp.where(cy.emp > 0))
    cy["log_estab_deaths"] = np.log1p(cy.estab_deaths)
    cy["log_job_destruction"] = np.log1p(cy.job_destruction)
    assert not cy.duplicated(["county_fips", "year"]).any(), "duplicate county-year keys"
    cy.to_parquet(PROC / "county_year_panel.parquet", index=False)
    log_frame(log, cy, "county_year_panel")

    # ---------------- industry & demographic panels ----------------
    qi = pd.read_parquet(INTER / "qwi_county_industry_quarter.parquet")
    cnt = ["Emp", "EmpEnd", "Sep", "SepBeg", "HirA", "HirN", "FrmJbLs", "Payroll"]
    g = qi.groupby(["county_fips", "yq", "industry_group"], as_index=False)[cnt].sum(min_count=1)
    w = qi.assign(wE=qi.EarnS * qi.EmpS).groupby(["county_fips", "yq", "industry_group"])[["wE", "EmpS"]].sum(min_count=1)
    g = g.merge((w.wE / w.EmpS).rename("EarnS").reset_index(), how="left")
    avg = (g.Emp + g.EmpEnd) / 2
    g["log_employment"] = np.log(g.EmpEnd.where(g.EmpEnd > 0))
    g["separation_rate"] = (g.Sep / avg.where(avg > 0)).where(lambda s: s.between(0, 2))
    g["hire_rate"] = (g.HirA / avg.where(avg > 0)).where(lambda s: s.between(0, 2))
    g["log_earnings"] = np.log(g.EarnS.where(g.EarnS > 0))
    g["job_destruction_rate_qwi"] = (g.FrmJbLs / avg.where(avg > 0)).where(lambda s: s.between(0, 2))
    g["year"] = g.yq // 10
    g = g.merge(base[["county_fips", "state_fips", "region"]], how="left")
    if qc.exists():
        qq = pd.read_parquet(qc).query("industry_group != 'Total'")
        g = g.merge(qq, how="left", on=["county_fips", "yq", "industry_group"])
    assert not g.duplicated(["county_fips", "yq", "industry_group"]).any()
    g.to_parquet(PROC / "county_industry_quarter_panel.parquet", index=False)
    log_frame(log, g, "county_industry_quarter_panel")

    ciy = pd.read_parquet(INTER / "cbp_county_industry_year.parquet").merge(
        base[["county_fips", "state_fips", "region"]], how="inner")
    ciy.to_parquet(PROC / "county_industry_year_panel.parquet", index=False)
    log_frame(log, ciy, "county_industry_year_panel")

    dm = pd.read_parquet(INTER / "qwi_county_demo_quarter.parquet")
    dm = dm.merge(base[["county_fips", "state_fips", "region"]], how="inner")
    assert not dm.duplicated(["county_fips", "yq", "demo_group"]).any()
    dm.to_parquet(PROC / "county_demographic_quarter_panel.parquet", index=False)
    log_frame(log, dm, "county_demographic_quarter_panel")

    # validation report
    val = [("cq negative EmpEnd", int((cq.EmpEnd < 0).sum())), ("cy negative estabs", int((cy.estabs < 0).sum())),
           ("cq missing state", int(cq.state_fips.isna().sum())),
           ("treated strict counties", int(base.ft_strict_primary.notna().sum())),
           ("treatment yq outside panel", int((base.ft_strict_primary > Y1 * 10 + 4).sum())),
           ("population 2000 total", float(base.baseline_pop.sum())),
           ("QWI county-quarters non-missing EmpEnd", int(cq.EmpEnd.notna().sum()))]
    pd.DataFrame(val, columns=["check", "value"]).to_csv(DIAG / "panel_validation.csv", index=False)
    for k, v in val:
        log.info("validation: %s = %s", k, v)


if __name__ == "__main__":
    main()
