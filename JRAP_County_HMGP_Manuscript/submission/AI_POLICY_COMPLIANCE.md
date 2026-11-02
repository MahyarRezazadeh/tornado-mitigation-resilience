# AI-policy compliance assessment

**Status: UNRESOLVED. The manuscript is not eligible for submission until the authors resolve this issue through legitimate means.**

Prepared 2026-10-13. The policy text was read on the official JRAP site that day.

## 1. JRAP policy (verbatim, official source)

Source: Guide for Authors, https://jrap.scholasticahq.com/for-authors (verified 2026-10-13)

> AI Disclosure: Authors must declare the use of AI in the manuscript preparation process. JRAP allows the use of generative AI (and other AI-assisted technologies) in manuscript production, only to improve writing quality. AI tools must not be listed as an author or co-author. If AI is used, authors are required to provide an AI usage disclosure in their manuscript. AI in other parts of the research process are not permissible and evidence of use of AI in other parts of the research process will be cause for rejection.

## 2. The source manuscript's disclosure (verbatim)

Source: `source_snapshot/risk_analysis_manuscript.tex`, section "Declaration of Generative AI Use"

> *[Draft for author review.]* The authors used a generative AI assistant (Anthropic's Claude) under their direction to write and run data-assembly and estimation code, to search for and verify literature, and to draft and edit the manuscript text. All data are public administrative records; no data were generated or altered by the assistant other than through documented, reproducible code that the authors have reviewed and rerun. The authors take full responsibility for the content.

## 3. Where the two conflict

| Disclosed use | Allowed under JRAP? |
|---|---|
| Draft and edit manuscript text | Editing to improve writing quality is allowed. *Drafting* text goes further than improving its quality, so the editor should be asked. |
| Write and run data-assembly and estimation code | **No.** This is part of the research process. |
| Search for and verify literature | **No, on a plain reading.** Literature search is part of the research process. |
| Revising text, structure and formatting for this JRAP version (Claude, 2026-10-13) | Mostly allowed. The revision changed no data, estimates or literature. It did reframe the argument and reorganize sections, so this too should be disclosed. |

The project records support the disclosure. The Tornedo project memory and the source `audit/` folder show that an AI assistant built the data pipeline (scripts 43–52), ran the estimations, generated the tables and figures (`scripts/make_tables_figures.py`), and verified references against Crossref (`scripts/build_bib.py`, `audit/reference_verification.csv`). Under JRAP's stated policy, evidence of these uses "will be cause for rejection."

## 4. What this draft does and does not do

- The JRAP manuscript (`sections/07_statements.tex`) keeps the full original disclosure. It adds one sentence stating that the same assistant revised this version, and a red author-decision flag.
- Nothing in the disclosure has been removed, softened or reworded to fit the policy. **Do not edit the disclosure to describe less AI use than actually occurred.**
- The cover letter is drafted but marked not to be sent until the editor has answered.
- No new analyses, literature searches or results were produced for this version.

## 5. Legitimate options for the authors

1. **Ask the editor before submitting (recommended).** Send the inquiry in `editor_inquiry_AI_use.md`. It describes the AI use exactly and asks whether the manuscript is eligible. Paying the $25 fee before this is settled risks losing it to a desk rejection, which is not refunded.
2. **Choose a journal whose policy allows the uses that occurred.** Several journals permit AI-assisted coding with disclosure.
3. **Redo the research yourselves, then disclose accurately.** Independently rewrite and rerun the data assembly and estimation, and independently carry out and check the literature review. Only then can the disclosure accurately describe a smaller AI role, and the authors should still tell the editor the history. This is substantial work. The disclosure should change only after that work has actually been done.

What is not legitimate: submitting with a narrowed disclosure, omitting the disclosure, or describing the coding and literature work as the authors' own unaided work.

## 6. Points to confirm in the existing disclosure

- "Code that the authors have reviewed and rerun": confirm this is true before submitting to any journal. The source project's `audit/remaining_research_tasks.md` lists rerunning the code as an outstanding task for the authors.
- "The authors": confirm the author list. It determines whether "we" and "the authors" are accurate.
