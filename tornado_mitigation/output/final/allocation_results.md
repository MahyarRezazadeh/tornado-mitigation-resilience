# Allocation / targeting analysis: who gets tornado mitigation money? (2026-10-09)

Code: `src/49_allocation_analysis.py`. Tables: `output/tables/alloc_*.csv`.
Hit E = SPC track crosses a populated 2020 block-group centroid. Declaration = county designated in a DR declaration for a tornado or severe storm with incident year t. Project = new strict mitigation obligation in t+1..t+3. Panel 1999–2021, county FE + state×year FE, county clusters.

## A. Funnel: hit → declaration → project
| | Estimate | Base | p |
|---|---|---|---|
| Hit → county declared | +10.9 pp | 14.9% | <0.001 |
| Hit → project within 3 yrs | +1.66 pp (+24%) | 6.85% | <0.001 |
| Hit → log fed $/capita within 3 yrs | +0.037 | 0.164 | 0.005 |
| Hit, not declared → project | +0.77 pp | | 0.13 |
| Hit × declared → project | +2.75 pp | | 0.008 |

Raw: P(declared | hit) = 27%. P(project | hit, declared) = 23.7%. P(project | hit, not declared) = 16.5%. P(project | no hit, not declared) = 5.5%.
**The declaration is the gate:** almost all of the hit → mitigation link runs through a federal declaration.

## B. Who converts? Heterogeneity by stage
| Group (vs rest) | Stage 1: declared when hit (E×char) | Stage 2: project given declared (within state-year) | Overall: project when hit |
|---|---|---|---|
| Low income (bottom third, ACS 2009) | **+5.2 pp (p<0.001)** | −0.5 pp (0.67) | **+3.0 pp (0.008)** |
| High poverty | +4.6 pp (<0.001) | +1.5 pp (0.18) | +1.4 pp (0.21) |
| High non-white share | −1.1 pp (0.34) | −0.7 pp (0.60) | −0.3 pp (0.73) |
| Small population (bottom third) | **+6.5 pp (<0.001)** | **−9.7 pp (<0.001); base 13.7%** | −0.8 pp (0.54) |
| Non-metro | +3.6 pp (0.003) | −0.4 pp (0.70) | −0.05 pp (0.96) |
| Aligned with president's party (2009+) | **−4.7 pp (<0.001)** | +1.0 pp (0.44) | −1.3 pp (0.33) |

- **Capacity bottleneck:** small counties are *more* likely to be declared when hit, plausibly because per-capita damage thresholds are easier to cross. But once declared they are 71% less likely to turn the declaration into a project, so the overall advantage is zero.
- **No low-income or minority penalty:** low-income counties actually end up with more projects after a hit.
- **Political alignment:** aligned counties are less likely to be declared. This runs against the usual favoritism prediction and is likely confounded by urban/rural partisan sorting across administrations. Treat it as tentative.

## C. Targeting: does money follow risk?
- **Within states:** 1999–2012 spending follows recent populated hits (1996–2010; +0.09 SD, p=0.004), not smoothed 1980–95 climatology (−0.02, p=0.53). Recent hits strongly predict 2013–24 hits (+0.27 SD, p<0.001), so reacting to recent hits is not obviously a "recency bias". Conditional on risk, spending does not predict future hits (+0.03, p=0.34).
- **Across states (no state FE):** spending loads as heavily on historical climatology (+0.24 SD, p=0.002) as on realized future hits (+0.23 SD).
- **Federal $ (1999–2012) per future (2013–24) populated hit, by 1980–95 climatology tercile:**
  - **low:** $0.18M; $0.56 per capita; track growth 1990–2004 → 2010–24: +1%
  - **mid:** $0.42M; $4.50 per capita; track growth +24%
  - **high:** $0.75M; $9.68 per capita; track growth −2%

  High-climatology (traditional Alley) counties receive about 4× more per future populated hit than low-climatology counties. Tornado activity grew most in the middle tercile, consistent with the documented eastward shift.

## Assessment
These are descriptive associations, not causal estimates. Two hooks have potential:
1. The small-county conversion gap (declared but not implemented).
2. The between-state allocation anchored on historical climatology and lagging the shifting risk.

Before either is credible: stage-2 controls (damage, state program design, declaration size), state safe-room programs as an explanation for the between-state gap, a damage-threshold explanation for the stage-1 small/low-income effects, and alignment robustness.
