# token-pilot

> 版本：v2.5.0 | 最后更新：2026-04-02

---

## 🚀 安装后 3 步完成所有设置

### 第 1 步：确认技能已激活（秒完成，无需操作）

安装即生效。下次对话时 agent 会自动加载 token-pilot 规则（R1-R10）。不需要任何配置。

> 想验证？在对话里说"检查 token-pilot 是否已激活"，agent 会确认。

---

### 第 2 步：跑一次诊断（5 分钟，只需一次）

**先找到技能路径：**
```powershell
# 在对话里说"告诉我 token-pilot 的安装路径"，agent 会给你。
# 或者直接用这个默认路径（大多数 Windows 用户适用）：
# C:\Users\<你的用户名>\.openclaw\skills\token-pilot
```

**然后跑诊断：**
```powershell
node "C:\Users\<你的用户名>\.openclaw\skills\token-pilot\scripts\audit.js" --all
```

输出是中文建议列表，只读不改文件。有问题再跑修复命令（会在输出里提示）。

> 💡 不确定路径？直接问 agent："帮我跑 token-pilot 诊断"，它会处理路径问题。

---

### 第 3 步：加一条 Cron（10 分钟，之后完全自动）

打开 `openclaw.json`（路径：`C:\Users\<你的用户名>\.openclaw\openclaw.json`），找到 `"cron"` 字段，在数组里加入：

```json
{
  "kind": "agentTurn",
  "schedule": "0 9 * * 1",
  "message": "运行 token-pilot 周度诊断：帮我检查 token 使用情况，扫描 cron 和 agent 配置有无优化空间，给出摘要建议。",
  "lightContext": true,
  "model": "Qwen/Qwen3-8B"
}
```

> 如果没有 `"cron"` 字段，在文件末尾的 `{}` 内加 `"cron": []`，再把上面这条放进去。
> 不确定怎么改 JSON？说"帮我把 token-pilot 周度 cron 加进 openclaw.json"，agent 来做。

**加完之后**：每周一早 9 点自动检查，用轻量模型，不占主会话 token。

---

## ✅ 覆盖范围：所有 agent，不只是主 agent

**token-pilot 安装一次，团队所有 agent 自动生效。**

OpenClaw 的 skills 存放在全局路径（`~/.openclaw/skills/`），所有 agent 共享同一个 skill 库。每次对话开始时，OpenClaw 自动把 skill 列表注入 system prompt；agent 判断任务适用后调用 `skill_get` 读取 SKILL.md，规则即刻激活。

这意味着：pm / architect / fe / be / qa / coder 以及 main，任何一个 agent 都会在合适的场景下应用 token-pilot 的行为规则，**不需要每个 agent 单独安装或配置**。

---

## 🔒 落实保障：三层机制确保优化不落空

| 层次 | 内容 | 是否自动 |
|------|------|---------|
| **行为规则层** R1-R10 | 安装即生效，每次对话自动遵循 | ✅ 全自动 |
| **首次诊断** | 安装后跑一次 audit，扫描工作区问题 | ⚠️ 需手动跑一次 |
| **定期维护** | 每周一次 optimize 扫描，Heartbeat cron 自动触发 | ✅ 配置后自动 |

### 首次诊断（安装后跑一次，之后无需再跑）

```powershell
# 全量诊断（只读，不改文件）
node "C:\Users\Administrator\.openclaw\skills\token-pilot\scripts\audit.js" --all

# 如有问题，自动修复工作区（只移动根目录杂散脚本，不改配置）
node "C:\Users\Administrator\.openclaw\skills\token-pilot\scripts\optimize.js" --apply
```

### 定期维护（加进 openclaw.json，配置后完全自动）

在 `openclaw.json` 的 cron 列表中加入：

```json
{
  "kind": "agentTurn",
  "schedule": "0 9 * * 1",
  "message": "运行 token-pilot 周度诊断：node C:\\Users\\Administrator\\.openclaw\\skills\\token-pilot\\scripts\\optimize.js --cron。只输出建议，不自动修改配置，把结果摘要告诉我。",
  "lightContext": true,
  "model": "Qwen/Qwen3-8B"
}
```

每周一早 9 点自动跑，轻量模型，不占主会话 token。

---

## 这是什么

`token-pilot` 是 OpenClaw 的 token 消耗优化技能，通过三层机制降低每次会话的上下文开销：

1. **行为规则层** — 安装即生效，无需任何配置
2. **配置优化层** — 经实测可用的 `openclaw.json` 配置写法
3. **诊断脚本层** — 主动扫描工作区、cron、agent 配置并给出建议

