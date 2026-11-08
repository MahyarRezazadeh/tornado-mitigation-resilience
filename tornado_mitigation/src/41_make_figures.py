"""Figures 6-20 (Figures 1-5 are produced by 25_descriptive_analysis.py). All causal plots show 95% CIs."""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from utils import FIGS, MODELS, TABLES, get_logger  # noqa: E402

log = get_logger(__file__)
Z = 1.96


def es_plot(var, title, fname, unit="quarters"):
    f = MODELS / f"tornado_es_{var}.csv"
    if not f.exists():
        return
    d = pd.read_csv(f).sort_values("k")
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    ax = axes[0]
    for col, lab, off, c in [("unmitigated", "Non-mitigated tornado", -0.12, "tab:red"),
                             ("mitigated", "Mitigated tornado", 0.12, "tab:blue")]:
        ax.errorbar(d.k + off, d[col], yerr=Z * d[col + "_se"], fmt="o-", ms=3, capsize=2, label=lab, color=c)
    ax.axhline(0, color="k", lw=0.7); ax.axvline(-0.5, color="grey", ls="--", lw=0.7)
    ax.set_xlabel(f"{unit} relative to EF1+ tornado (k=-1 reference)"); ax.legend(fontsize=8)
    ax.set_title("Response functions")
    ax = axes[1]
    ax.errorbar(d.k, d["diff"], yerr=Z * d["diff_se"], fmt="o-", ms=3, capsize=2, color="k")
    ax.axhline(0, color="k", lw=0.7); ax.axvline(-0.5, color="grey", ls="--", lw=0.7)
    ax.set_xlabel(f"{unit} relative to tornado"); ax.set_title("Difference: mitigated - non-mitigated (95% CI)")
    s = pd.read_csv(MODELS / "event_study_summary.csv").set_index("outcome")
    if var in s.index:
        ax.text(0.02, 0.95, f"pre-trend F={s.loc[var, 'pretrend_F']:.2f}, p={s.loc[var, 'pretrend_p']:.3f}",
                transform=ax.transAxes, fontsize=8, va="top")
    fig.suptitle(title)
    fig.tight_layout(); fig.savefig(FIGS / fname, dpi=160); plt.close(fig)


def spec_curve(var, title, fname):
    f = MODELS / f"robustness_{var}.csv"
    if not f.exists():
        return
    d = pd.read_csv(f)
    d = d[(d.status == "ok") & (d.credible_specification == 1)].sort_values("beta").reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(11, 4.5))
    col = np.where(d.p < 0.05, "tab:blue", np.where(d.p < 0.10, "tab:cyan", "grey"))
    ax.errorbar(d.index, d.beta, yerr=[d.beta - d.ci_low, d.ci_high - d.beta], fmt="none", ecolor="lightgrey", lw=1)
    ax.scatter(d.index, d.beta, c=col, s=14, zorder=3)
    pi = d.index[d.specification_id == "R00"]
    if len(pi):
        ax.scatter(pi, d.loc[pi, "beta"], marker="*", s=180, color="red", zorder=4, label="primary")
    ax.axhline(0, color="k", lw=0.7)
    ax.set_xticks(d.index, d.specification_id, rotation=90, fontsize=6)
    ax.set_ylabel("beta (Mitigated x Tornado), 95% CI"); ax.legend()
    ax.set_title(title + "  (blue p<.05, cyan p<.10, grey n.s.; credible specs only)")
    fig.tight_layout(); fig.savefig(FIGS / fname, dpi=160); plt.close(fig)


def coef_plot(df, label_col, title, fname, beta="beta", se="se", group=None):
    if df is None or len(df) == 0:
        return
    df = df.dropna(subset=[beta, se]).reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(8, max(3, 0.28 * len(df) + 1)))
    y = np.arange(len(df))
    ax.errorbar(df[beta], y, xerr=Z * df[se], fmt="o", ms=4, capsize=2)
    ax.axvline(0, color="k", lw=0.7)
    ax.set_yticks(y, df[label_col], fontsize=7)
    ax.set_title(title, fontsize=10)
    ax.set_xlabel("estimate with 95% CI")
    fig.tight_layout(); fig.savefig(FIGS / fname, dpi=160); plt.close(fig)


