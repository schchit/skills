---
name: knowledge-precipitation
description: |
  每日知识沉淀引擎（Knowledge Auto-Precipitation Engine，KAPE）。自动完成：下载昨日Get笔记内容 → 结合对话记录 → 深度分析用户学习、感悟、工作状态 → 生成含重点摘要的日志简报 → 同步归档到 Get笔记（带标签）+ 飞书知识库 + 飞书文档。触发场景：「整理昨天的日志」「生成日报简报」「知识沉淀」「整理学习记录」「存档昨天的内容」。
---

# KAPE — 知识自动沉淀引擎

## 核心工作流

每天自动生成日志简报，三端同步归档。

### 第一步：确定日期范围

- **目标日期**：昨天（`session_status` 可获取今日日期，向前减1天）
- **Get笔记 API**：`GET /open/api/v1/resource/note/list?since_id=0`，筛选 `created_at` 包含目标日期的笔记
- **会话记录**：`sessions_list` + `sessions_history`，筛选 `updatedAt` 在目标日期内的 session

### 第二步：获取数据（并行）

**Get笔记读取**：
- 调用 `GET /open/api/v1/resource/note/list?since_id=0`
- Fix int64 ID：response 中的 `id`、`note_id`、`next_cursor` 需做字符串化处理
  ```python
  text = re.sub(r'"(id|note_id|next_cursor|parent_id)"\s*:\s*(\d{16,})',
                lambda m: f'"{m.group(1)}":"{m.group(2)}"', text)
  ```
- 筛选 `created_at.startswith(target_date)` 的笔记
- **注意**：音频录音笔记（`recorder_audio`）和网页剪藏（`plain_text` from web）通常含 AI 整理的完整内容，优先读取

**对话记录获取**：
- 用 `sessions_list` 获取所有 active session
- 过滤出目标日期有活动的 session
- 用 `sessions_history` 读取每条 session 的内容（`includeTools=false`）
- 解析用户消息（`role: user`）作为对话记录

**词汇存档**（若有）：
- 读取 `workspace/vocabulary/{target_date}.md`
- 统计当日新增单词数量

### 第三步：深度分析与整理

**用户行为分析**：
- 从 Get笔记的 `tags`、`title`、`source` 推断用户关注领域
- 从 ref 笔记数量、录音笔记时长推断学习深度
- 从内容关键词（认知储备/精力管理/硬约束等）判断核心主题

**张公子画像维度**（供参考）：
| 维度 | 观察点 |
|------|--------|
| 学习风格 | 主动深度 vs 被动浏览 |
| 知识关联 | 是否跨领域建立联系 |
| 方法论倾向 | 重底层原理 vs 碎片技巧 |
| 时间感知 | 是否主动管理精力/时间 |
| 决策态度 | 务实程度、换方法频率 |

**生成日志简报结构**（见 references/briefing-template.md）

### 第四步：写入本地文件

文件路径：`workspace/日志管理/{target_date}-日志简报.md`

### 第五步：三端同步归档

**① Get笔记**（**必须写入完整简报全文，不得简写**）：
```
POST https://openapi.biji.com/open/api/v1/resource/note/save
Headers:
  Authorization: {GETNOTE_API_KEY}
  X-Client-ID: cli_a1b2c3d4e5f6789012345678abcdef90
Body:
  title: "日志简报 {target_date} | {姓名}"
  content: 【必须写入完整简报全文】，包含所有章节、分析、统计数据，不得写入摘要或简短版本
  note_type: "plain_text"
  tags: ["AI整理", "日志简报"]
```

> ⚠️ **重要**：Get笔记的 `content` 字段必须包含日志简报的**完整正文**（与写入本地文件和飞书文档的内容完全一致），不得以"详见链接"为由缩减内容。

**② 飞书知识库**：
- 先 `GET /open/api/v1/resource/knowledge/list` 确认知识库存在
- `feishu_wiki(action=nodes, space_id=个人知识库space_id)` 获取根目录
- `feishu_wiki(action=create, space_id=..., parent_node_token=..., obj_type=docx)` 创建节点
- `feishu_doc(action=write, doc_token=新文档token, content=简报内容)` 写入

**③ 飞书文档**（备用）：
- `feishu_doc(action=create, title=...)` 创建文档
- `feishu_doc(action=write, doc_token=..., content=...)` 写入

### 第六步：用户反馈

向用户发送完成通知，包含：
- 下载 Get笔记 数量（分类统计）
- 参考对话记录数量
- 简报核心发现摘要
- 各端存储结果链接

---

## 配置文件（openclaw.json 中的凭证）

```json
{
  "skills": {
    "entries": {
      "getnote": {
        "apiKey": "gk_live_...",
        "env": {
          "GETNOTE_CLIENT_ID": "cli_a1b2c3d4e5f6789012345678abcdef90"
        }
      }
    }
  }
}
```

飞书机器人需已加入知识库成员，否则 `feishu_wiki(spaces)` 返回空。
