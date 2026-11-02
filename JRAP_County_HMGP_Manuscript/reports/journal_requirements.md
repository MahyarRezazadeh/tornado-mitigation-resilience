# JRAP requirements: verified 2026-10-13

Official sources, read in the browser on 2026-10-13. The Scholastica pages render with JavaScript, so a plain HTTP fetch returns only the page title.

- Guide for Authors: https://jrap.scholasticahq.com/for-authors
- About: https://jrap.scholasticahq.com/about
- MCRSA journal page: https://www.mcrsa.org/journal-of-regional-analysis-and-policy/
- LaTeX template (linked from the Guide for Authors): https://www.overleaf.com/read/nzzsqrjvtkps#8e6dc8

"Verified" below means the requirement is stated on one of these pages. "Not stated" means none of these pages addresses it. Where a page is silent, no rule is assumed.

| # | Item | Requirement | Source | Status |
|---|---|---|---|---|
| 1 | Scope | Publishes "regional science/regional economics manuscripts that are theory-based, empirically sound, and policy-relevant." The About page adds that the journal "aggressively desk reject[s] articles that are not clearly building off of the regional science/regional economics literature." | For Authors; About | Verified. **The second point is the main editorial risk for this paper (see MANUSCRIPT_AUDIT.md §A).** |
| 2 | Submission types | Research article; Research Letter (<2,500 words including tables, figures and references); Economic Impact Analysis Summary (<2,500 words, ≤2 tables, 1 figure) | For Authors | Verified. This paper is a **Research Article**. |
| 3 | Length | Research articles have no word limit; no more than 8,000 words recommended | For Authors | Verified. The draft's main text is about 6,600 words (sections 1–6; `reports/verify_numbers.py`). |
| 4 | Abstract and keywords | A title page is *optional*. If included, it gives title, abstract, 3–5 keywords and author details. There is no stated abstract word limit. | For Authors | Verified. The draft has a 264-word abstract and 5 keywords. |
| 5 | Initial format | "All we require for an initial submission is a .pdf with no identifying information." All submissions must be PDFs. | For Authors | Verified |
| 6 | Review and anonymization | Double-blind peer review. "The manuscript file and file properties should not contain identifying information." | For Authors; About; MCRSA | Verified. The PDF metadata was checked (see QC_REPORT.md). |
| 7 | Figures, tables, supplements | No specific rules for research articles | — | Not stated. Tables and figures follow the text, and the supplement is appended to the same PDF. |
| 8 | Reference style | No style stated for initial submission. JRAP's published citation format is author–date, e.g. "Hicks, Michael J. 2024. 'Federal Fiscal Exposure of US Counties.' *Journal of Regional Analysis & Policy* 54 (2): 36–48." (article page) | Article page 127868 | Style not stated. The draft uses Chicago author–date (biblatex-chicago), which matches the published format. |
| 9 | Cover letter | Required with every submission. It must state the submission type, and may name up to two potential reviewers. Submissions without one are returned. | For Authors | Verified. Draft in `submission/cover_letter.tex`. |
| 10 | Funding, COI, data | "Other Recommended Statements": funding (sources, grant numbers), conflict of interest, and data and code availability | For Authors | Verified as *recommended*. Placeholders are in the draft. |
| 11 | AI | Disclosure is required. AI is allowed only to improve writing quality, and AI may not be an author. "AI in other parts of the research process are not permissible and evidence of use of AI in other parts of the research process will be cause for rejection." | For Authors | Verified. **There is a conflict; see AI_POLICY_COMPLIANCE.md.** |
| 12 | LaTeX and Overleaf | After acceptance, authors receive final formatting guidelines, "including using Overleaf to put their paper into LaTeX to generate their proof," and a template is linked. | For Authors | Verified. The template applies at the **production** stage. It was not opened, because opening it requires your Overleaf account to join the shared project, which shows your name and email to its editors. Initial submission needs only a PDF, so the draft uses a clean review layout. |
| 13 | Fees | "$25 submission fee for all manuscripts, with no refund if the manuscript is desk-rejected." | For Authors | Verified. Article processing charges are not stated. The journal is open access as a service to MCRSA members (MCRSA page). |
| — | Process | The editor screens for suitability, typically within 48 hours; manuscripts then go to two reviewers, aiming for a first decision within two months | For Authors | Verified |
| — | Editor | The About page lists Joshua C. Hall (2018–present). The MCRSA page lists Amir Borges Ferreira Neto as Editor-in-Chief (2026–present). | About; MCRSA | **The sources disagree.** The cover letter is addressed to "Editor-in-Chief" without a name. |

## Requirements the user's brief anticipated, checked against the official pages

- "~8,000 words recommended": confirmed.
- "Initial submission is a blinded PDF": confirmed.
- "Cover letter identifying the article type is mandatory": confirmed.
- "3–5 keywords": confirmed. The site states this in the description of the optional title page.
- "LaTeX template available, particularly for production after acceptance": confirmed.
- "Double-blind review": confirmed.
- "$25 submission fee": confirmed. The fee is not refunded after a desk rejection.
