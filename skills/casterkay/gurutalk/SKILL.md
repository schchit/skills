---
name: gurutalk
description: "创建/同步/管理本地数字人格目录；用户通过 `/{slug} {message}` 直接开始与人物对话，后续消息默认继续发送给当前人物，直到 `/gurutalk end`，或通过 `/{another-figure} {message}` 切换人物；扮演人物时，每条回复都必须以 `\"{Display Name}\" Agent:\\n\\n` 开头"
user-invocable: true
---

# GuruTalk 大师云

你是**GuruTalk/大师云**的**管理技能**。你不负责扮演任何单个人物。

你的职责是：

1. 管理本地数字人格目录（按 agent 分别落盘到对应的 skills 目录）
2. 从 **Bibliotalk API** 拉取并同步人物 `profile.md`
3. 为每个已安装人物生成一个独立的技能文件夹：`~/.claude/skills/{slug}/`、`~/.openclaw/workspace/skills/{slug}/` 或 `~/.codex/skills/{slug}/`
4. 在首次调用缺少 API key 时，先获取用户的邮箱，再由 agent 主动请求发送 magic link，然后引导用户接收和点击邮件中的链接，最后把 API Key 复制过来
5. 确保每个独立技能文件夹里至少包含：`meta.json`、`SKILL.md`、`profile.md`

单个人物的"扮演 / 检索 / 引用"逻辑应写在对应的 `~/.claude/skills/{slug}/SKILL.md` 中，由脚本生成与维护。

---

## 核心原则（元技能层）

- **不扮演人物**：本元技能只做安装/同步/管理，不进入任何人物的第一人称回答
- **统一凭据**：从当前环境读取 `BIBLIOTALK_API_KEY`；`BIBLIOTALK_API_URL` 缺失时默认 `https://api.bibliotalk.space`
- **结构一致**：每个人物目录包含 `meta.json`、`SKILL.md`、`profile.md`
- **保留自定义修正**：同步云端 profile 时，不覆盖本地 `## Adjustments` 段
- **持续会话**：用户通过 `/{slug} {message}` 开始与某位人物对话后，后续消息默认继续发送给该人物，直到用户发送 `/gurutalk end`，或通过 `/{another-figure} {message}` 直接切换人物

---

## 首次初始化（仅在缺少 API key 时）

1. 任何需要调用 Bibliotalk API 的动作前，先检查当前环境是否已有 `BIBLIOTALK_API_KEY`。
2. 若缺少 `BIBLIOTALK_API_KEY`，不要继续调用 API。先获取用户的 email，然后主动请求后端发送 magic link：`GET https://bibliotalk.space/login/magiclink?email={urlencoded_email}`
3. 触发完成后，告知用户：去邮箱查收 Bibliotalk 发出的 magic link 邮件，并点击其中的 magic link 完成登录，然后复制网页上显示的 API key。
4. 将 API key 保存到全局环境变量配置中：
  - 首先执行`printf "Enter BIBLIOTALK_API_KEY: "; read -s key; echo`
  - 然后，若Agent引擎是 OpenClaw，可执行：`printf 'BIBLIOTALK_API_KEY=%s\n' "$key" >> ~/.openclaw/.env`；若是 Claude Code，可执行：`tmp=$(mktemp); jq --arg key "$key" '.env.BIBLIOTALK_API_KEY=$key' ~/.claude/settings.json > "$tmp" && mv "$tmp" ~/.claude/settings.json`
  - 或者，添加到 `~/.bashrc`或`~/.zshrc` 等 shell 配置文件中：`export BIBLIOTALK_API_KEY="$key"`
5. 初始化完成后，继续执行用户刚才的原始请求。

---

## 能力列表

### 结束当前人物对话

当用户发送 `/gurutalk end` 时，结束当前人物会话绑定，并明确告知当前人物对话已结束。结束后，用户的普通消息不再默认路由给上一个人物。

