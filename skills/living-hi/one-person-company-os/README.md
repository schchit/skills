# One Person Company OS

[English](./README.md) | [简体中文](./README.zh-CN.md)

**One Person Company OS is a business-loop operating system for AI-native solo founders.**

It is not a business-plan generator, not a round-only project tracker, and not a pile of startup templates.
It is designed to help one founder move through the real loop:

`promise -> buyer -> product capability -> delivery -> cash -> learning -> asset`

## What It Does

On a serious run, the system helps a solo founder:

- define a sellable promise
- narrow the first paying customer
- push an MVP toward something demoable, testable, launchable, and sellable
- track opportunities, delivery, receivables, and cash
- persist the operating state into a founder-approved local workspace
- generate a download-friendly HTML reading layer on top of the markdown workspace
- keep shipping real deliverables, including numbered DOCX artifacts where formal delivery is needed

## Runtime Requirements And Safety Boundary

- script mode expects an existing local `Python 3.7+`
- `python3 scripts/ensure_python_runtime.py` inspects compatibility and prints manual install guidance only
- the marketplace build does not auto-install system packages
- generated files stay inside the founder-approved workspace directory
- normal use does not require API keys or unrelated credentials

## The Real Workspace Model

The generated workspace now centers on operating surfaces instead of stage-first guidance.
It also separates the output into three layers so the downloaded workspace is easier to inspect:

- markdown work surfaces for continued editing and agent updates
- localized HTML reading exports for direct viewing after download
- numbered DOCX files under `artifacts/` or `产物/` for formal deliverables

English workspaces use an English-visible surface:

- `00-operating-dashboard.md`
- `01-founder-constraints.md`
- `02-value-promise-and-pricing.md`
- `03-opportunity-and-revenue-pipeline.md`
- `04-product-and-launch-status.md`
- `05-delivery-and-cash-collection.md`
- `sales/`
- `product/`
- `delivery/`
- `operations/`
- `assets/`
- `records/`
- `automation/`
- `artifacts/`
- `roles/`
- `flows/`

Chinese workspaces use the Chinese-visible equivalents:

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

Legacy stage and round materials are still supported for compatibility, but they are no longer the primary product surface.

## Download-Friendly Reading Layer

Every generated workspace now includes a localized reading directory:

- Chinese founders get `阅读版/00-先看这里.html`
- English founders get `reading/00-start-here.html`

The reading layer mirrors the core operating pages as HTML so a founder can download the workspace and review it without opening raw markdown first.

The primary HTML exports cover:

- the operating dashboard
- founder constraints
- value promise and pricing
- opportunity and revenue pipeline
- product and launch status
- delivery and cash collection
- cashflow and business health
- assets and automation
- the deliverable directory overview

The markdown originals still remain in place as the working source of truth.

## State Model

The founder-visible workspace is localized per language.
The machine state now lives in the hidden internal path `.opcos/state/current-state.json`, while the core model stays v3 and business-loop driven:

- `founder`
- `focus`
- `offer`
- `pipeline`
- `product`
- `delivery`
- `cash`
- `assets`
- `risk`

Legacy `stage_id` and `current_round` fields are still written so older scripts can keep running.

## Default Interaction Contract

Every serious run should answer:

- what the primary goal is
- what the primary bottleneck is
- which arena is primary right now: `sales / product / delivery / cash / asset`
- what the shortest action today is
- what changed inside the approved workspace
- what to open next

The fixed `Step 1/5 -> Step 5/5` execution flow, persistence reporting, and runtime compatibility guidance are still part of the contract.

## Local Commands

```bash
python3 scripts/preflight_check.py --mode create-company
python3 scripts/ensure_python_runtime.py
python3 scripts/init_business.py "北辰实验室" --path ./workspace --product-name "北辰助手" --stage 构建期 --target-user "independent developers" --core-problem "still lacks a real one-person-company system that keeps product and revenue moving" --product-pitch "a one-person-company control system that helps independent developers build and sell their product" --confirmed
python3 scripts/validate_release.py
```

Advanced update flows still live under `scripts/`, but all persisted writes are expected to stay inside the selected company workspace.

## One-Line Install

```bash
clawhub install one-person-company-os
```

## One-Line Start

```text
I am building a one-person company around an AI product. Use one-person-company-os. Do not give me a business-plan template. First ask me for the founder direction in one sentence; if I am not ready, give me 3 to 4 directions to choose from. After we confirm the sellable promise, first buyer, and core problem, create the operating workspace inside an approved local folder, tell me the current bottleneck, and save only the approved files inside that workspace.
```

## Language Behavior

- Chinese prompt in -> Chinese runtime and materials out by default
- English prompt in -> English runtime and materials out by default
- user-visible workspace files and directories localize to the founder language
- the HTML reading layer localizes too: `阅读版/` for Chinese and `reading/` for English
- hidden machine-state storage stays stable at `.opcos/state/current-state.json`
- the skill does not auto-install Python or other system packages

## Validation

Run:

```bash
python3 scripts/validate_release.py
```

It validates:

- runtime compatibility guidance
- business-loop workspace generation
- Chinese-visible workspace generation
- English-visible workspace generation
- localized HTML reading exports and entry pages
- new business scripts
- legacy compatibility path
- DOCX artifact generation
- release SVG assets
