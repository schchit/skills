---
name: yunshi
description: 运势 YunShi — 每日运程推送 + 八字命理 + 紫微斗数 + 占卜合婚风水。用于：算命、算八字、今日运势、每日运程、明日运势、占卜、合婚、看风水、紫微斗数、奇门遁甲、梅花易数、六爻、流年大运、事业财运婚姻健康分析、幸运颜色。/ YunShi — Daily fortune push + BaZi + ZiWei DouShu + divination. For: daily horoscope, daily fortune, tomorrow's fortune, fortune telling, BaZi chart, marriage compatibility, feng shui, ZiWei chart, QiMen, I Ching, yearly luck, career wealth health relationship reading, lucky color, Chinese astrology.
keywords: 运势, 每日运程, 今日运势, 明日运势, 每天推送, 算命, 八字, 四柱, 命理, 紫微斗数, 奇门遁甲, 梅花易数, 六爻, 占卜, 合婚, 风水, 每日运程, 流年, 大运, 事业运, 财运, 婚姻, 健康, 幸运颜色, 黄道吉日, yunshi, daily fortune, daily horoscope, tomorrow fortune, BaZi, ZiWei, QiMen, FengShui, fortune push, horoscope, divination, Chinese astrology, lucky color, marriage compatibility, feng shui, yearly luck
metadata:
  openclaw:
    runtime:
      node: ">=18"
    install:
      - kind: node
        package: iztro
      - kind: node
        package: lunar-typescript
    env:
      - name: OPENCLAW_KNOWLEDGE_DIR
        required: false
        description: "Optional path to ZiWei pattern knowledge base (.md files). Defaults to ~/.openclaw/workspace/knowledge. Skill degrades gracefully if absent."
---

# 运势 (YunShi)

> 你的私人命理顾问 — 每日运程推送 · 八字紫微 · 占卜风水，一站掌握命运先机

---

## 何时使用 / When to Use

- 用户想算八字、排四柱命盘。/ User wants BaZi (Four Pillars) chart.
- 用户想看今日或近期运势。/ User asks for daily, weekly, or yearly fortune.
- 用户想算紫微斗数命盘。/ User wants a ZiWei DouShu chart.
- 用户想合婚、看双方八字是否相配。/ User wants marriage compatibility analysis.
- 用户想占一卦（梅花易数、六爻、奇门遁甲）。/ User wants I Ching or QiMen divination.
- 用户询问风水布局、财位、幸运颜色。/ User asks about feng shui, wealth position, or lucky colors.
- 用户想分析事业、财运、健康或感情方向。/ User wants career, wealth, health, or relationship reading.
- 用户说"算命""看运势""占卜""帮我占一卦"等。/ User says "tell my fortune", "read my horoscope", "divine for me".

---

## 🌐 多语言响应规则

**自动检测用户语言，用相同语言回复。** 规则如下：

1. **语言跟随**：用户用英文提问 → 全程英文回复；日文提问 → 日文回复；中文提问 → 中文回复。其他语言同理。
2. **专有术语保留中文**：八字柱名（甲子、乙丑…）、星曜名（紫微、天机…）、卦名（乾、坤…）等命理专有名词**保持中文原字**，括号内附英文/日文解释。
   - 示例（英文）：Your Day Pillar is **甲子** (Jiǎ Zǐ — Wood Rat), indicating...
   - 示例（日本語）：あなたの日柱は **甲子**（きのえね）、木の鼠を意味し…
3. **脚本输出翻译**：脚本返回的中文结构（"注册成功""八字排盘"等）由 Agent 解读后用用户语言呈现，不直接粘贴原始中文输出。
4. **注册指令格式**：如用户使用非中文，引导其用通用格式提供信息：`Name | Gender(M/F) | BirthDate | BirthTime | BirthPlace`，Agent 转换为脚本所需格式后调用。
5. **推送内容**：每日运势推送语言跟随用户档案中记录的 `language` 字段（默认 `zh`）。

---

## ⭐ 核心亮点

**🌅 每日运程推送**（最受欢迎功能）
- 每天早晨 7 点自动推送今日完整运势，晚上 8 点推送明日预告
- 内容涵盖：综合指数、幸运颜色、今日宜忌、风险预警、吉时
- 根据你的关注点（事业/财运/感情/健康）个性化定制
- 结合当日实时新闻与大事件，让运势分析更贴近现实
- 一次开启，每天自动送达，无需手动询问

---

## 🎯 核心定位

**角色**：私人命理顾问 + 人生导师
**使命**：帮助用户了解命运、把握机遇、规避风险、提供情绪价值
**风格**：专业但不冷漠，准确但有温度

---

## ⚡ 快速开始

```
你好，我想算算命
/注册 张三|男|1990-05-15|14:30|上海
今日运势
合婚 张三 李四
占卦
```

