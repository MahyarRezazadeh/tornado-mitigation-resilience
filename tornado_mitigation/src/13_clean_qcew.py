"""QCEW county x quarter x industry group (private ownership, own_code 5).

Employment = mean of the three monthly employment levels; disclosure code 'N' -> missing.
Output: data/intermediate/qcew_county_quarter.parquet (industry_group 'Total' = industry 10 private)
"""
from __future__ import annotations

import importlib

import numpy as np
import pandas as pd

from utils import INTER, RAW, get_logger, log_frame

log = get_logger(__file__)
xw = importlib.import_module("22_build_county_crosswalk")


def main() -> None:
    p = RAW / "qcew" / "qcew_county_quarter_industry.parquet"
    if not p.exists():
        log.warning("QCEW not downloaded; skipping")
        return
    d = pd.read_parquet(p)
    d = d[d.own_code == "5"].copy()
    nd = d.disclosure_code.fillna("").str.strip().eq("N")
    for c in ["qtrly_estabs", "month1_emplvl", "month2_emplvl", "month3_emplvl", "total_qtrly_wages", "avg_wkly_wage"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
        d.loc[nd, c] = np.nan
    d["qcew_emp"] = d[["month1_emplvl", "month2_emplvl", "month3_emplvl"]].mean(axis=1)
    d["qcew_emp_m3"] = d["month3_emplvl"]
    d["industry_group"] = np.where(d.industry_code == "10", "Total", d.industry_name)
    d["county_fips"] = xw.harmonize(d.area_fips)
    d["yq"] = d.year.astype(int) * 10 + d.qtr.astype(int)
    g = d.groupby(["county_fips", "yq", "industry_group"], as_index=False).agg(
        qcew_emp=("qcew_emp", "sum"), qcew_emp_m3=("qcew_emp_m3", "sum"), qcew_wages=("total_qtrly_wages", "sum"),
        qcew_estabs=("qtrly_estabs", "sum"), qcew_avg_wkly_wage=("avg_wkly_wage", "mean"),
        qcew_nondisclosed=("qcew_emp", lambda s: s.isna().all()))
    for c in ["qcew_emp", "qcew_emp_m3", "qcew_wages", "qcew_estabs"]:
        g.loc[g.qcew_nondisclosed, c] = np.nan
    g["log_qcew_emp"] = np.log(g.qcew_emp_m3.where(g.qcew_emp_m3 > 0))
    g["log_qcew_wkly_wage"] = np.log(g.qcew_avg_wkly_wage.where(g.qcew_avg_wkly_wage > 0))
    g["log_qcew_estabs"] = np.log(g.qcew_estabs.where(g.qcew_estabs > 0))
    g = g.drop(columns="qcew_nondisclosed")
    g.to_parquet(INTER / "qcew_county_quarter.parquet", index=False)
    log_frame(log, g, "qcew")


if __name__ == "__main__":
    main()
