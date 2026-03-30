---
name: inventory-reorder-calculator
description: Estimate ecommerce reorder timing and quantity using demand, lead time, and safety stock assumptions so teams can set reorder points and reduce stockout risk with less guesswork.
---

# Inventory Reorder Calculator

Estimate when to reorder and how much to buy before stock risk turns into lost revenue or excess inventory.

## Use when

- You need a practical reorder point for a SKU
- Demand is growing, volatile, or seasonal
- Lead time is long or unreliable
- You want to reduce stockouts without overbuying cash-intensive inventory

## Do not use when

- You need a full supply-chain planning system or ERP implementation
- Historical demand is too weak to support even rough assumptions
- Supplier constraints are unknown and nobody can estimate them
- The task is warehouse slotting or operations design rather than reorder planning

## Inputs

- current on-hand inventory
- average daily or weekly demand
- demand variability if known
- supplier lead time and lead-time variability
- safety stock target or service-level preference
- MOQ, carton multiple, or purchase constraints
- review cycle / reorder cadence
- optional promo, launch, or seasonality assumptions

## Workflow

1. Estimate demand during lead time.
2. Add safety stock based on uncertainty and risk tolerance.
3. Calculate reorder point.
4. Estimate recommended reorder quantity using demand, cadence, and purchasing constraints.
5. Flag stockout risk, overstock risk, and assumption sensitivity.

## Output

1. Assumptions table
2. Reorder point
3. Recommended reorder quantity
4. Stock-risk summary
5. Notes on sensitivity and next decision steps

## Quality bar

- Must clearly separate reorder point from reorder quantity
- Must show the impact of lead time and demand uncertainty
- Should support daily operating decisions, not just formula display
- Should call out where assumptions are fragile

## What better looks like

Better output helps the operator act with confidence:
- knows when to reorder
- knows roughly how much to buy
- sees the cash vs stockout tradeoff
- understands where lead-time risk changes the answer
- can explain the decision to a buyer, founder, or ops lead

## Resource

See `references/output-template.md`.
