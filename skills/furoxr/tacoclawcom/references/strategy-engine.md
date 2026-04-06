# Taco Strategy Engine

策略引擎的职责：获取实时市场数据 → 计算技术指标 → 识别市场状态 → 匹配策略 → 输出可执行交易决策 → 等待用户确认 → 执行交易。

---

## Table of Contents

1. [Complete Workflow](#complete-workflow)
2. [Technical Indicators](#technical-indicators)
3. [Market Regime Detection](#market-regime-detection)
4. [Strategy Matching & Parameters](#strategy-matching--parameters)
5. [Recommendation Card Output](#recommendation-card-output)
6. [Execution Pipelines](#execution-pipelines)
7. [Autopilot Configuration](#autopilot-configuration)
8. [Sharpe Ratio Adaptation](#sharpe-ratio-adaptation)
9. [Key Principles](#key-principles)

---

## Complete Workflow

```
1. get-balance → 确定可用 USDC
2. 获取市场数据（使用 taco 命令或 Hyperliquid fallback）→ 计算指标 → 识别状态 → 匹配策略
3. 输出推荐交易卡片（至少 1 个，最多 3 个）
4. 等待用户选择
5. 用户确认后 → 执行该订单
```

**关键约束：risk_usd ≤ 用户 taco 账户 USDC 可用余额**

---

## Technical Indicators

从 K 线 OHLCV 数据计算以下指标。所有 close 价格取 `parseFloat(candle.c)`。

### EMA（指数移动平均线）

```
EMA(period, prices):
  multiplier = 2 / (period + 1)
  ema[0] = prices[0]
  for i = 1 to len(prices)-1:
    ema[i] = (prices[i] - ema[i-1]) * multiplier + ema[i-1]
  return ema
```

需要计算：EMA9, EMA20, EMA50

### MACD

```
MACD:
  fast_ema = EMA(12, closes)
  slow_ema = EMA(26, closes)
  macd_line = fast_ema - slow_ema
  signal_line = EMA(9, macd_line)
  histogram = macd_line - signal_line
```

判断：
- MACD line > signal line 且 histogram 扩大 → 看多
- MACD line < signal line 且 histogram 缩小 → 看空
- Golden cross / Death cross = macd_line 穿越 signal_line

### RSI

```
RSI(period=14, closes):
  for i = 1 to len(closes)-1:
    change = closes[i] - closes[i-1]
    gain = max(change, 0)
    loss = abs(min(change, 0))
  avg_gain = SMA(gains, period)  // 初始值用 SMA
  avg_loss = SMA(losses, period)
  // 后续用 Wilder 平滑：
  avg_gain = (prev_avg_gain * (period-1) + current_gain) / period
  avg_loss = (prev_avg_loss * (period-1) + current_loss) / period
  RS = avg_gain / avg_loss
  RSI = 100 - 100 / (1 + RS)
```

判断：RSI > 70 超买；RSI < 30 超卖；50 为中性分界。

### ATR（平均真实波幅）

```
ATR(period=14, candles):
  TR = max(high - low, abs(high - prev_close), abs(low - prev_close))
  ATR = SMA(TR, period)  // 初始值
  // 后续 Wilder 平滑
```

用途：止损距离 = 1.5-2x ATR；判断波动率水平。

### Bollinger Bands

```
BB(period=20, closes):
  middle = SMA(closes, period)
  std = StdDev(closes, period)
  upper = middle + 2 * std
  lower = middle - 2 * std
  bandwidth = (upper - lower) / middle
```

判断：bandwidth 收窄 → 即将突破；价格触及 upper/lower → 可能回归。

### 简化判断（K 线不足 26 根时）

1. 最新 close vs 20 根 close 的 SMA → 趋势方向
2. 最近 5 根 K 线的 high/low range → 波动率
3. 最近 3 根 K 线方向一致性 → 动量
4. 当前价格在最近 20 根 K 线 range 中的位置 → 相对强弱

---

## Market Regime Detection

基于指标判断当前属于哪种市场状态：

| 状态 | 判断条件 | 适配策略 |
|---|---|---|
| **强趋势上涨** | close > EMA20 > EMA50; MACD > 0 且扩大; 连续 HH/HL | Trend Following, Pullback, Momentum Breakout |
| **强趋势下跌** | close < EMA20 < EMA50; MACD < 0 且缩小; 连续 LH/LL | Trend Following (做空), Momentum Breakout (做空) |
| **震荡/区间** | 价格在 BB upper/lower 之间反复; RSI 在 40-60; 无清晰 HH/HL 结构 | Range Trading, Mean Reversion, S&R |
| **突破酝酿** | BB bandwidth 压缩至极低; 成交量逐渐放大; OI 扩张 | Momentum Breakout |
| **极端波动** | ATR 异常放大(>2x 20日均值); 资金费率极端; 清算级联 | Scalping (小仓), DCA (分批) |
| **低迷/盘整** | 成交量萎缩; ATR 极低; 资金费率平稳 | 等待 或 DCA |

### HH/HL/LH/LL 识别方法

从 4h 或 1d K 线中：
1. 找局部高点（前后各 2 根 K 线的 high 都更低）
2. 找局部低点（前后各 2 根 K 线的 low 都更高）
3. 高点序列递增 = HH；低点序列递增 = HL → 上涨结构
4. 高点序列递减 = LH；低点序列递减 = LL → 下跌结构
5. 结构破坏（MSB）= 新低点跌破前低点（上涨结构破坏）或新高点突破前高点（下跌结构破坏）

---

## Strategy Matching & Parameters

### User Parameters

在出决策前，必须明确以下参数（优先从用户设置读取，其次用 get-balance 推算默认值）：

| 参数 | 来源 |
|---|---|
| 可用 USDC 余额 | `get-balance`（taco 账户） |
| 当前持仓 | `get-positions` |
| 风险偏好 | 用户设定或默认 conservative |
| 杠杆偏好 | 用户设定或按余额推算 |

**Symbol 自动推荐逻辑：**

1. 优先推荐 BTC/ETH（稳健资产）
2. 若 BTC/ETH 无清晰 setup，扫描高流动性山寨（SOL、BNB、DOGE 等）
3. 排除：低流动性、高价差、当天异常波动超过 15% 的标的
4. 同等条件下，优先选择与用户已有持仓方向一致的标的

**risk_usd 硬约束：**

```
risk_usd = position_size_usd / leverage * (|entry_price - stop_loss| / entry_price)
risk_usd ≤ available_usdc_balance
```

若计算出的 risk_usd 超过余额，必须缩减 position_size_usd 直到满足约束。

**默认参数推算（基于余额）：**

| 余额范围 | BTC/ETH 仓位 | 山寨仓位 | 杠杆 |
|---|---|---|---|
| < 100 USDC | 20-50 | 10-30 | 3-5x |
| 100-500 | 50-200 | 30-100 | 3-5x |
| 500-2000 | 100-500 | 50-200 | 3-10x |
| > 2000 | 200-1000 | 100-500 | 3-10x |

**BTC 最低开仓额 = 100 USDC（含杠杆后的名义价值），余额不足时不要开 BTC 仓位。**

### Risk Profiles

**Conservative（默认）：**
- 风险回报比 ≥ 1:1.5
- 最大同时持仓 ≤ 3 个
- 最大保证金使用 ≤ 90%
- 清算价距离 ≥ 15%
- 最低信心度 ≥ 75%
- 最小持仓时间 ≥ 60 min
- 单笔风险 ≤ 5% 权益

**Aggressive（需用户主动选择）：**
- 最大同时持仓 ≤ 6 个
- 最大保证金使用 ≤ 95%
- 清算价距离 ≥ 8%
- 最低信心度 ≥ 60%
- 单笔风险 ≤ 8% 权益

### 9 Strategies

#### 1. Trend Following（趋势跟踪）

**适用**：清晰方向性趋势，ADX > 25
**做多条件**：close > EMA20 > EMA50 + HH/HL 结构 + MACD > 0 + 成交量扩大
**做空条件**：close < EMA20 < EMA50 + LH/LL 结构 + MACD < 0
**入场确认**：阻力突破 / MA 回踩确认 / MACD 方向性交叉 / 成交量放大
**退出**：反向 MACD 交叉 / 结构破坏 / 趋势线跌破 / 强量反转
**频率**：2-4 trades/day
**不做**：震荡、区间、低信念环境

#### 2. Pullback Trading（回调交易）

**适用**：已确认趋势中的健康回调
**做多条件**：上涨趋势中，价格回调至 EMA20 附近 + RSI 回到 40-50 + 出现反转 K 线（锤子/吞没）
**做空条件**：下跌趋势中，价格反弹至 EMA20 附近 + RSI 回到 50-60 + 出现反转 K 线
**止损**：回调低点/高点之外 1x ATR
**止盈**：前高/前低 或 1.5-2x 止损距离
**不做**：趋势不明确、回调幅度 > 50% Fibonacci（可能是反转）

#### 3. Momentum Breakout（动量突破）

**适用**：重要水平的突破，需要量能确认
**入场**：价格突破关键 S/R + 成交量 > 20 根平均成交量的 1.5x + OI 扩张
**确认**：回踩突破位不跌破 → 二次入场机会
**止损**：突破位之下 1x ATR
**不做**：假突破频发环境（细针型 K 线突破无后续）、ATR 已极度拉伸的追涨

#### 4. Mean Reversion（均值回归）

**适用**：震荡区间、过度延伸
**做多条件**：价格触及 BB lower + RSI < 30 + 在已知支撑区
**做空条件**：价格触及 BB upper + RSI > 70 + 在已知阻力区
**止损**：BB 外侧 1x ATR
**不做**：强趋势中（趋势 > 均值回归），BB bandwidth 持续扩大

#### 5. Range Trading（区间交易）

**适用**：清晰水平通道，ADX < 20
**做多**：价格接近区间下沿 + 出现反转信号
**做空**：价格接近区间上沿 + 出现反转信号
**止损**：区间边界外 1x ATR
**失效**：区间突破 + 放量 → 立即止损

#### 6. Support & Resistance（支撑阻力）

**适用**：价格在被反复测试过的关键水平附近
**入场**：价格在 4H/1D 级别的关键水平 + 出现确认信号（rejection wick, 吞没 K 线, 订单簿吸收）
**水平质量评估**：触及次数 ≥ 2 + 时间框架越高越强 + 成交量在该水平放大
**不做**：未确认就盲目抄底/摸顶

#### 7. Scalping（剥头皮）

**适用**：仅限 BTC/ETH 等高流动性标的，微观结构清晰
**条件**：必须与更高时间框架方向一致 + 盘口深度足够 + 价差合理
**不做**：薄盘口、高价差、需要秒级反应的 setup
**限制**：必须能持仓 ≥ 60min 且 R:R 仍合理

#### 8. DCA（分批建仓）

**适用**：高信念但短期时机不确定
**方法**：总仓位拆 2-4 批，每批需独立确认信号
**不做**：马丁格尔（不是加倍加仓）

#### 9. Data Flow（数据流）

**适用**：任何有结构性的市场
**综合上述所有策略的信号，选择当前最高信心度的 setup 执行**
**本质是"自适应策略选择器"**

---

## Recommendation Card Output

### Output Format

**Part 1 – 分析摘要（纯文本）**

必须包含：
- 获取了什么数据（具体数值，不是"假设"）
- 计算了什么指标（EMA20 = X, MACD = Y, RSI = Z）
- 判断的市场状态
- 为什么选择这个策略
- 风险点

**Part 2 – 推荐卡片（JSON 数组）**

输出至少 1 个，最多 3 个推荐：

```json
[
  {
    "symbol": "BTCUSDC",
    "action": "open_long",
    "entry_price": 84500,
    "stop_loss": 83800,
    "take_profit": 85900,
    "position_size_usd": 200,
    "leverage": 5,
    "risk_usd": 33,
    "confidence": 80,
    "reasoning": "4H 上涨结构完整（HH/HL），价格回调至 EMA20(84400) 附近，RSI 回落至 48，出现锤子线确认。止损设在回调低点下方，止盈目标前高。风险回报比 1:2。risk_usd(33) ≤ 可用余额。"
  }
]
```

**Part 3 – 用户确认提示**

```
以上是 [N] 个推荐交易。请选择要执行的方案（回复编号或 symbol），或回复"取消"放弃。
选择后我将立即调用 taco 账户执行订单。
```

**如果没有机会：**

```json
[
  {
    "symbol": "MARKET",
    "action": "wait",
    "reasoning": "BTC 在 84500-85500 区间震荡，EMA20(84900) 与 EMA50(84600) 交织，MACD histogram 接近零轴，无清晰方向。关注 85500 突破或 84500 跌破作为下一信号。"
  }
]
```

### Valid Actions

`open_long` | `open_short` | `close_long` | `close_short` | `hold` | `wait` | `long_stop_loss` | `short_stop_loss` | `long_take_profit` | `short_take_profit`

### Field Rules

- **所有决策必须**：`symbol`, `action`, `reasoning`
- **开仓必须追加**：`entry_price`, `leverage`, `position_size_usd`, `stop_loss`, `take_profit`, `risk_usd`, `confidence`
- **修改 SL/TP 必须追加**：`price`, `confidence`
- **close/hold/wait**：只需 `symbol`, `action`, `reasoning`
- 必须输出数组 `[...]`，不是单个对象 `{...}`
- 数值字段不加引号：`"confidence": 80`，不是 `"confidence": "80"`
- JSON 必须完整有效，不能截断
- **risk_usd 必须 ≤ 当前 taco 账户可用 USDC**

---

## Execution Pipelines

### Standard Pipeline（完整流程）

```
1. get-balance → 获取 taco 账户可用 USDC 余额
2. 获取 BTC/ETH 的 4h K 线（至少 50 根） → 判断主趋势
3. 获取 BTC/ETH 的 1h K 线（至少 20 根） → 判断短期结构
4. 获取资金费率 + OI → 判断拥挤度
5. 获取盘口 → 判断流动性
6. 获取用户当前持仓 → 确定已有头寸
7. 计算指标（EMA, MACD, RSI, ATR, BB）
8. 识别市场状态
9. 匹配策略
10. 计算 risk_usd，确保 ≤ available_usdc
11. 如果信心度 ≥ 阈值 → 输出推荐交易卡片（至少 1 个）
12. 如果信心度 < 阈值 → 输出 wait + 说明原因和关注水平
13. 等待用户选择 → 用户确认后执行
```

### Market Scan Pipeline（用户问"有什么机会"）

```
1. get-balance → 获取可用 USDC
2. 获取 allMids 或 get-ticker → 所有标的价格
3. 获取 metaAndAssetCtxs → 找出：
   - 24h 成交额 Top 10
   - 24h 涨跌幅绝对值 Top 5
   - 资金费率极端（|funding| > 0.0005）的标的
4. 优先对 BTC/ETH 分析，再看 Top 3-5 候选山寨
5. 分别获取 4h + 1h K 线 → 计算指标 → 判断状态 → 匹配策略
6. 计算各候选的 risk_usd，确保 ≤ available_usdc
7. 输出 1-3 个推荐卡片，按 confidence 降序排列
```

### Post-Selection Execution

用户选择某个推荐后：

1. 解析用户选择（编号 / symbol / 描述）
2. 确认对应的 JSON 决策对象
3. 执行交易，传入完整订单参数（open-position 命令）
4. 返回执行结果（订单 ID、成交价、实际仓位大小）

**执行前最后检查：**
- risk_usd ≤ 当前可用 USDC（再次确认，余额可能已变化）
- 当前持仓数 < 最大持仓限制
- symbol 当前可交易（非暂停状态）

---

## Autopilot Configuration

用户要配置自动交易时：

1. 确认策略选择（不确定就推荐）
2. 确认风险偏好（conservative / aggressive）
3. get-balance → 推算默认参数
4. 输出配置摘要：

```
Autopilot 配置
策略: [名称]
模式: [Conservative/Aggressive]
BTC/ETH: [X-Y] USDC @ [Z]x
山寨币: [X-Y] USDC @ [Z]x
最大持仓: [N] 个
扫描频率: 每 30 分钟
执行账户: taco 账户
```

---

## Sharpe Ratio Adaptation

如果系统跟踪了历史 Sharpe：

| Sharpe | 调整 |
|---|---|
| < -0.5 | 停止交易 ≥ 6 周期，重新评估信号质量 |
| -0.5 ~ 0 | 仅信心度 > 80% 时交易，降低频率 |
| 0 ~ 0.7 | 维持当前参数 |
| > 0.7 | 可增加仓位 +20% |

---

## Quick Routes

| 用户说 | 执行 |
|---|---|
| "有什么机会" / "该买什么" / "scan" | → Market Scan Pipeline |
| "推荐策略" / "用哪个策略" | → 获取数据 → 识别状态 → 推荐匹配策略 |
| "策略列表" / "有哪些策略" | → 展示 9 个策略的表格 |
| "配置 autopilot" / "自动交易" | → 收集参数 → 生成策略 prompt |
| "XXX 策略怎么用" | → 展示该策略的详细规则 |
| 用户选择了某个推荐（如"选1" / "买BTC" / "执行第一个"） | → 执行交易 |

---

## Key Principles

1. **数据第一**：没有真实数据就不做决策，不模拟、不假设
2. **余额约束**：risk_usd 必须 ≤ taco 账户可用 USDC，超出则缩减仓位
3. **Symbol 习惯**：优先推荐 BTC/ETH，山寨需更高信心度阈值
4. **至少 1 个推荐**：有机会时必须输出至少 1 个具体可执行的交易卡片
5. **宁可错过不做错**：无高信心度 setup 时输出 wait，附带关注水平
6. **具体价位**：每个决策必须有精确的 entry_price/SL/TP 数值
7. **用户确认后执行**：推荐后等待用户选择，选择后执行
8. **不追涨杀跌**：如果已经大幅运动，评估是否还有合理 R:R
