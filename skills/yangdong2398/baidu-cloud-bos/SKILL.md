---
name: baidu-cloud-bos
description: >
  百度智能云对象存储(BOS)集成技能。当用户需要上传、下载、管理百度云存储文件，
  通过 Node.js SDK 脚本、Python SDK 脚本和 bcecmd 命令行工具管理。
---

# 百度智能云 BOS 技能

通过 Node.js SDK 脚本 + Python SDK 脚本 + bcecmd 工具管理百度智能云对象存储（BOS）。

## 首次使用 — 自动设置

当用户首次要求操作 BOS 时，按以下流程操作：

### 步骤 1：检查当前状态

```bash
{baseDir}/scripts/setup.sh --check-only
```

如果输出显示一切 OK（SDK 已安装、凭证已配置），跳到「执行策略」。

### 步骤 2：如果未配置，引导用户提供凭证

告诉用户：
> 我需要你的百度智能云凭证来连接 BOS 存储服务。请提供：
> 1. **AccessKeyId** — 百度云 AK
> 2. **SecretAccessKey** — 百度云 SK
> 3. **Endpoint** — BOS 服务端点（如 `bj.bcebos.com`、`gz.bcebos.com`、`su.bcebos.com`）
> 4. **Bucket** — 存储桶名称（如 `my-bucket`）
> 5. **StsToken**（可选） — 临时安全凭证的 SessionToken
>
> 你可以在 [百度智能云控制台 > 安全认证 > Access Key](https://console.bce.baidu.com/iam/#/iam/accesslist) 获取密钥，
> 在 [BOS 控制台](https://console.bce.baidu.com/bos/) 查看存储桶信息。
>
**Endpoint 对照表**：

| 区域 | Endpoint |
|------|----------|
| 北京 | `bj.bcebos.com` |
| 广州 | `gz.bcebos.com` |
| 苏州 | `su.bcebos.com` |
| 保定 | `bd.bcebos.com` |
| 香港 | `hkg.bcebos.com` |

### 步骤 3：用户提供凭证后，运行自动设置

```bash
{baseDir}/scripts/setup.sh --ak "<AccessKeyId>" --sk "<SecretAccessKey>" --endpoint "<Endpoint>" --bucket "<Bucket>"
```

脚本会自动：
- 检查并安装 `@baiducloud/sdk`（Node.js SDK）
- 检查并安装 `bce-python-sdk`（Python SDK）
- 检查 bcecmd 是否已安装
- 将凭证持久化到 `~/.config/openclaw/baidu-cloud-bos/credentials.json`（权限 600）
- 将凭证导出到当前 session 环境变量
- 配置 bcecmd（如已安装）
- 验证 BOS 连接

凭证读取优先级：**环境变量 > credentials.json 配置文件**。后续新 session 无需重新配置。

## 执行策略

三种方式按优先级降级，确保操作始终可完成：

1. **方式一：Node.js SDK 脚本**（优先） — 通过 `scripts/bos_node.mjs` 执行存储操作
2. **方式二：Python SDK 脚本** — 通过 `scripts/bos_python.py` 执行存储操作
3. **方式三：bcecmd 命令行** — 通过 shell 命令执行存储操作，支持目录同步

```
Node.js + @baiducloud/sdk 可用？
  ├─ 是 → 使用方式一（存储操作，JSON 输出，适合程序化处理）
  └─ 否 → Python + bce-python-sdk 可用？
              ├─ 是 → 使用方式二（存储操作，JSON 输出）
              └─ 否 → bcecmd 可用？（which bcecmd）
                        ├─ 是 → 使用方式三（存储操作 + 目录同步）
                        └─ 否 → 运行 setup.sh 安装
```

**判断方式一**：`node -e "require('@baiducloud/sdk')"` 成功则可用。
**判断方式二**：`python3 -c "import baidubce"` 成功则可用。
**判断方式三**：`which bcecmd` 有输出则可用。

---

## 方式一：Node.js SDK 脚本（优先）

> 官方文档: https://cloud.baidu.com/doc/BOS/s/Djwvyrhiw

当使用方式一时，通过 `scripts/bos_node.mjs` 执行存储操作。凭证读取优先级：环境变量 > `~/.config/openclaw/baidu-cloud-bos/credentials.json`。

支持的凭证来源：
- **环境变量**（优先）：`BCE_ACCESS_KEY_ID` / `BCE_SECRET_ACCESS_KEY` / `BCE_BOS_ENDPOINT` / `BCE_BOS_BUCKET`（必需），`BCE_STS_TOKEN`（可选，临时凭证）
- **配置文件**（回退）：`~/.config/openclaw/baidu-cloud-bos/credentials.json`

### 常用命令

> 以下省略 `node {baseDir}/scripts/bos_node.mjs` 前缀。完整格式：`node {baseDir}/scripts/bos_node.mjs <action> [options]`

```bash
# 上传文件
upload --file /path/to/file.jpg --key remote/path/file.jpg

# 上传字符串内容
put-string --content "文本内容" --key remote/file.txt --content-type "text/plain"

# 下载文件
download --key remote/path/file.jpg --output /path/to/save/file.jpg

# 列出文件
list --prefix "images/" --max-keys 100

# 获取签名 URL
sign-url --key remote/path/file.jpg --expires 3600

# 查看文件信息（HEAD）
head --key remote/path/file.jpg

# 删除文件
delete --key remote/path/file.jpg

# 复制文件（同桶或跨桶）
copy --source-bucket <bucket> --source-key <key> --key <dest-key>

# 列出所有 Bucket
list-buckets
```

所有命令输出 JSON 格式，`success: true` 表示成功，退出码 0。

### 限制

仅支持单文件操作，**不支持**目录递归上传/下载/同步（请用方式三 bcecmd）。

---

## 方式二：Python SDK 脚本

> 官方文档: https://cloud.baidu.com/doc/BOS/s/Vjwvyrfs3

当方式一不可用时，通过 `scripts/bos_python.py` 执行存储操作。凭证读取优先级：环境变量 > `~/.config/openclaw/baidu-cloud-bos/credentials.json`。

支持的凭证来源（同方式一）：
- **环境变量**（优先）：`BCE_ACCESS_KEY_ID` / `BCE_SECRET_ACCESS_KEY` / `BCE_BOS_ENDPOINT` / `BCE_BOS_BUCKET`（必需），`BCE_STS_TOKEN`（可选）
- **配置文件**（回退）：`~/.config/openclaw/baidu-cloud-bos/credentials.json`

### 常用命令

> 以下省略 `python3 {baseDir}/scripts/bos_python.py` 前缀。

```bash
# 上传文件
upload --file /path/to/file.jpg --key remote/path/file.jpg

# 上传字符串内容
put-string --content "文本内容" --key remote/file.txt --content-type "text/plain"

# 下载文件
download --key remote/path/file.jpg --output /path/to/save/file.jpg

# 列出文件
list --prefix "images/" --max-keys 100

# 获取签名 URL
sign-url --key remote/path/file.jpg --expires 3600

# 查看文件信息
head --key remote/path/file.jpg

# 删除文件
delete --key remote/path/file.jpg

# 复制文件
copy --source-bucket <bucket> --source-key <key> --key <dest-key>

# 列出所有 Bucket
list-buckets
```

所有命令输出 JSON 格式，与方式一保持一致。

### 限制

仅支持单文件操作，**不支持**目录递归上传/下载/同步（请用方式三 bcecmd）。

---

## 方式三：bcecmd 命令行

> 官方文档: https://cloud.baidu.com/doc/BOS/s/kmcn3zrup

当方式一和方式二均不可用时使用。bcecmd 是百度云官方命令行工具，支持目录同步等高级功能。

### 首次配置

```bash
bcecmd --conf-path ~/.bcecmd configure \
  --access-key <AK> \
  --secret-key <SK> \
  --domain <Endpoint>
```

配置文件保存在 `~/.bcecmd/credentials` 和 `~/.bcecmd/config`。

### 常用命令

```bash
# 上传文件
bcecmd bos cp /path/to/file.jpg bos:/<bucket>/remote/path/file.jpg

# 上传目录（递归）
bcecmd bos cp /path/to/folder/ bos:/<bucket>/remote/folder/ --recursive

# 下载文件
bcecmd bos cp bos:/<bucket>/remote/path/file.jpg /path/to/save/file.jpg

# 下载目录（递归）
bcecmd bos cp bos:/<bucket>/remote/folder/ /path/to/save/ --recursive

# 列出文件
bcecmd bos ls bos:/<bucket>/images/

# 删除文件
bcecmd bos rm bos:/<bucket>/remote/path/file.jpg

# 递归删除目录
bcecmd bos rm bos:/<bucket>/remote/folder/ --recursive --yes

# 同步本地目录到 BOS
bcecmd bos sync /path/to/local/ bos:/<bucket>/remote/ --delete

# 同步 BOS 目录到本地
bcecmd bos sync bos:/<bucket>/remote/ /path/to/local/ --delete

# 查看文件元信息
bcecmd bos head bos:/<bucket>/remote/path/file.jpg

# 获取签名 URL（默认 1800 秒，-e 后直接跟秒数无空格）
bcecmd bos gen_signed_url bos:/<bucket>/remote/path/file.jpg -e3600

# 列出所有 Bucket
bcecmd bos ls

# 创建 Bucket
bcecmd bos mb bos:/<bucket>

# 删除 Bucket（必须为空）
bcecmd bos rb bos:/<bucket>
```

### 优势

- **目录同步**：`bcecmd bos sync` 支持增量同步、`--delete` 删除远端多余文件
- **递归操作**：`--recursive` 支持目录级别的上传/下载/删除
- **大文件**：自动分片上传
- **Bucket 管理**：创建/删除 Bucket

---

## 功能对照表

| 功能 | 方式一 Node.js SDK | 方式二 Python SDK | 方式三 bcecmd |
|------|:-:|:-:|:-:|
| 上传文件 | ✅ | ✅ | ✅ |
| 上传字符串/内容 | ✅ | ✅ | ❌ |
| 下载文件 | ✅ | ✅ | ✅ |
| 列出文件 | ✅ | ✅ | ✅ |
| 获取签名 URL | ✅ | ✅ | ✅ |
| 删除文件 | ✅ | ✅ | ✅ |
| 查看文件信息 | ✅ | ✅ | ✅ |
| 复制文件 | ✅ | ✅ | ✅（cp 命令） |
| 递归上传/下载目录 | ❌ | ❌ | ✅ |
| 目录同步（增量） | ❌ | ❌ | ✅ |
| Bucket 管理 | ✅（list） | ✅（list） | ✅（创建/删除/列表） |
| JSON 结构化输出 | ✅ | ✅ | ❌ |

## 使用规范

1. **首次使用先运行** `{baseDir}/scripts/setup.sh --check-only` 检查环境
2. **凭证不明文展示**：引导用户自行通过 setup.sh 或编辑配置文件设置
3. **所有文件路径**（`--key`/BOS 路径）为存储桶内的相对路径，如 `images/photo.jpg`
4. **bcecmd 路径格式**：`bos:/<bucket>/path/to/file`，注意 `bos:/` 前缀
5. **上传后主动获取链接**：上传完成后调用 `sign-url`（方式一/二）或 `gen_signed_url`（方式三）返回访问链接
6. **错误处理**：调用失败时先用 `setup.sh --check-only` 诊断环境问题
7. **大批量操作优先用 bcecmd**：目录同步、批量上传等场景推荐方式三
8. **方式一脚本源码**见 `scripts/bos_node.mjs`
9. **方式二脚本源码**见 `scripts/bos_python.py`
10. **API 参考文档**见 `references/api_reference.md`