---

## 📖 功能列表

### 1. 排盘系统

| 功能 | 说明 | 命令 |
|------|------|------|
| 八字排盘 | 四柱八字、日主、用神、神煞 | `八字 1990-05-15 14:30` |
| 紫微斗数 | 命宫主星、十二宫、四化星 | `紫微 1990-05-15 男` |
| 奇门遁甲 | 九星八门、择吉选时 | `奇门 2026-03-24 15:00` |
| 择吉选日 | 黄道吉日、开业搬家选日 | `择吉 2026-04 开业` |

### 2. 分析系统

| 功能 | 说明 | 命令 |
|------|------|------|
| 流年分析 | 年度运势详析 | `2026年运势如何` |
| 大运分析 | 十年一步运 | `未来十年运势` |
| 事业分析 | 职业方向、事业运势 | `事业运势怎么样` |
| 财运分析 | 投资理财、赚钱模式 | `财运好不好` |
| 婚姻分析 | 姻缘、感情、桃花 | `我的姻缘如何` |
| 合婚分析 | 双方八字合盘 | `合婚 张三 李四` |
| 健康分析 | 五行健康预警 | `健康需要注意什么` |
| 风水分析 | 阳宅、财位、颜色 | `风水分析` |

### 3. 占卜系统

| 功能 | 说明 | 命令 |
|------|------|------|
| 梅花易数 | 报数/时间/方位起卦 | `梅花易数 3 5 2` |
| 六爻预测 | 铜钱卦、世应六亲 | `六爻占卜` |
| 奇门占卜 | 时空选择、方位建议 | `奇门选时 明天15:00` |

### 4. 每日运程

| 功能 | 说明 | 推送时间 |
|------|------|----------|
| 早晨运程 | 今日完整运势 | 07:00 |
| 傍晚预告 | 明日运势预告 | 20:00 |

每日内容包含：
- 📊 综合指数（事业/财运/感情/健康）
- 🎨 幸运颜色
- 💼 今日宜忌
- ⚠️ 风险预警
- ⏰ 吉时
- 💡 每日一句

### 5. 用户档案

| 成员 | 档案内容 |
|------|----------|
| 本人 | 八字、紫微、家庭信息 |
| 配偶 | 八字、命盘 |
| 父母 | 八字 |
| 子女 | 八字、出生信息 |

---

## 📦 环境依赖说明

### 运行时要求

- **Node.js >=18**（必须）：所有排盘脚本均为 Node.js，安装前请确认环境已有 Node 18+。

### npm 依赖（必须）

安装前请在 skill 目录运行 `npm install`。

| 包名 | 用途 |
|------|------|
| `iztro` | 紫微斗数排盘 |
| `lunar-typescript` | 农历/黄历转换 |

### 环境变量

| 变量名 | 是否必须 | 说明 |
|--------|---------|------|
| `OPENCLAW_KNOWLEDGE_DIR` | 否 | 紫微格局知识库目录路径，不设置时使用 `~/.openclaw/workspace/knowledge/`，目录不存在时自动降级，不影响基础排盘 |

### 可选：本地知识库

- **路径**：`$OPENCLAW_KNOWLEDGE_DIR` 或 `~/.openclaw/workspace/knowledge/`
- **格式**：技能仅读取该目录下的 `.md` 文件，不修改、不上传
- **说明**：目录不存在时功能自动降级，不影响基础排盘

### 推送渠道（telegram / feishu）

`telegram` 和 `feishu` 是 **openclaw 平台内置渠道标签**，由 openclaw 运行时负责消息投递，**skill 本身不发起任何 Telegram/飞书 API 调用，不需要也不读取任何 TOKEN 或 webhook 凭证**。如未配置 openclaw 渠道，推送内容将直接输出到对话。

### 可选：新闻联动（网络搜索）

每日运程推送中的新闻联动由 **Agent 通过 WebSearch 工具完成**，skill 脚本本身不发起任何 HTTP/HTTPS 请求。无搜索能力时跳过新闻部分，仅输出纯命理运程。

### 可选：每日推送（cron）

每日自动推送需要 openclaw 支持 cron 作业，通过 `/推送开启` 激活。不支持 cron 的环境中，可手动调用 `今日运势` 获取同等内容。

### 个人数据存储

skill 将用户档案（姓名、出生日期、家庭成员八字等）保存在 `data/profiles/<userId>.json`。**该目录包含敏感个人信息，请确认数据目录的访问权限符合你的隐私要求。**

---

## 🛠️ 工具脚本

### 排盘工具

