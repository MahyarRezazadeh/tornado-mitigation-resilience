**Bottom line.** Public data are more than sufficient to *run* this design (867 strict-treated counties, ~3,200
post-treatment EF1+ county-quarters, 1,900 untreated tornado-hit controls; 12 of 15 outcome groups rate EXCELLENT
feasibility), but the central resilience hypothesis is **not supported** at the county level:

1. **An EF1+ tornado leaves no detectable footprint on county aggregates.** Across all 28 outcomes the tornado main
   effect (unmitigated counties) is near zero and insignificant (e.g. log employment +0.09%, separation rate
   +0.00004). The distributed-lag event studies show no post-tornado employment dip and no recovery path to speak of.
   With no measurable disruption, there is nothing for mitigation to offset. This dilution of a 1-2 km-wide damage path
   in a county-wide aggregate is the binding constraint, not sample size.
2. **Labor-market outcomes: no protective effect.** Separations are a precise null (beta = +0.0005, 95% CI
   [-0.0011, +0.0020] vs E* = 0.0025; pretrend p = 0.23, placebo p = 0.93, RI p = 0.50, LOSO sign share 1.00) and are
   classified NO DETECTABLE EFFECT. Employment, earnings and hires are UNDERPOWERED: CIs cannot exclude a
   0.05 within-county-SD effect in either direction.
3. **Business outcomes: no protective effect; the consistent signs point the *wrong* way.** Small-firm (1-19)
   establishment deaths (beta = +0.10 pp, p = 0.10; stacked p = 0.04, IW p = 0.02; 98% sign consistency) and QWI firm job
   destruction (p = 0.07) are MODERATELY ROBUST in the *adverse* direction, but neither survives multiple-testing
   correction (BH q = 0.22 and 0.39). The most plausible reading is selection: HMGP safe rooms go to counties right
   after major disasters (94% HMGP; 44% after tornado/severe-storm declarations), which are on weaker trajectories.
   The only protective-signed significant result, CBP establishments (+0.7%), fails the stacked pretrend test
   (p = 0.019) and is NOT ROBUST.
4. **Physical damage is the one economically large signal, and it is not yet credible.** Mitigated counties report
   ~42% less property damage per EF step (p < 1e-6), robust to definitions, timing, dropping FL/OK/TX, safe-room-only,
   state clustering, and to a within-treated design that drops the 5 pre-treatment years (about -58% to -60%). But
   (i) before treatment, future-treated counties reported ~40-50% MORE damage per EF step than never-treated counties
   (placebo p < 1e-4), i.e. strong selection on damage; (ii) the EF rating is itself assigned from observed damage, so
   "intensity" is partly an outcome of mitigation; (iii) the pre/post comparison spans the 2007 F-to-EF change and
   changes in NWS damage-estimation practice. Fatalities are not reduced (within-treated +0.02 to +0.04 log points, p <= 0.02).
5. **Multiple testing and indices.** No confirmatory outcome survives BH or Holm correction (all q >= 0.58); the
   labor, business and household resilience indices are all insignificant (p = 0.05-0.95).

Feasible, but the county-quarter resilience design cannot answer the question it was built for. The informative null
on separations and the damage signal justify a redesign, not a paper in the current form.
<!--END-EXEC-->

<!--LIT-->
Closest prior work: Davlasheridze, Fisher-Vanden & Klaiber (2017, JEEM) estimate the hurricane analogue for property
losses; Healy & Malhotra (2009) and Rose et al. (2007) estimate returns to mitigation/preparedness in damages;
Merrell, Simmons & Sutter (2005) value tornado shelters by casualties. Disaster-labor/business papers (Groen et al.
2020; Basker & Miranda 2018; Boustan et al. 2020; Ewing et al. 2009 Oklahoma City tornado) have no mitigation
treatment. I found no close causal study in the searched economics/public-policy literature estimating FEMA
tornado/wind mitigation x subsequent tornado effects on labor or business outcomes (novelty HIGH for labor/business,
MEDIUM for migration/housing and damage). Google Scholar, SSRN and RePEc could not be queried by API.
<!--END-LIT-->

