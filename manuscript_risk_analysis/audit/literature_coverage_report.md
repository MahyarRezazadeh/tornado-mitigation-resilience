# Literature and citation coverage report

## How references were verified

- **Bibliographic metadata.** Every journal reference was resolved by DOI through the Crossref API (`scripts/verify_references.py`, `scripts/build_bib.py`).
  - Online-first years were replaced by the print-issue year.
  - Crossref author lists were corrected where incomplete or mis-split: Collins & Gerber (2006) appears in Crossref with one author; Healy & Malhotra is in capitals; Cameron and Klaiber have mis-split names.
  - Results are in `audit/reference_verification.csv` and `audit/bib_metadata.csv`.
- **Grey literature.** CRS report R46989 (Horn, 2022; author and date confirmed via EveryCRSReport), the Headwaters Economics web page (author Kris Smith; undated, so cited as n.d.), the FEMA policy documents and the data sources were checked by URL or search.
- **Content claims.** `audit/literature_matrix.csv` records, for each reference, whether the claim it supports was checked against the full text, an abstract or publisher summary, or metadata only.
  - Vila et al. (2022) is metadata only, so it is cited only as related work, with no specific finding attributed.
  - Simmons & Sutter (2006) and Merrell et al. (2005) are cited only for general statements consistent with their titles and summaries.

## Coverage audit

| Check | Result |
|---|---|
| All in-text citations present in references.bib | Yes: 55 cited, 0 missing (`scripts/citation_coverage.py`) |
| All bibliography entries cited | Yes: 10 uncited entries pruned (`scripts/prune_bib.py`) |
| Foundational risk and vulnerability literature | Lindell & Perry (2012, RA), Bubeck et al. (2012, RA), Cutter et al. (2003), Cutter & Finch (2008), Cutter et al. (2016), Burby (2006) |
| Directly related empirical work on the policy | Seong et al. (2022); Miao et al. (2025, RA); Frimpong et al. (2023, RA); Mach et al. (2019); Rose et al. (2007); Davlasheridze et al. (2017) |
| Small-jurisdiction and local-capacity literature | Collins & Gerber (2006, 2008); Hall (2008); Smith et al. (2025, PAR); Smith & Vila (2020); Vila et al. (2022); Brody et al. (2009, 2010); Sadiq & Noonan (2015); Li & Landry (2018); Posey (2009); Lyles et al. (2014); Berke et al. (2014) |
| Tornado hazard context | Ashley (2007); Sutter & Simmons (2010); Gensini & Brooks (2018); Doswell et al. (2009); Simmons & Sutter (2006, RA); Merrell et al. (2005) |
| Methods | Abadie et al. (2023); Cameron & Miller (2015); Roth et al. (2023) |
| Recent work (2021–2026) | Miao et al. (2025 ×2, RA); Smith et al. (2025); Frimpong et al. (2023); Seong et al. (2022); Vila et al. (2022); Emrich et al. (2022); Drakes et al. (2021); Roth et al. (2023); Abadie et al. (2023) |

## Novelty claim

The manuscript claims to locate the gap at the application stage using records that include failed applications, to compare counties within the same declaration, and to separate the mechanical and capacity components. It does **not** claim to be the first study of HMGP disparities: Seong et al. (2022) and Miao et al. (2025) are discussed as the closest antecedents.

The search was a targeted search of the web, Crossref, Europe PMC and OpenAlex, not a systematic review.

## Possible missing or uncertain references, for the authors

1. **A Scholar or Web of Science pass** on "HMGP" with "subapplication", "application", "local capacity" or "small communities", to confirm that no paper already studies the application margin.
2. **GAO reports on HMA administrative burden**, e.g. GAO-21-140 on streamlining hazard mitigation grants. Not verified here, so not cited.
3. **FEMA's HMGP equity analysis summary (2024)** was found but not read. It may contain relevant tract-level statistics.
4. **The Wiley full texts of Miao et al. (2025)**, to confirm the paraphrase of their findings.
5. **The tornado safe-room benefit–cost literature beyond Simmons & Sutter**, e.g. Merrell, Simmons & Sutter on the safety benefits of safe rooms. Verify which article contains which estimates before quoting numbers.
