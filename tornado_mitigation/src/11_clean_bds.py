"""Clean BDS county tables. Suppressed markers (D, S, X, N) -> missing, never zero.

Official BDS rates use denom = average of employment in t and t-1 (DHS denominator).
Establishment entry/exit rates are relative to the average establishment count (official columns kept).
BDS year t refers to activity between March 12 of t-1 and March 12 of t.

Outputs: data/intermediate/bds_county_year.parquet, bds_county_year_fsize.parquet,
         bds_county_year_fage.parquet, bds_county_year_sector.parquet
"""
from __future__ import annotations

import importlib

import numpy as np
import pandas as pd

from utils import DIAG, INTER, RAW, get_logger, log_frame

log = get_logger(__file__)
xw = importlib.import_module("22_build_county_crosswalk")
NUM = ["firms", "estabs", "emp", "denom", "estabs_entry", "estabs_entry_rate", "estabs_exit", "estabs_exit_rate",
       "job_creation", "job_creation_births", "job_creation_rate", "job_destruction", "job_destruction_deaths",
       "job_destruction_continuers", "job_destruction_rate_deaths", "job_destruction_rate", "net_job_creation",
       "net_job_creation_rate", "reallocation_rate", "firmdeath_firms", "firmdeath_estabs", "firmdeath_emp"]


def clean(t: str, extra: list[str]) -> pd.DataFrame:
    rel = (RAW / "bds" / "release.txt").read_text().strip()
    d = pd.read_csv(RAW / "bds" / f"bds{rel}_{t}.csv", dtype=str)
    supp = {}
    for c in NUM:
        if c in d:
            s = d[c].str.strip()
            supp[c] = (~s.str.match(r"^-?[0-9.]+$", na=False)).mean()
            d[c] = pd.to_numeric(s, errors="coerce")
    d["county_fips"] = xw.harmonize(d["st"].str.zfill(2) + d["cty"].str.zfill(3))
    d["year"] = d["year"].astype(int)
    d = d.rename(columns={"estabs_entry": "estab_births", "estabs_exit": "estab_deaths",
                          "estabs_entry_rate": "establishment_birth_rate", "estabs_exit_rate": "establishment_death_rate"})
    keys = ["county_fips", "year"] + extra
    dup = d.duplicated(keys).sum()
    if dup:
        log.warning("%s: %d duplicate keys after harmonization (recoded counties) -> summed counts", t, dup)
        cnt = [c for c in d.columns if c in ["firms", "estabs", "emp", "denom", "estab_births", "estab_deaths",
                                              "job_creation", "job_creation_births", "job_destruction",
                                              "job_destruction_deaths", "net_job_creation", "firmdeath_firms",
                                              "firmdeath_estabs", "firmdeath_emp"]]
        d = d.groupby(keys, as_index=False)[cnt].sum(min_count=1)
        d["establishment_birth_rate"] = np.nan
        d["establishment_death_rate"] = np.nan
    pd.Series(supp, name="suppressed_share").to_csv(DIAG / f"bds_{t}_suppression.csv")
    log.info("%s suppression shares: %s", t, {k: round(v, 3) for k, v in supp.items() if v > 0})
    return d


def main() -> None:
    base = clean("st_cty", [])
    base["job_destruction_rate_calc"] = 100 * base["job_destruction"] / base["denom"]
    base["job_creation_rate_calc"] = 100 * base["job_creation"] / base["denom"]
    base["estab_death_share"] = 100 * base["estab_deaths"] / base["estabs"]
    log.info("max |official - calc| JD rate: %.3f",
             (base["job_destruction_rate"] - base["job_destruction_rate_calc"]).abs().max())
    base.to_parquet(INTER / "bds_county_year.parquet", index=False)
    log_frame(log, base, "bds county")
    clean("st_cty_fzc", ["fsizecoarse"]).to_parquet(INTER / "bds_county_year_fsize.parquet", index=False)
    clean("st_cty_fac", ["fagecoarse"]).to_parquet(INTER / "bds_county_year_fage.parquet", index=False)
    clean("st_cty_sec", ["sector"]).to_parquet(INTER / "bds_county_year_sector.parquet", index=False)


if __name__ == "__main__":
    main()
