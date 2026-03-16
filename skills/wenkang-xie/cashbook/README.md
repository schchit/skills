# cashbook

> 个人记账 OpenClaw Skill，数据本地优先，支持自然语言、截图录入，提供预算追踪和周/月报告。

## 核心特性

✅ **自然语言记账** — "今天咖啡花了 38" → 自动解析金额/分类/账户  
✅ **截图记账** — 上传支付宝/微信/小票截图，自动提取字段  
✅ **账户管理** — 支持借记卡、信用卡、电子钱包，自动余额计算  
✅ **预算追踪** — 按分类或总预算设置月度限额，超支提示  
✅ **周月报告** — ASCII 进度条，分类分布 + 预算执行情况  
✅ **CSV 导入** — 支付宝/微信账单批量导入，自动分类和重复检测  
✅ **数据本地** — SQLite 单文件，完全数据主权，随时导出  

## 安装

```bash
clawhub install cashbook
```

首次使用初始化数据库：
```bash
python3 scripts/init.py
```

## 快速开始

### 1. 记一笔
```
你：今天买菜花了 68，用微信钱包
我：✅ 已记录：支出 ¥68.00 / 购物 / 微信钱包 / 今天
```

### 2. 预算
```
你：设置餐饮月预算 2000 块
我：✅ 已设置 餐饮 月度预算 ¥2,000.00

你：本月餐饮还剩多少
我：本月餐饮预算：¥2,000.00
   已支出：¥1,234.00（61.7%）
   剩余：¥766.00
   状态：正常 ✅
```

### 3. 截图记账
上传支付宝/微信账单截图 → 自动识别金额/商户/时间 → 确认入账

### 4. 月报
```
你：出一份本月月报
我：📊 2026年3月账单
   总支出：¥4,567.00    总收入：¥15,000.00    净额：+¥10,433.00
   
   支出分类排行：
     1. 餐饮      ¥1,234.00  27.0%  █████░░░░
     2. 交通      ¥890.00    19.5%  ████░░░░░
     ...
```

## 文件结构

```
cashbook/
├── SKILL.md                 # Skill 指令说明
├── references/              # 参考文档
│   ├── schema.md           # 数据模型
│   ├── account.md          # 账户管理说明
│   └── budget.md           # 预算管理说明
└── scripts/                # Python 脚本
    ├── db.py               # 数据库公共模块
    ├── init.py             # 初始化
    ├── add_tx.py           # 添加交易
    ├── delete_tx.py        # 删除交易
    ├── account.py          # 账户管理
    ├── category.py         # 分类管理
    ├── budget.py           # 预算管理
    ├── query.py            # 查询流水
    ├── report.py           # 周月报
    ├── import_csv.py       # CSV 导入
    └── export.py           # 数据导出
```

## 技术栈

- **语言**: Python 3
- **存储**: SQLite（本地单文件）
- **依赖**: 零第三方包（仅用标准库）
- **数据路径**: `~/.local/share/cashbook/cashbook.db`

## 数据安全

- ✅ 100% 本地存储，无云同步
- ✅ 只存卡号尾号，不存完整卡号/密码
- ✅ 用户随时可导出为 CSV/JSON
- ✅ 支持自定义数据库路径（`CASHBOOK_DB` 环境变量）

## 常见命令

### 对话触发（自然语言）
- "记一笔" → 自动识别金额/分类
- "今天花了多少" → 查询日期汇总
- "设置预算" → 设置月度限额
- "本月月报" → 生成报告
- "删除最后一笔" → 撤销记录

### 手动脚本（需要指定参数）
```bash
# 账户
python3 scripts/account.py add --nickname "招行卡" --type debit
python3 scripts/account.py list
python3 scripts/account.py default --id 1

# 预算
python3 scripts/budget.py set --category 餐饮 --amount 2000
python3 scripts/budget.py query --all

# 查询
python3 scripts/query.py --last 10
python3 scripts/query.py --period month

# 报告
python3 scripts/report.py --period month

# 导入
python3 scripts/import_csv.py --file ~/Downloads/alipay.csv --account "支付宝"

# 导出
python3 scripts/export.py --format csv
```

## 许可证

MIT

---

**Made with ❤️ for cashbook lovers**
