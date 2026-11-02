"""REDESIGN: stress tests of the one robust dose-response result (reported property damage).

  ppml        Poisson PML on damage $ level: Ex*S + Ex + S | county + state-year
  exposed     exposed county-years only (E=1): log1p damage on S, with log(pop in path), track km | state-year
  dose_bins   E x spending bins ($0, <=$10, $10-50, >$50 federal per capita)
  ef_mech     EF magnitude of tracks hitting populated places on S (EF is damage-rated: if mitigation lowers
              damage, EF should fall too -> consistency check, not independent evidence)
  dyn         E_t, E_t-1 interactions (damage should respond only contemporaneously)
Output: output/tables/redesign_damage_checks.csv
"""
from __future__ import annotations

import importlib.util

import numpy as np
import pandas as pd
import pyfixest as pf

from utils import SRC, TABLES, get_logger

log = get_logger(__file__)
spec = importlib.util.spec_from_file_location("ra", SRC / "46_redesign_analysis.py")
ra = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ra)


def take(m, term, label):
    t = m.tidy()
    r = t.loc[term]
    return {"check": label, "term": term, "b": r["Estimate"], "se": r["Std. Error"], "p": r["Pr(>|t|)"], "N": m._N}


def main() -> None:
    d = ra.build_panel()
    d = d[d.state_year.notna() & d.year.between(ra.Y0, ra.Y1)].copy()
    d["Ex"] = d.E.fillna(0)
    d["ExS"] = d.Ex * d.S
    d["dmg"] = d.reported_property_damage.fillna(0)
    vc = {"CRV1": "county_fips"}
    out = []
    m = pf.fepois("dmg ~ ExS + Ex + S | county_fips + state_year", data=d, vcov=vc)
    out.append(take(m, "ExS", "ppml_level"))
    e = d[d.Ex == 1].copy()
    e["lpe"] = np.log1p(e.pop_exposed)
    m = pf.feols("log_dmg ~ S + lpe + track_km | state_year", data=e, vcov=vc)
    out.append(take(m, "S", "exposed_only_stateyearFE"))
    m = pf.feols("log_dmg ~ S + lpe + track_km | state_year + county_fips", data=e, vcov=vc)
    out.append(take(m, "S", "exposed_only_countyFE"))
    pc = d.stock_fed / d.baseline_pop.clip(lower=100)
    for k, (lo, hi) in {"b1_0_10": (0, 10), "b2_10_50": (10, 50), "b3_50p": (50, np.inf)}.items():
        d[k] = ((pc > lo) & (pc <= hi)).astype(int)
        d["Ex_" + k] = d.Ex * d[k]
    m = pf.feols("log_dmg ~ Ex_b1_0_10 + Ex_b2_10_50 + Ex_b3_50p + Ex + b1_0_10 + b2_10_50 + b3_50p"
                 " | county_fips + state_year", data=d, vcov=vc)
    for k in ["Ex_b1_0_10", "Ex_b2_10_50", "Ex_b3_50p"]:
        out.append(take(m, k, "dose_bins"))
    e["mag"] = e.spc_max_mag.where(e.spc_max_mag >= 0)
    m = pf.feols("mag ~ S + lpe + track_km | state_year", data=e.dropna(subset=["mag"]), vcov=vc)
    out.append(take(m, "S", "ef_mech_exposed"))
    d["ExL1"] = d.E_L1.fillna(0)
    d["ExL1S"] = d.ExL1 * d.S
    m = pf.feols("log_dmg ~ ExS + ExL1S + Ex + ExL1 + S | county_fips + state_year", data=d, vcov=vc)
    out += [take(m, "ExS", "dyn"), take(m, "ExL1S", "dyn")]
    for k in ["b1_0_10", "b2_10_50", "b3_50p"]:
        out.append({"check": "bin_obs", "term": k, "N": int(((d[k] == 1) & (d.Ex == 1)).sum())})
    r = pd.DataFrame(out)
    r.to_csv(TABLES / "redesign_damage_checks.csv", index=False)
    log.info("damage checks:\n%s", r.round(4).to_string())


if __name__ == "__main__":
    main()
