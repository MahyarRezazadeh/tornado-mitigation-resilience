"""Warning-system alternative (Section 66) and Outcome 15 feasibility.

Measures what is observable in public data: FEMA HMA warning-system projects (type 600.1) as a dated,
county-level treatment, and NOAA tornado casualties as a high-frequency outcome. Other candidate treatment
and outcome sources are assessed from documentation (no national dated adoption panel located).
Output: output/final/warning_system_feasibility.md
"""
from __future__ import annotations

import pandas as pd

from utils import FINAL, INTER, get_logger

log = get_logger(__file__)


def main() -> None:
    p = pd.read_parquet(INTER / "fema_projects_classified.parquet")
    w = p[p.projectType.fillna("").str.contains(r"600\.1|Warning System", regex=True) & p.funded]
    nw, nc = len(w), w.county_fips.nunique()
    yrs = pd.to_datetime(w.initialObligationDate, errors="coerce").dt.year
    md = f"""# Warning-System Alternative: Feasibility Appendix (Section 66)

The primary project studies physical retrofits/safe rooms (A). This appendix assesses whether local
tornado WARNING systems (B) can be studied with public, nationally scalable data. Retrofit and warning
treatments are NOT combined anywhere in the analysis.

## Candidate treatment measures

| Treatment | National? | Dated adoption at county level? | Public? | Assessment |
|---|---|---|---|---|
| FEMA HMA warning-system projects (type 600.1, sirens/alert systems) | Yes | Yes (obligation date) | Yes (OpenFEMA) | **Feasible**: {nw:,} funded projects in {nc:,} counties, obligation years {int(yrs.min()) if nw else 'n/a'}-{int(yrs.max()) if nw else 'n/a'}; captures only FEMA-funded upgrades (most sirens are locally funded) |
| Outdoor siren adoption (all sources) | No | No | No national registry | Infeasible |
| Wireless Emergency Alerts (WEA, 2012) | Yes | No - national rollout, carrier/handset driven | Partial | National timing only; no county variation |
| NWS warning technology (NEXRAD 1992-97 rollout, storm-based polygons 2007) | Yes | Yes for NEXRAD radar coverage (Simmons & Sutter 2005 used this) | Yes | Feasible for a casualty paper; already studied (low novelty) |
| NOAA Weather Radio transmitter coverage | Yes | Transmitter install dates not in an open panel | Partial | Low feasibility |
| StormReady certification (NWS) | Yes | Recognition dates published on NWS site (scrape needed); voluntary, selected | Partial | Moderate feasibility, strong selection |
| Local emergency alert system upgrades | No | No | No | Infeasible |

## Candidate outcomes

| Outcome | Frequency | National public data | Assessment |
|---|---|---|---|
| Tornado fatalities / injuries | Event | NOAA Storm Events (used here) | **Feasible** (classic outcome; see Simmons & Sutter) |
| Electricity load | Hourly | EIA-930 balancing-authority level only | Not county-level -> infeasible for local warnings |
| Traffic counts | Hourly | FHWA TMAS stations (sparse, state-dependent) | Low feasibility |
| Airport operations | Daily | FAA OPSNET (airport-level) | Few counties; low feasibility |
| Mobility / foot traffic | Daily | SafeGraph/Advan (proprietary, 2018+) | Not public -> infeasible |
| Business openings | Daily | none public | Infeasible |
| School closures | Daily | none national | Infeasible |
| Emergency calls (911) | Event | none national | Infeasible |

## Outcome 15 (warning-induced shutdown costs) verdict

**INFEASIBLE with public, nationally scalable data.** QWI/QCEW are quarterly and cannot isolate hours-long
warning-induced shutdowns; no public county x day/hour economic-activity panel spans the FEMA era. No regression
was forced. A warning-system paper is feasible only for life-safety outcomes (fatalities/injuries) using NEXRAD
or FEMA 600.1 timing, which is a different and less novel question.
"""
    (FINAL / "warning_system_feasibility.md").write_text(md, encoding="utf-8")
    log.info("warning-system appendix written (%d FEMA warning projects)", nw)


if __name__ == "__main__":
    main()
