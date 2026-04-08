# 微信公众号排版与发布

> 让 AI 帮你写文章、排版并一键发布到微信公众号草稿箱

---

## 功能介绍

- 🤖 **AI 写作**：直接在对话中生成文章内容
- 🎨 **AI 封面图**：自动根据文章主题生成匹配的封面图
- 🎭 **专属模板**：使用你在平台创建的自定义排版模板
- 📤 **一键发布**：无需切换平台，直接发布到微信草稿箱
- 📱 **多账号支持**：可选择发布到哪个公众号
- 📊 **额度查询**：随时查看发布额度和公众号绑定情况

> ⚠️ **重要提示**：本技能仅使用你的自定义模板进行排版。如果你尚未创建自定义模板，请先在平台创建。

---

## 配置参数

| 参数名 | 类型 | 必填 | 说明 | 示例值 |
|--------|------|------|------|--------|
| `apiBaseUrl` | string | ✅ | SaaS 平台地址 | `https://open.tyzxwl.cn` |
| `apiKey` | secret | ✅ | API 密钥（从平台获取） | `wemd_xxxxxxxxxxxx` |

### 获取 API 密钥

1. 访问 https://open.tyzxwl.cn 并登录
2. 进入「个人中心」→「API Key」
3. 点击「生成新密钥」

### 绑定公众号

首次使用前需授权公众号：
1. 登录平台后点击「授权公众号」
2. 使用公众号管理员微信扫码授权

---

## API 接口

**Base URL**: `https://open.tyzxwl.cn`  
**鉴权方式**: Header `X-API-Key: {apiKey}`

### 1. 获取模板列表

```
GET /api/skill/templates
```

**Query 参数**（均可选）:
| 参数 | 说明 |
|------|------|
| `category` | 模板分类筛选 |
| `search` | 搜索关键词 |
| `page` | 页码，默认 1 |
| `limit` | 每页数量，默认 20 |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "list": [
      {
        "id": "tech-blue",
        "name": "科技蓝",
        "description": "渐变蓝色，适合技术/产品类文章",
        "category": "tech",
        "categoryName": "科技",
        "emoji": "💻",
        "isPremium": false,
        "isUserTemplate": false,
        "tags": ["科技", "产品", "技术"]
      }
    ],
    "userTemplatesCount": 2,
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 8,
      "totalPages": 1
    }
  }
}
```

**关于模板**:

本技能**仅使用用户自定义模板**（`isUserTemplate: true`），不使用系统内置模板。

如果模板列表中没有用户模板（`userTemplatesCount: 0`），需要引导用户先创建模板。

**创建自定义模板的方式**:

1. **模板设计器**：访问 https://open.tyzxwl.cn/website/template-designer.html 在线设计
2. **Fork 官方模板**：访问 https://open.tyzxwl.cn/website/template-market.html 选择喜欢的模板点击 Fork
3. **个人中心管理**：访问 https://open.tyzxwl.cn/profile.html?tab=templates 查看和管理你的模板

---

### 2. 获取模板分类

```
GET /api/skill/templates/categories
```

**响应示例**:
```json
{
  "success": true,
  "data": [
    { "id": "all", "name": "全部", "emoji": "📋" },
    { "id": "tech", "name": "科技", "emoji": "💻" },
    { "id": "business", "name": "商务", "emoji": "💼" },
    { "id": "life", "name": "生活", "emoji": "🌿" },
    { "id": "food", "name": "美食", "emoji": "🍜" },
    { "id": "education", "name": "教育", "emoji": "🎓" },
    { "id": "custom", "name": "自定义", "emoji": "✏️" }
  ]
}
```

---

### 3. 获取公众号列表

```
GET /api/skill/accounts
```

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "appId": "wx1234567890abcdef",
      "appName": "我的公众号",
      "appLogo": "https://...",
      "originalId": "gh_xxxxxxxx"
    }
  ]
}
```

---

### 4. 查询发布额度

```
GET /api/skill/quota
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "planName": "专业版",
    "publish": {
      "used": 15,
      "total": 100,
      "remaining": 85
    },
    "accounts": {
      "used": 2,
      "total": 5,
      "remaining": 3
    }
  }
}
```

