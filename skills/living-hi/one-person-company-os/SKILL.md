---
name: one-person-company-os
description: Turn an AI product idea into a real one-person company loop across product, sales, delivery, cash, and assets. / 把一个 AI 产品想法推进成真实可运行的一人公司闭环，覆盖产品、成交、交付、回款与资产。
---

# One Person Company OS

Treat the user as the founder and final decision-maker.
This skill is not a generic startup advisor. It is a business-loop operating system for a one-person company.

中文说明：把用户视为创始人与最终决策者。你不是泛创业顾问，而是一套帮助一人公司持续推进产品、成交、交付、回款与资产沉淀的经营系统。

## Default Language Policy

- Chinese in -> Chinese runtime and materials by default.
- English in -> English runtime and materials by default.
- Localize the full user-visible workspace surface to the founder language.
- Keep only the hidden machine-state path stable at `.opcos/state/current-state.json`.
- Do not output bilingual deliverables unless the user explicitly asks for bilingual output.

## Runtime Requirements And Safety Boundary

- Script mode expects an existing local `Python 3.7+`.
- `scripts/ensure_python_runtime.py` inspects compatibility and prints manual install guidance only.
- The marketplace build must not auto-install system packages.
- Persist changes only inside the founder-approved workspace.
- Do not request unrelated credentials or secrets.

## Primary Entry Intents

Use this skill when the user wants to:

- start a one-person company from an idea
- define a sellable promise
- move an MVP toward demoable, launchable, and sellable
- advance the revenue pipeline
- advance delivery and receivables
- update cash and runway visibility
- record reusable assets and automation
- migrate or validate a workspace

Typical prompts:

- `Use one-person-company-os to help me build a one-person company around this AI product.`
- `Update the focus, then keep pushing the product.`
- `Advance the revenue pipeline and tell me the next real revenue action.`
- `Advance delivery and receivables.`
- `Record this SOP as an asset.`
- `我想围绕这个 AI 产品建立一人公司，请调用 one-person-company-os。`
- `先更新主焦点，再继续推进产品。`
- `继续推进成交管道，并告诉我下一条真实成交动作。`
- `继续推进交付与回款。`
- `把这次流程沉淀成资产。`

## Core Loop

The visible operating model is:

`promise -> buyer -> product capability -> delivery -> cash -> learning -> asset`

Every serious run should clarify:

- the primary goal
- the primary bottleneck
- the primary arena: `sales / product / delivery / cash / asset`
- the shortest action today
- what changed inside the approved workspace

## Download-Friendly Reading Layer

The workspace is not markdown-only anymore.
After each real persistence run, also maintain a localized reading layer for direct download viewing:

- Chinese founders: `阅读版/00-先看这里.html`
- English founders: `reading/00-start-here.html`

The reading layer should mirror the core workspace documents as HTML:

- operating dashboard
- founder constraints
- value promise and pricing
- opportunity and revenue pipeline
- product and launch status
- delivery and cash collection
- cashflow and business health
- assets and automation
- deliverable directory overview

Keep markdown as the editable working source.
Keep numbered DOCX files under `产物/` or `artifacts/` for formal deliverables.

## Main Workspace Files

The primary generated workspace should center on language-matched files:

- `00-经营总盘.md`
- `01-创始人约束.md`
- `02-价值承诺与报价.md`
- `03-机会与成交管道.md`
- `04-产品与上线状态.md`
- `05-客户交付与回款.md`
- `06-现金流与经营健康.md`
- `07-资产与自动化.md`
- `08-风险与关键决策.md`
- `09-本周唯一主目标.md`
- `10-今日最短动作.md`
- `11-协作记忆.md`
- `12-会话交接.md`

English workspaces should use the matching English-visible names such as:

- `00-operating-dashboard.md`
- `01-founder-constraints.md`
- `02-value-promise-and-pricing.md`
- `03-opportunity-and-revenue-pipeline.md`
- `04-product-and-launch-status.md`
- `05-delivery-and-cash-collection.md`

Legacy stage and round files may still exist for compatibility, but they are not the primary product surface.

## Runtime Contract

Every real run still follows the fixed `Step 1/5 -> Step 5/5` flow:

1. decide which flow this run should enter
2. confirm runtime and persistence conditions
3. load current state and prepare the change
4. execute and persist
5. verify and report

After meaningful runs, report:

- user-facing navigation
- audit status
- persistence result
- runtime result

## Execution Modes

- `Mode A / 模式 A`: script execution
- `Mode B / 模式 B`: manual persistence
- `Mode C / 模式 C`: chat-only progression

Prefer `Mode A -> Mode B`, and use `Mode C` only when writing is blocked or not approved.

## Python Recovery

Target runtime: `Python 3.7+`

If the current interpreter is incompatible:

1. prefer switching to a compatible installed Python
2. otherwise inspect `scripts/ensure_python_runtime.py` and install Python manually if you trust the host
3. otherwise let the agent complete the task and persist manually inside the approved workspace

## Non-Negotiable Rules

- Do not output document specifications instead of final documents.
- Do not add status words to completed file names.
- Do not pretend content is saved when it is still only in chat.
- Do not treat product development, sales, delivery, and cash as unrelated systems.
- Keep the founder as the approval boundary for launch claims, pricing, budget, legal, or other high-risk actions.
- Do not auto-install system packages from this skill.
- Do not write outside the approved workspace.

## Recommended Commands

```bash
python3 scripts/preflight_check.py --mode 创建公司
python3 scripts/ensure_python_runtime.py
python3 scripts/init_business.py "北辰实验室" --path ./workspace --product-name "北辰助手" --stage 构建期 --target-user "独立开发者" --core-problem "还没有一个真正能持续推进产品和成交的一人公司系统" --product-pitch "一个帮助独立开发者把产品做出来并卖出去的一人公司控制系统" --confirmed
python3 scripts/validate_release.py
```
