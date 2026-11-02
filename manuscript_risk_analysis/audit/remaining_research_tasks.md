# Remaining research tasks before submission

## Evidence status

**Verified and included:**
- Small-county gap in applications, funded projects, and safe rooms/retrofits within declaration (Table 2), with its gradient (Figure 2).
- Robustness (Table 5).
- Decomposition by stage of the pipeline (Table 3).
- Mechanical versus residual gap (Table 2, column 5; Table 3, county-government columns).

**Included as suggestive, labelled as such in the text:**
- Within-county hit response (p ≈ 0.05).
- Association with state delivery (cross-state).
- DRRA null (wide CI).
- Exploratory safe-room pre-calculated-benefit test (Appendix S3; start date uncertain).

**Not causal.** County size is not assigned. No source of exogenous variation in local capacity has been found yet.

## Analyses still to do (priority order)

1. **Exogenous variation in capacity.** Candidates:
   - state adoption dates of HMGP Advance Assistance or state-funded application support (needs a state policy panel);
   - FEMA BRIC Direct Technical Assistance selections (2021+);
   - county emergency-manager presence or turnover (e.g. EMPG staffing data).
2. **Subapplication linkage.** Few older "Closed" and "Not Approved/Denied" subapplications carry benefiting counties. Options:
   - recover county links through project identifiers (`projectIdentifier` ↔ subapplication);
   - re-estimate the approval and denial comparison on the linkable universe.
3. **DRRA applicability date.** Confirm the HMGP subrecipient management-cost applicability date (FEMA interim policy FP 104-11-1; disasters declared on or after 1 Aug 2017, per the archived FEMA page found by search) against the policy text.
4. **Pre-calculated safe-room benefits.** Establish the first date of availability. If it predates 2015, re-run Appendix S3.
5. **Applicant-type classification.** Validate the text rules (county government, municipal, school, special, state) on a hand-coded sample. Report precision and recall.
6. **Safe room and retrofit identification.** Report the project-type codes used and their share of HMGP spending (from `03_classify_fema_projects.py`). Add a sensitivity check using HIGH-confidence classifications only.
7. **Multiple-hypothesis framing.** Table 4 reports 4 outcomes × 4 panels. Consider a pre-specified primary outcome per panel, or sharpened q-values.
8. **Alternative size definitions.** Population quartiles or quintiles, the rural–urban continuum, and per-capita versus total HMGP dollars.
9. **Outcome horizon for 2019–2021 declarations.** Pending subapplications may be censored. Re-estimate on declarations up to 2019.
10. **Replication package.** Deposit the code and processed data (OSF or ICPSR). Insert the DOI into the Data Availability Statement.

## Items for the authors (not research)

- Title page with authors, affiliations, funding and acknowledgments (kept out of the anonymous PDF).
- Conflict-of-interest statement.
- **Review and edit the AI-use disclosure.** Wiley prohibits using generative AI to create or alter research data or results. Here the AI assistant wrote and ran the estimation code. The authors must review and re-run the code (`scripts/make_tables_figures.py` and project scripts 43–52) and decide how to describe this use.
- Confirm the reference style (APA 7) and the line-numbering expectations in ScholarOne.
