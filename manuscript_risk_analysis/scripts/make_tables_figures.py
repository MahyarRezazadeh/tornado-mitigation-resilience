"""Reproduce every table, figure and in-text number of the Risk Analysis manuscript.

Inputs (built by the project pipeline in ../tornado_mitigation/src):
  data/processed/gap_county_disaster.parquet   (51_gap_mechanisms.py; county x declaration panel)
  data/processed/gap_subapps_linked.parquet    (51_gap_mechanisms.py; HMGP subapplications linked to counties)
  src/52_gap_causal_tests.py                   (finance(), state_intermediaries(), decl_dates())
  data/crosswalks/counties_2020.gpkg           (map)
Outputs: tables/table_*.tex, appendix/table_A*.tex, figures/figure_*.pdf, audit/results_numbers.json
Specifications are identical to scripts 50-52 of the project; this script does not alter any of them.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys
import warnings

import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyfixest as pf

warnings.filterwarnings("ignore")
MS = pathlib.Path(__file__).resolve().parents[1]
PROJ = MS.parent / "tornado_mitigation"
sys.path.insert(0, str(PROJ / "src"))
_s = importlib.util.spec_from_file_location("g52", PROJ / "src" / "52_gap_causal_tests.py")
g52 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(g52)

TAB, FIG, APP, AUD = MS / "tables", MS / "figures", MS / "appendix", MS / "audit"
for p in (TAB, FIG, APP, AUD):
    p.mkdir(exist_ok=True)
VC = {"CRV1": "county_fips"}
EXPO = "E + lpe + track_km + mag + cas + ldmg + ldmg_pc"
DEMO = "linc + pov_rate + nonwhite + nonmetro"
GOVS = "ln_gp + ln_sd + ln_sch"
NUM: dict = {}                 # every number quoted in the text, keyed for the claim map
BLUE, ORANGE, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#d9d8d4"

mpl.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"], "font.size": 9,
                     "axes.edgecolor": MUTED, "axes.linewidth": 0.6, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42,
                     "legend.frameon": False, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5,
                     "axes.axisbelow": True})


# ----------------------------------------------------------------------------- helpers
def fit(y, rhs, fe, data, term="small", vcov=None):
    m = pf.feols(f"{y} ~ {rhs} | {fe}", data=data, vcov=vcov or VC)
    t = m.tidy()
    r = t.loc[term]
    d = m._data
    ref = d.loc[d.small == 0, y].mean() if (term == "small" and "small" in d) else d[y].mean()
    return {"b": float(r["Estimate"]), "se": float(r["Std. Error"]), "p": float(r["Pr(>|t|)"]),
            "lo": float(r["2.5%"]), "hi": float(r["97.5%"]), "N": int(m._N),
            "clusters": int(d[(vcov or VC)["CRV1"]].nunique()), "ref_mean": float(ref), "model": m}


def stars(p):
    return "^{***}" if p < 0.01 else "^{**}" if p < 0.05 else "^{*}" if p < 0.1 else ""


def cell(r, scale=100, dig=2):
    return f"${r['b'] * scale:.{dig}f}{stars(r['p'])}$", f"$({r['se'] * scale:.{dig}f})$"


def save_tex(path, body):
    # shrink-to-fit guard: tables never exceed the text block
    body = body.replace("\\begin{tabular}", "\\begin{adjustbox}{max width=\\linewidth}\n\\begin{tabular}", 1)
    body = body.replace("\\end{tabular}", "\\end{tabular}\n\\end{adjustbox}", 1)
    path.write_text(body, encoding="utf-8")


def keep(key, r, scale=100):
    NUM[key] = {k: (round(v * scale, 3) if k in ("b", "se", "lo", "hi") else (round(v * (100 if k == "ref_mean" and scale == 100 else 1), 3)
                                                                             if isinstance(v, float) else v))
                for k, v in r.items() if k != "model"}


# ----------------------------------------------------------------------------- data
x = pd.read_parquet(PROJ / "data" / "processed" / "gap_county_disaster.parquet")
x = x.merge(g52.finance(), how="left", on="county_fips").merge(g52.decl_dates(), how="left", on="disasterNumber")
x = x.merge(g52.state_intermediaries(), how="left", on="STUSPS")
pop = x.baseline_pop.clip(lower=100)
for c in ["tax_cgov", "tax_all", "admin_cgov"]:
    x["l" + c + "_pc"] = np.log1p(x[c].fillna(0) / pop)
cty = x.drop_duplicates("county_fips").set_index("county_fips")
x["low_ladmin_cgov_pc"] = (x.county_fips.map(cty["ladmin_cgov_pc"].rank(pct=True)) <= 1 / 3).astype(int)
x["fed_pc"] = x.dis_fed / pop
x["pop_k"] = x.baseline_pop / 1000
x["dmg_m"] = x.reported_property_damage.fillna(0) / 1e6
x["inc_k"] = x.med_inc / 1000
NUM["sample"] = {"county_declarations": len(x), "counties": int(x.county_fips.nunique()),
                 "disasters": int(x.disasterNumber.nunique()), "states": int(x.STUSPS.nunique()),
                 "years": [int(x.year.min()), int(x.year.max())], "share_small": round(float(x.small.mean()), 3),
                 "share_hit": round(float(x.E.mean()), 3),
                 "small_pop_cutoff": float(x.loc[x.small == 1, "baseline_pop"].max())}
a = pd.read_parquet(PROJ / "data" / "processed" / "gap_subapps_linked.parquet")

# ----------------------------------------------------------------------------- Table 1
T1 = [("Outcomes (per county-declaration)", None),
      ("Any HMGP subapplication filed", "applied"), ("Number of HMGP subapplications", "n_app"),
      ("Any funded HMGP project", "dis_any"), ("Funded safe room or wind retrofit", "dis_strict"),
      ("Safe room or wind retrofit obligated within 3 years", "win3_strict"),
      ("Federal HMGP dollars per resident", "fed_pc"),
      ("Hazard exposure", None),
      ("Tornado path crossed a populated place", "E"), ("Residents in tornado paths", "pop_exposed"),
      ("Tornado track length in county (km)", "track_km"), ("Reported property damage (\\$ million)", "dmg_m"),
      ("County characteristics", None),
      ("Population (thousands)", "pop_k"), ("Median household income (\\$ thousand)", "inc_k"),
      ("Poverty rate", "pov_rate"), ("Non-White population share", "nonwhite"), ("Nonmetropolitan", "nonmetro"),
      ("Municipalities and townships", "n_gp"), ("Special districts", "n_sd"), ("School districts", "n_sch"),
      ("County government lists a website", "county_web"), ("Any prior HMA project", "prior_hma")]
rows = []
for lab, v in T1:
    if v is None:
        rows.append(f"\\multicolumn{{6}}{{l}}{{\\textit{{{lab}}}}} \\\\")
        continue
    s, sm, lg = x[v], x.loc[x.small == 1, v], x.loc[x.small == 0, v]
    dig = 3 if s.abs().max() <= 1.5 else 2 if s.abs().max() < 100 else 1
    f = lambda z: f"{z:,.{dig}f}"  # noqa: E731
    rows.append(f"\\quad {lab} & {s.notna().sum():,} & {f(s.mean())} & {f(s.std())} & {f(sm.mean())} & {f(lg.mean())} \\\\")
t1 = rf"""\begin{{table}}[!htbp]
\centering
\caption{{Summary statistics, county--declaration observations, 1999--2021}}
\label{{tab:summary}}
\footnotesize
\begin{{tabular}}{{@{{}}lrrrrr@{{}}}}
\toprule
 & & \multicolumn{{2}}{{c}}{{All}} & \multicolumn{{2}}{{c}}{{Mean by county size}} \\
