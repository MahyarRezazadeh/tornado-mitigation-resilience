"""Clean OpenFEMA HMA projects: types, dates, county FIPS, link subapplication text and payments.

Output: data/intermediate/fema_projects_clean.parquet
         output/diagnostics/fema_validation.csv
"""
from __future__ import annotations

import pandas as pd

from utils import DIAG, INTER, RAW, get_logger, log_frame

log = get_logger(__file__)
FUNDED = {"Closed", "Approved", "Obligated", "Awarded", "Completed"}
NOT_FUNDED = {"Not Approved / Denied", "Withdrawn", "Not Selected", "Void"}
DATE_COLS = ["dateInitiallyApproved", "initialObligationDate", "dateApproved", "dateClosed"]


def main() -> None:
    p = pd.read_parquet(RAW / "fema" / "fema_projects_raw.parquet")
    s = pd.read_parquet(RAW / "fema" / "fema_subapplications_raw.parquet")
    f = pd.read_parquet(RAW / "fema" / "fema_fin_transactions_raw.parquet")
    log_frame(log, p, "projects raw")
    checks = []

    for c in DATE_COLS:
        p[c] = pd.to_datetime(p[c], errors="coerce", utc=True).dt.tz_localize(None)
        bad = p[c].notna() & ((p[c].dt.year < 1985) | (p[c] > pd.Timestamp("2026-12-31")))
        checks.append((f"implausible {c}", int(bad.sum())))
        p.loc[bad, c] = pd.NaT

    p["state_fips"] = p["stateNumberCode"].astype("string").str.zfill(2)
    cc = p["countyCode"].astype("string").str.zfill(3)
    p["county_fips"] = (p["state_fips"] + cc).where(cc.notna() & (cc != "000"))
    p["statewide_flag"] = cc.eq("000") | cc.isna()
    checks.append(("statewide / missing county", int(p["statewide_flag"].sum())))
    checks.append(("duplicate projectIdentifier", int(p["projectIdentifier"].duplicated().sum())))

    p["funded"] = p["status"].isin(FUNDED)
    p["not_funded"] = p["status"].isin(NOT_FUNDED)

    # date consistency
    checks.append(("closed before initial approval",
                   int((p["dateClosed"] < p["dateInitiallyApproved"]).sum())))
    checks.append(("obligation before initial approval (>30d)",
                   int((p["initialObligationDate"] < p["dateInitiallyApproved"] - pd.Timedelta(days=30)).sum())))

    # financial transactions: first/last positive payment date per project (completion proxy)
    f["transactionDate"] = pd.to_datetime(f["transactionDate"], errors="coerce", utc=True).dt.tz_localize(None)
    pos = f[f["federalShareProjectCostAmt"] > 0]
    pay = pos.groupby("projectIdentifier").agg(first_payment_date=("transactionDate", "min"),
                                               last_payment_date=("transactionDate", "max"),
                                               paid_federal=("federalShareProjectCostAmt", "sum"))
    p = p.merge(pay, left_on="projectIdentifier", right_index=True, how="left")

    # subapplication text (title / activity / hazard) by identifier
    keep = ["subapplicationIdentifier", "subapplicationTitle", "primaryActivity", "primarySubactivity",
            "secondaryActivity", "primaryHazard", "secondaryHazard", "selectionStatus",
            "benefitCostRatio", "totalSubapplicationAmount", "subapplicantName", "subapplicantCity",
            "dateSubmittedToFema", "proposedProjectEndDate"]
    s2 = s[keep].drop_duplicates("subapplicationIdentifier").add_prefix("sub_")
    p = p.merge(s2, left_on="projectIdentifier", right_on="sub_subapplicationIdentifier", how="left")
    checks.append(("projects linked to subapplication", int(p["sub_subapplicationIdentifier"].notna().sum())))

    # treatment money
    p["total_cost"] = p["projectAmount"].where(p["projectAmount"] > 0)
    p["federal_share"] = p["federalShareObligated"].where(p["federalShareObligated"] > 0)
    p["federal_share"] = p["federal_share"].fillna(p["initialObligationAmount"].where(p["initialObligationAmount"] > 0))
    p["local_share"] = (p["total_cost"] - p["federal_share"]).clip(lower=0)

    p["approval_date"] = p["dateInitiallyApproved"].fillna(p["dateApproved"])
    p["obligation_date"] = p["initialObligationDate"]
    p["closeout_date"] = p["dateClosed"]
    p["completion_date"] = pd.NaT  # not published by OpenFEMA (see metadata); never imputed

    pd.DataFrame(checks, columns=["check", "count"]).to_csv(DIAG / "fema_validation.csv", index=False)
    for k, v in checks:
        log.info("validation: %s = %d", k, v)
    p.to_parquet(INTER / "fema_projects_clean.parquet", index=False)
    log_frame(log, p, "projects clean")


if __name__ == "__main__":
    main()
