"""Robustness of the SMALL-COUNTY CONVERSION GAP (2026-10-09).

Finding to test (49_allocation_analysis.py, stage 2): among declared county-years, bottom-third-population
counties are 9.7 pp (base 13.7%) less likely to obtain a strict mitigation project within t+1..t+3.

Unit here: county x disaster declaration (DR, Tornado/Severe Storm, county designated, incident year 1999-2021).
Outcomes
  dis_any       any funded HMGP project (any mitigation type) under THIS disaster number in this county
  dis_strict    funded strict (safe room / wind retrofit) project under this disaster in this county
  win3_strict   any funded strict project obligated in t+1..t+3 (original definition)
  win5_strict   same, t+1..t+5
  win3_anyhma   any funded HMA project of any type, t+1..t+3
  dis_fed_pc    log(1 + federal $ per capita) under this disaster (intensive margin)
  dis_any_sw    dis_any, crediting statewide projects of the same disaster to every designated county
Multi-county projects (projectCounties "A; B; C") are credited to every listed county.
Specs: state-year FE (replication) -> disaster FE (same declaration, same HMGP pot) -> + exposure/damage
controls -> + demographics -> hit-only sample -> state clusters -> continuous log pop / deciles ->
leave-one-state-out -> prior HMA experience interaction (mechanism).
Outputs: output/tables/small_gap_*.csv
"""
from __future__ import annotations

import importlib.util

import numpy as np
import pandas as pd
import pyfixest as pf

from utils import INTER, RAW, SRC, TABLES, XWALK, get_logger

log = get_logger(__file__)


def load(name, f):
    s = importlib.util.spec_from_file_location(name, SRC / f)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


al = load("al", "49_allocation_analysis.py")
ra = al.ra


def norm(x: str) -> str:
    return (x.upper().replace("SAINT ", "ST ").replace("ST. ", "ST ").replace(".", "").replace("'", "")
            .replace(" COUNTY", "").replace(" PARISH", "").replace(" BOROUGH", "").replace(" CITY AND", "")
            .replace(" (CITY)", "").strip())


def project_counties() -> pd.DataFrame:
    """Project -> county rows (multi-county expanded); statewide projects kept with county_fips = None."""
    p = pd.read_parquet(INTER / "fema_projects_classified.parquet")
    p = p[p.funded].copy()
    p["fed"] = p.federal_share.fillna(0.75 * p.total_cost).fillna(0)
    p["oy"] = p.obligation_date.dt.year.fillna(p.approval_date.dt.year)
    c = pd.read_parquet(XWALK / "counties_2020.parquet")
    key = {(s, norm(n)): f for s, n, f in zip(c.state_fips, c.NAME, c.county_fips)}
    rows = []
    for r in p[["projectIdentifier", "state_fips", "county_fips", "projectCounties", "disasterNumber", "programArea",
                "treat_strict", "fed", "oy"]].itertuples(index=False):
        names = [x.strip() for x in str(r.projectCounties).replace(",", ";").split(";") if x.strip()]
        fips = {key.get((r.state_fips, norm(n))) for n in names if n.upper() != "STATEWIDE"} - {None}
        if r.county_fips is not None and not pd.isna(r.county_fips):
            fips.add(r.county_fips)
        share = 1 / max(len(fips), 1)
        if not fips:
            rows.append((*r[:2], None, r.disasterNumber, r.programArea, r.treat_strict, r.fed, r.oy, 1))
        for f in fips:
            rows.append((*r[:2], f, r.disasterNumber, r.programArea, r.treat_strict, r.fed * share, r.oy, 0))
    out = pd.DataFrame(rows, columns=["pid", "state_fips", "county_fips", "disasterNumber", "programArea",
                                      "strict", "fed", "oy", "statewide"])
    log.info("project-county rows %d; multi-county expanded projects %d; statewide %d",
             len(out), (out.groupby("pid").county_fips.nunique() > 1).sum(), out.statewide.sum())
    return out


def county_disasters() -> pd.DataFrame:
    d = pd.read_csv(RAW / "fema" / "DisasterDeclarationsSummaries.csv",
                    usecols=["declarationType", "incidentType", "incidentBeginDate", "fipsStateCode",
                             "fipsCountyCode", "disasterNumber", "hmProgramDeclared", "paProgramDeclared",
                             "ihProgramDeclared"])
    d = d[(d.declarationType == "DR") & d.incidentType.isin(["Tornado", "Severe Storm"]) & (d.fipsCountyCode > 0)]
    d["year"] = pd.to_datetime(d.incidentBeginDate).dt.year
    d = d[d.year.between(1999, 2021)]
    d["county_fips"] = (d.fipsStateCode.astype(int).astype(str).str.zfill(2)
                        + d.fipsCountyCode.astype(int).astype(str).str.zfill(3))
    d["tornado_incident"] = (d.incidentType == "Tornado").astype(int)
    g = d.groupby(["county_fips", "disasterNumber"]).agg(year=("year", "min"), ia=("ihProgramDeclared", "max"),
                                                         pa=("paProgramDeclared", "max"),
                                                         tornado_incident=("tornado_incident", "max")).reset_index()
    # disaster size: number of designated counties
    g["n_cty_disaster"] = g.groupby("disasterNumber").county_fips.transform("nunique")
    return g