\cmidrule(lr){{3-4}}\cmidrule(lr){{5-6}}
Variable & $N$ & Mean & SD & Small & Larger \\
\midrule
{chr(10).join(rows)}
\bottomrule
\end{{tabular}}
\begin{{minipage}}{{0.95\linewidth}}\vspace{{4pt}}\scriptsize
\textit{{Note:}} One observation is a county designated in a major disaster declaration (DR) for a tornado or severe-storm incident that began in 1999--2021 ({NUM['sample']['county_declarations']:,} county--declarations; {NUM['sample']['counties']:,} counties; {NUM['sample']['disasters']} declarations). Small counties are the bottom third of U.S. counties by baseline population (at most {NUM['sample']['small_pop_cutoff']:,.0f} residents). HMGP outcomes are linked to the specific declaration; subapplications include withdrawn, denied, and pending records. Tornado exposure is constructed from Storm Prediction Center tracks and 2020 block-group population centroids; damage is from NOAA Storm Events; demographics from the 2009 American Community Survey; local-government counts from the 2017 Census of Governments.
\end{{minipage}}
\end{{table}}
"""
save_tex(TAB / "table_1.tex", t1)

# ----------------------------------------------------------------------------- Table 2: specification ladder
ladder = [("(1)", "small", "state_year"), ("(2)", "small", "disaster"), ("(3)", f"small + {EXPO}", "disaster"),
          ("(4)", f"small + {EXPO} + {DEMO}", "disaster"), ("(5)", f"small + {EXPO} + {DEMO} + {GOVS}", "disaster")]
panels = [("A. Any HMGP subapplication filed", "applied"), ("B. Any funded HMGP project", "dis_any"),
          ("C. Funded safe room or wind retrofit", "dis_strict")]
body = []
for plab, y in panels:
    body.append(f"\\multicolumn{{6}}{{l}}{{\\textit{{Panel {plab}}}}} \\\\")
    res = [fit(y, rhs, fe, x) for _, rhs, fe in ladder]
    for (c, _, _), r in zip(ladder, res):
        keep(f"T2_{y}_{c.strip('()')}", r)
    body.append("\\quad Small county & " + " & ".join(cell(r)[0] for r in res) + " \\\\")
    body.append(" & " + " & ".join(cell(r)[1] for r in res) + " \\\\")
    body.append("\\quad Mean, larger counties & " + " & ".join(f"{r['ref_mean'] * 100:.1f}" for r in res) + " \\\\")
body.append("\\midrule")
body.append("Observations & " + " & ".join(f"{r['N']:,}" for r in res) + " \\\\")
body.append("Counties (clusters) & " + " & ".join(f"{r['clusters']:,}" for r in res) + " \\\\")
body.append("Fixed effects & State$\\times$year & Decl. & Decl. & Decl. & Decl. \\\\")
body.append("Hazard exposure and damage & & & \\checkmark & \\checkmark & \\checkmark \\\\")
body.append("Income, poverty, race, nonmetro & & & & \\checkmark & \\checkmark \\\\")
body.append("Counts of local governments & & & & & \\checkmark \\\\")
t2 = rf"""\begin{{table}}[!htbp]
\centering
\caption{{The small-county gap in HMGP participation after tornado and severe-storm declarations}}
\label{{tab:baseline}}
\footnotesize
\begin{{tabular}}{{@{{}}lccccc@{{}}}}
\toprule
 & (1) & (2) & (3) & (4) & (5) \\
