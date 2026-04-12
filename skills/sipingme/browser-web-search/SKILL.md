---
name: browser-web-search
description: 把任何网站变成命令行 API。17 平台 37 命令 — 头条、小红书、知乎、B站、澎湃、腾讯、网易、新浪、微博等。专为 OpenClaw 设计，复用浏览器登录态。
version: 0.3.7
author: Ping Si <sipingme@gmail.com>
type: cli
requires:
  runtime:
    - name: node
      version: ">=18.0.0"
      description: Node.js 运行时
    - name: npm
      description: Node.js 包管理器（随 Node.js 安装）
  packages:
    - npm: browser-web-search
      global: false
  binaries:
    - name: openclaw
      description: OpenClaw CLI，用于浏览器自动化
install:
  command: npx --yes browser-web-search@0.3.7
  riskLevel: high
  riskReason: 通过 npx 动态拉取并执行第三方 npm 包，该包会在浏览器页面上下文中执行 JavaScript，可访问站点认证数据。存在供应链风险，使用前请审计源码。
  requiresApproval: true
  source:
    registry: npmjs.com
    package: browser-web-search
    repository: https://github.com/sipingme/browser-web-search
    npm: https://www.npmjs.com/package/browser-web-search
  verification:
    - 安装前请审查 GitHub 仓库代码
    - 检查 npm 包的下载量和维护状态
    - 对比 npm 发布版本与 GitHub 源码是否一致
  note: 此 Skill 仅包含使用说明，运行时行为完全取决于外部 npm 包
capabilities:
  sensitive:
    - type: browser-session-access
      riskLevel: high
      description: 通过 OpenClaw 在已认证的浏览器标签页中执行 JavaScript
      scope: 按 adapter 域名隔离（如 zhihu.com, xiaohongshu.com）
      access:
        - 当前页面 DOM
        - 当前页面 Session（继承，非提取）
        - 站点认证数据（登录态下的 API 响应）
        - 账户保护页面内容（如私信、收藏、个人资料）
      noAccess:
        - 浏览器 Cookie 文件（不直接读取）
        - 其他域名数据
        - 用户配置目录
      risks:
        - 第三方 npm 包（browser-web-search）在页面上下文中执行，可访问站点认证数据
        - 恶意代码可能窃取 cookies 或页面内容
        - 包代码不包含在此 Skill 中，需独立审计
      mitigations:
        - adapter 脚本开源可审计
        - 按域名隔离，无法跨站访问
        - 不持久化存储任何凭证
  privacyNotice:
    summary: 此 Skill 自动复用浏览器登录态，可读取您已登录站点的任何可见数据
    details:
      - 零配置意味着 CLI 自动获得您在 OpenClaw 浏览器中的登录会话访问权
      - 可读取账户保护的页面（私信、收藏、个人资料、订单等）
      - 访问范围取决于您在目标站点的登录权限
      - 建议仅在信任 browser-web-search 包代码后使用
configPaths:
  - path: ~/.bws/
    required: false
tags:
  - browser
  - web-search
  - scraping
  - automation
  - ai-agent
repository: https://github.com/sipingme/browser-web-search-skill
package: https://github.com/sipingme/browser-web-search
npm: https://www.npmjs.com/package/browser-web-search
---

# Browser Web Search (BWS) Skill

把任何网站变成命令行 API，专为 OpenClaw 设计，复用浏览器登录态。

## 🏗️ 架构说明

```
OpenClaw/AI Agent
    ↓ (读取 Skill 配置)
browser-web-search-skill
    ↓ (调用 CLI)
bws 命令
    ↓ (OpenClaw Browser)
目标网站
```

## 🎯 项目特点

### 专为 OpenClaw 设计
- **零配置**：无需 Chrome Extension、无需 Daemon，开箱即用
- **深度集成**：直接使用 OpenClaw 浏览器，与其他 Skill 共享登录态
- **轻量精简**：核心代码仅 22KB，无运行时依赖

### 复用登录态
- **无需 API Key**：使用你在浏览器中的登录状态
- **绕过反爬**：请求来自真实浏览器，不会被封禁
- **隐私安全**：数据在本地处理，不经过第三方服务器

### AI Agent 友好
- **结构化输出**：所有命令返回 JSON，便于 AI 解析
- **jq 过滤**：内置 jq 支持，精确提取所需数据
- **错误提示**：清晰的错误信息和修复建议

## 📋 前置要求

### 安装 browser-web-search

```bash
# 通过 npx 动态执行（无需全局安装）
npx --yes browser-web-search@0.3.7 --version

# 或全局安装（可选）
npm install -g browser-web-search
```

### 验证安装

```bash
npx --yes browser-web-search@0.3.7 site list
```

## 🚀 快速开始

