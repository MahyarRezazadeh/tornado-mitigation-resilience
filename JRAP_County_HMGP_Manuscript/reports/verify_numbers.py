"""Read-only consistency checks between the JRAP draft and the source manuscript.

1. Every numeric token in each revised table/appendix-table file equals, in order,
   the numeric tokens of the source table file.
2. Every number in the revised prose appears somewhere in the source manuscript
   (text, tables, appendix); numbers that do not are listed for review.
3. Every citation key resolves to references.bib and every bib entry is cited.
4. Word counts of the main text.
Run from the project root:  python reports/verify_numbers.py
"""
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
snap = root / "source_snapshot"
NUM = re.compile(r"(?<![A-Za-z\\])-?\d[\d,]*\.?\d*")


def nums(text):
    text = re.sub(r"\\label\{.*?\}|\\ref\{.*?\}|\\parencite\{.*?\}|\\textcite\{.*?\}", "", text)
    text = re.sub(r"\\(?:begin|end)\{.*?\}|\\cmidrule\(lr\)\{[\d-]+\}|p\{0\.\d+\\linewidth\}|\\tabcolsep\}\{[\d.]+pt\}"
                  r"|\{0\.\d+\\linewidth\}|\\vspace\{[\d.]+pt\}", "", text)  # layout lengths, not data
    return [t.rstrip(".,") for t in NUM.findall(text)]


print("== 1. Tables: numeric tokens, revised vs source")
pairs = [("table_1.tex", "tables/table1.tex"), ("table_2.tex", "tables/table2.tex"),
         ("table_3.tex", "tables/table3.tex"), ("table_4.tex", "tables/table4.tex"),
         ("table_5.tex", "tables/table5.tex"), ("table_A1_controls.tex", "appendix/tableS1.tex"),
         ("table_A2_deciles.tex", "appendix/tableS2.tex")]
for s, r in pairs:
    a = [x for x in nums((snap / s).read_text(encoding="utf-8")) if x]
    b = [x for x in nums((root / r).read_text(encoding="utf-8")) if x]
    status = "IDENTICAL" if a == b else "DIFFERENT"
    print(f"{r:24s} source {len(a):4d} tokens, revised {len(b):4d} tokens -> {status}")
    if a != b:
        import difflib
        for line in difflib.unified_diff(a, b, lineterm="", n=0):
            print("   ", line)

print("\n== 2. Numbers in revised prose not found in the source manuscript")
src_all = " ".join(p.read_text(encoding="utf-8") for p in snap.glob("*.tex"))
src_set = set(nums(src_all))
sections = sorted((root / "sections").glob("*.tex")) + [root / "appendix/supplementary.tex",
                                                         root / "figures/figures.tex"]
for f in sections:
    t = f.read_text(encoding="utf-8")
    t = "\n".join(l for l in t.splitlines() if not l.lstrip().startswith("%"))
    missing = sorted({x for x in nums(t) if x and x not in src_set})
    if missing:
        print(f"{f.relative_to(root)}: {missing}")

print("\n== 3. Citations")
bib = (root / "references.bib").read_text(encoding="utf-8")
keys = set(re.findall(r"@\w+\{([^,]+),", bib))
cited = set()
for f in list((root / "sections").glob("*.tex")) + [root / "appendix/supplementary.tex"]:
    for grp in re.findall(r"\\(?:paren|text)?cite\w*\{([^}]+)\}", f.read_text(encoding="utf-8")):
        cited.update(k.strip() for k in grp.split(","))
print("cited but missing from bib:", sorted(cited - keys) or "none")
print("in bib but never cited:   ", sorted(keys - cited) or "none")
print(f"{len(cited)} keys cited, {len(keys)} entries in bib")

print("\n== 4. Word counts (LaTeX commands stripped, approximate)")
def words(t):
    t = re.sub(r"%.*", "", t)
    t = re.sub(r"\\begin\{equation\}.*?\\end\{equation\}", " ", t, flags=re.S)
    t = re.sub(r"\\(?:paren|text)cite\{[^}]*\}", " CITE ", t)
    t = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?", " ", t)
    t = re.sub(r"[{}$~\\]", " ", t)
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'.,\-]*", t))
tot = 0
for f in sorted((root / "sections").glob("0[0-7]*.tex")):
    n = words(f.read_text(encoding="utf-8")); print(f"{f.name:32s} {n:5d}")
    if not f.name.startswith(("00", "07")):
        tot += n
print(f"main text (sections 1-6): {tot}")
