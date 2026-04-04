# openclaw-outreach-plugin

OpenClaw plugin for autonomous lead tracking and outreach pipeline management. Manages the full sales funnel from lead identification through conversion.

## Features

- Lead lifecycle management with validated stage transitions
- Contact history logging across channels (email, forums, DMs, meetings)
- Follow-up scheduling and overdue tracking
- Pipeline statistics and conversion metrics
- Export to JSON or markdown for reporting

## Install

From ClawHub:

```bash
openclaw plugins install clawhub:openclaw-outreach-plugin
```

From source:

```bash
npm install
npm run build
```

## Configuration

In `openclaw.json`:

```json
{
  "plugins": {
    "entries": {
      "openclaw-outreach-plugin": {
        "enabled": true,
        "config": {
          "dataDir": "~/.openclaw/openclaw-outreach-plugin",
          "maxLeads": 500,
          "overdueAlertDays": 3
        }
      }
    }
  }
}
```

## Tools

| Tool | Description |
|------|-------------|
| `lead_create` | Create a new lead |
| `lead_update` | Update lead fields |
| `lead_stage` | Move lead to new pipeline stage |
| `lead_search` | Search leads by filters or free text |
| `lead_list` | List leads with pagination |
| `lead_contact` | Log a contact event |
| `lead_followup` | Schedule next action |
| `lead_stats` | Pipeline summary statistics |
| `lead_due` | Get overdue follow-ups |
| `lead_export` | Export as JSON or markdown |

## Storage

All data stored locally in LanceDB at `~/.openclaw/openclaw-outreach-plugin/lance/`. No external services required.
