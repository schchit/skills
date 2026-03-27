---
name: openclaw-r-stats
description: >
  82 statistical analysis methods in R — regression, survival, Bayesian,
  meta-analysis, causal inference, SEM, IRT, clinical trial design, and more.
  JSON spec driven, reproducible, with mandatory effect sizes and assumption checks.
  Use when the user asks for any statistical analysis, hypothesis testing,
  or mentions R packages like ggplot2, brms, survival, metafor, lavaan, glmnet.
  支持中文：回归、检验、生存分析、贝叶斯、元分析、因果推断、SEM、IRT 等。
version: 0.7.0
metadata:
  openclaw:
    emoji: "📊"
    requires:
      bins:
        - Rscript
        - bash
---

# OpenClaw R Stats

## When to use
- User asks for statistical analysis, regression, hypothesis testing
- User asks to compare groups, test significance, find associations
- User mentions ANOVA, t-test, chi-square, correlation
- User asks for time series forecasting or trend analysis
- User uploads CSV and wants statistical insights
- User asks "is this significant?" or "what predicts X?"
- 用户用中文提到：回归、检验、预测、显著性、描述统计

## What this skill does NOT do
- Do not claim causality from observational data. Use "associated with".
- Do not run large exploratory fishing without clear user intent.
- Do not silently ignore assumption violations.
- Do not execute arbitrary inline R code. Always use the wrapper script.
- Do not install packages during analysis. Installation is a separate step.
- Do not report only p-values. Always include effect sizes and CIs.

## Pre-flight checks (mandatory before any analysis)

1. Confirm the dataset file exists and is readable.
2. Run schema inspection:
    bash {baseDir}/scripts/run-rstats.sh schema --data <path-to-csv>
3. Report to the user: row/column count, types, missing values, unique counts.
4. If missing data > 5%, warn and ask how to handle.
5. If sample size < 30, warn about small sample limitations.
6. Only then proceed to build the analysis spec.

## Environment check

If first time or errors occur:
    bash {baseDir}/scripts/run-rstats.sh doctor

If packages missing, install the profile for the analysis needed:
    Rscript {baseDir}/scripts/install-core.R          # t-test, regression, ANOVA, etc.
    Rscript {baseDir}/scripts/install-survival.R      # KM, Cox, competing risks
    Rscript {baseDir}/scripts/install-missing.R       # MICE, MCAR test
    Rscript {baseDir}/scripts/install-mixed.R         # LMM, GLMM, GEE
    Rscript {baseDir}/scripts/install-bayes.R         # brms, Bayes factors
    Rscript {baseDir}/scripts/install-causal.R        # PSM, IPTW, IV, DiD, RDD, TMLE
    Rscript {baseDir}/scripts/install-meta.R          # meta-analysis, NMA
    Rscript {baseDir}/scripts/install-sem.R           # SEM, CFA, lavaan
    Rscript {baseDir}/scripts/install-diagnostic.R    # ROC, kappa, alpha
    Rscript {baseDir}/scripts/install-advanced.R      # GAM, quantile, zero-inflated
    Rscript {baseDir}/scripts/install-power.R         # power/sample size

If an analysis fails with "Package 'X' required", run the matching install script and retry.

## Spec field reference

See {baseDir}/docs/SPEC_REFERENCE.md for the complete list of required and optional fields for each analysis_type.

## Standard workflow

1. Determine the correct analysis type.
2. Inspect dataset schema and missingness.
3. Build a JSON analysis spec:
    {
      "dataset_path": "<path>",
      "analysis_type": "<type>",
      "outcome": "<column>",
      "predictors": ["<col1>","<col2>"],
      "formula": "<R formula>",
      "group_var": "<column or null>",
      "hypothesis": "<plain language>",
      "missing_strategy": "complete_case",
      "alpha": 0.05,
      "seed": 42,
      "output_dir": "<path>"
    }
4. Save the spec as a .json file.
5. Run: bash {baseDir}/scripts/run-rstats.sh analyze --spec <path>
6. Read summary.json and report.md from the output directory.
7. Present results: Summary → Statistics → Interpretation → Plots → Assumptions → Caveats.
8. Offer follow-up: diagnostics, alternative methods, export.

## Analysis selection