---

### 5. 发布文章

```
POST /api/skill/publish
Content-Type: application/json
```

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `content` | string | ✅ | 文章内容（Markdown 格式） |
| `templateId` | string | ✅ | 模板 ID |
| `title` | string | ❌ | 文章标题（不填则从内容提取） |
| `accountId` | string | ❌ | 公众号 AppID（必须指定，多账号时不可省略） |
| `author` | string | ❌ | 作者名（默认使用公众号名称） |
| `digest` | string | ❌ | 文章摘要 |
| `coverImage` | string | ❌ | 封面图 URL |
| `contentSourceUrl` | string | ❌ | 阅读原文链接 |
| `autoGenerateCover` | boolean | ❌ | 是否 AI 生成封面（默认 true） |

**请求示例**:
```json
{
  "content": "# 文章标题\n\n这是文章正文内容...",
  "title": "文章标题",
  "templateId": "tech-blue",
  "accountId": "wx1234567890abcdef",
  "author": "作者名",
  "autoGenerateCover": true
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "taskId": "pub_a1b2c3d4e5f6g7h8",
    "status": "pending",
    "message": "发布任务已创建"
  }
}
```

---

### 6. 查询发布状态

```
GET /api/skill/publish/status?taskId={taskId}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "taskId": "pub_a1b2c3d4e5f6g7h8",
    "status": "completed",
    "progress": 100,
    "step": "✅ 发布成功",
    "logs": [
      { "time": "2026-04-06T10:00:00Z", "message": "获取用户信息" },
      { "time": "2026-04-06T10:00:01Z", "message": "🎨 应用模板样式" },
      { "time": "2026-04-06T10:00:05Z", "message": "🖼️ 处理文章图片" },
      { "time": "2026-04-06T10:00:10Z", "message": "📤 发布到微信草稿箱" },
      { "time": "2026-04-06T10:00:12Z", "message": "✅ 发布成功" }
    ],
    "result": {
      "mediaId": "xxxxxxxx",
      "draftUrl": "https://mp.weixin.qq.com/...",
      "accountName": "我的公众号",
      "templateName": "科技蓝",
      "publishedAt": "2026-04-06T10:00:12Z"
    },
    "error": null
  }
}
```

**状态值说明**:
| status | 说明 |
|--------|------|
| `pending` | 任务已创建，等待处理 |
| `processing` | 正在处理中 |
| `completed` | 发布成功 |
| `failed` | 发布失败（查看 error 字段） |

---

## 系统提示词

将以下内容添加到 Bot 的系统提示词中：

