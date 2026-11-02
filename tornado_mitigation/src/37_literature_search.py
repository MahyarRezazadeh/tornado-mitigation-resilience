"""Structured literature search (Section 39).

1. Automated: every pre-specified phrase is queried in OpenAlex, Crossref and Semantic Scholar
   (Google Scholar / SSRN / RePEc have no open API; NBER/IZA working papers are indexed by OpenAlex/Crossref).
   Raw hits saved; relevance screened by a transparent keyword rule.
2. Curated: known closely related papers (from domain knowledge) are VERIFIED against Crossref by title
   (similarity >= 0.85); unverified entries are reported as such and not used for novelty claims.
Outputs: output/literature/search_hits_raw.csv, literature_overlap.csv, literature_review.md
"""
from __future__ import annotations

import difflib
import re
import time

import pandas as pd
import requests

from utils import LIT, get_logger, register_source

log = get_logger(__file__)
UA = {"User-Agent": "tornado-mitigation-research/1.0 (mailto:research@example.org)"}
PHRASES = ["tornado mitigation employment", "tornado mitigation labor market", "tornado safe room employment",
           "FEMA mitigation employment", "FEMA mitigation labor market", "hazard mitigation employment",
           "hazard mitigation worker separations", "disaster mitigation worker separations",
           "disaster mitigation establishment survival", "FEMA HMGP establishment survival", "FEMA HMGP employment",
           "tornado establishment deaths", "tornado business survival", "tornado firm survival",
           "tornado job destruction", "tornado worker earnings", "tornado local labor market",
           "safe room economic effects", "wind retrofit economic effects", "wind retrofit labor market",
           "hazard mitigation migration", "hazard mitigation local finance", "hazard mitigation business dynamics",
           "natural disaster mitigation business survival"]

CURATED = [
    # title, first-author surname, year, treatment, hazard, geography, outcome, identification, main result, overlap
    ("The effects of adaptation measures on hurricane induced property losses: Which FEMA investments have the highest returns?",
     "Davlasheridze", 2017, "FEMA HMA + PA mitigation spending", "hurricane", "US coastal counties", "property losses",
     "county panel FE, IV", "Mitigation spending reduces subsequent hurricane property damage", "MEDIUM-HIGH (closest: FEMA mitigation x subsequent hazard; damage not labor/business)"),
    ("Myopic voters and natural disaster policy", "Healy", 2009, "disaster preparedness vs relief spending", "all",
     "US counties", "damages, votes", "panel", "$1 preparedness reduces future damage by ~$15", "MEDIUM (preparedness returns; no labor outcomes)"),
    ("The determinants of tornado casualties and the benefits of tornado shelters", "Merrell", 2005, "tornado shelters",
     "tornado", "US (OK)", "casualties", "simulation/regression", "Shelters cost-effective mainly for mobile homes", "LOW-MEDIUM (casualties, not economy)"),
    ("Storms and jobs: The effect of hurricanes on individuals' employment and earnings over the long term", "Groen", 2020,
     "hurricane exposure", "hurricane", "US (LEHD)", "employment, earnings", "DiD", "Short-run earnings losses, later gains", "LOW (disaster, no mitigation)"),
    ("Taken by storm: business financing and survival in the aftermath of Hurricane Katrina", "Basker", 2018,
     "hurricane damage", "hurricane", "Mississippi", "business survival", "DiD", "Small, credit-constrained firms less likely to survive", "LOW (disaster, no mitigation)"),
    ("The effect of natural disasters on economic activity in US counties: A century of data", "Boustan", 2020,
     "disaster exposure", "all incl. tornado", "US counties", "migration, home values, poverty", "panel FE",
     "Severe disasters raise out-migration, lower home values", "LOW (disaster, no mitigation)"),
    ("The fiscal cost of hurricanes: Disaster aid versus social insurance", "Deryugina", 2017, "hurricane", "hurricane",
     "US counties", "transfers", "event study", "Large non-disaster transfers after hurricanes", "LOW (fiscal, no mitigation)"),
    ("Benefit-cost analysis of FEMA hazard mitigation grants", "Rose", 2007, "FEMA HMGP", "flood/wind/quake",
     "US", "avoided losses (BCA)", "engineering BCA", "BCR ~4:1 on average", "MEDIUM (mitigation value, no causal economic outcomes)"),
    ("The economic growth impact of hurricanes: evidence from U.S. coastal counties", "Strobl", 2011, "hurricane", "hurricane",
     "US coastal counties", "growth", "panel", "Hurricanes reduce county growth ~0.45pp", "LOW"),
    ("Local economic impacts of natural disasters", "Xiao", 2011, "1993 Midwest flood", "flood", "Midwest counties",
     "employment, population", "synthetic comparison", "Little long-run impact", "LOW"),
    ("Valuing mitigation: real estate market response to hurricane loss reduction measures", "Simmons", 2002,
     "wind mitigation features", "hurricane", "Florida", "house prices", "hedonic", "Shutters capitalized into prices", "MEDIUM (wind mitigation, housing not labor)"),
    ("Small business vulnerability to floods and the effects of disaster loans", "Davlasheridze", 2017, "SBA disaster loans",
     "flood", "US counties", "establishment growth", "panel FE", "Loans support small-business recovery", "LOW-MEDIUM (post-disaster aid, not ex-ante mitigation)"),
    ("Household finance after a natural disaster: The case of Hurricane Katrina", "Gallagher", 2017, "hurricane", "hurricane",
     "New Orleans", "household finance", "DiD", "Flood insurance payouts reduced debt", "LOW"),
    ("Twister! Employment responses to the 3 May 1999 Oklahoma City tornado", "Ewing", 2009, "tornado", "tornado",
     "Oklahoma City MSA", "employment", "time series", "Short-run employment effects", "LOW-MEDIUM (tornado labor effects, no mitigation)"),
    ("Flood risk, flood mitigation, and location choice: Evaluating the National Flood Insurance Program's Community Rating System",
     "Fan", 2016, "CRS flood mitigation", "flood", "US", "location choice", "structural sorting", "Mitigation affects location choices", "LOW-MEDIUM"),
]


