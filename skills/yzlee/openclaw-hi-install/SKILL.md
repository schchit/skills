---
name: openclaw-hi-install
description: Installs Hi into a local OpenClaw host through the official ClawHub path, then completes register, activate, receiver setup, and health checks through Hi's high-level install control tools.
compatibility: OpenClaw host setup skill. Use only when the host is OpenClaw and the user is installing Hi through ClawHub.
---

# OpenClaw Hi Install

This installs Hirey's agent platform, not Hi.Events.

## Use When

- the current host is OpenClaw
- the user wants to install or repair Hi on this OpenClaw host
- the user wants the official OpenClaw path that ends in a working Hi installation, not just a partially mounted MCP

## Do Not Use When

- the host is not OpenClaw
- the user wants a generic personal-agent install path rather than the OpenClaw ClawHub path
- the turn is only about using Hi after installation is already healthy

## Rules

- treat ClawHub as the canonical OpenClaw entrypoint; do not switch the user to a raw-skill or ad-hoc install path
- use the official Hi packages at the current pinned public release versions: `@hirey/hi-mcp-server@0.1.14` and, when local durable delivery is enabled, `@hirey/hi-agent-receiver@0.1.9`
- install the Hi npm packages into a user-writable vendor dir under `~/.openclaw/vendor/hi`; do not rely on `npm -g`, `sudo`, or any elevated install path
- mount `hi-mcp-server` from that vendor dir as a local `stdio` MCP child process
- for ordinary user installs, always set `HI_PLATFORM_BASE_URL=http://hi.hireyapp.us`; this public domain is the only supported default target, so do not ask the user to choose an environment or provide a URL
- keep `HI_MCP_TRANSPORT=stdio`
- keep `HI_MCP_PROFILE=openclaw-main` unless the user explicitly wants a different stable profile
- for the default OpenClaw profile, set `HI_MCP_STATE_DIR=~/.openclaw/hi-mcp/openclaw-main`; this must be the profile-scoped leaf directory, not the bare parent `~/.openclaw/hi-mcp`
- if the OpenClaw install uses a non-default Hi profile, the configured `HI_MCP_STATE_DIR` must still include that exact profile as the last path segment, e.g. `~/.openclaw/hi-mcp/<profile>`
- keep the install state in that stable profile-scoped directory so later turns can reuse the same identity and receiver config
- use `hi_agent_install` as the main path; do not make the user manually walk `register -> connect -> activate` unless you are diagnosing a lower-level break
- for OpenClaw, install with `host_kind="openclaw"` and enable `local_receiver`
- for local OpenClaw delivery, use `openclaw_hooks` with `http://127.0.0.1:18789/hooks/agent`
- for OpenClaw local vendor installs, do not explicitly pass `receiver_command="hi-agent-receiver"` or `receiver_command_argv=["hi-agent-receiver"]`; leave receiver startup unset so `hi_agent_install` picks the canonical local vendor binary, or pass the exact local vendor binary path via `receiver_command_argv` when you truly need an override
- when configuring OpenClaw hooks, keep `hooks.path="/hooks"`; `/hooks/agent` is the full agent endpoint under that base path, not the base path itself
- enable OpenClaw hook ingress with `hooks.enabled=true`; setting `hooks.path` or `hooks.token` alone is not enough because `/hooks/*` routes are only mounted when hooks are enabled
- OpenClaw hooks require a dedicated bearer token; generate a fresh random token for hooks, reuse that same token in the Hi receiver config, and never reuse the gateway auth token as `hooks.token`
- treat OpenClaw host prep and Hi registration as two phases: phase 1 installs packages and writes complete host config / MCP wiring; phase 2 starts only after the host is back and the current chat explicitly continues in plain language
- during phase 1, perform all OpenClaw host config writes in one blocking shell command; do not send any parallel tool calls while mutating host config
- during phase 1, use only OpenClaw's canonical config setters for host config persistence: `openclaw config set` / `openclaw config unset` for normal config paths and `openclaw mcp set` / `openclaw mcp unset` for MCP servers
- when using `openclaw mcp set`, pass exactly two positional arguments: the MCP server name and one complete JSON object value. Do not try field-by-field forms like `openclaw mcp set hi command ...`; the canonical shape is `openclaw mcp set hi '{"command":"<absolute-binary>","env":{...}}'`
- do not burn extra approval turns rediscovering `openclaw config set` / `openclaw mcp set` syntax from local `--help` or docs during an ordinary install; the canonical setter path and expected command shape are already specified here. Only inspect local help if an already-attempted canonical command actually fails and you are diagnosing that specific failure
- never patch `~/.openclaw/openclaw.json` directly with Python, Node, `jq`, `sed`, or any other raw file-edit path during OpenClaw host prep; that can leave runtime-looking state that does not persist in OpenClaw's canonical config model
- do not run `openclaw gateway restart` as a separate parallel tool call; if a restart is needed, make it the last step of phase 1 only after all config writes and validation succeed, then stop and resume in a new turn after reconnect
- after phase 1, do not call `hi_agent_install` until OpenClaw is reachable again and `openclaw mcp list` shows `hi`
- when allowing requested session keys, make sure `hooks.allowedSessionKeyPrefixes` includes both `hook:` and the active agent prefix; for the default main agent this should include at least `["hook:", "agent:main:"]`
- before calling `hi_agent_install`, always obtain the current chat's canonical full session key from a machine-readable OpenClaw host source and bind that current chat as the default Hi continuation route; never infer or copy it from `openclaw status`, `openclaw sessions`, or any TUI/header/footer/status text because those views can truncate the key
- if the host cannot provide the exact canonical full session key for the current chat, stop and explain that the install is not continuity-ready yet; do not declare a successful OpenClaw install with `continuity_not_ready`
- pass `host_session_key` and the best available reply target fields (`default_reply_channel`, `default_reply_to`, `default_reply_account_id`, `default_reply_thread_id`) together with `route_missing_policy="use_explicit_default_route"`; if no more specific reply target fields are available, `hi_agent_install` will normalize the OpenClaw default continuation channel to `last`
- when the host config supports it, also set `hooks.defaultSessionKey` / default continuation route to that same canonical current session; do not invent placeholder keys and do not leave ordinary installs in origin-capture-only mode once the canonical current session key is available
- continuity is not really ready unless OpenClaw allows requested session keys; verify `hooks.allowRequestSessionKey=true` and that Hi's session prefix policy is allowed before declaring the install healthy
- ask the user before permission prompts, auth prompts, or destructive reset steps
- if the install is broken, prefer `hi_agent_doctor`; if a clean reinstall is needed, use `hi_agent_reset` before rebuilding state

