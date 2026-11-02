"""Leave-one-state-out (Section 44, R41) and leave-one-major-event-out (Section 45, R42).

Major episodes are chosen by predetermined criteria only: top 10 NOAA episodes (1990-2025, contiguous US)
by total fatalities, top 10 by maximum EF rating (ties broken by fatalities), top 10 by reported property
damage. Excluding an episode drops all county-periods it touched.
Outputs: output/models/loso_results.csv, output/models/loeo_results.csv, output/models/major_episodes.csv
"""
from __future__ import annotations

import pandas as pd
from joblib import Parallel, delayed

import est
from utils import INTER, MODELS, get_logger

log = get_logger(__file__)
OUTS = [("separation_rate", "q", "mar"), ("log_employment", "q", "mar"), ("log_earnings", "q", "mar"),
        ("establishment_death_rate", "y", "mar"), ("job_destruction_rate", "y", "mar"),
        ("hire_rate", "q", "mar"), ("outmigration_rate", "y", "mar"), ("log_establishments", "y", "mar")]
FOCUS = ["OK", "TX", "AL", "MS", "MO", "KS", "AR", "IA", "TN", "FL"]


def episodes() -> tuple[pd.DataFrame, dict]:
    t = pd.read_parquet(INTER / "tornadoes_clean.parquet")
    t = t[t.year >= 1990]
    e = t.groupby("EPISODE_ID").agg(date=("date", "min"), fatalities=("fatalities", "sum"), max_ef=("ef", "max"),
                                    damage=("damage_property", "sum"), n_counties=("county_fips", "nunique"),
                                    states=("STATE", lambda s: ",".join(sorted(set(s))[:4])))
    top = pd.concat([e.nlargest(10, "fatalities").assign(criterion="fatalities"),
                     e.sort_values(["max_ef", "fatalities"], ascending=False).head(10).assign(criterion="max_EF"),
                     e.nlargest(10, "damage").assign(criterion="damage")])
    top = top.reset_index().drop_duplicates("EPISODE_ID")
    top.to_csv(MODELS / "major_episodes.csv", index=False)
    t["mar_year"] = t.year + (t.quarter > 1).astype(int)
    keys = {}
    for ep in top.EPISODE_ID:
        s = t[t.EPISODE_ID == ep]
        keys[ep] = {"q": list(s.county_fips + "_" + s.yq.astype(str)),
                    "y_mar": list(s.county_fips + "_" + s.mar_year.astype(str)),
                    "y_cal": list(s.county_fips + "_" + s.year.astype(str))}
    return top, keys


def main() -> None:
    top, keys = episodes()
    states = sorted(est.panel("y").STUSPS.unique())
    import sys
    only = set(sys.argv[1:])
    lo, le = [], []
    for var, freq, align in [x for x in OUTS if not only or x[0] in only]:
        est._CACHE.clear(); __import__('gc').collect()
        base = est.Spec(outcome=var, freq=freq, align=align)
        prim = est.run(base)
        res = Parallel(n_jobs=2, backend="threading")(
            delayed(est.run)(base.but(sample={"drop_states": [s]}, label=f"LOSO_{s}")) for s in states)
        for s, r in zip(states, res):
            lo.append({"outcome": var, "state_removed": s, "beta": r.get("beta"), "SE": r.get("se"),
                       "pvalue": r.get("p"), "primary_beta": prim.get("beta"), "focus_state": s in FOCUS})
        kk = "q" if freq == "q" else ("y_mar" if align == "mar" else "y_cal")
        res = Parallel(n_jobs=2, backend="threading")(
            delayed(est.run)(base.but(sample={"drop_county_periods": keys[ep][kk]}, label=f"LOEO_{ep}"))
            for ep in top.EPISODE_ID)
        for (_, ep), r in zip(top.iterrows(), res):
            le.append({"outcome": var, "episode_removed": ep.EPISODE_ID, "date": ep.date, "criterion": ep.criterion,
                       "states": ep.states, "fatalities": ep.fatalities, "beta": r.get("beta"), "SE": r.get("se"),
                       "pvalue": r.get("p"), "primary_beta": prim.get("beta")})
        log.info("%s LOSO/LOEO done", var)
    for rows, fn in [(lo, "loso_results.csv"), (le, "loeo_results.csv")]:
        new = pd.DataFrame(rows)
        p = MODELS / fn
        if p.exists() and len(new):
            old = pd.read_csv(p)
            new = pd.concat([old[~old.outcome.isin(new.outcome.unique())], new], ignore_index=True)
        new.to_csv(p, index=False)


if __name__ == "__main__":
    main()
