"""Mechanisms behind the SMALL-COUNTY CONVERSION GAP (2026-10-09). Builds on 50_small_county_robustness.py.

Test 1  'Fewer eligible applicants' (mechanical): Census of Governments 2017 counts per county of
        municipalities+townships, special districts, school districts; and outcomes split by applicant
        type. Every county has exactly ONE county government, so a gap in county-government-applied projects
        cannot be an applicant-count artifact.
Test 2  'Did not apply' vs 'applied and failed': OpenFEMA HMGP subapplications (all statuses, linked by
        disaster number + benefiting county): P(apply), success rate, withdrawal rate, BCR, project size.
Outputs: output/tables/gap_mech_*.csv
"""
from __future__ import annotations

import importlib.util
import re

import numpy as np
import pandas as pd
import pyfixest as pf

from utils import RAW, SRC, TABLES, XWALK, get_logger

log = get_logger(__file__)
_s = importlib.util.spec_from_file_location("sc", SRC / "50_small_county_robustness.py")
sc = importlib.util.module_from_spec(_s)
_s.loader.exec_module(sc)
VC = {"CRV1": "county_fips"}
OK = {"Approved", "Closed", "Obligated", "Subaward Accepted"}
FAIL = {"Withdrawn", "Not Approved / Denied", "Not Approved", "Ineligible", "Not Selected"}


def cog() -> pd.DataFrame:
    f = RAW / "auxiliary" / "cog2017" / "Govt_Units_2017_Final.xlsx"
    x = pd.ExcelFile(f)
    gp = x.parse("General Purpose", dtype=str)
    gp["fips"] = gp.FIPS_STATE.str.zfill(2) + gp.FIPS_COUNTY.str.zfill(3)
    cty_gov = gp[gp.UNIT_TYPE.str.contains("COUNTY", case=False, na=False)]
    sub = gp[~gp.UNIT_TYPE.str.contains("COUNTY", case=False, na=False)]
    out = pd.DataFrame({"n_gp": sub.groupby("fips").size()})
    out["county_web"] = cty_gov.groupby("fips").WEB_ADDRESS.apply(lambda s: int(s.notna().any()))
    for sheet, col in [("Special District", "n_sd"), ("School District", "n_sch"), ("DEP School District", "n_dsch")]:
        d = x.parse(sheet, dtype=str)
        d["fips"] = d.FIPS_STATE.str.zfill(2) + d.FIPS_COUNTY.str.zfill(3)
        out[col] = d.groupby("fips").size()
    out = out.fillna(0)
    out["n_sch"] = out.n_sch + out.n_dsch
    out["n_local"] = out.n_gp + out.n_sd + out.n_sch
    log.info("CoG 2017 units by type (sum): %s; unit types: %s", out[["n_gp", "n_sd", "n_sch"]].sum().to_dict(),
             gp.UNIT_TYPE.value_counts().to_dict())
    return out.drop(columns="n_dsch").reset_index().rename(columns={"fips": "county_fips"})


def applicant_type(name: str, county_names: set) -> str:
    n = str(name).upper()
    if "STATEWIDE" in n or re.search(r"\bSTATE OF\b|DEPARTMENT|DEPT\b|DIVISION OF|UNIVERSITY|EMERGENCY MANAGEMENT AGENCY", n):
        return "state/other"
    if re.search(r"SCHOOL|\bISD\b|\bUSD\b|\bCISD\b|\bR-?\d|BOARD OF EDUCATION|PUBLIC SCHOOLS", n):
        return "school"
    if re.search(r"\(COUNTY\)|\bCOUNTY OF\b|\bCOUNTY\b|\bPARISH\b|\bCOMMISSION\b", n) and not re.search(r"CITY|TOWN|VILLAGE", n):
        return "county_gov"
    if re.search(r"\bCITY\b|\bTOWN\b|\bVILLAGE\b|TOWNSHIP|BOROUGH|\(CITY|\(TOWN|\(VILLAGE", n):
        return "municipal"
    if re.search(r"DISTRICT|AUTHORITY|COOP|ELECTRIC|WATER|SEWER|UTILIT|HOSPITAL|CHURCH|INC\b|LLC", n):
        return "special/other"
    return "municipal"     # bare place names (e.g., 'Cuero', 'Smithville') are overwhelmingly municipalities


def is_strict(text: str) -> bool:
    t = str(text).upper()
    return bool(re.search(r"SAFE ROOM|SAFEROOM|SHELTER|WIND RETROFIT|WIND.*RETROFIT|ROOF|STORM SHUTTER|TORNADO", t))


