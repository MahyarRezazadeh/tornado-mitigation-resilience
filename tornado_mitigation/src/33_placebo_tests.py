"""Placebo tests (Section 43; robustness R36-R40).

R36 future placebo: fake treatment 3 years before actual, pre-treatment periods only.
R37 historical placebo: fake treatment 6 years before actual, pre-treatment periods only.
R38 pre-treatment interaction: EverTreated x Tornado using only pre-treatment periods (placebo_pass test).
R39 randomized treatment years: treatment dates permuted among treated counties (20 draws).
R40 randomization inference: treatment status permuted within state x historical-risk tercile (100 draws).
Mechanical placebo outcome: log beginning-of-quarter employment (QWI Emp) cannot respond to a same-quarter tornado.
Outputs: output/models/placebo_results.csv, output/models/permutation_draws.csv
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

import est
from utils import MODELS, get_logger

log = get_logger(__file__)
PRIMARY = [("separation_rate", "q", "mar"), ("log_employment", "q", "mar"), ("log_earnings", "q", "mar"),
           ("establishment_death_rate", "y", "mar"), ("job_destruction_rate", "y", "mar")]
SECONDARY = [("hire_rate", "q", "mar"), ("job_destruction_rate_qwi", "q", "mar"), ("small_estab_death_rate", "y", "mar"),
             ("log_establishments", "y", "mar"), ("outmigration_rate", "y", "mar"), ("ihs_units", "y", "cal"),
             ("log_qcew_emp", "q", "mar")]
N_RI, N_DATES = 100, 20


def merge_save(rows, draws, outcomes):
    """Append/replace results for the outcomes just run (allows running one outcome per call)."""
    p = MODELS / "placebo_results.csv"
    new = pd.DataFrame(rows)
    if p.exists() and len(new):
        old = pd.read_csv(p)
        new = pd.concat([old[~old.outcome.isin(outcomes)], new], ignore_index=True)
    new.to_csv(p, index=False)
    if draws:
        pdraw = MODELS / "permutation_draws.csv"
        nd = pd.concat(draws)
        if pdraw.exists():
            od = pd.read_csv(pdraw)
            nd = pd.concat([od[~od.outcome.isin(outcomes)], nd], ignore_index=True)
        nd.to_csv(pdraw, index=False)


def main() -> None:
    import sys
    only = set(sys.argv[1:])
    rows, draws = [], []
    todo = [x for x in PRIMARY + SECONDARY if not only or x[0] in only]
    for var, freq, align in todo:
        est._CACHE.clear(); __import__('gc').collect()
        base = est.Spec(outcome=var, freq=freq, align=align)
        prim = est.run(base)
        for rid, pl in [("R36", "future"), ("R37", "historical"), ("R38", "pre_interaction")]:
            r = est.run(base.but(placebo=pl, label=rid))
            r.update({"specification_id": rid, "primary_beta": prim.get("beta")})
            rows.append(r)
        is_primary = (var, freq, align) in PRIMARY
        nd = N_DATES if is_primary else 5
        rd = Parallel(n_jobs=2, backend="threading")(
            delayed(est.run)(base.but(shuffle=i, shuffle_kind="dates", label="R39")) for i in range(nd))
        rd = pd.DataFrame(rd)
        ok = rd[rd.status == "ok"]
        rows.append({"outcome": var, "specification_id": "R39", "label": "R39", "status": "ok",
                     "beta": ok.beta.mean(), "se": ok.beta.std(), "p": np.nan,
                     "share_p05": (ok.p < 0.05).mean(), "n_draws": len(ok), "primary_beta": prim.get("beta")})
        if is_primary:
            ri = Parallel(n_jobs=2, backend="threading")(
                delayed(est.run)(base.but(shuffle=1000 + i, shuffle_kind="status", label="R40")) for i in range(N_RI))
            ri = pd.DataFrame(ri)
            ok = ri[ri.status == "ok"]
            p_ri = (np.abs(ok.beta) >= abs(prim["beta"])).mean() if prim.get("status") == "ok" else np.nan
            rows.append({"outcome": var, "specification_id": "R40", "label": "R40", "status": "ok",
                         "beta": ok.beta.mean(), "se": ok.beta.std(), "p": p_ri, "n_draws": len(ok),
                         "primary_beta": prim.get("beta")})
            draws.append(ok.assign(outcome=var)[["outcome", "beta", "se", "p"]])
        log.info("%s placebos done (primary b=%.4g)", var, prim.get("beta", np.nan))
    if not only or "log_beg_emp" in only:
        q = est.panel("q")
        q["log_beg_emp"] = np.log(q["Emp"].where(q["Emp"] > 0))
        r = est.run(est.Spec(outcome="log_beg_emp", freq="q", label="mechanical_placebo"))
        r.update({"specification_id": "PL_beg_emp", "description": "log beginning-of-quarter employment"})
        rows.append(r)
    merge_save(rows, draws, [v for v, _, _ in todo] + (["log_beg_emp"] if (not only or "log_beg_emp" in only) else []))


if __name__ == "__main__":
    main()
