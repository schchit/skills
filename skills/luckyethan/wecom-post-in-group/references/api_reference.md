# 企业微信群机器人 API 参考

## Webhook 地址

```
https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=<WEBHOOK_KEY>
```

- 在企业微信群中：**群设置 → 群机器人 → 添加/查看机器人** 获取 Webhook 地址
- Webhook Key 即为 URL 中 `key=` 后面的 UUID 值

## 支持的消息类型

### 1. 文本消息 (text)

```json
{
    "msgtype": "text",
    "text": {
        "content": "消息内容，最长不超过 2048 字节",
        "mentioned_list": ["userid1", "userid2", "@all"],
        "mentioned_mobile_list": ["13800138000", "@all"]
    }
}
```

- `mentioned_list`: @指定成员的 userid 列表，`["@all"]` 表示 @所有人
- `mentioned_mobile_list`: @指定成员的手机号列表，`["@all"]` 同上

### 2. Markdown 消息 (markdown)

```json
{
    "msgtype": "markdown",
    "markdown": {
        "content": "# 标题\n## 二级标题\n**加粗**\n[链接](url)"
    }
}
```

**支持的 Markdown 语法:**

| 语法 | 示例 |
|------|------|
| 标题 | `# 一级` `## 二级` `### 三级` |
| 加粗 | `**粗体**` |
| 链接 | `[文字](URL)` |
| 引用 | `> 引用文字` |
| 有序列表 | `1. 列表项` |
| 无序列表 | `- 列表项` |
| 字体颜色 | `<font color="info">绿色</font>` |
| | `<font color="comment">灰色</font>` |
| | `<font color="warning">橙红色</font>` |

**注意**: Markdown 消息**不支持** @成员功能；不支持图片插入。

### 3. 图片消息 (image) — 脚本暂未封装

```json
{
    "msgtype": "image",
    "image": {
        "base64": "<图片 Base64 编码>",
        "md5": "<图片 MD5>"
    }
}
```

### 4. 图文消息 (news) — 脚本暂未封装

```json
{
    "msgtype": "news",
    "news": {
        "articles": [
            {
                "title": "标题",
                "description": "描述",
                "url": "跳转链接",
                "picurl": "图片链接"
            }
        ]
    }
}
```

### 5. 文件消息 (file) — 脚本暂未封装

需先上传文件获取 media_id，再发送文件消息。

## 频率限制

- 每个机器人发送的消息不能超过 **20条/分钟**

## 常见错误码

| errcode | 含义 | 建议 |
|---------|------|------|
| 0 | 成功 | - |
| 93000 | Webhook 地址无效 | 检查 key 是否正确 |
| 45009 | 发送频率超过限制 | 减少发送频率，稍后重试 |
| -1 | 网络错误 | 检查网络连接 |