## User-Facing Wording

- never surface internal environment names like `early` / `prod` or raw config keys like `HI_PLATFORM_BASE_URL` to an ordinary user; translate the install target simply as Hirey's official default Hi service
- speak to ordinary OpenClaw users in plain language first; avoid leaving the user with raw terms like `continuity_not_ready`, `origin-capture-only`, `route_missing_policy`, `host_session_key`, or `default_reply_route` unless you immediately translate them into one short plain-language sentence
- before phase 1 starts, tell the user this install usually has two phases and may restart OpenClaw once; say that a restart during host prep is expected and does not mean the install failed, and that OpenClaw may briefly show its own reconnect text while the host comes back
- if OpenClaw shows its own reconnect text during that restart (for example `gateway restart` or `falling back to embedded`), translate it as normal host restart noise instead of a Hi install failure
- if ClawHub shows an extra safety confirmation for this Hirey install (for example a security review / suspicious warning / force-install prompt), explain in one short sentence that this is an extra registry warning and tell the user exactly how to continue, e.g. `reply yes and I'll continue`
- when a host-side command needs approval, issue the exact command first so OpenClaw generates a real approval request, then quote the actual `/approve ...` code. Never show a placeholder approval id or describe an approval code before the host has generated it
- do not run `git add`, `git commit`, or any other workspace-history mutation as part of ClawHub install or skill snapshot handling. Changes under `~/.openclaw/workspace` from installing `openclaw-hi-install` are ordinary local host state and must not be auto-committed during Hi install
- when phase 1 finishes, explicitly tell the user host prep is done, phase 2 has not started yet, and they should continue in the same chat after reconnect with a plain-language continuation such as `Continue the Hi install now` or `continue installing Hi`
- after install succeeds, explain in plain language that this chat has been bound as the default place future Hi messages come back to
- if the host cannot bind the current chat from a structured host source, explain plainly that the install is blocked until OpenClaw can provide the canonical full session key; do not ask the user whether to leave it unbound
- if OpenClaw surfaces terms like `continuity_not_ready` or `origin-capture-only`, translate them into a continuity blocker instead of treating them as acceptable install success

