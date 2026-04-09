---
name: tencent-agent-storage
description: |
  Cloud file storage, upload, backup, and file management tool for Tencent Agent Storage (专属云盘).
  Manages the user's personal cloud drive: upload files, list files, download, share links, preview, and backup.
  MUST trigger when the user mentions ANY of the following concepts:
  【云盘/网盘相关 — Cloud Drive Access】
  - "网盘", "云盘", "云空间", "龙虾盘", "龙虾云盘", "龙虾网盘", "龙虾空间"
  - "专属云盘", "专属网盘", "专属空间", "我的云盘", "我的网盘", "我的龙虾"
  - "打开网盘", "打开云盘", "进入网盘", "进入云盘", "看看云盘", "看看网盘"
  - "cloud drive", "my drive", "open drive", "lobster drive"
  【文件列表/查看 — File Listing & Browsing】
  - "列出文件", "有哪些文件", "看看文件", "文件列表", "我的文件"
  - "云盘里有什么", "空间里有啥", "查看云空间", "云空间文件"
  - "list files", "show files", "my files", "what files", "browse files"
  【上传/备份 — Upload & Backup】
  - "上传文件", "上传某个文件", "确定上传", "传到云空间", "上传到云空间"
  - "备份到云", "备份文件", "保存到云", "存到网盘", "传到网盘", "存到云盘", "传到云盘"
  - "文件传一下", "帮我传个文件", "把这个存一下"
  - "upload", "backup", "save to cloud", "back up"
  【发送/传输给用户 — Send & Deliver Files】
  - "把文件发给我", "整理好发我", "发到手机", "传到手机"
  - "做完了发我一份", "弄好了发给我", "完成后把文件给我"
  - "导出之后发我", "生成完发给我看看", "跑完了把结果给我"
  - "send file", "send to phone", "deliver file", "give me the file"
  【链接/分享 — Links & Sharing】
  - "生成下载链接", "做成链接", "给我下载链接"
  - "生成个链接发给同事", "发到群里", "分享文件", "分享给别人", "发个链接"
  - "download link", "share file", "share link", "generate link"
  【文件状态查询 — File Status Check】
  - "这个云文件还在吗", "之前上传的文件还能下吗", "链接过期了能重新生成吗"
  - "is file still there", "can I still download", "regenerate link"
  【隐式触发 — Implicit Triggers】
  - When a task produces output files (reports, exports, generated content) that need to be delivered to the user
  - When the user's intent implies needing a file on another device, even without explicitly saying "upload"
  - When MyClaw/agent needs to upload files to generate download links
  - Any mention of file transfer, cloud storage, or personal file space in the conversation context
metadata:
  openclaw:
    emoji: "☁️"
    requires:
      bins:
        - node
        - npm
      packages:
        npm:
          - smh-node-sdk
      env:
        - smh_libraryId
        - smh_accessToken
        - smh_spaceId
        - smh_basePath
---

# 云文件上传备份工具 (Tencent Agent Storage)

将本地文件上传至 Tecent Agent Storage，自动生成下载链接和图片预览。上传的文件存储在用户独有的云盘空间中，支持跨端访问——无论是手机、电脑还是平板，用户都可以随时随地查看和下载自己的文件。

## Setup

### Prerequisites

此 skill 依赖 `smh-node-sdk` npm 包。**必须在使用前完成安装**（二选一）：

```bash
# 方式一：全局安装（推荐）
npm install -g smh-node-sdk

# 方式二：本地安装到项目目录
npm install smh-node-sdk
```

> 脚本会按以下顺序查找 SDK：当前项目 node_modules → 全局 node_modules。如果未找到，脚本会报错并提示安装命令。

### About the upload script

此 skill 的运行脚本（`smh-upload.js`）完整内联在下方 **Script** 章节中。Agent 在首次执行时需将脚本内容写入 `/tmp/smh-upload.js`。脚本代码是此 skill bundle 的一部分，**不会从外部下载或动态生成**——其完整源码可在下方审阅。

### Credential configuration

脚本支持三种凭证模式（优先级从高到低）。

> **安全说明**：脚本仅读取配置文件中 `smh_` 前缀的环境变量（`smh_libraryId`、`smh_accessToken` 等），不会访问配置文件中的其他字段或敏感信息。

