"""Build references.bib (biblatex, APA style) from Crossref metadata for DOI-verified references,
plus hand-entered official documents/datasets whose URLs were checked separately.
Year = print-issue year (APA). Writes references.bib and audit/bib_metadata.csv."""
from __future__ import annotations

import csv
import html
import pathlib
import re
import time

import requests

HERE = pathlib.Path(__file__).resolve().parents[1]
UA = {"User-Agent": "refcheck/1.0 (mailto:refcheck@example.org)"}

DOIS = {
    "lindell2012padm": "10.1111/j.1539-6924.2011.01647.x",
    "bubeck2012review": "10.1111/j.1539-6924.2011.01783.x",
    "cutter2003sovi": "10.1111/1540-6237.8402002",
    "cutter2008place": "10.1016/j.gloenvcha.2008.07.013",
    "cutter2016urbanrural": "10.1080/24694452.2016.1194740",
    "burby2006katrina": "10.1177/0002716205284676",
    "rose2007bca": "10.1061/(ASCE)1527-6988(2007)8:4(97)",
    "godschalk2009foresight": "10.1080/09640560903083715",
    "healy2009myopic": "10.1017/S0003055409990104",
    "garrett2003political": "10.1093/ei/cbg023",
    "reeves2011political": "10.1017/S0022381611000843",
    "davlasheridze2017adaptation": "10.1016/j.jeem.2016.09.005",
    "simmons2006shelters": "10.1111/j.1539-6924.2006.00790.x",
    "merrell2005casualties": "10.3368/le.81.1.87",
    "ashley2007fatalities": "10.1175/2007WAF2007004.1",
    "gensini2018trends": "10.1038/s41612-018-0048-2",
    "sutter2010mobile": "10.1007/s11069-009-9416-x",
    "doswell2009ef": "10.1016/j.atmosres.2008.11.003",
    "seong2022naturally": "10.1080/10511482.2021.1938172",
    "collins2006redistributive": "10.1093/jopart/muj010",
    "collins2008taken": "10.1111/j.1540-6210.2008.00960.x",
    "hall2008grant": "10.1177/0275074007311385",
    "smith2020state": "10.3390/su122310013",
    "vila2022equity": "10.1016/j.envsci.2022.07.027",
    "smith2025rural": "10.1111/puar.70025",
    "lyles2014planners": "10.1080/09640568.2013.768973",
    "berke2014impacts": "10.1177/0739456X13517004",
    "brody2009policy": "10.1111/j.1539-6924.2009.01210.x",
    "brody2010identifying": "10.1007/s11069-009-9364-5",
    "frimpong2023federal": "10.1111/risa.14024",
    "noonan2018flood": "10.1111/risa.12853",
    "sadiq2015local": "10.1007/s11069-015-1776-9",
    "li2018flood": "10.3368/le.94.2.175",
    "landry2012participation": "10.1061/(ASCE)NH.1527-6996.0000073",
    "miao2025equity": "10.1111/risa.17660",
    "miao2025loss": "10.1111/risa.16111",
    "mach2019buyouts": "10.1126/sciadv.aax8995",
    "emrich2022distributive": "10.1016/j.ijdrr.2022.102855",
    "drakes2021social": "10.1016/j.ijdrr.2020.102010",
    "howell2019damages": "10.1093/socpro/spy016",
    "elliott2020racial": "10.1177/2378023120905439",
    "kahn2005death": "10.1162/0034653053970339",
    "deryugina2017fiscal": "10.1257/pol.20140296",
    "botzen2019economic": "10.1093/reep/rez004",
    "fothergill2004poverty": "10.1023/B:NHAZ.0000026792.76181.d9",
    "cutter2008temporal": "10.1073/pnas.0710375105",
    "tate2021flood": "10.1007/s11069-020-04470-2",
    "cameron2015practitioner": "10.3368/jhr.50.2.317",
    "abadie2023cluster": "10.1093/qje/qjac038",
    "roth2023trending": "10.1016/j.jeconom.2023.03.008",
    "best2025rent": "10.1111/risa.14224",
    "habets2025resilience": "10.1111/risa.17684",
    "kousky2014informing": "10.1016/j.eneco.2013.09.029",
    "sadiq2020participation": "10.1016/j.ijdrr.2020.101574",
    "posey2009determinants": "10.1016/j.gloenvcha.2009.06.003",
}
# print-issue years where Crossref 'issued' reflects online-first (checked against journal volume/issue)
YEAR_FIX = {"lindell2012padm": 2012, "frimpong2023federal": 2023, "noonan2018flood": 2018, "miao2025equity": 2025,
            "miao2025loss": 2025, "best2025rent": 2025, "habets2025resilience": 2025, "seong2022naturally": 2022,
            "lyles2014planners": 2014, "brody2010identifying": 2010, "sutter2010mobile": 2010, "howell2019damages": 2019,
            "abadie2023cluster": 2023, "smith2025rural": 2025}

# author lists corrected where Crossref metadata are incomplete or mis-split (checked against publisher records)
AUTHOR_FIX = {"collins2006redistributive": "Collins, Brian K. and Gerber, Brian J.",
              "healy2009myopic": "Healy, Andrew and Malhotra, Neil",
              "davlasheridze2017adaptation": "Davlasheridze, Meri and Fisher-Vanden, Karen and Klaiber, H. Allen",
              "cameron2015practitioner": "Cameron, A. Colin and Miller, Douglas L."}