---

## 安装后自动生效的行为规则（R1-R10）

无需任何操作，加载技能后自动遵循：

| 规则 | 效果 |
|---|---|
| R1：先读前 30 行，确认再全读 | 避免大文件盲读浪费 |
| R2：工具输出超长时只保留摘要 | 减少工具结果堆积 |
| R3：简单问题短答 | 减少 output token |
| R4：不重复读同一文件 | 去除冗余 read 调用 |
| R5：合并无依赖的工具调用 | 减少轮次 |
| R6：小改用 edit，不用 write 全覆盖 | 减少上下文写入 |
| R7：按角色重量裁剪工具使用范围 | 轻角色不开重工具 |
| R8：Prompt Cache 保护 | 固定内容稳定，动态内容后置，节省 75% input token |
| R9：机器接收方压缩输出格式 | Cron/agent 消息不输出装饰性 markdown |
| R10：动态内容分级限制 | 按类型设上限，总比例 <30%，防 cache 失效 |

---

## 🔍 来自 Claude Code 源码分析的优化（v2.x 新增）

以下优化来自对 Claude Code 官方源码的实际读取分析，每条标注来源文件，有工程数据背书。

| # | 优化点 | 来源 | 你需要做的 |
|---|--------|------|-----------|
| 1 | 禁止 system prompt 有动态内容 | `main.tsx` | AGENTS.md/SOUL.md 不加时间戳；进行中事项移出去放日记文件 |
| 2 | AGENTS.md 只放稳定内容 | `claudemd.ts` | 任务状态放 memory 日记，项目上下文放 context.md |
| 3 | 动态内容分级上限 | `context.ts` | exec 输出≤2000字符；工具返回≤5000；知识文件≤10KB；动态内容总比例<30% |
| 4 | MEMORY.md 改索引结构 | `memdir.ts` | 每行写指针 `- [标题](topics/file.md) — 摘要`，详情放 topic 文件 |
| 5 | feedback 同时记成功经验 | `memoryTypes.ts` | 用户说"对就这样"也要记，不只记纠正 |
| 6 | Cron/subagent 失败最多重试 3 次 | `autoCompact.ts` | 失败就停+告警，禁止无限重试 |
| 7 | Compaction 缓冲设 8000 token | `autoCompact.ts` | `softThresholdTokens: 8000`；压缩后 `/status` 确认在 10K-40K |
| 8 | 通知类 agent 关掉 cache | `modelCost.ts` | 每次内容不同的 agent 设 `cacheRetention: "none"` |
| 9 | Subagent 卡死主动 kill | `tokenBudget.ts` | 连续多轮无进展就 kill，不傻等 |

> **工程数据**：第 6 条来自 Claude Code 实测——1,279 个 session 发生 50+ 次连续失败，每天浪费 ~25 万次 API 调用。第 8 条：cache write $3.75/Mtok，比普通 input $3/Mtok 贵 25%，内容不重复开 cache = 纯亏损。

---

## 经实测的 openclaw.json 配置

以下配置已在真实部署中验证可用，可直接写入。

> 💡 **不确定放在哪里？** 直接说"帮我把 xxx 配置加进 openclaw.json"，agent 会找到正确位置写入，不需要你手动编辑 JSON。

> ⚠️ **注意层级**：所有字段放在 `agents.defaults` 下，**不是顶层**。写到顶层会导致启动失败。

### 长会话压缩稳定性

```json
"agents": {
  "defaults": {
    "compaction": {
      "mode": "safeguard",
      "memoryFlush": {
        "enabled": true,
        "softThresholdTokens": 8000
      }
    }
  }
}
```

### Bootstrap 文件大小限制

```json
"agents": {
  "defaults": {
    "bootstrapMaxChars": 12000,
    "bootstrapTotalMaxChars": 20000
  }
}
```

### Heartbeat（维持 prompt cache 不过期）

```json
"agents": {
  "defaults": {
    "heartbeat": {
      "every": "55m",
      "activeHours": { "start": "08:00", "end": "23:00" }
    }
  }
}
```

> 55m < Anthropic cache TTL（1h），心跳间隔略小于 TTL，保持缓存活跃，避免重新 cache write 的额外费用。

### 图片 token 控制（可选）

```json
"agents": {
  "defaults": {
    "imageMaxDimensionPx": 800
  }
}
```

### per-agent cache 策略（可选）

