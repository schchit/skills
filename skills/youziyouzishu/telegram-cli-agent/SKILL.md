---
name: telegram-cli
description: Manage Telegram via tgctl CLI - login, send/forward/edit/delete/pin messages, search, list chats/members, join/leave groups, kick/invite users, block/unblock, send files, download media, start bots, create groups/channels, manage admins, translate messages, update profile, listen for messages. Use when user asks to interact with Telegram as a user account (not bot API).
---

# Telegram CLI (tgctl)

User-account-level Telegram management via tgctl CLI.

## First-Time Setup

If `tgctl` is not installed or TOOLS.md has no tgctl config, run the setup flow:

### Step 1: Install binary
```bash
curl -fsSL https://raw.githubusercontent.com/youzixilan/telegram-cli/main/scripts/install.sh | bash
```

### Step 2: Get API credentials
Ask the user to go to https://my.telegram.org → API Development → get `api_id` and `api_hash`.

### Step 3: Login
```bash
TELEGRAM_API_ID=<id> TELEGRAM_API_HASH=<hash> tgctl login
```
User enters phone number, auth code (digits only, no spaces), and optional 2FA password interactively.

**Important:** Auth codes must NOT be sent via Telegram (will be invalidated).

### Step 4: Save config to TOOLS.md
After login succeeds, append to workspace TOOLS.md:
```markdown
### tgctl (Telegram CLI)
- Binary: ~/.local/bin/tgctl
- Env: TELEGRAM_API_ID=<id> TELEGRAM_API_HASH=<hash>
- Session: ~/.tgctl/
```

## Prerequisites (after setup)

- `tgctl` binary installed (check: `which tgctl` or `~/.local/bin/tgctl`)
- `TELEGRAM_API_ID` and `TELEGRAM_API_HASH` from TOOLS.md
- Session persists in `~/.tgctl/<profile>/session.json`

## Commands

```bash
TELEGRAM_API_ID=<id> TELEGRAM_API_HASH=<hash> tgctl [--profile <name>] <command>
```

### Messaging
| Command | Description |
|---------|-------------|
| `send <chat> <msg>` | Send message |
| `forward <from> <to> <msg_id>` | Forward a message |
| `edit <chat> <msg_id> <text>` | Edit a message |
| `delete <chat> <msg_id>` | Delete a message |
| `pin <chat> <msg_id>` | Pin a message |
| `unpin <chat> [msg_id]` | Unpin message (or all) |
| `read <chat>` | Mark chat as read |
| `sendfile <chat> <file>` | Send file or image |
| `download <chat> <msg_id>` | Download media from message |
| `callback <chat> <msg_id> <data>` | Click inline keyboard button |
| `typing <chat>` | Send typing status |
| `translate <chat> <msg_id> <lang>` | Translate a message |

### Search & Browse
| Command | Description |
|---------|-------------|
| `chats [limit]` | List chats |
| `history <chat> [limit]` | Chat history |
| `search <query>` | Search chats and users |
| `search-msg <chat> <query>` | Search messages in chat |
| `contacts` | List contacts |
| `members <chat> [limit]` | List group/channel members |
| `chatinfo <chat>` | Get chat/user details |
| `commonchats <user>` | Common chats with user |
| `resolve <username>` | Resolve username to ID |
| `resolvephone <phone>` | Resolve phone to user |

### Group & Channel Management
| Command | Description |
|---------|-------------|
| `creategroup <title> <user1> [user2...]` | Create a group |
| `createchannel <title> [about]` | Create a channel |
| `join <link_or_username>` | Join group/channel |
| `leave <chat>` | Leave group/channel |
| `kick <chat> <user>` | Kick user |
| `invite <chat> <user>` | Invite user |
| `editadmin <chat> <user> [remove]` | Set/remove admin |
| `startbot <chat> <bot> [param]` | Start bot in chat |

### User & Account
| Command | Description |
|---------|-------------|
| `login` | Login (phone + code + optional 2FA) |
| `me` | Current user info |
| `updateprofile [--first n] [--last n] [--about t]` | Update profile |
| `setstatus <online\|offline>` | Set online status |
| `block <user>` | Block user |
| `unblock <user>` | Unblock user |
| `listen [--user id] [--chat id]` | Listen for messages |
| `logout` | Logout |

## Multi-Account (--profile)

```bash
tgctl --profile work login
tgctl --profile work me
```

## Chat ID Format

- **User**: Positive ID (e.g. `8568316820`)
- **Group/Channel**: Negative ID (e.g. `-3842028710`)
- **@username**: Use directly (e.g. `@BotFather`)

## Security

- Credentials in env vars only, never hardcode
- `~/.tgctl/` contains auth session — protect it
- Auth codes must not be sent via Telegram (will be invalidated)
