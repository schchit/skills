---
name: dolphindb
description: DolphinDB Python 集成主技能 (v1.0.0)。提供统一的环境检测和入口，协调各子技能。**前置检查：自动执行环境检测**。
---

# DolphinDB Python 集成 v1.0.0

## 🎯 技能定位

这是 DolphinDB 套件的**主入口技能**，负责：
1. 自动执行环境检测
2. 协调子技能调用
3. 提供统一的 Python 调用接口

## ⚠️ 前置依赖（自动执行）

**本技能会自动执行环境检测，无需手动操作：**

```bash
source ~/.openclaw/skills/dolphindb/scripts/load_dolphindb_env.sh
```

## 子技能套件

| 子技能 | 版本 | 用途 |
|--------|------|------|
| 📘 `dolphindb-docker` | v1.0.0 | Docker 部署 |
| 📗 `dolphindb-basic` | v1.2.0 | 基础 CRUD |
| 📙 `dolphindb-quant-finance` | v1.1.0 | 量化金融 |
| 📕 `dolphindb-streaming` | v1.1.0 | 流式计算 |

## 调用关系

```
用户请求 → [dolphindb] → 环境检测 ✓ → 调用子技能
```

## 统一接口

```bash
source ~/.openclaw/skills/dolphindb/scripts/load_dolphindb_env.sh
dolphin_python script.py
```

## 版本

- **主技能:** v1.0.0
- **套件版本:** v1.2.0
