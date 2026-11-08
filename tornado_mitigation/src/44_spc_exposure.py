"""REDESIGN: damage-independent tornado exposure from SPC tracks.

Each SPC tornado (one row = whole track) -> straight line start->end, buffered by half the reported
path width = swept damage-path polygon. Intersected with 2020 county polygons:
  swept_km2         path area falling inside the county
  swept_share       swept_km2 / county land area (x1000 = per-mille of county swept)
  track_km          centerline length inside the county
  pop_exposed       2020 population of block groups whose population centroid lies inside the swept
                    polygon widened by 500 m (people/structures in the path, not reported damage)
  spc_hit           any track enters the county
  spc_pop_hit       pop_exposed > 0 (a track crosses a populated place)
EF magnitude, injuries, fatalities and SPC loss are carried ONLY as mechanism/outcome variables.
Caveat: path length/width are themselves taken from damage surveys, but they measure geometry, not $ loss
or EF rating; this is the best publicly available pre-2008 measure (radar rotation tracks start ~2008).

Outputs: data/processed/spc_exposure_cy.parquet (calendar year and March-aligned Apr(t-1)-Mar(t) versions)
         data/processed/spc_tracks.parquet (event-level, for diagnostics)
"""
from __future__ import annotations

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import LineString, Point

from utils import DIAG, PROC, RAW, XWALK, get_logger, cached_get

log = get_logger(__file__)
BG_URL = "https://www2.census.gov/geo/docs/reference/cenpop2020/blkgrp/CenPop2020_Mean_BG.txt"
Y0, Y1 = 1990, 2024


def tracks() -> gpd.GeoDataFrame:
    s = pd.read_csv(RAW / "spc" / "1950-2024_actual_tornadoes.csv")
    s = s[(s.yr >= 1980) & (s.yr <= Y1) & (s.slat > 20) & (s.slon < -60)].copy()
    s["has_end"] = (s.elat > 20) & (s.elon < -60)
    s["len_m"] = s["len"] * 1609.34
    s["wid_m"] = s["wid"].clip(lower=10) * 0.9144          # yards -> m; 10-yd floor for zero widths
    pts = gpd.GeoSeries([Point(x, y) for x, y in zip(s.slon, s.slat)], crs=4326).to_crs(5070)
    ends = gpd.GeoSeries([Point(x, y) if h else None for x, y, h in zip(s.elon, s.elat, s.has_end)],
                         crs=4326).to_crs(5070)
    geom = []
    for p, e, h, L, W in zip(pts, ends, s.has_end, s.len_m, s.wid_m):
        if h and p.distance(e) > 1:
            geom.append(LineString([p, e]).buffer(W / 2, cap_style="flat"))
        else:                                   # no end point: disc with the reported swept area
            geom.append(p.buffer(max(np.sqrt(max(L, W) * W / np.pi), W / 2)))
    g = gpd.GeoDataFrame(s[["om", "yr", "mo", "dy", "st", "mag", "inj", "fat", "loss", "len", "wid", "has_end"]]
                         .reset_index(drop=True), geometry=geom, crs=5070)
    g["line"] = [LineString([p, e]) if (h and p.distance(e) > 1) else None for p, e, h in zip(pts, ends, s.has_end)]
    g["tid"] = np.arange(len(g))
    g["yq"] = g.yr * 10 + (g.mo - 1) // 3 + 1
    g["mar_year"] = np.where(g.mo >= 4, g.yr + 1, g.yr)    # Apr(t-1)-Mar(t) window -> year t (BDS March reference)
    return g


