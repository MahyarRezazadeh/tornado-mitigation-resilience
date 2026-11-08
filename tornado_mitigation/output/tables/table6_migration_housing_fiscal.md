# Table 6. Migration / housing / fiscal results

Model: Y = b*Mitigated*Tornado + g1*Mitigated + g2*Tornado + county FE + state x time FE; clustered by county. Tornado = EF1+ (quarterly: same quarter; annual: March-aligned). Treatment = strict, obligation+2y.

| Outcome                        |   beta (MxT) |     SE |       t |      p |   CI low |   CI high |   Tornado main effect |   SE(T) |   Mean Y |   beta % mean |      N |   Counties |   Treated counties |   Treated tornado obs |   Within R2 |
|:-------------------------------|-------------:|-------:|--------:|-------:|---------:|----------:|----------------------:|--------:|---------:|--------------:|-------:|-----------:|-------------------:|----------------------:|------------:|
| Out-migration rate             |       0.0317 | 0.0214 |  1.4813 | 0.1386 |  -0.0103 |    0.0738 |                0.0071 |  0.0152 |   6.041  |        0.5255 |  36925 |       3105 |                869 |                  1815 |      0.0003 |
| Net migration rate             |      -0.0166 | 0.0325 | -0.5095 | 0.6104 |  -0.0803 |    0.0471 |               -0.0283 |  0.0255 |   0.2488 |       -6.6528 |  36746 |       3105 |                869 |                  1815 |      0.0001 |
| In-migration rate              |       0.0137 | 0.0282 |  0.4852 | 0.6275 |  -0.0416 |    0.069  |               -0.0197 |  0.0228 |   6.293  |        0.2175 |  36746 |       3105 |                869 |                  1815 |      0.0001 |
| Out-migrant AGI (log)          |      -0.001  | 0.0054 | -0.1923 | 0.8475 |  -0.0117 |    0.0096 |                0.007  |  0.0035 |  10.3886 |       -0.0101 |  36907 |       3105 |                869 |                  1815 |      0.0005 |
| Housing units authorized (IHS) |      -0.0072 | 0.0244 | -0.296  | 0.7673 |  -0.055  |    0.0406 |                0.0069 |  0.0082 |   4.5829 |       -0.1575 | 107690 |       3047 |                862 |                  2564 |      0.0002 |
| Single-family units (IHS)      |      -0.0203 | 0.0233 | -0.8718 | 0.3834 |  -0.066  |    0.0254 |                0.0073 |  0.0076 |   4.375  |       -0.4642 | 107690 |       3047 |                862 |                  2564 |      0.0001 |
| Multifamily units (IHS)        |       0.0517 | 0.0407 |  1.2711 | 0.2038 |  -0.028  |    0.1314 |               -0.0041 |  0.0149 |   2.1591 |        2.3934 | 107690 |       3047 |                862 |                  2564 |      0      |

Local fiscal outcomes: LOW feasibility, not estimated (see feasibility table).