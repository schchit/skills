# Link Transcriber Skill

一句话把抖音/小红书链接变成可读总结。

用户只需要粘贴链接，后台自动使用服务器已保存的 platform cookies 完成转写和总结，不需要自己填写 Cookie。

## Demo

这里最适合放一张 GIF 或截图：

- Claw 聊天框里粘贴一个抖音或小红书链接
- skill 自动发起转写
- 最终直接返回结构化总结

推荐素材：

- 15 秒操作录屏
- 输入前后对比截图
- 手机或电脑录屏都可以

## Why It Feels Good

- 不需要用户自己提供 Cookie
- 只返回最终总结，不输出一堆过程噪音
- 支持本地部署，也支持直接使用公开服务
- 适合把短视频内容快速变成可读信息

## Install

推荐从 ClawHub 安装到 Codex skills 目录：

```bash
npx clawhub@latest --workdir ~/.codex --dir skills install link-transcriber --force
```

已发布页面：

- `https://clawhub.ai/bobobo2026/link-transcriber`

如果你维护的是自定义环境，也可以通过这个 slug 安装：

```bash
npx clawhub@latest install link-transcriber
```

## Usage

自然语言直接用：

```text
分析这个抖音链接 https://v.douyin.com/xxxx
```

或者：

```text
Use $link-transcriber to summarize this Xiaohongshu link: https://xhslink.com/xxxx
```

预期输出：

- 标题或一句话总结
- 核心内容
- 亮点/要点

## How It Works

1. 识别抖音或小红书链接
2. 自动推断平台
3. 调用 `https://linktranscriber.store/linktranscriber-api`
4. 服务端使用已保存的 platform cookies 完成抓取或转写
5. 轮询结果
6. 返回最终总结

## Public Service

默认公开服务地址：

- `https://linktranscriber.store/linktranscriber-api`

这个 skill 的公开契约是：

- 用户提供链接
- 服务端负责处理平台访问所需配置
- 用户得到最终总结

## Local Override

如需接到自己的服务，可覆盖这些环境变量：

- `LINK_SKILL_API_BASE_URL`
- `LINK_SKILL_SUMMARY_PROVIDER_ID`
- `LINK_SKILL_SUMMARY_MODEL_NAME`

示例：

```bash
LINK_SKILL_API_BASE_URL=https://linktranscriber.store/linktranscriber-api \
python3 scripts/call_service_example.py 'https://xhslink.com/o/23s4jTem6em'
```

## Local Smoke

```bash
python3 scripts/check_service_health.py
python3 scripts/call_service_example.py 'https://xhslink.com/o/23s4jTem6em'
```

## What This Skill Is Not

- 不是 YouTube summarizer
- 不是原始转写 JSON 调试工具
- 不是多步骤工作流入口

## Files

- `SKILL.md` - canonical skill behavior
- `agents/openai.yaml` - Codex UI metadata
- `scripts/check_service_health.py` - Python health check for the hosted service
- `scripts/call_service_example.py` - transcribe + poll + summarize example
- `scripts/update_local_skill.sh` - install or refresh the local Codex skill copy
- `CLAWHUB.md` - ClawHub-oriented publish copy
