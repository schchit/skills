# CCDB Factor Search — Full Draft v0.1.3

Find the **best-fit CCDB / Carbonstop emission factor** for carbon accounting, carbon footprint, PCF, and LCA work — not just a raw result list.

This skill is built for the real business question most users actually have:

> **Which factor should I actually use?**

Instead of stopping at search results, this skill searches in Chinese and English, compares candidates across rounds, filters out weak or mismatched results, and returns a structured recommendation with risks, alternatives, and search trace.

---

## What this skill is good at

Use this skill when you need to:

- find the most suitable **carbon factor / emission factor** from CCDB
- support **carbon footprint / PCF / carbon accounting** work
- compare multiple factor candidates and decide which one is actually usable
- reject mismatched candidates such as wrong region, wrong unit, wrong stage, or spend-based factors
- surface the difference between **碳足迹因子** and **排放因子 / 二氧化碳排放因子**
- return a conservative `not_suitable` / `api_unavailable` result instead of forcing a weak recommendation

Typical scenarios:
- product carbon footprint (PCF)
- LCA inventory modeling
- supplier / material factor matching
- sustainability consulting delivery
- bilingual carbon factor lookup in CCDB / Carbonstop APIs

---

## Why this is better than plain search

A normal search flow often gives you **a list of possible factors**.

This skill is designed to go further:

- **bilingual search**: searches in Chinese and English, not just one language
- **iterative refinement**: broadens / narrows the search when first-pass results are weak
- **mismatch filtering**: downgrades wrong-region, wrong-unit, or spend-based candidates
- **best-fit recommendation**: selects one recommended factor when possible
- **risk-aware output**: explains caveats and shows alternatives
- **conservative fallback**: prefers `not_suitable` over a misleading answer

In short:
- plain search → “here are 10 factors”
- this skill → “this is the best candidate, here’s why, here are the risks, and here are the backups”

---

## Main capabilities

### 1. factor lookup
Search for factors by keyword in Chinese and English.

Typical use:
- 电力
- 天然气
- 原铝
- polyester chip / PET resin

### 2. factor comparison
Compare multiple candidate factors and select the best-fit one.

Typical use:
- compare carbon footprint factor vs emission factor
- compare China vs non-China candidates
- compare direct match vs fallback candidates

### 3. suitability judgment
Judge whether a candidate is safe to use directly or should be treated only as reference.

Typical use:
- reject spend-based factor when physical activity factor is needed
- flag missing region / year / unit constraints
- warn when factor type may not match the intended accounting purpose

---

## Example prompts

### Example 1 — latest China electricity factor
> 查询最新的中国全国电力因子，单位最好是 kgCO2e/kWh。

Expected behavior:
- prioritize Chinese official electricity factor candidates
- prefer the latest applicable year when the user asks for “latest / 最新”
- explain whether the chosen result is a **carbon footprint factor** or a **CO2 emission factor**

### Example 2 — bilingual material lookup
> 帮我检索聚酯切片的碳因子，如果中文结果不好就切英文继续找。

Expected behavior:
- derive terms like 聚酯切片 / PET resin / PET chip / polyester resin
- compare candidates across rounds
- return one recommended factor and alternatives

### Example 3 — conservative screening
> 请帮我找原铝的排放因子，优先物理量单位，不要误选成按金额计算的因子。

Expected behavior:
- reject or downgrade spend-based / monetary-unit candidates
- prefer physical activity factors
- explain why the chosen candidate is safer to use

### Example 4 — no guessing when evidence is weak
> 我要找英国蒸汽因子，如果查不到合适的，不要猜，直接告诉我。

Expected behavior:
- return `not_suitable` or `api_unavailable` when evidence is weak
- not fabricate a recommendation

---

## Typical use cases

### Scenario 1 — find the latest China electricity factor
User asks:
> 中国最新全国电力因子是多少？

Recommended output:
- latest China candidate
- factor type explanation
- whether it is suitable for carbon footprint or emissions accounting

### Scenario 2 — compare factor types
User asks:
> 电力碳足迹因子和电力排放因子有什么区别？

Recommended output:
- list both candidates if available
- explain factor type difference
- tell the user which one is suitable for which use case

### Scenario 3 — material factor matching
User asks:
> 帮我找聚酯切片最合适的因子。

Recommended output:
- bilingual search path
- selected candidate
- alternatives
- risk notes

### Scenario 4 — suitability review
User asks:
> 这个因子能不能直接用于正式报告？

Recommended output:
- direct-use guidance
- review recommendation
- missing constraints, if any

---

## Standard output example

```yaml
推荐结果:
  匹配等级: close_match
  因子名称: 电力
  因子值: 0.5777
  单位: kgCO2e/kWh
  适用地区: 中国
  适用年份: 2024
  来源机构: 生态环境部
  来源说明: 关于发布2024年电力碳足迹因子数据的公告

选择原因:
  - 中文词与英文词均已尝试
  - 中国地区候选优先
  - 在当前结果中年份最新且语义最贴近

风险与注意事项:
  - 这是碳足迹因子，不等同于CO2排放因子
  - 若用于温室气体核算或核查，请确认适用口径

候选备选:
  - 2023年全国电力平均碳足迹因子
  - 2023年全国电力二氧化碳排放因子

结论建议:
  - 可作为中国全国电力碳足迹口径的最新候选使用
  - 若用户要做排放核算，应改查“电力二氧化碳排放因子”
```

---

## Output fields

The final result should ideally explain these fields clearly:

- **因子名称 / name** → factor name
- **因子值 / factor value** → the numeric value of the factor
- **单位 / unit** → unit of the factor, critical for calculation
- **适用地区 / countries** → country / region where the factor applies
- **适用年份 / applyYear ~ applyYearEnd** → applicable time range
- **发布年份 / year** → publication year
- **来源机构 / institution** → publishing institution
- **来源级别 / sourceLevel** → authority level of the source
- **来源说明 / source** → source file / announcement text
- **描述 / description** → supporting context
- **规格 / specification** → more specific scenario or item scope

---

## Field guide: how to read the result

### Match classification
- `direct_match` → highly aligned; usually safe to use directly
- `close_match` → mostly aligned; should be reviewed before formal reporting
- `fallback_generic` → usable only as a temporary / generic estimate
- `not_suitable` → do not use directly
- `api_unavailable` → no recommendation; retry later

### Important fields
- **因子值 / 单位**: check whether the unit matches the intended activity data
- **适用地区**: critical for electricity / steam / gas factors
- **适用年份**: important when the user asks for latest or year-specific factors
- **来源机构 / 来源说明**: helps judge authority and reporting suitability
- **风险与注意事项**: must be read before direct use

### Direct-use guidance
- `direct_match` → usually safe for direct use after quick sanity check
- `close_match` → usually requires a human review before formal reporting
- `fallback_generic` → suitable only for rough estimate / temporary placeholder
- `not_suitable` → should not be used directly
- `api_unavailable` → retry later; do not infer a factor manually from this result alone

---

## Carbon footprint factor vs emission factor

This distinction is important and should not be ignored.

For some categories — especially electricity — the API may return both:
- **碳足迹因子 / carbon footprint factor**
- **二氧化碳排放因子 / CO2 emission factor**

They are not always interchangeable.

### Recommended handling
- if the user explicitly asks for **碳足迹 / carbon footprint / PCF**, prefer carbon footprint factors
- if the user explicitly asks for **排放因子 / CO2 emission factor / emissions accounting**, prefer CO2 emission factors
- if the user only says “电力因子” without clarifying purpose, the output should warn that multiple factor types may exist and should not be mixed directly

---

## Current API input assumptions

Current script uses a minimal request body:

```json
{
  "sign": "<md5 businessLabel+name>",
  "name": "电力",
  "lang": "zh"
}
```

Current query behavior should continue to assume that the interface is still a lightweight retrieval endpoint, so the core value of the skill remains:

1. query term design
2. bilingual expansion
3. post-query ranking
4. structured explanation

rather than strict API-side filtering.

---

## API field checklist to align in the next update

The following field understanding should be treated as the current working checklist and reflected consistently in the skill logic and contract notes:

- `year` → **发布年份**
- `applyYear` → **适用年份开始时间**
- `applyYearEnd` → **适用年份结束时间**
- `countries` → **发布国家 / 地区**
- `area` → **可忽略**
- `sourceLevel` → **来源级别**

These meanings should be used consistently in:
- ranking logic
- result explanation
- field interpretation in README
- `references/api-contract.md`

---

## Implementation direction in v0.1.3


### High priority
1. **fix raw-term truncation** so English phrases are not cut mid-word
2. **prioritize China candidates** for Chinese requests with no explicit region, especially for electricity / steam / gas
3. **add missing-region warning** for strongly geography-dependent factors
4. **add recency bonus** when the user asks for “latest / 最新”
5. **strengthen authority weighting** for official Chinese sources such as ministry / official announcement results
6. **distinguish carbon footprint factors vs emission factors** in ranking and final explanation
7. **add direct-use guidance** in the final answer so users know whether the result is safe to use directly

### Medium priority
8. sync `domain-lexicon.md` into code so more materials / fuels / logistics terms can expand bilingually
9. improve result formatting with clearer field explanations and output examples
10. expand tags / high-weight text for ClawHub search discovery:
   - `carbon`
   - `carbon-footprint`
   - `carbon-accounting`
   - `pcf`

### Nice to have
11. add automated eval runner
12. support bilingual output field labels based on input language

---

## Search discoverability on ClawHub

Current metadata already contains tags like:
- `carbon`
- `ccdb`
- `emission-factor`
- `lca`
- `sustainability`

But if ClawHub search for `carbon` still fails to surface the skill consistently, the skill should further strengthen discovery by:

- moving `carbon footprint / carbon accounting / PCF` into the earliest high-weight text
- expanding tags to include `carbon-footprint`, `carbon-accounting`, `pcf`
- making the summary and README opening more obviously carbon-oriented

---

## Runtime dependency

This skill depends on the Carbonstop CCDB API.

Current default endpoint:
- `https://gateway.carbonstop.com/management/system/website/queryFactorListClaw`

Current signing rule:
- `sign = md5("openclaw_ccdb" + name)`

Optional environment variables:
- `CCDB_API_BASE_URL`
- `CCDB_SIGN_PREFIX`

---

## Error handling / fallback behavior

This skill is intentionally conservative.

- if the API request fails, times out, or returns malformed data, it reports the failure instead of guessing
- if no suitable candidate is found, it prefers `not_suitable`
- if region / unit / year constraints are missing, it should surface that gap clearly
- if only weak candidates are available, it should return them as fallback candidates with risk notes, not as a fake direct match

This matters because **a wrong factor is often worse than no factor** in carbon accounting workflows.

---

## Known limitations

- some factor values are encrypted in the API response
- some scenarios may only yield close/fallback matches rather than direct matches
- steam-related queries may still return broader heat/steam fallback candidates depending on data coverage
- data quality and API coverage directly affect result quality
- current API request body is still minimal, so precision depends heavily on post-query ranking logic
