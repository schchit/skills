---
name: url2pdf-mk
description: |
  微信文章 / 网页抓取工具，将任意 URL 输出为含完整图片的 PDF 和 Markdown 文件。
  自动在桌面按当前日期创建目录，文件名使用文章发布日期 + 标题。
  当用户提到"网页转 PDF"、"保存微信文章"、"抓取网页内容"、"导出 PDF 和 Markdown"、
  "url2pdf"、"网页保存"、"url2pdf-mk"、"保存链接"、"离线阅读"、"网页存档"、"批量抓取"等时触发此技能。
---

# url2pdf-mk — 网页转 PDF + Markdown

> 一键将网页（尤其是微信文章）转换为可离线阅读的 PDF 和 Markdown 文档，完整保留排版、图片、样式。

---

## 🔒 安全说明（必读）

| 模式 | 命令 | Profile | 适用场景 |
|------|------|---------|----------|
| **隔离（推荐）** | `main.py --isolated <URL>` | 临时隔离 Profile，无 Cookie | 公开内容 |
| **默认** | `main.py <URL>` | 复用 Chrome 真实 Profile | 需登录态的微信文章 |

### 风险与缓解

| 风险项 | 说明 | 缓解措施 |
|--------|------|----------|
| Profile 复用 | 复用模式可访问 Chrome Cookie/登录态 | ✅ 抓取**公开内容一律用 `--isolated`** |
| CDP 远程调试 | 开启 Chrome DevTools 协议 | 仅监听 `127.0.0.1:9222~9232`（本机） |
| CDP Proxy | 创建本地代理守护进程 | 仅绑定 `127.0.0.1`，外网无法访问；WS 连接需 Token 验证 |
| 浏览器启动 | 可能复用已有浏览器窗口 | `--isolated` 模式始终启动独立实例 |
| sys.path | 仅添加本技能目录，不访问外部路径 | ✅ 已安全隔离 |
| pip 依赖 | 不再运行时自动安装 | ✅ 改为预装 + 报错提示 |

### 推荐规则

- **公开内容** → `--isolated`（无需登录，不影响浏览器会话）
- **需登录的内容** → 默认模式（确保浏览器已登录目标网站）

### ⚠️ 重要安全警告

1. **Cookie 和登录态访问**：默认模式会连接到你现有的 Chrome 实例，工具可以访问你的浏览器 cookies 和已登录的会话。**仅在你信任代码并需要抓取需登录的页面时使用默认模式**。

2. **临时文件**：脚本会在系统 temp 目录创建临时文件（xlsx、proxy state、pid 文件）。任务完成后会自动清理，但如需额外安全保障，可在任务结束后手动检查并删除 temp 目录中的相关文件。

3. **CDP 端口安全**：CDP 调试端口仅绑定 `127.0.0.1`（本机），外网无法访问。WebSocket 连接需要 Token 验证。

4. **不要以 root 运行**：建议以普通用户权限运行此工具。

5. **如需额外保证**：可在 VM 或 disposable 环境中运行，或修改 `browser_launcher.py` 强制仅使用隔离 profile。

---

## 用法

### 统一入口（推荐）

```bash
# 单篇
python3 scripts/main.py "https://mp.weixin.qq.com/s?__biz=..."

# 批量（多个 URL）
python3 scripts/main.py "https://url1" "https://url2" "https://url3"

# 批量（xlsx 文件）
python3 scripts/main.py /path/to/urls.xlsx

# 隔离模式（不使用登录态）
python3 scripts/main.py --isolated "https://..."
python3 scripts/main.py --isolated /path/to/urls.xlsx
```

### 智能路由

| 输入 | 处理方式 |
|------|----------|
| 1 个 URL | 单篇完整抓取（PDF + Markdown） |
| ≥2 个 URL | 批量抓取，Chrome 可用 → 浏览器版，否则 → HTTP 版 |
| xlsx 文件 | 根据内含 URL 数量自动路由 |

### xlsx 格式

| 列 | 内容 |
|----|------|
| B（第2列） | 文章标题 |
| C（第3列） | 发布日期 |
| F（第6列） | 文章 URL |

### 输出

```
~/Desktop/{当前日期}/
├── 2025-04-03_文章标题.md
└── 2025-04-03_文章标题.pdf
```

---

## 脚本说明

| 脚本 | 用途 |
|------|------|
| `main.py` | 统一入口，智能路由 |
| `scrape.py` | 单篇抓取，PDF + Markdown |
| `batch_scrape.py` | 批量浏览器版（需 Chrome） |
| `batch_http.py` | 批量 HTTP 版（无浏览器，仅 Markdown） |

---

## 环境

| 组件 | 要求 |
|------|------|
| Chrome / Chromium | 浏览器版（CDP）必需 |
| Python 3.7+ | 必需 |
| pip 依赖 | `websockets openpyxl requests reportlab`（**运行前预装，缺失时脚本会报错提示**） |

首次使用前请安装依赖：
```bash
pip install websockets openpyxl requests reportlab
```

---

## 已知限制

- 视频/音频：PDF 保留封面，Markdown 保留链接
- 微信小程序/互动组件：仅提取静态内容
- 反爬限制：HTTP 版可能失败，改用浏览器版

---

## 更新日志

### v1.0.8（2026-04-13）— 安全增强

- SKILL.md：新增**⚠️ 重要安全警告**章节，包含：
  - Cookie 和登录态访问警告
  - 临时文件安全说明
  - CDP 端口安全说明
  - 不要以 root 运行的建议
  - VM/disposable 环境运行建议
- main.py：临时文件清理添加日志输出，清理成功/失败都会提示

### v1.0.7（2026-04-13）— 文件名修复

- 批量抓取时，文件名（PDF + Markdown）现在使用**从网页提取的真实标题和日期**
- 修复了之前使用 xlsx 默认标题（如"文章1"）的问题
- `batch_scrape.py`：在提取网页内容后，用网页获取的真实标题覆盖 xlsx 中的标题

### v1.0.5（2026-04-13）— 安全修复

- 移除 `batch_http.py` 中的硬编码 xlsx 默认路径
- 所有脚本：pip 依赖从运行时 auto-install 改为**预装检查 + 报错提示**（安全加固）
- `batch_http.py` 新增系统目录路径安全校验
- SKILL.md：调整安全说明，`--isolated` 标记为公开内容首选

### v1.0.4（2026-04-13）

- 新增 `--isolated` 隔离模式参数
- 移除硬编码路径，必须提供 xlsx 路径
- 新增 `--output` 可指定输出目录
- 强化安全文档

### v1.0.1（2026-04-12）

- 新增批量抓取脚本
- 修复多项 bug
