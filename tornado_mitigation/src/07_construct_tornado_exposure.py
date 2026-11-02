"""County-quarter and county-year tornado exposure, path-based check, predetermined risk.

Exposure measures (from NOAA county segments): any_tornado, tornado_count, EF1_plus, EF2_plus,
EF3_plus, max_tornado_intensity, total_injuries, total_fatalities, reported_property_damage,
reported_crop_damage. Damage is an outcome/mechanism, never the exposure variable.

Path-based exposure: begin/end coordinates -> line, intersected with 2020 county polygons.
Historical risk: fixed 1950-1989 window (precedes all FEMA HMA treatment) -> never uses future storms.

Outputs:
  data/processed/tornado_exposure_cq.parquet, tornado_exposure_cy.parquet
  data/processed/historical_tornado_risk.parquet
  data/processed/other_hazards_cq.parquet, other_hazards_cy.parquet
  output/diagnostics/tornado_path_vs_zone.csv
"""
from __future__ import annotations

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import LineString, Point

from utils import DIAG, INTER, PROC, RAW, XWALK, get_logger, load_config

log = get_logger(__file__)


def aggregate(t: pd.DataFrame, keys: list[str], prefix: str = "") -> pd.DataFrame:
    g = t.assign(e1=t.ef >= 1, e2=t.ef >= 2, e3=t.ef >= 3, e0=t.ef == 0,
                 eu=t.ef_unknown).groupby(keys)
    a = g.agg(tornado_count=("EVENT_ID", "size"), EF0_count=("e0", "sum"), EF1_plus_count=("e1", "sum"),
              EF2_plus_count=("e2", "sum"), EF3_plus_count=("e3", "sum"), EFU_count=("eu", "sum"),
              max_tornado_intensity=("ef", "max"), total_injuries=("injuries", "sum"),
              total_fatalities=("fatalities", "sum"), reported_property_damage=("damage_property", "sum"),
              reported_crop_damage=("damage_crops", "sum"), n_episodes=("EPISODE_ID", "nunique")).reset_index()
    a["any_tornado"] = 1
    for k in ["EF1_plus", "EF2_plus", "EF3_plus"]:
        a[k] = (a[f"{k}_count"] > 0).astype(int)
    if prefix:
        a = a.rename(columns={c: prefix + c for c in a.columns if c not in keys})
    return a


def full_grid(counties, periods, name) -> pd.DataFrame:
    return pd.MultiIndex.from_product([counties, periods], names=["county_fips", name]).to_frame(index=False)