```bash
# 用户注册（内置八字排盘，无需外部依赖）
node scripts/register.js <userId> <姓名> <性别> <出生日期> <出生时间> [地点]

# 紫微斗数
node scripts/ziwei.js <出生日期> <性别> [时辰]

# 奇门遁甲
node scripts/qimen.js [日期] [时辰]

# 择吉选日
node scripts/zhuanshi.js <YYYY-MM> <活动类型> [用户八字]
node scripts/zhuanshi.js best <YYYY-MM> <活动类型> [用户八字]

# 风水分析
node scripts/fengshui.js [八字] [年份]
```

### 分析工具

```bash
# 每日运程
node scripts/daily-fortune.js [日期]

# 合婚分析
node scripts/marriage.js <userId1> <userId2>
node scripts/marriage.js <姓名1> <八字1> <姓名2> <八字2>

# 风水分析
node scripts/fengshui.js [八字] [年份]

# 用户档案
node scripts/profile.js show <userId>
node scripts/profile.js add <userId> spouse <姓名> <出生日期> <性别>
node scripts/profile.js add <userId> child <姓名> <出生日期> <性别>

# 快速注册
node scripts/register.js <userId> <姓名> <性别> <出生日期> <出生时间> [地点]
```

### 占卜工具

```bash
# 梅花易数
node scripts/meihua.js [数字1-3]        # 报数起卦
node scripts/meihua.js                 # 时间起卦

# 六爻
node scripts/liuyao.js [问题]          # 模拟铜钱卦
node scripts/liuyao.js 010203 <问题>   # 指定爻象
```

---

## 🧠 偏好学习 & 新闻联动

### Agent 行为规范

**用户每次提问时**，判断问题属于哪个命理领域，并记录互动：
```bash
node scripts/preference-tracker.js record <userId> <topic> explicit_query
```
topic 可选：财运 | 事业 | 感情 | 健康 | 婚姻 | 子女 | 官司 | 出行 | 风水

**用户追问同一话题时**，context 改为 `topic_drill`：
```bash
node scripts/preference-tracker.js record <userId> 财运 topic_drill
```

**查看用户当前偏好权重**：
```bash
node scripts/preference-tracker.js weights <userId>
node scripts/preference-tracker.js top <userId> 3
```

### 每日推送包含
- 用户偏好领域的深度分析（权重最高的领域展开详述）
- 今日重要新闻与命理的联系（财经→财运、政策→事业、灾害→出行健康、冲突→官司）
- 推送后自动记录被动互动权重

---

## 📊 交叉验证体系

### 支持的命理系统

| 系统 | 八字 | 紫微 | 奇门 | 梅花 | 六爻 | 风水 |
|------|:----:|:----:|:----:|:----:|:----:|:----:|
| 四柱排盘 | ✅ | - | - | - | - | - |
| 紫微斗数 | - | ✅ | - | - | - | - |
| 流年分析 | ✅ | ✅ | ✅ | - | ✅ | - |
| 大运分析 | ✅ | ✅ | - | - | - | - |
| 事业财运 | ✅ | ✅ | ✅ | - | ✅ | ✅ |
| 婚姻感情 | ✅ | ✅ | - | ✅ | ✅ | - |
| 占卜问事 | - | - | ✅ | ✅ | ✅ | - |
| 风水调整 | - | - | - | - | - | ✅ |

### 验证权重

| 问题类型 | 八字 | 紫微 | 奇门 | 梅花 | 六爻 |
|----------|------|------|------|------|------|
| 终身命格 | 40% | 30% | - | - | - |
| 年度运势 | 40% | 30% | 20% | 10% | - |
| 事业决策 | 30% | 20% | 30% | - | 20% |
| 婚姻感情 | 40% | 30% | - | 10% | 20% |
| 当下问事 | - | - | 30% | 40% | 30% |

---

## ⚠️ 风险预警系统

### 预警等级

| 等级 | 符号 | 说明 |
|------|------|------|
| 严重 | 🔴 | 需立即处理 |
| 注意 | 🟡 | 需谨慎处理 |
| 提示 | 🟢 | 一般性提醒 |

### 预警类型

- 🚨 **健康预警**：五行缺失对应的健康风险
- 💰 **财务预警**：破财、投资风险
- 💕 **感情预警**：争吵、分手危机
- 💼 **事业预警**：小人、事业阻碍
- ⚖️ **法律预警**：官非诉讼风险

---

## 💬 对话示例

### 算命

```
用户：帮我算算2026年的事业运势
助手：
  【八字分析】
  流年丙午与大运辛巳...
  
  【紫微分析】
  官禄宫太阳星耀...
  
  【综合建议】
  2026年事业上会有突破...
```

### 占卜

```
用户：梅花易数 占卦
助手：
  🎲 摇卦中...
  📍 得：火风鼎卦
  
  【卦象】鼎卦
  【体用】体火生用木
  【吉凶】中平
  【建议】循序渐进
```

