# Manuscript audit: source *Risk Analysis* draft → JRAP

Source: `source_snapshot/risk_analysis_manuscript.tex` and the PDF built from it (`risk_analysis_manuscript_latest.pdf`, 2026-10-10), with Tables 1–5, Figures 1–5 and Supporting Information S1–S4.

The source's code and data were opened read-only, only to check how the manuscript describes them. Nothing was re-estimated.

Severity: **H** = could change a reader's or referee's conclusion; **M** = a referee will likely raise it; **L** = presentation.

## Inventory

- **Sample:** 12,081 county–declarations; 2,767 counties; 736 declarations; 49 states; 1999–2021. 12,038 observations in the declaration-FE models (singletons dropped); 2,762 county clusters; 47 state clusters.
- **Equations:** (1) baseline with declaration FE; (2) county + declaration FE with a hit × small interaction; (3) DRRA Small × Post with county + declaration FE, 2010–2021.
- **Tables:** 1 summary statistics; 2 baseline gap, 5 columns × 3 panels; 3 pipeline, 7 columns; 4 mechanisms, 4 panels × 4 outcomes; 5 robustness, 10 rows × 3 outcomes; S1 all coefficients; S2 decile gradient.
- **Figures:** 1 maps; 2 decile gradient (raw and adjusted); 3 pipeline coefficients; 4 within-county hit response; 5 DRRA event study.
- **Citations:** 55 bib entries, all cited, and all citations resolve.
- **Estimation choices:** LPM by OLS (PyFixest); county-clustered SEs, with state clustering as a robustness check; small = bottom population tercile (≤15,136); hazard controls from SPC geometry; damage from NOAA Storm Events.
- **Stated limitations:** county size not assigned; coarse capacity proxies; subapplication linkage for older closed/denied records; low power of within-county and reform tests; scope limited to HMGP after tornado/severe-storm declarations; outcomes are awards, not completed projects or avoided losses.

## A. Weaknesses in the regional-economics framing

1. **(H)** The source is framed for *Risk Analysis*: "contributes to risk analysis", "a recurring concern in this journal" (twice), and a protective-action-decision literature opening. JRAP's About page says it "aggressively desk reject[s] articles that are not clearly building off of the regional science/regional economics literature." *Revised:* the paper is now framed as a study of geographic access to intergovernmental public investment (a matching grant delivered through a state intermediary, with fixed application costs and local government structure), and the journal-specific phrases are removed. **Unresolved:** the reference list still contains almost no regional-economics or fiscal-federalism journals. No literature was added (the brief prohibits AI literature research). Candidate areas are listed in `LITERATURE_FOR_AUTHOR_REVIEW.md` for the authors to check and decide on.
2. **(M)** The economic intuition for fixed application costs appeared in one sentence. *Revised:* the introduction explains it in plain terms, and the text says explicitly that it motivates the analysis but is not tested.
3. **(M)** The number of local governments was described as a "mechanical" channel. In regional and public economics this is better described as local *institutional structure* (fragmentation). *Revised wording;* the estimates are unchanged.

## B. Overly long or repetitive passages

1. **(L)** The introduction's results paragraph largely repeated the abstract. It has been rewritten so the abstract and introduction no longer repeat each other sentence by sentence.
2. **(L)** The planning literature on the Community Rating System (four citations in a chain) is not central to a JRAP reader. It has been condensed but all citations are retained, as instructed.
3. **(L)** Results subsections walked through table columns. They are now organized around questions (how large, how much is structural, at which stage, why).

## C. Unclear economic intuition

1. **(M)** Why per-resident administrative spending is *higher* in small counties (spreading fixed operating costs over fewer residents) was stated but not tied to the conclusion that per-resident fiscal proxies cannot measure expertise. *Revised:* the text now draws this connection.

## D. Overstated causal claims

