"""Clean QWI extracts and construct outcomes.

Suppression: status flags -2, -1, 5, 11 -> value set to missing (never zero). Flags 7/9/12
(distorted/fuzzed but released) kept and counted.
Rates use average employment (Emp + EmpEnd)/2 as denominator (QWI Explorer convention).
Emp is BEGINNING-of-quarter employment (cannot respond to a same-quarter tornado), so the
pre-specified employment outcome is EmpEnd (end-of-quarter).

Outputs:
  data/intermediate/qwi_county_quarter.parquet           (all industries, all workers)
  data/intermediate/qwi_county_industry_quarter.parquet  (NAICS sectors -> industry groups)
  data/intermediate/qwi_county_demo_quarter.parquet      (sex, age, education, race, ethnicity, firm size)
  output/diagnostics/qwi_suppression.csv
"""
from __future__ import annotations

import importlib

import numpy as np
import pandas as pd

from utils import DIAG, INTER, RAW, get_logger, log_frame

log = get_logger(__file__)
xw = importlib.import_module("22_build_county_crosswalk")
BAD = {-2, -1, 5, 11}
VARS = ["Emp", "EmpEnd", "EmpS", "HirA", "HirN", "Sep", "SepBeg", "SepS", "HirAS", "TurnOvrS", "FrmJbGn",
        "FrmJbLs", "FrmJbC", "EarnS", "EarnBeg", "EarnHirAS", "EarnHirNS", "Payroll"]
SECTOR_GROUP = {"23": "Construction", "31-33": "Manufacturing", "44-45": "Retail",
                "48-49": "Transportation/Warehousing", "51": "Information", "52": "Finance",
                "54": "Professional Services", "61": "Education", "62": "Health", "71": "Leisure/Hospitality",
                "72": "Leisure/Hospitality", "81": "Other Services"}


def apply_flags(d: pd.DataFrame, vars_: list[str]) -> dict:
    supp = {}
    for v in vars_:
        f = "s" + v
        if v in d and f in d:
            flag = pd.to_numeric(d[f], errors="coerce")
            bad = flag.isin(BAD)
            supp[v] = float(bad.mean())
            d[v] = pd.to_numeric(d[v], errors="coerce").where(~bad)
            d[f + "_distorted"] = flag.isin({7, 9, 12})
    return supp


def outcomes(d: pd.DataFrame) -> pd.DataFrame:
    avg = (d["Emp"] + d["EmpEnd"]) / 2
    d["avg_emp"] = avg
    d["employment"] = d["EmpEnd"]
    d["log_employment"] = np.log(d["EmpEnd"].where(d["EmpEnd"] > 0))
    d["beginning_employment"] = d["Emp"]
    d["ending_employment"] = d["EmpEnd"]
    d["employment_growth"] = (d["EmpEnd"] - d["Emp"]) / avg.where(avg > 0)          # DHS growth, in [-2, 2]
    d["separations"] = d["Sep"]
    d["separation_rate"] = d["Sep"] / avg.where(avg > 0)
    d["retention_rate"] = 1 - d["SepBeg"] / d["Emp"].where(d["Emp"] > 0)
    d["hires"] = d["HirA"]
    d["hire_rate"] = d["HirA"] / avg.where(avg > 0)
    d["new_hires"] = d["HirN"]
    d["new_hire_rate"] = d["HirN"] / avg.where(avg > 0)
    d["turnover"] = d["TurnOvrS"]
    d["average_earnings"] = d["EarnS"]
    d["log_earnings"] = np.log(d["EarnS"].where(d["EarnS"] > 0))
    d["new_hire_earnings"] = d["EarnHirNS"]
    d["log_new_hire_earnings"] = np.log(d["EarnHirNS"].where(d["EarnHirNS"] > 0))
    d["job_destruction_qwi"] = d["FrmJbLs"]
    d["job_destruction_rate_qwi"] = d["FrmJbLs"] / avg.where(avg > 0)
    d["job_creation_rate_qwi"] = d["FrmJbGn"] / avg.where(avg > 0) if "FrmJbGn" in d else np.nan
    # invalid ratios: rates outside [0, 2] indicate inconsistent cells -> missing
    for r in ["separation_rate", "hire_rate", "new_hire_rate", "job_destruction_rate_qwi"]:
        d.loc[(d[r] < 0) | (d[r] > 2), r] = np.nan
    return d


