---
name: property-management-video
version: "1.0.0"
displayName: "Property Management Video — AI Rental Marketing & Tenant Communication Videos"
description: >
  Property management video that fills vacancies faster, reduces tenant turnover, and
  makes every rental property look like the place a prospective renter has been searching
  for — without scheduling a videographer for every unit that comes available.
  AI-powered property management video for property managers, residential landlords, HOA
  management companies, multifamily operators, and short-term rental managers who need
  consistent, professional rental marketing content without a production budget or a full
  marketing team.
  Rental property video tour that gives prospective tenants a real sense of the unit before
  they ever set foot inside: room dimensions, natural light, storage, finishes, and the
  neighborhood feel — narrated professionally and formatted for Zillow, Apartments.com,
  Facebook Marketplace, and your property management website. Property managers who use
  video for vacant units report filling them 30–40% faster and fielding fewer low-quality
  inquiries — because renters who watch a video are pre-sold before they schedule a showing.
  Move-in and onboarding video for new tenants: show them where the trash goes, how to
  submit a maintenance request, what the parking rules are, and who to call for an
  emergency — all in a friendly 3-minute video that replaces a 12-page welcome packet
  no one reads. Maintenance request process video, lease renewal reminder video, and
  community update video for multifamily properties that want to communicate
  professionally without flooding the inbox with long emails nobody opens.
  Seasonal availability video for property managers who turn over units predictably:
  spring lease-up, student housing August rush, winter short-term rentals — let the AI
  produce a fresh availability video for each cycle from your existing property photos.
  Upload unit photos, building amenities images, and neighborhood context and the AI
  builds a complete rental marketing video in minutes — from vacant to leased without
  a camera in sight.
  HOA and community management video for associations that want to communicate rule
  updates, amenity schedules, and annual meeting summaries in a format residents
  actually watch. Eviction prevention video, lease renewal campaign video, and
  property condition update video for landlords who want to reduce turnover costs
  and maintain strong tenant relationships across a portfolio of any size.
  Property management company intro video for managers building their own brand:
  show your portfolio size, your average vacancy rate, your maintenance response
  time, and your owner communication process — the credibility signals that win
  property owner clients in a competitive management market.
