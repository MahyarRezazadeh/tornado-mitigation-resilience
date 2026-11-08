"""CBP county(-industry)-year panel. Suppressed employment (flagged ranges) -> missing.

Small establishment share = establishments with <20 employees / total establishments.
2017+ files use 'n<5' + 'n5_9' instead of 'n1_4'. Employment/payroll noise flags kept.
Outputs: data/intermediate/cbp_county_year.parquet, cbp_county_industry_year.parquet
"""
from __future__ import annotations

import importlib

import numpy as np
import pandas as pd

from utils import INTER, RAW, get_logger, log_frame

log = get_logger(__file__)
xw = importlib.import_module("22_build_county_crosswalk")
SECTOR_GROUP = {"23": "Construction", "31": "Manufacturing", "44": "Retail", "48": "Transportation/Warehousing",
                "51": "Information", "52": "Finance", "54": "Professional Services", "61": "Education",
                "62": "Health", "71": "Leisure/Hospitality", "72": "Leisure/Hospitality", "81": "Other Services"}


def main() -> None:
    d = pd.read_parquet(RAW / "cbp" / "cbp_county_raw.parquet")
    for c in d.columns:
        if c not in ["fipstate", "fipscty", "naics", "empflag", "emp_nf", "ap_nf", "year"]:
            d[c] = pd.to_numeric(d[c], errors="coerce")
    d["county_fips"] = xw.harmonize(d["fipstate"].str.zfill(2) + d["fipscty"].str.zfill(3))
    d = d[~d.fipscty.isin(["999"])]
    supp = d["empflag"].notna() & d["empflag"].str.strip().ne("")
    d.loc[supp, "emp"] = np.nan
    d.loc[supp, "ap"] = np.nan  # payroll withheld together with employment
    small = d.get("n1_4", pd.Series(np.nan, index=d.index)).fillna(0) + \
        d.get("n<5", pd.Series(np.nan, index=d.index)).fillna(0) + d["n5_9"].fillna(0) + d["n10_19"].fillna(0)
    d["small_estabs"] = small
    d["naics2"] = d["naics"].str.replace(r"[-/]", "", regex=True)
    tot = d[d.naics2 == ""].groupby(["county_fips", "year"], as_index=False)[["est", "emp", "ap", "small_estabs"]] \
        .sum(min_count=1)
    tot = tot.rename(columns={"est": "establishments", "emp": "cbp_employment", "ap": "annual_payroll"})
    tot["log_establishments"] = np.log(tot.establishments.where(tot.establishments > 0))
    tot["log_cbp_employment"] = np.log(tot.cbp_employment.where(tot.cbp_employment > 0))
    tot["log_payroll"] = np.log(tot.annual_payroll.where(tot.annual_payroll > 0))
    tot["small_estab_share"] = tot.small_estabs / tot.establishments
    tot["cbp_emp_suppressed"] = tot.cbp_employment.isna().astype(int)
    tot.to_parquet(INTER / "cbp_county_year.parquet", index=False)
    log_frame(log, tot, "cbp county")
    ind = d[d.naics2.str.len() == 2].copy()
    ind["industry_group"] = ind.naics2.map(SECTOR_GROUP).fillna("Other/Unassigned")
    ind = ind.groupby(["county_fips", "year", "industry_group"], as_index=False)[["est", "emp", "ap", "small_estabs"]] \
        .sum(min_count=1).rename(columns={"est": "establishments", "emp": "cbp_employment", "ap": "annual_payroll"})
    ind["log_establishments"] = np.log(ind.establishments.where(ind.establishments > 0))
    ind.to_parquet(INTER / "cbp_county_industry_year.parquet", index=False)
    log_frame(log, ind, "cbp county-industry")


if __name__ == "__main__":
    main()
