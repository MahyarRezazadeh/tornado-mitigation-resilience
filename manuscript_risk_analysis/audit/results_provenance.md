# Results provenance

This file records which project results the manuscript uses, where they come from, and why they are the valid and current estimates. File dates alone were not used to decide this.

## Project and research question

- **Project:** "Tornedo", in `Desktop/Tornedo/tornado_mitigation/`.
- **Original question (2026-10-07/08):** do FEMA tornado and wind mitigation projects improve county labor and business resilience after later tornadoes?
  - Result: GO WITH REDESIGN. Labor-market effects were null or underpowered, and the damage signal failed its placebo test (`output/final/research_assessment.md`).
- **Redesign (2026-10-09), script 43–48:** SPC tornado-track exposure plus land productivity.
  - No robust return to mitigation spending was found (`output/final/redesign_results.md`). These results are **not** used in the manuscript.
- **Allocation analysis (2026-10-09), script 49:** found the small-county conversion gap.
- **Latest line of work, used in the manuscript:**
  - script 50: robustness (`output/final/small_county_gap_robustness.md`);
  - script 51: mechanisms (`output/final/small_county_gap_mechanisms.md`);
  - script 52: causal-story tests (`output/final/small_county_gap_causal_tests.md`).

## Design used in the manuscript

| Item | Definition | Source |
|---|---|---|
| Research question | Whether, and at which stage, small counties fall behind in turning tornado and severe-storm declarations into funded HMGP mitigation | scripts 49–52 |
| Policy | FEMA Hazard Mitigation Grant Program (HMGP), post-disaster | OpenFEMA |
| Geographic unit | County | — |
| Observation | County × major disaster declaration (DR, Tornado/Severe Storm, county-designated, incident 1999–2021) | `50_small_county_robustness.py::county_disasters` |
| Small county | Bottom third of U.S. counties by baseline population (≤ 15,136 residents) | `50::build` (`pop_pct <= 1/3`) |
| Gap | Coefficient on Small with declaration FE (Eq. 1) | `make_tables_figures.py` |
| Outcomes | applied, l_napp, applied_cgov, dis_any, dis_strict, win3/5_strict, succ/wd/den rates, f_county_gov, dis_any_sw / dis_strict_sw | `50::build`, `51::main` |
| Preferred specification | Declaration FE + hazard (E, lpe, track_km, mag, cas, ldmg, ldmg_pc) + demographics (linc, pov_rate, nonwhite, nonmetro) [Table 2 col 4]; + local-government counts [col 5] | identical to scripts 50/51 |
| Identifying variation | Cross-county comparison within declaration (descriptive about size); within-county across declarations (Eq. 2); DRRA §1215 date (Eq. 3) | 52 |
| Inference | County-clustered SEs; state clustering as robustness | — |

## Reproduction chain

1. `tornado_mitigation/src/43–44` build the SPC exposure, written to `data/processed/spc_exposure_cy.parquet` and `spc_tracks.parquet`.
2. `46_redesign_analysis.py::build_panel` assembles the county-year covariates that script 50 uses.
3. `50_small_county_robustness.py::build` constructs the county × declaration panel and the project linkage.
4. `51_gap_mechanisms.py` adds Census of Governments counts, applicant types and subapplication linkage. It saves `data/processed/gap_county_disaster.parquet` and `gap_subapps_linked.parquet`.
5. `52_gap_causal_tests.py` provides `finance()`, `state_intermediaries()` and `decl_dates()`. Its output `output/tables/gap_causal_results.csv` supplies Appendix S3.
6. `manuscript_risk_analysis/scripts/make_tables_figures.py` re-estimates every number in the manuscript from the saved panel. It writes the tables, the figures and `audit/results_numbers.json`.
7. `scripts/check_claims.py` checks 82 numeric claims in the text against `results_numbers.json` and writes `claim_to_source_map.csv`. **0 mismatches.**

## Consistency checks against the earlier logs

The manuscript script reproduces the earlier estimates exactly:
- Table 2 ladder for any funded project: −11.43 / −11.25 / −10.51 / −8.79 pp, matching the script 50 log (−11.43, −11.25, −10.51, −8.79).
- Leave-one-state-out range for funded projects: −9.37 to −8.43, matching script 50.
- Table 4 estimates: identical to the script 52 log (e.g. hit × small on log number of subapplications: −7.23, p = 0.046).

**Specification note.** In Table 3 every column, including the subapplication-level size and BCR regressions, uses the column 5 specification, which adds local-government counts.
- Script 51 had run the subapplication-level regressions without local-government counts and found log requested amount −0.185 (p = 0.03).
- With counts added, the estimate is −0.102 (p = 0.28).
- The manuscript reports the with-counts version and describes the difference as not significant. That is the conservative choice.

## Not used / superseded

- Labor and business outcomes, damage outcomes and land-productivity outcomes from the original and redesign analyses: a different question, with null or non-robust results.
- Script 49's stage-2 estimate (−9.7 pp from 13.7%): it used county-year units and state × year FE. It is superseded by the county × declaration design of scripts 50–52.
- The 3% low-capacity BRIC statistic seen in news coverage: not verified against the primary source, so not used.