def main() -> None:
    g = tracks()
    log.info("SPC tracks %d-%d: %d (%.1f%% with end point)", g.yr.min(), g.yr.max(), len(g), 100 * g.has_end.mean())
    cg = gpd.read_file(XWALK / "counties_2020.gpkg").to_crs(5070)[["county_fips", "geometry"]]
    land = pd.read_parquet(XWALK / "counties_2020.parquet")[["county_fips", "land_area_km2"]]

    ov = gpd.overlay(g[["tid", "geometry"]], cg, how="intersection", keep_geom_type=True)
    ov["swept_km2"] = ov.area / 1e6
    ov = ov.drop(columns="geometry")
    ln = g[g.line.notna()][["tid", "line"]].set_geometry("line", crs=5070).rename_geometry("geometry")
    lo = gpd.overlay(ln, cg, how="intersection", keep_geom_type=True)
    lo["track_km"] = lo.length / 1e3
    ov = ov.merge(pd.DataFrame(lo.drop(columns="geometry")), how="left", on=["tid", "county_fips"])
    ov["track_km"] = ov["track_km"].fillna(0)

    # population in the path: block-group population centroids within swept polygon + 500 m
    bg_f = cached_get(BG_URL, RAW / "auxiliary" / "CenPop2020_Mean_BG.txt", log)
    bg = pd.read_csv(bg_f, encoding="utf-8-sig", dtype={"STATEFP": str, "COUNTYFP": str})
    bg["county_fips"] = bg.STATEFP.str.zfill(2) + bg.COUNTYFP.str.zfill(3)
    bgg = gpd.GeoDataFrame(bg[["county_fips", "POPULATION"]],
                           geometry=gpd.points_from_xy(bg.LONGITUDE, bg.LATITUDE), crs=4326).to_crs(5070)
    wide = g[["tid", "geometry"]].copy()
    wide["geometry"] = wide.buffer(500)
    pj = gpd.sjoin(bgg, wide, predicate="within")
    pe = pj.groupby(["tid", "county_fips"]).POPULATION.sum().rename("pop_exposed").reset_index()
    ov = ov.merge(pe, how="left", on=["tid", "county_fips"])
    ov["pop_exposed"] = ov["pop_exposed"].fillna(0)

    ev = ov.merge(pd.DataFrame(g.drop(columns=["geometry", "line"])), on="tid")
    ev.to_parquet(PROC / "spc_tracks.parquet", index=False)

    counties = sorted(cg.county_fips)
    out = []
    for tcol, pre in [("yr", ""), ("mar_year", "mar_")]:
        a = ev.groupby(["county_fips", tcol]).agg(
            swept_km2=("swept_km2", "sum"), track_km=("track_km", "sum"), pop_exposed=("pop_exposed", "sum"),
            n_tracks=("tid", "nunique"), spc_max_mag=("mag", "max"), spc_inj=("inj", "sum"),
            spc_fat=("fat", "sum")).reset_index().rename(columns={tcol: "year"})
        grid = pd.MultiIndex.from_product([counties, range(Y0, Y1 + 1)], names=["county_fips", "year"]).to_frame(index=False)
        a = grid.merge(a, how="left").merge(land, how="left")
        num = ["swept_km2", "track_km", "pop_exposed", "n_tracks", "spc_inj", "spc_fat"]
        a[num] = a[num].fillna(0)
        a["swept_share"] = 1000 * a.swept_km2 / a.land_area_km2           # per-mille of county area swept
        a["spc_hit"] = (a.n_tracks > 0).astype(int)
        a["spc_pop_hit"] = (a.pop_exposed > 0).astype(int)
        a["log_pop_exposed"] = np.log1p(a.pop_exposed)
        a = a.drop(columns="land_area_km2")
        out.append(a.set_index(["county_fips", "year"]).add_prefix(pre))
    cy = pd.concat(out, axis=1).reset_index()
    cy.to_parquet(PROC / "spc_exposure_cy.parquet", index=False)

    d = cy[cy.year >= 1996]
    summ = pd.DataFrame({
        "share_cy_hit": [d.spc_hit.mean()], "share_cy_pop_hit": [d.spc_pop_hit.mean()],
        "mean_swept_share_if_hit": [d.loc[d.spc_hit == 1, "swept_share"].mean()],
        "median_pop_exposed_if_hit": [d.loc[d.spc_hit == 1, "pop_exposed"].median()],
        "p90_pop_exposed_if_hit": [d.loc[d.spc_hit == 1, "pop_exposed"].quantile(0.9)]})
    summ.to_csv(DIAG / "spc_exposure_summary.csv", index=False)
    log.info("SPC exposure summary:\n%s", summ.T.to_string())


if __name__ == "__main__":
    main()


