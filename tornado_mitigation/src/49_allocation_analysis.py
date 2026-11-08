"""ALLOCATION / TARGETING analysis (2026-10-09): who gets tornado mitigation money, and does it follow risk?

A. Funnel   hit (SPC populated-place hit, E) -> county disaster declaration (DR, tornado/severe storm,
            incident year t) -> new strict mitigation obligation within t+1..t+3 (ProjWin).
B. Equity / capacity / politics: heterogeneity of each funnel stage by baseline (ACS 2009 5-yr) income,
            poverty, non-white share, small population, non-metro, and presidential alignment (2009+).
C. Targeting efficiency: do 1999-2012 dollars follow recent hits (1996-2010) or long-run climatology
            (smoothed 1980-1995 track density within 100 km)? Which of the two predicts 2013-2024 hits?
            Does spending land where future hits occur beyond risk?

Outputs: output/tables/alloc_*.csv, output/final/allocation_results.md (written by hand from these)
"""
from __future__ import annotations

import importlib.util

import numpy as np
import pandas as pd
import pyfixest as pf
import requests

from utils import PROC, RAW, SRC, TABLES, XWALK, census_key, get_logger, cached_get

log = get_logger(__file__)
spec = importlib.util.spec_from_file_location("ra", SRC / "46_redesign_analysis.py")
ra = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ra)
VC = {"CRV1": "county_fips"}
FE = "county_fips + state_year"
ELEC = "https://raw.githubusercontent.com/tonmcg/US_County_Level_Election_Results_08-24/master/"


# ----------------------------------------------------------------------------- data
def declarations() -> pd.DataFrame:
    d = pd.read_csv(RAW / "fema" / "DisasterDeclarationsSummaries.csv",
                    usecols=["declarationType", "incidentType", "incidentBeginDate", "fipsStateCode",
                             "fipsCountyCode", "hmProgramDeclared", "disasterNumber"])
    d = d[(d.declarationType == "DR") & d.incidentType.isin(["Tornado", "Severe Storm", "Severe Storms"])]
    d["year"] = pd.to_datetime(d.incidentBeginDate).dt.year
    c = d[d.fipsCountyCode > 0].copy()
    c["county_fips"] = c.fipsStateCode.astype(int).astype(str).str.zfill(2) + c.fipsCountyCode.astype(int).astype(str).str.zfill(3)
    out = c.groupby(["county_fips", "year"]).agg(decl=("disasterNumber", "nunique")).reset_index()
    out["decl"] = (out.decl > 0).astype(int)
    return out


def acs() -> pd.DataFrame:
    f = RAW / "auxiliary" / "acs2009_county.csv"
    if not f.exists():
        v = "B19013_001E,B17001_001E,B17001_002E,B02001_001E,B02001_002E"
        r = requests.get(f"https://api.census.gov/data/2009/acs/acs5?get={v}&for=county:*&key={census_key()}", timeout=120)
        r.raise_for_status()
        j = r.json()
        pd.DataFrame(j[1:], columns=j[0]).to_csv(f, index=False)
    a = pd.read_csv(f, dtype=str)
    a["county_fips"] = a.state.str.zfill(2) + a.county.str.zfill(3)
    for c in ["B19013_001E", "B17001_001E", "B17001_002E", "B02001_001E", "B02001_002E"]:
        a[c] = pd.to_numeric(a[c], errors="coerce")
    a["med_inc"] = a.B19013_001E
    a["pov_rate"] = a.B17001_002E / a.B17001_001E
    a["nonwhite"] = 1 - a.B02001_002E / a.B02001_001E
    return a[["county_fips", "med_inc", "pov_rate", "nonwhite"]]


