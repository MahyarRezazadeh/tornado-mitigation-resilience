"""Journal fit (Section 41): rule-based HIGH / MEDIUM / LOW fit per outcome; no acceptance probabilities.

Fit depends on (i) topical fit of the outcome domain and (ii) whether the evidence meets the journal's
evidentiary bar (proxied by robustness rating and identification rating).
Output: output/models/journal_fit.csv, output/tables/journal_fit.md
"""
from __future__ import annotations

import pandas as pd

from utils import MODELS, TABLES, get_logger

log = get_logger(__file__)
J = {  # journal: (domains with topical fit, bar: 'top'/'field'/'specialized', requirement text)
    "Journal of Environmental Economics and Management": ({"labor", "business", "household"}, "top",
        "strong quasi-experimental identification, clear adaptation contribution, clean event studies, economic significance, mechanisms"),
    "Journal of Policy Analysis and Management": ({"labor", "business", "household"}, "top",
        "strong program evaluation with credible policy counterfactual; distributional/implementation relevance"),
    "Journal of Human Resources": ({"labor"}, "top", "major labor-market contribution, worker-level mechanism, extremely strong identification"),
    "Journal of Urban Economics": ({"household"}, "top", "strong spatial/local-equilibrium or migration contribution"),
    "Labour Economics": ({"labor"}, "field", "clear labor-market mechanism and worker heterogeneity"),
    "ILR Review": ({"labor"}, "field", "clear labor-market mechanism, worker heterogeneity, policy relevance"),
    "Regional Science and Urban Economics": ({"labor", "business", "household"}, "field", "credible local economic resilience contribution"),
    "Journal of Regional Science": ({"labor", "business", "household"}, "field", "credible local economic resilience contribution"),
    "Land Economics": ({"household", "business"}, "field", "land/housing/environmental policy angle with credible design"),
    "Economic Inquiry": ({"labor", "business", "household"}, "field", "broad-interest applied question with clean identification"),
    "Small Business Economics": ({"business"}, "field", "small-business mechanism (liquidity, size heterogeneity)"),
    "Journal of Housing Economics": ({"household"}, "field", "housing/rebuilding outcomes"),
    "National Tax Journal": ({"fiscal"}, "field", "local public finance outcomes (infeasible here)"),
    "Review of Regional Studies": ({"labor", "business", "household"}, "specialized", "regional applied evidence"),
    "Natural Hazards Review": ({"labor", "business", "household", "damage"}, "specialized", "hazard-mitigation evaluation for practitioners"),
    "Risk Analysis": ({"labor", "business", "household", "damage"}, "specialized", "risk-reduction evidence, decision relevance"),
}
OK_BAR = {"top": {"ROBUST"}, "field": {"ROBUST", "MODERATELY ROBUST", "NO DETECTABLE EFFECT"},
          "specialized": {"ROBUST", "MODERATELY ROBUST", "NO DETECTABLE EFFECT", "MIXED", "UNDERPOWERED"}}


def main() -> None:
    rm = pd.read_csv(MODELS / "robustness_metrics.csv")
    pr = pd.read_csv(MODELS / "primary_results.csv").set_index("outcome_var")
    ps = pd.read_csv(MODELS / "publication_scores.csv").set_index("outcome_var")
    rows = []
    for _, m in rm.iterrows():
        fam = pr.loc[m.outcome_var, "family"]
        ident = ps.loc[m.outcome_var, "identification_rating"]
        ranked = []
        for j, (doms, bar, req) in J.items():
            topical = fam in doms
            meets = m.robustness_rating in OK_BAR[bar] and (bar != "top" or ident == "HIGH")
            fit = "HIGH FIT" if topical and meets else "MEDIUM FIT" if topical and (bar != "top" or m.robustness_rating in OK_BAR["field"]) else "LOW FIT"
            if not topical:
                fit = "LOW FIT"
            score = {"HIGH FIT": 3, "MEDIUM FIT": 2, "LOW FIT": 1}[fit] + {"top": 0.3, "field": 0.2, "specialized": 0.1}[bar] * (fit != "LOW FIT")
            ranked.append((score, j, fit, req))
        ranked.sort(reverse=True)
        top_req = ranked[0][3]
        rows.append({"outcome": m.outcome, "outcome_var": m.outcome_var, "robustness_rating": m.robustness_rating,
                     "best_journal": f"{ranked[0][1]} ({ranked[0][2]})", "second_journal": f"{ranked[1][1]} ({ranked[1][2]})",
                     "third_journal": f"{ranked[2][1]} ({ranked[2][2]})",
                     "what_would_make_top_choice_realistic": top_req,
                     "all_fits": "; ".join(f"{j}: {f}" for _, j, f, _ in ranked)})
    jf = pd.DataFrame(rows)
    jf.to_csv(MODELS / "journal_fit.csv", index=False)
    (TABLES / "journal_fit.md").write_text("# Journal fit (no acceptance probabilities)\n\n" +
                                           jf.drop(columns=["all_fits"]).to_markdown(index=False), encoding="utf-8")
    log.info("journal fit written")


if __name__ == "__main__":
    main()
