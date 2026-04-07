---
name: siluzan-tso
description: 当判断用户可能需要以下功能时可以使用siluzan-tso这个skillGoogle,Bing,Yandex,Tiktok,Kwai等广告账户的开户，账号数据分析共享/取消共享、Google MCC 绑定/解绑、Meta BM 绑定、TikTok BC 绑定/解绑TikTok 关闭、暂停 Google 账户撤回、Google 电子邮件访问邀请）；优化报告（TSO 管理员）、报告电子邮件推送、Meta/TikTok/Bing 账户分析发票及发票结算配置文件（发票信息）；优化和智能预警；TikTok/Meta潜在客户表单完整的Google广告管理，包括附加信息、地理位置定位和搜索词，以及关键词建议。Google广告账户详细的投放数据分析。
---


# Siluzan TSO Skill
本 Skill 只保留任务边界、文档路由与执行规则。具体业务细节、参数、模板、流程与示例均以下方 references 文档为准。遇到具体业务时，先读对应 references

## 功能以及对应文档

本skill包含以下功能，实现用户要求时，请先阅读对应功能文档：
| 文档 | 功能 |
|------|------|
| `references/setup.md` | 安装、登录、配置、环境切换、更新 |
| `references/workflows.md` | 多步骤业务流程与跨命令串联场景 |
| `references/tips.md` | `--json`、Node 过滤、分页与调试技巧 |
| `references/accounts.md` | 账户列表、余额、消耗、开户记录、授权/解绑/分享/MCC/BC/BM/邮箱授权 |
| `references/open-account-by-media.md` | 各媒体开户、参数与资料要求 |
| `references/google-ads.md` | Google Ads 创建、修改、优化与管理主流程 |
| `references/reporting.md` | Siluzan TSO 优化报告（Google/TikTok）的生成、推送与查看 |
| `references/account-analytics.md` | 广告平台账户分析数据拉取与分析/诊断报告模板 |
| `references/optimize.md` | AI 优化建议记录、详情与历史查询 |
| `references/clue.md` | TikTok / Meta 线索表单 |
| `references/forewarning.md` | 智能预警规则与通知 |
| `references/finance.md` | 转账、开票、发票抬头、充值网页引导 |
| `report-templates/report-template.html` | 默认 HTML 报告样式参考 |
---

## Skill要如何使用

### 报告的生成
报告分为两种：
- （不推荐）由siluzan平台在你调用接口提交后直接异步生成的报告(调用对应命令后，会返回一条报告链接)（详情请读取：`references/reporting.md`）
  - 这种报告你无法用它来做数据分析除非用户明确要求（Siluzan平台的优化报告）
- （推荐，默认生成这种报告）由你主动拉取数据，并按照skill给出的格式，输出给用户：详情请查看（`references/account-analytics.md`）

### 广告账户相关
- 广告账户开户请阅读： `references/open-account-by-media.md`
- 广告账户管理请阅读：`references/accounts.md`
- 广告账户分析请阅读：`references/account-analytics.md`
- Google广告的创建、修改、优化、查询广告详情等广告管理相关的功能：请阅读：`google-ads.md`

### 只调用接口，最终交付的内容不需要你输出的功能
- Google广告优化记录功能(`references/optimize.md`)，这个也跟优化报告类似，你调用接口，Siluzan平台按照一定的优化逻辑自动执行，你只能查询到结果，不能控制优化流程 注意不要与`google-ads.md`中的优化流程混淆两个是互相独立的功能，`references/google-ads.md`中的优化功能更为强大，在实际的优化过程中，也推荐使用`references/google-ads.md`中提供的内容
- TikTok / Meta 线索表单请阅读：`references/clue.md`
- Siluzan平台提供的预警功能请阅读：`references/forewarning.md`
  - 预警由Siluzan平台发送，当前仅支持微信推送，如果需要自定义的通知触达端，需要安装对应插件或skill+创建定时任务来完成
