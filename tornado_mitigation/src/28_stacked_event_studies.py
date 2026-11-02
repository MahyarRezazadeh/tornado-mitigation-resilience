"""Modern staggered-adoption estimators for the Mitigation x Tornado interaction (Section 26).

1. Stacked mitigation-cohort triple difference (Cengiz et al. 2019 / Callaway-Sant'Anna-type clean
   comparisons): stacks = 3-year adoption-cohort bins; controls = never treated or first treated after
   the stack window; Y ~ MT + M + T | stack^county + stack^state^time.
2. Interaction-weighted (IW) estimate: stack-specific betas averaged with weights = treated tornado obs.
3. Stacked clean tornado event study: events = EF1+ county-quarters (years for annual) with no EF1+ in the
   prior 8 quarters (3 years); controls = same-state counties with no EF1+ in the window; counties whose
   mitigation status changes inside the window are dropped. th_k = Event x Mitigated x k.
Outputs: output/models/estimator_comparison.csv, stacked_tornado_es_*.csv, stacked_es_summary.csv
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pyfixest as pf

import est
from utils import MODELS, get_logger

log = get_logger(__file__)
_wald = __import__("27_event_studies").wald
PRIMARY = [("log_employment", "q", "mar"), ("separation_rate", "q", "mar"), ("log_earnings", "q", "mar"),
           ("establishment_death_rate", "y", "mar"), ("job_destruction_rate", "y", "mar")]
SECONDARY = [("hire_rate", "q", "mar"), ("job_destruction_rate_qwi", "q", "mar"), ("outmigration_rate", "y", "mar"),
             ("log_establishments", "y", "mar"), ("small_estab_death_rate", "y", "mar"), ("ihs_units", "y", "cal")]


def stacked_cohort(var, freq, align):
    s = est.Spec(outcome=var, freq=freq, align=align)
    d, yv = est.build(s)
    ft = d[est.ft_col(s)].astype(float)
    fy = ft // 10
    pre_w, post_w, binw = 5, 8, 3
    lo, hi = int(d.year.min()), int(d.year.max())
    stacks, iw = [], []
    for b in range(lo + 2, hi - 1, binw):
        tr = fy.between(b, b + binw - 1)
        if tr.sum() == 0:
            continue
        ctrl = fy.isna() | (fy > b + binw - 1 + post_w)
        win = d.year.between(b - pre_w, b + binw - 1 + post_w)
        sd = d[(tr | ctrl) & win].copy()
        sd["ever"] = tr[(tr | ctrl) & win].astype(int)
        sd["M"] = sd["M"] * sd["ever"]
        sd["MT"] = sd["M"] * sd["T"]
        sd["stack"] = b
        if sd["MT"].sum() == 0:
            continue
        stacks.append(sd)
        try:
            st = "state_yq" if freq == "q" else "state_year"
            f = pf.feols(f"{yv} ~ MT + M + T | county_fips + {st}", data=sd, vcov={"CRV1": "county_fips"})
            iw.append({"stack": b, "beta": f.coef()["MT"], "se": f.se()["MT"], "w": float(sd["MT"].gt(0).sum())})
        except Exception:  # noqa: BLE001
            pass
    S = pd.concat(stacks, ignore_index=True)
    tcol = est.time_col(freq)
    S["sc"] = S["stack"].astype(str) + "_" + S["county_fips"]
    S["sst"] = S["stack"].astype(str) + "_" + S["state_fips"] + "_" + S[tcol].astype(str)
    f = pf.feols(f"{yv} ~ MT + M + T | sc + sst", data=S, vcov={"CRV1": "county_fips"})
    tb = f.tidy().loc["MT"]
    iwd = pd.DataFrame(iw)
    w = iwd.w / iwd.w.sum()
    iw_b = float((w * iwd.beta).sum())
    iw_se = float(np.sqrt((w ** 2 * iwd.se ** 2).sum()))
    return {"stacked_beta": tb["Estimate"], "stacked_se": tb["Std. Error"], "stacked_p": tb["Pr(>|t|)"],
            "stacked_N": int(f._N), "n_stacks": S["stack"].nunique(),
            "iw_beta": iw_b, "iw_se": iw_se, "iw_p": float(2 * (1 - __import__("scipy").stats.norm.cdf(abs(iw_b / iw_se)))),
            "iw_n_cohorts": len(iwd)}


def stacked_tornado(var, freq, align):
    kmin, kmax, clean = ((-8, 12, 8) if freq == "q" else (-5, 8, 3))
    s = est.Spec(outcome=var, freq=freq, align=align)
    d, yv = est.build(s)
    tcol = est.time_col(freq)
    full, _ = est.build(s.but(outcome="EF1_plus" if freq == "q" else ("mar_EF1_plus" if align == "mar" else "EF1_plus")))
    idx = "t" if freq == "q" else "year"
    full = full.sort_values(["county_fips", idx])
    T = full.pivot(index="county_fips", columns=idx, values="T").fillna(0)
    M = full.pivot(index="county_fips", columns=idx, values="M").fillna(0)
    cols = T.columns.values
    Tv, Mv = T.values > 0, M.values
    csum = np.cumsum(np.c_[np.zeros(len(T)), Tv], axis=1)
    def cnt(a, b):  # tornado count in [a, b] column positions (clipped)
        a2, b2 = max(a, 0), min(b, len(cols) - 1)
        return csum[:, b2 + 1] - csum[:, a2]
    dd = d.set_index(["county_fips", idx])
    stacks = []
    st_of = full.drop_duplicates("county_fips").set_index("county_fips")["state_fips"]
    for j in range(-kmin + clean, len(cols) - kmax):
        ev = Tv[:, j] & (cnt(j - clean, j - 1) == 0)
        if ev.sum() == 0:
            continue
        clean_ctrl = cnt(j + kmin, j + kmax) == 0
        stable = (Mv[:, j + kmin] == Mv[:, j + kmax])
        units = T.index[(ev | clean_ctrl) & stable]
        ev_units = set(T.index[ev & stable])
        states = set(st_of.reindex(list(ev_units)))
        has_y = set(dd.index.get_level_values(0))
        ev_units = {u for u in ev_units if u in has_y}
        if not ev_units:
            continue
        ctrl = [u for u in units if st_of.get(u) in states and u not in ev_units and u in has_y]
        # memory (8GB machine): up to 3 same-state clean controls per event county, seeded per stack
        rng = np.random.default_rng(20261007 + int(j))
        if len(ctrl) > 3 * len(ev_units):
            ctrl = list(rng.choice(ctrl, 3 * len(ev_units), replace=False))
        units = list(ev_units) + ctrl
        per = cols[j + kmin: j + kmax + 1]
        sub = pd.DataFrame([(u, p) for u in units for p in per], columns=["county_fips", idx])
        sub = sub.join(dd[[yv, "state_fips"]], on=["county_fips", idx], how="inner")
        sub["k"] = sub[idx] - cols[j]
        sub["E"] = sub.county_fips.isin(ev_units).astype(int)
        sub["Mc"] = sub.county_fips.map(pd.Series(Mv[:, j], index=T.index))
        sub["stack"] = j
        stacks.append(sub)
    S = pd.concat(stacks, ignore_index=True)
    S = S[S[yv].notna()]
    terms_e, terms_em, terms_m = [], [], []
    for k in range(kmin, kmax + 1):
        if k == -1:
            continue
        nm = f"m{abs(k)}" if k < 0 else f"p{k}"
        Dk = (S.k == k).astype(np.int8)
        S[f"E_{nm}"] = Dk * S.E
        S[f"EM_{nm}"] = Dk * S.E * S.Mc
        S[f"M_{nm}"] = Dk * S.Mc
        terms_e.append(f"E_{nm}")
        terms_em.append(f"EM_{nm}")
        terms_m.append(f"M_{nm}")
    S["sc"] = S["stack"].astype(str) + "_" + S.county_fips
    S["stime"] = S["stack"].astype(str) + "_" + S.k.astype(str) + "_" + S.state_fips
    f = pf.feols(f"{yv} ~ {' + '.join(terms_e + terms_em + terms_m)} | sc + stime", data=S,
                 vcov={"CRV1": "county_fips"})
    tb = f.tidy()
    rows = []
    for e, em in zip(terms_e, terms_em):
        k = -int(e.split("_")[1][1:]) if e.split("_")[1][0] == "m" else int(e.split("_")[1][1:])
        rows.append({"k": k, "unmitigated": tb.loc[e, "Estimate"], "unmitigated_se": tb.loc[e, "Std. Error"],
                     "diff": tb.loc[em, "Estimate"] if em in tb.index else np.nan,
                     "diff_se": tb.loc[em, "Std. Error"] if em in tb.index else np.nan})
    res = pd.DataFrame(rows).sort_values("k")
    pre = [t for t in terms_em if t.split("_")[1][0] == "m" and t in tb.index]
    post = [t for t in terms_em if t.split("_")[1][0] == "p" and t in tb.index]
    G = S.county_fips.nunique()
    F, p = _wald(f, pre, G)
    names = list(f.coef().index)
    V = f._vcov
    ip = [names.index(t) for t in post]
    w = np.ones(len(ip)) / len(ip)
    avg = float(w @ f.coef().values[ip])
    avg_se = float(np.sqrt(w @ V[np.ix_(ip, ip)] @ w))
    n_ev = int(S[(S.E == 1)].groupby("stack").county_fips.nunique().sum())
    n_ev_m = int(S[(S.E == 1) & (S.Mc == 1)].groupby("stack").county_fips.nunique().sum())
    return res, {"stacked_es_pretrend_F": F, "stacked_es_pretrend_p": p, "stacked_es_avg_post_diff": avg,
                 "stacked_es_avg_post_diff_se": avg_se, "stacked_es_events": n_ev, "stacked_es_mitigated_events": n_ev_m,
                 "stacked_es_N": int(f._N)}


def main() -> None:
    rows = []
    for var, freq, align in PRIMARY + SECONDARY:
        r = {"outcome": var}
        base = est.run(est.Spec(outcome=var, freq=freq, align=align))
        r.update({"twfe_beta": base.get("beta"), "twfe_se": base.get("se"), "twfe_p": base.get("p")})
        try:
            r.update(stacked_cohort(var, freq, align))
        except Exception as e:  # noqa: BLE001
            log.error("stacked cohort %s: %s", var, e)
        try:
            res, s = stacked_tornado(var, freq, align)
            res.to_csv(MODELS / f"stacked_tornado_es_{var}.csv", index=False)
            r.update(s)
        except Exception as e:  # noqa: BLE001
            log.error("stacked tornado ES %s: %s", var, e)
        rows.append(r)
        log.info("%s: TWFE %.4g | stacked %.4g | IW %.4g | stackedES post %.4g (pre p=%.3f)", var,
                 r.get("twfe_beta", np.nan), r.get("stacked_beta", np.nan), r.get("iw_beta", np.nan),
                 r.get("stacked_es_avg_post_diff", np.nan), r.get("stacked_es_pretrend_p", np.nan))
    pd.DataFrame(rows).to_csv(MODELS / "estimator_comparison.csv", index=False)


if __name__ == "__main__":
    main()
