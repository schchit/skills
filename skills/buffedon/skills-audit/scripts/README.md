# skills-audit 脚本说明（精简版）

目标：在不执行任何 skill 代码的前提下，对 `workspace/skills` 做**静态审计**，并把结果写入本地 **append-only NDJSON**。

## 输出（固定位置）

- 审计日志（追加写）：`~/.openclaw/skills-audit/logs.ndjson`
- 扫描状态（用于 diff）：`~/.openclaw/skills-audit/state.json`

日志字段以 `skills-audit/log-template.json` 为准。

## 主要脚本

- `skills_audit.py`
  - `init`：初始化 logs/state
  - `scan`：扫描 `workspace/skills`，对比 state，发现新增/变更/删除则追加写一条 `scan-detected`

- `skills_watch_and_notify.py`
  - 面向“监控推送”的消息生成脚本
  - 有变化时输出一段固定模板文本；无变化则不输出（便于 cron 实现“无变化不发”）


## 常用命令

初始化：

```bash
python3 skills/skills-audit/scripts/skills_audit.py init --workspace /root/.openclaw/workspace
```

手动扫描：

```bash
python3 skills/skills-audit/scripts/skills_audit.py scan --workspace /root/.openclaw/workspace --who cron --channel local
```

如需后台监控，推荐由 OpenClaw 自己创建 cron 任务，并定时执行：

```bash
python3 skills/skills-audit/scripts/skills_watch_and_notify.py --workspace /root/.openclaw/workspace
```

推荐由助手或运维使用 `openclaw cron add` / `openclaw cron edit` 来写定时任务，而不是由 skill 脚本直接写 `jobs.json`。

