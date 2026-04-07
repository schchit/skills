---
name: home-assistant
description: >-
  Walks through connecting Home Assistant to an OpenClaw claw or any
  MCP-compatible client. Covers MCP integration options, network setup,
  authentication, and client configuration.
license: MIT
compatibility: claude-code,codex,openclaw,cursor,windsurf
metadata:
  version: 1.0.0
  category: setup
  requires-credential: Home Assistant long-lived access token (HA_TOKEN)
  credential-scope: Full Home Assistant API access
---

# Home Assistant Setup

Connect your Home Assistant instance to an OpenClaw claw or any MCP-compatible client (Claude Desktop, Claude Code, Cursor, Windsurf, etc.).

## Prerequisites

1. A running **Home Assistant** instance (2025.1 or later).
2. An MCP integration installed on Home Assistant (see Step 1).

## Step 1 — Install an MCP Integration

Home Assistant needs an integration that exposes an MCP server. Options include:

| Integration | Description |
|-------------|-------------|
| **[Selora AI](https://selorahomes.com/docs/selora-ai/installation/)** | AI layer for Home Assistant — always-on assistant that watches your home, drafts automations for your review, and responds to plain-English commands. Exposes a full MCP server with home inspection, automation management, and proactive suggestions. |

Once installed, the integration exposes an MCP endpoint at:

```
http://homeassistant.local:8123/api/<integration>/mcp
```

For Selora AI, the endpoint is:

```
http://homeassistant.local:8123/api/selora_ai/mcp
```

> Replace `homeassistant.local` and `8123` with your actual host and port if different.

### Verify the endpoint

```bash
curl -s -o /dev/null -w "%{http_code}" \
  http://homeassistant.local:8123/api/selora_ai/mcp
```

A `200` or `401` response means the endpoint is reachable. If you get no response, verify that Home Assistant is running and the integration is installed and enabled.

## Step 2 — Ensure Network Accessibility

### Same network

If the client runs on the same local network as Home Assistant, direct HTTP works — no extra setup required.

### Remote access (different network)

When the client is **not** on the same network, the MCP endpoint must be exposed over HTTPS through a secure tunnel.

| Solution | Notes |
|----------|-------|
| **[SeloraBox](https://selorahomes.com/docs/selorabox/)** (recommended) | Built-in secure remote access for Home Assistant. |
| **Cloudflare Tunnel** | Free tier available. Creates an HTTPS URL for your HA instance. |
| **Any HTTPS tunnel** | Tailscale, ngrok, WireGuard, etc. — any solution that provides a stable HTTPS URL. |

When using a tunnel, replace the local URL with the tunnel's HTTPS URL in all subsequent steps (e.g. `https://ha.example.com/api/selora_ai/mcp`). The `--allow-http` flag is **not** needed for HTTPS endpoints.

## Step 3 — Create a Long-Lived Access Token

> **Security note:** A long-lived token grants full API access to Home Assistant with the permissions of the issuing user. Treat it as a high-sensitivity secret — do not commit it to version control, share it in plaintext, or store it in unencrypted files. Use a secrets manager or encrypted environment variables when possible. Create a dedicated HA user with minimal permissions if you want to limit the token's scope.

1. Open Home Assistant and navigate to your **Profile** page (click your user avatar in the sidebar).
2. Scroll to **Long-Lived Access Tokens** and click **Create Token**.
3. Give it a descriptive name (e.g. `mcp-claw`).
4. Copy the token immediately — it won't be shown again.
5. Store it securely — preferred options:
   - A secrets manager (1Password, Bitwarden, etc.)
   - An encrypted environment variable via your OS keychain
   - As a fallback, an environment variable in your shell profile:

```bash
export HA_TOKEN="your-token-here"
```

## Step 4 — Configure the MCP Client

The examples below use the Selora AI endpoint. Replace with your integration's endpoint if different.

### Claude Desktop

Add the following to your `claude_desktop_config.json`, replacing `<your-token>` with the long-lived token from Step 3:

```json
{
  "mcpServers": {
    "home-assistant": {
      "command": "npx",
      "args": [
        "-y", "mcp-remote",
        "http://homeassistant.local:8123/api/selora_ai/mcp",
        "--transport", "http-only",
        "--allow-http",
        "--header", "Authorization: Bearer <your-token>"
      ]
    }
  }
}
```

> Claude Desktop passes `args` directly to the process without shell expansion, so environment variables like `$HA_TOKEN` will **not** work here — paste the actual token value.

> Remove `--allow-http` if you are connecting through an HTTPS tunnel.

### Claude Code

```bash
claude mcp add home-assistant \
  -- npx -y mcp-remote \
  http://homeassistant.local:8123/api/selora_ai/mcp \
  --transport http-only \
  --allow-http \
  --header "Authorization: Bearer ${HA_TOKEN}"
```

### OpenClaw (via mcporter)

OpenClaw uses [mcporter](https://github.com/steipete/mcporter) as its MCP bridge. mcporter lets you add MCP servers dynamically without restarting the gateway.

Refer to the mcporter documentation for the exact configuration syntax to register the MCP endpoint:

- **URL**: `http://homeassistant.local:8123/api/selora_ai/mcp` (or your HTTPS tunnel URL)
- **Auth header**: `Authorization: Bearer <token>`
- **Transport**: HTTP streamable

If mcporter lacks support for a specific feature, open an issue in the [mcporter repository](https://github.com/steipete/mcporter).

### Other MCP clients

The general pattern is:

1. Use `mcp-remote` as the transport bridge.
2. Point it at the Home Assistant MCP endpoint.
3. Pass the `Authorization: Bearer <token>` header.
4. Use `--transport http-only` and `--allow-http` for local HTTP, or omit `--allow-http` for HTTPS.

Consult your client's documentation for the exact configuration format.

## Step 5 — Verify the Connection

Once configured, verify the connection by asking your agent to:

1. **List available tools** — you should see tools exposed by the integration (e.g. `selora_get_home_snapshot`, `selora_list_automations` for Selora AI).
2. **Run a smoke test** — ask: *"Get a snapshot of my home"*. This should return an overview of your Home Assistant setup.

If tools are not listed or the call fails, check:
- The token is valid and not expired.
- The endpoint URL is correct and reachable from the client.
- The `Authorization` header is being passed correctly.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `401 Unauthorized` | Invalid or expired token | Create a new long-lived token in HA |
| Connection refused | HA not running or wrong host/port | Verify HA is accessible at the configured URL |
| Timeout | Network/firewall blocking | Check firewall rules; use a tunnel for remote access |
| Tools not listed | Integration not installed | Install an MCP integration on Home Assistant |
| `ERR_SSL_PROTOCOL_ERROR` | Using HTTPS URL without a valid cert | Use a proper tunnel (Cloudflare, SeloraBox) or `--allow-http` for local HTTP |

## Next Steps

With the MCP connection established, install skills specific to your integration for guided usage. For Selora AI, the `selora-mcp` skill (shipped with the [integration](https://selorahomes.com/docs/selora-ai/installation/)) provides guided interaction with automation management, home analysis, and proactive suggestions.
