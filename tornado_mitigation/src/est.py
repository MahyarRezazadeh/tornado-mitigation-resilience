"""Estimation core: panel loading, treatment/exposure construction, the primary interaction model,
and the specification builder used for robustness (R01-R70), placebos and leave-one-out.

Primary model:  Y = b*M*T + g1*M + g2*T | county + state x time,  cluster county.
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass, field, replace

import numpy as np
import pandas as pd
import pyfixest as pf

from utils import CONFIG, INTER, PROC, SEED

warnings.filterwarnings("ignore")

_CACHE: dict = {}


def registry() -> pd.DataFrame:
    return pd.read_csv(CONFIG / "outcome_registry.csv")


def panel(freq: str) -> pd.DataFrame:
    if freq not in _CACHE:
        name = {"q": "county_quarter_panel", "y": "county_year_panel"}[freq]
        d = pd.read_parquet(PROC / f"{name}.parquet")
        tw = pd.read_parquet(PROC / "county_treatment_wide.parquet")
        ft = [c for c in tw.columns if c.startswith("ft_") and c not in d.columns]
        d = d.merge(tw[["county_fips"] + ft], how="left", on="county_fips")
        d = d.merge(type_specific_dates(), how="left", on="county_fips")
        d = d.merge(post_disaster_flags(), how="left", on="county_fips")
        d["post_tornado_award"] = d["post_tornado_award"].fillna(0)
        mw = PROC / "matching_weights.parquet"
        if mw.exists():
            d = d.merge(pd.read_parquet(mw), how="left", on="county_fips")
        # memory: strings -> category, float64 -> float32 for non-key numeric columns
        for c in d.columns:
            if d[c].dtype == object and c not in ("county_fips",):
                d[c] = d[c].astype("category")
            elif d[c].dtype == "float64" and not c.startswith("ft_"):
                d[c] = d[c].astype("float32")
        _CACHE[freq] = d
    return _CACHE[freq]


def type_specific_dates() -> pd.DataFrame:
    """First primary-timing date by project subtype (safe room / wind retrofit) for R64-R66."""
    p = pd.read_parquet(INTER / "fema_treatment_projects.parquet")
    p = p[(p.treat_strict == 1) & p.county_fips.notna() & p.t_primary.notna()]
    p["yq"] = p.t_primary.dt.year * 10 + p.t_primary.dt.quarter
    out = p.pivot_table(index="county_fips", columns="mitigation_type", values="yq", aggfunc="min")
    out = out.rename(columns={"safe_room": "ft_saferoom", "wind_retrofit": "ft_retrofit"})
    keep = [c for c in ["ft_saferoom", "ft_retrofit"] if c in out]
    out = out[keep].reset_index()
    cl = p[p.closeout_date.notna()].copy()
    cl["cyq"] = cl.closeout_date.dt.year * 10 + cl.closeout_date.dt.quarter
    out = out.merge(cl.groupby("county_fips").cyq.min().rename("ft_closeout_observed").reset_index(), how="left")
    return out


def post_disaster_flags() -> pd.DataFrame:
    """Counties whose FIRST strict project was an HMGP award following a tornado/severe-storm declaration."""
    p = pd.read_parquet(INTER / "fema_treatment_projects.parquet")
    p = p[(p.treat_strict == 1) & p.county_fips.notna() & p.t_primary.notna()].sort_values("t_primary")
    f = p.groupby("county_fips").first()
    flag = (f.programArea == "HMGP") & f.dis_incidentType.fillna("").str.contains("Tornado|Severe Storm")
    return flag.astype(int).rename("post_tornado_award").reset_index()


@dataclass
class Spec:
    outcome: str
    freq: str                      # 'q' or 'y'
    definition: str = "strict"
    timing: str = "primary"        # primary, closeout, last_payment, obligation_L0..3, approval_L0..3, saferoom...
    tornado: str = "EF1_plus"
    align: str = "mar"             # annual: 'mar' (March-aligned) or 'cal'
    fe: str = "state"              # state, twfe, region, risk
    cluster: str = "county"        # county, state, twoway
    weights: str | None = None     # None or 'pop'
    transform: str | None = None   # None, winsor, ihs, log
    sample: dict = field(default_factory=dict)
    controls: list = field(default_factory=list)
    detrend: bool = False
    intensity: str | None = None   # None, pc, count, spend
    placebo: str | None = None     # None, future, historical, pre_interaction
    shuffle: int | None = None     # seed for random treatment dates / permutation
    shuffle_kind: str = "dates"
    label: str = "primary"

    def but(self, **kw) -> "Spec":
        return replace(self, **kw)


def time_col(freq):
    return "yq" if freq == "q" else "year"


def ft_col(s: Spec) -> str:
    if s.timing in ("saferoom", "retrofit", "closeout_observed"):
        return f"ft_{s.timing}"
    return f"ft_{s.definition}_{s.timing}"


BASE_COLS = ["county_fips", "state_fips", "STUSPS", "year", "yq", "quarter", "t", "state_yq", "state_year",
             "region_yq", "region_year", "risk_tercile", "above_median_risk", "top_tercile_risk", "ever_tornado_hist",
             "baseline_pop", "min_confidence", "post_tornado_award", "ft_saferoom", "ft_retrofit",
             "ft_closeout_observed", "cum_fed_pc_strict", "cum_projects_strict", "cum_fed_share_strict",
             "ft_strict_primary", "max_tornado_intensity", "mar_max_tornado_intensity", "any_tornado",
             "total_fatalities", "total_injuries", "EF1_plus", "mar_EF1_plus"]


def needed_cols(s: Spec, all_cols) -> list[str]:
    pre = "mar_" if (s.freq == "y" and s.align == "mar") else ""
    tv = {"EF1_plus": "EF1_plus", "any_tornado": "any_tornado", "EF2_plus": "EF2_plus", "EF3_plus": "EF3_plus",
          "count": "tornado_count", "maxint": "max_tornado_intensity", "path_EF1_plus": "path_EF1_plus"}[s.tornado]
    want = set(BASE_COLS) | {s.outcome, pre + tv, tv, ft_col(s), TRANSFORM_BASE.get(s.outcome, ""),
                             ALT_FORM.get(s.outcome, ""), "reported_property_damage", "mar_reported_property_damage",
                             s.weights or ""} | set(s.controls)
    want |= {"w_nn", "w_maha", "w_ebal", "w_ipw"} if s.weights else set()
    return [c for c in all_cols if c in want]


def build(s: Spec) -> tuple[pd.DataFrame, str]:
    P = panel(s.freq)
    d = P[needed_cols(s, P.columns)].copy()
    for c in d.columns:
        if isinstance(d[c].dtype, pd.CategoricalDtype):
            d[c] = d[c].astype(str)
    y = s.outcome
    tcol = time_col(s.freq)
    ft = d[ft_col(s)].astype("float")
    # optional treatment-date shuffles (placebo R39 / permutation R40)
    if s.shuffle is not None:
        rng = np.random.default_rng(SEED + s.shuffle)
        cf = d[["county_fips", "state_fips", "risk_tercile"]].drop_duplicates("county_fips").copy()
        cf["ft"] = d.groupby("county_fips")[ft_col(s)].first().reindex(cf.county_fips).values
        if s.shuffle_kind == "dates":      # permute dates among treated counties
            tr = cf.ft.notna()
            cf.loc[tr, "ft"] = rng.permutation(cf.loc[tr, "ft"].values)
        else:                              # permute treatment status within state x risk tercile
            cf["ft"] = cf.groupby(["state_fips", "risk_tercile"])["ft"].transform(lambda x: rng.permutation(x.values))
        ft = d["county_fips"].map(cf.set_index("county_fips")["ft"]).astype(float)
    if s.sample.get("only_types") == "retrofit_only":
        ft = ft.where(d["ft_saferoom"].isna())
    # current period in yq units; annual March-aligned -> mitigation operational at window start (Q2 of t-1)
    if s.freq == "q":
        now = d["yq"].astype(float)
    elif s.align == "mar":
        now = (d["year"] - 1) * 10 + 2.0
    else:
        now = d["year"] * 10 + 1.0
    d["ever"] = ft.notna().astype(int)
    d["M"] = (ft <= now).astype(int)
    if s.placebo in ("future", "historical"):
        shift = 12 if s.placebo == "future" else 24     # quarters (yq arithmetic below)
        fy, fq = ft // 10, ft % 10
        idx = fy * 4 + fq - 1 - shift
        fake = (idx // 4) * 10 + idx % 4 + 1
        d["M"] = ((fake <= now) & (ft > now)).astype(int)
        d = d[~(d.ever.astype(bool) & (ft <= now))]     # drop actual post-treatment periods
    elif s.placebo == "pre_interaction":
        d["M"] = d["ever"]
        d = d[~(d.ever.astype(bool) & (ft <= now))]
    pre = "mar_" if (s.freq == "y" and s.align == "mar") else ""
    tvar = {"EF1_plus": "EF1_plus", "any_tornado": "any_tornado", "EF2_plus": "EF2_plus", "EF3_plus": "EF3_plus",
            "count": "tornado_count", "maxint": "max_tornado_intensity", "path_EF1_plus": "path_EF1_plus"}[s.tornado]
    T = d[pre + tvar] if pre + tvar in d else d[tvar]
    if s.tornado == "maxint":
        T = (T.fillna(-1) + 1)            # 0 = none, 1 = EF0 ... 6 = EF5
    d["T"] = T.fillna(0).astype(float)
    if s.intensity == "pc":
        d["M"] = d["cum_fed_pc_strict"].fillna(0) / 100.0          # $100 federal mitigation per capita
    elif s.intensity == "count":
        d["M"] = d["cum_projects_strict"].fillna(0)
    elif s.intensity == "spend":
        d["M"] = np.log1p(d["cum_fed_share_strict"].fillna(0) / 1e3)
    d["MT"] = d["M"] * d["T"]

    sm = s.sample
    if "drop_states" in sm:
        d = d[~d.STUSPS.isin(sm["drop_states"])]
    if "drop_years" in sm:
        d = d[~d.year.isin(sm["drop_years"])]
    if "drop_yq" in sm:
        d = d[~d.yq.isin(sm["drop_yq"])] if s.freq == "q" else d[~d.year.isin({q // 10 for q in sm["drop_yq"]})]
    if sm.get("drop_treat_window") is not None:
        k = sm["drop_treat_window"]                    # years around treatment to drop: 0 -> treatment year
        ty = ft // 10
        cur = d["year"]
        d = d[~(d.ever.astype(bool) & (cur - ty).between(0, k))]
    if sm.get("exclude_post_tornado_award"):
        d = d[d.post_tornado_award == 0]
    if sm.get("risk"):
        d = d[d[sm["risk"]] == 1]
    if sm.get("exclude_top_metro"):
        cut = d.drop_duplicates("county_fips").baseline_pop.quantile(0.99)
        d = d[d.baseline_pop < cut]
    if sm.get("confidence") == "HIGH":
        d = d[(d.ever == 0) | (d.min_confidence == "HIGH")]
    if sm.get("drop_top_damage"):
        dv = (pre + "reported_property_damage") if pre + "reported_property_damage" in d else "reported_property_damage"
        cut = d.loc[d[dv] > 0, dv].quantile(0.99)
        d = d[~(d[dv] >= cut)]
    if "drop_county_periods" in sm:
        key = d["county_fips"] + "_" + d[tcol].astype(str)
        d = d[~key.isin(sm["drop_county_periods"])]
    d = d[d[y].notna()]
    if sm.get("min_pre"):
        pre_n = d[(d.ever == 0) | (d.M == 0)].groupby("county_fips").size()
        d = d[d.county_fips.map(pre_n).fillna(0) >= sm["min_pre"]]
    if sm.get("balanced"):   # continuously observed: no internal gaps between first and last observation
        idx = d["t"] if s.freq == "q" else d["year"]
        g = idx.groupby(d.county_fips)
        span = g.max() - g.min() + 1
        n = g.nunique()
        cont = (n == span) & (n >= 0.5 * n.max())
        d = d[d.county_fips.map(cont).fillna(False).astype(bool)]
    if "keep_counties" in sm:
        d = d[d.county_fips.isin(sm["keep_counties"])]

    yv = y
    if s.transform == "winsor":
        lo, hi = d[y].quantile([0.01, 0.99])
        d["y_t"] = d[y].clip(lo, hi)
        yv = "y_t"
    elif s.transform in ("ihs", "log"):
        raw = TRANSFORM_BASE.get(y, y)
        d["y_t"] = np.arcsinh(d[raw]) if s.transform == "ihs" else np.log(d[raw].where(d[raw] > 0))
        d = d[d["y_t"].notna()]
        yv = "y_t"
    elif s.transform == "altform":
        alt = ALT_FORM.get(y)
        if alt is None or alt not in d:
            return d.iloc[0:0], yv
        d = d[d[alt].notna()]
        yv = alt
    if s.detrend:
        d = detrend(d, yv, tcol)
        yv = yv + "_dt"
    return d, yv


TRANSFORM_BASE = {"log_employment": "EmpEnd", "separation_rate": "Sep", "log_earnings": "EarnS",
                  "establishment_death_rate": "estab_deaths", "job_destruction_rate": "job_destruction"}
ALT_FORM = {"log_employment": "employment_growth", "separation_rate": "turnover", "log_earnings": "average_earnings",
            "establishment_death_rate": "log_estab_deaths", "job_destruction_rate": "log_job_destruction"}


def detrend(d: pd.DataFrame, y: str, tcol: str) -> pd.DataFrame:
    """Remove county-specific linear trends estimated on untreated periods (pre-treatment/never-treated)."""
    d = d.copy()
    t = d["year"] + (d["quarter"] - 1) / 4 if tcol == "yq" else d["year"].astype(float)
    d["_t"] = t - 2000
    base = d[d.M == 0]
    g = base.groupby("county_fips")
    mt, my = g["_t"].transform("mean"), g[y].transform("mean")
    cov = ((base["_t"] - mt) * (base[y] - my)).groupby(base.county_fips).sum()
    var = ((base["_t"] - mt) ** 2).groupby(base.county_fips).sum()
    slope = (cov / var.replace(0, np.nan)).fillna(0)
    d[y + "_dt"] = d[y] - d.county_fips.map(slope).fillna(0) * d["_t"]
    return d


def within_sd(d: pd.DataFrame, yv: str, freq: str) -> float:
    """SD of Y net of county and state-time means (alternating projections, 5 passes)."""
    st = "state_yq" if freq == "q" else "state_year"
    r = d[yv].astype(float) - d[yv].mean()
    for _ in range(5):
        r = r - r.groupby(d["county_fips"]).transform("mean")
        r = r - r.groupby(d[st]).transform("mean")
    return float(r.std())


def formula(s: Spec, yv: str) -> str:
    tcol = time_col(s.freq)
    st = "state_yq" if s.freq == "q" else "state_year"
    rg = "region_yq" if s.freq == "q" else "region_year"
    fe = {"state": f"county_fips + {st}", "twfe": f"county_fips + {tcol}",
          "region": f"county_fips + {rg}", "risk": f"county_fips + {st} + risk_tercile^{tcol}"}[s.fe]
    rhs = "MT + M + T" + "".join(f" + {c}" for c in s.controls)
    return f"{yv} ~ {rhs} | {fe}"


def vcov(s: Spec):
    st = "state_yq" if s.freq == "q" else "state_year"
    return {"county": {"CRV1": "county_fips"}, "state": {"CRV1": "state_fips"},
            "twoway": {"CRV1": f"county_fips+{st}"}}[s.cluster]


def run(s: Spec) -> dict:
    d, yv = build(s)
    base = {"outcome": s.outcome, "label": s.label, "definition": s.definition, "timing": s.timing,
            "tornado": s.tornado, "fe": s.fe, "cluster": s.cluster, "weights": s.weights or "none",
            "transform": s.transform or "none", "sample": str(s.sample) if s.sample else "full",
            "intensity": s.intensity or "binary", "placebo": s.placebo or ""}
    if len(d) == 0 or d["MT"].abs().sum() == 0:
        return {**base, "status": "not estimable (no treated tornado obs)"}
    wcol = None
    if s.weights:
        wcol = "baseline_pop" if s.weights == "pop" else s.weights
        d = d[d[wcol].notna() & (d[wcol] > 0)]
        if d["MT"].abs().sum() == 0:
            return {**base, "status": "not estimable after weighting"}
    try:
        fit = pf.feols(formula(s, yv), data=d, vcov=vcov(s), weights=wcol)
        tb = fit.tidy()
        if "MT" not in tb.index:
            return {**base, "status": "MT collinear"}
        r = tb.loc["MT"]
        g2 = tb.loc["T"] if "T" in tb.index else None
        mt = d["MT"] > 0
        out = {**base, "status": "ok", "beta": r["Estimate"], "se": r["Std. Error"], "t": r["t value"],
               "p": r["Pr(>|t|)"], "ci_low": r["2.5%"], "ci_high": r["97.5%"],
               "gamma_T": g2["Estimate"] if g2 is not None else np.nan,
               "gamma_T_se": g2["Std. Error"] if g2 is not None else np.nan,
               "gamma_M": tb.loc["M", "Estimate"] if "M" in tb.index else np.nan,
               "N": int(fit._N), "counties": d.county_fips.nunique(),
               "treated_counties": d.loc[d.ever == 1, "county_fips"].nunique(),
               "treated_tornado_obs": int(mt.sum()), "untreated_tornado_obs": int(((d["T"] > 0) & (d["M"] == 0)).sum()),
               "r2_within": getattr(fit, "_r2_within", np.nan),
               "y_mean": d[yv].mean(), "y_sd": d[yv].std(), "yvar": yv,
               "y_sd_within": within_sd(d, yv, s.freq),
               "n_clusters": d[vcov(s)["CRV1"].split("+")[0]].nunique()}
        return out
    except Exception as e:  # noqa: BLE001
        return {**base, "status": f"error: {str(e)[:120]}"}


def primary_spec(row: pd.Series) -> Spec:
    return Spec(outcome=row["variable"], freq=row["freq"], align=row.get("align", "mar"))
