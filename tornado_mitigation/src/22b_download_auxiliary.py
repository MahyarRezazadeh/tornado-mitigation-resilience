"""Auxiliary county covariates: population estimates (1990-2024) and metro/non-metro status.

Population: Census intercensal/postcensal county totals (no key).
  1990s: co-99-10 (1990-1999 intercensal county totals)
  2000s: co-est00int-tot.csv ; 2010s: co-est2020-alldata.csv ; 2020s: co-est2024-alldata.csv
Metro status: OMB 2020 CBSA delineation (Census list1_2020.xls).
Outputs: data/processed/county_population.parquet, data/processed/county_metro.parquet
"""
from __future__ import annotations

import importlib

import pandas as pd

from utils import PROC, RAW, cached_get, get_logger, register_source

log = get_logger(__file__)
xw = importlib.import_module("22_build_county_crosswalk")
A = RAW / "auxiliary"
POP = {
    "2000s": "https://www2.census.gov/programs-surveys/popest/datasets/2000-2010/intercensal/county/co-est00int-tot.csv",
    "2010s": "https://www2.census.gov/programs-surveys/popest/datasets/2010-2020/counties/totals/co-est2020-alldata.csv",
    "2020s": "https://www2.census.gov/programs-surveys/popest/datasets/2020-2024/counties/totals/co-est2024-alldata.csv",
}
POP1990 = "https://www2.census.gov/programs-surveys/popest/tables/1990-2000/intercensal/st-co/stch-icen1990.txt"
DELIN = "https://www2.census.gov/programs-surveys/metro-micro/geographies/reference-files/2020/delineation-files/list1_2020.xls"


def wide_pop(path, years) -> pd.DataFrame:
    d = pd.read_csv(path, encoding="latin-1", dtype={"STATE": str, "COUNTY": str})
    d = d[d["COUNTY"].astype(int) != 0]
    d["county_fips"] = d["STATE"].str.zfill(2) + d["COUNTY"].str.zfill(3)
    cols = {f"POPESTIMATE{y}": y for y in years if f"POPESTIMATE{y}" in d}
    if "POPESTIMATE2000" not in d and "ESTIMATESBASE2000" in d and 2000 in years:
        cols["ESTIMATESBASE2000"] = 2000
    m = d.melt(id_vars="county_fips", value_vars=list(cols), var_name="v", value_name="population")
    m["year"] = m["v"].map(cols)
    return m[["county_fips", "year", "population"]]


def main() -> None:
    parts = []
    p = cached_get(POP["2000s"], A / "co-est00int-tot.csv", log)
    parts.append(wide_pop(p, range(2000, 2010)))
    p = cached_get(POP["2010s"], A / "co-est2020-alldata.csv", log)
    parts.append(wide_pop(p, range(2010, 2020)))
    p = cached_get(POP["2020s"], A / "co-est2024-alldata.csv", log)
    parts.append(wide_pop(p, range(2020, 2025)))
    try:
        p = cached_get(POP1990, A / "stch-icen1990.txt", log)
        d = pd.read_fwf(p, header=None, names=["year", "fips", "agegrp", "racesex", "hisp", "pop"],
                        widths=[2, 6, 3, 2, 2, 8], dtype={"fips": str})
        d["year"] = 1900 + d["year"].astype(int)
        d["county_fips"] = d["fips"].str.strip().str.zfill(5)
        parts.append(d.groupby(["county_fips", "year"], as_index=False)["pop"].sum().rename(columns={"pop": "population"}))
    except Exception as e:  # noqa: BLE001
        log.warning("1990 population unavailable: %s", e)
    pop = pd.concat(parts, ignore_index=True)
    pop["population"] = pd.to_numeric(pop["population"], errors="coerce")
    pop = pop[pop["county_fips"].str.fullmatch(r"\d{5}", na=False)]
    pop["county_fips"] = xw.harmonize(pop["county_fips"])
    pop = pop.groupby(["county_fips", "year"], as_index=False)["population"].sum()
    pop.to_parquet(PROC / "county_population.parquet", index=False)
    log.info("population rows %d, years %s-%s", len(pop), pop.year.min(), pop.year.max())

    dl = cached_get(DELIN, A / "list1_2020.xls", log)
    m = pd.read_excel(dl, skiprows=2, dtype=str)
    m = m.dropna(subset=["FIPS State Code"])
    m["county_fips"] = m["FIPS State Code"].str.zfill(2) + m["FIPS County Code"].str.zfill(3)
    m = m[["county_fips", "Metropolitan/Micropolitan Statistical Area", "CBSA Code", "Central/Outlying County"]]
    m.columns = ["county_fips", "cbsa_type", "cbsa_code", "central_outlying"]
    m["metro"] = (m["cbsa_type"] == "Metropolitan Statistical Area").astype(int)
    m.to_parquet(PROC / "county_metro.parquet", index=False)
    log.info("delineation rows %d (metro %d)", len(m), m.metro.sum())
    register_source(dataset="census_popest", source_name="Census county population estimates (intercensal/postcensal)",
                    official_URL="https://www.census.gov/programs-surveys/popest.html",
                    download_URL=";".join(list(POP.values()) + [POP1990]), coverage_start="1990", coverage_end="2024")
    register_source(dataset="omb_cbsa_2020", source_name="OMB 2020 CBSA delineation (Census list1_2020)",
                    official_URL="https://www.census.gov/geographies/reference-files/time-series/demo/metro-micro/delineation-files.html",
                    download_URL=DELIN, coverage_start="2020", coverage_end="2020", notes="metro = Metropolitan SA county")


if __name__ == "__main__":
    main()
