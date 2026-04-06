---
name: clawtraces
description: "扫描本地 OpenClaw session 日志，筛选符合要求的对话，转换为 Anthropic trajectory 格式并提交到采集服务器。当用户说「采集数据」「提交日志」「扫描 session」「扫描日志」「扫描对话」「提交 trajectory」「提交数据」「查看提交记录」「clawtraces」或涉及扫描/提交本地对话记录的请求时使用此 Skill。"
user-invocable: true
---

# ClawTraces 数据采集

本 Skill 帮助用户从本地 OpenClaw 日志中采集符合要求的 session 数据，转换为 Anthropic 标准 trajectory 格式，并提交到数据收集服务器。

## 工作流程

按以下顺序执行，每一步完成后再进行下一步。

---

### 步骤 1：环境准备（认证 + 环境检查）

认证和环境检查作为一个整体自动完成，中间不需要额外提示。

#### 1.1 认证检查

```bash
python3 /{{baseDir}}/scripts/lib/auth.py
```

脚本输出 JSON，包含 `authenticated` 字段。

- **已认证**：直接进入 1.2。
- **未认证**：
  1. **必须先向用户询问手机号，等用户回复后才能继续。** 直接问："请提供你的手机号（11 位数字）"，然后 **停下来等待用户回复**。绝对不要自己编造或使用任何默认手机号。
  2. 用户回复手机号后，发送验证码：
     ```bash
     python3 -c "
     import sys; sys.path.insert(0, '/{{baseDir}}/scripts')
     from lib.auth import send_code, get_server_url
     result = send_code(get_server_url(), '<用户回复的手机号>')
     import json; print(json.dumps(result, indent=2))
     "
     ```
     其中 `<用户回复的手机号>` 替换为用户实际提供的号码。
  3. 告诉用户"验证码已发送，请查看短信并回复验证码"，然后 **再次停下来等待用户回复验证码**。
  4. 用户回复验证码后，验证：
     ```bash
     python3 -c "
     import sys; sys.path.insert(0, '/{{baseDir}}/scripts')
     from lib.auth import verify_code, save_key, get_server_url
     result = verify_code(get_server_url(), '<手机号>', '<用户回复的验证码>')
     import json; print(json.dumps(result, indent=2))
     if result.get('key'):
         save_key(result['key'])
     "
     ```
  5. 失败则提示错误并允许重试

#### 1.2 环境检查

```bash
python3 /{{baseDir}}/scripts/env_check.py
```

脚本会自动检查并修复三项配置：
- **cache-trace**：开启诊断日志（enabled + includeSystem），记录真实 system prompt
- **thinking level**：确保全局和所有 agent 的 thinkingDefault 至少为 high，提升推理质量
- **model reasoning**：确保自定义 provider 中白名单模型的 reasoning 为 true，启用推理能力

处理结果：

- **配置已正确**：无需额外操作。
- **配置被自动修改**：
  1. 将脚本输出的修改明细（`fixes` 字段）**完整展示给用户**，让用户知道对 openclaw.json 做了哪些改动
  2. 自动重启 OpenClaw：
     ```bash
     openclaw gateway restart
     ```
  3. 说明 cache-trace 仅记录重启后的新对话，之前的对话无法补充 system prompt 数据。如果当前没有重启后产生的新 session，本次扫描可能无结果，建议用户正常使用一段时间后再来采集。

#### 1.3 完成提示

- **如果 1.2 配置被修改（`changed: true`）**：本次流程到此结束，不继续后续步骤。输出：

  > ✅ 环境已就绪！cache-trace 已开启并已重启 OpenClaw。
  > 由于 cache-trace 只记录重启后的新对话，当前没有可采集的数据。
  > 请正常使用 OpenClaw 一段时间后，再运行 `/clawtraces` 采集数据。

- **如果 1.2 配置已正确（`changed: false`）**：输出以下提示，**然后停下来等待用户指令**：

  > ✅ 环境已就绪。你可以告诉我：
  > - **看看有哪些** — 先列出可用的 session，你来选择处理哪些
  > - **扫描** — 扫描并处理未提交的 session
  > - **查看提交记录** — 查看已提交的数据

  **必须等待用户回复后才能继续。** 不要自动开始扫描。用户可能用各种自然语言表达意图（如"扫描最近 3 条"、"全部扫"、"先列一下"、"帮我扫"等），根据语义判断进入步骤 2 的哪个分支。