def subapps() -> pd.DataFrame:
    s = pd.read_parquet(RAW / "fema" / "fema_subapplications_raw.parquet")
    s = s[(s.program == "Hazard Mitigation Grant Program") & s.disasterNumber.notna() & (s.status != "Void")].copy()
    c = pd.read_parquet(XWALK / "counties_2020.parquet")
    key = {(a, sc.norm(n)): f for a, n, f in zip(c.STUSPS, c.NAME, c.county_fips)}
    rows = []
    for r in s.itertuples(index=False):
        names = [x.strip() for x in str(r.benefitingCounties).replace(",", ";").split(";") if x.strip()]
        fips = {key.get((r.subapplicantStateAbbreviation, sc.norm(n))) for n in names if "STATEWIDE" not in n.upper()} - {None}
        for f in fips:
            rows.append({"county_fips": f, "disasterNumber": float(r.disasterNumber), "status": r.status,
                         "name": r.subapplicantName, "bcr": r.benefitCostRatio, "amt": r.totalSubapplicationAmount,
                         "strict": is_strict(f"{r.subapplicationTitle} {r.primaryActivity} {r.primarySubactivity}"),
                         "small_impov": r.smallImpoverished, "share": 1 / len(fips)})
    a = pd.DataFrame(rows)
    a["ok"] = a.status.isin(OK).astype(int)
    a["fail"] = a.status.isin(FAIL).astype(int)
    a["withdrawn"] = (a.status == "Withdrawn").astype(int)
    a["denied"] = a.status.isin({"Not Approved / Denied", "Not Approved", "Ineligible", "Not Selected"}).astype(int)
    a["decided"] = a.ok + a.fail
    log.info("HMGP subapps linked to counties: %d rows (%d unmatched-or-statewide dropped); status: %s",
             len(a), len(s) - a.groupby(["disasterNumber"]).size().sum() if False else -1, a.status.value_counts().to_dict())
    return a