def fill_zero(df: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    cnt = [c for c in df.columns if c not in keys and c != "max_tornado_intensity"
           and not c.endswith("max_tornado_intensity")]
    df[cnt] = df[cnt].fillna(0)
    return df


def path_exposure(t: pd.DataFrame, cg: gpd.GeoDataFrame) -> pd.DataFrame:
    ok = t[["BEGIN_LAT", "BEGIN_LON", "END_LAT", "END_LON"]].notna().all(axis=1) & \
         (t["BEGIN_LAT"].between(20, 55)) & (t["BEGIN_LON"].between(-130, -60))
    s = t[ok].copy()
    geom = [LineString([(a, b), (c, d)]) if (a, b) != (c, d) else Point(a, b).buffer(1e-4)
            for a, b, c, d in zip(s.BEGIN_LON, s.BEGIN_LAT, s.END_LON, s.END_LAT)]
    gs = gpd.GeoDataFrame(s[["EVENT_ID", "county_fips", "yq", "year", "ef", "ef_unknown", "injuries",
                             "fatalities", "damage_property", "damage_crops", "EPISODE_ID"]],
                          geometry=geom, crs=4326).to_crs(5070)
    j = gpd.sjoin(gs, cg[["county_fips", "geometry"]].rename(columns={"county_fips": "path_fips"}),
                  predicate="intersects", how="left")
    # discrepancy diagnostics: does the path touch the NOAA-listed county?
    hit = j.groupby("EVENT_ID").apply(lambda d: (d["path_fips"] == d["county_fips"]).any(), include_groups=False)
    n_cty = j.groupby("EVENT_ID")["path_fips"].nunique()
    diag = pd.DataFrame({"path_touches_listed_county": hit, "n_path_counties": n_cty})
    diag = diag.join(s.set_index("EVENT_ID")[["year", "ef"]])
    summ = diag.groupby(pd.cut(diag.year, [1949, 1979, 1995, 2007, 2030])).agg(
        segments=("n_path_counties", "size"), share_touch_listed=("path_touches_listed_county", "mean"),
        share_multi_county=("n_path_counties", lambda x: (x > 1).mean()))
    summ.loc["all"] = [len(diag), diag.path_touches_listed_county.mean(), (diag.n_path_counties > 1).mean()]
    summ["coord_coverage_share"] = ok.mean()
    summ.to_csv(DIAG / "tornado_path_vs_zone.csv")
    log.info("path vs zone:\n%s", summ.to_string())
    pj = j.dropna(subset=["path_fips"]).drop(columns="county_fips").rename(columns={"path_fips": "county_fips"})
    pj = pj.drop_duplicates(["EVENT_ID", "county_fips"])
    return pd.DataFrame(pj.drop(columns="geometry"))


def main() -> None:
    cfg = load_config()["data"]
    t = pd.read_parquet(INTER / "tornadoes_clean.parquet")
    cty = pd.read_parquet(XWALK / "counties_2020.parquet")
    counties = sorted(cty["county_fips"])
    years = range(cfg["noaa_start_year"], cfg["noaa_end_year"] + 1)
    yqs = [y * 10 + q for y in years for q in range(1, 5)]

    cq = full_grid(counties, yqs, "yq").merge(aggregate(t, ["county_fips", "yq"]), how="left")
    cq = fill_zero(cq, ["county_fips", "yq"])
    cy = full_grid(counties, list(years), "year").merge(aggregate(t, ["county_fips", "year"]), how="left")
    cy = fill_zero(cy, ["county_fips", "year"])

    cg = gpd.read_file(XWALK / "counties_2020.gpkg")
    pj = path_exposure(t, cg)
    pq = aggregate(pj, ["county_fips", "yq"], "path_")[["county_fips", "yq", "path_any_tornado",
                                                        "path_EF1_plus", "path_EF2_plus", "path_tornado_count"]]
    cq = cq.merge(pq, how="left", on=["county_fips", "yq"])
    cq[[c for c in cq if c.startswith("path_")]] = cq[[c for c in cq if c.startswith("path_")]].fillna(0)
    agree = pd.crosstab(cq.loc[cq.yq >= 19960, "EF1_plus"], cq.loc[cq.yq >= 19960, "path_EF1_plus"])
    agree.to_csv(DIAG / "tornado_path_vs_zone_EF1_cq_crosstab.csv")
    log.info("EF1+ county-quarter agreement (zone rows x path cols, 1996+):\n%s", agree.to_string())

    cq["year"] = cq["yq"] // 10
    cq["quarter"] = cq["yq"] % 10
    cq.to_parquet(PROC / "tornado_exposure_cq.parquet", index=False)
    cy.to_parquet(PROC / "tornado_exposure_cy.parquet", index=False)

    lo, hi = cfg["historical_risk_window"]
    h = t[(t.year >= lo) & (t.year <= hi)]
    hr = pd.DataFrame({"county_fips": counties}).merge(
        h.groupby("county_fips").agg(hist_tornado_count=("EVENT_ID", "size"),
                                     hist_EF2_plus_count=("ef", lambda x: (x >= 2).sum()),
                                     hist_mean_intensity=("ef", "mean")).reset_index(), how="left")
    hr[["hist_tornado_count", "hist_EF2_plus_count"]] = hr[["hist_tornado_count", "hist_EF2_plus_count"]].fillna(0)
    hr = hr.merge(cty[["county_fips", "land_area_km2"]])
    hr["hist_tornado_density"] = hr["hist_tornado_count"] / hr["land_area_km2"] * 1000
    hr["hist_EF2_density"] = hr["hist_EF2_plus_count"] / hr["land_area_km2"] * 1000
    hr["ever_tornado_hist"] = (hr["hist_tornado_count"] > 0).astype(int)
    hr["above_median_risk"] = (hr["hist_tornado_density"] > hr["hist_tornado_density"].median()).astype(int)
    hr["top_tercile_risk"] = (hr["hist_tornado_density"] > hr["hist_tornado_density"].quantile(2 / 3)).astype(int)
    hr["risk_tercile"] = pd.qcut(hr["hist_tornado_density"].rank(method="first"), 3, labels=[1, 2, 3]).astype(int)
    hr.to_parquet(PROC / "historical_tornado_risk.parquet", index=False)
    log.info("historical risk window %s-%s: %d counties with >=1 tornado", lo, hi, hr.ever_tornado_hist.sum())

    o = pd.read_parquet(RAW / "noaa" / "storm_events_other_hazards_county.parquet")
    o["county_fips"] = (o["STATE_FIPS"].astype(str).str.zfill(2) + o["CZ_FIPS"].astype(str).str.zfill(3))
    o["year"] = o["YEAR"].astype(int)
    o["yq"] = o["year"] * 10 + ((o["BEGIN_YEARMONTH"].astype(int) % 100 - 1) // 3 + 1)
    for keys, name in [(["county_fips", "yq"], "cq"), (["county_fips", "year"], "cy")]:
        w = o.pivot_table(index=keys, columns="control_type", values="EVENT_ID", aggfunc="count", fill_value=0)
        w.columns = [f"{c}_events" for c in w.columns]
        w.reset_index().to_parquet(PROC / f"other_hazards_{name}.parquet", index=False)
    log.info("cq rows %d, cy rows %d", len(cq), len(cy))
    _ = np


if __name__ == "__main__":
    main()
