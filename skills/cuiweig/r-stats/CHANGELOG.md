# Changelog

All notable changes to this project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.7.0] - 2026-03-27

### Added — Regularization / variable selection
- LASSO, Ridge, Elastic Net with CV lambda (glmnet)
- Adaptive LASSO with oracle property
- Group LASSO (gglasso), SCAD/MCP (ncvreg)
- Stability selection (stabs), Penalized Cox

### Added — Causal inference (frontier)
- TMLE (tmle), Causal forests/HTE (grf), G-computation, DAG analysis (dagitty + ggdag)

### Added — Longitudinal / multi-state
- Joint models (JM), Multi-state models (msm), Latent trajectory analysis (lcmm)

### Added — Psychometrics / social science
- IRT: 2PL with ICC curves and test information (mirt)
- Latent class analysis with BIC selection (poLCA)
- Multilevel mediation (lme4 + mediation)

### Added — Clinical trial design
- Equivalence/non-inferiority sample size (rpact)
- Cluster randomized trial power with DEFF
- Adaptive/group sequential design with alpha spending (rpact)

### Stats
- Total analysis methods: **82**
- New modules: R/regularization.R, R/longitudinal.R, R/psychometrics.R, R/dag.R

---

## [0.6.1] - 2026-03-27

### Added — Missing methods
- **Doubly robust estimation** (`doubly_robust`): AIPW estimator combining PS weighting + outcome model, comparison with naive OLS and IPW-only estimates
- **Hurdle models** (`hurdle`): pscl::hurdle for Poisson/NegBin, with AIC comparison to zero-inflated and standard Poisson
- **ETS forecasting** (`forecast_ets`): forecast::ets with ARIMA AIC comparison

### Added — Infrastructure
- Install scripts: `install-survival.R`, `install-causal.R`, `install-advanced.R`, `install-meta.R`, `install-power.R`, `install-sem.R`, `install-diagnostic.R`
- `tests/run_all_specs.sh`: automated test runner for all example specs
- `docs/INSTALL.md`: comprehensive installation guide with all 12 package profiles
- `docker/Dockerfile`: based on rocker/r-ver:4.4.0 with all packages pre-installed

### Stats
- Total analysis methods: **63** (60 + 3 new)
- All 52 example specs pass regression testing

---

## [0.6.0] - 2026-03-27

### Added — Meta-analysis
- **Meta-analysis** (`meta_analysis`): metafor::rma FE/RE, forest + funnel plots, I2/tau2/H2, Egger's test, trim-and-fill
- **Meta-regression** (`meta_regression`): moderator analysis with QM test, R2 analog
- **Subgroup meta** (`subgroup_meta`): per-subgroup pooled estimates, between-group Q test
- **Network meta** (`network_meta`): netmeta with P-scores, league table, network graph

### Added — Power / sample size
- **Power analysis** (`power_analysis`): pwr package — t-test, ANOVA, chi-square, correlation, regression, proportions; power curves
- **Survival power** (`power_survival`): Schoenfeld formula for log-rank sample size
- **Mixed model power** (`power_mixed`): normal approximation for repeated measures

### Added — Structural equation modeling
- **SEM** (`sem`): lavaan::sem with fit indices, R2, modification indices, semPlot path diagrams
- **CFA** (`cfa`): factor loadings, AVE/CR/alpha via semTools, low loading warnings
- **Measurement invariance** (`measurement_invariance`): 4-level stepwise, delta CFI criterion
- **Path analysis** (`path_analysis`): direct + indirect + total effects with := definitions

### Added — Diagnostic test accuracy
- **ROC/AUC** (`roc_auc`): pROC with DeLong CI, Youden optimal cutpoint, Sens/Spec/PPV/NPV/LR
- **Bland-Altman** (`bland_altman`): bias + 95% LoA, proportional bias check
- **Kappa** (`kappa`): Cohen's/Fleiss' kappa with Landis-Koch interpretation
- **Cronbach's alpha** (`cronbach_alpha`): raw + standardized alpha, item-if-dropped analysis

### Added — Infrastructure
- `R/meta.R`, `R/power.R`, `R/sem.R`, `R/diagnostic.R`: four new modules
- 15 new analysis types, 7 new example datasets, 13 new example specs

### Stats
- Total analysis methods: **60** (8+9+10+10+8+15)
- All 49 example specs pass regression testing

---

## [0.5.0] - 2026-03-27

### Added — Bayesian analysis
- **Bayesian regression** (`bayesian_regression`): brms::brm with gaussian/binomial/poisson, posterior summary (mean, SD, 95% CrI), convergence diagnostics (Rhat, ESS), trace plots, posterior distributions, PP check, optional LOO-CV with Pareto k diagnostics
- **Bayes factor** (`bayes_factor`): BayesFactor::ttestBF and lmBF, BF10 with Jeffreys/Lee-Wagenmakers evidence interpretation scale, evidence visualization