---

### 步骤 2：扫描 + 生成记录

根据用户指令选择对应的执行模式。

#### 模式 A：先列清单再选择

**触发**：用户说"看看有哪些"、"列一下"、"有几条"等想先了解情况的表达。

**2a-1. 列出可用 session**

```bash
python3 /{{baseDir}}/scripts/scan_and_convert.py --list-only
```

脚本输出 JSON 数组，每项包含 `session_id`、`agent_id`、`model`、`modified`（时间）、`file_size_kb`、`topic`（第一条用户消息摘要）、`has_cache_trace`（是否有 cache-trace 数据）。已按时间倒序排列（最新在前）。

将结果以表格形式展示给用户（序号、时间、模型、摘要），然后**等待用户选择**。例如：

> 找到 8 个可处理的 session：
>
> | # | 时间 | 模型 | 摘要 |
> |---|------|------|------|
> | 1 | 2026-04-04 10:30 | claude-opus-4-6 | 帮我把这个 React 组件重构一下... |
> | 2 | 2026-04-03 16:20 | claude-sonnet-4-6 | 分析一下这份 CSV 数据的趋势 |
> | ... | | | |
>
> 你想处理哪些？可以说"全部"、"前 3 个"、"第 1、3、5 个"等。

**如果列表为空**：输出无可用数据的提示，流程结束。

**2a-2. 按用户选择处理**

用户可能说：
- "全部" → 不传 `--sessions`，走默认全量处理
- "前 N 个" / "最近 N 条" → 从清单取前 N 个 session_id
- "第 1、3、5 个" → 从清单取对应序号的 session_id
- 直接给 session_id → 直接使用

确定要处理的 session_id 列表后，执行：

```bash
python3 /{{baseDir}}/scripts/scan_and_convert.py --sessions <id1> <id2> <id3>
```

#### 模式 B：直接扫描

**触发**：用户说"扫描"、"全部扫"、"帮我扫"等直接开始的表达。

**先执行预检**，用 `--list-only` 快速获取可用数量：

```bash
python3 /{{baseDir}}/scripts/scan_and_convert.py --list-only
```

根据返回的数组长度决定下一步：

- **≤ 20 条**：直接执行全量扫描，无需额外确认：
  ```bash
  python3 /{{baseDir}}/scripts/scan_and_convert.py
  ```

- **> 20 条**：展示数量和日期范围，建议用户缩小范围。从返回的 JSON 数组中取第一条（最新）和最后一条（最早）的 `modified` 字段：

  > 找到 {N} 个可处理的 session（{最早日期} ~ {最近日期}）。
  > 全量处理会消耗较多 token，建议缩小范围：
  > - **全部处理** — 一次性处理全部 {N} 条
  > - **最近 N 条** — 例如"最近 10 条"
  > - **按日期** — 例如"从 4 月 1 号开始"
  >
  > 你想怎么处理？

  **等待用户回复后**，根据用户选择走模式 B（全量）、C（`--limit`）或 D（`--since`）。

#### 模式 C：扫描指定数量

**触发**：用户说"扫描最近 3 条"、"处理 5 个"等指定数量的表达。

直接使用 `--limit` 参数，无需先 `--list-only`：

```bash
python3 /{{baseDir}}/scripts/scan_and_convert.py --limit <N>
```

#### 模式 D：按日期范围扫描

**触发**：用户说"扫描最近一周的"、"只要 4 月的"、"从 3 月 20 号开始"等指定日期范围的表达。

将用户的日期表达转换为 YYYY-MM-DD 格式，使用 `--since` 参数：

```bash
python3 /{{baseDir}}/scripts/scan_and_convert.py --since <YYYY-MM-DD>
```

`--since` 可与 `--limit` 组合使用。例如"最近一周的前 5 条"：

```bash
python3 /{{baseDir}}/scripts/scan_and_convert.py --since 2026-03-29 --limit 5
```

#### 扫描结果处理（所有模式共用）

