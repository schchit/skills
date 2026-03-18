# 小红书AI创作者识别 Skill

## 功能
自动在小红书平台搜索AI原创动画创作者，按预设规则筛选，导出结构化数据。

## 快速开始

### 1. 安装依赖

```bash
cd ~/.openclaw/workspace/skills/xiaohongshu-creator-finder
pip install -r requirements.txt
playwright install chromium
```

### 2. 首次运行（需要登录）

**方式1：使用OpenClaw命令**
```
/小红书创作者识别
```

**方式2：直接运行Python脚本**
```bash
# 基础搜索
python skill.py

# 自定义参数
python skill.py --keywords "AI动画,AI短剧" --min-likes 100 --min-followers 1000

# 使用配置文件
python skill.py --config config.example.json
```

### 3. 登录

首次运行会弹出浏览器窗口，请用手机小红书APP扫描二维码登录。
登录成功后，cookie会自动保存，下次运行无需再次登录。

## 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| keywords | array | ["AI动画","AI短剧"] | 搜索关键词 |
| min_likes | number | 50 | 最小点赞数 |
| min_comments | number | 5 | 最小评论数 |
| max_days_ago | number | 30 | 最大发布时间（天前） |
| min_followers | number | 500 | 最小粉丝量 |
| max_results | number | 30 | 每个关键词最大采集数 |
| output_format | string | excel | 输出格式 |
| headless | boolean | false | 无界面模式 |

## 命令行用法

```bash
# 基础用法
python skill.py

# 指定关键词
python skill.py -k "AI动画,AI短剧,AI视频"

# 提高筛选门槛
python skill.py --min-likes 200 --min-followers 2000 --max-days 15

# 无界面模式（仅已登录后可用）
python skill.py --headless

# 导出为JSON
python skill.py -o json
```

## 输出文件

运行完成后，在 `output/` 目录生成：

```
xiaohongshu_creators_20240317_143022.xlsx  # Excel表格
xiaohongshu_creators_20240317_143022.json  # JSON数据
```

## 表格字段

| 字段 | 说明 |
|------|------|
| 平台 | 小红书 |
| 创作者ID | 用户ID |
| 创作者名称 | 昵称 |
| 主页链接 | 小红书主页URL |
| 粉丝量 | 粉丝数 |
| 视频标题 | 匹配视频标题 |
| 视频链接 | 视频详情页 |
| 点赞数 | 视频点赞 |
| 评论数 | 视频评论 |
| 发布日期 | 视频发布时间 |
| 匹配关键词 | 搜索匹配的关键词 |
| 采集时间 | 数据抓取时间 |

## 注意事项

1. **反爬风险**：小红书有反爬机制，已内置随机延迟，建议不要频繁运行
2. **登录状态**：Cookie可能过期，如遇问题请删除 `cookies.json` 重新登录
3. **页面改版**：如解析失败，可能需要更新CSS选择器
4. **合规使用**：请遵守平台规则，仅供学习和研究使用

## 故障排查

### 无法登录
- 检查网络是否能访问 xiaohongshu.com
- 删除 `cookies.json` 重新扫码
- 确保手机小红书APP已登录

### 找不到视频
- 检查关键词是否有效
- 尝试降低筛选条件
- 页面结构可能变更，需要更新选择器

### 数据为空
- 筛选条件可能过于严格
- 该关键词下可能无符合条件的内容
- 检查登录状态是否正常
