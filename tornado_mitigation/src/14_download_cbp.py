"""Census County Business Patterns county files (bulk zip, no key), NAICS era 1998+."""
from __future__ import annotations

import zipfile

import pandas as pd

from utils import RAW, cached_get, get_logger, register_source

log = get_logger(__file__)
URL = "https://www2.census.gov/programs-surveys/cbp/datasets/{y}/cbp{yy}co.zip"
OUT = RAW / "cbp"
SIZE_COLS = ["n1_4", "n5_9", "n10_19", "n20_49", "n50_99", "n100_249", "n250_499", "n500_999",
             "n1000", "n1000_1", "n1000_2", "n1000_3", "n1000_4", "n<5", "n5_9"]


def main() -> None:
    frames = []
    for y in range(1998, 2024):
        try:
            z = cached_get(URL.format(y=y, yy=str(y)[2:]), OUT / f"cbp{str(y)[2:]}co.zip", log, timeout=600)
        except Exception as e:  # noqa: BLE001
            log.warning("CBP %s unavailable: %s", y, e)
            continue
        with zipfile.ZipFile(z) as zf:
            name = [n for n in zf.namelist() if n.lower().endswith(".txt") or n.lower().endswith(".csv")][0]
            d = pd.read_csv(zf.open(name), dtype=str, encoding="latin-1")
        d.columns = [c.lower() for c in d.columns]
        nm = d["naics"].str.replace("-", "").str.replace("/", "")
        d = d[(nm == "") | nm.str.fullmatch(r"\d{2}")]   # total + 2-digit sectors
        keep = ["fipstate", "fipscty", "naics", "emp", "empflag", "emp_nf", "qp1", "ap", "ap_nf", "est"] + \
               [c for c in d.columns if c.startswith("n") and c[1:2].isdigit() or c == "n<5"]
        d = d[[c for c in keep if c in d.columns]].assign(year=y)
        frames.append(d)
        log.info("CBP %s: %d rows", y, len(d))
    df = pd.concat(frames, ignore_index=True)
    df.to_parquet(OUT / "cbp_county_raw.parquet", index=False)
    register_source(dataset="cbp", source_name="Census County Business Patterns (county files)",
                    official_URL="https://www.census.gov/programs-surveys/cbp.html", download_URL=URL,
                    coverage_start="1998", coverage_end=str(df.year.max()), notes="total + 2-digit NAICS; size classes")


if __name__ == "__main__":
    main()
