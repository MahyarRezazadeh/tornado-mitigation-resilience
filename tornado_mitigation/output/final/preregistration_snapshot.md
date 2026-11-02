# Pre-Analysis Snapshot (frozen before any outcome regression)

Frozen: 2026-10-07, after the Section 62 pilot (treatment and tornado counts only) and before any
economic outcome was merged with treatment or estimated. No outcome coefficient had been computed
when this file was written. Any later change must be appended in the "Post-freeze modifications"
section with its reason.

## Primary specification (as specified by Section 48)

| Element | Primary choice |
|---|---|
| Treatment | STRICT FEMA tornado/severe-wind mitigation: funded HMA projects with FEMA type 206.x (Safe Room, Tornado and Severe Wind Shelter) or 205.7/205.8 (Wind retrofits), or explicit safe-room/wind-retrofit text |
| Treatment status | County treated from the first strict project's treatment date onward (absorbing) |
| Treatment date | Completion when observed, otherwise obligation + 2 years |
| Tornado definition | EF1+ (any EF1-EF5 tornado segment in the county in the period) |
| Sample | All contiguous-US counties (3,108, harmonized 2020 geography), 1990-2025, unbalanced where outcome data start later |
| Primary outcomes | employment, separations, earnings, establishment deaths, job destruction |
| Fixed effects | county FE + state x time FE |
| Cluster | county |
| Event window | -8 to +12 quarters (annual: -5 to +8 years), reference period -1 |

Model: `Y_ct = beta * Mitigated_ct * Tornado_ct + g1 * Mitigated_ct + g2 * Tornado_ct + county FE + state x time FE`.
beta is the confirmatory coefficient (change in the tornado-associated outcome after mitigation is operational).

## Data-limitation modifications (decided before estimation; labeled)

1. **No completion date exists in OpenFEMA** (verified in field metadata, 2026-10-07). The pre-specified
   fallback applies to 100% of projects: obligation + 2 years. Where obligation is missing: approval + 2 years;
   where both are missing (533 strict projects): closeout date (labeled `closeout_fallback`) so that funded
   counties are not mis-coded as controls. Closeout and last federal payment are reported as completion proxies.
2. **Outcome variable operationalization (fixed now):**
   - employment = log(EmpEnd), QWI end-of-quarter private employment. QWI `Emp` is beginning-of-quarter
     employment, mechanically unable to respond to a same-quarter tornado.
   - separations = QWI separation rate Sep / ((Emp + EmpEnd)/2).
   - earnings = log(EarnS), QWI average monthly earnings of full-quarter employees.
   - establishment deaths = BDS official establishment exit rate (year t, March-to-March).
   - job destruction = BDS official job destruction rate (DHS denominator).
3. **Timing alignment for annual BDS/CBP/IRS outcomes:** these measure March 12 of year t. Tornado exposure is
   March-aligned (Q2-Q4 of t-1 plus Q1 of t). Mitigated requires treatment on/before the window start.
   Quarterly QWI/QCEW use same-quarter tornado exposure; dynamics come from the event studies.
4. **QCEW** open-data slices cover 2014+ only; QCEW is a replication/industry source, not a primary outcome source.
5. **IRS migration** usable CSV files cover 2012-2023 only.
6. **Public finance** is LOW feasibility (sample-based annual survey); not estimated.

## Decision rules fixed now

- Economically meaningful effect E* = 50% offset of the average tornado-associated effect |g2| in the primary
  model. If the tornado main effect is not in the disruptive direction, E* = 0.05 x outcome SD.
- NO DETECTABLE EFFECT: |beta| small and the 95% CI excludes +/- E*.
- UNDERPOWERED: 95% CI contains both +E* and -E*.
- Robustness classes follow Section 35 exactly; sign consistency uses credible specifications only
  (placebos, permutation and multiple-testing rows are excluded from the sign-consistency denominator).
- pretrend_pass: joint test of pre-event (k = -8..-2) Mitigated x EventTime interactions in the stacked tornado
  event study has p > 0.10.
- placebo_pass: placebo (future mitigation x current tornado, before treatment) has p > 0.10.
- Power: MDE(80/90) = (z_0.975 + z_power) x clustered SE of beta. WELL POWERED if MDE80 <= E*,
  MODERATELY POWERED if MDE80 <= 2E*, otherwise UNDERPOWERED.
- Multiple testing: BH and Holm within the 5-outcome confirmatory family; separately within each exploratory family.
- Modern estimators: (i) stacked mitigation-cohort triple-difference with clean (not-yet/never treated) controls
  (Callaway-Sant'Anna / interaction-weighted analogue), (ii) stacked tornado-event study with clean controls,
  (iii) Sun-Abraham saturated and Gardner did2s event studies for the mitigation-adoption diagnostic.

## Confirmatory vs. exploratory

- Confirmatory: the five primary outcomes above, primary specification.
- Robustness: R01-R70 (Section 32), leave-one-state-out, leave-one-event-out.
- Exploratory: all secondary outcomes, mechanisms, heterogeneity (corrected within families).

## Post-freeze modifications

(none at freeze time)

**PF-1 (2026-10-08, after estimation; labeled):** "0.05 x outcome SD" in the E* rule is clarified to mean the
**within-county SD** (Y net of county and state x time means), not the raw pooled SD. Reason: for log-level
outcomes the raw SD mostly reflects cross-county size differences (e.g. 0.05 x raw SD of log employment = 8.6%),
which would make "NO DETECTABLE EFFECT" trivially easy. Noticed while reviewing E* values in the power table,
before any classification was reported; the raw-SD version is retained in `primary_results.csv`
(`E_star_rawSD_version`) for transparency. This change can only make NO DETECTABLE EFFECT harder to obtain.

**PF-2 (data limitation):** QCEW, IRS, and finance coverage as listed above; stacked clean-event study samples
up to 3 same-state clean controls per event county (seeded) because of an 8 GB RAM limit.
