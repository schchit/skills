# Obsidian Frontmatter 模板（Generator）

> 此文件是 feishu-sync-obsidian 的**输出模板**。
> Step 3 写入文档时，按此模板填充 frontmatter。

---

## 模板

```yaml
---
type: {type}
status: {status}
tags: [{tags}]
created: {created}
feishu_doc_token: {doc_token}
feishu_node_token: {node_token}
feishu_wiki: {wiki_name}
---
```

---

## 变量说明

| 变量 | 来源 | 示例值 |
|------|------|-------|
| `{type}` | 文档类型，固定为"随记" | `随记` |
| `{status}` | 固定为"2-进行中" | `2-进行中` |
| `{tags}` | 固定为"来源/飞书同步" | `来源/飞书同步` |
| `{created}` | 同步日期，格式 YYYY-MM-DD | `2026-03-29` |
| `{doc_token}` | 飞书文档 obj_token | `xxx` |
| `{node_token}` | 飞书节点 node_token | `xxx` |
| `{wiki_name}` | Wiki 名称 | `个人成长` |

---

## 完整输出示例

```yaml
---
type: 随记
status: 2-进行中
tags: [来源/飞书同步]
created: 2026-03-29
feishu_doc_token: VfcMbtzZUaWpOKs6PeOcamEjn1f
feishu_node_token: Yn63wd7AAi8BmEkAN20cqCycnLc
feishu_wiki: 个人成长
---

[文档内容接在这里]
```

---

## 填充规则

1. **type**：固定为"随记"，不随文档变化
2. **status**：固定为"2-进行中"，不随文档变化
3. **tags**：固定为"来源/飞书同步"，不随文档变化
4. **created**：使用同步时的日期，不是文档创建日期
5. **doc_token / node_token**：从 Wiki API 获取，直接填充
6. **wiki_name**：从节点所属 Wiki 确定

---

## Generator 指令

**Step 1**：加载本模板
**Step 2**：确认所有变量的值
**Step 3**：填充模板，生成完整 frontmatter
**Step 4**：将 frontmatter 追加到文档内容开头
