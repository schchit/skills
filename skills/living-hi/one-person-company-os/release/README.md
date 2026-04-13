# One Person Company OS

One Person Company OS turns a solo founder's vague AI product idea into a working business loop:

- define the promise
- move the MVP toward demoable, launchable, and sellable
- track opportunities and delivery
- recover cash and build reusable assets

Install:

```bash
clawhub install one-person-company-os
```

Best start prompt:

```text
I am building a one-person company around an AI product. Use one-person-company-os. Do not give me a business-plan template. First ask me for the founder direction in one sentence; if I am not ready, give me 3 to 4 directions to choose from. After we confirm the sellable promise, first buyer, and core problem, create the operating workspace inside an approved local folder, tell me the current bottleneck, and save only the approved files inside that workspace.
```

Safety boundary:

- script mode expects an existing local `Python 3.7+`
- `scripts/ensure_python_runtime.py` prints compatibility and manual install guidance only
- the marketplace build does not auto-install system packages
- persisted files stay inside the approved workspace
- normal use does not require API keys

The generated workspace now opens with a language-matched surface and a download-friendly reading layer.

For English founders:

- `00-operating-dashboard.md`
- `02-value-promise-and-pricing.md`
- `03-opportunity-and-revenue-pipeline.md`
- `04-product-and-launch-status.md`
- `05-delivery-and-cash-collection.md`
- `reading/00-start-here.html`

For Chinese founders:

- `00-经营总盘.md`
- `02-价值承诺与报价.md`
- `03-机会与成交管道.md`
- `04-产品与上线状态.md`
- `05-客户交付与回款.md`
- `阅读版/00-先看这里.html`

This release line supports:

- business-loop state v3
- direct product build and launch coordination
- pipeline, delivery, cash, and asset updates
- language-localized founder workspaces plus hidden machine-state storage at `.opcos/state/current-state.json`
- localized HTML reading exports for direct viewing after download
- legacy stage/round compatibility
- numbered final-named DOCX deliverables
