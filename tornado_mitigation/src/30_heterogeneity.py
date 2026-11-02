"""Heterogeneity (Section 31) -- EXPLORATORY. BH correction within each heterogeneity family.

County-characteristic splits (treated and controls split together): historical risk tercile, metro,
population (above/below median 2000), income proxy (1998 CBP payroll per employee), baseline employment,
census region.
Treatment-characteristic splits (controls kept, treated restricted): project type (safe room / retrofit),
per-capita federal spending (above/below treated median), number of strict projects (1 vs 2+),
treatment vintage (first treated <2005, 2005-2012, 2013+).
Worker groups (Outcome 6): main model estimated within each QWI demographic cell (sex, age, education,
race, ethnicity, firm size); cells with >30% missing are flagged.
Outputs: output/models/heterogeneity.csv, output/models/demographic_cells.csv
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pyfixest as pf
from statsmodels.stats.multitest import multipletests

import est
from utils import MODELS, PROC, get_logger

log = get_logger(__file__)
OUTS = [("separation_rate", "q"), ("log_employment", "q"), ("log_earnings", "q"),
        ("establishment_death_rate", "y"), ("job_destruction_rate", "y")]


def county_chars() -> pd.DataFrame:
    w = pd.read_parquet(PROC / "matching_weights.parquet")[["county_fips"]]
    cy = est.panel("y").drop_duplicates("county_fips")
    c = cy[["county_fips", "risk_tercile", "metro", "baseline_pop", "baseline_emp", "region", "ft_strict_primary"]].copy()
    for col in ["risk_tercile", "metro", "region"]:
        c[col] = c[col].astype(str)
    tw = pd.read_parquet(PROC / "county_treatment_wide.parquet")[
        ["county_fips", "n_projects_strict", "federal_share_strict", "n_safe_room_strict", "n_wind_retrofit_strict"]]
    c = c.merge(tw, how="left", on="county_fips")
    c["ft_strict_primary"] = c["ft_strict_primary"].astype(float)
    for col in ["baseline_pop", "baseline_emp", "n_projects_strict", "federal_share_strict", "n_safe_room_strict",
                "n_wind_retrofit_strict"]:
        c[col] = c[col].astype(float)
    cbp = pd.read_parquet(PROC.parent / "intermediate" / "cbp_county_year.parquet").query("year == 1998")
    c = c.merge((cbp.annual_payroll / cbp.cbp_employment).rename("pay_per_emp").to_frame().assign(
        county_fips=cbp.county_fips.values), how="left")
    c["pop_hi"] = (c.baseline_pop > c.baseline_pop.median()).astype(int)
    c["emp_hi"] = (c.baseline_emp > c.baseline_emp.median()).astype(int)
    c["income_hi"] = (c.pay_per_emp > c.pay_per_emp.median()).astype(int)
    tr = c.ft_strict_primary.notna()
    pc = c.federal_share_strict / c.baseline_pop
    c["spend_hi"] = np.where(tr, (pc > pc[tr].median()).astype(int), np.nan)
    c["multi_proj"] = np.where(tr, (c.n_projects_strict >= 2).astype(int), np.nan)
    fy = c.ft_strict_primary // 10
    c["vintage"] = np.where(~tr, np.nan, np.where(fy < 2005, 0, np.where(fy <= 2012, 1, 2)))
    c["type_saferoom"] = np.where(tr, (c.n_safe_room_strict > 0).astype(int), np.nan)
    c["type_retrofit"] = np.where(tr, (c.n_wind_retrofit_strict > 0).astype(int), np.nan)
    _ = w
    return c


def run_sub(var, freq, keep_counties, label, dim, level):
    r = est.run(est.Spec(outcome=var, freq=freq, sample={"keep_counties": list(keep_counties)}, label=label))
    return {"family": dim, "level": level, "outcome": var, "beta": r.get("beta"), "se": r.get("se"), "p": r.get("p"),
            "N": r.get("N"), "treated_counties": r.get("treated_counties"),
            "treated_tornado_obs": r.get("treated_tornado_obs"), "status": r.get("status")}


def main() -> None:
    c = county_chars()
    allc = set(c.county_fips)
    controls = set(c[c.ft_strict_primary.isna()].county_fips)
    rows = []
    county_dims = {"historical_risk_tercile": "risk_tercile", "metro": "metro", "population_hi": "pop_hi",
                   "income_hi": "income_hi", "baseline_emp_hi": "emp_hi", "region": "region"}
    treat_dims = {"spending_pc_hi": "spend_hi", "multiple_projects": "multi_proj", "vintage": "vintage",
                  "has_safe_room": "type_saferoom", "has_wind_retrofit": "type_retrofit"}
    import sys
    skip_county = "--cells-only" in sys.argv
    for var, freq in ([] if skip_county else OUTS):
        for dim, col in county_dims.items():
            for lev, g in c.groupby(col):
                rows.append(run_sub(var, freq, set(g.county_fips), f"H_{dim}_{lev}", dim, lev))
        for dim, col in treat_dims.items():
            for lev, g in c[c[col].notna()].groupby(col):
                rows.append(run_sub(var, freq, set(g.county_fips) | controls, f"H_{dim}_{lev}", dim, lev))
        log.info("%s heterogeneity done", var)
    h = pd.DataFrame(rows) if rows else pd.read_csv(MODELS / "heterogeneity.csv")
    h["family_key"] = h.family + "|" + h.outcome
    for k, g in h[h.p.notna()].groupby("family_key"):
        h.loc[g.index, "bh_q_within_family"] = multipletests(g.p, method="fdr_bh")[1]
    # difference tests between levels (independent-subsample z; vs first level)
    h["diff_vs_first_p"] = np.nan
    for k, g in h[h.beta.notna()].groupby("family_key"):
        b0, s0 = g.iloc[0].beta, g.iloc[0].se
        for i, r in g.iloc[1:].iterrows():
            z = (r.beta - b0) / np.sqrt(r.se ** 2 + s0 ** 2)
            h.loc[i, "diff_vs_first_p"] = 2 * (1 - __import__("scipy").stats.norm.cdf(abs(z)))
    h["label"] = "EXPLORATORY"
    h.to_csv(MODELS / "heterogeneity.csv", index=False)

    # worker / firm-size cells
    import pyarrow.parquet as pq
    d0, _ = est.build(est.Spec(outcome="EF1_plus", freq="q"))
    tl = d0[["county_fips", "yq", "M", "T", "ever"]]
    est._CACHE.clear()
    path = PROC / "county_demographic_quarter_panel.parquet"
    fams = pq.read_table(path, columns=["demo_family"]).column(0).unique().to_pylist()
    cols = ["county_fips", "yq", "state_fips", "demo_family", "demo_group", "separation_rate", "log_employment",
            "log_earnings"]
    out = []

    def groups():
        for fam in fams:                     # one family at a time (memory)
            dm = pd.read_parquet(path, columns=cols, filters=[("demo_family", "=", fam)])
            for key, g in dm.groupby(["demo_family", "demo_group"]):
                yield key, g
            del dm

    for (fam, grp), g in groups():
        s = g.merge(tl, on=["county_fips", "yq"], how="inner")
        s["MT"] = s.M * s["T"]
        s["sy"] = s.state_fips + "_" + s.yq.astype(str)
        for y in ["separation_rate", "log_employment", "log_earnings"]:
            ss = s[s[y].notna()]
            miss = 1 - len(ss) / max(len(s), 1)
            if ss.MT.sum() == 0 or len(ss) < 1000:
                continue
            try:
                f = pf.feols(f"{y} ~ MT + M + T | county_fips + sy", data=ss, vcov={"CRV1": "county_fips"})
                tb = f.tidy().loc["MT"]
                out.append({"family": fam, "group": grp, "outcome": y, "beta": tb["Estimate"], "se": tb["Std. Error"],
                            "p": tb["Pr(>|t|)"], "N": int(f._N), "missing_share": miss,
                            "high_suppression_flag": miss > 0.30, "mean_y": ss[y].mean()})
            except Exception as e:  # noqa: BLE001
                log.warning("cell %s %s %s: %s", fam, grp, y, e)
    cells = pd.DataFrame(out)
    if len(cells):
        for k, g in cells.groupby(["family", "outcome"]):
            cells.loc[g.index, "bh_q_within_family"] = multipletests(g.p, method="fdr_bh")[1]
    cells.to_csv(MODELS / "demographic_cells.csv", index=False)
    _ = allc


if __name__ == "__main__":
    main()
