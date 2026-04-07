---
name: socialcannon
description: >
  Publish, schedule, and manage social media posts across Twitter/X, Facebook,
  Instagram, and LinkedIn. Content calendar with gap analysis, A/B testing,
  engagement inbox, AI content repurposing, timing suggestions, and UTM tracking.
version: 1.0.0
metadata:
  openclaw:
    requires:
      env:
        - SOCIALCANNON_CLIENT_ID
        - SOCIALCANNON_CLIENT_SECRET
      bins:
        - curl
    primaryEnv: SOCIALCANNON_CLIENT_ID
    emoji: "\U0001F4E3"
    homepage: https://socialcannon.app
---

# SocialCannon

Social media publishing API. Publish to Twitter/X, Facebook, Instagram, and LinkedIn from one API with scheduling, analytics, A/B testing, and AI-powered features.

**Base URL:** `https://socialcannon.app`

## Authentication

All requests require a JWT Bearer token. Get one by exchanging your client credentials:

```bash
curl -X POST https://socialcannon.app/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d "{
    \"client_id\": \"$SOCIALCANNON_CLIENT_ID\",
    \"client_secret\": \"$SOCIALCANNON_CLIENT_SECRET\"
  }"
```

Response:
```json
{ "access_token": "eyJ...", "token_type": "bearer", "expires_in": 3600 }
```

Use the `access_token` as a Bearer token in all subsequent requests. Tokens expire after 1 hour — request a new one when you get a 401.

**All requests below require this header:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

## Response Format

All responses follow this shape:

- Success: `{ "success": true, "data": { ... } }`
- Error: `{ "success": false, "error": "message", "code": "ERROR_CODE" }`

## Accounts

### List connected accounts

```bash
curl https://socialcannon.app/api/v1/accounts \
  -H "Authorization: Bearer $TOKEN"
```

Returns all connected social accounts with their platform, username, and status. Use the account `id` field when creating posts.

### Get a single account

```bash
curl https://socialcannon.app/api/v1/accounts/<account_id> \
  -H "Authorization: Bearer $TOKEN"
```

### Disconnect an account

```bash
curl -X DELETE https://socialcannon.app/api/v1/accounts/<account_id> \
  -H "Authorization: Bearer $TOKEN"
```

## Posts

### Create a post

Publish immediately (omit `scheduledAt`) or schedule for later:

```bash
curl -X POST https://socialcannon.app/api/v1/posts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accountId": "<account_id>",
    "content": "Your post text here",
    "mediaUrls": ["https://example.com/image.jpg"],
    "scheduledAt": "2026-04-15T10:00:00Z",
    "platformOptions": {
      "autoUtm": true
    }
  }'
```

Fields:
- `accountId` (required) — ID from the accounts list
- `content` (required) — post text
- `mediaUrls` (optional) — array of public image/video URLs
- `scheduledAt` (optional) — ISO 8601 datetime; omit for immediate publish
- `platformOptions.autoUtm` (optional) — auto-tag URLs with UTM parameters

### List posts

```bash
curl "https://socialcannon.app/api/v1/posts?status=published&platform=twitter&limit=20" \
  -H "Authorization: Bearer $TOKEN"
```

Query params: `status` (draft/scheduled/published/failed), `platform`, `accountId`, `limit`, `cursor`

### Get a single post

```bash
curl https://socialcannon.app/api/v1/posts/<post_id> \
  -H "Authorization: Bearer $TOKEN"
```

### Update a draft or scheduled post

```bash
curl -X PATCH https://socialcannon.app/api/v1/posts/<post_id> \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Updated text",
    "scheduledAt": "2026-04-16T14:00:00Z"
  }'
```

### Delete a post

```bash
curl -X DELETE https://socialcannon.app/api/v1/posts/<post_id> \
  -H "Authorization: Bearer $TOKEN"
```

If the post is published, this also attempts to delete it from the social platform.

## Threads & Carousels

Create multi-part threads (Twitter reply chains, Instagram carousels, LinkedIn multi-segment posts):

```bash
curl -X POST https://socialcannon.app/api/v1/posts/thread \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accountId": "<account_id>",
    "items": [
      { "content": "Thread part 1 — the hook" },
      { "content": "Thread part 2 — the detail" },
      { "content": "Thread part 3 — the CTA", "mediaUrls": ["https://..."] }
    ],
    "scheduledAt": "2026-04-15T10:00:00Z"
  }'
```

Min 2 items, max 25 (Pro tier). Instagram requires media on each item.

## Media Upload

Upload images/videos before creating posts:

```bash
curl -X POST https://socialcannon.app/api/v1/media/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@photo.jpg"
```

Response: `{ "data": { "url": "https://...", "contentType": "image/jpeg", "size": 102400 } }`

Use the returned `url` in the `mediaUrls` field when creating posts. Images are auto-optimized to JPEG.

## Content Calendar

### Get calendar view

See posts grouped by date with gap analysis:

```bash
curl "https://socialcannon.app/api/v1/calendar?startDate=2026-04-01&endDate=2026-04-30" \
  -H "Authorization: Bearer $TOKEN"
```

Returns `posts`, `summary` (totals by status/platform/day), and `gaps` (dates with no posts).