### Added — Advanced modeling
- **GAM** (`gam`): mgcv::gam with smooth term partial effect plots, edf, deviance explained, gam.check diagnostics
- **Quantile regression** (`quantile_regression`): quantreg::rq with multi-tau coefficient plots and OLS comparison
- **Robust regression** (`robust_regression`): MASS::rlm MM-estimation with weight histogram and OLS comparison
- **Zero-inflated** (`zero_inflated`): pscl::zeroinfl for ZIP/ZINB, count + zero model coefficients, observed vs predicted zero comparison
- **Ordinal regression** (`ordinal_regression`): MASS::polr proportional odds with OR + CI
- **Multinomial** (`multinomial`): nnet::multinom with RRR + CI per outcome level vs reference

### Added — Infrastructure
- `R/bayesian.R`, `R/advanced.R`: two new modules
- Updated `scripts/install-bayes.R` (brms, rstan, bayesplot, loo, BayesFactor, bridgesampling)
- `scripts/run-rstats.sh`: auto-detect Rtools PATH on Windows for Stan compilation
- Example datasets: nonlinear_sim.csv, zero_inflated_counts.csv, ordinal_satisfaction.csv
- Example specs for all 8 new analysis types

### Stats
- Total analysis methods: **45** (8 v0.1 + 9 v0.2 + 10 v0.3 + 10 v0.4 + 8 v0.5)
- All 36 example specs pass regression testing

---

## [0.4.0] - 2026-03-27

### Added — Mixed-effects models
- **Linear mixed model** (`lmm`): lme4::lmer + lmerTest Satterthwaite p-values, random effects variance components, ICC via performance::icc, AIC/BIC, residual diagnostics, singular fit detection
- **GLMM** (`glmm`): lme4::glmer for binomial/Poisson with exponentiated fixed effects (OR/IRR), convergence check, overdispersion check, forest plot
- **GEE** (`gee`): geepack::geeglm with configurable correlation structure, robust SE, QIC, explains GEE vs GLMM distinction
- **ICC** (`icc`): standalone intraclass correlation from null model, variance decomposition, Cicchetti guidelines

### Added — Causal inference
- **Propensity score matching** (`propensity_match`): MatchIt with nearest/optimal/full, caliper support, cobalt balance diagnostics with Love plot, post-match ATT estimation
- **Propensity score weighting** (`propensity_weight`): WeightIt with ATE/ATT/ATO estimands, ESS, extreme weight warnings, robust SE outcome estimation
- **Causal mediation** (`mediation_analysis`): mediation::mediate with bootstrap CIs, ACME + ADE + proportion mediated, effect decomposition plot
- **IV regression** (`iv_regression`): ivreg 2SLS, first-stage F (weak instrument test), Wu-Hausman, Sargan, OLS vs IV comparison
- **Difference-in-differences** (`did`): classic 2×2 DiD via interaction, parallel trends visualization, ATT with CI
- **Regression discontinuity** (`rdd`): rdrobust with MSE-optimal bandwidth, conventional + robust estimates, McCrary manipulation test (rddensity), RD plot

### Added — Infrastructure
- `R/mixed.R`, `R/causal.R`: two new modules
- `scripts/install-mixed.R`: lme4, lmerTest, geepack, broom.mixed, performance
- Example datasets: sleepstudy.csv, clustered_binary.csv, observational_treatment.csv, mediation_sim.csv, iv_sim.csv, did_policy.csv, rdd_election.csv
- Example specs for all 10 new analysis types

### Stats
- Total analysis methods: **37** (8 v0.1 + 9 v0.2 + 10 v0.3 + 10 v0.4)
- All 28 example specs pass regression testing

---

## [0.3.0] - 2026-03-27

### Added — Survival analysis
- **Kaplan-Meier** (`kaplan_meier`): KM curves via survminer with risk table, CI, p-value annotation; log-rank test; median survival with CI; survival at configurable time points; HR for 2-group comparisons
- **Cox proportional hazards** (`cox_regression`): HR + 95% CI, C-index, AIC; PH assumption check via cox.zph (per-variable + global); Schoenfeld residual plots; forest plot; natural language HR interpretation
- **Competing risks** (`competing_risks`): Fine-Gray subdistribution hazard model (cmprsk::crr); CIF plots; Gray's test for group comparison; report explains KM vs CIF difference
- **Cox time-dependent** (`cox_time_dependent`): counting process (start, stop] format; HR + CI + PH check; warns about immortal time bias
- **RMST** (`rmst`): restricted mean survival time via survRM2; difference + ratio + CI; configurable tau; explains when RMST is preferred over HR

