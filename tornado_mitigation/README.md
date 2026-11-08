# Local Tornado Mitigation and Economic Resilience ("Tornedo" project)

Do FEMA-funded tornado/severe-wind mitigation investments (safe rooms, wind retrofits) reduce the economic
disruption caused by *subsequent* tornadoes in U.S. counties? Estimand: Mitigation x subsequent tornado.
Full specification: `../PROJECT_SPEC.md`. Frozen analysis plan: `output/final/preregistration_snapshot.md`.

## Quick start

```powershell
py -3.13 -m pip install -r requirements.txt     # Python 3.11+ (built with 3.13)
copy .env.example .env                          # then add CENSUS_API_KEY=... (free: https://api.census.gov/data/key_signup.html)
py -3.13 run_all.py --all                       # or any of --download --clean --build --estimate --robustness --report
py -3.13 -m pytest tests                        # 20 tests (parsers, crosswalk, panels, estimator simulations)
```

Raw downloads are cached; re-running never re-downloads. Random seed 20261007 everywhere.
Hardware note: built on an 8 GB RAM machine; heavy steps use 2-3 workers and column-pruned panels.

## Data (all public; see `output/logs/data_sources.csv`)

| Source | Use | Access |
|---|---|---|
| OpenFEMA HMA Projects v4, HMA Subapplications v2, HMA Financial Transactions v1, Disaster Declarations v2 | treatment | no key |
| NOAA/NCEI Storm Events details 1950-2025 | tornado exposure, damage, casualties | no key |
| Census LEHD QWI (bulk sa files; API for education/race/ethnicity/firm-size cells) | labor outcomes | bulk no key; API needs key |
| Census BDS 2023 (county, x firm size/age/sector) | establishment deaths, job destruction, births | no key |
| BLS QCEW open-data slices 2014-2025 | employment replication, industries | no key |
| Census CBP 1998-2023 | establishments, payroll, size classes | no key |
| IRS SOI county migration 2011/12-2022/23 | migration | no key |
| Census Building Permits Survey 1990-2025 | rebuilding | no key |
| Census population estimates; OMB 2020 CBSA delineation | controls | no key |

Key data facts: OpenFEMA publishes **no physical completion date** -> primary timing = obligation + 2 years
(pre-specified fallback). Public finance is LOW feasibility (sample-based annual survey) and is not estimated.

## Pipeline (src/)

`00`-`21` download/clean; `22` crosswalk (+`22b` population, metro); `23` master panels; `24` feasibility;
`25` descriptives; `26` primary models; `27` tornado & adoption event studies; `28` stacked estimators;
`29` mechanisms; `30` heterogeneity; `31` matching/weighting; `32` robustness R01-R69 + spec curves;
`33` placebos R36-R40; `34` leave-one-state/event-out; `35` power; `36` multiple testing, indices,
robustness metrics and classification; `37` literature search (`37b` quasi-experiment, `37c` warning systems);
`38` publication score; `39` journal fit; `40` tables; `41` figures; `42` report. Core estimator: `src/est.py`.

## Key outputs

- `output/final/master_outcome_assessment.xlsx` / `.md` - the main deliverable
- `output/final/research_assessment.md` - full report with answers A-T and the GO/NO-GO decision
- `output/final/preliminary_feasibility.md`, `preregistration_snapshot.md`, `quasi_experiment_assessment.md`,
  `warning_system_feasibility.md`, `paper_bundles.md`
- `output/tables/` Tables 1-12; `output/figures/` Figures 1-20; `output/models/` every estimate (CSV)
- `output/literature/literature_overlap.csv`, `literature_review.md`
- `output/diagnostics/` validation reports, classification sample (500+), balance tables
