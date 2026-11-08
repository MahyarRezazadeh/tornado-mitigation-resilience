"""QWI demographic / firm-size cells via Census API (requires CENSUS_API_KEY).

County x quarter, all industries, private ownership (A05):
  education E1-E4 (se endpoint), race A1/A2 x ethnicity A0, ethnicity A2 x race A0 (rh endpoint),
  firm size 1-5 (sa endpoint). One call per state x cell family; cached JSON.
"""
from __future__ import annotations

import json
import time

import pandas as pd
import requests

from utils import RAW, XWALK, census_key, get_logger, register_source

log = get_logger(__file__)
API = "https://api.census.gov/data/timeseries/qwi/{ep}"
VARS = "Emp,EmpEnd,Sep,HirA,HirN,EarnS,EarnHirNS,FrmJbLs,sEmp,sEmpEnd,sSep,sEarnS"
FAMILIES = {
    "education": ("se", {"education": ["E1", "E2", "E3", "E4"]}),
    "race": ("rh", {"race": ["A1", "A2"], "ethnicity": "A0"}),
    "ethnicity": ("rh", {"race": "A0", "ethnicity": ["A1", "A2"]}),
    "firmsize": ("sa", {"firmsize": ["1", "2", "3", "4", "5"]}),
}
OUT = RAW / "qwi" / "api_cells"


def fetch(st: str, fam: str, key: str) -> pd.DataFrame:
    dest = OUT / f"{fam}_{st}.json"
    if not dest.exists():
        ep, extra = FAMILIES[fam]
        params = {"get": VARS, "for": "county:*", "in": f"state:{st}", "time": "from 1990-Q1 to 2025-Q4",
                  "ownercode": "A05", "key": key, **extra}
        for attempt in range(4):
            r = requests.get(API.format(ep=ep), params=params, timeout=600)
            if r.status_code == 200:
                dest.write_text(r.text, encoding="utf-8")
                break
            if r.status_code == 204:
                dest.write_text("[]", encoding="utf-8")
                break
            log.warning("%s %s status %s: %s", fam, st, r.status_code, r.text[:200])
            time.sleep(5 * (attempt + 1))
        else:
            raise RuntimeError(f"{fam} {st} failed")
    j = json.loads(dest.read_text(encoding="utf-8"))
    if not j:
        return pd.DataFrame()
    return pd.DataFrame(j[1:], columns=j[0]).assign(family=fam)


def main() -> None:
    key = census_key()
    if not key:
        log.error("CENSUS_API_KEY missing: add it to .env (https://api.census.gov/data/key_signup.html). "
                  "Demographic/firm-size QWI cells skipped; all other analyses continue.")
        return
    OUT.mkdir(parents=True, exist_ok=True)
    states = sorted(pd.read_parquet(XWALK / "counties_2020.parquet")["state_fips"].unique())
    frames = []
    for fam in FAMILIES:
        for st in states:
            try:
                frames.append(fetch(st, fam, key))
            except Exception as e:  # noqa: BLE001
                log.error("FAILED %s %s: %s", fam, st, e)
        log.info("family %s done", fam)
    df = pd.concat(frames, ignore_index=True)
    df.to_parquet(RAW / "qwi" / "qwi_api_cells.parquet", index=False)
    log.info("api cells rows: %d", len(df))
    register_source(dataset="qwi_api_cells", source_name="Census QWI API (se, rh, sa endpoints)",
                    official_URL="https://www.census.gov/data/developers/data-sets/qwi.html",
                    API_endpoint=API.format(ep="{se,rh,sa}"), coverage_start="1990", coverage_end="2025",
                    notes="education E1-E4; race A1/A2; Hispanic; firmsize 1-5; ownercode A05; industry total")


if __name__ == "__main__":
    main()