> **关于 token 权限**：Tencent Agent Storage 的文件上传和下载链接生成 API 要求 `space_admin` 级别的 accessToken，这是 Tencent Agent Storage 服务端对文件写入操作的最低权限要求。

**模式一：直接凭证（accessToken）**

在 `~/.openclaw/openclaw.json` 的 `env` 字段中配置：

```json
{
  "env": {
    "smh_basePath": "https://api.tencentsmh.cn",
    "smh_libraryId": "smhxxx-xxxxx",
    "smh_spaceId": "space-xxxxx",
    "smh_accessToken": "<your-access-token>"
  }
}
```

或在当前工作目录的 `.env` 文件中配置：

```env
smh_basePath=https://api.tencentsmh.cn
smh_libraryId=smhxxx-xxxxx
smh_spaceId=space-xxxxx
smh_accessToken=<your-access-token>
```


**模式二：命令行直接传参（临时覆盖，优先级最高）**

在每条命令的 JSON 参数中直接传入：

```json
{
  "basePath": "https://api.tencentsmh.cn",
  "libraryId": "smhxxx-xxxxx",
  "spaceId": "space-xxxxx",
  "accessToken": "<your-access-token>"
}
```

---

## Workflow

MyClaw uses this skill in any scenario that requires uploading files to the cloud.

### Complete flow

```
User triggers file upload
  → Step 1: Identify the local file path(s)
  → Step 2: Run upload script (loop for batch)
  → Step 3: Extract downloadUrl from JSON output (signed COS URL)
  → Step 4: Deliver the download link with execution notice
```

> **IMPORTANT**: 默认必须使用 `conflictStrategy: "ask"` 上传。这样当云端已存在同名文件时，脚本会返回错误，MyClaw 可以询问用户如何处理。**只有用户明确说了 "覆盖"/"替换" 或 "重命名" 时，才使用对应的 `conflictStrategy: "overwrite"` 或 `conflictStrategy: "rename"`。**

### Step 2: Upload

**Single file (默认):**

```bash
node /tmp/smh-upload.js upload '{"localPath":"/path/to/file.pdf","conflictStrategy":"ask"}'
```

**Upload to specific directory:**

```bash
node /tmp/smh-upload.js upload '{"localPath":"/path/to/photo.jpg","remotePath":"photos/photo.jpg","conflictStrategy":"ask"}'
```

**User explicitly requested overwrite:**

```bash
node /tmp/smh-upload.js upload '{"localPath":"/path/to/report.pdf","conflictStrategy":"overwrite"}'
```

**Batch upload:**

```bash
node /tmp/smh-upload.js upload '{"localPath":"/path/to/file1.pdf","conflictStrategy":"ask"}'
node /tmp/smh-upload.js upload '{"localPath":"/path/to/file2.docx","conflictStrategy":"ask"}'
```

#### Conflict handling

When using `conflictStrategy: "ask"` (默认), if a same-name file already exists, the script returns `{"success":false,"conflict":true}`. MyClaw must then ask the user:

> 云端已存在同名文件 `{filename}`，你想怎么处理？
>
> 1. 🔄 覆盖 — 替换云端文件
> 2. 📝 重命名 — 自动改名上传（如 file(1).pdf）
> 3. ❌ 取消 — 不上传

**三种策略对照：**

| Strategy | Behavior | When to use |
|----------|----------|-------------|
| `ask` (**默认，必须使用**) | 同名文件存在时返回错误，MyClaw 询问用户 | 用户未表明偏好时 |
| `overwrite` | 直接覆盖已有文件 | 用户明确说 "覆盖", "替换", "更新文件" |
| `rename` | 自动重命名 → `file(1).pdf` | 用户明确说 "重命名", "改名上传" |

### Step 4: Deliver link + execution notice

After every successful upload, include this notice alongside the download link(s):

> 链接已生成，链接有效期 2 小时，可直接在浏览器或手机中打开。

**Single file example:**

> 链接已生成，链接有效期 2 小时，可直接在浏览器或手机中打开。
>
> 已上传文件: report.pdf  大小: (2.3 MB)
> 下载链接: https://api.tencentsmh.cn/api/v1/file/smhxxx/space-xxx/report.pdf?access_token=acctk...&ContentDisposition=attachment&Purpose=download

**Batch example:**

