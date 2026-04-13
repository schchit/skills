# 外出任务自动配置 - 使用指南

## 当前状态

✅ 技能已创建并测试通过  
⚠️ OpenClaw 不支持自定义插件，需要手动调用

## 使用方式

### 方式 1：阿爪手动调用（推荐）

当用户告知外出时，阿爪执行：

```bash
node ~/.openclaw/skills/outbound-auto-setup/message-middleware.js "明天 8 点去闲林职高"
```

### 方式 2：脚本调用

```bash
./scripts/auto-setup-outbound.sh "2026-03-28" "08:00" "闲林职高" "考务拍摄" "work"
```

### 方式 3：心跳检查（已启用）

每 2 小时心跳结束时，自动检查 pending-tasks.md 中的待验证任务

## 集成到 OpenClaw

由于 OpenClaw 不支持自定义插件，建议：

1. **阿爪识别外出关键词后**，手动调用技能
2. **或使用脚本工具**一键配置
3. **心跳检查作为兜底**

## 测试

```bash
cd ~/.openclaw/skills/outbound-auto-setup
node test/outbound-detect.test.js
```

## 日志

查看运行日志：
```bash
tail -f ~/.openclaw/logs/outbound-auto-setup.log
```
