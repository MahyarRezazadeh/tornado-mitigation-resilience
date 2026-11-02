"""Robustness specifications R01-R69 for every major outcome + specification-curve datasets.

Placebo/permutation specs (R36-R40) are in 33_placebo_tests.py, leave-one-out (R41-R42) in
34_leave_one_out.py, multiple-testing (R70) in 36_multiple_testing.py; their results are merged
into the robustness metrics there. Rows that duplicate the primary specification are kept for
transparency but flagged credible_specification = 0 so they do not inflate sign consistency.
Outputs: output/models/robustness_<outcome>.csv, output/models/spec_curve_all.csv
"""
from __future__ import annotations

import sys

import pandas as pd
from joblib import Parallel, delayed

import est
from utils import MODELS, get_logger

log = get_logger(__file__)
MAJOR = [("separation_rate", "q", "mar"), ("log_employment", "q", "mar"), ("log_earnings", "q", "mar"),
         ("establishment_death_rate", "y", "mar"), ("job_destruction_rate", "y", "mar"),
         ("hire_rate", "q", "mar"), ("job_destruction_rate_qwi", "q", "mar"), ("small_estab_death_rate", "y", "mar"),
         ("log_establishments", "y", "mar"), ("outmigration_rate", "y", "mar"), ("ihs_units", "y", "cal"),
         ("log_qcew_emp", "q", "mar")]


def specs(base: est.Spec) -> list[tuple[str, str, est.Spec, int, str]]:
    """(id, description, spec, credible, category)."""
    q = base.freq == "q"
    L = []
    a = L.append
    a(("R00", "PRIMARY", base, 1, "primary"))
    a(("R01", "strict treatment (= primary)", base, 0, "treatment_def"))
    a(("R02", "moderate treatment", base.but(definition="moderate"), 1, "treatment_def"))
    a(("R03", "broad treatment", base.but(definition="broad"), 1, "treatment_def"))
    a(("R04", "completion proxy: closeout date", base.but(timing="closeout"), 1, "timing"))
    a(("R04b", "completion proxy: last federal payment", base.but(timing="last_payment"), 1, "timing"))
    a(("R05", "obligation date (lag 0)", base.but(timing="obligation_L0"), 1, "timing"))
    a(("R06", "approval date (lag 0)", base.but(timing="approval_L0"), 1, "timing"))
    a(("R07", "obligation + 0y (= R05)", base.but(timing="obligation_L0"), 0, "timing"))
    a(("R08", "obligation + 1y", base.but(timing="obligation_L1"), 1, "timing"))
    a(("R09", "obligation + 2y", base.but(timing="obligation_L2"), 1, "timing"))
    a(("R10", "obligation + 3y", base.but(timing="obligation_L3"), 1, "timing"))
    a(("R10b", "approval + 1y", base.but(timing="approval_L1"), 1, "timing"))
    a(("R10c", "approval + 2y", base.but(timing="approval_L2"), 1, "timing"))
    a(("R10d", "approval + 3y", base.but(timing="approval_L3"), 1, "timing"))
    a(("R11", "any tornado", base.but(tornado="any_tornado"), 1, "hazard"))
    a(("R12", "EF1+ (= primary)", base, 0, "hazard"))
    a(("R13", "EF2+", base.but(tornado="EF2_plus"), 1, "hazard"))
    a(("R14", "EF3+", base.but(tornado="EF3_plus"), 1, "hazard"))
    a(("R15", "continuous tornado count", base.but(tornado="count"), 1, "hazard"))
    a(("R16", "continuous max intensity (0=none,1=EF0..6=EF5)", base.but(tornado="maxint"), 1, "hazard"))
    if q:
        a(("R16b", "path-based EF1+ exposure", base.but(tornado="path_EF1_plus"), 1, "hazard"))
    a(("R17", "drop treatment year", base.but(sample={"drop_treat_window": 0}), 1, "sample"))
    a(("R18", "drop treatment year + first post year", base.but(sample={"drop_treat_window": 1}), 1, "sample"))
    a(("R19", "drop treatment year + first two post years", base.but(sample={"drop_treat_window": 2}), 1, "sample"))
    a(("R20", "exclude counties first treated by post-tornado/severe-storm HMGP award",
       base.but(sample={"exclude_post_tornado_award": True}), 1, "sample"))
    a(("R21", "county FE + time FE", base.but(fe="twfe"), 1, "fixed_effects"))
    a(("R22", "state x time FE (= primary)", base, 0, "fixed_effects"))
    a(("R23", "region x time FE", base.but(fe="region"), 1, "fixed_effects"))
    a(("R24", "county-specific linear trends (estimated on untreated periods)", base.but(detrend=True), 1, "fixed_effects"))
    a(("R25", "population weighted", base.but(weights="pop"), 1, "weighting"))
    a(("R26", "unweighted (= primary)", base, 0, "weighting"))
    a(("R27", "winsorize Y 1/99", base.but(transform="winsor"), 1, "functional_form"))
    a(("R28", "IHS of underlying count", base.but(transform="ihs"), 1, "functional_form"))
    a(("R29", "log of underlying count", base.but(transform="log"), 1, "functional_form"))
    a(("R30", "exclude top-1% population counties", base.but(sample={"exclude_top_metro": True}), 1, "sample"))
    a(("R31", "tornado-prone (above-median historical risk)", base.but(sample={"risk": "above_median_risk"}), 1, "sample"))
    a(("R31b", "top-tercile historical risk", base.but(sample={"risk": "top_tercile_risk"}), 1, "sample"))
    a(("R32", "ever-tornado (1950-89) counties", base.but(sample={"risk": "ever_tornado_hist"}), 1, "sample"))
    a(("R33", "matched sample (1:3 NN propensity)", base.but(weights="w_nn"), 1, "matching"))
    a(("R33b", "Mahalanobis matched (1:3, within region)", base.but(weights="w_maha"), 1, "matching"))
    a(("R34", "entropy balanced", base.but(weights="w_ebal"), 1, "matching"))
    a(("R35", "IPW (ATT odds)", base.but(weights="w_ipw"), 1, "matching"))
    a(("R43", "cluster county (= primary)", base, 0, "clustering"))
    a(("R44", "cluster state", base.but(cluster="state"), 1, "clustering"))
    a(("R45", "two-way cluster county & state-time", base.but(cluster="twoway"), 1, "clustering"))
    a(("R46", "exclude Oklahoma", base.but(sample={"drop_states": ["OK"]}), 1, "sample"))
    a(("R47", "exclude Texas", base.but(sample={"drop_states": ["TX"]}), 1, "sample"))
    a(("R48", "exclude highest-treatment state", base.but(sample={"drop_states": ["__TOP__"]}), 1, "sample"))
    a(("R49", "exclude 2011 Super Outbreak period (2011Q2)", base.but(sample={"drop_yq": [20112]}), 1, "sample"))
    a(("R50", "exclude top-1% property-damage tornado periods", base.but(sample={"drop_top_damage": True}), 1, "sample"))
    a(("R51", "control hurricanes", base.but(controls=["hurricane_events"]), 1, "controls"))
    a(("R52", "control floods", base.but(controls=["flood_events"]), 1, "controls"))
    a(("R53", "control other severe storms", base.but(controls=["severe_storm_events"]), 1, "controls"))
    a(("R54", "drop 2020", base.but(sample={"drop_years": [2020]}), 1, "sample"))
    a(("R55", "drop 2020-2021", base.but(sample={"drop_years": [2020, 2021]}), 1, "sample"))
    a(("R56", "drop 2008-2009", base.but(sample={"drop_years": [2008, 2009]}), 1, "sample"))
    a(("R57", "historical-risk tercile x time FE", base.but(fe="risk"), 1, "controls"))
    a(("R58", "alternative functional form", base.but(transform="altform"), 1, "functional_form"))
    a(("R59", "exclude counties with few untreated periods", base.but(sample={"min_pre": 8 if q else 3}), 1, "sample"))
    a(("R60", "continuously observed counties (balanced)", base.but(sample={"balanced": True}), 1, "sample"))
    a(("R61", "exclude low-confidence classifications (no LOW in strict -> = primary)", base, 0, "treatment_def"))
    a(("R62", "only HIGH-confidence treated counties", base.but(sample={"confidence": "HIGH"}), 1, "treatment_def"))
    a(("R63", "only projects with observed closeout (completion unobserved)", base.but(timing="closeout_observed"), 1, "timing"))
    a(("R64", "only safe-room projects", base.but(timing="saferoom"), 1, "treatment_def"))
    a(("R65", "only structural wind retrofit projects", base.but(timing="retrofit"), 1, "treatment_def"))
    a(("R66", "retrofit counties without safe rooms", base.but(timing="retrofit", sample={"only_types": "retrofit_only"}), 1, "treatment_def"))
    a(("R67", "per-capita federal mitigation intensity ($100 pc) x tornado", base.but(intensity="pc"), 1, "intensity"))
    a(("R68", "cumulative project-count intensity x tornado", base.but(intensity="count"), 1, "intensity"))
    a(("R69", "log(1+cumulative federal $k) x tornado", base.but(intensity="spend"), 1, "intensity"))
    return L


