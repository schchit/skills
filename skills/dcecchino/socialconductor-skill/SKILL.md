---
name: socialconductor
description: Control all your SocialConductor AI bots from WhatsApp, Slack, or Telegram. Manage your YouTube, TikTok, and Facebook/Instagram comment automation — check status, pause replies, view logs, post manual replies, and manage video polling — all from chat.
version: "1.1.0"
metadata:
  openclaw:
    requires:
      env:
        - SC_YT_API_KEY
    emoji: "🤖"
    homepage: https://studio.socialconductor.ai
    primaryEnv: SC_YT_API_KEY
---

# SocialConductor — All Platforms

Control all your SocialConductor AI comment bots from any chat app.

## Platforms

| Platform | Status | App URL |
|----------|--------|---------|
| 📺 YouTube | ✅ Live | studio.socialconductor.ai |
| 🎵 TikTok | 🔜 Coming Soon | violin.socialconductor.ai |
| 👥 Facebook / Instagram | 🔜 Coming Soon | podium.socialconductor.ai |

---

## YouTube — Setup (first time only)

Say this to OpenClaw:

> connect my youtube channel

OpenClaw will register you, then send a one-time browser link. Open it, sign
in with Google (30 seconds), close the tab. All commands are now active.

## YouTube — Commands

| Say this | What happens |
|----------|-------------|
| check my youtube bot status | Mode, plan, daily usage, last 3 comments |
| pause my youtube bot | Hold mode ON — replies stop immediately |
| resume my youtube bot | Hold mode OFF — replies resume |
| show recent youtube comments | Last 5 log entries |
| show posted youtube comments | Only live-posted replies |
| show youtube gate skipped comments | Comments the bot skipped |
| show youtube leads | Lead-trigger comments only |
| reply to youtube comment abc123 with Great question! | Posts manual reply |
| turn on fast youtube response mode | Sets delay mode to fast |
| turn on aggressive youtube response mode | Sets delay mode to aggressive |
| turn on youtube simulation mode | Replies generated but not posted |
| go youtube live | Disables simulation — bot posts for real |
| enable my youtube bot | Turns on auto-reply |
| disable my youtube bot | Turns off auto-reply |
| show my youtube videos | Video polling status |
| show stale youtube videos | Videos with no recent activity |
| reactivate youtube video abc123 | Resumes polling that video |

## YouTube — Webhook Base URL
https://studio.socialconductor.ai/api/openclaw/

---

## TikTok — Coming Soon 🔜

TikTok bot control via chat is in development.
Visit violin.socialconductor.ai to manage your TikTok bot in the meantime.

Planned commands:
- check my tiktok bot status
- pause my tiktok bot / resume my tiktok bot
- show recent tiktok comments
- show tiktok leads
- reply to tiktok comment abc123 with Great video!

---

## Facebook / Instagram — Coming Soon 🔜

Facebook and Instagram bot control via chat is in development.
Visit podium.socialconductor.ai to manage your Facebook bot in the meantime.

Planned commands:
- check my facebook bot status
- pause my facebook bot / resume my facebook bot
- show recent facebook comments
- show facebook leads
- reply to facebook comment abc123 with Thanks!

---

## Auth
Bearer token — stored automatically by OpenClaw after setup.
Each platform will use its own API key registered at setup time.

## Registration Flow
On first use OpenClaw calls POST /api/openclaw/register with your openclaw_user_id.
Your API key is stored locally and sent as a Bearer token on every subsequent call.
To link your YouTube channel, OpenClaw calls POST /api/openclaw/link_token and sends
you a browser link. After OAuth your channel is permanently connected.
