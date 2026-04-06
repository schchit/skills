---
name: skill-atlas
version: "1.0.0"

# ── 安装规范 ─────────────────────────────────────────────
install:
  type: skill-package
  version: "1.0.0"
  files:
    - scripts/skill_atlas.py      # 主管理工具（17 个命令）
    - scripts/skill-inspect.py    # 技能审视分析脚本
    - scripts/skill-vetter.py     # 安全审查脚本（依赖 agent-memory）
    - config/scenes.json          # 场景 + 分类 + 常驻技能列表
    - config/clawhub_skills.md    # ClawHub 热门技能数据库
    - config/daily/               # 每日同步报告目录
  checks:
    - binary: clawhub
      note: "通过 PowerShell 调用，用于搜索/安装/更新技能"
    - binary: python
      note: "运行 skill_atlas.py、skill-inspect.py、skill-vetter.py"
    - binary: powershell
      note: "运行 clawhub CLI（clawhub.ps1）和 PowerShell 脚本"
    - script: scripts/skill-vetter.py
      note: "安全审查脚本，install/update/cat-add 时强制调用"
      required: true
      source: "必选，skill-atlas 依赖此脚本进行安全审查，安装前需先安装 agent-memory"
  steps:
    - copy: "复制所有文件到 WORKSPACE/skills/skill-atlas/"
    - check: "验证 WORKSPACE/scripts/skill-vetter.py 存在（来自 agent-memory）"
    - check: "验证 WORKSPACE/scripts/skill-inspect.py 存在"
    - init: "首次调用时自动创建 config/daily/ 目录和初始化 scenes.json"
  verify:
    - command: "python WORKSPACE/skills/skill-atlas/scripts/skill_atlas.py status"
      expect: "输出技能列表，无报错"
    - command: "python WORKSPACE/scripts/skill-vetter.py inspect skill-atlas"
      expect: "输出安全审查结果"

# ── 依赖声明 ─────────────────────────────────────────────
requires:
  binaries:
    - name: clawhub
      note: "通过 PowerShell 调用，用于搜索/安装/更新技能"
      required: true
    - name: python
      note: "运行 skill_atlas.py、skill-inspect.py、skill-vetter.py"
      required: true
    - name: powershell
      note: "运行 clawhub CLI（clawhub.ps1）和 PowerShell 脚本"
      required: true
  scripts:
    - path: scripts/skill-vetter.py
      note: "安全审查脚本，install/update/cat-add 时强制调用"
      required: true
      source: "来自 agent-memory（clawhub install agent-memory）"
    - path: scripts/skill-inspect.py
      note: "技能审视分析脚本"
      required: false
  env:
    - name: OPENCLAW_WORKSPACE
      default: "用户工作区根目录，如 C:/Users/23210/.openclaw/workspace"
      note: "用于定位 skills/、scripts/、config/ 目录"

# ── 权限声明 ─────────────────────────────────────────────
permissions:
  workspace_read:
    - skills/*/SKILL.md
    - skills/*/config/scenes.json
    - skills/*/config/daily/*.md
    - skills/*/scripts/*.py
    - skills/*/scripts/*.ps1
  workspace_write:
    - skills/skill-atlas/config/scenes.json
    - skills/skill-atlas/config/daily/
    - skills/*/config/scenes.json
  external:
    - name: clawhub install
      scope: "仅安装已审查的技能，更新前强制安全审查"
      mode: "interactive"
    - name: clawhub update
      scope: "仅更新已安装的技能，更新前强制安全审查"
      mode: "interactive"
    - name: clawhub search
      scope: "只读操作，不修改任何文件"
      mode: "read-only"
    - name: clawhub list
      scope: "只读操作，获取本地已安装技能列表"
      mode: "read-only"
    - name: clawhub inspect
      scope: "只读操作，获取远程技能元数据"
      mode: "read-only"

# ── 限制声明 ─────────────────────────────────────────────
limits:
  - "不读取 ~/.ssh、~/.aws、~/.config、~/.netrc 等敏感路径和凭据文件"
  - "不访问 MEMORY.md、USER.md、SOUL.md、IDENTITY.md 等身份文件"
  - "不发送凭据或敏感数据到外部服务器"
  - "clawhub install/update 仅影响 skills/ 目录，不修改系统文件"
  - "不执行未经安全审查的外部脚本（curl → 文件、eval、exec 等）"
  - "不请求提权/sudo，不修改 PATH 或系统环境变量"
  - "workspace_write 仅限于 skills/*/config/ 目录"
