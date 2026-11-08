# Small-county application gap: causal-story tests (2026-10-09)

Code: `src/52_gap_causal_tests.py` (+ inline checks). Tables: `output/tables/gap_causal_*.csv`.
Unit: county × tornado/severe-storm DR declaration, 1999–2021 (N ≈ 12,000). County clusters.

## T1. Fiscal or administrative capacity: NOT supported
- Census of Governments 2017 finance shows small counties have **higher** per-capita county taxes (log 6.02 vs 5.67) and administrative spending (financial administration + central staff; 4.36 vs 3.90).
- Adding taxes and admin spending leaves the gap unchanged: applied −5.37 → −5.38 pp; county-government applications −2.35 → −2.52 pp.
- No interaction with low tax or low admin capacity (all p > 0.2).
- Holding population fixed, absolute admin spending and absolute taxes do not predict applying (p = 0.85 / 0.69). Population itself does (+6.9 pp per log point).
- Verdict: the 25% match and money for administration are not what binds.

## T2. State / regional intermediaries: partly supported
- **Measure:** state-level, pre-2009 share of HMGP subapplications filed by the state itself, or by regional planning/development bodies. Outcomes are for 2009–2021, with disaster FE.
- **State-filed share:** +1 SD → small-county gap smaller by **2.6 pp for applying (p = 0.04)** and **3.0 pp for funded projects (p = 0.02)**, on a gap of about 4.5 pp.
- **Regional-body share:** narrows the safe room/retrofit gap (+1.1 pp per SD, p = 0.01) but not applying overall.
- **Caveat:** these are cross-state associations with crude measures. Regional bodies are rare (≤ 9% of applications in any state).

## T3. Same county, tornado shock: supported (marginal)
Specification: county FE + disaster FE, comparing declarations in which the county was hit by a populated-place track with declarations in which it was not. Damage is excluded because it is the channel through which a hit acts.

| Outcome | Hit (large counties) | Hit × small | Net for small |
|---|---|---|---|
| log number of applications | +4.3% (p = 0.016) | −7.2% (p = 0.046) | ≈ −3% |
| County government applies | +2.4 pp (p = 0.045) | −4.2 pp (p = 0.059) | ≈ −1.8 pp |
| Any application | +2.4 pp (p = 0.14) | −4.1 pp (p = 0.23) | |
| log people in path (continuous), county-gov applies | +0.35 pp (p = 0.02) | −0.60 pp (p = 0.05) | |

- Same county, same kind of shock: larger counties raise applications after a hit, small counties do not.
- This rules out time-invariant "small counties need less" explanations, and fits a constraint on the capacity to respond.
- With damage controls the hit effect itself vanishes, as expected for a mediator.

## T4. Application-cost policy shocks: NOT supported (null)
- **DRRA §1215** (subrecipient management-cost reimbursement, declarations from 2017-08-01): small × post = −1.9 pp (SE 3.6, p = 0.59) for applying; −1.7 pp for funded.
  - Event study by declaration year is flat (all p > 0.25). Placebo cutoff 2014-08 is null.
  - Raw gap went from 16.2 pp to 12.4 pp, but none of that change survives FE.
  - The CI rules out the reform closing more than about half of the gap.
- **Pre-calculated safe-room benefits** (2015, start date uncertain): triple diff +0.7 pp (p = 0.81). Exploratory only.

## Overall
- **Robust facts:**
  - The gap is at the application margin, not approval.
  - About a third of it is mechanical (fewer local units).
  - The rest is not explained by damage, poverty, race, rurality, fiscal or administrative budgets, or FEMA screening.
- **Causal-leaning evidence:**
  - Within-county response to tornado hits is muted in small counties.
  - Smaller gaps where states file applications themselves.
- **Against a simple cost story:** reimbursing management costs (DRRA) and removing BCA work (pre-calculated benefits) did not narrow the gap.
  - Consistent with a non-monetary, up-front constraint (expertise, staff time, knowing how to apply).
  - Also consistent with limited power.
- **Missing for a causal claim:** exogenous variation in local capacity. Candidates:
  - state adoption timing of HMGP Advance Assistance or state-funded application support;
  - FEMA BRIC Direct Technical Assistance selection (2021+, a lottery-like selection);
  - turnover of county emergency-management staff.
