# GitHub 上传专项 | GitHub Publishing Guide

本文件定义技能通过独立 GitHub 仓库发布的操作规范。

## 适用场景

- 技能有独立的 GitHub 仓库
- 非 ClawHub 平台发布（如个人仓库、GitHub Pages 等）
- 需与 ClawHub 发布流程区分

## 两步验证流程

### 第一步：发现问题 → 确认问题 → 给出解决方案 → **逐个确认**

**⚠️ 重要原则：逐个修改，逐个确认**
- 多个文件/版本时，必须逐个处理
- 每修改完一个文件，等待用户确认后再改下一个
- 避免批量操作导致遗漏或 AI 幻觉
- 尤其适用于多语言 README 的修改

**汇报内容**：

| 项目 | 内容 |
|------|------|
| 当前处理 | 当前正在修改的文件（如 README_FR.md） |
| 仓库地址 | `https://github.com/<owner>/<repo>` |
| 当前状态 | 已修改未提交 / 已提交未推送 |
| 修改文件 | 列出所有变更文件 |
| 修改内容 | 简述每项改动 |
| 问题说明 | 发现的问题（如有） |
| 解决方案 | 针对问题的修复方案 |

**确认标志**：等待用户明确回复「好」「确认」「下一个」等。

### 第二步：用户确认后执行

```bash
# 1. 进入仓库目录
cd <skill-dir>

# 2. 添加所有变更
git add -A

# 3. 提交（英文在前，中文在后）
git commit -m "[English message]. [中文信息]。"

# 4. 推送到远程
git push
```

## Commit Message 规范

- 英文在前，中文在后
- 正式发布语气
- 禁止：个人纠错、格式调整、私人调试记录、玩笑、道歉式表述
- 示例：`fix: 修复徽章HTML兼容性问题，清理各语言版本中文残留`

## 安全约束

1. **严禁擅自上传** — 未获用户明确确认前不得执行 `git push`
2. **汇报当前状态** — 每次修改后必须汇报状态（已修改/未提交/已上传）
3. **等待明确指令** — 用户回复「好」「确认」「上传」后才执行 push

## Git 状态检查命令

```bash
# 查看当前状态
git status

# 查看变更统计
git diff --stat

# 查看完整变更内容
git diff

# 查看提交历史
git log --oneline -5
```

## 常见问题处理

### 有未提交的变更

用户要求上传前，先检查 `git status`：
- 如有未提交的变更，必须在汇报中列出
- 等待用户确认后再 add/commit/push

### 远程分支落后

```bash
# 先拉取最新
git pull --rebase

# 再推送
git push
```

### 冲突处理

1. 报告用户存在冲突
2. 等待用户指示如何解决
3. 不得强制覆盖远程分支

## 工作流程示例（多语言场景）

```
用户：修复所有语言版本的徽章显示问题
↓
AI：发现问题，列出 8 个语言版本
↓
AI：开始修改 README.md（第一个）
↓
用户：好
↓
AI：修改 README.md，确认完成后汇报
↓
AI：开始修改 README_ZH.md（第二个）
↓
用户：好
↓
AI：修改 README_ZH.md，确认完成后汇报
↓
...（以此类推，逐个确认）
↓
AI：全部修改完成，汇报当前状态（未提交）
↓
用户：好，上传
↓
AI：git add → commit → push
↓
AI：汇报完成（已上传 GitHub）
```

**⚠️ 关键点**：每修改完一个文件，必须汇报并等待用户确认，再处理下一个。这样可以：
1. 避免 AI 在长序列中遗漏文件
2. 确保每个文件的修改都被正确处理
3. 用户可以及时发现并纠正问题

## GitHub Release 专项 | GitHub Release Guide

创建 GitHub Release 同样需要两步验证。Release Notes 是对外展示的正式说明，必须符合规范。

### 何时需要创建 Release

- 首次正式发布版本（如 v1.0.0）
- 重要版本更新
- 用户明确要求创建 Release

### Release Notes 规范

**格式**：Markdown 语法，结构清晰
**内容**：
- 标题（版本号 + 简短描述）
- 变更说明（功能/修复/优化）
- 技术规格（如适用）
- 安装方式（如适用）

**禁止**：
- 个人调试记录
- 道歉式表述
- 不完整的描述

### 两步验证流程

#### 第一步：检查与汇报

| 项目 | 内容 |
|------|------|
| 仓库地址 | `https://github.com/<owner>/<repo>` |
| 当前 tag | 已有 tag 列表 |
| 新版本号 | 如 v1.0.0 |
| Release Notes | 拟定的正式说明 |
| 变更内容 | 列出主要变更 |

**确认标志**：等待用户明确回复「好」「确认」等。

#### 第二步：用户确认后执行

```bash
# 1. 创建 tag（如尚未创建）
git tag -a <version> -m "<version>"

# 2. 推送 tag
git push origin <version>

# 3. 使用 gh 创建 Release
gh release create <version> \
  --title "<标题>" \
  --notes "<Markdown 格式的 Release Notes>" \
  --target <branch>
```

### Release Notes 示例

````markdown
## What's New

**Skill Name** — 简短描述

基于 xxx，为用户提供 yyy 功能。

### 功能更新
- 新增 xxx 功能
- 优化 xxx 体验
- 修复 xxx 问题

### 技术规格
- 版本：1.0.0
- 支持平台：xxx
- 依赖：xxx

### 安装方式
```bash
xxx install command
````

### 验证命令

```bash
# 查看已创建的 Release
gh release list

# 查看特定 Release 详情
gh release view <tag>

# 更新 Release Notes
gh release edit <tag> --notes "<新内容>"
```

## 与 ClawHub 的区别

| 维度 | ClawHub | GitHub（独立仓库） |
|------|---------|-------------------|
| 平台 | clawhub CLI | git + gh CLI |
| 版本管理 | clawhub 内部管理 | git tag + Release |
| 验证方式 | `clawhub inspect` | `git log` + `gh release list` |
| 发布命令 | `clawhub publish` | `git push` + `gh release create` |
| 对外说明 | Changelog | Release Notes |
| 适用场景 | 技能市场分发 | 独立项目/文档站 |