Query params: `startDate` (required), `endDate` (required), `accountId`, `platform`

### Find available slots

```bash
curl "https://socialcannon.app/api/v1/calendar/slots?startDate=2026-04-01&endDate=2026-04-07" \
  -H "Authorization: Bearer $TOKEN"
```

Returns time slots not occupied by existing posts.

## Analytics

### Per-post analytics

Fetch live engagement metrics from the platform:

```bash
curl https://socialcannon.app/api/v1/posts/<post_id>/analytics \
  -H "Authorization: Bearer $TOKEN"
```

Returns: likes, comments, shares, impressions, reach, clicks, engagementRate, plus historical snapshots.

### Aggregate analytics

```bash
curl "https://socialcannon.app/api/v1/analytics/summary?startDate=2026-04-01&endDate=2026-04-30" \
  -H "Authorization: Bearer $TOKEN"
```

Returns totals across all posts for the date range.

### Bulk refresh analytics

```bash
curl -X POST https://socialcannon.app/api/v1/analytics/refresh \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "platform": "twitter", "limit": 20 }'
```

## Engagements (Comment Inbox)

### List engagements

```bash
curl "https://socialcannon.app/api/v1/engagements?isRead=false&limit=20" \
  -H "Authorization: Bearer $TOKEN"
```

Query params: `postId`, `isRead` (true/false), `limit`, `cursor`

### Fetch engagements for a post

```bash
curl https://socialcannon.app/api/v1/posts/<post_id>/engagements \
  -H "Authorization: Bearer $TOKEN"
```

Fetches fresh comments from the platform and stores them.

### Mark as read

```bash
curl -X PATCH https://socialcannon.app/api/v1/engagements/<engagement_id> \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "isRead": true }'
```

### Reply to an engagement

```bash
curl -X POST https://socialcannon.app/api/v1/engagements/<engagement_id>/reply \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "content": "Thanks for the feedback!" }'
```

Posts the reply directly on the social platform.

## AI Content Repurposing

Adapt content for multiple platforms using AI:

```bash
curl -X POST https://socialcannon.app/api/v1/posts/repurpose \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sourceContent": "Your long-form content here...",
    "targetPlatforms": ["twitter", "linkedin", "instagram"],
    "tone": "professional"
  }'
```

Returns platform-optimized variants, each pre-validated against the platform's content rules.

## A/B Testing (Pro)

### Create a test

```bash
curl -X POST https://socialcannon.app/api/v1/ab-tests \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accountId": "<account_id>",
    "name": "CTA test",
    "variants": [
      { "content": "Check out our new feature!" },
      { "content": "You won'\''t believe this new feature..." }
    ],
    "metric": "engagementRate",
    "minDurationHours": 24
  }'
```

Each variant is published as a separate post. Auto-completes after `minDurationHours`.

### Get test results

```bash
curl https://socialcannon.app/api/v1/ab-tests/<test_id> \
  -H "Authorization: Bearer $TOKEN"
```

Returns per-variant metrics, current winner, and confidence score.

### List tests

```bash
curl "https://socialcannon.app/api/v1/ab-tests?status=active" \
  -H "Authorization: Bearer $TOKEN"
```

### Force-complete a test

```bash
curl -X POST https://socialcannon.app/api/v1/ab-tests/<test_id>/complete \
  -H "Authorization: Bearer $TOKEN"
```

## Timing Suggestions (Pro)

Get recommended posting times based on historical engagement data:

```bash
curl "https://socialcannon.app/api/v1/accounts/<account_id>/timing?timezone=UTC-5" \
  -H "Authorization: Bearer $TOKEN"
```

Returns top 5 time slots ranked by average engagement rate with confidence scores.

## UTM Link Tracking

Generate UTM-tagged URLs:

```bash
curl -X POST https://socialcannon.app/api/v1/links/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/product",
    "platform": "twitter",
    "campaign": "spring-launch",
    "save": true
  }'
```

### List tracked links

```bash
curl "https://socialcannon.app/api/v1/links?limit=20" \
  -H "Authorization: Bearer $TOKEN"
```

## Platforms

List supported platforms and their capabilities (public, no auth required):

```bash
curl https://socialcannon.app/api/v1/platforms
```

## Platform-Specific Notes

- **Twitter/X**: 280 char limit. Up to 4 images. Threads via reply chains.
- **Facebook**: 63,206 char limit. Supports native scheduling. Page-level tokens.
- **Instagram**: Requires media (no text-only). Max 10 carousel items. No API deletion.
- **LinkedIn**: 3,000 char limit. Visibility: PUBLIC or CONNECTIONS. 2-step image upload.

## Rate Limits

- Free tier: 60 requests/minute
- Pro tier: 300 requests/minute
- Returns `429` with `Retry-After` header when exceeded

## Tips for Agents

1. Always list accounts first to get valid `accountId` values before creating posts.
2. Use the calendar endpoint to check for gaps before suggesting new posts.
3. For Instagram, always include at least one image URL — text-only posts will fail.
4. Use `autoUtm: true` in `platformOptions` to automatically tag URLs in posts.
5. Check analytics after 24+ hours for meaningful engagement data.
6. When repurposing content, review the returned `validation` field — if `valid` is false, adjust the content before publishing.