def elections() -> pd.DataFrame:
    f1 = cached_get(ELEC + "US_County_Level_Presidential_Results_08-16.csv", RAW / "auxiliary" / "pres_08_16.csv", log)
    f2 = cached_get(ELEC + "2020_US_County_Level_Presidential_Results.csv", RAW / "auxiliary" / "pres_20.csv", log)
    a = pd.read_csv(f1, dtype={"fips_code": str})
    a["county_fips"] = a.fips_code.str.zfill(5)
    b = pd.read_csv(f2, dtype={"county_fips": str})
    b["county_fips"] = b.county_fips.str.zfill(5)
    r = a[["county_fips"]].copy()
    for y in (2008, 2012, 2016):
        r[f"gop_{y}"] = a[f"gop_{y}"] / (a[f"gop_{y}"] + a[f"dem_{y}"])
    r = r.merge(b[["county_fips", "votes_gop", "votes_dem"]], how="outer")
    r["gop_2020"] = r.votes_gop / (r.votes_gop + r.votes_dem)
    rows = []
    # president's party: 2009-16 D (Obama), 2017-20 R (Trump), 2021-24 D (Biden); use most recent election
    for y in range(2009, 2025):
        e = 2008 if y <= 2012 else 2012 if y <= 2016 else 2016 if y <= 2020 else 2020
        pres_r = 2017 <= y <= 2020
        g = r[f"gop_{e}"]
        rows.append(pd.DataFrame({"county_fips": r.county_fips, "year": y,
                                  "aligned": ((g > 0.5) == pres_r).astype(float).where(g.notna())}))
    al = pd.concat(rows)
    return al, r[["county_fips", "gop_2008"]]


def climatology() -> pd.DataFrame:
    """Smoothed 1980-1995 tornado track density: track start points within 100 km of county centroid per 1000 km2."""
    s = pd.read_csv(RAW / "spc" / "1950-2024_actual_tornadoes.csv", usecols=["yr", "slat", "slon"])
    s = s[s.yr.between(1980, 1995) & (s.slat > 20)]
    c = pd.read_parquet(XWALK / "counties_2020.parquet")[["county_fips", "lat", "lon"]].dropna()
    la1, lo1 = np.radians(c.lat.values)[:, None], np.radians(c.lon.values)[:, None]
    la2, lo2 = np.radians(s.slat.values)[None, :], np.radians(s.slon.values)[None, :]
    cnt = np.zeros(len(c))
    for i in range(0, len(c), 300):
        a = (np.sin((la2 - la1[i:i + 300]) / 2) ** 2 + np.cos(la1[i:i + 300]) * np.cos(la2)
             * np.sin((lo2 - lo1[i:i + 300]) / 2) ** 2)
        dist = 2 * 6371 * np.arcsin(np.sqrt(a))
        cnt[i:i + 300] = (dist <= 100).sum(axis=1)
    c["clim"] = cnt / (np.pi * 100 ** 2) * 1000 / 16      # tracks per 1000 km2 per year
    return c[["county_fips", "clim"]]


def z(x):
    return (x - x.mean()) / x.std()


