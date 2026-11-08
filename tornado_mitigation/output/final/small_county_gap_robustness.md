# Small-county conversion gap: robustness (2026-10-09)

Code: `src/50_small_county_robustness.py`. Tables: `output/tables/small_gap_*.csv`.

- **Unit:** county × disaster declaration. Major disaster (DR), tornado or severe storm, county designated, incident year 1999–2021. N = 12,038 county-declarations (2,767 counties, 736 disasters). Small = bottom third of counties nationally by population.
- **Project attribution:** multi-county projects (1,620) are credited to every listed county. HMGP projects are linked to the specific disaster number.
- **Preferred spec (S4):** disaster FE (same declaration, same HMGP pot) plus hit / people-in-path / track km / EF / casualties / log damage / damage per capita, plus log income, poverty, non-white share and non-metro. County clusters.

## Gap: small minus other counties (S4)
| Outcome | Gap | Base (others) | Relative | p |
|---|---|---|---|---|
| Any HMGP project from this disaster | −8.8 pp | 27.2% | −32% | <0.001 |
| Safe room / wind retrofit from this disaster | −3.1 pp | 6.4% | −49% | <0.001 |
| Strict project within 3 yrs | −8.1 pp | 14.6% | −55% | <0.001 |
| Strict project within 5 yrs | −10.5 pp | 19.7% | −53% | <0.001 |
| Any HMA project within 3 yrs | −12.9 pp | 64.7% | −20% | <0.001 |
| log federal $ per capita from this disaster | −0.089 | | | <0.001 |

## Stability
- **Specification ladder:** the gap barely moves going from state-year FE (−11.4 pp on any-project-from-disaster) to disaster FE (−11.3), + exposure/damage (−10.5), + demographics (−8.8).
- **State clusters, IA-declared counties only:** unchanged.
- **Hit-only sample (N = 1,203):** larger gap, −14.3 pp (any) and −13.4 pp (strict, 3 yrs).
- **Leave one state out:** −8.4 to −9.4 pp (any); −6.6 to −9.0 pp (strict, 3 yrs). All p < 0.001.
- **Continuous log population:** +7.8 pp per log point (p < 0.001).
- **Population deciles vs the top decile:** a smooth, monotone gradient (−35.5, −32.4, −29.6, −26.9, −23.1, −21.1, −19.9, −15.9, −11.5 pp). There is no threshold; it is a size gradient, not a "tiny counties" effect.
- **"Tornado" incident-type declarations only (N = 361):** the gap shrinks and is not significant (−1.5 pp, SE 4.0). The confidence interval contains the main estimate, so this test is underpowered rather than contradictory.

## Alternative explanations
- **States run the projects for small counties (statewide projects):** crediting every statewide HMGP project of the same disaster to all designated counties nearly closes the any-type gap (−0.9 pp). But that outcome is saturated: 89% of county-declarations have some statewide project, mostly planning, generators and similar. For safe rooms and retrofits the gap remains: −2.8 pp on a 10% base (−28%), p < 0.001. Statewide delivery offsets part of the gap, not all of it.
- **Damage size or declaration thresholds:** ruled out by the damage and damage-per-capita controls and by the disaster FE.
- **Poverty, race, rurality:** controlled; they shrink the gap only modestly.
- **Learning from experience:** rejected. Prior HMA experience raises conversion for larger counties (+5.0 pp any, +7.2 pp strict) but not for small ones; the interaction fully offsets it (−5.4 and −7.4 pp). Experience does not close the gap; it widens it. That fits standing staff capacity (larger counties keep mitigation or grants staff) better than one-off learning.

## Not yet ruled out
- **Number of eligible applicants:** cities, school districts and special districts scale with population. A smooth population gradient is exactly what a "more applicant entities" mechanism would produce.
  - Next: control for the count of local governments per county (Census of Governments 2002/2007/2012/2017), and use the subrecipient type field to separate county-government applications from city/district ones.
- **Applications vs approvals:** we only see funded projects. OpenFEMA HMA subapplication data cover recent BRIC/FMA cycles only, so for HMGP we cannot separate "did not apply" from "applied and was rejected".
