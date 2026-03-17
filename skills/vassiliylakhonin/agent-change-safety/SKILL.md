---
name: agent-change-safety
description: Evaluate safety of AI agent changes before deployment using structured risk scoring, blast radius analysis, rollback planning, and deployment safety gates.
author: vassiliylakhonin
tags:
  - ai
  - agent
  - safety
  - deployment
  - devops
  - change-management
homepage: https://clawhub.ai/vassiliylakhonin/agent-change-safety
---

# AI Agent Change Safety

## What this skill does

This skill evaluates whether a change to an AI agent or workflow is safe to deploy.

It helps teams:

- score deployment risk
- estimate blast radius
- define safeguards
- prepare rollback plans
- decide Go / Conditional Go / No-Go

---

## Security constraints

To ensure safe operation:

- use only information explicitly provided by the user
- do not access local files, credentials, or system configuration automatically
- do not execute external scripts unless explicitly provided and approved
- do not retrieve external data sources automatically

All analysis must rely only on user-provided information or synthetic examples.

---

# Change evaluation workflow

Follow these stages when reviewing a change.

## 1. Change description

Identify the exact modification.

Possible categories:

- Prompt change
- Model change
- Tool integration
- Workflow logic change
- System configuration change

Record:

- purpose of change
- expected improvement
- affected components

---

## 2. Risk scoring matrix

Score each factor from **1 (low risk) to 5 (high risk)**.

Risk factors:

Operational impact – could the change break workflows?

Safety risk – could the change cause harmful outputs?

Tool reliability – could tool calls fail or behave differently?

User impact – could users receive incorrect responses?

Reversibility – how easy is rollback?

Risk classification:

5–8 → Low risk  
9–15 → Medium risk  
16–25 → High risk

---

## 3. Blast radius analysis

Estimate how widely the change may affect the system.

Questions to evaluate:

- which workflows are affected
- which users or systems depend on this change
- could failures cascade across tools or workflows

Blast radius levels:

Low – isolated feature or workflow  
Medium – multiple workflows affected  
High – core system logic affected

---

## 4. Safeguard requirements

Determine required protections.

Examples:

- human approval checkpoints
- validation prompts
- tool-call verification
- monitoring alerts
- rate limiting

High-risk changes should require human-in-the-loop validation.

---

## 5. Incident prevention checks

Check for:

- hallucination risk increases
- tool misuse patterns
- infinite loop conditions
- unsafe autonomous actions
- missing safety prompts

Document mitigation strategies.

---

## 6. Rollback planning

Every deployment must include a rollback plan.

Define:

- previous working version
- rollback trigger conditions
- rollback procedure
- rollback validation tests

Rollback must be executable quickly if failures occur.

---

# Deployment safety gates

Before approving deployment verify:

- change purpose clearly documented
- risk score calculated
- blast radius assessed
- regression tests executed
- rollback plan validated
- monitoring enabled

High-risk changes require explicit human approval.

---

# Validation checklist

Confirm before deployment:

- agent responses remain correct
- tool calls remain valid
- safety boundaries remain intact
- failure rates do not increase
- rollback procedure is tested

---

# Required output format

## Executive summary

Describe the change and evaluation result.

## Risk score

Provide numeric score and classification.

## Blast radius

Explain potential system impact.

## Required safeguards

List protections required before deployment.

## Rollback plan

Provide rollback trigger and rollback steps.

## Final recommendation

Possible outcomes:

Go  
Conditional Go  
No-Go

Explain reasoning clearly.

---

# Minimal output example

Change type: Prompt update

Risk score: 12 (Medium risk)

Blast radius: Medium – affects multiple workflows

Safeguards:
Add monitoring for tool-call failures.

Rollback:
Revert to previous prompt version if error rate increases.

Final verdict:
Conditional Go

---

# Related skills

This skill is part of an AI agent reliability toolkit.

- agent-evals-lab – evaluate agent quality
- agent-incident-analyzer – analyze agent failures

---

# Search phrases

- ai deployment safety
- agent change review
- prompt change risk
- safe ai rollout
- ai change management