脚本会自动：
- 按硬性规则过滤（模型、轮次 > 5、领域分类）
- 按数字指标过滤（用户消息平均长度、工具调用、长消息数）
- 从 cache-trace 提取真实 system prompt（自动模式下无数据则跳过；`--sessions` 显式指定时使用重建 prompt）
- 生成 .trajectory.json 文件
- 输出 candidates.json（含每个候选的用户消息，供语义初审）

**如果候选数量为 0**：本次流程结束，不继续后续步骤。输出：

> 本次扫描未发现新的可采集数据。可能的原因：所有符合条件的 session 已提交或已初审，或没有使用支持的模型（claude-sonnet-4-6 / claude-opus-4-5 / claude-opus-4-6）的对话。

**如果有候选**：展示扫描结果（候选数量、每个 session 的模型和轮次），然后继续步骤 3。

---

### 步骤 3：语义初审 + 领域分类（合并为一次判断）

读取 `output/candidates.json` 文件，对每个候选 session 的 `user_messages` 字段完成两个判断：

1. **初审判定**：PASS 或 FAIL（这是系统自动初审，不代表最终人工审核结果）
2. **领域分类**：从 13 个领域中选择最匹配的一个

#### 分批审核

为控制单次上下文消耗，当候选数量 **超过 15 个**时，**必须分批审核**：

1. 将 candidates.json 按每批 15 个分组
2. 每批读取对应范围的候选（例如第 1-15 个、第 16-30 个...），逐批完成初审判定和领域分类
3. 每批审核完成后立即执行该批的后续处理（更新 stats / 调用 reject.py），再进入下一批
4. 所有批次处理完毕后，汇总结果进入步骤 4

候选数量 ≤ 15 个时，一次性处理即可。

#### 初审判定标准

**合格（PASS）** — 满足以下任一条件：
- 用户围绕一个明确的任务目标在与 AI 协作（如开发功能、分析数据、撰写文档、解决技术问题等）
- 对话涉及特定领域的专业知识探讨（如编程、系统运维、数据分析、金融、内容创作等）
- 用户在进行有深度的信息调研或方案设计
- 对话体现了多轮迭代推进的工作过程（需求描述 → 方案讨论 → 执行 → 调整）

**不合格（FAIL）** — 满足以下任一条件：
- 用户消息几乎全是简单指令（"继续"、"好的"、"下一个"），没有实质性需求描述
- 对话内容是闲聊、打招呼、测试 AI 能力（"你是谁"、"讲个笑话"、"hello"）
- 用户在做重复性的简单操作，没有专业知识深度
- 对话内容涉及不当、违规或纯粹无意义的灌水

#### 领域分类（13 选 1）

根据用户消息的核心意图，从以下 13 个领域中选择最匹配的：

| ID | 名称 | 判定要点 |
|----|------|---------|
| `development` | 软件开发与工程 | 写代码、调试、测试、Git 操作、架构设计 |
| `system_admin` | 系统运维与管理 | 装软件、配服务器、管文件、网络/防火墙 |
| `data_analysis` | 数据分析与建模 | 数据清洗、统计、可视化、机器学习 |
| `research` | 研究与信息检索 | 调研、对比方案、文献查找、行业分析 |
| `content_creation` | 内容与文案创作 | 写文章、翻译、润色、报告、营销文案 |
| `communication` | 通信与消息管理 | 飞书/微信/邮件/Telegram 消息收发 |
| `media_processing` | 多媒体内容处理 | 图片/视频/音频处理、OCR、TTS |
| `automation` | 工作流与智能体编排 | 自动化脚本、定时任务、pipeline、agent |
| `monitoring` | 系统监控与诊断 | 监控告警、日志分析、性能诊断、健康检查 |
| `scheduling` | 日程与任务管理 | 日程安排、待办、提醒、日报周报 |
| `knowledge_mgmt` | 知识与记忆管理 | 笔记、知识库、归档、RAG 检索 |
| `finance` | 金融与量化交易 | 股票/基金/加密货币、量化策略、回测 |
| `crm` | 客户与业务运营 | 客户管理、销售、电商、订单运营 |

**判定原则**：基于用户的核心意图而非表面关键词。例如「用 Playwright 截图对比监控网页变化」核心意图是监控，应分类为 `monitoring` 而非 `development`。详细的边界判定规则参考 `showcase/domain-categories.md`。

#### 输出格式

