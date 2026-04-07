# 账户分析数据拉取与周期报告

> 所属 skill：`siluzan-tso`。
>
> 本文档说明如何通过 CLI 拉取 **Google / Meta / TikTok / Bing** 的账户分析数据，供撰写**分析报告、诊断报告**使用。  
> **TSO 平台生成的优化报告**（`report list` / `create` / `push`）见 `references/reporting.md`。

---

## 默认做法
1. 询问用户需要生成哪些维度的报告，或直接生成默认报告：包含以下维度：执行摘要、每日投放趋势、月度汇总、广告系列表现、设备分布、地域分布、关键词表现、优化建议
2. 确定报告需要如何分析请查看（`report-templates/README.md`）
3. 根据默认模板：`report-templates/report-template.html` 为样式基准来生成html 然后将html转为pdf交付
4. 输出 HTML 时：**默认**以 `report-templates/report-template.html` 为样式基准（适用于一切总结性、报告性、汇总性成稿）；若场景更适合作正式件、深色、单页等，再从 `report-templates/report-template*.html` 中选或询问用户，并对照 `report-templates/README.md`
5. 注意最终交付的是用html生成的PDF
6. 使用浏览器或能够打开html/pdf的插件帮用户打开报告

用于按账户维度拉取 Google Ads 报表、结构类数据。

## Google 账户分析数据接口

### 指标字段对照

多条报表行的原始体里，消耗类指标常用下列字段名（调用方若要做统一展示，可按此对照；**以实际响应为准**）：

| 常见展示名 | 响应中常见字段名 |
|------------|------------------|
| 消耗 | `spend` |
| 展示 | `impressions` |
| 点击 | `clicks` |
| 转化 | `conversions` |
| 点击率 | `ctr` |
| 转化率 | `conversionRate` |
| 平均点击成本 | `averageCpc` |
| 转化成本 | `costPerConversion` |

---

### google-analysis

使用已配置的 `googleApiUrl` 与 Token，无需手写 curl。

```text
siluzan-tso google-analysis <子命令> -a <mediaCustomerId> [选项]
```

**通用选项**

| 选项 | 说明 |
|------|------|
| `-a, --account` | Google `mediaCustomerId`（必填） |
| `--start` / `--end` | 统计区间；**须同传或同省略**（省略则默认近 7 天截至昨天） |
| `--json` | 输出完整响应 JSON |
| `-t, --token` | 鉴权 Token（可选，默认读配置） |
| `--verbose` | 打印详细错误 |

**子命令与网关路径对应**

| 子命令 | 说明 |
|--------|------|
| `overview` | 总览 `OverviewSectionData` |
| `keywords` | 关键词 `KeywordSectionData`；可选 `--limit`、`--no-order-by-cost` |
| `search-terms` | 搜索词 `searchtermmanagement/v2/list`；同上 |
| `campaigns` | 系列 `CampaignSectionData` |
| `ads` | 广告 `admanagement/v2/list` |
| `extensions` | 附加信息 `extensionmanagement/v2/list`；可选 `--level`（Account / Campaign / Ad Group） |
| `devices` | 设备 `DeviceSectionData` |
| `geographic` | 地域 `GeographicSectionData` |
| `audience` | 受众 `AdGroupAudienceData`；可选 `--audience-type SystemDefined \| UserDefined` |
| `asset-images` | 图片素材 `CampaignAssetView` |
| `videos` | 视频 `Videos` |
| `materials` | 合并 `CampaignAssetView` + `Videos`（一次输出 `{ images, videos }`） |
| `resource-counts` | 结构 `resource-counts` |
| `conversion-actions` | 转化动作 |
| `daily-metrics` | 按日 `reports` |
| `gold-account` | 黄金账户 `GoldAccountData` |
| `ads-index` | 质量指标 `AdsIndexData` |
| `final-urls` | 最终到达网址（**不要**传 `--start`/`--end`） |
| `dimension-summary` | 账户汇总 `reports/combined` |
| `campaign-types` | 系列类型（**不要**传 `--start`/`--end`） |

**示例**

```bash
siluzan-tso google-analysis overview -a 6326027735 --start 2026-03-01 --end 2026-03-31 --json
siluzan-tso google-analysis keywords -a 6326027735 --limit 50
siluzan-tso google-analysis final-urls -a 6326027735 --json
```

---

## Meta 账户分析总览（TSO）

```bash
siluzan-tso report meta-overview -a <mediaCustomerId> [--start YYYY-MM-DD --end YYYY-MM-DD] [--json]
```

`--start` / `--end` 须**同传或同省略**；省略时默认**近 7 天（截至昨天）**，与 `google-analysis` 日期规则一致。

响应结构可与 Google 总览类比（如 `accountId`、`totalCost`、`currentPeriod` / `previousPeriod`、`optimizationScore` 等），**以实际 JSON 为准**。

**报告模板**：`report-templates/meta-period-report.md`

---

## TikTok 账户分析（TSO）

