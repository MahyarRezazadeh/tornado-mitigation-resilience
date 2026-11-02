"""Construct project- and county-level treatment timing for each definition.

OpenFEMA publishes no physical completion date, so 'completion' is unobserved for 100% of
projects. Per the pre-specified rule (completion if observed, else obligation + 2 years)
the primary timing is obligation + 2y (fallback: initial approval + 2y). Closeout and last
federal payment are reported as alternative completion proxies, never as the only timing.

Outputs:
  data/intermediate/fema_treatment_projects.parquet  (funded, classified, county-identified)
  data/processed/county_treatment.parquet           (county x definition x timing: first date, intensity)
  output/diagnostics/fema_timing_quality.csv
"""
from __future__ import annotations

import pandas as pd

from utils import DIAG, INTER, PROC, get_logger

log = get_logger(__file__)
DEFS = ["strict", "moderate", "broad"]


def add_timings(p: pd.DataFrame) -> pd.DataFrame:
    yr = pd.DateOffset(years=1)
    for L in range(4):
        p[f"t_obligation_L{L}"] = p["obligation_date"] + L * yr
        p[f"t_approval_L{L}"] = p["approval_date"] + L * yr
    p["t_closeout"] = p["closeout_date"]
    p["t_last_payment"] = p["last_payment_date"]
    p["t_completion"] = p["completion_date"]
    # primary: completion -> obligation+2 -> approval+2
    # DATA-LIMITATION MODIFICATION (logged): closeout used as last fallback so projects lacking
    # obligation/approval dates do not silently enter the control group.
    p["t_primary"] = (p["t_completion"].fillna(p["t_obligation_L2"]).fillna(p["t_approval_L2"])
                      .fillna(p["t_closeout"]))
    p["t_primary_source"] = (p["t_completion"].notna().map({True: "completion", False: None})
                             .fillna(p["t_obligation_L2"].notna().map({True: "obligation+2", False: None}))
                             .fillna(p["t_approval_L2"].notna().map({True: "approval+2", False: None}))
                             .fillna(p["t_closeout"].notna().map({True: "closeout_fallback", False: "missing"})))
    return p


def main() -> None:
    p = pd.read_parquet(INTER / "fema_projects_classified.parquet")
    p = p[(p["treat_broad"] == 1) & p["funded"]].copy()
    p = add_timings(p)

    # timing quality diagnostics on otherwise usable (funded, county-identified) projects
    q = []
    for d in DEFS:
        t = p[(p[f"treat_{d}"] == 1) & p["county_fips"].notna()]
        q.append({"definition": d, "projects": len(t),
                  "share_completion": t["t_completion"].notna().mean(),
                  "share_closeout": t["t_closeout"].notna().mean(),
                  "share_last_payment": t["t_last_payment"].notna().mean(),
                  "share_obligation": t["obligation_date"].notna().mean(),
                  "share_approval": t["approval_date"].notna().mean(),
                  "share_primary_nonmissing": t["t_primary"].notna().mean(),
                  "median_oblig_to_close_yrs": ((t["closeout_date"] - t["obligation_date"]).dt.days / 365.25).median(),
                  "median_approval_to_close_yrs": ((t["closeout_date"] - t["approval_date"]).dt.days / 365.25).median(),
                  "median_primary_year": t["t_primary"].dt.year.median()})
    q = pd.DataFrame(q)
    q.to_csv(DIAG / "fema_timing_quality.csv", index=False)
    log.info("timing quality:\n%s", q.round(3).to_string())
    log.info("primary timing source (strict): %s",
             p.loc[p.treat_strict == 1, "t_primary_source"].value_counts().to_dict())

    p.to_parquet(INTER / "fema_treatment_projects.parquet", index=False)

    timings = ["t_primary", "t_closeout", "t_last_payment"] + \
              [f"t_obligation_L{L}" for L in range(4)] + [f"t_approval_L{L}" for L in range(4)]
    rows = []
    pc = p[p["county_fips"].notna()]
    for d in DEFS:
        t = pc[pc[f"treat_{d}"] == 1]
        for tm in timings:
            g = t.dropna(subset=[tm]).groupby("county_fips").agg(
                first_treat_date=(tm, "min"), n_projects=("projectIdentifier", "nunique"),
                total_cost=("total_cost", "sum"), federal_share=("federal_share", "sum"),
                n_safe_room=("mitigation_type", lambda s: (s == "safe_room").sum()),
                n_wind_retrofit=("mitigation_type", lambda s: (s == "wind_retrofit").sum()),
                min_confidence=("classification_confidence",
                                lambda s: "LOW" if (s == "LOW").any() else ("MEDIUM" if (s == "MEDIUM").any() else "HIGH")),
                state_fips=("state_fips", "first")).reset_index()
            g["definition"], g["timing"] = d, tm
            rows.append(g)
    ct = pd.concat(rows, ignore_index=True)
    ct.to_parquet(PROC / "county_treatment.parquet", index=False)
    s = ct[ct.timing == "t_primary"].groupby("definition").agg(
        counties=("county_fips", "nunique"), states=("state_fips", "nunique"),
        median_year=("first_treat_date", lambda x: x.dt.year.median()))
    log.info("treated counties (primary timing):\n%s", s.to_string())


if __name__ == "__main__":
    main()
