"""Section 22/63 outcome feasibility: quantitative score 0-100 for every outcome group (1-15).

Outputs: output/tables/outcome_feasibility.csv, output/tables/table3_outcome_feasibility.md
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

import est
from utils import DIAG, INTER, PROC, TABLES, get_logger

log = get_logger(__file__)
FEMA_YEARS = (1990, 2025)


def stats_for(var: str, freq: str, align: str = "mar", panel_override: pd.DataFrame | None = None) -> dict:
    s = est.Spec(outcome=var, freq=freq, align=align if isinstance(align, str) and align else "mar")
    full = est.panel(freq)
    d, _ = est.build(s)
    if len(d) == 0:
        return {}
    tcol = est.time_col(freq)
    yrs = d["year"]
    tr = d[d.ever == 1]
    post_t = d[(d.M == 1) & (d["T"] > 0)]
    per = 4 if freq == "q" else 1
    cover = full[full.year.between(yrs.min(), yrs.max())]
    miss = 1 - len(d) / len(cover)
    return {"first_year": int(yrs.min()), "last_year": int(yrs.max()),
            "years_overlap_with_FEMA": int(min(yrs.max(), FEMA_YEARS[1]) - max(yrs.min(), FEMA_YEARS[0]) + 1),
            "number_observations": len(d), "number_counties": d.county_fips.nunique(),
            "treated_counties": tr.county_fips.nunique(),
            "treated_counties_with_post_treatment_tornado": post_t.county_fips.nunique(),
            "post_treatment_tornado_events": int(post_t["T"].sum()),
            "untreated_tornado_controls": d[(d.ever == 0) & (d["T"] > 0)].county_fips.nunique(),
            "mean_pre_periods": tr[tr.M == 0].groupby("county_fips").size().mean() / per,
            "mean_post_periods": tr[tr.M == 1].groupby("county_fips").size().mean() / per,
            "missing_share": max(miss, 0.0), "time_unit": tcol}


def score(r: dict) -> float:
    if not r.get("public_data_available"):
        return 0.0
    s = 10
    s += {"county": 7, "county-industry": 10, "county-demographic": 10, "state": 2}.get(r["geographic_resolution"], 4)
    s += {"quarterly": 9, "annual": 6, "monthly": 10, "irregular": 2}.get(r["temporal_frequency"], 2)
    s += 10 * min(1, r.get("years_overlap_with_FEMA", 0) / 25)
    s += 15 * min(1, r.get("treated_counties", 0) / 300)
    s += 15 * min(1, r.get("post_treatment_tornado_events", 0) / 300)
    s += 10 * min(1, r.get("untreated_tornado_controls", 0) / 500)
    s += 10 * (1 - min(1, r.get("missing_share", 1) + r.get("suppression_share", 0)))
    s += r.get("timing_points", 0)
    return round(s, 1)


def rating(x):
    return "EXCELLENT" if x >= 80 else "GOOD" if x >= 65 else "MODERATE" if x >= 50 else "LOW"


def main() -> None:
    reg = est.registry()
    qsupp = pd.read_csv(DIAG / "qwi_county_total_missing.csv", index_col=0).iloc[:, 0].to_dict() \
        if (DIAG / "qwi_county_total_missing.csv").exists() else {}
    bsupp = pd.read_csv(DIAG / "bds_st_cty_suppression.csv", index_col=0).iloc[:, 0].to_dict()
    supp_map = {"separation_rate": qsupp.get("Sep", 0), "log_employment": qsupp.get("EmpEnd", 0),
                "log_earnings": qsupp.get("EarnS", 0), "log_new_hire_earnings": qsupp.get("EarnHirNS", 0),
                "hire_rate": qsupp.get("HirA", 0), "job_destruction_rate_qwi": qsupp.get("FrmJbLs", 0),
                "establishment_death_rate": bsupp.get("estabs_exit", 0), "job_destruction_rate": bsupp.get("job_destruction", 0),
                "establishment_birth_rate": bsupp.get("estabs_entry", 0)}
    groups = {
        1: ("Worker separations and job retention", "O1a"), 2: ("Establishment survival and deaths", "O2a"),
        3: ("Job creation and job destruction", "O3a"), 4: ("Employment recovery speed", "O4a"),
        5: ("Worker earnings", "O5a"), 6: ("Distributional labor effects", None),
        7: ("Hiring and new-hire earnings", "O7a"), 8: ("Small-business resilience", "O8a"),
        9: ("Industry reallocation", None), 10: ("Business formation / entrepreneurship", "O10a"),
        11: ("Migration", "O11a"), 12: ("Housing/rebuilding", "O12a"), 13: ("Local fiscal resilience", None),
        14: ("Establishment count and payroll", "O14a"), 15: ("Warning-induced shutdown costs", None)}
    rows = []
    for g, (name, oid) in groups.items():
        r = {"group": g, "outcome": name}
        if oid:
            row = reg.set_index("outcome_id").loc[oid]
            st = stats_for(row.variable, row.freq, row.align if isinstance(row.align, str) else "mar")
            r.update(st)
            r.update({"dataset": row.dataset, "variable": row.variable, "public_data_available": True,
                      "geographic_resolution": "county",
                      "temporal_frequency": "quarterly" if row.freq == "q" else "annual",
                      "suppression_share": supp_map.get(row.variable, 0.0),
                      "timing_points": 6 if row.freq == "q" else 7})
        elif g == 6:
            dm = pd.read_parquet(PROC / "county_demographic_quarter_panel.parquet")
            fam = dm.demo_family.unique().tolist()
            base = stats_for("separation_rate", "q")
            r.update(base)
            r.update({"dataset": "QWI (sa bulk; se/rh/firmsize API)", "variable": f"cells: {fam}",
                      "public_data_available": True, "geographic_resolution": "county-demographic",
                      "temporal_frequency": "quarterly", "timing_points": 6,
                      "suppression_share": float(dm["Sep"].isna().mean()),
                      "number_observations": len(dm)})
        elif g == 9:
            ind = pd.read_parquet(PROC / "county_industry_quarter_panel.parquet")
            base = stats_for("separation_rate", "q")
            r.update(base)
            r.update({"dataset": "QWI industry groups (+QCEW 2014+, CBP)", "variable": "industry cells",
                      "public_data_available": True, "geographic_resolution": "county-industry",
                      "temporal_frequency": "quarterly", "timing_points": 6,
                      "suppression_share": float(ind["EmpEnd"].isna().mean()), "number_observations": len(ind)})
        elif g == 13:
            stt = json.loads((INTER / "public_finance_status.json").read_text())
            r.update({"dataset": "Census Annual Survey of Local Govt Finances", "variable": "property tax etc.",
                      "public_data_available": True, "geographic_resolution": "county (sample-based)",
                      "temporal_frequency": "irregular", "timing_points": 2, "years_overlap_with_FEMA": 6,
                      "treated_counties": 0, "post_treatment_tornado_events": 0, "untreated_tornado_controls": 0,
                      "missing_share": 0.8, "note": stt["reason"]})
        elif g == 15:
            r.update({"dataset": "none nationally scalable (see warning_system_feasibility.md)",
                      "variable": "high-frequency activity", "public_data_available": False,
                      "geographic_resolution": "none", "temporal_frequency": "irregular",
                      "note": "No public, national, county x day/hour economic-activity panel spanning the FEMA era"})
        r["treatment_timing_quality"] = "proxy: obligation+2y (no completion date)"
        r["geographic_matching_quality"] = "primary-county FIPS (8% statewide projects excluded)"
        r["feasibility_score"] = score(r)
        r["feasibility_rating"] = rating(r["feasibility_score"])
        if g == 15:
            r["feasibility_rating"] = "INFEASIBLE"
        r["low_power_risk"] = (r.get("treated_counties", 0) < 30) or (r.get("post_treatment_tornado_events", 0) < 30)
        rows.append(r)
    df = pd.DataFrame(rows)
    df.to_csv(TABLES / "outcome_feasibility.csv", index=False)
    show = df.assign(**{"Public?": df.public_data_available.map({True: "Yes", False: "No"}),
                        "Missingness": df.missing_share.map(lambda x: f"{x:.2f}" if pd.notna(x) else ""),
                        "Suppression": df.suppression_share.map(lambda x: f"{x:.2f}" if pd.notna(x) else "")})
    cols = {"outcome": "Outcome", "dataset": "Dataset", "Public?": "Public?", "geographic_resolution": "Geography",
            "temporal_frequency": "Frequency", "years_overlap_with_FEMA": "Years overlap",
            "treated_counties": "Treated counties", "post_treatment_tornado_events": "Post-treatment tornado events",
            "Missingness": "Missingness", "Suppression": "Suppression", "feasibility_score": "Feasibility score",
            "feasibility_rating": "Feasibility"}
    md = show[list(cols)].rename(columns=cols).to_markdown(index=False)
    (TABLES / "table3_outcome_feasibility.md").write_text("# Table 3. Outcome feasibility\n\n" + md, encoding="utf-8")
    log.info("\n%s", md)
    _ = np


if __name__ == "__main__":
    main()
