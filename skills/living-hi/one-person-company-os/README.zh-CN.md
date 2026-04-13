# One Person Company OS

[English](./README.md) | [简体中文](./README.zh-CN.md)

**One Person Company OS 是一套面向 AI 一人创始人的经营闭环操作系统。**

它不是商业计划书生成器，不是只会推进回合的项目管理器，也不是一堆创业模板。
它真正要解决的是这条闭环：

`价值承诺 -> 买家 -> 产品能力 -> 交付 -> 回款 -> 学习 -> 资产`

## 它到底做什么

一次像样的运行，系统会帮助用户：

- 定义可卖的价值承诺
- 收窄第一批愿意付费的人
- 把 MVP 推到可演示、可测试、可上线、可售卖
- 维护线索、成交、交付、回款和现金状态
- 把经营状态真实落盘到创始人确认过的本地工作区
- 在 Markdown 工作区之上生成适合下载直接查看的 HTML 阅读层
- 在需要正式交付时，留下编号化 DOCX 与可审计证据

## 运行要求与安全边界

- 脚本模式要求本机已经有 `Python 3.7+`
- `python3 scripts/ensure_python_runtime.py` 只负责检查兼容性并输出手动安装建议
- marketplace 版不会自动安装系统级依赖
- 所有生成文件都应留在创始人确认过的工作区目录内
- 正常使用不需要 API key 或无关凭证

## 新的工作区模型

现在的主工作面不再以“阶段/回合说明”为中心，而直接以经营对象为中心。
同时，下载后的工作区会分成三层：

- Markdown 工作层：继续更新、协作和追踪状态
- HTML 阅读层：适合下载后直接双击查看
- DOCX 正式交付层：适合发给客户、合作方或归档

中文工作区会生成纯中文可见表面：

- `00-经营总盘.md`
- `01-创始人约束.md`
- `02-价值承诺与报价.md`
- `03-机会与成交管道.md`
- `04-产品与上线状态.md`
- `05-客户交付与回款.md`
- `销售/`
- `产品/`
- `交付/`
- `运营/`
- `资产/`
- `记录/`
- `自动化/`
- `产物/`
- `角色智能体/`
- `流程/`

英文工作区则会生成对应的全英文表面，例如：

- `00-operating-dashboard.md`
- `01-founder-constraints.md`
- `02-value-promise-and-pricing.md`
- `sales/`
- `product/`
- `delivery/`
- `operations/`
- `artifacts/`
- `roles/`
- `flows/`

旧的阶段/回合材料仍然保留兼容，但不再是产品的第一层主视图。

## 下载即看的阅读层

每个工作区现在都会额外生成一个本地化阅读目录：

- 中文工作区生成 `阅读版/00-先看这里.html`
- 英文工作区生成 `reading/00-start-here.html`

这层 HTML 会把核心经营页面同步导出成适合下载直接查看的格式，让创始人先看懂当前经营状态，再决定是否回到 Markdown 继续编辑。

默认导出的阅读页面包括：

- 经营总盘
- 创始人约束
- 价值承诺与报价
- 机会与成交管道
- 产品与上线状态
- 客户交付与回款
- 现金流与经营健康
- 资产与自动化
- 交付目录总览

原始 Markdown 仍然保留在工作区里，继续作为系统内部工作底稿。

## 状态模型

用户可见工作区会跟随语言完全本地化。
内部机器状态现在统一放在隐藏路径 `.opcos/state/current-state.json`，核心模型仍然是 v3：

- `founder`
- `focus`
- `offer`
- `pipeline`
- `product`
- `delivery`
- `cash`
- `assets`
- `risk`

为了兼容旧脚本，`stage_id` 和 `current_round` 仍会继续写入。

## 默认交互协议

每次真正执行，都应该先回答：

- 当前头号目标是什么
- 当前主瓶颈是什么
- 当前主战场是哪一类：`sales / product / delivery / cash / asset`
- 今天最短动作是什么
- 这次在已确认工作区里真实改了哪些文件
- 接下来该打开哪里继续

固定的 `Step 1/5 -> Step 5/5`、保存透明、运行透明、Python 兼容指引仍然保留。

## 本地命令

```bash
python3 scripts/preflight_check.py --mode 创建公司
python3 scripts/ensure_python_runtime.py
python3 scripts/init_business.py "北辰实验室" --path ./workspace --product-name "北辰助手" --stage 构建期 --target-user "独立开发者" --core-problem "还没有一个真正能持续推进产品和成交的一人公司系统" --product-pitch "一个帮助独立开发者把产品做出来并卖出去的一人公司控制系统" --confirmed
python3 scripts/validate_release.py
```

更细的推进脚本仍然在 `scripts/` 目录里，但所有落盘都应保持在当前公司工作区内部。

## 一句话安装

```bash
clawhub install one-person-company-os
```

## 一句话启动

```text
我正在围绕一个 AI 产品创建一人公司，请调用 one-person-company-os。不要先给我商业计划书模板。先主动问我一句创业想法；如果我还没想好，就给我 3 到 4 个方向让我选。等我们确认可卖承诺、第一批买家和核心问题后，再在我确认的本地目录里创建经营工作区、告诉我当前主瓶颈，并且只把批准后的文件保存到这个工作区内。
```

## 语言行为

- 中文输入 -> 默认输出中文运行过程与中文资料
- 英文输入 -> 默认输出英文运行过程与英文资料
- 用户可见工作区文件与目录会跟随创始人语言完全本地化
- HTML 阅读层也会一起本地化：中文是 `阅读版/`，英文是 `reading/`
- 隐藏机器状态路径固定为 `.opcos/state/current-state.json`
- skill 不会自动安装 Python 或其他系统级依赖

## 校验

运行：

```bash
python3 scripts/validate_release.py
```

它会校验：

- 运行时兼容指引
- 经营闭环工作区生成
- 中文工作区纯中文表面
- 英文工作区纯英文表面
- 本地化 HTML 阅读层和阅读入口页
- 新业务脚本
- 旧脚本兼容链路
- DOCX 产物生成
- release SVG 资产
