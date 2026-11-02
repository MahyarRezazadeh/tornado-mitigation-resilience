# Quality-control report: local build of 2026-10-13

Toolchain: MiKTeX pdfLaTeX + biber (biblatex-chicago). Sequence: pdflatex → biber → pdflatex → pdflatex.

| Check | Result |
|---|---|
| LaTeX errors | None |
| Undefined citations/references | None |
| Overfull boxes | None (Table 5 was 16pt too wide; fixed by narrowing and stacking the labels) |
| Missing characters / font substitutions | None reported |
| Figure paths | All 5 resolve (relative `figures/…`) |
| Numbering | Sections 1–6; equations (1)–(3); Tables 1–5, S1–S2; Figures 1–5 |
| Citations | 55 cited = 55 in the bib |
| Pages | 39: title 1, abstract 2, text 3–23, statements 22–23, references 24–28, tables 29–33, figures 34–36, appendix 37–39 |
| Main-text words | about 6,640 (sections 1–6) |
| Blinding (text) | No author names, affiliations, emails or acknowledgments |
| Blinding (metadata) | Author, Subject, Keywords and Producer empty; Creator "LaTeX"; no XMP; no file paths in the raw PDF; embedded figure PDFs carry only Matplotlib creator strings |
| Visual inspection | Title page, abstract, first text page, all 5 tables, all figure pages, references, and all appendix pages rendered and viewed |

## Remaining limitations of the PDF

- Red "Author input required" placeholders appear in the statements section. This is intentional: the PDF must not be submitted before they are resolved.
- Tables and figures come after the references, which is acceptable for review. Move them into the text if preferred.
- Tables 3 and 5 use `\footnotesize` with tighter column spacing; they remain legible at 100% zoom.
- The cover letter and author-information PDFs (`output/`) contain placeholders by design.