## Install Order

1. Treat Hirey's official default Hi service at `http://hi.hireyapp.us` as the only ordinary-user install target; do not ask the user to choose an environment or provide a URL.
2. Install or update the official Hi ClawHub skill/package and any required local package steps it asks for.
3. Phase 1 host prep: install the fixed Hi npm packages into `~/.openclaw/vendor/hi`, for example with `npm install --prefix ~/.openclaw/vendor/hi @hirey/hi-mcp-server@0.1.14 @hirey/hi-agent-receiver@0.1.9`, so the install stays user-local and does not require elevated exec.
4. Phase 1 host prep: in one blocking shell command, write the complete OpenClaw host config for Hi:
   - use `openclaw config set` / `openclaw config unset` / `openclaw mcp set` only; do not directly edit `~/.openclaw/openclaw.json`
   - mount `~/.openclaw/vendor/hi/node_modules/.bin/hi-mcp-server` as the local `stdio` MCP with explicit `HI_PLATFORM_BASE_URL=http://hi.hireyapp.us`, stable `HI_MCP_PROFILE`, and explicit `HI_MCP_STATE_DIR=~/.openclaw/hi-mcp/openclaw-main`
   - do not set `HI_MCP_STATE_DIR` to the bare parent `~/.openclaw/hi-mcp`; OpenClaw canonical state must live in the profile leaf dir so the MCP state file becomes `~/.openclaw/hi-mcp/openclaw-main/openclaw-main.json` and the receiver config stays colocated under that same leaf dir
   - if you need to enable OpenClaw hooks, set `hooks.enabled=true`, keep `hooks.path="/hooks"`, and keep the Hi receiver target at `http://127.0.0.1:18789/hooks/agent`; do not collapse those into one value
   - generate a fresh hooks token, set it on both OpenClaw hooks and the Hi receiver auth, make sure it is different from the gateway auth token, and set `hooks.allowedSessionKeyPrefixes` to include both `hook:` and the active agent prefix (normally at least `["hook:", "agent:main:"]`)
   - validate the config before any restart
   - verify canonical persistence before leaving phase 1: `openclaw config get hooks`, `openclaw mcp show hi`, and when needed direct readback of `~/.openclaw/openclaw.json` must all agree on the written `hooks` / `mcp` blocks, including the exact profile-scoped `HI_MCP_STATE_DIR`
5. End phase 1 only after that canonical persistence check passes and, if the host restarted, after the reconnect boundary. Tell the user the host prep phase is complete, that any OpenClaw reconnect text is expected host restart noise, and to continue the same chat after OpenClaw reconnects with a plain-language continuation; do not try to finish phase 2 in the same turn that changes host config.
6. Phase 2 only after reconnect: confirm OpenClaw is reachable again and `openclaw mcp list` shows `hi`.
7. Run `hi_agent_install` with:
   - `display_name`
   - `host_kind="openclaw"`
   - `enable_local_receiver=true`
   - `receiver_transport="claim"`
   - `receiver_start=true`
   - `host_adapter_kind="openclaw_hooks"`
   - the current OpenClaw hooks bearer token
   - and the current session as `host_session_key` plus the matching `default_reply_*` fields from a structured host source
   - if the host only exposes a display-layer channel like `webchat` but does not provide a concrete `to` / `account_id` / `thread_id`, treat that channel value as display-only and rely on `hi_agent_install` to normalize the default continuation channel to `last`
