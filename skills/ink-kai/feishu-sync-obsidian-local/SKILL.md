---
name: feishu-sync-obsidian
description: >
  将飞书 Wiki 文档同步到 Obsidian PARA 知识库。
  触发：当用户说"同步飞书"或"同步文档"时使用。
  遵循 Pipeline 模式，4 步顺序执行，带硬检查点。
metadata:
  pattern: pipeline
  steps: "4"
---

# Feishu → Obsidian PARA Sync

> **模式：Pipeline** | 按需加载 Tool Wrapper（PARA 路由知识）

---

## 硬性规则

**禁止跳过步骤。禁止在用户确认前进入下一步。**

---

## Step 1 — 获取 Wiki 节点列表

**触发**：用户要求同步飞书文档

**执行**：
1. 加载 `references/routing-rules.md` 了解 Wiki Space 配置
2. 使用 `feishu_wiki_space_node` 工具获取两个知识库的节点：

```
Wiki Space 列表：
- 个人成长：space_id = 7619963059842419643
- openclaw知识库：space_id = 7617330356886178745

工具调用：
feishu_wiki_space_node(action="list", space_id="7619963059842419643")
feishu_wiki_space_node(action="list", space_id="7617330356886178745")
```

**Gate**：获取到节点列表后，显示节点数量，问用户确认是否继续。

---

## Step 2 — 匹配 PARA 路由规则

**触发**：Step 1 确认后

**执行**：
1. 加载 `references/routing-rules.md` 获取路由知识
2. 对每个 docx 类型节点，按优先级匹配目标路径：
   - 遍历规则，第一个命中终止
   - 命中条件：标题包含关键词（不区分大小写）
3. 未命中任何规则 → 落入该 wiki 的兜底目录

**路由知识**（来自 routing-rules.md）：
- 个人成长 wiki → 兜底：`05进思斋`
- openclaw知识库 wiki → 兜底：`03藏珍之库/工具`

**Gate**：显示每个文档的目标路径，确认是否继续。

---

## Step 3 — 获取文档内容并写入 Obsidian

**触发**：Step 2 确认后

**执行**：
1. 对每个新文档（vault 中不存在的）：
   - 使用 `feishu_fetch_doc` 获取文档内容
   - 按 `assets/frontmatter-template.md` 生成 frontmatter
   - 调用 sync.py 写入 Obsidian

**同步逻辑**：
- 按 feishu_doc_token 去重（已存在则跳过）
- 目标路径不存在时自动创建目录
- 非 docx 类型（sheet/bitable）只写链接占位符

**Gate**：显示将写入的文件列表，确认后执行。

---

## Step 4 — 质量检查

**触发**：Step 3 执行完成后

**执行**：
1. 加载 `references/review-checklist.md`
2. 对照检查清单验证同步结果：
   - 每个文档都有 frontmatter
   - feishu_doc_token / feishu_node_token 正确
   - 路径符合 PARA 映射
3. 报告检查结果，修复可修复的问题

**输出格式**：
```
【同步报告】
- 写入：X 个文档
- 跳过：X 个（已存在）
- 失败：X 个（错误信息）
```

---

## 参考文件

| 文件 | 模式 | 作用 |
|------|------|------|
| `references/routing-rules.md` | Tool Wrapper | PARA 路由知识库 |
| `references/review-checklist.md` | Reviewer | 同步质量检查清单 |
| `assets/frontmatter-template.md` | Generator | frontmatter 填空模板 |
| `scripts/sync.py` | - | 执行脚本 |

---

## 已知限制

- 电子表格（sheet）、多维表格（bitable）只写链接占位符，不拉内容
- 同步需要飞书 Access Token（由 OpenClaw 插件管理）
- sync.py 每次运行会缓存规则到内存（同一个进程内有效）
