# Table 10. Multiple-testing adjustment

Families: confirmatory (5 pre-specified primary outcomes); exploratory families by outcome domain. BH = Benjamini-Hochberg q-value; Holm = Holm-adjusted p.

| outcome                                        | fam_mt                |    beta |     se |      p |   bh_q |   holm_p |
|:-----------------------------------------------|:----------------------|--------:|-------:|-------:|-------:|---------:|
| Worker separations (rate)                      | confirmatory          |  0.0005 | 0.0008 | 0.5416 | 0.677  |   1      |
| Employment retention                           | exploratory_labor     | -0.0003 | 0.0004 | 0.4552 | 0.5311 |   0.9775 |
| Establishment deaths (exit rate)               | confirmatory          |  0.0437 | 0.0468 | 0.3501 | 0.5835 |   1      |
| Establishment deaths (log count)               | exploratory_business  |  0.0196 | 0.0064 | 0.0022 | 0.0201 |   0.0201 |
| Job destruction rate (BDS)                     | confirmatory          |  0.1107 | 0.1067 | 0.2995 | 0.5835 |   1      |
| Job creation rate (BDS)                        | exploratory_business  |  0.1595 | 0.09   | 0.0766 | 0.2227 |   0.5361 |
| Job destruction rate (QWI firm job loss)       | exploratory_labor     |  0.0007 | 0.0004 | 0.0734 | 0.3922 |   0.5138 |
| Employment (log end-of-quarter)                | confirmatory          |  0.0012 | 0.0035 | 0.7307 | 0.7307 |   1      |
| Employment (QCEW log; 2014+)                   | exploratory_labor     | -0.0003 | 0.0021 | 0.9037 | 0.9037 |   0.9775 |
| Earnings (log avg monthly; stable)             | confirmatory          | -0.0017 | 0.0018 | 0.3418 | 0.5835 |   1      |
| New-hire earnings (log)                        | exploratory_labor     | -0.0045 | 0.0029 | 0.1181 | 0.3922 |   0.7086 |
| Hire rate                                      | exploratory_labor     | -0.0011 | 0.0009 | 0.1955 | 0.3922 |   0.9775 |
| New-hire rate                                  | exploratory_labor     | -0.0007 | 0.0007 | 0.2804 | 0.3926 |   0.9775 |
| Turnover (stable)                              | exploratory_labor     | -0.0004 | 0.0003 | 0.2241 | 0.3922 |   0.9775 |
| Small-firm establishment death rate (BDS 1-19) | exploratory_business  |  0.1003 | 0.0608 | 0.099  | 0.2227 |   0.5938 |
| Small-establishment share (CBP <20)            | exploratory_business  | -0.0002 | 0.0004 | 0.5546 | 0.6239 |   1      |
| Establishment birth rate                       | exploratory_business  | -0.0296 | 0.047  | 0.5286 | 0.6239 |   1      |
| Startup rate (age-0 firms' estabs)             | exploratory_business  | -0.0259 | 0.0392 | 0.5083 | 0.6239 |   1      |
| Out-migration rate                             | exploratory_household |  0.0317 | 0.0214 | 0.1386 | 0.7133 |   0.9705 |
| Net migration rate                             | exploratory_household | -0.0166 | 0.0325 | 0.6104 | 0.8475 |   1      |
| In-migration rate                              | exploratory_household |  0.0137 | 0.0282 | 0.6275 | 0.8475 |   1      |
| Out-migrant AGI (log)                          | exploratory_household | -0.001  | 0.0054 | 0.8475 | 0.8475 |   1      |
| Housing units authorized (IHS)                 | exploratory_household | -0.0072 | 0.0244 | 0.7673 | 0.8475 |   1      |
| Single-family units (IHS)                      | exploratory_household | -0.0203 | 0.0233 | 0.3834 | 0.8475 |   1      |
| Multifamily units (IHS)                        | exploratory_household |  0.0517 | 0.0407 | 0.2038 | 0.7133 |   1      |
| Establishments (CBP log)                       | exploratory_business  |  0.0074 | 0.0033 | 0.0222 | 0.1001 |   0.178  |
| Employment (CBP log)                           | exploratory_business  |  0.0046 | 0.0044 | 0.2995 | 0.5391 |   1      |
| Payroll (CBP log)                              | exploratory_business  |  0.0012 | 0.0054 | 0.8185 | 0.8185 |   1      |

## Resilience indices

| index                             |     beta |       se |        p |     bh_q |   holm_p |      N | status                                      |
|:----------------------------------|---------:|---------:|---------:|---------:|---------:|-------:|:--------------------------------------------|
| labor_market_resilience_index     |  -0.0034 |   0.0044 |   0.4441 |   0.6661 |   1      | 352873 | ok                                          |
| labor_market_resilience_index_icw |  -0.0025 |   0.0042 |   0.5561 |   0.6673 |   1      | 346150 | ok                                          |
| business_resilience_index         |  -0.0008 |   0.0118 |   0.9465 |   0.9465 |   1      | 103750 | ok                                          |
| business_resilience_index_icw     |  -0.0188 |   0.0097 |   0.0515 |   0.3093 |   0.3093 |  79072 | ok                                          |
| household_resilience_index        |  -0.0092 |   0.0084 |   0.2753 |   0.5911 |   1      |  36746 | ok                                          |
| household_resilience_index_icw    |  -0.0088 |   0.0084 |   0.2955 |   0.5911 |   1      |  36746 | ok                                          |
| fiscal_resilience_index           | nan      | nan      | nan      | nan      | nan      |    nan | INFEASIBLE (public finance LOW feasibility) |