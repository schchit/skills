# 📊 Roadmap — openclaw-r-stats

> **Mission:** Build a comprehensive, opinionated statistical analysis toolkit that follows strict reporting standards and covers the methods used in biostatistics and medical research.

Every version follows the **Statistical Protocol** at the bottom of this document. No exceptions.

---

## v0.1 — Foundation (current)

Core parametric methods and the reproducible analysis pipeline.

| analysis_type | Method | R Packages |
|---|---|---|
| `summary` | Descriptive statistics, EDA | base, dplyr, janitor |
| `ttest` | Welch's / Student's t-test, paired | stats, effectsize |
| `anova` | One-way ANOVA + Tukey post-hoc | stats, effectsize |
| `correlation` | Pearson / Spearman | stats, effectsize |
| `linear_regression` | OLS with diagnostics | stats, broom, car, effectsize |
| `logistic_regression` | GLM binomial, odds ratios | stats, broom, effectsize |
| `poisson_regression` | GLM Poisson, overdispersion check | stats, broom, performance |
| `forecast_arima` | auto.arima + stationarity test | forecast, tseries |

---

## v0.2 — Classical Non-parametric + Missing Data

**Theme:** Complete the classical test battery. Handle real-world messy data.

### New analysis types

| analysis_type | Method | R Packages |
|---|---|---|
| `wilcoxon` | Wilcoxon rank-sum (Mann-Whitney U) / signed-rank | stats, effectsize |
| `kruskal` | Kruskal-Wallis + Dunn post-hoc | stats, dunn.test, effectsize |
| `chisq` | Chi-square test of independence | stats, effectsize |
| `fisher` | Fisher's exact test | stats, effectsize |
| `mcnemar` | McNemar's test for paired proportions | stats, effectsize |
| `friedman` | Friedman test for repeated measures | stats, effectsize |
| `missing_diagnostics` | MCAR test + missingness pattern | naniar, missMech |
| `multiple_imputation` | MICE / Amelia imputation + pooled analysis | mice, Amelia, broom |

### New capabilities

- **Multiple comparison correction:** Bonferroni, Holm, BH/FDR via `stats::p.adjust`. Available as a `p_adjust_method` field in any spec involving multiple tests.
- **Complete case vs imputed comparison:** When imputation is used, automatically run the analysis on both complete cases and imputed data, report side-by-side.

### Example spec — Wilcoxon rank-sum

```json
{
  "dataset_path": "examples/data/mtcars.csv",
  "analysis_type": "wilcoxon",
  "outcome": "mpg",
  "group_var": "am",
  "paired": false,
  "hypothesis": "Fuel efficiency differs between automatic and manual transmission",
  "alpha": 0.05,
  "seed": 42,
  "output_dir": "output/wilcoxon_mtcars"
}
```

### Example spec — Missing data diagnostics

```json
{
  "dataset_path": "data/clinical_trial.csv",
  "analysis_type": "missing_diagnostics",
  "variables": ["age", "bmi", "outcome", "treatment"],
  "mcar_test": true,
  "visualize_pattern": true,
  "output_dir": "output/missing_clinical"
}
```

### Example spec — Multiple imputation

```json
{
  "dataset_path": "data/clinical_trial.csv",
  "analysis_type": "multiple_imputation",
  "method": "mice",
  "m": 20,
  "downstream_analysis": {
    "analysis_type": "linear_regression",
    "outcome": "outcome",
    "predictors": ["age", "bmi", "treatment"],
    "formula": "outcome ~ age + bmi + treatment"
  },
  "compare_complete_case": true,
  "seed": 42,
  "output_dir": "output/imputed_regression"
}
```

### Package profile: `nonparam`

```bash
Rscript scripts/install-nonparam.R
# Installs: dunn.test, naniar, missMech, mice, Amelia
```

---

## v0.3 — Survival Analysis + Epidemiology

**Theme:** The bread and butter of biostatistics and clinical research.

### New analysis types

| analysis_type | Method | R Packages |
|---|---|---|
| `kaplan_meier` | KM curves + log-rank test | survival, survminer |
| `cox_regression` | Cox proportional hazards | survival, broom |
| `cox_td` | Cox with time-dependent covariates | survival |
| `competing_risks` | Fine-Gray subdistribution hazards | cmprsk, tidycmprsk |
| `rmst` | Restricted mean survival time | survRM2 |
| `incidence_rate` | Incidence rate ratio with CI | epitools, epiR |
| `odds_ratio` | Odds ratio / Risk ratio with CI | epitools, epiR |
| `mantel_haenszel` | Stratified analysis, Mantel-Haenszel | stats |
| `nnt` | Number needed to treat/harm | custom (base R) |