\midrule
{chr(10).join(body)}
\bottomrule
\end{{tabular}}
\begin{{minipage}}{{0.95\linewidth}}\vspace{{4pt}}\scriptsize
\textit{{Note:}} Linear probability models estimated by OLS. Coefficients and means are multiplied by 100 and read as percentage points. ``Small county'' is an indicator for the bottom third of counties by population. Standard errors clustered by county in parentheses. Declaration fixed effects compare counties designated in the same disaster declaration, which share the same HMGP allocation, state administration, and incident. Hazard controls: populated-place tornado hit, log residents in tornado paths, track length, maximum EF rating, log casualties, log reported damage, and log damage per resident. Declarations with a single designated county drop out of columns (2)--(5) as singletons. $^{{*}}p<0.1$; $^{{**}}p<0.05$; $^{{***}}p<0.01$.
\end{{minipage}}
\end{{table}}
"""
save_tex(TAB / "table_2.tex", t2)

# ----------------------------------------------------------------------------- Table 3: where in the pipeline
S5 = f"small + {EXPO} + {DEMO} + {GOVS}"
ap = x[x.n_dec > 0]
cols = [("Applied", "applied", x), ("\\shortstack{Log(1+\\\\number)}", "l_napp", x), ("\\shortstack{County gov.\\\\applied}", "applied_cgov", x),
        ("Approved", "succ_rate", ap), ("Withdrawn", "wd_rate", ap), ("Denied", "den_rate", ap),
        ("\\shortstack{County gov.\\\\funded}", "f_county_gov", x)]
res3 = []
for lab, y, d in cols:
    r = fit(y, S5, "disaster", d)
    keep(f"T3_{y}", r)
    res3.append(r)
# subapplication level (decided subapplications)
a2 = a.merge(x[["county_fips", "disasterNumber", "small", "E", "lpe", "track_km", "mag", "cas", "ldmg", "ldmg_pc", "linc",
                "pov_rate", "nonwhite", "nonmetro", "disaster", "ln_gp", "ln_sd", "ln_sch"]].drop_duplicates(["county_fips", "disasterNumber"]),
             how="inner", on=["county_fips", "disasterNumber"])
a2 = a2[a2.decided == 1].copy()
a2["lamt"] = np.log(a2.amt.where(a2.amt > 0))
a2["lbcr"] = np.log(a2.bcr.where(a2.bcr > 0))
sub = {y: fit(y, S5, "disaster", a2.dropna(subset=[y])) for y in ["lamt", "lbcr"]}
for y, r in sub.items():
    keep(f"T3sub_{y}", r)
NUM["subapps"] = {"linked_rows": int(len(a)), "decided": int(a.decided.sum()),
                  "status_counts": a.status.value_counts().to_dict()}
hdr = " & ".join(f"({i})" for i in range(1, 8))
t3 = rf"""\begin{{table}}[!htbp]
\centering
\caption{{Where the gap arises: applications versus decisions}}
\label{{tab:pipeline}}
\footnotesize
\begin{{tabular}}{{@{{}}lccccccc@{{}}}}
\toprule
 & \multicolumn{{3}}{{c}}{{Application margin}} & \multicolumn{{3}}{{c}}{{Share of decided subapplications}} & Award \\
\cmidrule(lr){{2-4}}\cmidrule(lr){{5-7}}\cmidrule(lr){{8-8}}
 & {' & '.join(c[0] for c in cols)} \\
 & {hdr} \\
\midrule
Small county & {' & '.join(cell(r)[0] for r in res3)} \\
 & {' & '.join(cell(r)[1] for r in res3)} \\
