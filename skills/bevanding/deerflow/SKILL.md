---
name: deerflow
slug: deerflow
version: 1.1.0
description: "Deep research and async task execution via DeerFlow LangGraph engine. Submit multi-step research tasks through a lightweight API-only Docker deployment (no frontend). Triggers: /deerflow, deep research, async research, deerflow."
metadata:
  openclaw:
    requires:
      bins: [python3]
    env: []
    os: [linux, darwin]
---

# DeerFlow Integration

## Overview

DeerFlow is a LangGraph-based deep research engine that chains web search, reasoning, and synthesis into structured reports. This skill provides OpenClaw integration for submitting and monitoring research tasks.

**Architecture note**: This skill targets the **minimal API-only deployment** — no Nginx, no frontend. Only two Docker services run:

| Service | Port | Role |
|---------|------|------|
| `deer-flow-gateway` | 8001 | Business logic & channel glue |
| `deer-flow-langgraph` | 2024 | Core agent orchestration (the only endpoint this skill calls) |

This is the recommended deployment for resource-constrained environments (VPS, small servers). All task submission is done by calling the LangGraph API directly.

## Quick Start

```
/deerflow <research topic>
```

Example: `/deerflow Analyze the Chinese AI companion market`

The skill returns a `thread_id` and `run_id` for status tracking.

## Minimal Docker Deployment (API-Only)

### 1. Clone and configure

```bash
git clone https://github.com/bytedance/deer-flow.git
cd deer-flow
cp .env.example .env
```

Edit `.env` with your model API keys:

```bash
# Required: at least one LLM provider
OPENAI_API_KEY=sk-...
# Or MiniMax
MINIMAX_API_KEY=...
MINIMAX_API_BASE=https://api.minimax.com

# Optional: Tavily for web search
TAVILY_API_KEY=tvly-...
```

### 2. Start API-only services

```bash
# No nginx, no frontend — just gateway + langgraph
docker compose up -d deer-flow-gateway deer-flow-langgraph
```

Verify:

```bash
curl http://localhost:2024/openapi.json | head   # should return OpenAPI spec
curl http://localhost:8001/health               # should return 200
```

### 3. Submit your first task

```bash
curl -X POST http://localhost:2024/threads \
  -H "Content-Type: application/json" \
  -d '{}'
# Returns: { "thread_id": "..." }
```

Then submit a task:

```bash
curl -X POST http://localhost:2024/threads/{thread_id}/runs \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "lead_agent",
    "input": {
      "messages": [{
        "type": "human",
        "content": [{ "type": "text", "text": "Your research query here" }]
      }]
    },
    "config": {
      "recursion_limit": 200,
      "configurable": {
        "model_name": "minimax-m2.7",
        "thinking_enabled": true,
        "is_plan_mode": false,
        "subagent_enabled": false
      }
    }
  }'
# Returns: { "run_id": "..." }
```

Poll for completion:

```bash
curl http://localhost:2024/threads/{thread_id}/runs/{run_id}
```

When status = `success`, fetch results:

```bash
curl http://localhost:2024/threads/{thread_id}/history
```

## Model Configuration

Set `model_name` in the `configurable` block:

| Model | Config Value | Notes |
|-------|-------------|-------|
| MiniMax M2.7 | `minimax-m2.7` | Default, reasoning-capable |
| MiniMax M2.5 | `minimax-m2.5` | Lighter alternative |
| Kimi | `kimi` | Requires DeerFlow `.env` to have Kimi credentials |

Set `thinking_enabled: true` to enable extended chain-of-thought reasoning (recommended for research tasks).

## Skill Scripts

This skill includes two helper scripts in `scripts/`:

### submit_task.py

```bash
cd ~/.openclaw/workspace/skills/deerflow
python3 scripts/submit_task.py "Your research topic"
# Returns thread_id and run_id
```

### check_status.py

```bash
python3 scripts/check_status.py <thread_id> <run_id>
# Polls until completion, then prints the full report
```

## OpenClaw Tool Injection

The skill is auto-injected into OpenClaw as the `deerflow` tool. OpenClaw agents call it directly when the user triggers the keyword.

## Resource Comparison

| Deployment | Services | RAM Est. | Use Case |
|-----------|----------|----------|----------|
| **API-only (this skill)** | gateway + langgraph | ~2 GB | Self-hosted agents, VPS |
| Full stack | + nginx + frontend | ~4+ GB | Team shared UI |

## Troubleshooting

### LangGraph returns 404

Verify the container is healthy:
```bash
docker ps | grep langgraph
curl http://localhost:2024/openapi.json
```

### Task hangs or returns "error" status

Check LangGraph logs:
```bash
docker logs deer-flow-langgraph --tail 50
```

### Model API errors

Ensure credentials in DeerFlow's `.env` are valid and the `model_name` in your request matches a configured provider.

## File Structure

```
skills/deerflow/
├── SKILL.md           # This file
└── scripts/
    ├── submit_task.py  # Submit a research task
    └── check_status.py # Poll and retrieve results
```
