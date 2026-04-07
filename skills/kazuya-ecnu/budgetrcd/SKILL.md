---
name: budgetRcd
description: 个人记账预算管理（支持工作日/周末差异预算 + 动态预算更新机制）。Budget tracking & planning (weekday/weekend differentiated + dynamic budget carry-forward). 记账/设置预算/查余额/存钱目标。Record expenses, set budgets, check balance, savings goals.
triggers: 记账, 花了, 预算, 存钱, 花了多少, 剩余, 本月, record expense, budget, spent, save, remaining
version: 1.3.0
author: Kazuya-ECNU / Akira
license: MIT
---

# budgetRcd v1.0 - 个人记账预算管理 / Budget Tracking & Planning

## 预算规则 / Budget Rules（按 config/config.json 动态读取 / Read from config dynamically）
- 工作日（周一~五）/ Weekdays (Mon–Fri)：日预算 / Daily budget **100 元**
- 周末（周六/日）/ Weekends (Sat–Sun)：日预算 / Daily budget **200 元**

---

## 文件 / Files（数据与技能分离 / Data separated from skill）

> 数据存放路径 / Data path：`~/.openclaw/workspace/budget-data/`
> 本地用户实际路径 / Local user path：`~/Documents/02_Personal/01_Budget/`

- `config/pools.json` — 预算池 / Budget pools {id: {name}}
- `config/config.json` — {reminder_day, timezone, budget_rules: {weekday, weekend}, dynamic_budget: {enabled: true|false}}
- `data/budget_YYYYMM.json` — 月度总预算 / Monthly budget {month, total, pools}
- `data/expense_YYYYMM.json` — 开销记录 / Expense records [{date, pool, amount, note, image_path?}]
- `data/goals.json` — 储蓄目标 / Savings goals {monthly: {target, desc}, custom: {days, target, desc}}
- `images/` — 开销相关照片 / Expense photos，按日期命名 / named `YYYY-MM-DD_merchant.jpg`

---

## 操作 / Operations

1. **记账 / Record Expense**
   解析日期/金额/类型 → 追加到 expense_YYYYMM.json → 计算剩余并反馈
   Parse date/amount/category → append to expense_YYYYMM.json → calculate remaining & respond

2. **设预算 / Set Budget**
   按 budget_rules 计算月总预算 → 写入 budget_YYYYMM.json
   Calculate monthly total per budget_rules → write to budget_YYYYMM.json

3. **查状态 / Check Status**
   读预算+开销 → 按工作日/周末分别计算已花/剩余 → 输出进度
   Read budget + expenses → calculate spent/remaining by weekday/weekend → output progress

4. **存钱目标 / Savings Goal**
   解析目标 → 写入 goals.json → 算每日需存
   Parse target → write goals.json → calculate daily savings needed

5. **每月提醒 / Monthly Reminder**
   16号检查，未设预算则提醒 / Check on 16th, remind if no budget set

6. **超支提醒 / Overspend Alert**
   记账后检查当日累计，超过日预算立即提醒
   After recording, check daily total; alert if over daily budget immediately

---

## 动态预算机制 / Dynamic Budget (v1.3+)

### 配置 / Configuration
```json
{
  "dynamic_budget": {
    "enabled": true
  }
}
```
开启后：未用完的预算或赤字会平均分配到剩余天数（工作日/周末分开）。
When enabled: unused budget or overspend carries forward, spread evenly across remaining days (weekday/weekend calculated separately).

### 核心逻辑
- **工作日**和**周末**分开计算，互不影响
- Past unused budget → spreads across remaining days (加到剩余天数的日预算上)
- Past overspend (赤字) → reduces remaining days' daily budget (从剩余天数的日预算中扣除)

### 计算公式
```
已过时期:
  past_weekday_budget = past_weekday_count × 100
  past_weekend_budget = past_weekend_count × 200
  unused_weekday = past_weekday_budget - spent_weekday
  unused_weekend = past_weekend_budget - spent_weekend

剩余时期:
  remaining_weekday_budget = total_weekday_budget - past_weekday_budget
  remaining_weekend_budget = total_weekend_budget - past_weekend_budget
  
  dynamic_weekday = (remaining_weekday_budget + unused_weekday) / remaining_weekday_count
  dynamic_weekend = (remaining_weekend_budget + unused_weekend) / remaining_weekend_count
```

