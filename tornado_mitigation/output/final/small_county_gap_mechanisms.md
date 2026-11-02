# Small-county gap: mechanism tests (2026-10-09)

Code: `src/51_gap_mechanisms.py`. Table: `output/tables/gap_mech_results.csv`.
Spec: county × declaration, disaster FE, exposure/damage and demographic controls (S4 from `small_county_gap_robustness.md`), county clusters.

## Test 1: fewer eligible applicants (mechanical)?
Census of Governments 2017: small counties average 9.8 municipalities/townships (vs 14.0), 7.5 special districts (vs 14.6), 2.3 school districts (vs 6.2). 48% of small county governments list a website, vs 72% of others.

| Outcome | Gap, S4 | + counts of local units | Share of gap explained |
|---|---|---|---|
| Any HMGP project from this disaster | −8.8 pp | −5.0 pp (p<0.001) | 43% |
| Safe room / retrofit from this disaster | −3.1 pp | −2.4 pp (p<0.001) | 24% |
| Strict project within 3 yrs | −8.1 pp | −5.9 pp (p<0.001) | 27% |

- School-district count is the strongest predictor (+5–7 pp per log point). Adding the county-website proxy changes nothing.
- **County-government projects only** (exactly one county government per county, so not an applicant-count artifact): gap −2.4 pp on an 11.5% base (−21%, p=0.001). County-government *applications*: −2.35 pp on 11.2% (−21%, p=0.001).
- Gaps by applicant type: municipal −2.9 pp; school −0.5 pp (p=0.08).
- **Verdict:** the number of eligible applicants explains roughly a quarter to two-fifths of the gap. A real residual gap remains even for the single county government.

## Test 2: didn't apply, or applied and failed?
OpenFEMA HMGP subapplications (non-void), linked by disaster number + benefiting county: 32,607 county-application rows. Validation: "any approved application" vs "funded HMGP project" correlation 0.92.

| | Small | Other | Adjusted gap |
|---|---|---|---|
| Any application from this disaster | 14.6% | 26.3% | **−8.9 pp (p<0.001)**; −5.4 pp with gov counts |
| Safe room / retrofit application | | 5.4% | −3.0 pp (p<0.001) |
| Success rate, given applied | 87.0% | 86.4% | −0.2 pp (p=0.91) |
| Withdrawal rate, given applied | 10.7% | 11.9% | −1.1 pp (p=0.52) |
| Denial rate, given applied | 2.3% | 1.7% | +1.3 pp (p=0.045) |
| Application size, log $ | | | −0.19 (p=0.03) |
| Benefit–cost ratio, log | | | −0.07 (p=0.23) |

- **Verdict:** essentially the whole gap is at the **application margin**. Once small counties apply, they succeed at the same rate and do not withdraw more. The extra denials are statistically detectable but tiny in absolute terms. Their applications are about 17% smaller in dollars, and the BCR difference is not significant.
- **Caveat:** the county-linked subset contains few "Closed" and "Not Approved / Denied" records (the benefiting-county field seems to be missing for older or closed records). The conditional success comparison therefore rests mainly on Approved / Withdrawn / Not Approved records. Investigate before publication.

## Implication
The gap is an **application / participation gap**. About a third of it is mechanical, from fewer potential applicant entities. The rest is a lower propensity to apply, even by the county government itself. That is consistent with fixed application costs (BCA, engineering, 25% match, grant-management capacity), not with FEMA or state screening.
