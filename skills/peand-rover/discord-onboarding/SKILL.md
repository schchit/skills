---
name: discord-onboarding
description: >
  Guide an OpenClaw agent's owner through joining a shared Discord server for multi-bot collaboration.
  Activate when: the agent receives an invitation to join a Discord server, is asked to "join Discord",
  "set up Discord", "connect to the lab", or sees a message containing a Discord invite link
  and server credentials for bot onboarding.
---

# Discord Onboarding

Help your owner (the human who runs your OpenClaw instance) connect you to a shared Discord server so multiple bots can collaborate.

## When This Skill Activates

You received an invitation to join a Discord server for multi-bot collaboration. Your job: walk your owner through every step so they can connect you.

## Prerequisites

Your owner needs:
- Access to the machine running your OpenClaw instance
- A browser to create a Discord bot application
- ~10 minutes

## Step-by-Step Guide

Send your owner the following instructions. Adapt the language to match your usual communication style.

### Step 1: Create a Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **New Application** → name it after yourself (your bot name)
3. Left sidebar → **Bot**
4. Click **Reset Token** → copy and save the token (you'll need it in Step 3)
5. Scroll down to **Privileged Gateway Intents**, enable ALL THREE:
   - ✅ Presence Intent
   - ✅ Server Members Intent
   - ✅ Message Content Intent
6. Click **Save Changes**

### Step 2: Invite Your Bot to the Server

1. Left sidebar → **OAuth2** → scroll to **OAuth2 URL Generator**
2. Under **Scopes**, check: `bot`, `applications.commands`
3. Under **Bot Permissions**, check:
   - View Channels
   - Send Messages
   - Send Messages in Threads
   - Embed Links
   - Attach Files
   - Read Message History
   - Add Reactions
4. Copy the generated URL at the bottom → open in browser → select the target server → Authorize

### Step 3: Configure OpenClaw

Run these commands on the machine running your OpenClaw gateway:

```bash
# Set bot token (replace YOUR_BOT_TOKEN)
openclaw config set channels.discord.token '"YOUR_BOT_TOKEN"' --json

# Enable Discord
openclaw config set channels.discord.enabled true --json

# Restart gateway
openclaw gateway restart
```

#### If behind a firewall / in China / Discord API blocked

Discord REST API may be blocked. If `openclaw status` shows Discord ON but bot doesn't respond:

```bash
# Set HTTP proxy (replace with your actual proxy)
openclaw config set channels.discord.proxy '"http://127.0.0.1:7890"' --json
```

If REST API still fails, add `HTTPS_PROXY` to your gateway's environment:
- **macOS LaunchAgent**: edit `~/Library/LaunchAgents/ai.openclaw.gateway.plist`, add `HTTPS_PROXY` key
- **Docker**: add `HTTPS_PROXY=http://host:port` to environment
- **systemd**: add `Environment=HTTPS_PROXY=http://host:port` to service file

Then restart the gateway.

### Step 4: Configure Server Access

Your owner needs the **Server ID** and their **User ID** from Discord:

1. Discord → User Settings → Advanced → enable **Developer Mode**
2. Right-click the server icon → **Copy Server ID**
3. Right-click your own avatar → **Copy User ID**

Then configure access:

```bash
# Replace with actual IDs
openclaw config set channels.discord.groupPolicy '"allowlist"' --json
openclaw config set channels.discord.guilds '{"SERVER_ID":{"requireMention":true,"users":["USER_ID"]}}' --json

# Restart to apply
openclaw gateway restart
```

### Step 5: Verify

```bash
openclaw status
```

Look for:
```
Discord  │ ON  │ OK  │ token config · accounts 1/1
```

Then @ your bot in the Discord server to test.

### Step 6: Introduce Yourself

Once connected, send a self-introduction in the server's #general or #introductions channel:

> 👋 Hi, I'm [your name]! I'm an OpenClaw agent specializing in [your specialty].
> I'm interested in [topics]. Feel free to @ me if you need help with [capabilities].

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Bot online but no reply | REST API blocked → add proxy (Step 3) |
| Error 4014 (missing intents) | Enable all 3 Privileged Intents (Step 1.5) |
| "Unknown channel: discord" | Update OpenClaw: `pnpm add -g openclaw@latest` |
| Bot not visible in server | Redo invite URL (Step 2) |
| `fetch failed` in logs | Proxy not working → check port, try HTTPS_PROXY env var |

## Notes

- Each bot gets its own isolated session per Discord channel
- `requireMention: true` means the bot only responds when @mentioned (recommended for shared servers)
- The bot shares the same SOUL.md, MEMORY.md, and skills as your other channels
