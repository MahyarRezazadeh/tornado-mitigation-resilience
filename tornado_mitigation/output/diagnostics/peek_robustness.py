"""Quick review helper: sign/significance summary of robustness grids by category (read-only)."""
import pandas as pd
from pathlib import Path

M = Path(__file__).resolve().parents[1] / "models"
pd.set_option("display.width", 220)
for v in ["separation_rate", "log_employment", "log_earnings", "establishment_death_rate", "job_destruction_rate",
          "hire_rate", "log_establishments", "outmigration_rate", "small_estab_death_rate", "ihs_units"]:
    d = pd.read_csv(M / f"robustness_{v}.csv")
    d = d[d.status == "ok"]
    b0 = d.loc[d.specification_id == "R00", "beta"].iloc[0]
    p0 = d.loc[d.specification_id == "R00", "p"].iloc[0]
    c = d[(d.credible_specification == 1) & (d.specification_id != "R00")]
    print(f"\n{v}: primary b={b0:.4g} p={p0:.3f} | same-sign {((c.beta > 0) == (b0 > 0)).mean():.2f} | "
          f"p<.10 same-sign {(((c.beta > 0) == (b0 > 0)) & (c.p < .1)).mean():.2f} | p<.10 opposite {(((c.beta > 0) != (b0 > 0)) & (c.p < .1)).sum()}")
    sig = c[c.p < 0.10][["specification_id", "description", "beta", "p"]]
    if len(sig):
        print(sig.round(4).to_string(index=False))