---

# 🧭 Skill Atlas · 技能图谱

> **让每一个技能各归其位，让每一次搜索有所依凭。**

---

## 🎯 定位

技能图谱是 OpenClaw 的**技能加载规则系统**。它定义：哪些技能在何时加载、如何分类、如何发现、以及如何在三大平台保持同步。

ClawHub 上有 **42,000+** 个技能，SkillHub（腾讯版）和国内镜像加起来更多。skill-atlas 就是你这台机器上的技能导航 + 加载规则。

---

## 三大来源

```
🇨🇳 ClawHub CN → mirror-cn.clawhub.com
🌐 ClawHub 全球 → clawhub.ai（42,000+ 技能）
🔧 SkillHub 腾讯版 → skillhub.tencent.com
```

**搜索和安装直接调用各平台 CLI，不依赖 find-skills：**

| 操作 | ClawHub CN | ClawHub 全球 | SkillHub |
|------|-----------|--------------|---------|
| 搜索 | `clawhub search <keyword>` | `clawhub search <keyword>` | _(网页访问)_ |
| 安装 | `clawhub install <slug>` | `clawhub install <slug>` | _(网页访问)_ |

---

## ⚡ 核心功能

| 功能 | 说明 |
|------|------|
| 📦 **技能 Inventory** | 核心 / 常驻 / 本地，三层分类 |
| 🔍 **跨平台搜索** | 三平台同时搜，按相关性排序 |
| 🔒 **安装安全审查** | 每次安装/更新前必做，自动执行 skill-vetter |
| 📥 **按分类下载** | 选分类 → 检测缺失 → 安全审查 → 安装 → 报告 |
| 🔔 **版本检测** | 每日检测，列出更新清单等你决定 |
| 📊 **每日报告** | 常驻技能 / 分类技能 / 可更新 / 待确认 |
| 🌟 **自动升降级** | 分类技能用够次数自动升常驻 |
| ⏰ **定时同步** | 每日 07:30 自动执行 |

---

## 🏗️ 技能加载规则

以下规则在**每次会话**生效，由 skill-atlas 定义：

### 三层加载架构

| 层 | 说明 | 加载方式 |
|----|------|----------|
| **核心层** | skill-atlas · proactive-agent · skill-vetter · self-improving-agent · agent-memory | 建议安装，每次会话自动加载 |
| **常驻层** | 用户常用技能（见 `config/scenes.json` 的 `resident_skills`） | 每次会话加载，可手动调整 |
| **分类层** | 用户按需安装的技能（通过「探索 [分类]」触发） | 按需加载，不永久驻留 |

### 每次会话加载顺序

```
1. 核心层技能（自动，始终加载）
2. 常驻层技能（自动，读取 scenes.json resident_skills）
3. 当前消息相关的分类技能（如有调用则加载）
```

> 注意：核心层技能为建议安装项，安装后每次会话自动加载。单个技能是否加载取决于它是否属于核心层或常驻层。

---

## 🔒 安全审查流程（自动，无需用户触发）

**原则：安装或更新任何技能前，必须通过安全审查。skill-vetter 是必须步骤，不是可选项。**

### 安装 / 更新流程（每次）

```
用户请求安装/更新
    ↓
clawhub inspect <slug> --json（获取信息）
    ↓
[自动] 执行 skill-vetter 审查协议
    ↓
┌─────────────────────────────────────┐
│ 🟢 LOW        → 直接安装/更新        │
│ 🟡 MEDIUM     → 完整审查后安装，报告  │
│ 🔴 HIGH       → 阻止安装，要求用户确认│
│ ⛔ EXTREME    → 拒绝安装，记录原因    │
└─────────────────────────────────────┘
```

### 审查内容（每次自动执行）

1. **Source Check** — 来源 / 作者 / 下载量 / 更新时间
2. **Code Review** — 扫描所有文件，检查红标命令
3. **Permission Scope** — 文件读写范围 / 网络访问 / 命令执行
4. **Risk Classification** — LOW / MEDIUM / HIGH / EXTREME

### 红标命令（任何一条 → 直接拒绝）

