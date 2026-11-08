"""Claim-to-source map: every numeric claim in the manuscript text, its source, and an automatic check
against audit/results_numbers.json (or the named project file). Writes audit/claim_to_source_map.csv."""
from __future__ import annotations

import csv
import json
import pathlib

import pandas as pd

MS = pathlib.Path(__file__).resolve().parents[1]
N = json.loads((MS / "audit" / "results_numbers.json").read_text())
PROJ = MS.parent / "tornado_mitigation"
TEX = (MS / "risk_analysis_manuscript.tex").read_text(encoding="utf-8") + \
      (MS / "appendix" / "supplementary_material.tex").read_text(encoding="utf-8")


def g(path):
    v = N
    for k in path.split("."):
        v = v[k] if not isinstance(v, list) else v[int(k)]
    return v


T5 = {k: v for k, v in N.items() if k.startswith("T5_")}


def t5(prefix, y):
    return next(v for k, v in T5.items() if k.startswith("T5_" + prefix) and k.endswith("_" + y))


cv = pd.read_csv(PROJ / "output" / "tables" / "gap_causal_results.csv")
t4b = cv[(cv.test.str.contains("T4b")) & (cv.term == "sm_post_sr")].iloc[0]

# (claim text as it appears, location, computed value, displayed value, tolerance, source)
C = [
 ("12,081 county--declaration", "Abstract; 3.1", g("sample.county_declarations"), 12081, 0, "results_numbers.json:sample"),
 ("2,767 counties", "Abstract; 3.1", g("sample.counties"), 2767, 0, "sample"),
 ("736 declarations", "Abstract; 3.1", g("sample.disasters"), 736, 0, "sample"),
 ("49 states", "3.1", g("sample.states"), 49, 0, "sample"),
 ("at most 15,136 residents", "3.3", g("sample.small_pop_cutoff"), 15136, 0, "sample"),
 ("34.7\\%", "3.3", g("sample.share_small") * 100, 34.7, 0.05, "sample"),
 ("11.1\\%", "3.3", g("sample.share_hit") * 100, 11.1, 0.05, "sample"),
 ("14.6\\% of their county--declarations", "3.3", g("raw_rates.applied_small"), 14.6, 0.05, "raw_rates"),
 ("26.3\\% for larger", "3.3", g("raw_rates.applied_larger"), 26.3, 0.05, "raw_rates"),
 ("15.1\\% and 27.2\\%", "3.3", g("raw_rates.funded_small"), 15.1, 0.05, "raw_rates (larger 27.2)"),
 ("(8.4 versus 14.0 on average)", "3.3", g("govcounts.n_gp.1"), 8.4, 0.05, "govcounts"),
 ("special districts (6.9 versus 15.1)", "3.3", g("govcounts.n_sd.0"), 15.1, 0.05, "govcounts (small 6.9)"),
 ("school districts (2.2 versus 6.0)", "3.3", g("govcounts.n_sch.0"), 6.0, 0.05, "govcounts (small 2.2)"),
 ("8.8 percentage points less likely to obtain any HMGP project", "Abstract; 1; 4.2", -g("T2_dis_any_4.b"), 8.8, 0.05, "Table 2 B(4)"),
 ("larger-county mean: 27.1\\%", "Abstract", g("T2_dis_any_4.ref_mean"), 27.1, 0.05, "Table 2 B(4)"),
 ("half as likely to obtain a safe room", "Abstract; 1", g("T2_dis_strict_4.b") / g("T2_dis_strict_4.ref_mean"), -0.5, 0.01, "Table 2 C(4): b/mean"),
 ("About two-fifths of the gap", "Abstract; 4.2", 1 - g("T2_dis_any_5.b") / g("T2_dis_any_4.b"), 0.43, 0.02, "Table 2 B(5) vs B(4)"),
 ("gap of roughly one-fifth remains for applications by the county government", "Abstract", g("T3_applied_cgov.b") / g("T3_applied_cgov.ref_mean"), -0.21, 0.01, "Table 3 (3)"),
 ("11.4 percentage points less likely", "4.2", -g("T2_dis_any_1.b"), 11.4, 0.05, "Table 2 B(1)"),
 ("column 3, $-10.5$ percentage points", "4.2", g("T2_dis_any_3.b"), -10.5, 0.05, "Table 2 B(3)"),
 ("or 32\\% of the larger-county mean", "4.2", -g("T2_dis_any_4.b") / g("T2_dis_any_4.ref_mean") * 100, 32, 0.6, "Table 2 B(4)"),
 ("$-8.9$ percentage points on a mean of 26.1\\%", "4.2", g("T2_applied_4.b"), -8.9, 0.06, "Table 2 A(4)"),
 ("3.1 percentage points less likely to obtain a safe room", "4.2", -g("T2_dis_strict_4.b"), 3.1, 0.05, "Table 2 C(4)"),
 ("mean of 6.3\\%", "4.2", g("T2_dis_strict_4.ref_mean"), 6.3, 0.05, "Table 2 C(4)"),
 ("8.1 percentage points on a mean of 14.6\\%", "4.2", -t5("Baseline", "win3_strict")["b"], 8.1, 0.05, "Table 5"),
 ("35.5 percentage points lower in the smallest decile", "4.2", -g("deciles.dis_any.1"), 35.5, 0.05, "Table S2"),
 ("23.1 points lower in the fifth decile", "4.2", -g("deciles.dis_any.5"), 23.1, 0.05, "Table S2"),
 ("11.5 points lower in the ninth", "4.2", -g("deciles.dis_any.9"), 11.5, 0.05, "Table S2"),
 ("raises the probability of a funded project by 7.8 percentage points", "4.2", t5("Continuous", "dis_any")["b"], 7.8, 0.05, "Table 5"),
 ("falls from 8.8 to 5.0 percentage points", "4.2", -g("T2_dis_any_5.b"), 5.0, 0.05, "Table 2 B(5)"),
 ("subapplications from 8.9 to 5.4 points", "4.2", -g("T2_applied_5.b"), 5.4, 0.05, "Table 2 A(5)"),
 ("from 3.1 to 2.4 percentage points", "4.2", -g("T2_dis_strict_5.b"), 2.4, 0.05, "Table 2 C(5)"),
 ("leaving a gap of 38\\% of the larger-county mean", "4.2", -g("T2_dis_strict_5.b") / g("T2_dis_strict_5.ref_mean") * 100, 38, 0.6, "Table 2 C(5)"),
 ("14.3\\% in the smallest decile (median population 3,426)", "4.1", g("fig2_raw.1.applied"), 14.3, 0.05, "Figure 2a"),
 ("43.2\\% in the largest (median 413,325)", "4.1", g("fig2_raw.10.applied"), 43.2, 0.05, "Figure 2a"),
 ("5.4 percentage points less likely to file any subapplication", "4.3", -g("T3_applied.b"), 5.4, 0.05, "Table 3 (1)"),
 ("file about 4.7\\% fewer", "4.3", -g("T3_l_napp.b"), 4.7, 0.05, "Table 3 (2)"),
 ("(2,515 observations)", "4.3", g("T3_succ_rate.N"), 2515, 0, "Table 3 (4)"),
 ("$-0.5$ percentage points (95\\% confidence interval from $-4.2$ to $3.2$)", "4.3", g("T3_succ_rate.lo"), -4.2, 0.06, "Table 3 (4) CI"),
 ("on a mean of 86.6\\%", "4.3", g("T3_succ_rate.ref_mean"), 86.6, 0.05, "Table 3 (4)"),
 ("withdrawal rate by $-0.9$ points ($-4.4$ to $2.7$)", "4.3", g("T3_wd_rate.hi"), 2.7, 0.06, "Table 3 (5) CI"),
 ("The denial rate is 1.4 percentage points higher ($p = 0.03$)", "4.3", g("T3_den_rate.b"), 1.4, 0.05, "Table 3 (6)"),
 ("from a low base of 1.7\\%", "4.3", g("T3_den_rate.ref_mean"), 1.7, 0.05, "Table 3 (6)"),
 ("2.4 percentage points less likely to file an HMGP subapplication under a declaration, on a mean of 11.1\\%", "4.3", g("T3_applied_cgov.ref_mean"), 11.1, 0.05, "Table 3 (3)"),
 ("2.4 points less likely to receive a project, on a mean of 11.4\\%", "4.3", g("T3_f_county_gov.ref_mean"), 11.4, 0.05, "Table 3 (7)"),
 ("raises the number of subapplications by 4.3\\% ($p = 0.02$)", "4.4", g("T4_E_l_napp.b"), 4.3, 0.05, "Table 4A"),
 ("by 2.4 percentage points ($p = 0.045$)", "4.4", g("T4_E_applied_cgov.p"), 0.045, 0.0015, "Table 4A"),
 ("responses are $-2.9\\%$ and $-1.8$ points", "4.4", g("fig4_l_napp.small_b"), -2.9, 0.05, "Figure 4"),
 ("are $-7.2\\%$ ($p = 0.046$)", "4.4", g("T4_E_small_l_napp.b"), -7.2, 0.05, "Table 4A"),
 ("$-4.2$ points ($p = 0.06$)", "4.4", g("T4_E_small_applied_cgov.p"), 0.06, 0.005, "Table 4A"),
 ("($0.35$ points per log unit for larger county governments, $p = 0.02$", "4.4", g("T4_lpe_applied_cgov.b"), 0.35, 0.005, "Table 4A"),
 ("interaction $-0.60$, $p = 0.05$", "4.4", g("T4_lpe_small_applied_cgov.b"), -0.60, 0.005, "Table 4A"),
 ("imprecise ($p = 0.23$ and $p = 0.16$)", "4.4", g("T4_E_small_dis_any.p"), 0.16, 0.005, "Table 4A (applied p=0.227)"),
 ("leaves the gap in subapplications at 5.4 percentage points", "4.4", -g("T4_small_applied.b"), 5.4, 0.05, "Table 4B"),
 ("(interaction $-0.5$ points, standard error 1.6)", "4.4", g("T4_sm_lowadmin_applied.b"), -0.5, 0.05, "Table 4B"),
 ("filed by state agencies before 2009 (mean 18.5\\%)", "4.4", g("state_shares.sh_state_mean") * 100, 18.5, 0.05, "state_shares"),
 ("2.6 percentage point smaller gap in subapplications ($p = 0.04$)", "4.4", g("T4_sm_z_sh_state_applied.b"), 2.6, 0.05, "Table 4C"),
 ("3.0 point smaller gap in funded projects ($p = 0.02$)", "4.4", g("T4_sm_z_sh_state_dis_any.b"), 3.0, 0.05, "Table 4C"),
 ("gap in subapplications was 16.2 percentage points", "4.4", g("drra_raw.0.0") - g("drra_raw.1.0"), 16.2, 0.05, "drra_raw (larger pre 31.0, small pre 14.8)"),
 ("and 12.4 points afterward", "4.4", g("drra_raw.0.1") - g("drra_raw.1.1"), 12.4, 0.05, "drra_raw"),
 ("change is $-1.9$ percentage points (standard error 3.6)", "4.4", g("T4_sm_post_applied.b"), -1.9, 0.05, "Table 4D"),
 ("$-1.7$ points (3.6) for funded projects", "4.4", g("T4_sm_post_dis_any.b"), -1.7, 0.05, "Table 4D"),
 ("(smallest $p = 0.14$)", "4.4", g("drra_event_min_p.dis_any"), 0.14, 0.005, "Figure 5"),
 ("rule out reductions larger than roughly half of the baseline gap", "4.4", g("T4_sm_post_applied.b") + 1.96 * g("T4_sm_post_applied.se"), 5.2, 0.1, "upper 95% bound of Table 4D(1) vs adjusted gap ~9-11 pp"),
 ("enlarges the gap to 14.3 percentage points on a mean of 33.8\\%", "4.5", -t5("Hit-only", "dis_any")["b"], 14.3, 0.05, "Table 5"),
 ("9.2 points for safe rooms and retrofits on a mean of 14.5\\%", "4.5", -t5("Hit-only", "dis_strict")["b"], 9.2, 0.05, "Table 5"),
 ("gaps between 8.4 and 9.4 percentage points", "4.5", -g("T5_loso.dis_any.1"), 8.4, 0.05, "Table 5 LOSO"),
 ("between 2.7 and 3.5 points", "4.5", -g("T5_loso.dis_strict.0"), 3.5, 0.05, "Table 5 LOSO"),
 ("10.5 points on a mean of 19.7\\%", "4.5", -t5("Five-year", "win5_strict")["b"], 10.5, 0.05, "Table 5"),
 ("nearly disappears ($-0.9$ points)", "4.5", t5("Credit statewide", "dis_any_sw")["b"], -0.9, 0.05, "Table 5"),
 ("about 89\\% of larger counties", "4.5", t5("Credit statewide", "dis_any_sw")["ref_mean"], 88.6, 0.05, "Table 5 bracket (88.6, larger counties)"),
 ("($-2.8$ points on a mean of 9.9\\%)", "4.5", t5("Credit statewide", "dis_strict_sw")["b"], -2.8, 0.05, "Table 5"),
 ("($-1.5$ points, standard error 4.0)", "4.5", t5("Declarations with incide", "dis_any")["b"], -1.5, 0.05, "Table 5"),
 ("Among the 361 county--declarations", "4.5", t5("Declarations with incide", "dis_any")["N"], 361, 0, "Table 5"),
 ("(47 clusters)", "3.5", t5("Standard errors", "dis_any")["clusters"], 47, 0, "Table 5"),
 ("leaving 12,038 observations", "3.5", g("T2_dis_any_2.N"), 12038, 0, "Table 2"),
 ("0.73 percentage points (county-clustered standard error 2.95", "S3", t4b.b * 100, 0.73, 0.005, "project gap_causal_results.csv (52)"),
 ("9,856 stacked observations", "S3", t4b.N, 9856, 0, "gap_causal_results.csv"),
 ("Of 32,607 linked county--subapplication records", "S4", g("subapps.linked_rows"), 32607, 0, "subapps"),
 ("4,287 pending or submitted", "S4", g("subapps.status_counts.Pending") + g("subapps.status_counts.Submitted to FEMA"), 4287, 0, "subapps"),
 ("nonmetropolitan counties are about three percentage points less likely", "S1", g("controls_col4.dis_any.nonmetro"), -3.5, 0.6, "Table S1"),
 ("one fewer case out of every ten county--declarations", "Conclusion", -g("T2_dis_any_4.b") / 10, 0.88, 0.02, "Table 2 B(4)"),
]
EXT = [
 ("correlated at 0.92", "3.2", "tornado_mitigation/output/logs/51_gap_mechanisms.log: 'corr 0.920'"),
 ("\\$22.4 billion", "1", "Horn (2022) CRS R46989 cover summary"),
 ("86\\% of small counties", "4.5", "tornado_mitigation/output/logs/50_small_county_robustness.log raw means: dis_any_sw small 0.861"),
 ("up to 15\\% of the first \\$2 billion", "2.1", "Horn (2022) CRS R46989"),
 ("about 80\\% of FEMA's Hazard Mitigation Assistance spending", "2.1", "Frimpong et al. (2023), Sec. 4"),
 ("29\\% of the funding they requested", "2.2", "Smith (n.d.), Headwaters Economics web page"),
 ("25\\% nonfederal", "1", "Frimpong et al. (2023), Sec. 1; Horn (2022)"),
 ("up to 5\\% of their subaward", "2.1", "FEMA Section 1215 management costs page; FEMA HMGP management cost guidance (see audit note)"),
 ("August 1, 2017", "2.1; 3.4", "FEMA interim policy FP 104-11-1 (archived page) via web search; flagged for author verification"),
]
rows, bad = [], 0
for claim, loc, val, shown, tol, src in C:
    ok = abs(float(val) - float(shown)) <= tol + 1e-9
    present = claim.split(" (")[0][:40] in TEX
    bad += (not ok) or (not present)
    rows.append({"claim_text": claim, "location": loc, "displayed": shown, "computed": round(float(val), 4),
                 "matches_within_rounding": ok, "text_found_in_tex": present, "source": src})
for claim, loc, src in EXT:
    rows.append({"claim_text": claim, "location": loc, "displayed": "", "computed": "", "matches_within_rounding": "external",
                 "text_found_in_tex": claim[:30] in TEX, "source": src})
with open(MS / "audit" / "claim_to_source_map.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print(f"{len(C)} computed claims checked; problems: {bad}")
for r in rows:
    if r["matches_within_rounding"] is False or r["text_found_in_tex"] is False:
        print("CHECK:", r)