对每个候选输出：
- **初审结果**：PASS 或 FAIL + 简短理由（不超过 20 字）。注意：展示时必须使用「初审结果」而非「审核结果」，以明确这是系统自动初审，提交后还需经过人工终审
- **领域**：13 个 ID 之一（仅 PASS 的需要）
- **标题**：一句话概括该 session 的核心任务（不超过 30 字，仅 PASS 的需要）。例如「为 React 项目添加用户认证模块」「分析 Q1 销售数据并生成可视化报告」

#### 后续处理

**对于初审 PASS 的候选**：将领域分类和标题写入 stats 文件（trajectory 文件保持纯净不修改）：

```bash
python3 -c "
import sys, os; sys.path.insert(0, '/{{baseDir}}/scripts')
from lib.paths import get_default_output_dir
import json
path = os.path.join(get_default_output_dir(), '{session_id}.stats.json')
with open(path) as f: s = json.load(f)
s['domain'] = '{domain_id}'
s['title'] = '{title}'
with open(path, 'w') as f: json.dump(s, f, ensure_ascii=False, indent=2)
"
```

对所有 PASS 的候选批量执行上述更新。

**对于初审 FAIL 的候选**：运行以下命令记录拒绝并删除 trajectory 文件（支持批量）：

```bash
python3 /{{baseDir}}/scripts/reject.py \
  --sessions 'session_id_1:拒绝理由1' 'session_id_2:拒绝理由2'
```

将实际的 session_id 和理由替换进去。脚本会自动删除对应的 .trajectory.json 文件并记录到 manifest.json 的 `rejected` 字段，下次扫描会跳过这些 session。

**如果所有候选均 FAIL**：本次流程结束，不继续步骤 4。输出：

> 本次初审的所有候选均未通过语义质量检查，没有可提交的数据。

---

### 步骤 4：提交

展示通过初审的最终待提交列表，格式如下：

```
找到 N 条可提交的日志：

  1. 为 React 项目添加用户认证模块  | 软件开发 | 8 轮
  2. 分析 Q1 销售数据并生成报告    | 数据分析 | 12 轮

是否确认提交这 N 条记录？
```

每条展示标题、领域名称和轮次，不再展示 session_id。

**必须等待用户明确确认后才能提交。**

用户确认后运行：

```bash
python3 /{{baseDir}}/scripts/submit.py
```

提交完成后展示：本次提交数量 + 你累计已提交的数量（注意：这是当前用户个人的提交总数，不是全平台的）。并提示用户可以说「查看提交记录」来查看历史提交。

提交脚本的输出中包含 `workspace_threshold`、`workspace_submitted` 字段，用于判断是否触发步骤 4.5。

---

### 步骤 4.5：Workspace 配置采集（条件触发）

**触发条件**：步骤 4 提交完成后，如果满足以下两个条件则触发：
1. 用户累计提交数量 ≥ `workspace_threshold`（阈值由服务端控制）
2. `workspace_submitted` 为 false（尚未提交过 workspace）

如果不满足条件，静默跳过此步骤。

**触发后**：

#### 4.5.1 征询同意

告知用户：

> 你已提交 {count} 条数据（达到 {threshold} 条阈值）。为提升数据质量，我们希望额外采集你的 Workspace 配置文件（SOUL.md、USER.md 等）。这是一次性采集，所有文件会在本地自动脱敏后再提交。是否同意？

**等待用户确认。** 用户拒绝则跳过此步骤。

#### 4.5.2 本地打包 + 脱敏

用户同意后，先执行打包（不上传）：

```bash
python3 /{{baseDir}}/scripts/workspace_bundle.py --bundle-only
```

脚本输出 JSON，包含每个 workspace 的打包结果和脱敏报告：
- `workspaces[].zip_file` — 生成的 zip 文件名
- `workspaces[].zip_size` — 文件大小
- `workspaces[].scrub_report.total_redactions` — 脱敏替换总数
- `workspaces[].scrub_report.by_category` — 按类别统计（如 `{"手机号": 2, "邮箱": 1}`）
- `workspaces[].scrub_report.files_scrubbed` — 被脱敏的文件列表及各自的替换详情

#### 4.5.3 展示脱敏信息，确认提交

**必须将脱敏信息展示给用户**，让用户了解隐私处理情况：

