"""Multiple testing (Section 38), resilience indices, robustness metrics (Section 34) and
robustness classification (Section 35).

Families: confirmatory = 5 primary outcomes; exploratory = secondary outcomes within labor / business /
household families. BH q-values and Holm-adjusted p-values within each family.
Indices (higher = more resilient): equal-weight z-score index and inverse-covariance-weighted (Anderson 2008)
index, standardized on never-treated county-periods.
Outputs: output/models/multiple_testing.csv, robustness_metrics.csv, resilience_indices.csv,
         output/tables/table9_robustness_summary.md, table10_multiple_testing.md
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests

import est
from utils import MODELS, TABLES, get_logger, load_config

log = get_logger(__file__)
RB = load_config()["robustness"]
INDICES = {
    "labor_market_resilience_index": ("q", [("separation_rate", -1), ("log_employment", 1), ("log_earnings", 1),
                                            ("job_destruction_rate_qwi", -1), ("turnover", -1)]),
    "business_resilience_index": ("y", [("establishment_death_rate", -1), ("job_destruction_rate", -1),
                                        ("log_establishments", 1), ("small_estab_death_rate", -1)]),
    "household_resilience_index": ("y", [("outmigration_rate", -1), ("net_migration_rate", 1)]),
}


def build_indices() -> list[dict]:
    out = []
    for name, (freq, comps) in INDICES.items():
        p = est.panel(freq)
        ctrl = p[p.ft_strict_primary.isna()]
        Z = pd.DataFrame(index=p.index)
        for v, sgn in comps:
            Z[v] = sgn * (p[v] - ctrl[v].mean()) / ctrl[v].std()
        p[name] = Z.mean(axis=1, skipna=False) if len(comps) <= 2 else Z.mean(axis=1).where(Z.notna().sum(1) >= len(comps) - 1)
        S = Z.dropna()
        try:
            w = np.linalg.inv(np.cov(S.T.values)).sum(axis=1)
            w = w / w.sum()
            p[name + "_icw"] = (Z * w).sum(axis=1, min_count=len(comps))
        except np.linalg.LinAlgError:
            p[name + "_icw"] = np.nan
        for v in [name, name + "_icw"]:
            r = est.run(est.Spec(outcome=v, freq=freq, label=v))
            r["index"] = v
            r["components"] = ";".join(c for c, _ in comps)
            out.append(r)
    out.append({"index": "fiscal_resilience_index", "status": "INFEASIBLE (public finance LOW feasibility)"})
    return out


def adjust(df: pd.DataFrame, fam_col: str) -> pd.DataFrame:
    df = df.copy()
    for fam, g in df[df.p.notna()].groupby(fam_col):
        df.loc[g.index, "bh_q"] = multipletests(g.p, method="fdr_bh")[1]
        df.loc[g.index, "holm_p"] = multipletests(g.p, method="holm")[1]
    return df


def signed_share(x: pd.Series, sign: float) -> float:
    return float((np.sign(x) == sign).mean()) if len(x) else np.nan


def metrics(var: str, pr_row: pd.Series, es: pd.DataFrame, plc: pd.DataFrame, loso: pd.DataFrame,
            loeo: pd.DataFrame, estc: pd.DataFrame) -> dict:
    f = MODELS / f"robustness_{var}.csv"
    if not f.exists():
        return {}
    rb = pd.read_csv(f)
    rb = rb[rb.status == "ok"]
    b0, se0, p0, Es = pr_row.beta, pr_row.se, pr_row.p, pr_row.E_star
    sgn = np.sign(b0)
    cr = rb[(rb.credible_specification == 1) & (rb.specification_id != "R00")]
    m = {"outcome_var": var, "primary_beta": b0, "n_credible": len(cr)}
    m["sign_consistency"] = signed_share(cr.beta, sgn)
    m["sig_consistency"] = float(((np.sign(cr.beta) == sgn) & (cr.p < 0.10)).mean()) if len(cr) else np.nan
    m["significant_5_share"] = float(((np.sign(cr.beta) == sgn) & (cr.p < 0.05)).mean()) if len(cr) else np.nan
    m["median_beta"] = cr.beta.median()
    m["median_absolute_beta"] = cr.beta.abs().median()
    ratio = cr.beta / b0 if b0 != 0 else pd.Series(dtype=float)
    ratio = ratio[ratio.abs() < 20]
    m["median_beta_ratio"] = ratio.median() if len(ratio) else np.nan
    opp = np.where(sgn > 0, cr.ci_low, -cr.ci_high)          # magnitude of the opposite-direction bound
    m["CI_consistency"] = float((np.asarray(opp) > -Es).mean()) if len(cr) else np.nan
    m["robust_specs"] = int(((np.sign(cr.beta) == sgn) & (cr.p < 0.10)).sum())
    m["sig_opposite_specs"] = int(((np.sign(cr.beta) == -sgn) & (cr.p < 0.10)).sum())

    def cat_pass(cat, thresh=0.8):
        s = cr[cr.category == cat]
        if len(s) == 0:
            return np.nan
        same = signed_share(s.beta, sgn)
        sig_opp = ((np.sign(s.beta) == -sgn) & (s.p < 0.10)).any()
        return int(same >= thresh and not sig_opp)
    td = rb[rb.specification_id.isin(["R00", "R02", "R03"])]
    m["treatment_definition_pass"] = int((np.sign(td.beta) == sgn).all() and not ((np.sign(td.beta) == -sgn) & (td.p < 0.10)).any())
    m["timing_pass"] = cat_pass("timing")
    m["hazard_definition_pass"] = cat_pass("hazard", 0.75)
    m["matching_pass"] = cat_pass("matching", 0.75)
    e = es[es.outcome == var]
    m["pretrend_p"] = float(e.pretrend_p.iloc[0]) if len(e) and "pretrend_p" in e else np.nan
    ec = estc[estc.outcome == var]
    if len(ec):
        ec = ec.iloc[0]
        m["stacked_beta"], m["stacked_p"] = ec.get("stacked_beta"), ec.get("stacked_p")
        m["iw_beta"], m["iw_p"] = ec.get("iw_beta"), ec.get("iw_p")
        m["stacked_es_pretrend_p"] = ec.get("stacked_es_pretrend_p")
        if np.isnan(m["pretrend_p"]):
            m["pretrend_p"] = ec.get("stacked_es_pretrend_p", np.nan)
        modern = [(ec.get("stacked_beta"), ec.get("stacked_p")), (ec.get("iw_beta"), ec.get("iw_p"))]
        modern = [(b, p) for b, p in modern if pd.notna(b)]
        contra = any(np.sign(b) == -sgn and p < 0.10 for b, p in modern)
        support = all(np.sign(b) == sgn for b, _ in modern) if modern else False
        m["estimator_pass"] = int(support and not contra)
        m["estimator_contradiction"] = int(contra)
    else:
        m["estimator_pass"], m["estimator_contradiction"] = np.nan, 0
    m["pretrend_pass"] = int(m["pretrend_p"] > RB["pretrend_threshold"]) if pd.notna(m["pretrend_p"]) else np.nan
    pl = plc[(plc.outcome == var) & (plc.specification_id == "R38")]
    if len(pl) and pl.iloc[0].status == "ok":
        m["placebo_beta"], m["placebo_p"] = pl.iloc[0].beta, pl.iloc[0].p
        m["placebo_pass"] = int(m["placebo_p"] > RB["placebo_threshold"])
        m["placebo_similar"] = int(abs(m["placebo_beta"]) >= 0.75 * abs(b0) and m["placebo_p"] < 0.10)
    ri = plc[(plc.outcome == var) & (plc.specification_id == "R40")]
    m["ri_p"] = float(ri.iloc[0].p) if len(ri) else np.nan
    lo = loso[loso.outcome == var]
    m["leave_state_out_sign_share"] = signed_share(lo.beta.dropna(), sgn) if len(lo) else np.nan
    m["leave_state_out_pass"] = int(m["leave_state_out_sign_share"] >= RB["leave_state_out_share"]) if len(lo) else np.nan
    sig0 = p0 < 0.10
    drv_state = lo[(np.sign(lo.beta) != sgn) | (lo.beta.abs() < abs(b0) / 3)].state_removed.tolist() if sig0 and len(lo) else []
    le = loeo[loeo.outcome == var]
    drv_event = le[(np.sign(le.beta) != sgn) | (le.beta.abs() < abs(b0) / 3)].episode_removed.tolist() if sig0 and len(le) else []
    m["driving_states"] = ",".join(drv_state)
    m["driving_events"] = ",".join(map(str, drv_event))
    m["single_unit_drives"] = int(bool(drv_state or drv_event))
    m["loeo_sign_share"] = signed_share(le.beta.dropna(), sgn) if len(le) else np.nan
    for st in ["OK", "TX"]:
        r = lo[lo.state_removed == st]
        m[f"beta_without_{st}"] = float(r.beta.iloc[0]) if len(r) else np.nan
        m[f"p_without_{st}"] = float(r.pvalue.iloc[0]) if len(r) else np.nan
    return m


def classify(m: dict, pr: pd.Series) -> tuple[str, str]:
    if pr.get("status") != "ok":
        return "INFEASIBLE", "Infeasible"
    b, lo, hi, p, Es = pr.beta, pr.ci_low, pr.ci_high, pr.p, pr.E_star
    exp = pr.expected_sign
    prot_sign = 1 if exp == "+" else -1 if exp == "-" else -np.sign(pr.gamma_T) if pr.gamma_T != 0 else 1
    if p >= 0.10:
        if lo > -Es and hi < Es:
            return "NO DETECTABLE EFFECT", "No detectable effect"
        return "UNDERPOWERED", "Underpowered"
    direction = "Protective" if np.sign(b) == prot_sign else "Adverse"
    sc = m.get("sign_consistency", np.nan)
    strong_pre = pd.notna(m.get("pretrend_p")) and m["pretrend_p"] < 0.05
    if (pd.notna(sc) and sc < 0.5) or strong_pre or m.get("placebo_similar", 0) == 1 \
            or m.get("single_unit_drives", 0) == 1 or m.get("estimator_contradiction", 0) == 1:
        return "NOT ROBUST", direction
    opp = lo if b > 0 else -hi
    precise = (abs(b) >= Es) or (opp > -Es)
    if (sc >= RB["robust_sign_share"] and m.get("pretrend_pass") == 1 and m.get("placebo_pass") == 1
            and m.get("leave_state_out_pass") == 1 and m.get("treatment_definition_pass") == 1
            and m.get("estimator_pass") == 1 and precise):
        return "ROBUST", direction
    if (sc >= RB["moderate_sign_share"] and m.get("treatment_definition_pass") == 1
            and m.get("hazard_definition_pass", 1) != 0 and m.get("timing_pass", 1) != 0
            and (m.get("sig_consistency", 0) or 0) >= 1 / 3):
        return "MODERATELY ROBUST", direction
    return "MIXED", direction


def main() -> None:
    pr = pd.read_csv(MODELS / "primary_results.csv")
    pr["fam_mt"] = np.where(pr.primary == 1, "confirmatory", "exploratory_" + pr.family)
    mt = adjust(pr[pr.status == "ok"], "fam_mt")
    idx = pd.DataFrame(build_indices())
    idx["fam_mt"] = "indices"
    idx = adjust(idx, "fam_mt")
    idx.to_csv(MODELS / "resilience_indices.csv", index=False)
    mt.to_csv(MODELS / "multiple_testing.csv", index=False)

    es = pd.read_csv(MODELS / "event_study_summary.csv") if (MODELS / "event_study_summary.csv").exists() else pd.DataFrame(columns=["outcome"])
    plc = pd.read_csv(MODELS / "placebo_results.csv") if (MODELS / "placebo_results.csv").exists() else pd.DataFrame(columns=["outcome", "specification_id"])
    loso = pd.read_csv(MODELS / "loso_results.csv") if (MODELS / "loso_results.csv").exists() else pd.DataFrame(columns=["outcome"])
    loeo = pd.read_csv(MODELS / "loeo_results.csv") if (MODELS / "loeo_results.csv").exists() else pd.DataFrame(columns=["outcome"])
    estc = pd.read_csv(MODELS / "estimator_comparison.csv") if (MODELS / "estimator_comparison.csv").exists() else pd.DataFrame(columns=["outcome"])
    rows = []
    for _, r in mt.iterrows():
        m = metrics(r.outcome_var, r, es, plc, loso, loeo, estc)
        m.update({"outcome_id": r.outcome_id, "outcome": r.outcome, "outcome_var": r.outcome_var,
                  "bh_q": r.bh_q, "holm_p": r.holm_p, "family_mt": r.fam_mt})
        rating, main_res = classify(m, r)
        m["robustness_rating"], m["main_result"] = rating, main_res
        rows.append(m)
    rm = pd.DataFrame(rows)
    rm.to_csv(MODELS / "robustness_metrics.csv", index=False)
    cols = ["outcome", "primary_beta", "sign_consistency", "sig_consistency", "significant_5_share", "median_beta_ratio",
            "CI_consistency", "pretrend_p", "placebo_p", "ri_p", "leave_state_out_sign_share", "treatment_definition_pass",
            "timing_pass", "hazard_definition_pass", "matching_pass", "estimator_pass", "robust_specs", "n_credible",
            "robustness_rating", "main_result"]
    (TABLES / "table9_robustness_summary.md").write_text(
        "# Table 9. Robustness summary\n\nSign consistency uses credible specifications only (duplicates of the primary, "
        "placebos and permutation draws excluded). Classification follows Section 35 rules frozen in the "
        "pre-registration snapshot.\n\n" + rm[[c for c in cols if c in rm]].round(3).to_markdown(index=False), encoding="utf-8")
    t10 = mt[["outcome", "fam_mt", "beta", "se", "p", "bh_q", "holm_p"]]
    (TABLES / "table10_multiple_testing.md").write_text(
        "# Table 10. Multiple-testing adjustment\n\nFamilies: confirmatory (5 pre-specified primary outcomes); "
        "exploratory families by outcome domain. BH = Benjamini-Hochberg q-value; Holm = Holm-adjusted p.\n\n"
        + t10.round(4).to_markdown(index=False) + "\n\n## Resilience indices\n\n"
        + idx[[c for c in ["index", "beta", "se", "p", "bh_q", "holm_p", "N", "status"] if c in idx]].round(4).to_markdown(index=False),
        encoding="utf-8")
    log.info("\n%s", rm[["outcome", "robustness_rating", "main_result"]].to_string())


if __name__ == "__main__":
    main()
