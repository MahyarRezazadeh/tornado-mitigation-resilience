# Redesign results: SPC tornado tracks, spending first stage, land productivity (2026-10-09)

Code: `src/43_download_redesign.py` → `44_spc_exposure.py` → `45_land_productivity.py` → `46_redesign_analysis.py` → `47_redesign_robustness.py` → `48_redesign_damage_checks.py`.
Tables: `output/tables/redesign_*.csv`. Sample: county-years 1999–2024, county FE + state×year FE, SEs clustered by county unless stated.

## 1. Exposure measure (SPC tracks)
- 51,600 SPC tornadoes from 1980 to 2024. Each track is a straight start→end line, buffered by half the reported path width (77% have an end point; the rest are an area-equivalent disc). The track is intersected with 2020 county polygons.
- **E (primary)** = the swept path (+500 m) contains the population centroid of at least one 2020 block group, i.e. the tornado crossed a populated place. Neither the EF rating nor any damage enters E. Caveat: path length and width come from damage surveys, but they describe geometry, not dollar losses.
- **Dilution, measured directly:** 25.8% of county-years have any track, but only 6.3% have a track through a populated place. A hit sweeps on average 1.85‰ (about 0.19%) of the county's land.

## 2. First stage: more-exposed places implement more mitigation (yes)
| | Estimate | p |
|---|---|---|
| Populated-place hit at t−2 → P(new strict project obligated in t) | +1.49 pp (mean 2.78%, i.e. +54%) | <0.001 |
| Same → log(1 + new federal $ per capita) | +0.031 (mean 0.058) | <0.001 |
| Hit at t−1 → P(new project) | +0.66 pp | 0.08 |
| Leads t+1, t+2 (placebo) | −0.07 pp, −0.48 pp | 0.85, 0.15 |
| Contemporaneous, t−3, t−4 | ≈0 | >0.5 |
| Robust to population-decile×year FE (t−2) | +0.031 | <0.001 |
| Any-track exposure (population-independent), t−2 / t−4 | +0.010 / +0.012 | 0.05 / 0.02 |
| **Cross-section:** 1 SD of pre-1996 people-in-path per 1,000 residents → log total 1999–2024 strict federal $/capita | +0.25 | <0.001 |
| Cross-section, extensive margin (ever treated) | +1.5 pp | 0.10 |
| Cross-section, pre-1996 swept *area* share | ≈0 | 0.50 |
| Instrument Z = leave-own-county-out state mitigation pool × pre-1996 exposure → operational stock S | F = 19.0 | <0.001 |

The first-stage timing is sharp. Obligations peak two years after a populated-place hit, which matches the HMGP declaration→obligation pipeline, and the placebo leads are null. Implementation follows people in the path, not swept area. In the cross-section, prior exposure mainly raises how much is spent, not whether a county gets any project at all.

## 3. Land productivity per hectare
- **Real GDP per hectare** (BEA CAGDP9, chained 2017 $, 2001–2024; median $5,504/ha).
- **Agricultural real GDP per hectare** (BEA).
- **Crop cash receipts per hectare** (BEA CAINC45, 1969–2022).
- **Crop yield, corn+soy+wheat, tonnes per harvested hectare** (NASS survey, stream-filtered from the QuickStats bulk file; median 2.71 t/ha; corn 4.43 t/ha).

## 4. Dose-response: did counties that spent more fare better when hit?
Model: Y = b·(E × S) + g·E + d·S. S = log(1 + operational strict federal $ per capita), using obligation+2y timing. Among treated counties in 2024, median S = 3.3 (≈$26/capita) and IQR 2.0–4.4.