- curl/wget 到未知 URL
- 发送数据到外部服务器
- 请求凭据 / API Key
- 读取 ~/.ssh、~/.aws、~/.config
- 访问 MEMORY.md / USER.md / SOUL.md / IDENTITY.md
- base64 decode、eval()、exec()
- 修改 workspace 外的系统文件
- 安装未声明的包
- 混淆代码（压缩/编码/混淆）
- 请求提权/sudo

### 审查输出格式

```
🔒 安全审查报告
═══════════════════════════════════════
Skill: [name]
Source: [ClawHub / GitHub / other]
Author: [username] · ⭐ [stars] · 📥 [downloads]
Version: [version] · Updated: [date]
───────────────────────────────────────
RED FLAGS: [None / 列表]

PERMISSIONS:
• Files: [列表]
• Network: [列表]
• Commands: [列表]
───────────────────────────────────────
RISK LEVEL: 🟢 LOW

VERDICT: ✅ 审查通过，安装中...
═══════════════════════════════════════
```

### 特殊处理

- **核心技能（已在列表）**：首次安装仍需审查，但信任级别更高
- **已知高星作者（⭐1000+）**：审查后降一级（MEDIUM → LOW）
- **凭据类技能（🔴 HIGH）**：必须用户明确批准才能安装
- **本地已修改的 skill**：标记「本地修改」，更新时只报告差异不覆盖

---

## 📂 分类与代表技能

| 分类 | 代表技能 |
|------|----------|
| 🔍 **搜索资讯** | Summarize、Tavily Search、Brave Search、Multi Search Engine |
| 🧠 **记忆/知识** | ontology、Elite Longterm Memory、Memory Setup |
| 🤖 **AI 增强** | Proactive Agent、self-improving-agent、Evolver |
| 🌐 **浏览器自动化** | Agent Browser、Browser Use、Playwright MCP |
| 📁 **文件处理** | Nano Pdf、Word/DOCX、Excel/XLSX、Markdown Converter |
| ⚡ **自动化** | Automation Workflows、Desktop Control、Auto-Updater |
| 💼 **工作办公** | Gmail、Notion、Slack、Trello、Himalaya |
| 💰 **投资交易** | Polymarket、Stock Analysis、Stock Watcher |
| 🎨 **创意设计** | Nano Banana Pro、SuperDesign |
| 🎬 **多媒体** | Openai Whisper、YouTube Watcher、Video Frames |
| 🌤️ **生活** | Weather、Sonoscli |
| 🔌 **API 集成** | Github、Gog、Discord、Telegram |
| 📱 **社交媒体** | tieba-claw、Xiaohongshu Automation |
| 🗃️ **数据分析** | Data Analysis、AdMapix |

---

## 🔧 管理命令

```
技能审视 / 技能分析    → 分析所有已安装技能，输出详细报告

搜索 [关键词]          → clawhub search（跨 CN / 全球平台）
安装 [技能名]          → 自动安全审查 → 安装（审查不通过则阻止）
探索 [分类名]          → 检测缺失 + 自动安全审查 → 下载

更新 [技能名]          → 自动安全审查 → 更新（审查不通过则阻止）
全部更新              → 批量安全审查 → 依次更新
审查技能 [技能名]      → 手动触发独立审查（结果存查）

分类创建 [分类名]      → 新建自定义分类（创建后自动审查分类内容）
分类删除 [分类名]      → 删除自定义分类（仅删除分类，技能文件保留）
分类添加 [分类名] [skill] → 添加技能到分类（自动审查该技能）
分类移除 [分类名] [skill] → 从分类移除技能
分类启用 [分类名]      → 启用分类（该分类下所有技能一起加载）
分类禁用 [分类名]      → 禁用分类（该分类下所有技能不加载）
分类列表              → 查看所有自定义分类
分类详情 [分类名]      → 查看分类详情（含技能列表、审查状态）

添加常驻 [技能名]      → 手动提升为常驻
移除常驻 [技能名]      → 从常驻层移除
取消加载 [技能名]      → 申请取消（下次心跳确认后移除）
保留 [技能名]         → 撤销取消申请

当前场景              → 查看当前场景及推荐技能
查看每日报告          → 查看今日同步报告
```

---

## ⏰ 定时同步

每日 07:30（Asia/Shanghai）自动执行 `scripts/daily-skill-sync.ps1`（首次启用时自动生成），包含：

