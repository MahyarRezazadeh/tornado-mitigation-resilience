# Research Assessment: Local Tornado Mitigation and Economic Resilience

Generated from pipeline outputs. Primary specification frozen in `preregistration_snapshot.md`.

## 1. Executive Summary

**Bottom line.** Public data are more than sufficient to *run* this design (867 strict-treated counties, ~3,200
post-treatment EF1+ county-quarters, 1,900 untreated tornado-hit controls; 12 of 15 outcome groups rate EXCELLENT
feasibility), but the central resilience hypothesis is **not supported** at the county level:

1. **An EF1+ tornado leaves no detectable footprint on county aggregates.** Across all 28 outcomes the tornado main
   effect (unmitigated counties) is near zero and insignificant (e.g. log employment +0.09%, separation rate
   +0.00004). The distributed-lag event studies show no post-tornado employment dip and no recovery path to speak of.
   With no measurable disruption, there is nothing for mitigation to offset. This dilution of a 1-2 km-wide damage path
   in a county-wide aggregate is the binding constraint, not sample size.
2. **Labor-market outcomes: no protective effect.** Separations are a precise null (beta = +0.0005, 95% CI
   [-0.0011, +0.0020] vs E* = 0.0025; pretrend p = 0.23, placebo p = 0.93, RI p = 0.50, LOSO sign share 1.00) and are
   classified NO DETECTABLE EFFECT. Employment, earnings and hires are UNDERPOWERED: CIs cannot exclude a
   0.05 within-county-SD effect in either direction.
3. **Business outcomes: no protective effect; the consistent signs point the *wrong* way.** Small-firm (1-19)
   establishment deaths (beta = +0.10 pp, p = 0.10; stacked p = 0.04, IW p = 0.02; 98% sign consistency) and QWI firm job
   destruction (p = 0.07) are MODERATELY ROBUST in the *adverse* direction, but neither survives multiple-testing
   correction (BH q = 0.22 and 0.39). The most plausible reading is selection: HMGP safe rooms go to counties right
   after major disasters (94% HMGP; 44% after tornado/severe-storm declarations), which are on weaker trajectories.
   The only protective-signed significant result, CBP establishments (+0.7%), fails the stacked pretrend test
   (p = 0.019) and is NOT ROBUST.
4. **Physical damage is the one economically large signal, and it is not yet credible.** Mitigated counties report
   ~42% less property damage per EF step (p < 1e-6), robust to definitions, timing, dropping FL/OK/TX, safe-room-only,
   state clustering, and to a within-treated design that drops the 5 pre-treatment years (about -58% to -60%). But
   (i) before treatment, future-treated counties reported ~40-50% MORE damage per EF step than never-treated counties
   (placebo p < 1e-4), i.e. strong selection on damage; (ii) the EF rating is itself assigned from observed damage, so
   "intensity" is partly an outcome of mitigation; (iii) the pre/post comparison spans the 2007 F-to-EF change and
   changes in NWS damage-estimation practice. Fatalities are not reduced (within-treated +0.02 to +0.04 log points, p <= 0.02).
5. **Multiple testing and indices.** No confirmatory outcome survives BH or Holm correction (all q >= 0.58); the
   labor, business and household resilience indices are all insignificant (p = 0.05-0.95).

Feasible, but the county-quarter resilience design cannot answer the question it was built for. The informative null
on separations and the damage signal justify a redesign, not a paper in the current form.


**Final decision: GO WITH REDESIGN**

## 2. Research Question

Do ex-ante FEMA-funded tornado/severe-wind mitigation investments (safe rooms, wind retrofits) reduce the economic disruption caused by subsequent tornadoes? The estimand is Mitigation x subsequent tornado exposure (resilience), not mitigation -> unconditional growth.

## 3. FEMA Policy / Treatment Definition

# Table 1. FEMA tornado/wind mitigation treatment summary (funded projects, contiguous US, county-identified)

| Definition   |   Projects |   Counties |   States |   Federal share ($M) |   Total cost ($M) |   Safe-room projects |   Wind-retrofit projects |   HIGH confidence share |   Median primary-timing year |   Timing = obligation+2y |   HMGP share |   Post tornado/severe-storm declaration share |
|:-------------|-----------:|-----------:|---------:|---------------------:|------------------:|---------------------:|-------------------------:|------------------------:|-----------------------------:|-------------------------:|-------------:|----------------------------------------------:|
| strict       |       5056 |        869 |       37 |               2653.7 |            4032.3 |                 3180 |                     1876 |                   0.991 |                         2014 |                    0.833 |        0.942 |                                         0.435 |
| moderate     |       5144 |        880 |       37 |               2785.2 |            4226.6 |                 3180 |                     1876 |                   0.974 |                         2014 |                    0.834 |        0.943 |                                         0.427 |
| broad        |       5818 |       1094 |       45 |               3433.1 |            5184.1 |                 3180 |                     1876 |                   0.861 |                         2014 |                    0.81  |        0.948 |                                         0.441 |

Classification rules: `config/treatment_keywords.csv`; manual-check sample: `output/diagnostics/fema_classification_sample.xlsx`.

## 4. Data

| dataset                    | source_name                                                         | coverage_start         | coverage_end   | notes                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
|:---------------------------|:--------------------------------------------------------------------|:-----------------------|:---------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| fema_projects_raw          | OpenFEMA HazardMitigationAssistanceProjects v4                      | nan                    | nan            | 56410 records; paged $top=10000                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| fema_subapplications_raw   | OpenFEMA HmaSubapplications v2                                      | nan                    | nan            | 63593 records; paged $top=10000                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| fema_fin_transactions_raw  | OpenFEMA HazardMitigationAssistanceProjectsFinancialTransactions v1 | nan                    | nan            | 78621 records; paged $top=10000                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| fema_disaster_declarations | OpenFEMA DisasterDeclarationsSummaries v2                           | 1953                   | present        | Used for incidentType of disaster linked to HMGP projects                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| noaa_storm_events          | NOAA NCEI Storm Events Database (details files)                     | 1950                   | 2025           | latest c-stamp per year; 1950:20260323;1951:20260323;1952:20260323;1953:20260323;1954:20260323;1955:20260323;1956:20260323;1957:20260323;1958:20260323;1959:20260323;1960:20260323;1961:20260323;1962:20260323;1963:20260323;1964:20260323;1965:20260323;1966:20260323;1967:20260323;1968:20260323;1969:20260323;1970:20260323;1971:20260323;1972:20260323;1973:20260323;1974:20260323;1975:20260323;1976:20260323;1977:20260323;1978:20260323;1979:20260323;1980:20260323;1981:20260323;1982:20260323;1983:20260323;1984:20260527;1985:20260323;1986:20260323;1987:20260323;1988:20260323;1989:20260323;1990:20260323;1991:20260323;1992:20260323;1993:20260323;1994:20260323;1995:20260323;1996:20260323;1997:20260323;1998:20260323;1999:20260323;2000:20260323;2001:20260323;2002:20260323;2003:20260323;2004:20260323;2005:20260323;2006:20260323;2007:20260323;2008:20260323;2009:20260323;2010:20260323;2011:20260323;2012:20260323;2013:20260323;2014:20260323;2015:20260323;2016:20260323;2017:20260519;2018:20260323;2019:20260323;2020:20260323;2021:20260323;2022:20260625;2023:20260323;2024:20260728;2025:20260819 |
| bds                        | Census Business Dynamics Statistics 2023 release                    | 1978                   | 2023           | county total, county x firm size (fzc), firm age (fac), sector                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| census_cb_county_2020      | Census cartographic boundary counties 2020 (500k)                   | 2020                   | 2020           | harmonized geography; contiguous US + DC                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| census_popest              | Census county population estimates (intercensal/postcensal)         | 1990                   | 2024           | nan                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| omb_cbsa_2020              | OMB 2020 CBSA delineation (Census list1_2020)                       | 2020                   | 2020           | metro = Metropolitan SA county                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| public_finance_probe       | Census Annual Survey of State & Local Gov Finances                  | 1992                   | 2018           | full-census years only [1992, 1997, 2002, 2007, 2012, 2017]; annual years are samples -> no consistent annual county panel                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| qwi_api_cells              | Census QWI API (se, rh, sa endpoints)                               | 1990                   | 2025           | education E1-E4; race A1/A2; Hispanic; firmsize 1-5; ownercode A05; industry total                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| irs_migration              | IRS SOI U.S. Population Migration Data (county)                     | 2011-2012              | outflow2223    | filing-year pairs; files: inflow1112,outflow1112,inflow1213,outflow1213,inflow1314,outflow1314,inflow1415,outflow1415,inflow1516,outflow1516,inflow1617,outflow1617,inflow1718,outflow1718,inflow1819,outflow1819,inflow1920,outflow1920,inflow2021,outflow2021,inflow2122,outflow2122,inflow2223,outflow2223                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| building_permits           | Census Building Permits Survey (county annual)                      | 1990                   | 2025           | county totals include imputation for non-reporting places; coverage flag from reporting                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| literature_apis            | OpenAlex, Crossref, Semantic Scholar APIs                           | nan                    | nan            | 24 phrases; 1152 raw hits                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| cbp                        | Census County Business Patterns (county files)                      | 1998                   | 2023           | total + 2-digit NAICS; size classes                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| qcew                       | BLS Quarterly Census of Employment and Wages (open data slices)     | 2014                   | 2025           | county x quarter x 12 industry groups; private ownership (own 5) + total covered (own 0)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| qwi                        | Census LEHD Quarterly Workforce Indicators (R latest_release)       | state-specific (1990s) | latest release | sa_f_gc_ns_op_u; private ownership; filtered extract kept (raw >5GB not retained)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |

## 5. Feasibility

| Outcome                               | Dataset                                                      | Public?   | Geography             | Frequency   |   Years overlap |   Treated counties |   Post-treatment tornado events |   Missingness |   Suppression |   Feasibility score | Feasibility   |
|:--------------------------------------|:-------------------------------------------------------------|:----------|:----------------------|:------------|----------------:|-------------------:|--------------------------------:|--------------:|--------------:|--------------------:|:--------------|
| Worker separations and job retention  | QWI                                                          | Yes       | county                | quarterly   |              36 |                867 |                            3183 |          0.21 |          0.01 |                89.8 | EXCELLENT     |
| Establishment survival and deaths     | BDS                                                          | Yes       | county                | annual      |              34 |                867 |                            2153 |          0.02 |          0.02 |                89.7 | EXCELLENT     |
| Job creation and job destruction      | BDS                                                          | Yes       | county                | annual      |              34 |                867 |                            2154 |          0    |          0    |                90   | EXCELLENT     |
| Employment recovery speed             | QWI                                                          | Yes       | county                | quarterly   |              36 |                867 |                            3185 |          0.2  |          0.01 |                89.9 | EXCELLENT     |
| Worker earnings                       | QWI                                                          | Yes       | county                | quarterly   |              36 |                867 |                            3183 |          0.21 |          0.02 |                89.7 | EXCELLENT     |
| Distributional labor effects          | QWI (sa bulk; se/rh/firmsize API)                            | Yes       | county-demographic    | quarterly   |              36 |                867 |                            3183 |          0.21 |          0.02 |                92.7 | EXCELLENT     |
| Hiring and new-hire earnings          | QWI                                                          | Yes       | county                | quarterly   |              36 |                867 |                            3183 |          0.21 |          0.01 |                89.8 | EXCELLENT     |
| Small-business resilience             | BDS                                                          | Yes       | county                | annual      |              34 |                867 |                            2153 |          0.02 |          0    |                89.8 | EXCELLENT     |
| Industry reallocation                 | QWI industry groups (+QCEW 2014+, CBP)                       | Yes       | county-industry       | quarterly   |              36 |                867 |                            3183 |          0.21 |          0.06 |                92.3 | EXCELLENT     |
| Business formation / entrepreneurship | BDS                                                          | Yes       | county                | annual      |              34 |                867 |                            2151 |          0.02 |          0.02 |                89.7 | EXCELLENT     |
| Migration                             | IRS                                                          | Yes       | county                | annual      |              12 |                869 |                            1815 |          0.01 |          0    |                84.7 | EXCELLENT     |
| Housing/rebuilding                    | BPS                                                          | Yes       | county                | annual      |              36 |                862 |                            2564 |          0.04 |          0    |                89.6 | EXCELLENT     |
| Local fiscal resilience               | Census Annual Survey of Local Govt Finances                  | Yes       | county (sample-based) | irregular   |               6 |                  0 |                               0 |          0.8  |               |                22.4 | LOW           |
| Establishment count and payroll       | CBP                                                          | Yes       | county                | annual      |              26 |                869 |                            2153 |          0    |          0    |                90   | EXCELLENT     |
| Warning-induced shutdown costs        | none nationally scalable (see warning_system_feasibility.md) | No        | none                  | irregular   |             nan |                nan |                             nan |               |               |                 0   | INFEASIBLE    |

## 6. Identification Strategy

Primary: Y = b*M*T + g1*M + g2*T + county FE + state x time FE, clustered by county (Section 24). b compares the tornado-associated change in Y in counties whose mitigation is operational with the tornado-associated change elsewhere in the same state and period. Dynamic: distributed-lag tornado event study (k=-8..12 quarters), stacked clean-event study with same-state controls, stacked mitigation-cohort triple difference, interaction-weighted cohort average; mitigation-adoption event studies (TWFE, Sun-Abraham, two-stage imputation) as diagnostics; entropy balancing, IPW, NN and Mahalanobis matching.

## 7. Treatment Timing

No. OpenFEMA publishes no physical completion date (0% coverage). Closeout is observed for 88.8% of strict projects (median 3.6 years after obligation) and is an administrative upper bound on completion. Primary timing is therefore a proxy.

| definition   |   projects |   share_completion |   share_closeout |   share_last_payment |   share_obligation |   share_approval |   share_primary_nonmissing |   median_oblig_to_close_yrs |   median_approval_to_close_yrs |   median_primary_year |
|:-------------|-----------:|-------------------:|-----------------:|---------------------:|-------------------:|-----------------:|---------------------------:|----------------------------:|-------------------------------:|----------------------:|
| strict       |       5541 |                  0 |            0.888 |                0.879 |              0.82  |            0.871 |                          1 |                       3.578 |                          3.524 |                  2014 |
| moderate     |       5630 |                  0 |            0.882 |                0.879 |              0.821 |            0.871 |                          1 |                       3.581 |                          3.526 |                  2014 |
| broad        |       6390 |                  0 |            0.879 |                0.866 |              0.799 |            0.859 |                          1 |                       3.544 |                          3.472 |                  2014 |

## 8. Main Results



