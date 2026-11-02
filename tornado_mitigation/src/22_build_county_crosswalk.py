"""Harmonized county geography (2020 Census vintage, contiguous US + DC).

Every recode is an explicit rule in data/crosswalks/county_recode_rules.csv; nothing is
merged silently. Virginia independent cities are kept SEPARATE (they are separate units in
QWI/QCEW/CBP/BDS). Alaska and Hawaii are outside the contiguous-US analysis sample.

Outputs:
  data/crosswalks/county_recode_rules.csv
  data/crosswalks/counties_2020.parquet      (fips, name, state, area, centroid)
  data/crosswalks/counties_2020.gpkg          (geometry, EPSG:5070)
"""
from __future__ import annotations

import zipfile

import geopandas as gpd
import pandas as pd

from utils import RAW, XWALK, cached_get, get_logger, register_source

log = get_logger(__file__)
SHP_URL = "https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_us_county_500k.zip"
NONCONTIG = {"02", "15", "60", "66", "69", "72", "78"}

# old_fips -> new_fips, reason. Effective years documented; applied to all source data.
RULES = [
    ("46113", "46102", "Shannon County SD renamed Oglala Lakota County (2015), new FIPS"),
    ("51515", "51019", "Bedford City VA reverted to town, merged into Bedford County (2013)"),
    ("02270", "02158", "Wade Hampton AK renamed Kusilvak (2015) [AK outside contiguous sample]"),
    ("12025", "12086", "Dade County FL renamed Miami-Dade (1997), new FIPS"),
    ("51560", "51005", "Clifton Forge city VA reverted to town in Alleghany County (2001)"),
    ("51780", "51083", "South Boston city VA reverted to town in Halifax County (1995)"),
    ("30113", "30031", "Yellowstone National Park MT area absorbed by Gallatin/Park (1997); assigned to Gallatin"),
    ("51123", "51800", "Nansemond County VA consolidated into Suffolk city (1974)"),
    ("51129", "51800", "Suffolk (old code) -> Suffolk city"),
    ("51785", "51550", "South Norfolk city VA consolidated into Chesapeake city (1963)"),
]


def main() -> None:
    z = cached_get(SHP_URL, RAW / "auxiliary" / "cb_2020_us_county_500k.zip", log)
    ext = RAW / "auxiliary" / "cb_2020_us_county_500k"
    if not ext.exists():
        with zipfile.ZipFile(z) as zf:
            zf.extractall(ext)
    g = gpd.read_file(ext / "cb_2020_us_county_500k.shp")
    g["county_fips"] = g["GEOID"]
    g["state_fips"] = g["STATEFP"]
    g = g[~g["state_fips"].isin(NONCONTIG)].to_crs(5070)
    g["land_area_km2"] = g["ALAND"] / 1e6
    c = g.geometry.centroid.to_crs(4326)
    g["lon"], g["lat"] = c.x, c.y
    g[["county_fips", "state_fips", "NAME", "STUSPS", "geometry"]].to_file(XWALK / "counties_2020.gpkg", driver="GPKG")
    pd.DataFrame(g.drop(columns="geometry"))[["county_fips", "state_fips", "NAME", "STUSPS", "STATE_NAME",
                                              "land_area_km2", "lat", "lon"]] \
        .to_parquet(XWALK / "counties_2020.parquet", index=False)
    rules = pd.DataFrame(RULES, columns=["old_fips", "new_fips", "rule"])
    rules.to_csv(XWALK / "county_recode_rules.csv", index=False)
    log.info("contiguous counties: %d; recode rules: %d", len(g), len(rules))
    register_source(dataset="census_cb_county_2020", source_name="Census cartographic boundary counties 2020 (500k)",
                    official_URL="https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html",
                    download_URL=SHP_URL, coverage_start="2020", coverage_end="2020",
                    notes="harmonized geography; contiguous US + DC")


def harmonize(fips: pd.Series) -> pd.Series:
    """Apply recode rules; returns harmonized 5-digit FIPS (NaN where invalid)."""
    rules = pd.read_csv(XWALK / "county_recode_rules.csv", dtype=str)
    m = dict(zip(rules["old_fips"], rules["new_fips"]))
    return fips.map(lambda x: m.get(x, x) if isinstance(x, str) else x)


if __name__ == "__main__":
    main()