```
你是微信公众号排版发布助手。你必须严格按照以下步骤执行，不允许跳过或合并任何步骤。

## ⚠️ 强制工作流程（每一步都必须完成，禁止跳过）

### 第1步：接收用户需求
用户可能提供文章内容，或者让你生成文章内容。

### 第2步：检查并选择用户自定义模板（必须执行，不可省略）
- 调用 GET /api/skill/templates 获取模板列表
- **只使用 isUserTemplate: true 的用户自定义模板，忽略系统内置模板**
- 检查返回结果中的 userTemplatesCount 字段：

**如果 userTemplatesCount > 0**：
- 列出所有用户自定义模板（仅 isUserTemplate: true 的），让用户选择
- 等待用户明确回复选择了哪个模板后，再进行下一步

**如果 userTemplatesCount = 0**：
- 停止发布流程，告知用户需要先创建自定义模板
- 展示以下创建模板的引导信息：

---
⚠️ 您还没有创建自定义排版模板，请先创建模板后再发布文章。

**创建模板的方式：**

1️⃣ **模板设计器**（推荐）
   访问：https://open.tyzxwl.cn/website/template-designer.html
   可视化设计你的专属排版样式

2️⃣ **Fork 官方模板**
   访问：https://open.tyzxwl.cn/website/template-market.html
   浏览 36+ 精选模板，点击 Fork 即可复制到你的模板库

3️⃣ **个人中心管理**
   访问：https://open.tyzxwl.cn/profile.html?tab=templates
   管理和编辑你已有的模板

创建完成后，再回来告诉我，我来帮你排版发布！
---

- ❌ 禁止使用系统内置模板（isUserTemplate: false）
- ❌ 禁止自动选择任何模板
- ❌ 禁止在用户未回复前继续

### 第3步：让用户选择发布的公众号（必须执行，不可省略）
- 调用 GET /api/skill/accounts 获取用户已授权的公众号列表
- 将所有公众号列出（包括公众号名称），让用户选择要发布到哪个公众号
- **等待用户明确回复选择了哪个公众号后，再进行下一步**
- ❌ 即使用户只有1个公众号，也必须展示并询问确认
- ❌ 禁止自动选择第一个公众号

### 第4步：确认发布信息
- 汇总展示给用户确认：文章标题、所选模板名称、所选公众号名称
- 作者名称默认填写公众号名称（用户可自行修改）
- **等待用户回复"确认"后，才能调用发布接口**

### 第5步：执行发布
- 调用 POST /api/skill/publish，参数中必须包含：
  - templateId：第2步用户选择的自定义模板 ID
  - accountId：第3步用户选择的公众号 appId
  - author：默认使用公众号名称，用户指定则用用户的
- 调用 GET /api/skill/publish/status 轮询任务状态（每2秒一次，直到 completed 或 failed）
- 返回发布结果给用户

## 🚫 禁止事项（违反任何一条都是错误行为）

1. **禁止使用系统内置模板**：只能使用用户自定义模板（isUserTemplate: true）
2. **禁止跳过模板检查**：必须检查用户是否有自定义模板
3. **禁止在无模板时继续发布**：用户没有自定义模板时必须引导创建
4. **禁止跳过公众号选择**：必须让用户亲自选择公众号
5. **禁止自动选择**：不要替用户做任何选择
6. **禁止合并步骤**：模板选择和公众号选择必须分开进行
7. **禁止在用户未确认前调用发布接口**
8. 如果发布失败，展示完整的错误信息
```

---

## 使用示例

### 自然语言触发

```
写一篇关于人工智能的文章，发布到公众号
```

```
帮我写个美食探店文案，发到微信公众号
```

```
查询我的发布额度
```

### 命令触发

```
/publish 写一篇关于 ChatGPT 的科普文章
```

```
/quota
```

```
/status taskId=pub_a1b2c3d4e5f6g7h8
```

---

## 错误码说明

| HTTP 状态码 | 错误信息 | 解决方案 |
|-------------|----------|----------|
| 400 | 缺少文章内容 | 确保 content 参数不为空 |
| 400 | 缺少模板 ID | 确保 templateId 参数不为空 |
| 401 | 未授权 | 检查 API Key 是否正确 |
| 403 | 发布配额已用完 | 升级套餐或等待下月重置 |
| 404 | 模板不存在 | 检查 templateId 是否正确 |
| 429 | 请求频率超限 | 降低调用频率（默认 100 次/小时） |

---

## 常见问题

**Q: 为什么发布后样式没生效？**  
A: 微信公众号不支持 `<style>` 标签，系统已自动将 CSS 转为内联样式。如仍有问题请检查模板 CSS 是否正确。

**Q: 封面图比例不对怎么办？**  
A: 系统会自动裁剪封面图到 2.35:1 比例（900×383），也可设置 `autoGenerateCover: true` 让 AI 生成封面。

**Q: 为什么没有让我选模板/公众号？**  
A: 请确保系统提示词中明确要求必须让用户确认选择，不能自动跳过。

**Q: 接口返回 401 错误？**  
A: 检查 API Key 是否正确、是否已过期。

**Q: 看不到我的自定义模板？**  
A: 确保 API Key 对应的用户已在 Web 端创建了自定义模板。

---

## 联系方式

- 平台地址：https://open.tyzxwl.cn
- 邮箱：lanren0405@163.com
- 微信：sugu717

---

## 版本信息

**当前版本**: v1.2.0

### 更新日志

- v1.2.0: 新增额度查询、文章预览、自定义模板支持
- v1.1.0: 新增 AI 封面图生成、5 层兜底策略
- v1.0.0: 基础发布功能、6 种内置模板
