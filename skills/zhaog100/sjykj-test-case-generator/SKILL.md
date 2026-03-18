# Test Case Generator

自动从代码生成测试用例，支持5种测试设计方法。

## 功能

- **等价类划分** — 按类型划分有效/无效等价类
- **边界值分析** — 自动提取边界值和次边界值
- **场景法** — 基本流+备选流+异常流
- **因果图** — 输入→输出因果关系，生成判定表
- **错误推测** — 基于经验库+启发式规则

## 用法

```bash
# 分析代码文件，生成pytest测试
python3 -m src.test_generator

# 从需求文档提取测试点
python3 -m src.requirement_analyzer
```

## 支持语言

- Python (ast解析，零依赖)

## 许可证

MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
