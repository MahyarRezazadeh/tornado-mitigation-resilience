# Quasi-Experiment Assessment (Section 42)

Data: OpenFEMA HazardMitigationAssistanceProjects v4 (status, BCR) and HmaSubapplications v2 (selection fields).
Strict tornado/wind project records (all statuses): 7,110; funded: 5,764; not funded
(denied / withdrawn / not selected / void): 827.

## Status distribution (strict projects)

| status                |    n |
|:----------------------|-----:|
| Closed                | 5116 |
| Approved              |  622 |
| Pending               |  518 |
| Not Approved / Denied |  364 |
| Withdrawn             |  289 |
| Not Selected          |  117 |
| Void                  |   57 |
| Obligated             |   26 |
| Revision Requested    |    1 |

## Candidate designs

| Institutional rule | Running variable | Cutoff | Sample size | Manipulation risk | Balance test feasible | RD credible? | IV credible? | Recommended use |
|---|---|---|---|---|---|---|---|---|
| Benefit-cost requirement (BCR >= 1.0 for HMA cost-effectiveness) | Reported BCR | 1.0 | 6,455 strict records with BCR > 0; 42 below 1 | HIGH: BCR is computed by applicants/states with FEMA BCA Toolkit and pre-calculated benefits (e.g., safe-room pre-calculated benefits), so projects are engineered to clear 1.0; non-cost-effective projects are typically not submitted or are revised | Partly (county covariates) | **No** - few observations just below 1 and funding share does not jump discretely (funded share BCR<1: 0.51; BCR>=1: 0.84); BCR = 0 / missing for most HMGP records | No | Descriptive only |
| BRIC / FMA national competition scores | Technical + qualitative score | Annual funding line | Safe-room subapplications by program: {'Hazard Mitigation Grant Program': 3292, 'Pre-Disaster Mitigation': 385, 'Building Resilient Infrastructure and Communities': 224, 'Hazard Mitigation Grant Program Post Fire': 33, 'Legislative Pre-Disaster Mitigation': 10, 'Pre-Disaster Mitigation Congressionally Directed Spending': 8, 'Fire Management Assistance Grant - Hazard Mitigation Grant Program': 2} ; selection status values: {None: 3793, 'Not Selected': 96, 'Identified for Further Review': 38, 'Did Not Meet HMA Requirements': 27} | Moderate | Not possible | **No** - scores and the funding line are not published in OpenFEMA; BRIC began FY2020 and is tiny for safe rooms | No | Future FOIA request |
| HMGP formula: 15% (20% enhanced-plan states) of post-disaster federal assistance | State HMGP ceiling by disaster | none (continuous) | All HMGP disasters | Low (formula) | Yes | No | **Possibly**: HMGP ceiling scales with disaster aid in the STATE, which is plausibly exogenous to a given county's later tornado exposure, but it also reflects the state's own disaster history; exclusion restriction weak | Shift-share style instrument for a redesign; requires state-disaster ceilings (HazardMitigationGrantProgramDisasterSummaries) |
| Cost-share changes (e.g., 90% federal share in some declarations; 2018 DRRA) | Declaration date | rule dates | Few rule changes | Low | Yes | No | Weak first stage expected | Event-study robustness only |
| Rejected vs accepted subapplications | Status | n/a | Never-funded applicant counties: 36 | Selection on unobserved project quality / admin capacity | Yes | No | No | **Alternative control group** (applicant counties that never received a strict project) |

## Design check: comparison group = applicant counties never funded (exploratory)

| outcome                  |     beta |      se |       p |      N |   control_counties | status   |
|:-------------------------|---------:|--------:|--------:|-------:|-------------------:|:---------|
| separation_rate          |  0.00048 | 0.00108 | 0.65621 |  99604 |                 36 | ok       |
| log_employment           |  0.00356 | 0.00465 | 0.44474 | 100503 |                 36 | ok       |
| log_earnings             | -0.00289 | 0.0022  | 0.18817 |  99605 |                 36 | ok       |
| establishment_death_rate |  0.05999 | 0.05762 | 0.29816 |  30392 |                 36 | ok       |
| job_destruction_rate     |  0.13321 | 0.12611 | 0.29115 |  30531 |                 36 | ok       |

## Assessment

- No sharp funding cutoff with a published, non-manipulable running variable exists in public data; an RD on
  the BCR = 1 threshold is **not credible** (manipulation by construction, little mass below 1, BCR missing/zero
  for most HMGP records).
- An IV based on state HMGP ceilings (post-declaration formula) is the most promising quasi-experimental
  redesign, but the exclusion restriction (state disaster history affects later outcomes) needs defending.
- The never-funded-applicant comparison group is feasible but small (36 counties) and selected on
  application capacity; it is a useful robustness check, not a quasi-experiment.
- **A FEMA funding cutoff would materially improve identification only if FEMA released BRIC/PDM national
  scores and funding lines (FOIA).** With public data, the design remains a selection-on-observables /
  difference-in-differences design whose credibility rests on the pre-trend and placebo evidence.