def main() -> None:
    files = sorted((RAW / "qwi").glob("qwi_*_sa_f_gc_ns_op_u_extract.parquet"))
    log.info("%d state extracts", len(files))
    keep = ["county_fips", "yq", "year", "quarter", "industry", "sex", "agegrp"] + VARS + \
           ["avg_emp", "employment", "log_employment", "beginning_employment", "ending_employment",
            "employment_growth", "separations", "separation_rate", "retention_rate", "hires", "hire_rate",
            "new_hires", "new_hire_rate", "turnover", "average_earnings", "log_earnings", "new_hire_earnings",
            "log_new_hire_earnings", "job_destruction_qwi", "job_destruction_rate_qwi", "job_creation_rate_qwi"]
    ind_keep = ["county_fips", "yq", "industry", "Emp", "EmpEnd", "EmpS", "Sep", "SepBeg", "HirA", "HirN",
                "FrmJbLs", "Payroll", "EarnS"]
    tots, inds, demos, supps = [], [], [], []
    for f in files:                      # one state at a time (8 GB machine)
        d = pd.read_parquet(f)
        supps.append(pd.Series(apply_flags(d, VARS)))
        d["county_fips"] = xw.harmonize(d["geography"].str.zfill(5))
        d["yq"] = d["year"].astype(int) * 10 + d["quarter"].astype(int)
        d = outcomes(d)[keep]
        fl = d.select_dtypes("float64").columns
        d[fl] = d[fl].astype("float32")
        tots.append(d[(d.industry == "00") & (d.sex == "0") & (d.agegrp == "A00")].drop(columns=["industry", "sex", "agegrp"]))
        inds.append(d.loc[(d.industry != "00") & (d.sex == "0") & (d.agegrp == "A00"), ind_keep])
        demos.append(d[(d.industry == "00") & ~((d.sex == "0") & (d.agegrp == "A00"))])
        del d
    supp = pd.concat(supps, axis=1).mean(axis=1).to_dict()
    tot = pd.concat(tots, ignore_index=True)
    dup = tot.duplicated(["county_fips", "yq"]).sum()
    log.info("county-quarter duplicate keys: %d (multi-state border recodes; first kept)", dup)
    tot = tot.drop_duplicates(["county_fips", "yq"])
    tot.to_parquet(INTER / "qwi_county_quarter.parquet", index=False)
    log_frame(log, tot, "qwi county-quarter")

    ind = pd.concat(inds, ignore_index=True)
    del inds
    ind["industry_group"] = ind["industry"].map(SECTOR_GROUP).fillna("Other/Unassigned")
    ind.to_parquet(INTER / "qwi_county_industry_quarter.parquet", index=False)
    log_frame(log, ind, "qwi county-industry")
    del ind

    demo = pd.concat(demos, ignore_index=True)
    del demos
    demo["demo_family"] = np.where(demo.sex != "0", "sex", "age")
    demo["demo_group"] = np.where(demo.sex != "0", "sex" + demo.sex, demo.agegrp)
    demo = demo.drop(columns=["industry", "sex", "agegrp"])
    api = RAW / "qwi" / "qwi_api_cells.parquet"
    if api.exists():
        a = pd.read_parquet(api)
        apply_flags(a, ["Emp", "EmpEnd", "Sep", "EarnS"])
        for v in ["Emp", "EmpEnd", "Sep", "HirA", "HirN", "EarnS", "EarnHirNS", "FrmJbLs"]:
            a[v] = pd.to_numeric(a[v], errors="coerce")
        a["county_fips"] = xw.harmonize(a["state"] + a["county"])
        a["year"] = a["time"].str[:4].astype(int)
        a["quarter"] = a["time"].str[-1].astype(int)
        a["yq"] = a["year"] * 10 + a["quarter"]
        a["demo_family"] = a["family"]
        a["demo_group"] = np.select(
            [a.family == "education", a.family == "race", a.family == "ethnicity", a.family == "firmsize"],
            ["edu_" + a.get("education", pd.Series("", index=a.index)).fillna(""),
             "race_" + a.get("race", pd.Series("", index=a.index)).fillna(""),
             "eth_" + a.get("ethnicity", pd.Series("", index=a.index)).fillna(""),
             "fsize_" + a.get("firmsize", pd.Series("", index=a.index)).fillna("")], "")
        a["SepBeg"] = np.nan
        a["TurnOvrS"] = np.nan
        a = outcomes(a)
        demo = pd.concat([demo, a[[c for c in demo.columns if c in a.columns]]], ignore_index=True)
    else:
        log.warning("QWI API cells not found -> education/race/ethnicity/firmsize cells unavailable")
    demo.to_parquet(INTER / "qwi_county_demo_quarter.parquet", index=False)
    log_frame(log, demo, "qwi demo")
    pd.Series(supp, name="suppressed_share_all_cells").to_csv(DIAG / "qwi_suppression.csv")
    tsupp = tot[["EmpEnd", "Sep", "EarnS", "HirA", "EarnHirNS", "FrmJbLs"]].isna().mean()
    tsupp.rename("missing_share_county_total").to_csv(DIAG / "qwi_county_total_missing.csv")
    log.info("county-total missing shares: %s", tsupp.round(3).to_dict())


if __name__ == "__main__":
    main()