### 🔔 版本检测（优先执行）
1. `clawhub list` 获取本地已安装技能及版本
2. `clawhub inspect <slug> --json` 获取远程最新版本
3. 对比差异，生成 `config/daily/updates_YYYY-MM-DD.md`
4. 如有更新，在心跳时展示更新表格并询问用户

### 🔒 更新前安全审查

用户批准更新后，**每次更新前**仍需重新审查（skill 可能已更新代码）：

```
批准更新 → 对每个待更新技能执行 skill-vetter 审查
    ↓
🟢 LOW  → 直接更新
🟡 MEDIUM → 审查通过后更新，报告结果
🔴 HIGH → 暂停，要求二次确认
⛔ EXTREME → 跳过，记录并报告
```

### 📊 每日报告（同步后生成）

同步完成后自动生成 `config/daily/daily_YYYY-MM-DD.md`，展示：

```
## 🏠 常驻技能（N 个）
列表：名称 / 版本 / 下载量 / ⭐

## 📂 分类加载技能（N 个）
列表：名称 / 版本 / 已用次数 / 状态
状态：✅ 正常 / 🟡 可升级 / ❌ 申请取消

## 🔔 可更新技能（N 个）
表格：技能 / 当前版本 / 最新版本 / 更新说明

## 📌 待确认事项
- 🔴 有 N 个技能可更新，是否现在更新？
- 🟡 以下分类技能已达 5 次，是否取消加载？
- 🟢 以下分类技能连续使用 10 次，已自动升级为常驻技能
```

### 技能升降级规则

| 触发条件 | 自动操作 | 告知用户 |
|----------|----------|----------|
| 分类技能使用 ≥ 10 次 | 自动移入常驻层 | ✅ 告知 |
| 分类技能使用 ≥ 5 次 | 标记「可升级」 | ✅ 询问是否取消 |
| 用户申请取消 | 心跳确认后移除 | ✅ 确认 |
| 常驻技能 7 天未用 | 标记可降级 | ✅ 询问 |

### 用户回复指令

```
更新 [技能名]     → 安全审查 → clawhub update（审查通过后执行）
全部更新          → 批量安全审查 → 依次更新
取消加载 [技能名] → 标记取消，心跳确认后移除
保留 [技能名]    → 撤销取消申请
```

---

## ⚙️ 配置文件

| 文件 | 说明 |
|------|------|
| `config/clawhub_skills.md` | 热门技能数据库 |
| `config/scenes.json` | 场景 + 分类 + 常驻技能列表 + 自定义分类 |
| `config/daily/` | 每日同步增量记录 |
| `config/daily/daily_*.md` | 每日报告 |
| `config/daily/updates_*.md` | 版本更新详细报告 |
| `config/user-preferences.json` | 分类技能运行时状态、取消申请 |
| `scripts/` | 脚本目录（首次启用时自动生成） |
| `scripts/skill-inspect.py` | 技能审视分析脚本 |

---

## 🔍 新功能一：技能审视分析

**命令：** `技能审视` / `技能分析`

自动分析所有本地已安装技能，输出详细报告：

### 审视维度

| 维度 | 说明 |
|------|------|
| 📋 **基础信息** | 名称 / 版本 / 描述 / 安装来源 |
| 📦 **体积** | 文件总大小（KB） |
| 🔗 **依赖** | 所需 binary / 环境变量 / 其他技能 |
| ⚙️ **运行状态** | 可用 / 部分可用 / 缺依赖 / 需配置 |
| 🛡️ **安全** | 红标命令数 / 可疑模式 |
| 🔄 **可更新** | clawhub 版本 vs 本地版本 |
| 📁 **文件清单** | 所有文件列表 |

### 状态分级

| 状态 | 含义 |
|------|------|
| ✅ **正常** | 完整可用，所有依赖满足 |
| ⚠️ **部分可用** | 主体可用，缺某些非核心依赖 |
| 🔴 **不可用** | 缺少关键 binary 或配置 |
| 🔵 **自定义** | 本地修改版，非 clawhub 原装 |

### 审视报告格式