Mean, larger counties & {' & '.join(f"{r['ref_mean'] * 100:.1f}" for r in res3)} \\
Observations & {' & '.join(f"{r['N']:,}" for r in res3)} \\
Counties (clusters) & {' & '.join(f"{r['clusters']:,}" for r in res3)} \\
\bottomrule
\end{{tabular}}
\begin{{minipage}}{{0.95\linewidth}}\vspace{{4pt}}\scriptsize
\textit{{Note:}} All columns use the column (5) specification of Table~\ref{{tab:baseline}} (declaration fixed effects; hazard, demographic, and local-government-count controls). Coefficients multiplied by 100. Columns (1)--(3) and (7) use all county--declarations; ``county gov.'' restricts to subapplications or projects whose applicant is the county government itself, of which every county has exactly one. Columns (4)--(6) restrict to county--declarations with at least one decided subapplication and measure the share approved, withdrawn, or denied. Standard errors clustered by county. At the subapplication level (same controls), small-county subapplications request {abs(sub['lamt']['b']):.3f} log points less funding (SE {sub['lamt']['se']:.3f}) and report benefit--cost ratios {abs(sub['lbcr']['b']):.3f} log points lower (SE {sub['lbcr']['se']:.3f}). $^{{*}}p<0.1$; $^{{**}}p<0.05$; $^{{***}}p<0.01$.
\end{{minipage}}
\end{{table}}
"""
save_tex(TAB / "table_3.tex", t3)

# ----------------------------------------------------------------------------- Table 4: explanations
x["E_small"] = x.E * x.small
x["lpe_small"] = x.lpe * x.small
x["sm_lowadmin"] = x.small * x.low_ladmin_cgov_pc
p2 = x[x.year >= 2009].copy()
for c in ["sh_state", "sh_regional"]:
    p2["z_" + c] = (p2[c] - p2[c].mean()) / p2[c].std()
    p2["sm_z_" + c] = p2.small * p2["z_" + c]
d4 = x[(x.decl_date >= "2010-01-01") & (x.decl_date <= "2021-12-31")].copy()
d4["post"] = (d4.decl_date >= "2017-08-01").astype(int)
d4["sm_post"] = d4.small * d4.post
pl = d4[d4.post == 0].copy()
pl["sm_fake"] = pl.small * (pl.decl_date >= "2014-08-01").astype(int)
expl = []   # (panel, row label, term, outcome results list)
outs4 = [("applied", "Applied"), ("l_napp", "\\shortstack{Log(1+\\\\number)}"), ("applied_cgov", "\\shortstack{County gov.\\\\applied}"), ("dis_any", "Funded")]


def run4(fml_rhs, fe, data, term):
    return [fit(y, fml_rhs, fe, data, term=term) for y, _ in outs4]


blocks = [
    ("A. Same county, different declarations (county and declaration fixed effects)", [
        ("Tornado hit a populated place", run4("E + E_small", "county_fips + disaster", x, "E"), "E"),
        ("\\quad $\\times$ small county", run4("E + E_small", "county_fips + disaster", x, "E_small"), "E_small"),
        ("Log residents in tornado paths", run4("lpe + lpe_small", "county_fips + disaster", x, "lpe"), "lpe"),
        ("\\quad $\\times$ small county", run4("lpe + lpe_small", "county_fips + disaster", x, "lpe_small"), "lpe_small")]),
    ("B. Fiscal and administrative capacity (declaration fixed effects, full controls)", [
        ("Small county, controlling for taxes and administrative spending per resident",
         run4(f"small + ltax_cgov_pc + ltax_all_pc + ladmin_cgov_pc + {EXPO} + {DEMO} + {GOVS}", "disaster", x, "small"), "small"),
        ("Small $\\times$ low administrative spending",
         run4(f"small + low_ladmin_cgov_pc + sm_lowadmin + {EXPO} + {DEMO} + {GOVS}", "disaster", x, "sm_lowadmin"), "sm_lowadmin")]),
    ("C. State delivery (declarations 2009--2021; declaration fixed effects, full controls)", [
        ("Small $\\times$ state-filed share (SD), pre-2009",
         run4(f"small + sm_z_sh_state + {EXPO} + {DEMO} + {GOVS}", "disaster", p2, "sm_z_sh_state"), "sm_z_sh_state"),
        ("Small $\\times$ regional-body share (SD), pre-2009",
         run4(f"small + sm_z_sh_regional + {EXPO} + {DEMO} + {GOVS}", "disaster", p2, "sm_z_sh_regional"), "sm_z_sh_regional")]),
    ("D. Management-cost reimbursement, DRRA \\S1215 (county and declaration fixed effects)", [
        ("Small $\\times$ declared on/after 1 Aug 2017", run4(f"sm_post + {EXPO}", "county_fips + disaster", d4, "sm_post"), "sm_post"),
        ("Placebo: small $\\times$ declared on/after 1 Aug 2014 (pre-2017 sample)",
         run4(f"sm_fake + {EXPO}", "county_fips + disaster", pl, "sm_fake"), "sm_fake")]),
]
body = []
for plab, rws in blocks:
    body.append(f"\\multicolumn{{5}}{{l}}{{\\textit{{Panel {plab}}}}} \\\\")
    for lab, res, term in rws:
        for (y, _), r in zip(outs4, res):
            keep(f"T4_{term}_{y}", r)
        body.append(f"{lab} & " + " & ".join(cell(r)[0] for r in res) + " \\\\")
        body.append(" & " + " & ".join(cell(r)[1] for r in res) + " \\\\")
    body.append(f"\\quad Observations & " + " & ".join(f"{r['N']:,}" for r in rws[-1][1]) + " \\\\")
    body.append("\\addlinespace")
t4 = rf"""\begin{{table}}[!htbp]
\centering
\caption{{Testing explanations for the small-county application gap}}
\label{{tab:mechanisms}}
\footnotesize
\begin{{tabular}}{{@{{}}p{{0.47\linewidth}}cccc@{{}}}}
\toprule
 & {' & '.join(o[1] for o in outs4)} \\
 & (1) & (2) & (3) & (4) \\
