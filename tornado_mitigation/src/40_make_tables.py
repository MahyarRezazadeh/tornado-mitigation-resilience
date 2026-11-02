"""Assemble Tables 7-8, the master outcome assessment (Section 50) and human-readable tables (51, 64).

Ranking (Section 51): identification credibility, then robustness, then publication potential, then
feasibility. Never by p-value.
Outputs: output/tables/table7_mechanisms.md, table8_heterogeneity.md,
         output/final/master_outcome_assessment.{csv,xlsx,md}
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from utils import FINAL, INTER, MODELS, TABLES, get_logger

log = get_logger(__file__)
ROB_ORDER = {"ROBUST": 0, "MODERATELY ROBUST": 1, "NO DETECTABLE EFFECT": 2, "MIXED": 3, "UNDERPOWERED": 4,
             "NOT ROBUST": 5, "INFEASIBLE": 6}
ID_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}


def mech_result(var, mech, pr):
    if var in ("separation_rate", "hire_rate", "turnover", "log_employment"):
        s = pr.get("separation_rate"); h = pr.get("hire_rate"); t = pr.get("turnover")
        if s is not None and h is not None:
            ok = s["beta"] < 0 and s["p"] < 0.10 and not (h["beta"] > 0 and h["p"] < 0.10)
            return "M3 supported" if ok else "M3 not supported (separations not reduced)"
    if var in ("establishment_death_rate", "job_destruction_rate", "small_estab_death_rate"):
        m4 = mech[(mech.mechanism == "M4") & (mech.term == "MTS") & (mech.outcome == ("establishment_death_rate" if var != "job_destruction_rate" else var))]
        if len(m4):
            r = m4.iloc[0]
            return f"M4 small-firm diff b={r.beta:.3g} (p={r.p:.2f})"
    m1 = mech[(mech.mechanism == "M1") & (mech.term == "MI") & (mech.sample == "all county-quarters")]
    if len(m1):
        return "M1: " + "; ".join(f"{r.outcome} b={r.beta:.3g} (p={r.p:.2f})" for _, r in m1.iterrows())
    return "n/a"


def main() -> None:
    pr = pd.read_csv(MODELS / "primary_results.csv")
    rm = pd.read_csv(MODELS / "robustness_metrics.csv")
    pw = pd.read_csv(MODELS / "power.csv")
    ps = pd.read_csv(MODELS / "publication_scores.csv")
    jf = pd.read_csv(MODELS / "journal_fit.csv")
    fe = pd.read_csv(TABLES / "outcome_feasibility.csv")
    mech = pd.read_csv(MODELS / "mechanisms.csv") if (MODELS / "mechanisms.csv").exists() else pd.DataFrame(columns=["mechanism", "term", "sample", "outcome", "beta", "p"])
    reg = pd.read_csv(TABLES.parents[1] / "config" / "outcome_registry.csv")
    prd = {r.outcome_var: r for _, r in pr.iterrows()}

    # Table 7 & 8
    if len(mech):
        (TABLES / "table7_mechanisms.md").write_text("# Table 7. Mechanisms\n\n" + mech.round(4).to_markdown(index=False)
                                                     + ("\n\n## Severity gradient\n\n" + pd.read_csv(MODELS / "severity_gradient.csv").round(4).to_markdown(index=False)
                                                        if (MODELS / "severity_gradient.csv").exists() else ""), encoding="utf-8")
    if (MODELS / "heterogeneity.csv").exists():
        h = pd.read_csv(MODELS / "heterogeneity.csv")
        txt = "# Table 8. Heterogeneity (EXPLORATORY; BH q within family)\n\n" + h.round(4).to_markdown(index=False)
        if (MODELS / "demographic_cells.csv").exists():
            txt += "\n\n## Worker / firm-size cells\n\n" + pd.read_csv(MODELS / "demographic_cells.csv").round(4).to_markdown(index=False)
        (TABLES / "table8_heterogeneity.md").write_text(txt, encoding="utf-8")

    rows = []
    for _, o in reg.iterrows():
        v = o.variable
        p = pr[pr.outcome_var == v].iloc[0] if (pr.outcome_var == v).any() else None
        m = rm[rm.outcome_var == v].iloc[0] if (rm.outcome_var == v).any() else pd.Series(dtype=object)
        w = pw[pw.outcome == o.outcome].iloc[0] if (pw.outcome == o.outcome).any() else pd.Series(dtype=object)
        s = ps[ps.outcome_var == v].iloc[0] if (ps.outcome_var == v).any() else pd.Series(dtype=object)
        j = jf[jf.outcome_var == v].iloc[0] if (jf.outcome_var == v).any() else pd.Series(dtype=object)
        f = fe[fe.group == o.group].iloc[0]
        ok = p is not None and p.status == "ok"
        rows.append({
            "Outcome": o.outcome, "Outcome_Family": o.family, "Dataset": o.dataset,
            "Frequency": "quarterly" if o.freq == "q" else "annual", "Geography": "county",
            "Years": f"{int(f.first_year)}-{int(f.last_year)}" if pd.notna(f.get("first_year")) else "",
            "Observations": p.N if ok else np.nan, "Counties": p.counties if ok else np.nan,
            "Treated_Counties": p.treated_counties if ok else np.nan,
            "PostTreatment_Tornado_Events": p.treated_tornado_obs if ok else np.nan,
            "Untreated_Tornado_Events": p.untreated_tornado_obs if ok else np.nan,
            "Feasibility_Score": f.feasibility_score, "Feasibility_Rating": f.feasibility_rating,
            "Primary_Beta": p.beta if ok else np.nan, "Primary_SE": p.se if ok else np.nan,
            "Primary_P": p.p if ok else np.nan, "BH_Q_Value": m.get("bh_q"), "Holm_P": m.get("holm_p"),
            "CI_Lower": p.ci_low if ok else np.nan, "CI_Upper": p.ci_high if ok else np.nan,
            "Outcome_Mean": p.y_mean if ok else np.nan, "Outcome_SD": p.y_sd if ok else np.nan,
            "Effect_Percent_Mean": p.effect_pct_mean if ok else np.nan, "Effect_SD": p.effect_sd if ok else np.nan,
            "Expected_Sign": o.expected_sign, "Observed_Sign": ("+" if p.beta > 0 else "-") if ok else "",
            "Main_Result": m.get("main_result", "Infeasible"),
            "Mechanism_Result": mech_result(v, mech, prd) if ok else "",
            "Pretrend_P": m.get("pretrend_p"), "Placebo_P": m.get("placebo_p"),
            "Sign_Consistency": m.get("sign_consistency"), "Sig_Consistency": m.get("sig_consistency"),
            "Leave_State_Out_Sign_Share": m.get("leave_state_out_sign_share"),
            "Treatment_Definition_Pass": m.get("treatment_definition_pass"), "Timing_Pass": m.get("timing_pass"),
            "Hazard_Definition_Pass": m.get("hazard_definition_pass"), "Estimator_Pass": m.get("estimator_pass"),
            "Matching_Pass": m.get("matching_pass"), "Robust_Specs": m.get("robust_specs"),
            "Total_Credible_Specs": m.get("n_credible"),
            "Robustness_Rating": m.get("robustness_rating", "INFEASIBLE"),
            "Power_Rating": w.get("power_rating", ""), "Novelty_Rating": s.get("novelty_rating", ""),
            "Identification_Rating": s.get("identification_rating", ""),
            "Data_Quality_Rating": f.feasibility_rating, "Publication_Score": s.get("publication_score"),
            "Best_Journal_Fit": j.get("best_journal", ""), "Second_Journal_Fit": j.get("second_journal", ""),
            "Third_Journal_Fit": j.get("third_journal", ""), "Key_Limitation": "", "Recommendation": ""})
    # infeasible groups without registry rows
    st = json.loads((INTER / "public_finance_status.json").read_text())
    for g, name, why in [(13, "Local fiscal resilience", st["reason"]),
                         (15, "Warning-induced shutdown costs", "No public national high-frequency county activity data")]:
        f = fe[fe.group == g].iloc[0]
        rows.append({"Outcome": name, "Outcome_Family": "fiscal" if g == 13 else "warning", "Dataset": f.dataset,
                     "Feasibility_Score": f.feasibility_score, "Feasibility_Rating": f.feasibility_rating,
                     "Main_Result": "Infeasible", "Robustness_Rating": "INFEASIBLE", "Key_Limitation": why,
                     "Recommendation": "Do not pursue with public data"})
    M = pd.DataFrame(rows)
    # key limitation / recommendation (rule-based; refined in report)
    for i, r in M.iterrows():
        if r.Robustness_Rating == "INFEASIBLE":
            continue
        lim = ["treatment timing is a proxy (no completion date)"]
        if r.Power_Rating == "UNDERPOWERED":
            lim.append("CI too wide to rule out meaningful effects")
        if pd.notna(r.Pretrend_P) and r.Pretrend_P < 0.10:
            lim.append("differential pre-trend")
        if r.Estimator_Pass == 0:
            lim.append("modern estimators do not support")
        if pd.isna(r.Total_Credible_Specs):
            lim.append("exploratory: primary spec only, no robustness grid (rating cannot exceed MIXED)")
        M.at[i, "Key_Limitation"] = "; ".join(lim)
        M.at[i, "Recommendation"] = {"ROBUST": "Lead result", "MODERATELY ROBUST": "Pursue; strengthen identification",
                                     "NO DETECTABLE EFFECT": "Report as informative null",
                                     "MIXED": "Secondary/appendix only", "UNDERPOWERED": "Appendix; not a headline",
                                     "NOT ROBUST": "Do not claim"}.get(r.Robustness_Rating, "")
        if r.Main_Result == "Adverse" and r.Robustness_Rating in ("ROBUST", "MODERATELY ROBUST", "MIXED"):
            M.at[i, "Recommendation"] = ("Report transparently; adverse sign most likely reflects post-disaster "
                                         "selection; do not claim causal harm (fails multiple testing)"
                                         if (pd.isna(r.BH_Q_Value) or r.BH_Q_Value > 0.10) else
                                         "Report transparently; investigate selection before any causal claim")
    M["_id"] = M.Identification_Rating.map(ID_ORDER).fillna(3)
    M["_rb"] = M.Robustness_Rating.map(ROB_ORDER).fillna(7)
    M = M.sort_values(["_id", "_rb", "Publication_Score", "Feasibility_Score"], ascending=[True, True, False, False])
    M = M.drop(columns=["_id", "_rb"]).reset_index(drop=True)
    M.insert(0, "Rank", np.arange(1, len(M) + 1))
    M.to_csv(FINAL / "master_outcome_assessment.csv", index=False)
    with pd.ExcelWriter(FINAL / "master_outcome_assessment.xlsx", engine="xlsxwriter") as xw:
        M.to_excel(xw, sheet_name="master", index=False)
        ws = xw.sheets["master"]
        ws.freeze_panes(1, 2)
        ws.autofilter(0, 0, len(M), M.shape[1] - 1)
        for k, c in enumerate(M.columns):
            ws.set_column(k, k, min(40, max(10, len(c) + 2)))
        pd.read_csv(TABLES / "outcome_feasibility.csv").to_excel(xw, sheet_name="feasibility", index=False)
        rm.to_excel(xw, sheet_name="robustness_metrics", index=False)
        ps.to_excel(xw, sheet_name="publication_scores", index=False)
        jf.to_excel(xw, sheet_name="journal_fit", index=False)

    def fnum(x, d=3):
        return "" if pd.isna(x) else f"{x:.{d}f}"
    hr = pd.DataFrame({
        "Rank": M.Rank, "Outcome": M.Outcome, "Feasibility": M.Feasibility_Rating, "Primary result": M.Main_Result,
        "Effect size": M.Effect_Percent_Mean.map(lambda x: "" if pd.isna(x) else f"{x:.2f}% of mean"),
        "p-value": M.Primary_P.map(fnum), "q-value": M.BH_Q_Value.map(fnum), "Pretrend": M.Pretrend_P.map(fnum),
        "Robust?": M.Robustness_Rating, "Mechanism supported?": M.Mechanism_Result, "Power": M.Power_Rating,
        "Novelty": M.Novelty_Rating, "Publication potential": M.Publication_Score.map(lambda x: fnum(x, 1)),
        "Best journal": M.Best_Journal_Fit, "Recommendation": M.Recommendation})
    res = pd.DataFrame({
        "Outcome": M.Outcome, "Primary beta": M.Primary_Beta.map(lambda x: fnum(x, 5)), "SE": M.Primary_SE.map(lambda x: fnum(x, 5)),
        "p-value": M.Primary_P.map(fnum), "BH q-value": M.BH_Q_Value.map(fnum),
        "Effect % mean": M.Effect_Percent_Mean.map(lambda x: fnum(x, 2)),
        "95% CI": [f"[{fnum(a, 4)}, {fnum(b, 4)}]" if pd.notna(a) else "" for a, b in zip(M.CI_Lower, M.CI_Upper)],
        "Expected sign": M.Expected_Sign, "Observed result": M.Main_Result, "Pretrend p": M.Pretrend_P.map(fnum),
        "Placebo p": M.Placebo_P.map(fnum), "Sign consistency": M.Sign_Consistency.map(lambda x: fnum(x, 2)),
        "Leave-state-out consistency": M.Leave_State_Out_Sign_Share.map(lambda x: fnum(x, 2)),
        "Robustness": M.Robustness_Rating, "Power": M.Power_Rating, "Mechanism": M.Mechanism_Result,
        "Novelty": M.Novelty_Rating, "Publication score": M.Publication_Score.map(lambda x: fnum(x, 1)),
        "Best journal": M.Best_Journal_Fit})
    md = ["# Master Outcome Assessment", "",
          "Ranked by identification credibility, then robustness, then publication potential, then feasibility (never by p-value).",
          "Primary specification: strict FEMA tornado/wind mitigation (obligation + 2y), EF1+ tornado, county FE + state x time FE, county-clustered SE.",
          "", "## Human-readable summary (Section 51)", "", hr.to_markdown(index=False), "",
          "## Result table (Section 64)", "", res.to_markdown(index=False), "",
          "Full column set (Section 50) in master_outcome_assessment.csv / .xlsx."]
    (FINAL / "master_outcome_assessment.md").write_text("\n".join(md), encoding="utf-8")
    hr.to_csv(FINAL / "final_summary_table.csv", index=False)
    log.info("master table written (%d outcomes)", len(M))


if __name__ == "__main__":
    main()
