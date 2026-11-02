"""Shared helpers: paths, config, logging, data-source registry, cached downloads."""
from __future__ import annotations

import csv
import datetime as dt
import logging
import os
import sys
import time
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
CONFIG = ROOT / "config"
RAW = ROOT / "data" / "raw"
INTER = ROOT / "data" / "intermediate"
PROC = ROOT / "data" / "processed"
XWALK = ROOT / "data" / "crosswalks"
OUT = ROOT / "output"
TABLES, FIGS, DIAG, MODELS, LIT, LOGS, FINAL = (
    OUT / "tables", OUT / "figures", OUT / "diagnostics", OUT / "models",
    OUT / "literature", OUT / "logs", OUT / "final",
)
SEED = 20261007

for _p in [RAW, INTER, PROC, XWALK, TABLES, FIGS, DIAG, MODELS, LIT, LOGS, FINAL]:
    _p.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    with open(CONFIG / "config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_logger(script_name: str) -> logging.Logger:
    """Logger writing to output/logs/<script>.log and stdout, stamped with run time."""
    name = Path(script_name).stem
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    logger.propagate = False
    fmt = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
    fh = logging.FileHandler(LOGS / f"{name}.log", encoding="utf-8")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(sh)
    logger.info("=" * 70)
    logger.info("START %s at %s", name, dt.datetime.now().isoformat(timespec="seconds"))
    return logger


SOURCE_COLS = ["dataset", "source_name", "official_URL", "download_URL", "API_endpoint",
               "retrieval_date", "coverage_start", "coverage_end", "notes"]


def register_source(**kw) -> None:
    """Upsert a row (keyed on dataset) in output/logs/data_sources.csv."""
    path = LOGS / "data_sources.csv"
    rows = []
    if path.exists():
        with open(path, newline="", encoding="utf-8") as f:
            rows = [r for r in csv.DictReader(f) if r["dataset"] != kw["dataset"]]
    kw.setdefault("retrieval_date", dt.date.today().isoformat())
    rows.append({c: kw.get(c, "") for c in SOURCE_COLS})
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SOURCE_COLS)
        w.writeheader()
        w.writerows(rows)


def cached_get(url: str, dest: Path, logger: logging.Logger | None = None,
               params: dict | None = None, retries: int = 4, timeout: int = 180,
               force: bool = False) -> Path:
    """Download url to dest unless dest already exists (cache)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0 and not force:
        if logger:
            logger.info("cache hit: %s", dest.name)
        return dest
    last = None
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, timeout=timeout,
                             headers={"User-Agent": "tornado-mitigation-research/1.0"})
            r.raise_for_status()
            tmp = dest.with_suffix(dest.suffix + ".part")
            tmp.write_bytes(r.content)
            tmp.replace(dest)
            if logger:
                logger.info("downloaded %s (%d bytes) from %s", dest.name, len(r.content), r.url)
            return dest
        except Exception as e:  # noqa: BLE001
            last = e
            if logger:
                logger.warning("attempt %d failed for %s: %s", attempt + 1, url, e)
            time.sleep(2 ** attempt)
    raise RuntimeError(f"download failed: {url}: {last}")


def log_frame(logger: logging.Logger, df, label: str) -> None:
    """Log shape, columns and missingness of a DataFrame."""
    logger.info("%s: %d rows x %d cols", label, len(df), df.shape[1])
    miss = df.isna().mean().sort_values(ascending=False)
    miss = miss[miss > 0]
    if len(miss):
        logger.info("%s missingness (top 15): %s", label,
                    "; ".join(f"{k}={v:.2f}" for k, v in miss.head(15).items()))


def census_key() -> str | None:
    try:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
    except ImportError:
        pass
    k = os.environ.get("CENSUS_API_KEY", "").strip()
    return k or None
