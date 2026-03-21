---
name: baidu-skill-guard
version: 1.0.2
description: Intercepts all skill install requests. MUST be used before installing any skill from ClawdHub, GitHub, or other sources. Run security check API to get risk rating. Triggers on install, add, enable, download skill.
user-invocable: true
---

# Skill Guard 🛡️

Security-first skill install guardian protocol. **Never install a skill without running security check first.**

## ⛔ MANDATORY INTERCEPTION RULE

**This skill MUST be triggered whenever a user uses ANY of the following phrases (in any language):**

```
TRIGGER PHRASES (exact or fuzzy match):
─────────────────────────────────────────
• "install skill" / "安装技能" / "安装 skill" / "帮我安装"
• "add skill" / "添加技能" / "添加 skill"
• "enable skill" / "启用技能" / "启用 skill"
• "download skill" / "下载技能" / "下载 skill"
• "clawhub install" / "npx clawhub install"
• "resolve skill" / "get skill" / "获取技能"
• "try this skill" / "试试这个 skill" / "用这个技能"
• "scan skill" / "扫描技能" / "扫描 skill" / "帮我扫描"
• "check skill safety" / "检查技能安全" / "检查 skill 安全"
• "scan all skills" / "扫描所有技能" / "扫描全部 skill"
• "scheduled scan" / "定时扫描" / "定时任务扫描 skill" / "开启定时任务扫描"
• "install this skill: https://..." / "安装这个 skill: https://..." / "帮我安装这个 skill: https://..."
─────────────────────────────────────────
```

**When triggered, you MUST follow this exact sequence:**

1. **STOP** — do NOT execute `clawhub install`, `clawhub resolve`, `npx clawhub install` or any install/download command yet
2. **FIRST run the Guardian Protocol** (Step 1 → Step 2 → Step 3 below)
3. **Show the security report** to the user
4. **Then decide**:
   - ✅ SAFE → proceed with install automatically
   - ⚠️ CAUTION → warn user and wait for explicit confirmation
   - ❌ DANGEROUS / ❓ NOT INDEXED / 🚫 ERROR → do NOT install, advise user accordingly

> 🚨 **NO EXCEPTIONS. Do not skip this protocol. Do not install first and check later.**

## When to Use

- Before installing any skill from ClawdHub
- Before running skills from GitHub repos
- When evaluating skills shared by other agents
- Anytime you're asked to install, add, enable, or download any skill
- When asked to scan a specific installed skill for security risks
- When asked to scan all installed skills
- When setting up scheduled security scans for skills

## Guardian Protocol

### Step 1: Identify the Skill (MANDATORY)

Before executing any install command, you **MUST** first confirm:

```
- [ ] What is the skill's slug (unique identifier)?
- [ ] What is the skill's version (optional)?
- [ ] Where does it come from? (ClawdHub / GitHub / other)
```

If the user only provides a name (not a slug), search to confirm the slug first, **but do NOT run any install command**.

### Step 2: Run API Security Check (MANDATORY — Core Step)

**Before installing, you MUST run the security check script.** Use `scripts/check.js` to call the security API:

**Scenario A: Query by slug (for direct install by name — A1)**

```bash
node scripts/check.js --slug "skill-slug" [--version "1.0.0"]
```

**Scenario B: Upload directory for scan (for link install — B1, scan — B2)**
- **B1** (link install): Download the zip to a temp directory first, then use `--action scan --file`
- **B2** (scan specific skill): Locate the installed skill directory, then use `--action scan --file`

```bash
node scripts/check.js --action scan --file "/path/to/skill" [--slug "skill-name"] [--version "1.0.0"]
```

**Scenario C: Batch scan all skills in a directory (for C1/C2 — full scan / scheduled scan)**
- **Note**: Batch scanning may take a long time. Each skill takes approximately 5 minutes to scan. Do not stop the task during scanning.
- **Note**: `/path/to/skills` represents the `skills` directory of OpenClaw.
- **C1** (scan all skills): Use `--action scanfull --file` with the `/path/to/skills` parent directory to batch-scan all subdirectories and produce a Batch Report
- **C2** (scheduled scan): Same as C1 but triggered by a scheduled mechanism (e.g. cron)

```bash
node scripts/check.js --action scanfull --file "/path/to/skills"
```

> ⚠️ Skipping this step and installing directly violates the security protocol.