### Automatic checks

- **PH assumption:** Every Cox model automatically runs `cox.zph()` (Schoenfeld residuals). Violations flagged with severity level and suggested alternatives (stratification, time-varying coefficients).
- **Case-control / cohort detection:** Spec includes `study_design` field (`case_control`, `cohort`, `rct`). Effect measure automatically selected: OR for case-control, RR for cohort, HR for survival.

### Example spec — Kaplan-Meier + log-rank

```json
{
  "dataset_path": "data/lung_cancer.csv",
  "analysis_type": "kaplan_meier",
  "time_var": "time",
  "event_var": "status",
  "group_var": "sex",
  "hypothesis": "Survival differs between male and female lung cancer patients",
  "median_survival": true,
  "alpha": 0.05,
  "output_dir": "output/km_lung"
}
```

### Example spec — Cox proportional hazards

```json
{
  "dataset_path": "data/lung_cancer.csv",
  "analysis_type": "cox_regression",
  "time_var": "time",
  "event_var": "status",
  "predictors": ["age", "sex", "ph.ecog", "wt.loss"],
  "formula": "Surv(time, status) ~ age + sex + ph.ecog + wt.loss",
  "check_ph": true,
  "hypothesis": "Age, sex, ECOG score, and weight loss are associated with survival",
  "alpha": 0.05,
  "seed": 42,
  "output_dir": "output/cox_lung"
}
```

### Example spec — Odds ratio (case-control)

```json
{
  "dataset_path": "data/case_control_smoking.csv",
  "analysis_type": "odds_ratio",
  "exposure": "smoking",
  "outcome": "lung_cancer",
  "strata": "age_group",
  "study_design": "case_control",
  "output_dir": "output/or_smoking"
}
```

### Package profile: `survival`

```bash
Rscript scripts/install-survival.R
# Installs: survival, survminer, cmprsk, tidycmprsk, survRM2, epitools, epiR
```

---

## v0.4 — Mixed Effects + Longitudinal + Causal Inference

**Theme:** Handle clustered/hierarchical data. Move toward causal reasoning with proper methodology.

### New analysis types

| analysis_type | Method | R Packages |
|---|---|---|
| `lmm` | Linear mixed models (random intercepts/slopes) | lme4, lmerTest |
| `glmm` | Generalized linear mixed models | lme4 |
| `gee` | Generalized estimating equations | geepack |
| `icc` | Intraclass correlation coefficient | performance |
| `ps_matching` | Propensity score matching | MatchIt, cobalt |
| `ps_weighting` | IPW / IPTW propensity score weighting | WeightIt, PSweight, cobalt |
| `doubly_robust` | Doubly robust estimation (PS + outcome model) | WeightIt, sandwich |
| `mediation` | Causal mediation analysis | mediation |
| `iv_regression` | Instrumental variable / 2SLS | ivreg, AER |
| `did` | Difference-in-differences | did |
| `rdd` | Regression discontinuity design | rdrobust |

### Automatic checks

- **Mixed models:** ICC reported automatically. Singular fit warnings surfaced. Random effects structure guidance.
- **Propensity scores:** Balance diagnostics mandatory (standardized mean differences, Love plots via cobalt). Positivity violations flagged.
- **Causal methods:** DAG-awareness — spec accepts optional `dag` field describing assumed causal structure. Warnings when methods require assumptions not verifiable from data.

### Example spec — Linear mixed model

```json
{
  "dataset_path": "data/classroom.csv",
  "analysis_type": "lmm",
  "outcome": "math_score",
  "fixed_effects": ["ses", "minority", "female"],
  "random_effects": {
    "intercept": "school_id",
    "slopes": [{"var": "ses", "group": "school_id"}]
  },
  "formula": "math_score ~ ses + minority + female + (1 + ses | school_id)",
  "hypothesis": "SES, minority status, and sex are associated with math scores after accounting for school-level clustering",
  "alpha": 0.05,
  "seed": 42,
  "output_dir": "output/lmm_classroom"
}
```

### Example spec — Propensity score matching