> 链接已生成，链接有效期 2 小时，可直接在浏览器或手机中打开。
>
> 📎 report.pdf (2.3 MB) — https://api.tencentsmh.cn/api/v1/file/smhxxx/space-xxx/report.pdf?access_token=acctk...&ContentDisposition=attachment&Purpose=download
> 📎 photo.jpg (1.1 MB) — https://api.tencentsmh.cn/api/v1/file/smhxxx/space-xxx/photo.jpg?access_token=acctk...&ContentDisposition=attachment&Purpose=download

---

## File Size Support

**There is NO file size limit.** The upload script supports files of any size, including multi-GB videos.

- **Small files (≤ 50 MB)**: Single-part upload.
- **Large files (> 50 MB)**: Multipart upload — the file is read in 5 MB chunks, never loaded entirely into memory.

---

## Commands

所有命令输出 JSON 到 stdout。在执行前先将脚本写入 `/tmp/smh-upload.js`（见 **Script** 章节）。

### upload

```bash
node /tmp/smh-upload.js upload '<json>'
```

**JSON 参数：**
- `localPath`（必填）：本地文件绝对路径，支持 `~` 展开
- `remotePath`（可选）：云端目标路径，省略则上传到根目录并保留原文件名
- `conflictStrategy`（可选）：`ask`（默认）| `rename` | `overwrite`
- `basePath`（可选）：SMH API 地址，如 `https://api.tencentsmh.cn`，有此参数时走直接传参模式
- `libraryId`（可选）：媒体库 ID，直接传参模式必填
- `spaceId`（可选）：空间 ID，直接传参模式必填
- `accessToken`（可选）：SMH accessToken，直接传参模式必填

**Output:**

```json
{
  "success": true,
  "upload": {
    "localFile": "/path/to/photo.jpg",
    "remotePath": "photo.jpg",
    "fileSize": 2048576,
    "fileSizeHuman": "2.0 MB",
    "uploadTime": "3.2s",
    "rapidUpload": false
  },
  "downloadUrl": "https://api.tencentsmh.cn/api/v1/file/smhxxx/space-xxx/photo.jpg?access_token=acctk...&ContentDisposition=attachment&Purpose=download"
}
```

### info

```bash
node /tmp/smh-upload.js info '<json>'
```

**JSON 参数：**
- `remotePath`（必填）：云端文件路径
- `basePath` / `libraryId` / `spaceId` / `accessToken`（可选）：直接传参模式凭证

**Output:**

```json
{
  "success": true,
  "remotePath": "report.pdf",
  "downloadUrl": "https://api.tencentsmh.cn/api/v1/file/smhxxx/space-xxx/report.pdf?access_token=acctk...&ContentDisposition=attachment&Purpose=download",
  "fileInfo": {
    "name": "report.pdf",
    "size": 2048576,
    "type": "application/pdf",
    "creationTime": "2026-03-13T10:00:00Z",
    "modificationTime": "2026-03-13T10:00:00Z"
  }
}
```

### list

```bash
node /tmp/smh-upload.js list '<json>'
```

**JSON 参数：**
- `dirPath`（可选）：目录路径，默认 `/`
- `limit`（可选）：最大返回数量，默认 50
- `basePath` / `libraryId` / `spaceId` / `accessToken`（可选）：直接传参模式凭证

---

## Script

**在执行任何命令前，先将以下脚本写入 `/tmp/smh-upload.js`：**