\midrule
{chr(10).join(body)}
\bottomrule
\end{{tabular}}
\begin{{minipage}}{{0.95\linewidth}}\vspace{{4pt}}\scriptsize
\textit{{Note:}} Coefficients multiplied by 100. Outcomes: (1) any HMGP subapplication; (2) log one plus the number of subapplications; (3) a subapplication by the county government; (4) any funded HMGP project. Panel A omits damage controls because damage is the channel through which a hit operates. Panel B uses Census of Governments 2017 finance data; ``low'' is the bottom third of county-government administrative spending (financial administration and central staff) per resident. Panel C interacts the small-county indicator with the standardized share of each state's FY1989--2008 HMGP subapplications filed by state agencies or by regional planning and development bodies; the main effects are absorbed by declaration fixed effects. Panel D compares declarations made before and after 1 August 2017, the date from which DRRA \S1215 reimbursement of subrecipient management costs applies; the placebo repeats the comparison at a false date within the pre-reform period. Standard errors clustered by county. $^{{*}}p<0.1$; $^{{**}}p<0.05$; $^{{***}}p<0.01$.
\end{{minipage}}
\end{{table}}
"""
save_tex(TAB / "table_4.tex", t4)

# ----------------------------------------------------------------------------- Table 5: robustness
FULL = f"small + {EXPO} + {DEMO}"
rob = [("Baseline (Table 2, column 4)", FULL, "disaster", x, VC, "small"),
       ("Standard errors clustered by state", FULL, "disaster", x, {"CRV1": "state_fips"}, "small"),
       ("Hit-only sample (populated-place tornado hit)", f"small + lpe + track_km + mag + cas + ldmg + ldmg_pc + {DEMO}", "disaster", x[x.E == 1], VC, "small"),
       ("Declarations with incident type ``Tornado'' only", FULL, "disaster", x[x.tornado_incident == 1], VC, "small"),
       ("Declarations with Individual Assistance", FULL, "disaster", x[x.ia == 1], VC, "small"),
       ("Adding counts of local governments", f"{FULL} + {GOVS}", "disaster", x, VC, "small"),
       ("Continuous log population (per log point)", f"lpop + {EXPO} + {DEMO}", "disaster", x, VC, "lpop")]
routs = [("dis_any", "Funded HMGP project"), ("dis_strict", "Funded safe room/retrofit"), ("win3_strict", "Safe room/retrofit, 3 yrs")]
body = []
for lab, rhs, fe, d, vc, term in rob:
    res = [fit(y, rhs, fe, d, term=term, vcov=vc) for y, _ in routs]
    for (y, _), r in zip(routs, res):
        keep(f"T5_{lab[:24]}_{y}", r)
    body.append(f"{lab} & " + " & ".join(cell(r)[0] + " " + cell(r)[1] for r in res) + f" & {res[0]['N']:,} \\\\")
# outcomes that credit statewide projects / longer window
alt = [("Credit statewide projects of the same declaration", ["dis_any_sw", "dis_strict_sw", None]),
       ("Five-year window", [None, None, "win5_strict"])]
for lab, ys in alt:
    cells, ns = [], []
    for y in ys:
        if y is None:
            cells.append("--")
        else:
            r = fit(y, FULL, "disaster", x)
            keep(f"T5_{lab[:24]}_{y}", r)
            ns.append(r["N"])
            cells.append(cell(r)[0] + " " + cell(r)[1] + f" [{r['ref_mean'] * 100:.1f}]")
    body.append(f"{lab} & " + " & ".join(cells) + f" & {ns[0]:,} \\\\")
# leave-one-state-out
loso = {y: [] for y, _ in routs}
for st in sorted(x.STUSPS.unique()):
    s = x[x.STUSPS != st]
    for y, _ in routs:
        loso[y].append(fit(y, FULL, "disaster", s)["b"])
NUM["T5_loso"] = {y: [round(min(v) * 100, 2), round(max(v) * 100, 2)] for y, v in loso.items()}
body.append("Leave one state out: range of estimates & " + " & ".join(f"[${min(v) * 100:.2f}$, ${max(v) * 100:.2f}$]" for v in loso.values()) + " & -- \\\\")
t5 = rf"""\begin{{table}}[!htbp]
\centering
\caption{{Robustness of the small-county gap in funded projects}}
\label{{tab:robust}}
\footnotesize
\begin{{tabular}}{{@{{}}p{{0.40\linewidth}}cccr@{{}}}}
\toprule
 & {' & '.join(o[1] for o in routs)} & $N$ \\
\midrule
{chr(10).join(body)}
\bottomrule
\end{{tabular}}
\begin{{minipage}}{{0.95\linewidth}}\vspace{{4pt}}\scriptsize
\textit{{Note:}} Each cell reports the small-county coefficient (multiplied by 100) with its county-clustered standard error in parentheses, from the column (4) specification of Table~\ref{{tab:baseline}} unless stated. Means for larger counties of the two alternative outcomes are in brackets. ``Credit statewide projects'' counts a county as served when the state ran any HMGP project under the same declaration on a statewide basis. The leave-one-state-out row reports the minimum and maximum of the estimates obtained by dropping each state in turn. $^{{*}}p<0.1$; $^{{**}}p<0.05$; $^{{***}}p<0.01$.
\end{{minipage}}
\end{{table}}
"""
save_tex(TAB / "table_5.tex", t5)

# ----------------------------------------------------------------------------- Appendix: decile gradient & DRRA event study tables
dec_res = {}
for y in ["applied", "dis_any"]:
    m = pf.feols(f"{y} ~ i(pop_dec, ref=9) + {EXPO} + {DEMO} | disaster", data=x, vcov=VC)
    t = m.tidy()
    t = t[t.index.str.contains("pop_dec")]
    dec_res[y] = pd.DataFrame({"decile": [int(i.split("::")[1]) + 1 for i in t.index], "b": t["Estimate"].values,
                               "lo": t["2.5%"].values, "hi": t["97.5%"].values, "se": t["Std. Error"].values})
NUM["deciles"] = {y: dict(zip(v.decile, (v.b * 100).round(2))) for y, v in dec_res.items()}
d4["dy"] = d4.decl_date.dt.year
es = {}
for y in ["applied", "dis_any"]:
    m = pf.feols(f"{y} ~ i(dy, small, ref=2016) + {EXPO} | county_fips + disaster", data=d4, vcov=VC)
    t = m.tidy()
    t = t[t.index.str.contains("dy::")]
    es[y] = pd.DataFrame({"year": [int(i.split("::")[1].split(":")[0]) for i in t.index], "b": t["Estimate"].values,
                          "lo": t["2.5%"].values, "hi": t["97.5%"].values, "p": t["Pr(>|t|)"].values})
NUM["drra_event_min_p"] = {y: round(float(v.p.min()), 3) for y, v in es.items()}
rows = []
for i in range(10):
    r = [f"{i + 1}"]
    for y in ["applied", "dis_any"]:
        v = dec_res[y]
        rr = v[v.decile == i + 1]
        r.append("0 (reference)" if rr.empty else f"${rr.b.iloc[0] * 100:.2f}$ $({rr.se.iloc[0] * 100:.2f})$")
    rows.append(" & ".join(r) + " \\\\")
ta1 = rf"""\begin{{table}}[!htbp]
\centering
\caption{{Population-decile gradient (relative to the largest decile)}}
\label{{tab:deciles}}
\footnotesize
\begin{{tabular}}{{@{{}}ccc@{{}}}}
\toprule
Population decile & Any subapplication & Any funded project \\
\midrule
{chr(10).join(rows)}
\bottomrule
\end{{tabular}}
\begin{{minipage}}{{0.8\linewidth}}\vspace{{4pt}}\scriptsize
\textit{{Note:}} Declaration fixed effects with hazard and demographic controls (Table~\ref{{tab:baseline}}, column 4). Coefficients multiplied by 100; county-clustered standard errors in parentheses.
\end{{minipage}}
\end{{table}}
"""
save_tex(APP / "table_A2_deciles.tex", ta1)

# Appendix: coefficients on controls in the column (4) and (5) specifications
CL = [("small", "Small county"), ("E", "Tornado path crossed a populated place"), ("lpe", "Log residents in tornado paths"),
      ("track_km", "Track length in county (km)"), ("mag", "Maximum EF rating (+1)"), ("cas", "Log casualties"),
      ("ldmg", "Log reported damage"), ("ldmg_pc", "Log damage per resident"), ("linc", "Log median household income"),
      ("pov_rate", "Poverty rate"), ("nonwhite", "Non-White share"), ("nonmetro", "Nonmetropolitan"),
      ("ln_gp", "Log municipalities and townships"), ("ln_sd", "Log special districts"), ("ln_sch", "Log school districts")]
ctab = {}
for y in ["applied", "dis_any"]:
    for spec, rhs in [("4", f"small + {EXPO} + {DEMO}"), ("5", f"small + {EXPO} + {DEMO} + {GOVS}")]:
        m = pf.feols(f"{y} ~ {rhs} | disaster", data=x, vcov=VC)
        ctab[(y, spec)] = m.tidy()
rows = []
for v, lab in CL:
    cells = []
    for y in ["applied", "dis_any"]:
        for spec in ["4", "5"]:
            t = ctab[(y, spec)]
            cells.append("" if v not in t.index else
                         f"${t.loc[v, 'Estimate'] * 100:.2f}{stars(t.loc[v, 'Pr(>|t|)'])}$ $({t.loc[v, 'Std. Error'] * 100:.2f})$")
    rows.append(f"{lab} & " + " & ".join(cells) + " \\\\")
NUM["controls_col4"] = {y: {v: round(float(ctab[(y, '4')].loc[v, 'Estimate']) * 100, 3) for v, _ in CL if v in ctab[(y, '4')].index}
                        for y in ["applied", "dis_any"]}
ta2 = rf"""\begin{{table}}[!htbp]
\centering
\caption{{Coefficients on all regressors in the baseline specifications}}
\label{{tab:controls}}
\scriptsize
\begin{{tabular}}{{@{{}}lcccc@{{}}}}
\toprule
 & \multicolumn{{2}}{{c}}{{Any subapplication}} & \multicolumn{{2}}{{c}}{{Any funded project}} \\