```json
{
  "dataset_path": "data/observational_treatment.csv",
  "analysis_type": "ps_matching",
  "treatment": "treated",
  "outcome": "recovery_time",
  "covariates": ["age", "sex", "bmi", "comorbidity_score"],
  "matching_method": "nearest",
  "caliper": 0.2,
  "ratio": 1,
  "balance_check": true,
  "downstream_analysis": {
    "analysis_type": "linear_regression",
    "formula": "recovery_time ~ treated"
  },
  "hypothesis": "Treatment is associated with reduced recovery time after adjusting for confounders",
  "output_dir": "output/psm_treatment"
}
```

### Example spec — Difference-in-differences

```json
{
  "dataset_path": "data/policy_evaluation.csv",
  "analysis_type": "did",
  "outcome": "health_outcome",
  "treatment_var": "policy_group",
  "time_var": "period",
  "id_var": "county_id",
  "check_parallel_trends": true,
  "hypothesis": "Policy intervention is associated with improved health outcomes",
  "output_dir": "output/did_policy"
}
```

### Package profile: `mixed`

```bash
Rscript scripts/install-mixed.R
# Installs: lme4, lmerTest, geepack, MatchIt, WeightIt, PSweight, cobalt, mediation, ivreg, AER, did, rdrobust
```

---

## v0.5 — Bayesian + Advanced Modeling

**Theme:** Full Bayesian workflow. Advanced GLM extensions for real clinical data quirks.

### New analysis types

| analysis_type | Method | R Packages |
|---|---|---|
| `bayes_regression` | Bayesian linear/logistic/Poisson regression | brms, rstanarm |
| `bayes_mixed` | Bayesian mixed effects models | brms |
| `bayes_compare` | Bayes factors for model comparison | BayesFactor, bridgesampling |
| `gam` | Generalized additive models | mgcv |
| `quantile_regression` | Quantile regression | quantreg |
| `robust_regression` | M-estimation, MM-estimation | robustbase, MASS |
| `zero_inflated` | Zero-inflated Poisson / Negative Binomial | pscl |
| `hurdle` | Hurdle models | pscl |
| `ordinal_regression` | Proportional odds / cumulative logit | MASS, ordinal |
| `multinomial` | Multinomial logistic regression | nnet |

### Bayesian workflow requirements

Every Bayesian analysis automatically includes:
1. **Prior specification** — explicit in spec (`priors` field), with default weakly informative priors documented
2. **Prior sensitivity analysis** — re-run with 2–3 alternative prior sets, compare posteriors
3. **Convergence diagnostics** — R̂, ESS (bulk + tail), trace plots, rank plots
4. **Posterior predictive checks** — visual + numeric (pp_check)
5. **LOO-CV** — leave-one-out cross-validation via `loo` package, ELPD reported
6. **Credible intervals** — 95% HDI (highest density interval) as default, not equal-tailed

### Example spec — Bayesian regression

```json
{
  "dataset_path": "examples/data/mtcars.csv",
  "analysis_type": "bayes_regression",
  "outcome": "mpg",
  "predictors": ["wt", "hp", "am"],
  "formula": "mpg ~ wt + hp + am",
  "family": "gaussian",
  "priors": {
    "intercept": "normal(20, 10)",
    "coefficients": "normal(0, 5)",
    "sigma": "half_cauchy(0, 5)"
  },
  "prior_sensitivity": true,
  "chains": 4,
  "iter": 4000,
  "warmup": 1000,
  "hypothesis": "Vehicle weight, horsepower, and transmission type are associated with fuel efficiency",
  "seed": 42,
  "output_dir": "output/bayes_mtcars"
}
```

### Example spec — Zero-inflated Poisson

```json
{
  "dataset_path": "data/doctor_visits.csv",
  "analysis_type": "zero_inflated",
  "outcome": "visits",
  "predictors": ["age", "sex", "insurance", "chronic"],
  "formula": "visits ~ age + sex + insurance + chronic",
  "family": "poisson",
  "zero_formula": "~ insurance + chronic",
  "overdispersion_check": true,
  "hypothesis": "Age, sex, insurance, and chronic conditions are associated with doctor visit counts",
  "seed": 42,
  "output_dir": "output/zip_visits"
}
```

### Example spec — GAM