def main() -> None:
    es_plot("log_employment", "Figure 6. Employment (log end-of-quarter) around EF1+ tornadoes", "fig06_es_employment.png")
    es_plot("separation_rate", "Figure 7. Worker separation rate around EF1+ tornadoes", "fig07_es_separations.png")
    es_plot("log_earnings", "Figure 8. Earnings (log) around EF1+ tornadoes", "fig08_es_earnings.png")
    es_plot("establishment_death_rate", "Figure 9. Establishment death rate around EF1+ tornado years (BDS)",
            "fig09_es_establishment_deaths.png", unit="years")
    es_plot("job_destruction_rate", "Figure 10. Job destruction rate around EF1+ tornado years (BDS)",
            "fig10_es_job_destruction.png", unit="years")
    sg = MODELS / "severity_gradient.csv"
    if sg.exists():
        d = pd.read_csv(sg)
        outs = d.outcome.unique()
        fig, axes = plt.subplots(1, len(outs), figsize=(4 * len(outs), 3.6))
        for ax, o in zip(np.atleast_1d(axes), outs):
            s = d[d.outcome == o]
            x = np.arange(len(s))
            ax.errorbar(x - 0.1, s.tornado_effect, yerr=Z * s.tornado_se, fmt="o", label="tornado (unmitigated)")
            ax.errorbar(x + 0.1, s.mitig_diff, yerr=Z * s.mitig_diff_se, fmt="s", label="mitigated - unmitigated")
            ax.axhline(0, color="k", lw=0.7); ax.set_xticks(x, s.bin); ax.set_title(o, fontsize=9)
        np.atleast_1d(axes)[0].legend(fontsize=7)
        fig.suptitle("Figure 11. Severity gradient (95% CI)")
        fig.tight_layout(); fig.savefig(FIGS / "fig11_severity_gradient.png", dpi=160); plt.close(fig)
    mech = pd.read_csv(MODELS / "mechanisms.csv") if (MODELS / "mechanisms.csv").exists() else None
    if mech is not None and "mechanism" in mech:
        m4 = mech[mech.mechanism == "M4"].copy()
        m4["lab"] = m4.outcome + " | " + m4.term + " | " + m4["sample"]
        coef_plot(m4, "lab", "Figure 12. Small-business heterogeneity (MTS = extra effect for small firms)",
                  "fig12_small_business.png")
    ib = MODELS / "industry_by_group.csv"
    if ib.exists():
        d = pd.read_csv(ib)
        d = d[d.status == "ok"]
        d["lab"] = d.source + " " + d.outcome + " | " + d.industry
        coef_plot(d.sort_values(["outcome", "industry"]), "lab", "Figure 13. Industry heterogeneity: Mitigated x Tornado by industry",
                  "fig13_industry.png")
    dc = MODELS / "demographic_cells.csv"
    if dc.exists():
        d = pd.read_csv(dc)
        d = d[d.outcome == "separation_rate"]
        d["lab"] = d.family + ": " + d.group + np.where(d.high_suppression_flag, " (high supp.)", "")
        coef_plot(d, "lab", "Figure 14. Worker-group heterogeneity: separation rate, Mitigated x Tornado",
                  "fig14_demographic.png")
    lo = MODELS / "loso_results.csv"
    if lo.exists():
        d = pd.read_csv(lo)
        outs = d.outcome.unique()
        fig, axes = plt.subplots(1, len(outs), figsize=(3.2 * len(outs), 8), sharey=True)
        for ax, o in zip(np.atleast_1d(axes), outs):
            s = d[d.outcome == o].reset_index(drop=True)
            y = np.arange(len(s))
            c = np.where(s.focus_state, "tab:red", "tab:blue")
            ax.errorbar(s.beta, y, xerr=Z * s.SE, fmt="none", ecolor="lightgrey")
            ax.scatter(s.beta, y, c=c, s=10)
            ax.axvline(s.primary_beta.iloc[0], color="k", ls="--", lw=0.8)
            ax.axvline(0, color="k", lw=0.5)
            ax.set_title(o, fontsize=8)
        np.atleast_1d(axes)[0].set_yticks(np.arange(len(s)), s.state_removed, fontsize=6)
        fig.suptitle("Figure 15. Leave-one-state-out (red = high-tornado focus states; dashed = primary)")
        fig.tight_layout(); fig.savefig(FIGS / "fig15_loso.png", dpi=160); plt.close(fig)
    spec_curve("separation_rate", "Figure 16. Specification curve: separation rate", "fig16_spec_separations.png")
    spec_curve("log_employment", "Figure 17. Specification curve: log employment", "fig17_spec_employment.png")
    spec_curve("establishment_death_rate", "Figure 18. Specification curve: establishment death rate", "fig18_spec_estab_deaths.png")
    rows = []
    for v in ["separation_rate", "log_employment", "log_earnings", "establishment_death_rate", "job_destruction_rate"]:
        f = MODELS / f"robustness_{v}.csv"
        if f.exists():
            d = pd.read_csv(f)
            d = d[d.specification_id.isin(["R00", "R02", "R03", "R62", "R64", "R65", "R66"]) & (d.status == "ok")]
            for _, r in d.iterrows():
                rows.append({"outcome": v, "spec": r.description, "beta_std": r.beta / r.y_sd, "se_std": r.se / r.y_sd})
    if rows:
        d = pd.DataFrame(rows)
        d["lab"] = d.outcome + " | " + d.spec
        coef_plot(d, "lab", "Figure 19. Treatment-definition sensitivity (beta in SD units, 95% CI)", "fig19_treatment_defs.png",
                  beta="beta_std", se="se_std")
    ps = MODELS / "publication_scores.csv"
    fe = TABLES / "outcome_feasibility.csv"
    if ps.exists() and fe.exists():
        p = pd.read_csv(ps)
        f = pd.read_csv(fe)[["variable", "feasibility_score"]]
        d = p.merge(f, left_on="outcome_var", right_on="variable", how="left")
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(d.feasibility_score, d.publication_score)
        for _, r in d.iterrows():
            ax.annotate(r.outcome[:28], (r.feasibility_score, r.publication_score), fontsize=6)
        ax.set_xlabel("Feasibility score"); ax.set_ylabel("Publication-potential score (heuristic)")
        ax.set_title("Figure 20. Publication potential vs feasibility")
        fig.tight_layout(); fig.savefig(FIGS / "fig20_pub_vs_feasibility.png", dpi=160); plt.close(fig)
    log.info("figures done")


if __name__ == "__main__":
    main()