def build() -> pd.DataFrame:
    pc = project_counties()
    cd = county_disasters()
    # outcomes linked to the disaster number
    hm = pc[pc.programArea == "HMGP"]
    link = hm[hm.county_fips.notna()].groupby(["county_fips", "disasterNumber"]).agg(
        dis_any=("pid", "size"), dis_strict=("strict", "sum"), dis_fed=("fed", "sum")).reset_index()
    sw = hm[hm.statewide == 1].groupby("disasterNumber").agg(sw_any=("pid", "size"), sw_strict=("strict", "sum"))
    x = cd.merge(link, how="left", on=["county_fips", "disasterNumber"]).merge(sw.reset_index(), how="left", on="disasterNumber")
    for c in ["dis_any", "dis_strict", "dis_fed", "sw_any", "sw_strict"]:
        x[c] = x[c].fillna(0)
    x["dis_any_sw"] = ((x.dis_any + x.sw_any) > 0).astype(int)
    x["dis_strict_sw"] = ((x.dis_strict + x.sw_strict) > 0).astype(int)
    x["dis_any"] = (x.dis_any > 0).astype(int)
    x["dis_strict"] = (x.dis_strict > 0).astype(int)
    # window outcomes from county-level obligations (expanded multi-county)
    cc = pc[pc.county_fips.notna()]
    for lab, cond, k in [("win3_strict", cc.strict == 1, 3), ("win5_strict", cc.strict == 1, 5), ("win3_anyhma", cc.strict >= 0, 3)]:
        yrs = cc[cond].groupby("county_fips").oy.apply(lambda s: set(s.dropna().astype(int)))
        x[lab] = [int(any(y + j in yrs.get(f, set()) for j in range(1, k + 1))) for f, y in zip(x.county_fips, x.year)]
    # prior HMA experience: any funded HMA project obligated before the incident year
    first = cc.groupby("county_fips").oy.min()
    x["prior_hma"] = (x.county_fips.map(first) < x.year).astype(int)
    # county-year covariates
    d = ra.build_panel()
    keep = ["county_fips", "year", "state_fips", "STUSPS", "state_year", "baseline_pop", "E", "pop_exposed",
            "track_km", "spc_max_mag", "spc_inj", "spc_fat", "reported_property_damage", "swept_share"]
    x = x.merge(d[keep], how="inner", on=["county_fips", "year"])
    x = x.merge(al.acs(), how="left", on="county_fips")
    mt = pd.read_parquet(XWALK.parent / "processed" / "county_metro.parquet").set_index("county_fips")["metro"]
    x["nonmetro"] = (x.county_fips.map(mt).fillna(0) != 1).astype(int)
    cty = d.drop_duplicates("county_fips").set_index("county_fips").baseline_pop.rank(pct=True)   # national terciles as in 49
    x["pop_pct"] = x.county_fips.map(cty)
    x["small"] = (x.pop_pct <= 1 / 3).astype(int)
    x["pop_dec"] = np.minimum((x.pop_pct * 10).astype(int), 9)
    x["lpop"] = np.log(x.baseline_pop.clip(lower=100))
    x["dis_fed_pc"] = np.log1p(x.dis_fed / x.baseline_pop.clip(lower=100))
    x["ldmg"] = np.log1p(x.reported_property_damage.fillna(0))
    x["ldmg_pc"] = np.log1p(x.reported_property_damage.fillna(0) / x.baseline_pop.clip(lower=100))
    x["lpe"] = np.log1p(x.pop_exposed.fillna(0))
    x["cas"] = np.log1p(x.spc_inj.fillna(0) + x.spc_fat.fillna(0))
    x["mag"] = x.spc_max_mag.fillna(-1).clip(lower=-1) + 1
    x["linc"] = np.log(x.med_inc)
    x["disaster"] = x.disasterNumber.astype(str)
    return x


OUTS = ["dis_any", "dis_strict", "win3_strict", "win5_strict", "win3_anyhma", "dis_fed_pc", "dis_any_sw", "dis_strict_sw"]
EXPO = "E + lpe + track_km + mag + cas + ldmg + ldmg_pc"
DEMO = "linc + pov_rate + nonwhite + nonmetro"


def est(x, y, rhs, fe, vc, term="small"):
    m = pf.feols(f"{y} ~ {rhs} | {fe}", data=x, vcov=vc)
    t = m.tidy().loc[term]
    return {"b": t.Estimate, "se": t["Std. Error"], "p": t["Pr(>|t|)"], "N": m._N,
            "base": x.loc[x.small == 0, y].mean() if term == "small" else x[y].mean()}


