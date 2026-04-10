---
name: nail-art-pinterest-scraper
description: Pinterest 美甲图片扒取技能。从 Pinterest 搜索页批量采集美甲图片，支持 MD5 排重、自动下载、防封策略。单页循环模式防止上下文爆掉。触发场景：用户说「采集 Pinterest 美甲图片」、「扒取美甲图」、「Pinterest 扒图」、「下载美甲图片」、「px」。
---

# Nail Art Pinterest Scraper

专注美甲图片的 Pinterest 扒图工作流。

## 工作流程

### 执行前确认
向用户展示完整流程，等待确认后再执行：
1. 打开 Pinterest 搜索页（关键词由用户提供）
2. 滚动加载获取 Pin 列表
3. 逐个点击 Pin 详情页，等待 random(2.1~4.8) 秒
4. 用 JS 提取主图 URL，原 URL 直接下载
5. 下载前查哈希库去重，下载后立即追加新哈希
6. 保存为 `F:\4.9nn\nail3_art_XXX.png`（序号连续）
7. 节奏：每张间隔 random(2.1~4.8) 秒，每 10-15 张深度休息 random(20~45) 秒
8. 完成后展示文件数量和列表

### 关键技术细节

**浏览器**：OpenClaw browser tool（profile=openclaw）

**图片提取 JS**：使用 `document.querySelector('img[src*="i.pinimg.com"]')?.src` 提取最大尺寸主图 URL

**下载**：PowerShell `Invoke-WebRequest`，必须携带 headers：User-Agent + Referer: https://www.pinterest.com/

**原 URL 直接下载**：提取到啥URL就下啥URL，禁止修改分辨率

**哈希库**：`F:\4.9nn\hashes.txt`，格式：`MD5HASH,filename`，每行一条

**防封铁律**：
- 单页循环：始终保持 1 个工作标签页，禁止新开标签页
- 随机间隔：random(2.1~4.8) 秒 + 每 10-15 张深度休息 random(20~45) 秒
- 浏览器仅在真正异常时重启（页面卡死/超时）

### 异常处理
- 403/AVIF → 直接跳过该 Pin，不重试
- 浏览器超时 → 重启 browser session

### 文件路径
- 图片保存：`F:\4.9nn\nail3_art_XXX.png`（序号连续不跳号）
- 哈希库：`F:\4.9nn\hashes.txt`

### 排重规则
- 下载前先查哈希库，命中则跳过不下载，不占序号
- 每完成一批，立即将新哈希追加写入哈希库
- 同一图片可能出现在不同 Pin 中，必须以内容哈希而非 Pin ID 排重
