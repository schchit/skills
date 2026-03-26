---
name: ogp
description: >
  OGP (Open Gateway Protocol) — schedule meetings, query peers, and coordinate
  with other OpenClaw users via federated gateway messaging. Use when the user
  asks to schedule a meeting with someone, check a peer's availability, or
  manage OGP federation relationships.
---

# OGP — Open Gateway Protocol

OGP lets this gateway securely exchange messages with other OpenClaw gateways.
Each relationship is explicitly approved, scoped, and authenticated with Ed25519 signatures.

## State Directory

```bash
OPENCLAW_STATE_DIR=~/.openclaw     # main gateway state dir
PEER_FILE=$OPENCLAW_STATE_DIR/federation-peers.json
```

## Step 1 — Find the peer

```bash
# List all approved peers
node ~/Documents/GitHub/openclaw/dist/index.js federation list

# Check peer capabilities (what intents they support)
curl -s https://<peer-gateway-url>/.well-known/ogp | python3 -m json.tool
```

**Decision tree:**
- Peer found + approved + has required intent → go to Step 2
- Peer found + pending → tell user: "federation request pending, can't act yet"
- Peer found + approved + missing intent → tell user: "peer doesn't support this yet"
- Peer not found → go to Step 1b (request federation)

## Step 1b — Request federation (if no peer exists)

```bash
node ~/Documents/GitHub/openclaw/dist/index.js federation request \
  --gateway <peer-gateway-url> \
  --scope calendar-read,calendar-write,ping
```

Then inform the user and wait for approval before proceeding.

## Step 2 — Schedule a meeting (calendar-read + calendar-write)

### 2a. Query peer's availability

```bash
node ~/Documents/GitHub/openclaw/dist/index.js federation send \
  <peer-gateway-id> \
  --intent calendar-read \
  --payload "{\"start\":\"<ISO_START>\",\"end\":\"<ISO_END>\",\"duration\":<MINS>}"
```

- Default window: next week, Mon–Fri, 9am–5pm peer's timezone
- Duration: 30 minutes unless specified
- The reply contains `available: [{start, end, duration}]`
- Pick the **first available slot** unless user specifies otherwise

### 2b. Create the calendar event (on YOUR calendar, invite peer)

```bash
~/Documents/GitHub/openclaw-federation/scripts/gwb-calendar-write.sh \
  "<START_ISO>" \
  "<END_ISO>" \
  "Meeting with <peer-display-name>" \
  "<peer-email>" \
  "<peer-display-name>"
```

The peer's email comes from their stored peer record:
```bash
cat ~/.openclaw/federation-peers.json | python3 -c "
import json,sys
d=json.load(sys.stdin)
for k,v in d.items():
    if '<peer-name>' in v.get('displayName','').lower():
        print(v.get('email','not set'))
"
```

## Step 3 — Confirm to user

After booking:
> "Done. Meeting scheduled with [Name] for [Day] [Date] at [Time] [TZ].
>  Calendar invite sent to [email]. I'll let you know when they respond."

## Step 4 — Monitor invite response (optional)

```bash
# Check if attendee has responded to a calendar event
~/.nvm/versions/node/v22.22.0/bin/gws calendar events list \
  --params '{"calendarId":"primary","timeMin":"<START>","timeMax":"<END>","singleEvents":true}' \
  | python3 -c "
import json,sys
events = json.load(sys.stdin).get('items',[])
for e in events:
    for a in e.get('attendees',[]):
        print(a.get('email'), ':', a.get('responseStatus'))
"
```

Response statuses: `needsAction` | `accepted` | `declined` | `tentative`

## Peer Address Book

Known peers (update as federation relationships are added):

| Name | Gateway ID | Gateway URL | Email | Notes |
|---|---|---|---|---|
| Alex Chen (demo) | latent-genius.local:12010 | http://localhost:12010 | david@theproctors.cloud | Demo Gateway B |

To look up any peer dynamically:
```bash
cat ~/.openclaw/federation-peers.json | python3 -c "
import json,sys
peers = json.load(sys.stdin)
for k,v in peers.items():
    if v.get('status') == 'approved':
        print(f\"{v['displayName']} | {k} | {v.get('email','no email')} | {v.get('scope')}\")
"
```

## Common Intents

| Intent | What it does | Required payload |
|---|---|---|
| `ping` | Check if peer gateway is alive | `{}` |
| `calendar-read` | Get peer's available slots | `{start, end, duration}` |
| `calendar-write` | Create event on peer's calendar | `{start, end, title, attendee_email, attendee_name}` |
| `web-search` | Ask peer's gateway to search | `{query}` |

## CLI Quick Reference

```bash
# List peers
node ~/Documents/GitHub/openclaw/dist/index.js federation list

# Ping a peer
node ~/Documents/GitHub/openclaw/dist/index.js federation send <id> --intent ping

# Check peer capabilities  
curl -s <gateway-url>/.well-known/ogp | python3 -m json.tool

# Request new federation
node ~/Documents/GitHub/openclaw/dist/index.js federation request \
  --gateway <url> --scope calendar-read,calendar-write,ping

# Approve inbound request
node ~/Documents/GitHub/openclaw/dist/index.js federation approve <gateway-id>

# List registered intent handlers
node ~/Documents/GitHub/openclaw/dist/index.js federation intents

# Register a new intent handler
node ~/Documents/GitHub/openclaw/dist/index.js federation register-intent <intent> \
  --command "<shell command with {param} substitutions>"
```

## Environment Variables (for test gateways)

When using test gateway A (port 12000) or B (port 12010), prefix commands with:
```bash
OPENCLAW_CONFIG_PATH=~/.openclaw-fed-a/openclaw.json \
OPENCLAW_STATE_DIR=~/.openclaw-fed-a \
OPENCLAW_GATEWAY_PORT=12000 \
```

For the main production gateway, no prefix needed — defaults apply.

## Error Handling

| Error | Likely cause | Fix |
|---|---|---|
| `Peer not found or not approved` | Not federated or pending | Check `federation list` |
| `Intent X not in approved scope` | Scope too narrow | Re-request with wider scope |
| `Invalid signature` | Wrong keypair or stale peer record | Clear peers, re-establish trust |
| `No reply received within 30 seconds` | Peer gateway down or intent handler misconfigured | Ping the peer first |
