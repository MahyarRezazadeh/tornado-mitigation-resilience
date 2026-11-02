# Revision log: *Risk Analysis* draft (2026-10-10) → JRAP editorial draft (2026-10-13)

Type: **E** = editorial (wording, structure, format); **S** = substantive (changes what a claim says, though no estimate changed).

## Empirical content that did NOT change

- All coefficients, standard errors, p-values, means, sample sizes, cluster counts and fixed-effects structures.
- All five tables and both appendix tables (numerically identical; see TABLE_FIGURE_VALIDATION.md).
- All five figures (byte-identical files).
- Equations (1)–(3), the sample definition, outcome definitions, controls, clustering and estimation software.
- All 55 references (no additions or removals; one entry type changed for the style driver).
- Supplementary Appendix S1–S4 (content kept; two clarifications listed below).

## Changes

| # | Where | What changed | Why | Type |
|---|---|---|---|---|
| 1 | Title | "…County Size and **Participation in Post-Disaster Hazard Mitigation**…" → "…County Size and **Access to Federal Hazard Mitigation Grants**…" | Signals the intergovernmental-grant framing JRAP expects; no causal claim (TITLE_OPTIONS.md) | E |
| 2 | Abstract | Rewritten: opens with grant delivery through local applications; adds the non-causal statement; "capacity … appears to shape" replaced by an association with county size | JRAP framing; removes an overstated claim (Audit D1) | S |
| 3 | Keywords | "hazard mitigation; HMGP; local government capacity; rural counties; tornadoes" → "intergovernmental grants; hazard mitigation; local government capacity; rural counties; regional disparities" | Regional-economics indexing; 5 keywords (JRAP: 3–5) | E |
| 4 | Front matter | JEL codes H77, H84, R50, Q54 added | Conventional for economics readers; optional | E |
| 5 | §1 | Reorganized: allocation tension → grant mechanics → fixed-cost intuition (stated as motivation, not a result) → evidence gaps → design → results → contributions → roadmap. "Contributes to risk analysis" → contributions to the regional economics of intergovernmental transfers. "In this journal" removed. | JRAP scope; Audit A1–A2 | S (framing) |
| 6 | §1 | The within-county result is described as "negative and imprecise; difference marginally significant" instead of "raises applications in larger counties but not in small ones" | Matches the estimates (Audit D2) | S |
| 7 | §2.1 | New paragraph on three features of HMGP as an intergovernmental grant (common pool per declaration, matching, claims only via local entities) | Economic intuition; uses only facts already in the source | E |
| 8 | §2.2 | Two literature subsections merged and tightened; all citations kept; a sentence on the political economy of declarations moved here | Concision; JRAP framing | E |
| 9 | §2.3 | H2: "local capacity" → "local conditions"; H3: "not purely mechanical" → "not solely a consequence of the number of eligible entities"; H4: "lower the cost of applying" → "lower the cost of participating" | DRRA reimburses post-award costs (Audit E1); avoids presupposing capacity | S (wording) |
| 10 | §3.2 | Sentence added: the outcomes measure access to funding, not completion or avoided losses | Audit K6 | E |
| 11 | §3.3 | Population described as a summary measure; counts of local governments described as institutional structure; finance variables as coarse proxies | Audit E2, K3 | E |
| 12 | §3.3 | Exposure definition: "in the incident year" → "in the calendar year in which the incident began"; path geometry described as in the code | Accurate description (Audit K2, J2); no change to the data | E (accuracy) |
| 13 | §3.3 | "Averaged across counties" added to the local-government count comparison, with a pointer to Table 1 for county–declaration means | Resolves an apparent text–table inconsistency (Audit J1) | E (accuracy) |
| 14 | §3.4–3.5 | The declaration-FE logic gets its own paragraph; §3.5 is retitled "What the Design Identifies" and adds that the applicant-count decomposition is descriptive | Audit K4 | E |
| 15 | §4 | Subsections reorganized around questions; the "mechanical" component is renamed "institutional structure" | Readability; Audit A3, B3 | E |
| 16 | §4.3 | Note added that decision rates rest mainly on recent records | Audit K1 | E |
| 17 | §4.4 | Fiscal panel: sentence added that spending measures do not capture expertise | Audit C1 | E |
| 18 | §4.4 | DRRA: "rule out reductions larger than roughly half of the baseline gap" → upper CI bound of about 5 pp; a full-gap narrowing not supported | Precision (Audit D4) | S (wording) |
| 19 | §4.5 | IA row: "estimates unchanged" → funded-project gap unchanged (−8.8), safe-room gap −4.3 | The source sentence misdescribed Table 5 (Audit F2) | S (accuracy) |
| 20 | §4.5 | Tornado-only row: garbled sentence rewritten ("too small to yield informative estimates") | Audit F3 | E |
| 21 | §5 | Split into four subsections (access to intergovernmental investment; relation to prior findings; grant design; limitations). Conclusions on capacity hedged ("consistent with … The data do not measure these costs"). | Audit D3, G1 | S (framing) |
| 22 | §5.4 | Limitations added: calendar-year exposure matching; possible censoring of late pending subapplications; observational decomposition; awards ≠ realized risk reduction | Audit K1–K6 | S (disclosure) |
| 23 | §6 | Rewritten around the lesson for intergovernmental grant delivery; "likely to require help … rather than money" softened; future causal work named | Audit D3 | S (framing) |
| 24 | Statements | Funding and conflict-of-interest placeholders added; data statement kept plus a DOI placeholder; AI disclosure kept verbatim plus one sentence on the JRAP revision and a red author-decision flag | JRAP policy; truthful disclosure | E |
| 25 | Appendix S4 | "incident year" → "calendar year in which the incident began"; path buffer described as half-width on each side, 10-yard minimum width | Matches the code (read-only check) | E (accuracy) |
| 26 | Tables | Rewrapped in threeparttable; values unchanged | Layout | E |
| 27 | Bibliography | APA → Chicago author–date (biblatex-chicago); `pyfixest` `@software` → `@misc` | JRAP published format; driver support | E |
| 28 | Layout | Line numbers kept; double spacing; tables and figures after the references; supplement appended | Review format; JRAP requires only a blinded PDF | E |

## Items that still require author verification

See `UNRESOLVED_ISSUES.md`.
