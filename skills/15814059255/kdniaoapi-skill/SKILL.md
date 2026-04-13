---
name: kuaidi-bird-tracking
description: 支持通过快递鸟API实时查询运单轨迹信息；当用户需要查询快递物流状态、追踪运单进度或获取包裹配送详情时使用
dependency:
  python:
    - requests>=2.28.0
---

# 快递鸟运单查询

## 任务目标
- 本 Skill 用于：查询快递运单的实时物流轨迹信息
- 能力包含：调用快递鸟API获取物流状态、解析轨迹数据、展示配送进度
- 触发条件：用户提出查询快递物流、追踪运单、查看配送状态等需求

## 前置准备

### 依赖安装
- Python依赖：requests>=2.28.0
- 安装命令：
  ```bash
  pip install requests>=2.28.0
  ```

### 凭证配置

**必需环境变量**：
- `KUAIDI_BIRD_API_CREDENTIALS`：快递鸟API凭证

**凭证格式**：
```
CUSTOMER_CODE|APP_KEY
```

**格式说明**：
- 使用竖线（`|`）分隔商户ID和API密钥
- 商户ID（CUSTOMER_CODE）：快递鸟账号的唯一标识
- API密钥（APP_KEY）：用于API请求签名的密钥

**获取方式**：
1. 访问快递鸟官网（https://www.kdniao.com/）注册账号
2. 登录后进入"API管理"或"开发者中心"
3. 在商户信息中获取商户ID（CUSTOMER_CODE）
4. 在API密钥管理中获取API密钥（APP_KEY）
5. 使用竖线（|）拼接两个值作为环境变量值

**配置示例**：
```bash
# Linux/Mac
export KUAIDI_BIRD_API_CREDENTIALS="1292092|703d0b97-07fa-478c-bfea-ca3597f2ce0f"

# Windows PowerShell
$env:KUAIDI_BIRD_API_CREDENTIALS="1292092|703d0b97-07fa-478c-bfea-ca3597f2ce0f"

# Windows CMD
set KUAIDI_BIRD_API_CREDENTIALS=1292092|703d0b97-07fa-478c-bfea-ca3597f2ce0f
```

### 套餐要求
快递鸟账号需开通快递查询服务套餐（免费或付费）

### 安全建议
- 妥善保管API密钥，避免泄露到代码仓库或公共平台
- 建议使用环境变量或密钥管理工具存储凭证
- 在生产环境使用前，先在测试环境验证
- 定期检查API调用额度和使用情况
- 不要在脚本中硬编码凭证

## 操作步骤

### 标准流程
1. **确认运单信息**
   - 获取用户提供的运单号（LogisticCode）
   - 验证运单号格式（通常为10-20位数字或字母数字组合）

2. **执行查询**
   - 调用 `scripts/query_tracking.py` 处理运单查询
   - 参数说明：
     - `--logistic-code`：运单号（必需）
     - `--api-url`：API地址（可选，默认为快递鸟正式环境）
   - 示例：
     ```bash
     python /workspace/projects/kuaidi-bird-tracking/scripts/query_tracking.py --logistic-code 773367326370601
     ```

3. **解析与展示结果**
   - 脚本返回结构化的JSON结果
   - 智能体解析返回数据，提取关键信息：
     - 物流状态（已揽收、运输中、派送中、已签收等）
     - 轨迹时间线（按时间顺序的物流节点）
     - 当前最新状态
   - 以自然语言向用户展示查询结果

### 可选分支
- 当 运单号无效或不存在：提示用户检查运单号是否正确
- 当 提示"缺少快递鸟API凭证配置"：检查环境变量 `KUAIDI_BIRD_API_CREDENTIALS` 是否已正确设置
- 当 提示"凭证解析失败"：确认凭证格式为 `CUSTOMER_CODE|APP_KEY`，使用竖线（|）分隔
- 当 查询失败或API异常：检查凭证配置，确认账号套餐状态，建议稍后重试
- 当 提示"没有可用套餐"：说明快递鸟账号未开通查询服务，需在快递鸟官网开通套餐
- 当 物流信息为空：说明该运单暂无轨迹更新

## 资源索引
- 必要脚本：见 [scripts/query_tracking.py](scripts/query_tracking.py)（用途：调用快递鸟API查询运单轨迹；参数：运单号、API地址）

## 注意事项

### 环境变量配置
- **必需环境变量**：`KUAIDI_BIRD_API_CREDENTIALS`
- **格式要求**：`CUSTOMER_CODE|APP_KEY`（使用竖线分隔）
- **配置示例**：
  ```bash
  export KUAIDI_BIRD_API_CREDENTIALS="1292092|703d0b97-07fa-478c-bfea-ca3597f2ce0f"
  ```

### API使用
- 本Skill使用快递鸟API，需要先配置商户ID和API密钥
- 默认使用快递鸟正式环境API地址（https://api.kdniao.com/api/dist）
- 快递鸟账号需开通快递查询服务套餐（免费或付费），否则会提示"没有可用套餐"

### 安全建议
- 妥善保管API密钥，避免泄露到代码仓库或公共平台
- 建议使用环境变量或密钥管理工具存储凭证
- 在生产环境使用前，先在测试环境验证
- 定期检查API调用额度和使用情况
- 脚本代码简短清晰，建议在使用前阅读并理解其逻辑
- 环境变量使用清晰命名（KUAIDI_BIRD_API_CREDENTIALS），易于理解和维护

### 其他
- 不同快递公司的查询结果格式可能略有差异
- 建议在查询前提醒用户确认运单号准确性

## 使用示例

### 示例1：查询顺丰运单
- **功能说明**：查询顺丰快递的物流轨迹
- **执行方式**：脚本查询 + 智能体解析展示
- **关键参数**：运单号 `SF1234567890`
- **执行**：
  ```bash
  python /workspace/projects/kuaidi-bird-tracking/scripts/query_tracking.py --logistic-code SF1234567890
  ```
- **结果**：智能体展示"包裹已揽收→运输中→派送中→已签收"的完整轨迹

### 示例2：查询圆通运单
- **功能说明**：查询圆通速递的物流状态
- **执行方式**：脚本查询 + 智能体解析展示
- **关键参数**：运单号 `YT1234567890123`
- **执行**：
  ```bash
  python /workspace/projects/kuaidi-bird-tracking/scripts/query_tracking.py --logistic-code YT1234567890123
  ```
- **结果**：智能体展示当前物流状态和最新物流节点

### 示例3：批量查询
- **功能说明**：依次查询多个运单的物流信息
- **执行方式**：循环调用脚本
- **执行**：智能体依次处理每个运单号，汇总展示结果