def top_state() -> str:
    d = est.panel("y").drop_duplicates("county_fips")
    return d[d.ft_strict_primary.notna()].STUSPS.value_counts().index[0]


def run_one(rid, desc, sp, cred, cat, top):
    if sp.sample.get("drop_states") == ["__TOP__"]:
        sp = sp.but(sample={"drop_states": [top]})
        desc = f"{desc} ({top})"
    try:
        r = est.run(sp.but(label=rid))
    except Exception as e:  # noqa: BLE001
        r = {"outcome": sp.outcome, "status": f"error: {str(e)[:150]}"}
    r.update({"specification_id": rid, "description": desc, "credible_specification": cred, "category": cat})
    return r


def main(only: list[str] | None = None) -> None:
    top = top_state()
    allrows = []
    for var, freq, align in MAJOR:
        if only and var not in only:
            continue
        est._CACHE.clear(); __import__('gc').collect()
        base = est.Spec(outcome=var, freq=freq, align=align)
        est.panel(freq)
        rows = Parallel(n_jobs=2, backend="threading")(delayed(run_one)(*x, top) for x in specs(base))
        df = pd.DataFrame(rows)
        df.to_csv(MODELS / f"robustness_{var}.csv", index=False)
        allrows.append(df)
        ok = df[df.status == "ok"]
        log.info("%s: %d specs ok, %d failed/infeasible", var, len(ok), len(df) - len(ok))
    allrows = [pd.read_csv(f) for f in sorted(MODELS.glob("robustness_*.csv"))]   # all outcomes run so far
    sc = pd.concat(allrows, ignore_index=True)
    sc = sc.rename(columns={"definition": "treatment_definition", "timing": "treatment_date", "tornado": "tornado_definition",
                            "fe": "fixed_effects", "weights": "weighting", "cluster": "clustering",
                            "beta": "coefficient", "se": "SE", "p": "pvalue", "ci_low": "CI_low", "ci_high": "CI_high"})
    sc["implementation_lag"] = sc["treatment_date"].str.extract(r"L(\d)")[0].fillna("")
    sc.to_csv(MODELS / "spec_curve_all.csv", index=False)


if __name__ == "__main__":
    main(sys.argv[1:] or None)
