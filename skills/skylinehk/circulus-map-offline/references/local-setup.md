# Local setup

This skill is the portable local/offline sibling of the hosted `circulus-map` skill.

Use it when the package should stay inside a bundled or localhost workflow instead of depending on the public Workers deployment.

## Startup steps

From the repo root:

```bash
npm run dev
npm run mcp:dev
```

Expected local services:

- App: `http://127.0.0.1:3000`
- MCP health: `http://127.0.0.1:8788/health`
- MCP endpoint: `http://127.0.0.1:8788/mcp`

## Recommended local env vars

- `CIRCULUS_APP_BASE_URL=http://127.0.0.1:3000`
- `MCP_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000`

## Packaging note

Keep this skill separate from the hosted `skills/circulus-map/` package.

If you redistribute the offline bundle, keep the MCP URL pointed at a local worker unless you are intentionally repackaging it for another environment.
