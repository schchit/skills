---
name: create-harness-docs
description: "分析当前项目结构，快速创建符合 Harness Engineering 要求的文档体系。包括 AGENTS.md、架构文档、质量评级、执行计划等模板文档。"
---

# Create Harness Docs

自动分析当前项目并创建 Harness Engineering 文档体系。

## 功能

1. **分析项目** - 扫描项目结构，识别现有代码/文档
2. **创建 AGENTS.md** - 根据项目实际情况生成入口文件
3. **生成架构文档** - 基于现有代码生成 ARCHITECTURE.md
4. **创建质量评级** - 初始化 quality 追踪
5. **生成计划模板** - 创建 plans 目录结构
6. **配置 CI 约束** - 生成架构检查脚本

## 使用方法

```bash
# 分析当前项目并创建所有文档
create-harness-docs --init

# 仅创建 AGENTS.md
create-harness-docs --agents

# 仅创建架构文档
create-harness-docs --architecture

# 仅创建质量评级
create-harness-docs --quality

# 验证现有文档是否符合规范
create-harness-docs --validate
```

## 创建的文件

```
.
├── AGENTS.md                     # 项目入口/索引
├── docs/
│   ├── architecture/
│   │   ├── ARCHITECTURE.md       # 架构总览
│   │   └── domains/              # 业务域详情
│   ├── design/
│   │   └── adr/                  # 架构决策
│   ├── plans/
│   │   ├── active/               # 活跃计划
│   │   ├── completed/            # 已完成
│   │   └── debt/                 # 技术债务
│   └── quality/
│       └── grades.md             # 质量评级
├── scripts/
│   └── check-layers.js            # 架构约束检查
└── .github/
    └── workflows/
        └── harness-ci.yml         # CI 配置
```

## 核心原则

遵循 OpenAI Harness Engineering:

1. **AGENTS.md 是目录，不是手册** - 知识放 docs/
2. **严格分层** - Types → Config → Repo → Service → Runtime → UI
3. **约束即代码** - 用 linter 强制规则
4. **持续清理** - 定期处理技术债务
