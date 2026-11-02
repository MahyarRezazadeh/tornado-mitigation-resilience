"""County-level pre-treatment comparison weights (Section 29). Only pre-1990/1990s covariates are used.

Covariates: historical tornado density (1950-89), historical EF2+ density, log 2000 population,
log 1995-99 employment (BDS), establishments per 1,000 residents, metro, region, 1998 CBP industry
shares (construction, manufacturing, retail, health, leisure), 1998 payroll per employee, 1990-99
employment growth (BDS).
Treated = ever strict-treated (primary timing). Methods: entropy balancing (first moments),
IPW (ATT odds weights, trimmed), 1:3 nearest-neighbour on the propensity score (with replacement),
1:3 Mahalanobis nearest neighbour within census region.
Outputs: data/processed/matching_weights.parquet, output/diagnostics/balance_table.csv,
         output/figures/balance_*.png
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.optimize import minimize  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.neighbors import NearestNeighbors  # noqa: E402

from utils import DIAG, FIGS, INTER, PROC, SEED, get_logger  # noqa: E402

log = get_logger(__file__)


def covariates() -> pd.DataFrame:
    cy = pd.read_parquet(PROC / "county_year_panel.parquet")
    b = cy.drop_duplicates("county_fips")[["county_fips", "state_fips", "region", "metro", "baseline_pop",
                                           "baseline_emp", "baseline_estabs", "hist_tornado_density",
                                           "hist_EF2_density", "ft_strict_primary"]].copy()
    g = cy[cy.year.isin([1990, 1999])].pivot(index="county_fips", columns="year", values="emp")
    b = b.merge(np.log(g[1999] / g[1990]).rename("emp_growth_90s").reset_index(), how="left")
    ci = pd.read_parquet(INTER / "cbp_county_industry_year.parquet")
    c98 = ci[ci.year == 1998]
    tot = pd.read_parquet(INTER / "cbp_county_year.parquet").query("year == 1998")[["county_fips", "establishments",
                                                                                   "cbp_employment", "annual_payroll"]]
    sh = c98.pivot_table(index="county_fips", columns="industry_group", values="establishments", aggfunc="sum")
    sh = sh.div(sh.sum(axis=1), axis=0)
    keep = {"Construction": "sh_constr", "Manufacturing": "sh_manuf", "Retail": "sh_retail", "Health": "sh_health",
            "Leisure/Hospitality": "sh_leisure"}
    sh = sh[[k for k in keep if k in sh]].rename(columns=keep).reset_index()
    b = b.merge(sh, how="left").merge(tot, how="left")
    b["log_hist_density"] = np.log1p(b.hist_tornado_density)
    b["log_hist_EF2_density"] = np.log1p(b.hist_EF2_density)
    b["log_pop"] = np.log(b.baseline_pop)
    b["log_emp"] = np.log(b.baseline_emp)
    b["estabs_pc"] = b.baseline_estabs / b.baseline_pop * 1000
    b["pay_per_emp"] = b.annual_payroll / b.cbp_employment
    for r in ["Midwest", "South", "West"]:
        b[f"reg_{r}"] = (b.region == r).astype(int)
    b["treated"] = b.ft_strict_primary.notna().astype(int)
    return b


COVS = ["log_hist_density", "log_hist_EF2_density", "log_pop", "log_emp", "estabs_pc", "metro", "reg_Midwest",
        "reg_South", "reg_West", "sh_constr", "sh_manuf", "sh_retail", "sh_health", "sh_leisure", "pay_per_emp",
        "emp_growth_90s"]


def ebal(X0: np.ndarray, target: np.ndarray) -> np.ndarray:
    Z = (X0 - target)
    sd = Z.std(axis=0) + 1e-9
    Z = Z / sd
    def obj(lam):
        e = np.exp(Z @ lam)
        return np.log(e.sum()), (Z * e[:, None]).sum(0) / e.sum()
    res = minimize(lambda l: obj(l)[0], np.zeros(Z.shape[1]), jac=lambda l: obj(l)[1], method="BFGS",
                   options={"maxiter": 2000})
    w = np.exp(Z @ res.x)
    return w / w.sum() * len(w)


def smd(x, t, w):
    x1, x0 = x[t == 1], x[t == 0]
    w1, w0 = w[t == 1], w[t == 0]
    m1, m0 = np.average(x1, weights=w1), np.average(x0, weights=w0)
    v = (x1.var() + x0.var()) / 2
    return (m1 - m0) / np.sqrt(v) if v > 0 else 0.0


def main() -> None:
    b = covariates()
    d = b.dropna(subset=COVS).copy()
    log.info("matching sample: %d counties (%d treated); dropped %d with missing covariates",
             len(d), d.treated.sum(), len(b) - len(d))
    X = d[COVS].values.astype(float)
    t = d.treated.values
    Xs = (X - X.mean(0)) / (X.std(0) + 1e-9)
    # propensity
    lr = LogisticRegression(max_iter=5000, C=1.0).fit(Xs, t)
    ps = lr.predict_proba(Xs)[:, 1]
    d["pscore"] = ps
    w_ipw = np.where(t == 1, 1.0, np.clip(ps, 0, 0.95) / (1 - np.clip(ps, 0, 0.95)))
    w_ipw[t == 0] *= (t == 0).sum() / w_ipw[t == 0].sum()
    # entropy balancing
    w_eb = np.ones(len(d))
    w_eb[t == 0] = ebal(X[t == 0], X[t == 1].mean(0))
    # NN on pscore (1:3, with replacement)
    nn = NearestNeighbors(n_neighbors=3).fit(ps[t == 0].reshape(-1, 1))
    _, idx = nn.kneighbors(ps[t == 1].reshape(-1, 1))
    cnt = np.bincount(idx.ravel(), minlength=(t == 0).sum())
    w_nn = np.zeros(len(d))
    w_nn[t == 1] = 1
    w_nn[np.where(t == 0)[0]] = cnt / 3
    # Mahalanobis within region
    w_mh = np.zeros(len(d))
    w_mh[t == 1] = 1
    VI = np.linalg.pinv(np.cov(Xs[:, [0, 1, 2, 3, 4, 5, 9, 10, 11, 14, 15]].T))
    sub = [0, 1, 2, 3, 4, 5, 9, 10, 11, 14, 15]
    for r in d.region.unique():
        m = (d.region == r).values
        tr, co = np.where(m & (t == 1))[0], np.where(m & (t == 0))[0]
        if len(tr) == 0 or len(co) < 3:
            continue
        A, B = Xs[np.ix_(tr, sub)], Xs[np.ix_(co, sub)]
        diff = A[:, None, :] - B[None, :, :]
        dist = np.einsum("ijk,kl,ijl->ij", diff, VI, diff)
        nn3 = np.argsort(dist, axis=1)[:, :3]
        for row in nn3:
            w_mh[co[row]] += 1 / 3
    d["w_ebal"], d["w_ipw"], d["w_nn"], d["w_maha"] = w_eb, w_ipw, w_nn, w_mh
    d[["county_fips", "pscore", "w_ebal", "w_ipw", "w_nn", "w_maha"]].to_parquet(PROC / "matching_weights.parquet", index=False)

    rows = []
    for c_i, c in enumerate(COVS):
        x = X[:, c_i]
        rows.append({"covariate": c, "mean_treated": x[t == 1].mean(), "mean_control": x[t == 0].mean(),
                     "smd_raw": smd(x, t, np.ones(len(d))), "smd_ebal": smd(x, t, w_eb + 1e-12),
                     "smd_ipw": smd(x, t, w_ipw + 1e-12), "smd_nn": smd(x, t, w_nn + 1e-12),
                     "smd_maha": smd(x, t, w_mh + 1e-12)})
    bal = pd.DataFrame(rows)
    bal.to_csv(DIAG / "balance_table.csv", index=False)
    log.info("max |SMD| raw %.3f, ebal %.3f, ipw %.3f, nn %.3f, maha %.3f",
             *[bal[c].abs().max() for c in ["smd_raw", "smd_ebal", "smd_ipw", "smd_nn", "smd_maha"]])
    fig, ax = plt.subplots(figsize=(7, 6))
    yy = np.arange(len(bal))
    for c, mk in [("smd_raw", "o"), ("smd_ebal", "s"), ("smd_ipw", "^"), ("smd_nn", "D"), ("smd_maha", "x")]:
        ax.scatter(bal[c], yy, marker=mk, label=c.replace("smd_", ""))
    ax.axvline(0, color="k", lw=0.8)
    for v in (-0.1, 0.1):
        ax.axvline(v, color="grey", ls="--", lw=0.8)
    ax.set_yticks(yy, bal.covariate)
    ax.set_xlabel("Standardized mean difference (treated - control)")
    ax.set_title("Covariate balance: strict-treated vs. comparison counties")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGS / "balance_smd.png", dpi=150)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(ps[t == 0], bins=40, alpha=0.6, density=True, label="never treated")
    ax.hist(ps[t == 1], bins=40, alpha=0.6, density=True, label="treated")
    ax.set_xlabel("Propensity score")
    ax.legend()
    ax.set_title("Propensity score overlap")
    fig.tight_layout()
    fig.savefig(FIGS / "balance_pscore_overlap.png", dpi=150)
    plt.close(fig)
    _ = SEED


if __name__ == "__main__":
    main()