1. **(H)** Abstract (source): "Local capacity to apply, rather than need or federal screening, appears to shape where mitigation dollars go." Capacity is never measured directly (see E2). *Revised:* the abstract describes associations with county size and states the non-causal interpretation.
2. **(M)** Abstract and conclusion: "a tornado hit raises applications in larger counties but not in small ones." The small-county response (−2.9 percent, SE 3.14 per `results_numbers.json`) is imprecise, and the difference has p = 0.046 / 0.06. *Revised:* "negative and imprecise; the difference … marginally significant."
3. **(M)** Conclusion (source): "closing the gap is likely to require help in preparing applications rather than additional money after an award." This rests on a null with a wide CI plus a cross-state association. *Revised:* "suggest … a more promising policy margin." Policy options are explicitly not evaluated.
4. **(M)** DRRA (source): "rule out reductions larger than roughly half of the baseline gap." The upper 95% bound is −1.92 + 1.96×3.61 = 5.16 pp, against a column-4 gap of 8.85 pp (58%) or a column-5 gap of 5.37 pp (96%). "Half" depends on the benchmark chosen. *Revised:* "the upper end of the 95 percent confidence interval … corresponds to a narrowing of about 5 percentage points … a narrowing of the size of the full baseline gap is not supported." This is derived arithmetic, recorded in TABLE_FIGURE_VALIDATION.md.

## E. Unclear mechanisms

1. **(M)** H4 bundles "lower the cost of applying" with a DRRA test, but DRRA §1215 reimburses *management costs of a subaward*, which are post-award. The source's discussion recognizes this, but the hypothesis wording does not. *Revised:* H4 now reads "lower the cost of participating." **Author to verify** whether §1215 management costs can cover any pre-award (application-development) activity for HMGP subrecipients. If they can, the interpretation in §5.1 needs adjusting.
2. **(H)** **Population vs. capacity.** "Small" is a population tercile, and population bundles applicant counts, staff, tax base, rurality and exposure. The source acknowledges this in §3.5 but the abstract and conclusion slide into "capacity." *Revised:* §3.3 states that population is the dimension along which the gap is *described*, and the text keeps "capacity" for the interpretive discussion.

## F. Statements not supported by the evidence shown

1. **(M)** "Tornado safe rooms and wind retrofits are a large share of HMGP construction" (Introduction). No source or number is given. Retained, but **author to support** with a figure (e.g. from `03_classify_fema_projects.py` output) or soften it.
2. **(L)** "Limiting the sample to declarations that included Individual Assistance leaves the estimates unchanged." Table 5 shows −8.81 (unchanged) for any project, but −4.34 vs −3.14 for safe rooms. *Corrected to describe Table 5 accurately* (editorial accuracy fix; no number changed).
3. **(L)** "this subsample is too small to distinguish the main estimate from zero" (tornado-only row) is garbled. Rewritten as "too small to yield informative estimates."

## G. Missing links from results to policy

1. **(M)** The policy paragraph listed options without connecting them to the structure of intergovernmental grant delivery. *Revised:* §5.3 relates the implications to how place-based grants are delivered (local application vs. state preparation) and states that the options are not evaluated.

## H. Formatting differences from JRAP

| Source (Risk Analysis style) | JRAP draft |
|---|---|
| APA 7 (biblatex-apa) | Chicago author–date. JRAP's published format; no style is mandated for initial submission. |
| Upper-case section titles, numbered | Numbered sentence-case headings |
| "Supporting Information S1–S4" | "Supplementary Appendix S1–S4" (same content) |
| No funding statement | Funding, conflict-of-interest, data/code and AI statements (JRAP lists the first three as recommended and requires the AI disclosure) |
| No JEL codes | JEL H77, H84, R50, Q54 added. Optional, editorial choice; remove if not wanted. |

## I. Citation–bibliography consistency

- All 55 keys are cited and all citations resolve (`verify_numbers.py` §3).
- `pyfixest` changed from `@software` to `@misc`, because biblatex-chicago has no `software` driver. The content is unchanged.
- **Author to verify:** `smith2025rural` has year 2025 but volume 86 (2), which may be a 2026 issue; `headwaters_nd` has no date (renders "n.d."); `fema1215mgmtcosts` is dated 2023 with access date 2026-10-09; `abadie2023cluster` and `howell2019damages` give authors' middle initials without periods (Crossref form).

## J. Numerical and factual inconsistencies

