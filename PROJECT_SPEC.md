# Tornedo Project — Full Specification

Saved 2026-10-07. Verbatim project brief as provided by the user.
Project root for all outputs: `C:\Users\mahya\OneDrive - Simon Fraser University (1sfu)\Desktop\Tornedo`
(The `tornado_mitigation/` tree described below lives inside this folder.)

---

You are a senior empirical economist, econometrician, research software engineer, and replication specialist.

Your task is to BUILD AND EXECUTE a complete, reproducible empirical economics project evaluating whether local FEMA-supported tornado/severe-wind mitigation investments improve subsequent local economic resilience in the United States.

Do not only write a research plan.

You must:

1. Create the complete project.
2. Locate and download publicly available U.S. data.
3. Construct FEMA mitigation treatment variables.
4. Construct tornado exposure.
5. Merge economic/labor-market outcomes.
6. Test feasibility of every proposed outcome.
7. Estimate primary causal models.
8. Estimate dynamic/event-study models.
9. Run mechanism tests.
10. Run heterogeneity tests.
11. Run extensive robustness checks.
12. Test pre-trends and placebos.
13. Evaluate statistical power.
14. Correct for multiple hypothesis testing.
15. assess literature novelty.
16. create a transparent publication-potential score.
17. identify likely journal fit.
18. create final tables reporting whether each result is ROBUST, MODERATELY ROBUST, MIXED, NOT ROBUST, NO DETECTABLE EFFECT, UNDERPOWERED, or INFEASIBLE.
19. identify the best paper that can be written from the results.
20. save all code, raw data references, intermediate files, tables, figures, logs, and final reports.

Do not hide null results.

Do not select specifications because they produce statistical significance.

Do not call something robust simply because p < 0.05.

============================================================
SECTION 1
MAIN RESEARCH QUESTION
============================================================

Research question:

Do local ex-ante tornado/severe-wind mitigation investments reduce subsequent economic and labor-market disruption caused by tornadoes?

The key causal object is NOT:

mitigation -> unconditional local economic growth

The central causal object is:

mitigation × subsequent tornado exposure -> economic resilience

The hypothesis is that when a tornado subsequently occurs, places with operational mitigation investments experience:

- fewer worker separations,
- smaller employment losses,
- smaller earnings losses,
- fewer establishment deaths,
- lower job destruction,
- faster employment recovery,
- greater establishment survival,
- reduced out-migration,
- smaller local fiscal losses,
- smaller disruptions among vulnerable workers,
- lower physical damages conditional on hazard severity.

This is therefore primarily a RESILIENCE paper.

============================================================
SECTION 2
PROJECT DIRECTORY
============================================================

Create:

```
tornado_mitigation/
    README.md
    requirements.txt
    .env
    .env.example

    config/
        config.yaml
        outcome_registry.csv
        treatment_keywords.csv
        industry_groups.csv
        state_fips.csv

    data/
        raw/
            fema/
            noaa/
            qwi/
            bds/
            qcew/
            cbp/
            irs/
            building_permits/
            public_finance/
            auxiliary/

        intermediate/
        processed/
        crosswalks/

    src/
        00_check_environment.py
        01_download_fema.py
        02_clean_fema.py
        03_classify_fema_projects.py
        04_construct_treatment.py
        05_download_noaa_storms.py
        06_clean_tornadoes.py
        07_construct_tornado_exposure.py
        08_download_qwi.py
        09_clean_qwi.py
        10_download_bds.py
        11_clean_bds.py
        12_download_qcew.py
        13_clean_qcew.py
        14_download_cbp.py
        15_clean_cbp.py
        16_download_irs.py
        17_clean_irs.py
        18_download_building_permits.py
        19_clean_building_permits.py
        20_download_public_finance.py
        21_clean_public_finance.py
        22_build_county_crosswalk.py
        23_build_master_panels.py
        24_feasibility_analysis.py
        25_descriptive_analysis.py
        26_primary_models.py
        27_event_studies.py
        28_stacked_event_studies.py
        29_mechanisms.py
        30_heterogeneity.py
        31_matching_weighting.py
        32_robustness.py
        33_placebo_tests.py
        34_leave_one_out.py
        35_power_analysis.py
        36_multiple_testing.py
        37_literature_search.py
        38_publication_score.py
        39_journal_fit.py
        40_make_tables.py
        41_make_figures.py
        42_generate_report.py
        run_all.py

    output/
        tables/
        figures/
        diagnostics/
        models/
        literature/
        logs/
        final/

    tests/
        test_fema.py
        test_tornadoes.py
        test_crosswalks.py
        test_panels.py
        test_regressions.py
```

============================================================
SECTION 3
PYTHON ENVIRONMENT
============================================================

Use Python 3.11+ if available.

Use libraries:

pandas, numpy, polars, pyarrow, duckdb, requests, urllib3, beautifulsoup4, lxml, geopandas, shapely, pyproj, statsmodels, linearmodels, pyfixest, scipy, scikit-learn, matplotlib, openpyxl, xlsxwriter, jinja2, tqdm, python-dotenv, pyyaml, joblib

If some package cannot be installed, substitute an equivalent.

Create requirements.txt.

Use Parquet whenever practical for intermediate datasets.

Do not repeatedly download the same raw datasets.

Cache all downloads.

============================================================
SECTION 4
CONFIGURATION
============================================================

Create config/config.yaml with:

```yaml
project:
  name: "Local Tornado Mitigation and Economic Resilience"
  country: "United States"
  primary_geography: "county"
  preferred_frequency: "quarterly"

treatment:
  primary_definition: "strict"
  alternatives:
    - strict
    - moderate
    - broad

  treatment_dates:
    - completion
    - obligation
    - approval

  implementation_lags:
    - 0
    - 1
    - 2
    - 3

tornado:
  primary_definition: "EF1_plus"

  alternatives:
    - any_tornado
    - EF1_plus
    - EF2_plus
    - EF3_plus
    - tornado_count
    - maximum_intensity

event_study:
  quarterly_pre: 8
  quarterly_post: 12
  annual_pre: 5
  annual_post: 8
  reference_period: -1

inference:
  alpha: 0.05
  primary_cluster: "county"

  alternative_clusters:
    - state
    - county_time_two_way

primary_outcomes:
  - employment
  - separations
  - earnings
  - establishment_deaths
  - job_destruction

secondary_outcomes:
  - hires
  - new_hire_earnings
  - business_births
  - small_business_resilience
  - industry_reallocation
  - migration
  - building_permits
  - establishments
  - payroll
  - local_government_finance

robustness:
  robust_sign_share: 0.80
  moderate_sign_share: 0.65
  pretrend_threshold: 0.10
  placebo_threshold: 0.10
  leave_state_out_share: 0.80

power:
  alpha: 0.05
  target_power:
    - 0.80
    - 0.90

multiple_testing:
  methods:
    - benjamini_hochberg
    - holm
```

============================================================
SECTION 5
FEMA TREATMENT DATA
============================================================

Use OpenFEMA Hazard Mitigation Assistance project data.

First inspect current official OpenFEMA API metadata.

Do not hard-code obsolete field names.

Download all available relevant project records.

At minimum retain where available:

project identifier, subapplication identifier, grant identifier, state, state FIPS, county, county FIPS, city, community, subrecipient, project title, project description, project type, project category, grant program, federal share, local share, total project cost, benefit-cost ratio if available, approval date, obligation date, award date, completion date, closeout date, project status, disaster number, latitude, longitude