```bash
cat > /tmp/smh-upload.js << 'SCRIPT_EOF'
#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');

// ==================== 加载 smh-node-sdk ====================

function loadSMHClient() {
  // 按优先级从项目本地和全局 node_modules 加载 smh-node-sdk
  const candidates = [
    () => require('smh-node-sdk'),
    () => {
      // 尝试全局 node_modules
      const { execSync } = require('child_process');
      const globalPath = execSync('npm root -g 2>/dev/null').toString().trim();
      return require(path.join(globalPath, 'smh-node-sdk'));
    },
  ];
  for (const load of candidates) {
    try { return load(); } catch (e) { /* 继续尝试下一个 */ }
  }
  throw new Error(
    'smh-node-sdk 未安装，请先运行：\n' +
    '  npm install -g smh-node-sdk\n' +
    '或：\n' +
    '  npm install smh-node-sdk'
  );
}

const { SMHClient } = loadSMHClient();

// ==================== 凭证加载 ====================

// 凭证优先级：
// 1. 命令行直接传参（args 中有 basePath + libraryId + spaceId + accessToken）
// 2. 配置文件直接凭证（openclaw.json smh 字段有 spaceId + accessToken）
function loadEnvConfig() {
  // 优先读取 .env 文件（当前工作目录）
  const dotEnvPath = path.join(process.cwd(), '.env');
  const envVars = {};
  if (fs.existsSync(dotEnvPath)) {
    const lines = fs.readFileSync(dotEnvPath, 'utf8').split('\n');
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) continue;
      const eqIdx = trimmed.indexOf('=');
      if (eqIdx === -1) continue;
      const key = trimmed.slice(0, eqIdx).trim();
      const val = trimmed.slice(eqIdx + 1).trim().replace(/^["']|["']$/g, '');
      envVars[key] = val;
    }
  }
  // 再读取 openclaw.json 的 env 字段（.env 优先级更高，已有的不覆盖）
  const cfgPath = path.join(os.homedir(), '.openclaw', 'openclaw.json');
  if (fs.existsSync(cfgPath)) {
    try {
      const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
      const envSection = cfg.env || {};
      for (const [k, v] of Object.entries(envSection)) {
        if (!(k in envVars)) envVars[k] = v;
      }
    } catch (e) { /* 解析失败忽略 */ }
  }
  return {
    basePath: envVars['smh_basePath'] || envVars['SMH_BASE_PATH'],
    libraryId: envVars['smh_libraryId'] || envVars['SMH_LIBRARY_ID'],
    spaceId: envVars['smh_spaceId'] || envVars['SMH_SPACE_ID'],
    accessToken: envVars['smh_accessToken'] || envVars['SMH_ACCESS_TOKEN'],
  };
}

async function resolveCredentials(args) {
  const { basePath, libraryId, spaceId, accessToken } = args;
  // 优先级 1：命令行直接传参
  if (basePath && libraryId && spaceId && accessToken) {
    return { host: basePath, libraryId, spaceId, accessToken };
  }
  // 读取环境配置（.env 或 openclaw.json env 字段）
  const smh = loadEnvConfig();
  const host = smh.basePath || 'https://api.tencentsmh.cn';
  const cfgLibraryId = smh.libraryId;
  if (!cfgLibraryId) {
    throw new Error('缺少 SMH 凭证，请在 ~/.openclaw/openclaw.json 的 env 字段或 .env 文件中配置 smh_libraryId');
  }
  // 优先级 2：配置文件直接凭证（有 spaceId + accessToken）
  if (smh.spaceId && smh.accessToken) {
    return { host, libraryId: cfgLibraryId, spaceId: smh.spaceId, accessToken: smh.accessToken };
  }
}

async function getDefaultSpaceId(client, libraryId, adminToken) {
  const res = await client.space.listSpace({
    libraryId,
    accessToken: adminToken,
    userId: '9527',
    page: 1,
    pageSize: 10,
  });
  const list = (res.data && res.data.list) || [];
  if (list.length === 0) throw new Error('没有可用的云存储空间，请先在管理后台创建空间');
  return list[0].spaceId;
}

// ==================== 工具函数 ====================

function expandHome(p) {
  if (!p) return p;
  if (p.startsWith('~/') || p === '~') return path.join(os.homedir(), p.slice(1));
  return p;
}

function formatSize(bytes) {
  if (!bytes) return '0 B';
  const u = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${u[i]}`;
}

function out(obj) { process.stdout.write(JSON.stringify(obj) + '\n'); }

// ==================== 命令处理 ====================

