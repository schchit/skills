---
name: creek-config
description: Configure Creek projects with creek.toml — render modes, build settings,
  resource bindings, environment variables, and custom domains. Use when the user
  asks about Creek configuration, creek.toml, bindings, env vars, or custom domains.
license: Apache-2.0
metadata:
  author: solcreek
  version: "1.0"
---

# Creek Configuration

Creek uses `creek.toml` for project configuration. Most fields are optional — Creek auto-detects framework and build settings from your project.

## creek.toml Reference

```toml
[project]
name = "my-app"              # Required. Lowercase alphanumeric + hyphens.
framework = "nextjs"         # Optional. Auto-detected from package.json.

[build]
command = "npm run build"    # Build command (default: npm run build)
output = "dist"              # Build output directory (framework-specific default)
worker = "worker/index.ts"   # Optional: custom Worker entry point

[resources]
d1 = true                   # Cloudflare D1 database
kv = true                   # Cloudflare KV namespace
r2 = true                   # Cloudflare R2 object storage
ai = true                   # Cloudflare Workers AI
```

## Render Modes

Creek automatically determines the render mode based on your framework and config:

### SPA (Single-Page Application)
- Vite-based frameworks: `vite-react`, `vite-vue`, `vite-svelte`, `vite-solid`
- Next.js with `output: "export"` in next.config
- Static HTML sites
- **Result**: Assets served from Cloudflare edge, no server component

### SSR (Server-Side Rendering)
- `nextjs`, `react-router`, `sveltekit`, `nuxt`, `solidstart`, `tanstack-start`
- **Result**: Server code runs in Cloudflare Workers, static assets on edge

### Worker
- When `[build] worker` is specified in creek.toml
- **Result**: Full Cloudflare Worker with access to all bindings

## Resource Bindings

Enable Cloudflare resources in `[resources]`:

| Resource | Type | Access in Worker |
|----------|------|-----------------|
| `d1` | SQLite database | `env.DB` |
| `kv` | Key-value store | `env.KV` |
| `r2` | Object storage | `env.BUCKET` |
| `ai` | AI models | `env.AI` |

Creek provisions per-tenant isolated instances automatically.

## Environment Variables

Manage secrets and config values that shouldn't be in code:

```bash
creek env set DATABASE_URL "postgres://..."
creek env ls                  # List all env vars
creek env ls --show           # Show values (hidden by default)
creek env rm DATABASE_URL     # Remove
```

Environment variables are encrypted at rest and injected at runtime.

## Custom Domains

```bash
creek domains add app.example.com       # Add domain
creek domains ls                        # List domains
creek domains activate app.example.com  # Activate after DNS setup
creek domains rm app.example.com        # Remove domain
```

See [DOMAINS.md](references/DOMAINS.md) for DNS configuration details.
