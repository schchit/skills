---
name: openclaw-feishu-base
description: Unified Feishu Base/Bitable management for OpenClaw. Use when you need to inspect Base schema, manage tables/fields, or query/create/update/delete records in Feishu Base/Bitable with existing Feishu credentials.
---

# OpenClaw Feishu Base

Use this plugin when working with **Feishu Base / Bitable** in OpenClaw.

## What it provides

A unified tool:

- `feishu_base`

Recommended actions include:

- `resolve_link`
- `list_bases`
- `find_table`
- `list_tables`
- `get_table`
- `get_record`
- `query_records`
- `create_records`
- `update_records`
- `upsert_records`
- `delete_records`
- `create_table`
- `rename_table`
- `delete_table`
- `create_field` (including linked fields via `link.table_id` / `link.table_name`, plus duplex links via `link.back_field_name`)
- `rename_field`
- `update_field`
- `delete_field`
- `list_folder`

## Best-use guidance

- Prefer **direct Base links** or explicit identifiers (`app_token`, `table_id`) when available.
- Discovery helpers are convenience features; direct link/token workflows are more reliable.
- Inspect schema before writing when field names are uncertain.
- Query/list before update when locating existing records.

## Safety

Destructive operations are supported but should be **disabled by default** unless explicitly needed.

Config flag:

- `allowDelete: false` (recommended default)

When deletion is disabled, destructive actions should be blocked:

- `delete_records`
- `delete_field`
- `delete_table`

## Requirements

- OpenClaw with Feishu channel configured
- valid Feishu credentials already present in OpenClaw config
- access to the target Base/Bitable resources

## Notes

- This plugin works best as a link-first / token-first Feishu Base tool.
- Some discovery flows depend on what Feishu APIs expose in the current tenant/account context.
- For field creation and schema mutation, prefer **serialized one-by-one writes**. Parallel field creation can hit Feishu-side limits and cause intermittent `400` failures.
- Credential resolution prefers explicit `account_id`, then active runtime/session account context when available, then runtime-injected `channels.feishu`, and finally persisted OpenClaw config from `OPENCLAW_CONFIG_PATH` or `~/.openclaw/openclaw.json` when some runtime paths do not inject Feishu config consistently.
