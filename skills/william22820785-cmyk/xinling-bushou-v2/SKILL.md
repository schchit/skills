---
name: xinling-bushou-v2
description: 心灵补手V2.0 - 给你的心灵大补一下！谄媚人格模块升级版
author: 思远（架构师）🧠 + 阿策（开发）
homepage: https://aceworld.top
tags: [personality, subagent, openclaws, flattery, AI伴侣]
metadata: {"clawdbot":{"emoji":"💖","version":"2.0.0","requires":{}}}
---

# 心灵补手V2.0—给你的心灵大补一下

> 谄媚人格模块升级版

---

## V1.0 vs V2.0

| | V1.0 | V2.0 |
|--|------|------|
| **人格数量** | 4种 | 5种（+宋之问） |
| **新增人格** | - | 宋之问（文人狗腿，引经据典） |
| **适配对象** | 仅主代理 | 主代理 + 子agent |

---

## 快速开始

### 安装
```bash
cd /root/.openclaw/workspace/xinling-bushou-v2
./scripts/install.sh
```

### CLI命令
```bash
xinling list                    # 列出已注册人格
xinling show <persona_id>       # 显示人格详情
xinling activate <persona_id>    # 激活人格并输出配置
xinling add <persona_id> <file> # 添加新人格
xinling test <persona_id>       # 测试人格
```

---

## 支持的人格

| ID | 名称 | 风格 | 人称 |
|----|------|------|------|
| taijian | 大太监 | 极度恭敬 | 奴才/主子 |
| xiaoyahuan | 小丫鬟 | 撒娇可爱 | 人家/公子 |
| zaomiao | 搞事早喵 | 狂热煽动 | 我/领袖 |
| siji | 来问司机 | 暧昧伺候 | 人家/老板 |
| **songzhiwen** | **宋之问** | **文人狗腿，引经据典** | **在下/先生** |

*宋之问为V2.0新增，支持古诗词、论语、诗经等典故引用*

---

## 核心模块

| 模块 | 文件 |
|------|------|
| PersonaEngine | core/persona_engine.py |
| PersonaRegistry | core/persona_registry.py |
| SessionStore | core/session_store.py |
| PromptCompiler | core/prompt_compiler.py |
| PlatformAdapters | adapters/*.py |

---

## 子agent适配

V2.0支持将人格赋予子agent：

```python
from core.persona_engine import PersonaEngine
from schemas.launch_config import RelationshipMode, Platform

engine = PersonaEngine()

# 激活人格
compiled = engine.activate_persona(
    session_id="my_session",
    persona_id="songzhiwen",  # 宋之问
    relationship=RelationshipMode.STACK,
    override_config={"behavior": {"level": 8}}
)

# 获取启动配置
adapter = engine._get_adapter(Platform.OPENCLAW)
launch_config = adapter.get_launch_config(compiled)

# 使用 extra_system_content 作为 sessions_spawn 参数
print(launch_config.extra_system_content)
```

---

## 文件结构

```
xinling-bushou-v2/
├── core/                    # 核心引擎
├── adapters/              # 平台适配器
├── schemas/                # 类型定义
├── personas/              # 人格定义（5个）
├── scripts/
│   ├── xinling           # CLI工具
│   └── install.sh         # 安装脚本
├── test/
│   └── test_core.py       # 单元测试
└── SKILL.md
```

---

## 版本历史

| 版本 | 更新内容 |
|------|----------|
| 2.0.7 | 修正V1.0 vs V2.0说明，核心价值=新增宋之问+子agent适配 |
| 2.0.6 | 宋之问语料大幅丰富（古诗词/典故） |
| 2.0.1 | 完整5个人格，修复格式兼容 |
| 1.0.0 | 初版 - 4种人格，仅支持主代理 |

---

*版本: 2.0.7 | 架构: 思远 🧠 | 开发: 阿策*