```json
"agents": {
  "list": [
    { "id": "main", "params": { "cacheRetention": "long" } },
    { "id": "alerts", "params": { "cacheRetention": "none" } }
  ]
}
```

### 工具白名单（每 agent 省 4000-8000 tok）

在各 agent `tools.allow` 里设置精确白名单，替代 `["*"]`：

| 角色类型 | 建议白名单 | 可去掉 |
|---|---|---|
| 情报/搜索类 | web_search/web_fetch/read/write/edit/exec/memory_*/message | browser/canvas/tts/feishu_bitable/sessions_spawn |
| 数据分析类 | read/write/edit/exec/web_search/feishu_bitable/memory_*/message | browser/canvas/tts/feishu_wiki |
| 产品管理类 | read/write/edit/exec/web_search/feishu_doc/feishu_bitable/feishu_wiki/memory_*/message | browser/canvas/tts |
| 交付/开发类 | read/write/edit/exec/web_search/web_fetch/browser/sessions_spawn/memory_*/message | canvas/tts/feishu_bitable |

---

## 实时诊断命令

```bash
/status              # 当前 session token 用量 + 预估费用
/usage tokens        # 每条回复后显示 token 用量
/context list        # context 分解（各文件/工具/skill 各占多少）
/context detail      # 详细分解
/compact             # 手动触发 session 压缩
```

---

## AGENTS.md 精简原则

- 子 agent AGENTS.md 控制在 **400 tok 以内**
- ✅ 保留：启动规则、记忆规则、安全规则
- ❌ 删除：context-mode 使用说明（系统自动注入）、群聊规则、无关示例代码
- 主 workspace AGENTS.md 是维护文档，允许更大

---

## Skill 描述精简建议

OpenClaw 每次对话都注入全部已安装 Skill 的 metadata：
- description 控制在 **50 字以内**
- 不用的 skill 及时卸载：`openclaw skills uninstall <skill-name>`
- 用 `/context detail` 查看 skill list 实际占用 token

---

## 技能协同

| 技能 | 协同方式 |
|---|---|
| `smart-agent-memory` / `memos-local` | memory_search 优先，避免重读文件；解决后立即记录，防止重复调查 |
| `coding-lead` | 大上下文写磁盘 context 文件，ACP prompt 只放最小头部 |
| `qmd` | 检索代替读文件，只在确认需要时再 read |

---

## 相关文件

- `SKILL.md` — 技能主文件（agent 行为规则 + 插件协同 + 配置）
- `scripts/audit.js` — 审计脚本
- `scripts/optimize.js` — 优化建议脚本
- `scripts/catalog.js` — 技能目录索引生成
- `references/workspace-patterns.md` — 工作区文件组织最佳实践
- `references/cron-optimization.md` — Cron 模型路由指南

---

## 更新日志

| 版本 | 日期 | 变更 |
|---|---|---|
| v2.5.0 | 2026-04-02 | 第二轮源码分析：新增 5 条（autocompact 熔断/compaction 13K缓冲/压缩后 10K-40K区间/cache write 贵 25% 推论/subagent 边际递减检测）；softThresholdTokens 从 4000 调整为 8000 |
| v2.4.0 | 2026-04-02 | README 全面重写：覆盖所有 agent 说明 + 落实三层机制 + 源码分析独立章节 |
| v2.3.0 | 2026-04-02 | SKILL.md 新增记忆系统三条规范（MEMORY.md 索引结构/记忆四分类/feedback记成功）；同步重组主 workspace MEMORY.md 为索引结构 |
| v2.2.0 | 2026-04-02 | README 新增一键命令；SKILL.md 新增首次加载主动提示 + 周度 Heartbeat cron |
| v2.1.0 | 2026-04-02 | 新增 R10 动态内容分级限制；R8 补充 AGENTS.md 拆分建议 |
| v2.0.0 | 2026-03-31 | imageMaxDimensionPx；per-agent cacheRetention；Skill 描述精简；诊断命令 |
| v1.9.0 | 2026-03-31 | Cron lightContext + 便宜模型 |
| v1.8.0 | 2026-03-31 | R8 补充：动态 memory_search 破坏 prompt cache |
| v1.7.0 | 2026-03-31 | R8 Prompt Cache Awareness；R9 Non-Human Output Compression |
| v1.6.0 | 2026-03-31 | tools.allow 白名单 |
| v1.5.0 | 2026-03-31 | Config Change Safety Rules；workspace 根目录文件组织 |
| v1.4.0 | 2026-03-31 | Validated Config Patterns；AGENTS.md 精简原则 |
