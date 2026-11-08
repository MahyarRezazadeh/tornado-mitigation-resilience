"""REDESIGN robustness for the dose-response coefficient b on E x S (see 46_redesign_analysis.py).

Concern: E = 'track crosses a populated block group' is more likely in large/growing counties, so the
exposure main effect can pick up growth trends. Checks:
  base        county + state-year FE
  popdecXyr   + baseline-population decile x year FE
  ctrend      + county-specific linear trends (alternating projections, OLS on residuals)
  E_anyhit    E = any SPC track enters the county (population-independent)
  E_logpop    E = log(1 + population in path), continuous
  E_t_or_t1   E = hit in t or t-1
  cl_state    cluster by state
  drop_FL     drop Florida (hurricane-driven wind retrofits)
  hmgp_only   S built from HMGP projects only is not available separately -> skipped
Also: first-stage robustness (lag-2 coefficient) under popdecXyr and ctrend.

Output: output/tables/redesign_robustness.csv
"""
from __future__ import annotations

import importlib.util

import numpy as np
import pandas as pd
import pyfixest as pf
from linearmodels.iv import IV2SLS

from utils import SRC, TABLES, get_logger

log = get_logger(__file__)
spec = importlib.util.spec_from_file_location("ra", SRC / "46_redesign_analysis.py")
ra = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ra)

KEY = [o for o in ra.OUTCOMES if o[0] in ("log_gdp_per_ha", "log_ag_gdp_per_ha", "log_crop_rcpt_per_ha",
                                          "log_crop_t_per_ha", "log_dmg", "log_cas", "log_cbp_employment",
                                          "log_establishments", "job_destruction_rate", "establishment_death_rate")]


def ctrend_ols(s, y, xs):
    """Absorb county intercept+trend and state-year means by alternating projections; OLS, county clusters."""
    cols = [y] + xs
    D = s[cols].astype(float).copy()
    t = (s.year - s.year.mean()).astype(float)
    cg, sg = s.county_fips, s.state_year
    for _ in range(30):
        # county intercept + slope
        mt = t.groupby(cg).transform("mean")
        tc = t - mt
        vt = (tc ** 2).groupby(cg).transform("sum").replace(0, np.nan)
        for c in cols:
            m = D[c].groupby(cg).transform("mean")
            b = ((D[c] - m) * tc).groupby(cg).transform("sum") / vt
            D[c] = D[c] - m - b.fillna(0) * tc
            D[c] = D[c] - D[c].groupby(sg).transform("mean")
    r = IV2SLS(D[y], D[xs], None, None).fit(cov_type="clustered", clusters=pd.factorize(cg)[0])
    return r.params, r.std_errors, r.pvalues


def est(s, y, fe, vc, xs=("ExS", "Ex", "S"), how="feols"):
    if how == "ctrend":
        b, se, p = ctrend_ols(s, y, list(xs))
        return b["ExS"], se["ExS"], p["ExS"], len(s)
    m = pf.feols(f"{y} ~ {' + '.join(xs)} | {fe}", data=s, vcov=vc)
    t = m.tidy()
    return t.loc["ExS", "Estimate"], t.loc["ExS", "Std. Error"], t.loc["ExS", "Pr(>|t|)"], m._N


def main() -> None:
    d = ra.build_panel()
    d = d[d.state_year.notna() & d.year.between(ra.Y0, ra.Y1)].copy()
    dec = d.drop_duplicates("county_fips").set_index("county_fips").baseline_pop.rank(pct=True)
    d["popdec"] = (d.county_fips.map(dec) * 10).clip(upper=9.999).astype(int)
    d["popdec_year"] = d.popdec.astype(str) + "_" + d.year.astype(str)
    rows = []
    for y, lab, ecol, (lo, hi) in KEY:
        base = d[d.year.between(lo, hi) & d[y].notna()].copy()
        if base.empty:
            continue
        mar = ecol == "E_mar"
        variants = {
            "base": (ecol, ra.FE, {"CRV1": "county_fips"}, "feols", None),
            "popdecXyr": (ecol, ra.FE + " + popdec_year", {"CRV1": "county_fips"}, "feols", None),
            "ctrend": (ecol, None, None, "ctrend", None),
            "E_anyhit": ("mar_spc_hit" if mar else "spc_hit", ra.FE, {"CRV1": "county_fips"}, "feols", None),
            "E_logpop": ("mar_log_pop_exposed" if mar else "log_pop_exposed", ra.FE, {"CRV1": "county_fips"}, "feols", None),
            "E_t_or_t1": ("E01", ra.FE, {"CRV1": "county_fips"}, "feols", None),
            "cl_state": (ecol, ra.FE, {"CRV1": "state_fips"}, "feols", None),
            "drop_FL": (ecol, ra.FE, {"CRV1": "county_fips"}, "feols", "FL"),
        }
        for name, (ec, fe, vc, how, drop) in variants.items():
            s = base if drop is None else base[base.STUSPS != drop]
            s = s.copy()
            s["Ex"] = s[ec].fillna(0).astype(float)
            s["ExS"] = s.Ex * s.S
            try:
                b, se, p, n = est(s, y, fe, vc, how=how)
                rows.append({"outcome": lab, "var": y, "variant": name, "b": b, "se": se, "p": p, "N": n})
            except Exception as e:  # noqa: BLE001
                rows.append({"outcome": lab, "var": y, "variant": name, "status": str(e)[:100]})
        log.info("%s done", y)
    r = pd.DataFrame(rows)
    r.to_csv(TABLES / "redesign_robustness.csv", index=False)
    wide = r.pivot_table(index="var", columns="variant", values="b")
    pw = r.pivot_table(index="var", columns="variant", values="p")
    log.info("b(E x S) by variant:\n%s", wide.round(4).to_string())
    log.info("p-values:\n%s", pw.round(3).to_string())

    # first-stage robustness: new obligations on lagged exposure
    fs = []
    lags = "E + E_L1 + E_L2 + E_L3 + E_L4 + E_F1 + E_F2"
    for name, fe in [("base", ra.FE), ("popdecXyr", ra.FE + " + popdec_year")]:
        m = pf.feols(f"new_log_pc ~ {lags} | {fe}", data=d, vcov={"CRV1": "county_fips"})
        t = m.tidy()
        for term in ["E_F2", "E_F1", "E", "E_L1", "E_L2", "E_L3", "E_L4"]:
            fs.append({"variant": name, "term": term, "b": t.loc[term, "Estimate"], "p": t.loc[term, "Pr(>|t|)"]})
    for ex in ["spc_hit"]:
        g = d.groupby("county_fips")[ex]
        for k in range(1, 5):
            d[f"{ex}_L{k}"] = g.shift(k)
        m = pf.feols(f"new_log_pc ~ {ex} + " + " + ".join(f"{ex}_L{k}" for k in range(1, 5)) + f" | {ra.FE}",
                     data=d, vcov={"CRV1": "county_fips"})
        t = m.tidy()
        for term in t.index:
            fs.append({"variant": f"E={ex}", "term": term, "b": t.loc[term, "Estimate"], "p": t.loc[term, "Pr(>|t|)"]})
    fs = pd.DataFrame(fs)
    fs.to_csv(TABLES / "redesign_first_stage_robustness.csv", index=False)
    log.info("first-stage robustness:\n%s", fs.round(4).to_string())


if __name__ == "__main__":
    main()