Save raw API responses or downloads.

Create:

data/raw/fema/fema_projects_raw.parquet

============================================================
SECTION 6
CLASSIFY FEMA PROJECTS
============================================================

Create three treatment definitions.

STRICT:

Only projects unambiguously related to tornado/severe-wind structural mitigation.

Examples: tornado safe room, community safe room, storm shelter, tornado shelter, severe wind shelter, wind retrofit, wind-resistant retrofit, wind hardening, tornado retrofit, structural wind retrofit, critical facility wind protection

MODERATE:

STRICT plus: safe rooms where tornado/severe wind is plausible, school safe rooms, community shelters, critical-facility wind retrofits, public building wind protection, roof strengthening, wind-resistant doors/windows, structural reinforcement for high winds

BROAD:

MODERATE plus structural projects related to wind/hurricane resistance where tornado/severe-wind protection is plausible.

Explicitly exclude from all baseline definitions:

planning grants, hazard mitigation plan writing, administrative costs, education/outreach only, flood-only acquisitions, flood elevation, wildfire projects, earthquake projects, drought, erosion-only projects, drainage-only projects, generators unless directly incorporated into an eligible tornado resilience definition, post-disaster debris removal, routine maintenance

Use classification evidence from: project type, project title, project description, grant program, project category

Create transparent regex dictionaries.

Save: config/treatment_keywords.csv

Columns: keyword, category, include_strict, include_moderate, include_broad, exclusion, notes

Classify each FEMA project.

Create fields: treat_strict, treat_moderate, treat_broad, classification_confidence, classification_reason, ambiguous_flag

Classification confidence: HIGH / MEDIUM / LOW

Randomly sample at least 500 classified projects for manual inspection.

Save: output/diagnostics/fema_classification_sample.xlsx

Also save all ambiguous projects.

============================================================
SECTION 7
TREATMENT TIMING
============================================================

Construct alternative treatment dates.

Preferred hierarchy:

1. actual completion date
2. project closeout date
3. obligation date + implementation lag
4. approval date + implementation lag

Never assume approval equals physical completion.

For obligation and approval dates create: lag 0, lag 1 year, lag 2 years, lag 3 years

Primary treatment timing:

Use completion date if completeness and plausibility are sufficient.

If fewer than 50% of otherwise usable projects have completion dates, do not make completion timing the only specification.

Construct: treated_strict_ct, treated_moderate_ct, treated_broad_ct

and: years_since_treatment, quarters_since_treatment

Treatment remains on after implementation.

Also construct: treatment_intensity_total_cost, treatment_intensity_federal_share, number_of_projects, per_capita_mitigation_spending

Do not use intensity as the only specification.

============================================================
SECTION 8
NOAA TORNADO DATA
============================================================

Use NOAA/NCEI Storm Events Database.

Download bulk Storm Events CSV files for all overlapping years.

Select: EVENT_TYPE == "Tornado"

Retain: BEGIN_DATE_TIME, END_DATE_TIME, STATE, STATE_FIPS, CZ_NAME, CZ_FIPS, CZ_TYPE, BEGIN_LAT, BEGIN_LON, END_LAT, END_LON, TOR_F_SCALE, INJURIES_DIRECT, INJURIES_INDIRECT, DEATHS_DIRECT, DEATHS_INDIRECT, DAMAGE_PROPERTY, DAMAGE_CROPS, EPISODE_ID, EVENT_ID

Correctly parse K, M, B and numeric damage suffixes.

Construct numerical tornado intensity:

EF0/F0 = 0, EF1/F1 = 1, EF2/F2 = 2, EF3/F3 = 3, EF4/F4 = 4, EF5/F5 = 5

Treat unknown intensity separately.

============================================================
SECTION 9
TORNADO EXPOSURE
============================================================

Construct county-quarter and county-year exposure.

Measures: any_tornado, tornado_count, EF1_plus, EF2_plus, EF3_plus, max_tornado_intensity, total_injuries, total_fatalities, reported_property_damage, reported_crop_damage

Main exposure: EF1_plus

Robustness exposures: any tornado, EF2+, EF3+, continuous tornado count, continuous maximum intensity

Important identification principle:

Reported property damage must NOT be used as the primary tornado exposure variable because mitigation itself can affect damage.

Property damage is a mechanism/outcome.

Where NOAA tornado start/end coordinates exist:

- create geographic tornado line paths
- intersect paths with county boundaries
- construct geographically precise county exposure

Compare coordinate/path-based exposure against NOAA county-zone exposure.

Save discrepancy diagnostics.

============================================================
SECTION 10
GEOGRAPHIC CROSSWALKS
============================================================

Build a county FIPS crosswalk.

Handle: county renaming, county consolidation, independent cities, Virginia independent cities, Alaska county equivalents, historical FIPS changes, South Dakota Shannon/Oglala Lakota change, Bedford City changes, other known historical changes

Use consistent modern or harmonized county geography.

Document every crosswalk rule.

Never silently combine counties.

============================================================
SECTION 11
QWI LABOR DATA
============================================================

Use Census Quarterly Workforce Indicators.

Use Census API.

Read CENSUS_API_KEY from .env.

If no key exists: print instructions and continue all analyses that do not require the key.

Download county-quarter QWI data.

At minimum variables where available: Emp, EmpBeg, EmpEnd, Sep, SepBeg, HirA, HirN, EarnS, EarnBeg, EarnHirAS, EarnHirNS, FrmJbGn, FrmJbLs, FrmJbC, TurnOvrS

Use correct official QWI variable definitions.

Do not infer variable meanings from names without checking Census metadata.

Retrieve geography: state, county

Retrieve industry at useful NAICS level where feasible.

Retrieve worker characteristics where feasible: sex, agegrp, education, race, ethnicity

Retrieve firm characteristics if practical: firmsize, firmage

Respect disclosure/suppression flags.

Suppressed values are missing, never zero.

============================================================
SECTION 12
QWI OUTCOMES
============================================================

Construct: employment, log_employment, employment_growth, separations, separation_rate, hires, hire_rate, new_hires, turnover, average_earnings, new_hire_earnings, beginning_employment, ending_employment

Compute rates with denominators justified using Census definitions.

Avoid constructing invalid ratios.

Store both raw and transformed versions.

============================================================
SECTION 13
BDS DATA
============================================================

Download Census Business Dynamics Statistics.

Use county/year datasets if available.

Variables to obtain where available: establishments, establishment births, establishment deaths, firm births, firm deaths, job creation, job destruction, net job creation, employment, startup measures

Also retrieve: firm size, firm age, industry — where geography/sample availability permits.

Create rates: establishment_birth_rate, establishment_death_rate, job_creation_rate, job_destruction_rate

Follow official Census definitions.

============================================================
SECTION 14
QCEW
============================================================

Download BLS Quarterly Census of Employment and Wages.

Use county × quarter × industry data.

At minimum: employment, average weekly wage, total wages, establishment count

Industry aggregation: Total private, Construction, Manufacturing, Retail, Transportation/Warehousing, Information, Finance, Professional Services, Education, Health, Leisure/Hospitality, Other Services

Use QCEW especially for industry mechanisms and replication of QWI employment results.

============================================================
SECTION 15
COUNTY BUSINESS PATTERNS
============================================================

Download Census County Business Patterns.

Retrieve: county, year, NAICS, establishment counts, employment, annual payroll, establishment size categories if available

