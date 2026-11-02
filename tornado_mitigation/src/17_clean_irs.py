"""IRS county migration -> county-year inflow/outflow/net measures.

Uses the official aggregate rows (code 96 = Total Migration-US and Foreign) for each county,
so county-to-county pairs are never summed (no double counting). Non-migrant row gives stayers.
Year label = second filing year of the pair (file 1920 -> year 2020): moves between ~spring 2019
and ~spring 2020 filings. Suppressed values (-1) -> missing.
n1 = returns (households), n2 = exemptions/individuals (persons), agi in $1000.
Output: data/intermediate/irs_county_year.parquet
"""
from __future__ import annotations

import importlib
import re

import numpy as np
import pandas as pd

from utils import INTER, RAW, get_logger, log_frame

log = get_logger(__file__)
xw = importlib.import_module("22_build_county_crosswalk")


def read(path, own_st, own_ct, oth_st):
    d = pd.read_csv(path, dtype=str, encoding="latin-1")
    d.columns = [c.lower() for c in d.columns]
    for c in ["n1", "n2", "agi"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
        d.loc[d[c] < 0, c] = np.nan
    d["county_fips"] = d[own_st].str.zfill(2) + d[own_ct].str.zfill(3)
    tot = d[(d[oth_st] == "96")].set_index("county_fips")[["n1", "n2", "agi"]]
    non = d[d["y1_countyname" if "y1_countyname" in d else "y2_countyname"].str.contains("Non-migrants", na=False)] \
        .set_index("county_fips")[["n1", "n2", "agi"]]
    return tot, non


def main() -> None:
    rows = []
    for f in sorted((RAW / "irs").glob("countyinflow*.csv")):
        a, b = re.findall(r"(\d\d)(\d\d)\.csv", f.name)[0]
        year = 2000 + int(b)
        inn, non = read(f, "y2_statefips", "y2_countyfips", "y1_statefips")
        of = RAW / "irs" / f.name.replace("inflow", "outflow")
        out, _ = read(of, "y1_statefips", "y1_countyfips", "y2_statefips")
        d = pd.DataFrame({"inflow_returns": inn.n1, "inflow_exemptions": inn.n2, "inflow_AGI": inn.agi})
        d = d.join(pd.DataFrame({"outflow_returns": out.n1, "outflow_exemptions": out.n2, "outflow_AGI": out.agi}),
                   how="outer")
        d = d.join(pd.DataFrame({"nonmig_returns": non.n1, "nonmig_exemptions": non.n2, "nonmig_AGI": non.agi}),
                   how="left")
        d["year"] = year
        rows.append(d.reset_index())
    df = pd.concat(rows, ignore_index=True)
    df = df[~df.county_fips.str.endswith("000")]
    df["county_fips"] = xw.harmonize(df["county_fips"])
    df = df.groupby(["county_fips", "year"], as_index=False).sum(min_count=1)
    base_people = df["nonmig_exemptions"] + df["outflow_exemptions"]
    df["net_migration_people"] = df["inflow_exemptions"] - df["outflow_exemptions"]
    df["net_migration_returns"] = df["inflow_returns"] - df["outflow_returns"]
    df["net_AGI_migration"] = df["inflow_AGI"] - df["outflow_AGI"]
    df["outmigration_rate"] = 100 * df["outflow_exemptions"] / base_people
    df["inmigration_rate"] = 100 * df["inflow_exemptions"] / base_people
    df["net_migration_rate"] = 100 * df["net_migration_people"] / base_people
    df["mean_AGI_outmigrant"] = df["outflow_AGI"] / df["outflow_returns"]
    df["mean_AGI_inmigrant"] = df["inflow_AGI"] / df["inflow_returns"]
    df["log_outflow_AGI"] = np.log(df["outflow_AGI"].where(df["outflow_AGI"] > 0))
    df.to_parquet(INTER / "irs_county_year.parquet", index=False)
    log_frame(log, df, "irs county-year")
    log.info("years: %s", sorted(df.year.unique()))


if __name__ == "__main__":
    main()
