# Contributing to openclaw-r-stats

Thanks for your interest. This project aims to bring rigorous statistical analysis to the AI agent ecosystem. Contributions that uphold statistical integrity are welcome.

## Ground Rules

### Statistical Standards (non-negotiable)

These rules apply to all analysis code and reporting:

1. **Never report only p-values.** Every test must include effect sizes and confidence intervals.
2. **Never claim causality from observational data.** Use "associated with," "evidence suggests," or "estimated effect."
3. **Always check assumptions.** Normality, homoscedasticity, multicollinearity — test them, report them, warn on violations.
4. **No fishing.** Do not add analyses that silently run dozens of tests without user intent.
5. **Default conservative.** When in doubt, understate rather than overstate findings.

If your PR violates any of these, it will be rejected regardless of code quality.

### Code Standards

- All analysis logic goes in `R/` as modular functions
- All analyses are driven by JSON specs — no ad-hoc inline R
- Every analysis must produce: `summary.json`, `report.md`, `session_info.txt`, `executed_spec.json`
- Every analysis must set a random seed for reproducibility
- No internet access during analysis execution
- No package installation during analysis execution

## How to Contribute

### Adding a New Analysis Type

1. **Create the function** in the appropriate `R/*.R` file (or a new one)
   - Function signature: `run_<type>(data, spec)` → returns `list(summary, report_lines)`
   - Include effect sizes and CIs
   - Check assumptions and warn on violations
2. **Register it** in `scripts/oc_rstats.R` switch statement
3. **Add to the analysis selection table** in `SKILL.md`
4. **Create an example spec** in `examples/specs/`
5. **Update CHANGELOG.md**

### Adding a New Diagnostic Check

1. Add the function to `R/diagnostics.R`
2. Integrate it into the relevant analysis functions
3. Ensure warnings propagate to `summary.json` and `report.md`

### Fixing a Bug

1. Describe the bug and expected behavior in the PR
2. If it affects statistical output, explain the statistical reasoning
3. Add a test case if possible

## Pull Request Process

1. Fork the repo and create a branch from `main`
2. Run `bash scripts/run-rstats.sh doctor` — all core + stats must pass
3. Run the example specs and verify output is correct
4. Update CHANGELOG.md with your changes
5. Submit a PR with a clear description

## Development Setup

```bash
# Clone
git clone https://github.com/CuiweiG/openclaw-r-stats.git
cd openclaw-r-stats

# Install R packages
Rscript scripts/install-core.R

# Verify
bash scripts/run-rstats.sh doctor

# Generate test data
Rscript scripts/generate_example_data.R

# Run an example
bash scripts/run-rstats.sh analyze --spec examples/specs/regression_mtcars.json
```

## Reporting Issues

When reporting a bug, please include:
- R version (`R --version`)
- OS and platform
- The JSON spec that triggered the issue
- The full error output
- `session_info.txt` if available

## Roadmap

82 analysis methods are implemented (v0.1–v0.7). Current priorities:

### v0.8 — Usability + Integration
- **Quarto/HTML report export** — self-contained publication-ready reports ([#11](https://github.com/CuiweiG/openclaw-r-stats/issues/11))
- **Typed OpenClaw plugin** — register `r_stats_analyze` as a typed tool with schema validation ([#12](https://github.com/CuiweiG/openclaw-r-stats/issues/12))
- **MCP server compatibility** — expose the R engine via Model Context Protocol for cross-platform agent use ([#13](https://github.com/CuiweiG/openclaw-r-stats/issues/13))
- **Automated method selection advisor** — suggest the right method from dataset + research question ([#15](https://github.com/CuiweiG/openclaw-r-stats/issues/15))

### v0.9 — Robustness + Ecosystem
- **CI/CD pipeline** — GitHub Actions running full regression test suite on each PR
- **pkgdown documentation site** — auto-generated from SKILL.md + report examples
- **ClawHub publishing** — official listing on clawhub.com
- **R package submission** — wrap core engine as an installable R package (CRAN or r-universe)

### v1.0 — Production Ready
- **Comprehensive test suite** — unit tests per function, not just integration specs
- **Error recovery** — graceful handling of convergence failures, missing packages, malformed specs
- **Streaming output** — progress updates for long-running analyses (brms, causal forest)
- **Multilingual reports** — report.md in English and Chinese

### Ongoing
- Community-requested methods (open an issue to suggest)
- Package version compatibility tracking
- Performance benchmarks for large datasets

See [GitHub Issues](https://github.com/CuiweiG/openclaw-r-stats/issues) for detailed tracking.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
