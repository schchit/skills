# Installation Guide

## Prerequisites

- **R >= 4.1** ([download](https://cran.r-project.org/))
- **bash** (Git Bash on Windows, native on macOS/Linux)
- **Rtools** (Windows only, required for Bayesian/brms — [download](https://cran.r-project.org/bin/windows/Rtools/))

## Quick Install (core only)

```bash
# 1. Clone
git clone https://github.com/CuiweiG/openclaw-r-stats.git
cd openclaw-r-stats

# 2. Install core R packages
Rscript scripts/install-core.R

# 3. Verify
bash scripts/run-rstats.sh doctor

# 4. Run a test
bash scripts/run-rstats.sh analyze --spec examples/specs/regression_mtcars.json
```

## Package Profiles

Install only what you need:

| Profile | Command | Methods enabled |
|---------|---------|-----------------|
| **core** | `Rscript scripts/install-core.R` | t-test, ANOVA, correlation, regression, EDA |
| **forecast** | `Rscript scripts/install-forecast.R` | ARIMA, ETS |
| **missing** | `Rscript scripts/install-missing.R` | MICE imputation, MCAR test |
| **mixed** | `Rscript scripts/install-mixed.R` | LMM, GLMM, GEE, ICC |
| **bayes** | `Rscript scripts/install-bayes.R` | brms, Bayes factors (requires Rtools on Windows) |
| **survival** | `Rscript scripts/install-survival.R` | KM, Cox, competing risks, RMST, epi measures |
| **causal** | `Rscript scripts/install-causal.R` | PSM, IPTW, mediation, IV, DiD, RDD |
| **advanced** | `Rscript scripts/install-advanced.R` | GAM, quantile, robust, zero-inflated, ordinal, multinomial |
| **meta** | `Rscript scripts/install-meta.R` | Meta-analysis, network meta |
| **power** | `Rscript scripts/install-power.R` | Power/sample size calculations |
| **sem** | `Rscript scripts/install-sem.R` | SEM, CFA, measurement invariance |
| **diagnostic** | `Rscript scripts/install-diagnostic.R` | ROC/AUC, Bland-Altman, kappa, alpha |

## Install Everything

```bash
for script in scripts/install-*.R; do Rscript "$script"; done
```

## Docker

```bash
docker build -t openclaw-r-stats docker/
docker run --rm -v $(pwd):/work openclaw-r-stats \
  bash scripts/run-rstats.sh analyze --spec /work/examples/specs/regression_mtcars.json
```

## Windows Notes

- Use **Git Bash** (bundled with Git for Windows) to run shell scripts
- For Bayesian analysis (brms), install **Rtools 4.5+** from CRAN
- The `run-rstats.sh` script auto-detects Rtools and adds it to PATH

## Verify Installation

```bash
# Run all example specs
bash tests/run_all_specs.sh
```

## Use with OpenClaw

```bash
clawhub install openclaw-r-stats
# or
cp -r openclaw-r-stats ~/.openclaw/skills/r-stats
```

The agent auto-detects the skill via `SKILL.md` and can run any of the 82 analysis types.
