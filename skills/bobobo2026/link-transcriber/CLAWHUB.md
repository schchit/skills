# Link Transcriber ClawHub Notes

一句话把抖音/小红书链接变成可读总结。

这个 skill 的公开承诺很简单：

- 用户只要粘贴链接
- 服务端自动使用已保存的 platform cookies
- 最终只返回总结结果

公开服务地址：

- `https://linktranscriber.store/linktranscriber-api`

推荐强调的价值点：

- 不需要用户自己填写 Cookie
- 只返回最终总结，不输出一堆中间过程
- 支持 Douyin 和 Xiaohongshu
- 既可本地部署，也可直接使用公开服务

推荐演示方式：

- 输入一个抖音或小红书链接
- 直接展示返回的结构化总结
- 最好配 15 秒 GIF 或输入前后对比截图

推荐安装口径：

```bash
npx clawhub@latest --workdir ~/.codex --dir skills install link-transcriber --force
```

当前发布页：

- `https://clawhub.ai/bobobo2026/link-transcriber`

对外描述保持克制：

- 输入：`url`
- 平台：自动推断，必要时再确认
- 输出：最终 summary
- 不把平台 cookies 暴露给终端用户
- 不扩展到其它复杂工作流能力
