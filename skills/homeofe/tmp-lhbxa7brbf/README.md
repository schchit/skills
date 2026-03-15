# @elvatis_com/openclaw-ispconfig

**Current version:** 0.2.1

OpenClaw plugin to manage ISPConfig via the Remote JSON API.

## Features

- Session-based API client with auto-reconnect
- 31 tools for read, write, and one-command provisioning
- `/ispconfig` chat command for quick help and tool reference
- Safety guards via `readOnly` and `allowedOperations`
- Live integration tests against a real ISPConfig host (read-only)

## ISPConfig API format

This plugin uses the JSON endpoint format:

- URL: `https://server:8080/remote/json.php?method_name`
- Method is passed as query string, not in JSON body
- Body format:
  - login: `{ "username": "...", "password": "..." }`
  - normal calls: `{ "session_id": "...", ...params }`
  - logout: `{ "session_id": "..." }`

## Installation

### ClawHub

```bash
clawhub install openclaw-ispconfig
```

### npm

```bash
npm install @elvatis_com/openclaw-ispconfig
```

## ISPConfig setup

1. In ISPConfig, create a Remote User.
2. Grant required API permissions.
3. Copy endpoint URL and credentials.
4. Configure plugin in OpenClaw.

## Configuration

`openclaw.plugin.json` config keys:

- `apiUrl` (required): ISPConfig JSON API URL
- `username` (required): remote user
- `password` (required, secret): remote password
- `serverId` (default `1`): default server id
- `defaultServerIp` (optional): fallback IP for provisioning DNS A record
- `readOnly` (default `false`): block write tools
- `allowedOperations` (default `[]`): whitelist of tool names
- `verifySsl` (default `true`): TLS certificate verification

## Chat Command

### `/ispconfig`

Type `/ispconfig` in any connected chat to display the full list of available tools, the plugin version, and the connected ISPConfig hostname (credentials are never shown).

Example output:

```
🖥️ ISPConfig Plugin
Version 0.2.0 | Connected to isp.elvatis.com

📋 Read Commands
• isp_system_info — Server-Info
• isp_client_list — Alle Clients
...

✏️ Write Commands
• isp_client_add — Client anlegen
...

🚀 Provisioning
• isp_provision_site — Alles auf einmal (domain, clientName, clientEmail)
```

## OpenClaw Plugin API

This plugin uses the modern OpenClaw Plugin API (`api.*`) instead of the legacy `(runtime, config)` registration pattern.

The entry point exports a default plugin object with a `register(api)` function:

```ts
export default {
  manifest: pluginManifest,
  register(api: PluginApi): void {
    // Register tools
    api.registerTool({ name, description, parameters, execute });

    // Register chat commands
    api.registerCommand({ name, description, usage, handler });
  },
};
```

Key API methods used:

- `api.registerTool({ name, description, parameters, execute })` — exposes an AI-callable tool with JSON Schema parameters
- `api.registerCommand({ name, description, usage, handler })` — registers a `/command` for chat
- `api.pluginConfig` — typed plugin configuration from `openclaw.json`
- `api.logger` — structured logger (info, warn, error)

## Tools

### Read tools (15)

- `isp_system_info` — params: none
- `isp_methods_list` — params: none
- `isp_client_list` — params: optional filter fields
- `isp_client_get` — params: `client_id`
- `isp_sites_list` — params: optional filters accepted by `sites_web_domain_get`
- `isp_site_get` — params: `primary_id` (or `site_id`, `domain_id`)
- `isp_domains_list` — params: none
- `isp_dns_zone_list` — params: user-related filter params
- `isp_dns_record_list` — params: `zone_id`
- `isp_mail_domain_list` — params: optional filters
- `isp_mail_user_list` — params: optional filters
- `isp_db_list` — params: user-related filters
- `isp_ssl_status` — params: none
- `isp_quota_check` — params: `client_id`
- `isp_cron_list` — params: optional filters

### Write tools (15)

