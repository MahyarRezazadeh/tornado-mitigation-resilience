import importlib
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from utils import XWALK  # noqa: E402

xw = importlib.import_module("22_build_county_crosswalk")


def test_known_recodes():
    s = pd.Series(["46113", "51515", "12025", "01001"])
    assert list(xw.harmonize(s)) == ["46102", "51019", "12086", "01001"]


def test_virginia_cities_kept_separate():
    c = pd.read_parquet(XWALK / "counties_2020.parquet")
    assert {"51760", "51710", "51810"} <= set(c.county_fips)   # Richmond, Norfolk, Virginia Beach


def test_contiguous_only():
    c = pd.read_parquet(XWALK / "counties_2020.parquet")
    assert not c.state_fips.isin(["02", "15", "72"]).any()
    assert c.county_fips.is_unique and len(c) > 3100