\cmidrule(lr){{2-3}}\cmidrule(lr){{4-5}}
 & (4) & (5) & (4) & (5) \\
\midrule
{chr(10).join(rows)}
\bottomrule
\end{{tabular}}
\begin{{minipage}}{{0.9\linewidth}}\vspace{{4pt}}\scriptsize
\textit{{Note:}} Columns correspond to columns (4) and (5) of Table~\ref{{tab:baseline}}, with declaration fixed effects. Coefficients multiplied by 100; county-clustered standard errors in parentheses. $^{{*}}p<0.1$; $^{{**}}p<0.05$; $^{{***}}p<0.01$.
\end{{minipage}}
\end{{table}}
"""
save_tex(APP / "table_A1_controls.tex", ta2)

# ----------------------------------------------------------------------------- Figures
# Figure 1: map
cg = gpd.read_file(PROJ / "data" / "crosswalks" / "counties_2020.gpkg")
cg = cg[~cg.county_fips.str[:2].isin(["02", "15", "60", "66", "69", "72", "78"])].to_crs(5070)
ndec = x.groupby("county_fips").disasterNumber.nunique()
size = x.drop_duplicates("county_fips").set_index("county_fips").small
allcty = pd.read_parquet(PROJ / "data" / "crosswalks" / "counties_2020.parquet")[["county_fips"]]
pr = pd.read_parquet(PROJ / "data" / "processed" / "county_year_panel.parquet", columns=["county_fips", "baseline_pop"]).drop_duplicates("county_fips")
pr["small_all"] = (pr.baseline_pop.rank(pct=True) <= 1 / 3).astype(int)
cg = cg.merge(pr[["county_fips", "small_all"]], how="left").merge(ndec.rename("ndec").reset_index(), how="left")
cg["ndec"] = cg.ndec.fillna(0)
fig, axs = plt.subplots(1, 2, figsize=(7.0, 2.6))
seq = ["#f3f3f1", "#c6dbf3", "#86b4e8", "#4a8fdc", "#2a78d6", "#1b4f8f"]
bins = [-0.5, 0.5, 1.5, 2.5, 4.5, 7.5, 100]
labs = ["0", "1", "2", "3–4", "5–7", "8+"]
cg["dcat"] = pd.cut(cg.ndec, bins, labels=labs)
for k, (lab, col) in enumerate(zip(labs, seq)):
    cg[cg.dcat == lab].plot(ax=axs[0], color=col, linewidth=0.05, edgecolor="#ffffff", rasterized=True)
axs[0].set_title("(a) Tornado and severe-storm declarations, 1999–2021", fontsize=8.5, color=INK, loc="left")
handles = [mpl.patches.Patch(facecolor=c, edgecolor=MUTED, linewidth=0.3, label=l) for l, c in zip(labs, seq)]
axs[0].legend(handles=handles, loc="lower right", fontsize=6.5, title="Declarations", title_fontsize=6.5, ncol=2,
              handlelength=1, columnspacing=0.6)
cg[cg.small_all == 0].plot(ax=axs[1], color="#e4e3df", linewidth=0.05, edgecolor="#ffffff", rasterized=True)
cg[cg.small_all == 1].plot(ax=axs[1], color=ORANGE, linewidth=0.05, edgecolor="#ffffff", rasterized=True)
axs[1].set_title("(b) Small counties (bottom third by population)", fontsize=8.5, color=INK, loc="left")
axs[1].legend(handles=[mpl.patches.Patch(facecolor=ORANGE, label="Small"), mpl.patches.Patch(facecolor="#e4e3df", label="Larger")],
              loc="lower right", fontsize=6.5)
for ax in axs:
    ax.set_axis_off()
fig.tight_layout()
fig.savefig(FIG / "figure_1.pdf", dpi=300)  # polygons rasterized (file size); text stays vector
plt.close(fig)

# Figure 2: raw funnel and adjusted gradient by population decile
raw = x.groupby(x.pop_dec + 1).agg(applied=("applied", "mean"), funded=("dis_any", "mean"),
                                   pop_med=("baseline_pop", "median"))
NUM["fig2_raw"] = {int(k): {"applied": round(v.applied * 100, 1), "funded": round(v.funded * 100, 1), "pop_median": int(v.pop_med)}
                   for k, v in raw.iterrows()}
fig, axs = plt.subplots(1, 2, figsize=(7.0, 2.7))
axs[0].plot(raw.index, raw.applied * 100, color=BLUE, lw=2, marker="o", ms=4.5, label="Any subapplication")
axs[0].plot(raw.index, raw.funded * 100, color=ORANGE, lw=2, marker="s", ms=4.5, label="Any funded project")
axs[0].set_xlabel("Population decile (1 = smallest)")
axs[0].set_ylabel("Share of county–declarations (%)")
axs[0].set_title("(a) Raw shares", fontsize=8.5, loc="left", color=INK)
axs[0].set_xticks(range(1, 11))
axs[0].set_ylim(0, None)
axs[0].legend(fontsize=7, loc="upper left")
for y, col, mk, off, lab in [("applied", BLUE, "o", -0.12, "Any subapplication"), ("dis_any", ORANGE, "s", 0.12, "Any funded project")]:
    v = dec_res[y]
    xs = list(v.decile) + [10]
    bs = list(v.b * 100) + [0]
    los = list(v.lo * 100) + [0]
    his = list(v.hi * 100) + [0]
    xx = np.array(xs) + off
    axs[1].vlines(xx, los, his, color=col, lw=1)
    axs[1].plot(xx, bs, color=col, lw=0, marker=mk, ms=4.5, label=lab)
axs[1].axhline(0, color=MUTED, lw=0.8)
axs[1].set_xlabel("Population decile (10 = reference)")
axs[1].set_ylabel("Difference from largest decile (pp)")
axs[1].set_title("(b) Adjusted, within declaration", fontsize=8.5, loc="left", color=INK)
axs[1].set_xticks(range(1, 11))
axs[1].legend(fontsize=7, loc="lower right")
fig.tight_layout()
fig.savefig(FIG / "figure_2.pdf")
plt.close(fig)

# Figure 3: pipeline decomposition (Table 3, coefficient plot)
labels3 = ["Any subapplication", "Log(1+number of\nsubapplications)", "County government\napplied", "Approved, given\ndecided subapps",
           "Withdrawn, given\ndecided subapps", "Denied, given\ndecided subapps", "County government\nfunded"]
fig, ax = plt.subplots(figsize=(6.2, 3.0))
ypos = np.arange(len(res3))[::-1]
for yy, r, lab in zip(ypos, res3, labels3):
    col = BLUE if lab.startswith(("Approved", "Withdrawn", "Denied")) else ORANGE
    mk = "D" if col == BLUE else "o"
    ax.hlines(yy, r["lo"] * 100, r["hi"] * 100, color=col, lw=1.5)
    ax.plot(r["b"] * 100, yy, marker=mk, color=col, ms=5.5, lw=0)
ax.axvline(0, color=MUTED, lw=0.8)
ax.set_yticks(ypos)
ax.set_yticklabels(labels3, fontsize=7.5)
ax.set_xlabel("Small minus larger counties (percentage points; 95% CI)")
ax.grid(axis="y", visible=False)
fig.legend(handles=[mpl.lines.Line2D([], [], color=ORANGE, marker="o", lw=1.5, label="Application or award margin"),
                    mpl.lines.Line2D([], [], color=BLUE, marker="D", lw=1.5, label="Decision margin (conditional on applying)")],
           fontsize=7, loc="upper center", ncol=2, bbox_to_anchor=(0.6, 1.0))
fig.subplots_adjust(top=0.88)
fig.tight_layout(rect=(0, 0, 1, 0.92))
fig.savefig(FIG / "figure_3.pdf")
plt.close(fig)

# Figure 4: within-county response to a tornado hit, larger vs small counties
resp = []
for y, lab in [("l_napp", "Log(1+number of\nsubapplications)"), ("applied_cgov", "County government\napplied"),
               ("applied", "Any subapplication")]:
    m = pf.feols(f"{y} ~ E + E_small | county_fips + disaster", data=x, vcov=VC)
    b, V = m.coef(), m._vcov
    names = list(m.coef().index)
    iE, iS = names.index("E"), names.index("E_small")
    bl, sel = b.iloc[iE], np.sqrt(V[iE, iE])
    bs = b.iloc[iE] + b.iloc[iS]
    ses = np.sqrt(V[iE, iE] + V[iS, iS] + 2 * V[iE, iS])
    resp.append((lab, bl, sel, bs, ses))
    NUM[f"fig4_{y}"] = {"larger_b": round(bl * 100, 2), "larger_se": round(sel * 100, 2), "small_b": round(bs * 100, 2),
                        "small_se": round(ses * 100, 2)}
fig, ax = plt.subplots(figsize=(6.2, 2.6))
for i, (lab, bl, sel, bs, ses) in enumerate(resp):
    yy = len(resp) - 1 - i
    ax.hlines(yy + 0.14, (bl - 1.96 * sel) * 100, (bl + 1.96 * sel) * 100, color=BLUE, lw=1.5)
    ax.plot(bl * 100, yy + 0.14, "o", color=BLUE, ms=5.5)
    ax.hlines(yy - 0.14, (bs - 1.96 * ses) * 100, (bs + 1.96 * ses) * 100, color=ORANGE, lw=1.5)
    ax.plot(bs * 100, yy - 0.14, "s", color=ORANGE, ms=5.5)
ax.axvline(0, color=MUTED, lw=0.8)
ax.set_yticks(range(len(resp))[::-1])
ax.set_yticklabels([r[0] for r in resp], fontsize=7.5)
ax.set_xlabel("Effect of a populated-place tornado hit (×100; 95% CI)")
ax.grid(axis="y", visible=False)
ax.legend(handles=[mpl.lines.Line2D([], [], color=BLUE, marker="o", lw=1.5, label="Larger counties"),
                   mpl.lines.Line2D([], [], color=ORANGE, marker="s", lw=1.5, label="Small counties")], fontsize=7,
          loc="lower center", ncol=2, bbox_to_anchor=(0.5, 1.0))
fig.tight_layout()
fig.savefig(FIG / "figure_4.pdf")
plt.close(fig)

# Figure 5: DRRA event study
fig, ax = plt.subplots(figsize=(6.2, 2.7))
for y, col, mk, off, lab in [("applied", BLUE, "o", -0.12, "Any subapplication"), ("dis_any", ORANGE, "s", 0.12, "Any funded project")]:
    v = es[y]
    yrs = list(v.year) + [2016]
    bs = list(v.b * 100) + [0]
    los = list(v.lo * 100) + [0]
    his = list(v.hi * 100) + [0]
    xx = np.array(yrs) + off
    ax.vlines(xx, los, his, color=col, lw=1)
    ax.plot(xx, bs, marker=mk, color=col, lw=0, ms=4.5, label=lab)
ax.axhline(0, color=MUTED, lw=0.8)
ax.axvline(2017.58, color=INK, lw=0.8, ls="--", label="DRRA §1215 applies (declared on/after 1 Aug 2017)")
ax.set_xticks(range(2010, 2022))
ax.set_xlabel("Year of declaration (2016 = reference)")
ax.set_ylabel("Small × year (pp)")
ax.legend(fontsize=7, loc="lower center", ncol=3, bbox_to_anchor=(0.5, 1.0))
fig.tight_layout()
fig.savefig(FIG / "figure_5.pdf")
plt.close(fig)

# ----------------------------------------------------------------------------- extra numbers used in text
NUM["raw_rates"] = {"applied_small": round(float(x.loc[x.small == 1, "applied"].mean()) * 100, 1),
                    "applied_larger": round(float(x.loc[x.small == 0, "applied"].mean()) * 100, 1),
                    "funded_small": round(float(x.loc[x.small == 1, "dis_any"].mean()) * 100, 1),
                    "funded_larger": round(float(x.loc[x.small == 0, "dis_any"].mean()) * 100, 1),
                    "succ_small": round(float(ap.loc[ap.small == 1, "succ_rate"].mean()) * 100, 1),
                    "succ_larger": round(float(ap.loc[ap.small == 0, "succ_rate"].mean()) * 100, 1),
                    "strict_larger": round(float(x.loc[x.small == 0, "dis_strict"].mean()) * 100, 1),
                    "strict_small": round(float(x.loc[x.small == 1, "dis_strict"].mean()) * 100, 1)}
NUM["govcounts"] = x.drop_duplicates("county_fips").groupby("small")[["n_gp", "n_sd", "n_sch", "county_web"]].mean().round(2).to_dict()
NUM["fiscal_means"] = x.drop_duplicates("county_fips").groupby("small")[["ladmin_cgov_pc", "ltax_cgov_pc"]].mean().round(3).to_dict()
NUM["state_shares"] = {"sh_state_mean": round(float(p2.drop_duplicates("STUSPS").sh_state.mean()), 3),
                       "sh_state_sd": round(float(p2.sh_state.std()), 3),
                       "sh_regional_max": round(float(p2.drop_duplicates("STUSPS").sh_regional.max()), 3)}
NUM["drra_raw"] = d4.groupby(["post", "small"]).applied.mean().mul(100).round(1).unstack().to_dict()
NUM["drra_N"] = int(len(d4))
(AUD / "results_numbers.json").write_text(json.dumps(NUM, indent=1, default=str), encoding="utf-8")
print(json.dumps({k: NUM[k] for k in ["sample", "raw_rates"]}, indent=1, default=str))
print("T2 dis_any:", [NUM[f"T2_dis_any_{i}"]["b"] for i in range(1, 6)])
print("T2 applied:", [NUM[f"T2_applied_{i}"]["b"] for i in range(1, 6)])
print("T2 dis_strict:", [NUM[f"T2_dis_strict_{i}"]["b"] for i in range(1, 6)])
print("T3:", {k: (v["b"], v["se"], round(v["p"], 3)) for k, v in NUM.items() if k.startswith("T3")})
print("T4:", {k: (v["b"], v["se"], round(v["p"], 3)) for k, v in NUM.items() if k.startswith("T4")})
print("T5:", {k: (v["b"], v["se"], round(v["p"], 3)) for k, v in NUM.items() if k.startswith("T5_") and isinstance(v, dict) and "b" in v})
print("LOSO:", NUM["T5_loso"])
print("fig4:", {k: v for k, v in NUM.items() if k.startswith("fig4")})
print("drra event min p:", NUM["drra_event_min_p"], "raw:", NUM["drra_raw"])




