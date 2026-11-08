"""Keep only entries cited in the manuscript/appendix (run after build_bib.py)."""
import pathlib
import re

MS = pathlib.Path(__file__).resolve().parents[1]
txt = (MS / "risk_analysis_manuscript.tex").read_text(encoding="utf-8") + (MS / "appendix" / "supplementary_material.tex").read_text(encoding="utf-8")
cited = {k.strip() for g in re.findall(r"\\(?:parencite|textcite|cite)\{([^}]*)\}", txt) for k in g.split(",")}
bib = (MS / "references.bib").read_text(encoding="utf-8")
entries = re.split(r"\n(?=@)", bib)
head = [e for e in entries if not e.lstrip().startswith("@")]
keep = [e for e in entries if e.lstrip().startswith("@") and re.match(r"\s*@\w+\{([^,]+),", e).group(1) in cited]
drop = [re.match(r"\s*@\w+\{([^,]+),", e).group(1) for e in entries if e.lstrip().startswith("@") and e not in keep]
(MS / "references.bib").write_text("\n".join(head + keep).strip() + "\n", encoding="utf-8")
print("kept", len(keep), "dropped", drop)
