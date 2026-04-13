# 📍 外出任务自动配置技能

**技能名称**：outbound-auto-setup  
**版本**：1.0.0  
**用途**：监听用户消息中的外出关键词，自动创建所有提醒

---

## 🎯 功能

1. **自动检测**：监听用户消息中的外出关键词
2. **信息提取**：自动提取日期、时间、地点、事项
3. **自动配置**：一键创建所有提醒（Apple 提醒 + cron 推送 + pending-tasks）
4. **自动验证**：验证所有配置是否成功
5. **报告用户**：输出完整验证报告

---

## 📋 触发关键词

### 外出相关
- 去 [地点]
- 外出 [地点]
- 出发 [地点]
- 到 [地点]
- 前往 [地点]

### 时间相关
- 明天/后天/下周一
- [时间] 点/[时间]:[分钟]
- [日期]

### 事项相关
- 调研/会议/拍摄/考务
- 拿/取/办/处理
- 拜访/访问/见面

---

## 🔧 配置

### 安装方式

```bash
# 1. 复制技能文件
cp -r ~/.openclaw/workspace/skills/outbound-auto-setup ~/.openclaw/skills/

# 2. 启用技能
openclaw skills enable outbound-auto-setup

# 3. 验证安装
openclaw skills list | grep outbound
```

### 配置文件

**位置**：`skills/outbound-auto-setup/config.json`

```json
{
  "enabled": true,
  "keywords": ["去", "外出", "出发", "到", "前往"],
  "autoSetup": true,
  "notifyUser": true,
  "checkInterval": "every_message"
}
```

---

## 📝 使用示例

### 示例 1：工作外出

**用户消息**：
```
明天 8 点去闲林职高考务视频拍摄
```

**自动响应**：
```markdown
🚀 **检测到外出任务，正在自动配置...**

**提取信息**：
- 日期：2026-03-28
- 时间：08:00
- 地点：闲林职高
- 事项：考务视频拍摄
- 类型：工作外出 ✅

**配置提醒**：
- ✅ Apple 提醒事项：2026-03-28 07:45
- ✅ cron 定时推送：2026-03-28 07:45
- ✅ pending-tasks.md：已记录

**验证结果**：
- ✅ Apple 提醒：验证通过
- ✅ cron 推送：验证通过
- ✅ pending-tasks：验证通过

**状态**：✅ 配置完成
```

### 示例 2：生活外出

**用户消息**：
```
周六下午 2 点到留家村拿茶叶
```

**自动响应**：
```markdown
🚀 **检测到外出任务，正在自动配置...**

**提取信息**：
- 日期：2026-03-28
- 时间：14:00
- 地点：留家村
- 事项：拿茶叶
- 类型：生活外出 🏠

**配置提醒**：
- ✅ Apple 提醒事项：2026-03-28 13:45
- ✅ cron 定时推送：2026-03-28 13:45
- ✅ pending-tasks.md：已记录

**状态**：✅ 配置完成
```

---

## 🛠️ 技术实现

### 主脚本

**文件**：`skills/outbound-auto-setup/index.js`

**核心逻辑**：
```javascript
// 监听消息
onUserMessage(async (message) => {
  // 1. 检测外出关键词
  if (!containsOutboundKeywords(message)) {
    return;
  }
  
  // 2. 提取关键信息
  const info = extractOutboundInfo(message);
  if (!info) {
    reply('⚠️ 未识别到完整的外出信息，请提供日期、时间、地点、事项');
    return;
  }
  
  // 3. 自动配置提醒
  const result = await setupOutbound(info);
  
  // 4. 输出报告
  reply(formatReport(result));
});
```

### 信息提取

**函数**：`extractOutboundInfo(message)`

**提取规则**：
```javascript
// 日期提取
const datePatterns = [
  /明天 (\d+ 月 \d+ 日)/,
  /后天 (\d+ 月 \d+ 日)/,
  /(\d+ 月 \d+ 日)/,
  /(\d{4}-\d{2}-\d{2})/
];

// 时间提取
const timePatterns = [
  /(\d+)[点:：](\d+)/,
  /(\d+) 点/,
  /上午 (\d+) 点/,
  /下午 (\d+) 点/
];

// 地点提取
const locationPatterns = [
  /去 ([\u4e00-\u9fa5]+)/,
  /到 ([\u4e00-\u9fa5]+)/,
  /前往 ([\u4e00-\u9fa5]+)/
];
```

### 自动配置

**函数**：`setupOutbound(info)`

**执行流程**：
```bash
# 1. 创建 Apple 提醒事项
remindctl add --list "工作" "📍 $TYPE：$LOCATION - $TIME" --due "$REMIND_TIME"

# 2. 创建 cron 推送
node create-cron-job.js "$DATE" "$TIME" "$LOCATION" "$TASK" "$TYPE"

# 3. 更新 pending-tasks.md
echo "| $DATE | $TIME | $LOCATION | $TASK | $TYPE | $(date +%H:%M) | ✅ 已验证 | ⏳ 待完成 |" >> pending-tasks.md

# 4. 验证配置
verifyAllCreated()

# 5. 返回结果
return result
```

---

## 🧪 测试

### 测试用例

| 测试场景 | 输入消息 | 预期结果 |
|----------|----------|----------|
| 工作外出 | 明天 8 点去闲林职高考务拍摄 | ✅ 配置工作外出提醒 |
| 生活外出 | 周六 2 点到留家村拿茶叶 | ✅ 配置生活外出提醒 |
| 模糊时间 | 去闲林职高 | ⚠️ 提示补充时间 |
| 模糊地点 | 明天 8 点去调研 | ⚠️ 提示补充地点 |
| 非外出 | 今天天气不错 | ❌ 不触发 |

### 测试命令

```bash
# 运行测试
npm test -- outbound-auto-setup

# 或手动测试
node test/outbound-detect.test.js
```

---

## 📊 监控

### 统计指标

| 指标 | 说明 | 目标 |
|------|------|------|
| 检测率 | 成功检测的外出消息 / 总外出消息 | 100% |
| 配置率 | 成功配置的提醒 / 检测到的外出 | 100% |
| 误报率 | 误触发次数 / 总触发次数 | < 1% |

### 日志位置

**文件**：`logs/outbound-auto-setup.log`

**格式**：
```
[2026-03-27 20:56:00] 检测到外出消息：明天 8 点去闲林职高
[2026-03-27 20:56:01] 提取信息：日期=2026-03-28, 时间=08:00, 地点=闲林职高
[2026-03-27 20:56:02] 创建 Apple 提醒事项：✅ 成功
[2026-03-27 20:56:03] 创建 cron 推送：✅ 成功
[2026-03-27 20:56:04] 更新 pending-tasks.md：✅ 成功
[2026-03-27 20:56:05] 验证配置：✅ 全部通过
```

---

## ⚠️ 注意事项

1. **隐私保护**：仅检测外出相关消息，不检测其他内容
2. **用户确认**：首次使用时询问用户是否启用
3. **错误处理**：配置失败时立即通知用户
4. **性能优化**：避免频繁检测影响性能

---

## 🔄 更新日志

### v1.0.0 (2026-03-27)
- ✅ 初始版本
- ✅ 外出关键词检测
- ✅ 信息自动提取
- ✅ 自动配置提醒
- ✅ 自动验证
- ✅ 报告用户

---

_此技能实现外出任务的全自动配置，无需人工干预_