Construct: log establishments, log employment, log payroll, small establishment share

Use annual county and county-industry panels.

============================================================
SECTION 16
IRS MIGRATION
============================================================

Download IRS county-to-county migration data.

Construct county-year: inflow_returns, inflow_exemptions, inflow_AGI, outflow_returns, outflow_exemptions, outflow_AGI

Then construct: net_migration_people, net_migration_returns, net_AGI_migration, outmigration_rate, inmigration_rate, mean_AGI_outmigrant, mean_AGI_inmigrant

Avoid double counting county-to-county flows.

============================================================
SECTION 17
BUILDING PERMITS
============================================================

Download Census Building Permits Survey.

Construct county or place-county measures: total housing units authorized, single family units, 2-4 unit structures, 5+ unit structures, total permits, permit valuation if consistently available

Aggregate place data to county where required using valid geographic mapping.

Clearly flag partial-coverage counties.

============================================================
SECTION 18
PUBLIC FINANCE
============================================================

Attempt to build publicly available local government fiscal outcomes using Census of Governments / Annual Survey of State and Local Government Finances.

Candidate outcomes: property tax revenue, total taxes, general revenue, own-source revenue, intergovernmental transfers, general expenditure, public safety expenditure, capital expenditure, debt

Important:

If county-level/local-government matching is not sufficiently consistent across years, mark this outcome MODERATE or LOW feasibility.

Do not manufacture a county panel.

============================================================
SECTION 19
OUTCOMES TO TEST
============================================================

Test every outcome below.

OUTCOME 1: Worker separations and job retention.
Main data: QWI. Main variables: Sep, separation rate, employment retention.
Hypothesis: Mitigation × Tornado < 0 for separations. Priority: VERY HIGH.

OUTCOME 2: Establishment survival and deaths.
Main data: BDS. Variables: establishment deaths, death rate, shutdowns if available.
Hypothesis: Mitigation × Tornado < 0. Priority: VERY HIGH.

OUTCOME 3: Job creation and job destruction.
Data: BDS; QWI if appropriate.
Primary prediction: Mitigation reduces tornado-induced job destruction. Priority: VERY HIGH.

OUTCOME 4: Employment recovery speed.
Data: QWI, QCEW. Construct quarterly dynamic outcomes. Estimate event time: -8 through +12 quarters.
Construct: recovery_4q, recovery_8q, recovery_12q, and time_to_95pct_recovery, time_to_100pct_recovery, time_to_pretrend_recovery.
Use pre-event trend rather than raw employment where feasible. Priority: VERY HIGH.

OUTCOME 5: Worker earnings.
QWI: average monthly earnings, new-hire earnings, earnings growth.
Hypothesis: mitigation reduces tornado-associated earnings losses.

OUTCOME 6: Distributional labor effects.
QWI demographic cells: sex, age, education, race, ethnicity. Test treatment protection separately.
Primary vulnerability groups: younger workers, older workers, lower-education workers, women, racial/ethnic minorities where sample size permits.
Do not over-interpret cells with high suppression.

OUTCOME 7: Hiring and new-hire earnings.
QWI: hires, hire rate, new hires, new-hire earnings.
Mechanism: If separations decrease but hires do not increase equivalently, mitigation appears to preserve existing worker-firm matches.

OUTCOME 8: Small-business resilience.
Data: BDS firm-size categories, CBP establishment-size categories, QWI firm-size groups if available.
Estimate: Mitigation × Tornado × SmallFirm. Test whether effects are stronger among small establishments.

OUTCOME 9: Industry reallocation.
QWI/QCEW/CBP. Test construction versus: retail, manufacturing, hospitality, health, professional services, transportation, other services.
Hypothesis: untreated areas may experience larger construction/rebuilding spikes and larger declines in normal local sectors.

OUTCOME 10: Business formation / entrepreneurship.
BDS. Measures: establishment births, firm startups, birth rate, startup rate.
Test short-run post-tornado reconstruction effects versus medium-run confidence effects.

OUTCOME 11: Migration.
IRS. Measures: outmigration, inmigration, net migration, AGI migration.
Hypothesis: mitigation reduces post-tornado population and income outflow.

OUTCOME 12: Housing/rebuilding.
Building Permits Survey. Measures: permits, single-family permits, multifamily permits, units authorized.
Interpret carefully: Mitigation may reduce immediate reconstruction permits while increasing longer-run investment.

OUTCOME 13: Local fiscal resilience.
Public finance. Measures: property taxes, own-source revenue, total revenue, capital spending, public safety expenditure.
Hypothesis: mitigation protects the tax base and reduces fiscal disruption.

OUTCOME 14: Establishment count and payroll.
CBP. Measures: establishments, employment, payroll.
Hypothesis: mitigation reduces business displacement/closure.

OUTCOME 15: Warning-induced economic shutdown costs.
First conduct feasibility analysis. Do NOT assume QWI/QCEW are high-frequency enough for individual warnings.
Search publicly available nationally scalable datasets such as: electricity load, traffic counts, airport operations, public mobility indicators, business opening indicators.
If no nationally scalable high-frequency outcome exists: FEASIBILITY = LOW or INFEASIBLE. Do not force a regression.

============================================================
SECTION 20
MASTER PANELS
============================================================

Create: county_quarter_panel.parquet, county_year_panel.parquet, county_industry_quarter_panel.parquet, county_industry_year_panel.parquet, county_demographic_quarter_panel.parquet

Each panel must include: county FIPS, state FIPS, time, treatment status, treatment date, years/quarters since treatment, treatment definition, tornado exposure measures, economic outcomes, controls, historical tornado exposure, baseline population, baseline employment

Check unique panel keys.

============================================================
SECTION 21
PREDETERMINED RISK
============================================================

Construct historical tornado risk using ONLY periods prior to treatment or an early fixed historical window.

Examples: historical tornado count, historical EF2+ count, historical average intensity

Never use future tornadoes to classify baseline risk.

Define tornado-prone samples: all counties, ever-tornado counties, above-median historical tornado risk, top tercile historical tornado risk

============================================================
SECTION 22
FEASIBILITY ANALYSIS
============================================================

Before causal regressions, assess feasibility quantitatively.

For every outcome compute: public_data_available, geographic_resolution, temporal_frequency, first_year, last_year, years_overlap_with_FEMA, number_observations, number_counties, treated_counties, treated_counties_with_post_treatment_tornado, post_treatment_tornado_events, untreated_tornado_controls, mean_pre_periods, mean_post_periods, missing_share, suppression_share, treatment_timing_quality, geographic_matching_quality

Construct feasibility score 0-100.

Scoring suggestion:

- PUBLIC DATA: 10 points
- GEOGRAPHIC RESOLUTION: county = 7, subcounty/county-industry = 10, state only = 2
- TEMPORAL FREQUENCY: monthly/higher = 10, quarterly = 9, annual = 6, irregular = 2
- TIME COVERAGE: 10
- TREATED SAMPLE SIZE: 15
- POST-TREATMENT TORNADO EVENTS: 15
- UNTREATED CONTROLS: 10
- MISSINGNESS/SUPPRESSION: 10
- TREATMENT TIMING COMPATIBILITY: 10

Maximum: 100.

Ratings: 80-100 EXCELLENT; 65-79 GOOD; 50-64 MODERATE; <50 LOW

Minimum thresholds: treated counties >= 30; treated post-treatment tornado events >= 30

If below thresholds, flag LOW POWER RISK.

