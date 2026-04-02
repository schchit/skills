---
name: experience-manager
description: "经验管理工具：提取经验生成标准格式zip包，学习经验并转化为自身能力"
metadata:
  version: 1.1.1
  author: zhulianxin@corp.netease.com
---

# Experience Manager Skill

经验管理工具，支持经验的提取、学习和列表查看。

## 功能

### 1. 创建经验 (create)

将自然语言描述的经验转化为标准格式的 zip 包。

**使用方式：**
```
创建经验 <经验描述>
```

**示例：**
```
创建经验 用 feishu_doc 写入后必须验证 block_count，不然会静默失败
```

**命令行用法：**
```bash
# 自动提取 name
node create.mjs "feishu_doc 写入后必须验证 block_count"

# 手动指定 name（中文描述时使用）
node create.mjs "中文描述" --name=feishu-doc-validation
```

**流程：**
1. 解析用户输入，提取结构化信息
2. 识别依赖的技能和知识领域
3. 生成标准格式的 exp.yml
4. 生成 references/ 目录下的依赖文件
5. 打包为 zip 文件
6. 保存到 ~/.openclaw/experiences/packages/

**输出：**
- 生成 zip 文件：~/.openclaw/experiences/packages/{name}.zip
- 包含 exp.yml 和 references/ 目录
- 显示经验包预览和保存路径

### 2. 学习经验 (learn)

从 zip 包中学习经验，转化为自己的 SOUL/AGENTS/TOOLS。

**使用方式：**
```
学习经验 <zip包路径或URL>
```

**支持的来源：**
- 在线地址：`https://example.com/exp.zip`
- 本地路径：`file:///path/to/exp.zip` 或 `/path/to/exp.zip`
- 已下载的经验：`~/.openclaw/experiences/packages/exp.zip`

**示例：**
```
学习经验 https://example.com/feishu-doc-write-validation.zip
学习经验 ~/.openclaw/experiences/packages/feishu-doc-write-validation.zip
```

**流程：**
1. 下载/读取 zip 包
2. 检查是否已学习过（name + version 判断）
3. 检查依赖是否满足
4. 分析相关性
5. 生成转化方案
6. 应用并记录学习状态

**冲突处理：**
- name 相同，version 相同：提示已学习，跳过
- name 相同，version 不同：提示有新版本，可选更新
- name 不同：正常学习

### 3. 经验列表 (list)

显示所有经验包及学习状态。

**使用方式：**
```
经验列表
```

**输出：**
```
📚 经验列表

✅ 已学习 (2)
  feishu-doc-write-validation    v1.0.0    feishu_doc 写入验证
  subagent-timeout-handling      v1.0.0    子agent超时处理

⏳ 未学习 (1)
  complex-task-split             v1.0.0    复杂任务拆分策略
```

## 经验包格式 (Schema v1)

### Schema 版本

**当前版本**: `openclaw.experience.v1`

版本说明：
- **v1.0.0**: 初始版本，精简格式
- 后续破坏性字段修改需升级版本号
- `create.mjs` 和 `learn.mjs` 根据 `schema` 字段处理不同格式

### zip 包结构

```
{name}.zip
├── exp.yml              # 主文件（精简，只含元数据和引用）
└── references/          # 详细内容（可选）
    ├── soul.md          # SOUL 相关内容
    ├── agents.md        # AGENTS 相关内容
    └── tools.md         # TOOLS 相关内容
```

### exp.yml 格式 (v1)

```yaml
schema: openclaw.experience.v1    # Schema 版本标识
name: feishu-doc-blockcount       # 经验包名称（英文小写+中划线+数字）
description: 经验描述              # 问题/经验描述
metadata:
  version: 1.0.0                  # 经验包版本
  author: unknown                 # 作者
soul: references/soul.md          # 指向 SOUL 相关内容（可选）
agents: references/agents.md      # 指向 AGENTS 相关内容（可选）
tools: references/tools.md        # 指向 TOOLS 相关内容（可选）
skills:                           # 依赖的 skills 列表
  - feishu_doc
```

