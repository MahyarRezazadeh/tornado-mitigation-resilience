"""Dynamic designs (Sections 27-28, Outcome 4 recovery).

A. Tornado event study (distributed-lag form for recurrent events, Schmidheiny & Siegloch 2023):
   Y_ct = sum_k d_k T_{c,t-k} + sum_k th_k T_{c,t-k} M_{c,t-k} + M_ct + county FE + state x time FE
   k = -8..12 quarters (annual: -5..8 years), k = -1 omitted. th_k = differential response of mitigated
   tornado events. Pre-trend: joint test th_k = 0 for k <= -2 (cluster-robust Wald, F(J, G-1)).
B. Mitigation-adoption event study (diagnostic): TWFE dummies and Sun-Abraham (cohort x relative-time,
   never-treated control, cohort-share aggregation); Gardner did2s where estimable.
Outputs: output/models/tornado_es_*.csv, adoption_es_*.csv, event_study_summary.csv, recovery_metrics.csv
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pyfixest as pf
from scipy import stats

import est
from utils import MODELS, get_logger

log = get_logger(__file__)
OUTS = [("log_employment", "q"), ("separation_rate", "q"), ("log_earnings", "q"), ("hire_rate", "q"),
        ("job_destruction_rate_qwi", "q"), ("establishment_death_rate", "y"), ("job_destruction_rate", "y"),
        ("log_qcew_emp", "q")]


def lag_design(d: pd.DataFrame, freq: str, kmin: int, kmax: int) -> tuple[pd.DataFrame, list, list]:
    tcol = est.time_col(freq)
    d = d.sort_values(["county_fips", tcol]).copy()
    d["_idx"] = d["t"] if freq == "q" else d["year"]
    g = d.groupby("county_fips")
    Ls, MLs = [], []
    for k in range(kmin, kmax + 1):
        if k == -1:
            continue
        nm = f"m{abs(k)}" if k < 0 else f"p{k}"
        sh_T = g["T"].shift(k)
        sh_M = g["M"].shift(k)
        sh_i = g["_idx"].shift(k)
        ok = (d["_idx"] - sh_i) == k             # guard against gaps
        d[f"L_{nm}"] = sh_T.where(ok).fillna(0)
        d[f"ML_{nm}"] = (sh_T * sh_M).where(ok).fillna(0)
        Ls.append(f"L_{nm}")
        MLs.append(f"ML_{nm}")
    return d, Ls, MLs


def kval(nm: str) -> int:
    s = nm.split("_")[1]
    return -int(s[1:]) if s[0] == "m" else int(s[1:])


def wald(fit, names: list[str], G: int) -> tuple[float, float]:
    b = fit.coef()[names].values
    V = fit._vcov
    idx = [list(fit.coef().index).index(n) for n in names]
    Vs = V[np.ix_(idx, idx)]
    try:
        F = float(b @ np.linalg.pinv(Vs) @ b) / len(names)
    except Exception:  # noqa: BLE001
        return np.nan, np.nan
    return F, float(1 - stats.f.cdf(F, len(names), G - 1))


def tornado_es(var: str, freq: str, spec_kw: dict | None = None) -> tuple[pd.DataFrame, dict]:
    kmin, kmax = (-8, 12) if freq == "q" else (-5, 8)
    s = est.Spec(outcome=var, freq=freq, **(spec_kw or {}))
    full = est.panel(freq)
    s_all = s.but()
    d, yv = est.build(s_all.but(sample={**s_all.sample}))
    # rebuild lags on the full grid (build drops missing y) -> recompute on full panel then filter
    dd, _ = est.build(s.but(outcome="EF1_plus" if freq == "q" else "mar_EF1_plus"))
    dd = dd[["county_fips", est.time_col(freq), "T", "M", "t" if freq == "q" else "year"]].copy() \
        if freq == "q" else dd[["county_fips", "year", "T", "M"]].copy()
    dd, Ls, MLs = lag_design(dd, freq, kmin, kmax)
    tcol = est.time_col(freq)
    d = d.merge(dd[["county_fips", tcol] + Ls + MLs], on=["county_fips", tcol], how="left")
    st = "state_yq" if freq == "q" else "state_year"
    fml = f"{yv} ~ {' + '.join(Ls + MLs)} + M | county_fips + {st}"
    fit = pf.feols(fml, data=d, vcov={"CRV1": "county_fips"})
    tb = fit.tidy()
    rows = []
    for L, ML in zip(Ls, MLs):
        k = kval(L)
        rows.append({"k": k, "unmitigated": tb.loc[L, "Estimate"], "unmitigated_se": tb.loc[L, "Std. Error"],
                     "diff": tb.loc[ML, "Estimate"], "diff_se": tb.loc[ML, "Std. Error"],
                     "diff_p": tb.loc[ML, "Pr(>|t|)"]})
    res = pd.DataFrame(rows)
    # mitigated response = d_k + th_k with covariance
    V = fit._vcov
    names = list(fit.coef().index)
    se_m = []
    for L, ML in zip(Ls, MLs):
        i, j = names.index(L), names.index(ML)
        se_m.append(np.sqrt(V[i, i] + V[j, j] + 2 * V[i, j]))
    res["mitigated"] = res["unmitigated"] + res["diff"]
    res["mitigated_se"] = se_m
    res = pd.concat([res, pd.DataFrame([{"k": -1, "unmitigated": 0, "unmitigated_se": 0, "diff": 0, "diff_se": 0,
                                         "mitigated": 0, "mitigated_se": 0}])]).sort_values("k")
    G = d.county_fips.nunique()
    pre = [m for m in MLs if kval(m) <= -2]
    post = [m for m in MLs if kval(m) >= 0]
    F, p = wald(fit, pre, G)
    Fpost, ppost = wald(fit, post, G)
    Fu, pu = wald(fit, [L for L in Ls if kval(L) <= -2], G)
    summ = {"outcome": var, "freq": freq, "pretrend_F": F, "pretrend_p": p, "post_joint_F": Fpost,
            "post_joint_p": ppost, "pretrend_unmitigated_p": pu, "N": int(fit._N),
            "mean_post_diff": res.loc[res.k >= 0, "diff"].mean(),
            "mean_post_unmitigated": res.loc[res.k >= 0, "unmitigated"].mean(),
            "avg_post_diff_se": np.sqrt(np.diag(V[np.ix_([names.index(m) for m in post], [names.index(m) for m in post])]).sum()) / len(post)}
    return res, summ


def recovery(res: pd.DataFrame, var: str, freq: str) -> dict:
    out = {"outcome": var}
    pre = res[(res.k <= -2)]
    for grp in ["unmitigated", "mitigated"]:
        path = res[res.k >= 0].set_index("k")[grp]
        slope = np.polyfit(pre.k, pre[grp], 1)[0] if len(pre) > 2 else 0.0
        trend_adj = path - slope * path.index
        trough_k = path.idxmin() if var in ("log_employment", "log_qcew_emp", "log_earnings") else path.idxmax()
        trough = path.loc[trough_k]
        for h in ([4, 8, 12] if freq == "q" else [1, 2, 4]):
            out[f"{grp}_recovery_{h}{'q' if freq == 'q' else 'y'}"] = path.get(h, np.nan)
        after = path.loc[trough_k:]
        sign = 1 if var in ("log_employment", "log_qcew_emp", "log_earnings") else -1
        if sign * trough < 0:
            t95 = after[sign * after >= sign * 0.05 * trough]
            t100 = after[sign * after >= 0]
            tpt = trend_adj.loc[trough_k:][sign * trend_adj.loc[trough_k:] >= 0]
            out[f"{grp}_time_to_95pct_recovery"] = (t95.index[0] - trough_k) if len(t95) else np.nan
            out[f"{grp}_time_to_100pct_recovery"] = (t100.index[0] - trough_k) if len(t100) else np.nan
            out[f"{grp}_time_to_pretrend_recovery"] = (tpt.index[0] - trough_k) if len(tpt) else np.nan
        out[f"{grp}_trough"] = trough
        out[f"{grp}_trough_k"] = trough_k
    return out


def adoption_es(var: str, freq: str) -> tuple[pd.DataFrame, dict]:
    kmin, kmax = (-8, 12) if freq == "q" else (-5, 8)
    s = est.Spec(outcome=var, freq=freq)
    d, yv = est.build(s)
    tcol = est.time_col(freq)
    ft = d[est.ft_col(s)]
    if freq == "q":
        fidx = (ft // 10 - est.panel("q").year.min()) * 4 + ft % 10 - 1
        d["rel"] = d["t"] - fidx
        d["cohort"] = ft // 10
    else:
        d["rel"] = d["year"] - (ft // 10 + 1)      # first March-aligned year with M = 1 (approx.)
        d["cohort"] = ft // 10
    d["relb"] = d["rel"].clip(kmin, kmax)
    tr = d.ever == 1
    st = "state_yq" if freq == "q" else "state_year"
    # TWFE dynamic
    for k in range(kmin, kmax + 1):
        if k != -1:
            d[f"D_{k}".replace("-", "m")] = (tr & (d.relb == k)).astype(int)
    D = [c for c in d.columns if c.startswith("D_")]
    fit = pf.feols(f"{yv} ~ {' + '.join(D)} | county_fips + {st}", data=d, vcov={"CRV1": "county_fips"})
    tb = fit.tidy()
    rows = [{"k": int(c[2:].replace("m", "-")), "twfe": tb.loc[c, "Estimate"], "twfe_se": tb.loc[c, "Std. Error"]}
            for c in D if c in tb.index]
    res = pd.DataFrame(rows)
    # Sun-Abraham: cohort x rel interactions, never-treated controls; aggregate by cohort share
    dd = d[(~tr) | d.rel.between(kmin, kmax)].copy()
    dd["coh"] = dd["cohort"].fillna(0).astype(int)
    cell = dd[dd.ever == 1].groupby(["coh", "rel"]).size()
    keep = cell[cell >= 5].index
    sa_terms = []
    for (c, k) in keep:
        if k == -1:
            continue
        nm = f"SA_{c}_{k}".replace("-", "m")
        dd[nm] = ((dd.coh == c) & (dd.rel == k)).astype(np.int8)
        sa_terms.append((nm, c, k))
    if sa_terms:
        fit2 = pf.feols(f"{yv} ~ {' + '.join(n for n, _, _ in sa_terms)} | county_fips + {st}", data=dd,
                        vcov={"CRV1": "county_fips"})
        cf, V = fit2.coef(), fit2._vcov
        names = list(cf.index)
        sa = []
        for k in range(kmin, kmax + 1):
            if k == -1:
                continue
            terms = [(n, c) for n, c, kk in sa_terms if kk == k and n in names]
            if not terms:
                continue
            w = np.array([cell.get((c, k), 0) for _, c in terms], float)
            w = w / w.sum()
            idx = [names.index(n) for n, _ in terms]
            est_k = float(w @ cf.values[idx])
            se_k = float(np.sqrt(w @ V[np.ix_(idx, idx)] @ w))
            sa.append({"k": k, "sun_abraham": est_k, "sun_abraham_se": se_k})
        res = res.merge(pd.DataFrame(sa), on="k", how="outer")
    # Gardner (2021) two-stage imputation: stage 1 FE on untreated obs, stage 2 on imputed residuals.
    # Stage-2 SEs are clustered by county but not corrected for stage-1 estimation (noted in report).
    try:
        un = d[d.M == 0]
        f1 = pf.feols(f"{yv} ~ 1 | county_fips + {st}", data=un)
        d2 = d.copy()
        d2["yhat0"] = f1.predict(newdata=d2)
        d2["ytil"] = d2[yv] - d2["yhat0"]
        d2 = d2[d2.ytil.notna() & tr & d2.rel.between(kmin, kmax)]
        terms = []
        for k in range(kmin, kmax + 1):
            nm = f"G_{k}".replace("-", "m")
            d2[nm] = (d2.rel == k).astype(int)
            terms.append(nm)
        f3 = pf.feols(f"ytil ~ {' + '.join(terms)} - 1", data=d2, vcov={"CRV1": "county_fips"})
        tb3 = f3.tidy()
        g = [{"k": int(t[2:].replace("m", "-")), "did2s": tb3.loc[t, "Estimate"], "did2s_se": tb3.loc[t, "Std. Error"]}
             for t in terms if t in tb3.index]
        res = res.merge(pd.DataFrame(g), on="k", how="outer")
    except Exception as e:  # noqa: BLE001
        log.warning("two-stage imputation failed for %s: %s", var, str(e)[:150])
    res = res.sort_values("k")
    pre = res[res.k <= -2]
    summ = {"outcome": var, "adoption_pre_mean_twfe": pre["twfe"].mean(),
            "adoption_pre_mean_sa": pre.get("sun_abraham", pd.Series(dtype=float)).mean(),
            "adoption_post_mean_twfe": res.loc[res.k >= 0, "twfe"].mean(),
            "adoption_post_mean_sa": res.loc[res.k >= 0].get("sun_abraham", pd.Series(dtype=float)).mean()}
    Dpre = [c for c in D if int(c[2:].replace("m", "-")) <= -2]
    summ["adoption_pretrend_F"], summ["adoption_pretrend_p"] = wald(fit, Dpre, d.county_fips.nunique())
    return res, summ


def main() -> None:
    import gc
    import sys
    only = set(sys.argv[1:])
    summ, rec, adop = [], [], []
    for var, freq in OUTS:
        if only and var not in only:
            continue
        est._CACHE.clear()
        gc.collect()
        try:
            res, s = tornado_es(var, freq)
            res.to_csv(MODELS / f"tornado_es_{var}.csv", index=False)
            summ.append(s)
            rec.append(recovery(res, var, freq))
            log.info("tornado ES %s: pretrend p=%.3f, mean post diff=%.4g", var, s["pretrend_p"], s["mean_post_diff"])
        except Exception as e:  # noqa: BLE001
            log.error("tornado ES failed %s: %s", var, e)
        try:
            ares, a = adoption_es(var, freq)
            ares.to_csv(MODELS / f"adoption_es_{var}.csv", index=False)
            adop.append(a)
            log.info("adoption ES %s: pre p=%.3f", var, a["adoption_pretrend_p"])
        except Exception as e:  # noqa: BLE001
            log.error("adoption ES failed %s: %s", var, e)
    new = pd.DataFrame(summ).merge(pd.DataFrame(adop), on="outcome", how="outer") if summ or adop else pd.DataFrame()
    newr = pd.DataFrame(rec)
    for df, fn in [(new, "event_study_summary.csv"), (newr, "recovery_metrics.csv")]:
        p = MODELS / fn
        if only and p.exists() and len(df):
            old = pd.read_csv(p)
            df = pd.concat([old[~old.outcome.isin(df.outcome)], df], ignore_index=True)
        if len(df):
            df.to_csv(p, index=False)


if __name__ == "__main__":
    main()