def main() -> None:
    x = build()
    x = x.dropna(subset=["med_inc", "pov_rate", "nonwhite"])
    log.info("county-disaster obs %d (counties %d, disasters %d); small share %.3f; hit share %.3f",
             len(x), x.county_fips.nunique(), x.disasterNumber.nunique(), x.small.mean(), x.E.mean())
    log.info("raw means by small:\n%s", x.groupby("small")[OUTS + ["E", "prior_hma"]].mean().round(3).to_string())
    cv, cs = {"CRV1": "county_fips"}, {"CRV1": "state_fips"}
    specs = [
        ("S1 state-year FE (replication)", x, "small", "state_year", cv),
        ("S2 disaster FE", x, "small", "disaster", cv),
        ("S3 disaster FE + exposure/damage", x, f"small + {EXPO}", "disaster", cv),
        ("S4 + demographics", x, f"small + {EXPO} + {DEMO}", "disaster", cv),
        ("S5 hit-only sample (S4)", x[x.E == 1], f"small + lpe + track_km + mag + cas + ldmg + ldmg_pc + {DEMO}", "disaster", cv),
        ("S6 S4, state clusters", x, f"small + {EXPO} + {DEMO}", "disaster", cs),
        ("S7 S4, tornado-type incidents only", x[x.tornado_incident == 1], f"small + {EXPO} + {DEMO}", "disaster", cv),
        ("S8 S4, IA-declared counties only", x[x.ia == 1], f"small + {EXPO} + {DEMO}", "disaster", cv),
    ]
    rows = []
    for lab, s, rhs, fe, vc in specs:
        for y in OUTS:
            try:
                rows.append({"spec": lab, "outcome": y, **est(s, y, rhs, fe, vc)})
            except Exception as e:  # noqa: BLE001
                rows.append({"spec": lab, "outcome": y, "status": str(e)[:80]})
    # continuous population
    for y in ["dis_any", "dis_strict", "win3_strict"]:
        rows.append({"spec": "S9 log pop (continuous), S4 controls", "outcome": y,
                     **est(x, y, f"lpop + {EXPO} + {DEMO}", "disaster", cv, term="lpop")})
    r = pd.DataFrame(rows)
    r.to_csv(TABLES / "small_gap_robustness.csv", index=False)
    log.info("robustness (b on small):\n%s", r.pivot_table(index="spec", columns="outcome", values="b").round(4).to_string())
    log.info("p:\n%s", r.pivot_table(index="spec", columns="outcome", values="p").round(3).to_string())
    log.info("base (non-small mean):\n%s", r.pivot_table(index="spec", columns="outcome", values="base").round(3).to_string())

    # population deciles (dose shape), disaster FE + S4 controls
    dec = []
    for y in ["dis_any", "win3_strict"]:
        m = pf.feols(f"{y} ~ i(pop_dec, ref=9) + {EXPO} + {DEMO} | disaster", data=x, vcov=cv)
        t = m.tidy()
        for term, rr in t[t.index.str.contains("pop_dec")].iterrows():
            dec.append({"outcome": y, "decile": term, "b": rr.Estimate, "se": rr["Std. Error"], "p": rr["Pr(>|t|)"]})
    dec = pd.DataFrame(dec)
    dec.to_csv(TABLES / "small_gap_deciles.csv", index=False)
    log.info("deciles (ref = top decile):\n%s", dec.round(3).to_string())

    # leave-one-state-out (dis_any and win3_strict, S4)
    lo = []
    for st in sorted(x.STUSPS.unique()):
        s = x[x.STUSPS != st]
        for y in ["dis_any", "win3_strict"]:
            e = est(s, y, f"small + {EXPO} + {DEMO}", "disaster", cv)
            lo.append({"dropped": st, "outcome": y, **e})
    lo = pd.DataFrame(lo)
    lo.to_csv(TABLES / "small_gap_leave_one_state.csv", index=False)
    log.info("leave-one-state-out range:\n%s", lo.groupby("outcome").agg(bmin=("b", "min"), bmax=("b", "max"),
                                                                       pmax=("p", "max")).round(4).to_string())

    # mechanism: does prior HMA experience close the gap?
    x["small_prior"] = x.small * x.prior_hma
    mech = []
    for y in ["dis_any", "dis_strict", "win3_strict"]:
        m = pf.feols(f"{y} ~ small + prior_hma + small_prior + {EXPO} + {DEMO} | disaster", data=x, vcov=cv)
        t = m.tidy()
        for term in ["small", "prior_hma", "small_prior"]:
            mech.append({"outcome": y, "term": term, "b": t.loc[term, "Estimate"], "p": t.loc[term, "Pr(>|t|)"]})
    mech = pd.DataFrame(mech)
    mech.to_csv(TABLES / "small_gap_mechanism.csv", index=False)
    log.info("mechanism (prior HMA experience):\n%s", mech.round(4).to_string())
    log.info("prior_hma share: small %.3f, non-small %.3f", x.loc[x.small == 1, "prior_hma"].mean(),
             x.loc[x.small == 0, "prior_hma"].mean())


if __name__ == "__main__":
    main()