async function cmdUpload(args) {
  const { localPath, remotePath, conflictStrategy = 'ask' } = args;
  if (!localPath) return out({ success: false, error: '缺少必填参数 localPath' });

  const absLocal = expandHome(localPath);
  if (!fs.existsSync(absLocal)) return out({ success: false, error: `本地文件不存在: ${absLocal}` });
  const stat = fs.statSync(absLocal);
  if (!stat.isFile()) return out({ success: false, error: `路径不是文件: ${absLocal}` });

  const fileSize = stat.size;
  const fileName = path.basename(absLocal);
  const cloudPath = remotePath || fileName;

  const startTime = Date.now();
  const { host, libraryId, spaceId, accessToken } = await resolveCredentials(args);

  // 使用 SMHClient 创建上传任务（支持秒传、简单上传、分片上传）
  const client = new SMHClient({ basePath: host });
  let rapidUpload = false;

  try {
    const task = await client.createUploadTask({
      libraryId,
      spaceId,
      accessToken,
      filePath: cloudPath,
      localPath: absLocal,
      conflictResolutionStrategy: conflictStrategy,
      onProgress: (state, progress) => {
        if (progress > 0 && progress < 100) {
          process.stderr.write(`[上传进度] ${fileName}: ${progress}%\n`);
        }
      },
      onComplete: (response) => {
        rapidUpload = !!(response && response.rapidUpload);
      },
    });
    await task.start();
  } catch (err) {
    // 409 冲突
    const status = err && err.response && err.response.status;
    if (status === 409) {
      return out({ success: false, conflict: true, fileName, error: `云端已存在同名文件 "${fileName}"` });
    }
    return out({ success: false, error: `Upload failed: ${err.message}` });
  }

  const uploadTime = ((Date.now() - startTime) / 1000).toFixed(1) + 's';

  // 构建带 access_token 的 SMH 直链（302 跳转到带签名的 COS URL，可直接访问）
  const encodedCloudPath = cloudPath.split('/').map(encodeURIComponent).join('/');
  const downloadUrl = `${host}/api/v1/file/${libraryId}/${spaceId}/${encodedCloudPath}?access_token=${encodeURIComponent(accessToken)}&ContentDisposition=attachment&Purpose=download`;

  out({
    success: true,
    upload: { localFile: absLocal, remotePath: cloudPath, fileSize, fileSizeHuman: formatSize(fileSize), uploadTime, rapidUpload },
    downloadUrl,
  });
}

async function cmdInfo(args) {
  const { remotePath } = args;
  if (!remotePath) return out({ success: false, error: '缺少必填参数 remotePath' });

  const { host, libraryId, spaceId, accessToken } = await resolveCredentials(args);
  const client = new SMHClient({ basePath: host });

  let info;
  try {
    const res = await client.file.infoFile({
      libraryId,
      spaceId,
      filePath: remotePath,
      info: 1,
      accessToken,
    });
    info = res.data;
  } catch (e) {
    const status = e && e.response && e.response.status;
    if (status === 404) return out({ success: false, error: `云端文件不存在: ${remotePath}` });
    return out({ success: false, error: e.message });
  }

  // 构建带 access_token 的 SMH 直链（302 跳转到带签名的 COS URL，可直接访问）
  const encodedRemotePath = remotePath.split('/').map(encodeURIComponent).join('/');
  const downloadUrl = `${host}/api/v1/file/${libraryId}/${spaceId}/${encodedRemotePath}?access_token=${encodeURIComponent(accessToken)}&ContentDisposition=attachment&Purpose=download`;

  out({
    success: true, remotePath,
    downloadUrl,
    fileInfo: {
      name: path.basename(remotePath),
      size: info && info.size ? parseInt(info.size, 10) : null,
      type: (info && info.contentType) || '',
      creationTime: (info && info.creationTime) || null,
      modificationTime: (info && info.modificationTime) || null,
    },
  });
}

