[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![R ≥ 4.1](https://img.shields.io/badge/R-%E2%89%A5%204.1-276DC3.svg?logo=r)](https://www.r-project.org/)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-7C3AED.svg)](https://openclaw.ai)

# 📊 openclaw-r-stats

**Bring serious statistics to your AI agent.**

An [OpenClaw](https://github.com/openclaw/openclaw) skill that gives your agent the ability to run professional-grade statistical analysis in R — with reproducible specs, opinionated reporting, and diagnostic rigor.

This is not "let an AI run R." This is **a serious statistical analysis toolkit with opinionated reporting standards.**

## Why

LLMs are good at interpreting results. They are bad at computing them. R is the opposite. This skill bridges the gap:

- **R-native**: Real R engine, real packages (tidyverse, broom, effectsize, forecast). Not a Python wrapper pretending to be R.
- **Reproducible**: Every analysis is driven by a JSON spec. Same spec → same results. Always.
- **Statistically opinionated**: Effect sizes are mandatory. P-values alone are not enough. Causality claims from observational data are forbidden. Assumption violations trigger warnings, not silence.

## Quick Start

### 1. Install R

```bash
# macOS
brew install r

# Ubuntu/Debian
sudo apt install r-base

# Windows
winget install RProject.R
```

### 2. Install core R packages

```bash
Rscript scripts/install-core.R
```

### 3. Check environment

```bash
bash scripts/run-rstats.sh doctor
```

> **Windows note:** The shell scripts require `bash`. Use [Git Bash](https://git-scm.com/downloads) (bundled with Git for Windows) or WSL. Git Bash works out of the box — no WSL setup needed.

### 4. Generate example data

```bash
Rscript scripts/generate_example_data.R
```

### 5. Run an analysis

```bash
# Linear regression: mpg ~ wt + hp
bash scripts/run-rstats.sh analyze --spec examples/specs/regression_mtcars.json

# T-test: mpg by transmission type
bash scripts/run-rstats.sh analyze --spec examples/specs/ttest_mtcars.json

# Time series forecast (requires forecast profile)
Rscript scripts/install-forecast.R
bash scripts/run-rstats.sh analyze --spec examples/specs/forecast_airpassengers.json
```

### 6. Check results

```
output/regression_mtcars/
├── summary.json          # Machine-readable results
├── report.md             # Human-readable report
├── schema.json           # Dataset column info
├── session_info.txt      # R version, packages, timestamp
├── executed_spec.json    # Exact spec used (reproducibility)
├── tables/
│   ├── coefficients.csv
│   ├── model_fit.csv
│   └── standardized_coef.csv
└── figures/
    ├── regression_fit.png
    └── regression_diagnostics.png
```

## Demo

<!-- ![Demo](docs/demo.gif) -->
*Demo GIF in progress — see [Example Output](#example-output) below for sample results.*

## Example Output

Here's what a real analysis looks like. The agent was asked: *"Regress mpg on weight, horsepower, and transmission type using mtcars."*

### Model Fit

- **R² = 0.840** (adjusted R² = 0.823) — the model explains 84% of variance in fuel efficiency
- **Cohen's f² = 5.25** — large effect (> 0.35 threshold)
- **F(3, 28) = 48.96, p < 0.001**

### Coefficients

| Term | Estimate | 95% CI | p | Std. β |
|------|----------|--------|---|--------|
| (Intercept) | 34.00 | [28.59, 39.42] | < 0.001 *** | — |
| **wt** | **-2.88** | **[-4.73, -1.02]** | **0.004 \*\*** | **-0.47** |
| **hp** | **-0.037** | **[-0.057, -0.018]** | **< 0.001 \*\*\*** | **-0.43** |
| am | 2.08 | [-0.74, 4.90] | 0.141 ns | 0.17 |

### Assumption Checks

- ✅ Linearity: residuals vs fitted — no major pattern
- ✅ Normality: Q-Q plot — approximate normality, slight right-tail deviation
- ⚠️ Homoscedasticity: mild increase in variance with fitted values
- ✅ Influential points: no observations exceed Cook's distance = 0.5

### Generated Artifacts

```
output/regression_mtcars_full/
├── summary.json, report.md, schema.json, session_info.txt
├── tables/coefficients.csv, model_fit.csv, standardized_coef.csv
└── figures/regression_diagnostics.png
```

> Every analysis — from t-test to meta-analysis — produces this full artifact set. Same spec → same results. Always.

---

### Survival Analysis: Kaplan-Meier

*"Compare survival between male and female lung cancer patients."*

- **Log-rank:** χ²(1) = 10.33, p = 0.001
- **HR** = 0.59 [0.42, 0.82] — female patients have 41% lower hazard
- **Median survival:** Male 270 days [212, 310] · Female 426 days [348, 550]
- Generates: KM curve with risk table, survival at 6/12/24 months

### Meta-Analysis: BCG Vaccine

*"Pool the BCG vaccine trial results."*

- **Pooled log-RR** = -0.71 [-1.07, -0.36], p < 0.001
- **I²** = 92.2% (high heterogeneity)
- **Egger's test:** p = 0.19 (no publication bias)
- Generates: forest plot, funnel plot, trim-and-fill

### Bayesian Regression

*"Bayesian regression: mpg ~ wt + hp"*

- **wt:** posterior mean = -3.89, 95% CrI [-5.24, -2.56]
- **hp:** posterior mean = -0.032, 95% CrI [-0.050, -0.013]
- **Rhat** = 1.003 (converged), **LOO ELPD** = -79.1
- Generates: posterior distributions, trace plots, PP check

## Use with OpenClaw

Install as a skill in your OpenClaw workspace:

```bash
# From ClawHub (when published)
clawhub install openclaw-r-stats

# Or clone directly
git clone https://github.com/CuiweiG/openclaw-r-stats.git
```

Then just talk to your agent:

> "Analyze this CSV — what predicts sales?"
>
> "这两组数据有显著差异吗？"
>
> "Run a regression of mpg on weight and horsepower"
>
> "Forecast the next 12 months of this time series"

The agent reads `SKILL.md`, inspects your data, builds a spec, runs R, and reports back with effect sizes, confidence intervals, assumption checks, and plots.

## 82 Analysis Methods ✅

### Academic Coverage

This skill covers methods commonly used in graduate-level biostatistics, epidemiology, psychometrics, and quantitative social science:

- **Biostatistics:** regression, survival analysis, mixed models, missing data, diagnostics
- **Epidemiology:** OR/RR/IRR, Mantel-Haenszel, NNT, competing risks, RMST
- **Clinical Trials:** power analysis, equivalence/NI design, CRT, adaptive/group sequential
- **Causal Inference:** PSM, IPTW, TMLE, causal forests, G-computation, IV, DiD, RDD, DAGs
- **Psychometrics:** IRT, CFA, Cronbach's alpha, measurement invariance, latent class analysis
- **Longitudinal Research:** LMM/GLMM, GEE, joint models, multi-state, trajectory analysis
- **High-Dimensional Data:** LASSO/Ridge/Elastic Net, adaptive LASSO, SCAD/MCP, stability selection
- **Bayesian Inference:** brms regression, LOO-CV, posterior predictive checks, Bayes factors
- **Meta-Analysis:** fixed/random effects, forest/funnel plots, network meta-analysis, meta-regression
- **Structural Equation Modeling:** SEM, CFA, path analysis, measurement invariance

### For Researchers

Every method in this toolkit follows strict reporting standards:
- **Effect sizes + confidence intervals** — mandatory for every test, not just p-values
- **Automatic assumption checking** — violations flagged with alternatives suggested
- **Conservative statistical language** — "associated with", never "causes" for observational data
- **Full reproducibility** — random seed, session info, and executed spec saved with every run
- **Standardized output** — summary.json + report.md + tables/ + figures/ for every analysis

### All 82 Methods

### Foundation (8)
Summary/EDA · T-test · ANOVA + Tukey · Correlation · Linear regression · Logistic regression · Poisson regression · ARIMA forecast

### Non-parametric + Missing Data (9)
Wilcoxon · Kruskal-Wallis + Dunn · Chi-square · Fisher's exact · McNemar · Friedman · MCAR test + missing diagnostics · MICE imputation · P-value adjustment

### Survival + Epidemiology (10)
Kaplan-Meier · Cox PH · Competing risks · Cox time-dependent · RMST · Odds ratio · Risk ratio + NNT · Incidence rate ratio · Mantel-Haenszel · NNT/NNH

### Mixed Effects + Causal Inference (10)
LMM · GLMM · GEE · ICC · PS matching · PS weighting · Causal mediation · IV regression · DiD · RDD

### Bayesian + Advanced (11)
Bayesian regression (brms) + LOO-CV · Bayes factors · GAM · Quantile regression · Robust regression · Zero-inflated · Hurdle models · Ordinal regression · Multinomial · ETS forecast · Doubly robust

### Meta + Power + SEM + Diagnostics (15)
Meta-analysis · Meta-regression · Subgroup meta · Network meta · Power (6 types) · Survival power · Mixed power · SEM · CFA · Measurement invariance · Path analysis · ROC/AUC · Bland-Altman · Kappa · Cronbach's alpha

### Regularization + Variable Selection (6)
LASSO · Ridge · Elastic Net · Adaptive LASSO · Group LASSO · SCAD/MCP · Stability selection · Penalized Cox

### Causal Inference Frontier (4)
TMLE · Causal forests/HTE · G-computation · DAG analysis

### Longitudinal + Multi-State (3)
Joint models · Multi-state models · Trajectory/LCMM

### Psychometrics + Social Science (3)
IRT (2PL) · Latent class analysis · Multilevel mediation

### Clinical Trial Design (3)
Equivalence/NI power · CRT power · Adaptive/group sequential

> **Full roadmap with JSON spec examples:** [docs/ROADMAP.md](docs/ROADMAP.md)

## Statistical Philosophy

This skill follows strict reporting standards:

1. **Never report only p-values.** Every test includes effect sizes (Cohen's d, η², R², OR) and confidence intervals.
2. **Never claim causality from observational data.** Language is always "associated with" or "evidence suggests."
3. **Always check assumptions first.** Normality, homoscedasticity, multicollinearity — violations are flagged, not ignored.
4. **Automatic method switching.** Non-normal + small n → Welch or non-parametric. Small expected counts → Fisher. Heteroscedastic → robust SE warning.
5. **Reproducibility is non-negotiable.** Random seed, full session info, and executed spec saved with every run.

## Package Profiles

| Profile | Packages | Install |
|---------|----------|---------|
| **core** | jsonlite, readr, dplyr, tidyr, janitor, ggplot2, broom, effectsize, performance, car, MASS, sandwich, lmtest | `Rscript scripts/install-core.R` |
| **forecast** | forecast, tseries, zoo | `Rscript scripts/install-forecast.R` |
| **missing** | naniar, mice, VIM | `Rscript scripts/install-missing.R` |
| **mixed** | lme4, lmerTest, geepack, broom.mixed | `Rscript scripts/install-mixed.R` |
| **bayes** | brms, rstan, bayesplot, loo, BayesFactor, bridgesampling | `Rscript scripts/install-bayes.R` |

Additional packages installed on demand: survival, survminer, cmprsk, survRM2, epitools, epiR, MatchIt, WeightIt, cobalt, mediation, ivreg, did, rdrobust, metafor, meta, netmeta, pwr, lavaan, semTools, semPlot, pROC, irr, psych, mgcv, quantreg, pscl, ordinal, nnet.

## Project Structure

```
openclaw-r-stats/
├── SKILL.md                    # OpenClaw skill definition
├── README.md
├── LICENSE (MIT)
├── CHANGELOG.md
├── docs/ROADMAP.md             # Full method roadmap with JSON spec examples
├── scripts/
│   ├── run-rstats.sh           # Entry point: doctor / schema / analyze
│   ├── oc_rstats.R             # Main orchestrator (82 analysis routes)
│   ├── install-*.R             # Package profile installers
│   └── ...
├── R/                          # 12 analysis modules
│   ├── tests.R                 # t-test, ANOVA, Wilcoxon, chi-square, etc.
│   ├── regression.R            # Linear, logistic, Poisson
│   ├── survival.R              # KM, Cox, competing risks, RMST
│   ├── epi.R                   # OR, RR, IRR, MH, NNT
│   ├── mixed.R                 # LMM, GLMM, GEE, ICC
│   ├── causal.R                # PSM, IPTW, mediation, IV, DiD, RDD
│   ├── bayesian.R              # brms, Bayes factors
│   ├── advanced.R              # GAM, quantile, robust, ZIP, ordinal, multinomial
│   ├── meta.R                  # Meta-analysis, NMA
│   ├── power.R                 # Power/sample size
│   ├── sem.R                   # SEM, CFA, invariance, path
│   ├── diagnostic.R            # ROC, Bland-Altman, kappa, alpha
│   └── ...
├── examples/
│   ├── data/                   # 20+ example datasets
│   └── specs/                  # 49 example JSON specs
└── output/                     # Generated results (gitignored)
```

## Roadmap

82 methods are implemented. Next priorities:

**v0.8 — Usability + Integration**
- Quarto/HTML publication-ready report export ([#11](https://github.com/CuiweiG/openclaw-r-stats/issues/11))
- Typed OpenClaw plugin with schema validation ([#12](https://github.com/CuiweiG/openclaw-r-stats/issues/12))
- MCP server for cross-platform agent integration ([#13](https://github.com/CuiweiG/openclaw-r-stats/issues/13))
- Automated method selection advisor ([#15](https://github.com/CuiweiG/openclaw-r-stats/issues/15))

**v0.9 — Ecosystem**
- CI/CD with GitHub Actions · pkgdown docs site · ClawHub listing · R package (CRAN/r-universe)

**v1.0 — Production**
- Unit test suite · Error recovery · Streaming output · Multilingual reports

See [GitHub Issues](https://github.com/CuiweiG/openclaw-r-stats/issues) and [CONTRIBUTING.md](docs/CONTRIBUTING.md) for details.

## Contributing

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).
