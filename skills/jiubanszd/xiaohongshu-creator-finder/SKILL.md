# 小红书AI创作者识别 Skill

## 名称
xiaohongshu-creator-finder

## 描述
在小红书平台按预设规则自动搜索并识别AI原创动画创作者。支持多关键词搜索、智能筛选、数据导出到Excel/JSON。

## 触发方式

### 方式1：命令触发
```
/小红书创作者识别
/找AI创作者
/xhs-finder
```

### 方式2：自然语言
- "帮我找小红书上的AI动画创作者"
- "搜索小红书的AI短剧创作者"
- "识别小红书上做AI视频的博主"

## 项目结构

```
xiaohongshu-creator-finder/
├── skill.py                  # 主入口文件
├── skill.json                # Skill配置
├── src/
│   └── xhs_creator_finder.py # 核心程序
├── config/
│   ├── settings.json         # 运行参数配置 ⭐修改这里
│   └── cookies.json          # 登录Cookie（自动生成）
├── output/                   # 输出结果 ⭐结果在这里
│   ├── creators_YYYYMMDD_HHMMSS.xlsx
│   └── creators_YYYYMMDD_HHMMSS.json
├── docs/
│   └── 使用说明书.md          # 详细文档
└── logs/                     # 运行日志
```

## 配置文件说明

编辑 `config/settings.json` 自定义搜索规则：

```json
{
  "keywords": ["AI动画", "AI短剧", "AI视频"],
  "max_results": 15,
  "min_followers": 1000,
  "min_comments": 20,
  "output_format": "excel"
}
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `keywords` | 搜索关键词列表 | ["AI动画"] |
| `max_results` | 每个关键词搜索多少个视频 | 15 |
| `min_followers` | 最小粉丝量（过滤条件） | 1000 |
| `min_comments` | 最小评论数（过滤条件） | 20 |
| `output_format` | 输出格式 | excel |
| `chrome_path` | Chrome浏览器路径 | 自动检测 |

## 输出结果

### 文件位置
```
output/creators_YYYYMMDD_HHMMSS.xlsx
output/creators_YYYYMMDD_HHMMSS.json
```

### 数据字段
- 平台、创作者ID、创作者名称
- 主页链接、粉丝量
- 视频链接、点赞数、评论数
- 匹配关键词、采集时间

## 首次使用

1. 触发命令 `/小红书创作者识别`
2. 弹出Chrome窗口，**扫码登录**小红书
3. Cookie自动保存，后续无需登录
4. 等待运行完成，查看 `output/` 目录结果

## 注意事项

1. **运行时间**: 1个关键词约3-4分钟（受OpenClaw 5分钟超时限制）
2. **频率控制**: 建议间隔5-10分钟再运行
3. **Cookie过期**: 如遇登录问题，删除 `config/cookies.json` 重新登录
4. **筛选说明**: 
   - `[FILTER]` = 粉丝/评论数不达标
   - `[SKIP]` = 非视频内容
   - `[FAIL]` = 解析失败

## 依赖

- Python 3.8+
- Playwright
- pandas
- openpyxl

```bash
pip install playwright pandas openpyxl
playwright install chromium
```

## 详细文档

查看 `docs/使用说明书.md` 获取完整使用指南。
