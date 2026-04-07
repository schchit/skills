---
name: project-standard
description: |
  四视角项目巡检标准库。适用于 auto-evolve 扫描任何项目时的标准参照。
  当需要进行项目巡检、架构评审、需求对齐、代码审查，或调用 auto-evolve scan 时使用。
  覆盖用户视角、产品视角、项目视角、技术视角的完整检查清单。
  当用户提到「巡检」「项目标准」「检查项目」「评估项目」时使用。
---

# project-standard

**四视角项目巡检标准库** — auto-evolve 的评判标准参照。

> 任何项目都能用四视角巡检：用户 → 产品 → 项目 → 技术。

---

## 核心理念

**四视角不是四个团队的工作，是同一个人审视项目的四个角度。**

当你接到一个项目，无论是自己做的还是别人做的，都要从这四个视角过一遍：

| 视角 | 问自己 | 例子 |
|------|---------|------|
| 👤 **用户** | 我用起来顺手吗 | CLI 直不直观、报错说不说人话 |
| 📦 **产品** | 它说到做到了吗 | README 承诺的功能实现了多少 |
| 🏗 **项目** | 运作方式健康吗 | learnings 有没有闭环、巡检有没有节奏 |
| ⚙️ **技术** | 代码本身健康吗 | 重复代码、测试覆盖率、安全漏洞 |

**优先级**：用户 > 产品 > 项目 > 技术

---

## 四视角速查

### 👤 用户视角

**核心问题：这个工具/产品用起来顺手吗？**

| 维度 | 问什么 |
|------|--------|
| CLI/交互设计 | 参数名直观吗？默认值合理吗？help 清晰吗？ |
| 学习门槛 | 新人上手要多久？文档够吗？ |
| 错误提示 | 报错是说人话还是说机器话？ |
| 容错性 | 某一步失败了会怎样？会丢数据吗？ |
| 操作流程度 | 完成一个操作要几步？能更少吗？ |

→ 详见：[references/user/user-perspective.md](references/user/user-perspective.md)

### 📦 产品视角

**核心问题：这个项目声称解决什么，实际做到了吗？**

| 维度 | 问什么 |
|------|--------|
| README 承诺 | README 写的功能，实际做到了吗？ |
| 痛点解决 | 文档里 ❌ 标记的痛点，哪些还没解决？ |
| 功能完整性 | 声称的 feature 是完整实现还是半成品？ |
| 文档一致性 | 文档和代码说的是同一件事吗？ |

→ 详见：[references/product-requirements.md](references/product-requirements.md)

### 🏗 项目视角

**核心问题：这个项目的运作方式健康吗？**

| 维度 | 问什么 |
|------|--------|
| learnings 闭环 | 上次发现的问题追踪了吗？learnings 有积累吗？ |
| 巡检节奏 | 有没有稳定的巡检节奏还是想起来才扫？ |
| 配置合理性 | 配置项是否合理？有无过度配置？ |
| 依赖管理 | 依赖是否过多、过旧、有安全风险？ |

→ 详见：[references/project-inspection.md](references/project-inspection.md)

### ⚙️ 技术视角

**核心问题：代码本身健康吗？**

| 维度 | 问什么 |
|------|--------|
| 代码质量 | 重复代码、长函数、坏味道 |
| 架构设计 | 模块间耦合是否合理？ |
| 测试覆盖 | 核心逻辑有测试吗？ |
| 性能安全 | 有无明显性能问题或安全漏洞？ |

→ 详见：[references/code-standards.md](references/code-standards.md)

---

## 项目分类系统

扫描前先判断项目类型，不同类型问的问题不同：

### Skill

**定义**：OpenClaw 的扩展 skill，扩展 AI 能力

| 视角 | 重点问什么 |
|------|-----------|
| 用户 | CLI 参数设计、激活关键词是否直觉 |
| 产品 | SKILL.md 承诺的功能实际做到了吗 |
| 项目 | learnings 有没有积累、巡检有没有闭环 |
| 技术 | 代码是否可复用、依赖是否干净 |

### CLI 工具

**定义**：命令行工具，用户通过终端交互

| 视角 | 重点问什么 |
|------|-----------|
| 用户 | --help 清晰吗？错误提示说人话吗？ |
| 产品 | 核心功能是否完整、参数设计是否合理 |
| 项目 | 配置管理是否规范 |
| 技术 | 参数解析是否健壮、是否有 dry-run 模式 |

### Python 库 / 包

**定义**：被其他代码 import 使用的库

| 视角 | 重点问什么 |
|------|-----------|
| 用户 | API 设计是否符合直觉、文档清晰吗 |
| 产品 | README 承诺的接口是否都实现了 |
| 项目 | 版本管理是否规范 |
| 技术 | 类型提示是否完整、有无循环依赖 |

### Web 应用

**定义**：有前端界面的 Web 服务

| 视角 | 重点问什么 |
|------|-----------|
| 用户 | 核心路径流畅吗、错误提示友好吗 |
| 产品 | 主要功能是否完整、用户旅程是否顺畅 |
| 项目 | 部署配置是否规范 |
| 技术 | 前后端分离是否合理、API 设计是否规范 |

→ 详见：[references/project-types.md](references/project-types.md)

---

## 与 auto-evolve 的配合

auto-evolve 扫描项目时，会自动参照本 skill 的标准：

```
auto-evolve scan
    ↓
判断项目类型（Skill / CLI / 库 / Web）
    ↓
四视角巡检 × 项目类型权重
    ↓
输出分组报告（按视角 + 按项目）
    ↓
参照 project-standard reference 给出评判标准
```

---

## 快速使用

### 作为巡检标准参照

直接加载对应 reference 文件：

```
references/user/user-perspective.md      → 用户视角检查清单
references/product-requirements.md        → 产品视角检查清单
references/project-inspection.md         → 项目视角检查清单
references/code-standards.md             → 技术视角检查清单
references/project-types.md             → 项目类型定义
```

### 作为 auto-evolve 的标准库

auto-evolve 会自动加载本 skill 作为评判标准，无需额外配置。

---

## 目录结构

```
project-standard/
├── SKILL.md
├── references/
│   ├── user/
│   │   └── user-perspective.md       ← 用户视角标准
│   ├── product-requirements.md        ← 产品视角标准
│   ├── project-inspection.md          ← 项目视角标准
│   ├── project-types.md              ← 项目分类系统
│   ├── code-standards.md              ← 技术视角标准
│   ├── architecture.md               ← 架构设计标准
│   ├── security.md                   ← 安全规范
│   ├── metrics.md                    ← 指标体系
│   └── inspection-template.md         ← 巡检报告模板
└── _meta.json
```

---

## 核心原则

1. **用户优先** — 用户体验是一切的前提，技术再好不好用也没意义
2. **说到做到** — README 承诺的功能必须实现，文档必须与代码一致
3. **持续改进** — 有巡检节奏，learnings 有闭环，不是想起来才扫
4. **技术为用** — 技术选型和代码质量服务于产品目标，不是炫技
