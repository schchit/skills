# Validation Report

## Scope

This report records end-to-end validation runs executed against real project samples derived from the historical quotation corpus.

## Validation Cases

### Case 1: 行业 AI 魔方

- Historical total: `90,000 元`
- Generated total: `120,375 元`
- Delta: `+30,375 元`
- Delta rate: `+33.75%`
- Recognized domains: `ai`, `miniapp`, `platform`

Observed behavior:

- The workflow completed end-to-end and produced markdown, JSON, and DOCX.
- Calibration selected `profile_calibrated` for all main line items.
- Integration-heavy items such as `会员体系与支付` and `热点数据抓取与接口输出` pushed the total upward.
- The generated output still treated some high-level wording as module rows, which increases the overall estimate.

Interpretation:

- The current estimator is conservative for AI + miniapp + platform combinations.
- Integration pricing is likely overweight relative to this specific historical project.

### Case 2: 企业内部AI助手

- Historical total: `150,000 元`
- Generated total: `112,200 元`
- Delta: `-37,800 元`
- Delta rate: `-25.2%`
- Recognized domains: `ai`, `iot`

Observed behavior:

- The workflow completed end-to-end and produced markdown, JSON, and DOCX.
- The output underpriced the project relative to history.
- The line items treated consultation, data work, and knowledge-base delivery as ordinary development modules rather than higher-value consulting + deployment packages.
- The phrase `不含硬件采购` was priced as a development item and should be treated as a boundary note instead.

Interpretation:

- The current estimator undervalues AI private-deployment and consulting-heavy work.
- Boundary statements should be filtered out before line-item estimation.
- Knowledge-base deployment and data-cleaning work need their own stronger pricing priors.

## Current Conclusions

1. The end-to-end pipeline is operational.
2. Document generation is stable across markdown, JSON, and DOCX outputs.
3. Price accuracy is promising but still sensitive to requirement normalization quality.
4. The largest remaining error source is feature parsing, not rendering.

## Recommended Next Calibration Tasks

1. Filter exclusion notes such as `不含硬件采购` out of line-item estimation.
2. Add stronger pricing priors for consulting-heavy AI deployment projects.
3. Separate `integration`, `deployment`, and `consulting` into clearer estimation classes.
4. Reduce duplication between project title rows and real feature rows.
5. Add a validation harness over 5-10 historical projects to measure median absolute percentage error.
