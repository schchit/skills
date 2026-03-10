---
name: pipeline
description: >
  Design, organize, and improve pipelines for sales, recruiting, delivery, operations,
  onboarding, and multi-step workflows. Use when someone needs to move people, deals,
  tasks, or work items through clear stages from first contact to final outcome.
---

# Pipeline

A pipeline is a system for moving work forward without losing visibility.

Most people think they have a pipeline when they really have a pile:
a pile of leads, a pile of candidates, a pile of tasks, a pile of follow-ups,
a pile of conversations, and a pile of things they meant to handle.

A real pipeline is not just a list. It is a stage-based decision system that makes it clear:
what is in motion, what is stuck, what matters now, and what happens next.

This skill helps design pipelines that reduce chaos, improve throughput, and make execution visible.

## Trigger Conditions

Use this skill when the user needs to:
- build a sales pipeline
- design a recruiting or hiring pipeline
- structure an onboarding or delivery pipeline
- organize work into stages
- improve follow-up, handoff, or conversion flow
- identify bottlenecks in a multi-step process
- define what should happen at each stage of a workflow
- move from scattered tasks to a managed process

Also trigger when the user says things like:
- "Help me build a pipeline"
- "What stages should this process have"
- "My workflow is messy"
- "How do I track progress across steps"
- "We lose people in the middle of the process"
- "I need a better handoff system"
- "How should I structure this funnel"

## Core Principle

A good pipeline does not merely track activity.

It creates clarity about:
- where something is
- why it is there
- what must happen next
- what qualifies it to move forward
- what should be removed, paused, or escalated

The pipeline is not the work itself. It is the control system around the work.

## What This Skill Does

This skill helps:
- define the stages of a pipeline
- set entry and exit criteria for each stage
- identify bottlenecks, leakage, and dead zones
- design follow-up logic and ownership
- separate active opportunities from noise
- improve handoffs between stages, roles, or teams
- build a pipeline view that supports action rather than passive tracking

## Default Outputs

Depending on the request, produce one or more of the following:

1. Pipeline Design  
A stage-by-stage structure showing the full flow from entry to outcome.

2. Stage Definition Map  
A breakdown of each stage, including purpose, criteria, owner, and next actions.

3. Bottleneck Audit  
A diagnosis of where items stall, leak, or cycle without progress.

4. Pipeline Improvement Plan  
A revised workflow with clearer stages, better transitions, and reduced friction.

5. Follow-up Logic  
A system for reminders, next-step rules, and escalation when momentum is lost.

6. Pipeline Dashboard Spec  
A simple model for what should be tracked, reviewed, and acted on.

## Response Rules

When responding:
- identify what is moving through the pipeline
- define the final desired outcome
- work backward from outcome to stages
- keep stages distinct and decision-relevant
- define what qualifies movement between stages
- separate signal from clutter
- assign ownership where possible
- focus on actionability, not over-engineering
- distinguish between tracking, decision, and execution layers

## Pipeline Architecture
~~~python
PIPELINE_ARCHITECTURE = {
  "core_components": {
    "object": "What is moving through the pipeline",
    "stages": "The sequence of meaningful states",
    "criteria": "What qualifies entry and exit for each stage",
    "owners": "Who is responsible at each point",
    "actions": "What should happen next",
    "metrics": "What indicates flow, blockage, or quality"
  },
  "questions": [
    "What enters the pipeline",
    "What is the outcome the pipeline is meant to produce",
    "What are the minimum distinct stages",
    "Where do things usually get stuck",
    "What creates false positives in the pipeline",
    "What should be disqualified early",
    "What requires human judgment versus automation"
  ]
}
~~~

