"""Primary interaction models for every registered outcome (Sections 24-25, 36).

Also reports the county FE + time FE benchmark (no state x time) and economic-significance
translations (beta as % of mean / SD; implied counts evaluated at treated-tornado observations).
Outputs: output/models/primary_results.csv, output/tables/table4/5/6_*.md
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import est
from utils import MODELS, TABLES, get_logger

log = get_logger(__file__)


def meaningful(r: dict, expected: str) -> float:
    """E* (pre-registered): 50% offset of the tornado main effect if it is disruptive, else 0.05 SD."""
    g = r.get("gamma_T", np.nan)
    disruptive = (expected == "+" and g < 0) or (expected == "-" and g > 0) or (expected == "0" and abs(g) > 0)
    if np.isfinite(g) and disruptive and r.get("gamma_T_se", np.inf) > 0 and abs(g) / r["gamma_T_se"] > 1:
        return 0.5 * abs(g)
    # POST-FREEZE CLARIFICATION (labeled in preregistration_snapshot.md): SD = within-county SD
    # (net of county and state-time means); raw SD of log levels reflects county size, not variation.
    return 0.05 * r["y_sd_within"]


def main() -> None:
    reg = est.registry()
    rows = []
    for _, o in reg.iterrows():
        align = o.align if isinstance(o.align, str) else "mar"
        s = est.Spec(outcome=o.variable, freq=o.freq, align=align)
        r = est.run(s)
        b = est.run(s.but(fe="twfe", label="county+time FE"))
        r.update({k: o[k] for k in ["outcome_id", "outcome", "group", "family", "dataset", "expected_sign", "primary"]})
        r["outcome_var"] = o.variable
        r["outcome"] = o.outcome
        r["beta_twfe_benchmark"] = b.get("beta")
        r["p_twfe_benchmark"] = b.get("p")
        if r.get("status") == "ok":
            r["E_star"] = meaningful(r, o.expected_sign)
            r["E_star_rawSD_version"] = 0.05 * r["y_sd"] if r["E_star"] == 0.05 * r["y_sd_within"] else r["E_star"]
            r["effect_sd_within"] = r["beta"] / r["y_sd_within"]
            r["effect_pct_mean"] = 100 * r["beta"] / r["y_mean"] if abs(r["y_mean"]) > 1e-9 else np.nan
            r["effect_sd"] = r["beta"] / r["y_sd"]
            r["offset_share_of_tornado_effect"] = -r["beta"] / r["gamma_T"] if abs(r["gamma_T"]) > 1e-12 else np.nan
        rows.append(r)
        log.info("%-45s b=%s se=%s p=%s gT=%s N=%s", o.outcome, f"{r.get('beta', np.nan):.4g}",
                 f"{r.get('se', np.nan):.3g}", f"{r.get('p', np.nan):.3f}", f"{r.get('gamma_T', np.nan):.4g}", r.get("N"))
    df = pd.DataFrame(rows)
    df.to_csv(MODELS / "primary_results.csv", index=False)

    def fmt(sub):
        t = sub[["outcome", "beta", "se", "t", "p", "ci_low", "ci_high", "gamma_T", "gamma_T_se", "y_mean",
                 "effect_pct_mean", "N", "counties", "treated_counties", "treated_tornado_obs", "r2_within"]].copy()
        t.columns = ["Outcome", "beta (MxT)", "SE", "t", "p", "CI low", "CI high", "Tornado main effect", "SE(T)",
                     "Mean Y", "beta % mean", "N", "Counties", "Treated counties", "Treated tornado obs", "Within R2"]
        return t.round(4).to_markdown(index=False)
    hdr = ("Model: Y = b*Mitigated*Tornado + g1*Mitigated + g2*Tornado + county FE + state x time FE; "
           "clustered by county. Tornado = EF1+ (quarterly: same quarter; annual: March-aligned). "
           "Treatment = strict, obligation+2y.\n\n")
    lab = df[df.family == "labor"]
    bus = df[df.family == "business"]
    hh = df[df.family == "household"]
    (TABLES / "table4_labor_results.md").write_text("# Table 4. Main labor-market results\n\n" + hdr + fmt(lab), encoding="utf-8")
    (TABLES / "table5_business_results.md").write_text("# Table 5. Business dynamics results\n\n" + hdr + fmt(bus), encoding="utf-8")
    (TABLES / "table6_migration_housing_fiscal.md").write_text(
        "# Table 6. Migration / housing / fiscal results\n\n" + hdr + fmt(hh) +
        "\n\nLocal fiscal outcomes: LOW feasibility, not estimated (see feasibility table).", encoding="utf-8")


if __name__ == "__main__":
    main()