```
🔍 技能审视报告
═══════════════════════════════════════
共 N 个技能 ·核心 N 个 ·常驻 N 个 ·分类 N 个 ·自定义 N 个
───────────────────────────────────────
✅ 正常（N 个）
  • skill-a · v1.0 · 12KB · 核心
  • skill-b · v2.3 · 8KB · 常驻

⚠️ 部分可用（N 个）
  • skill-c · v1.0 · 45KB · 分类
    ⚠️ 缺 binary: summarize

🔴 不可用（N 个）
  • skill-d · v1.0 · 30KB
    🔴 缺 python 包: xxx
    🔴 缺 API Key: TAVILY_API_KEY

🔵 自定义修改（N 个）
  • proactive-agent · v3.1.0 · 81KB
    🔵 本地 WAL 协议修改

🔄 可更新（N 个）
  • self-improving-agent · 3.0.10 → 3.0.12
───────────────────────────────────────
📌 建议操作
  • skill-c: 安装 summarize binary
  • skill-d: 设置 TAVILY_API_KEY 或卸载
  • self-improving-agent: 可更新 → 回复「更新 self-improving-agent」
═══════════════════════════════════════
```

**触发时机：**
- 用户主动执行「技能审视」
- 首次使用 skill-atlas 时自动运行（不展示，只记录到日志）

---

## 📦 新功能二：自定义分类

**概念：** 用户创建自己的技能分类，分类内的技能可以一键整体加载/禁用。

### 自定义分类 vs 内置分类

| | 内置分类 | 自定义分类 |
|---|---|---|
| 创建者 | skill-atlas 内置 | 用户创建 |
| 编辑 | 不可修改 | 用户随时编辑 |
| 启用方式 | 场景切换 | 分类启用命令 |
| 技能审查 | 手动触发 | 创建/修改时自动审查 |

### 工作流程

```
分类创建 [my-trading]
    ↓
输入分类描述（可选）
    ↓
分类添加 [my-trading] polymarket
    ↓
自动审查 polymarket（skill-vetter）
    ↓
┌──────────────────────────────────┐
│ 🟢 LOW      → 加入分类            │
│ 🟡 MEDIUM   → 加入并报告          │
│ 🔴 HIGH     → 拒绝添加，要求确认   │
│ ⛔ EXTREME  → 拒绝，记录原因      │
└──────────────────────────────────┘
    ↓
分类启用 [my-trading]
    ↓
所有技能加载，输出报告
```

### 分类数据结构（scenes.json）

```json
{
  "custom_categories": {
    "my-trading": {
      "name": "我的交易套件",
      "description": "交易相关技能合集",
      "enabled": false,
      "skills": ["polymarket", "stock-analysis"],
      "created_at": "2026-04-03",
      "last_vetted_at": "2026-04-03"
    }
  }
}
```

### 分类加载规则

| 操作 | 行为 |
|------|------|
| **分类启用** | 所有技能加入常驻层，下次会话加载 |
| **分类禁用** | 所有技能从常驻层移除，但不删除文件 |
| **分类删除** | 移除分类，技能文件保留，不影响当前会话 |
| **分类内 skill 单独取消** | 从分类中移除，不影响分类启用状态 |

---

---

## 🚀 首次启用（自动）

skill-atlas 安装后首次调用时，自动完成初始化：

```
skill-atlas 初始化完成

  🧭 skill-atlas · 技能图谱
  ─────────────────────────────────────────
  42,000+ 技能 · 三大平台 · 每日自动同步

  三大来源：
  🌐 ClawHub（clawhub.ai）
  🇨🇳 ClawHub CN（mirror-cn.clawhub.com）
  🔧 SkillHub（skillhub.tencent.com）

  ─────────────────────────────────────────
  已就绪功能：

  🔍 跨平台搜索
     同时搜索三个平台，按相关性排序返回结果

  📥 按分类下载
     选定分类 → 检测本地已有 → 自动安装缺失技能
     → 生成详细报告（版本 / 下载量 / 星级 / 介绍）

  🔔 版本检测
     每日检测所有已安装技能，发现更新立即列出清单
     → 你决定是否更新，回复「更新」或「全部更新」

  📊 每日报告
     常驻技能 / 分类加载技能 / 可更新技能 / 待确认事项
     → 每天定时生成，主动推送到你面前

  🌟 自动升降级
     分类技能连续使用 10 次 → 自动升为常驻
     常驻技能 7 天未用 → 提示是否降级

  ─────────────────────────────────────────
  定时任务：每日 07:30（Asia/Shanghai）自动同步

  快速开始：
  「探索 [分类名]」   → 下载并安装该分类下的热门技能
  「技能状态」        → 查看当前核心 / 常驻 / 分类三层技能
  「搜索 [关键词]」   → 跨平台搜索技能
  「查看每日报告」    → 查看今日同步结果
```