### Added — Epidemiology
- **Odds ratio** (`odds_ratio`): 2×2 OR with Wald CI, chi-square test, forest-style plot; configurable exposure/outcome levels
- **Risk ratio** (`risk_ratio`): RR + RD + NNT from 2×2 table; automatic NNT/NNH classification; risk per group
- **Incidence rate ratio** (`incidence_rate`): IRR from person-time data with log-method CI
- **Mantel-Haenszel** (`mantel_haenszel`): crude OR vs MH-adjusted OR; stratum-specific ORs; Breslow-Day homogeneity test; confounding assessment (>10% change rule); forest plot
- **NNT** (`nnt`): standalone NNT/NNH calculation from ARR with CI; clinical interpretation

### Added — Infrastructure
- `R/survival.R`: survival analysis module (5 functions)
- `R/epi.R`: epidemiology module (5 functions)
- Example datasets: lung_cancer.csv, competing_risks_sim.csv, case_control.csv, cohort_study.csv
- Example specs for all 10 new analysis types
- Package dependencies: survival, survminer, cmprsk, tidycmprsk, survRM2, epitools, epiR

### Stats
- Total analysis methods: **27** (8 v0.1 + 9 v0.2 + 10 v0.3)
- All 19 example specs pass regression testing

---

## [0.2.0] - 2026-03-27

### Added — Non-parametric tests
- **Wilcoxon rank-sum / signed-rank test** (`wilcoxon`): independent and paired modes, rank-biserial r effect size with CI, location shift CI, boxplot with jitter
- **Kruskal-Wallis test** (`kruskal`): H statistic, rank epsilon² effect size, automatic Dunn post-hoc with configurable p-value adjustment (Holm default)
- **Chi-square test** (`chisq`): contingency table, Cramér's V with CI, expected count check (auto-warns if >20% cells < 5), stacked bar plot
- **Fisher's exact test** (`fisher`): 2×2 with odds ratio + CI, r×c with Monte Carlo simulation (B=10,000)
- **McNemar's test** (`mcnemar`): paired categorical data, discordant pair reporting, before/after visualization
- **Friedman test** (`friedman`): non-parametric repeated measures, pairwise Wilcoxon post-hoc with p.adjust, handles unbalanced subjects

### Added — Missing data
- **Missing data diagnostics** (`missing_diagnostics`): per-column missingness stats, naniar::vis_miss pattern visualization, Little's MCAR test, tiered strategy recommendations (<5% / 5-20% / >20%)
- **Multiple imputation** (`multiple_imputation`): MICE with configurable method/m/maxit, observed vs imputed distribution comparison, convergence plots, optional pooled downstream regression (Rubin's rules) with complete-case comparison

### Added — Multiple comparison correction
- **P-value adjustment** (`p_adjust`): Bonferroni, Holm, Hochberg, BH (FDR), BY methods; accepts p-values from spec, CSV, or data; before/after comparison table with -log10(p) visualization

### Added — Infrastructure
- `scripts/install-missing.R`: installs naniar, mice, VIM
- `R/missing.R`: missing data analysis module
- `R/adjustments.R`: p-value adjustment module
- Example datasets: iris.csv, titanic.csv, fisher_small.csv, mcnemar_treatment.csv, friedman_repeated.csv, airquality_missing.csv
- Example specs for all 9 new analysis types

### Fixed
- `fmt()` in utils.R: handle vector inputs safely (fixes `'length = 2' in coercion to logical(1)` error)

### Stats
- Total analysis methods: **17** (8 from v0.1 + 9 new)
- All 12 example specs pass regression testing

---

## [0.1.0] - 2026-03-27

### Added
- **Core analysis engine** with JSON spec-driven workflow
- **Analysis types**: summary/EDA, t-test (Welch/Student), ANOVA with Tukey post-hoc, Pearson/Spearman correlation, linear regression, logistic regression, Poisson regression, ARIMA forecasting
- **Diagnostic framework**: Shapiro-Wilk normality, Breusch-Pagan heteroscedasticity, VIF multicollinearity, regression diagnostic plots
- **Statistically opinionated reporting**: mandatory effect sizes (Cohen's d, η², R², OR), confidence intervals, assumption checks, and conservative language
- **Schema inspector**: column types, missingness, numeric summaries, automatic warnings for >5% missing or n<30
- **Doctor command**: environment diagnostics across 4 package profiles (core, stats, forecast, bayes)
- **Reproducibility**: random seed, executed spec copy, full session info capture per run
- **Output artifacts**: summary.json, report.md, schema.json, session_info.txt, tables/*.csv, figures/*.png
- **Example specs**: mtcars regression, mtcars t-test, AirPassengers ARIMA forecast
- **SKILL.md**: OpenClaw skill definition with analysis selection guide and method switching guardrails
- **Bilingual support**: English and Chinese (中文) query recognition

*(All planned features from v0.2 through v0.7 have been implemented. See releases above.)*
