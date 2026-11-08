"""Download Census Business Dynamics Statistics county tables (bulk CSV, no key needed)."""
from __future__ import annotations

import re

import requests

from utils import RAW, cached_get, get_logger, register_source

log = get_logger(__file__)
INDEX = "https://www2.census.gov/programs-surveys/bds/tables/time-series/"
TABLES = ["st_cty", "st_cty_fzc", "st_cty_fac", "st_cty_sec"]


def latest_release() -> int:
    html = requests.get(INDEX, timeout=120).text
    return max(int(y) for y in re.findall(r'href="(\d{4})/"', html))


def main() -> None:
    rel = latest_release()
    for t in TABLES:
        url = f"{INDEX}{rel}/bds{rel}_{t}.csv"
        cached_get(url, RAW / "bds" / f"bds{rel}_{t}.csv", log, timeout=900)
    register_source(dataset="bds", source_name=f"Census Business Dynamics Statistics {rel} release",
                    official_URL="https://www.census.gov/programs-surveys/bds.html",
                    download_URL=f"{INDEX}{rel}/", coverage_start="1978", coverage_end=str(rel),
                    notes="county total, county x firm size (fzc), firm age (fac), sector")
    (RAW / "bds" / "release.txt").write_text(str(rel))
    log.info("BDS release %s downloaded", rel)


if __name__ == "__main__":
    main()
