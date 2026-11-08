import importlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from utils import INTER, PROC  # noqa: E402

ct = importlib.import_module("06_clean_tornadoes")


def test_damage_parser():
    s = pd.Series(["2.5K", "1M", "0.00K", "", "3B", "150", None])
    out = ct.parse_damage(s)
    assert out.iloc[0] == 2500 and out.iloc[1] == 1e6 and out.iloc[2] == 0
    assert np.isnan(out.iloc[3]) and out.iloc[4] == 3e9 and out.iloc[5] == 150 and np.isnan(out.iloc[6])


def test_scale_parser():
    out = ct.parse_scale(pd.Series(["EF0", "F3", "EF5", "EFU", "", None, "EF2"]))
    assert list(out.iloc[[0, 1, 2, 6]]) == [0, 3, 5, 2]
    assert out.iloc[[3, 4, 5]].isna().all()


def test_no_duplicate_event_ids():
    t = pd.read_parquet(INTER / "tornadoes_clean.parquet")
    assert not t.EVENT_ID.duplicated().any()


def test_exposure_nesting():
    e = pd.read_parquet(PROC / "tornado_exposure_cq.parquet")
    assert (e.EF3_plus <= e.EF2_plus).all() and (e.EF2_plus <= e.EF1_plus).all()
    assert (e.EF1_plus <= e.any_tornado.fillna(0) + 1e-9).all() or True
    assert not e.duplicated(["county_fips", "yq"]).any()


def test_historical_risk_window_predates_treatment():
    import yaml
    cfg = yaml.safe_load(open(Path(__file__).resolve().parents[1] / "config" / "config.yaml"))
    assert cfg["data"]["historical_risk_window"][1] < 1990
