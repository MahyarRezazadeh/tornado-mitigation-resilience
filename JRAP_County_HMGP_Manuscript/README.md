# JRAP_County_HMGP_Manuscript

Editorial draft of "Declared but Not Applied: County Size and Access to Federal Hazard Mitigation Grants after Tornadoes and Severe Storms", prepared for the *Journal of Regional Analysis & Policy* (Research Article). It is revised from the 2026-10-10 *Risk Analysis* draft in `../manuscript_risk_analysis/`.

**Status: editorial draft, NOT ready for submission.** JRAP's AI policy may make the paper ineligible. See `submission/AI_POLICY_COMPLIANCE.md`.

## Build

```
pdflatex main
biber main
pdflatex main
pdflatex main
```

On Overleaf, set the compiler to pdfLaTeX and the main document to `main.tex`; biber runs automatically.

## Layout

| Path | Content |
|---|---|
| `main.tex`, `preamble.tex` | Blinded manuscript |
| `sections/00–07` | Abstract, six sections, statements |
| `tables/table1–5.tex` | Main tables (values identical to the source) |
| `figures/` | Original vector figures and `figures.tex` (captions) |
| `appendix/` | Supplementary Appendix S1–S4 and Tables S1–S2 |
| `references.bib` | 55 entries, Chicago author–date via biblatex-chicago |
| `submission/` | Cover letter, author information page, compliance checklist, AI-policy assessment, editor inquiry draft |
| `reports/` | Journal requirements, audit, style report, title options, table/figure validation, changelog, unresolved issues, QC report, literature for author review, `verify_numbers.py`, `convert_tables.py` |
| `output/` | Compiled `main.pdf`, `cover_letter.pdf`, `author_information.pdf` |
| `source_snapshot/` | Read-only copy of the source tex, tables and PDF used for validation (not uploaded to Overleaf) |

Run `python reports/verify_numbers.py` to recheck the table values, prose numbers and citations against the source.