Do not automatically drop outcome.

============================================================
SECTION 23
DESCRIPTIVE ANALYSIS
============================================================

Produce descriptive tables: treated versus untreated counties, pre-treatment characteristics, historical tornado exposure, population, employment, earnings, industry shares, business counts

Plot: number of treated counties over time, FEMA spending over time, tornado counts over time, geographic treatment map

Check treatment concentration by state.

Report top 10 states by: treated counties, project count, spending

============================================================
SECTION 24
PRIMARY CAUSAL MODEL
============================================================

Main model:

Y_c,t = beta * Mitigated_c,t * Tornado_c,t + gamma1 * Mitigated_c,t + gamma2 * Tornado_c,t + county FE + time FE + state × time FE + error

Primary coefficient: beta

Interpretation: change in tornado-induced economic disruption after mitigation becomes operational.

Use quarterly models for QWI/QCEW.

Use annual models for BDS/CBP/IRS/finance.

Cluster at county level.

Report: coefficient, standard error, t-statistic, p-value, 95% CI, sample size, counties, treated counties, tornado events, within R2

============================================================
SECTION 25
PRIMARY EMPIRICAL SPECIFICATION
============================================================

Quarterly baseline:

Y_cqt = beta(Mitigation_cqt × Tornado_cqt) + county FE + year-quarter FE + state × year-quarter FE + error

If state × quarter FE absorb important variation but remain estimable, retain them.

For county-industry data:

Y_ciqt = beta(Mitigation_cqt × Tornado_cqt) + county × industry FE + industry × time FE + state × time FE + error

For demographic QWI:

Y_cdqt = beta(Mitigation_cqt × Tornado_cqt) + county × demographic-group FE + demographic-group × time FE + state × time FE + error

============================================================
SECTION 26
STAGGERED ADOPTION
============================================================

Do NOT rely only on standard TWFE.

Estimate:

1. ordinary TWFE benchmark
2. Sun-Abraham-style cohort/event-time estimator if implementable
3. Callaway-Sant'Anna-style group-time ATT or equivalent
4. stacked event study
5. interaction-weighted estimator if appropriate

Report differences across estimators.

If estimates differ dramatically, downgrade robustness.

============================================================
SECTION 27
TORNADO EVENT STUDY
============================================================

The main dynamic causal design should study local economic responses surrounding tornado events.

Construct tornado event time: k = -8,-7,...,-2,-1,0,1,...,12 quarters. Reference: k=-1

Estimate separate response functions for: mitigated tornado events; non-mitigated comparable tornado events

Interaction model: EventTime_k × MitigationAtTornado

Plot coefficients with 95% CI.

Run joint test: all pre-event interaction coefficients = 0

Save: pretrend_F, pretrend_p

A strong result should show: little differential pretrend and smaller post-event deterioration after mitigation.

============================================================
SECTION 28
TREATMENT EVENT STUDY
============================================================

Also estimate economic outcomes around mitigation adoption itself.

Purpose: detect whether treated counties were already trending differently before mitigation.

Event time around mitigation: -8 to +12 quarters, or -5 to +8 years for annual outcomes.

This is a diagnostic.

Do not interpret unconditional post-treatment employment increases as causal evidence that mitigation creates jobs.

============================================================
SECTION 29
MATCHING AND WEIGHTING
============================================================

Construct pre-treatment comparison weights using: historical tornado risk, population, employment, earnings, income if available, urban/rural classification, industry structure, business counts, historical growth, region/state

Methods:

1. entropy balancing if available
2. inverse propensity score weighting
3. nearest-neighbor matching
4. Mahalanobis matching

Never use post-treatment variables in matching.

Check standardized mean differences before/after weighting.

Save balance plots.

Re-run main models.

============================================================
SECTION 30
MECHANISMS
============================================================

MECHANISM 1: Physical damage reduction.
Outcome: log(1 + reported_property_damage). Regressor: Mitigation × tornado intensity. Controls: county FE, time FE, state × time FE. Prediction: negative.
Do NOT use damage as tornado treatment intensity in this specification.

MECHANISM 2: Business continuity.
Compare sectors reliant on physical premises (manufacturing, retail, hospitality, health facilities) against relatively remote-capable sectors.
Estimate: Mitigation × Tornado × PhysicalPremiseIndustry

MECHANISM 3: Worker-firm match preservation.
Evidence supports this mechanism if: worker separations fall AND new hires do not rise equivalently AND/OR turnover declines.

MECHANISM 4: Small-business financial vulnerability.
Estimate: Mitigation × Tornado × SmallBusiness. Prediction: larger protective effects for small businesses.

MECHANISM 5: Critical facility protection.
Classify FEMA projects involving: schools, hospitals, emergency operations centers, fire stations, police, municipal buildings, community shelters.
Estimate heterogeneity by protected facility type.

MECHANISM 6: Severity gradient.
Estimate separately for: EF0, EF1, EF2, EF3+ or alternative bins.
Expected pattern: little effect when hazard is trivial; larger mitigation value at meaningful tornado severity; possible attenuation for catastrophic EF4/EF5 events if mitigation is overwhelmed.

============================================================
SECTION 31
HETEROGENEITY
============================================================

Test heterogeneity by: historical tornado risk, urban/rural status, population, income, baseline employment, region, state, industry, firm size, firm age, worker age, worker education, worker sex, worker race/ethnicity, FEMA project type, project spending per capita, number of mitigation projects, treatment vintage

Clearly label exploratory heterogeneity.

Correct for multiple testing within heterogeneity families.

============================================================
SECTION 32
ROBUSTNESS TESTS
============================================================

For every major outcome run all reasonable tests below.

- R01: strict treatment
- R02: moderate treatment
- R03: broad treatment
- R04: completion date treatment
- R05: obligation date treatment
- R06: approval date treatment
- R07: 0-year implementation lag
- R08: 1-year implementation lag
- R09: 2-year implementation lag
- R10: 3-year implementation lag
- R11: any tornado
- R12: EF1+
- R13: EF2+
- R14: EF3+
- R15: continuous tornado count
- R16: continuous max intensity
- R17: drop treatment year
- R18: drop first post-treatment year
- R19: drop first two post-treatment years
- R20: exclude projects awarded directly after major tornadoes
- R21: county FE + time FE
- R22: state × time FE
- R23: region × time FE
- R24: county-specific linear trends
- R25: population weighted
- R26: unweighted
- R27: winsorize dependent variable 1/99
- R28: IHS transformation
- R29: log transformation where valid
- R30: exclude largest metropolitan counties
- R31: tornado-prone sample
- R32: ever-tornado sample
- R33: matched sample
- R34: entropy-balanced sample
- R35: IPW sample
- R36: placebo future treatment
- R37: placebo historical treatment
- R38: pre-treatment fake tornado interactions
- R39: random treatment dates
- R40: permutation/randomization inference
- R41: leave-one-state-out
- R42: leave-one-major-tornado-out
- R43: cluster county
- R44: cluster state
- R45: two-way cluster county × time if feasible
- R46: exclude Oklahoma
- R47: exclude Texas
- R48: exclude highest-treatment state
- R49: exclude 2011 Super Outbreak period
- R50: exclude top 1% property damage tornadoes
- R51: control for hurricanes
- R52: control for floods
- R53: control for other severe storms
- R54: drop 2020
- R55: drop 2020-2021
- R56: drop 2008-2009
- R57: alternative historical-risk controls
- R58: alternative functional form
- R59: exclude counties with very few pre-period observations
- R60: restrict to counties observed continuously
- R61: exclude low-confidence FEMA classifications
- R62: only high-confidence FEMA classifications
- R63: only FEMA projects with observed completion dates
- R64: only safe-room projects
- R65: only structural wind retrofit projects
- R66: exclude safe rooms, keep structural retrofits
- R67: per-capita treatment intensity
- R68: project-count treatment intensity
- R69: continuous FEMA spending interaction
- R70: multiple-testing corrected inference

