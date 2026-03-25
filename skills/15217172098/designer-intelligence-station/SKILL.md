---
name: designer-intelligence-station
description: 设计师情报收集工具。监控 40 个公开信息源（AI/硬件/手机/设计），6 维筛选标准 v2.0（基于 120+ 条行为分析），生成结构化日报/周报。仅抓取公开内容，不登录、不提交表单、不绕过付费墙。支持依赖自动检测和安装。
version: 2.0.0
author: 梨然 - 阿里版
license: MIT

category: research
tags:
  - design
  - intelligence
  - news
  - ai
  - hardware
  - mobile
  - structured-output
  - trend-analysis
  - open-sources-only
  - auto-dependency-check
  - screening-2.0

models:
  recommended:
    - qwen3.5-plus

capabilities:
  - intelligence_collection
  - news_filtering
  - daily_briefing
  - weekly_report
  - dependency_autoinstall
  - behavioral_screening

languages:
  - zh

related_skills: []
---

# 设计师情报站 v2.0.0

## 🔒 安全承诺（首次运行前必读）

**本技能仅抓取公开内容，明确承诺：**

| 承诺 | 说明 |
|------|------|
| ❌ 不登录 | 不需要任何账号或凭证 |
| ❌ 不提交表单 | 不会与网站进行任何交互 |
| ❌ 不绕过付费墙 | 只访问完全公开的页面 |
| ❌ 不存储敏感数据 | 所有数据本地保存，不发送外部 |
| ✅ 仅公开 URL | 所有 40 个监测源都是公开网站 |

### 首次运行前步骤

**请务必完成以下检查：**

1. **审查监测源** - 确认都是你信任的公开站点
   ```bash
   cat data/default_sources.json | grep '"url"'
   ```

2. **手动运行测试** - 不要立即启用自动化
   ```bash
   ./execute_daily.sh
   ```

3. **检查输出** - 确认链接都来自公开页面

4. **监控网络活动**（可选）
   ```bash
   sudo netstat -tnp | grep python
   ```

**完成上述检查后，再考虑启用定时自动化。**

---

## 功能

**监控 40 个公开信息源**，覆盖 AI、智能硬件、手机、设计四大领域：

- 📰 **中文媒体**（9 个）：36 氪、机器之心、量子位、爱范儿、少数派等
- 🎨 **设计媒体**（8 个）：Dezeen、Fast Company、UX Collective 等
- 🌐 **英文媒体**（5 个）：The Verge、TechCrunch、Wired 等
- 📡 **RSS 源**（6 个）：TechCrunch RSS、The Verge RSS 等
- 💬 **社区平台**（4 个）：GitHub Trending、Product Hunt 等
- 📱 **社交平台**（8 个，可选配置）：微博、B 站、知乎等

**输出格式**：
- 📊 结构化日报（v1.3.3 格式，表格 + 超链接）
- 📈 深度周报（趋势分析 + 竞品动态）

---

## 安装

```bash
# 1. 安装技能
clawhub install designer-intelligence-station

# 2. 进入目录
cd ~/.clawhub/skills/designer-intelligence-station

# 3. 安装依赖
pip install -r requirements.txt

# 4. 审查监测源（重要！）
cat data/default_sources.json | grep '"url"'

# 5. 初始化数据库
python3 data/import_sources.py

# 6. 手动测试运行
./execute_daily.sh
```

---

## 依赖

**Python 3.10+**，需要以下包（都是知名开源库）：

```txt
feedparser>=6.0.0      # RSS 解析（BSD）
requests>=2.28.0       # HTTP 请求（Apache 2.0）
beautifulsoup4>=4.11.0 # HTML 解析（MIT）
lxml>=4.9.0            # XML 解析（BSD）
python-dateutil>=2.8.2 # 日期解析（Apache 2.0）
```

**无需**：
- ❌ 浏览器自动化
- ❌ 外部 API 密钥
- ❌ 登录凭证

---

## 运行模式

### 模式一：手动触发（推荐）

```bash
./execute_daily.sh
```

或在对话中请求：
```
请生成今日的设计师情报日报
```

**执行流程**：
1. 自动检查 Python 版本（需要 3.10+）
2. 自动检查 Python 依赖包
3. 如有缺失，提示并自动安装
4. 执行情报抓取和生成

### 模式二：定时自动化（可选）

**仅在手动模式测试正常后启用**：

```bash
# 配置每日早上 8 点运行
crontab -e
# 添加：0 8 * * * cd ~/.clawhub/skills/designer-intelligence-station && ./execute_daily.sh
```

### 模式三：依赖检查（独立运行）

```bash
# 仅检查依赖，不执行抓取
python3 tools/check_dependencies.py
```

---

## 数据流向

