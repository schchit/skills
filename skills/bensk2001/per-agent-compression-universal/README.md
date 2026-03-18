请往下翻页查看中文说明

---

# Per-Agent Memory Compression Skill (Universal)

**Version**: 1.2.4  
**Purpose**: Zero-config deployment of weekly memory consolidation for multi-agent OpenClaw systems  
**Created**: 2026-03-18  
**Compatibility**: OpenClaw 2026.3.8+  
**Status**: ✅ Production Ready (lightly tested)

---

## Value Proposition

### Why You Need This

- **⏱️ Saves Hours** - Automates the tedious process of manually reviewing daily notes and updating long-term memory across multiple agents.
- **🧠 Better Memory** - Each agent maintains its own contextual memory (USER.md, IDENTITY.md, SOUL.md, MEMORY.md) tailored to its domain, leading to more relevant and personalized interactions.
- **🔄 Self-Healing** - State tracking with `.compression_state.json` means if the task fails midway, it resumes from the last successful note—no duplication, no missing data.
- **📊 Visibility** - DingTalk summary notifications tell you exactly how many notes were compressed and how many remain for future runs.
- **🚀 Zero Config** - Just run the installer; it auto-discovers all agents and creates staggered tasks. No manual YAML editing.

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Auto-Discovery** | Automatically finds all agents with workspaces via `openclaw agents list` |
| **Per-Agent Isolation** | Each agent compresses only its own `memory/` directory and updates its own config files |
| **State Persistence** | `.compression_state.json` tracks processed notes, last run time, and status |
| **Deduplication** | Before appending, checks if the note's date already exists in target files |
| **Moved-File Marking** | Processed notes are moved to `memory/processed/` for clear separation |
| **Domain Filtering** | Each task uses DOMAIN_CONTEXT (e.g., "HR/work", "parenting") to guide extraction |
| **Remaining Notes Report** | Summary announces count of old notes still pending for the next run |
| **Staggered Schedule** | Tasks run on Sundays from 03:00 to 05:00 Shanghai (30min apart) |
| **Error Isolation** | One note failing doesn't stop the whole task; errors are logged and continue |
| **DingTalk Notify** | Announces completion summary via dingtalk-connector |

---

## Installation

### Quick Start

```bash
cd /root/.openclaw/workspace
chmod +x skills/per-agent-compression-universal/install.sh
./skills/per-agent-compression-universal/install.sh
```

That's it! The installer will:
- ✅ Verify OpenClaw is running
- ✅ Discover all agents with workspaces
- ✅ Create 1 cron task per agent (staggered schedule)
- ✅ Report any issues

### What Gets Created

For each agent (e.g., `main`, `hrbp`, `parenting`, `decoration`, `memory_master`):
- A cron task named `per_agent_compression_<agent_id>` (normalized to `peragent_compression_<agent_id>` internally)
- Schedule: Sunday, every week, staggered 30 minutes apart starting at 03:00 Shanghai
- Timeout: 1200 seconds (20 minutes)
- Delivery: DingTalk announce to the configured account

---

## How It Works

### 1. Discovery
The installer runs `openclaw agents list --json` and filters agents that have a `workspace` field.

### 2. Task Creation
For each discovered agent, the installer calls:

```bash
openclaw cron add \
  --name "per_agent_compression_<agent_id>" \
  --cron "<cron_expr>" \
  --tz "Asia/Shanghai" \
  --agent "main" \
  --message "<concise_execution_plan>" \
  --model "openrouter/stepfun/step-3.5-flash:free" \
  --timeout 1200 \
  --session "isolated" \
  --announce \
  --channel "dingtalk-connector" \
  --to "05566651511149398" \
  --best-effort-deliver
```

**Note on message length**: Due to CLI constraints, the `--message` is kept concise (~1200 chars) but contains all essential logic. Full details are documented in this README. If you need the ultra-detailed version (with every step and edge case), you can manually edit the task after install:

