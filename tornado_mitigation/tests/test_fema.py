import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from utils import INTER, PROC  # noqa: E402


def test_classification_nesting():
    p = pd.read_parquet(INTER / "fema_projects_classified.parquet")
    assert (p.treat_strict <= p.treat_moderate).all()
    assert (p.treat_moderate <= p.treat_broad).all()


def test_strict_codes_are_wind():
    p = pd.read_parquet(INTER / "fema_projects_classified.parquet")
    s = p[p.treat_strict == 1].projectType.fillna("")
    assert s.str.contains(r"206\.|205\.[78]|safe ?room|wind", case=False, regex=True).mean() > 0.95


def test_excluded_types_not_strict():
    p = pd.read_parquet(INTER / "fema_projects_classified.parquet")
    only_plan = p.projectType.fillna("").str.fullmatch(r"9[0-7]\.\d+:.*Plan.*")
    assert p.loc[only_plan, "treat_strict"].sum() == 0


def test_no_duplicate_ids_in_treatment():
    p = pd.read_parquet(INTER / "fema_treatment_projects.parquet")
    assert not p.id.duplicated().any()


def test_primary_timing_never_completion_assumed_from_approval():
    p = pd.read_parquet(INTER / "fema_treatment_projects.parquet")
    assert p.completion_date.isna().all()          # OpenFEMA has no completion date
    assert set(p.t_primary_source.unique()) <= {"obligation+2", "approval+2", "closeout_fallback", "missing"}


def test_county_treatment_first_date_minimum():
    ct = pd.read_parquet(PROC / "county_treatment.parquet")
    assert not ct.duplicated(["county_fips", "definition", "timing"]).any()