| Outcome | g: exposure alone | b: E×S (p) | Survives pop-decile×yr FE? | Survives county trends? | Pre-treatment placebo (p) | 2SLS b (p) |
|---|---|---|---|---|---|---|
| Real GDP/ha (log) | +0.005 (p=0.03) | +0.0047 (0.018) | **No** (+0.0007, 0.72) | **No** (−0.0002, 0.86) | 0.000 (0.99) | +0.009 (0.07) |
| Ag GDP/ha (log) | −0.003 (0.81) | +0.001 (0.89) | – | – | 0.007 (0.39) | −0.014 (0.48) |
| Crop receipts/ha (log) | −0.012 (0.02) | −0.018 (0.002) | **No** (−0.007, 0.21) | **No** (+0.004, 0.18) | 0.004 (0.12) | −0.038 (0.003) |
| Crop yield t/ha (log, NASS) | −0.006 (0.23) | +0.002 (0.69) | +0.004 (0.53) | +0.003 (0.58) | 0.002 (0.66) | −0.012 (0.43) |
| Property damage (log1p $, NOAA) | +7.2 (<0.001) | **−0.318 (<0.001)** | **Yes** (−0.316, <0.001) | **Yes** (−0.306, <0.001) | +0.084 (0.10) | −0.49 (0.001) |
| Casualties (log1p inj+fat) | +0.55 (<0.001) | −0.006 (0.63) | – | – | **+0.051 (<0.001)** | +0.005 (0.85) |
| Establishment death rate | −0.007 (0.79) | −0.011 (0.57) | – | – | 0.003 (0.89) | −0.040 (0.25) |
| Job destruction rate | −0.16 (0.003) | +0.004 (0.93) | – | – | 0.054 (0.14) | −0.13 (0.09) |
| Small-firm death rate | −0.015 (0.63) | −0.001 (0.98) | – | – | 0.009 (0.73) | 0.003 (0.95) |
| Employment (log, CBP) | +0.005 (0.01) | +0.0067 (0.001) | **No** (0.0005, 0.79) | **No** (−0.0003, 0.79) | 0.001 (0.52) | +0.009 (0.17) |
| Establishments (log, CBP) | +0.004 (0.02) | +0.0073 (<0.001) | **No** (0.0009, 0.58) | **No** (−0.0005, 0.24) | −0.001 (0.36) | +0.012 (0.05) |

### Reading
1. **Land productivity:** spending gives no robust gain. The positive GDP/ha, employment and establishment interactions disappear completely once population-decile×year FE or county trends are added. Large, growing counties both spend more and are more likely to have tornadoes cross their populated places, and that confound drives the naive estimates. Crop yields per hectare don't respond to exposure or to spending, which fits a hit sweeping about 0.2% of county land.
2. **Damage, the only robust interaction:** b = −0.32 survives population×year FE, county trends, dropping Florida, state clustering (p=0.07) and 2SLS. Its pre-treatment placebo has the *opposite* sign (+0.08), unlike the old EF-based design (+39–50%). **Decomposition shows it is purely an extensive-margin effect:**
   - P(any damage reported | hit) falls 2.7 pp per unit of S (p<0.001), about −9 pp at median spending.
   - log $ damage when positive: b = +0.003 (p=0.93).
   - PPML on $ levels: +0.14 (p=0.24). Exposed-only comparisons: n.s.
   - Dose bins (federal $/capita, relative to $0): ≤$10 −1.33, $10–50 −1.67, >$50 −0.73 (p=0.07). Not monotone; the highest spenders gain least.
   - The effect is absent with any-track exposure (+0.05, p=0.26).

   Taken together: when a tornado hits a mitigated populated place, counties are less likely to report any damage, but dollar losses don't fall and more spending doesn't do better. Real avoided minor damage can't be separated from county/NWS-office reporting practices.
3. **Casualties:** no effect, and the placebo fails (+0.05, p<0.001). Counties that later receive mitigation already had more casualties per hit, so safe-room targeting follows past casualties.
4. **"Spent more → better outcomes":** **not supported** for productivity, labor, business, casualties or dollar losses. The spending tiers point the "right" way only for the outcomes that fail the trend checks.

## 5. Assessment
- **Established:** a strong, well-timed first stage. Exposure of populated places raises mitigation implementation about two years later, with clean leads. That is publishable descriptive/political-economy evidence on post-disaster HMA allocation.
- **Not established:** any economic return to mitigation spending at the county level, measured as land productivity, GDP, employment or crop yields.
- **Remaining credible angle:** structure-level outcomes. Damage surveys or the NWS DAT points, matched to project sites, would avoid county dilution. The county-level design has now failed with two independent exposure measures.