```bash
openclaw cron edit per_agent_compression_<agent_id> --message "$(cat FULL_DETAILED_MESSAGE.txt)"
```

### 3. Execution
When the cron triggers, the `main` agent executes the task instructions:

1. **Pre-check** - Verifies workspace, `memory/` dir, target files exist
2. **Load state** - Reads `{workspace}/memory/.compression_state.json` (or initializes)
3. **List notes** - Finds `memory/*.md` matching `YYYY-MM-DD.md`, filters date < today-7, excludes already processed
4. **Sort & limit** - Oldest first, max 5 notes per run
5. **Process each note**:
   - Read full content
   - Extract: user preferences, key decisions, personal info (domain-specific)
   - Dedupe: skip if target files already have entry for this note date
   - Append to:
     - `USER.md` → under `## Personal Info / Preferences`, header `### [YYYY-MM-DD]`
     - `IDENTITY.md` → under `## Notes` (create if missing), header `### [YYYY-MM-DD]`
     - `SOUL.md` → under `## Principles` or `## Boundaries` as appropriate, header `### [YYYY-MM-DD]`
     - `MEMORY.md` → under `## Key Learnings` (create if missing), format `- [YYYY-MM-DD] <summary>`
   - Move note file to `{workspace}/memory/processed/`
   - Update state: `processed_notes.append(filename)`, `last_compressed_date = note_date`
6. **Finalize** - Save state (`last_run_at`, `status="completed"`), clean working buffer
7. **Announce** - Send summary to DingTalk: agent, count processed, remaining old notes, any errors

---

## What Gets Updated

Each agent's files are **appended only**; existing content is never overwritten.

**Example append to `MEMORY.md`**:
```markdown
## Key Learnings

- [2026-03-10] User prefers morning exercise and reads tech news before breakfast.
- [2026-03-12] Decoration project delayed due to material shortage; new timeline: April 15.
```

**Example append to `USER.md`**:
```markdown
## Personal Info / Preferences

### [2026-03-10]
- Preferred communication channel: DingTalk
- Working hours: 9:00-18:00 Beijing time
- Do not disturb: 12:00-14:00 lunch break
```

---

## Configuration

No configuration needed! But if you want to customize:

- **Schedule**: Edit the cron expression in the task (not recommended; re-run install after modifying `install.sh` offsets)
- **Timeout**: Change `--timeout` value in `install.sh` (default 1200s)
- **Delivery channel**: Modify `--channel` and `--to` in `install.sh`
- **Domain context**: Edit the `DOMAIN_CONTEXT` associative array in `install.sh` to add/change per-agent descriptions

---

## Testing & Limitations

### Known Limitations

1. **CLI message length limit**  
   `openclaw cron add --message` truncates messages > ~1KB. The skill works around this by using a concise template. For fully detailed instructions, manually edit the task post-install using `openclaw cron edit --message`.  
   **Impact**: Low—the concise template already contains all operational logic. Detailed examples are in README.

2. **No per-agent install filter**  
   The skill always discovers *all* agents. If you only want to install for one agent (e.g., `decoration`), you must either:
   - Edit `install.sh` to comment out other agents, OR
   - Run install, then immediately `openclaw cron delete` the unwanted tasks  
   **Impact**: Medium—extra manual cleanup if you need selective deployment.

3. **Requires `self-improve-agent` for full automation** (optional)  
   The skill itself does not depend on it, but if you want agents to automatically write daily notes or refine memories, you may need that separate skill.  
   **Impact**: Low—compression works without it.

4. **Memory/processed/ directory must be writable**  
   The task attempts to create `processed/` if missing. If permissions are insufficient, the task will fail on that note but continue with others.  
   **Impact**: Low—standard permissions are fine.

### Tested Scenarios

- ✅ Fresh install on clean system (no pre-existing per-agent tasks)
- ✅ Reinstall over existing tasks (skips duplicates)
- ✅ Uninstall removes all skill-created tasks
- ✅ Task payload includes all expected fields (state file, processed dir, domain context)
- ✅ Gateway logs show no errors during installation
- ✅ Daily note (2026-03-18) recorded full session for future compression

