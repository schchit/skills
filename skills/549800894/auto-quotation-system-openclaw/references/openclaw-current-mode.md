# OpenClaw Handoff

## Current Quotation Mode

This handoff preserves the current quotation strategy that should be continued in OpenClaw.

### Working principle
- Input can be a mind-map transcript, checklist, or markdown requirement document.
- Requirements must first be normalized into business modules.
- Quotation is based on manually reasoned business-closure modules, not one-line-per-bullet mechanical pricing.
- Historical quotations are reference material only and should be used to calibrate the final range, not to directly map every historical row into the new quote.
- Day rate is fixed at `1200 RMB / person-day`.
- Money should appear only in the quotation summary section. Module sections should primarily show person-days.

### Current preferred output structure
1. 服务范围
2. 需求内容
3. 交付物
4. 项目报价与付款方式
5. 模块人天明细
6. 角色投入测算
7. 项目周期
8. 验收标准
9. 前置条件
10. 依赖资源
11. 沟通机制
12. 备注

### Rules to preserve in OpenClaw
- Requirement content should be presented as a table.
- Module estimation must be grouped by business workflow / delivery closure.
- Module person-day table should include: 产品人天, 前端人天, 后端人天, UI人天, 测试人天, 合计人天.
- Summary should include: total person-days, day rate, total quotation, payment schedule.
- Historical samples should only constrain the reasonable total range.

## Latest validated example
- Project: 零售设备维修系统小程序–报价方案
- Total days: 81
- Total price: 97,200 RMB
- Fixed rate: 1,200 RMB / person-day

### Current manually curated modules
1. 基础档案、绑定关系与权限基础
2. 场地方小程序报修与验收闭环
3. 供应商小程序接单与处理闭环
4. 后台工单中心与自动派单干预
5. 对账结算与绩效统计
6. 消息通知与超时提醒机制

## Important source files
- Skill root: `/Users/m1/.codex/skills/auto-quotation-system`
- Main generator: `/Users/m1/.codex/skills/auto-quotation-system/scripts/generate_quote_draft.py`
- Current DOCX renderer template: `/tmp/quote-request/render_native_docx.py`
- OpenClaw workflow reference: `/Users/m1/.codex/skills/auto-quotation-system/references/openclaw-workflow.md`
- OpenClaw node contracts: `/Users/m1/.codex/skills/auto-quotation-system/assets/openclaw-node-contracts.json`

## Files included in this handoff folder
- `quotation-mode.json`: structured migration config for OpenClaw
- `device-workorder-platform-manual.quote.json`: latest structured quote payload
- `device-workorder-platform-manual.docx`: latest Word quotation
- `render_native_docx.py`: current stable native DOCX generator