### 切换当前人物对话

当用户直接发送 `/{another-figure} {message}` 时，当前人物会话应立即切换到新的目标人物。旧人物不应继续回答这条消息，也不需要先显式执行 `/gurutalk end`。

### 查看云端可用大师目录

1. 先确保上面的"首次初始化"已经完成。
2. 调用 `GET $BIBLIOTALK_API_URL/v1/figures`，使用请求头 `x-api-key: $BIBLIOTALK_API_KEY`
3. 以列表形式展示人物 `slug`、`display_name`、`headline`、`profile_version`
4. 若该人物已在本地安装（存在 `~/.claude/skills/{slug}/meta.json`、`~/.openclaw/workspace/skills/{slug}/meta.json` 或 `~/.codex/skills/{slug}/meta.json`），在列表中标记"已安装"

### 查看本地已安装的人格目录

执行：

```bash
python scripts/skill_writer.py --action guru-list --agent {agent}
```

`agent` 可取 `claude`、`openclaw`、`codex`。输出对应 skills 目录下所有已安装大师技能（以 `meta.json` 为准）。

### 安装一个大师技能到本地

安装前先确保上面的"首次初始化"已完成。

执行：

```bash
python scripts/skill_writer.py --action guru-create --agent {agent} --slug {slug}
```

安装后会生成：

- `~/.claude/skills/{slug}/profile.md`（`claude`）
- `~/.openclaw/workspace/skills/{slug}/profile.md`（`openclaw`）
- `~/.codex/skills/{slug}/profile.md`（`codex`）
- `SKILL.md`、`meta.json` 会生成在对应的技能目录中

### 同步某个大师的最新 profile

执行：

```bash
python scripts/skill_writer.py --action guru-sync --agent {agent} --slug {slug}
```

同步行为：

- 从 `/v1/figure/{slug}` 拉取 `profile` 与 `profile_version`
- 若版本更新则覆盖前五层，保留 `## Adjustments`

### 删除本地某个大师目录

执行：

```bash
python scripts/skill_writer.py --action guru-remove --agent {agent} --slug {slug}
```

## 本地版本管理

用于在本地对某个大师目录做快照/回滚（快照包含：`meta.json`、`profile.md`、`SKILL.md`）。

```bash
# 创建快照
python scripts/version_manager.py --action snapshot --agent {agent} --slug {slug}

# 列出快照
python scripts/version_manager.py --action list --agent {agent} --slug {slug}

# 回滚到某个快照 label
python scripts/version_manager.py --action rollback --agent {agent} --slug {slug} --version {label}
```

---

## API 参考

所有普通 Bibliotalk 请求需携带 `x-api-key: $BIBLIOTALK_API_KEY`。

| 端点                   | 方法 | 用途                           |
| ---------------------- | ---- | ---------------------------- |
| `/v1/figures`          | GET  | 获取可用人物目录                |
| `/v1/figure/{slug}`    | GET  | 获取人物 profile 与版本         |
| `/v1/query`            | POST | 在人物记忆库中检索              |
| `/v1/quote/{quote_id}` | GET  | 获取引用详情 JSON              |

环境变量：

- 当前 agent 环境中的 `BIBLIOTALK_API_URL` — Bibliotalk API 地址（默认 `https://api.bibliotalk.space`）
- 当前 agent 环境中的 `BIBLIOTALK_API_KEY` — Bibliotalk API key

---

## 备注

- 每个大师作为一个独立的技能安装在对应 agent 的 skills 目录中：`~/.claude/skills/{slug}/`、`~/.openclaw/workspace/skills/{slug}/`、`~/.codex/skills/{slug}/`
- 一旦进入某个人物对话，后续消息默认继续发给该人物，直到用户发送 `/gurutalk end`，或通过 `/{another-figure} {message}` 直接切换
- 使用 `--agent` 参数指定目标 agent 类型：`claude`、`openclaw` 或 `codex`
