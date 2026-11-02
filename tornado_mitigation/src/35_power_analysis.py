"""Power analysis (Section 37): cluster-robust MDE from the primary specification.

MDE(power) = (z_{1-alpha/2} + z_power) * SE_cluster(beta). Classification (pre-registered):
WELL POWERED if MDE80 <= E*, MODERATELY POWERED if MDE80 <= 2 E*, else UNDERPOWERED,
where E* = 50% offset of the tornado main effect (or 0.05 SD if tornadoes are not disruptive).
Output: output/models/power.csv, output/tables/table11_power.md
"""
from __future__ import annotations

import pandas as pd
from scipy.stats import norm

from utils import MODELS, TABLES, get_logger, load_config

log = get_logger(__file__)


def main() -> None:
    cfg = load_config()["power"]
    pr = pd.read_csv(MODELS / "primary_results.csv")
    pr = pr[pr.status == "ok"].copy()
    za = norm.ppf(1 - cfg["alpha"] / 2)
    for pw in cfg["target_power"]:
        k = za + norm.ppf(pw)
        tag = int(pw * 100)
        pr[f"MDE{tag}"] = k * pr.se
        pr[f"MDE{tag}_pct_mean"] = 100 * pr[f"MDE{tag}"] / pr.y_mean.abs()
        pr[f"MDE{tag}_sd"] = pr[f"MDE{tag}"] / pr.y_sd
    pr["MDE80_over_Estar"] = pr.MDE80 / pr.E_star
    pr["power_rating"] = pd.cut(pr.MDE80_over_Estar, [-1, 1, 2, 1e12],
                                labels=["WELL POWERED", "MODERATELY POWERED", "UNDERPOWERED"]).astype(str)
    pr["tornado_effect_sd"] = pr.gamma_T / pr.y_sd
    cols = ["outcome_id", "outcome", "treated_counties", "treated_tornado_obs", "n_clusters", "se", "y_mean", "y_sd",
            "gamma_T", "tornado_effect_sd", "E_star", "MDE80", "MDE80_pct_mean", "MDE80_sd", "MDE90", "MDE90_pct_mean",
            "MDE90_sd", "MDE80_over_Estar", "power_rating"]
    pr[cols].to_csv(MODELS / "power.csv", index=False)
    (TABLES / "table11_power.md").write_text(
        "# Table 11. Power analysis (cluster-robust MDE, primary specification)\n\n"
        "E* = pre-registered economically meaningful effect (50% offset of the tornado main effect, or 0.05 SD "
        "when the tornado main effect is not disruptive).\n\n" + pr[cols].round(5).to_markdown(index=False),
        encoding="utf-8")
    log.info("\n%s", pr[["outcome", "MDE80", "E_star", "power_rating"]].to_string())


if __name__ == "__main__":
    main()