```
公开网站（RSS/API/Web）
    ↓
Python 脚本（requests/feedparser）
    ↓
本地 JSON 缓存（data/cache/）
    ↓
合并去重（tools/fetch_all.py）
    ↓
SQLite 数据库（data/intelligence_sources.db）
    ↓
Agent 筛选和格式化
    ↓
本地 Markdown 文件（temp/）
    ↓
发送给用户（ClawHub 消息通道）
```

**所有数据本地存储**，不发送到外部服务。

---

## 监测源清单

完整列表见 `data/default_sources.json`，包括：

**科技媒体**：
- 36kr.com（36 氪）
- huxiu.com（虎嗅）
- ifanr.com（爱范儿）
- sspai.com（少数派）
- theverge.com（The Verge）
- techcrunch.com（TechCrunch）

**设计媒体**：
- dezeen.com（Dezeen）
- smashingmagazine.com（Smashing Magazine）
- uxdesign.cc（UX Collective）
- fastcompany.com（Fast Company）

**社区平台**：
- github.com/trending（GitHub Trending）
- producthunt.com（Product Hunt）

**社交平台**（可选，需额外配置）：
- weibo.com（微博）
- bilibili.com（B 站）
- zhihu.com（知乎）

---

## 筛选标准（v2.0 - 基于 120+ 条行为分析）

### 6 维筛选

| 维度 | 权重 | 说明 | 采用率 |
|------|------|------|--------|
| [1] 交互/视觉创新 | ⭐⭐⭐ | 专利（有创新）/新交互/视觉技术 | 100% |
| [2] 设计工具/资源 | ⭐⭐⭐ | 提升设计师效率的工具/资源 | 85% |
| [3] 深度分析/洞察 | ⭐⭐⭐ | 趋势/方法论/行业洞察 | 85% |
| [4] 大厂 AI/设计战略 | ⭐⭐ | 苹果/谷歌/华为的 AI 或设计发布 | 60% |
| [5] 设计作品/案例 | ⭐⭐ | 创意参考/趣味性/大厂案例 | 70% |
| [6] AI+ 设计工作流 | ⭐⭐⭐ | AI 工具/工作流创新 | 80% |

### 分级（维度组合）

| 等级 | 规则 | 目标占比 |
|------|------|---------|
| **S 级** | [1]+[3] 或 [1]+[6] 或 [3]+[6] | 10-15% |
| **A 级** | [1] 或 [2] 或 [3] 或 [6] | 40-50% |
| **B 级** | [4] 或 [5]（优质） | 30-40% |
| **C 级** | 纯资讯/市场数据/营销/教程/八卦 | 排除 |

**详细筛选指南**：见 `docs/screening-guide.md`

---

## 故障排查

### 依赖安装失败

```bash
python3 --version  # 需要 3.10+
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### 抓取失败

```bash
# 测试单个源
python3 tools/web_fetcher_standalone.py fetch CN004

# 检查网络
curl -I https://www.ifanr.com/
```

### 数据库错误

```bash
rm data/intelligence_sources.db
python3 data/import_sources.py
```

---

## 文档

- **INSTALL.md** - 详细安装指南
- **QUICKSTART.md** - 快速入门
- **docs/** - 详细文档（筛选指南、配置说明等）
- **CHANGELOG.md** - 更新日志

---

## 版本历史

### v2.0.0 (2026-03-25) - 筛选标准重大升级
- **重构**：6 维筛选标准 v2.0（基于 120+ 条历史情报行为分析）
- **新增**：[1] 交互/视觉创新维度（专利/新交互/视觉技术）
- **新增**：[6] AI+ 设计工作流维度（AI 工具/工作流创新）
- **优化**：分级规则量化（S 级：[1]+[3] 或 [1]+[6] 或 [3]+[6]）
- **新增**：排除清单（9 类明确排除内容）
- **新增**：边界情况判断流程
- **文档**：`docs/screening-guide.md` 详细指南

### v1.6.0 (2026-03-25)
- **新增**：依赖自动检测和安装功能
- **新增**：`tools/check_dependencies.py` - 依赖检查工具
- **优化**：`execute_daily.sh` 在执行前自动检查依赖
- **优化**：缺失依赖时自动提示并安装，无需手动干预

### v1.5.3 (2026-03-24)
- 修复：安全声明前置，首次运行前必读
- 新增：监测源审查步骤
- 优化：简化描述，突出安全承诺

### v1.5.2 (2026-03-24)
- 新增：DS007 体验碎周报专栏

### v1.5.1 (2026-03-24)
- 新增：独立网页抓取器（qclaw 适配）
- 优化：全自动执行流程

---

## 许可证

MIT License - 免费使用、修改和分发。

---

*最后更新：2026-03-25 | 设计师情报站 v2.0.0*