- `isp_client_add` — params: ISPConfig `client_add` payload
- `isp_site_add` — params: ISPConfig `sites_web_domain_add` payload
- `isp_domain_add` — alias for `isp_site_add`
- `isp_dns_zone_add` — params: ISPConfig `dns_zone_add` payload
- `isp_dns_record_add` — params: include `type` (`A`, `AAAA`, `MX`, `TXT`, `CNAME`) and matching payload
- `isp_dns_record_delete` — params: include `type` and matching delete payload
- `isp_mail_domain_add` — params: ISPConfig `mail_domain_add` payload
- `isp_mail_user_add` — params: ISPConfig `mail_user_add` payload
- `isp_mail_user_delete` — params: ISPConfig `mail_user_delete` payload
- `isp_db_add` — params: ISPConfig `sites_database_add` payload
- `isp_db_user_add` — params: ISPConfig `sites_database_user_add` payload
- `isp_shell_user_add` — params: ISPConfig `sites_shell_user_add` payload
- `isp_ftp_user_add` — params: ISPConfig `sites_ftp_user_add` payload
- `isp_cron_add` — params: ISPConfig `sites_cron_add` payload
- `isp_backup_list` — params: none (returns skipped if API method unavailable)

### Provisioning tool (1)

- `isp_provision_site`
- Required params:
  - `domain`
  - `clientName`
  - `clientEmail`
- Optional params:
  - `serverIp`
  - `createMail` (default `true`)
  - `createDb` (default `true`)
  - `serverId` (default from config)

Workflow:

1. Create client
2. Create site with SSL and Let's Encrypt enabled
3. Create DNS zone
4. Add DNS records (`A`, `CNAME`, SPF TXT, DMARC TXT)
5. Optionally create mail domain and `info@` + `admin@` mailboxes
6. Optionally create DB user and database
7. Ensure SSL flags are enabled on the site

**Total: 31 tools** (15 read + 14 write + 1 alias + 1 provisioning)

## Safety

- `readOnly=true` blocks all write and provisioning tools
- `allowedOperations=[...]` allows only named tools

## Roadmap

ISPConfig's Remote JSON API supports many more methods not yet covered by this plugin. Planned additions:

### Client Management
- `client_update` — update existing client fields
- `client_delete` — remove a client

### Website / Domain Management
- `sites_web_domain_delete` — delete a website
- `sites_web_domain_update` — update site config (internal helper exists, but no dedicated tool yet)

### Mail
- `mail_alias_add` / `mail_alias_delete` / `mail_alias_get` — mail aliases
- `mail_forward_add` / `mail_forward_delete` / `mail_forward_get` — mail forwards
- `mail_domain_delete` — remove a mail domain
- `mail_domain_update` — update mail domain settings

### DNS
- `dns_zone_delete` — remove a DNS zone
- `dns_zone_update` — update zone settings (TTL, SOA, etc.)
- `dns_a_update` / `dns_aaaa_update` / `dns_cname_update` / `dns_mx_update` / `dns_txt_update` — update individual DNS records (currently only add/delete is supported)

### Databases
- `sites_database_delete` — remove a database
- `sites_database_user_delete` — remove a database user

### FTP / Shell
- `sites_ftp_user_delete` — remove an FTP user
- `sites_shell_user_delete` — remove a shell user

### Cron
- `sites_cron_delete` — remove a cron job
- `sites_cron_update` — update an existing cron job

## Development

```bash
npm run build
npm test
```

For live tests, provide environment variables:

- `ISPCONFIG_API_URL`
- `ISPCONFIG_USER`
- `ISPCONFIG_PASS`

## Shared Template

For automation that creates GitHub issues, use `src/templates/github-issue-helper.ts`.
It provides `isValidIssueRepoSlug()`, `resolveIssueRepo()`, and `buildGhIssueCreateCommand()`.

## Changelog

### 0.2.1 (2026-03-15)

**Bug fix:** Resolve `"Cannot read properties of undefined (reading 'properties')"` crash in OpenClaw UI.

- **Added JSON Schema `parameters` to all 31 tool definitions** — previously tools only had `name`, `description`, and `run`, causing the UI to crash when accessing `tool.parameters.properties`
- **Fixed `registerViaApi()` to pass `parameters` through** to `api.registerTool()` — schemas were defined but never forwarded to OpenClaw
- **Changed tool registration from `run` to `execute`** — OpenClaw's plugin API expects `execute(params)`, not `run(params)`
- **Updated `BoundTool` interface** to include optional `parameters` field
- **Updated `ToolDefinition` interface** to include optional `parameters` field

### 0.2.0 (2026-03-07)

- Initial release with 31 tools, `/ispconfig` command, safety guards

## License

MIT
