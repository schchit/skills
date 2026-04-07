# 安装与配置

## 安装 CLI

```bash
npm install -g siluzan-tso-cli
```

环境要求：Node.js 18+

---

## 初始化 Skill 文件

```bash
siluzan-tso init -d /path/to-your/skills       # 写入自定义目录
```

使用 `init -d /path/to/skills`的方式，将skill复制到你的skill目录下

支持的 `--ai` 目标：
| 值 | 写入路径 |
|----|---------|
| `cursor` | `.cursor/skills/siluzan-tso/` |
| `claude` | `.claude/skills/siluzan-tso/` |
| `openclaw-workspace` | `skills/siluzan-tso/` |
| `openclaw-global` | `~/.openclaw/skills/siluzan-tso/` |
| `workbuddy-workspace` | `.workbuddy/skills/siluzan-tso/` |
| `workbuddy-global` | `~/.workbuddy/skills/siluzan-tso/` |
| `all` | 以上全部 |

---

## 首次登录 / 配置凭据

`siluzan-tso` 与 `siluzan-cso` **共用同一份凭据**，存储在 `~/.siluzan/config.json`，配置一次两个 CLI 均可使用。

```bash
siluzan-tso login                          # 交互式登录，按提示创建 API Key 后粘贴
siluzan-tso login --api-key <YOUR_API_KEY> # 直接设置 API Key（跳过交互）
siluzan-tso config set --api-key <Key>     # 或通过 config set 直接写入
siluzan-tso config set --token <Token>     # 备用：设置 JWT Token
```

API Key 获取入口：`https://www.siluzan.com/v3/foreign_trade/settings/apiKeyManagement`

---

## 查看当前配置

```bash
siluzan-tso config show
```
输出示例：
```
  构建环境     : production
  apiBaseUrl   : https://tso-api.siluzan.com
  googleApiUrl : https://googleapi.mysiluzan.com
  webUrl       : https://www.siluzan.com
  apiKey       : abcd****1234
```

`webUrl` 是前端页面基地址，需要引导用户打开网页时用此值拼接路径。

---

## 使用 webUrl 进行网页操作

- 涉及充值、账户激活、首页看板等**必须在网页完成**的操作时，应先通过 `siluzan-tso config show` 获取 `webUrl` 值，再按各业务文档提供的相对路径拼接完整链接，引导用户在浏览器中完成后续步骤。

## 更新

需要严格按照步骤执行
- 执行 npm install -g siluzan-tso-cli@[beta|latest]根据当前使用的是beta版本还是正式版本更新对应的版本到最新版
- 执行 siluzan-tso init -d /path/to/skills 复制项目中最新的skill文件来更新你的skill

---

## 修改其他配置

```bash
siluzan-tso config set --api-base <url>    # 切换 TSO API 地址
siluzan-tso config set --google-api <url>  # 切换 Google 网关地址
siluzan-tso config clear                   # 清空所有凭据
```

---