### 示例 / Example (4月7日查询)
- 已过: 1工作日(花100.7) + 1周末日(花240.7)
- 工作日赤字: 100.7 - 100 = -0.7 → 动态日预算 = (1800 + (-0.7)) / 18 = 99.96
- 周末赤字: 240.7 - 200 = -40.7 → 动态日预算 = (1200 + (-40.7)) / 6 = 193.22

## 注意事项 / Notes

- 不使用统一日均预算，按工作日/周末区分计算
  No unified daily budget; calculate separately for weekdays vs weekends
- Past unused/overspent budget dynamically adjusts remaining days' daily budget
- 查询时按"本周工作日剩余"和"本周末剩余"分别反馈
  When querying, report "weekday remaining" and "weekend remaining" separately
- 每个工作日日预算 100元，周末日预算 200元
  Each weekday: 100, each weekend day: 200

---

## 📖 使用示例 / Usage Examples

### 记账 / Recording
```
用户: 食其家花了37块9
助手: 记上了！✅ 食其家 -37.9元 | 今日已花 37.9元

User: Spent 37.9 at Sikich
Assistant: Recorded! ✅ Sikich -37.9 | Today's total: 37.9
```

### 查询今日花销 / Today's Expenses
```
用户: 今天钱花哪了
助手: 4月5日花销汇总 💸
     食其家 鸡蛋灌饼  20元
     罗森 苏打水      4.8元
     皮爷咖啡 冰摇柠檬咖啡 42元
     今日合计: 66.8元 | 剩余预算: 3133.2元

User: Where did I spend today?
Assistant: Apr 5 expenses 💸
     Sikich - 20
     Lawson - 4.8
     Peet's Coffee - 42
     Total: 66.8 | Remaining: 3133.2
```

### 查看本月预算状态 / Monthly Budget Status
```
用户: 本月还剩多少
助手: 4月预算状态 📊
     总预算: 3300元 | 已花: 239.8元 | 剩余: 3060.2元
     工作日剩余: 1900元 | 周末剩余: 1400元

User: How much left this month?
Assistant: Apr budget 📊
     Total: 3300 | Spent: 239.8 | Remaining: 3060.2
     Weekdays left: 1900 | Weekends left: 1400
```

### 重置预算 / Reset Budget
```
用户: 清空之前的开销记录，从今天开始重新记
助手: ✅ 已清空！4月从5日起，剩余26天
     工作日(19天): 1900元 周末(7天): 1400元
     总剩余预算: 3300元

User: Clear all records, start fresh from today
Assistant: ✅ Cleared! Apr starting from the 5th, 26 days left
     Weekdays(19): 1900 | Weekends(7): 1400 | Total: 3300
```

### 拍照记录 / Photo Receipt
```
用户: [发送收据照片]
助手: 看到照片了！这是什么？花了多少？
用户: 便利店买了零食 23块
助手: 记上了！✅ 全家 -23元 | 剩余预算: 3122.2元
      📎 图片已保存: images/2026-04-06_family.jpg

User: [sends receipt photo]
Assistant: Got it! What is it and how much?
User: Snacks at FamilyMart, 23
Assistant: Recorded! ✅ FamilyMart -23 | Remaining: 3122.2
      📎 Image saved: images/2026-04-06_family.jpg
```

**记账时附带图片**：图片保存到 `images/YYYY-MM-DD_merchant.jpg`，expense 记录中 `image_path` 字段存储该路径。
When recording with photo: image saved to `images/YYYY-MM-DD_merchant.jpg`, `image_path` in expense record stores the path.

### 超支提醒 / Overspend Alert
```
用户: 罗森买水 8块
助手: 记上了！✅ 罗森 -8元
     ⚠️ 今日已花 244.8元，超过周日预算(200元) 44.8元！

User: Got water at Lawson, 8
Assistant: Recorded! ✅ Lawson -8
     ⚠️ Today: 244.8, over Sunday budget (200) by 44.8!
```

### 设置存钱目标 / Savings Goal
```
用户: 每月存1500块
助手: 已设置！💰 4月存钱目标: 1500元
     每日需存: ~58元 | 本月剩余: 26天

User: Save 1500 per month
Assistant: Set! 💰 Apr savings goal: 1500
     Daily: ~58 | Days left: 26
```