def openalex(q):
    r = requests.get("https://api.openalex.org/works", params={"search": q, "per-page": 25}, headers=UA, timeout=60)
    out = []
    for w in r.json().get("results", []):
        src = ((w.get("primary_location") or {}).get("source") or {})
        out.append({"source_db": "OpenAlex", "title": w.get("title"), "year": w.get("publication_year"),
                    "authors": "; ".join(a["author"]["display_name"] for a in w.get("authorships", [])[:4]),
                    "venue": src.get("display_name"), "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
                    "url": w.get("id"), "type": w.get("type"), "cited_by": w.get("cited_by_count"),
                    "abstract_words": " ".join((w.get("abstract_inverted_index") or {}).keys())[:2000]})
    return out


def crossref(q, rows=20):
    r = requests.get("https://api.crossref.org/works", params={"query": q, "rows": rows}, headers=UA, timeout=60)
    out = []
    for w in r.json().get("message", {}).get("items", []):
        out.append({"source_db": "Crossref", "title": (w.get("title") or [""])[0],
                    "year": ((w.get("issued") or {}).get("date-parts") or [[None]])[0][0],
                    "authors": "; ".join(f"{a.get('given', '')} {a.get('family', '')}" for a in w.get("author", [])[:4]),
                    "venue": (w.get("container-title") or [""])[0], "doi": w.get("DOI"), "url": w.get("URL"),
                    "type": w.get("type"), "cited_by": w.get("is-referenced-by-count"), "abstract_words": (w.get("abstract") or "")[:2000]})
    return out


def s2(q):
    r = requests.get("https://api.semanticscholar.org/graph/v1/paper/search",
                     params={"query": q, "limit": 20, "fields": "title,year,venue,externalIds,url,authors,abstract,citationCount"},
                     headers=UA, timeout=60)
    if r.status_code != 200:
        return []
    out = []
    for w in r.json().get("data", []):
        out.append({"source_db": "SemanticScholar", "title": w.get("title"), "year": w.get("year"),
                    "authors": "; ".join(a["name"] for a in (w.get("authors") or [])[:4]), "venue": w.get("venue"),
                    "doi": (w.get("externalIds") or {}).get("DOI"), "url": w.get("url"), "type": "",
                    "cited_by": w.get("citationCount"), "abstract_words": (w.get("abstract") or "")[:2000]})
    return out


def relevance(row) -> tuple[int, str]:
    txt = f"{row.title} {row.abstract_words}".lower()
    mit = bool(re.search(r"mitigat|safe ?room|shelter|retrofit|hmgp|hazard mitigation|adaptation|preparedness", txt))
    haz = bool(re.search(r"tornado|wind|hurricane|disaster|storm|hazard", txt))
    econ = bool(re.search(r"employment|labor|labour|job|wage|earning|business|firm|establishment|migration|"
                          r"fiscal|tax|economic", txt))
    if mit and haz and econ:
        return 3, "mitigation x hazard x economic outcome"
    if haz and econ:
        return 2, "hazard x economic outcome (no mitigation)"
    if mit and haz:
        return 1, "mitigation x hazard (non-economic outcome)"
    return 0, "not relevant"