```json
{
  "dataset_path": "data/environmental.csv",
  "analysis_type": "gam",
  "outcome": "health_index",
  "smooth_terms": ["s(temperature)", "s(humidity)", "s(pm25)"],
  "linear_terms": ["age", "sex"],
  "formula": "health_index ~ s(temperature) + s(humidity) + s(pm25) + age + sex",
  "family": "gaussian",
  "method": "REML",
  "hypothesis": "Temperature, humidity, and PM2.5 have non-linear associations with health index",
  "output_dir": "output/gam_environmental"
}
```

### Package profile: `bayes`

```bash
Rscript scripts/install-bayes.R
# Installs: brms, rstanarm, bayesplot, loo, BayesFactor, bridgesampling
```

### Package profile: `advanced`

```bash
Rscript scripts/install-advanced.R
# Installs: mgcv, quantreg, robustbase, pscl, ordinal, nnet
```

---

## v0.6 — Meta-analysis + Power + SEM + Diagnostic Tests

**Theme:** Study-level methods. The full toolkit for systematic reviews, study planning, psychometrics, and clinical diagnostics.

### New analysis types

| analysis_type | Method | R Packages |
|---|---|---|
| `meta_analysis` | Fixed/random effects meta-analysis | metafor, meta |
| `network_meta` | Network meta-analysis (NMA) | netmeta |
| `meta_regression` | Meta-regression + subgroup analysis | metafor |
| `power_analysis` | Power / sample size calculation | pwr, WebPower |
| `power_survival` | Sample size for survival studies | ssanv |
| `power_mixed` | Sample size for mixed models (simulation-based) | simr, longpower |
| `sem` | Structural equation modeling | lavaan |
| `cfa` | Confirmatory factor analysis | lavaan |
| `path_analysis` | Path analysis | lavaan |
| `measurement_invariance` | Configural, metric, scalar invariance testing | lavaan, semTools |
| `roc_auc` | ROC curves, AUC, optimal cutoff | pROC, ROCR |
| `bland_altman` | Bland-Altman agreement analysis | blandr (or custom) |
| `reliability` | Cohen's κ, Fleiss' κ, Cronbach's α | irr, psych |

### Meta-analysis requirements

- **Heterogeneity:** I², τ², Q-test, prediction interval — all reported automatically
- **Publication bias:** Funnel plot + Egger's regression test + trim-and-fill
- **Forest plots:** Auto-generated with study labels, effect sizes, CIs, weights, and diamond summary
- **Network meta:** League table, network graph, inconsistency check (node-splitting)

### SEM requirements

- **Fit indices:** χ², RMSEA (+ 90% CI), CFI, TLI, SRMR — all mandatory
- **Modification indices** reported but with warning against post-hoc fishing
- **Measurement invariance:** Stepwise configural → metric → scalar → strict, with ΔCFI criterion

### Example spec — Random effects meta-analysis

```json
{
  "dataset_path": "data/meta_rct.csv",
  "analysis_type": "meta_analysis",
  "effect_size_col": "yi",
  "variance_col": "vi",
  "study_label_col": "study",
  "model": "random",
  "method": "REML",
  "publication_bias": true,
  "forest_plot": true,
  "funnel_plot": true,
  "hypothesis": "Treatment has an overall effect across randomized controlled trials",
  "output_dir": "output/meta_rct"
}
```

### Example spec — Power analysis

```json
{
  "dataset_path": null,
  "analysis_type": "power_analysis",
  "test_type": "two_sample_t",
  "effect_size": 0.5,
  "alpha": 0.05,
  "power": 0.80,
  "ratio": 1,
  "alternative": "two.sided",
  "hypothesis": "Determine required sample size to detect medium effect (d=0.5) with 80% power",
  "output_dir": "output/power_ttest"
}
```

### Example spec — SEM

```json
{
  "dataset_path": "data/survey.csv",
  "analysis_type": "sem",
  "model_syntax": "
    # Measurement model
    depression =~ dep1 + dep2 + dep3 + dep4
    anxiety =~ anx1 + anx2 + anx3 + anx4
    # Structural model
    depression ~ stress + social_support
    anxiety ~ stress + social_support
    depression ~~ anxiety
  ",
  "estimator": "MLR",
  "missing": "FIML",
  "hypothesis": "Stress and social support are associated with depression and anxiety, which are correlated",
  "output_dir": "output/sem_mental_health"
}
```

### Example spec — ROC / AUC

