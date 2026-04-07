---
name: wechat-article-fetch
description: 微信公众号文章抓取技能。当用户发送微信文章链接（mp.weixin.qq.com/s/xxx）并表达"抓取"、"获取"、"保存"、"转成笔记"等意图时自动触发。使用 Playwright 渲染页面并提取文章标题、正文内容和原始 URL。
metadata:
  claudibot:
    emoji: "📖"
    category: "content-processing"
  requires:
    env: []
  files:
    - "scripts/*"
---

# 微信公众号文章抓取

## 功能

从微信公众号文章链接提取：
- 文章标题
- 正文内容（纯文本）
- 实际 URL（处理重定向后）

## 使用方式

```bash
node <skill-path>/scripts/wx-article-fetch.js "<url>"
```

## 返回值

JSON 格式：
```json
{
  "success": true,
  "title": "文章标题",
  "content": "正文内容...",
  "url": "https://mp.weixin.qq.com/s/xxx"
}
```

## 依赖

- Node.js 18+
- Playwright（**安装后需执行 `npm install` 安装依赖**）
- Chromium（Playwright 自动下载）

## 已知限制

| 限制类型 | 说明 |
|---------|------|
| 需微信登录 | 部分文章需授权，无法获取 |
| 付费内容 | 无法获取 |
| 私有公众号 | 无法获取 |
| 图片 | 目前只提取文本，图片保留原始 URL |

## 技术原理

使用 Playwright 启动无头 Chromium 浏览器，等待页面 JS 渲染完成后，从 `#js_content` 容器提取正文。

## 安全与隐私

**数据处理说明：**
- **纯本地执行**：所有抓取操作在本地浏览器完成，不上传任何数据到外部服务器
- **无外部 API**：不依赖任何第三方服务
- **数据存储**：抓取的内容仅存在于调用者的会话上下文中，不做任何持久化存储
- **隐私保护**：不获取、不存储、不传输任何微信账号信息或登录凭证

**安全特性：**
- Playwright 浏览器在 headless 模式下运行，无界面渲染
- 每次抓取独立浏览器实例，无状态残留
- 不执行任何 JavaScript 恶意代码（只提取文本内容）
