# Table 7. Mechanisms

| mechanism   | outcome                  | sample                                 |   mean_y | term                   |    beta |     se |      p |   ci_low |   ci_high |       N | status   |
|:------------|:-------------------------|:---------------------------------------|---------:|:-----------------------|--------:|-------:|-------:|---------:|----------:|--------:|:---------|
| M1          | log_damage               | all county-quarters                    |   0.4669 | MI                     | -0.3662 | 0.0742 | 0      |  -0.5116 |   -0.2208 |  447408 | ok       |
| M1          | log_damage               | tornado county-quarters (EF bins FE)   |   6.5455 | M                      | -0.2087 | 0.1458 | 0.1526 |  -0.4947 |    0.0773 |   30861 | ok       |
| M1          | log_damage               | tornado county-quarters, M x intensity |   6.5455 | MI                     | -0.5425 | 0.0937 | 0      |  -0.7262 |   -0.3588 |   30861 | ok       |
| M1          | log_fatalities           | all county-quarters                    |   0.002  | MI                     |  0.0098 | 0.0035 | 0.0058 |   0.0028 |    0.0167 |  447408 | ok       |
| M1          | log_fatalities           | tornado county-quarters (EF bins FE)   |   0.028  | M                      | -0.0065 | 0.0061 | 0.2913 |  -0.0185 |    0.0055 |   30861 | ok       |
| M1          | log_fatalities           | tornado county-quarters, M x intensity |   0.028  | MI                     |  0.0365 | 0.0077 | 0      |   0.0215 |    0.0516 |   30861 | ok       |
| M1          | log_injuries             | all county-quarters                    |   0.0123 | MI                     | -0.0006 | 0.0087 | 0.9446 |  -0.0177 |    0.0165 |  447408 | ok       |
| M1          | log_injuries             | tornado county-quarters (EF bins FE)   |   0.1719 | M                      | -0.0176 | 0.0164 | 0.2826 |  -0.0498 |    0.0145 |   30861 | ok       |
| M1          | log_injuries             | tornado county-quarters, M x intensity |   0.1719 | MI                     |  0.0495 | 0.0186 | 0.0078 |   0.013  |    0.086  |   30861 | ok       |
| M4          | establishment_death_rate | BDS firm size 1-19 vs 20+              | nan      | MTS                    |  0.1213 | 0.0829 | 0.1436 |  -0.0413 |    0.284  |  249531 | ok       |
| M4          | establishment_death_rate | BDS firm size 20+ baseline MxT         | nan      | MT                     | -0.0221 | 0.0621 | 0.7214 |  -0.1438 |    0.0996 |  249531 | ok       |
| M4          | job_destruction_rate     | BDS firm size 1-19 vs 20+              | nan      | MTS                    |  0.0399 | 0.1483 | 0.7881 |  -0.2509 |    0.3306 |  310726 | ok       |
| M4          | job_destruction_rate     | BDS firm size 20+ baseline MxT         | nan      | MT                     |  0.0675 | 0.1295 | 0.602  |  -0.1863 |    0.3214 |  310726 | ok       |
| M4          | separation_rate          | QWI firm size <20 vs 20+               | nan      | MTS                    |  0.0009 | 0.0013 | 0.4867 |  -0.0017 |    0.0035 | 1662682 | ok       |
| M4          | log_employment           | QWI firm size <20 vs 20+               | nan      | MTS                    |  0.009  | 0.0056 | 0.1061 |  -0.0019 |    0.0199 | 1695674 | ok       |
| M5          | separation_rate          | facility-type split (overlapping)      | nan      | MT_school              |  0      | 0.0013 | 0.9971 |  -0.0025 |    0.0025 |  352841 | ok       |
| M5          | separation_rate          | facility-type split (overlapping)      | nan      | MT_residential_private | -0.0015 | 0.0012 | 0.1965 |  -0.0039 |    0.0008 |  352841 | ok       |
| M5          | separation_rate          | facility-type split (overlapping)      | nan      | MT_hospital            | -0.0014 | 0.0024 | 0.5527 |  -0.0062 |    0.0033 |  352841 | ok       |
| M5          | separation_rate          | facility-type split (overlapping)      | nan      | MT_fire_police         | -0.0009 | 0.0031 | 0.7792 |  -0.0069 |    0.0052 |  352841 | ok       |
| M5          | separation_rate          | facility-type split (overlapping)      | nan      | MT_community_shelter   |  0.0012 | 0.0025 | 0.6216 |  -0.0036 |    0.0061 |  352841 | ok       |
| M5          | separation_rate          | facility-type split (overlapping)      | nan      | MT_unknown             |  0.0013 | 0.001  | 0.1695 |  -0.0006 |    0.0032 |  352841 | ok       |
| M5          | establishment_death_rate | facility-type split (overlapping)      | nan      | MT_school              |  0.168  | 0.0789 | 0.0334 |   0.0132 |    0.3227 |  103769 | ok       |
| M5          | establishment_death_rate | facility-type split (overlapping)      | nan      | MT_residential_private | -0.0269 | 0.0803 | 0.7375 |  -0.1843 |    0.1305 |  103769 | ok       |
| M5          | establishment_death_rate | facility-type split (overlapping)      | nan      | MT_hospital            | -0.1479 | 0.1605 | 0.3568 |  -0.4626 |    0.1668 |  103769 | ok       |
| M5          | establishment_death_rate | facility-type split (overlapping)      | nan      | MT_fire_police         |  0.1899 | 0.2472 | 0.4424 |  -0.2948 |    0.6746 |  103769 | ok       |
| M5          | establishment_death_rate | facility-type split (overlapping)      | nan      | MT_community_shelter   | -0.1607 | 0.1362 | 0.2382 |  -0.4278 |    0.1064 |  103769 | ok       |
| M5          | establishment_death_rate | facility-type split (overlapping)      | nan      | MT_unknown             |  0.0253 | 0.0608 | 0.6772 |  -0.0939 |    0.1446 |  103769 | ok       |
| M5          | log_employment           | facility-type split (overlapping)      | nan      | MT_school              |  0.0013 | 0.0051 | 0.799  |  -0.0087 |    0.0113 |  356048 | ok       |
| M5          | log_employment           | facility-type split (overlapping)      | nan      | MT_residential_private | -0.0003 | 0.0064 | 0.9643 |  -0.0129 |    0.0123 |  356048 | ok       |
| M5          | log_employment           | facility-type split (overlapping)      | nan      | MT_hospital            | -0.0187 | 0.0083 | 0.0238 |  -0.0348 |   -0.0025 |  356048 | ok       |
| M5          | log_employment           | facility-type split (overlapping)      | nan      | MT_fire_police         |  0.0263 | 0.0123 | 0.0324 |   0.0022 |    0.0504 |  356048 | ok       |
| M5          | log_employment           | facility-type split (overlapping)      | nan      | MT_community_shelter   |  0.0058 | 0.0094 | 0.5365 |  -0.0126 |    0.0242 |  356048 | ok       |
| M5          | log_employment           | facility-type split (overlapping)      | nan      | MT_unknown             | -0.0009 | 0.0048 | 0.8531 |  -0.0104 |    0.0086 |  356048 | ok       |
| M2          | separation_rate          | physical vs remote-capable industries  | nan      | MTP                    |  0.0034 | 0.0013 | 0.01   |   0.0008 |    0.006  | 2231113 | ok       |
| M2          | separation_rate          | remote-capable baseline MxT            | nan      | MT                     | -0.0018 | 0.0011 | 0.1019 |  -0.004  |    0.0004 | 2231113 | ok       |
| M2          | log_employment           | physical vs remote-capable industries  | nan      | MTP                    |  0.0026 | 0.005  | 0.6052 |  -0.0072 |    0.0124 | 2364677 | ok       |
| M2          | log_employment           | remote-capable baseline MxT            | nan      | MT                     | -0.0002 | 0.005  | 0.9715 |  -0.0101 |    0.0097 | 2364677 | ok       |
| M2          | log_earnings             | physical vs remote-capable industries  | nan      | MTP                    |  0.002  | 0.0028 | 0.477  |  -0.0035 |    0.0074 | 2342729 | ok       |
| M2          | log_earnings             | remote-capable baseline MxT            | nan      | MT                     | -0.0031 | 0.0026 | 0.2375 |  -0.0082 |    0.002  | 2342729 | ok       |
| M2          | job_destruction_rate_qwi | physical vs remote-capable industries  | nan      | MTP                    |  0.0011 | 0.0008 | 0.1635 |  -0.0005 |    0.0027 | 2343453 | ok       |
| M2          | job_destruction_rate_qwi | remote-capable baseline MxT            | nan      | MT                     |  0.0001 | 0.0007 | 0.8619 |  -0.0013 |    0.0015 | 2343453 | ok       |