MANUAL = r"""
@report{fema2015saferoomprecalc,
  author = {{Federal Emergency Management Agency}},
  title = {Safe Room Project Application Using Pre-Calculated Benefits},
  type = {Job aid},
  institution = {U.S. Department of Homeland Security},
  year = {2015},
  url = {https://www.fema.gov/sites/default/files/2020-09/fema_safe_room_project_application_using_precalculated_benefits_02-19-15.pdf}
}
@report{fema2024bcapolicy,
  author = {{Federal Emergency Management Agency}},
  title = {{FEMA} Policy 206-23-001: Benefit-Cost Analysis Discount Rate and Streamlined Cost-Effectiveness Analysis Approaches},
  institution = {U.S. Department of Homeland Security},
  year = {2024},
  url = {https://www.fema.gov/sites/default/files/documents/fema_policy-206-23-001-bca-discount-rate-and-streamlined-approaches_april-24-2024.pdf}
}
@online{fema1215mgmtcosts,
  author = {{Federal Emergency Management Agency}},
  title = {Section 1215: Management Costs},
  year = {2023},
  url = {https://www.fema.gov/assistance/public/policy-guidance-fact-sheets/section-1215-management-costs},
  urldate = {2026-10-09}
}
@online{openfema2026,
  author = {{Federal Emergency Management Agency}},
  title = {{OpenFEMA} Data Sets: Hazard Mitigation Assistance Projects (v4), {HMA} Subapplications (v2), and Disaster Declarations Summaries},
  year = {2026},
  url = {https://www.fema.gov/about/openfema/data-sets},
  urldate = {2026-10-07}
}
@online{spc2025database,
  author = {{NOAA Storm Prediction Center}},
  title = {Severe Weather Database Files (1950--2024): Tornadoes},
  year = {2025},
  url = {https://www.spc.noaa.gov/wcm/},
  urldate = {2026-10-09}
}
@online{census2017cog,
  author = {{U.S. Census Bureau}},
  title = {2017 {Census of Governments}: Government Units Listing and Individual Unit Finance File},
  year = {2019},
  url = {https://www.census.gov/programs-surveys/cog.html},
  urldate = {2026-10-09}
}
@report{horn2022crs,
  author = {Horn, Diane P.},
  title = {{FEMA} Hazard Mitigation: A First Step Toward Climate Adaptation},
  type = {CRS Report},
  number = {R46989},
  institution = {Congressional Research Service},
  year = {2022},
  url = {https://www.congress.gov/crs-product/R46989}
}
@online{headwaters_nd,
  author = {Smith, Kris},
  title = {Mountain, Midwest, and {Gulf} States Fail to Secure {FEMA} Resilience Funding},
  organization = {Headwaters Economics},
  url = {https://headwaterseconomics.org/natural-hazards/bric-funding/},
  urldate = {2026-10-09}
}
@misc{drra2018,
  author = {{U.S. Congress}},
  title = {Disaster Recovery Reform Act of 2018},
  howpublished = {Division D of the FAA Reauthorization Act of 2018, Pub. L. No. 115-254},
  year = {2018}
}
@software{pyfixest,
  author = {Fischer, Alexander and Sch{\"a}r, Styfen},
  title = {{PyFixest}: Fast High-Dimensional Fixed Effects Regression in {Python}},
  year = {2024},
  url = {https://github.com/py-econometrics/pyfixest}
}
"""


def clean(s):
    s = html.unescape(re.sub(r"<[^>]+>.*?</[^>]+>|<[^>]+>", "", s or ""))
    return " ".join(s.split())


def protect(title):
    # protect capitals of acronyms / proper nouns for APA sentence casing
    return re.sub(r"\b([A-Z]{2,}[A-Za-z]*|United States|U\.S\.|US|Florida|Texas|North Carolina|Gulf|Katrina|FEMA|NFIP|Fujita|USA)\b",
                  lambda m: "{" + m.group(1) + "}", title)


def main():
    out, meta = [], []
    for key, doi in DOIS.items():
        m = requests.get(f"https://api.crossref.org/works/{doi}", headers=UA, timeout=60).json()["message"]
        authors = AUTHOR_FIX.get(key) or " and ".join(f"{clean(a.get('family'))}, {clean(a.get('given', ''))}".strip(", ")
                               for a in m.get("author", []))
        dp = (m.get("published-print") or m.get("journal-issue", {}).get("published-print") or m.get("issued"))["date-parts"][0]
        year = YEAR_FIX.get(key, dp[0])
        jt = clean((m.get("container-title") or [""])[0]).replace("&amp;", "\\&").replace("&", "\\&")
        title = protect(clean((m.get("title") or [""])[0]))
        title = re.sub(r"(\?\s+)([A-Za-z])", r"\1{\2}", title)   # keep capital after a question mark (APA)
        f = {"author": authors, "title": title, "journaltitle": jt, "year": str(year), "volume": m.get("volume"),
             "number": m.get("issue"), "pages": (m.get("page") or "").replace("-", "--") or None,
             "eid": m.get("article-number"), "doi": m.get("DOI")}
        if not f["pages"] and f["eid"]:
            f["pages"] = None
        body = ",\n".join(f"  {k} = {{{v}}}" for k, v in f.items() if v)
        out.append(f"@article{{{key},\n{body}\n}}")
        meta.append({"key": key, "doi": doi, "year": year, "journal": jt, "first_author": authors.split(",")[0],
                     "title": clean((m.get('title') or [''])[0])})
        time.sleep(0.2)
    (HERE / "references.bib").write_text("% Generated by scripts/build_bib.py from Crossref (DOI-verified) + manual official sources\n\n"
                                         + "\n\n".join(out) + "\n" + MANUAL, encoding="utf-8")
    with open(HERE / "audit" / "bib_metadata.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(meta[0]))
        w.writeheader()
        w.writerows(meta)
    print("entries:", len(out), "+ manual")


if __name__ == "__main__":
    main()




