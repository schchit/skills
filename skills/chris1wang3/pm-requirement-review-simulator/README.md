# PRD Review Simulator（需求评审模拟器）

> Stress-test your product requirements before the real meeting. Five cross-functional roles challenge your PRD with realistic pushback — outputs a scored HTML survival report.

## What It Does

Describe your product requirement and choose a difficulty level. The agent simulates a **cross-functional review meeting** where 5 roles — Engineering, Operations, Design, Executive, and Legal — each challenge your PRD with role-specific concerns and speaking styles. It then generates a **themed HTML report** (Business Blue / Black Gold / Minimal White) with:

- **Survival Score** — deterministic scoring engine (per-item 0/1/2 → weighted formula), not vibes
- **5-Dimension Radar Chart** — visual breakdown of strengths and fatal weaknesses
- **Decision Gates** — value / risk / resource / strategy gates with A/B/C option comparison
- **Counterargument Playbook** — TOP 3 hardest questions with "normal reply" vs "killer reply" + technique breakdown
- **RACI Matrix** — cross-team collaboration plan with conflict identification and resolution
- **Meeting Script** — ready-to-use opening → core argument → risk mitigation → decision → wrap-up
- **Action Checklist** — owner + deadline + deliverable + review checkpoint

## Difficulty Levels

| Level | Style | Best For |
|-------|-------|----------|
| 🟢 Rookie | Gentle suggestions, constructive tone | New PMs, first-time practice |
| 🟡 Realistic | Standard big-tech review intensity | Pre-meeting dry run |
| 🔴 Hell Mode | All hostile + industry jargon attacks | Senior PMs stress-testing edge cases |

## Quick Start

```text
Review my team's group-buying feature. Realistic mode.
```

The agent will output an **info collection checklist** first (goal, scope, constraints, etc.), then generate the full report after confirmation.

## Workflow

```
Submit requirement → Info collection checklist → 5-role challenge + scoring → HTML report
```

1. **Input**: identify requirement type (major feature / tool / MVP / iteration / compliance) + PRD source
2. **Processing**: 5 roles challenge by persona → per-item scoring → weight normalization → survival rate
3. **Output**: generate 9-section HTML report (3 themes)

## Report Sections

| # | Section | Description |
|---|---------|-------------|
| 1 | Cover | Requirement overview, grade badge, decision label |
| 2 | Survival Score | 5-dimension radar + fatal flaws + lifelines |
| 3 | Decision Gates | Value/risk/resource/strategy gates + A/B/C comparison |
| 4 | Challenge Log | Per-role questions sorted by fatal/major/minor |
| 5 | Killer Replies TOP 3 | Normal vs killer reply + technique analysis |
| 6 | Collaboration Pack | RACI matrix + conflict identification & resolution |
| 7 | Meeting Script | Opening → core argument → risk plan → decision → close |
| 8 | Optimization Suggestions | 🔴 must-fix / 🟡 optional / ⚪ defer |
| 9 | Action Checklist | Owner + deadline + deliverable + review checkpoint |

## File Structure

| File | Role |
|------|------|
| `SKILL.md` | Master rules (workflow + output spec + quality standards) |
| `user_templates.md` | User input templates (general + industry add-ons) |
| `references/scoring-engine-deterministic.md` | Deterministic scoring engine (SSOT: weights, items, tiers, exemptions) |
| `references/review-playbook.md` | Role challenge handbook (personas + scripts + meeting flow) |
| `references/report-template-pro.html` | HTML report template (3 themes + 9 sections) |

---

# 中文说明

> 模拟真实跨部门评审会议的攻防推演技能。五方角色（技术/运营/设计/老板/法务）轮番质疑，输出带存活率评分的 HTML 可视化报告。

## 适用场景

- 评审前预演：提前暴露需求盲区，带着应对方案进会议室
- PRD 自检：用确定性评分引擎给需求文档做"体检"
- 新人练兵：模拟大厂评审会压力，练习应对尖锐质疑
- 展示版 PRD 评测：对公开发表的 PRD 文章做专业度评估

## 快速启动

```text
帮我评审一下我们要做的拼团功能，实战模式。
```

技能会先输出「信息采集清单」引导补充，确认后生成完整 HTML 报告。详细输入模板见 `user_templates.md`。