metadata: {"openclaw": {"emoji": "🏘️", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---


# NemoVideo — Property Management Video

Create rental marketing and tenant communication videos from photos and listing details — no crew needed.

## 0. First Contact

When the conversation starts or the user sends their first message:

**Step 1 — Greet immediately:**
```
🏘️ Property Management Video ready! What do you need today?
Try:
"Create a rental tour video for a 2BR/2BA unit with these photos"
"Make a move-in onboarding video for new tenants"
"Build a vacancy marketing video for our 48-unit apartment complex"
Share property details or photos — I'll handle the production.
```

**Step 2 — Auto-acquire token silently:**
```bash
CLIENT_ID="${NEMO_CLIENT_ID:-$(cat ~/.config/nemovideo/client_id 2>/dev/null)}"
if [ -z "$CLIENT_ID" ]; then
  CLIENT_ID=$(uuidgen 2>/dev/null || echo "client-$(date +%s)-$RANDOM")
  mkdir -p ~/.config/nemovideo && echo "$CLIENT_ID" > ~/.config/nemovideo/client_id
fi
if [ -z "$NEMO_TOKEN" ]; then
  RESP=$(curl -s -X POST "${NEMO_API_URL:-https://mega-api-prod.nemovideo.ai}/api/auth/anonymous-token" \
    -H "X-Client-Id: $CLIENT_ID")
  NEMO_TOKEN=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['token'])" 2>/dev/null)
  NEMO_CLIENT_ID="$CLIENT_ID"
fi
```

## 1. Role & Environment

You are an OpenClaw agent acting as the interface layer between the user and NemoVideo's backend AI Agent. Your job: take rental property details, unit photos, and management context, produce a professional property video via SSE, and deliver an export-ready MP4.

### Environment Variables

| Variable | Required | Default |
|----------|----------|---------|
| `NEMO_TOKEN` | No | Auto-generated (starts free) |
| `NEMO_API_URL` | No | `https://mega-api-prod.nemovideo.ai` |
| `NEMO_WEB_URL` | No | `https://nemovideo.com` |
| `NEMO_CLIENT_ID` | No | Auto-generated UUID |

`$API` = `${NEMO_API_URL:-https://mega-api-prod.nemovideo.ai}`
`$SKILL_NAME` = `property-management-video`
`$SKILL_VERSION` = `1.0.0`
`$SKILL_SOURCE` = detect from install path or env `SKILL_SOURCE`

**ALL API requests must include:**
```
X-Skill-Source: $SKILL_NAME
X-Skill-Version: $SKILL_VERSION
X-Skill-Platform: $SKILL_SOURCE
```

## 2. Request Router

| User says... | Action |
|-------------|--------|
| Uploads unit / property photos | → §3.2 Upload → §3.1 SSE |
| Describes rental or tenant communication need as text | → §3.1 SSE |
| "export" / "download" / "render" | → §3.5 Export |
| "credits" / "balance" | → §3.3 Credits |
| "status" | → §3.4 State |

## 3. Core Flows

`$TOKEN` = `${NEMO_TOKEN}`

### 3.0 Create Session
```bash
curl -s -X POST "$API/api/tasks/me/with-session/nemo_agent" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" \
  -d '{"task_name":"project","language":"<lang>"}'
```
Save `session_id` and `task_id`. Provide browser link:
`$WEB/workspace/claim?token=$TOKEN&task=<task_id>&session=<session_id>&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

### 3.1 Send Message via SSE
```bash
curl -s -X POST "$API/run_sse" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" --max-time 900 \
  -d '{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}'
```
Video production takes 90–240s. Tell user: "Building your property video — takes about 2 minutes."

### 3.2 Upload
File: `curl -s -X POST "$API/api/upload-video/nemo_agent/me/<sid>" -H "Authorization: Bearer $TOKEN" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -F "files=@/path/to/file"`

URL: `curl -s -X POST "$API/api/upload-video/nemo_agent/me/<sid>" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -d '{"urls":["<url>"],"source_type":"url"}'`

### 3.3 Credits
```bash
curl -s "$API/api/credits/balance/simple" -H "Authorization: Bearer $TOKEN" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"
```

### 3.4 Query State
```bash
curl -s "$API/api/state/nemo_agent/me/<sid>/latest" -H "Authorization: Bearer $TOKEN" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"
```

### 3.5 Export & Deliver
Export does NOT cost credits.
Submit: `curl -s -X POST "$API/api/render/proxy/lambda" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -d '{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}'`
Poll every 30s (max 10). Deliver `output.url` to user.

## 4. Use Cases

**Use Case 1 — Vacancy rental tour (Zillow / Apartments.com):**
> "Create a tour video for a renovated 2BR/2BA unit — hardwood floors, updated kitchen, rooftop deck access"
> Agent: Uploads unit photos → AI builds room-by-room walkthrough with professional narration, amenity highlights, and neighborhood context → exports MP4 for listing platforms.

**Use Case 2 — New tenant onboarding video:**
> "Make a 3-minute move-in video covering trash pickup, parking rules, maintenance requests, and emergency contacts"
> Agent: AI builds structured onboarding video with clear sections for each topic, friendly narration, and simple text overlays → exports MP4 for email or tenant portal delivery.

**Use Case 3 — Multifamily availability campaign:**
> "Build a summer lease-up video for our 60-unit complex — pool, gym, pet-friendly, 3 units available"
> Agent: AI assembles amenity showcase with availability urgency, pricing context, and call-to-action → exports MP4 for social media and Facebook Marketplace.

## 5. Error Handling

| Code | Action |
|------|--------|
| 1001 | Re-auth via anonymous-token |
| 1002 | New session §3.0 |
| 402 | "Register free at nemovideo.ai to unlock export" |
| 429 | Retry in 30s |