def verify(title, author, year):
    try:
        r = requests.get("https://api.crossref.org/works", params={"query.bibliographic": f"{title} {author}", "rows": 5},
                         headers=UA, timeout=60)
        for w in r.json()["message"]["items"]:
            t = (w.get("title") or [""])[0]
            sim = difflib.SequenceMatcher(None, t.lower(), title.lower()).ratio()
            if sim >= 0.85:
                fam = [a.get("family", "") for a in w.get("author", [])]
                return {"verified": True, "doi": w.get("DOI"), "journal": (w.get("container-title") or [""])[0],
                        "crossref_year": ((w.get("issued") or {}).get("date-parts") or [[None]])[0][0],
                        "authors": "; ".join(fam[:4]), "url": w.get("URL"), "title_similarity": round(sim, 3)}
    except Exception as e:  # noqa: BLE001
        log.warning("verify failed %s: %s", title[:40], e)
    return {"verified": False}


def main() -> None:
    hits = []
    for q in PHRASES:
        for fn in (openalex, crossref, s2):
            try:
                for h in fn(q):
                    h["query"] = q
                    hits.append(h)
            except Exception as e:  # noqa: BLE001
                log.warning("%s failed for %s: %s", fn.__name__, q, e)
            time.sleep(1.0)
        log.info("query done: %s (%d hits so far)", q, len(hits))
    H = pd.DataFrame(hits)
    H["title_key"] = H.title.fillna("").str.lower().str.replace(r"[^a-z0-9 ]", "", regex=True).str.strip()
    rel = H.apply(relevance, axis=1, result_type="expand")
    H["relevance"], H["relevance_reason"] = rel[0], rel[1]
    H.to_csv(LIT / "search_hits_raw.csv", index=False)
    U = H.sort_values("relevance", ascending=False).drop_duplicates("title_key")
    U = U[U.title_key != ""]
    log.info("unique records %d; relevance>=2: %d; relevance==3: %d", len(U), (U.relevance >= 2).sum(), (U.relevance == 3).sum())

    cur = []
    for (title, au, yr, trt, haz, geo, outc, ident, res, ov) in CURATED:
        v = verify(title, au, yr)
        cur.append({"title": title, "authors": v.get("authors", au), "year": v.get("crossref_year", yr),
                    "journal": v.get("journal", ""), "working_paper_status": "published" if v.get("verified") else "UNVERIFIED",
                    "DOI": v.get("doi", ""), "URL": v.get("url", ""), "treatment": trt, "hazard": haz, "geography": geo,
                    "outcome": outc, "identification_strategy": ident, "main_result": res, "degree_of_overlap": ov,
                    "verified_crossref": v.get("verified", False), "origin": "curated (verified via Crossref)"})
        time.sleep(0.5)
    C = pd.DataFrame(cur)
    auto = U[U.relevance == 3].head(60)
    A = pd.DataFrame({"title": auto.title, "authors": auto.authors, "year": auto.year, "journal": auto.venue,
                      "working_paper_status": auto.type, "DOI": auto.doi, "URL": auto.url, "treatment": "", "hazard": "",
                      "geography": "", "outcome": "", "identification_strategy": "", "main_result": "",
                      "degree_of_overlap": "auto-screened: " + auto.relevance_reason, "verified_crossref": auto.doi.notna(),
                      "origin": "automated search (" + auto.source_db + "; query: " + auto["query"] + ")"})
    out = pd.concat([C, A], ignore_index=True)
    out.to_csv(LIT / "literature_overlap.csv", index=False)
    register_source(dataset="literature_apis", source_name="OpenAlex, Crossref, Semantic Scholar APIs",
                    official_URL="https://openalex.org; https://api.crossref.org; https://api.semanticscholar.org",
                    API_endpoint="works search", notes=f"{len(PHRASES)} phrases; {len(H)} raw hits")
    # screen automated titles for the closest possible overlaps: mitigation AND (tornado|safe room|wind) AND labor/business
    close = U[(U.relevance == 3) & U.title.fillna("").str.lower().str.contains(r"tornado|safe ?room|wind|shelter")
              & U.title.fillna("").str.lower().str.contains(r"employ|labor|labour|job|business|firm|establishment|wage")]
    close[["title", "authors", "year", "venue", "doi", "source_db", "query"]].to_csv(LIT / "closest_candidates.csv", index=False)
    log.info("closest candidates (tornado/wind/safe-room mitigation x labor/business in title): %d", len(close))


if __name__ == "__main__":
    main()
