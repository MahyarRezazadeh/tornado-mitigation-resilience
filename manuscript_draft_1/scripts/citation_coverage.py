"""Citation coverage: cited keys vs references.bib; where each key is cited (section)."""
import pathlib
import re

MS = pathlib.Path(__file__).resolve().parents[1]
tex = (MS / "risk_analysis_manuscript.tex").read_text(encoding="utf-8")
app = (MS / "appendix" / "supplementary_material.tex").read_text(encoding="utf-8")
bib = set(re.findall(r"@\w+\{([^,]+),", (MS / "references.bib").read_text(encoding="utf-8")))
where = {}
section = "front"
for line in (tex + "\n" + app).splitlines():
    m = re.match(r"\\(sub)*section\*?\{([^}]*)\}", line.strip())
    if m:
        section = m.group(2)
    for grp in re.findall(r"\\(?:parencite|textcite|cite)\{([^}]*)\}", line):
        for k in grp.split(","):
            where.setdefault(k.strip(), []).append(section)
cited = set(where)
print("cited keys:", len(cited), "| bib entries:", len(bib))
print("cited but missing from bib:", sorted(cited - bib))
print("in bib but not cited:", sorted(bib - cited))
for k in sorted(cited):
    print(f"{k:28s} {len(where[k]):2d}x  {sorted(set(where[k]))}")