### Manual Verification

After install, verify with:
```bash
openclaw cron list | grep per_agent_compression
```

You should see 1 task per discovered agent. Check one task's message:
```bash
openclaw cron get <job_id> | jq '.payload.message'
```

Ensure the message includes:
- `DAILY_NOTES_DIR`
- `PROCESSED_DIR`
- `STATE_FILE`
- `TARGET_FILES`
- `DOMAIN_CONTEXT`
- Steps 1-7 including dedupe and remaining notes reporting

---

## Uninstall

```bash
cd /root/.openclaw/workspace
./skills/per-agent-compression-universal/uninstall.sh
```

This removes **all** `per_agent_compression_*` tasks. It will not touch other cron jobs (e.g., `proactive_notes_compression_*`).

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and detailed changes.

---

## Contributing

This skill is open for improvement. Found a bug or have an enhancement?

- **Issues**: Report via GitHub (if published) or directly to the skill author
- **Enhancements**: Feel free to fork, modify `install.sh` and `README`, and submit a PR

---

## Disclaimer

**This skill is currently in active testing.** While core functionality is stable, edge cases (e.g., message length limits, agent filtering) may require manual intervention. Use in production with the understanding that minor adjustments might be needed. Always backup your `MEMORY.md` and daily notes before first run.

---

## Support

- **Documentation**: This README and CHANGELOG
- **Community**: OpenClaw Discord (`#agent-skills` channel)
- **Direct**: Contact the skill author or repository maintainer

---

**Happy Compressing!**

---

================================================================================

以下是完整的中文说明

================================================================================

---

# 通用代理记忆压缩技能 (Per-Agent Memory Compression Universal)

**版本**: 1.2.2  
**用途**: 为多代理 OpenClaw 系统提供零配置的每周记忆整合  
**创建日期**: 2026-03-18  
**兼容性**: OpenClaw 2026.3.8+  
**状态**: ✅ 生产就绪（轻量测试）

---

## 价值主张

### 为什么你需要这个技能

- **⏱️ 节省时间** - 自动化跨多个代理的手动审查每日笔记和更新长期记忆的繁琐过程。
- **🧠 更好记忆** - 每个代理维护自己的上下文记忆（USER.md、IDENTITY.md、SOUL.md、MEMORY.md），根据其领域定制，从而实现更相关和个性化的交互。
- **🔄 自愈能力** - 使用 `.compression_state.json` 进行状态跟踪，如果任务中途失败，会从最后一个成功笔记处继续——无重复、无丢失数据。
- **📊 可见性** - 钉钉摘要通知告诉你确切压缩了多少笔记以及未来还剩多少待处理。
- **🚀 零配置** - 只需运行安装程序；它会自动发现所有代理并创建交错任务。无需手动编辑 YAML。

---

## 核心特性

| 特性 | 描述 |
|------|------|
| **自动发现** | 通过 `openclaw agents list` 自动发现所有带有工作区的代理 |
| **代理隔离** | 每个代理仅压缩自己的 `memory/` 目录并更新自己的配置文件 |
| **状态持久化** | `.compression_state.json` 跟踪已处理笔记、上次运行时间和状态 |
| **去重** | 追加前检查目标文件是否已存在该笔记日期，避免重复 |
| **移动文件标记** | 已处理笔记移动到 `memory/processed/` 以实现清晰分离 |
| **领域过滤** | 每个任务使用 DOMAIN_CONTEXT（如"HR/工作"、"育儿"）指导提取 |
| **剩余笔记报告** | 摘要播报下次运行仍待处理的老笔记数量 |
| **交错调度** | 任务在周日上海时间 03:00 至 05:00 运行（间隔 30 分钟） |
| **错误隔离** | 一个笔记失败不会停止整个任务；错误被记录并继续 |
| **钉钉通知** | 通过钉钉连接器广播完成摘要 |

