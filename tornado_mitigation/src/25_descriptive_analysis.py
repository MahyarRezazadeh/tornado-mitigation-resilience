"""Descriptive analysis (Section 23): Table 1, Table 2, top-10 states, Figures 1-5.

Outputs: output/tables/table1_fema_treatment_summary.md, table2_treated_vs_control.md, top10_states.md
         output/figures/fig01..fig05*.png
"""
from __future__ import annotations

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from utils import FIGS, INTER, PROC, TABLES, XWALK, get_logger  # noqa: E402

log = get_logger(__file__)


def main() -> None:
    p = pd.read_parquet(INTER / "fema_treatment_projects.parquet")
    cty = pd.read_parquet(XWALK / "counties_2020.parquet")
    p = p[p.county_fips.isin(cty.county_fips)]
    rows = []
    for d in ["strict", "moderate", "broad"]:
        t = p[p[f"treat_{d}"] == 1]
        rows.append({"Definition": d, "Projects": t.projectIdentifier.nunique(), "Counties": t.county_fips.nunique(),
                     "States": t.state_fips.nunique(), "Federal share ($M)": round(t.federal_share.sum() / 1e6, 1),
                     "Total cost ($M)": round(t.total_cost.sum() / 1e6, 1),
                     "Safe-room projects": int((t.mitigation_type == "safe_room").sum()),
                     "Wind-retrofit projects": int((t.mitigation_type == "wind_retrofit").sum()),
                     "HIGH confidence share": round((t.classification_confidence == "HIGH").mean(), 3),
                     "Median primary-timing year": int(t.t_primary.dt.year.median()),
                     "Timing = obligation+2y": round((t.t_primary_source == "obligation+2").mean(), 3),
                     "HMGP share": round((t.programArea == "HMGP").mean(), 3),
                     "Post tornado/severe-storm declaration share": round(t.dis_incidentType.fillna("").str.contains("Tornado|Severe Storm").mean(), 3)})
    t1 = pd.DataFrame(rows)
    (TABLES / "table1_fema_treatment_summary.md").write_text(
        "# Table 1. FEMA tornado/wind mitigation treatment summary (funded projects, contiguous US, county-identified)\n\n"
        + t1.to_markdown(index=False), encoding="utf-8")

    st = p[p.treat_strict == 1].merge(cty[["county_fips", "STUSPS"]], on="county_fips")
    top = {"by treated counties": st.groupby("STUSPS").county_fips.nunique().nlargest(10),
           "by project count": st.groupby("STUSPS").projectIdentifier.nunique().nlargest(10),
           "by federal spending ($M)": (st.groupby("STUSPS").federal_share.sum() / 1e6).round(1).nlargest(10)}
    md = ["# Top 10 states (strict treatment)\n"]
    for k, v in top.items():
        md += [f"## {k}\n", v.to_frame(k).to_markdown(), ""]
    hhi = (st.groupby("STUSPS").county_fips.nunique() / st.county_fips.nunique()) ** 2
    md.append(f"Treated-county HHI across states: {hhi.sum():.3f} (1/HHI = {1 / hhi.sum():.1f} effective states)")
    (TABLES / "top10_states.md").write_text("\n".join(md), encoding="utf-8")

    cy = pd.read_parquet(PROC / "county_year_panel.parquet")
    b = cy.drop_duplicates("county_fips").copy()
    b["treated"] = b.ft_strict_primary.notna()
    c98 = pd.read_parquet(INTER / "cbp_county_year.parquet").query("year == 1998")
    b = b.merge(c98[["county_fips", "establishments", "annual_payroll", "cbp_employment", "small_estab_share"]].add_suffix("_98")
                .rename(columns={"county_fips_98": "county_fips"}), how="left")
    q = pd.read_parquet(PROC / "county_quarter_panel.parquet")
    qe = q[q.year.between(2000, 2004)].groupby("county_fips").agg(qwi_earn=("EarnS", "mean"), qwi_sep=("separation_rate", "mean"))
    b = b.merge(qe.reset_index(), how="left")
    ind = pd.read_parquet(INTER / "cbp_county_industry_year.parquet").query("year == 1998")
    sh = ind.pivot_table(index="county_fips", columns="industry_group", values="cbp_employment", aggfunc="sum")
    sh = sh.div(sh.sum(1), axis=0)[["Construction", "Manufacturing", "Retail", "Health", "Leisure/Hospitality"]]
    sh.columns = ["emp_share_" + c.split("/")[0].lower() for c in sh.columns]
    b = b.merge(sh.reset_index(), how="left")
    b["pay_per_emp_98"] = b.annual_payroll_98 / b.cbp_employment_98
    vars_ = {"baseline_pop": "Population 2000", "baseline_emp": "Employment 1995-99 (BDS)",
             "baseline_estabs": "Establishments 1995-99 (BDS)", "pay_per_emp_98": "Payroll per employee 1998 ($k)",
             "qwi_earn": "QWI monthly earnings 2000-04", "qwi_sep": "QWI separation rate 2000-04",
             "small_estab_share_98": "Small-establishment share 1998", "emp_share_construction": "Construction emp. share",
             "emp_share_manufacturing": "Manufacturing emp. share", "emp_share_retail": "Retail emp. share",
             "emp_share_health": "Health emp. share", "emp_share_leisure": "Leisure emp. share",
             "hist_tornado_count": "Tornadoes 1950-89", "hist_EF2_plus_count": "EF2+ tornadoes 1950-89",
             "hist_tornado_density": "Tornadoes per 1,000 km2 1950-89", "metro": "Metro county"}
    r2 = []
    for v, lab in vars_.items():
        x1, x0 = b.loc[b.treated, v], b.loc[~b.treated, v]
        sd = np.sqrt((x1.var() + x0.var()) / 2)
        r2.append({"Characteristic": lab, "Treated mean": x1.mean(), "Never-treated mean": x0.mean(),
                   "SMD": (x1.mean() - x0.mean()) / sd if sd > 0 else np.nan, "N treated": x1.notna().sum(),
                   "N control": x0.notna().sum()})
    t2 = pd.DataFrame(r2)
    (TABLES / "table2_treated_vs_control.md").write_text(
        "# Table 2. Pre-treatment characteristics: strict-treated vs never-treated counties\n\n"
        + t2.round(3).to_markdown(index=False), encoding="utf-8")

    # ---------- figures 1-5 ----------
    g = gpd.read_file(XWALK / "counties_2020.gpkg")
    n = st.groupby("county_fips").projectIdentifier.nunique().rename("n")
    g = g.merge(n, left_on="county_fips", right_index=True, how="left")
    fig, ax = plt.subplots(figsize=(11, 6.5))
    g.plot(ax=ax, color="#eeeeee", linewidth=0.05, edgecolor="white")
    g[g.n.notna()].plot(ax=ax, column=np.log1p(g.loc[g.n.notna(), "n"]), cmap="viridis", linewidth=0.05,
                        legend=True, legend_kwds={"label": "log(1 + strict projects)", "shrink": 0.6})
    ax.set_axis_off()
    ax.set_title("Figure 1. FEMA strict tornado/wind mitigation projects by county (funded, 1989-2026)")
    fig.tight_layout(); fig.savefig(FIGS / "fig01_mitigation_map.png", dpi=160); plt.close(fig)

    ct = pd.read_parquet(PROC / "county_treatment.parquet")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for d in ["strict", "moderate", "broad"]:
        s = ct[(ct.definition == d) & (ct.timing == "t_primary") & ct.county_fips.isin(cty.county_fips)]
        yr = s.first_treat_date.dt.year.value_counts().sort_index().cumsum()
        ax.step(yr.index, yr.values, where="post", label=d)
    ax.set_xlim(1990, 2026); ax.set_ylabel("Cumulative treated counties"); ax.legend()
    ax.set_title("Figure 2. Treated counties over time (primary timing: obligation + 2y)")
    fig.tight_layout(); fig.savefig(FIGS / "fig02_treated_counties.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    for d in ["strict", "moderate", "broad"]:
        s = p[(p[f"treat_{d}"] == 1)]
        yr = s.groupby(s.obligation_date.dt.year).federal_share.sum() / 1e6
        ax.plot(yr.index, yr.values, marker=".", label=d)
    ax.set_ylabel("Federal share obligated ($M, nominal)"); ax.legend()
    ax.set_title("Figure 3. FEMA tornado/wind mitigation spending by obligation year")
    fig.tight_layout(); fig.savefig(FIGS / "fig03_spending.png", dpi=160); plt.close(fig)

    ex = pd.read_parquet(PROC / "tornado_exposure_cq.parquet")
    e = ex[ex.year >= 1990].groupby("county_fips").EF1_plus.sum().rename("ef1q")
    g2 = g.merge(e, left_on="county_fips", right_index=True, how="left")
    fig, ax = plt.subplots(figsize=(11, 6.5))
    g2.plot(ax=ax, column="ef1q", cmap="magma_r", linewidth=0.05, legend=True,
            legend_kwds={"label": "County-quarters with EF1+ tornado, 1990-2025", "shrink": 0.6})
    ax.set_axis_off(); ax.set_title("Figure 4. Tornado exposure (EF1+ county-quarters, 1990-2025)")
    fig.tight_layout(); fig.savefig(FIGS / "fig04_tornado_map.png", dpi=160); plt.close(fig)

    t = pd.read_parquet(INTER / "tornadoes_clean.parquet")
    t = t[t.year >= 1990]
    yc = t.assign(b=pd.cut(t.ef.fillna(-1), [-2, -0.5, 0.5, 1.5, 2.5, 6], labels=["unknown", "EF0", "EF1", "EF2", "EF3+"])) \
        .groupby(["year", "b"]).size().unstack(fill_value=0)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    yc.plot.bar(stacked=True, ax=ax, width=0.85)
    ax.set_ylabel("Tornado county-segments"); ax.set_xlabel("")
    ax.set_xticks(range(0, len(yc), 5), yc.index[::5])
    ax.set_title("Figure 5. Tornado events over time (NOAA Storm Events, contiguous US)")
    fig.tight_layout(); fig.savefig(FIGS / "fig05_tornado_events.png", dpi=160); plt.close(fig)
    log.info("descriptives done:\n%s", t1.to_string())


if __name__ == "__main__":
    main()
