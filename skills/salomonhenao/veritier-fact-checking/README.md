# Veritier - Fact-Checking Skill for AI Agents

Real-time claim verification for any MCP-compatible AI agent. Veritier extracts every falsifiable statement from text and validates each one against live web evidence, returning a structured verdict, confidence score, and source URLs.

- **Free tier** - 25 claims/month, no credit card required
- **Homepage** - https://veritier.ai
- **Full docs** - https://veritier.ai/docs

---

## What this package contains

```
SKILL.md                    Agent instructions and tool reference (read this first)
scripts/
  veritier_mcp_proxy.py     Lightweight stdio proxy for local MCP connections
  veritier_mcp_test.py      Integration test to verify the proxy is working
```

---

## Quick Start

### Option A - Remote URL (recommended, no install)

Point your MCP client directly at the Veritier cloud endpoint. No Python, no proxy, no local setup.

```json
{
  "mcpServers": {
    "veritier": {
      "type": "http",
      "url": "https://api.veritier.ai/mcp/",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

Get your free API key at **https://veritier.ai/dashboard** (register first at https://veritier.ai/register).

---

### Option B - Local stdio Proxy

For MCP clients that require a local subprocess (stdio transport) instead of a remote HTTP connection.

**Prerequisites:** Python 3.10+, `pip install mcp httpx`

**1. Set your API key:**
```bash
# macOS / Linux
export VERITIER_API_KEY="vt_your_key_here"

# Windows (PowerShell)
$env:VERITIER_API_KEY = "vt_your_key_here"
```

**2. Configure your MCP client:**
```json
{
  "mcpServers": {
    "veritier": {
      "command": "python",
      "args": ["/absolute/path/to/scripts/veritier_mcp_proxy.py"],
      "env": {
        "VERITIER_API_KEY": "vt_your_key_here"
      }
    }
  }
}
```

**3. Verify it works:**
```bash
python scripts/veritier_mcp_test.py
```

Expected output:
```
✓ Initialize: server=veritier-proxy v1.0.0
✓ Tools discovered: ['verify_text']
✓ Verification result:

  Claim: 'The Eiffel Tower is located in Berlin.'
    Verdict: False
    Confidence: 1.0
    Explanation: The Eiffel Tower is located in Paris, France, not Berlin.
    Sources: https://...

✓ All checks passed! Your MCP integration is working correctly.
```

---

## The `verify_text` Tool

Once connected, your agent has access to one tool:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `text` | string | Yes | Any text containing claims to fact-check. Up to 2,000 characters. |

**Response:** One result object per claim extracted:

```
Claim: '<statement>'
  Verdict: true | false | null
  Confidence: 0.0-1.0
  Explanation: <plain-language rationale>
  Sources: <comma-separated evidence URLs>
```

| Verdict | Meaning |
|---------|---------|
| `true` | Supported by evidence |
| `false` | Contradicted by evidence |
| `null` | Insufficient evidence to determine |

---

## First-Time User Setup

Your agent can do all of this on your behalf:

1. **Register** at https://veritier.ai/register (free, no card)
2. **Confirm** the verification email
3. **Go to** https://veritier.ai/dashboard
4. **Click** "Mint New Key" — the key is shown once, copy it immediately
5. **Set `VERITIER_API_KEY`** in your MCP client environment config (see Option A or B above) - the key stays in your local config and is only ever sent to `api.veritier.ai`

---

## Plans

| Tier | Price | Claims/month | Req/min |
|------|-------|:---:|:---:|
| Free | $0 | 25 | 3 |
| Pro | $19.99/mo | 500 | 20 |
| Business | $249.99/mo | 10,000 | 60 |

Upgrade at https://veritier.ai/dashboard - takes effect immediately.

---

## Security

- API keys are prefixed `vt_` and SHA-256 hashed at rest - Veritier never stores the raw value
- Keys can be revoked at any time from the dashboard
- Only send your key to `https://api.veritier.ai`
- All inputs are screened by a content firewall before reaching the verification engine

---

## License

The scripts in this package are provided under the MIT License.
The Veritier API is a commercial service - see https://veritier.ai for terms.