1. **(M)** **Local-government counts.** Source text: "8.4 versus 14.0", "6.9 versus 15.1", "2.2 versus 6.0". Source Table 1: 9.8 / 13.9, 7.5 / 14.6, 2.3 / 6.2. The cause, from `make_tables_figures.py` line 607 (read-only): the text figures are means across *unique counties*, while Table 1 averages across *county–declarations*. Both are correct, but the source never said so. *Revised:* the text says "Averaged across counties" and points to Table 1 for the county–declaration means. No number changed.
2. **(L)** **Path-width description.** Source main text: "widened by the reported path width plus 500 meters". Source S4: "buffered by half the reported path width". Per `44_spc_exposure.py` (read-only), a line is buffered by W/2 (total width = reported width, 10-yard floor), then by 500 m. *Revised:* both passages now say this unambiguously.
3. **(L)** Table 5's IA row: see F2.
4. **(L)** 49 states in the sample vs. 47 state clusters in the FE models. Plausibly due to singletons or missing covariates, but not explained. **Author to confirm.**
5. **(L)** Table 1 shows any funded project (23.0%) above any subapplication (22.2%), so some funded projects have no linked subapplication. This is consistent with the linkage gap (J/K1) but should be stated. **Author to confirm and add a sentence.**

## K. The six issues the brief asked about specifically

1. **Historical coverage of the subapplication data (H).** S4 reports that few closed or not-approved/denied records carry benefiting counties, and that only 330 "not approved" records were linked. The approval/denial comparison (Table 3, columns 4–6) therefore rests mostly on recent records and may understate denials, especially for earlier years. The draft states this in §4.3 and §5.4. Suggested follow-up from the source's own task list: recover links through project identifiers and re-estimate on the linkable universe. **Not done; requires new analysis.**
2. **Exposure matched to the declaration or to the calendar year? (H).** Confirmed from `50_small_county_robustness.py` (read-only; merge on `county_fips, year`, with year = incident begin year): **the hit indicator, residents in paths, track length, EF and casualties refer to the calendar year in which the incident began, not to the incident period.** A tornado from another event in the same year, before or after the declared incident, can make a county–declaration count as "hit." This measurement error is probably non-classical: counties with multiple declarations per year are affected more. It applies to Eq. (1) controls and especially to Eq. (2), where H is the treatment. The source called this "the incident year" without flagging it. *Revised:* the definition now says "calendar year in which the incident began", and §5.4 lists it as a limitation. **The estimates are unchanged; re-matching to incident dates would be new analysis.**
3. **County population vs. measured capacity (H).** See E2. The draft keeps the distinction explicit throughout.
4. **The applicant-count decomposition is observational (M).** Adding log counts is a conditional comparison, not a counterfactual. The counts are correlated with population, and the "two-fifths" share depends on functional form (log counts) and on which controls come first. *Revised:* §3.5 and §4.2 say the decomposition "statistically accounts for" part of the gap and does not show what would happen if the counts changed.
5. **Precision of the reform estimates (M).** SE 3.6 on a gap of about 5–9 pp; the event study has smallest p = 0.14; the placebo is −4.14 (SE 3.92), which is itself not small. *Revised:* see D4. Multiple-testing note: Table 4 has 4 panels × 4 outcomes, and the source's task list (#7) suggests pre-specified primary outcomes or sharpened q-values. **Not done.**
6. **Funding obtained vs. completed mitigation or avoided losses (M).** Outcomes are subapplications and funded projects (obligations), not completion, and not avoided losses. *Revised:* this is stated in §3.2 ("These outcomes measure access to funding…") and in §5.4.

## L. Other points a referee may raise (not fixed; author judgment)

- Damage and casualty controls in Eq. (1) may themselves depend on county size through reporting practices, a possible bad-control problem. Columns 2 vs 3 show only a small change.
- Hit-only sample N = 1,203, while 11.1% of 12,081 is about 1,341. The difference is presumably singletons; confirm.
- The year in which "baseline population" is measured is not stated in the text. **Author to state it.**
- Declarations from 2019–2021 may have pending subapplications that are censored (source task #9). A sentence was added to the limitations; the robustness check itself was not run.