============================================================
SECTION 33
SPECIFICATION CURVE
============================================================

For each primary outcome construct specification-curve dataset.

Each row: outcome, specification_id, treatment_definition, treatment_date, implementation_lag, tornado_definition, sample, fixed_effects, weighting, clustering, coefficient, SE, pvalue, CI_low, CI_high, N, counties

Plot all coefficients sorted by magnitude.

Mark primary specification.

Do not treat obviously invalid specifications as robustness evidence.

Create a variable: credible_specification = 1/0

Only credible specifications count toward robustness classification.

============================================================
SECTION 34
ROBUSTNESS METRICS
============================================================

For each outcome calculate:

- primary_beta
- sign_consistency = share of credible robustness coefficients with same sign as primary_beta
- sig_consistency = share of credible specifications with p < 0.10 and same sign
- significant_5_share = share with p < 0.05 and same sign
- median_beta
- median_absolute_beta
- median_beta_ratio = median(beta_robustness / primary_beta) after removing numerically pathological ratios
- CI_consistency = share of specifications whose 95% confidence interval does not imply a large effect in the opposite direction
- pretrend_pass = 1 if pretrend joint p > 0.10
- placebo_pass = 1 if placebo tests show no comparable pre-treatment effect
- leave_state_out_sign_share = share of leave-one-state-out estimates matching primary sign
- leave_state_out_pass = 1 if >= 0.80
- treatment_definition_pass = 1 if strict, moderate and broad produce directionally similar estimates
- timing_definition_pass = 1 if conclusions reasonably survive timing choices
- hazard_definition_pass = 1 if conclusions survive reasonable tornado severity choices
- matching_pass = 1 if weighted/matched results are similar
- estimator_pass = 1 if modern staggered estimators support baseline conclusion

============================================================
SECTION 35
ROBUSTNESS CLASSIFICATION
============================================================

ROBUST — use only when: sign_consistency >= 0.80 AND pretrend_pass == 1 AND placebo_pass == 1 AND leave_state_out_pass == 1 AND treatment_definition_pass == 1 AND no single state or tornado drives results AND modern staggered-treatment estimators are directionally supportive AND confidence intervals imply an economically meaningful effect or are precise enough to reject a substantively large opposite effect. Statistical significance alone is insufficient.

MODERATELY ROBUST — if: sign_consistency >= 0.65 AND no major pretrend failure AND core treatment/exposure definitions support same direction BUT precision or some secondary specifications vary.

MIXED — if: sign_consistency between 0.50 and 0.65 OR different reasonable treatment definitions materially change results OR statistical significance is highly specification-dependent OR timing assumptions materially alter conclusions.

NOT ROBUST — if: sign_consistency < 0.50 OR strong pretrends OR placebo effects look similar to main effect OR one state/event drives result OR modern DiD estimates contradict naive TWFE.

NO DETECTABLE EFFECT — if: point estimates are consistently near zero AND confidence intervals are sufficiently narrow to reject economically meaningful effects.

UNDERPOWERED — if: confidence intervals include economically important protective and adverse effects.

INFEASIBLE — if: public data cannot reliably identify treatment/outcome.

============================================================
SECTION 36
ECONOMIC SIGNIFICANCE
============================================================

For every estimate report: beta, standard error, p-value, 95% confidence interval, baseline mean, baseline standard deviation, beta as percent of mean, beta as percent of SD

Where meaningful compute: jobs retained, separations avoided, establishment deaths avoided, job destruction avoided, earnings preserved, outmigration avoided

Do not exaggerate aggregate effects.

============================================================
SECTION 37
POWER ANALYSIS
============================================================

For every outcome calculate: number treated counties, number treated tornado events, residual variance, cluster count, approximate minimum detectable effect

MDE at: 80% power, 90% power

Report MDE: raw units, percent outcome mean, standard deviations

Classify: WELL POWERED / MODERATELY POWERED / UNDERPOWERED

Use cluster-aware approximations where practical.

============================================================
SECTION 38
MULTIPLE TESTING
============================================================

Primary confirmatory outcomes:

1. worker separations
2. employment
3. earnings
4. establishment deaths
5. job destruction

Secondary outcomes are exploratory unless otherwise stated.

For each family report: raw p-value, Benjamini-Hochberg q-value, Holm-adjusted p-value

Construct standardized resilience indices: labor_market_resilience_index, business_resilience_index, household_resilience_index, fiscal_resilience_index

Use: equal-weight standardized index and, if practical, inverse covariance weighted index.

============================================================
SECTION 39
LITERATURE SEARCH
============================================================

Conduct a structured literature search before claiming novelty.

Search: Google Scholar if accessible, OpenAlex, Semantic Scholar, Crossref, NBER, RePEc, IZA, SSRN, journal websites, working-paper repositories

Search phrases:

"tornado mitigation employment", "tornado mitigation labor market", "tornado safe room employment", "FEMA mitigation employment", "FEMA mitigation labor market", "hazard mitigation employment", "hazard mitigation worker separations", "disaster mitigation worker separations", "disaster mitigation establishment survival", "FEMA HMGP establishment survival", "FEMA HMGP employment", "tornado establishment deaths", "tornado business survival", "tornado firm survival", "tornado job destruction", "tornado worker earnings", "tornado local labor market", "safe room economic effects", "wind retrofit economic effects", "wind retrofit labor market", "hazard mitigation migration", "hazard mitigation local finance", "hazard mitigation business dynamics", "natural disaster mitigation business survival"

For every relevant paper record: title, authors, year, journal, working paper status, DOI, URL, treatment, hazard, geography, outcome, identification strategy, main result, degree of overlap

Save: output/literature/literature_overlap.csv, output/literature/literature_review.md

Novelty classifications:

- HIGH: No close causal mitigation paper studies the same economic outcome.
- MEDIUM: Disaster-outcome literature exists but mitigation link appears absent.
- LOW: A close causal study already estimates essentially the same treatment-outcome relationship.

Do not write "this has never been studied" unless supported by unusually comprehensive evidence.

Preferred wording: "I found no close causal study in the searched economics/public-policy literature."

============================================================
SECTION 40
PUBLICATION POTENTIAL SCORE
============================================================

Publication probability cannot be objectively estimated.

Instead construct a transparent publication-potential heuristic. Total: 100 points.

- IDENTIFICATION QUALITY: 30 points (credible source of variation, pretrend quality, comparison group, treatment timing, modern estimator consistency, selection concerns)
- NOVELTY: 20 points
- DATA QUALITY: 15 points
- RESULT STRENGTH: 15 points
- MECHANISM EVIDENCE: 10 points
- POLICY IMPORTANCE: 10 points

Penalties:

- -10 severe pretrends
- -10 unclear treatment completion timing
- -10 result driven by one state
- -10 fewer than 30 treated post-treatment tornado events
- -10 major multiple-testing fragility
- -10 weak/no control group
- -10 inconsistent staggered-DiD result
- -5 high data suppression
- -5 ambiguous FEMA classification

