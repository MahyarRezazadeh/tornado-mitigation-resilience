"""Download QWI (LEHD bulk files, no key needed) and keep only needed cells.

Source: https://lehd.ces.census.gov/data/qwi/latest_release/{st}/qwi_{st}_sa_f_gc_ns_op_u.csv.gz
  sa = sex x age, f = all firms, gc = county, ns = NAICS sector (+ all-industry rows),
  op = private ownership, u = not seasonally adjusted.
State files are 10-500 MB each, so they are streamed to a temp file, filtered, and the
filtered extract (parquet) is the cached artifact; the original URL + release stamp are logged.

Kept cells:
  (a) industry x county, sex=0 agegrp=A00   (county totals + sector panel)
  (b) industry 00, sex 1/2, agegrp A00       (sex cells)
  (c) industry 00, sex 0, agegrp A01-A08     (age cells)
Optional (with CENSUS_API_KEY): education, race/ethnicity, firm size via 08b_qwi_api_cells.py.
"""
from __future__ import annotations

import os
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests

from utils import RAW, XWALK, cached_get, get_logger, register_source

log = get_logger(__file__)
BASE = "https://lehd.ces.census.gov/data/qwi/latest_release/{st}/qwi_{st}_sa_f_gc_ns_op_u.csv.gz"
OUT = RAW / "qwi"
VARS = ["Emp", "EmpEnd", "EmpS", "HirA", "HirN", "HirR", "Sep", "SepBeg", "HirAS", "HirNS", "SepS",
        "TurnOvrS", "FrmJbGn", "FrmJbLs", "FrmJbC", "FrmJbGnS", "FrmJbLsS", "EarnS", "EarnBeg",
        "EarnHirAS", "EarnHirNS", "Payroll"]
KEYS = ["geography", "industry", "sex", "agegrp", "year", "quarter"]
USECOLS = ["geo_level", "ind_level"] + KEYS + VARS + ["s" + v for v in VARS]


def one_state(st: str) -> tuple[str, int]:
    dest = OUT / f"qwi_{st}_sa_f_gc_ns_op_u_extract.parquet"
    if dest.exists():
        return st, -1
    url = BASE.format(st=st)
    fd, tmp = tempfile.mkstemp(suffix=".csv.gz")
    os.close(fd)
    try:
        with requests.get(url, stream=True, timeout=600) as r:
            r.raise_for_status()
            with open(tmp, "wb") as f:
                for chunk in r.iter_content(1 << 20):
                    f.write(chunk)
        # low-memory stream filter: only kept rows (a small share of the file) are held in memory
        import csv
        import gzip
        with gzip.open(tmp, "rt", newline="") as fh:
            rd = csv.reader(fh)
            hdr = next(rd)
            pos = {c: i for i, c in enumerate(hdr)}
            keep_idx = [pos[c] for c in USECOLS if c in pos and c != "geo_level"]
            names = [hdr[i] for i in keep_idx]
            gl, ind, sx, ag = pos["geo_level"], pos["industry"], pos["sex"], pos["agegrp"]
            kept = tmp + ".kept.csv"
            with open(kept, "w", newline="") as fo:
                wr = csv.writer(fo)
                wr.writerow(names)
                for r in rd:
                    if r[gl] != "C":
                        continue
                    i_, s_, a_ = r[ind], r[sx], r[ag]
                    if (s_ == "0" and a_ == "A00") or (i_ == "00" and ((s_ in ("1", "2") and a_ == "A00") or (s_ == "0"))):
                        wr.writerow([r[i] for i in keep_idx])
        keys = {k: str for k in KEYS}
        df = pd.read_csv(kept, dtype=keys)
        os.remove(kept)
        for v in VARS + ["s" + v for v in VARS] + ["year", "quarter"]:
            df[v] = pd.to_numeric(df[v], errors="coerce")
        df.to_parquet(dest, index=False)
        return st, len(df)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cached_get("https://lehd.ces.census.gov/data/schema/latest/label_flags.csv", OUT / "label_flags.csv", log)
    cached_get("https://lehd.ces.census.gov/data/schema/latest/variables_qwi.csv", OUT / "variables_qwi.csv", log)
    states = sorted(pd.read_parquet(XWALK / "counties_2020.parquet")["STUSPS"].str.lower().unique())
    with ThreadPoolExecutor(max_workers=1) as ex:   # 1 worker + stream filter: fits on an 8GB machine
        futs = {ex.submit(one_state, s): s for s in states}
        for f in as_completed(futs):
            try:
                st, n = f.result()
                log.info("QWI %s: %s rows kept", st, "cached" if n < 0 else n)
            except Exception as e:  # noqa: BLE001
                log.error("QWI %s FAILED: %s", futs[f], e)
    register_source(dataset="qwi", source_name="Census LEHD Quarterly Workforce Indicators (R latest_release)",
                    official_URL="https://lehd.ces.census.gov/data/#qwi", download_URL=BASE,
                    API_endpoint="https://api.census.gov/data/timeseries/qwi/sa (alternative, key required)",
                    coverage_start="state-specific (1990s)", coverage_end="latest release",
                    notes="sa_f_gc_ns_op_u; private ownership; filtered extract kept (raw >5GB not retained)")


if __name__ == "__main__":
    main()
