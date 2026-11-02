# Preliminary Feasibility (Section 62 pilot)

Generated 2026-10-07 13:04. Analysis window for tornadoes: 1990-2025 (NOAA Storm Events, contiguous US).
Treatment = funded OpenFEMA HMA projects (status Closed/Approved/Obligated/Awarded/Completed) with an identified primary county.
Primary timing = obligation date + 2 years (fallback approval + 2y, then closeout). **OpenFEMA publishes no physical completion date.**

## Main table (primary timing)

| Treatment definition   |   Treated counties |   Post-treatment tornado counties |   Any tornado events |   EF1+ events |   EF2+ events |   EF3+ events | Assessment                                   |
|:-----------------------|-------------------:|----------------------------------:|---------------------:|--------------:|--------------:|--------------:|:---------------------------------------------|
| strict                 |                829 |                               758 |                 8939 |          4672 |          1138 |           294 | ADEQUATE event count for county-level design |
| moderate               |                840 |                               765 |                 8967 |          4682 |          1140 |           295 | ADEQUATE event count for county-level design |
| broad                  |               1042 |                               932 |                10600 |          5358 |          1327 |           339 | ADEQUATE event count for county-level design |

## Treated counties and post-treatment events under alternative timings

| Treatment definition   | Timing          |   Treated counties |   Median treatment year |   Post-trt EF1+ counties |   Post-trt EF2+ counties |   Post-trt EF3+ counties |   EF1+ events |   Post-trt EF1+ county-quarters |   Untreated EF1+ control counties |
|:-----------------------|:----------------|-------------------:|------------------------:|-------------------------:|-------------------------:|-------------------------:|--------------:|--------------------------------:|----------------------------------:|
| strict                 | t_primary       |                829 |                    2012 |                      689 |                      461 |                      192 |          4672 |                            3168 |                              1901 |
| strict                 | t_closeout      |                798 |                    2013 |                      665 |                      443 |                      188 |          4344 |                            2927 |                              1931 |
| strict                 | t_obligation_L0 |                798 |                    2010 |                      686 |                      469 |                      202 |          4810 |                            3266 |                              1930 |
| strict                 | t_approval_L0   |                808 |                    2010 |                      696 |                      480 |                      207 |          5012 |                            3418 |                              1921 |
| strict                 | t_obligation_L3 |                752 |                    2013 |                      624 |                      410 |                      170 |          4013 |                            2696 |                              1976 |
| moderate               | t_primary       |                840 |                    2012 |                      693 |                      461 |                      193 |          4682 |                            3176 |                              1890 |
| moderate               | t_closeout      |                808 |                    2013 |                      666 |                      443 |                      188 |          4349 |                            2931 |                              1921 |
| moderate               | t_obligation_L0 |                811 |                    2010 |                      693 |                      470 |                      202 |          4835 |                            3285 |                              1917 |
| moderate               | t_approval_L0   |                819 |                    2010 |                      702 |                      481 |                      207 |          5036 |                            3436 |                              1910 |
| moderate               | t_obligation_L3 |                764 |                    2013 |                      628 |                      411 |                      171 |          4028 |                            2705 |                              1964 |
| broad                  | t_primary       |               1042 |                    2011 |                      822 |                      541 |                      224 |          5358 |                            3667 |                              1723 |
| broad                  | t_closeout      |               1008 |                    2013 |                      790 |                      519 |                      216 |          4985 |                            3390 |                              1757 |
| broad                  | t_obligation_L0 |                963 |                    2010 |                      781 |                      527 |                      222 |          5274 |                            3607 |                              1789 |
| broad                  | t_approval_L0   |               1007 |                    2010 |                      814 |                      554 |                      235 |          5706 |                            3912 |                              1751 |
| broad                  | t_obligation_L3 |                903 |                    2013 |                      720 |                      463 |                      187 |          4426 |                            2999 |                              1849 |

## Treatment counts

- Funded wind/tornado-classified projects (broad, any geography): 6,739
- Strict projects with county FIPS in contiguous US: 5,056
- Treated states (strict): 37
- Largest state's share of strict treated counties: 7.6% (FL)

### Projects by mitigation type

| mitigation_type   |   projects |   counties |
|:------------------|-----------:|-----------:|
| broad_other       |        674 |        353 |
| moderate_other    |         88 |         39 |
| safe_room         |       3180 |        745 |
| wind_retrofit     |       1876 |        228 |

### Strict projects by protected facility type (text-based, approximate)

| facility_type       |   projects |
|:--------------------|-----------:|
| unknown             |       3115 |
| residential_private |        957 |
| school              |        734 |
| hospital            |        129 |
| fire_police         |         70 |
| community_shelter   |         42 |
| municipal           |          9 |

### Top 15 states (strict)

| STUSPS   |   projects |   counties |   federal_share_$M |
|:---------|-----------:|-----------:|-------------------:|
| FL       |       1365 |         66 |              731.5 |
| AL       |       1181 |         64 |              176.4 |
| TX       |        329 |         78 |              249.1 |
| OK       |        302 |         58 |              103.7 |
| MO       |        301 |         78 |              309.6 |
| LA       |        260 |         51 |              187.2 |
| MS       |        231 |         54 |              273.4 |
| AR       |        222 |         49 |              127.9 |
| KS       |        200 |         43 |               80.5 |
| KY       |        128 |         39 |               22.6 |
| TN       |         99 |         27 |               89.4 |
| IA       |         91 |         48 |               48.7 |
| SC       |         70 |         21 |               28.4 |
| WI       |         40 |         24 |               29.8 |
| GA       |         31 |         23 |               11.6 |
