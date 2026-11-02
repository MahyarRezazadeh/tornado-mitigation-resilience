"""Run the full pipeline in dependency order.

Usage (from project root or src/):
    python src/run_all.py --all
    python run_all.py --download --clean --build
    python run_all.py --estimate --robustness --report
Raw data are cached; re-running never re-downloads existing files.
"""
from __future__ import annotations

import argparse
import os
import random
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

SRC = Path(__file__).resolve().parent
STAGES = {
    "download": ["00_check_environment.py", "01_download_fema.py", "05_download_noaa_storms.py",
                 "22_build_county_crosswalk.py", "22b_download_auxiliary.py", "08_download_qwi.py",
                 "08b_download_qwi_api_cells.py", "10_download_bds.py", "12_download_qcew.py", "14_download_cbp.py",
                 "16_download_irs.py", "18_download_building_permits.py", "20_download_public_finance.py"],
    "clean": ["02_clean_fema.py", "03_classify_fema_projects.py", "04_construct_treatment.py", "06_clean_tornadoes.py",
              "07_construct_tornado_exposure.py", "07b_preliminary_feasibility.py", "09_clean_qwi.py", "11_clean_bds.py",
              "13_clean_qcew.py", "15_clean_cbp.py", "17_clean_irs.py", "19_clean_building_permits.py",
              "21_clean_public_finance.py"],
    "build": ["23_build_master_panels.py", "31_matching_weighting.py", "24_feasibility_analysis.py",
              "25_descriptive_analysis.py"],
    "estimate": ["26_primary_models.py", "27_event_studies.py", "28_stacked_event_studies.py", "29_mechanisms.py", "29b_damage_robustness.py",
                 "30_heterogeneity.py"],
    "robustness": ["32_robustness.py", "33_placebo_tests.py", "34_leave_one_out.py", "35_power_analysis.py",
                   "36_multiple_testing.py"],
    "report": ["37_literature_search.py", "37b_quasi_experiment.py", "37c_warning_system_feasibility.py",
               "38_publication_score.py", "39_journal_fit.py", "40_make_tables.py", "41_make_figures.py",
               "42_generate_report.py"],
}


def main() -> None:
    ap = argparse.ArgumentParser()
    for s in STAGES:
        ap.add_argument(f"--{s}", action="store_true")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    chosen = [s for s in STAGES if a.all or getattr(a, s)] or list(STAGES)
    random.seed(20261007)
    np.random.seed(20261007)
    env = {**os.environ, "PYTHONHASHSEED": "20261007"}
    for stage in chosen:
        for script in STAGES[stage]:
            t = time.time()
            print(f"[{stage}] {script} ...", flush=True)
            r = subprocess.run([sys.executable, str(SRC / script)], cwd=SRC, env=env)
            status = "ok" if r.returncode == 0 else f"FAILED ({r.returncode})"
            print(f"[{stage}] {script}: {status} in {time.time() - t:.0f}s", flush=True)
            if r.returncode != 0 and stage in ("build",):
                sys.exit(f"stopping: {script} failed in a stage later steps depend on")


if __name__ == "__main__":
    main()