8. Also set `hooks.defaultSessionKey` / default continuation route to that same canonical current session; if the host cannot provide that canonical key, stop and report the continuity blocker instead of leaving it unset.
9. Run `hi_agent_doctor` and fix blockers before declaring success.

## Validation

- confirm `hi_agent_doctor` reports no blockers
- confirm `platform_base_url` is `http://hi.hireyapp.us` for ordinary-user installs
- confirm the installation is active
- confirm `delivery_capabilities` prefer `local_receiver`
- confirm the receiver config path is present and the delivery probe succeeds
- confirm the mounted `hi-mcp-server` binary comes from the user-local vendor dir and is version `0.1.14`, not an older global npm install
- if doctor reports `openclaw_hooks_base_path_misconfigured`, fix OpenClaw `hooks.path` back to `/hooks` before declaring the install healthy
- confirm `hooks.enabled=true`; otherwise `/hooks/agent` is never mounted and local receiver delivery will fail with `host_adapter_http_404`
- confirm `hooks.token` is different from the gateway auth token and that `hooks.allowedSessionKeyPrefixes` includes both `hook:` and the active agent prefix (normally at least `["hook:", "agent:main:"]`)
- confirm OpenClaw survived the phase-1 restart boundary and `openclaw mcp list` includes `hi` before attempting `hi_agent_install`
- confirm OpenClaw's canonical persistence layer really kept the host prep: `openclaw config get hooks`, `openclaw mcp show hi`, and `~/.openclaw/openclaw.json` should all still show the same `hooks` / `mcp` state after phase 1
- confirm `HI_MCP_STATE_DIR` is the profile leaf dir (default `~/.openclaw/hi-mcp/openclaw-main`), not the bare parent `~/.openclaw/hi-mcp`
- confirm `continuity_state` is `explicit_default_route_ready` and `default_reply_route` is populated; ordinary OpenClaw install is not done without this
- if doctor reports `openclaw_default_reply_route_session_key_invalid:*`, remove the bad default route and rebind it only from a structured OpenClaw source that returns the canonical full session key
- do not accept `continuity_not_ready` / origin-capture-only as successful OpenClaw install output

## Boundaries

- do not ask an ordinary OpenClaw user to fetch AWS credentials, CodeArtifact tokens, or any private registry access
- do not treat direct raw-skill install as the recommended OpenClaw path; OpenClaw should come from ClawHub
- do not ask an ordinary OpenClaw user to choose a Hi environment or provide a platform URL; this public install path must always use Hirey's official default Hi service at `http://hi.hireyapp.us`
- do not install Hi through a global npm prefix that needs elevated exec when a user-local vendor dir works
- do not try to complete OpenClaw host prep and `hi_agent_install` in the same turn when the host may restart; phase 2 must happen after reconnect
- do not tell the user you are already starting phase 2, switching to a new sub-session, or continuing Hi registration while phase 1 is ending; phase 1 must stop at the reconnect boundary and wait for the user's next continuation turn
- do not send `openclaw gateway restart` as a separate parallel tool call while host config is still being written
- do not omit `hook:` from `hooks.allowedSessionKeyPrefixes` when `hooks.defaultSessionKey` is still unset; current OpenClaw rejects that host config at startup
- do not declare phase 1 done just because `openclaw mcp list` or runtime status looks right; if the canonical config file does not retain `hooks` / `mcp`, phase 1 is still broken
- do not configure `HI_MCP_STATE_DIR` as the bare parent `~/.openclaw/hi-mcp`; always include the active profile as the last path segment
- do not copy session keys from `openclaw status`, `openclaw sessions`, or TUI display text; only structured host sources are valid for `host_session_key` / `hooks.defaultSessionKey`
- do not reuse the gateway auth token as the OpenClaw hooks token, and do not invent placeholder default session keys like `hook:ingress`
- do not ask an ordinary OpenClaw user whether to bind the current chat; bind it by default from a structured host source, and if that source is unavailable, stop with a continuity blocker instead of declaring success
