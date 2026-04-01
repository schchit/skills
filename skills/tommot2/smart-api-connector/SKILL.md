---
name: smart-api-connector
description: "Connect to any REST API without writing code. Provide an endpoint and API key, and the agent handles authentication, request formatting, error parsing, retries, and rate limiting. Use when: user wants to query an API, test an endpoint, automate API calls, parse API responses, or integrate with external services. Supports GET, POST, PUT, DELETE with JSON payloads. Homepage: https://clawhub.ai/skills/smart-api-connector"
---

# Smart API Connector

Connect to any REST API without code. The agent handles everything — you just provide the endpoint.

## Language

Detect from the user's message language. Default: English.

## Related Skills

| Skill | Why |
|-------|-----|
| `setup-doctor` | Diagnose environment issues before API work |
| `context-brief` | Long API sessions consume context — brief keeps things lean |
| `locale-dates` | Format API timestamps to user's locale |

> 💡 **Full suite**: `clawhub install setup-doctor && clawhub install context-brief && clawhub install locale-dates`

## Quick Start

User provides:
1. **API base URL** (e.g., `https://api.example.com/v1`)
2. **API key** (used in-session only — see Security below)
3. **What they want to do** in natural language

Agent does everything else.

## Security & Credentials

### ⚠️ API Key Handling — Read This

**This skill does NOT persist API keys.** However, the following is true:

- The agent's **conversation history and logs may retain keys** that were typed or used in requests
- If the key appears in command arguments (e.g., curl commands), it may appear in process listings (`ps aux`)
- This depends on your **platform configuration**, not this skill

**Recommendations:**
- Use **scoped or test API keys** when possible — never long-lived production secrets
- After sensitive API work, consider clearing conversation history if your platform supports it
- For permanent storage, use your OS keychain (1Password, Bitwarden, Windows Credential Manager)

### Safe Key Supply Patterns (Required)

**The agent MUST use one of these methods to pass API keys. Never pass keys as plain command-line arguments.**

#### Method 1: Environment Variable (Preferred)

Set the key as an env var for the command, then reference it:

```bash
# Bash
API_KEY="your_key_here" curl -s -H "Authorization: Bearer $API_KEY" "https://api.example.com/v1/endpoint"

# PowerShell
$env:API_KEY="your_key_here"; Invoke-WebRequest -Headers @{Authorization="Bearer $env:API_KEY"} "https://api.example.com/v1/endpoint"
```

Keys in env vars do NOT appear in process listings visible to other users.

#### Method 2: Stdin / Heredoc (For file-based payloads)

```bash
# Pass key via env var, body via stdin
echo '{"key":"value"}' | API_KEY="your_key" curl -s -X POST -H "Authorization: Bearer $API_KEY" -H "Content-Type: application/json" -d @- "https://api.example.com/v1/endpoint"
```

#### Method 3: Netrc File (For frequent API use)

```bash
# Create ~/.netrc (permissions: 600)
machine api.example.com
  login your_api_key
  password x-oauth-basic

# curl automatically picks up .netrc
curl -s -n "https://api.example.com/v1/endpoint"
```

#### Method 4: PowerShell -SecureString (Windows)

```powershell
$secureKey = ConvertTo-SecureString "your_key_here" -AsPlainText -Force
$headers = @{ Authorization = "Bearer $($secureKey | ConvertFrom-SecureString -AsPlainText)" }
Invoke-WebRequest -Headers $headers "https://api.example.com/v1/endpoint"
```

#### ❌ Never Do This

```bash
# BAD: Key visible in process listings and shell history
curl -s -H "Authorization: Bearer sk_live_abc123def456..." "https://api.example.com/v1/endpoint"
```

### HTTP Client

This skill uses the agent's **built-in exec tool** to run HTTP requests. No external binaries are required.

If `curl` is available on the system, it will be used for its superior header/formatting support. If not, the agent falls back to `Invoke-WebRequest` (PowerShell) or `python3 -c` with urllib — all of which are standard in modern environments.

**Regardless of HTTP client, always use env vars or headers — never inline secrets in command arguments.**

## Connection Setup

### Step 1: Handle API Key

When user provides an API key, use it in-session for the current request chain:

- Use the key only within the current conversation/session
- Store in an **environment variable** for the duration of the request chain — never in command arguments
- NEVER display the full key back or log it
- After the session ends, the user must provide it again

If the user asks to store a key permanently, recommend their OS keychain or a secret manager.

### Step 2: Verify Connection

Test with a simple request before any real work.

