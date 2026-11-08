"""REDESIGN (2026-10-09) downloads: SPC tornado tracks, BEA county GDP/farm income, NASS county crop yields.

  data/raw/spc/1950-2024_actual_tornadoes.csv     SPC WCM tornado database (track start/end, length, width)
  data/raw/bea/CAGDP9.zip, CAINC45.zip            county real GDP (chained 2017$) and farm income/receipts
  data/raw/nass/nass_county_yields.parquet        stream-filtered NASS QuickStats crops bulk file:
                                                  county-level SURVEY yields + harvested area, major field crops
"""
from __future__ import annotations

import gzip
import io

import pandas as pd
import requests

from utils import RAW, get_logger

log = get_logger(__file__)

SPC = "https://www.spc.noaa.gov/wcm/data/1950-2024_actual_tornadoes.csv"
BEA = ["https://apps.bea.gov/regional/zip/CAGDP9.zip", "https://apps.bea.gov/regional/zip/CAINC45.zip"]
NASS = "https://www.nass.usda.gov/datasets/qs.crops_20261009.txt.gz"
SERIES = {f"{c} - {s}" for c in ["CORN, GRAIN", "SOYBEANS", "WHEAT"]
          for s in ["PRODUCTION, MEASURED IN BU", "ACRES HARVESTED", "YIELD, MEASURED IN BU / ACRE"]}


def fetch(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        log.info("cached %s", dest.name)
        return
    with requests.get(url, stream=True, timeout=300) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for ch in r.iter_content(1 << 20):
                f.write(ch)
    log.info("downloaded %s (%.1f MB)", dest.name, dest.stat().st_size / 1e6)


def nass_filter():
    out = RAW / "nass" / "nass_county_yields.parquet"
    if out.exists():
        log.info("cached %s", out.name)
        return
    gz = RAW / "nass" / "qs.crops.txt.gz"
    fetch(NASS, gz)
    keep = []
    with gzip.open(gz, "rt", encoding="utf-8", errors="replace") as fh:
        for i, chunk in enumerate(pd.read_csv(fh, sep="\t", dtype=str, chunksize=500_000)):
            c = chunk[(chunk.AGG_LEVEL_DESC == "COUNTY") & (chunk.SOURCE_DESC == "SURVEY")
                      & (chunk.FREQ_DESC == "ANNUAL") & (chunk.REFERENCE_PERIOD_DESC == "YEAR")
                      & chunk.SHORT_DESC.isin(SERIES) & (chunk.DOMAIN_DESC == "TOTAL")]
            if len(c):
                keep.append(c[["COMMODITY_DESC", "SHORT_DESC", "STATISTICCAT_DESC", "UNIT_DESC", "STATE_FIPS_CODE",
                               "COUNTY_CODE", "COUNTY_NAME", "YEAR", "VALUE"]])
            if i % 10 == 0:
                log.info("nass chunk %d, kept %d", i, sum(map(len, keep)))
    d = pd.concat(keep, ignore_index=True)
    d.to_parquet(out, index=False)
    log.info("nass county rows %d", len(d))
    gz.unlink()


def main():
    fetch(SPC, RAW / "spc" / "1950-2024_actual_tornadoes.csv")
    for u in BEA:
        fetch(u, RAW / "bea" / u.rsplit("/", 1)[1])
    nass_filter()
    _ = io


if __name__ == "__main__":
    main()