---

## 安装

### 快速开始

```bash
cd /root/.openclaw/workspace
chmod +x skills/per-agent-compression-universal/install.sh
./skills/per-agent-compression-universal/install.sh
```

就是这样！安装程序将：
- ✅ 验证 OpenClaw 是否运行
- ✅ 发现所有带有工作区的代理
- ✅ 为每个代理创建 1 个 cron 任务（交错调度）
- ✅ 报告任何问题

### 创建内容

对于每个代理（如 `main`, `hrbp`, `parenting`, `decoration`, `memory_master`）：
- 创建名为 `per_agent_compression_<agent_id>` 的 cron 任务（内部标准化为 `peragent_compression_<agent_id>`）
- 调度：每周日，从上海 03:00 开始，每 30 分钟间隔一个
- 超时：1200 秒（20 分钟）
- 交付：通过钉钉连接器向配置的账户发送通知

---

## 工作原理

### 1. 发现
安装程序运行 `openclaw agents list --json` 并过滤出具有 `workspace` 字段的代理。

### 2. 任务创建
对于每个发现的代理，安装程序调用：

```bash
openclaw cron add \
  --name "per_agent_compression_<agent_id>" \
  --cron "<cron_expr>" \
  --tz "Asia/Shanghai" \
  --agent "main" \
  --message "<concise_execution_plan>" \
  --model "openrouter/stepfun/step-3.5-flash:free" \
  --timeout 1200 \
  --session "isolated" \
  --announce \
  --channel "dingtalk-connector" \
  --to "05566651511149398" \
  --best-effort-deliver
```

**关于消息长度的说明**：由于 CLI 限制，`--message` 保持简洁（约 1200 字符）但包含所有基本逻辑。完整细节记录在本 README 中。如果需要超详细版本（包含每个步骤和边缘情况），可以在安装后手动编辑任务：

```bash
openclaw cron edit per_agent_compression_<agent_id> --message "$(cat FULL_DETAILED_MESSAGE.txt)"
```

### 3. 执行
当 cron 触发时，`main` 代理执行任务指令：

1. **预检查** - 验证工作区、`memory/` 目录、目标文件存在
2. **加载状态** - 读取 `{workspace}/memory/.compression_state.json`（或初始化）
3. **列出笔记** - 查找匹配 `YYYY-MM-DD.md` 的 `memory/*.md`，过滤日期 < 今天-7，排除已处理
4. **排序与限制** - 最旧优先，每次运行最多 5 个笔记
5. **处理每个笔记**：
   - 读取完整内容
   - 提取：用户偏好、关键决策、个人信息（领域特定）
   - 去重：如果目标文件已存在该笔记日期则跳过
   - 追加到：
     - `USER.md` → 在 `## Personal Info / Preferences` 下，头 `### [YYYY-MM-DD]`
     - `IDENTITY.md` → 在 `## Notes` 下（如不存在则创建），头 `### [YYYY-MM-DD]`
     - `SOUL.md` → 在 `## Principles` 或 `## Boundaries` 下（视情况），头 `### [YYYY-MM-DD]`
     - `MEMORY.md` → 在 `## Key Learnings` 下（如不存在则创建），格式 `- [YYYY-MM-DD] <summary>`
   - 移动笔记文件到 `{workspace}/memory/processed/`
   - 更新状态：`processed_notes.append(filename)`, `last_compressed_date = note_date`
6. **完成** - 保存状态（`last_run_at`, `status="completed"`），清理工作缓冲区
7. **通知** - 发送摘要到钉钉：代理、处理数量、剩余老笔记、任何错误

---

## 更新内容

每个代理的文件都是**仅追加**；现有内容从不被覆盖。

**示例追加到 `MEMORY.md`**：
```markdown
## Key Learnings

- [2026-03-10] User prefers morning exercise and reads tech news before breakfast.
- [2026-03-12] Decoration project delayed due to material shortage; new timeline: April 15.
```

