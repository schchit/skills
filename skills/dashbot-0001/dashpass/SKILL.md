---
name: dashpass
version: "0.7.0"
description: >
  Encrypted credential vault on Dash Platform for AI agents.
  Store and retrieve API keys, tokens, and passwords — encrypted on-chain, decryptable only by you.
  Triggers on: credential management, password vault, API key storage, secret store, Dash Platform credentials.
requires:
  env:
    - CRITICAL_WIF
    - DASHPASS_IDENTITY_ID
  bins:
    - node
  packages:
    - "@dashevo/evo-sdk@3.1.0-dev.1"
---

<!-- Safety: this file is documentation only — no executable code -->

# DashPass — Encrypted Credential Vault on Dash Platform

DashPass lets you store API keys, passwords, and other secrets **encrypted on the Dash blockchain**. Only someone with your private key can decrypt them — not the blockchain nodes, not your AI agent, not anyone else.

Your AI agent calls a CLI tool to store and retrieve credentials. Encryption happens locally *before* anything touches the network. The blockchain only ever sees ciphertext. Think of it as a password manager where the "cloud" is a decentralized blockchain.

## Why DashPass Instead of a `.env` File

| | `.env` file | DashPass |
|---|---|---|
| **Where secrets live** | Plain-text file on one machine | Encrypted on decentralized blockchain |
| **Disk failure** | Secrets gone (unless backed up) | Recoverable with your key |
| **Encryption** | None | AES-256-GCM per credential |
| **Rotation tracking** | Manual | Built-in version history |
| **Expiry alerts** | None | `check --expiring-within 7d` |
| **Multi-machine** | Copy file around (risky) | Any machine with your key |

---

## Quick Reference

```bash
CLI=skills/dashpass/scripts/dashpass-cli.mjs

# Store a credential
echo "sk-xxx" | node $CLI put --service anthropic-api --type api-key --level sensitive --label "Anthropic key" --value-stdin

# Retrieve a credential
node $CLI get --service anthropic-api --pipe

# List all credentials
node $CLI list

# Rotate to new value
echo "sk-NEW" | node $CLI rotate --service anthropic-api --value-stdin

# Check expiring credentials
node $CLI check --expiring-within 7d

# Vault status + credit balance
node $CLI status

# Delete a credential
node $CLI delete --service my-service

# Export as env vars (for eval)
eval $(node $CLI env --services anthropic-api,brave-search-api)
```

---

## When to Use DashPass

Activate this skill when the user or agent needs to:

- Store an API key, token, password, or other secret
- Retrieve a previously stored credential
- Rotate / update an existing credential
- Check which credentials are expiring
- List all stored credentials
- Delete a credential from the vault
- Export credentials as environment variables
- Check vault status or credit balance
- Discuss credential management strategy
- Compare DashPass with other secret storage approaches

---

## Agent Behavior Rules

1. **Never log or display decrypted values** unless the user explicitly asks. Use `--pipe` for programmatic access.
2. **Always use `--value-stdin`** (pipe) for `put` and `rotate`. Never use `--value` with literal secrets — it leaks to shell history.
3. **Never hardcode WIF or Identity ID** in scripts. They come from environment variables only.
4. **Wait 3-5 seconds** between consecutive write operations (put, rotate, delete) to the same Identity. Platform nonce timing constraint.
5. **Check `status` first** if any operation fails with credit or balance errors.
6. **Testnet only** — do not attempt mainnet operations unless the user explicitly authorizes.
7. **Treat `CRITICAL_WIF` as radioactive** — if it appears in conversation, immediately warn the user about exposure risk.

---

## First-Time Setup

If the user has not used DashPass before, read the setup guide:

```
Read {baseDir}/setup.md
```

---

## Detailed References

For full CLI command documentation (all parameters, examples, output formats):

```
Read {baseDir}/references/cli-commands.md
```

For encryption details, architecture diagrams, trust model, and security analysis:

```
Read {baseDir}/references/security-model.md
```

For troubleshooting common errors and known limitations:

```
Read {baseDir}/references/faq.md
```

For the prior security audit summary:

```
Read {baseDir}/references/security-analysis-summary.md
```

---

## Command → Reference Map

| Intent | CLI Command | Reference |
|--------|-------------|-----------|
| Store a secret | `put` | `{baseDir}/references/cli-commands.md` |
| Retrieve a secret | `get` | `{baseDir}/references/cli-commands.md` |
| List credentials | `list` | `{baseDir}/references/cli-commands.md` |
| Rotate a credential | `rotate` | `{baseDir}/references/cli-commands.md` |
| Check expiring | `check` | `{baseDir}/references/cli-commands.md` |
| Vault status | `status` | `{baseDir}/references/cli-commands.md` |
| Delete credential | `delete` | `{baseDir}/references/cli-commands.md` |
| Export as env vars | `env` | `{baseDir}/references/cli-commands.md` |
| How encryption works | — | `{baseDir}/references/security-model.md` |
| Error troubleshooting | — | `{baseDir}/references/faq.md` |
| First-time setup | — | `{baseDir}/setup.md` |
