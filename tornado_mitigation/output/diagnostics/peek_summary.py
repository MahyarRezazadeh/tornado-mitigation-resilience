"""Review helper: compact print of the key evidence used to write analyst_notes.md (read-only)."""
import pandas as pd
from pathlib import Path

O = Path(__file__).resolve().parents[1]
M = O / "models"
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
rm = pd.read_csv(M / "robustness_metrics.csv")
print(rm[["outcome", "primary_beta", "bh_q", "sign_consistency", "sig_consistency", "pretrend_p", "placebo_p", "ri_p",
          "leave_state_out_sign_share", "treatment_definition_pass", "timing_pass", "hazard_definition_pass",
          "matching_pass", "estimator_pass", "driving_states", "robustness_rating", "main_result"]].round(3).to_string())
print(rm[["outcome", "beta_without_OK", "p_without_OK", "beta_without_TX", "p_without_TX", "stacked_beta", "stacked_p",
          "iw_beta", "iw_p", "stacked_es_pretrend_p"]].round(4).to_string())
pr = pd.read_csv(M / "primary_results.csv")
print(pr[["outcome", "beta", "se", "p", "ci_low", "ci_high", "gamma_T", "gamma_T_se", "E_star", "y_sd_within",
          "effect_pct_mean", "treated_tornado_obs"]].round(5).to_string())
print(pd.read_csv(M / "event_study_summary.csv").round(3).to_string())
print(pd.read_csv(M / "estimator_comparison.csv").round(4).to_string())
print(pd.read_csv(O / "diagnostics" / "qe_applicant_control_estimates.csv").round(4).to_string())
print(pd.read_csv(M / "severity_gradient.csv").round(4).to_string())
pl = pd.read_csv(M / "placebo_results.csv")
print(pl[["outcome", "specification_id", "beta", "se", "p", "primary_beta"]].round(4).to_string())
print(pd.read_csv(M / "resilience_indices.csv")[["index", "beta", "se", "p", "bh_q"]].round(4).to_string())
print(pd.read_csv(M / "recovery_metrics.csv").round(4).to_string())
