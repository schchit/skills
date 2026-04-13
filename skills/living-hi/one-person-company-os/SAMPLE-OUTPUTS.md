# Sample Outputs

These excerpts show the current behavior: direction-first setup, business-loop execution, a fully localized founder-visible workspace surface, and a download-friendly HTML reading layer.

## Interaction Output Structure

Chinese users see Chinese runtime output. English users see English runtime output.
Every major operation includes:

- `User Navigation View` or `用户导航版`
- `Audit View` or `审计版`
- explicit workspace-boundary and persistence details
- explicit runtime status

## Chinese Dashboard

```md
# 经营总盘

- 当前头号目标: 把 MVP 推到可演示并拿到第一批对话
- 当前主瓶颈: 价值表达和产品演示都还不够可卖
- 当前主战场: 产品
- 今天最短动作: 先补 homepage hero 的价值表达和 CTA 路径
```

## English Dashboard

```md
# Operating Dashboard

- Primary goal: push the MVP to a demoable state and get the first real conversations
- Main bottleneck: the value expression and demo are not sellable enough yet
- Primary arena: product
- Shortest action today: tighten the homepage hero and CTA path
```

## Chinese Workspace Surface

```text
北辰实验室/
  00-经营总盘.md
  01-创始人约束.md
  02-价值承诺与报价.md
  03-机会与成交管道.md
  04-产品与上线状态.md
  05-客户交付与回款.md
  销售/
  产品/
  交付/
  运营/
  资产/
  记录/
  自动化/
  阅读版/
    00-先看这里.html
    00-经营总盘.html
    02-价值承诺与报价.html
  产物/
  角色智能体/
  流程/
  .opcos/state/current-state.json
```

## English Workspace Surface

```text
North Star Lab/
  00-operating-dashboard.md
  01-founder-constraints.md
  02-value-promise-and-pricing.md
  03-opportunity-and-revenue-pipeline.md
  04-product-and-launch-status.md
  05-delivery-and-cash-collection.md
  sales/
  product/
  delivery/
  operations/
  assets/
  records/
  automation/
  reading/
    00-start-here.html
    00-operating-dashboard.html
    02-value-promise-and-pricing.html
  artifacts/
  roles/
  flows/
  .opcos/state/current-state.json
```

## Reading Layer Entry

```text
阅读版/00-先看这里.html
reading/00-start-here.html
```

The reading layer is the first stop after download.
It points founders to the core HTML views, explains how the workspace is split between HTML, markdown, and DOCX, and keeps the language-matched surface intact.
