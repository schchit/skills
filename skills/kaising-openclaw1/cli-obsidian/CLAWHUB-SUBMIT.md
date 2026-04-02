# CLI-Obsidian - ClawHub 提交文档

## 基本信息

- **名称**: CLI-Obsidian
- **版本**: 1.0.0
- **分类**: 效率工具 / AI Agent
- **价格**: ¥68 (个人永久许可)
- **语言**: Python 3.10+

## 描述

CLI-Obsidian 是 Obsidian 笔记的命令行接口，专为 AI Agent 设计。

### 核心功能

- 📝 **笔记管理**: 创建、列出、搜索笔记
- 🏷️ **标签支持**: 添加和管理标签
- 🤖 **Agent 友好**: JSON 输出，完美适配 AI Agent
- 💻 **跨平台**: macOS/Windows/Linux 全支持

### 使用场景

1. **AI Agent 集成**: 让 OpenClaw/Claude Code 直接操作笔记
2. **自动化工作流**: 脚本批量管理笔记
3. **快速搜索**: 命令行快速查找笔记
4. **数据导出**: 导出为 Markdown/HTML/JSON

## 安装

```bash
# 下载后解压
cd cli-obsidian

# 安装依赖
pip install click

# 运行
python3 cli-obsidian-simple.py --help
```

## 使用示例

```bash
# 创建笔记
python3 cli-obsidian-simple.py create -t "Meeting Notes" --tags "meeting,work"

# 列出笔记
python3 cli-obsidian-simple.py list

# 搜索笔记
python3 cli-obsidian-simple.py search "project"

# JSON 输出 (Agent 使用)
python3 cli-obsidian-simple.py --json list
```

## 技术规格

- **Python**: 3.10+
- **依赖**: click (命令行框架)
- **大小**: < 10KB
- **平台**: 跨平台

## 许可

- **个人使用**: ¥68 永久许可
- **商业使用**: ¥198 永久许可 + 优先支持
- **企业定制**: 面议

## 支持

- **邮箱**: cli-skill-factory@example.com
- **文档**: GitHub README
- **更新**: 免费小版本更新

## 开发者

CLI Skill Factory - 专注 AI Agent 工具开发

---

## ClawHub 元数据

```json
{
  "name": "cli-obsidian",
  "version": "1.0.0",
  "description": "CLI interface for Obsidian - Make your notes agent-native",
  "author": "CLI Skill Factory",
  "category": "productivity",
  "price": 68,
  "currency": "CNY",
  "license": "commercial",
  "python_version": ">=3.10",
  "tags": ["obsidian", "cli", "automation", "ai", "agent", "notes"],
  "screenshots": [
    "screenshot1.png",
    "screenshot2.png"
  ],
  "download_url": "https://github.com/your-repo/cli-obsidian/archive/v1.0.0.tar.gz"
}
```
