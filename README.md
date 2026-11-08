# The Application Gap: Why Small Counties Receive Fewer Federal Disaster Mitigation Grants

## Purpose

This repository contains the Python pipeline and LaTeX manuscript drafts for a county-level study of FEMA hazard mitigation funding after tornadoes and severe storms in the United States. The project began with the question of whether FEMA-funded tornado and wind mitigation projects reduce the economic disruption caused by later tornadoes. The later scripts (49 to 52) study a different question, which the manuscript drafts use: whether, and at which stage, small counties fall behind in turning tornado and severe-storm disaster declarations into funded Hazard Mitigation Grant Program (HMGP) projects. The unit of observation in that analysis is a county by major disaster declaration.

## Status

The paper is under review. The manuscript folders in this repository hold earlier drafts under different working titles; they are manuscript drafts, not the version under review.

## Author

Mahyar Rezazadeh (sole author).

## Data

The data are **not** included in this repository, apart from a few small files noted under Known limitations. All sources listed in the code are public. Most are downloaded by the scripts; two Census of Governments files must be placed by hand.

| Source | Use | How to obtain |
|---|---|---|
| OpenFEMA: HMA Projects, HMA Subapplications, HMA Financial Transactions, Disaster Declarations Summaries | treatment, applications, declarations | downloaded by `01_download_fema.py`; no key |
| NOAA/NCEI Storm Events details, 1950 onward | tornado exposure, damage, casualties | downloaded by `05_download_noaa_storms.py`; no key |
| NOAA Storm Prediction Center tornado tracks (`1950-2024_actual_tornadoes.csv`) | track-based exposure | downloaded by `43_download_redesign.py` |
| Census LEHD QWI | labour outcomes | bulk files without a key; demographic and firm-size cells through the Census API, which needs a free `CENSUS_API_KEY` in `tornado_mitigation/.env` |
| Census BDS, CBP, Building Permits Survey; BLS QCEW; IRS SOI county migration | business, employment, migration and building outcomes | downloaded by scripts 10 to 19; no key |
| Census county population estimates; OMB 2020 CBSA delineation; ACS 2009 5-year | controls | downloaded by `22b_download_auxiliary.py` and `43_download_redesign.py` |
| BEA county GDP and farm income; USDA NASS county crop yields | land productivity (redesign analysis) | downloaded by `43_download_redesign.py` |
| Census of Governments 2017: `Govt_Units_2017_Final.xlsx` and `2017FinEstDAT_09202024modp_pu.txt` | local-government counts and finances | **not downloaded by any script**; place in `tornado_mitigation/data/raw/auxiliary/cog2017/` and `.../govfin2017/` |

The scripts record each download in `tornado_mitigation/output/logs/data_sources.csv` (created when the pipeline runs; not in the repository).

## Software

- Python. `tornado_mitigation/README.md` says "Python 3.11+ (built with 3.13)", and `00_check_environment.py` stops on versions below 3.11. The manuscript build notes use Python 3.13.
- Packages: see `requirements.txt` at the repository root. Minimum versions are stated in `tornado_mitigation/requirements.txt`; exact versions used are not recorded.
- LaTeX with biber (MiKTeX or TeX Live) to compile the manuscript drafts.

## Folder map

```
tornado_mitigation/                data pipeline and analysis
  run_all.py                       entry point (calls src/run_all.py)
  config/config.yaml               analysis settings
  src/00-52_*.py                   numbered download, cleaning, build, estimation and report scripts
  src/est.py, src/utils.py         shared estimator and helper functions (paths, logging, API key)
  tests/                           pytest tests
  output/final/, output/tables/    Markdown and JSON summaries and tables from earlier runs
  output/logs/                     console logs from earlier runs
  data/                            a few small committed files (see Known limitations)
manuscript_draft_1/                manuscript draft 1 (LaTeX) and scripts to build tables and figures
manuscript_draft_2/                manuscript draft 2 (LaTeX), revised from draft 1
```

## How to run

`tornado_mitigation/run_all.py` is the entry script for scripts 00 to 42, grouped into stages:

```
cd tornado_mitigation
copy .env.example .env          # then add CENSUS_API_KEY=...
python -m pip install -r ../requirements.txt
python run_all.py --all         # or --download --clean --build --estimate --robustness --report
python -m pytest tests
```


1. `python run_all.py --download --clean --build` (FEMA, storm, outcome and crosswalk files, and the county-year panel).
2. In `tornado_mitigation/src/`: `43_download_redesign.py`, `44_spc_exposure.py`, `45_land_productivity.py` (script 50 uses `46_redesign_analysis.py::build_panel`, which reads the outputs of 23, 44 and 45).
3. `49_allocation_analysis.py`, `50_small_county_robustness.py`, `51_gap_mechanisms.py`, `52_gap_causal_tests.py` (51 and 52 need the Census of Governments files above).
4. `manuscript_draft_1/scripts/make_tables_figures.py` re-estimates the manuscript numbers from the saved panels and writes the tables and figures.
5. Compile a draft with `pdflatex`, `biber`, `pdflatex`, `pdflatex`.

Scripts 46 to 48 belong to a redesign analysis that, per `results_provenance.md`, is not used in the manuscript drafts.

The pipeline sets the random seed 20261007.

## Expected running time

Not recorded. The logs in `tornado_mitigation/output/logs/` show timestamps for individual steps but no total run time. `tornado_mitigation/README.md` notes the project was built on an 8 GB RAM machine.

## Known limitations

- No hard-coded absolute paths were found in the Python code; paths are set relative to the project in `src/utils.py`. Absolute local paths do appear in committed text files, for example:
  - `tornado_mitigation/output/logs/chain_build.txt`: tracebacks with `C:\Users\mahya\OneDrive - Simon Fraser University (1sfu)\Desktop\Tornedo\tornado_mitigation\src\...`
- Scripts 43 to 52 must be run by hand; `run_all.py` does not include them.
- The Census of Governments 2017 files are read from fixed file names that no script downloads.
- Some small data files are already tracked in git (`tornado_mitigation/data/raw/qwi/api_cells/*.json`, `tornado_mitigation/data/raw/bds/release.txt`, `tornado_mitigation/data/intermediate/public_finance_status.json`). The new `.gitignore` stops new data files from being added but does not remove files already tracked.
- `tornado_mitigation/.pytest_cache/` is tracked in git.
- Exact package versions and a full run log are not recorded, so earlier outputs cannot be matched to a specific environment.
- Downloads depend on live public endpoints. File names with release dates (for example the NOAA Storm Events files and the NASS bulk file) may change.
