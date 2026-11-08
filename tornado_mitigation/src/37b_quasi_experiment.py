"""Quasi-experiment search (Section 42) using OpenFEMA HmaSubapplications + HMA projects.

Quantifies: funded vs not-funded tornado/wind applications, availability of BCR (running variable),
mass near the BCR = 1 threshold (manipulation check), selection-status fields (BRIC/FMA national
competition), and the county-level 'denied-only' applicant pool usable as an alternative control group.
Then estimates the primary model with the comparison group restricted to applicant-but-never-funded
counties (design check, labeled exploratory).
Output: output/final/quasi_experiment_assessment.md, output/diagnostics/qe_*.csv
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import est
from utils import DIAG, FINAL, INTER, RAW, get_logger

log = get_logger(__file__)


def main() -> None:
    s = pd.read_parquet(RAW / "fema" / "fema_subapplications_raw.parquet")
    p = pd.read_parquet(INTER / "fema_projects_classified.parquet")
    wind = p[p.treat_strict == 1].copy()
    wind["bcr"] = pd.to_numeric(wind.benefitCostRatio, errors="coerce").replace(0, np.nan)
    st = wind.status.value_counts()
    funded = wind.funded.sum()
    notf = wind.not_funded.sum()
    bcr = wind.bcr.dropna()
    near = bcr[(bcr > 0.5) & (bcr < 1.5)]
    bins = pd.cut(near, np.arange(0.5, 1.55, 0.05)).value_counts().sort_index()
    bins.to_csv(DIAG / "qe_bcr_density_near1.csv")
    below = (bcr < 1).sum()
    fb = wind.groupby(wind.bcr >= 1).funded.mean()
    sel = s[s.primaryActivity.fillna("").str.contains("Saferoom|shelter", case=False)]
    selcols = sel.selectionStatus.value_counts(dropna=False)
    prog = sel.program.value_counts()
    # counties that applied for strict projects but were never funded
    ap = wind[wind.county_fips.notna()]
    ever_f = set(ap[ap.funded].county_fips)
    denied_only = set(ap[ap.not_funded].county_fips) - ever_f
    pd.Series(sorted(denied_only), name="county_fips").to_csv(DIAG / "qe_denied_only_counties.csv", index=False)
    # design check: comparison group = never-funded applicant counties only
    res = []
    for var, freq in [("separation_rate", "q"), ("log_employment", "q"), ("log_earnings", "q"),
                      ("establishment_death_rate", "y"), ("job_destruction_rate", "y")]:
        keep = list(ever_f | denied_only)
        r = est.run(est.Spec(outcome=var, freq=freq, sample={"keep_counties": keep}, label="applicant_controls"))
        res.append({"outcome": var, "beta": r.get("beta"), "se": r.get("se"), "p": r.get("p"), "N": r.get("N"),
                    "control_counties": len(denied_only), "status": r.get("status")})
    rd = pd.DataFrame(res)
    rd.to_csv(DIAG / "qe_applicant_control_estimates.csv", index=False)

    md = f"""# Quasi-Experiment Assessment (Section 42)

Data: OpenFEMA HazardMitigationAssistanceProjects v4 (status, BCR) and HmaSubapplications v2 (selection fields).
Strict tornado/wind project records (all statuses): {len(wind):,}; funded: {int(funded):,}; not funded
(denied / withdrawn / not selected / void): {int(notf):,}.

## Status distribution (strict projects)

{st.to_frame('n').to_markdown()}

## Candidate designs

| Institutional rule | Running variable | Cutoff | Sample size | Manipulation risk | Balance test feasible | RD credible? | IV credible? | Recommended use |
|---|---|---|---|---|---|---|---|---|
| Benefit-cost requirement (BCR >= 1.0 for HMA cost-effectiveness) | Reported BCR | 1.0 | {len(bcr):,} strict records with BCR > 0; {int(below):,} below 1 | HIGH: BCR is computed by applicants/states with FEMA BCA Toolkit and pre-calculated benefits (e.g., safe-room pre-calculated benefits), so projects are engineered to clear 1.0; non-cost-effective projects are typically not submitted or are revised | Partly (county covariates) | **No** - few observations just below 1 and funding share does not jump discretely (funded share BCR<1: {fb.get(False, np.nan):.2f}; BCR>=1: {fb.get(True, np.nan):.2f}); BCR = 0 / missing for most HMGP records | No | Descriptive only |
| BRIC / FMA national competition scores | Technical + qualitative score | Annual funding line | Safe-room subapplications by program: {prog.to_dict()} ; selection status values: {selcols.head(8).to_dict()} | Moderate | Not possible | **No** - scores and the funding line are not published in OpenFEMA; BRIC began FY2020 and is tiny for safe rooms | No | Future FOIA request |
| HMGP formula: 15% (20% enhanced-plan states) of post-disaster federal assistance | State HMGP ceiling by disaster | none (continuous) | All HMGP disasters | Low (formula) | Yes | No | **Possibly**: HMGP ceiling scales with disaster aid in the STATE, which is plausibly exogenous to a given county's later tornado exposure, but it also reflects the state's own disaster history; exclusion restriction weak | Shift-share style instrument for a redesign; requires state-disaster ceilings (HazardMitigationGrantProgramDisasterSummaries) |
| Cost-share changes (e.g., 90% federal share in some declarations; 2018 DRRA) | Declaration date | rule dates | Few rule changes | Low | Yes | No | Weak first stage expected | Event-study robustness only |
| Rejected vs accepted subapplications | Status | n/a | Never-funded applicant counties: {len(denied_only):,} | Selection on unobserved project quality / admin capacity | Yes | No | No | **Alternative control group** (applicant counties that never received a strict project) |

## Design check: comparison group = applicant counties never funded (exploratory)

{rd.round(5).to_markdown(index=False)}

## Assessment

- No sharp funding cutoff with a published, non-manipulable running variable exists in public data; an RD on
  the BCR = 1 threshold is **not credible** (manipulation by construction, little mass below 1, BCR missing/zero
  for most HMGP records).
- An IV based on state HMGP ceilings (post-declaration formula) is the most promising quasi-experimental
  redesign, but the exclusion restriction (state disaster history affects later outcomes) needs defending.
- The never-funded-applicant comparison group is feasible but small ({len(denied_only):,} counties) and selected on
  application capacity; it is a useful robustness check, not a quasi-experiment.
- **A FEMA funding cutoff would materially improve identification only if FEMA released BRIC/PDM national
  scores and funding lines (FOIA).** With public data, the design remains a selection-on-observables /
  difference-in-differences design whose credibility rests on the pre-trend and placebo evidence.
"""
    (FINAL / "quasi_experiment_assessment.md").write_text(md, encoding="utf-8")
    log.info("QE assessment written; denied-only counties %d; BCR records %d", len(denied_only), len(bcr))


if __name__ == "__main__":
    main()
