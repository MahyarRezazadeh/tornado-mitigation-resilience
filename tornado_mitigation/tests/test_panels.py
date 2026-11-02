import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from utils import PROC  # noqa: E402


def test_unique_keys():
    q = pd.read_parquet(PROC / "county_quarter_panel.parquet", columns=["county_fips", "yq"])
    y = pd.read_parquet(PROC / "county_year_panel.parquet", columns=["county_fips", "year"])
    assert not q.duplicated().any() and not y.duplicated().any()


def test_no_negative_counts():
    q = pd.read_parquet(PROC / "county_quarter_panel.parquet", columns=["EmpEnd", "Sep"])
    y = pd.read_parquet(PROC / "county_year_panel.parquet", columns=["estabs", "estab_deaths"])
    assert (q.dropna() >= 0).all().all() and (y.dropna() >= 0).all().all()


def test_suppressed_not_zero():
    # suppressed QWI cells are NaN, so share of exact zeros in county separations should be ~0
    q = pd.read_parquet(PROC / "county_quarter_panel.parquet", columns=["Sep"])
    assert (q.Sep == 0).mean() < 0.01


def test_march_alignment():
    y = pd.read_parquet(PROC / "county_year_panel.parquet", columns=["county_fips", "year", "mar_tornado_count"])
    q = pd.read_parquet(PROC / "tornado_exposure_cq.parquet", columns=["county_fips", "year", "quarter", "tornado_count"])
    c = "40109"
    tot = q[(q.county_fips == c) & (((q.year == 2012) & (q.quarter > 1)) | ((q.year == 2013) & (q.quarter == 1)))].tornado_count.sum()
    assert y[(y.county_fips == c) & (y.year == 2013)].mar_tornado_count.iloc[0] == tot
