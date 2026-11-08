# Literature Review and Novelty Assessment (Section 39)

## Search protocol

- 24 pre-specified phrases (Section 39) queried on 2026-10-07 in **OpenAlex** (25 results/query),
  **Crossref** (20/query) and **Semantic Scholar** (20/query). OpenAlex and Crossref index NBER, IZA, SSRN
  and most journal/working-paper DOIs. **Google Scholar, SSRN search and RePEc/IDEAS have no open API and
  were not queried directly**, so coverage of non-DOI working papers is incomplete.
- 1,100+ raw hits, 852 unique titles. A transparent keyword screen classified records as
  (3) mitigation x hazard x economic outcome (138), (2) hazard x economic outcome (90), (1) mitigation x hazard
  only, (0) irrelevant. All level-3 titles were read by hand.
- 15 known closely related papers were checked against Crossref by title (similarity >= 0.85).
  14 were verified; *Healy & Malhotra (2009, APSR)* failed only because of a Crossref API error and is cited
  from domain knowledge. See `literature_overlap.csv` for fields (treatment, hazard, geography, outcome,
  identification, result, overlap).

## What exists

1. **FEMA mitigation and hazard losses (closest).** Davlasheridze, Fisher-Vanden & Klaiber (2017, *JEEM*) show
   FEMA mitigation spending reduces subsequent *hurricane property losses* across coastal counties; Healy &
   Malhotra (2009, *APSR*) estimate large returns to preparedness spending in damages; Rose et al. (2007,
   *Natural Hazards Review*) give engineering benefit-cost ratios for FEMA grants. None studies labor-market or
   business-dynamics outcomes, and none focuses on tornado/wind mitigation.
2. **Tornado shelters and life safety.** Merrell, Simmons & Sutter (2005, *Land Economics*) and related
   Simmons-Sutter work value shelters via avoided casualties, mainly for mobile homes.
3. **Disasters and local economies (no mitigation).** Groen, Kutzbach & Polivka (2020, *JOLE*), Basker &
   Miranda (2018, *JEG*), Boustan et al. (2020, *JUE*), Deryugina (2017, *AEJ:Policy*), Strobl (2011, *REStat*),
   Xiao (2011, *JRS*), Ewing, Kruse & Thompson (2009, *Applied Economics*, Oklahoma City tornado employment), and a
   2020 *Demography* paper on severe tornadoes and demographic change.
4. **Post-disaster aid, not ex-ante mitigation.** Davlasheridze & Geylani (2017, *Small Business Economics*, SBA
   loans), a 2022 *JAERE* paper on federal disaster assistance and business survival, Gallagher & Hartley
   (Katrina household finance).
5. **Adjacent mitigation evaluations with non-causal or non-economic designs.** Wind-retrofit simulation of
   community resilience metrics (*Journal of Infrastructure Systems*, 2021); HMA and flood-related migration
   (*Urban Climate*, 2022); wind-mitigation capitalization into house prices (Simmons, Kruse & Smith 2002, *SEJ*);
   CRS flood mitigation and location choice (*Risk Analysis*).

## Novelty classification

| Outcome domain | Classification | Reason |
|---|---|---|
| Worker separations, employment, earnings, hires (QWI) | **HIGH** | I found no close causal study in the searched economics/public-policy literature estimating FEMA tornado/wind mitigation x subsequent tornado effects on labor-market flows. |
| Establishment deaths, job destruction, business formation (BDS/CBP) | **HIGH** | Disaster-business literature exists (Basker & Miranda; SBA loans), but no study links ex-ante wind mitigation to business dynamics after tornadoes. |
| Migration, building permits | **MEDIUM** | Disaster-migration literature is substantial (Boustan et al.; tornado demography paper); a flood-focused HMA-migration paper exists. |
| Property damage / casualties (mechanism) | **MEDIUM** | Davlasheridze et al. (2017) estimate the hurricane analogue for damages; shelter-casualty literature exists. |

Preferred wording for any paper: *"I found no close causal study in the searched economics/public-policy
literature"*. A "never studied" claim is not supported, because Google Scholar, SSRN and RePEc were not
searched by API.
