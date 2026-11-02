# Manuscript quality check (2026-10-10)

| # | Check | Result |
|---|---|---|
| 1 | Compiles to PDF | Yes. pdflatex → biber → pdflatex ×2 (latexmk unavailable: MiKTeX has no Perl). No LaTeX errors. |
| 2 | Compilation errors resolved | Yes. Fixed a `\Bbbk` clash (amssymb vs newtxmath) by removing amssymb. |
| 3 | Missing citations | None. 55 cited = 55 in bib; biber reports no warnings. |
| 4 | Broken figure and table references | None. No "undefined" warnings in the final log. |
| 5 | Figures render | Yes. All 5 checked as rendered images (`audit/preview_figure_*.png`, `page_figs.png`). Legend overlaps in Figs 3–5 were fixed. |
| 6 | Tables within margins | Yes. 0 overfull hboxes in the final log; tables are wrapped in a shrink-only adjustbox. |
| 7 | Layout and readability | Pages 3, 25, 27 and 28, the reference page and the figure page were inspected as rendered images. |
| 8 | Abstract ≤ 250 words | 248 words (counted from both the LaTeX source and the PDF text). |
| 9 | Main text < 7,000 words | 5,806 words (PDF text, Introduction through Conclusion, citations expanded, line numbers removed); 5,484 from source excluding citation commands. |
| 10 | Numeric claims match source | 82 computed claims checked automatically, 0 mismatches (`claim_to_source_map.csv`); 9 external claims mapped to documents and logs. |
| 11 | Coherent argument | Intro (problem → gap → question → design → findings) → institutions/literature → H1–H4 → data/specification → results in hypothesis order → discussion → conclusion. Each hypothesis is answered in Sec. 4 and revisited in Sec. 5. |
| 12 | Generic language removed | Scanned for the banned phrases ("important to note", "sheds light", "delve", "nuanced", "underscore", "multifaceted", "valuable insights", "crucial", "pivotal", "landscape"): none. "Robust" appears once, in its statistical sense. |
| 13 | Mechanisms not overstated | Capacity is described as "consistent with", "fits", "suggestive". The text says size is not randomly assigned. The DRRA null is described with its CI, and no p ≈ 0.05 result is called conclusive. |
| 14 | Nothing invented | Every coefficient is re-estimated by `make_tables_figures.py` from the project panel. No robustness test is reported that was not run. Unread sources are cited only at the level of their abstracts (see literature matrix). |
| 15 | PDF saved in project | `manuscript_risk_analysis/risk_analysis_manuscript.pdf`, and a copy at `Tornedo/risk_analysis_manuscript_latest.pdf`. |
| 16 | Reflects the latest small-county findings | Yes: scripts 50–52 (2026-10-09); see `results_provenance.md`. |
| 17 | All main-text figures and tables cited and explained | Tables 1–5 and Figures 1–5 are each introduced and interpreted in Sec. 3.3/4.x; Tables S1–S2 in the appendix. |
| 18 | Anonymity | No author names or affiliations in the text or PDF metadata; title-only first page. Funding, acknowledgments and COI are left as placeholders. |

## Unresolved issues for author review

1. **AI disclosure.** The draft statement must be reviewed against Wiley's policy (see `remaining_research_tasks.md`).
2. **Reference style.** APA 7, inferred from recent Risk Analysis articles; confirm.
3. **DRRA §1215 applicability date.** 1 Aug 2017; confirm against the FEMA HMGP policy text.
4. **Subapplication linkage gap.** Older closed and denied records are sparsely linked; this is disclosed in Sec. 5 and Appendix S4.
5. **Table 4 outcomes.** They are related (applied, number, county-government applied, funded); interpret individual p-values with that in mind.
6. **Line numbers.** Added on main-text pages for reviewers; remove if the editorial office prefers.