def main() -> None:
    x = sc.build().dropna(subset=["med_inc", "pov_rate", "nonwhite"])
    g = cog()
    x = x.merge(g, how="left", on="county_fips")
    for c in ["n_gp", "n_sd", "n_sch", "n_local"]:
        x["l" + c] = np.log1p(x[c].fillna(0))
    log.info("CoG coverage %.3f; mean units small vs other:\n%s", x.n_gp.notna().mean(),
             x.groupby("small")[["n_gp", "n_sd", "n_sch", "county_web"]].mean().round(2).to_string())

    # ---- funded projects split by applicant type (HMGP, this disaster)
    p = sc.project_counties()
    pr = pd.read_parquet(RAW.parent / "intermediate" / "fema_projects_classified.parquet",
                         columns=["projectIdentifier", "subrecipient"]).drop_duplicates("projectIdentifier")
    p = p.merge(pr.rename(columns={"projectIdentifier": "pid"}), how="left", on="pid")
    cn = set(sc.norm(n) for n in pd.read_parquet(XWALK / "counties_2020.parquet").NAME)
    p["atype"] = [applicant_type(n, cn) for n in p.subrecipient]
    hm = p[(p.programArea == "HMGP") & p.county_fips.notna()]
    for t in ["county_gov", "municipal", "school", "special/other"]:
        k = hm[hm.atype == t].groupby(["county_fips", "disasterNumber"]).size().rename(f"f_{t}")
        x = x.merge(k.reset_index(), how="left", on=["county_fips", "disasterNumber"])
        x[f"f_{t}"] = (x[f"f_{t}"].fillna(0) > 0).astype(int)
    x["f_noncounty"] = ((x.f_municipal + x.f_school + x["f_special/other"]) > 0).astype(int)
    log.info("applicant-type mix of funded HMGP project-county rows: %s", hm.atype.value_counts(normalize=True).round(3).to_dict())

    # ---- applications
    a = subapps()
    a["atype"] = [applicant_type(n, cn) for n in a.name]
    agg = a.groupby(["county_fips", "disasterNumber"]).agg(
        n_app=("status", "size"), n_ok=("ok", "sum"), n_fail=("fail", "sum"), n_wd=("withdrawn", "sum"),
        n_den=("denied", "sum"), n_dec=("decided", "sum"), n_app_strict=("strict", "sum")).reset_index()
    cg = a[a.atype == "county_gov"].groupby(["county_fips", "disasterNumber"]).size().rename("n_app_cgov").reset_index()
    x = x.merge(agg, how="left", on=["county_fips", "disasterNumber"]).merge(cg, how="left", on=["county_fips", "disasterNumber"])
    for c in ["n_app", "n_ok", "n_fail", "n_wd", "n_den", "n_dec", "n_app_strict", "n_app_cgov"]:
        x[c] = x[c].fillna(0)
    x["applied"] = (x.n_app > 0).astype(int)
    x["applied_strict"] = (x.n_app_strict > 0).astype(int)
    x["applied_cgov"] = (x.n_app_cgov > 0).astype(int)
    x["any_ok"] = (x.n_ok > 0).astype(int)
    x["l_napp"] = np.log1p(x.n_app)
    x["succ_rate"] = (x.n_ok / x.n_dec).where(x.n_dec > 0)
    x["wd_rate"] = (x.n_wd / x.n_dec).where(x.n_dec > 0)
    x["den_rate"] = (x.n_den / x.n_dec).where(x.n_dec > 0)
    log.info("validation: P(any approved subapp) %.3f vs P(funded HMGP project, dis_any) %.3f; corr %.3f",
             x.any_ok.mean(), x.dis_any.mean(), x[["any_ok", "dis_any"]].corr().iloc[0, 1])

    x.to_parquet(RAW.parent / "processed" / "gap_county_disaster.parquet", index=False)
    a.to_parquet(RAW.parent / "processed" / "gap_subapps_linked.parquet", index=False)
    ctrl = f"{sc.EXPO} + {sc.DEMO}"
    govs = "ln_gp + ln_sd + ln_sch"
    rows = []

    def add(test, y, rhs, data, term="small"):
        m = pf.feols(f"{y} ~ {rhs} | disaster", data=data, vcov=VC)
        t = m.tidy()
        rows.append({"test": test, "outcome": y, "rhs": rhs.split(" + ")[0] + (" +govcounts" if "ln_gp" in rhs else "")
                     + (" +web" if "county_web" in rhs else ""), "b": t.loc[term, "Estimate"],
                     "se": t.loc[term, "Std. Error"], "p": t.loc[term, "Pr(>|t|)"], "N": m._N,
                     "base": data.loc[data.small == 0, y].mean()})
        return t

    # Test 1a: does controlling for the number of local units close the gap?
    for y in ["dis_any", "dis_strict", "win3_strict"]:
        add("T1a base S4", y, f"small + {ctrl}", x)
        t = add("T1a + gov counts", y, f"small + {govs} + {ctrl}", x)
        for v in ["ln_gp", "ln_sd", "ln_sch"]:
            rows.append({"test": "T1a coef", "outcome": y, "rhs": v, "b": t.loc[v, "Estimate"], "p": t.loc[v, "Pr(>|t|)"]})
        add("T1a + gov counts + county website", y, f"small + {govs} + county_web + {ctrl}", x)
    # Test 1b: outcomes by applicant type (county government: exactly one per county)
    for y in ["f_county_gov", "f_noncounty", "f_municipal", "f_school", "applied_cgov"]:
        add("T1b by applicant type", y, f"small + {govs} + {ctrl}", x)

    # Test 2: applications vs approvals
    for y in ["applied", "applied_strict", "l_napp", "any_ok"]:
        add("T2 apply margin", y, f"small + {ctrl}", x)
        add("T2 apply margin", y, f"small + {govs} + {ctrl}", x)
    ap = x[x.n_dec > 0]
    for y in ["succ_rate", "wd_rate", "den_rate"]:
        add("T2 conditional on applying", y, f"small + {ctrl}", ap)
        add("T2 conditional on applying", y, f"small + {govs} + {ctrl}", ap)
    # subapplication level: success, withdrawal, BCR, size
    a2 = a.merge(x[["county_fips", "disasterNumber", "small", "lpop", "E", "lpe", "track_km", "mag", "cas", "ldmg",
                    "ldmg_pc", "linc", "pov_rate", "nonwhite", "nonmetro", "disaster"]].drop_duplicates(["county_fips", "disasterNumber"]),
                 how="inner", on=["county_fips", "disasterNumber"])
    a2 = a2[a2.decided == 1].copy()
    a2["lamt"] = np.log(a2.amt.where(a2.amt > 0))
    a2["lbcr"] = np.log(a2.bcr.where(a2.bcr > 0))
    for y in ["ok", "withdrawn", "denied", "lamt", "lbcr"]:
        d = a2.dropna(subset=[y])
        add("T2 subapp level", y, f"small + {ctrl}", d)
    r = pd.DataFrame(rows)
    r.to_csv(TABLES / "gap_mech_results.csv", index=False)
    pd.set_option("display.width", 250)
    log.info("results:\n%s", r.round(4).to_string())
    # descriptive funnel by size
    fun = x.groupby("small").agg(applied=("applied", "mean"), n_app=("n_app", "mean"), succ=("succ_rate", "mean"),
                                 wd=("wd_rate", "mean"), den=("den_rate", "mean"), any_ok=("any_ok", "mean"),
                                 funded=("dis_any", "mean"), cgov_applied=("applied_cgov", "mean"),
                                 f_cgov=("f_county_gov", "mean"), f_noncounty=("f_noncounty", "mean"))
    fun.to_csv(TABLES / "gap_mech_funnel.csv")
    log.info("raw funnel by small:\n%s", fun.round(3).to_string())
    log.info("subapp app-type mix: %s", a.atype.value_counts(normalize=True).round(3).to_dict())


if __name__ == "__main__":
    main()
