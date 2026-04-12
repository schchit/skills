# Browser Web Search Skill

**把任何网站变成命令行 API** — 专为 OpenClaw 设计，复用浏览器登录态

## 快速开始

```bash
# 查看所有命令
npx --yes browser-web-search site list

# 运行
npx --yes browser-web-search site toutiao/hot           # 今日头条热榜
npx --yes browser-web-search site xiaohongshu/search "旅行"  # 小红书搜索
npx --yes browser-web-search site zhihu/hot             # 知乎热榜
npx --yes browser-web-search site bilibili/popular      # B站热门

# jq 过滤
npx --yes browser-web-search site zhihu/hot --jq '.items[].title'
```

## 内置平台（17 个）

| 平台 | 命令 |
|-----|------|
| **今日头条** | `toutiao/hot`, `toutiao/search`, `toutiao/feed` |
| **澎湃新闻** | `thepaper/hot` |
| **腾讯新闻** | `qqnews/hot` |
| **网易新闻** | `netease/hot` |
| **新浪新闻** | `sina/hot` |
| **微博** | `weibo/hot` |
| **微信公众号** | `weixin/search`, `weixin/article` |
| **小红书** | `xiaohongshu/search`, `xiaohongshu/note`, `xiaohongshu/comments`, `xiaohongshu/feed`, `xiaohongshu/me`, `xiaohongshu/user_posts` |
| **36kr** | `36kr/newsflash`, `36kr/search`, `36kr/article` |
| **知乎** | `zhihu/hot`, `zhihu/search`, `zhihu/question`, `zhihu/me` |
| **CSDN** | `csdn/search` |
| **博客园** | `cnblogs/search` |
| **Bilibili** | `bilibili/popular`, `bilibili/trending`, `bilibili/ranking`, `bilibili/search`, `bilibili/video`, `bilibili/comments`, `bilibili/feed`, `bilibili/history`, `bilibili/me` |
| **BOSS直聘** | `boss/search`, `boss/detail` |
| **Baidu** | `baidu/search` |
| **Bing** | `bing/search` |
| **Google** | `google/search` |

## 环境要求

- Node.js >= 18.0.0
- OpenClaw 环境

## 文档

详细使用说明：[SKILL.md](./SKILL.md)

## 链接

- [GitHub](https://github.com/sipingme/browser-web-search)
- [npm](https://www.npmjs.com/package/browser-web-search)

## License

MIT