| User intent | analysis_type |
|---|---|
| Describe data / EDA | summary |
| Compare 2 groups (continuous) | ttest |
| Compare 2 groups (non-normal/small n) | wilcoxon |
| Compare 3+ groups (continuous, normal) | anova |
| Compare 3+ groups (non-normal/ordinal) | kruskal |
| Compare categorical variables | chisq |
| Categorical (small expected counts) | fisher |
| Paired categorical (before/after) | mcnemar |
| Repeated measures non-parametric | friedman |
| Association between 2 continuous vars | correlation |
| Predict continuous outcome | linear_regression |
| Predict binary outcome | logistic_regression |
| Predict count outcome | poisson_regression |
| Forecast time series | forecast_arima |
| Assess missing data patterns | missing_diagnostics |
| Impute missing values | multiple_imputation |
| Correct for multiple comparisons | p_adjust |
| Survival curves + median survival | kaplan_meier |
| Survival regression (HR) | cox_regression |
| Competing risks (Fine-Gray) | competing_risks |
| Time-dependent Cox model | cox_time_dependent |
| Restricted mean survival time | rmst |
| Odds ratio (case-control) | odds_ratio |
| Risk ratio + NNT (cohort/RCT) | risk_ratio |
| Incidence rate ratio (person-time) | incidence_rate |
| Stratified analysis (confounding) | mantel_haenszel |
| Number needed to treat/harm | nnt |
| Linear mixed model (random effects) | lmm |
| Generalized linear mixed model | glmm |
| GEE marginal model | gee |
| Intraclass correlation | icc |
| Propensity score matching | propensity_match |
| Propensity score weighting (IPW) | propensity_weight |
| Causal mediation analysis | mediation_analysis |
| Instrumental variable regression | iv_regression |
| Difference-in-differences | did |
| Regression discontinuity | rdd |
| Bayesian regression (brms) | bayesian_regression |
| Bayes factors | bayes_factor |
| Generalized additive model (GAM) | gam |
| Quantile regression | quantile_regression |
| Robust regression (MM-estimation) | robust_regression |
| Zero-inflated Poisson/NegBin | zero_inflated |
| Ordinal logistic regression | ordinal_regression |
| Multinomial logistic regression | multinomial |
| Meta-analysis (forest/funnel) | meta_analysis |
| Meta-regression (moderators) | meta_regression |
| Subgroup meta-analysis | subgroup_meta |
| Network meta-analysis (NMA) | network_meta |
| Power / sample size (classical) | power_analysis |
| Survival sample size | power_survival |
| Mixed model power | power_mixed |
| SEM (structural equation model) | sem |
| CFA (confirmatory factor analysis) | cfa |
| Measurement invariance | measurement_invariance |
| Path analysis (indirect effects) | path_analysis |
| ROC / AUC with optimal cutpoint | roc_auc |
| Bland-Altman agreement | bland_altman |
| Inter-rater agreement (Kappa) | kappa |
| Cronbach's alpha (internal consistency) | cronbach_alpha |
| Doubly robust estimation (AIPW) | doubly_robust |
| Hurdle model (Poisson/NegBin) | hurdle |
| ETS forecasting | forecast_ets |
| LASSO / Ridge / Elastic Net | penalized_regression |
| Penalized Cox (high-dim survival) | penalized_cox |
| Adaptive LASSO | adaptive_lasso |
| Group LASSO | group_lasso |
| SCAD / MCP | ncvreg |
| Stability selection | stability_selection |
| TMLE (targeted MLE) | tmle |
| Causal forest / HTE | causal_forest |
| G-computation | g_computation |
| DAG analysis (adjustment sets) | dag_analysis |
| Joint model (longitudinal+survival) | joint_model |
| Multi-state model | multistate |
| Trajectory / latent class mixed | trajectory |
| IRT (item response theory) | irt |
| Latent class analysis | lca |
| Multilevel mediation | multilevel_mediation |
| Equivalence / non-inferiority power | power_equivalence |
| Cluster randomized trial power | power_cluster |
| Adaptive / group sequential design | adaptive_design |

## Automatic method switching guardrails

- Normality doubtful AND n < 30 → prefer wilcoxon over ttest
- Variance equality doubtful → use Welch t-test (equal_var: false)
- Expected cell counts < 5 → prefer fisher over chisq
- Overdispersion in Poisson → warn, suggest negative binomial
- Residuals heteroscedastic → warn about robust SE

## Reporting rules (non-negotiable)

Every analysis MUST include:
- Sample size (n) and missing data handling
- Method name and selection rationale
- Point estimates with confidence intervals
- Effect sizes (Cohen's d, η², R², OR, etc.)
- Assumption check results
- Warnings or limitations

Language rules:
- ✓ "associated with" / "evidence suggests" / "estimated effect"
- ✗ NEVER "causes" / "proves" / "definitively shows"

## Output artifacts (every run)

summary.json (status + findings), report.md (human-readable), schema.json, session_info.txt, executed_spec.json, tables/*.csv, figures/*.png

## Rules

- Use the wrapper script, not ad-hoc inline R code.
- Do not install packages during analysis. Use install scripts beforehand.
- Always use absolute paths for dataset_path when calling from outside the project directory.
- Always set a random seed for reproducibility.
- Support both English and Chinese (中文) queries.