Do not double count penalties unreasonably.

Score interpretation:

- 90-100: potentially exceptional field-level contribution, potentially broader if identification is unusually strong
- 80-89: strong field-journal potential
- 70-79: good field-journal potential
- 60-69: specialized/regional journal potential
- 50-59: interesting but significant redesign likely required
- <50: unlikely to be publishable in target economics/public-policy outlets without major redesign

Never increase publication score merely because p < 0.05.

============================================================
SECTION 41
JOURNAL FIT
============================================================

Assess fit among: Journal of Environmental Economics and Management, Journal of Policy Analysis and Management, Journal of Human Resources, Journal of Urban Economics, Labour Economics, ILR Review, Regional Science and Urban Economics, Journal of Regional Science, Land Economics, Economic Inquiry, Small Business Economics, Journal of Housing Economics, National Tax Journal, Review of Regional Studies, Natural Hazards Review, Risk Analysis

Rank: HIGH FIT / MEDIUM FIT / LOW FIT

Do not provide acceptance probabilities.

For each outcome state what would be required for the highest-ranked journal to become realistic.

Examples:

- JEEM: strong quasi-experimental identification, clear environmental adaptation contribution, clean event-study evidence, economic significance, mechanisms
- JPAM: strong public-program evaluation, credible policy counterfactual, distributional or implementation relevance
- JHR: major labor-market contribution, worker-level mechanism, extremely strong identification
- JUE: strong spatial/local equilibrium or migration contribution
- Labour Economics / ILR: clear labor-market mechanism and worker heterogeneity
- RSUE/JRS: credible local economic resilience contribution

============================================================
SECTION 42
QUASI-EXPERIMENT SEARCH
============================================================

Investigate FEMA institutional rules.

Search for: benefit-cost ratio thresholds, project scoring cutoffs, BRIC score thresholds, funding exhaustion, state allocation rules, federal disaster declaration eligibility, cost-share rule changes, application ranking, rejected versus accepted subapplications, grant program changes

Use FEMA HMA Subapplications data if publicly available.

Identify whether funded and unfunded applicants can be compared.

Potential designs: regression discontinuity, rank-based cutoff, difference-in-differences around rule changes, instrument based on funding exhaustion, close-score winner/loser comparison

Do NOT claim a quasi-experiment unless program rules actually support it.

Create: output/final/quasi_experiment_assessment.md

Include: institutional rule, running variable, cutoff, sample size, manipulation risk, balance test feasibility, whether RD is credible, whether IV is credible, recommended use

============================================================
SECTION 43
PLACEBO TESTS
============================================================

Run:

- future mitigation status × current tornado
- fake treatment dates
- pre-treatment tornado × future mitigation
- randomized treatment counties within state/risk group
- randomized treatment years
- outcomes that should theoretically not respond immediately where appropriate

A convincing project should show placebo effects substantially smaller than actual post-treatment effects.

============================================================
SECTION 44
LEAVE-ONE-STATE-OUT
============================================================

For every primary outcome: loop over states, remove one state, re-estimate primary coefficient.

Store: state_removed, beta, SE, pvalue

Plot coefficients.

Calculate sign stability.

Highlight whether Oklahoma, Texas, Alabama, Mississippi, Missouri, Kansas, Arkansas, Iowa, Tennessee or another individual state drives results.

============================================================
SECTION 45
LEAVE-ONE-EVENT-OUT
============================================================

Identify top tornado episodes by: fatalities, EF intensity, reported damage

For major episodes, re-estimate excluding each one.

Check whether Joplin, Tuscaloosa, Moore, 2011 Super Outbreak, or other large events drive results.

Do not manually choose events based on coefficient changes.

Use predetermined top-event criteria.

============================================================
SECTION 46
COVID AND MACRO SHOCKS
============================================================

Estimate sensitivity excluding: 2020; 2020-2021; also 2008-2009.

State × time fixed effects should absorb many macro shocks.

If sample extends across COVID, include explicit discussion.

============================================================
SECTION 47
ADDITIONAL CONTROLS
============================================================

Only where needed and not endogenous.

Potential controls: county population, lagged employment, historical tornado risk, urban/rural classification

Avoid "bad controls" potentially affected by mitigation.

Fixed effects are preferred.

============================================================
SECTION 48
PRE-ANALYSIS SNAPSHOT
============================================================

Before estimating outcomes create: output/final/preregistration_snapshot.md

State:

- primary treatment = strict FEMA tornado/wind mitigation
- primary treatment date = completion when observed, otherwise obligation + 2 years
- primary tornado definition = EF1+
- primary sample = counties with tornado exposure potential / full contiguous-US sample as defined before outcomes
- primary outcomes = employment, separations, earnings, establishment deaths, job destruction
- primary fixed effects = county FE, state × time FE
- primary cluster = county
- primary event window = -8 to +12 quarters

Do not modify these after viewing results except when data limitations make them impossible.

Any modifications must be explicitly labeled.

============================================================
SECTION 49
TABLES
============================================================

- Table 1: FEMA treatment summary
- Table 2: Treated vs control characteristics
- Table 3: Outcome feasibility
- Table 4: Main labor-market results
- Table 5: Business dynamics results
- Table 6: Migration/housing/fiscal results
- Table 7: Mechanisms
- Table 8: Heterogeneity
- Table 9: Robustness summary
- Table 10: Multiple-testing adjustment
- Table 11: Power analysis
- Table 12: Publication assessment

============================================================
SECTION 50
MASTER OUTCOME TABLE
============================================================

Create: output/final/master_outcome_assessment.csv, output/final/master_outcome_assessment.xlsx, output/final/master_outcome_assessment.md

Required columns:

Rank, Outcome, Outcome_Family, Dataset, Frequency, Geography, Years, Observations, Counties, Treated_Counties, PostTreatment_Tornado_Events, Untreated_Tornado_Events, Feasibility_Score, Feasibility_Rating, Primary_Beta, Primary_SE, Primary_P, BH_Q_Value, Holm_P, CI_Lower, CI_Upper, Outcome_Mean, Outcome_SD, Effect_Percent_Mean, Effect_SD, Expected_Sign, Observed_Sign, Main_Result, Mechanism_Result, Pretrend_P, Placebo_P, Sign_Consistency, Sig_Consistency, Leave_State_Out_Sign_Share, Treatment_Definition_Pass, Timing_Pass, Hazard_Definition_Pass, Estimator_Pass, Matching_Pass, Robust_Specs, Total_Credible_Specs, Robustness_Rating, Power_Rating, Novelty_Rating, Identification_Rating, Data_Quality_Rating, Publication_Score, Best_Journal_Fit, Second_Journal_Fit, Third_Journal_Fit, Key_Limitation, Recommendation

Main_Result allowed values: Protective, Adverse, No detectable effect, Underpowered, Infeasible

Robustness_Rating allowed values: ROBUST, MODERATELY ROBUST, MIXED, NOT ROBUST, NO DETECTABLE EFFECT, UNDERPOWERED, INFEASIBLE

============================================================
SECTION 51
HUMAN-READABLE FINAL TABLE
============================================================

| Rank | Outcome | Feasibility | Primary result | Effect size | p-value | q-value | Pretrend | Robust? | Mechanism supported? | Power | Novelty | Publication potential | Best journal | Recommendation |

Sort by:

1. identification credibility
2. robustness
3. publication potential
4. feasibility