async function cmdList(args) {
  const { dirPath = '/', limit = 50 } = args;
  const { host, libraryId, spaceId, accessToken } = await resolveCredentials(args);
  const client = new SMHClient({ basePath: host });

  // 目录路径：根目录传空字符串
  const normalized = dirPath === '/' || dirPath === '' ? '' : dirPath.replace(/^\//, '');

  let data;
  try {
    const res = await client.directory.listDirectoryByPage({
      libraryId,
      spaceId,
      filePath: normalized,
      byPage: 1,
      page: 1,
      pageSize: Math.min(limit, 200),
      accessToken,
    });
    data = res.data;
  } catch (e) { return out({ success: false, error: e.message }); }

  const files = ((data && data.contents) || []).map((item) => ({
    name: item.name || '',
    type: item.type || 'file',
    size: item.size ? parseInt(item.size, 10) : null,
    sizeHuman: item.size ? formatSize(parseInt(item.size, 10)) : null,
    creationTime: item.creationTime || null,
    modificationTime: item.modificationTime || null,
    path: normalized ? `${normalized}/${item.name}` : item.name,
  }));

  out({ success: true, dirPath, total: (data && data.totalNum) || files.length, files });
}

// ==================== 入口 ====================

const [,, cmd, argsStr] = process.argv;
let args = {};
try { if (argsStr) args = JSON.parse(argsStr); } catch (e) { out({ success: false, error: `参数解析失败: ${e.message}` }); process.exit(1); }

const cmds = { upload: cmdUpload, info: cmdInfo, list: cmdList };
if (!cmds[cmd]) { out({ success: false, error: `未知命令: ${cmd}，支持: upload / info / list` }); process.exit(1); }

cmds[cmd](args).catch((e) => { out({ success: false, error: e.message }); process.exit(1); });
SCRIPT_EOF
```

---

## Full Example (macOS / Linux)

```bash
# Step 0: 安装 smh-node-sdk（首次使用前执行一次）
npm install -g smh-node-sdk

# Step 1: 写入脚本（每次会话执行一次即可）
cat > /tmp/smh-upload.js << 'SCRIPT_EOF'
# ... (脚本内容见上方 Script 章节)
SCRIPT_EOF

# Step 2: 获取父进程 ID（日志追踪）
PPID_VAL=$(python3 -c "import os; print(os.getppid())")
echo "[MyClaw] Parent PID: $PPID_VAL"

# Step 3: 上传文件
node /tmp/smh-upload.js upload '{"localPath":"/path/to/report.pdf","conflictStrategy":"ask"}'

# Step 4: 查询文件信息
node /tmp/smh-upload.js info '{"remotePath":"report.pdf"}'

# Step 5: 列出云端文件
node /tmp/smh-upload.js list '{"dirPath":"/","limit":20}'
```

---

## Error Handling

所有命令输出 JSON 到 stdout。错误也以 JSON 返回：`{"success": false, "error": "..."}`

| 错误 | 处理方式 |
|------|---------|
| 上传失败（`success: false`） | 告诉用户："文件上传失败：{具体原因}。你可以稍后再试，或者检查网络连接。" |
| 同名冲突（`conflict: true`） | 询问用户选择覆盖、重命名或取消 |
| 文件不存在 | 让用户确认路径 |
| 网络错误 | 重试 2 次，间隔 3s；仍失败告知用户 |
| 配置缺失 | 提示用户在 `~/.openclaw/openclaw.json` 的 `env` 字段或 `.env` 文件中添加 `smh_*` 配置 |

**上传失败 MyClaw 对话模板**（当 `success: false` 时必须使用）：

> ❌ 文件上传失败：{error 中的具体原因}。
>
> 你可以：
> 1. 🔄 重试 — 重新上传这个文件
> 2. ❌ 取消 — 暂时不上传

---

## 禁止行为

- **NEVER** 在 `success: false` 时展示下载链接
- **NEVER** 在上传失败时不告知用户，必须明确提示"文件上传失败"及原因
- **NEVER** 硬编码或暴露 SMH 凭证给用户
- **NEVER** 未经用户主动要求就上传其本地个人文件
- **NEVER** 跳过执行通知："链接已生成，有效期 2 小时，可直接在浏览器或手机中打开"
- **NEVER** 在用户未明确表态时使用 `conflictStrategy: "rename"` 或 `conflictStrategy: "overwrite"`

---

## 重要注意

- 用户说"上传文件"但没指定路径 → 追问："你要上传哪个文件？告诉我文件路径或文件名就行。"
- 用户说"确定上传 xxx"或"把 xxx 发给我" → 直接执行上传（`conflictStrategy: "ask"`）
- **同名文件冲突**：上传时必须使用 `conflictStrategy: "ask"`。如果返回 `conflict: true`，必须询问用户选择覆盖、重命名或取消
- 文件默认上传到云空间根目录，用户可通过 `remotePath` 参数指定目标路径
- 下载链接为带 `access_token` 的 SMH 直链（`${basePath}/api/v1/file/${libraryId}/${spaceId}/...?access_token=...&ContentDisposition=attachment&Purpose=download`），SMH 服务会 302 跳转到带签名的 COS URL，可直接在浏览器或手机中打开，**有效期与 accessToken 一致**
- 批量上传按顺序处理（不并行），避免 API 过载
- **执行通知**：每次上传完成后必须告知用户："链接已生成，有效期 2 小时，可直接在浏览器或手机中打开"
- `/tmp/smh-upload.js` 脚本在同一会话中只需写入一次，后续命令直接复用
