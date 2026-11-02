"""Re-wrap the source manuscript's table files in threeparttable layout.

Only the float wrapper, font size, and note environment change; every row of
the tabular body is copied verbatim so that no reported value can change.
"""
import re
import sys
from pathlib import Path

src = Path(sys.argv[1])   # source_snapshot dir
dst = Path(sys.argv[2])   # project root

jobs = {
    "table_1.tex": ("tables/table1.tex", r"\small", None),
    "table_2.tex": ("tables/table2.tex", r"\small", None),
    "table_3.tex": ("tables/table3.tex", r"\footnotesize", None),
    "table_4.tex": ("tables/table4.tex", r"\footnotesize", None),
    "table_5.tex": ("tables/table5.tex", r"\footnotesize", None),
    "table_A1_controls.tex": ("appendix/tableS1.tex", r"\footnotesize", None),
    "table_A2_deciles.tex": ("appendix/tableS2.tex", r"\small", None),
}

for name, (out, size, _) in jobs.items():
    t = (src / name).read_text(encoding="utf-8")
    cap = re.search(r"\\caption\{(.*?)\}\n", t).group(1)
    lab = re.search(r"\\label\{(.*?)\}", t).group(1)
    tab = re.search(r"(\\begin\{tabular\}.*?\\end\{tabular\})", t, re.S).group(1)
    tail = t[t.index(r"\end{tabular}"):]
    note = re.search(r"\\scriptsize\n(.*?)\n\\end\{minipage\}", tail, re.S).group(1).strip()
    note = note.replace(r"\textit{Note:}", r"\textit{Notes:}")
    # Table 4 and 5: shrink the fixed-width label column slightly so the table fits the text block
    tab = tab.replace(r"p{0.47\linewidth}", r">{\raggedright\arraybackslash}p{0.42\linewidth}")
    tab = tab.replace(r"p{0.40\linewidth}", r">{\raggedright\arraybackslash}p{0.27\linewidth}")
    # Table 5 header: stack the long column labels (wording unchanged)
    tab = tab.replace(r" & Funded HMGP project & Funded safe room/retrofit & Safe room/retrofit, 3 yrs & $N$ \\",
                      r" & \shortstack{Funded\\HMGP project} & \shortstack{Funded safe\\room/retrofit} & \shortstack{Safe room/\\retrofit, 3 yrs} & $N$ \\")
    adjust = name in ("table_5.tex", "table_A1_controls.tex", "table_3.tex")
    body = tab if not adjust else "\\setlength{\\tabcolsep}{3.5pt}\n" + tab
    out_t = (
        "\\begin{table}[!htbp]\n\\centering\n" + size + "\n"
        "\\begin{threeparttable}\n"
        f"\\caption{{{cap}}}\n\\label{{{lab}}}\n"
        + body + "\n"
        "\\begin{tablenotes}[flushleft]\n\\footnotesize\n\\item " + note + "\n\\end{tablenotes}\n"
        "\\end{threeparttable}\n\\end{table}\n"
    )
    (dst / out).write_text(out_t, encoding="utf-8")
    print("wrote", out)

