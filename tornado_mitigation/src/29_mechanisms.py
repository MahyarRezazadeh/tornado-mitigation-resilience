"""Mechanism tests (Section 30) + industry reallocation (Outcome 9) + small business (Outcome 8).

M1 physical damage / casualties: log(1+damage), log(1+fatalities), log(1+injuries) on Mitigated x intensity
   (intensity = max EF + 1, 0 if none); damage is NEVER used as exposure.
M2 business continuity: county x industry quarterly QWI; Mitigated x Tornado x PhysicalPremise
   (manufacturing, retail, leisure/hospitality, health) vs remote-capable (information, finance, professional).
M3 match preservation: assessed from separations / hires / turnover primary estimates (in 38).
M4 small business: BDS county x firm-size class; Mitigated x Tornado x Small(1-19).
M5 critical-facility type: treatment split by protected facility type of the county's strict projects.
M6 severity gradient: tornado bins EF0-only / EF1 / EF2 / EF3+ each interacted with Mitigated.
Industry reallocation: main model estimated separately for each industry group (QWI quarterly, CBP annual).
Outputs: output/models/mechanisms.csv, industry_by_group.csv, severity_gradient.csv
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pyfixest as pf

import est
from utils import INTER, MODELS, PROC, get_logger

log = get_logger(__file__)
PHYS = {"Manufacturing", "Retail", "Leisure/Hospitality", "Health"}
REMOTE = {"Information", "Finance", "Professional Services"}


def tidy_row(fit, term, **kw):
    tb = fit.tidy()
    if term not in tb.index:
        return {**kw, "term": term, "status": "not estimated"}
    r = tb.loc[term]
    return {**kw, "term": term, "beta": r["Estimate"], "se": r["Std. Error"], "p": r["Pr(>|t|)"],
            "ci_low": r["2.5%"], "ci_high": r["97.5%"], "N": int(fit._N), "status": "ok"}


def treat_lookup(freq="q"):
    d, _ = est.build(est.Spec(outcome="EF1_plus" if freq == "q" else "mar_EF1_plus", freq=freq))
    t = est.time_col(freq)
    return d[["county_fips", t, "M", "T", "ever"]]


def m1(rows):
    d, _ = est.build(est.Spec(outcome="EF1_plus", freq="q"))
    d["I"] = (d["max_tornado_intensity"].fillna(-1) + 1)
    d["MI"] = d["M"] * d["I"]
    for y, raw in [("log_damage", "reported_property_damage"), ("log_fatalities", "total_fatalities"),
                   ("log_injuries", "total_injuries")]:
        d[y] = np.log1p(d[raw].fillna(0))
        f = pf.feols(f"{y} ~ MI + M + I | county_fips + state_yq", data=d, vcov={"CRV1": "county_fips"})
        rows.append(tidy_row(f, "MI", mechanism="M1", outcome=y, sample="all county-quarters",
                             mean_y=d[y].mean()))
        s = d[d.any_tornado > 0]
        f = pf.feols(f"{y} ~ M + C(I) | county_fips + state_yq", data=s, vcov={"CRV1": "county_fips"})
        rows.append(tidy_row(f, "M", mechanism="M1", outcome=y, sample="tornado county-quarters (EF bins FE)",
                             mean_y=s[y].mean()))
        f = pf.feols(f"{y} ~ MI + M + C(I) | county_fips + state_yq", data=s, vcov={"CRV1": "county_fips"})
        rows.append(tidy_row(f, "MI", mechanism="M1", outcome=y, sample="tornado county-quarters, M x intensity",
                             mean_y=s[y].mean()))


def industry_panel():
    cols = ["county_fips", "yq", "industry_group", "state_fips", "separation_rate", "log_employment", "log_earnings",
            "job_destruction_rate_qwi"]
    ind = pd.read_parquet(PROC / "county_industry_quarter_panel.parquet", columns=cols)
    ind = ind[ind.industry_group != "Other/Unassigned"]
    for c in ["separation_rate", "log_employment", "log_earnings", "job_destruction_rate_qwi"]:
        ind[c] = ind[c].astype("float32")
    tl = treat_lookup("q")
    tl["M"] = tl["M"].astype("int8")
    ind = ind.merge(tl, on=["county_fips", "yq"], how="inner")
    ind["MT"] = ind.M * ind["T"]
    ig = pd.factorize(ind.industry_group)[0].astype("int64")
    cf = ind.county_fips.astype("int64")
    ind["iy"] = ig * 100000 + ind.yq.astype("int64")
    ind["ci"] = cf * 100 + ig
    ind["sy"] = ind.state_fips.astype("int64") * 100000 + ind.yq.astype("int64")
    return ind


def m2(rows, ind):
    d = ind[ind.industry_group.isin(PHYS | REMOTE)].copy()
    d["P"] = d.industry_group.isin(PHYS).astype(int)
    d["MTP"], d["MP"], d["TP"] = d.MT * d.P, d.M * d.P, d["T"] * d.P
    for y in ["separation_rate", "log_employment", "log_earnings", "job_destruction_rate_qwi"]:
        f = pf.feols(f"{y} ~ MTP + MT + MP + TP + M + T | ci + iy + sy", data=d[d[y].notna()],
                     vcov={"CRV1": "county_fips"})
        rows.append(tidy_row(f, "MTP", mechanism="M2", outcome=y, sample="physical vs remote-capable industries"))
        rows.append(tidy_row(f, "MT", mechanism="M2", outcome=y, sample="remote-capable baseline MxT"))


def industry_by_group(ind):
    out = []
    for g, d in ind.groupby("industry_group"):
        for y in ["log_employment", "separation_rate"]:
            s = d[d[y].notna()]
            if s.MT.sum() == 0:
                continue
            f = pf.feols(f"{y} ~ MT + M + T | county_fips + sy", data=s, vcov={"CRV1": "county_fips"})
            out.append(tidy_row(f, "MT", industry=g, outcome=y, source="QWI", mean_y=s[y].mean()))
    cbp = pd.read_parquet(PROC / "county_industry_year_panel.parquet")
    tl = treat_lookup("y")
    cbp = cbp.merge(tl, on=["county_fips", "year"], how="inner")
    cbp["MT"] = cbp.M * cbp["T"]
    cbp["sy"] = cbp.state_fips + "_" + cbp.year.astype(str)
    for g, d in cbp.groupby("industry_group"):
        s = d[d.log_establishments.notna()]
        if s.MT.sum() == 0:
            continue
        f = pf.feols("log_establishments ~ MT + M + T | county_fips + sy", data=s, vcov={"CRV1": "county_fips"})
        out.append(tidy_row(f, "MT", industry=g, outcome="log_establishments", source="CBP", mean_y=s.log_establishments.mean()))
    pd.DataFrame(out).to_csv(MODELS / "industry_by_group.csv", index=False)


def m4(rows):
    fz = pd.read_parquet(INTER / "bds_county_year_fsize.parquet")
    tl = treat_lookup("y")
    d = fz.merge(tl, on=["county_fips", "year"], how="inner")
    d = d.merge(est.panel("y")[["county_fips", "year", "state_year"]], on=["county_fips", "year"])
    d["S"] = (d.fsizecoarse == "a) 1 to 19").astype(int)
    d["MT"] = d.M * d["T"]
    d["MTS"], d["MS"], d["TS"] = d.MT * d.S, d.M * d.S, d["T"] * d.S
    d["cs"] = d.county_fips + "_" + d.fsizecoarse
    d["sz_y"] = d.fsizecoarse + "_" + d.year.astype(str)
    for y in ["establishment_death_rate", "job_destruction_rate"]:
        s = d[d[y].notna()]
        f = pf.feols(f"{y} ~ MTS + MT + MS + TS + M + T | cs + sz_y + state_year", data=s, vcov={"CRV1": "county_fips"})
        rows.append(tidy_row(f, "MTS", mechanism="M4", outcome=y, sample="BDS firm size 1-19 vs 20+"))
        rows.append(tidy_row(f, "MT", mechanism="M4", outcome=y, sample="BDS firm size 20+ baseline MxT"))
    # QWI firm-size cells (API) if present
    dm = pd.read_parquet(PROC / "county_demographic_quarter_panel.parquet")
    q = dm[dm.demo_family == "firmsize"].copy()
    if len(q):
        tlq = treat_lookup("q")
        q = q.merge(tlq, on=["county_fips", "yq"], how="inner")
        q["S"] = q.demo_group.isin(["fsize_1", "fsize_2"]).astype(int)   # <20 employees
        q["MT"] = q.M * q["T"]
        q["MTS"], q["MS"], q["TS"] = q.MT * q.S, q.M * q.S, q["T"] * q.S
        q["cg"] = q.county_fips + "_" + q.demo_group
        q["gy"] = q.demo_group + "_" + q.yq.astype(str)
        q["sy"] = q.state_fips + "_" + q.yq.astype(str)
        for y in ["separation_rate", "log_employment"]:
            s = q[q[y].notna()]
            f = pf.feols(f"{y} ~ MTS + MT + MS + TS + M + T | cg + gy + sy", data=s, vcov={"CRV1": "county_fips"})
            rows.append(tidy_row(f, "MTS", mechanism="M4", outcome=y, sample="QWI firm size <20 vs 20+"))


def m5(rows):
    p = pd.read_parquet(INTER / "fema_treatment_projects.parquet")
    p = p[(p.treat_strict == 1) & p.county_fips.notna()]
    types = p.groupby("county_fips").facility_type.agg(lambda s: set(s))
    for var, freq in [("separation_rate", "q"), ("establishment_death_rate", "y"), ("log_employment", "q")]:
        d, yv = est.build(est.Spec(outcome=var, freq=freq))
        st = "state_yq" if freq == "q" else "state_year"
        terms = []
        for ft in ["school", "residential_private", "hospital", "fire_police", "community_shelter", "unknown"]:
            has = d.county_fips.map(types).apply(lambda s, ft=ft: isinstance(s, set) and ft in s).astype(int)
            d[f"MT_{ft}"] = d.MT * has
            d[f"M_{ft}"] = d.M * has
            if d[f"MT_{ft}"].sum() > 0:
                terms += [f"MT_{ft}", f"M_{ft}"]
        f = pf.feols(f"{yv} ~ {' + '.join(terms)} + T | county_fips + {st}", data=d, vcov={"CRV1": "county_fips"})
        for t in terms:
            if t.startswith("MT_"):
                rows.append(tidy_row(f, t, mechanism="M5", outcome=var, sample="facility-type split (overlapping)"))


def m6():
    out = []
    specs = [("separation_rate", "q", "max_tornado_intensity"), ("log_employment", "q", "max_tornado_intensity"),
             ("log_earnings", "q", "max_tornado_intensity"),
             ("establishment_death_rate", "y", "mar_max_tornado_intensity"),
             ("job_destruction_rate", "y", "mar_max_tornado_intensity")]
    for var, freq, iv in specs:
        d, yv = est.build(est.Spec(outcome=var, freq=freq))
        st = "state_yq" if freq == "q" else "state_year"
        I = d[iv]
        bins = {"EF0": I == 0, "EF1": I == 1, "EF2": I == 2, "EF3plus": I >= 3}
        terms = []
        for b, m in bins.items():
            d[f"B_{b}"] = m.fillna(False).astype(int)
            d[f"MB_{b}"] = d[f"B_{b}"] * d.M
            terms += [f"B_{b}", f"MB_{b}"]
        f = pf.feols(f"{yv} ~ {' + '.join(terms)} + M | county_fips + {st}", data=d, vcov={"CRV1": "county_fips"})
        tb = f.tidy()
        for b in bins:
            out.append({"outcome": var, "bin": b, "tornado_effect": tb.loc[f"B_{b}", "Estimate"],
                        "tornado_se": tb.loc[f"B_{b}", "Std. Error"], "mitig_diff": tb.loc[f"MB_{b}", "Estimate"],
                        "mitig_diff_se": tb.loc[f"MB_{b}", "Std. Error"], "mitig_diff_p": tb.loc[f"MB_{b}", "Pr(>|t|)"],
                        "n_treated_obs": int(d[f"MB_{b}"].sum())})
    pd.DataFrame(out).to_csv(MODELS / "severity_gradient.csv", index=False)


def main() -> None:
    rows = []
    for fn in [m1, m4, m5]:
        try:
            fn(rows)
        except Exception as e:  # noqa: BLE001
            log.error("%s failed: %s", fn.__name__, e)
    try:
        ind = industry_panel()
        m2(rows, ind)
        industry_by_group(ind)
    except Exception as e:  # noqa: BLE001
        log.error("industry mechanisms failed: %s", e)
    try:
        m6()
    except Exception as e:  # noqa: BLE001
        log.error("severity gradient failed: %s", e)
    df = pd.DataFrame(rows)
    df.to_csv(MODELS / "mechanisms.csv", index=False)
    log.info("\n%s", df[[c for c in ["mechanism", "outcome", "sample", "term", "beta", "se", "p"] if c in df]].to_string())


if __name__ == "__main__":
    main()