```json
{
  "dataset_path": "data/biomarker.csv",
  "analysis_type": "roc_auc",
  "predictor": "biomarker_score",
  "outcome": "disease_status",
  "optimal_cutoff_method": "youden",
  "compare_predictors": ["biomarker_score", "clinical_score"],
  "hypothesis": "Biomarker score has diagnostic accuracy for disease status",
  "output_dir": "output/roc_biomarker"
}
```

### Example spec — Reliability (Cohen's kappa)

```json
{
  "dataset_path": "data/rater_agreement.csv",
  "analysis_type": "reliability",
  "method": "cohens_kappa",
  "rater_cols": ["rater1", "rater2"],
  "weighted": true,
  "hypothesis": "Raters show substantial agreement in diagnosis classification",
  "output_dir": "output/kappa_raters"
}
```

### Package profile: `meta`

```bash
Rscript scripts/install-meta.R
# Installs: metafor, meta, netmeta
```

### Package profile: `power`

```bash
Rscript scripts/install-power.R
# Installs: pwr, WebPower, ssanv, simr, longpower
```

### Package profile: `sem`

```bash
Rscript scripts/install-sem.R
# Installs: lavaan, semTools
```

### Package profile: `diagnostic`

```bash
Rscript scripts/install-diagnostic.R
# Installs: pROC, ROCR, blandr, irr, psych
```

---

## Statistical Protocol (all versions)

Every analysis type across all versions **must** comply with:

### 1. Effect sizes + confidence intervals — mandatory
No test reports only a p-value. Every method includes the appropriate effect size measure and its confidence interval.

| Method family | Effect size | Package |
|---|---|---|
| t-test, Wilcoxon | Cohen's d, rank-biserial r | effectsize |
| ANOVA, Kruskal-Wallis | η², ε², rank η² | effectsize |
| Chi-square, Fisher | Cramér's V, φ | effectsize |
| Regression | R², adjusted R², Cohen's f² | effectsize, performance |
| Logistic | OR with CI | broom |
| Cox | HR with CI | broom |
| Mixed models | Marginal/conditional R² | performance |
| Meta-analysis | Pooled effect + I², τ² | metafor |
| Bayesian | Posterior median + HDI, BF | bayestestR |
| SEM | Standardized loadings, fit indices | lavaan |

### 2. Automatic assumption checking
Before running any analysis, the system checks:
- Sample size adequacy (method-specific thresholds)
- Data type compatibility (continuous, categorical, ordinal, survival)
- Distribution assumptions (normality, homoscedasticity, proportional hazards, etc.)
- Missing data pattern and proportion

Violations are reported with severity level (⚠️ warning vs ❌ critical) and alternative method suggestions.

### 3. Standardized output artifacts
Every single analysis produces:

```
output/<analysis_name>/
├── summary.json          # Machine-readable: status, method, findings, warnings
├── report.md             # Human-readable analysis report
├── schema.json           # Dataset column types, missingness
├── session_info.txt      # R version, packages, platform, timestamp
├── executed_spec.json    # Exact input spec (reproducibility)
├── tables/               # CSVs: coefficients, fit stats, group summaries
└── figures/              # PNGs: diagnostic plots, result plots
```

### 4. Bilingual support
Every analysis type supports triggering in both English and Chinese (中文). SKILL.md maintains keyword mappings for both languages.

### 5. Conservative statistical language
- ✅ "associated with", "evidence suggests", "estimated effect"
- ❌ Never "causes", "proves", "definitively shows"
- Observational data → association language only
- RCT data → may use stronger causal language with caveats noted

### 6. Example specs + test datasets
Every new analysis type ships with:
- At least 1 example JSON spec in `examples/specs/`
- At least 1 test dataset in `examples/data/` (real or simulated)
- The example must run end-to-end with `run-rstats.sh analyze --spec`

---

## Cumulative method count

| Version | New methods | Cumulative | Focus |
|---------|-------------|------------|-------|
| v0.1 | 8 | 8 | Foundation |
| v0.2 | 8 | 16 | Non-parametric + Missing data |
| v0.3 | 9 | 25 | Survival + Epidemiology |
| v0.4 | 11 | 36 | Mixed effects + Causal |
| v0.5 | 10 | 46 | Bayesian + Advanced GLM |
| v0.6 | 14 | 60 | Meta + Power + SEM + Diagnostics |

**60 analysis types. One unified interface. Spec in, report out.**
