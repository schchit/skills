---
name: openclaw-threadsctl
description: Manage Threads accounts, OAuth connect URLs, drafts, and publishing through the local `threadsctl` CLI. Use when the user wants to post to Threads, create or approve drafts, connect a Threads account, or work with Threads safely without raw curl or direct HTTP requests.
---

# OpenClaw Threads via threadsctl

Use `threadsctl` as the default interface for Threads operations.

## Use when

- The user wants to publish to Threads
- The user wants to create, approve, or publish a draft
- The user wants to connect a Threads account
- The user wants to inspect accounts, stats, drafts, or published posts
- The user would otherwise need raw `curl` or direct HTTP requests

## Rules

1. Prefer `threadsctl` over raw `curl` or manual HTTP requests.
2. Support both workflows:
   - direct publish
   - draft-first
3. If the user says "post now", use direct publish.
4. If the user says "draft", "prepare", "queue", or wants review first, use draft flow.
5. If the account is unclear, ask which account label or ID to use.
6. Prefer account labels over raw account IDs when communicating with the user.
7. Use `--confirmed` only when the user clearly intends immediate publishing.
8. Show concise summaries of results and include IDs only when useful.
9. If a command fails, surface the real error and explain the likely next step.

## Commands

### Accounts

```bash
threadsctl accounts list
threadsctl accounts stats --account main-brand
```

### OAuth

```bash
threadsctl auth connect-url --label main-brand
```

### Drafts

```bash
threadsctl drafts list --account main-brand
threadsctl draft create --account main-brand --type text --text "Post content" --created-by "OpenClaw"
threadsctl draft create --account main-brand --type image --media-url "https://example.com/image.jpg" --text "Caption" --alt-text "Alt text" --created-by "OpenClaw"
threadsctl draft approve --id draft_xxx --approved-by "OpenClaw"
threadsctl draft publish --id draft_xxx --actor "OpenClaw"
```

### Direct publish

```bash
threadsctl publish text --account main-brand --text "Hello from Threads" --confirmed
threadsctl publish image --account main-brand --media-url "https://example.com/image.jpg" --text "Caption" --alt-text "Alt text" --confirmed
```

### Published posts

```bash
threadsctl published list --account main-brand
```

## Workflow

### Direct publish

Use when the user clearly wants an immediate post.

Example:

```bash
threadsctl publish text --account main-brand --text "Launching today" --confirmed
```

### Draft-first

Use when the user wants review, approval, or preparation before posting.

Example:

```bash
threadsctl draft create --account main-brand --type text --text "Launching today" --created-by "OpenClaw"
```

## Account connection

To connect a new Threads account:

1. Run:

```bash
threadsctl auth connect-url --label client-two
```

2. Return the generated URL to the user.
3. Tell the user to open it in a browser and complete OAuth.

## Do not

- Do not use raw `curl` when `threadsctl` supports the action.
- Do not invent account IDs.
- Do not silently switch accounts.
- Do not pass `--confirmed` unless immediate publishing is intended.
- Do not hide command errors.

## Output style

Prefer short result summaries such as:

- `Published successfully from main-brand.`
- `Draft created for second-brand.`
- `Could not publish because confirmation was not provided.`

## Additional resources

- See [examples.md](examples.md) for ready-to-copy scenarios.