Expected responses:
- HTTP 200 → ✅ Connected
- HTTP 401 → ❌ Invalid key — ask user to verify
- HTTP 403 → ⚠️ Valid key, insufficient permissions
- Timeout → ⚠️ Network issue or API down

### Step 3: Discover Endpoints (optional)

If user says "explore" or "what can I do", fetch the OpenAPI spec:

- Try `{base_url}/openapi.json` or `{base_url}/openapi.yaml`
- Parse the spec and list available endpoints with descriptions

## Making Requests

### HTTP Methods

| Method | Use When | Notes |
|--------|----------|-------|
| GET | "get X", "fetch Y", "list Z" | Read-only, safe |
| POST | "create X", "send Y", "add Z" | Include JSON body |
| PUT/PATCH | "update X", "change Y" | Include JSON body |
| DELETE | "delete X", "remove Y" | ⚠️ ALWAYS confirm first |

### DELETE Safety

**⚠️ ALWAYS confirm before DELETE.** Show exactly what will be deleted and get explicit "yes" / "ja" before proceeding.

## Authentication Methods

| Method | Header | When to use |
|--------|--------|-------------|
| Bearer Token | `Authorization: Bearer $KEY` | Most modern APIs (Stripe, Notion, OpenAI) |
| API Key (query) | `?api_key=$KEY` | Legacy APIs |
| API Key (header) | `X-API-Key: $KEY` | AWS, SendGrid |
| Basic Auth | `Authorization: Basic base64(user:pass)` | Simple APIs |
| Custom | Varies | Ask user for docs or header name |

If user doesn't specify auth method, try Bearer Token first (most common). If 401, ask user for correct auth method.

## Retry Logic

### Automatic Retries

Retry on these HTTP codes without asking:

| Code | Meaning | Action |
|------|---------|--------|
| 429 | Rate limited | Wait `Retry-After` seconds, then retry. If no header: 5s → 10s → 20s (max 3 retries) |
| 500 | Server error | 2s → 4s → 8s (max 3 retries) |
| 502 | Bad gateway | 3s → 6s → 12s (max 2 retries) |
| 503 | Service unavailable | 5s → 10s (max 2 retries) |
| 504 | Gateway timeout | 5s → 10s (max 2 retries) |

### No Automatic Retry

These require user intervention:

| Code | Meaning | Action |
|------|---------|--------|
| 400 | Bad request | Show the error body — user likely has a parameter wrong |
| 401 | Unauthorized | Ask user to check API key |
| 403 | Forbidden | Explain permissions issue |
| 404 | Not found | Confirm endpoint URL with user |
| 422 | Validation error | Show validation errors from response body |

## Rate Limiting

When making multiple requests in sequence:

- **Default delay**: 500ms between requests
- **If 429 received**: Extract `Retry-After` header, wait that long, then continue
- **If X-RateLimit-Remaining < 5**: Slow to 1 request/second
- **For bulk operations** (10+ requests): Ask user before proceeding — estimate time and confirm

## Response Parsing

### JSON Responses

Parse and present as structured markdown:

```markdown
## Result ({count} items)

| Field1 | Field2 | Field3 |
|--------|--------|--------|
| value  | value  | value  |
```

If response is large (> 50 items), summarize:
- Show first 10 items as table
- Show count: "X total items (showing first 10)"
- Offer: "Vis alle" / "Show all" / "Filter by..." / "Export to file"

### Error Responses

Always extract and show the error message from the response body:

> ❌ **Rate limit exceeded** (rate_limit) — Too many requests. Waiting 5s before retry...

### Non-JSON Responses

If response is not JSON (HTML, XML, plain text):
- Show first 500 characters
- Note the content type
- Offer to save full response to a file for inspection

## Saved Connections

Track configured APIs in the current session:

```markdown
## Configured APIs

| Name | Base URL | Auth | Last Tested |
|------|----------|------|-------------|
| Example API | https://api.example.com/v1 | Bearer | today |
```

When user asks to list APIs — show configured connections from this session.

## Output Format

Adapts to user language.

### English
```markdown
## 🔗 API Response — {endpoint}

**Status:** 200 OK | **Time:** {X}ms | **Items:** {X}

| ... |

---
Retry: 0/3 | Rate limit remaining: X
```

### Norwegian
```markdown
## 🔗 API-respons — {endpoint}

**Status:** 200 OK | **Tid:** {X}ms | **Elementer:** {X}

| ... |

---
Forsøk: 0/3 | Rate limit gjenstående: X
```

## More by TommoT2

- **workflow-builder-lite** — Chain multi-step workflows with conditional logic
- **setup-doctor** — Diagnose and fix OpenClaw setup issues
- **tommo-skill-guard** — Security scanner for all installed skills