```bash
# 查看所有可用命令
bws site list

# 运行 adapter
bws zhihu/hot                      # 知乎热榜
bws xiaohongshu/search "旅行"       # 小红书搜索
bws bilibili/popular               # B站热门
bws weibo/hot                      # 微博热搜
```

## 📊 内置平台（17 个）

| 平台 | 说明 | 命令 |
|-----|------|-----|
| **今日头条** | 新闻资讯 | `toutiao/hot`, `toutiao/search`, `toutiao/feed` |
| **澎湃新闻** | 权威新闻 | `thepaper/hot` |
| **腾讯新闻** | 热点新闻 | `qqnews/hot` |
| **网易新闻** | 热点新闻 | `netease/hot` |
| **新浪新闻** | 门户新闻 | `sina/hot` |
| **微博** | 社交热搜 | `weibo/hot` |
| **微信公众号** | 公众号文章 | `weixin/search`, `weixin/article` |
| **小红书** | 生活分享 | `xiaohongshu/search`, `xiaohongshu/note`, `xiaohongshu/comments`, `xiaohongshu/feed`, `xiaohongshu/me`, `xiaohongshu/user_posts` |
| **36kr** | 科技创投 | `36kr/newsflash`, `36kr/search`, `36kr/article` |
| **知乎** | 问答社区 | `zhihu/hot`, `zhihu/search`, `zhihu/question`, `zhihu/me` |
| **CSDN** | 开发者社区 | `csdn/search` |
| **博客园** | 技术博客 | `cnblogs/search` |
| **Bilibili** | 视频弹幕 | `bilibili/popular`, `bilibili/trending`, `bilibili/ranking`, `bilibili/search`, `bilibili/video`, `bilibili/comments`, `bilibili/feed`, `bilibili/history`, `bilibili/me` |
| **BOSS直聘** | 招聘平台 | `boss/search`, `boss/detail` |
| **Baidu** | 百度搜索 | `baidu/search` |
| **Bing** | 必应搜索 | `bing/search` |
| **Google** | 谷歌搜索 | `google/search` |

## 🔧 标准操作流程 (SOP)

### 操作 1：查看可用命令

**场景**：用户想知道有哪些可用的 adapter

**命令**：
```bash
bws site list
```

**输出示例**：
```
zhihu/
  hot                  - Get Zhihu hot list
  search               - Search Zhihu
  question             - Get question details
  me                   - Get logged-in user info

xiaohongshu/
  search               - 搜索小红书笔记
  note                 - 获取笔记详情
  ...
```

---

### 操作 2：搜索 adapter

**场景**：用户想找特定平台的命令

**命令**：
```bash
bws site search bilibili
```

**输出示例**：
```
bilibili/popular       Get Bilibili popular videos
bilibili/search        Search Bilibili videos
bilibili/video         Get video details
...
```

---

### 操作 3：查看 adapter 详情

**场景**：用户想了解某个命令的参数

**命令**：
```bash
bws site info bilibili/video
```

**输出示例**：
```
bilibili/video - Get Bilibili video details by bvid

参数:
  bvid (required)      视频 BV 号

示例:
  bws site bilibili/video BV1xx411c7mD
```

---

### 操作 4：获取知乎热榜

**场景**：用户想获取知乎热门话题

**命令**：
```bash
bws zhihu/hot
```

**输出示例**：
```json
{
  "items": [
    {
      "title": "如何评价...",
      "url": "https://www.zhihu.com/question/...",
      "heat": "1234万热度"
    }
  ]
}
```

---

### 操作 5：搜索小红书

**场景**：用户想搜索小红书内容

**命令**：
```bash
bws xiaohongshu/search "旅行攻略"
```

**输出示例**：
```json
{
  "notes": [
    {
      "id": "abc123",
      "title": "云南旅行攻略",
      "author": "旅行博主",
      "likes": 1234
    }
  ]
}
```

---

### 操作 6：获取 B站热门视频

**场景**：用户想看 B站热门

**命令**：
```bash
bws bilibili/popular
```

**输出示例**：
```json
{
  "videos": [
    {
      "bvid": "BV1xx411c7mD",
      "title": "视频标题",
      "author": "UP主",
      "play": "100万",
      "like": "5万"
    }
  ]
}
```

---

### 操作 7：使用 jq 过滤

**场景**：用户只需要部分数据

**命令**：
```bash
# 只获取标题
bws zhihu/hot --jq '.items[].title'

# 提取特定字段
bws bilibili/popular --jq '.videos[] | {title, play}'
```

---

### 操作 8：获取微博热搜

**场景**：用户想查看微博热搜

**命令**：
```bash
bws weibo/hot
```

**输出示例**：
```json
{
  "count": 30,
  "items": [
    {
      "rank": 1,
      "title": "某某事件",
      "hot": 1234567,
      "url": "https://s.weibo.com/weibo?q=..."
    }
  ]
}
```