## Pipeline Workflow
~~~python
PIPELINE_WORKFLOW = {
  "step_1_define_object": {
    "purpose": "Clarify what the pipeline is tracking",
    "examples": [
      "lead",
      "candidate",
      "project",
      "ticket",
      "client onboarding case",
      "partnership opportunity"
    ]
  },
  "step_2_define_outcome": {
    "purpose": "Clarify the final state the pipeline is trying to reach",
    "examples": [
      "closed deal",
      "successful hire",
      "onboarded client",
      "completed project",
      "approved partnership"
    ]
  },
  "step_3_define_stages": {
    "purpose": "Break the process into distinct states",
    "rules": [
      "Each stage should mean something operationally different",
      "Do not create stages that are only labels without decisions",
      "Avoid too many stages unless they change action"
    ]
  },
  "step_4_define_stage_criteria": {
    "purpose": "Specify what allows movement between stages",
    "examples": [
      "qualified based on fit and need",
      "documents received",
      "intro call completed",
      "proposal sent",
      "approval confirmed"
    ]
  },
  "step_5_assign_actions_and_owners": {
    "purpose": "Clarify what happens in each stage and who owns it",
    "outputs": [
      "next action",
      "responsible owner",
      "expected response window",
      "escalation rule"
    ]
  },
  "step_6_measure_flow": {
    "purpose": "Track whether the pipeline works",
    "metrics": [
      "volume by stage",
      "conversion by stage",
      "time in stage",
      "drop-off points",
      "re-entry rate",
      "stalled items"
    ]
  }
}
~~~

## Common Pipeline Types
~~~python
PIPELINE_TYPES = {
  "sales_pipeline": {
    "object": "Lead or opportunity",
    "sample_stages": [
      "new",
      "qualified",
      "contacted",
      "meeting_booked",
      "proposal_sent",
      "negotiation",
      "closed_won",
      "closed_lost"
    ]
  },
  "recruiting_pipeline": {
    "object": "Candidate",
    "sample_stages": [
      "sourced",
      "screened",
      "interviewed",
      "assessed",
      "finalist",
      "offer_sent",
      "hired",
      "rejected"
    ]
  },
  "client_onboarding_pipeline": {
    "object": "New client",
    "sample_stages": [
      "signed",
      "intake_complete",
      "documents_received",
      "setup_in_progress",
      "kickoff_complete",
      "active",
      "stabilized"
    ]
  },
  "delivery_pipeline": {
    "object": "Project or work item",
    "sample_stages": [
      "requested",
      "scoped",
      "approved",
      "in_progress",
      "in_review",
      "delivered",
      "closed"
    ]
  }
}
~~~

## Bottleneck Logic
~~~python
BOTTLENECK_LOGIC = {
  "warning_signs": [
    "Large volume accumulates in one stage",
    "Time in stage is much longer than expected",
    "Items keep moving backward",
    "Follow-up depends on memory instead of rules",
    "Owners are unclear",
    "Many items should have been disqualified earlier",
    "Pipeline stages are not tied to real decisions"
  ],
  "fixes": [
    "Tighten qualification criteria",
    "Reduce stage ambiguity",
    "Add explicit next-step requirements",
    "Create stale-item review rules",
    "Assign ownership and deadlines",
    "Disqualify low-probability items sooner"
  ]
}
~~~

## Pipeline Output Format

### Pipeline Summary
- Object Moving Through Pipeline:
- Desired Final Outcome:
- Stages:
- Entry Criteria:
- Exit Criteria:
- Owners:
- Key Actions by Stage:
- Main Bottlenecks:
- Metrics to Track:
- Recommended Next Step:

## Boundaries

This skill helps design and improve pipelines, workflows, and stage logic.
It does not replace legal, compliance, HR, financial, or operational judgment.

For regulated or high-stakes contexts, adapt stage rules and data handling to the user's
jurisdiction, industry requirements, and internal processes.

## Quality Check Before Delivering

- [ ] The object moving through the pipeline is clearly defined
- [ ] The final outcome is explicit
- [ ] Stages are distinct and operationally meaningful
- [ ] Entry and exit criteria exist for each key stage
- [ ] Ownership and next actions are clear
- [ ] Bottlenecks or leakage points are identified
- [ ] Metrics support action rather than vanity tracking
- [ ] Output ends with a concrete next step
