"""REDESIGN analysis (2026-10-09): SPC damage-independent exposure, mitigation spending dose, land productivity.

A. Exposure validity     Does SPC exposure move outcomes at all (gamma_E)?  E = population in path (spc_pop_hit)
B. First stage           Does exposure raise mitigation implementation?
     B1 panel flows:     NewOblig_ct (any; log $ per capita) on E lags 0..4 and leads 1..2 (placebo) | county + state-year
     B2 cross-section:   total 1999-2024 strict federal $ per capita on 1980-1995 SPC exposure | state FE
     B3 instrument FS:   operational stock S_c,t-1 on Z = leave-own-county-out state mitigation pool x pre-1996 exposure
C. Dose-response         Y_ct = b*E_ct*S_c,t-1 + g*E_ct + d*S_c,t-1 | county + state-year, cluster county
     S = log1p(cumulative operational strict federal $ per capita); also spending tiers (low/high per capita)
     b < 0 for losses / b > 0 for productivity => counties that spent more fared better when hit.
D. Pre-treatment placebo E x log1p(eventual spending pc) on never-yet-treated county-years (selection check)
E. 2SLS                  S and E*S instrumented by Z and E*Z.

Outputs: output/tables/redesign_*.csv, output/final/redesign_results.md
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pyfixest as pf

from utils import FINAL, INTER, PROC, TABLES, get_logger

log = get_logger(__file__)
Y0, Y1 = 1999, 2024


# ----------------------------------------------------------------------------- data
def spending() -> tuple[pd.DataFrame, pd.DataFrame]:
    p = pd.read_parquet(INTER / "fema_treatment_projects.parquet")
    p = p[(p.treat_strict == 1) & p.county_fips.notna()].copy()
    p["fed"] = p.federal_share.fillna(0.75 * p.total_cost).fillna(0)
    p["oblig_year"] = p.obligation_date.dt.year.fillna(p.approval_date.dt.year).fillna(p.t_primary.dt.year - 2)
    p["oper_year"] = p.t_primary.dt.year                       # operational = obligation + 2y (primary timing)
    flow = p.groupby(["county_fips", "oblig_year"]).agg(new_fed=("fed", "sum"), new_proj=("fed", "size")).reset_index()
    flow = flow.rename(columns={"oblig_year": "year"})
    oper = p.groupby(["county_fips", "oper_year"]).fed.sum().rename("oper_fed").reset_index().rename(columns={"oper_year": "year"})
    return flow, oper


def build_panel() -> pd.DataFrame:
    cols = ["county_fips", "year", "state_fips", "STUSPS", "state_year", "baseline_pop", "land_area_km2",
            "reported_property_damage", "establishment_death_rate", "job_destruction_rate", "log_establishments",
            "log_cbp_employment", "log_payroll", "small_estab_death_rate", "outmigration_rate", "ihs_units"]
    d = pd.read_parquet(PROC / "county_year_panel.parquet", columns=cols)
    d = d[(d.year >= 1990) & (d.year <= Y1)]
    spc = pd.read_parquet(PROC / "spc_exposure_cy.parquet")
    d = d.merge(spc, how="left", on=["county_fips", "year"])
    lp = pd.read_parquet(PROC / "land_productivity_cy.parquet")
    d = d.merge(lp, how="left", on=["county_fips", "year"])
    flow, oper = spending()
    d = d.merge(flow, how="left", on=["county_fips", "year"]).merge(oper, how="left", on=["county_fips", "year"])
    d[["new_fed", "new_proj", "oper_fed"]] = d[["new_fed", "new_proj", "oper_fed"]].fillna(0)
    d = d.sort_values(["county_fips", "year"])
    g = d.groupby("county_fips")
    pop = d.baseline_pop.clip(lower=100)
    # operational stock available at the START of year t (projects operational by t-1)
    d["stock_fed"] = g.oper_fed.cumsum() - d.oper_fed
    d["S"] = np.log1p(d.stock_fed / pop)                       # log(1 + $ per capita)
    d["new_any"] = (d.new_proj > 0).astype(int)
    d["new_log_pc"] = np.log1p(d.new_fed / pop)
    for k in range(1, 5):
        d[f"E_L{k}"] = g.spc_pop_hit.shift(k)
        d[f"lpe_L{k}"] = g.log_pop_exposed.shift(k)
    for k in (1, 2):
        d[f"E_F{k}"] = g.spc_pop_hit.shift(-k)
    d["E"] = d.spc_pop_hit
    d["E_mar"] = d.mar_spc_pop_hit
    d["E01"] = ((d.E == 1) | (d.E_L1 == 1)).astype(int)        # hit in t or t-1 (GDP/crops respond with a lag)
    # pre-period exposure 1980-1995 (precedes every strict obligation) per 1,000 residents
    pre = pd.read_parquet(PROC / "spc_exposure_cy.parquet")
    pre = pre[pre.year.between(1990, 1995)]                    # grid starts 1990; add 1980-89 from tracks
    tr = pd.read_parquet(PROC / "spc_tracks.parquet")
    h = tr[tr.yr.between(1980, 1995)].groupby("county_fips").agg(h_pop=("pop_exposed", "sum"), h_sw=("swept_km2", "sum"))
    d = d.merge(h.reset_index(), how="left", on="county_fips")
    d[["h_pop", "h_sw"]] = d[["h_pop", "h_sw"]].fillna(0)
    d["H"] = np.log1p(1000 * d.h_pop / pop)                     # pre-1996 people-in-path per 1,000 residents
    # eventual total spending (for placebo / tiers)
    tot = d.groupby("county_fips").oper_fed.sum()
    d["tot_pc"] = d.county_fips.map(tot) / pop
    d["S_ever"] = np.log1p(d.tot_pc)
    tpc = d.drop_duplicates("county_fips").set_index("county_fips").tot_pc
    med = tpc[tpc > 0].median()
    d["tier_low"] = ((d.stock_fed > 0) & (d.stock_fed / pop <= med)).astype(int)
    d["tier_high"] = ((d.stock_fed / pop) > med).astype(int)
    # instrument: leave-own-county-out state operational stock per state resident x pre-period exposure
    st = d.groupby(["state_fips", "year"]).agg(st_stock=("stock_fed", "sum"), st_pop=("baseline_pop", "sum")).reset_index()
    d = d.merge(st, how="left", on=["state_fips", "year"])
    d["pool"] = np.log1p((d.st_stock - d.stock_fed) / (d.st_pop - d.baseline_pop).clip(lower=1000))
    d["Z"] = d.pool * d.H
    d["casualties"] = d.spc_inj + d.spc_fat
    d["log_cas"] = np.log1p(d.casualties)
    d["log_dmg"] = np.log1p(d.reported_property_damage)
    log.info("spending tiers: median eventual strict fed $/capita among treated = %.1f", med)
    _ = pre
    return d


# ----------------------------------------------------------------------------- helpers
def fit(fml, data, vc=None, label=""):
    vc = vc or {"CRV1": "county_fips"}
    try:
        m = pf.feols(fml, data=data, vcov=vc)
        t = m.tidy().reset_index().rename(columns={"Coefficient": "term"})
        t["model"], t["N"], t["label"] = fml, m._N, label
        return m, t
    except Exception as e:  # noqa: BLE001
        log.warning("failed %s: %s", fml, e)
        return None, pd.DataFrame()


def iv2(s, y, exog, endog, inst):
    """2SLS with county + state-year FE partialled out (FWL), county-clustered SEs.
    pyfixest supports only one endogenous regressor; here E*S and S are both endogenous."""
    from linearmodels.iv import IV2SLS
    from pyfixest.estimation import demean
    cols = [y] + exog + endog + inst
    s = s.dropna(subset=cols)
    fl = np.column_stack([pd.factorize(s.county_fips)[0], pd.factorize(s.state_year)[0]]).astype(np.uintp)
    X, ok = demean(s[cols].to_numpy(np.float64), fl, np.ones(len(s)), tol=1e-8, maxiter=10_000)
    D = pd.DataFrame(X, columns=cols, index=s.index)
    m = IV2SLS(D[y], D[exog], D[endog], D[inst]).fit(cov_type="clustered", clusters=pd.factorize(s.county_fips)[0])
    t = pd.DataFrame({"term": m.params.index, "Estimate": m.params.values, "Std. Error": m.std_errors.values,
                      "Pr(>|t|)": m.pvalues.values})
    t["model"], t["N"], t["label"] = f"IV {y}", len(s), f"E:{y}"
    fs = m.first_stage.diagnostics
    t["fs_partialF_min"] = float(fs["f.stat"].min())
    return t


def row(t, term):
    r = t[t.term == term]
    if r.empty:
        return dict(b=np.nan, se=np.nan, p=np.nan)
    r = r.iloc[0]
    return dict(b=r["Estimate"], se=r["Std. Error"], p=r["Pr(>|t|)"])


FE = "county_fips + state_year"
OUTCOMES = [  # (var, label, exposure col, years)
    ("log_gdp_per_ha", "Real GDP per hectare (log, BEA)", "E", (2001, 2024)),
    ("log_ag_gdp_per_ha", "Agricultural real GDP per hectare (log, BEA)", "E", (2001, 2024)),
    ("log_crop_rcpt_per_ha", "Crop cash receipts per hectare (log, BEA)", "E", (1999, 2022)),
    ("log_crop_t_per_ha", "Crop yield, corn+soy+wheat t/ha (log, NASS)", "E", (1999, 2024)),
    ("log_dmg", "Reported property damage (log1p $, NOAA)", "E", (1999, 2024)),
    ("log_cas", "Tornado casualties (log1p inj+fat, SPC)", "E", (1999, 2024)),
    ("establishment_death_rate", "Establishment death rate (BDS)", "E_mar", (1999, 2023)),
    ("job_destruction_rate", "Job destruction rate (BDS)", "E_mar", (1999, 2023)),
    ("small_estab_death_rate", "Small-firm estab. death rate (BDS)", "E_mar", (1999, 2023)),
    ("log_cbp_employment", "Employment (log, CBP)", "E_mar", (1999, 2023)),
    ("log_establishments", "Establishments (log, CBP)", "E_mar", (1999, 2023)),
    ("outmigration_rate", "Out-migration rate (IRS)", "E", (1999, 2022)),
]


def main() -> None:
    d = build_panel()
    d = d[d.state_year.notna()]
    a = d[d.year.between(Y0, Y1)].copy()
    res = []

    # ---------------- B1 first stage, panel flows
    lags = " + ".join(["E"] + [f"E_L{k}" for k in range(1, 5)])
    fs_rows = []
    for dep in ["new_any", "new_log_pc"]:
        m, t = fit(f"{dep} ~ {lags} + E_F1 + E_F2 | {FE}", a, label="B1")
        res.append(t)
        for term in ["E_F2", "E_F1", "E", "E_L1", "E_L2", "E_L3", "E_L4"]:
            fs_rows.append({"dep": dep, "term": term, **row(t, term), "N": m._N if m else np.nan,
                            "dep_mean": a[dep].mean()})
        m, t = fit(f"{dep} ~ log_pop_exposed + lpe_L1 + lpe_L2 + lpe_L3 + lpe_L4 | {FE}", a, label="B1c")
        res.append(t)
        for term in ["log_pop_exposed", "lpe_L1", "lpe_L2", "lpe_L3", "lpe_L4"]:
            fs_rows.append({"dep": dep, "term": term, **row(t, term), "N": m._N if m else np.nan,
                            "dep_mean": a[dep].mean()})
    fs = pd.DataFrame(fs_rows)
    fs.to_csv(TABLES / "redesign_first_stage_panel.csv", index=False)
    log.info("B1 first stage:\n%s", fs.round(4).to_string())

    # ---------------- B2 cross-section
    cs = d.drop_duplicates("county_fips").copy()
    cs["ever"] = (cs.tot_pc > 0).astype(int)
    cs["log_pop"] = np.log(cs.baseline_pop.clip(lower=100))
    cs["log_land"] = np.log(cs.land_area_km2)
    cs["h_swept_share"] = 1000 * cs.h_sw / cs.land_area_km2
    cs_rows = []
    for dep in ["S_ever", "ever"]:
        for x in ["H", "h_swept_share"]:
            m, t = fit(f"{dep} ~ {x} + log_pop + log_land | state_fips", cs, vc={"CRV1": "state_fips"}, label="B2")
            res.append(t)
            cs_rows.append({"dep": dep, "x": x, **row(t, x), "N": m._N if m else np.nan, "x_sd": cs[x].std(),
                            "dep_mean": cs[dep].mean()})
    cs_t = pd.DataFrame(cs_rows)
    cs_t["effect_of_1sd"] = cs_t.b * cs_t.x_sd
    cs_t.to_csv(TABLES / "redesign_first_stage_cross_section.csv", index=False)
    log.info("B2 cross-section:\n%s", cs_t.round(4).to_string())

    # ---------------- B3 instrument first stage
    m, t = fit(f"S ~ Z | {FE}", a, label="B3")
    res.append(t)
    z_fs = {**row(t, "Z"), "F": (row(t, "Z")["b"] / row(t, "Z")["se"]) ** 2, "N": m._N}
    log.info("B3 instrument first stage S ~ Z: %s", z_fs)

    # ---------------- A + C dose-response, tiers; D placebo; E 2SLS
    out = []
    for y, lab, ecol, (lo, hi) in OUTCOMES:
        s = a[a.year.between(lo, hi) & a[y].notna()].copy()
        if s.empty or s[y].nunique() < 3:
            out.append({"outcome": lab, "status": "no data"})
            continue
        s["Ex"] = s[ecol].fillna(0)
        s["ExS"] = s.Ex * s.S
        s["Ex_lo"], s["Ex_hi"] = s.Ex * s.tier_low, s.Ex * s.tier_high
        s["ExZ"] = s.Ex * s.Z
        r = {"outcome": lab, "var": y, "exposure": ecol, "N": len(s), "counties": s.county_fips.nunique(),
             "y_mean": s[y].mean(), "y_sd": s[y].std(), "treated_exposed_obs": int(((s.Ex > 0) & (s.S > 0)).sum())}
        # A: exposure main effect alone
        _, t = fit(f"{y} ~ Ex | {FE}", s, label=f"A:{y}")
        res.append(t)
        r.update({f"A_E_{k}": v for k, v in row(t, "Ex").items()})
        # C: dose
        _, t = fit(f"{y} ~ ExS + Ex + S | {FE}", s, label=f"C:{y}")
        res.append(t)
        r.update({f"C_ExS_{k}": v for k, v in row(t, "ExS").items()})
        r.update({f"C_E_{k}": v for k, v in row(t, "Ex").items()})
        r.update({f"C_S_{k}": v for k, v in row(t, "S").items()})
        # C-tiers
        _, t = fit(f"{y} ~ Ex_lo + Ex_hi + Ex + tier_low + tier_high | {FE}", s, label=f"Ct:{y}")
        res.append(t)
        r.update({f"T_lo_{k}": v for k, v in row(t, "Ex_lo").items()})
        r.update({f"T_hi_{k}": v for k, v in row(t, "Ex_hi").items()})
        # C-lag: exposure in t or t-1 (calendar outcomes)
        if ecol == "E":
            s["E01S"] = s.E01 * s.S
            _, t = fit(f"{y} ~ E01S + E01 + S | {FE}", s, label=f"Cl:{y}")
            res.append(t)
            r.update({f"CL_ExS_{k}": v for k, v in row(t, "E01S").items()})
        # D: placebo on not-yet-treated periods: does eventual spending already shape exposure response?
        pre = s[s.stock_fed == 0].copy()
        pre["ExSe"] = pre.Ex * pre.S_ever
        _, t = fit(f"{y} ~ ExSe + Ex | {FE}", pre, label=f"D:{y}")
        res.append(t)
        r.update({f"D_plac_{k}": v for k, v in row(t, "ExSe").items()})
        # E: 2SLS
        try:
            t = iv2(s, y, ["Ex"], ["ExS", "S"], ["ExZ", "Z"])
            res.append(t)
            r.update({f"IV_ExS_{k}": v for k, v in row(t, "ExS").items()})
            r["IV_fsF_min"] = t.fs_partialF_min.iloc[0]
        except Exception as e:  # noqa: BLE001
            log.warning("IV failed %s: %s", y, e)
            r.update(IV_ExS_b=np.nan, IV_ExS_se=np.nan, IV_ExS_p=np.nan)
        out.append(r)
        log.info("%s: A_E=%.4f(p%.3f) C_ExS=%.4f(p%.3f) tiers lo=%.4f hi=%.4f placebo=%.4f(p%.3f) IV=%.4f(p%.3f)",
                 y, r["A_E_b"], r["A_E_p"], r["C_ExS_b"], r["C_ExS_p"], r["T_lo_b"], r["T_hi_b"],
                 r["D_plac_b"], r["D_plac_p"], r["IV_ExS_b"], r["IV_ExS_p"])
    o = pd.DataFrame(out)
    o.to_csv(TABLES / "redesign_dose_response.csv", index=False)
    pd.concat(res, ignore_index=True).to_csv(TABLES / "redesign_all_coefficients.csv", index=False)
    pd.DataFrame([z_fs]).to_csv(TABLES / "redesign_instrument_first_stage.csv", index=False)
    d[["county_fips", "year", "S", "stock_fed", "tot_pc", "H", "Z"]].to_parquet(PROC / "redesign_spending_cy.parquet", index=False)
    log.info("done")


if __name__ == "__main__":
    main()
