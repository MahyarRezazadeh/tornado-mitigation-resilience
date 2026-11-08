"""Clean NOAA Storm Events tornado records (county segments).

- dates from YEAR/BEGIN_YEARMONTH/BEGIN_DAY (BEGIN_DATE_TIME uses 2-digit years -> ambiguous)
- damage strings with K/M/B suffixes -> dollars
- F/EF scale -> 0..5, unknown (EFU / blank) kept as NaN with flag
- county FIPS harmonized via crosswalk rules; invalid codes logged

Output: data/intermediate/tornadoes_clean.parquet, output/diagnostics/tornado_validation.csv
"""
from __future__ import annotations

import importlib

import numpy as np
import pandas as pd

from utils import DIAG, INTER, RAW, XWALK, get_logger, log_frame

log = get_logger(__file__)
xw = importlib.import_module("22_build_county_crosswalk")
MULT = {"": 1, "H": 1e2, "K": 1e3, "M": 1e6, "B": 1e9, "T": 1e12}


def parse_damage(s: pd.Series) -> pd.Series:
    s = s.fillna("").astype(str).str.strip().str.upper()
    m = s.str.extract(r"^([0-9]*\.?[0-9]*)\s*([HKMBT]?)$")
    num = pd.to_numeric(m[0].replace("", np.nan), errors="coerce")
    # bare suffix like "K" means 1 unit of that suffix in NCEI convention? treat as missing
    out = num * m[1].map(MULT).fillna(1)
    return out.where(s != "", np.nan)


def parse_scale(s: pd.Series) -> pd.Series:
    d = s.fillna("").str.upper().str.extract(r"E?F([0-5])")[0]
    return pd.to_numeric(d, errors="coerce")


def main() -> None:
    t = pd.read_parquet(RAW / "noaa" / "storm_events_tornado_raw.parquet")
    log_frame(log, t, "tornado raw")
    checks = [("raw rows", len(t)), ("duplicate EVENT_ID", int(t["EVENT_ID"].duplicated().sum()))]
    t = t.drop_duplicates("EVENT_ID")

    ym = t["BEGIN_YEARMONTH"].astype(str)
    t["date"] = pd.to_datetime(ym + t["BEGIN_DAY"].astype(str).str.zfill(2), format="%Y%m%d", errors="coerce")
    checks.append(("invalid dates", int(t["date"].isna().sum())))
    t["year"] = t["date"].dt.year
    t["quarter"] = t["date"].dt.quarter
    t["yq"] = t["year"] * 10 + t["quarter"]

    t["damage_property"] = parse_damage(t["DAMAGE_PROPERTY"])
    t["damage_crops"] = parse_damage(t["DAMAGE_CROPS"])
    checks.append(("unparseable property damage (non-blank)",
                   int((t["damage_property"].isna() & t["DAMAGE_PROPERTY"].fillna("").str.strip().ne("")).sum())))

    t["ef"] = parse_scale(t["TOR_F_SCALE"])
    t["ef_unknown"] = t["ef"].isna()
    t["scale_system"] = np.where(t["TOR_F_SCALE"].fillna("").str.upper().str.startswith("EF"), "EF", "F")
    checks.append(("unknown intensity (EFU/blank)", int(t["ef_unknown"].sum())))
    checks.append(("unparsed scale strings", int((t["ef_unknown"] & ~t["TOR_F_SCALE"].fillna("").str.upper()
                                                  .isin(["", "EFU", "FU", "EF-U"])).sum())))

    for c in ["INJURIES_DIRECT", "INJURIES_INDIRECT", "DEATHS_DIRECT", "DEATHS_INDIRECT",
              "BEGIN_LAT", "BEGIN_LON", "END_LAT", "END_LON", "TOR_LENGTH", "TOR_WIDTH"]:
        t[c] = pd.to_numeric(t[c], errors="coerce")
    t["injuries"] = t[["INJURIES_DIRECT", "INJURIES_INDIRECT"]].sum(axis=1, min_count=1)
    t["fatalities"] = t[["DEATHS_DIRECT", "DEATHS_INDIRECT"]].sum(axis=1, min_count=1)

    t["county_fips_raw"] = t["STATE_FIPS"].astype(str).str.zfill(2) + t["CZ_FIPS"].astype(str).str.zfill(3)
    t["county_fips"] = xw.harmonize(t["county_fips_raw"])
    valid = set(pd.read_parquet(XWALK / "counties_2020.parquet")["county_fips"])
    t["state_fips"] = t["county_fips"].str[:2]
    t["in_contig"] = t["county_fips"].isin(valid)
    checks.append(("CZ_TYPE != C", int((t["CZ_TYPE"] != "C").sum())))
    checks.append(("recoded via crosswalk", int((t["county_fips"] != t["county_fips_raw"]).sum())))
    bad = t[~t["in_contig"] & ~t["STATE_FIPS"].astype(str).str.zfill(2).isin(["02", "15", "72", "78", "66", "60", "99"])]
    checks.append(("contiguous-state rows with invalid county FIPS", len(bad)))
    bad["county_fips_raw"].value_counts().head(50).to_csv(DIAG / "tornado_invalid_fips.csv")

    pd.DataFrame(checks, columns=["check", "count"]).to_csv(DIAG / "tornado_validation.csv", index=False)
    for k, v in checks:
        log.info("validation: %s = %s", k, v)
    keep = ["EVENT_ID", "EPISODE_ID", "date", "year", "quarter", "yq", "county_fips", "state_fips", "in_contig",
            "CZ_NAME", "STATE", "ef", "ef_unknown", "scale_system", "injuries", "fatalities",
            "damage_property", "damage_crops", "BEGIN_LAT", "BEGIN_LON", "END_LAT", "END_LON",
            "TOR_LENGTH", "TOR_WIDTH", "TOR_OTHER_CZ_STATE", "TOR_OTHER_CZ_FIPS"]
    out = t[t["in_contig"]][keep]
    out.to_parquet(INTER / "tornadoes_clean.parquet", index=False)
    log_frame(log, out, "tornado clean (contiguous)")
    log.info("EF distribution: %s", out["ef"].value_counts(dropna=False).sort_index().to_dict())


if __name__ == "__main__":
    main()
