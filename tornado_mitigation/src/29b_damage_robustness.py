"""Robustness of the M1 physical-damage mechanism (exploratory; added after main results, labeled).

Outcome log(1 + reported property damage) in tornado county-quarters (EF bins FE) on Mitigated x intensity.
Variants: primary; moderate/broad; safe-room only; retrofit only; exclude FL; exclude OK/TX; state cluster;
EF1+ county-quarters only; 1996+ (modern Storm Events damage reporting); pre-treatment placebo
(ever-treated x intensity using only pre-treatment periods); fatalities and injuries alongside.
Output: output/models/damage_robustness.csv
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pyfixest as pf

import est
from utils import MODELS, get_logger

log = get_logger(__file__)


def one(label, spec, y="log_damage", sample=None, vc=None, within=False):
    d, _ = est.build(spec)
    d = d[d.any_tornado > 0].copy()
    d["I"] = d["max_tornado_intensity"].fillna(-1) + 1
    d["MI"] = d["M"] * d["I"]
    d["EI"] = d["ever"] * d["I"]   # ever-treated x intensity: absorbs selection on pre-treatment damage slope
    raw = {"log_damage": "reported_property_damage", "log_fatalities": "total_fatalities",
           "log_injuries": "total_injuries"}[y]
    d[y] = np.log1p(d[raw].fillna(0))
    if sample:
        d = sample(d)
    rhs = "MI + EI + M + C(I)" if within else "MI + M + C(I)"
    f = pf.feols(f"{y} ~ {rhs} | county_fips + state_yq", data=d, vcov=vc or {"CRV1": "county_fips"})
    t = f.tidy().loc["MI"]
    return {"variant": label, "outcome": y, "beta": t["Estimate"], "se": t["Std. Error"], "p": t["Pr(>|t|)"],
            "N": int(f._N), "treated_obs": int((d.M > 0).sum()), "pct_per_EF_step": 100 * (np.exp(t["Estimate"]) - 1)}


def main() -> None:
    base = est.Spec(outcome="EF1_plus", freq="q")
    est.panel("q")
    rows = [one("primary (strict, obligation+2y)", base)]
    for lab, sp in [("moderate", base.but(definition="moderate")), ("broad", base.but(definition="broad")),
                    ("safe-room only", base.but(timing="saferoom")), ("wind-retrofit only", base.but(timing="retrofit")),
                    ("closeout timing", base.but(timing="closeout")), ("approval lag 0", base.but(timing="approval_L0")),
                    ("exclude FL", base.but(sample={"drop_states": ["FL"]})),
                    ("exclude OK and TX", base.but(sample={"drop_states": ["OK", "TX"]})),
                    ("exclude post-tornado HMGP awards", base.but(sample={"exclude_post_tornado_award": True})),
                    ("PLACEBO: ever-treated x intensity, pre-treatment only", base.but(placebo="pre_interaction"))]:
        try:
            rows.append(one(lab, sp))
        except Exception as e:  # noqa: BLE001
            rows.append({"variant": lab, "status": str(e)[:100]})
    rows.append(one("1996+ only (modern damage reporting)", base, sample=lambda d: d[d.year >= 1996]))
    rows.append(one("EF1+ county-quarters only", base, sample=lambda d: d[d.EF1_plus > 0]))
    rows.append(one("cluster by state", base, vc={"CRV1": "state_fips"}))
    for y in ["log_fatalities", "log_injuries"]:
        rows.append(one("primary", base, y=y))
        rows.append(one("PLACEBO pre-treatment", base.but(placebo="pre_interaction"), y=y))
    # within-treated design: post-treatment slope change relative to treated counties' own pre-treatment slope
    for y in ["log_damage", "log_fatalities", "log_injuries"]:
        rows.append(one("WITHIN-TREATED (controls ever-treated x intensity)", base, y=y, within=True))
    rows.append(one("WITHIN-TREATED, safe-room only", base.but(timing="saferoom"), within=True))
    rows.append(one("WITHIN-TREATED, 1996+", base, sample=lambda d: d[d.year >= 1996], within=True))
    # mean-reversion check: drop treated counties' 5 pre-treatment years (contains the disaster that triggered HMGP)
    drop5 = lambda d: d[~((d.ever == 1) & (d.M == 0) & (d.yq >= d.ft_strict_primary.astype(float) - 50))]  # noqa: E731
    for y in ["log_damage", "log_fatalities", "log_injuries"]:
        rows.append(one("WITHIN-TREATED, drop 5 pre-treatment years (mean-reversion check)", base, y=y,
                        sample=drop5, within=True))
    rows.append(one("WITHIN-TREATED, drop 5 pre years, excl. post-tornado HMGP awards",
                    base.but(sample={"exclude_post_tornado_award": True}), sample=drop5, within=True))
    rows.append(one("PLACEBO pre-treatment, excluding 5 pre years", base.but(placebo="pre_interaction"),
                    sample=lambda d: d[~((d.ever == 1) & (d.yq >= d.ft_strict_primary.astype(float) - 50))]))
    df = pd.DataFrame(rows)
    df.to_csv(MODELS / "damage_robustness.csv", index=False)
    log.info("\n%s", df.round(4).to_string())


if __name__ == "__main__":
    main()
