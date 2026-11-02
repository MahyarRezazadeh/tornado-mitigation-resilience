"""Causal-story tests for the SMALL-COUNTY APPLICATION GAP (2026-10-09). Uses data saved by 51_gap_mechanisms.py.

T1 Fiscal / administrative capacity (Census of Governments 2017 finance, individual-unit file):
   county-government own taxes per capita, all-local taxes per capita, county-government spending on
   financial administration + central staff (E23+E29) per capita. Do they absorb the gap? Is the gap
   concentrated where capacity is low?
T2 State / regional intermediaries: state-level pre-period (FY<=2008) share of HMGP subapplications filed by
   regional bodies (planning/development commissions, councils of governments) or by the state. Is the
   2009-2021 small-county gap smaller in intermediary states?
T3 Demand shock within county: county FE + disaster FE. Does a tornado hit (populated-place SPC track)
   raise applications less in small counties? (same county, same shock -> response gap = capacity)
T4 Application-cost policy shock: DRRA s.1215 reimburses subrecipient management costs (up to 5%) for
   disasters declared on/after 2017-08-01. DiD small x post with county + disaster FE; event study by
   declaration year; placebo cutoff 2014-08-01.
T4b Exploratory: FEMA pre-calculated safe-room benefits (job aid dated 2015-02-19; exact start uncertain):
   triple difference small x post x safe-room-application.
Outputs: output/tables/gap_causal_*.csv
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd
import pyfixest as pf

from utils import PROC, RAW, TABLES, get_logger

log = get_logger(__file__)
VC = {"CRV1": "county_fips"}
EXPO = "E + lpe + track_km + mag + cas + ldmg + ldmg_pc"
EXPO_TV = "lpe + track_km + mag + cas + ldmg + ldmg_pc"
DEMO = "linc + pov_rate + nonwhite + nonmetro"
GOVS = "ln_gp + ln_sd + ln_sch"
REGIONAL = r"PLANNING|REGIONAL|COUNCIL OF GOV|\bCOG\b|DEVELOPMENT DIST|DEVELOPMENT COMM|DEVELOPMENT AUTH|AREA DEVELOPMENT|PLANNING DIST"


def finance() -> pd.DataFrame:
    d = RAW / "auxiliary" / "govfin2017"
    rows = []
    with open(d / "2017FinEstDAT_09202024modp_pu.txt", encoding="latin-1") as fh:
        for ln in fh:
            item = ln[12:15]
            if item[0] == "T" or item in ("E23", "E29"):
                rows.append((ln[0:2] + ln[3:6], ln[2], item, float(ln[15:27])))
    f = pd.DataFrame(rows, columns=["county_fips", "type", "item", "amt"])
    f["amt"] *= 1000
    tax = f[f.item.str.startswith("T")]
    out = pd.DataFrame({
        "tax_cgov": tax[tax.type == "1"].groupby("county_fips").amt.sum(),
        "tax_all": tax[tax.type.isin(list("12345"))].groupby("county_fips").amt.sum(),
        "admin_cgov": f[(f.type == "1") & f.item.isin(["E23", "E29"])].groupby("county_fips").amt.sum()}).fillna(0)
    return out.reset_index()


def state_intermediaries() -> pd.DataFrame:
    s = pd.read_parquet(RAW / "fema" / "fema_subapplications_raw.parquet")
    s = s[(s.program == "Hazard Mitigation Grant Program") & (s.fiscalYear <= 2008) & (s.status != "Void")].copy()
    n = s.subapplicantName.astype(str).str.upper()
    s["regional"] = n.str.contains(REGIONAL, regex=True)
    s["state_run"] = (n.str.contains(r"STATE OF|DEPARTMENT|DEPT\b|DIVISION OF|EMERGENCY MANAGEMENT|STATEWIDE", regex=True)
                      | s.benefitingCounties.astype(str).str.upper().str.contains("STATEWIDE"))
    g = s.groupby("subapplicantStateAbbreviation").agg(sh_regional=("regional", "mean"), sh_state=("state_run", "mean"),
                                                       n_pre=("regional", "size"))
    log.info("pre-2009 intermediary shares (top regional):\n%s", g.sort_values("sh_regional", ascending=False).head(12).round(3).to_string())
    return g.reset_index().rename(columns={"subapplicantStateAbbreviation": "STUSPS"})


def decl_dates() -> pd.DataFrame:
    d = pd.read_csv(RAW / "fema" / "DisasterDeclarationsSummaries.csv", usecols=["disasterNumber", "declarationDate"])
    d["decl_date"] = pd.to_datetime(d.declarationDate).dt.tz_localize(None)
    return d.groupby("disasterNumber").decl_date.min().reset_index()


def fit(rows, test, y, fml, data, terms, note=""):
    try:
        m = pf.feols(f"{y} ~ {fml}", data=data, vcov=VC)
        t = m.tidy()
        for term in terms:
            if term in t.index:
                rows.append({"test": test, "outcome": y, "term": term, "b": t.loc[term, "Estimate"],
                             "se": t.loc[term, "Std. Error"], "p": t.loc[term, "Pr(>|t|)"], "N": m._N,
                             "y_mean": data[y].mean(), "note": note})
    except Exception as e:  # noqa: BLE001
        rows.append({"test": test, "outcome": y, "term": "ERR", "note": str(e)[:100]})


def main() -> None:
    x = pd.read_parquet(PROC / "gap_county_disaster.parquet")
    x = x.merge(finance(), how="left", on="county_fips").merge(decl_dates(), how="left", on="disasterNumber")
    pop = x.baseline_pop.clip(lower=100)
    for c in ["tax_cgov", "tax_all", "admin_cgov"]:
        x["l" + c + "_pc"] = np.log1p(x[c].fillna(0) / pop)
    cty = x.drop_duplicates("county_fips").set_index("county_fips")
    for c in ["ltax_cgov_pc", "ladmin_cgov_pc", "ltax_all_pc"]:
        x["low_" + c] = (x.county_fips.map(cty[c].rank(pct=True)) <= 1 / 3).astype(int)
    log.info("finance coverage %.3f; means small vs other:\n%s", x.tax_cgov.notna().mean(),
             x.groupby("small")[["ltax_cgov_pc", "ladmin_cgov_pc", "ltax_all_pc"]].mean().round(3).to_string())
    x = x.merge(state_intermediaries(), how="left", on="STUSPS")
    x["n_app_nonstrict"] = x.n_app - x.n_app_strict
    x["applied_nonstrict"] = (x.n_app_nonstrict > 0).astype(int)
    rows = []
    OUT = ["applied", "dis_any", "dis_strict", "applied_cgov"]

    # ---------------- T1 fiscal / administrative capacity
    for y in OUT:
        fit(rows, "T1 base (S4 + gov counts)", y, f"small + {GOVS} + {EXPO} + {DEMO} | disaster", x, ["small"])
        fit(rows, "T1 + fiscal capacity", y, f"small + {GOVS} + ltax_cgov_pc + ltax_all_pc + ladmin_cgov_pc + {EXPO} + {DEMO} | disaster",
            x, ["small", "ltax_cgov_pc", "ltax_all_pc", "ladmin_cgov_pc"])
        for c in ["low_ltax_cgov_pc", "low_ladmin_cgov_pc"]:
            x["sm_x"] = x.small * x[c]
            fit(rows, f"T1 small x {c}", y, f"small + {c} + sm_x + {GOVS} + {EXPO} + {DEMO} | disaster", x,
                ["small", c, "sm_x"])

    # ---------------- T2 intermediaries (pre-period state shares; outcomes 2009-2021)
    p2 = x[x.year >= 2009].copy()
    for c in ["sh_regional", "sh_state"]:
        p2["z"] = (p2[c] - p2[c].mean()) / p2[c].std()
        p2["sm_z"] = p2.small * p2.z
        for y in OUT:
            fit(rows, f"T2 small x z({c}) [2009-21]", y, f"small + sm_z + {GOVS} + {EXPO} + {DEMO} | disaster", p2,
                ["small", "sm_z"], note="z absorbed by disaster FE")
    # state-specific gaps (descriptive): states with >= 150 obs
    sg = []
    for st, g in x[x.year >= 2009].groupby("STUSPS"):
        if len(g) >= 150 and g.small.between(0.1, 0.9).mean() and 0.1 < g.small.mean() < 0.9:
            try:
                m = pf.feols(f"applied ~ small + {EXPO} | disaster", data=g, vcov=VC)
                sg.append({"STUSPS": st, "gap": m.tidy().loc["small", "Estimate"], "N": m._N,
                           "sh_regional": g.sh_regional.iloc[0], "sh_state": g.sh_state.iloc[0]})
            except Exception:  # noqa: BLE001
                pass
    sg = pd.DataFrame(sg)
    sg.to_csv(TABLES / "gap_causal_state_gaps.csv", index=False)
    if len(sg) > 5:
        log.info("state gaps (n=%d): corr(gap, sh_regional)=%.3f, corr(gap, sh_state)=%.3f\n%s", len(sg),
                 sg.gap.corr(sg.sh_regional), sg.gap.corr(sg.sh_state), sg.sort_values("gap").round(3).to_string())

    # ---------------- T3 demand shock within county (county FE + disaster FE)
    x["E_small"] = x.E * x.small
    x["E_lpop"] = x.E * (x.lpop - x.lpop.mean())
    x["dpc_small"] = x.ldmg_pc * x.small
    for y in OUT + ["l_napp"]:
        fit(rows, "T3 hit x small | county+disaster FE", y, f"E + E_small + {EXPO_TV} | county_fips + disaster", x, ["E", "E_small"])
        fit(rows, "T3 hit x log pop | county+disaster FE", y, f"E + E_lpop + {EXPO_TV} | county_fips + disaster", x, ["E", "E_lpop"])
        fit(rows, "T3 damage pc x small | county+disaster FE", y, f"ldmg_pc + dpc_small + E + lpe + track_km + mag + cas + ldmg | county_fips + disaster",
            x, ["ldmg_pc", "dpc_small"])

    # ---------------- T4 DRRA s.1215 management-cost reimbursement (declared >= 2017-08-01)
    d4 = x[(x.decl_date >= "2010-01-01") & (x.decl_date <= "2021-12-31")].copy()
    d4["post"] = (d4.decl_date >= "2017-08-01").astype(int)
    d4["sm_post"] = d4.small * d4.post
    d4["lpop_post"] = (d4.lpop - d4.lpop.mean()) * d4.post
    for y in OUT + ["l_napp"]:
        fit(rows, "T4 DRRA small x post | county+disaster FE", y, f"sm_post + {EXPO} | county_fips + disaster", d4, ["sm_post"])
        fit(rows, "T4 DRRA logpop x post | county+disaster FE", y, f"lpop_post + {EXPO} | county_fips + disaster", d4, ["lpop_post"])
    # placebo: pre-period only, fake cutoff 2014-08-01
    pl = d4[d4.post == 0].copy()
    pl["sm_fake"] = pl.small * (pl.decl_date >= "2014-08-01").astype(int)
    for y in OUT:
        fit(rows, "T4 placebo cutoff 2014-08 (pre-DRRA sample)", y, f"sm_fake + {EXPO} | county_fips + disaster", pl, ["sm_fake"])
    # event study by declaration year (ref 2016)
    d4["dy"] = d4.decl_date.dt.year
    es = []
    for y in ["applied", "dis_any"]:
        m = pf.feols(f"{y} ~ i(dy, small, ref=2016) + {EXPO} | county_fips + disaster", data=d4, vcov=VC)
        t = m.tidy()
        for term, r in t[t.index.str.contains("dy::")].iterrows():
            es.append({"outcome": y, "term": term, "b": r.Estimate, "se": r["Std. Error"], "p": r["Pr(>|t|)"]})
    es = pd.DataFrame(es)
    es.to_csv(TABLES / "gap_causal_drra_event_study.csv", index=False)
    log.info("DRRA event study (small x declaration year, ref 2016):\n%s", es.round(4).to_string())
    log.info("raw applied rate by period x small:\n%s", d4.groupby(["post", "small"]).applied.mean().unstack().round(3).to_string())

    # ---------------- T4b exploratory: pre-calculated safe-room benefits (2015-02-19), triple difference
    d5 = x[(x.decl_date >= "2009-01-01") & (x.decl_date <= "2021-12-31")].copy()
    d5["post"] = (d5.decl_date >= "2015-02-19").astype(int)
    st = pd.concat([d5.assign(yy=d5.applied_strict, sr=1), d5.assign(yy=d5.applied_nonstrict, sr=0)])
    st["cty_sr"] = st.county_fips + "_" + st.sr.astype(str)
    st["dis_sr"] = st.disaster + "_" + st.sr.astype(str)
    st["sm_post_sr"] = st.small * st.post * st.sr
    st["sm_sr"] = st.small * st.sr
    st["sm_post"] = st.small * st.post
    fit(rows, "T4b safe-room precalc triple diff (exploratory)", "yy", "sm_post_sr + sm_post | cty_sr + dis_sr", st,
        ["sm_post_sr", "sm_post"])

    r = pd.DataFrame(rows)
    r.to_csv(TABLES / "gap_causal_results.csv", index=False)
    pd.set_option("display.width", 250)
    log.info("results:\n%s", r[["test", "outcome", "term", "b", "se", "p", "N", "y_mean"]].round(4).to_string())


if __name__ == "__main__":
    main()