Do NOT rank by p-value.

============================================================
SECTION 52
FIGURES
============================================================

- Figure 1: Map of FEMA tornado/wind mitigation projects
- Figure 2: Number of treated counties over time
- Figure 3: FEMA mitigation spending over time
- Figure 4: Tornado exposure map
- Figure 5: Tornado events over time
- Figure 6: Employment event study
- Figure 7: Worker separation event study
- Figure 8: Earnings event study
- Figure 9: Establishment death estimates
- Figure 10: Job destruction estimates
- Figure 11: Severity gradient
- Figure 12: Small business heterogeneity
- Figure 13: Industry heterogeneity
- Figure 14: Worker demographic heterogeneity
- Figure 15: Leave-one-state-out plot
- Figure 16: Specification curve for separations
- Figure 17: Specification curve for employment
- Figure 18: Specification curve for establishment deaths
- Figure 19: Treatment-definition sensitivity
- Figure 20: Publication potential versus feasibility scatter plot

All causal plots must show confidence intervals.

============================================================
SECTION 53
PAPER BUNDLES
============================================================

PAPER A: LABOR MARKET RESILIENCE
Primary: worker separations. Secondary: employment, earnings, hires, new-hire earnings, turnover. Heterogeneity: worker demographics, industry. Mechanism: worker-firm match preservation. Potential journals: JEEM, JPAM, Labour Economics, ILR Review, RSUE

PAPER B: BUSINESS RESILIENCE
Primary: establishment deaths, job destruction. Secondary: births, startups, employment, payroll, small-business effects. Mechanisms: physical damage, liquidity constraints, industry dependence. Potential journals: JEEM, RSUE, Journal of Regional Science, Small Business Economics

PAPER C: SPATIAL/FISCAL RESILIENCE
Primary possibilities: migration, building permits, local fiscal outcomes. Potential journals: JUE if extremely strong spatial contribution, Land Economics, Journal of Housing Economics, National Tax Journal, RSUE

For each bundle provide: research question, primary outcome, secondary outcomes, identification, strongest result, weakest result, mechanisms, robustness, publication potential, best journal, main threat, GO / MAYBE / NO-GO

============================================================
SECTION 54
PUBLICATION ASSESSMENT
============================================================

For every paper bundle answer:

1. Is the central result statistically distinguishable from zero?
2. Is it economically meaningful?
3. Does it survive modern DiD estimators?
4. Does it survive alternative treatment timing?
5. Does it survive alternative tornado definitions?
6. Does it survive leave-one-state-out?
7. Does it pass pretrend tests?
8. Does it pass placebo tests?
9. Is there mechanism evidence?
10. Is novelty high?
11. Is statistical power adequate?
12. Is treatment assignment sufficiently credible?

Then calculate publication score.

Do not treat statistical significance as sufficient.

============================================================
SECTION 55
NO P-HACKING RULES
============================================================

Never:

- choose treatment definition because it gives p < .05
- choose EF threshold because it gives p < .05
- choose an event window based on desired coefficients
- drop states solely because they weaken significance
- exclude tornadoes solely because they weaken significance
- hide null outcomes
- hide adverse-sign results
- interpret suppressed QWI data as zero
- report only one treatment date
- report only one fixed-effect structure
- report only TWFE when treatment timing is staggered

Use all pre-specified primary outcomes.

Clearly separate: confirmatory analyses, robustness analyses, exploratory analyses

============================================================
SECTION 56
DATA VALIDATION
============================================================

Every dataset must be validated.

Check: duplicate panel observations, missing county FIPS, invalid county FIPS, invalid dates, unexpected year gaps, negative employment, negative establishment counts, duplicate FEMA project IDs, duplicate NOAA event IDs, FEMA completion before approval, FEMA obligation before approval if inconsistent, treatment dates outside dataset, tornado intensity parsing errors, QWI disclosure/suppression, BDS suppressions, industry code inconsistencies

Create validation reports.

If errors are found, fix transparently and log.

============================================================
SECTION 57
LOGGING
============================================================

Each script must log: execution timestamp, script name, data URLs, API endpoints, download date, dataset vintage, rows downloaded, rows retained, columns, missingness, errors, warnings

Save logs to: output/logs/

Maintain: output/logs/data_sources.csv

Columns: dataset, source_name, official_URL, download_URL, API_endpoint, retrieval_date, coverage_start, coverage_end, notes

============================================================
SECTION 58
REPRODUCIBILITY
============================================================

Create run_all.py that runs the pipeline in dependency order.

Support: `python src/run_all.py` or from root: `python run_all.py`

Use cached raw data.

Add command-line options: --download, --clean, --build, --estimate, --robustness, --report, --all

Set random seeds.

Write README instructions.

============================================================
SECTION 59
FAILURE HANDLING
============================================================

Do not stop because one data endpoint changes.

If an endpoint fails:

1. inspect current official documentation
2. identify replacement endpoint
3. update code
4. log change
5. continue

If one outcome is unavailable: mark it INFEASIBLE; continue remaining outcomes.

If Census API key is missing: continue FEMA/NOAA and feasibility tasks that do not require it and clearly list what requires the key.

============================================================
SECTION 60
FINAL RESEARCH REPORT
============================================================

Generate: output/final/research_assessment.md

Structure:

1. Executive Summary
2. Research Question
3. FEMA Policy/Treatment Definition
4. Data
5. Feasibility
6. Identification Strategy
7. Treatment Timing
8. Main Results
9. Labor-Market Results
10. Business Results
11. Migration/Housing/Fiscal Results
12. Dynamic Event Studies
13. Pre-Trends
14. Mechanisms
15. Heterogeneity
16. Robustness
17. Placebos
18. Leave-One-State-Out
19. Multiple Testing
20. Statistical Power
21. Literature Novelty
22. Publication Potential
23. Journal Fit
24. Identification Threats
25. Best Paper Design
26. Alternative Paper Designs
27. Data Improvements That Would Matter Most
28. Final GO/NO-GO Recommendation

Explicitly answer:

- A. Which outcome has the strongest credible causal result?
- B. Which outcome is most statistically robust?
- C. Which outcome has the largest economically meaningful effect?
- D. Which outcome has the best combination of novelty and feasibility?
- E. Which outcome has the highest publication potential?
- F. Which promising outcome is underpowered?
- G. Which apparent effects disappear under robustness testing?
- H. Are results driven by Oklahoma or Texas?
- I. Are results driven by the 2011 Super Outbreak or another major event?
- J. Does treatment timing matter?
- K. Does the strict treatment definition survive?
- L. Are results present for EF2+ tornadoes?
- M. Do modern staggered-DiD estimators confirm naive TWFE?
- N. Are pretrends acceptable?
- O. Do placebo tests pass?
- P. Is FEMA completion timing reliable enough for causal inference?
- Q. Is there convincing evidence of the proposed mechanism?
- R. Is treatment adoption too endogenous for credible publication?
- S. Would a FEMA funding cutoff or close applicant comparison materially improve identification?
- T. What is the best paper to write?

============================================================
SECTION 61
FINAL DECISION RULE
============================================================

End the report with exactly one overall project recommendation:

GO — use only if: at least one economically important outcome is ROBUST or strongly MODERATELY ROBUST AND identification is credible AND pretrends/placebos are acceptable AND power is adequate.

GO WITH REDESIGN — use if: economically interesting results exist BUT treatment timing, selection, control group, or identification requires improvement.

