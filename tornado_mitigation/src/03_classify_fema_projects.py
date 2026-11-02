"""Classify FEMA HMA projects into strict / moderate / broad tornado-wind mitigation.

Evidence: projectType codes + subapplication title/activity + linked hazard
(subapplication primaryHazard, else the disaster declaration incident type).
Rules live in config/treatment_keywords.csv (transparent regex dictionary).

Outputs:
  data/intermediate/fema_projects_classified.parquet
  output/diagnostics/fema_classification_sample.xlsx  (>=500 random + all ambiguous)
  output/diagnostics/fema_ambiguous_projects.csv
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd

from utils import CONFIG, DIAG, INTER, RAW, SEED, cached_get, get_logger, register_source

log = get_logger(__file__)
WIND_HAZ = re.compile(r"tornado|wind|severe storm|hurricane|tropical|coastal storm|typhoon", re.I)
FACILITY = [
    ("school", r"school|\bisd\b|\busd\b|college|universit|academy|elementary|high school|campus"),
    ("hospital", r"hospital|medical|clinic|health"),
    ("eoc", r"emergency operation|\beoc\b|911|dispatch"),
    ("fire_police", r"fire|police|sheriff|public safety"),
    ("municipal", r"city hall|town hall|courthouse|municipal|county (building|office)|administration"),
    ("community_shelter", r"community|park|shelter|neighborhood|mobile home|manufactured"),
]


def disaster_incident_types() -> pd.Series:
    url = "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries.csv"
    dest = RAW / "fema" / "DisasterDeclarationsSummaries.csv"
    cached_get(url, dest, log, timeout=600)
    register_source(dataset="fema_disaster_declarations", source_name="OpenFEMA DisasterDeclarationsSummaries v2",
                    official_URL="https://www.fema.gov/openfema-data-page/disaster-declarations-summaries-v2",
                    download_URL=url, API_endpoint=url, coverage_start="1953", coverage_end="present",
                    notes="Used for incidentType of disaster linked to HMGP projects")
    d = pd.read_csv(dest, usecols=["disasterNumber", "incidentType", "incidentBeginDate", "state"])
    return d.drop_duplicates("disasterNumber").set_index("disasterNumber")


def main() -> None:
    p = pd.read_parquet(INTER / "fema_projects_clean.parquet")
    kw = pd.read_csv(CONFIG / "treatment_keywords.csv")
    dis = disaster_incident_types()
    p = p.merge(dis[["incidentType", "incidentBeginDate"]].rename(columns=lambda c: "dis_" + c),
                left_on="disasterNumber", right_index=True, how="left")
    p["hazard"] = p["sub_primaryHazard"].fillna(p["dis_incidentType"]).fillna("")
    p["wind_hazard"] = p["hazard"].str.contains(WIND_HAZ)

    p["type_text"] = p["projectType"].fillna("").str.lower()
    p["free_text"] = (p["sub_subapplicationTitle"].fillna("") + " | " + p["sub_primaryActivity"].fillna("")
                      + " | " + p["sub_primarySubactivity"].fillna("")).str.lower()
    p["all_text"] = p["type_text"] + " || " + p["free_text"]

    hits = {}
    for _, r in kw.iterrows():
        hits[r["category"]] = p["all_text"].str.contains(r["keyword"], flags=re.I, regex=True)
    H = pd.DataFrame(hits)

    code_strict = H["safe_room_code"] | H["wind_retrofit_code"]
    text_strict = (H["safe_room_text"] | H["wind_retrofit_text"]) & ~code_strict
    mod_cond = (H["shelter_activity"] | H["generic_shelter"] | H["wind_component_text"]
                | H["mitigation_reconstruction"]) & p["wind_hazard"]
    broad_cond = (H["other_structural"] | H["utility_hardening"] | H["vegetation_wind"]
                  | H["generic_retrofit"]) & p["wind_hazard"]
    excl_cats = kw.loc[kw["exclusion"] == 1, "category"].tolist()
    any_excl = H[excl_cats].any(axis=1)

    p["treat_strict"] = (code_strict | text_strict).astype(int)
    p["treat_moderate"] = (p["treat_strict"].astype(bool) | mod_cond).astype(int)
    p["treat_broad"] = (p["treat_moderate"].astype(bool) | broad_cond).astype(int)

    p["mitigation_type"] = np.select(
        [H["safe_room_code"] | H["safe_room_text"], H["wind_retrofit_code"] | H["wind_retrofit_text"],
         mod_cond, broad_cond],
        ["safe_room", "wind_retrofit", "moderate_other", "broad_other"], "none")
    p["private_structure"] = p["type_text"].str.contains(r"private structures")

    p["classification_confidence"] = np.select(
        [code_strict, text_strict | (mod_cond & p["sub_primaryHazard"].fillna("").str.contains("ornado")),
         p["treat_broad"].astype(bool)], ["HIGH", "MEDIUM", "LOW"], "HIGH")  # non-treated by clear code = HIGH
    p.loc[(p["treat_broad"] == 0) & ~any_excl, "classification_confidence"] = "LOW"  # unclassifiable

    reasons = []
    for i, row in H.iterrows():
        cats = [c for c, v in row.items() if v]
        reasons.append(";".join(cats) if cats else "no_rule_matched")
    p["classification_reason"] = reasons
    p["ambiguous_flag"] = ((p["treat_broad"].astype(bool) & any_excl)       # mixed with excluded activities
                           | text_strict | (p["treat_moderate"].astype(bool) & ~code_strict)
                           | ((p["treat_broad"] == 0) & ~any_excl)).astype(int)

    # critical facility type (mechanism 5), only meaningful for treated projects
    ftxt = (p["sub_subapplicationTitle"].fillna("") + " " + p["subrecipient"].fillna("")).str.lower()
    p["facility_type"] = "unknown"
    for name, rx in reversed(FACILITY):
        p.loc[ftxt.str.contains(rx, regex=True), "facility_type"] = name
    p.loc[p["private_structure"], "facility_type"] = "residential_private"

    p = p.drop(columns=["type_text", "free_text", "all_text"])
    p.to_parquet(INTER / "fema_projects_classified.parquet", index=False)

    # diagnostics
    for d in ["strict", "moderate", "broad"]:
        t = p[(p[f"treat_{d}"] == 1)]
        log.info("%s: %d projects (%d funded), %d funded with county FIPS", d, len(t), t["funded"].sum(),
                 (t["funded"] & t["county_fips"].notna()).sum())
    log.info("confidence: %s", p.loc[p.treat_broad == 1, "classification_confidence"].value_counts().to_dict())

    cols = ["projectIdentifier", "programArea", "state", "county", "county_fips", "status", "projectType",
            "sub_subapplicationTitle", "sub_primaryActivity", "hazard", "treat_strict", "treat_moderate",
            "treat_broad", "mitigation_type", "facility_type", "classification_confidence",
            "classification_reason", "ambiguous_flag"]
    rng = np.random.default_rng(SEED)
    treated = p[p.treat_broad == 1]
    samp = pd.concat([treated.sample(min(350, len(treated)), random_state=SEED),
                      p[p.treat_broad == 0].sample(250, random_state=SEED)])
    amb = p[p["ambiguous_flag"] == 1]
    with pd.ExcelWriter(DIAG / "fema_classification_sample.xlsx", engine="xlsxwriter") as xw:
        samp[cols].assign(manual_check="").to_excel(xw, sheet_name="random_sample_600", index=False)
        amb[cols].to_excel(xw, sheet_name="ambiguous_all", index=False)
        p.groupby(["mitigation_type", "classification_confidence"]).size().rename("n").reset_index() \
            .to_excel(xw, sheet_name="summary", index=False)
    amb[cols].to_csv(DIAG / "fema_ambiguous_projects.csv", index=False)
    log.info("sample %d, ambiguous %d saved", len(samp), len(amb))
    _ = rng


if __name__ == "__main__":
    main()
