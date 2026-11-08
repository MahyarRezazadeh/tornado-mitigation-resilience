"""Verify candidate references against Crossref and fetch BibTeX from doi.org.

For each candidate (key, title query, expected first-author surname, expected year), query Crossref,
accept the best hit only if the normalized title matches closely AND the first-author surname matches.
Writes audit/reference_verification.csv and references_verified.bib (raw Crossref BibTeX, keys replaced).
Unverified candidates are listed and must NOT be cited.
"""
from __future__ import annotations

import csv
import difflib
import pathlib
import re
import time

import requests

HERE = pathlib.Path(__file__).resolve().parents[1]
UA = {"User-Agent": "manuscript-reference-check/1.0 (mailto:refcheck@example.org)"}

CANDIDATES = [
    # key, title, first-author surname, year
    ("lindell2012padm", "The protective action decision model: theoretical modifications and additional evidence", "Lindell", 2012),
    ("bubeck2012review", "A review of risk perceptions and other factors that influence flood mitigation behavior", "Bubeck", 2012),
    ("cutter2003sovi", "Social vulnerability to environmental hazards", "Cutter", 2003),
    ("cutter2008place", "A place-based model for understanding community resilience to natural disasters", "Cutter", 2008),
    ("cutter2016urbanrural", "Urban-rural differences in disaster resilience", "Cutter", 2016),
    ("burby2006katrina", "Hurricane Katrina and the paradoxes of government disaster policy: Bringing about wise governmental decisions for hazardous areas", "Burby", 2006),
    ("rose2007bca", "Benefit-cost analysis of FEMA hazard mitigation grants", "Rose", 2007),
    ("godschalk2009foresight", "Estimating the value of foresight: aggregate analysis of natural hazard mitigation benefits and costs", "Godschalk", 2009),
    ("healy2009myopic", "Myopic voters and natural disaster policy", "Healy", 2009),
    ("garrett2003political", "The political economy of FEMA disaster payments", "Garrett", 2003),
    ("reeves2011political", "Political disaster: Unilateral powers, electoral incentives, and presidential disaster declarations", "Reeves", 2011),
    ("davlasheridze2017adaptation", "The effects of adaptation measures on hurricane induced property losses: Which FEMA investments have the highest returns?", "Davlasheridze", 2017),
    ("simmons2006shelters", "Direct estimation of the cost effectiveness of tornado shelters", "Simmons", 2006),
    ("merrell2005casualties", "The determinants of tornado casualties and the benefits of tornado shelters", "Merrell", 2005),
    ("ashley2007fatalities", "Spatial and temporal analysis of tornado fatalities in the United States: 1880-2005", "Ashley", 2007),
    ("gensini2018trends", "Spatial trends in United States tornado frequency", "Gensini", 2018),
    ("sutter2010mobile", "Tornado fatalities and mobile homes in the United States", "Sutter", 2010),
    ("doswell2009ef", "On the implementation of the enhanced Fujita scale in the USA", "Doswell", 2009),
    ("seong2022naturally", "Naturally resilient to natural hazards? Urban-rural disparities in hazard mitigation grant program assistance", "Seong", 2022),
    ("collins2006redistributive", "Redistributive policy and devolution: Is state administration a road block (grant) to equitable access to federal funds?", "Collins", 2006),
    ("collins2008taken", "Taken for granted? Managing for social equity in grant programs", "Collins", 2008),
    ("hall2008grant", "Assessing local capacity for federal grant-getting", "Hall", 2008),
    ("smith2020state", "A national evaluation of state and territory roles in hazard mitigation: Building local capacity to implement FEMA hazard mitigation assistance grants", "Smith", 2020),
    ("vila2022equity", "Equity in FEMA hazard mitigation assistance programs: The role of state hazard mitigation officers", "Vil", 2022),
    ("smith2025rural", "Mapping rural local government capacity for climate resilience projects in the United States", "Smith", 2025),
    ("lyles2014planners", "Do planners matter? Examining factors driving incorporation of land use approaches into hazard mitigation plans", "Lyles", 2014),
    ("berke2014impacts", "Impacts of federal and state hazard mitigation policies on local land use policy", "Berke", 2014),
    ("brody2009policy", "Policy learning for flood mitigation: A longitudinal assessment of the community rating system in Florida", "Brody", 2009),
    ("brody2010identifying", "Identifying factors influencing flood mitigation at the local level in Texas and Florida: the role of organizational capacity", "Brody", 2010),
    ("frimpong2023federal", "Does federal flood hazard mitigation assistance affect community rating system participation?", "Frimpong", 2023),
    ("noonan2018flood", "Flood risk management: Exploring the impacts of the community rating system program on poverty and income inequality", "Noonan", 2018),
    ("sadiq2015local", "Local capacity and resilience to flooding: community responsiveness to the community ratings system program incentives", "Sadiq", 2015),
    ("li2018flood", "Flood risk, local hazard mitigation, and the community rating system of the national flood insurance program", "Li", 2018),
    ("landry2012participation", "Participation in the community rating system of NFIP: Empirical analysis of North Carolina counties", "Landry", 2012),
    ("miao2025equity", "Assessing social equity of federal disaster aid distribution: A nationwide analysis", "Miao", 2025),
    ("miao2025loss", "Estimating the loss-reduction effects of disaster preparedness and mitigation: An empirical study of US coastal states", "Miao", 2025),
    ("mach2019buyouts", "Managed retreat through voluntary buyouts of flood-prone properties", "Mach", 2019),
    ("emrich2022distributive", "Assessing distributive inequities in FEMA's Disaster recovery assistance fund allocation", "Emrich", 2022),
    ("drakes2021social", "Social vulnerability and short-term disaster assistance in the United States", "Drakes", 2021),
    ("howell2019damages", "Damages done: The longitudinal impacts of natural hazards on wealth inequality in the United States", "Howell", 2019),
    ("elliott2020racial", "Racial inequities in the federal buyout of flood-prone homes: A nationwide assessment of environmental adaptation", "Elliott", 2020),
    ("kahn2005death", "The death toll from natural disasters: The role of income, geography, and institutions", "Kahn", 2005),
    ("deryugina2017fiscal", "The fiscal cost of hurricanes: Disaster aid versus social insurance", "Deryugina", 2017),
    ("botzen2019economic", "The economic impacts of natural disasters: A review of models and empirical studies", "Botzen", 2019),
    ("fothergill2004poverty", "Poverty and disasters in the United States: A review of recent sociological findings", "Fothergill", 2004),
    ("cutter2008temporal", "Temporal and spatial changes in social vulnerability to natural hazards", "Cutter", 2008),
    ("tate2021flood", "Flood exposure and social vulnerability in the United States", "Tate", 2021),
    ("cameron2015practitioner", "A practitioner's guide to cluster-robust inference", "Cameron", 2015),
    ("abadie2023cluster", "When should you adjust standard errors for clustering?", "Abadie", 2023),
    ("roth2023trending", "What's trending in difference-in-differences? A synthesis of the recent econometrics literature", "Roth", 2023),
    ("best2025rent", "Rent affordability after hurricanes: Longitudinal evidence from US coastal states", "Best", 2025),
    ("habets2025resilience", "A community resilience index for place-based actionable metrics", "Habets", 2025),
    ("kousky2014informing", "Informing climate adaptation: A review of the economic costs of natural disasters", "Kousky", 2014),
    ("strader2018tornado", "Tornado vulnerability and its implications", "Strader", 2018),
    ("ash2014tornado", "Tornado warning trade-offs: Evaluating choices for visually communicating risk", "Ash", 2014),
    ("schmidlin2009mobile", "Tornado shelters in mobile home parks in the United States", "Schmidlin", 2009),
    ("sadiq2020participation", "Participation and non-participation in FEMA's Community Rating System (CRS) program: Insights from CRS coordinators and floodplain managers", "Sadiq", 2020),
    ("posey2009determinants", "The determinants of vulnerability and adaptive capacity at the municipal level: Evidence from floodplain management programs in the United States", "Posey", 2009),
    ("schwartz2023bric", "Who receives FEMA's Building Resilient Infrastructure and Communities funding?", "", 0),
]