PILOT ONLY — use if: data are feasible but estimates are underpowered or unstable.

NO-GO — use if: treatment cannot be reliably measured or public outcome data cannot support credible inference.

Never choose GO based only on statistical significance.

============================================================
SECTION 62
FIRST-STAGE FEASIBILITY BEFORE EXPENSIVE DOWNLOADS
============================================================

Before downloading every QWI/BDS/CBP file, first perform a lightweight pilot.

- STEP 1: Download FEMA treatment data.
- STEP 2: Classify strict/moderate/broad projects.
- STEP 3: Report: number of projects, number of treated counties, number of treated states, median treatment year, projects by state, projects by type
- STEP 4: Download NOAA tornado data.
- STEP 5: Count: treated counties ever hit after treatment, treated counties hit by EF1+, treated counties hit by EF2+, treated counties hit by EF3+, number of post-treatment tornado events, number of potential untreated controls
- STEP 6: Create output/final/preliminary_feasibility.md with table:

| Treatment definition | Treated counties | Post-treatment tornado counties | Any tornado events | EF1+ events | EF2+ events | EF3+ events | Assessment |

- STEP 7: If strict treatment generates fewer than 20 post-treatment tornado-treated counties: do NOT abandon automatically. Investigate: moderate definition, longer sample, wind retrofit categories, safe-room definition, treatment intensity, state-level concentration. Then explain limitations.

============================================================
SECTION 63
OUTCOME FEASIBILITY TABLE
============================================================

Before estimation produce:

| Outcome | Dataset | Public? | Geography | Frequency | Years overlap | Treated counties | Post-treatment tornado events | Missingness | Suppression | Feasibility score | Feasibility |

Include all 15 outcome groups.

============================================================
SECTION 64
RESULT TABLE
============================================================

After estimation produce:

| Outcome | Primary beta | SE | p-value | BH q-value | Effect % mean | 95% CI | Expected sign | Observed result | Pretrend p | Placebo p | Sign consistency | Leave-state-out consistency | Robustness | Power | Mechanism | Novelty | Publication score | Best journal |

============================================================
SECTION 65
INTERPRETATION RULES
============================================================

Do not say "mitigation caused employment to increase" unless identification supports that statement.

Prefer: "the estimated tornado-associated decline in employment is smaller in counties after mitigation."

Distinguish: prevention, resilience, recovery, reconstruction

A mitigation program may not increase average local employment but can reduce losses conditional on hazard realization.

============================================================
SECTION 66
WARNING SYSTEM ALTERNATIVE
============================================================

The policy description may be referring either to:

A. physical retrofitting/mitigation, or
B. local tornado warning systems.

The primary project described above concerns A.

However, add a separate appendix: output/final/warning_system_feasibility.md

Assess whether local warning-system adoption can be measured.

Potential treatment variables: tornado siren adoption, Wireless Emergency Alerts, NWS warning technology, local emergency alert systems, NOAA Weather Radio, StormReady certification, local warning-system upgrades

Search whether adoption dates can be measured nationally.

If no credible national adoption panel exists, state that clearly.

Potential warning-system outcomes: fatalities, injuries, traffic activity, electricity load, business operations, airport operations, school closures, emergency calls

Assess whether high-frequency economic outcomes are publicly available.

Do not combine warning-system and retrofit treatment unless empirically justified.

============================================================
SECTION 67
PUBLICATION CHANCE INTERPRETATION
============================================================

Never output a fake acceptance probability such as "JEEM: 35% chance".

Instead output publication potential: HIGH / MEDIUM-HIGH / MEDIUM / LOW, and explain why.

Possible mapping: 85+ HIGH; 75-84 MEDIUM-HIGH; 60-74 MEDIUM; <60 LOW

============================================================
SECTION 68
GOAL OF THE PROJECT
============================================================

The purpose is not to maximize statistically significant outcomes.

The purpose is to discover whether there is a credible, novel and publishable empirical relationship between tornado mitigation and local economic resilience.

A null result can still be valuable if: design is credible; confidence intervals are narrow; the literature expects economically meaningful benefits; the result rules out substantial labor-market benefits.

============================================================
SECTION 69
DELIVERABLE SUMMARY
============================================================

1. Complete reproducible Python code.
2. README with execution instructions.
3. Public data-source log.
4. FEMA classified treatment dataset.
5. Tornado exposure panel.
6. Economic outcome panels.
7. Feasibility table.
8. Primary regression tables.
9. Event-study figures.
10. Mechanism tests.
11. Heterogeneity tests.
12. All robustness estimates.
13. Specification curves.
14. Placebo tests.
15. Leave-one-state-out results.
16. Power analysis.
17. Multiple-testing-adjusted results.
18. Literature overlap table.
19. Publication-potential table.
20. Journal-fit table.
21. Master outcome assessment.
22. Paper bundle recommendations.
23. Final GO / GO WITH REDESIGN / PILOT ONLY / NO-GO decision.

============================================================
SECTION 70
REQUIRED MASTER TABLE
============================================================

The single most important deliverable is: output/final/master_outcome_assessment.xlsx and the matching output/final/master_outcome_assessment.md

It must include all outcomes and clearly state: FEASIBILITY, PRIMARY RESULT, PRIMARY EFFECT SIZE, STATISTICAL PRECISION, ROBUSTNESS, MECHANISM SUPPORT, POWER, NOVELTY, IDENTIFICATION QUALITY, PUBLICATION POTENTIAL, BEST JOURNAL, RECOMMENDATION

Never leave "robustness" based solely on p-values.

============================================================
SECTION 71
START EXECUTION
============================================================

Perform the following in order:

1. Create the directory structure.
2. Create requirements.txt.
3. Create config.yaml.
4. Create .env.example containing: CENSUS_API_KEY=
5. Build FEMA downloader.
6. Inspect current OpenFEMA metadata.
7. Download FEMA project records.
8. Build FEMA classification.
9. Build strict/moderate/broad treatment definitions.
10. Download NOAA tornado data.
11. Construct county-level tornado exposure.
12. Produce preliminary feasibility counts.
13. Display the preliminary feasibility table.
14. Continue into QWI/BDS/QCEW/CBP/IRS/building-permit/public-finance acquisition.
15. Build master panels.
16. Run feasibility analysis.
17. Freeze preregistration_snapshot.md.
18. Run primary models.
19. Run event studies.
20. Run mechanisms.
21. Run heterogeneity.
22. Run robustness.
23. Run placebos.
24. Run power analysis.
25. Run multiple-testing correction.
26. Run literature search.
27. Create publication scores.
28. Create journal-fit analysis.
29. Generate tables and figures.
30. Generate final research report.

Do not stop because an individual outcome is infeasible. Continue with all remaining outcomes.

At the very end print this table directly in the terminal:

| Rank | Outcome | Feasibility | Primary result | Effect % mean | p-value | q-value | Pretrend | Robustness | Power | Mechanism | Novelty | Publication score | Best journal | Recommendation |

Then print:

- BEST OVERALL OUTCOME: [answer]
- BEST PAPER: [answer]
- STRONGEST MECHANISM: [answer]
- MOST ROBUST RESULT: [answer]
- BEST JOURNAL TARGET: [answer]
- BIGGEST IDENTIFICATION THREAT: [answer]
- WHAT WOULD MOST IMPROVE THE PAPER: [answer]
- FINAL PROJECT DECISION: GO / GO WITH REDESIGN / PILOT ONLY / NO-GO
