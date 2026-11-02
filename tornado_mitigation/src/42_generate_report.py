"""Final research assessment (Sections 53, 54, 60, 61) + terminal summary (Section 71).

Numbers are pulled from the result files; answers A-T and the GO/NO-GO decision follow explicit rules
printed in the report. Analyst interpretation (written after reviewing results) is read from
output/final/analyst_notes.md if present and inserted verbatim.
Output: output/final/research_assessment.md, output/final/paper_bundles.md
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from utils import FINAL, INTER, LIT, MODELS, TABLES, get_logger

log = get_logger(__file__)
BUNDLES = {
    "A": ("LABOR MARKET RESILIENCE", "separation_rate",
          ["log_employment", "log_earnings", "hire_rate", "log_new_hire_earnings", "turnover", "new_hire_rate"],
          "Do FEMA tornado/wind mitigation investments reduce tornado-induced worker separations and employment/earnings losses?"),
    "B": ("BUSINESS RESILIENCE", "establishment_death_rate",
          ["job_destruction_rate", "establishment_birth_rate", "startup_rate", "log_establishments", "log_payroll",
           "small_estab_death_rate"],
          "Do FEMA tornado/wind mitigation investments reduce tornado-induced establishment deaths and job destruction?"),
    "C": ("SPATIAL / FISCAL RESILIENCE", "outmigration_rate",
          ["net_migration_rate", "inmigration_rate", "ihs_units", "ihs_sf_units"],
          "Do FEMA tornado/wind mitigation investments reduce post-tornado out-migration and change rebuilding?"),
}


def f(x, d=4):
    return "n/a" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{d}f}"


def yn(b):
    return "n/a" if b is None or (isinstance(b, float) and np.isnan(b)) else ("Yes" if b else "No")


def load():
    R = {k: pd.read_csv(MODELS / f"{k}.csv") for k in ["primary_results", "robustness_metrics", "power",
                                                       "publication_scores", "journal_fit", "estimator_comparison",
                                                       "event_study_summary", "mechanisms", "loso_results",
                                                       "loeo_results", "placebo_results", "resilience_indices",
                                                       "severity_gradient", "recovery_metrics", "major_episodes"]
         if (MODELS / f"{k}.csv").exists()}
    R["master"] = pd.read_csv(FINAL / "master_outcome_assessment.csv")
    R["feas"] = pd.read_csv(TABLES / "outcome_feasibility.csv")
    R["lit"] = pd.read_csv(LIT / "literature_overlap.csv")
    return R


def row(df, col, v):
    s = df[df[col] == v]
    return s.iloc[0] if len(s) else None


def bundle_eval(key, R):
    name, prim, secs, q = BUNDLES[key]
    pr = row(R["primary_results"], "outcome_var", prim)
    m = row(R["robustness_metrics"], "outcome_var", prim)
    ps = row(R["publication_scores"], "outcome_var", prim)
    jf = row(R["journal_fit"], "outcome_var", prim)
    pw = row(R["power"], "outcome", pr.outcome) if pr is not None else None
    secs_r = R["robustness_metrics"][R["robustness_metrics"].outcome_var.isin(secs)]
    if pr is None or m is None:
        return {"name": name, "decision": "NO-GO", "q": q}
    ans = {
        "1. Statistically distinguishable from zero?": f"{yn(pr.p < 0.05)} (beta={f(pr.beta)}, p={f(pr.p, 3)}, BH q={f(m.bh_q, 3)})",
        "2. Economically meaningful?": f"{yn(abs(pr.beta) >= pr.E_star)} (|beta| vs E*={f(pr.E_star)}; {f(pr.effect_pct_mean, 2)}% of mean)",
        "3. Survives modern DiD estimators?": f"{yn(m.estimator_pass == 1)} (stacked={f(m.get('stacked_beta'))}, p={f(m.get('stacked_p'), 3)}; IW={f(m.get('iw_beta'))})",
        "4. Survives alternative treatment timing?": yn(m.timing_pass == 1),
        "5. Survives alternative tornado definitions?": yn(m.hazard_definition_pass == 1),
        "6. Survives leave-one-state-out?": f"{yn(m.leave_state_out_pass == 1)} (sign share {f(m.leave_state_out_sign_share, 2)})",
        "7. Passes pretrend tests?": f"{yn(m.pretrend_pass == 1)} (p={f(m.pretrend_p, 3)})",
        "8. Passes placebo tests?": f"{yn(m.get('placebo_pass') == 1)} (p={f(m.get('placebo_p'), 3)}; RI p={f(m.get('ri_p'), 3)})",
        "9. Mechanism evidence?": ps.mechanism_note if ps is not None else "n/a",
        "10. Novelty high?": ps.novelty_rating if ps is not None else "n/a",
        "11. Power adequate?": pw.power_rating if pw is not None else "n/a",
        "12. Treatment assignment sufficiently credible?": "Partly: DiD on staggered FEMA awards with matched/weighted "
                                                           "comparisons; no quasi-random assignment (see quasi_experiment_assessment.md)",
    }
    rr = m.robustness_rating
    if rr in ("ROBUST", "MODERATELY ROBUST") and m.main_result == "Protective":
        dec = "GO"
    elif rr == "NO DETECTABLE EFFECT" or (rr in ("MIXED", "MODERATELY ROBUST") and m.main_result == "Protective") \
            or (secs_r.robustness_rating.isin(["ROBUST", "MODERATELY ROBUST"]) & (secs_r.main_result == "Protective")).any():
        dec = "MAYBE"
    else:
        dec = "NO-GO"
    best_sec = secs_r.sort_values("robustness_rating", key=lambda s: s.map(
        {"ROBUST": 0, "MODERATELY ROBUST": 1, "NO DETECTABLE EFFECT": 2, "MIXED": 3, "UNDERPOWERED": 4, "NOT ROBUST": 5})).head(1)
    return {"name": name, "q": q, "primary": pr.outcome, "secondary": ", ".join(secs), "answers": ans,
            "rating": rr, "main_result": m.main_result,
            "strongest": f"{best_sec.outcome.iloc[0]} ({best_sec.robustness_rating.iloc[0]}, {best_sec.main_result.iloc[0]})" if len(best_sec) else "n/a",
            "score": ps.publication_score if ps is not None else np.nan,
            "potential": ps.publication_potential if ps is not None else "n/a",
            "journal": jf.best_journal if jf is not None else "n/a", "decision": dec,
            "threat": "endogenous post-disaster HMGP awards and proxy (obligation+2y) completion timing"}


def main() -> None:
    R = load()
    M, pr, rm = R["master"], R["primary_results"], R["robustness_metrics"]
    notes = (FINAL / "analyst_notes.md").read_text(encoding="utf-8") if (FINAL / "analyst_notes.md").exists() else ""
    prim = rm[rm.family_mt == "confirmatory"]
    B = {k: bundle_eval(k, R) for k in BUNDLES}

    # ---------------- answers A-T (rules) ----------------
    order = {"ROBUST": 0, "MODERATELY ROBUST": 1, "NO DETECTABLE EFFECT": 2, "MIXED": 3, "UNDERPOWERED": 4,
             "NOT ROBUST": 5, "INFEASIBLE": 6}
    est_ = M[M.Robustness_Rating != "INFEASIBLE"].copy()
    est_["_o"] = est_.Robustness_Rating.map(order)
    prot = est_[est_.Main_Result == "Protective"].sort_values(["_o", "Primary_P"])
    A = (f"{prot.Outcome.iloc[0]} ({prot.Robustness_Rating.iloc[0]})" if len(prot)
         else "None: no outcome shows a protective effect that survives the robustness rules.")
    Bq = est_.sort_values(["_o", "Sign_Consistency"], ascending=[True, False]).iloc[0]
    est_["abs_sd"] = est_.Effect_SD.abs()
    sig = est_[(est_.Primary_P < 0.05)]
    C = (f"{sig.sort_values('abs_sd', ascending=False).Outcome.iloc[0]} ({f(sig.sort_values('abs_sd', ascending=False).Effect_SD.iloc[0], 3)} SD; "
         f"{sig.sort_values('abs_sd', ascending=False).Robustness_Rating.iloc[0]})" if len(sig) else "No statistically distinguishable effect is economically large.")
    D = M.sort_values(["Novelty_Rating", "Feasibility_Score"], ascending=[True, False]).iloc[0].Outcome
    E = M.sort_values("Publication_Score", ascending=False).iloc[0]
    F = ", ".join(M[M.Power_Rating == "UNDERPOWERED"].Outcome.head(6)) or "none"
    G = ", ".join(M[(M.Primary_P < 0.05) & M.Robustness_Rating.isin(["NOT ROBUST", "MIXED"])].Outcome) or "none"
    ok_tx = []
    for _, r in prim.iterrows():
        p0 = row(pr, "outcome_var", r.outcome_var)
        ok_tx.append(f"{r.outcome}: primary {f(p0.beta)}; without OK {f(r.beta_without_OK)} (p={f(r.p_without_OK, 3)}); "
                     f"without TX {f(r.beta_without_TX)} (p={f(r.p_without_TX, 3)})")
    H = "; ".join(ok_tx)
    I_ = "; ".join(f"{r.outcome}: LOEO sign share {f(r.loeo_sign_share, 2)}, driving events [{r.driving_events or 'none'}]"
                   for _, r in prim.iterrows())
    J = "; ".join(f"{r.outcome}: timing_pass={r.timing_pass}" for _, r in prim.iterrows())
    K = "; ".join(f"{r.outcome}: {r.robustness_rating} ({r.main_result})" for _, r in prim.iterrows())
    L_ = []
    for _, r in prim.iterrows():
        rb = pd.read_csv(MODELS / f"robustness_{r.outcome_var}.csv")
        e2 = rb[rb.specification_id == "R13"]
        if len(e2):
            L_.append(f"{r.outcome}: EF2+ beta={f(e2.beta.iloc[0])} (p={f(e2.p.iloc[0], 3)})")
    Mq = "; ".join(f"{r.outcome}: TWFE {f(r.primary_beta)} vs stacked {f(r.get('stacked_beta'))} / IW {f(r.get('iw_beta'))} "
                   f"-> estimator_pass={r.estimator_pass}" for _, r in prim.iterrows())
    N_ = "; ".join(f"{r.outcome}: p={f(r.pretrend_p, 3)}" for _, r in prim.iterrows())
    O_ = "; ".join(f"{r.outcome}: placebo p={f(r.get('placebo_p'), 3)}, RI p={f(r.get('ri_p'), 3)}" for _, r in prim.iterrows())
    tq = pd.read_csv(TABLES.parent / "diagnostics" / "fema_timing_quality.csv")
    P_ = (f"No. OpenFEMA publishes no physical completion date (0% coverage). Closeout is observed for "
          f"{f(tq.share_closeout.iloc[0] * 100, 1)}% of strict projects (median {f(tq.median_oblig_to_close_yrs.iloc[0], 1)} years "
          f"after obligation) and is an administrative upper bound on completion. Primary timing is therefore a proxy.")
    mech = R.get("mechanisms", pd.DataFrame())
    m1 = mech[(mech.mechanism == "M1") & (mech.term == "MI") & (mech["sample"] == "all county-quarters")] if len(mech) else pd.DataFrame()
    Q_ = "; ".join(f"M1 {r.outcome}: {f(r.beta)} (p={f(r.p, 3)})" for _, r in m1.iterrows()) or "n/a"
    t1 = (TABLES / "table1_fema_treatment_summary.md").read_text(encoding="utf-8")
    qe = (FINAL / "quasi_experiment_assessment.md").read_text(encoding="utf-8") if (FINAL / "quasi_experiment_assessment.md").exists() else ""

    goc = prim[(prim.robustness_rating.isin(["ROBUST", "MODERATELY ROBUST"])) & (prim.main_result == "Protective")]
    interesting = M[(M.Main_Result == "Protective") & (M.Primary_P < 0.10)]
    if len(goc) and (goc.pretrend_pass == 1).all() and (goc.get("placebo_pass", 0) == 1).all():
        decision = "GO"
    elif len(interesting) or (M.Robustness_Rating == "NO DETECTABLE EFFECT").sum() >= 2:
        decision = "GO WITH REDESIGN"
    elif (M.Feasibility_Rating.isin(["EXCELLENT", "GOOD"])).any():
        decision = "PILOT ONLY"
    else:
        decision = "NO-GO"
    if (FINAL / "analyst_decision.json").exists():
        ad = json.loads((FINAL / "analyst_decision.json").read_text())
        decision, dec_reason = ad["decision"], ad["reason"]
    else:
        dec_reason = "rule-based"

    hr = pd.read_csv(FINAL / "final_summary_table.csv")
    lit = R["lit"]
    ver = lit[lit.verified_crossref.astype(str) == "True"]
    sec = []
    S = sec.append
    S("# Research Assessment: Local Tornado Mitigation and Economic Resilience\n")
    S(f"Generated from pipeline outputs. Primary specification frozen in `preregistration_snapshot.md`.\n")
    S("## 1. Executive Summary\n")
    S(notes.split("<!--END-EXEC-->")[0] if notes else "(analyst notes not yet written)")
    S(f"\n**Final decision: {decision}**\n")
    S("## 2. Research Question\n\nDo ex-ante FEMA-funded tornado/severe-wind mitigation investments (safe rooms, wind "
      "retrofits) reduce the economic disruption caused by subsequent tornadoes? The estimand is Mitigation x "
      "subsequent tornado exposure (resilience), not mitigation -> unconditional growth.\n")
    S("## 3. FEMA Policy / Treatment Definition\n\n" + t1 + "\n\nClassification rules: `config/treatment_keywords.csv`; "
      "manual-check sample: `output/diagnostics/fema_classification_sample.xlsx`.\n")
    S("## 4. Data\n\n" + pd.read_csv(TABLES.parent / "logs" / "data_sources.csv")[["dataset", "source_name", "coverage_start",
                                                                                 "coverage_end", "notes"]].to_markdown(index=False) + "\n")
    S("## 5. Feasibility\n\n" + (TABLES / "table3_outcome_feasibility.md").read_text(encoding="utf-8").split("\n", 2)[-1] + "\n")
    S("## 6. Identification Strategy\n\nPrimary: Y = b*M*T + g1*M + g2*T + county FE + state x time FE, clustered by "
      "county (Section 24). b compares the tornado-associated change in Y in counties whose mitigation is operational with "
      "the tornado-associated change elsewhere in the same state and period. Dynamic: distributed-lag tornado event study "
      "(k=-8..12 quarters), stacked clean-event study with same-state controls, stacked mitigation-cohort triple "
      "difference, interaction-weighted cohort average; mitigation-adoption event studies (TWFE, Sun-Abraham, two-stage "
      "imputation) as diagnostics; entropy balancing, IPW, NN and Mahalanobis matching.\n")
    S("## 7. Treatment Timing\n\n" + P_ + "\n\n" + tq.round(3).to_markdown(index=False) + "\n")
    S("## 8. Main Results\n\n" + (FINAL / "master_outcome_assessment.md").read_text(encoding="utf-8").split("## Result table (Section 64)")[1]
      .split("Full column set")[0] + "\n")
    for title, fam in [("9. Labor-Market Results", "labor"), ("10. Business Results", "business"),
                       ("11. Migration/Housing/Fiscal Results", "household")]:
        sub = pr[pr.family == fam][["outcome", "beta", "se", "p", "ci_low", "ci_high", "gamma_T", "effect_pct_mean", "N",
                                    "treated_counties", "treated_tornado_obs"]]
        S(f"## {title}\n\n" + sub.round(5).to_markdown(index=False) + "\n")
    S("Local fiscal outcomes: LOW feasibility; not estimated (no consistent annual county panel).\n")
    es = R.get("event_study_summary", pd.DataFrame())
    S("## 12. Dynamic Event Studies\n\n" + (es.round(4).to_markdown(index=False) if len(es) else "n/a") +
      "\n\nRecovery metrics:\n\n" + (R["recovery_metrics"].round(4).to_markdown(index=False) if "recovery_metrics" in R else "n/a") +
      "\n\nFigures 6-10 in output/figures/.\n")
    S("## 13. Pre-Trends\n\n" + N_ + "\n\nAdoption-event diagnostics (pre-period mean, TWFE vs Sun-Abraham) are in "
      "event_study_summary.csv.\n")
    S("## 14. Mechanisms\n\n" + (mech.round(4).to_markdown(index=False) if len(mech) else "n/a") + "\n\nSeverity gradient:\n\n" +
      (R["severity_gradient"].round(4).to_markdown(index=False) if "severity_gradient" in R else "n/a") +
      ("\n\nDamage-mechanism robustness (exploratory, added after main results; includes the failing pre-treatment "
       "placebo and the within-treated design):\n\n" + pd.read_csv(MODELS / "damage_robustness.csv").round(4)
       .to_markdown(index=False) if (MODELS / "damage_robustness.csv").exists() else "") + "\n")
    S("## 15. Heterogeneity (exploratory)\n\nSee `output/tables/table8_heterogeneity.md` (BH within family) and "
      "Figures 12-14.\n")
    S("## 16. Robustness\n\n" + (TABLES / "table9_robustness_summary.md").read_text(encoding="utf-8").split("\n", 2)[-1] + "\n")
    pl = R.get("placebo_results", pd.DataFrame())
    S("## 17. Placebos\n\n" + (pl[[c for c in ["outcome", "specification_id", "beta", "se", "p", "share_p05", "n_draws",
                                              "primary_beta"] if c in pl]].round(4).to_markdown(index=False) if len(pl) else "n/a") + "\n")
    lo = R.get("loso_results", pd.DataFrame())
    S("## 18. Leave-One-State-Out\n\n" + H + "\n\n" +
      (lo[lo.focus_state].round(4).to_markdown(index=False) if len(lo) else "") + "\n\nLeave-one-event-out: " + I_ + "\n")
    S("## 19. Multiple Testing\n\n" + (TABLES / "table10_multiple_testing.md").read_text(encoding="utf-8").split("\n", 2)[-1] + "\n")
    S("## 20. Statistical Power\n\n" + (TABLES / "table11_power.md").read_text(encoding="utf-8").split("\n", 2)[-1] + "\n")
    S(f"## 21. Literature Novelty\n\nStructured search: 24 phrases x OpenAlex/Crossref/Semantic Scholar "
      f"({len(pd.read_csv(LIT / 'search_hits_raw.csv'))} raw hits). Verified closely related papers: {len(ver)}. "
      "See literature_review.md and literature_overlap.csv.\n\n"
      + (notes.split("<!--LIT-->")[1].split("<!--END-LIT-->")[0] if "<!--LIT-->" in notes else "") + "\n")
    S("## 22. Publication Potential\n\n" + (TABLES / "table12_publication_assessment.md").read_text(encoding="utf-8").split("\n", 2)[-1] + "\n")
    S("## 23. Journal Fit\n\n" + (TABLES / "journal_fit.md").read_text(encoding="utf-8").split("\n", 2)[-1] + "\n")
    S("## 24. Identification Threats\n\n" + (notes.split("<!--THREATS-->")[1].split("<!--END-THREATS-->")[0]
                                              if "<!--THREATS-->" in notes else "") + "\n")
    bun = []
    for k, b in B.items():
        bun.append(f"### PAPER {k}: {b['name']} -- **{b['decision']}**\n")
        if "answers" in b:
            bun.append(f"- Research question: {b['q']}\n- Primary outcome: {b['primary']} ({b['rating']}, {b['main_result']})\n"
                       f"- Secondary outcomes: {b['secondary']}\n- Strongest secondary result: {b['strongest']}\n"
                       f"- Publication score (heuristic): {f(b['score'], 1)} ({b['potential']})\n- Best journal: {b['journal']}\n"
                       f"- Main threat: {b['threat']}\n\n| Question | Answer |\n|---|---|\n" +
                       "\n".join(f"| {q} | {a} |" for q, a in b["answers"].items()) + "\n")
    (FINAL / "paper_bundles.md").write_text("# Paper bundles (Sections 53-54)\n\n" + "\n".join(bun), encoding="utf-8")
    S("## 25. Best Paper Design\n\n" + (notes.split("<!--BEST-->")[1].split("<!--END-BEST-->")[0] if "<!--BEST-->" in notes else "") + "\n")
    S("## 26. Alternative Paper Designs\n\n" + "\n".join(bun) + "\n")
    S("## 27. Data Improvements That Would Matter Most\n\n" + (notes.split("<!--DATA-->")[1].split("<!--END-DATA-->")[0]
                                                               if "<!--DATA-->" in notes else "") + "\n\n" + qe.split("## Assessment")[-1] + "\n")
    answers = {"A. Strongest credible causal result": A, "B. Most statistically robust outcome": f"{Bq.Outcome} ({Bq.Robustness_Rating})",
               "C. Largest economically meaningful effect": C, "D. Best novelty x feasibility": D,
               "E. Highest publication potential": f"{E.Outcome} (score {f(E.Publication_Score, 1)})",
               "F. Promising but underpowered": F, "G. Effects that disappear under robustness": G,
               "H. Driven by Oklahoma or Texas?": H, "I. Driven by 2011 Super Outbreak / major events?": I_,
               "J. Does treatment timing matter?": J, "K. Does strict definition survive?": K,
               "L. Results for EF2+?": "; ".join(L_), "M. Do modern estimators confirm TWFE?": Mq,
               "N. Pretrends acceptable?": N_, "O. Placebos pass?": O_, "P. Completion timing reliable?": P_,
               "Q. Convincing mechanism evidence?": Q_,
               "R. Treatment adoption too endogenous?": (notes.split("<!--R-->")[1].split("<!--END-R-->")[0] if "<!--R-->" in notes else "see Section 24"),
               "S. Would a funding cutoff help?": "Yes, materially, but no usable public cutoff exists (see quasi_experiment_assessment.md).",
               "T. Best paper to write": (notes.split("<!--T-->")[1].split("<!--END-T-->")[0] if "<!--T-->" in notes else "see Section 25")}
    ov = FINAL / "analyst_answers.json"
    if ov.exists():   # analyst overrides where rule output lacks context; rule output kept alongside
        for k, v in json.loads(ov.read_text(encoding="utf-8")).items():
            key = next((a for a in answers if a.startswith(k + ".")), None)
            if key:
                answers[key] = f"{v} *(analyst answer; rule-based output was: {answers[key]})*"
    S("## 28. Final GO/NO-GO Recommendation\n\n### Explicit answers\n\n" + "\n".join(f"**{k}.** {v}\n" for k, v in answers.items()))
    S(f"\n### Decision rule applied\n\nGO requires a ROBUST/strongly MODERATELY ROBUST economically important outcome, "
      f"credible identification, acceptable pretrends/placebos and adequate power. Decision basis: {dec_reason}.\n")
    S(f"\n# FINAL PROJECT DECISION: {decision}\n")
    (FINAL / "research_assessment.md").write_text("\n".join(sec), encoding="utf-8")
    (FINAL / "terminal_summary.md").write_text(hr.to_markdown(index=False) + "\n\n" + "\n".join(
        f"{k}: {v}" for k, v in (json.loads((FINAL / 'analyst_headlines.json').read_text()) if (FINAL / 'analyst_headlines.json').exists() else {}).items())
        + f"\n\nFINAL PROJECT DECISION: {decision}\n", encoding="utf-8")
    log.info("report written; decision %s", decision)
    print(hr.drop(columns=["Effect size"]).assign(**{"Effect % mean": hr["Effect size"]}).to_markdown(index=False))


if __name__ == "__main__":
    main()
