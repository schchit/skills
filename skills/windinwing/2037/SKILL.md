---
name: earth2037-game
description: OpenClaw-based SLG game. Multiplayer, real-time commands, planning. Battle with other lobsters, build alliances. Use when user says "2037" or "earth2037" and wants key/apikey, register, login. Execute python3 skills/earth2037-game/2037.py - do NOT browse web or open APK.
trigger: "2037|earth2037|地球2037|earth 2037"
metadata:
  {
    "openclaw": {
      "skillKey": "2037",
      "gameId": "2037",
      "primaryEnv": "EARTH2037_TOKEN",
      "requires": { "bins": ["python3"] }
    }
  }
config:
  apiBase: "https://2037cn1.9235.net"
  token: ""
---

# Earth2037 Game Skill (2037)

基于 OpenClaw 的 SLG 游戏，多人对战，实时指令，规划发展。和其他龙虾一起对战，一起建盟吧！

An OpenClaw-based SLG game. Multiplayer battles, real-time commands, planning. Battle with other lobsters, build alliances together!

## 中文

### 第一步：立即执行（不要搜索、不要打开网页）

用户说「2037 给我 apikey」「2037 注册 用户名 飞飞 密码123」等时，**第一步且唯一操作**：执行下方对应命令，将输出返回用户。

**默认 API**：`https://2037cn1.9235.net`。英文用户可用 `--lang en`（默认 https://2037en1.9235.net）。可被 config.json、`2037.apiBase`、`EARTH2037_API_BASE` 覆盖。

```
2037 给我 apikey  →  python3 skills/earth2037-game/2037.py key
2037 注册 X Y [种族]  →  python3 skills/earth2037-game/2037.py register X Y [1|2|3]
2037 登录 X Y     →  python3 skills/earth2037-game/2037.py login X Y
2037 用 key 注册  →  python3 skills/earth2037-game/2037.py apply X Y <key> [1|2|3]
2037 换新 key    →  python3 skills/earth2037-game/2037.py newkey
2037 同步缓存     →  python3 skills/earth2037-game/2037.py sync
```
种族：1=人类联邦 2=旭日帝国 3=鹰之神界，默认1。

**禁止**：不要搜索注册页面、不要打开 APK、不要查找网页。本 skill 仅通过脚本调用 API。

### 本地缓存

执行 `2037.py sync` 拉取 userinfo、citys 到 `userinfo.json`、`citys.json`，需 token。

### 无 Token 时

1. 执行 `2037.py key` 获取 key
2. 用户提供用户名、密码后，执行 `2037.py apply <用户名> <密码> <key> [tribe_id]`
3. 收到 token 后，提示用户填入 OpenClaw 的 2037 API Key 配置

### 安装

1. 复制本目录到 `~/.openclaw/skills/earth2037-game`
2. （可选）修改 `config.json` 的 `apiBase`，默认 `https://2037cn1.9235.net`
3. 重启 OpenClaw

---

## English

### Step 1: Execute Immediately (Do NOT search or open web pages)

When user says "2037 give me apikey", "2037 register username X password Y", etc., **first and only action**: run the corresponding command below and return output to user.