# ----------------------------------------------------------------------------- analysis
def main() -> None:
    d = ra.build_panel()
    d = d[d.state_year.notna()].copy()
    d = d.merge(declarations(), how="left", on=["county_fips", "year"])
    d["decl"] = d.decl.fillna(0)
    g = d.sort_values(["county_fips", "year"]).groupby("county_fips")
    d["proj_win"] = sum(g.new_any.shift(-k).fillna(0) for k in (1, 2, 3)).clip(upper=1)
    d["fed_win_pc"] = np.log1p(sum(g.new_fed.shift(-k).fillna(0) for k in (1, 2, 3)) / d.baseline_pop.clip(lower=100))
    ac = acs()
    al, gop = elections()
    cl = climatology()
    d = d.merge(ac, how="left", on="county_fips").merge(al, how="left", on=["county_fips", "year"]).merge(cl, how="left")
    cty = d.drop_duplicates("county_fips")
    q = lambda v: cty.set_index("county_fips")[v].rank(pct=True)   # noqa: E731
    d["low_inc"] = (d.county_fips.map(q("med_inc")) <= 1 / 3).astype(int)
    d["high_pov"] = (d.county_fips.map(q("pov_rate")) > 2 / 3).astype(int)
    d["high_nonwhite"] = (d.county_fips.map(q("nonwhite")) > 2 / 3).astype(int)
    d["small_pop"] = (d.county_fips.map(q("baseline_pop")) <= 1 / 3).astype(int)
    mt = pd.read_parquet(PROC / "county_metro.parquet").set_index("county_fips")["metro"]
    d["nonmetro"] = (d.county_fips.map(mt).fillna(0) != 1).astype(int)        # outside any metro CBSA = non-metro
    p = d[d.year.between(1999, 2021)].copy()            # proj window t+1..t+3 observed through 2024

    # ---- A. funnel
    fun = []
    for dep, rhs in [("decl", "E"), ("proj_win", "E"), ("fed_win_pc", "E"), ("proj_win", "E + decl + E:decl")]:
        m = pf.feols(f"{dep} ~ {rhs} | {FE}", data=p, vcov=VC)
        for term, r in m.tidy().iterrows():
            fun.append({"dep": dep, "rhs": rhs, "term": term, "b": r.Estimate, "se": r["Std. Error"],
                        "p": r["Pr(>|t|)"], "N": m._N, "dep_mean": p[dep].mean()})
    fun = pd.DataFrame(fun)
    h = p[p.E == 1]
    rates = {"P(decl|hit)": h.decl.mean(), "P(decl|no hit)": p.loc[p.E == 0, "decl"].mean(),
             "P(proj|hit,decl)": h.loc[h.decl == 1, "proj_win"].mean(),
             "P(proj|hit,no decl)": h.loc[h.decl == 0, "proj_win"].mean(),
             "P(proj|no hit, decl)": p.loc[(p.E == 0) & (p.decl == 1), "proj_win"].mean(),
             "P(proj|no hit,no decl)": p.loc[(p.E == 0) & (p.decl == 0), "proj_win"].mean(),
             "hit county-years": len(h), "hit & declared": int(h.decl.sum())}
    fun.to_csv(TABLES / "alloc_funnel.csv", index=False)
    pd.Series(rates).to_csv(TABLES / "alloc_funnel_rates.csv")
    log.info("A funnel:\n%s\nrates: %s", fun.round(4).to_string(), {k: round(v, 4) for k, v in rates.items()})

    # ---- B. heterogeneity of each stage
    het = []
    for ch in ["low_inc", "high_pov", "high_nonwhite", "small_pop", "nonmetro", "aligned"]:
        s = p[p[ch].notna()].copy()
        s["Ech"] = s.E * s[ch]
        log.info("%s: n=%d share=%.3f hits with char=%d", ch, len(s), s[ch].mean(), int(s.Ech.sum()))
        m = pf.feols(f"decl ~ E + Ech | {FE}", data=s, vcov=VC)            # stage 1: declaration given hit
        t = m.tidy()
        het.append({"char": ch, "stage": "1 decl|hit (panel, E x char)", "b_E": t.loc["E", "Estimate"],
                    "b_int": t.loc["Ech", "Estimate"], "p_int": t.loc["Ech", "Pr(>|t|)"], "N": m._N})
        m = pf.feols(f"proj_win ~ E + Ech | {FE}", data=s, vcov=VC)        # overall: project given hit
        t = m.tidy()
        het.append({"char": ch, "stage": "overall proj|hit (panel, E x char)", "b_E": t.loc["E", "Estimate"],
                    "b_int": t.loc["Ech", "Estimate"], "p_int": t.loc["Ech", "Pr(>|t|)"], "N": m._N})
        c = s[s.decl == 1].copy()                                            # stage 2: project given declaration
        c["lpop"] = np.log(c.baseline_pop.clip(lower=100))
        fml = f"proj_win ~ {ch} + E + lpop | state_year" if ch not in ("small_pop",) else f"proj_win ~ {ch} + E | state_year"
        m = pf.feols(fml, data=c, vcov=VC)
        t = m.tidy()
        het.append({"char": ch, "stage": "2 proj|declared (x-section within state-year)", "b_E": np.nan,
                    "b_int": t.loc[ch, "Estimate"], "p_int": t.loc[ch, "Pr(>|t|)"], "N": m._N,
                    "mean_ref": c.loc[c[ch] == 0, "proj_win"].mean()})
    het = pd.DataFrame(het)
    het.to_csv(TABLES / "alloc_heterogeneity.csv", index=False)
    log.info("B heterogeneity:\n%s", het.round(4).to_string())

    # ---- C. targeting efficiency (cross-section)
    sp = pd.read_parquet(INTER_P := RAW.parent / "intermediate" / "fema_treatment_projects.parquet")
    sp = sp[(sp.treat_strict == 1) & sp.county_fips.notna()].copy()
    sp["fed"] = sp.federal_share.fillna(0.75 * sp.total_cost).fillna(0)
    sp["y"] = sp.obligation_date.dt.year.fillna(sp.approval_date.dt.year)
    early = sp[sp.y.between(1999, 2012)].groupby("county_fips").fed.sum()
    x = d.drop_duplicates("county_fips")[["county_fips", "state_fips", "baseline_pop", "land_area_km2", "clim",
                                          "med_inc", "gop_2008" if "gop_2008" in d else "county_fips"]].copy()
    x = x.loc[:, ~x.columns.duplicated()]
    hits = d.groupby("county_fips").apply(lambda g_: pd.Series({
        "recent_hits": g_.loc[g_.year.between(1996, 2010), "E"].sum(),
        "future_hits": g_.loc[g_.year.between(2013, 2024), "E"].sum(),
        "future_pop_exposed": g_.loc[g_.year.between(2013, 2024), "pop_exposed"].sum()}), include_groups=False)
    x = x.merge(hits.reset_index(), on="county_fips").merge(early.rename("fed_early").reset_index(), how="left")
    x["fed_early"] = x.fed_early.fillna(0)
    x["spend_pc"] = np.log1p(x.fed_early / x.baseline_pop.clip(lower=100))
    x["ever_early"] = (x.fed_early > 0).astype(int)
    x["lpop"], x["lland"] = np.log(x.baseline_pop.clip(lower=100)), np.log(x.land_area_km2)
    x["z_recent"], x["z_clim"], x["z_spend"] = z(x.recent_hits), z(x.clim), z(x.spend_pc)
    x["z_future"] = z(x.future_hits)
    ct = []
    for dep, rhs, lab in [("spend_pc", "z_recent + z_clim + lpop + lland", "C1 spending on recency vs climatology"),
                          ("ever_early", "z_recent + z_clim + lpop + lland", "C1b any project"),
                          ("z_future", "z_recent + z_clim + lpop + lland", "C2 future hits on recency vs climatology"),
                          ("z_future", "z_spend + z_recent + z_clim + lpop + lland", "C3 future hits on spending | risk")]:
        m = pf.feols(f"{dep} ~ {rhs} | state_fips", data=x, vcov={"CRV1": "state_fips"})
        for term, r in m.tidy().iterrows():
            if term.startswith("z_"):
                ct.append({"model": lab, "dep": dep, "term": term, "b": r.Estimate, "se": r["Std. Error"],
                           "p": r["Pr(>|t|)"], "N": m._N, "r2": m._r2})
    ct = pd.DataFrame(ct)
    ct.to_csv(TABLES / "alloc_targeting.csv", index=False)
    log.info("C targeting:\n%s", ct.round(4).to_string())
    # descriptive: shares by climatology tercile
    x["clim_t"] = pd.qcut(x.clim.rank(method="first"), 3, labels=["low", "mid", "high"])
    x["recent_t"] = np.where(x.recent_hits > 0, "recent hit", "no recent hit")
    tab = x.groupby(["clim_t", "recent_t"], observed=True).agg(
        counties=("county_fips", "size"), pop=("baseline_pop", "sum"), fed_early=("fed_early", "sum"),
        recent_hits=("recent_hits", "sum"), future_hits=("future_hits", "sum"))
    for c in ["pop", "fed_early", "recent_hits", "future_hits"]:
        tab[c + "_share"] = tab[c] / tab[c].sum()
    tab["future_hits_per_county"] = tab.future_hits / tab.counties
    tab.to_csv(TABLES / "alloc_targeting_shares.csv")
    log.info("shares:\n%s", tab.round(3).to_string())
    _ = INTER_P


if __name__ == "__main__":
    main()

