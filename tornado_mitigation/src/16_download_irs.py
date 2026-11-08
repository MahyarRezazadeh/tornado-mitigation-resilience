"""IRS SOI county-to-county migration (inflow/outflow CSV files, 2011-12 onward; no key).

Pre-2011 files are per-state Excel/DAT in changing layouts; not used (documented limitation).
Totals rows (y1/y2_statefips 96 = 'Total Migration-US and Foreign') avoid double counting pairs.
"""
from __future__ import annotations

from utils import RAW, cached_get, get_logger, register_source

log = get_logger(__file__)
URL = "https://www.irs.gov/pub/irs-soi/county{d}{a}{b}.csv"


def main() -> None:
    got = []
    for y in range(2011, 2024):
        a, b = str(y)[2:], str(y + 1)[2:]
        for d in ["inflow", "outflow"]:
            try:
                cached_get(URL.format(d=d, a=a, b=b), RAW / "irs" / f"county{d}{a}{b}.csv", log)
                got.append(f"{d}{a}{b}")
            except Exception as e:  # noqa: BLE001
                log.warning("IRS %s %s%s unavailable: %s", d, a, b, e)
    register_source(dataset="irs_migration", source_name="IRS SOI U.S. Population Migration Data (county)",
                    official_URL="https://www.irs.gov/statistics/soi-tax-stats-migration-data",
                    download_URL=URL, coverage_start="2011-2012", coverage_end=got[-1] if got else "",
                    notes="filing-year pairs; files: " + ",".join(got))


if __name__ == "__main__":
    main()
