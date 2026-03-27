---
name: "cc-live-setup"
description: "This skill should be used when the user needs to create or configure a CC live streaming room via API, including room creation, authentication setup, and credential management."
---

# CC Live Setup Skill

This skill provides workflows for creating and configuring CC live streaming rooms through the HTTP API.

## When to Use This Skill

Use this skill when:
- User wants to create a new live streaming room on CC platform
- User needs to configure authentication for a live room
- User wants to manage CC API credentials

## Interactive Workflow

This skill works through conversation. Follow these steps in order:

### Step 1: Collect Credentials (Ask the User)

Ask: "请提供您的 CC 账户 ID 和 API 密钥"

If user already provided in conversation, skip this step.

### Step 2: Collect Room Name (Ask the User)

Ask: "直播间名称是什么？" (max 40 characters)

### Step 3: Collect Template Type (Ask the User)

Ask: "直播模板是什么？"

Provide options:
- **1** - 纯视频模板
- **2** - 视频+文档模板

### Step 4: Create Room

Use the `scripts/create_room.py` script with:
- userid
- api_key
- name
- templatetype (1 or 2)

### Step 5: Return Result & Notice

Present to user:
- Room ID
- Whether creation was successful
- Notice: "本直播间默认设置为免密码登录。如需调整登录方式，请登录云直播控制台设置。"

## Credentials

Get these from CC admin console:
- **Account ID (userid)**: Your CC account ID
- **API Key**: Secret key for THQS signature generation

## Authentication

All CC API requests require THQS (Time-based Hash Query String) signature authentication using MD5:

```python
import hashlib
import time
import urllib.parse

def get_thqs(params, api_key):
    l = []
    for k in params:
        k_encoded = urllib.parse.quote_plus(str(k))
        v_encoded = urllib.parse.quote_plus(str(params[k]))
        l.append('%s=%s' % (k_encoded, v_encoded))
    l.sort()
    qs = '&'.join(l)

    qftime = 'time=%d' % int(time.time())
    salt = 'salt=%s' % api_key
    qf = qs + '&' + qftime + '&' + salt

    hash_value = hashlib.new('md5', qf.encode('utf-8')).hexdigest().upper()

    return qs + '&' + qftime + '&hash=' + hash_value
```

## Create Live Room

### API Endpoint
```
GET https://api.csslcloud.net/api/room/create
```

### Parameters
- userid, name, desc, templatetype, authtype, publisherpass, assistantpass, time, hash

### Template Types
| Value | Description |
|-------|-------------|
| 1 | 纯视频模板 |
| 2 | 视频+文档模板 |

### Default Settings
- authtype: 2 (免密码登录)

## Reference Files

- `references/api_docs.md`: Full API documentation reference
- `scripts/create_room.py`: Python script for room creation