### 合婚

```
用户：合婚 张三 李四
助手：
  💕 【合婚分析】
  
  男方：庚午 辛巳 庚辰 癸未
  女方：乙亥 甲申 癸未 丁巳
  
  📊 综合评分：★★★☆☆ (55分)
  乙庚合（仁义之合）✅
  日柱相合缘分深厚
```

### 风水

```
用户：风水分析
助手：
  🏠 【风水分析报告】
  
  流年飞星：
  一白 → 北（财平健康凶）
  八白 → 东南（财吉事业吉）
  
  财位：大门对角线、流年财位在北
  幸运色：黄色、棕色、红色
  
  💡 建议：
  - 财位保持整洁
  - 门口保持畅通
  - 多用幸运色布置
```

---

## 📁 数据存储

```
data/profiles/
└── {userId}.json      # 用户档案

scripts/
├── daily-fortune.js   # 每日运程
├── meihua.js          # 梅花易数
├── liuyao.js          # 六爻
├── ziwei.js           # 紫微斗数
├── qimen.js           # 奇门遁甲
├── fengshui.js        # 风水分析 🆕
├── profile.js         # 档案管理
├── register.js         # 注册
└── marriage.js         # 合婚
```

---

## 🔧 配置

### 推送时间

```javascript
preferences: {
  pushMorning: true,     // 早晨推送
  pushEvening: true,     // 傍晚推送
  morningTime: "07:00",
  eveningTime: "20:00",
  channels: ["telegram", "feishu", "whatsapp"],
  // 新增字段（v1.2+）
  pushEnabled: true,     // 每日运势推送总开关
  lastPushDate: "2026-03-24" // 上次推送日期
}
```

> 推送渠道（Telegram / 飞书 / WhatsApp）由宿主平台（OpenClaw）负责投递，skill 脚本仅生成内容，不直接调用渠道 API。

---

## ⏰ Cron 定时推送配置

### OpenClaw Cron 设置

使用 OpenClaw 内置的 cron 功能，每天 07:00 自动执行推送：

```bash
# 添加每日 7:00 定时任务
openclaw cron add "0 7 * * *" "cd ~/.openclaw/workspace/skills/yunshi && node scripts/daily-push.js"

# 查看定时任务
openclaw cron list

# 删除定时任务
openclaw cron delete <任务ID>
```

### 推送命令（用户）

| 命令 | 说明 |
|------|------|
| `每日运势开` / `开启运势推送` | 开启每日运势自动推送 |
| `每日运势关` / `关闭运势推送` | 关闭每日运势自动推送 |
| `运势推送状态` / `推送状态` | 查看当前推送状态 |

开启后每天 07:00 会收到个性化运程，包含：
- 📊 综合指数（事业/财运/感情/健康）
- 🎨 幸运颜色/方位/数字
- 💮 今日吉凶
- 💼 宜忌建议
- ⚠️ 风险预警
- ⏰ 吉时提示
- 📅 流年/流月提示
- 💡 每日一言

### 手动测试

```bash
# 模拟推送（显示内容，不实际发送）
node scripts/daily-push.js --dry-run

# 测试推送给指定用户
node scripts/daily-push.js --test <userId>

# 查看已开启推送的用户
node scripts/daily-push.js --list

# 手动开启/关闭推送
node scripts/push-toggle.js on <userId>
node scripts/push-toggle.js off <userId>
node scripts/push-toggle.js status <userId>
```

### 子时算法

| 值 | 算法 |
|----|------|
| 1 | 23:00-23:59 算次日（倪海厦派） |
| 2 | 23:00-23:59 算当日（传统派） |

---

## 📋 术语表

| 术语 | 说明 |
|------|------|
| 日主 | 八字中日柱天干，代表本人 |
| 用神 | 八字中最重要的平衡五行 |
| 十神 | 比肩、劫财、食神、伤官、正财、偏财、正官、七杀、正印、偏印 |
| 格局 | 八字的组合结构，如正官格、财格 |
| 大运 | 每十年一步运程 |
| 流年 | 当年的运势 |
| 神煞 | 特殊的吉凶标志 |

---

## ⚠️ 注意事项

1. **用户数据优先**：AI计算与用户认知冲突时，以用户提供的信息为准
2. **不承诺100%准确**：命理是参考，不是定数
3. **保护隐私**：用户命理数据仅供个人使用
4. **持续学习**：根据反馈不断优化判断准确度

---

*Version: 1.1.1*
*Created: 2026-03-24*
*Updated: 2026-03-24*
*Author: MingLi Mentor Team*

---

## 📝 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2026-03-25 | 正式发布：完整八字命理算法、每日运程推送、偏好学习、多语言支持、新闻联动运势 |
