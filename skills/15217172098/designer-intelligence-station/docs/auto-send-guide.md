# 设计师情报站 - 自动发送日报指南

## 📬 输出优化说明

### v1.5.0 起，日报生成后会自动发送：

1. **📊 日报摘要** - 情报数量、分级统计、抓取成功率
2. **📄 MD 文件** - 完整日报（v1.3.3 格式）

---

## 🤖 Agent 执行流程

### 步骤 1: 执行抓取脚本

```bash
./execute_daily.sh
```

### 步骤 2: Agent 调用 web_fetch 抓取网页

根据 `/tmp/dis_daily/web_fetch_instructions.json` 中的列表，并行抓取网页源。

### 步骤 3: 合并结果

```bash
python3 tools/fetch_all.py --merge \
  /tmp/dis_daily/rss_items.json \
  /tmp/dis_daily/api_items.json \
  /tmp/dis_daily/web_items.json \
  --output /tmp/dis_daily/all_items.json
```

### 步骤 4: 生成 v1.3.3 格式日报

Agent 读取 `/tmp/dis_daily/all_items.json`，按 5 维筛选标准判断，生成：
- `temp/intelligence-daily-YYYY-MM-DD.md`

### 步骤 5: 发送给用户

**发送内容**：
1. 📊 **日报摘要**（文字消息）
2. 📄 **MD 文件**（附件）

**发送方式**：
```python
# 使用 message 工具发送
message(
  action="send",
  channel="openim",
  target="group_713131094",  # 或用户 ID
  filePath="/path/to/intelligence-daily-YYYY-MM-DD.md",
  caption="📊 设计师情报站 · YYYY-MM-DD 日报（v1.3.3 格式 · XX 条情报）"
)
```

---

## 📊 日报摘要模板

```
✅ 设计师情报站 · YYYY-MM-DD 日报生成完成！

📊 抓取结果:
- RSS 源：XX 条（X/X 成功）
- API 源：XX 条（X/X 成功）
- Web 源：XX 条（X/X 成功）
- 总计：XX 条（去重后）

📈 分级统计:
- S 级（头条）：X 条
- A 级（重点）：X 条
- B 级（简讯）：X 条
- 排除：X 条

🔥 头条情报:
1. [标题 1](链接)
2. [标题 2](链接)
3. [标题 3](链接)

💡 趋势洞察:
- 趋势 1 关键词
- 趋势 2 关键词
- 趋势 3 关键词

📄 完整日报已以附件形式发送。
```

---

## 📄 MD 文件格式（v1.3.3）

```markdown
# 📊 AI/硬件/手机/设计情报日报

**日期**: YYYY 年 M 月 D 日  
**覆盖时段**: M 月 D 日 -M 月 D 日  
**情报官**: 梨然 - 阿里版  
**筛选标准**: 大厂动态 | 趋势洞察 | 设计哲学 | 竞品策略 | 判断力提升

---

### 🔴 今日头条（P0 级·S 级情报）

| 公司/机构 | 事件 | 影响 | 来源 | 条件 |
| --- | --- | --- | --- | --- |
| ... | ... | ... | ... | ... |

---

### 📱 手机领域
### 🤖 AI 领域
### 🔌 智能硬件
### 🎨 设计领域

---

### 💡 趋势洞察

#### 1. 趋势标题

**观察**: ...
**洞察**: ...
**建议**: ...

---

### 💡 今日设计思考
### 📅 明日关注
### 📌 排除内容说明
```

---

## 🛠️ 故障排查

### 问题 1：文件未发送

**检查**：
```bash
ls -la temp/intelligence-daily-*.md
```

**解决**：手动发送
```python
message(action="send", filePath="temp/intelligence-daily-YYYY-MM-DD.md")
```

### 问题 2：内容为空

**检查**：
```bash
cat /tmp/dis_daily/all_items.json | head -20
```

**解决**：重新抓取网页源

### 问题 3：格式错误

**检查**：
```bash
head -50 temp/intelligence-daily-YYYY-MM-DD.md
```

**解决**：检查 Agent 是否正确应用 v1.3.3 模板

---

## 📝 示例输出

### 摘要消息

```
✅ 设计师情报站 · 2026-03-24 日报生成完成！

📊 抓取结果:
- RSS 源：36 条（4/6 成功）
- API 源：15 条（2/4 成功）
- Web 源：24 条（16/21 成功）
- 总计：75 条（去重后）

📈 分级统计:
- S 级（头条）：3 条
- A 级（重点）：5 条
- B 级（简讯）：12 条
- 排除：15 条

🔥 头条情报:
1. Claude 获得 Mac 控制能力
2. 美图 AI Skills 接入 OpenClaw 生态
3. OpenAI 洽谈收购 Fusion 公司电力

💡 趋势洞察:
- AI Agent 进入「执行时代」
- AI 成本问题凸显
- 智能硬件进入「专利深水区」

📄 完整日报已以附件形式发送。
```

### MD 文件

见：`temp/intelligence-daily-2026-03-24.md`

---

*最后更新：2026-03-24 | 设计师情报站 v1.5.0*
