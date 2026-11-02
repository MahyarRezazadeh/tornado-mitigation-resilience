# Reference articles examined, and structural decisions

## Journal requirements (verified)

The Wiley author-guidelines page refused automated access (HTTP 403). The requirements below come from the official page's indexed text, retrieved by web search on 2026-10-10:
- **Length:** Original Research under 7,000 words, excluding references, tables and figures.
- **Page 1:** title only, because review is double-blind.
- **Page 2:** abstract of 250 words or fewer, plus 3–5 keywords.
- **Page 3:** main text starts.
- **Layout:** double-spaced, margins of at least 1 inch.
- **Headings:** main headings in bold capitals and numbered; subheadings bold and numbered (1.1); sub-subheadings italic.
- **Back matter:** REFERENCES followed by tables and figures, which are numbered.

**Reference style.** The page excerpt does not state it. Risk Analysis articles published in 2023–2025 (all four below) use APA author–date citations, so APA 7 is used via `biblatex-apa`. **Author to confirm on the submission system.**

**Generative-AI policy.** This comes from Wiley's AI guidelines, reproduced on third-party mirrors.
- Substantive AI use must be disclosed in Methods, Acknowledgements or a disclosure statement.
- AI must not be used to create or alter research data or results.

## Articles actually read

| Article | Access | Use |
|---|---|---|
| **Frimpong, Reilly & Niemeier (2023)**, "Does federal flood hazard mitigation assistance affect community rating system participation?" *Risk Analysis* 43:1414–1433 | Full text (open-access PDF, UMD DRUM) | **Principal structural model** |
| Best, He, Reilly, Tran & Niemeier (2025), "Rent affordability after hurricanes: Longitudinal evidence from US coastal states," *Risk Analysis* 45:3439–3451 | Full text (Europe PMC) | Style of a county-panel econometric paper |
| Habets & Cutter (2025), "A community resilience index for place-based actionable metrics," *Risk Analysis* | Full text (Europe PMC) | Discussion and conclusion style; measurement of capacity |
| Geronimo et al. (2025), "Cultural and institutional factors driving severe repetitive flood losses," *Risk Analysis* | Introduction and structure read (Europe PMC) | Framing of institutional and fiscal-federalism arguments |

**Not read in full.** Wiley's bot protection blocked the full text of Miao, Davlasheridze & Reilly (2025), Miao & Davlasheridze (2025) and Brody et al. (2009). These are cited only for findings stated in their abstracts.

## Why Frimpong et al. (2023)

It is the closest Risk Analysis article in subject matter: FEMA Hazard Mitigation Assistance, local governments' participation in a FEMA program, and a national panel econometric design. It shows how this journal presents program institutions, mechanisms and regression results to a risk-analysis audience.

## Structural decisions borrowed (logic, not wording)

1. **Introduction:** opens with the concrete program and its stakes; the gap is stated as what prior work could not establish; the question and design follow.
2. **Background:** a dedicated section on how the program works (Frimpong's "CRS in practice and theory"), followed by a synthesis of the participation literature with explicit expectations. We state hypotheses H1–H4, as Best et al. state theirs.
3. **Data section:** each variable class has its source and construction; a summary-statistics table follows the variable definitions.
4. **Equations:** numbered and defined term by term, followed by the estimator and why it fits (Frimpong's GMM justification corresponds to our declaration fixed-effects justification).
5. **Results:** subsections organized by question rather than by table. Each coefficient is interpreted in natural units and compared with prior studies.
6. **Discussion:** findings are related to the program's design, with policy implications stated cautiously and limitations given as specific data constraints.
7. **Tables:** "Note:" lines under each table state the SE convention and significance stars, following Frimpong's tables.

**Departures from the model, by design:**
- Our design is a cross-sectional comparison within declaration rather than a dynamic panel GMM. This fits the question about county size.
- We add the decomposition by stage of the grant pipeline, which Frimpong et al. could not do.
- No sentences or distinctive phrases were copied.