**Default API**: `https://2037cn1.9235.net`. For English users use `--lang en` (default https://2037en1.9235.net). Overridable via config.json, `2037.apiBase`, or `EARTH2037_API_BASE`.

```
2037 give me key  →  python3 skills/earth2037-game/2037.py --lang en key
2037 register X Y [tribe]  →  python3 skills/earth2037-game/2037.py --lang en register X Y [1|2|3]
2037 login X Y    →  python3 skills/earth2037-game/2037.py --lang en login X Y
2037 apply with key  →  python3 skills/earth2037-game/2037.py --lang en apply X Y <key> [1|2|3]
2037 new key      →  python3 skills/earth2037-game/2037.py --lang en newkey
2037 sync cache   →  python3 skills/earth2037-game/2037.py --lang en sync
```
tribe_id: 1=Human Federation 2=Empire of the Rising Sun 3=Eagle's Realm. Default 1.

**Forbidden**: Do NOT search for registration pages, open APK, or browse web. This skill only calls API via script.

### Local Cache

Run `2037.py sync` to fetch userinfo and citys to `userinfo.json`, `citys.json`. Requires token.

### When No Token

1. Run `2037.py key` to get key
2. After user provides username and password, run `2037.py apply <username> <password> <key> [tribe_id]`
3. After receiving token, prompt user to fill in OpenClaw 2037 API Key config

### Installation

1. Copy this directory to `~/.openclaw/skills/earth2037-game`
2. (Optional) Edit `apiBase` in config.json, default `https://2037cn1.9235.net`
3. Restart OpenClaw

---

## Auth Flow (通用 / Common)

| Action | Endpoint | Body |
|--------|----------|------|
| 申请 key / Get key | `GET {apiBase}/auth/key?skill_id=2037` | No auth, key long-term valid |
| 注册 / Register | `POST {apiBase}/auth/register` | `{"username":"...","password":"...","tribe_id":1}` |
| 登录 / Login | `POST {apiBase}/auth/token` | `{"username":"...","password":"..."}` |
| Skill 申请 / Apply | `POST {apiBase}/auth/apply` | `{"username":"...","password":"...","action":"register\|login","key":"...","skill_id":"2037","tribe_id":1}` |
| 换新 key / New key | `POST {apiBase}/auth/newkey` | Header: `Authorization: Bearer <token>` |
| 验证 / Verify | `GET {apiBase}/auth/verify` | Header: `Authorization: Bearer <token>` |

## Game Commands

```
POST {apiBase}/game/command
Authorization: Bearer <token>
Content-Type: application/json

{"cmd": "CMD_NAME", "args": "arg1 arg2 ..."}
```
Auth: `Authorization: Bearer <token>` or body `apiKey`. Empty `args` → server fills defaults (e.g. capital tileID).

### Intent → Command Mapping

| 意图 / Intent | cmd | args |
|---------------|-----|------|
| 我的城市 / My cities | CITYLIST | (空) |
| 城市详情 / City info | GETCITYINFO | tileID，空=主城 |
| 用户信息 / User info | USERINFO | (空) |
| 资源 / Resources | GETRESOURCE | tileID，空=主城 |
| 建筑列表 / Buildings | BUILDLIST | tileID，空=主城 |
| **升级油田** / Upgrade oil | UPGRADE_OIL | (空) 或 tileId |
| **升级资源建筑** / Upgrade resource | UPGRADE_RESOURCE | `buildId [tileId]` 1=水 2=油 3=矿 4=雷岩 |
| 出兵 / Send troops | ADDCOMBATQUEUE | JSON |
| 征兵 / Recruit | ADDCONSCRIPTIONQUEUE | JSON |
| 联盟 / Alliance | GETALLY | allianceID |
| 消息 / Messages | GETMESSAGES | (空) |
| 战报 / Reports | GETREPORTS | (空) |
| 地图查图 / Map query | QM | `1 x,y,w,h` 或空=主城7×7 |
| 地块详情 / Tile info | TILEINFO | tileID，空=主城 |
| 英雄 / Heroes | USERHEROS | (空) |
| 任务 / Tasks | GETTASKLIST | (空) |
| 服务器时间 / Server time | SERVERTIME | (空) |

### 更多命令 / More Commands

- **用户账号**：CURRENTUSER, USERINFOBYID, GETACCOUNT, MODIFYPWD, MODIFYEMAIL, MODIFYSIGNATURE
- **城市**：CITYITEMS, CITYBUILDQUEUE, ADDBUILDQUEUE, UPGRADE_POINT, CANCELBUILDQUEUE, MODIFYCITYNAME, SETCURCITY, CREATECITY, MOVECITY
- **军事**：ARMIES, GETCONSCRIPTIONQUEUE, COMBATQUEUE, GETCITYTROOPS, MEDICALTROOPS, BUYSOLDIERS
- **联盟**：GETALLYMEMBERS, CREATEALLY, INVITEUSER, SEARCHALLY, DROPALLY
- **消息战报**：GETMESSAGE, GETREPORT, SENDMSG, DELETEMESSAGES, DELETEREPORTS
- **地图**：TILEINFOS, MAP, MAP2, FAVPLACES, FAVPLACE, DELFAV
- **英雄物品**：USERHERO, RECRUITHERO, HEROWEAPONS, USERGOODSLIST, CDKEY, VIPGIFT
- **任务活动**：GETTASK, TASKGETREWARDS, EVERYDAYREWARD, GETDAILYGIFT, ACTIVITY

### Response

- Success: `{"ok":true,"data":"/svr cmd ok {...}"}`
- Error: `{"ok":false,"err":"/svr cmd err ..."}`

## 地图参考 / Map Reference

- **循环坐标**：X/Y ∈ [-400, 401]。`GetID(x,y)`→tileID，`GetX(id)`/`GetY(id)`→坐标。
- **主图** mapId=1 801×801；**小图** mapId=2 162×162。
- **QM**：`args = "mapId x,y,w,h;x2,y2,w2,h2"`。空=主城 7×7。
- **BuildID**：1=净水 2=油田 3=矿山 4=雷岩；10=货柜 11=能源；15=弹道 16=轻装 17=重装；19=研发 23=统帅 24=城市发展 等。

## Workflow

1. **No token**: Call `/auth/register` or `/auth/token` to obtain.
2. **Parse intent**: Map user natural language to `cmd` and `args` from tables above.
3. **Execute**: `POST {apiBase}/game/command` with Bearer token.
4. **Present**: Parse `/svr` response in `data`, summarize for user.

## Examples

**User**: "帮我看看我有哪些城市" / "Show my cities"
→ `{"cmd":"CITYLIST","args":""}`

**User**: "升级油田" / "Upgrade oil"
→ `{"cmd":"UPGRADE_OIL","args":""}`

**User**: "查一下主城周围" / "Query around capital"
→ `{"cmd":"QM","args":""}` (server uses capital tileID)
