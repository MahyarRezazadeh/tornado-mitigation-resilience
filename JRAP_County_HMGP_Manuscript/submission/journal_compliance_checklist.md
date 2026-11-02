# JRAP compliance checklist: Research Article

Requirements verified 2026-10-13 (see `reports/journal_requirements.md`).

**Overall: NOT READY FOR SUBMISSION.** The AI-policy eligibility question (item 1) is open, and several author inputs are missing.

| # | Requirement | Status | Where / action |
|---|---|---|---|
| 1 | AI use limited to improving writing quality, and disclosed | ❌ **Unresolved conflict** | `AI_POLICY_COMPLIANCE.md`. Author decision required. |
| 2 | Submission is a PDF | ✅ | `output/main.pdf` |
| 3 | No identifying information in the manuscript | ✅ No author names, affiliations, emails or acknowledgments | Check again after the placeholders are filled. Funder names can identify authors. |
| 4 | No identifying file properties | ✅ PDF Author, Subject, Keywords and Producer are empty; Creator is "LaTeX" | Before uploading, also rename the file (e.g. `JRAP_manuscript_blinded.pdf`) and avoid OneDrive/Word re-saves that add the account name. |
| 5 | Cover letter naming the submission type | ⚠️ Drafted ("Research Article") | `cover_letter.tex`: fill the placeholders and do not send until item 1 is settled. |
| 6 | Optional title page (title, abstract, 3–5 keywords, author details) | ⚠️ Template drafted | `author_information.tex`: author details needed |
| 7 | 3–5 keywords | ✅ 5 keywords | `main.tex` |
| 8 | Length ≤ ~8,000 words (recommended) | ✅ about 6,600 words of main text | `reports/verify_numbers.py` |
| 9 | Builds on the regional science / regional economics literature (desk-rejection criterion) | ⚠️ Partly | The framing has been revised, but the reference list contains almost no regional-economics journals. See `reports/MANUSCRIPT_AUDIT.md` §A and `reports/LITERATURE_FOR_AUTHOR_REVIEW.md`. |
| 10 | Funding statement (recommended) | ⚠️ Placeholder | `sections/07_statements.tex` |
| 11 | Conflict-of-interest statement (recommended) | ⚠️ Placeholder | `sections/07_statements.tex` |
| 12 | Data and code availability (recommended) | ⚠️ Text present; repository DOI missing | `sections/07_statements.tex` |
| 13 | AI is not listed as an author | ✅ | — |
| 14 | $25 fee (no refund after desk rejection) | ℹ️ | Pay only after item 1 is settled. |
| 15 | LaTeX/Overleaf template | ℹ️ Required after acceptance only | `reports/journal_requirements.md` #12 |