### name 格式约束

| 规则 | 说明 |
|------|------|
| 允许字符 | `a-z` 小写字母、`0-9` 数字、`-` 中划线 |
| 转换规则 | 空格 → 中划线；下划线 `_` 删除；中文删除 |
| 长度限制 | 最多 50 字符 |

**示例转换：**
- `feishu_doc 写入后必须验证 block_count` → `feishudoc-blockcount`
- `My_Experience_Name` → `myexperiencename`

### references 文件格式

#### soul.md

```markdown
# {标题} - 行为准则

> 来源: 经验包
> 类型: tool_tip

## 涉及原则
- 原则1
- 原则2

## 行为准则
- 准则1
```

#### agents.md

```markdown
# {标题} - 工作流程

> 来源: 经验包
> 类型: tool_tip

## 场景
问题描述

## 处理流程
1. 步骤1
2. 步骤2

## 相关规则
- 规则1
```

#### tools.md

```markdown
# {标题} - 工具使用

> 来源: 经验包
> 类型: tool_tip

## 问题
问题描述

## 解决方案
1. 步骤1
2. 步骤2

## 代码示例
```代码```

## 涉及工具
- 工具1
```

## 存储结构

```
~/.openclaw/experiences/
├── packages/                          # zip 包存储
│   ├── feishu-doc-write-validation.zip
│   └── subagent-timeout-handling.zip
├── extracted/                         # 解压后的 exp.yml
│   ├── feishu-doc-write-validation/
│   │   └── exp.yml
│   └── subagent-timeout-handling/
│       └── exp.yml
└── index.json                         # 学习状态索引
```

## index.json 格式

```json
{
  "experiences": [
    {
      "name": "feishu-doc-write-validation",
      "version": "1.0.0",
      "title": "feishu_doc 写入验证",
      "status": "learned",
      "learned_at": "2026-03-28T20:39:00+08:00"
    }
  ]
}
```

## 依赖

- Node.js >= 18
- js-yaml: YAML 解析和生成
- adm-zip: zip 文件处理

## 安装

```bash
# 安装依赖
cd /data/openclaw/skills/experience-manager
npm install js-yaml adm-zip
```

## 使用方法

### 直接运行脚本

```bash
# 设置环境变量
export PATH="/usr/local/node/bin:$PATH"
export OPENCLAW_USER_ID="your-user-id"
export OPENCLAW_WORKSPACE="/path/to/workspace"

# 创建经验
node /data/openclaw/skills/experience-manager/scripts/create.mjs "经验描述"

# 创建经验（手动指定 name）
node /data/openclaw/skills/experience-manager/scripts/create.mjs "中文描述" --name=my-experience

# 学习经验
node /data/openclaw/skills/experience-manager/scripts/learn.mjs <zip路径或URL>

# 查看列表
node /data/openclaw/skills/experience-manager/scripts/list.mjs
```

### 作为 OpenClaw Skill 使用

在 OpenClaw 中，可以通过以下方式调用：

```
创建经验 <描述>
学习经验 <zip路径或URL>
经验列表
```

## 使用方法

### 命令行用法

```bash
# 1. 创建经验
node scripts/create.mjs "使用 feishu_doc 读取文档"

# 2. 创建经验（指定 Agent，会扫描 Agent 特定 skills）
node scripts/create.mjs "使用 feishu_doc 读取文档" --agent=严哥

# 3. 学习到当前 Agent
node scripts/learn.mjs ~/.openclaw/experiences/packages/feishudoc.zip

# 4. 学习到指定 Agent
node scripts/learn.mjs ~/.openclaw/experiences/packages/feishudoc.zip --agent=严哥

# 5. 预览变更（不实际应用）
node scripts/learn.mjs exp.zip --agent=严哥 --dry-run

# 6. 查看列表
node scripts/list.mjs

# 7. 查看指定 Agent 的学习记录
node scripts/list.mjs --agent=严哥
```
