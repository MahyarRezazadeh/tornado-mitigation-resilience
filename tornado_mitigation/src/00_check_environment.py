"""Check Python version, packages, directory tree and Census key; print instructions if missing."""
from __future__ import annotations

import importlib
import sys

from utils import ROOT, census_key, get_logger

log = get_logger(__file__)
PKGS = ["pandas", "numpy", "polars", "pyarrow", "duckdb", "requests", "bs4", "lxml", "geopandas", "shapely", "pyproj",
        "statsmodels", "linearmodels", "pyfixest", "scipy", "sklearn", "matplotlib", "openpyxl", "xlsxwriter",
        "jinja2", "tqdm", "dotenv", "yaml", "joblib", "tabulate", "xlrd"]


def main() -> None:
    log.info("Python %s", sys.version.split()[0])
    if sys.version_info < (3, 11):
        log.warning("Python 3.11+ recommended")
    missing = []
    for p in PKGS:
        try:
            m = importlib.import_module(p)
            log.info("%-12s %s", p, getattr(m, "__version__", "ok"))
        except ImportError:
            missing.append(p)
    if missing:
        log.warning("missing packages (substitutes may apply): %s -> pip install -r requirements.txt", missing)
    if census_key():
        log.info("CENSUS_API_KEY found")
    else:
        log.warning("CENSUS_API_KEY not set. Get a free key at https://api.census.gov/data/key_signup.html and put "
                    "CENSUS_API_KEY=... in %s. Without it, QWI education/race/ethnicity/firm-size cells (08b) are "
                    "skipped; everything else uses keyless bulk files.", ROOT / ".env")


if __name__ == "__main__":
    main()
