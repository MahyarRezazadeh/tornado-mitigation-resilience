"""Download OpenFEMA Hazard Mitigation Assistance datasets (paged JSON API, cached).

Datasets:
  - HazardMitigationAssistanceProjects (v4): project-level treatment source
  - HmaSubapplications (v2): titles, hazards, activities, selection status (FEMA GO era)
  - HazardMitigationAssistanceProjectsFinancialTransactions (v1): payment dates (completion proxy)
Field metadata (DataSetFields) is saved alongside so field names are never hard-coded blindly.
"""
from __future__ import annotations

import json

import pandas as pd
import requests

from utils import RAW, cached_get, get_logger, log_frame, register_source

log = get_logger(__file__)
BASE = "https://www.fema.gov/api/open"
DATASETS = [
    ("v4", "HazardMitigationAssistanceProjects", "fema_projects_raw"),
    ("v2", "HmaSubapplications", "fema_subapplications_raw"),
    ("v1", "HazardMitigationAssistanceProjectsFinancialTransactions", "fema_fin_transactions_raw"),
]
PAGE = 10000
OUTDIR = RAW / "fema"


def fetch_metadata(name: str, version: str) -> pd.DataFrame:
    ver = int(version.lstrip("v"))
    url = f"{BASE}/v1/DataSetFields"
    r = requests.get(url, params={"$filter": f"openFemaDataSet eq '{name}' and datasetVersion eq {ver}",
                                  "$top": 500}, timeout=120)
    r.raise_for_status()
    meta = pd.DataFrame(r.json()["DataSetFields"])
    meta.to_csv(OUTDIR / f"metadata_{name}_v{ver}.csv", index=False)
    log.info("metadata %s: %d fields", name, len(meta))
    return meta


def fetch_dataset(version: str, name: str, stem: str) -> pd.DataFrame:
    out = OUTDIR / f"{stem}.parquet"
    if out.exists():
        log.info("cache hit %s", out.name)
        return pd.read_parquet(out)
    url = f"{BASE}/{version}/{name}"
    first = requests.get(url, params={"$top": 1, "$inlinecount": "allpages"}, timeout=120).json()
    total = first["metadata"]["count"]
    log.info("%s: %d records reported by API", name, total)
    frames = []
    for skip in range(0, total, PAGE):
        dest = OUTDIR / "pages" / f"{stem}_{skip:07d}.json"
        cached_get(url, dest, log, params={"$top": PAGE, "$skip": skip})
        frames.append(pd.DataFrame(json.loads(dest.read_text(encoding="utf-8"))[name]))
    df = pd.concat(frames, ignore_index=True)
    if "id" in df:
        dup = df["id"].duplicated().sum()
        log.info("%s duplicate ids: %d (dropped)", name, dup)
        df = df.drop_duplicates("id")
    if len(df) != total:
        log.warning("%s retrieved %d of %d reported", name, len(df), total)
    df.to_parquet(out, index=False)
    log_frame(log, df, name)
    register_source(dataset=stem, source_name=f"OpenFEMA {name} {version}",
                    official_URL=f"https://www.fema.gov/openfema-data-page/{name.lower()}-{version}",
                    download_URL=url, API_endpoint=url,
                    coverage_start="", coverage_end="",
                    notes=f"{len(df)} records; paged $top={PAGE}")
    return df


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    for version, name, stem in DATASETS:
        try:
            fetch_metadata(name, version)
            fetch_dataset(version, name, stem)
        except Exception as e:  # noqa: BLE001  keep going if one endpoint fails
            log.error("FAILED %s: %s", name, e)
    log.info("done")


if __name__ == "__main__":
    main()
