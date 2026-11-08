"""Census BPS county annual files -> county-year permits.

Columns: imputed totals (1-unit, 2-units, 3-4, 5+: bldgs, units, value) followed by
reported-only blocks. Coverage flag: reported units / imputed units < 0.9 -> partial coverage.
Output: data/intermediate/bps_county_year.parquet
"""
from __future__ import annotations

import importlib
import re

import numpy as np
import pandas as pd

from utils import INTER, RAW, get_logger, log_frame

log = get_logger(__file__)
xw = importlib.import_module("22_build_county_crosswalk")
NAMES = ["date", "st", "cty", "region", "division", "name"] + \
        [f"{t}_{m}{r}" for r in ["", "_rep"] for t in ["u1", "u2", "u34", "u5"] for m in ["bldgs", "units", "value"]]


def main() -> None:
    rows = []
    for f in sorted((RAW / "building_permits").glob("co*a.txt")):
        y = int(re.findall(r"co(\d{4})a", f.name)[0])
        d = pd.read_csv(f, skiprows=3, header=None, names=NAMES, dtype=str, skipinitialspace=True)
        d = d[d["st"].notna() & d["cty"].notna()]
        for c in NAMES[6:]:
            d[c] = pd.to_numeric(d[c].astype(str).str.strip(), errors="coerce")
        d["county_fips"] = d["st"].str.strip().str.zfill(2) + d["cty"].str.strip().str.zfill(3)
        d["year"] = y
        rows.append(d)
    df = pd.concat(rows, ignore_index=True)
    df = df[df.county_fips.str.fullmatch(r"\d{5}")]
    df["county_fips"] = xw.harmonize(df["county_fips"])
    num = [c for c in NAMES[6:]]
    df = df.groupby(["county_fips", "year"], as_index=False)[num].sum(min_count=1)
    df["total_units"] = df[["u1_units", "u2_units", "u34_units", "u5_units"]].sum(axis=1)
    df["total_permits"] = df[["u1_bldgs", "u2_bldgs", "u34_bldgs", "u5_bldgs"]].sum(axis=1)
    df["single_family_units"] = df["u1_units"]
    df["units_2_4"] = df["u2_units"] + df["u34_units"]
    df["units_5plus"] = df["u5_units"]
    df["permit_value"] = df[["u1_value", "u2_value", "u34_value", "u5_value"]].sum(axis=1)
    rep = df[["u1_units_rep", "u2_units_rep", "u34_units_rep", "u5_units_rep"]].sum(axis=1)
    df["reported_share"] = np.where(df["total_units"] > 0, rep / df["total_units"], np.nan)
    df["partial_coverage"] = (df["reported_share"] < 0.9).astype(int)
    df["ihs_units"] = np.arcsinh(df["total_units"])
    df["ihs_sf_units"] = np.arcsinh(df["single_family_units"])
    df["ihs_mf_units"] = np.arcsinh(df["units_2_4"] + df["units_5plus"])
    df = df[["county_fips", "year", "total_units", "total_permits", "single_family_units", "units_2_4",
             "units_5plus", "permit_value", "reported_share", "partial_coverage", "ihs_units", "ihs_sf_units",
             "ihs_mf_units"]]
    df.to_parquet(INTER / "bps_county_year.parquet", index=False)
    log_frame(log, df, "bps")
    log.info("partial coverage share: %.3f", df.partial_coverage.mean())


if __name__ == "__main__":
    main()
