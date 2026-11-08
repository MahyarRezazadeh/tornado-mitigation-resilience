"""Print the key numbers from audit/results_numbers.json (for writing and auditing the text)."""
import json
import pathlib
import sys

N = json.loads((pathlib.Path(__file__).resolve().parents[1] / "audit" / "results_numbers.json").read_text())
pref = tuple(sys.argv[1:]) or ("T2", "T3", "T4", "T5_")
for k, v in N.items():
    if k.startswith(pref) and isinstance(v, dict) and "b" in v:
        print(f"{k:58s} b={v['b']:8.3f} se={v['se']:6.3f} p={v['p']:.3f} N={v['N']} cl={v['clusters']} ref={v['ref_mean']}")
for k in ["govcounts", "fiscal_means", "state_shares", "deciles", "subapps", "fig2_raw", "drra_raw", "drra_N", "T5_loso"]:
    print(k, N.get(k))
