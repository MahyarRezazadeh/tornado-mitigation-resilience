"""Transparent publication-potential heuristic (Section 40). NOT a probability.

Components (max): identification 30, novelty 20, data quality 15, result strength 15, mechanism 10,
policy importance 10; penalties per Section 40 (no double counting: each penalty applied at most once).
Statistical significance never adds points by itself: result strength is driven by the robustness rating.
Outputs: output/models/publication_scores.csv, output/tables/table12_publication_assessment.md
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from utils import LIT, MODELS, TABLES, get_logger

log = get_logger(__file__)
STRENGTH = {"ROBUST": 15, "MODERATELY ROBUST": 10, "NO DETECTABLE EFFECT": 8, "MIXED": 6, "UNDERPOWERED": 3,
            "NOT ROBUST": 2, "INFEASIBLE": 0}
# Novelty by outcome domain, from the structured search (see literature_review.md): no close causal study of
# FEMA tornado/wind mitigation x subsequent tornado on these outcomes was found; disaster-outcome literatures exist.
NOVELTY = {"labor": ("HIGH", 16), "business": ("HIGH", 15), "household": ("MEDIUM", 11), "damage": ("MEDIUM", 9)}


def potential(x):
    return "HIGH" if x >= 85 else "MEDIUM-HIGH" if x >= 75 else "MEDIUM" if x >= 60 else "LOW"


def mech_points(var: str, mech: pd.DataFrame, pr: pd.DataFrame) -> tuple[int, str]:
    pts, notes = 0, []
    m1 = mech[(mech.mechanism == "M1") & (mech.term == "MI") & (mech.sample == "all county-quarters")]
    sig_m1 = m1[(m1.beta < 0) & (m1.p < 0.05)]
    if len(sig_m1):
        pts += 3
        notes.append("M1 casualty/damage reduction: " + ",".join(sig_m1.outcome))
    get = lambda v: pr.set_index("outcome_var").loc[v] if v in set(pr.outcome_var) else None  # noqa: E731
    if var in ("separation_rate", "log_employment", "hire_rate", "turnover"):
        sep, hir, tov = get("separation_rate"), get("hire_rate"), get("turnover")
        if sep is not None and sep.beta < 0 and sep.p < 0.10 and hir is not None and not (hir.beta > 0 and hir.p < 0.10):
            pts += 5
            notes.append("M3 match preservation consistent")
    if var in ("establishment_death_rate", "job_destruction_rate", "small_estab_death_rate"):
        m4 = mech[(mech.mechanism == "M4") & (mech.term == "MTS")]
        if len(m4[(m4.beta < 0) & (m4.p < 0.10)]):
            pts += 5
            notes.append("M4 small-business amplification")
    m2 = mech[(mech.mechanism == "M2") & (mech.term == "MTP") & (mech.outcome == var)]
    protective_m2 = len(m2) and ((m2.iloc[0].beta < 0) if var != "log_employment" else (m2.iloc[0].beta > 0))
    if len(m2) and m2.iloc[0].p < 0.10 and protective_m2:   # only a protective-direction difference counts
        pts += 2
        notes.append("M2 physical-premise industries differ")
    return min(pts, 10), "; ".join(notes) if notes else "no supporting mechanism evidence"


def main() -> None:
    rm = pd.read_csv(MODELS / "robustness_metrics.csv")
    pr = pd.read_csv(MODELS / "primary_results.csv")
    pw = pd.read_csv(MODELS / "power.csv")
    fe = pd.read_csv(TABLES.parent / "tables" / "outcome_feasibility.csv")
    mech = pd.read_csv(MODELS / "mechanisms.csv") if (MODELS / "mechanisms.csv").exists() else pd.DataFrame(columns=["mechanism", "term", "sample", "outcome", "beta", "p"])
    close = pd.read_csv(LIT / "closest_candidates.csv") if (LIT / "closest_candidates.csv").exists() else pd.DataFrame()
    fscore = dict(zip(fe.variable, fe.feasibility_score))
    supp = dict(zip(fe.variable, fe.suppression_share))
    rows = []
    prr = pr.set_index("outcome_var")
    for _, m in rm.iterrows():
        v = m.outcome_var
        p = prr.loc[v]
        comp = {}
        pre = m.get("pretrend_p", np.nan)
        comp["id_variation"] = 3
        comp["id_pretrend"] = 6 if pre > 0.10 else 3 if pre > 0.05 else 0 if pd.notna(pre) else 2
        comp["id_comparison"] = 4 if m.get("matching_pass") == 1 else 2
        comp["id_timing"] = 3 if m.get("timing_pass") == 1 else 1
        comp["id_estimators"] = 4 if m.get("estimator_pass") == 1 else 1
        r20 = pd.read_csv(MODELS / f"robustness_{v}.csv").query("specification_id == 'R20'") \
            if (MODELS / f"robustness_{v}.csv").exists() else pd.DataFrame()
        comp["id_selection"] = 2 if (len(r20) and np.sign(r20.beta.iloc[0]) == np.sign(p.beta)) else 0
        ident = sum(comp.values())
        fam = p.family
        nov_r, nov = NOVELTY.get(fam, ("MEDIUM", 10))
        if len(close):
            nov -= 2
        data_q = round(0.15 * fscore.get(v, fe.feasibility_score.median()), 1)
        strength = STRENGTH.get(m.robustness_rating, 0)
        mpts, mnote = mech_points(v, mech, pr)
        policy = 8 if p.primary == 1 else 6
        pen = {}
        if pd.notna(pre) and pre < 0.05:
            pen["severe_pretrends"] = -10
        pen["unclear_completion_timing"] = -10           # OpenFEMA has no completion date (applies to all)
        if m.get("single_unit_drives") == 1:
            pen["one_state_or_event"] = -10
        if p.treated_tornado_obs < 30:
            pen["lt30_post_events"] = -10
        if p.p < 0.05 and m.get("bh_q", 1) > 0.10:
            pen["multiple_testing_fragility"] = -10
        if m.get("matching_pass") == 0 and m.get("estimator_pass") == 0:
            pen["weak_control_group"] = -10
        if m.get("estimator_contradiction") == 1:
            pen["inconsistent_staggered_did"] = -10
        if supp.get(v, 0) > 0.20:
            pen["high_suppression"] = -5
        total = ident + nov + data_q + strength + mpts + policy + sum(pen.values())
        total = float(np.clip(total, 0, 100))
        rows.append({"outcome_var": v, "outcome": m.outcome, "identification_points": ident, **comp,
                     "novelty_rating": nov_r, "novelty_points": nov, "data_quality_points": data_q,
                     "result_strength_points": strength, "mechanism_points": mpts, "mechanism_note": mnote,
                     "policy_points": policy, "penalties": ";".join(f"{k}{v}" for k, v in pen.items()),
                     "penalty_total": sum(pen.values()), "publication_score": round(total, 1),
                     "publication_potential": potential(total),
                     "identification_rating": "HIGH" if ident >= 22 else "MEDIUM" if ident >= 15 else "LOW",
                     "power_rating": pw.set_index("outcome").power_rating.get(m.outcome, "")})
    ps = pd.DataFrame(rows)
    ps.to_csv(MODELS / "publication_scores.csv", index=False)
    (TABLES / "table12_publication_assessment.md").write_text(
        "# Table 12. Publication-potential heuristic (transparent; not an acceptance probability)\n\n"
        + ps.drop(columns=["mechanism_note"]).round(1).to_markdown(index=False), encoding="utf-8")
    log.info("\n%s", ps[["outcome", "publication_score", "publication_potential"]].to_string())


if __name__ == "__main__":
    main()