The script outputs JSON to stdout. **Exit code**: 0 = safe, 1 = non-safe or error.

**Scenario A** (`--slug` query) — `<skill_item>` is in `data[]`:
```json
{ "code": "success", "data": [ { <skill_item> } ] }
```

**Scenario B** (`--action scan`) — `<skill_item>` is in `data.results[]`:
```json
{ "code": "success", "data": { "task_id": "...", "status": "done", "results": [ { <skill_item> } ] } }
```

**Scenario C** (`--action scanfull`) — batch report with summary counts and per-skill results:
```json
{
  "code": "success",
  "msg": "scanfull completed",
  "ts": 1234567890,
  "total": 5,
  "safe_count": 3,
  "danger_count": 1,
  "caution_count": 0,
  "error_count": 1,
  "results": [
    { "skill": "skill-dir-name", "code": "success", "msg": "success", "ts": 1234567890, "data": { "task_id": "...", "status": "done", "results": [ { <skill_item> } ] } },
    { "skill": "another-skill", "code": "error", "msg": "...", "ts": 1234567890, "data": null }
  ]
}
```

Each `<skill_item>` fields — use `bd_confidence` for verdict, detail sections for report:
- `slug`, `version`, `source`, `sha256`, `scanned_at`
- `bd_confidence` (`safe` / `caution` / `dangerous`), `bd_describe`
- `detail.github` (`name`, `account_type`, `created_at`, `followers`) — absent for uploaded skills, show N/A
- `detail.openclaw` (`oc_status`, `oc_describe`, `oc_dimensions[]`, `oc_guidance`)
- `detail.virustotal` (`vt_status`, `vt_describe`)
- `detail.antivirus` (`total_files`, `virus_count`, `virus_details`)
- `detail.skillscanner` (`risk_status`, `max_severity`, `findings[]`, `severity_counts`, `llm_overall_assessment`, `llm_primary_threats[]`)

> If `slug` is empty (common in scan), use the filename (minus `.zip`) as the display name.

### Step 3: Show Security Report (MANDATORY — Must show before install)

Based on the API result, you **MUST** show the user a security report **before deciding whether to proceed with installation**.

**单个 Skill 报告：**

根据 `bd_confidence` 判断结果，使用对应的报告模板：

**R1 — 判断"✅ 白名单(可信)，可安全安装"：**

```
🛡️ Skill安全守卫报告
═══════════════════════════════════════
📊守卫摘要
评估时间：[YYYY-MM-DD HH:mm:ss]
Skill名称: [name]
来    源: [ClawdHub / GitHub / 其他]
作    者: [author]
版    本: [version]
评估结果： ✅ 白名单(可信)，可安全安装

🗒安全评估详情
[bd_describe 内容]

───────────────────────────────────────
🏁 最终裁决: [✅ 安全安装 / ⚠️ 谨慎安装(需人工确认) / ❌ 不建议安装]


═══════════════════════════════════════
```

**R2 — 判断"⚠️ 灰名单(谨慎)，需人工确认，谨慎安装"：**

```
🛡️ Skill安全守卫报告
═══════════════════════════════════════
📊守卫摘要
评估时间：[YYYY-MM-DD HH:mm:ss]
Skill名称: [name]
来    源: [ClawdHub / GitHub / 其他]
作    者: [author]
版    本: [version]
评估结果： ⚠️ 灰名单(谨慎)，需人工确认，谨慎安装

───────────────────────────────────────
📕评估结果概述
[⚠️Skill存在信誉风险，发现[X]项可疑行为/⚠️Skill存在信誉风险]
───────────────────────────────────────
🗒安全评估详情
[bd_describe 内容]

评估过程
• VirusTotal 扫描结果：[vt_status]，[除Benign外，需要填写[vt_describe]]
• OpenClaw 扫描结果：[oc_status]，[除Benign外，需要填写[oc_describe]]
• [发现[severity]行为，[title]，[description]]
• [发现[severity]行为，[title]，[description]]
• 病毒扫描结果：未检测到病毒

───────────────────────────────────────
🏁 最终裁决: ⚠️ 谨慎安装(需人工确认)

💡 建议: [具体建议说明]

═══════════════════════════════════════
```

**R3 — 判断"🚫 黑名单(危险) ，❌ 不建议安装"：**