---

### 操作 9：搜索引擎搜索

**场景**：用户想使用搜索引擎

**命令**：
```bash
bws google/search "OpenClaw AI"
bws baidu/search "人工智能"
bws bing/search "machine learning"
```

---

## 🔧 技术架构：如何访问登录态

BWS **不直接读取**浏览器 Cookie 文件或用户配置文件。它通过 OpenClaw 提供的 API 与浏览器交互：

```
bws 命令
    ↓ 调用
openclaw browser evaluate <script>
    ↓ 在已打开的标签页中执行 JavaScript
目标网站（使用该标签页的登录态）
```

### 工作原理

1. **BWS 调用 OpenClaw CLI**：
   ```bash
   openclaw browser evaluate --domain "zhihu.com" "<adapter-script>"
   ```

2. **OpenClaw 在浏览器标签页中执行脚本**：
   - 找到匹配域名的已打开标签页
   - 或打开新标签页访问目标网站
   - 在页面上下文中执行 adapter 脚本

3. **脚本在页面中运行**：
   - 脚本以网页的身份运行（如同 DevTools Console）
   - 自动继承该页面的登录态（Cookie、Session）
   - 通过 DOM 操作或 fetch 获取数据

### 数据访问范围

| 访问内容 | 是否访问 | 说明 |
|---------|---------|------|
| 浏览器 Cookie 文件 | ❌ 否 | 不直接读取 `~/.config/chromium/Cookies` 等文件 |
| 用户配置目录 | ❌ 否 | 不访问 `~/.bws/` 以外的配置 |
| 其他网站数据 | ❌ 否 | 只能访问 adapter 指定的域名 |
| 当前页面 DOM | ✅ 是 | adapter 脚本在页面中执行 |
| 当前页面 Session | ✅ 是 | 继承页面的登录状态 |

### 安全边界

- **隔离性**：每个 adapter 只能访问其声明的 `domain`
- **透明性**：所有 adapter 代码是公开的 JS 文件，可审计
- **无持久化**：BWS 不保存任何 Cookie 或 Session Token
- **用户控制**：登录操作由用户在浏览器中手动完成

---

## ⚠️ 登录态管理

如果网站需要登录，命令会返回 401/403 错误。

**解决步骤**：

1. 在 OpenClaw 浏览器中打开网站：
   ```bash
   openclaw browser open https://xiaohongshu.com
   ```

2. 手动完成登录（BWS 不参与此过程）

3. 重试命令：
   ```bash
   bws xiaohongshu/me
   ```

**注意**：BWS 只是在已登录的页面中执行脚本，不会存储或传输你的登录凭证。

---

## 📝 输出格式

所有命令默认返回 JSON 格式：

**成功响应**：
```json
{
  "items": [...],
  "count": 10
}
```

**错误响应**：
```json
{
  "success": false,
  "error": "错误信息"
}
```

---

## 🎓 示例对话

**用户**：帮我看看知乎今天有什么热门话题

**AI**：好的，我来获取知乎热榜。

```bash
bws zhihu/hot
```

**AI**：以下是知乎热榜前 10：
1. 如何评价...（1234万热度）
2. 为什么...（890万热度）
...

---

**用户**：搜索一下小红书上关于"露营"的笔记

**AI**：好的，我来搜索小红书。

```bash
bws xiaohongshu/search "露营"
```

**AI**：找到以下相关笔记：
1. 《新手露营装备清单》- 点赞 5.2k
2. 《周末露营好去处》- 点赞 3.8k
...

---

## 🔒 安全性说明

- ✅ 所有操作在本地执行
- ✅ 使用 OpenClaw 浏览器的登录态
- ❌ 不会收集用户信息
- ❌ 不会上传到第三方服务器

---

## 📚 参考资料

- [项目 GitHub](https://github.com/sipingme/browser-web-search-skill)
- [browser-web-search 核心库](https://github.com/sipingme/browser-web-search)
- [npm 包](https://www.npmjs.com/package/browser-web-search)

---

## 📝 维护说明

- **版本**: 0.3.7
- **最后更新**: 2026-04-10
- **维护者**: Ping Si <sipingme@gmail.com>
- **许可证**: MIT

---

## ✅ 首次成功检查清单

新用户应该能在 2 分钟内完成：

- [ ] 安装工具：`npx --yes browser-web-search@0.3.7 --version`
- [ ] 查看命令：`npx --yes browser-web-search@0.3.7 site list`
- [ ] 测试运行：`npx --yes browser-web-search@0.3.7 zhihu/hot`
- [ ] 看到 JSON 输出

如果以上步骤都能顺利完成，说明 Skill 已正确配置！
