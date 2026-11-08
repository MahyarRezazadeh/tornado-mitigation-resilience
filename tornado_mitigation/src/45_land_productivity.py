"""REDESIGN: land productivity per hectare, county-year.

  gdp_per_ha        BEA CAGDP9 real GDP, all industries (chained 2017 $) / county land hectares   2001-2024
  ag_gdp_per_ha     BEA CAGDP9 agriculture/forestry/fishing real GDP / land hectares               2001-2024
  crop_rcpt_per_ha  BEA CAINC45 cash receipts from crops (nominal $; state-year FE absorbs prices) / land ha   1969-2022
  crop_t_per_ha     NASS survey: (corn grain + soybeans + wheat) production in tonnes / harvested ha 1990-2024
  corn_t_per_ha, soy_t_per_ha   NASS survey yields converted to tonnes per hectare
Logs are taken where the level is > 0. BEA suppressed cells ("(D)", "(NA)") -> missing.

Output: data/processed/land_productivity_cy.parquet
"""
from __future__ import annotations

import zipfile

import numpy as np
import pandas as pd

from utils import DIAG, PROC, RAW, XWALK, get_logger

log = get_logger(__file__)
BU_T = {"CORN": 0.0254012, "SOYBEANS": 0.0272155, "WHEAT": 0.0272155}   # tonnes per bushel
AC_HA = 0.404686


def bea(table: str, lines: dict) -> pd.DataFrame:
    z = zipfile.ZipFile(RAW / "bea" / f"{table}.zip")
    n = [x for x in z.namelist() if "ALL_AREAS" in x][0]
    d = pd.read_csv(z.open(n), encoding="latin-1", dtype=str)
    d = d[d.LineCode.str.strip().isin(lines)]
    d["county_fips"] = d.GeoFIPS.str.replace('"', "").str.strip()
    d = d[~d.county_fips.str.endswith("000")]
    yrs = [c for c in d.columns if c.isdigit()]
    m = d.melt(id_vars=["county_fips", "LineCode"], value_vars=yrs, var_name="year", value_name="v")
    m["v"] = pd.to_numeric(m.v.str.strip(), errors="coerce") * 1000
    m["year"] = m.year.astype(int)
    m["var"] = m.LineCode.str.strip().map(lines)
    return m.pivot_table(index=["county_fips", "year"], columns="var", values="v").reset_index()


def nass() -> pd.DataFrame:
    f = RAW / "nass" / "nass_county_yields.parquet"
    if not f.exists():
        log.warning("NASS file missing; crop yields skipped")
        return pd.DataFrame(columns=["county_fips", "year"])
    d = pd.read_parquet(f)
    d = d[d.COUNTY_CODE.str.isdigit() & (d.COUNTY_CODE != "998")]
    d["county_fips"] = d.STATE_FIPS_CODE.str.zfill(2) + d.COUNTY_CODE.str.zfill(3)
    d["year"] = d.YEAR.astype(int)
    d["v"] = pd.to_numeric(d.VALUE.str.replace(",", ""), errors="coerce")
    want = {("CORN", "CORN, GRAIN - PRODUCTION, MEASURED IN BU"): "prod",
            ("CORN", "CORN, GRAIN - ACRES HARVESTED"): "acres",
            ("CORN", "CORN, GRAIN - YIELD, MEASURED IN BU / ACRE"): "yield",
            ("SOYBEANS", "SOYBEANS - PRODUCTION, MEASURED IN BU"): "prod",
            ("SOYBEANS", "SOYBEANS - ACRES HARVESTED"): "acres",
            ("SOYBEANS", "SOYBEANS - YIELD, MEASURED IN BU / ACRE"): "yield",
            ("WHEAT", "WHEAT - PRODUCTION, MEASURED IN BU"): "prod",
            ("WHEAT", "WHEAT - ACRES HARVESTED"): "acres",
            ("WHEAT", "WHEAT - YIELD, MEASURED IN BU / ACRE"): "yield"}
    d["stat"] = [want.get((c, s)) for c, s in zip(d.COMMODITY_DESC, d.SHORT_DESC)]
    d = d[d.stat.notna() & d.v.notna()]
    w = d.pivot_table(index=["county_fips", "year", "COMMODITY_DESC"], columns="stat", values="v", aggfunc="sum").reset_index()
    w["tonnes"] = w["prod"] * w.COMMODITY_DESC.map(BU_T)
    w["ha"] = w["acres"] * AC_HA
    w["t_per_ha"] = w["yield"] * w.COMMODITY_DESC.map(BU_T) / AC_HA
    comp = w.dropna(subset=["tonnes", "ha"]).groupby(["county_fips", "year"])[["tonnes", "ha"]].sum()
    comp["crop_t_per_ha"] = comp.tonnes / comp.ha
    comp = comp.rename(columns={"ha": "crop_harvested_ha"})[["crop_t_per_ha", "crop_harvested_ha"]]
    y = w.pivot_table(index=["county_fips", "year"], columns="COMMODITY_DESC", values="t_per_ha")
    y = y.rename(columns={"CORN": "corn_t_per_ha", "SOYBEANS": "soy_t_per_ha", "WHEAT": "wheat_t_per_ha"})
    return comp.join(y, how="outer").reset_index()


def main() -> None:
    land = pd.read_parquet(XWALK / "counties_2020.parquet")[["county_fips", "land_area_km2"]]
    g = bea("CAGDP9", {"1": "real_gdp", "3": "real_gdp_ag"})
    c = bea("CAINC45", {"60": "crop_receipts", "10": "farm_receipts"})
    n = nass()
    d = g.merge(c, how="outer", on=["county_fips", "year"]).merge(n, how="outer", on=["county_fips", "year"])
    d = d.merge(land, how="inner", on="county_fips")
    ha = d.land_area_km2 * 100
    d["gdp_per_ha"] = d.real_gdp / ha
    d["ag_gdp_per_ha"] = d.real_gdp_ag / ha
    d["crop_rcpt_per_ha"] = d.crop_receipts / ha
    for v in ["gdp_per_ha", "ag_gdp_per_ha", "crop_rcpt_per_ha", "crop_t_per_ha", "corn_t_per_ha", "soy_t_per_ha"]:
        if v not in d:
            d[v] = np.nan
        d["log_" + v] = np.log(d[v].where(d[v] > 0))
    d = d.drop(columns="land_area_km2")
    d.to_parquet(PROC / "land_productivity_cy.parquet", index=False)
    cov = d.groupby(d.year // 5 * 5)[["log_gdp_per_ha", "log_ag_gdp_per_ha", "log_crop_rcpt_per_ha",
                                      "log_crop_t_per_ha", "log_corn_t_per_ha"]].count()
    cov.to_csv(DIAG / "land_productivity_coverage.csv")
    log.info("non-missing county-years by 5-yr bin:\n%s", cov.to_string())
    log.info("levels (median): %s", d[["gdp_per_ha", "ag_gdp_per_ha", "crop_rcpt_per_ha", "crop_t_per_ha",
                                       "corn_t_per_ha"]].median().round(2).to_dict())


if __name__ == "__main__":
    main()
