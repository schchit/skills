---
name: unipile-instagram-sdk
description: Instagram messaging and content via Unipile's official Node.js SDK. Send DMs, view profiles, list posts, create content, react and comment. Use for Instagram automation, reading/sending DMs, fetching profiles, getting posts, or interacting with content. Triggers: "instagram dm", "instagram message", "instagram profile", "instagram posts", "send instagram", "instagram api".
metadata:
  openclaw:
    requires:
      env:
        - UNIPILE_DSN
        - UNIPILE_ACCESS_TOKEN
      optionalEnv:
        - UNIPILE_PERMISSIONS
    primaryEnv: UNIPILE_ACCESS_TOKEN
    emoji: "📸"
    homepage: https://clawhub.ai/mohit21gojs/unipile-instagram-sdk
    source: https://clawhub.ai/mohit21gojs/unipile-instagram-sdk
---

# Unipile Instagram SDK

Instagram API via official [unipile-node-sdk](https://github.com/unipile/unipile-node-sdk) for messaging, profiles, posts, and interactions.

## ⚠️ Important Security Notes

**This skill uses Unipile, a third-party API service.** Your Instagram credentials and access tokens are sent to Unipile's servers, not directly to Instagram. Before using:

1. **Verify Unipile** — Review [unipile.com](https://unipile.com) and their privacy policy
2. **Audit the SDK** — The [unipile-node-sdk](https://github.com/unipile/unipile-node-sdk) is open source and auditable
3. **Use least privilege** — Set `UNIPILE_PERMISSIONS=read` unless you need write access
4. **Consider a dedicated account** — Use a separate Instagram account for automation

### Least Privilege

**Recommended:** Set `UNIPILE_PERMISSIONS=read` for read-only access.

```bash
# Safe: Read-only mode
UNIPILE_PERMISSIONS=read node scripts/instagram.mjs posts <account> nasa

# Only when you need to send messages or create posts
UNIPILE_PERMISSIONS=read,write node scripts/instagram.mjs send <chat_id> "Hello"
```

## Installation

### Install the Skill

```bash
# Using OpenClaw CLI
openclaw skills install unipile-instagram-sdk

# Or using ClawHub CLI
npx clawhub@latest install unipile-instagram-sdk
```

### Install Dependencies

After installing the skill, install the Node.js dependencies:

```bash
cd ~/.openclaw/workspace/skills/unipile-instagram-sdk
npm install
```

This installs `unipile-node-sdk@^1.9.3` from [npm registry](https://www.npmjs.com/package/unipile-node-sdk).

**Verify the SDK:**
```bash
npm info unipile-node-sdk
# Source: https://github.com/unipile/unipile-node-sdk
# License: MIT
```

## Setup

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `UNIPILE_DSN` | ✅ | API endpoint (e.g., `https://api34.unipile.com:16473`) |
| `UNIPILE_ACCESS_TOKEN` | ✅ | Token from [dashboard.unipile.com](https://dashboard.unipile.com) |
| `UNIPILE_PERMISSIONS` | Optional | `read`, `write`, or `read,write` (default: `read,write`) |

### Get Credentials

1. Sign up at [dashboard.unipile.com](https://dashboard.unipile.com)
2. Get your DSN and generate an access token
3. Connect an Instagram account via dashboard or API

### Client Initialization

```javascript
import { UnipileClient } from 'unipile-node-sdk';

const client = new UnipileClient(
  process.env.UNIPILE_DSN,
  process.env.UNIPILE_ACCESS_TOKEN
);
```

## Account Connection

```javascript
// Connect Instagram account
await client.account.connectInstagram({
  username: 'your_username',
  password: 'your_password',
});

// Hosted Auth (multi-user apps)
const link = await client.account.createHostedAuthLink({
  type: 'create',
  providers: ['INSTAGRAM'],
  success_redirect_url: 'https://yourapp.com/success',
});

// Handle 2FA
await client.account.solveCodeCheckpoint({
  account_id: accountId,
  provider: 'INSTAGRAM',
  code: '123456'
});
```

## Usage Examples

### Get Account ID (First Step)

All operations require an account ID. Get it first:

```javascript
const accounts = await client.account.getAll();
const instagram = accounts.items.find(a => a.type === 'INSTAGRAM');
const accountId = instagram.id;
```

### Profiles

```javascript
// Get any profile by username
const profile = await client.users.getProfile({
  account_id: accountId,
  identifier: 'nasa'
});

// Get your own profile
const me = await client.users.getOwnProfile(accountId);

// Get followers/following
const relations = await client.users.getAllRelations({
  account_id: accountId,
  limit: 100
});
```

### Posts

```javascript
// List posts from a user
const posts = await client.users.getAllPosts({
  account_id: accountId,
  identifier: 'nasa',
  limit: 10
});

// Get specific post
const post = await client.users.getPost({
  account_id: accountId,
  post_id: 'post_id'
});

// Create a post
await client.users.createPost({
  account_id: accountId,
  text: 'Check this out! 📸'
});

// React to a post
await client.users.sendPostReaction({
  account_id: accountId,
  post_id: 'post_id',
  reaction_type: 'like'  // 'heart', 'laugh', etc.
});

// Comment on a post
await client.users.sendPostComment({
  account_id: accountId,
  post_id: 'post_id',
  text: 'Amazing! 🔥'
});

// List comments
const comments = await client.users.getAllPostComments({
  account_id: accountId,
  post_id: 'post_id'
});
```

### Messaging (DMs)

```javascript
// List all chats
const chats = await client.messaging.getAllChats({
  account_type: 'INSTAGRAM',
  account_id: accountId,
  limit: 20
});

// Get messages from a chat
const messages = await client.messaging.getAllMessagesFromChat({
  chat_id: 'chat_id',
  limit: 50
});

// Send message to existing chat
await client.messaging.sendMessage({
  chat_id: 'chat_id',
  text: 'Hey! 👋'
});

// Start new chat
await client.messaging.startNewChat({
  account_id: accountId,
  attendees_ids: ['provider_id'],
  text: 'Hi, wanted to reach out...'
});
```

### Attachments

```javascript
import { readFile } from 'fs/promises';

const fileBuffer = await readFile('./photo.jpg');
await client.messaging.sendMessage({
  chat_id: 'chat_id',
  text: 'Check this out!',
  attachments: [['photo.jpg', fileBuffer]],
});
```

## CLI Tool

The skill includes a CLI for quick operations:

```bash
# Set environment
export UNIPILE_DSN="https://api33.unipile.com:16376"
export UNIPILE_ACCESS_TOKEN="your_token"

# Read operations
node scripts/instagram.mjs accounts
node scripts/instagram.mjs my-profile <account_id>
node scripts/instagram.mjs profile <account_id> <username>
node scripts/instagram.mjs posts <account_id> <username> --limit=5
node scripts/instagram.mjs chats --account_id=<id>
node scripts/instagram.mjs messages <chat_id> --limit=10

# Write operations (require UNIPILE_PERMISSIONS=write)
node scripts/instagram.mjs send <chat_id> "Hello"
node scripts/instagram.mjs start-chat <account_id> "Hi" --to=<provider_id>
node scripts/instagram.mjs create-post <account_id> "Post text"
node scripts/instagram.mjs comment <account_id> <post_id> "Nice!"
node scripts/instagram.mjs react <account_id> <post_id> --type=like
```

## Quick Reference

### Read Operations

| Task | Method |
|------|--------|
| List accounts | `client.account.getAll()` |
| Get profile | `client.users.getProfile({ account_id, identifier })` |
| Get own profile | `client.users.getOwnProfile(account_id)` |
| Get followers | `client.users.getAllRelations({ account_id })` |
| List posts | `client.users.getAllPosts({ account_id, identifier })` |
| Get post | `client.users.getPost({ account_id, post_id })` |
| List chats | `client.messaging.getAllChats({ account_type: 'INSTAGRAM', account_id })` |
| Get messages | `client.messaging.getAllMessagesFromChat({ chat_id })` |

### Write Operations

| Task | Method |
|------|--------|
| Create post | `client.users.createPost({ account_id, text })` |
| React | `client.users.sendPostReaction({ account_id, post_id, reaction_type })` |
| Comment | `client.users.sendPostComment({ account_id, post_id, text })` |
| Send DM | `client.messaging.sendMessage({ chat_id, text })` |
| Start chat | `client.messaging.startNewChat({ account_id, attendees_ids, text })` |

## Error Handling

```javascript
import { UnsuccessfulRequestError } from 'unipile-node-sdk';

try {
  await client.users.getProfile({ account_id, identifier });
} catch (err) {
  if (err instanceof UnsuccessfulRequestError) {
    const { status, type } = err.body;
    // type: 'errors/invalid_credentials', 'errors/checkpoint_error', etc.
  }
}
```

### Common Errors

| Type | Meaning | Action |
|------|---------|--------|
| `errors/invalid_credentials` | Wrong password | Reconnect account |
| `errors/checkpoint_error` | 2FA required | Call `solveCodeCheckpoint` |
| `errors/disconnected_account` | Session expired | Reconnect |
| `errors/resource_not_found` | Invalid ID | Verify exists |

## Limitations

- **No connection requests** — Instagram doesn't have LinkedIn-style invitations
- **Rate limits** — Implement backoff for bulk operations
- **Following API** — Requires raw data API (not in SDK convenience methods)

## Resources

- [SDK Repository](https://github.com/unipile/unipile-node-sdk)
- [Unipile Docs](https://developer.unipile.com/docs/list-provider-features)
- [Unipile Dashboard](https://dashboard.unipile.com)
