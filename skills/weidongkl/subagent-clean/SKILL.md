# subagent-clean 技能

清理 OpenClaw 子 agent 会话的统一技能，整合了快速清理和完整清理功能。

---

```yaml
name: subagent-clean
version: 1.0.0
description: 清理 OpenClaw 子 agent 会话
author: OpenClaw Community
license: MIT
tags:
  - subagent
  - cleanup
  - session
  - maintenance
```

## 触发条件

用户请求（以下任意一个）：
- "清理子 agent"
- "清理 subagent"
- "清除子会话"
- "delete subagent"
- "清理已完成的子 agent"
- "清除所有 subagent"
- "清除子 agent"
- "清理会话"
- "删除所有子会话"
- "清空 subagent"
- "reset subagent"
- "清理 archiver"
- "clean"
- "cls"
- "清理"
- "重置"
- "reset"
- "clean subagent"
- "清理环境"

## 命令参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| target | string | 否 | 子 agent ID（如 5faf4b81-...），不填则清理所有已完成子 agent |
| mode | string | 否 | 模式：dry-run | full | cleanup-only（默认：full） |
| backup | boolean | 否 | 是否备份（默认：true） |
| force | boolean | 否 | 强制删除活跃子 agent（默认：false） |

## 斜杠命令

**`/subclean`** - 快捷清理子 agent 会话

```
/subclean              # 快速清理所有子 agent
/subclean --list       # 列出所有子 agent
/subclean --dry-run    # 预览模式
/subclean --force      # 强制清理（包括活跃子 agent）
/subclean --agent qq   # 清理指定 agent 的子会话
/subclean --all        # 清理所有 agent 的子会话
```

## 工作流程

1. 列出所有子 agent（活跃 + 历史）
2. 检查备份状态（24h 内已有备份则跳过）
3. 执行备份（如需要）
4. **清理 sessions.json** - 删除子 agent 条目
5. **清理 childSessions** - 从主会话移除引用
6. 归档会话文件（移动到 archive/ 目录）
7. 验证清理结果

## 清理步骤（详细）

### 1. 清理 sessions.json

```bash
# 只保留主会话，删除所有子 agent 条目
# 注意：{agent} 会自动替换为当前 agent 名称（如 orchestrator, qq, discord 等）
AGENT_DIR="/root/.openclaw/agents/{agent}/sessions"
cat $AGENT_DIR/sessions.json | \
  jq 'with_entries(select(.key | endswith(":main")))' > /tmp/sessions-cleaned.json && \
  mv /tmp/sessions-cleaned.json $AGENT_DIR/sessions.json
```

### 2. 清理 childSessions

```bash
# 设置 childSessions 为 null
MAIN_KEY=$(cat $AGENT_DIR/sessions.json | jq -r 'keys[] | select(endswith(":main"))')
cat $AGENT_DIR/sessions.json | \
  jq ".[\"$MAIN_KEY\"].childSessions = null" > /tmp/sessions-cleaned.json && \
  mv /tmp/sessions-cleaned.json $AGENT_DIR/sessions.json
```

### 3. 归档会话文件

```bash
# 归档所有子会话文件（保留主会话）
cd $AGENT_DIR
mkdir -p archive
MAIN_KEY=$(cat sessions.json | jq -r 'keys[] | select(endswith(":main"))')
MAIN_FILE="$(cat sessions.json | jq -r ".[\"$MAIN_KEY\"].sessionId").jsonl"
for file in *.jsonl; do
  if [[ "$file" != "$MAIN_FILE" ]]; then
    mv "$file" archive/
  fi
done
```

## 备份策略

- **备份位置**: `~/.openclaw/agents/{agent}/sessions/backups/`
- **备份内容**: sessions.json + 会话文件 + 状态快照
- **保留策略**: 最多 10 个备份，保留 30 天
- **压缩**: 7 天以上的备份自动压缩

## 清除策略

- **sessions.json**: 删除子 agent 条目 + 清理 childSessions 引用 ⭐
- **会话文件**: 移动到 archive/ 目录，7 天后删除 ⭐
- **活跃子 agent**: 默认跳过，--force 强制终止
- **已有备份**: 24h 内备份存在则跳过备份直接清理

## 使用方法

```bash
# 清理所有已完成子 agent（推荐）
python3 ~/.openclaw/skills/subagent-clean/scripts/delete-subagent.py

# 清理指定子 agent
python3 ~/.openclaw/skills/subagent-clean/scripts/delete-subagent.py --target <ID>

# 预览模式（不实际删除）
python3 ~/.openclaw/skills/subagent-clean/scripts/delete-subagent.py --dry-run

# 强制清理（包括活跃子 agent）
python3 ~/.openclaw/skills/subagent-clean/scripts/delete-subagent.py --force

# 不创建备份
python3 ~/.openclaw/skills/subagent-clean/scripts/delete-subagent.py --no-backup

# 彻底删除（包括旧备份）
python3 ~/.openclaw/skills/subagent-clean/scripts/delete-subagent.py --purge

# 列出所有子 agent
python3 ~/.openclaw/skills/subagent-clean/scripts/delete-subagent.py --list

# 清理归档（30 天以上）
python3 ~/.openclaw/skills/subagent-clean/scripts/delete-subagent.py --cleanup-archive --days 30

# 快速清理（仅清理 sessions.json 和归档文件）
python3 ~/.openclaw/skills/subagent-clean/scripts/delete-subagent.py --quick-clean

# 清理指定 agent
python3 ~/.openclaw/skills/subagent-clean/scripts/delete-subagent.py --agent qq
```

## 输出示例

```
🔍 扫描子 agent...
  活跃：0
  历史：1
  cron runs: 2

📦 备份检查...
  ✓ 无 24h 内备份，创建新备份

💾 创建备份...
  sessions.json → backups/sessions.json.backup.20260331_210500
  fc7e7c06....jsonl → backups/fc7e7c06....jsonl.backup.20260331_210500

🗑️  删除条目...
  ✓ agent:xxx:subagent:5faf4b81-...
  ✓ 从 main.childSessions 移除引用

✅ 清理完成
  删除：1 个条目
  备份：2 个文件
  释放：~320KB
```

## 安全特性

- ✅ 操作前自动备份
- ✅ 24h 内不重复备份
- ✅ 会话文件先归档后删除
- ✅ 活跃子 agent 默认保护
- ✅ JSON 有效性验证
- ✅ 支持 dry-run 预览

## 文件结构

```
~/.openclaw/skills/subagent-clean/
├── SKILL.md                    # 技能说明
├── scripts/
│   └── delete-subagent.py      # 主执行脚本
└── (运行时创建)
    └── backups/                # 备份目录（在每个 agent 的 sessions 目录下）
```

## 配置

```yaml
# SKILL.md 头部配置
name: subagent-clean
version: 1.0.0
description: 清理 OpenClaw 子 agent 会话
user-invocable: true
command-dispatch: tool  # 直接路由到工具，不经过模型
```

## 工具调用

技能通过以下工具调用执行：

```javascript
{
  name: "exec",
  arguments: {
    command: "python3 /root/.openclaw/skills/subagent-clean/scripts/delete-subagent.py --quick-clean"
  }
}
```

## 注意事项

- 自动备份 sessions.json
- 归档所有子会话文件
- 保留主会话
- 默认清理当前 agent 的子会话
- 使用 `--agent` 参数可指定其他 agent
- 使用 `--all` 参数可清理所有 agent
