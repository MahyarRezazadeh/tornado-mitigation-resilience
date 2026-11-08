"""BLS QCEW county x quarter x industry via BLS open-data CSV slices (no key).

Open-data slices exist for 2014+ only (pre-2014 requires ~0.5GB/yr bulk files; not retained).
Each industry slice covers all areas; county rows (agglvl 70-78 range) kept, private ownership
(own_code 5) for industries plus total covered (own_code 0) for industry 10.
"""
from __future__ import annotations

import io
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import requests

from utils import RAW, get_logger, register_source

log = get_logger(__file__)
URL = "https://data.bls.gov/cew/data/api/{y}/{q}/industry/{ind}.csv"
INDUSTRIES = {"10": "Total", "23": "Construction", "31_33": "Manufacturing", "44_45": "Retail",
              "48_49": "Transportation/Warehousing", "51": "Information", "52": "Finance",
              "54": "Professional Services", "61": "Education", "62": "Health",
              "1026": "Leisure/Hospitality", "81": "Other Services"}
OUT = RAW / "qcew"
KEEP = ["area_fips", "own_code", "industry_code", "agglvl_code", "year", "qtr", "disclosure_code",
        "qtrly_estabs", "month1_emplvl", "month2_emplvl", "month3_emplvl", "total_qtrly_wages", "avg_wkly_wage"]


def get(y: int, q: int, ind: str) -> pd.DataFrame | None:
    dest = OUT / "slices" / f"{y}_{q}_{ind}.parquet"
    if dest.exists():
        return pd.read_parquet(dest)
    r = requests.get(URL.format(y=y, q=q, ind=ind), timeout=300, headers={"User-Agent": "research"})
    if r.status_code != 200:
        return None
    d = pd.read_csv(io.StringIO(r.text), dtype={"area_fips": str, "own_code": str, "industry_code": str,
                                                "agglvl_code": str, "disclosure_code": str})
    d = d[d.area_fips.str.match(r"^\d{5}$") & ~d.area_fips.str.endswith("000")]
    d = d[(d.own_code == "5") | ((d.own_code == "0") & (ind == "10"))][[c for c in KEEP if c in d]]
    dest.parent.mkdir(parents=True, exist_ok=True)
    d.to_parquet(dest, index=False)
    return d


def main() -> None:
    jobs = [(y, q, i) for y in range(2014, 2026) for q in range(1, 5) for i in INDUSTRIES]
    with ThreadPoolExecutor(max_workers=6) as ex:
        res = list(ex.map(lambda a: get(*a), jobs))
    ok = [r for r in res if r is not None]
    log.info("slices retrieved: %d of %d", len(ok), len(jobs))
    df = pd.concat(ok, ignore_index=True)
    df["industry_name"] = df.industry_code.str.replace("-", "_").map(INDUSTRIES)
    df.to_parquet(OUT / "qcew_county_quarter_industry.parquet", index=False)
    log.info("QCEW rows %d, years %s-%s", len(df), df.year.min(), df.year.max())
    register_source(dataset="qcew", source_name="BLS Quarterly Census of Employment and Wages (open data slices)",
                    official_URL="https://www.bls.gov/cew/", download_URL=URL, API_endpoint=URL,
                    coverage_start="2014", coverage_end=str(df.year.max()),
                    notes="county x quarter x 12 industry groups; private ownership (own 5) + total covered (own 0)")


if __name__ == "__main__":
    main()
