---
name: openclaw-skills-audit
version: 1.0.3
description: 面向 OpenClaw Skills 的安全审计 + 追加写日志 + 变更监控推送。
---

# Skills Audit（skills-audit）

`skills-audit` 是一个偏安全与可观测性的 skill，帮助你更安全地管理 OpenClaw 的 skills，核心包含三项能力：

1）**威胁扫描分析能力（静态）**  
2）**日志记录功能（自动生成并本地保存）**  
3）**Skills 监控与变更提醒（可选推送）**

> 本 skill 只做**静态分析**，不会执行未知 skill 的代码。

---

## 核心能力

### 1）威胁扫描分析能力（网络/危险命令/可疑文件）
通过 `skills_audit.py` 对安装后的 skill 目录做静态扫描，提取风险信号：

- **网络扫描/指标**：从文本中提取 URL/域名，并识别 `curl/wget/requests` 等外联线索
- **危险命令扫描**：`curl|sh`、`wget|bash`、`eval`、动态执行、base64 解码管道等
- **可疑文件/行为扫描**：持久化（cron/systemd 等）、敏感路径访问（`~/.ssh`、`~/.aws`、`/etc` 等）

风险输出：
- `risk.level`：`low | medium | high | extreme`
- `risk.decision`：`allow | allow_with_caution | require_sandbox | deny`
- `risk.risk_signals[]`：证据（文件 + snippet）
- `risk.network.domains[]`：提取到的域名列表

### 2）日志记录功能（Append-only NDJSON）
将每一次检测结果以 NDJSON（每行一个 JSON）追加写入本地：

- 日志：`~/.openclaw/skills-audit/logs.ndjson`（append-only）
- 状态：`~/.openclaw/skills-audit/state.json`（用于 diff：新增/变更/删除）

日志结构以 `skills-audit/log-template.json` 为准，关键点：
- 顶层包含 `md5`（skill 目录内 `SKILL.md` 的 MD5，用于完整性提示）
- `observed.install_path` 是安装路径的唯一来源
- **不包含** `source`、`approval` 字段（减少冗余/敏感信息采集范围）

### 3）Skills 监控与变更提醒（可选推送）
对 `workspace/skills` 做周期性监控，发现 **新增/变更/删除** 时生成提醒消息并可推送到企业微信。

- 无变化：不推送
- 有变化：推送一条消息（避免重复与噪音）

组件：
- `skills_watch_and_notify.py`：生成固定模板提醒文本（无变化则无输出）
- `openclaw cron add / edit`：由 OpenClaw 负责创建/更新定时任务与消息投递

提醒样式（固定，不得省略关键信息）：
- 所有“有变化”的提醒都必须使用**固定模板**输出，不能只输出“风险”或只输出 skill 名称。
- 固定模板必须至少包含以下字段，并按这个顺序保留：
  1. 标题：`【Skills 监控提醒】`
  2. 说明行：`检测到 skills 目录发生变更`
  3. 变更分组：按 `【新增】` / `【变更】` / `【删除】` 分段展示（仅展示有内容的分组）
  4. 每个 skill 一行，格式：`• <slug>｜风险等级：<risk_label>`
  5. 路径行：`📁 路径：<skills_dir>`
  6. 时间行：`🕒 时间：<timestamp> (<timezone>)`
  7. 审计日志行：`🧾 审计日志：<logs_path>`
- 上述 1~7 属于固定输出骨架，**不能因为模型摘要、渠道压缩、风格改写而省略**。
- 若无变化：不输出任何内容。
- 风险等级使用固定图标样式展示：
  - `🟢 低`
  - `🟢 中`
  - `🟡 高`
  - `🔴 极高`
  - `⚪ 未知`

推荐固定模板示例：

```text
【Skills 监控提醒】
检测到 skills 目录发生变更

【删除】
• weather｜风险等级：⚪ 未知

📁 路径：/root/.openclaw/workspace/skills
🕒 时间：2026-03-27 17:58:11 (Asia/Shanghai)
🧾 审计日志：/root/.openclaw/skills-audit/logs.ndjson
```

> 推送目标不写死，通过当前会话 / delivery 参数传入。

---

## 如何启动（启用）skills-audit

默认情况下本 skill **不会常驻后台**。你可以通过以下两种方式“启动/启用”它：

### 推荐方式：直接用对话文字启动（无需敲命令）

在对话框直接说一句：

> “帮我启动 skills-audit，开启每分钟监控 skills，有变更就推送到当前会话。”

推荐的新启动话术是“**推送到当前会话**”，而不是指定某个固定渠道（如企业微信）。
这样助手应当：

1. 初始化 `skills_audit.py` 所需的本地日志/状态文件
2. 使用 `openclaw cron add`（或已有任务则 `openclaw cron edit`）创建/更新定时任务
3. 将投递目标设置为**当前会话**，由 OpenClaw 自己根据当前消息上下文决定 channel / recipient

你也可以在文字里补充参数（可选）：
- 频率：`SCHEDULE="*/5 * * * *"`
- 时区：`TZ=Asia/Shanghai`
- 只巡检不推送：说明“仅落日志，不推送”
- 仅预览计划：说明“先预览，不实际创建”

> 设计原则：`skills-audit` 只负责**扫描、日志、提醒文本生成**；定时调度与消息投递由 **OpenClaw cron** 负责。

### 备用方式：手动命令启动

### 方式 1：手动扫描（首次建议）

1）初始化本地日志/状态文件：

```bash
python3 skills/skills-audit/scripts/skills_audit.py init --workspace /root/.openclaw/workspace
```

2）手动扫描一次：

```bash
python3 skills/skills-audit/scripts/skills_audit.py scan --workspace /root/.openclaw/workspace --who user --channel local
```

会生成/更新：
- `~/.openclaw/skills-audit/logs.ndjson`
- `~/.openclaw/skills-audit/state.json`

### 方式 2：后台监控（生产推荐）

使用 OpenClaw 自己的 cron 能力创建应用级定时任务（默认每分钟运行一次）。

### C）安装监控定时任务（推荐）

推荐由助手或运维用 `openclaw cron add` / `openclaw cron edit` 创建任务，而不是让 skill 自己直接写 `jobs.json`。

推荐原则：
- **skills-audit 不直接写定时任务文件**
- **OpenClaw cron 负责调度**
- **消息投递回当前会话**（由 OpenClaw 根据当前上下文决定）

如果只是本地验证，也可以直接手动运行：

```bash
python3 skills/skills-audit/scripts/skills_watch_and_notify.py --workspace /root/.openclaw/workspace
```

---

## 注意

- 本技能只做**静态分析**，不要在审计过程中执行任何未知 skill 代码。
- 当风险等级为 `high/extreme` 时，建议要求人工确认或在隔离环境中验证。
- 推荐由 OpenClaw 的 `cron add` / `cron edit` 负责定时任务写入与消息投递。