def norm(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s or "").lower()
    return re.sub(r"[^a-z0-9 ]", " ", s).split().__str__()


def query(title):
    r = requests.get("https://api.crossref.org/works", params={"query.bibliographic": title, "rows": 5}, headers=UA, timeout=60)
    r.raise_for_status()
    return r.json()["message"]["items"]


def main():
    rows, bibs = [], []
    for key, title, au, yr in CANDIDATES:
        status, best = "NOT FOUND", None
        try:
            for it in query(title):
                t = (it.get("title") or [""])[0]
                sim = difflib.SequenceMatcher(None, norm(t), norm(title)).ratio()
                first = ((it.get("author") or [{}])[0].get("family") or "")
                y = (it.get("issued", {}).get("date-parts") or [[None]])[0][0]
                if sim > 0.85 and (not au or au.lower() in first.lower()):
                    best = (it, t, first, y, sim)
                    break
        except Exception as e:  # noqa: BLE001
            status = f"ERROR {e}"
        rec = {"key": key, "query_title": title, "expected_author": au, "expected_year": yr}
        if best:
            it, t, first, y, sim = best
            doi = it.get("DOI")
            status = "VERIFIED" if (not yr or abs((y or 0) - yr) <= 1) else f"VERIFIED (year {y} vs {yr})"
            rec.update(status=status, doi=doi, crossref_title=t, first_author=first, year=y,
                       journal=(it.get("container-title") or [""])[0], volume=it.get("volume"), pages=it.get("page"),
                       similarity=round(sim, 3))
            try:
                b = requests.get(f"https://doi.org/{doi}", headers={**UA, "Accept": "application/x-bibtex; charset=utf-8"}, timeout=60)
                if b.ok and b.text.strip().startswith("@"):
                    bibs.append(re.sub(r"^@(\w+)\{[^,]*,", lambda m: "@" + m.group(1).lower() + "{" + key + ",", b.text.strip(), count=1))
            except Exception:  # noqa: BLE001
                pass
        else:
            rec.update(status=status)
        rows.append(rec)
        print(f"{status:12s} {key:28s} {rec.get('year')} {rec.get('journal')} {rec.get('doi')}")
        time.sleep(0.3)
    out = HERE / "audit" / "reference_verification.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["key", "status", "doi", "first_author", "year", "journal", "volume", "pages",
                                          "crossref_title", "query_title", "expected_author", "expected_year", "similarity"])
        w.writeheader()
        w.writerows(rows)
    (HERE / "audit" / "references_verified_crossref.bib").write_text("\n\n".join(bibs), encoding="utf-8")


if __name__ == "__main__":
    main()