<!--THREATS-->
1. **Endogenous, post-disaster treatment assignment (biggest threat).** 94% of strict projects are HMGP grants that
   exist only after a disaster declaration; 44% follow tornado/severe-storm declarations. Treated counties differ on
   pre-treatment damage per intensity (+40-50%, placebo p < 1e-4) and on historical tornado density (raw SMD 0.6-0.9).
   Matching/weighting fixes observables but not selection on recent shocks; the never-funded applicant pool is
   only 36 counties.
2. **Treatment timing is a proxy.** OpenFEMA has no completion date; obligation + 2 years vs. a median 3.6-year
   obligation-to-closeout gap means misclassification of operational status near the cutoff (attenuation).
3. **Exposure-outcome scale mismatch.** Tornado paths cover a tiny share of a county; county aggregates dilute both
   the shock and any protection, which drives the near-zero tornado main effects and the UNDERPOWERED ratings.
4. **Geographic mismatch of treatment.** Projects are coded to a primary county; 8% are statewide; safe rooms protect
   specific sites (schools, mobile-home parks), not county labor markets.
5. **Intensity is damage-based.** EF ratings are inferred from damage, so Mitigation x intensity specifications
   condition on a variable mitigation can affect.
6. **Outcome measurement.** NOAA property damage is an estimate whose methods changed over time; QWI suppression is low
   (1-2%) at county totals but higher in cells.
<!--END-THREATS-->

<!--BEST-->
**Best paper to write (redesign): "Does Tornado Mitigation Reduce Losses? Evidence from FEMA Safe Rooms and Wind
Retrofits."** A tornado analogue to Davlasheridze et al. (2017), with three changes that address the threats above:
(a) **exposure independent of damage**: tornado path length/width and swath area from NOAA/SPC GIS tracks, or
radar-derived rotation/wind fields (e.g. Multi-Radar Multi-Sensor rotation tracks, 2000s+), instead of EF ratings;
(b) **sub-county matching**: intersect tornado swaths with project sites (HMA project-site inventories
geocode many projects) and with census blocks/ZIPs, so the comparison is struck-and-protected vs struck-and-unprotected
places; (c) **selection**: compare counties/places with funded projects to applicants denied or not selected, and use
the state HMGP ceiling (a formula share of post-disaster aid) as an instrument for mitigation intensity. The labor-market
null (separations) becomes a secondary, informative result: even large wind-mitigation programs do not show up in
county labor-market flows, which bounds the labor-market benefits in BCA.
<!--END-BEST-->

<!--DATA-->
Most valuable improvements, in order: (1) **project completion dates and geocoded project sites** (FEMA FOIA, or the
HmaSubapplicationsProjectSiteInventories dataset for recent projects); (2) **damage-independent hazard intensity**
(SPC GIS tracks with width, MRMS rotation tracks); (3) **sub-county outcomes**: LEHD LODES block-level jobs,
ZIP Business Patterns, or establishment-level microdata (Census RDC: LBD/BR) to match outcomes to tornado swaths;
(4) **BRIC/PDM national competition scores and funding lines** (FOIA) for an RD; (5) property-level losses (FEMA
Individual Assistance inspections, insurance claims) for a damage outcome not produced by NWS estimators.
<!--END-DATA-->

<!--R-->
Partly. Adoption is clearly endogenous to past disasters (pre-treatment damage placebo fails, p < 1e-4), but the
economic outcomes show no adoption pre-trends (adoption event-study pre p = 0.21-0.88, except earnings p = 0.03)
and acceptable tornado-event pre-trends (p = 0.23-0.99, except earnings p = 0.053, borderline). For the economic outcomes endogeneity is less of a problem than
power and dilution; for the damage outcome it is decisive. Credible publication requires the redesign in Section 25.
<!--END-R-->

<!--T-->
The damage-loss paper (Section 25), redesigned with damage-independent exposure, sub-county matching and
applicant/HMGP-ceiling identification. Labor/business resilience at the county level should be reported only as a
bounded null within that paper, not as a standalone paper.
<!--END-T-->