| Outcome                                        |   Primary beta |      SE |   p-value |   BH q-value |   Effect % mean | 95% CI            | Expected sign   | Observed result      |   Pretrend p |   Placebo p |   Sign consistency |   Leave-state-out consistency | Robustness           | Power              | Mechanism                                  | Novelty   |   Publication score | Best journal                                    |
|:-----------------------------------------------|---------------:|--------:|----------:|-------------:|----------------:|:------------------|:----------------|:---------------------|-------------:|------------:|-------------------:|------------------------------:|:---------------------|:-------------------|:-------------------------------------------|:----------|--------------------:|:------------------------------------------------|
| Job destruction rate (QWI firm job loss)       |        0.00075 | 0.00042 |     0.073 |        0.392 |            1.26 | [-0.0001, 0.0016] | -               | Adverse              |        0.632 |       0.996 |               0.98 |                               | MODERATELY ROBUST    | WELL POWERED       | n/a                                        | HIGH      |                57.5 | Regional Science and Urban Economics (HIGH FIT) |
| Small-firm establishment death rate (BDS 1-19) |        0.10031 | 0.06078 |     0.099 |        0.223 |            0.89 | [-0.0189, 0.2195] | -               | Adverse              |        0.383 |       0.85  |               0.98 |                               | MODERATELY ROBUST    | UNDERPOWERED       | M4 small-firm diff b=0.121 (p=0.14)        | HIGH      |                56.5 | Small Business Economics (HIGH FIT)             |
| Job destruction rate (BDS)                     |        0.11068 | 0.10667 |     0.3   |        0.584 |            0.84 | [-0.0985, 0.3198] | -               | Underpowered         |        0.277 |       0.672 |               0.93 |                          1    | UNDERPOWERED         | MODERATELY POWERED | M4 small-firm diff b=0.0399 (p=0.79)       | HIGH      |                51.5 | Risk Analysis (HIGH FIT)                        |
| Hire rate                                      |       -0.00112 | 0.00087 |     0.195 |        0.392 |           -0.52 | [-0.0028, 0.0006] | 0               | Underpowered         |        0.604 |       0.979 |               0.9  |                          1    | UNDERPOWERED         | WELL POWERED       | M3 not supported (separations not reduced) | HIGH      |                50.5 | Risk Analysis (HIGH FIT)                        |
| Housing units authorized (IHS)                 |       -0.00722 | 0.02438 |     0.767 |        0.848 |           -0.16 | [-0.0550, 0.0406] | 0               | Underpowered         |        0.278 |       0.039 |               0.97 |                               | UNDERPOWERED         | MODERATELY POWERED | n/a                                        | MEDIUM    |                45.4 | Risk Analysis (HIGH FIT)                        |
| Out-migration rate                             |        0.03174 | 0.02143 |     0.139 |        0.713 |            0.53 | [-0.0103, 0.0738] | -               | Underpowered         |        0.883 |       0.457 |               0.97 |                          1    | UNDERPOWERED         | MODERATELY POWERED | n/a                                        | MEDIUM    |                44.7 | Risk Analysis (HIGH FIT)                        |
| Worker separations (rate)                      |        0.00047 | 0.00078 |     0.542 |        0.677 |            0.22 | [-0.0010, 0.0020] | -               | No detectable effect |        0.226 |       0.932 |               0.89 |                          1    | NO DETECTABLE EFFECT | WELL POWERED       | M3 not supported (separations not reduced) | HIGH      |                55.5 | Regional Science and Urban Economics (HIGH FIT) |
| Employment (log end-of-quarter)                |        0.00119 | 0.00345 |     0.731 |        0.731 |            0.01 | [-0.0056, 0.0080] | +               | Underpowered         |        0.888 |       0.653 |               0.71 |                          0.96 | UNDERPOWERED         | MODERATELY POWERED | M3 not supported (separations not reduced) | HIGH      |                48.5 | Risk Analysis (HIGH FIT)                        |
| Establishment deaths (exit rate)               |        0.04373 | 0.04679 |     0.35  |        0.584 |            0.47 | [-0.0480, 0.1355] | -               | Underpowered         |        0.735 |       0.593 |               0.85 |                          1    | UNDERPOWERED         | MODERATELY POWERED | M4 small-firm diff b=0.121 (p=0.14)        | HIGH      |                47.5 | Risk Analysis (HIGH FIT)                        |
| Earnings (log avg monthly; stable)             |       -0.00168 | 0.00177 |     0.342 |        0.584 |           -0.02 | [-0.0052, 0.0018] | +               | Underpowered         |        0.053 |       0.742 |               0.87 |                          1    | UNDERPOWERED         | UNDERPOWERED       | n/a                                        | HIGH      |                47.5 | Risk Analysis (HIGH FIT)                        |
| Establishments (CBP log)                       |        0.00744 | 0.00325 |     0.022 |        0.1   |            0.12 | [0.0011, 0.0138]  | +               | Protective           |        0.019 |       0.712 |               0.95 |                          1    | NOT ROBUST           | UNDERPOWERED       | n/a                                        | HIGH      |                22.5 | Small Business Economics (MEDIUM FIT)           |
| Employment retention                           |       -0.0003  | 0.00041 |     0.455 |        0.531 |           -0.04 | [-0.0011, 0.0005] | +               | No detectable effect |              |             |                    |                               | NO DETECTABLE EFFECT | WELL POWERED       | n/a                                        | HIGH      |                42.5 | Regional Science and Urban Economics (HIGH FIT) |
| In-migration rate                              |        0.01368 | 0.0282  |     0.628 |        0.848 |            0.22 | [-0.0416, 0.0690] | 0               | No detectable effect |              |             |                    |                               | NO DETECTABLE EFFECT | WELL POWERED       | n/a                                        | MEDIUM    |                37.5 | Regional Science and Urban Economics (HIGH FIT) |
| Job creation rate (BDS)                        |        0.15951 | 0.09005 |     0.077 |        0.223 |            1.15 | [-0.0170, 0.3361] | 0               | Protective           |              |             |                    |                               | MIXED                | MODERATELY POWERED | n/a                                        | HIGH      |                39.5 | Risk Analysis (HIGH FIT)                        |
| Establishment deaths (log count)               |        0.01961 | 0.00641 |     0.002 |        0.02  |            0.49 | [0.0070, 0.0322]  | -               | Adverse              |              |             |                    |                               | MIXED                | MODERATELY POWERED | n/a                                        | HIGH      |                39.5 | Risk Analysis (HIGH FIT)                        |
| Employment (QCEW log; 2014+)                   |       -0.00025 | 0.00209 |     0.904 |        0.904 |           -0    | [-0.0044, 0.0039] | +               | Underpowered         |        0.995 |       0.326 |               0.64 |                               | UNDERPOWERED         | MODERATELY POWERED | n/a                                        | HIGH      |                41.5 | Risk Analysis (HIGH FIT)                        |
| New-hire rate                                  |       -0.00073 | 0.00068 |     0.28  |        0.393 |           -0.41 | [-0.0021, 0.0006] | 0               | Underpowered         |              |             |                    |                               | UNDERPOWERED         | WELL POWERED       | n/a                                        | HIGH      |                37.5 | Risk Analysis (HIGH FIT)                        |
| Turnover (stable)                              |       -0.00037 | 0.0003  |     0.224 |        0.392 |           -0.35 | [-0.0010, 0.0002] | -               | Underpowered         |              |             |                    |                               | UNDERPOWERED         | UNDERPOWERED       | M3 not supported (separations not reduced) | HIGH      |                37.5 | Risk Analysis (HIGH FIT)                        |
| New-hire earnings (log)                        |       -0.00449 | 0.00287 |     0.118 |        0.392 |           -0.06 | [-0.0101, 0.0011] | +               | Underpowered         |              |             |                    |                               | UNDERPOWERED         | MODERATELY POWERED | n/a                                        | HIGH      |                37.5 | Risk Analysis (HIGH FIT)                        |
| Employment (CBP log)                           |        0.0046  | 0.00443 |     0.299 |        0.539 |            0.05 | [-0.0041, 0.0133] | +               | Underpowered         |              |             |                    |                               | UNDERPOWERED         | MODERATELY POWERED | n/a                                        | HIGH      |                36.5 | Risk Analysis (HIGH FIT)                        |
| Payroll (CBP log)                              |        0.00123 | 0.00537 |     0.819 |        0.819 |            0.01 | [-0.0093, 0.0118] | +               | Underpowered         |              |             |                    |                               | UNDERPOWERED         | MODERATELY POWERED | n/a                                        | HIGH      |                36.5 | Risk Analysis (HIGH FIT)                        |
| Small-establishment share (CBP <20)            |       -0.00022 | 0.00037 |     0.555 |        0.624 |           -0.02 | [-0.0010, 0.0005] | +               | Underpowered         |              |             |                    |                               | UNDERPOWERED         | MODERATELY POWERED | n/a                                        | HIGH      |                36.5 | Risk Analysis (HIGH FIT)                        |
| Establishment birth rate                       |       -0.02961 | 0.04698 |     0.529 |        0.624 |           -0.3  | [-0.1217, 0.0625] | 0               | Underpowered         |              |             |                    |                               | UNDERPOWERED         | MODERATELY POWERED | n/a                                        | HIGH      |                36.5 | Risk Analysis (HIGH FIT)                        |
| Startup rate (age-0 firms' estabs)             |       -0.02593 | 0.03919 |     0.508 |        0.624 |           -0.4  | [-0.1028, 0.0509] | 0               | Underpowered         |              |             |                    |                               | UNDERPOWERED         | MODERATELY POWERED | n/a                                        | HIGH      |                36.5 | Risk Analysis (HIGH FIT)                        |
| Single-family units (IHS)                      |       -0.02031 | 0.02329 |     0.383 |        0.848 |           -0.46 | [-0.0660, 0.0254] | 0               | Underpowered         |              |             |                    |                               | UNDERPOWERED         | MODERATELY POWERED | n/a                                        | MEDIUM    |                32.5 | Risk Analysis (HIGH FIT)                        |
| Multifamily units (IHS)                        |        0.05168 | 0.04066 |     0.204 |        0.713 |            2.39 | [-0.0280, 0.1314] | 0               | Underpowered         |              |             |                    |                               | UNDERPOWERED         | MODERATELY POWERED | n/a                                        | MEDIUM    |                32.5 | Risk Analysis (HIGH FIT)                        |
| Net migration rate                             |       -0.01655 | 0.03249 |     0.61  |        0.848 |           -6.65 | [-0.0803, 0.0471] | +               | Underpowered         |              |             |                    |                               | UNDERPOWERED         | UNDERPOWERED       | n/a                                        | MEDIUM    |                32.5 | Risk Analysis (HIGH FIT)                        |
| Out-migrant AGI (log)                          |       -0.00105 | 0.00543 |     0.848 |        0.848 |           -0.01 | [-0.0117, 0.0096] | -               | Underpowered         |              |             |                    |                               | UNDERPOWERED         | UNDERPOWERED       | n/a                                        | MEDIUM    |                32.5 | Risk Analysis (HIGH FIT)                        |
| Local fiscal resilience                        |                |         |           |              |                 |                   | nan             | Infeasible           |              |             |                    |                               | INFEASIBLE           | nan                | nan                                        | nan       |                     | nan                                             |
| Warning-induced shutdown costs                 |                |         |           |              |                 |                   | nan             | Infeasible           |              |             |                    |                               | INFEASIBLE           | nan                | nan                                        | nan       |                     | nan                                             |



## 9. Labor-Market Results

| outcome                                  |     beta |      se |       p |   ci_low |   ci_high |   gamma_T |   effect_pct_mean |      N |   treated_counties |   treated_tornado_obs |
|:-----------------------------------------|---------:|--------:|--------:|---------:|----------:|----------:|------------------:|-------:|-------------------:|----------------------:|
| Worker separations (rate)                |  0.00047 | 0.00078 | 0.54157 | -0.00105 |   0.002   |   4e-05   |           0.22246 | 352841 |                867 |                  3183 |
| Employment retention                     | -0.0003  | 0.00041 | 0.45521 | -0.0011  |   0.00049 |  -0.00014 |          -0.03535 | 352761 |                867 |                  3183 |
| Job destruction rate (QWI firm job loss) |  0.00075 | 0.00042 | 0.0734  | -7e-05   |   0.00157 |   0.00011 |           1.25803 | 352949 |                867 |                  3183 |
| Employment (log end-of-quarter)          |  0.00119 | 0.00345 | 0.73073 | -0.00558 |   0.00796 |   0.00089 |           0.01344 | 356048 |                867 |                  3185 |
| Employment (QCEW log; 2014+)             | -0.00025 | 0.00209 | 0.9037  | -0.00436 |   0.00385 |  -0.00021 |          -0.00284 | 148426 |                869 |                  2477 |
| Earnings (log avg monthly; stable)       | -0.00168 | 0.00177 | 0.34176 | -0.00516 |   0.00179 |  -0.00095 |          -0.0211  | 352963 |                867 |                  3183 |
| New-hire earnings (log)                  | -0.00449 | 0.00287 | 0.11811 | -0.01011 |   0.00114 |   0.0011  |          -0.05934 | 340437 |                867 |                  3173 |
| Hire rate                                | -0.00112 | 0.00087 | 0.19549 | -0.00282 |   0.00058 |  -0.00028 |          -0.52188 | 352851 |                867 |                  3183 |
| New-hire rate                            | -0.00073 | 0.00068 | 0.28044 | -0.00207 |   0.0006  |  -0.00039 |          -0.40688 | 343498 |                867 |                  3175 |
| Turnover (stable)                        | -0.00037 | 0.0003  | 0.22411 | -0.00096 |   0.00023 |   0.00044 |          -0.35422 | 346182 |                867 |                  3169 |

## 10. Business Results

| outcome                                        |     beta |      se |       p |   ci_low |   ci_high |   gamma_T |   effect_pct_mean |      N |   treated_counties |   treated_tornado_obs |
|:-----------------------------------------------|---------:|--------:|--------:|---------:|----------:|----------:|------------------:|-------:|-------------------:|----------------------:|
| Establishment deaths (exit rate)               |  0.04373 | 0.04679 | 0.3501  | -0.04802 |   0.13548 |   0.0175  |           0.46611 | 103769 |                867 |                  2153 |
| Establishment deaths (log count)               |  0.01961 | 0.00641 | 0.00223 |  0.00705 |   0.03218 |   0.00035 |           0.48828 | 103782 |                867 |                  2153 |
| Job destruction rate (BDS)                     |  0.11068 | 0.10667 | 0.29954 | -0.09847 |   0.31982 |   0.03809 |           0.84063 | 105307 |                867 |                  2154 |
| Job creation rate (BDS)                        |  0.15951 | 0.09005 | 0.07659 | -0.01705 |   0.33607 |  -0.01006 |           1.1457  | 105312 |                867 |                  2154 |
| Small-firm establishment death rate (BDS 1-19) |  0.10031 | 0.06078 | 0.09896 | -0.01886 |   0.21949 |   0.02765 |           0.89158 | 103496 |                867 |                  2153 |
| Small-establishment share (CBP <20)            | -0.00022 | 0.00037 | 0.5546  | -0.00095 |   0.00051 |   5e-05   |          -0.02483 |  80739 |                869 |                  2153 |
| Establishment birth rate                       | -0.02961 | 0.04698 | 0.52863 | -0.12173 |   0.06251 |   0.01225 |          -0.2994  | 103698 |                867 |                  2151 |
| Startup rate (age-0 firms' estabs)             | -0.02593 | 0.03919 | 0.5083  | -0.10276 |   0.05091 |  -0.00306 |          -0.39545 | 102087 |                867 |                  2144 |
| Establishments (CBP log)                       |  0.00744 | 0.00325 | 0.02225 |  0.00106 |   0.01382 |   9e-05   |           0.11531 |  80739 |                869 |                  2153 |
| Employment (CBP log)                           |  0.0046  | 0.00443 | 0.2995  | -0.00409 |   0.0133  |   0.0012  |           0.05177 |  80305 |                869 |                  2153 |
| Payroll (CBP log)                              |  0.00123 | 0.00537 | 0.81853 | -0.0093  |   0.01176 |   0.00173 |           0.00999 |  80305 |                869 |                  2153 |

## 11. Migration/Housing/Fiscal Results

| outcome                        |     beta |      se |       p |   ci_low |   ci_high |   gamma_T |   effect_pct_mean |      N |   treated_counties |   treated_tornado_obs |
|:-------------------------------|---------:|--------:|--------:|---------:|----------:|----------:|------------------:|-------:|-------------------:|----------------------:|
| Out-migration rate             |  0.03174 | 0.02143 | 0.13864 | -0.01028 |   0.07376 |   0.00708 |           0.52547 |  36925 |                869 |                  1815 |
| Net migration rate             | -0.01655 | 0.03249 | 0.61044 | -0.08025 |   0.04715 |  -0.02825 |          -6.65281 |  36746 |                869 |                  1815 |
| In-migration rate              |  0.01368 | 0.0282  | 0.62754 | -0.04161 |   0.06898 |  -0.01966 |           0.21746 |  36746 |                869 |                  1815 |
| Out-migrant AGI (log)          | -0.00105 | 0.00543 | 0.84753 | -0.0117  |   0.00961 |   0.00701 |          -0.01006 |  36907 |                869 |                  1815 |
| Housing units authorized (IHS) | -0.00722 | 0.02438 | 0.76725 | -0.05502 |   0.04059 |   0.00693 |          -0.15747 | 107690 |                862 |                  2564 |
| Single-family units (IHS)      | -0.02031 | 0.02329 | 0.38339 | -0.06598 |   0.02537 |   0.00726 |          -0.46418 | 107690 |                862 |                  2564 |
| Multifamily units (IHS)        |  0.05168 | 0.04066 | 0.2038  | -0.02804 |   0.1314  |  -0.00413 |           2.39345 | 107690 |                862 |                  2564 |

Local fiscal outcomes: LOW feasibility; not estimated (no consistent annual county panel).

## 12. Dynamic Event Studies

| outcome                  | freq   |   pretrend_F |   pretrend_p |   post_joint_F |   post_joint_p |   pretrend_unmitigated_p |      N |   mean_post_diff |   mean_post_unmitigated |   avg_post_diff_se |   adoption_pre_mean_twfe |   adoption_pre_mean_sa |   adoption_post_mean_twfe |   adoption_post_mean_sa |   adoption_pretrend_F |   adoption_pretrend_p |
|:-------------------------|:-------|-------------:|-------------:|---------------:|---------------:|-------------------------:|-------:|-----------------:|------------------------:|-------------------:|-------------------------:|-----------------------:|--------------------------:|------------------------:|----------------------:|----------------------:|
| hire_rate                | q      |       0.7806 |       0.6035 |         1.2171 |         0.2596 |                   0.0006 | 352851 |          -0.0003 |                  0.0002 |             0.0002 |                   0.0011 |                -0      |                    0.0013 |                  0.0005 |                1.2468 |                0.2732 |
| log_earnings             | q      |       1.9918 |       0.0526 |         1.5009 |         0.1088 |                   0.8287 | 352963 |          -0.0028 |                 -0      |             0.0005 |                   0.0037 |                -0.0026 |                   -0.0014 |                  0.0009 |                2.2435 |                0.0282 |
| log_employment           | q      |       0.4241 |       0.8878 |         1.2109 |         0.264  |                   0.1829 | 356048 |           0.002  |                  0.0011 |             0.0009 |                  -0.0027 |                -0.0061 |                    0.0059 |                  0.0065 |                1.1721 |                0.3153 |
| separation_rate          | q      |       1.3414 |       0.2263 |         1.283  |         0.2152 |                   0.2085 | 352841 |          -0.0001 |                  0.0002 |             0.0002 |                  -0.0003 |                 0.0005 |                    0.0002 |                 -0.0009 |                0.8464 |                0.5486 |
| establishment_death_rate | y      |       0.5004 |       0.7354 |         0.4129 |         0.929  |                   0.1712 | 103769 |          -0.0155 |                  0.0025 |             0.0179 |                   0.102  |                 0.1148 |                    0.0525 |                  0.052  |                0.7296 |                0.5717 |
| job_destruction_rate     | y      |       1.2751 |       0.2774 |         0.4946 |         0.8791 |                   0.4218 | 105307 |           0.0041 |                 -0.0104 |             0.0386 |                  -0.144  |                -0.0638 |                   -0.2008 |                 -0.1305 |                0.2956 |                0.881  |
| job_destruction_rate_qwi | q      |       0.7469 |       0.6322 |         0.9091 |         0.5427 |                   0.0853 | 352949 |           0.0002 |                 -0      |             0.0001 |                  -0.0005 |                -0.0007 |                   -0.0003 |                 -0.0006 |                1.3724 |                0.2124 |
| log_qcew_emp             | q      |       0.1409 |       0.995  |         1.1882 |         0.281  |                   0.4026 | 148426 |           0.0002 |                  0.0003 |             0.0007 |                  -0.0037 |                -0.0014 |                   -0.0006 |                  0.0041 |                1.049  |                0.3943 |

Recovery metrics:

| outcome                  |   unmitigated_recovery_4q |   unmitigated_recovery_8q |   unmitigated_recovery_12q |   unmitigated_time_to_95pct_recovery |   unmitigated_time_to_100pct_recovery |   unmitigated_time_to_pretrend_recovery |   unmitigated_trough |   unmitigated_trough_k |   mitigated_recovery_4q |   mitigated_recovery_8q |   mitigated_recovery_12q |   mitigated_trough |   mitigated_trough_k |   mitigated_time_to_95pct_recovery |   mitigated_time_to_100pct_recovery |   mitigated_time_to_pretrend_recovery |   unmitigated_recovery_1y |   unmitigated_recovery_2y |   unmitigated_recovery_4y |   mitigated_recovery_1y |   mitigated_recovery_2y |   mitigated_recovery_4y |
|:-------------------------|--------------------------:|--------------------------:|---------------------------:|-------------------------------------:|--------------------------------------:|----------------------------------------:|---------------------:|-----------------------:|------------------------:|------------------------:|-------------------------:|-------------------:|---------------------:|-----------------------------------:|------------------------------------:|--------------------------------------:|--------------------------:|--------------------------:|--------------------------:|------------------------:|------------------------:|------------------------:|
| log_employment           |                    0.0011 |                   -0.0001 |                     0.0006 |                                    1 |                                     1 |                                     nan |              -0.0001 |                      8 |                  0.0017 |                  0.0012 |                   0.0047 |             0.0012 |                    8 |                                nan |                                 nan |                                   nan |                  nan      |                  nan      |                  nan      |                nan      |                nan      |                nan      |
| separation_rate          |                   -0.0006 |                   -0.0003 |                    -0.0007 |                                    1 |                                     1 |                                       1 |               0.0011 |                     11 |                  0.0007 |                  0.0001 |                   0.0003 |             0.0007 |                    4 |                                  2 |                                   2 |                                     2 |                  nan      |                  nan      |                  nan      |                nan      |                nan      |                nan      |
| log_earnings             |                    0.0004 |                    0.0002 |                     0.0002 |                                    2 |                                     2 |                                       2 |              -0.0011 |                      0 |                 -0.0029 |                 -0.0035 |                  -0.0023 |            -0.0045 |                   10 |                                nan |                                 nan |                                   nan |                  nan      |                  nan      |                  nan      |                nan      |                nan      |                nan      |
| hire_rate                |                   -0.001  |                   -0.0015 |                    -0.0013 |                                    3 |                                     3 |                                       2 |               0.0015 |                      1 |                 -0.001  |                 -0.0015 |                  -0.0007 |             0.0011 |                    5 |                                  1 |                                   1 |                                     1 |                  nan      |                  nan      |                  nan      |                nan      |                nan      |                nan      |
| establishment_death_rate |                  nan      |                  nan      |                   nan      |                                    1 |                                     1 |                                       0 |               0.028  |                      7 |                nan      |                nan      |                 nan      |             0.0638 |                    0 |                                  1 |                                   1 |                                     1 |                    0.0122 |                   -0.0024 |                   -0.0222 |                 -0.0302 |                 -0.0179 |                 -0.0735 |
| job_destruction_rate     |                  nan      |                  nan      |                   nan      |                                    2 |                                     2 |                                       1 |               0.0343 |                      0 |                nan      |                nan      |                 nan      |             0.1431 |                    0 |                                  3 |                                   3 |                                     3 |                    0.0035 |                   -0.0109 |                   -0.0312 |                  0.0851 |                  0.0204 |                  0.0163 |
| job_destruction_rate_qwi |                    0.0001 |                    0.0001 |                    -0.0001 |                                    1 |                                     1 |                                     nan |               0.0007 |                     11 |                  0.0009 |                  0.0007 |                   0.0006 |             0.0009 |                    7 |                                  3 |                                   3 |                                   nan |                  nan      |                  nan      |                  nan      |                nan      |                nan      |                nan      |
| log_qcew_emp             |                   -0.0001 |                    0.0012 |                     0.0008 |                                    1 |                                     1 |                                     nan |              -0.0007 |                     11 |                  0.0005 |                 -0.0005 |                  -0.0024 |            -0.0024 |                   12 |                                nan |                                 nan |                                   nan |                  nan      |                  nan      |                  nan      |                nan      |                nan      |                nan      |

Figures 6-10 in output/figures/.

## 13. Pre-Trends

Worker separations (rate): p=0.226; Establishment deaths (exit rate): p=0.735; Job destruction rate (BDS): p=0.277; Employment (log end-of-quarter): p=0.888; Earnings (log avg monthly; stable): p=0.053

Adoption-event diagnostics (pre-period mean, TWFE vs Sun-Abraham) are in event_study_summary.csv.

## 14. Mechanisms

| mechanism   | outcome                  | sample                                 |   mean_y | term                   |    beta |     se |      p |   ci_low |   ci_high |       N | status   |
|:------------|:-------------------------|:---------------------------------------|---------:|:-----------------------|--------:|-------:|-------:|---------:|----------:|--------:|:---------|
| M1          | log_damage               | all county-quarters                    |   0.4669 | MI                     | -0.3662 | 0.0742 | 0      |  -0.5116 |   -0.2208 |  447408 | ok       |
| M1          | log_damage               | tornado county-quarters (EF bins FE)   |   6.5455 | M                      | -0.2087 | 0.1458 | 0.1526 |  -0.4947 |    0.0773 |   30861 | ok       |
| M1          | log_damage               | tornado county-quarters, M x intensity |   6.5455 | MI                     | -0.5425 | 0.0937 | 0      |  -0.7262 |   -0.3588 |   30861 | ok       |
| M1          | log_fatalities           | all county-quarters                    |   0.002  | MI                     |  0.0098 | 0.0035 | 0.0058 |   0.0028 |    0.0167 |  447408 | ok       |
| M1          | log_fatalities           | tornado county-quarters (EF bins FE)   |   0.028  | M                      | -0.0065 | 0.0061 | 0.2913 |  -0.0185 |    0.0055 |   30861 | ok       |
| M1          | log_fatalities           | tornado county-quarters, M x intensity |   0.028  | MI                     |  0.0365 | 0.0077 | 0      |   0.0215 |    0.0516 |   30861 | ok       |
| M1          | log_injuries             | all county-quarters                    |   0.0123 | MI                     | -0.0006 | 0.0087 | 0.9446 |  -0.0177 |    0.0165 |  447408 | ok       |
| M1          | log_injuries             | tornado county-quarters (EF bins FE)   |   0.1719 | M                      | -0.0176 | 0.0164 | 0.2826 |  -0.0498 |    0.0145 |   30861 | ok       |
| M1          | log_injuries             | tornado county-quarters, M x intensity |   0.1719 | MI                     |  0.0495 | 0.0186 | 0.0078 |   0.013  |    0.086  |   30861 | ok       |
| M4          | establishment_death_rate | BDS firm size 1-19 vs 20+              | nan      | MTS                    |  0.1213 | 0.0829 | 0.1436 |  -0.0413 |    0.284  |  249531 | ok       |
| M4          | establishment_death_rate | BDS firm size 20+ baseline MxT         | nan      | MT                     | -0.0221 | 0.0621 | 0.7214 |  -0.1438 |    0.0996 |  249531 | ok       |
| M4          | job_destruction_rate     | BDS firm size 1-19 vs 20+              | nan      | MTS                    |  0.0399 | 0.1483 | 0.7881 |  -0.2509 |    0.3306 |  310726 | ok       |
| M4          | job_destruction_rate     | BDS firm size 20+ baseline MxT         | nan      | MT                     |  0.0675 | 0.1295 | 0.602  |  -0.1863 |    0.3214 |  310726 | ok       |
| M4          | separation_rate          | QWI firm size <20 vs 20+               | nan      | MTS                    |  0.0009 | 0.0013 | 0.4867 |  -0.0017 |    0.0035 | 1662682 | ok       |
| M4          | log_employment           | QWI firm size <20 vs 20+               | nan      | MTS                    |  0.009  | 0.0056 | 0.1061 |  -0.0019 |    0.0199 | 1695674 | ok       |
| M5          | separation_rate          | facility-type split (overlapping)      | nan      | MT_school              |  0      | 0.0013 | 0.9971 |  -0.0025 |    0.0025 |  352841 | ok       |
| M5          | separation_rate          | facility-type split (overlapping)      | nan      | MT_residential_private | -0.0015 | 0.0012 | 0.1965 |  -0.0039 |    0.0008 |  352841 | ok       |
| M5          | separation_rate          | facility-type split (overlapping)      | nan      | MT_hospital            | -0.0014 | 0.0024 | 0.5527 |  -0.0062 |    0.0033 |  352841 | ok       |
| M5          | separation_rate          | facility-type split (overlapping)      | nan      | MT_fire_police         | -0.0009 | 0.0031 | 0.7792 |  -0.0069 |    0.0052 |  352841 | ok       |
| M5          | separation_rate          | facility-type split (overlapping)      | nan      | MT_community_shelter   |  0.0012 | 0.0025 | 0.6216 |  -0.0036 |    0.0061 |  352841 | ok       |
| M5          | separation_rate          | facility-type split (overlapping)      | nan      | MT_unknown             |  0.0013 | 0.001  | 0.1695 |  -0.0006 |    0.0032 |  352841 | ok       |
| M5          | establishment_death_rate | facility-type split (overlapping)      | nan      | MT_school              |  0.168  | 0.0789 | 0.0334 |   0.0132 |    0.3227 |  103769 | ok       |
| M5          | establishment_death_rate | facility-type split (overlapping)      | nan      | MT_residential_private | -0.0269 | 0.0803 | 0.7375 |  -0.1843 |    0.1305 |  103769 | ok       |
| M5          | establishment_death_rate | facility-type split (overlapping)      | nan      | MT_hospital            | -0.1479 | 0.1605 | 0.3568 |  -0.4626 |    0.1668 |  103769 | ok       |
| M5          | establishment_death_rate | facility-type split (overlapping)      | nan      | MT_fire_police         |  0.1899 | 0.2472 | 0.4424 |  -0.2948 |    0.6746 |  103769 | ok       |
| M5          | establishment_death_rate | facility-type split (overlapping)      | nan      | MT_community_shelter   | -0.1607 | 0.1362 | 0.2382 |  -0.4278 |    0.1064 |  103769 | ok       |
| M5          | establishment_death_rate | facility-type split (overlapping)      | nan      | MT_unknown             |  0.0253 | 0.0608 | 0.6772 |  -0.0939 |    0.1446 |  103769 | ok       |
| M5          | log_employment           | facility-type split (overlapping)      | nan      | MT_school              |  0.0013 | 0.0051 | 0.799  |  -0.0087 |    0.0113 |  356048 | ok       |
| M5          | log_employment           | facility-type split (overlapping)      | nan      | MT_residential_private | -0.0003 | 0.0064 | 0.9643 |  -0.0129 |    0.0123 |  356048 | ok       |
| M5          | log_employment           | facility-type split (overlapping)      | nan      | MT_hospital            | -0.0187 | 0.0083 | 0.0238 |  -0.0348 |   -0.0025 |  356048 | ok       |
| M5          | log_employment           | facility-type split (overlapping)      | nan      | MT_fire_police         |  0.0263 | 0.0123 | 0.0324 |   0.0022 |    0.0504 |  356048 | ok       |
| M5          | log_employment           | facility-type split (overlapping)      | nan      | MT_community_shelter   |  0.0058 | 0.0094 | 0.5365 |  -0.0126 |    0.0242 |  356048 | ok       |
| M5          | log_employment           | facility-type split (overlapping)      | nan      | MT_unknown             | -0.0009 | 0.0048 | 0.8531 |  -0.0104 |    0.0086 |  356048 | ok       |
| M2          | separation_rate          | physical vs remote-capable industries  | nan      | MTP                    |  0.0034 | 0.0013 | 0.01   |   0.0008 |    0.006  | 2231113 | ok       |
| M2          | separation_rate          | remote-capable baseline MxT            | nan      | MT                     | -0.0018 | 0.0011 | 0.1019 |  -0.004  |    0.0004 | 2231113 | ok       |
| M2          | log_employment           | physical vs remote-capable industries  | nan      | MTP                    |  0.0026 | 0.005  | 0.6052 |  -0.0072 |    0.0124 | 2364677 | ok       |
| M2          | log_employment           | remote-capable baseline MxT            | nan      | MT                     | -0.0002 | 0.005  | 0.9715 |  -0.0101 |    0.0097 | 2364677 | ok       |
| M2          | log_earnings             | physical vs remote-capable industries  | nan      | MTP                    |  0.002  | 0.0028 | 0.477  |  -0.0035 |    0.0074 | 2342729 | ok       |
| M2          | log_earnings             | remote-capable baseline MxT            | nan      | MT                     | -0.0031 | 0.0026 | 0.2375 |  -0.0082 |    0.002  | 2342729 | ok       |
| M2          | job_destruction_rate_qwi | physical vs remote-capable industries  | nan      | MTP                    |  0.0011 | 0.0008 | 0.1635 |  -0.0005 |    0.0027 | 2343453 | ok       |
| M2          | job_destruction_rate_qwi | remote-capable baseline MxT            | nan      | MT                     |  0.0001 | 0.0007 | 0.8619 |  -0.0013 |    0.0015 | 2343453 | ok       |

Severity gradient:

| outcome                  | bin     |   tornado_effect |   tornado_se |   mitig_diff |   mitig_diff_se |   mitig_diff_p |   n_treated_obs |
|:-------------------------|:--------|-----------------:|-------------:|-------------:|----------------:|---------------:|----------------:|
| separation_rate          | EF0     |          -0.0013 |       0.0005 |       0.0024 |          0.0009 |         0.0102 |            2116 |
| separation_rate          | EF1     |          -0.0006 |       0.0005 |       0.001  |          0.0009 |         0.2726 |            2229 |
| separation_rate          | EF2     |           0.0007 |       0.001  |       0.0007 |          0.0014 |         0.5958 |             694 |
| separation_rate          | EF3plus |           0.0018 |       0.0016 |      -0.0021 |          0.0022 |         0.3425 |             260 |
| log_employment           | EF0     |           0.0025 |       0.0018 |       0.0065 |          0.004  |         0.1063 |            2118 |
| log_employment           | EF1     |           0.0009 |       0.0018 |       0.0021 |          0.0038 |         0.5734 |            2231 |
| log_employment           | EF2     |          -0.0002 |       0.0032 |       0.0013 |          0.0061 |         0.8267 |             694 |
| log_employment           | EF3plus |           0.0066 |       0.005  |      -0.0014 |          0.009  |         0.8767 |             260 |
| log_earnings             | EF0     |          -0.0002 |       0.001  |       0.0011 |          0.0021 |         0.5957 |            2116 |
| log_earnings             | EF1     |          -0.0023 |       0.001  |       0.0001 |          0.002  |         0.9546 |            2229 |
| log_earnings             | EF2     |           0.0032 |       0.0017 |      -0.0076 |          0.0031 |         0.014  |             694 |
| log_earnings             | EF3plus |          -0.0012 |       0.003  |       0.0006 |          0.0053 |         0.9091 |             260 |
| establishment_death_rate | EF0     |          -0.0052 |       0.0237 |      -0.0449 |          0.0533 |         0.399  |            1307 |
| establishment_death_rate | EF1     |           0.0207 |       0.0272 |       0.0006 |          0.0553 |         0.9913 |            1477 |
| establishment_death_rate | EF2     |           0.005  |       0.0411 |       0.1268 |          0.0864 |         0.1422 |             485 |
| establishment_death_rate | EF3plus |           0.0165 |       0.0596 |       0.0638 |          0.13   |         0.6234 |             191 |
| job_destruction_rate     | EF0     |           0.0246 |       0.0499 |       0.0143 |          0.1173 |         0.9027 |            1308 |
| job_destruction_rate     | EF1     |           0.0129 |       0.0526 |       0.1442 |          0.1242 |         0.2456 |            1478 |
| job_destruction_rate     | EF2     |           0.152  |       0.1025 |       0.0914 |          0.1939 |         0.6375 |             485 |
| job_destruction_rate     | EF3plus |          -0.0241 |       0.1264 |      -0.0418 |          0.2745 |         0.879  |             191 |

Damage-mechanism robustness (exploratory, added after main results; includes the failing pre-treatment placebo and the within-treated design):

| variant                                                           | outcome        |    beta |     se |      p |     N |   treated_obs |   pct_per_EF_step |
|:------------------------------------------------------------------|:---------------|--------:|-------:|-------:|------:|--------------:|------------------:|
| primary (strict, obligation+2y)                                   | log_damage     | -0.5425 | 0.0937 | 0      | 30861 |          5564 |          -41.8719 |
| moderate                                                          | log_damage     | -0.5426 | 0.0935 | 0      | 30861 |          5586 |          -41.8753 |
| broad                                                             | log_damage     | -0.5806 | 0.0894 | 0      | 30861 |          6612 |          -44.0425 |
| safe-room only                                                    | log_damage     | -0.5295 | 0.0987 | 0      | 30861 |          4086 |          -41.1127 |
| wind-retrofit only                                                | log_damage     | -0.3407 | 0.1839 | 0.0641 | 30861 |          2125 |          -28.8696 |
| closeout timing                                                   | log_damage     | -0.5949 | 0.096  | 0      | 30861 |          5071 |          -44.8366 |
| approval lag 0                                                    | log_damage     | -0.5502 | 0.0955 | 0      | 30861 |          6036 |          -42.3182 |
| exclude FL                                                        | log_damage     | -0.6211 | 0.0954 | 0      | 29446 |          4735 |          -46.2674 |
| exclude OK and TX                                                 | log_damage     | -0.5962 | 0.1063 | 0      | 26270 |          4608 |          -44.9079 |
| exclude post-tornado HMGP awards                                  | log_damage     | -0.5608 | 0.1173 | 0      | 25937 |          3675 |          -42.9243 |
| PLACEBO: ever-treated x intensity, pre-treatment only             | log_damage     |  0.3263 | 0.0808 | 0.0001 | 25221 |          7933 |           38.5899 |
| 1996+ only (modern damage reporting)                              | log_damage     | -0.4579 | 0.0952 | 0      | 26457 |          5564 |          -36.7411 |
| EF1+ county-quarters only                                         | log_damage     | -0.152  | 0.1552 | 0.3274 | 14986 |          3204 |          -14.1018 |
| cluster by state                                                  | log_damage     | -0.5425 | 0.2108 | 0.0133 | 30861 |          5564 |          -41.8719 |
| primary                                                           | log_fatalities |  0.0365 | 0.0077 | 0      | 30861 |          5564 |            3.7202 |
| PLACEBO pre-treatment                                             | log_fatalities |  0.027  | 0.0075 | 0.0003 | 25221 |          7933 |            2.7414 |
| primary                                                           | log_injuries   |  0.0495 | 0.0186 | 0.0078 | 30861 |          5564 |            5.079  |
| PLACEBO pre-treatment                                             | log_injuries   |  0.0997 | 0.0182 | 0      | 25221 |          7933 |           10.4799 |
| WITHIN-TREATED (controls ever-treated x intensity)                | log_damage     | -0.7287 | 0.1017 | 0      | 30861 |          5564 |          -51.7475 |
| WITHIN-TREATED (controls ever-treated x intensity)                | log_fatalities |  0.0219 | 0.0095 | 0.0208 | 30861 |          5564 |            2.2162 |
| WITHIN-TREATED (controls ever-treated x intensity)                | log_injuries   | -0.0132 | 0.0224 | 0.5558 | 30861 |          5564 |           -1.3095 |
| WITHIN-TREATED, safe-room only                                    | log_damage     | -0.7345 | 0.1053 | 0      | 30861 |          4086 |          -52.0255 |
| WITHIN-TREATED, 1996+                                             | log_damage     | -0.6492 | 0.1078 | 0      | 26457 |          5564 |          -47.7521 |
| WITHIN-TREATED, drop 5 pre-treatment years (mean-reversion check) | log_damage     | -0.8675 | 0.1126 | 0      | 28803 |          5564 |          -57.9981 |
| WITHIN-TREATED, drop 5 pre-treatment years (mean-reversion check) | log_fatalities |  0.0413 | 0.0094 | 0      | 28803 |          5564 |            4.2118 |
| WITHIN-TREATED, drop 5 pre-treatment years (mean-reversion check) | log_injuries   |  0.0164 | 0.0231 | 0.4772 | 28803 |          5564 |            1.653  |
| WITHIN-TREATED, drop 5 pre years, excl. post-tornado HMGP awards  | log_damage     | -0.9209 | 0.1464 | 0      | 24640 |          3675 |          -60.1823 |
| PLACEBO pre-treatment, excluding 5 pre years                      | log_damage     |  0.4027 | 0.089  | 0      | 23156 |          5894 |           49.5853 |

## 15. Heterogeneity (exploratory)

See `output/tables/table8_heterogeneity.md` (BH within family) and Figures 12-14.

## 16. Robustness

Sign consistency uses credible specifications only (duplicates of the primary, placebos and permutation draws excluded). Classification follows Section 35 rules frozen in the pre-registration snapshot.

| outcome                                        |   primary_beta |   sign_consistency |   sig_consistency |   significant_5_share |   median_beta_ratio |   CI_consistency |   pretrend_p |   placebo_p |   ri_p |   leave_state_out_sign_share |   treatment_definition_pass |   timing_pass |   hazard_definition_pass |   matching_pass |   estimator_pass |   robust_specs |   n_credible | robustness_rating    | main_result          |
|:-----------------------------------------------|---------------:|-------------------:|------------------:|----------------------:|--------------------:|-----------------:|-------------:|------------:|-------:|-----------------------------:|----------------------------:|--------------:|-------------------------:|----------------:|-----------------:|---------------:|-------------:|:---------------------|:---------------------|
| Worker separations (rate)                      |          0     |              0.887 |             0.081 |                 0.065 |               1.036 |            0.903 |        0.226 |       0.932 |   0.5  |                        1     |                           1 |             1 |                        0 |               1 |                1 |              5 |           62 | NO DETECTABLE EFFECT | No detectable effect |
| Employment retention                           |        nan     |            nan     |           nan     |               nan     |             nan     |          nan     |      nan     |     nan     | nan    |                      nan     |                         nan |           nan |                      nan |             nan |              nan |            nan |          nan | NO DETECTABLE EFFECT | No detectable effect |
| Establishment deaths (exit rate)               |          0.044 |              0.852 |             0.049 |                 0.049 |               0.879 |            0.869 |        0.735 |       0.593 |   0.36 |                        1     |                           1 |             0 |                        1 |               1 |                1 |              3 |           61 | UNDERPOWERED         | Underpowered         |
| Establishment deaths (log count)               |        nan     |            nan     |           nan     |               nan     |             nan     |          nan     |      nan     |     nan     | nan    |                      nan     |                         nan |           nan |                      nan |             nan |              nan |            nan |          nan | MIXED                | Adverse              |
| Job destruction rate (BDS)                     |          0.111 |              0.934 |             0.098 |                 0.016 |               0.976 |            0.934 |        0.277 |       0.672 |   0.26 |                        1     |                           1 |             1 |                        0 |               1 |                1 |              6 |           61 | UNDERPOWERED         | Underpowered         |
| Job creation rate (BDS)                        |        nan     |            nan     |           nan     |               nan     |             nan     |          nan     |      nan     |     nan     | nan    |                      nan     |                         nan |           nan |                      nan |             nan |              nan |            nan |          nan | MIXED                | Protective           |
| Job destruction rate (QWI firm job loss)       |          0.001 |              0.984 |             0.721 |                 0.328 |               1.002 |            0.951 |        0.632 |       0.996 | nan    |                      nan     |                           1 |             1 |                        1 |               1 |                1 |             44 |           61 | MODERATELY ROBUST    | Adverse              |
| Employment (log end-of-quarter)                |          0.001 |              0.71  |             0.016 |                 0.016 |               0.842 |            0.758 |        0.888 |       0.653 |   0.83 |                        0.959 |                           1 |             0 |                        0 |               0 |                1 |              1 |           62 | UNDERPOWERED         | Underpowered         |
| Employment (QCEW log; 2014+)                   |         -0     |              0.639 |             0     |                 0     |               0.931 |            0.639 |        0.995 |       0.326 | nan    |                      nan     |                           0 |             0 |                        0 |               0 |              nan |              0 |           61 | UNDERPOWERED         | Underpowered         |
| Earnings (log avg monthly; stable)             |         -0.002 |              0.871 |             0.016 |                 0     |               0.931 |            0.048 |        0.053 |       0.742 |   0.57 |                        1     |                           1 |             0 |                        1 |               1 |                1 |              1 |           62 | UNDERPOWERED         | Underpowered         |
| New-hire earnings (log)                        |        nan     |            nan     |           nan     |               nan     |             nan     |          nan     |      nan     |     nan     | nan    |                      nan     |                         nan |           nan |                      nan |             nan |              nan |            nan |          nan | UNDERPOWERED         | Underpowered         |
| Hire rate                                      |         -0.001 |              0.902 |             0.148 |                 0.049 |               0.926 |            0.951 |        0.604 |       0.979 | nan    |                        1     |                           1 |             1 |                        1 |               1 |                1 |              9 |           61 | UNDERPOWERED         | Underpowered         |
| New-hire rate                                  |        nan     |            nan     |           nan     |               nan     |             nan     |          nan     |      nan     |     nan     | nan    |                      nan     |                         nan |           nan |                      nan |             nan |              nan |            nan |          nan | UNDERPOWERED         | Underpowered         |
| Turnover (stable)                              |        nan     |            nan     |           nan     |               nan     |             nan     |          nan     |      nan     |     nan     | nan    |                      nan     |                         nan |           nan |                      nan |             nan |              nan |            nan |          nan | UNDERPOWERED         | Underpowered         |
| Small-firm establishment death rate (BDS 1-19) |          0.1   |              0.983 |             0.367 |                 0.017 |               0.941 |            0.2   |        0.383 |       0.85  | nan    |                      nan     |                           1 |             1 |                        1 |               1 |                1 |             22 |           60 | MODERATELY ROBUST    | Adverse              |
| Small-establishment share (CBP <20)            |        nan     |            nan     |           nan     |               nan     |             nan     |          nan     |      nan     |     nan     | nan    |                      nan     |                         nan |           nan |                      nan |             nan |              nan |            nan |          nan | UNDERPOWERED         | Underpowered         |
| Establishment birth rate                       |        nan     |            nan     |           nan     |               nan     |             nan     |          nan     |      nan     |     nan     | nan    |                      nan     |                         nan |           nan |                      nan |             nan |              nan |            nan |          nan | UNDERPOWERED         | Underpowered         |
| Startup rate (age-0 firms' estabs)             |        nan     |            nan     |           nan     |               nan     |             nan     |          nan     |      nan     |     nan     | nan    |                      nan     |                         nan |           nan |                      nan |             nan |              nan |            nan |          nan | UNDERPOWERED         | Underpowered         |
| Out-migration rate                             |          0.032 |              0.967 |             0.233 |                 0.083 |               1     |            0.9   |        0.883 |       0.457 | nan    |                        1     |                           1 |             1 |                        1 |               1 |                1 |             14 |           60 | UNDERPOWERED         | Underpowered         |
| Net migration rate                             |        nan     |            nan     |           nan     |               nan     |             nan     |          nan     |      nan     |     nan     | nan    |                      nan     |                         nan |           nan |                      nan |             nan |              nan |            nan |          nan | UNDERPOWERED         | Underpowered         |
| In-migration rate                              |        nan     |            nan     |           nan     |               nan     |             nan     |          nan     |      nan     |     nan     | nan    |                      nan     |                         nan |           nan |                      nan |             nan |              nan |            nan |          nan | NO DETECTABLE EFFECT | No detectable effect |
| Out-migrant AGI (log)                          |        nan     |            nan     |           nan     |               nan     |             nan     |          nan     |      nan     |     nan     | nan    |                      nan     |                         nan |           nan |                      nan |             nan |              nan |            nan |          nan | UNDERPOWERED         | Underpowered         |
| Housing units authorized (IHS)                 |         -0.007 |              0.967 |             0.017 |                 0.017 |               3.142 |            0.817 |        0.278 |       0.039 | nan    |                      nan     |                           1 |             1 |                        1 |               1 |                1 |              1 |           60 | UNDERPOWERED         | Underpowered         |
| Single-family units (IHS)                      |        nan     |            nan     |           nan     |               nan     |             nan     |          nan     |      nan     |     nan     | nan    |                      nan     |                         nan |           nan |                      nan |             nan |              nan |            nan |          nan | UNDERPOWERED         | Underpowered         |
| Multifamily units (IHS)                        |        nan     |            nan     |           nan     |               nan     |             nan     |          nan     |      nan     |     nan     | nan    |                      nan     |                         nan |           nan |                      nan |             nan |              nan |            nan |          nan | UNDERPOWERED         | Underpowered         |
| Establishments (CBP log)                       |          0.007 |              0.95  |             0.8   |                 0.7   |               0.976 |            0.933 |        0.019 |       0.712 | nan    |                        1     |                           1 |             1 |                        1 |               1 |                1 |             48 |           60 | NOT ROBUST           | Protective           |
| Employment (CBP log)                           |        nan     |            nan     |           nan     |               nan     |             nan     |          nan     |      nan     |     nan     | nan    |                      nan     |                         nan |           nan |                      nan |             nan |              nan |            nan |          nan | UNDERPOWERED         | Underpowered         |
| Payroll (CBP log)                              |        nan     |            nan     |           nan     |               nan     |             nan     |          nan     |      nan     |     nan     | nan    |                      nan     |                         nan |           nan |                      nan |             nan |              nan |            nan |          nan | UNDERPOWERED         | Underpowered         |

## 17. Placebos

| outcome                  | specification_id   |    beta |     se |        p |   share_p05 |   n_draws |   primary_beta |
|:-------------------------|:-------------------|--------:|-------:|---------:|------------:|----------:|---------------:|
| separation_rate          | R36                |  0.0001 | 0.0014 |   0.9591 |      nan    |       nan |         0.0005 |
| separation_rate          | R37                |  0      | 0.0012 |   0.9957 |      nan    |       nan |         0.0005 |
| separation_rate          | R38                |  0.0001 | 0.001  |   0.9319 |      nan    |       nan |         0.0005 |
| separation_rate          | R39                | -0      | 0.0004 | nan      |        0    |        20 |         0.0005 |
| separation_rate          | R40                |  0      | 0.0007 |   0.5    |      nan    |       100 |         0.0005 |
| log_employment           | R36                |  0.0136 | 0.0055 |   0.0137 |      nan    |       nan |         0.0012 |
| log_employment           | R37                |  0.0066 | 0.004  |   0.1025 |      nan    |       nan |         0.0012 |
| log_employment           | R38                | -0.0014 | 0.0031 |   0.6533 |      nan    |       nan |         0.0012 |
| log_employment           | R39                |  0.0037 | 0.0019 | nan      |        0.05 |        20 |         0.0012 |
| log_employment           | R40                |  0.0034 | 0.0032 |   0.83   |      nan    |       100 |         0.0012 |
| log_earnings             | R36                |  0.0055 | 0.0035 |   0.1178 |      nan    |       nan |        -0.0017 |
| log_earnings             | R37                |  0.0062 | 0.0026 |   0.0162 |      nan    |       nan |        -0.0017 |
| log_earnings             | R38                | -0.0006 | 0.0017 |   0.7417 |      nan    |       nan |        -0.0017 |
| log_earnings             | R39                |  0.0005 | 0.0009 | nan      |        0    |        20 |        -0.0017 |
| log_earnings             | R40                | -0.0019 | 0.0014 |   0.57   |      nan    |       100 |        -0.0017 |
| establishment_death_rate | R36                | -0.2283 | 0.0906 |   0.0118 |      nan    |       nan |         0.0437 |
| establishment_death_rate | R37                | -0.0908 | 0.0768 |   0.2374 |      nan    |       nan |         0.0437 |
| establishment_death_rate | R38                | -0.0262 | 0.049  |   0.5929 |      nan    |       nan |         0.0437 |
| establishment_death_rate | R39                |  0.0113 | 0.0335 | nan      |        0    |        20 |         0.0437 |
| establishment_death_rate | R40                | -0.0246 | 0.039  |   0.36   |      nan    |       100 |         0.0437 |
| job_destruction_rate     | R36                | -0.257  | 0.195  |   0.1877 |      nan    |       nan |         0.1107 |
| job_destruction_rate     | R37                | -0.0707 | 0.1514 |   0.6406 |      nan    |       nan |         0.1107 |
| job_destruction_rate     | R38                | -0.0415 | 0.0981 |   0.6722 |      nan    |       nan |         0.1107 |
| job_destruction_rate     | R39                |  0.0577 | 0.0689 | nan      |        0    |        20 |         0.1107 |
| job_destruction_rate     | R40                |  0.0372 | 0.0892 |   0.26   |      nan    |       100 |         0.1107 |
| hire_rate                | R36                |  0.0028 | 0.0018 |   0.1223 |      nan    |       nan |        -0.0011 |
| hire_rate                | R37                |  0.0005 | 0.0013 |   0.6696 |      nan    |       nan |        -0.0011 |
| hire_rate                | R38                | -0      | 0.0011 |   0.9793 |      nan    |       nan |        -0.0011 |
| hire_rate                | R39                | -0.0006 | 0.0005 | nan      |        0    |         5 |        -0.0011 |
| job_destruction_rate_qwi | R36                | -0.0005 | 0.0009 |   0.5676 |      nan    |       nan |         0.0007 |
| job_destruction_rate_qwi | R37                |  0      | 0.0007 |   0.9506 |      nan    |       nan |         0.0007 |
| job_destruction_rate_qwi | R38                | -0      | 0.0006 |   0.9958 |      nan    |       nan |         0.0007 |
| job_destruction_rate_qwi | R39                |  0.0006 | 0.0002 | nan      |        0    |         5 |         0.0007 |
| small_estab_death_rate   | R36                | -0.2908 | 0.1188 |   0.0144 |      nan    |       nan |         0.1003 |
| small_estab_death_rate   | R37                | -0.1467 | 0.0982 |   0.1353 |      nan    |       nan |         0.1003 |
| small_estab_death_rate   | R38                | -0.0113 | 0.0599 |   0.8498 |      nan    |       nan |         0.1003 |
| small_estab_death_rate   | R39                |  0.0302 | 0.0418 | nan      |        0    |         5 |         0.1003 |
| log_establishments       | R36                |  0.0118 | 0.0053 |   0.0254 |      nan    |       nan |         0.0074 |
| log_establishments       | R37                |  0.0074 | 0.0038 |   0.0523 |      nan    |       nan |         0.0074 |
| log_establishments       | R38                | -0.0009 | 0.0024 |   0.7116 |      nan    |       nan |         0.0074 |
| log_establishments       | R39                |  0.0057 | 0.0009 | nan      |        0.4  |         5 |         0.0074 |
| outmigration_rate        | R36                |  0.0253 | 0.0528 |   0.6318 |      nan    |       nan |         0.0317 |
| outmigration_rate        | R37                | -0.0585 | 0.0417 |   0.1605 |      nan    |       nan |         0.0317 |
| outmigration_rate        | R38                | -0.0333 | 0.0448 |   0.4574 |      nan    |       nan |         0.0317 |
| outmigration_rate        | R39                | -0.0002 | 0.0041 | nan      |        0    |         5 |         0.0317 |
| ihs_units                | R36                |  0.0585 | 0.0401 |   0.1444 |      nan    |       nan |        -0.0229 |
| ihs_units                | R37                |  0.0636 | 0.029  |   0.0281 |      nan    |       nan |        -0.0229 |
| ihs_units                | R38                |  0.0354 | 0.0171 |   0.0388 |      nan    |       nan |        -0.0229 |
| ihs_units                | R39                | -0.0179 | 0.017  | nan      |        0    |         5 |        -0.0229 |
| log_qcew_emp             | R36                |  0.0138 | 0.0104 |   0.1821 |      nan    |       nan |        -0.0003 |
| log_qcew_emp             | R37                |  0.0049 | 0.0063 |   0.4372 |      nan    |       nan |        -0.0003 |
| log_qcew_emp             | R38                |  0.0047 | 0.0048 |   0.3259 |      nan    |       nan |        -0.0003 |
| log_qcew_emp             | R39                |  0.0007 | 0.0009 | nan      |        0    |         5 |        -0.0003 |
| log_beg_emp              | PL_beg_emp         |  0.0023 | 0.0034 |   0.4898 |      nan    |       nan |       nan      |

## 18. Leave-One-State-Out

Worker separations (rate): primary 0.0005; without OK 0.0005 (p=0.534); without TX 0.0005 (p=0.533); Establishment deaths (exit rate): primary 0.0437; without OK 0.0505 (p=0.306); without TX 0.0524 (p=0.277); Job destruction rate (BDS): primary 0.1107; without OK 0.1581 (p=0.151); without TX 0.1257 (p=0.241); Employment (log end-of-quarter): primary 0.0012; without OK -0.0002 (p=0.962); without TX 0.0032 (p=0.342); Earnings (log avg monthly; stable): primary -0.0017; without OK -0.0021 (p=0.260); without TX -0.0011 (p=0.513)

| outcome                  | state_removed   |    beta |     SE |   pvalue |   primary_beta | focus_state   |
|:-------------------------|:----------------|--------:|-------:|---------:|---------------:|:--------------|
| separation_rate          | AL              |  0.0007 | 0.0008 |   0.3793 |         0.0005 | True          |
| separation_rate          | AR              |  0.0006 | 0.0008 |   0.4809 |         0.0005 | True          |
| separation_rate          | FL              |  0.0006 | 0.0008 |   0.4236 |         0.0005 | True          |
| separation_rate          | IA              |  0.0005 | 0.0008 |   0.5109 |         0.0005 | True          |
| separation_rate          | KS              |  0.0004 | 0.0008 |   0.6424 |         0.0005 | True          |
| separation_rate          | MO              |  0.0005 | 0.0008 |   0.5284 |         0.0005 | True          |
| separation_rate          | MS              |  0.0006 | 0.0008 |   0.4353 |         0.0005 | True          |
| separation_rate          | OK              |  0.0005 | 0.0008 |   0.5336 |         0.0005 | True          |
| separation_rate          | TN              |  0.0003 | 0.0008 |   0.6879 |         0.0005 | True          |
| separation_rate          | TX              |  0.0005 | 0.0008 |   0.5326 |         0.0005 | True          |
| log_employment           | AL              |  0.0018 | 0.0038 |   0.6418 |         0.0012 | True          |
| log_employment           | AR              |  0.0008 | 0.0037 |   0.8283 |         0.0012 | True          |
| log_employment           | FL              |  0.0008 | 0.0035 |   0.8249 |         0.0012 | True          |
| log_employment           | IA              |  0.0008 | 0.0036 |   0.8265 |         0.0012 | True          |
| log_employment           | KS              |  0.0012 | 0.0035 |   0.7374 |         0.0012 | True          |
| log_employment           | MO              |  0.0022 | 0.0036 |   0.5445 |         0.0012 | True          |
| log_employment           | MS              | -0.0002 | 0.0035 |   0.9617 |         0.0012 | True          |
| log_employment           | OK              | -0.0002 | 0.0036 |   0.9619 |         0.0012 | True          |
| log_employment           | TN              |  0.0015 | 0.0035 |   0.6794 |         0.0012 | True          |
| log_employment           | TX              |  0.0032 | 0.0033 |   0.3425 |         0.0012 | True          |
| log_earnings             | AL              | -0.0031 | 0.0019 |   0.1099 |        -0.0017 | True          |
| log_earnings             | AR              | -0.0015 | 0.0019 |   0.4169 |        -0.0017 | True          |
| log_earnings             | FL              | -0.0021 | 0.0019 |   0.271  |        -0.0017 | True          |
| log_earnings             | IA              | -0.0013 | 0.0018 |   0.4931 |        -0.0017 | True          |
| log_earnings             | KS              | -0.0015 | 0.0018 |   0.413  |        -0.0017 | True          |
| log_earnings             | MO              | -0.0023 | 0.0018 |   0.2143 |        -0.0017 | True          |
| log_earnings             | MS              | -0.0011 | 0.0018 |   0.5611 |        -0.0017 | True          |
| log_earnings             | OK              | -0.0021 | 0.0019 |   0.26   |        -0.0017 | True          |
| log_earnings             | TN              | -0.0011 | 0.0018 |   0.5414 |        -0.0017 | True          |
| log_earnings             | TX              | -0.0011 | 0.0017 |   0.5134 |        -0.0017 | True          |
| establishment_death_rate | AL              |  0.031  | 0.0502 |   0.5375 |         0.0437 | True          |
| establishment_death_rate | AR              |  0.0309 | 0.0488 |   0.5272 |         0.0437 | True          |
| establishment_death_rate | FL              |  0.0452 | 0.0497 |   0.3632 |         0.0437 | True          |
| establishment_death_rate | IA              |  0.0342 | 0.0485 |   0.4804 |         0.0437 | True          |
| establishment_death_rate | KS              |  0.0442 | 0.0478 |   0.355  |         0.0437 | True          |
| establishment_death_rate | MO              |  0.0355 | 0.0485 |   0.4641 |         0.0437 | True          |
| establishment_death_rate | MS              |  0.0412 | 0.0462 |   0.3727 |         0.0437 | True          |
| establishment_death_rate | OK              |  0.0505 | 0.0493 |   0.3056 |         0.0437 | True          |
| establishment_death_rate | TN              |  0.0377 | 0.0472 |   0.4244 |         0.0437 | True          |
| establishment_death_rate | TX              |  0.0524 | 0.0482 |   0.2774 |         0.0437 | True          |
| job_destruction_rate     | AL              |  0.1129 | 0.1136 |   0.3201 |         0.1107 | True          |
| job_destruction_rate     | AR              |  0.0831 | 0.1085 |   0.4436 |         0.1107 | True          |
| job_destruction_rate     | FL              |  0.1216 | 0.1141 |   0.2864 |         0.1107 | True          |
| job_destruction_rate     | IA              |  0.0787 | 0.1107 |   0.4775 |         0.1107 | True          |
| job_destruction_rate     | KS              |  0.1114 | 0.1095 |   0.3091 |         0.1107 | True          |
| job_destruction_rate     | MO              |  0.0411 | 0.1071 |   0.7011 |         0.1107 | True          |
| job_destruction_rate     | MS              |  0.1242 | 0.1095 |   0.2567 |         0.1107 | True          |
| job_destruction_rate     | OK              |  0.1581 | 0.1101 |   0.151  |         0.1107 | True          |
| job_destruction_rate     | TN              |  0.1109 | 0.1085 |   0.3068 |         0.1107 | True          |
| job_destruction_rate     | TX              |  0.1257 | 0.1071 |   0.2408 |         0.1107 | True          |
| hire_rate                | AL              | -0.001  | 0.0009 |   0.2702 |        -0.0011 | True          |
| hire_rate                | AR              | -0.0008 | 0.0009 |   0.3706 |        -0.0011 | True          |
| hire_rate                | FL              | -0.0014 | 0.0009 |   0.1125 |        -0.0011 | True          |
| hire_rate                | IA              | -0.0012 | 0.0009 |   0.1811 |        -0.0011 | True          |
| hire_rate                | KS              | -0.0009 | 0.0009 |   0.3203 |        -0.0011 | True          |
| hire_rate                | MO              | -0.0008 | 0.0009 |   0.3843 |        -0.0011 | True          |
| hire_rate                | MS              | -0.0006 | 0.0009 |   0.4729 |        -0.0011 | True          |
| hire_rate                | OK              | -0.0012 | 0.0009 |   0.1892 |        -0.0011 | True          |
| hire_rate                | TN              | -0.0015 | 0.0009 |   0.0977 |        -0.0011 | True          |
| hire_rate                | TX              | -0.0009 | 0.0009 |   0.3005 |        -0.0011 | True          |
| outmigration_rate        | AL              |  0.0392 | 0.0225 |   0.0819 |         0.0317 | True          |
| outmigration_rate        | AR              |  0.028  | 0.0222 |   0.2074 |         0.0317 | True          |
| outmigration_rate        | FL              |  0.0289 | 0.0221 |   0.1916 |         0.0317 | True          |
| outmigration_rate        | IA              |  0.0357 | 0.0222 |   0.1082 |         0.0317 | True          |
| outmigration_rate        | KS              |  0.0249 | 0.0207 |   0.231  |         0.0317 | True          |
| outmigration_rate        | MO              |  0.0312 | 0.0219 |   0.1551 |         0.0317 | True          |
| outmigration_rate        | MS              |  0.0335 | 0.0219 |   0.1265 |         0.0317 | True          |
| outmigration_rate        | OK              |  0.0327 | 0.022  |   0.1363 |         0.0317 | True          |
| outmigration_rate        | TN              |  0.0341 | 0.0218 |   0.1188 |         0.0317 | True          |
| outmigration_rate        | TX              |  0.0323 | 0.0221 |   0.1431 |         0.0317 | True          |
| log_establishments       | AL              |  0.0091 | 0.0036 |   0.0107 |         0.0074 | True          |
| log_establishments       | AR              |  0.0055 | 0.0034 |   0.1064 |         0.0074 | True          |
| log_establishments       | FL              |  0.008  | 0.0034 |   0.0178 |         0.0074 | True          |
| log_establishments       | IA              |  0.007  | 0.0034 |   0.039  |         0.0074 | True          |
| log_establishments       | KS              |  0.0068 | 0.0034 |   0.044  |         0.0074 | True          |
| log_establishments       | MO              |  0.008  | 0.0034 |   0.0187 |         0.0074 | True          |
| log_establishments       | MS              |  0.006  | 0.0032 |   0.0608 |         0.0074 | True          |
| log_establishments       | OK              |  0.0056 | 0.0034 |   0.105  |         0.0074 | True          |
| log_establishments       | TN              |  0.0076 | 0.0033 |   0.0225 |         0.0074 | True          |
| log_establishments       | TX              |  0.0094 | 0.0031 |   0.0026 |         0.0074 | True          |

Leave-one-event-out: Worker separations (rate): LOEO sign share 1.00, driving events [nan]; Establishment deaths (exit rate): LOEO sign share 1.00, driving events [nan]; Job destruction rate (BDS): LOEO sign share 1.00, driving events [nan]; Employment (log end-of-quarter): LOEO sign share 1.00, driving events [nan]; Earnings (log avg monthly; stable): LOEO sign share 1.00, driving events [nan]

## 19. Multiple Testing

Families: confirmatory (5 pre-specified primary outcomes); exploratory families by outcome domain. BH = Benjamini-Hochberg q-value; Holm = Holm-adjusted p.

| outcome                                        | fam_mt                |    beta |     se |      p |   bh_q |   holm_p |
|:-----------------------------------------------|:----------------------|--------:|-------:|-------:|-------:|---------:|
| Worker separations (rate)                      | confirmatory          |  0.0005 | 0.0008 | 0.5416 | 0.677  |   1      |
| Employment retention                           | exploratory_labor     | -0.0003 | 0.0004 | 0.4552 | 0.5311 |   0.9775 |
| Establishment deaths (exit rate)               | confirmatory          |  0.0437 | 0.0468 | 0.3501 | 0.5835 |   1      |
| Establishment deaths (log count)               | exploratory_business  |  0.0196 | 0.0064 | 0.0022 | 0.0201 |   0.0201 |
| Job destruction rate (BDS)                     | confirmatory          |  0.1107 | 0.1067 | 0.2995 | 0.5835 |   1      |
| Job creation rate (BDS)                        | exploratory_business  |  0.1595 | 0.09   | 0.0766 | 0.2227 |   0.5361 |
| Job destruction rate (QWI firm job loss)       | exploratory_labor     |  0.0007 | 0.0004 | 0.0734 | 0.3922 |   0.5138 |
| Employment (log end-of-quarter)                | confirmatory          |  0.0012 | 0.0035 | 0.7307 | 0.7307 |   1      |
| Employment (QCEW log; 2014+)                   | exploratory_labor     | -0.0003 | 0.0021 | 0.9037 | 0.9037 |   0.9775 |
| Earnings (log avg monthly; stable)             | confirmatory          | -0.0017 | 0.0018 | 0.3418 | 0.5835 |   1      |
| New-hire earnings (log)                        | exploratory_labor     | -0.0045 | 0.0029 | 0.1181 | 0.3922 |   0.7086 |
| Hire rate                                      | exploratory_labor     | -0.0011 | 0.0009 | 0.1955 | 0.3922 |   0.9775 |
| New-hire rate                                  | exploratory_labor     | -0.0007 | 0.0007 | 0.2804 | 0.3926 |   0.9775 |
| Turnover (stable)                              | exploratory_labor     | -0.0004 | 0.0003 | 0.2241 | 0.3922 |   0.9775 |
| Small-firm establishment death rate (BDS 1-19) | exploratory_business  |  0.1003 | 0.0608 | 0.099  | 0.2227 |   0.5938 |
| Small-establishment share (CBP <20)            | exploratory_business  | -0.0002 | 0.0004 | 0.5546 | 0.6239 |   1      |
| Establishment birth rate                       | exploratory_business  | -0.0296 | 0.047  | 0.5286 | 0.6239 |   1      |
| Startup rate (age-0 firms' estabs)             | exploratory_business  | -0.0259 | 0.0392 | 0.5083 | 0.6239 |   1      |
| Out-migration rate                             | exploratory_household |  0.0317 | 0.0214 | 0.1386 | 0.7133 |   0.9705 |
| Net migration rate                             | exploratory_household | -0.0166 | 0.0325 | 0.6104 | 0.8475 |   1      |
| In-migration rate                              | exploratory_household |  0.0137 | 0.0282 | 0.6275 | 0.8475 |   1      |
| Out-migrant AGI (log)                          | exploratory_household | -0.001  | 0.0054 | 0.8475 | 0.8475 |   1      |
| Housing units authorized (IHS)                 | exploratory_household | -0.0072 | 0.0244 | 0.7673 | 0.8475 |   1      |
| Single-family units (IHS)                      | exploratory_household | -0.0203 | 0.0233 | 0.3834 | 0.8475 |   1      |
| Multifamily units (IHS)                        | exploratory_household |  0.0517 | 0.0407 | 0.2038 | 0.7133 |   1      |
| Establishments (CBP log)                       | exploratory_business  |  0.0074 | 0.0033 | 0.0222 | 0.1001 |   0.178  |
| Employment (CBP log)                           | exploratory_business  |  0.0046 | 0.0044 | 0.2995 | 0.5391 |   1      |
| Payroll (CBP log)                              | exploratory_business  |  0.0012 | 0.0054 | 0.8185 | 0.8185 |   1      |

## Resilience indices

| index                             |     beta |       se |        p |     bh_q |   holm_p |      N | status                                      |
|:----------------------------------|---------:|---------:|---------:|---------:|---------:|-------:|:--------------------------------------------|
| labor_market_resilience_index     |  -0.0034 |   0.0044 |   0.4441 |   0.6661 |   1      | 352873 | ok                                          |
| labor_market_resilience_index_icw |  -0.0025 |   0.0042 |   0.5561 |   0.6673 |   1      | 346150 | ok                                          |
| business_resilience_index         |  -0.0008 |   0.0118 |   0.9465 |   0.9465 |   1      | 103750 | ok                                          |
| business_resilience_index_icw     |  -0.0188 |   0.0097 |   0.0515 |   0.3093 |   0.3093 |  79072 | ok                                          |
| household_resilience_index        |  -0.0092 |   0.0084 |   0.2753 |   0.5911 |   1      |  36746 | ok                                          |
| household_resilience_index_icw    |  -0.0088 |   0.0084 |   0.2955 |   0.5911 |   1      |  36746 | ok                                          |
| fiscal_resilience_index           | nan      | nan      | nan      | nan      | nan      |    nan | INFEASIBLE (public finance LOW feasibility) |

## 20. Statistical Power

E* = pre-registered economically meaningful effect (50% offset of the tornado main effect, or 0.05 SD when the tornado main effect is not disruptive).

| outcome_id   | outcome                                        |   treated_counties |   treated_tornado_obs |   n_clusters |      se |   y_mean |    y_sd |   gamma_T |   tornado_effect_sd |   E_star |   MDE80 |   MDE80_pct_mean |   MDE80_sd |   MDE90 |   MDE90_pct_mean |   MDE90_sd |   MDE80_over_Estar | power_rating       |
|:-------------|:-----------------------------------------------|-------------------:|----------------------:|-------------:|--------:|---------:|--------:|----------:|--------------------:|---------:|--------:|-----------------:|-----------:|--------:|-----------------:|-----------:|-------------------:|:-------------------|
| O1a          | Worker separations (rate)                      |                867 |                  3183 |         3100 | 0.00078 |  0.21311 | 0.0847  |   4e-05   |             0.00042 |  0.0025  | 0.00218 |          1.02088 |    0.02569 | 0.00252 |          1.18118 |    0.02972 |            0.86969 | WELL POWERED       |
| O1b          | Employment retention                           |                867 |                  3183 |         3100 | 0.00041 |  0.86157 | 0.04103 |  -0.00014 |            -0.00339 |  0.00126 | 0.00114 |          0.13259 |    0.02784 | 0.00132 |          0.15341 |    0.03221 |            0.90869 | WELL POWERED       |
| O2a          | Establishment deaths (exit rate)               |                867 |                  2153 |         3100 | 0.04679 |  9.38195 | 2.64058 |   0.0175  |             0.00663 |  0.10337 | 0.1311  |          1.39732 |    0.04965 | 0.15168 |          1.61674 |    0.05744 |            1.26827 | MODERATELY POWERED |
| O2b          | Establishment deaths (log count)               |                867 |                  2153 |         3100 | 0.00641 |  4.01651 | 1.42131 |   0.00035 |             0.00025 |  0.01091 | 0.01795 |          0.44696 |    0.01263 | 0.02077 |          0.51714 |    0.01461 |            1.64569 | MODERATELY POWERED |
| O3a          | Job destruction rate (BDS)                     |                867 |                  2154 |         3100 | 0.10667 | 13.1658  | 5.27113 |   0.03809 |             0.00723 |  0.22399 | 0.29883 |          2.26977 |    0.05669 | 0.34576 |          2.62619 |    0.06559 |            1.3341  | MODERATELY POWERED |
| O3b          | Job creation rate (BDS)                        |                867 |                  2154 |         3100 | 0.09005 | 13.9227  | 5.43401 |  -0.01006 |            -0.00185 |  0.22112 | 0.25228 |          1.812   |    0.04643 | 0.29189 |          2.09653 |    0.05372 |            1.14091 | MODERATELY POWERED |
| O3c          | Job destruction rate (QWI firm job loss)       |                867 |                  3183 |         3100 | 0.00042 |  0.05944 | 0.03997 |   0.00011 |             0.00266 |  0.00148 | 0.00117 |          1.96796 |    0.02926 | 0.00135 |          2.27698 |    0.03386 |            0.7915  | WELL POWERED       |
| O4a          | Employment (log end-of-quarter)                |                867 |                  3185 |         3100 | 0.00345 |  8.83995 | 1.7261  |   0.00089 |             0.00051 |  0.00716 | 0.00967 |          0.10938 |    0.0056  | 0.01119 |          0.12656 |    0.00648 |            1.3507  | MODERATELY POWERED |
| O4b          | Employment (QCEW log; 2014+)                   |                869 |                  2477 |         3107 | 0.00209 |  8.90489 | 1.71991 |  -0.00021 |            -0.00012 |  0.00414 | 0.00587 |          0.06587 |    0.00341 | 0.00679 |          0.07621 |    0.00395 |            1.41558 | MODERATELY POWERED |
| O5a          | Earnings (log avg monthly; stable)             |                867 |                  3183 |         3100 | 0.00177 |  7.98389 | 0.34868 |  -0.00095 |            -0.00272 |  0.00047 | 0.00496 |          0.06218 |    0.01424 | 0.00574 |          0.07195 |    0.01647 |           10.4542  | UNDERPOWERED       |
| O5b          | New-hire earnings (log)                        |                867 |                  3173 |         3100 | 0.00287 |  7.56052 | 0.38163 |   0.0011  |             0.00287 |  0.00748 | 0.00804 |          0.10635 |    0.02107 | 0.0093  |          0.12305 |    0.02438 |            1.07458 | MODERATELY POWERED |
| O7a          | Hire rate                                      |                867 |                  3183 |         3100 | 0.00087 |  0.21467 | 0.08821 |  -0.00028 |            -0.00312 |  0.00268 | 0.00242 |          1.12921 |    0.02748 | 0.0028  |          1.30653 |    0.03179 |            0.90571 | WELL POWERED       |
| O7b          | New-hire rate                                  |                867 |                  3175 |         3100 | 0.00068 |  0.1805  | 0.06942 |  -0.00039 |            -0.00557 |  0.00206 | 0.00191 |          1.05593 |    0.02746 | 0.00221 |          1.22175 |    0.03177 |            0.92361 | WELL POWERED       |
| O7c          | Turnover (stable)                              |                867 |                  3169 |         3100 | 0.0003  |  0.10387 | 0.02898 |   0.00044 |             0.01524 |  0.00022 | 0.00085 |          0.81616 |    0.02926 | 0.00098 |          0.94432 |    0.03385 |            3.83975 | UNDERPOWERED       |
| O8a          | Small-firm establishment death rate (BDS 1-19) |                867 |                  2153 |         3099 | 0.06078 | 11.2512  | 3.13439 |   0.02765 |             0.00882 |  0.01383 | 0.17028 |          1.51348 |    0.05433 | 0.19702 |          1.75114 |    0.06286 |           12.3151  | UNDERPOWERED       |
| O8b          | Small-establishment share (CBP <20)            |                869 |                  2153 |         3108 | 0.00037 |  0.8892  | 0.03853 |   5e-05   |             0.00127 |  0.00073 | 0.00105 |          0.11769 |    0.02716 | 0.00121 |          0.13617 |    0.03143 |            1.42539 | MODERATELY POWERED |
| O10a         | Establishment birth rate                       |                867 |                  2151 |         3100 | 0.04698 |  9.88874 | 3.15389 |   0.01225 |             0.00389 |  0.10716 | 0.13163 |          1.33108 |    0.04173 | 0.1523  |          1.5401  |    0.04829 |            1.22833 | MODERATELY POWERED |
| O10b         | Startup rate (age-0 firms' estabs)             |                867 |                  2144 |         3100 | 0.03919 |  6.55612 | 2.49688 |  -0.00306 |            -0.00123 |  0.08139 | 0.10979 |          1.67463 |    0.04397 | 0.12703 |          1.9376  |    0.05088 |            1.34902 | MODERATELY POWERED |
| O11a         | Out-migration rate                             |                869 |                  1815 |         3105 | 0.02143 |  6.04104 | 2.16164 |   0.00708 |             0.00328 |  0.03656 | 0.06004 |          0.99385 |    0.02777 | 0.06947 |          1.14992 |    0.03214 |            1.64201 | MODERATELY POWERED |
| O11b         | Net migration rate                             |                869 |                  1815 |         3105 | 0.03249 |  0.2488  | 2.86398 |  -0.02825 |            -0.00986 |  0.01413 | 0.09102 |         36.5821  |    0.03178 | 0.10531 |         42.3265  |    0.03677 |            6.44361 | UNDERPOWERED       |
| O11c         | In-migration rate                              |                869 |                  1815 |         3105 | 0.0282  |  6.29304 | 3.4807  |  -0.01966 |            -0.00565 |  0.12414 | 0.07901 |          1.25552 |    0.0227  | 0.09142 |          1.45267 |    0.02626 |            0.63645 | WELL POWERED       |
| O11d         | Out-migrant AGI (log)                          |                869 |                  1815 |         3105 | 0.00543 | 10.3886  | 1.68213 |   0.00701 |             0.00417 |  0.0035  | 0.01523 |          0.14657 |    0.00905 | 0.01762 |          0.16958 |    0.01047 |            4.34648 | UNDERPOWERED       |
| O12a         | Housing units authorized (IHS)                 |                862 |                  2564 |         3047 | 0.02438 |  4.58291 | 2.3698  |   0.00693 |             0.00293 |  0.03584 | 0.0683  |          1.49041 |    0.02882 | 0.07903 |          1.72444 |    0.03335 |            1.90571 | MODERATELY POWERED |
| O12b         | Single-family units (IHS)                      |                862 |                  2564 |         3047 | 0.02329 |  4.37495 | 2.30119 |   0.00726 |             0.00315 |  0.03308 | 0.06526 |          1.49166 |    0.02836 | 0.07551 |          1.72589 |    0.03281 |            1.9728  | MODERATELY POWERED |
| O12c         | Multifamily units (IHS)                        |                862 |                  2564 |         3047 | 0.04066 |  2.15913 | 2.55798 |  -0.00413 |            -0.00162 |  0.06721 | 0.1139  |          5.27547 |    0.04453 | 0.13179 |          6.10387 |    0.05152 |            1.69481 | MODERATELY POWERED |
| O14a         | Establishments (CBP log)                       |                869 |                  2153 |         3108 | 0.00325 |  6.45122 | 1.49361 |   9e-05   |             6e-05   |  0.00436 | 0.00911 |          0.14124 |    0.0061  | 0.01054 |          0.16341 |    0.00706 |            2.08955 | UNDERPOWERED       |
| O14b         | Employment (CBP log)                           |                869 |                  2153 |         3107 | 0.00443 |  8.88861 | 1.72656 |   0.0012  |             0.00069 |  0.00663 | 0.01242 |          0.13978 |    0.0072  | 0.01438 |          0.16173 |    0.00833 |            1.87478 | MODERATELY POWERED |
| O14c         | Payroll (CBP log)                              |                869 |                  2153 |         3107 | 0.00537 | 12.3418  | 1.87574 |   0.00173 |             0.00092 |  0.0083  | 0.01505 |          0.12192 |    0.00802 | 0.01741 |          0.14107 |    0.00928 |            1.81201 | MODERATELY POWERED |

## 21. Literature Novelty

Structured search: 24 phrases x OpenAlex/Crossref/Semantic Scholar (1152 raw hits). Verified closely related papers: 74. See literature_review.md and literature_overlap.csv.


Closest prior work: Davlasheridze, Fisher-Vanden & Klaiber (2017, JEEM) estimate the hurricane analogue for property
losses; Healy & Malhotra (2009) and Rose et al. (2007) estimate returns to mitigation/preparedness in damages;
Merrell, Simmons & Sutter (2005) value tornado shelters by casualties. Disaster-labor/business papers (Groen et al.
2020; Basker & Miranda 2018; Boustan et al. 2020; Ewing et al. 2009 Oklahoma City tornado) have no mitigation
treatment. I found no close causal study in the searched economics/public-policy literature estimating FEMA
tornado/wind mitigation x subsequent tornado effects on labor or business outcomes (novelty HIGH for labor/business,
MEDIUM for migration/housing and damage). Google Scholar, SSRN and RePEc could not be queried by API.


## 22. Publication Potential

| outcome_var              | outcome                                        |   identification_points |   id_variation |   id_pretrend |   id_comparison |   id_timing |   id_estimators |   id_selection | novelty_rating   |   novelty_points |   data_quality_points |   result_strength_points |   mechanism_points |   policy_points | penalties                                                                      |   penalty_total |   publication_score | publication_potential   | identification_rating   | power_rating       |
|:-------------------------|:-----------------------------------------------|------------------------:|---------------:|--------------:|----------------:|------------:|----------------:|---------------:|:-----------------|-----------------:|----------------------:|-------------------------:|-------------------:|----------------:|:-------------------------------------------------------------------------------|----------------:|--------------------:|:------------------------|:------------------------|:-------------------|
| separation_rate          | Worker separations (rate)                      |                      20 |              3 |             6 |               4 |           3 |               4 |              0 | HIGH             |               16 |                  13.5 |                        8 |                  0 |               8 | unclear_completion_timing-10                                                   |             -10 |                55.5 | LOW                     | MEDIUM                  | WELL POWERED       |
| retention_rate           | Employment retention                           |                       9 |              3 |             2 |               2 |           1 |               1 |              0 | HIGH             |               16 |                  13.5 |                        8 |                  0 |               6 | unclear_completion_timing-10                                                   |             -10 |                42.5 | LOW                     | LOW                     | WELL POWERED       |
| establishment_death_rate | Establishment deaths (exit rate)               |                      18 |              3 |             6 |               4 |           1 |               4 |              0 | HIGH             |               15 |                  13.5 |                        3 |                  0 |               8 | unclear_completion_timing-10                                                   |             -10 |                47.5 | LOW                     | MEDIUM                  | MODERATELY POWERED |
| log_estab_deaths         | Establishment deaths (log count)               |                       9 |              3 |             2 |               2 |           1 |               1 |              0 | HIGH             |               15 |                  13.5 |                        6 |                  0 |               6 | unclear_completion_timing-10                                                   |             -10 |                39.5 | LOW                     | LOW                     | MODERATELY POWERED |
| job_destruction_rate     | Job destruction rate (BDS)                     |                      22 |              3 |             6 |               4 |           3 |               4 |              2 | HIGH             |               15 |                  13.5 |                        3 |                  0 |               8 | unclear_completion_timing-10                                                   |             -10 |                51.5 | LOW                     | HIGH                    | MODERATELY POWERED |
| job_creation_rate        | Job creation rate (BDS)                        |                       9 |              3 |             2 |               2 |           1 |               1 |              0 | HIGH             |               15 |                  13.5 |                        6 |                  0 |               6 | unclear_completion_timing-10                                                   |             -10 |                39.5 | LOW                     | LOW                     | MODERATELY POWERED |
| job_destruction_rate_qwi | Job destruction rate (QWI firm job loss)       |                      22 |              3 |             6 |               4 |           3 |               4 |              2 | HIGH             |               16 |                  13.5 |                       10 |                  0 |               6 | unclear_completion_timing-10                                                   |             -10 |                57.5 | LOW                     | HIGH                    | WELL POWERED       |
| log_employment           | Employment (log end-of-quarter)                |                      18 |              3 |             6 |               2 |           1 |               4 |              2 | HIGH             |               16 |                  13.5 |                        3 |                  0 |               8 | unclear_completion_timing-10                                                   |             -10 |                48.5 | LOW                     | MEDIUM                  | MODERATELY POWERED |
| log_qcew_emp             | Employment (QCEW log; 2014+)                   |                      13 |              3 |             6 |               2 |           1 |               1 |              0 | HIGH             |               16 |                  13.5 |                        3 |                  0 |               6 | unclear_completion_timing-10                                                   |             -10 |                41.5 | LOW                     | LOW                     | MODERATELY POWERED |
| log_earnings             | Earnings (log avg monthly; stable)             |                      17 |              3 |             3 |               4 |           1 |               4 |              2 | HIGH             |               16 |                  13.5 |                        3 |                  0 |               8 | unclear_completion_timing-10                                                   |             -10 |                47.5 | LOW                     | MEDIUM                  | UNDERPOWERED       |
| log_new_hire_earnings    | New-hire earnings (log)                        |                       9 |              3 |             2 |               2 |           1 |               1 |              0 | HIGH             |               16 |                  13.5 |                        3 |                  0 |               6 | unclear_completion_timing-10                                                   |             -10 |                37.5 | LOW                     | LOW                     | MODERATELY POWERED |
| hire_rate                | Hire rate                                      |                      22 |              3 |             6 |               4 |           3 |               4 |              2 | HIGH             |               16 |                  13.5 |                        3 |                  0 |               6 | unclear_completion_timing-10                                                   |             -10 |                50.5 | LOW                     | HIGH                    | WELL POWERED       |
| new_hire_rate            | New-hire rate                                  |                       9 |              3 |             2 |               2 |           1 |               1 |              0 | HIGH             |               16 |                  13.5 |                        3 |                  0 |               6 | unclear_completion_timing-10                                                   |             -10 |                37.5 | LOW                     | LOW                     | WELL POWERED       |
| turnover                 | Turnover (stable)                              |                       9 |              3 |             2 |               2 |           1 |               1 |              0 | HIGH             |               16 |                  13.5 |                        3 |                  0 |               6 | unclear_completion_timing-10                                                   |             -10 |                37.5 | LOW                     | LOW                     | UNDERPOWERED       |
| small_estab_death_rate   | Small-firm establishment death rate (BDS 1-19) |                      22 |              3 |             6 |               4 |           3 |               4 |              2 | HIGH             |               15 |                  13.5 |                       10 |                  0 |               6 | unclear_completion_timing-10                                                   |             -10 |                56.5 | LOW                     | HIGH                    | UNDERPOWERED       |
| small_estab_share        | Small-establishment share (CBP <20)            |                       9 |              3 |             2 |               2 |           1 |               1 |              0 | HIGH             |               15 |                  13.5 |                        3 |                  0 |               6 | unclear_completion_timing-10                                                   |             -10 |                36.5 | LOW                     | LOW                     | MODERATELY POWERED |
| establishment_birth_rate | Establishment birth rate                       |                       9 |              3 |             2 |               2 |           1 |               1 |              0 | HIGH             |               15 |                  13.5 |                        3 |                  0 |               6 | unclear_completion_timing-10                                                   |             -10 |                36.5 | LOW                     | LOW                     | MODERATELY POWERED |
| startup_rate             | Startup rate (age-0 firms' estabs)             |                       9 |              3 |             2 |               2 |           1 |               1 |              0 | HIGH             |               15 |                  13.5 |                        3 |                  0 |               6 | unclear_completion_timing-10                                                   |             -10 |                36.5 | LOW                     | LOW                     | MODERATELY POWERED |
| outmigration_rate        | Out-migration rate                             |                      22 |              3 |             6 |               4 |           3 |               4 |              2 | MEDIUM           |               11 |                  12.7 |                        3 |                  0 |               6 | unclear_completion_timing-10                                                   |             -10 |                44.7 | LOW                     | HIGH                    | MODERATELY POWERED |
| net_migration_rate       | Net migration rate                             |                       9 |              3 |             2 |               2 |           1 |               1 |              0 | MEDIUM           |               11 |                  13.5 |                        3 |                  0 |               6 | unclear_completion_timing-10                                                   |             -10 |                32.5 | LOW                     | LOW                     | UNDERPOWERED       |
| inmigration_rate         | In-migration rate                              |                       9 |              3 |             2 |               2 |           1 |               1 |              0 | MEDIUM           |               11 |                  13.5 |                        8 |                  0 |               6 | unclear_completion_timing-10                                                   |             -10 |                37.5 | LOW                     | LOW                     | WELL POWERED       |
| log_outflow_AGI          | Out-migrant AGI (log)                          |                       9 |              3 |             2 |               2 |           1 |               1 |              0 | MEDIUM           |               11 |                  13.5 |                        3 |                  0 |               6 | unclear_completion_timing-10                                                   |             -10 |                32.5 | LOW                     | LOW                     | UNDERPOWERED       |
| ihs_units                | Housing units authorized (IHS)                 |                      22 |              3 |             6 |               4 |           3 |               4 |              2 | MEDIUM           |               11 |                  13.4 |                        3 |                  0 |               6 | unclear_completion_timing-10                                                   |             -10 |                45.4 | LOW                     | HIGH                    | MODERATELY POWERED |
| ihs_sf_units             | Single-family units (IHS)                      |                       9 |              3 |             2 |               2 |           1 |               1 |              0 | MEDIUM           |               11 |                  13.5 |                        3 |                  0 |               6 | unclear_completion_timing-10                                                   |             -10 |                32.5 | LOW                     | LOW                     | MODERATELY POWERED |
| ihs_mf_units             | Multifamily units (IHS)                        |                       9 |              3 |             2 |               2 |           1 |               1 |              0 | MEDIUM           |               11 |                  13.5 |                        3 |                  0 |               6 | unclear_completion_timing-10                                                   |             -10 |                32.5 | LOW                     | LOW                     | MODERATELY POWERED |
| log_establishments       | Establishments (CBP log)                       |                      16 |              3 |             0 |               4 |           3 |               4 |              2 | HIGH             |               15 |                  13.5 |                        2 |                  0 |               6 | severe_pretrends-10;unclear_completion_timing-10;multiple_testing_fragility-10 |             -30 |                22.5 | LOW                     | MEDIUM                  | UNDERPOWERED       |
| log_cbp_employment       | Employment (CBP log)                           |                       9 |              3 |             2 |               2 |           1 |               1 |              0 | HIGH             |               15 |                  13.5 |                        3 |                  0 |               6 | unclear_completion_timing-10                                                   |             -10 |                36.5 | LOW                     | LOW                     | MODERATELY POWERED |
| log_payroll              | Payroll (CBP log)                              |                       9 |              3 |             2 |               2 |           1 |               1 |              0 | HIGH             |               15 |                  13.5 |                        3 |                  0 |               6 | unclear_completion_timing-10                                                   |             -10 |                36.5 | LOW                     | LOW                     | MODERATELY POWERED |

## 23. Journal Fit

| outcome                                        | outcome_var              | robustness_rating    | best_journal                                    | second_journal                                    | third_journal                          | what_would_make_top_choice_realistic                     |
|:-----------------------------------------------|:-------------------------|:---------------------|:------------------------------------------------|:--------------------------------------------------|:---------------------------------------|:---------------------------------------------------------|
| Worker separations (rate)                      | separation_rate          | NO DETECTABLE EFFECT | Regional Science and Urban Economics (HIGH FIT) | Labour Economics (HIGH FIT)                       | Journal of Regional Science (HIGH FIT) | credible local economic resilience contribution          |
| Employment retention                           | retention_rate           | NO DETECTABLE EFFECT | Regional Science and Urban Economics (HIGH FIT) | Labour Economics (HIGH FIT)                       | Journal of Regional Science (HIGH FIT) | credible local economic resilience contribution          |
| Establishment deaths (exit rate)               | establishment_death_rate | UNDERPOWERED         | Risk Analysis (HIGH FIT)                        | Review of Regional Studies (HIGH FIT)             | Natural Hazards Review (HIGH FIT)      | risk-reduction evidence, decision relevance              |
| Establishment deaths (log count)               | log_estab_deaths         | MIXED                | Risk Analysis (HIGH FIT)                        | Review of Regional Studies (HIGH FIT)             | Natural Hazards Review (HIGH FIT)      | risk-reduction evidence, decision relevance              |
| Job destruction rate (BDS)                     | job_destruction_rate     | UNDERPOWERED         | Risk Analysis (HIGH FIT)                        | Review of Regional Studies (HIGH FIT)             | Natural Hazards Review (HIGH FIT)      | risk-reduction evidence, decision relevance              |
| Job creation rate (BDS)                        | job_creation_rate        | MIXED                | Risk Analysis (HIGH FIT)                        | Review of Regional Studies (HIGH FIT)             | Natural Hazards Review (HIGH FIT)      | risk-reduction evidence, decision relevance              |
| Job destruction rate (QWI firm job loss)       | job_destruction_rate_qwi | MODERATELY ROBUST    | Regional Science and Urban Economics (HIGH FIT) | Labour Economics (HIGH FIT)                       | Journal of Regional Science (HIGH FIT) | credible local economic resilience contribution          |
| Employment (log end-of-quarter)                | log_employment           | UNDERPOWERED         | Risk Analysis (HIGH FIT)                        | Review of Regional Studies (HIGH FIT)             | Natural Hazards Review (HIGH FIT)      | risk-reduction evidence, decision relevance              |
| Employment (QCEW log; 2014+)                   | log_qcew_emp             | UNDERPOWERED         | Risk Analysis (HIGH FIT)                        | Review of Regional Studies (HIGH FIT)             | Natural Hazards Review (HIGH FIT)      | risk-reduction evidence, decision relevance              |
| Earnings (log avg monthly; stable)             | log_earnings             | UNDERPOWERED         | Risk Analysis (HIGH FIT)                        | Review of Regional Studies (HIGH FIT)             | Natural Hazards Review (HIGH FIT)      | risk-reduction evidence, decision relevance              |
| New-hire earnings (log)                        | log_new_hire_earnings    | UNDERPOWERED         | Risk Analysis (HIGH FIT)                        | Review of Regional Studies (HIGH FIT)             | Natural Hazards Review (HIGH FIT)      | risk-reduction evidence, decision relevance              |
| Hire rate                                      | hire_rate                | UNDERPOWERED         | Risk Analysis (HIGH FIT)                        | Review of Regional Studies (HIGH FIT)             | Natural Hazards Review (HIGH FIT)      | risk-reduction evidence, decision relevance              |
| New-hire rate                                  | new_hire_rate            | UNDERPOWERED         | Risk Analysis (HIGH FIT)                        | Review of Regional Studies (HIGH FIT)             | Natural Hazards Review (HIGH FIT)      | risk-reduction evidence, decision relevance              |
| Turnover (stable)                              | turnover                 | UNDERPOWERED         | Risk Analysis (HIGH FIT)                        | Review of Regional Studies (HIGH FIT)             | Natural Hazards Review (HIGH FIT)      | risk-reduction evidence, decision relevance              |
| Small-firm establishment death rate (BDS 1-19) | small_estab_death_rate   | MODERATELY ROBUST    | Small Business Economics (HIGH FIT)             | Regional Science and Urban Economics (HIGH FIT)   | Land Economics (HIGH FIT)              | small-business mechanism (liquidity, size heterogeneity) |
| Small-establishment share (CBP <20)            | small_estab_share        | UNDERPOWERED         | Risk Analysis (HIGH FIT)                        | Review of Regional Studies (HIGH FIT)             | Natural Hazards Review (HIGH FIT)      | risk-reduction evidence, decision relevance              |
| Establishment birth rate                       | establishment_birth_rate | UNDERPOWERED         | Risk Analysis (HIGH FIT)                        | Review of Regional Studies (HIGH FIT)             | Natural Hazards Review (HIGH FIT)      | risk-reduction evidence, decision relevance              |
| Startup rate (age-0 firms' estabs)             | startup_rate             | UNDERPOWERED         | Risk Analysis (HIGH FIT)                        | Review of Regional Studies (HIGH FIT)             | Natural Hazards Review (HIGH FIT)      | risk-reduction evidence, decision relevance              |
| Out-migration rate                             | outmigration_rate        | UNDERPOWERED         | Risk Analysis (HIGH FIT)                        | Review of Regional Studies (HIGH FIT)             | Natural Hazards Review (HIGH FIT)      | risk-reduction evidence, decision relevance              |
| Net migration rate                             | net_migration_rate       | UNDERPOWERED         | Risk Analysis (HIGH FIT)                        | Review of Regional Studies (HIGH FIT)             | Natural Hazards Review (HIGH FIT)      | risk-reduction evidence, decision relevance              |
| In-migration rate                              | inmigration_rate         | NO DETECTABLE EFFECT | Regional Science and Urban Economics (HIGH FIT) | Land Economics (HIGH FIT)                         | Journal of Regional Science (HIGH FIT) | credible local economic resilience contribution          |
| Out-migrant AGI (log)                          | log_outflow_AGI          | UNDERPOWERED         | Risk Analysis (HIGH FIT)                        | Review of Regional Studies (HIGH FIT)             | Natural Hazards Review (HIGH FIT)      | risk-reduction evidence, decision relevance              |
| Housing units authorized (IHS)                 | ihs_units                | UNDERPOWERED         | Risk Analysis (HIGH FIT)                        | Review of Regional Studies (HIGH FIT)             | Natural Hazards Review (HIGH FIT)      | risk-reduction evidence, decision relevance              |
| Single-family units (IHS)                      | ihs_sf_units             | UNDERPOWERED         | Risk Analysis (HIGH FIT)                        | Review of Regional Studies (HIGH FIT)             | Natural Hazards Review (HIGH FIT)      | risk-reduction evidence, decision relevance              |
| Multifamily units (IHS)                        | ihs_mf_units             | UNDERPOWERED         | Risk Analysis (HIGH FIT)                        | Review of Regional Studies (HIGH FIT)             | Natural Hazards Review (HIGH FIT)      | risk-reduction evidence, decision relevance              |
| Establishments (CBP log)                       | log_establishments       | NOT ROBUST           | Small Business Economics (MEDIUM FIT)           | Regional Science and Urban Economics (MEDIUM FIT) | Land Economics (MEDIUM FIT)            | small-business mechanism (liquidity, size heterogeneity) |
| Employment (CBP log)                           | log_cbp_employment       | UNDERPOWERED         | Risk Analysis (HIGH FIT)                        | Review of Regional Studies (HIGH FIT)             | Natural Hazards Review (HIGH FIT)      | risk-reduction evidence, decision relevance              |
| Payroll (CBP log)                              | log_payroll              | UNDERPOWERED         | Risk Analysis (HIGH FIT)                        | Review of Regional Studies (HIGH FIT)             | Natural Hazards Review (HIGH FIT)      | risk-reduction evidence, decision relevance              |

## 24. Identification Threats


1. **Endogenous, post-disaster treatment assignment (biggest threat).** 94% of strict projects are HMGP grants that
   exist only after a disaster declaration; 44% follow tornado/severe-storm declarations. Treated counties differ on
   pre-treatment damage per intensity (+40-50%, placebo p < 1e-4) and on historical tornado density (raw SMD 0.6-0.9).
   Matching/weighting fixes observables but not selection on recent shocks; the never-funded applicant pool is
   only 36 counties.
2. **Treatment timing is a proxy.** OpenFEMA has no completion date; obligation + 2 years vs. a median 3.6-year
   obligation-to-closeout gap means misclassification of operational status near the cutoff (attenuation).
3. **Exposure-outcome scale mismatch.** Tornado paths cover a tiny share of a county; county aggregates dilute both
   the shock and any protection, which drives the near-zero tornado main effects and the UNDERPOWERED ratings.
4. **Geographic mismatch of treatment.** Projects are coded to a primary county; 8% are statewide; safe rooms protect
   specific sites (schools, mobile-home parks), not county labor markets.
5. **Intensity is damage-based.** EF ratings are inferred from damage, so Mitigation x intensity specifications
   condition on a variable mitigation can affect.
6. **Outcome measurement.** NOAA property damage is an estimate whose methods changed over time; QWI suppression is low
   (1-2%) at county totals but higher in cells.


## 25. Best Paper Design


**Best paper to write (redesign): "Does Tornado Mitigation Reduce Losses? Evidence from FEMA Safe Rooms and Wind
Retrofits."** A tornado analogue to Davlasheridze et al. (2017), with three changes that address the threats above:
(a) **exposure independent of damage**: tornado path length/width and swath area from NOAA/SPC GIS tracks, or
radar-derived rotation/wind fields (e.g. Multi-Radar Multi-Sensor rotation tracks, 2000s+), instead of EF ratings;
(b) **sub-county matching**: intersect tornado swaths with project sites (HMA project-site inventories
geocode many projects) and with census blocks/ZIPs, so the comparison is struck-and-protected vs struck-and-unprotected
places; (c) **selection**: compare counties/places with funded projects to applicants denied or not selected, and use
the state HMGP ceiling (a formula share of post-disaster aid) as an instrument for mitigation intensity. The labor-market
null (separations) becomes a secondary, informative result: even large wind-mitigation programs do not show up in
county labor-market flows, which bounds the labor-market benefits in BCA.


## 26. Alternative Paper Designs

### PAPER A: LABOR MARKET RESILIENCE -- **MAYBE**

- Research question: Do FEMA tornado/wind mitigation investments reduce tornado-induced worker separations and employment/earnings losses?
- Primary outcome: Worker separations (rate) (NO DETECTABLE EFFECT, No detectable effect)
- Secondary outcomes: log_employment, log_earnings, hire_rate, log_new_hire_earnings, turnover, new_hire_rate
- Strongest secondary result: Employment (log end-of-quarter) (UNDERPOWERED, Underpowered)
- Publication score (heuristic): 55.5 (LOW)
- Best journal: Regional Science and Urban Economics (HIGH FIT)
- Main threat: endogenous post-disaster HMGP awards and proxy (obligation+2y) completion timing

| Question | Answer |
|---|---|
| 1. Statistically distinguishable from zero? | No (beta=0.0005, p=0.542, BH q=0.677) |
| 2. Economically meaningful? | No (|beta| vs E*=0.0025; 0.22% of mean) |
| 3. Survives modern DiD estimators? | Yes (stacked=0.0007, p=0.482; IW=0.0004) |
| 4. Survives alternative treatment timing? | Yes |
| 5. Survives alternative tornado definitions? | No |
| 6. Survives leave-one-state-out? | Yes (sign share 1.00) |
| 7. Passes pretrend tests? | Yes (p=0.226) |
| 8. Passes placebo tests? | Yes (p=0.932; RI p=0.500) |
| 9. Mechanism evidence? | no supporting mechanism evidence |
| 10. Novelty high? | HIGH |
| 11. Power adequate? | WELL POWERED |
| 12. Treatment assignment sufficiently credible? | Partly: DiD on staggered FEMA awards with matched/weighted comparisons; no quasi-random assignment (see quasi_experiment_assessment.md) |

### PAPER B: BUSINESS RESILIENCE -- **NO-GO**

- Research question: Do FEMA tornado/wind mitigation investments reduce tornado-induced establishment deaths and job destruction?
- Primary outcome: Establishment deaths (exit rate) (UNDERPOWERED, Underpowered)
- Secondary outcomes: job_destruction_rate, establishment_birth_rate, startup_rate, log_establishments, log_payroll, small_estab_death_rate
- Strongest secondary result: Small-firm establishment death rate (BDS 1-19) (MODERATELY ROBUST, Adverse)
- Publication score (heuristic): 47.5 (LOW)
- Best journal: Risk Analysis (HIGH FIT)
- Main threat: endogenous post-disaster HMGP awards and proxy (obligation+2y) completion timing

| Question | Answer |
|---|---|
| 1. Statistically distinguishable from zero? | No (beta=0.0437, p=0.350, BH q=0.584) |
| 2. Economically meaningful? | No (|beta| vs E*=0.1034; 0.47% of mean) |
| 3. Survives modern DiD estimators? | Yes (stacked=0.1038, p=0.100; IW=0.1216) |
| 4. Survives alternative treatment timing? | No |
| 5. Survives alternative tornado definitions? | Yes |
| 6. Survives leave-one-state-out? | Yes (sign share 1.00) |
| 7. Passes pretrend tests? | Yes (p=0.735) |
| 8. Passes placebo tests? | Yes (p=0.593; RI p=0.360) |
| 9. Mechanism evidence? | no supporting mechanism evidence |
| 10. Novelty high? | HIGH |
| 11. Power adequate? | MODERATELY POWERED |
| 12. Treatment assignment sufficiently credible? | Partly: DiD on staggered FEMA awards with matched/weighted comparisons; no quasi-random assignment (see quasi_experiment_assessment.md) |

### PAPER C: SPATIAL / FISCAL RESILIENCE -- **NO-GO**

- Research question: Do FEMA tornado/wind mitigation investments reduce post-tornado out-migration and change rebuilding?
- Primary outcome: Out-migration rate (UNDERPOWERED, Underpowered)
- Secondary outcomes: net_migration_rate, inmigration_rate, ihs_units, ihs_sf_units
- Strongest secondary result: In-migration rate (NO DETECTABLE EFFECT, No detectable effect)
- Publication score (heuristic): 44.7 (LOW)
- Best journal: Risk Analysis (HIGH FIT)
- Main threat: endogenous post-disaster HMGP awards and proxy (obligation+2y) completion timing

| Question | Answer |
|---|---|
| 1. Statistically distinguishable from zero? | No (beta=0.0317, p=0.139, BH q=0.713) |
| 2. Economically meaningful? | No (|beta| vs E*=0.0366; 0.53% of mean) |
| 3. Survives modern DiD estimators? | Yes (stacked=0.0402, p=0.306; IW=0.0379) |
| 4. Survives alternative treatment timing? | Yes |
| 5. Survives alternative tornado definitions? | Yes |
| 6. Survives leave-one-state-out? | Yes (sign share 1.00) |
| 7. Passes pretrend tests? | Yes (p=0.883) |
| 8. Passes placebo tests? | Yes (p=0.457; RI p=n/a) |
| 9. Mechanism evidence? | no supporting mechanism evidence |
| 10. Novelty high? | MEDIUM |
| 11. Power adequate? | MODERATELY POWERED |
| 12. Treatment assignment sufficiently credible? | Partly: DiD on staggered FEMA awards with matched/weighted comparisons; no quasi-random assignment (see quasi_experiment_assessment.md) |


## 27. Data Improvements That Would Matter Most


Most valuable improvements, in order: (1) **project completion dates and geocoded project sites** (FEMA FOIA, or the
HmaSubapplicationsProjectSiteInventories dataset for recent projects); (2) **damage-independent hazard intensity**
(SPC GIS tracks with width, MRMS rotation tracks); (3) **sub-county outcomes**: LEHD LODES block-level jobs,
ZIP Business Patterns, or establishment-level microdata (Census RDC: LBD/BR) to match outcomes to tornado swaths;
(4) **BRIC/PDM national competition scores and funding lines** (FOIA) for an RD; (5) property-level losses (FEMA
Individual Assistance inspections, insurance claims) for a damage outcome not produced by NWS estimators.




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


## 28. Final GO/NO-GO Recommendation

### Explicit answers

**A. Strongest credible causal result.** None. No outcome shows a protective effect that is both statistically distinguishable after multiple testing and robust; the strongest *credible* causal statement is the informative null for worker separations (95% CI rules out effects larger than 0.05 within-county SD; pretrend, placebo, RI and leave-one-state-out all pass). *(analyst answer; rule-based output was: Job creation rate (BDS) (MIXED))*

**B. Most statistically robust outcome.** Worker separations as a null (sign consistency 0.89, LOSO 1.00, placebo p = 0.93, RI p = 0.50). Among non-null signs, small-firm establishment deaths are the most consistently signed (98% of credible specs), but in the adverse direction and with BH q = 0.22. *(analyst answer; rule-based output was: Job destruction rate (QWI firm job loss) (MODERATELY ROBUST))*

**C. Largest economically meaningful effect.** None that is credible. The only large effect is the reported-damage reduction (about -42% per EF step), which fails the pre-treatment placebo; all labor and business point estimates are below 1.3% of the mean. *(analyst answer; rule-based output was: Establishment deaths (log count) (0.014 SD; MIXED))*

**D. Best novelty x feasibility.** Job destruction rate (QWI firm job loss)

**E. Highest publication potential.** No outcome reaches 60 on the heuristic in its current form (max 57.5: separations and QWI job destruction). The redesigned damage-loss paper has the highest potential (see Section 25). *(analyst answer; rule-based output was: Job destruction rate (QWI firm job loss) (score 57.5))*

**F. Promising but underpowered.** Small-firm establishment death rate (BDS 1-19), Earnings (log avg monthly; stable), Establishments (CBP log), Turnover (stable), Net migration rate, Out-migrant AGI (log)

**G. Effects that disappear under robustness.** Establishments (CBP log), Establishment deaths (log count)

**H. Driven by Oklahoma or Texas?.** Worker separations (rate): primary 0.0005; without OK 0.0005 (p=0.534); without TX 0.0005 (p=0.533); Establishment deaths (exit rate): primary 0.0437; without OK 0.0505 (p=0.306); without TX 0.0524 (p=0.277); Job destruction rate (BDS): primary 0.1107; without OK 0.1581 (p=0.151); without TX 0.1257 (p=0.241); Employment (log end-of-quarter): primary 0.0012; without OK -0.0002 (p=0.962); without TX 0.0032 (p=0.342); Earnings (log avg monthly; stable): primary -0.0017; without OK -0.0021 (p=0.260); without TX -0.0011 (p=0.513)

**I. Driven by 2011 Super Outbreak / major events?.** Worker separations (rate): LOEO sign share 1.00, driving events [nan]; Establishment deaths (exit rate): LOEO sign share 1.00, driving events [nan]; Job destruction rate (BDS): LOEO sign share 1.00, driving events [nan]; Employment (log end-of-quarter): LOEO sign share 1.00, driving events [nan]; Earnings (log avg monthly; stable): LOEO sign share 1.00, driving events [nan]

**J. Does treatment timing matter?.** Worker separations (rate): timing_pass=1.0; Establishment deaths (exit rate): timing_pass=0.0; Job destruction rate (BDS): timing_pass=1.0; Employment (log end-of-quarter): timing_pass=0.0; Earnings (log avg monthly; stable): timing_pass=0.0

**K. Does strict definition survive?.** Worker separations (rate): NO DETECTABLE EFFECT (No detectable effect); Establishment deaths (exit rate): UNDERPOWERED (Underpowered); Job destruction rate (BDS): UNDERPOWERED (Underpowered); Employment (log end-of-quarter): UNDERPOWERED (Underpowered); Earnings (log avg monthly; stable): UNDERPOWERED (Underpowered)

**L. Results for EF2+?.** Worker separations (rate): EF2+ beta=-0.0003 (p=0.826); Establishment deaths (exit rate): EF2+ beta=0.1133 (p=0.122); Job destruction rate (BDS): EF2+ beta=0.0230 (p=0.889); Employment (log end-of-quarter): EF2+ beta=-0.0001 (p=0.986); Earnings (log avg monthly; stable): EF2+ beta=-0.0053 (p=0.055)

**M. Do modern estimators confirm TWFE?.** Worker separations (rate): TWFE 0.0005 vs stacked 0.0007 / IW 0.0004 -> estimator_pass=1.0; Establishment deaths (exit rate): TWFE 0.0437 vs stacked 0.1038 / IW 0.1216 -> estimator_pass=1.0; Job destruction rate (BDS): TWFE 0.1107 vs stacked 0.1202 / IW 0.1572 -> estimator_pass=1.0; Employment (log end-of-quarter): TWFE 0.0012 vs stacked 0.0017 / IW 0.0023 -> estimator_pass=1.0; Earnings (log avg monthly; stable): TWFE -0.0017 vs stacked -0.0004 / IW -0.0009 -> estimator_pass=1.0

**N. Pretrends acceptable?.** Worker separations (rate): p=0.226; Establishment deaths (exit rate): p=0.735; Job destruction rate (BDS): p=0.277; Employment (log end-of-quarter): p=0.888; Earnings (log avg monthly; stable): p=0.053

**O. Placebos pass?.** Worker separations (rate): placebo p=0.932, RI p=0.500; Establishment deaths (exit rate): placebo p=0.593, RI p=0.360; Job destruction rate (BDS): placebo p=0.672, RI p=0.260; Employment (log end-of-quarter): placebo p=0.653, RI p=0.830; Earnings (log avg monthly; stable): placebo p=0.742, RI p=0.570

**P. Completion timing reliable?.** No. OpenFEMA publishes no physical completion date (0% coverage). Closeout is observed for 88.8% of strict projects (median 3.6 years after obligation) and is an administrative upper bound on completion. Primary timing is therefore a proxy.

**Q. Convincing mechanism evidence?.** No. M1 damage reduction is large and specification-robust (-42% per EF step; -58% within-treated after dropping 5 pre-treatment years) but fails the pre-treatment placebo (+39% to +50%, p < 1e-4) and relies on damage-based EF ratings; fatalities and injuries are not reduced. M2 business continuity goes the wrong way (physical-premise industries have higher separations, p = 0.01); M3 match preservation and M4 small-business protection are not supported. *(analyst answer; rule-based output was: M1 log_damage: -0.3662 (p=0.000); M1 log_fatalities: 0.0098 (p=0.006); M1 log_injuries: -0.0006 (p=0.945))*

**R. Treatment adoption too endogenous?.** 
Partly. Adoption is clearly endogenous to past disasters (pre-treatment damage placebo fails, p < 1e-4), but the
economic outcomes show no adoption pre-trends (adoption event-study pre p = 0.21-0.88, except earnings p = 0.03)
and acceptable tornado-event pre-trends (p = 0.23-0.99, except earnings p = 0.053, borderline). For the economic outcomes endogeneity is less of a problem than
power and dilution; for the damage outcome it is decisive. Credible publication requires the redesign in Section 25.


**S. Would a funding cutoff help?.** Yes, materially, but no usable public cutoff exists (see quasi_experiment_assessment.md).

**T. Best paper to write.** 
The damage-loss paper (Section 25), redesigned with damage-independent exposure, sub-county matching and
applicant/HMGP-ceiling identification. Labor/business resilience at the county level should be reported only as a
bounded null within that paper, not as a standalone paper.



### Decision rule applied

GO requires a ROBUST/strongly MODERATELY ROBUST economically important outcome, credible identification, acceptable pretrends/placebos and adequate power. Decision basis: No confirmatory outcome is ROBUST or MODERATELY ROBUST in the protective direction; separations are an informative null, other labor outcomes are underpowered, and the only consistent business signs are adverse and fail multiple testing. The original county-level labor/business resilience paper is therefore NO-GO in its current form. However, an economically large and specification-robust reduction in reported tornado damage per EF step in mitigated counties (about -42% to -60%) exists, while its identification fails the pre-treatment placebo (selection on damage) and relies on a damage-based intensity measure. This matches GO WITH REDESIGN: an interesting result whose identification (exposure measured independently of damage, sub-county matching, applicant or HMGP-ceiling comparisons, completion timing) must be improved. Not PILOT ONLY, because the data are already fully assembled and the remaining problem is identification, not instability..


# FINAL PROJECT DECISION: GO WITH REDESIGN
