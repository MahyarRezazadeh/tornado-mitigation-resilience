"""Simulation tests: the estimation core recovers a known interaction effect and placebo nulls."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyfixest as pf

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def sim(beta=-0.5, n=400, t=40, seed=1):
    rng = np.random.default_rng(seed)
    c = np.repeat(np.arange(n), t)
    tt = np.tile(np.arange(t), n)
    st = c % 10
    ft = np.where(rng.random(n) < 0.4, rng.integers(5, 35, n), 10**6)[c]
    M = (tt >= ft).astype(int)
    T = (rng.random(n * t) < 0.05).astype(int)
    y = 0.3 * c / n + 0.02 * tt + 1.0 * T + beta * M * T + rng.normal(0, 1, n * t)
    return pd.DataFrame({"c": c, "t": tt, "st": [f"{a}_{b}" for a, b in zip(st, tt)], "M": M, "T": T, "MT": M * T, "y": y})


def test_recovers_interaction():
    d = sim()
    f = pf.feols("y ~ MT + M + T | c + st", data=d, vcov={"CRV1": "c"})
    b, se = f.coef()["MT"], f.se()["MT"]
    assert abs(b - (-0.5)) < 3 * se


def test_null_when_no_effect():
    d = sim(beta=0.0, seed=7)
    f = pf.feols("y ~ MT + M + T | c + st", data=d, vcov={"CRV1": "c"})
    assert abs(f.coef()["MT"]) < 3.5 * f.se()["MT"]