- 转账、开票、发票抬头、充值网页引导请阅读：`references/finance.md`
- 
## AI 行为规范
### 如何更好的使用本skill执行任务
遵循计划，确认，执行，验证，推测用户下一步意图
1. 计划阶段：
  - 根据功能以及对应文档读取对应references
  - 根据references文件中的内容配合命令行工具提供的-h参数，来确认命令行的正确调用方式
  - 不暴露cli执行细节的前提下，输出一份计划
2. 确认阶段：在不暴露执行命令行的前提下，与用户确认关键信息
3. 执行阶段：按计划执行
4. 验证阶段：
  - 一般情况下，读取/写入的命令都是成对的。通过这两种命令的配合来进行结果验证
  - 如果是异步任务，需要你轮询读取命令，每5s一次查看任务状态，直到确认所有异步任务都有一个结果
  - 如果失败则可以查看失败具体原因，或者结合现有命令行使用其他方式进行重试，尽量让任务执行完成，而不是告诉用户任务失败就结束了。
5. 对话历史验证：
  - 如果任务前面有计划，你需要确认每个步骤都已经按计划中的内容执行完毕
6. 完成任务后的输出
  - 结合命令行工具与references文件中的说明，对用户下一步的操作进行合理预测

### 硬规范
- **不确定时读文档**：遇到不熟悉的命令，先读对应 references 文件或使用-h查看命令帮助，不要猜参数。
- **先查账户再操作**：对具体账户做操作前，先通过 `list-accounts -m [mediaType] -k [mediaCustomerId]` 确认。特别是不确定是Google/Bing/TikTok这些媒体平台中的哪一个的时候
- **使用 --json 处理数据**：需对返回数据做计算或筛选时，加 `--json`，再用 `node -e` 过滤提取（见 `references/tips.md`）。
- **不要猜测账户 ID**：`entityId` ≠ `mediaCustomerId`，两者均来自 `list-accounts`。
- **媒体类型区分大小写**：`Google`、`TikTok`、`MetaAd`、`BingV2`、`Kwai`。
- **严格禁止任何让用户执行命令的行为**：除了 `setup` 中的 `login` 命令，所有命令行工具都是交由你完全代替用户执行。禁止向用户透露任何命令行、参数或代码逻辑。
- **具体业务的额外规范**：开户、优化、报告、Google 广告创建等场景的详细约束，请分别在执行前阅读对应的 `references/*.md` 文档。
- **完成写/修改/编辑/更新等操作后需要确认数据是否正确**

### 必须一定要遵守的规范，如不遵守，会导致skill无法使用

- 在使用本skill输出的任何内容中，包括但不限于报告，计划，总结，严禁让用户执行本skill提供的命令行。（setup.md）中的命令除外
- 主动更新（详情请读取`references/setup.md`）
- 所有使用本skill获取的数据输出的报告，总结，分析性的内容，都需要通过skill中内置模板的格式来输出

## 一些tips

### 账户ID示例
用于快速确定用户发送账号的类型,xxx是脱敏处理，一般主要通过位数就能确定账号类型，无法确定再查list-account -m [mediatype] -k [id] 
Google: 4545xxx137
Tiktok: 70083497xxx59820033
Meta(Facebook): 1716030xxx734076, 6843984xxx14909, 479423xxx752348
Bing: 138xxx763， 1882xxx80
Yandex: porg-uthxxxrk
Kwai: act_1716030xxx734076

### 容易出错http状态码
- 400 Bad Request
参数错误，请你查看对应功能reference或使用-h了解命令行如何使用

- 401 Unauthorized
注意是平台方返回的还是我们自己返回的401，通常，平台方（google,bing, yandex，tiktok,kwai）返回的需要用户重新授权
如果是我们自己的接口返回的，则可以让用户 重新打开命令行执行 `siluzan-tso login`（详情请读取`references/setup.md`）

- 500 
大概率是服务可能正在部署或升级，可以让用户提交给Silizan相关人员