"""Word counts for the Risk Analysis limits: abstract (<=250) and main text (<7,000; excludes references, tables, figures)."""
import pathlib
import re

tex = (pathlib.Path(__file__).resolve().parents[1] / "risk_analysis_manuscript.tex").read_text(encoding="utf-8")


def plain(s):
    s = re.sub(r"(?<!\\)%.*", "", s)
    s = re.sub(r"\\begin\{equation\}.*?\\end\{equation\}", " ", s, flags=re.S)
    s = re.sub(r"\\(parencite|textcite|ref|label|eqref|cite)\{[^}]*\}", " CIT ", s)
    s = re.sub(r"\\[a-zA-Z]+\*?(\[[^]]*\])?", " ", s)
    s = re.sub(r"[{}$~\\]", " ", s)
    return [w for w in s.split() if re.search(r"[A-Za-z0-9]", w)]


ab = tex.split(r"\textbf{Abstract}")[1].split(r"\textbf{Keywords:}")[0]
main = tex.split(r"\section{Introduction}")[1].split(r"\section*{Data Availability Statement}")[0]
a, m = plain(ab), plain(main)
cit = sum(1 for w in m if w == "CIT")
print(f"abstract words: {len(a)}")
print(f"main text words (incl. in-text citation placeholders counted once each): {len(m)}; without citation tokens: {len(m) - cit}")