## Severity gradient

| outcome                  | bin     |   tornado_effect |   tornado_se |   mitig_diff |   mitig_diff_se |   mitig_diff_p |   n_treated_obs |
|:-------------------------|:--------|-----------------:|-------------:|-------------:|----------------:|---------------:|----------------:|
| separation_rate          | EF0     |          -0.0013 |       0.0005 |       0.0024 |          0.0009 |         0.0102 |            2116 |
| separation_rate          | EF1     |          -0.0006 |       0.0005 |       0.001  |          0.0009 |         0.2726 |            2229 |
| separation_rate          | EF2     |           0.0007 |       0.001  |       0.0007 |          0.0014 |         0.5958 |             694 |
| separation_rate          | EF3plus |           0.0018 |       0.0016 |      -0.0021 |          0.0022 |         0.3425 |             260 |
| log_employment           | EF0     |           0.0025 |       0.0018 |       0.0065 |          0.004  |         0.1063 |            2118 |
| log_employment           | EF1     |           0.0009 |       0.0018 |       0.0021 |          0.0038 |         0.5734 |            2231 |
| log_employment           | EF2     |          -0.0002 |       0.0032 |       0.0013 |          0.0061 |         0.8267 |             694 |
| log_employment           | EF3plus |           0.0066 |       0.005  |      -0.0014 |          0.009  |         0.8767 |             260 |
| log_earnings             | EF0     |          -0.0002 |       0.001  |       0.0011 |          0.0021 |         0.5957 |            2116 |
| log_earnings             | EF1     |          -0.0023 |       0.001  |       0.0001 |          0.002  |         0.9546 |            2229 |
| log_earnings             | EF2     |           0.0032 |       0.0017 |      -0.0076 |          0.0031 |         0.014  |             694 |
| log_earnings             | EF3plus |          -0.0012 |       0.003  |       0.0006 |          0.0053 |         0.9091 |             260 |
| establishment_death_rate | EF0     |          -0.0052 |       0.0237 |      -0.0449 |          0.0533 |         0.399  |            1307 |
| establishment_death_rate | EF1     |           0.0207 |       0.0272 |       0.0006 |          0.0553 |         0.9913 |            1477 |
| establishment_death_rate | EF2     |           0.005  |       0.0411 |       0.1268 |          0.0864 |         0.1422 |             485 |
| establishment_death_rate | EF3plus |           0.0165 |       0.0596 |       0.0638 |          0.13   |         0.6234 |             191 |
| job_destruction_rate     | EF0     |           0.0246 |       0.0499 |       0.0143 |          0.1173 |         0.9027 |            1308 |
| job_destruction_rate     | EF1     |           0.0129 |       0.0526 |       0.1442 |          0.1242 |         0.2456 |            1478 |
| job_destruction_rate     | EF2     |           0.152  |       0.1025 |       0.0914 |          0.1939 |         0.6375 |             485 |
| job_destruction_rate     | EF3plus |          -0.0241 |       0.1264 |      -0.0418 |          0.2745 |         0.879  |             191 |