与周期报告常见数据块对应关系见 **`report-templates/tiktok-period-report.md`**。

| 子命令 | HTTP 段 / 说明 |
|--------|----------------|
| `report tiktok-overview` | `.../OverviewSectionData?startDate=&endDate=` |
| `report tiktok-campaigns` | `.../CampaignSectionData?startDate=&endDate=&take=`（默认 `take=100`） |
| `report tiktok-ad-groups` | `.../AdGroupReport?...` |
| `report tiktok-ads` | `.../AdReport?...` |
| `report tiktok-videos` | `.../VideoReport?...` |
| `report tiktok-audience` | `.../AudienceReport?...&dimensions=` + `-d` 取值见 CLI 帮助（gender / age / interest_category 等） |
| `report tiktok-audience-merged` | 同上接口三次（`gender`、`age`、`interest_category`），**合并输出 JSON** |
| `report tiktok-areacode` | `GET {mainApiUrl}/query/media-account/tiktok/TikTokAreacode/Read` |
| `report tiktok-interest-list` | `{tiktokApiUrl}/.../GetInterestList?mediaCustomerId=`（需配置 `tiktokApiUrl`） |

**日期与鉴权**：`--start` / `--end` 须**同传或同省略**；省略时默认**近 7 天（截至昨天）**。鉴权与 TSO 其他接口相同。

**示例**

```bash
siluzan-tso report tiktok-overview -a 1234567890 --json
siluzan-tso report tiktok-campaigns -a 1234567890 --start 2026-03-01 --end 2026-03-31 --take 50 --json
siluzan-tso report tiktok-audience -a 1234567890 -d gender --json
siluzan-tso report tiktok-audience-merged -a 1234567890 --start 2026-03-01 --end 2026-03-07
siluzan-tso report tiktok-areacode --json
```

---

## Bing（BingV2）账户分析（TSO）

章节与数据块对照见 **`report-templates/bing-period-report.md`**。

**重要（日期）**：Bing 报表**不能包含「今天」或「昨天」**（接口限制，与 Web 端校验一致）。`--start` / `--end` 须**同传或同省略**；**省略时** CLI 默认区间为**截至前天**的近 7 天（避免误含昨天）。

| 子命令 | HTTP 段 / 说明 |
|--------|----------------|
| `report bing-overview` | `.../OverviewSectionData?startDate=&endDate=` |
| `report bing-device` | `.../DeviceSectionData?...` |
| `report bing-geographic` | `.../GeographicSectionData?...` |
| `report bing-age-audience` | `.../AgeAudienceData?...` |
| `report bing-gender-audience` | `.../GenderAudienceData?...` |
| `report bing-audience-merged` | 上两项并行拉取，**合并输出 JSON** |
| `report bing-campaigns` | `.../CampaignReport?...` |
| `report bing-ad-groups` | `.../AdGroupReport?...` |
| `report bing-ads` | `.../AdReport?...` |
| `report bing-keywords` | `.../KeywordReport?startDate=&endDate=&limit=&orderByCost=true`（默认 `limit=100`） |
| `report bing-search-terms` | `.../SearchQueryReport?...`（同上） |

**示例**

```bash
siluzan-tso report bing-overview -a <mediaCustomerId> --json
siluzan-tso report bing-keywords -a <mediaCustomerId> --start 2026-03-01 --end 2026-03-20 --limit 50 --json
siluzan-tso report bing-audience-merged -a <mediaCustomerId>
```

---

## 报告模板与输出形式

报告输出内容参考 **`report-templates/`**：

- `report-templates/google-period-report.md` — 单周期汇总报告章节
- `report-templates/google-account-diagnosis-report.md` — 诊断类报告章节（纲要）
- `report-templates/google-ads-diagnosis.md` — 与网页版《Google Ads 账户诊断报告》**章节与数据块对齐**的完整骨架
- `report-templates/meta-period-report.md` — Meta（Facebook）周期报告纲要（当前仅总览）
- `report-templates/tiktok-period-report.md` — TikTok 周期报告纲要（与 `report tiktok-*` 对齐）
- `report-templates/bing-period-report.md` — Bing（BingV2）分析纲要（与 `report bing-*` 对齐）
- `report-templates/README.md` — 索引与规则

`report-templates` 目录下的 `.html` 文件（如 `report-template.html`、`report-template-academic.html` 等）为**样式参考**，可先生成 HTML 再转为 PDF。

> **分析报告做法**：按 `google-period-report.md`（或对应媒体 `*.md`）中的默认维度拉数撰写，同时列出可选追加维度询问用户。**TSO 优化报告**（`report list` / `create` / `push`）不走此流程，详见 `references/reporting.md`。  
> 报告内容以各 `*.md` 纲要为准，`report-template*.html` 仅提供样式；如未另行指定，所有总结 / 报告 / 汇总类 HTML 默认对齐 `report-templates/report-template.html` 的区块结构与视觉风格。
