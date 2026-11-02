"""Public finance feasibility probe (Census of Governments / Annual Survey of Local Government Finances).

Probes the official dataset index to record which years have full-census (all local governments)
versus sample-only coverage. A county-area annual panel would require the annual SAMPLE survey
(units change across years) -> not a consistent county panel. Only Census-of-Governments years
(years ending in 2 and 7) cover all units. Result is written to the feasibility registry; no
county panel is manufactured.
Output: data/raw/public_finance/govfin_index_probe.csv
"""
from __future__ import annotations

import re

import pandas as pd
import requests

from utils import RAW, get_logger, register_source

log = get_logger(__file__)
INDEX = "https://www2.census.gov/programs-surveys/gov-finances/datasets/"


def main() -> None:
    out = RAW / "public_finance"
    out.mkdir(parents=True, exist_ok=True)
    try:
        html = requests.get(INDEX, timeout=120).text
        years = sorted({int(y) for y in re.findall(r'href="(\d{4})/"', html)})
    except Exception as e:  # noqa: BLE001
        log.error("index unavailable: %s", e)
        years = []
    rows = []
    for y in years:
        census = y % 5 == 2
        rows.append({"year": y, "census_of_governments_year": census,
                     "coverage": "all local governments" if census else "sample of local governments"})
    df = pd.DataFrame(rows)
    df.to_csv(out / "govfin_index_probe.csv", index=False)
    full = df[df.census_of_governments_year].year.tolist() if len(df) else []
    log.info("finance years listed: %s; full-census years: %s", years, full)
    register_source(dataset="public_finance_probe", source_name="Census Annual Survey of State & Local Gov Finances",
                    official_URL="https://www.census.gov/programs-surveys/gov-finances.html", download_URL=INDEX,
                    coverage_start=str(min(years)) if years else "", coverage_end=str(max(years)) if years else "",
                    notes=f"full-census years only {full}; annual years are samples -> no consistent annual county panel")


if __name__ == "__main__":
    main()
