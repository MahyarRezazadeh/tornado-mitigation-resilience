"""Public finance outcome status (Outcome 13). No county panel is manufactured.

Writes data/intermediate/public_finance_status.json used by the feasibility analysis.
"""
from __future__ import annotations

import json

import pandas as pd

from utils import INTER, RAW, get_logger

log = get_logger(__file__)


def main() -> None:
    p = RAW / "public_finance" / "govfin_index_probe.csv"
    full = pd.read_csv(p).query("census_of_governments_year").year.tolist() if p.exists() else []
    status = {"outcome": "local_fiscal_resilience", "feasibility": "LOW",
              "reason": ("Annual Survey of Local Government Finances is a sample in non-census years; only "
                         f"Census-of-Governments years {full} cover all units. County-area aggregation across "
                         "years is not consistent; an annual county panel would be manufactured. Quinquennial "
                         "data give at most 6 waves, too coarse to time tornado shocks relative to mitigation."),
              "full_census_years": full, "estimated": False}
    (INTER / "public_finance_status.json").write_text(json.dumps(status, indent=2))
    log.info("public finance marked LOW feasibility; not estimated")


if __name__ == "__main__":
    main()