**示例追加到 `USER.md`**：
```markdown
## Personal Info / Preferences

### [2026-03-10]
- Preferred communication channel: DingTalk
- Working hours: 9:00-18:00 Beijing time
- Do not disturb: 12:00-14:00 lunch break
```

---

## 配置

不需要配置！但如果你想自定义：

- **调度**: 编辑任务中的 cron 表达式（不建议；修改 `install.sh` 偏移后重新运行安装）
- **超时**: 更改 `install.sh` 中的 `--timeout` 值（默认 1200s）
- **交付通道**: 修改 `install.sh` 中的 `--channel` 和 `--to`
- **领域上下文**: 编辑 `install.sh` 中的 `DOMAIN_CONTEXT` 关联数组以添加/更改每个代理的描述

---

## 测试与限制

### 已知限制

1. **CLI 消息长度限制**  
   `openclaw cron add --message` 会截断超过 ~1KB 的消息。该技能通过使用简洁模板来绕过此限制。如需完全详细的指令，安装后手动使用 `openclaw cron edit --message` 编辑任务。  
   **影响**: 低——简洁模板已包含所有操作逻辑。详细示例见 README。

2. **无代理安装过滤器**  
   该技能总是发现*所有*代理。如果只想安装单个代理（如 `decoration`），必须：
   - 编辑 `install.sh` 注释掉其他代理，或
   - 运行安装后立即 `openclaw cron delete` 删除不需要的任务  
   **影响**: 中等——如果选择性部署需要额外手动清理。

3. **需要 `self-improve-agent` 以实现全自动化**（可选）  
   技能本身不依赖它，但如果希望代理自动写每日笔记或优化记忆，可能需要那个独立技能。  
   **影响**: 低——压缩无需它。

4. **memory/processed/ 目录必须可写**  
   任务会尝试创建 `processed/`（如果缺失）。如果权限不足，该笔记任务会失败但继续其他笔记。  
   **影响**: 低——标准权限即可。

### 已测试场景

- ✅ 干净系统全新安装（无预存在的 per-agent 任务）
- ✅ 覆盖现有任务重新安装（跳过重复）
- ✅ 卸载删除所有技能创建的任务
- ✅ 任务负载包含所有预期字段（状态文件、处理目录、领域上下文）
- ✅ 安装期间网关日志无错误
- ✅ 每日笔记 (2026-03-18) 记录完整会话供未来压缩

### 手动验证

安装后，验证：
```bash
openclaw cron list | grep per_agent_compression
```

应看到每个发现代理有 1 个任务。检查一个任务的消息：
```bash
openclaw cron get <job_id> | jq '.payload.message'
```

确保消息包括：
- `DAILY_NOTES_DIR`
- `PROCESSED_DIR`
- `STATE_FILE`
- `TARGET_FILES`
- `DOMAIN_CONTEXT`
- 步骤 1-7 包括去重和剩余笔记报告

---

## 卸载

```bash
cd /root/.openclaw/workspace
./skills/per-agent-compression-universal/uninstall.sh
```

这将删除**所有** `per_agent_compression_*` 任务。不会触及其他 cron 作业（如 `proactive_notes_compression_*`）。

---

## 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本历史和详细变更。

---

## 贡献

此技能开放改进。发现错误或有增强建议？

- **问题**: 通过 GitHub（如果已发布）或直接联系技能作者报告
- **增强**: 欢迎 fork，修改 `install.sh` 和 `README`，并提交 PR

---

## 免责声明

**此技能目前处于积极测试阶段。** 虽然核心功能稳定，但边缘情况（如消息长度限制、代理过滤）可能需要进行手动调整。生产使用时请注意，可能需要进行微小调整。首次运行前务必备份您的 `MEMORY.md` 和每日笔记。

---

## 支持

- **文档**: 本 README 和 CHANGELOG
- **社区**: OpenClaw Discord (`#agent-skills` 频道)
- **直接**: 联系技能作者或仓库维护者

---

**压缩愉快！**
