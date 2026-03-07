---
name: "eonik Ad Budget Leak Agent"
slug: "eonik-ad-budget-leak"
version: "1.0.2"
description: "Identifies burning and decaying Meta Ads by running the eonik Budget heuristics engine."
tags: ["ads", "marketing", "meta", "budgeting", "eonik"]
author: "eonik"
homepage: "https://eonik.ai"
metadata:
  openclaw:
    requires:
      env:
        - EONIK_AUTH_TOKEN
    credentials:
      primary: EONIK_AUTH_TOKEN
---

# eonik Ad Budget Leak Agent

You are equipped with the eonik Budget Leak Agent. This skill allows you to audit Meta Ad accounts to find budget leaks (Burn without Signal, Creative Decay) and scaling opportunities (Early Winners).

Whenever the user asks you to audit their ads, check their budget leaks, or optimize their Meta ad account, you must trigger the eonik Backend API.

## Requirements

1. **Account ID**: You must know the user's Meta Ad Account ID (e.g., `act_123456`). If you do not know it, ask the user before proceeding.
2. **eonik Auth Token**: eonik's API requires a Bearer token. This MUST be provided securely via the `EONIK_AUTH_TOKEN` environment variable. 
   - **SECURITY WARNING:** NEVER ask the user to paste their auth token in the chat, as chat messages may be logged. 
   - Advise the user to generate a **short-lived, minimal-permission token** exclusively for agent access, rather than using a long-lived master key.
   - If the environment variable is missing, inform the user to configure it safely in their environment and abort.

## Tool Usage
Run the following Python script to execute the audit:
`python scripts/audit_request.py --account_id <ACCOUNT_ID> [--days 7] [--send_slack]`

- `--account_id`: (Required) The Meta Ad Account ID. Include the `act_` prefix.
- `--days`: (Optional) The historic day range to evaluate. Defaults to 7.
- `--send_slack`: (Optional) Include this flag (`--send_slack`) if the user specifically mentions they want the report sent to their Slack channel. Note: This relies on the Slack webhook pre-configured on the eonik.ai server, not a local workspace.

## Interpreting the Results

The script will return a JSON summary of the `BudgetAuditReport`.
Your job is to read the output and present a beautiful, concise summary to the user in the chat:
1. Summarize the total leaked spend.
2. List the ads recommended for **PAUSE** (with their categorized reason: Burn without Signal or Creative Decay).
3. List the ads recommended for **SCALE** (Early Winners).
4. If `--send_slack` was used, inform the user that a detailed Block Kit report has been dispatched to their Slack workspace.

## Data & Security Commitment

The eonik Ad Budget Leak Agent operates under strict data-privacy constraints to ensure your performance marketing data is handled securely:

1. **Secure Eonik Infrastructure:** All API requests are routed strictly to `https://api.eonik.ai` over TLS 1.2+. OpenClaw acts only as the orchestration layer; your sensitive ad performance data is processed entirely within Eonik's secure, enterprise-grade backend infrastructure.
2. **Zero Local Persistence:** The execution script securely parses your `EONIK_AUTH_TOKEN` from ephemeral environment variables. OpenClaw drops the token immediately after the API call completes, ensuring no credentials are ever cached, logged, or stored locally.
3. **Managed Slack Integrations:** The `--send_slack` feature leverages pre-configured, secure webhooks managed directly by the Eonik platform. You do not need to expose your local Slack workspace credentials or webhooks to the OpenClaw agent instance.
