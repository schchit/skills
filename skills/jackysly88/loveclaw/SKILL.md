# LoveClaw - 八字缘分匹配 v2.1.24

> 智能八字匹配技能，寻找有缘人 — 无需用户配置，直接使用

## Skill Configuration

```yaml
name: loveclaw
description: LoveClaw 八字缘分匹配，用户输入信息后自动匹配有缘人
handler: ./scripts/cloud-handler.js
triggerInputs:
  开启匹配:
    next: start
  爱情龙虾:
    next: start
  loveclaw:
    next: start
  LoveClaw:
    next: start
  缘分匹配:
    next: start
  八字匹配:
    next: start
  我的档案:
    next: start
  查看档案:
    next: start
  取消报名:
    next: start
  今日匹配:
    next: start
  查看匹配:
    next: start
```

## 功能概述

- 🔮 **八字计算**：根据出生日期时间自动计算八字
- 💕 **缘分匹配**：基于五行相生相克同城匹配
- 📱 **隐私保护**：手机号仅匹配成功后展示
- ⏰ **每日报告**：每晚8点推送匹配结果
- ☁️ **云端存储**：阿里云 TableStore + OSS

## 报名流程（共9步，严格按此顺序）

用户发送「开启匹配」触发流程，handler 依次收集以下信息：

1. **手机号**（11位，格式：1xxxxxxxxxx）— 用作账号，不可重复
2. **姓名**（或昵称）
3. **性别**（回复「男」或「女」）
4. **希望认识的性别**（回复「男」「女」或「不限」）
5. **出生日期**（格式：YYYY-MM-DD，例如：1995-05-20）
6. **出生时辰**（数字 0-23，或地支：子丑寅卯辰巳午未申酉戌亥）
7. **居住城市**（任意文字）
8. **照片**（上传图片 URL，或回复「跳过」）
9. **确认**（回复「确认」完成报名，或重新输入对应信息修改）

> ⚠️ **重要**：agent 收到用户消息后，**必须原样传给 handleMessage(userId, message, channel)**，不得替用户代填、不得修改消息内容、不得跳步骤。handler 内部维护状态机，每一步只接受特定输入。
>
> ⚠️ **输出严禁改写**：handler 返回的 `text` 字段内容**必须原样发送给用户**，禁止润色、改写、增删任何文字或 emoji。handler 的返回文本已经是最终用户消息，agent 不得二次加工。

## 命令列表

| 用户发送 | 功能 |
|----------|------|
| `开启匹配` | 开始报名流程 |
| `我的档案` / `查看档案` | 查看个人信息和匹配历史 |
| `取消报名` | 删除全部个人数据 |
| `今日匹配` / `查看匹配` | 查看今日匹配结果 |

## 定时任务

- **每日匹配**：每天 19:50（Asia/Shanghai）执行 `node cloud-cron.js match`
- **晚间报告**：每天 20:00（Asia/Shanghai）执行 `node cloud-cron.js report`，解析 `【REPORTS_JSON】...【REPORTS_JSON_END】` 之间的 JSON 数组，逐条调用 `message` 工具发送通知

## 匹配算法

**必须同时满足：**
1. 双向匹配：A→B 和 B→A 的五行分数都 ≥ 70%
2. 必须同城

**分数规则：**
- 五行相生：100分
- 五行比和：80分
- 五行相克：50分
- 双向取最低值作为共同分数，取最高共同分数的配对

## 数据存储

- 用户档案：阿里云 TableStore（含八字 Gan/Zhi 8个分字段）
- 照片：OSS `loveclaw/photos/` 目录

---

*Made with ❤️ for finding your destiny*