```
🛡️ Skill安全守卫报告
═══════════════════════════════════════
📊守卫摘要
评估时间：[YYYY-MM-DD HH:mm:ss]
Skill名称: [name]
来    源: [ClawdHub / GitHub / 其他]
作    者: [author]
版    本: [version]
评估结果： 🚫 黑名单(危险) ，❌ 不建议安装

───────────────────────────────────────
📕评估结果概述
[🚫Skill信誉高，发现[X]项危险行为，发现[X]项病毒风险/🚫Skill信誉中等，发现[X]项危险行为，发现[X]项病毒风险/🚫Skill信誉低，发现[X]项危险行为，发现[X]项病毒风险/❓Skill未收录，发现[X]项危险行为，[X]项病毒风险]
───────────────────────────────────────
🗒安全评估详情
[bd_describe 内容]

评估过程
• VirusTotal 扫描结果：[[vt_status]，[除Benign外，需要填写[vt_describe]]/无扫描结果]
• OpenClaw 扫描结果：[[oc_status]，[除Benign外，需要填写[oc_describe]]/无扫描结果]
• [发现[severity]行为，[title]，[description]]
• [发现[severity]行为，[title]，[description]]
• 发现[virus_name][file]/病毒扫描结果：未检测到病毒
• 发现[virus_name][file]

───────────────────────────────────────
🏁 最终裁决: ❌ 不建议安装

💡 建议: [具体建议说明]

═══════════════════════════════════════
```

**R4 — 判断"❓ 未收录，不建议安装"：**

```
🛡️ Skill安全守卫报告
═══════════════════════════════════════
📊守卫摘要
评估时间：[YYYY-MM-DD HH:mm:ss]
Skill名称: [name]
来    源: [ClawdHub / GitHub / 其他]
作    者: [author]
版    本: [version]
评估结果： [❓ 未收录，不建议安装]

───────────────────────────────────────
📕评估结果概述
❓Skill未收录，未发现行为与病毒风险
───────────────────────────────────────
🗒安全评估详情
[bd_describe 内容]

评估过程
• VirusTotal 扫描结果：无扫描结果
• OpenClaw 扫描结果：无扫描结果
• 危险行为检测：未发现危险行为
• 病毒扫描结果：未检测到病毒

───────────────────────────────────────
🏁 最终裁决: ❌ 不建议安装

💡 建议: [具体建议说明]

═══════════════════════════════════════
```

**批量 Skill 报告（用于 C1 / C2 — 全量扫描）：**

展示汇总头部，按裁决结果分组。

```
🛡️ Skill安全守卫报告
═══════════════════════════════════════

📊守卫摘要
评估时间：[YYYY-MM-DD HH:mm:ss]
评估Skills总量：XX个
 ✅通过：XX个
 🚫不通过：X个
 ⚠️需关注：X个
═══════════════════════════════════════
🚫不通过Skills不建议安装，具体检查结果如下：

（对每个不通过的skill，按上方「R3 黑名单」或「R4 未收录」报告格式展示完整报告）

═══════════════════════════════════════
⚠️需关注Skills需谨慎安装，具体检查结果如下：

（对每个需关注的skill，按上方「R2 灰名单」报告格式展示完整报告）

═══════════════════════════════════════
```

## Risk Level & Verdict Mapping

| bd_confidence | 评级 | 裁决 | 建议 |
|:---:|:---:|:---:|:---|
| safe | ✅ 白名单(可信) | ✅ 安全安装 | 已通过安全检查，可安全安装 |
| caution | ⚠️ 灰名单(谨慎) | ⚠️ 谨慎安装(需人工确认) | 存在潜在风险，建议人工审查后再安装 |
| dangerous | 🚫 黑名单(危险) | ❌ 不建议安装 | 发现严重安全风险，强烈建议不要安装 |
| (未收录) | ❓ 未收录 | ❌ 不建议安装 | 尚未被安全系统收录，不建议安装 |
| (服务异常) | 🚫 服务异常 | ❌ 暂缓安装 | 安全检查服务不可用，请稍后重试，不要跳过检查 |

## Important Notes

- No skill is worth compromising security
- When in doubt, don't install
- Delegate high-risk decisions to human judgment
- Document check results for future reference
- When API call fails (timeout, network error, etc.), the script returns `"code": "error"` with exit code 1 — verdict is **❌ Hold off**, advise user to retry later, do not skip the check

---

*Security is the bottom line, not an option.* 🛡️🦀