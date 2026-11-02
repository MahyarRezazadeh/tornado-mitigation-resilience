"""Download NOAA/NCEI Storm Events bulk 'details' CSV files (all years), cached.

Lists the official directory to pick the latest-revision file per year (file names carry a
creation-date stamp that changes with each NCEI revision, so names are never hard-coded).
Tornado rows (and hurricane/flood/other severe-storm county counts used as controls R51-R53)
are extracted to parquet.
"""
from __future__ import annotations

import re

import pandas as pd
import requests

from utils import RAW, cached_get, get_logger, load_config, register_source

log = get_logger(__file__)
BASE = "https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/"
OUT = RAW / "noaa"
KEEP = ["BEGIN_YEARMONTH", "BEGIN_DAY", "BEGIN_TIME", "END_YEARMONTH", "END_DAY", "END_TIME",
        "EPISODE_ID", "EVENT_ID", "STATE", "STATE_FIPS", "YEAR", "MONTH_NAME", "EVENT_TYPE",
        "CZ_TYPE", "CZ_FIPS", "CZ_NAME", "BEGIN_DATE_TIME", "END_DATE_TIME", "CZ_TIMEZONE",
        "INJURIES_DIRECT", "INJURIES_INDIRECT", "DEATHS_DIRECT", "DEATHS_INDIRECT",
        "DAMAGE_PROPERTY", "DAMAGE_CROPS", "TOR_F_SCALE", "TOR_LENGTH", "TOR_WIDTH",
        "TOR_OTHER_WFO", "TOR_OTHER_CZ_STATE", "TOR_OTHER_CZ_FIPS", "TOR_OTHER_CZ_NAME",
        "BEGIN_LAT", "BEGIN_LON", "END_LAT", "END_LON", "MAGNITUDE"]
CONTROL_TYPES = {
    "hurricane": r"Hurricane|Tropical Storm|Tropical Depression|Storm Surge",
    "flood": r"Flood",
    "severe_storm": r"Thunderstorm Wind|Hail|High Wind|Strong Wind",
}


def main() -> None:
    cfg = load_config()["data"]
    html = requests.get(BASE, timeout=120).text
    files = re.findall(r'href="(StormEvents_details-ftp_v1\.0_d(\d{4})_c(\d{8})\.csv\.gz)"', html)
    latest = {}
    for fn, yr, c in files:
        yr = int(yr)
        if cfg["noaa_start_year"] <= yr <= cfg["noaa_end_year"] and (yr not in latest or c > latest[yr][1]):
            latest[yr] = (fn, c)
    log.info("%d yearly detail files found (%s-%s)", len(latest), min(latest), max(latest))

    tor, ctrl = [], []
    for yr in sorted(latest):
        fn = latest[yr][0]
        dest = cached_get(BASE + fn, OUT / fn, log, timeout=600)
        d = pd.read_csv(dest, compression="gzip", usecols=lambda c: c in KEEP, dtype=str, low_memory=False)
        t = d[d["EVENT_TYPE"] == "Tornado"]
        tor.append(t)
        cz = d[d["CZ_TYPE"] == "C"]
        for k, rx in CONTROL_TYPES.items():
            m = cz[cz["EVENT_TYPE"].str.contains(rx, regex=True, na=False)]
            if len(m):
                ctrl.append(m.assign(control_type=k)[["YEAR", "BEGIN_YEARMONTH", "STATE_FIPS", "CZ_FIPS",
                                                      "EVENT_ID", "control_type", "EVENT_TYPE"]])
        log.info("%d: %d rows, %d tornado rows (file %s)", yr, len(d), len(t), fn)
    tor = pd.concat(tor, ignore_index=True)
    tor.to_parquet(OUT / "storm_events_tornado_raw.parquet", index=False)
    pd.concat(ctrl, ignore_index=True).to_parquet(OUT / "storm_events_other_hazards_county.parquet", index=False)
    log.info("tornado rows total: %d", len(tor))
    register_source(dataset="noaa_storm_events", source_name="NOAA NCEI Storm Events Database (details files)",
                    official_URL="https://www.ncdc.noaa.gov/stormevents/", download_URL=BASE, API_endpoint="",
                    coverage_start=str(min(latest)), coverage_end=str(max(latest)),
                    notes="latest c-stamp per year; " + ";".join(f"{y}:{latest[y][1]}" for y in sorted(latest)))


if __name__ == "__main__":
    main()
