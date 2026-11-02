"""Census Building Permits Survey, county annual files (no key)."""
from __future__ import annotations

from utils import RAW, cached_get, get_logger, register_source

log = get_logger(__file__)
URL = "https://www2.census.gov/econ/bps/County/co{y}a.txt"


def main() -> None:
    got = []
    for y in range(1990, 2026):
        try:
            cached_get(URL.format(y=y), RAW / "building_permits" / f"co{y}a.txt", log)
            got.append(y)
        except Exception as e:  # noqa: BLE001
            log.warning("BPS %s unavailable: %s", y, e)
    register_source(dataset="building_permits", source_name="Census Building Permits Survey (county annual)",
                    official_URL="https://www.census.gov/construction/bps/", download_URL=URL,
                    coverage_start=str(min(got)), coverage_end=str(max(got)),
                    notes="county totals include imputation for non-reporting places; coverage flag from reporting")


if __name__ == "__main__":
    main()