- 如果有脱敏操作（`total_redactions > 0`）：

  > 打包完成。以下文件中检测到敏感信息并已自动脱敏：
  >
  > | 文件 | 脱敏项 |
  > |------|--------|
  > | SOUL.md | 手机号 ×2, 邮箱 ×1 |
  > | memory/user_profile.md | API Key ×1 |
  >
  > 共 {total} 处敏感信息已替换为占位符（如 `[PHONE]`、`[EMAIL]`），原始内容不会上传。
  > 是否确认提交？

- 如果没有脱敏操作（`total_redactions == 0`）：

  > 打包完成，未检测到需要脱敏的敏感信息。是否确认提交？

**等待用户确认。**

#### 4.5.4 上传

用户确认后执行上传：

```bash
python3 /{{baseDir}}/scripts/workspace_bundle.py --upload-only
```

展示上传结果（成功/失败的 workspace 数量）。

---

### 步骤 5：查询（可选）

如果用户想查看已提交的记录：

```bash
python3 /{{baseDir}}/scripts/query.py [--page N]
```

展示已提交的 session 列表（标题、领域、轮次、提交时间），默认每页 100 条。

---

### 步骤 6：重新提交（独立操作）

当用户明确要求"重新提交"某条记录时使用。**必须提供 session_id**，不提供则要求用户补充。

此操作会重新转换该 session 并强制覆盖服务端已有记录（trajectory 文件、metadata、stats 全部覆盖）。

#### 流程

1. 确认认证状态（同步骤 1.1）
2. 用户提供的 session_id 对应的 trajectory 文件必须已存在于 `output/` 目录。如果不存在，需要先重新运行扫描转换（步骤 2）生成该文件，再继续。
3. 运行重新提交：

```bash
python3 /{{baseDir}}/scripts/submit.py --resubmit {session_id}
```

4. 展示结果（是否覆盖成功、累计提交数）。

**注意**：此步骤仅在用户明确说"重新提交 xxx"时触发，正常的批量提交流程（步骤 2-4）不会使用 force 参数。

---

## 401 处理

在任何步骤中，如果 API 返回 401（unauthorized），说明 key 已失效：
1. 通知用户 key 已失效
2. 自动清除本地 key（脚本已自动完成）
3. 重新进入步骤 1.1 的认证流程（跳过 1.2 环境检查，因为环境配置不受 key 失效影响）
4. 认证成功后，从发生 401 的步骤继续执行

## 数据目录

数据文件存放在 workspace 根目录的 `.clawtraces/` 下（与 `.clawhub/` 同级），独立于 skill 安装目录，不受升级影响：

```
{workspace}/.clawtraces/
├── .env                             # API key + server URL
└── output/
    ├── candidates.json              # 扫描结果（候选 session 列表，含用户消息）
    ├── {session_id}.trajectory.json # 转换后的 Anthropic trajectory 文件
    ├── {session_id}.stats.json      # session 元数据
    └── manifest.json                # 提交记录 + 拒绝记录（已处理 session 跟踪）
```

## 注意事项

- **认证完成后必须等待用户指令**，不要自动开始扫描。用户需要主动说"扫描"或指定处理方式
- `--list-only` 是轻量操作（只读索引和文件元数据），不消耗大量资源
- `--limit N` 只处理最近 N 个 session，减少处理量和后续语义审核的 token 消耗
- `--since YYYY-MM-DD` 只处理该日期之后的 session，可与 `--limit` 组合使用
- `--sessions` 指定的 session 会跳过"最新 session"和"已提交"的自动过滤，因为用户明确选择了它们
- 扫描通过 sessions.json 索引快速过滤模型，不会读取不符合要求的 .jsonl 文件
- 全局最新的 session 在 `--list-only` 和默认模式下会被跳过（可能还在进行中），但通过 `--sessions` 显式指定时不跳过
- 用户消息中的隐私信息（Sender 身份、时间戳）会在转换时自动清除
- System prompt 从 cache-trace 提取。自动扫描模式下，无 cache-trace 数据的 session 会被跳过（历史 session）；通过 `--sessions` 显式指定的 session 会使用重建的 system prompt 作为回退
- 提交需要用户确认，确保数据授权合规
- 已提交和已拒绝的 session 不会重复处理（manifest.json 跟踪）
