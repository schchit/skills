---
name: ncss
description: 自动化小说创作系统，支持章节规划、内容生成、质量审计、连续性管理；当用户需要创作小说、续写章节、分析文风或审计质量时使用
---

# NCSS - 自动化小说创作系统

## 任务目标
- 本 Skill 用于: 自动化长篇小说的创作与管理
- 能力包含: 章节规划、内容生成、质量审计、连续性检查、文风管理
- 触发条件: 用户需要创作小说、续写章节、分析文风、审计内容质量、管理创作状态

## 前置准备
- 依赖说明: 无外部 Python 依赖，使用标准库
- 项目结构准备:
  ```bash
  # 在当前目录创建小说项目结构
  mkdir -p ./novel-project/{chapters,state,reference}
  ```

## 操作步骤

### 1. 初始化小说项目
- 智能体将根据用户需求创建小说基础结构
- 生成以下核心文件:
  - `reference/story_bible.md`: 故事设定（世界观、角色、魔法体系等）
  - `reference/outline.md`: 大纲规划
  - `state/world_state.md`: 世界状态
  - `state/character_matrix.md`: 角色矩阵
  - `state/pending_hooks.md`: 未闭合伏笔
  - `state/chapter_summaries.md`: 章节摘要
- 使用 `assets/templates/character_template.md` 创建角色卡

### 2. 章节规划
- 智能体阅读 `reference/outline.md` 和状态文件
- 生成下一章节的详细大纲
- 确定本章的:
  - 核心冲突
  - 出场角色
  - 关键情节
  - 情感走向
  - 伏笔推进

### 3. 内容生成
- 智能体根据章节大纲和当前世界状态撰写正文
- 调用 `scripts/word_counter.py` 统计字数
- 保持与 `state/` 文件的连续性
- 遵循 [writing_guide.md](references/writing_guide.md) 中的写作规范
- 符合 [genre_templates.md](references/genre_templates.md) 中的题材特征

### 4. 质量审计
- 智能体对照 [audit_checklist.md](references/audit_checklist.md) 进行多维度检查
- 检查内容:
  - 角色行为一致性
  - 物资和道具连续性
  - 伏笔回收进度
  - 叙事节奏
  - 情感弧线
  - 语言表达
- 审计通过后保存章节到 `chapters/chapter-XX.md`
- 审计不通过则进入修订流程

### 5. 状态更新
- 智能体提取章节中的关键信息
- 更新所有状态文件:
  - `state/world_state.md`: 角色位置、关系变化、已知信息更新
  - `state/character_matrix.md`: 角色交互记录
  - `state/pending_hooks.md`: 新增/解决/推迟伏笔
  - `state/chapter_summaries.md`: 本章摘要
- 调用 `scripts/state_manager.py` 验证状态文件格式

### 6. 章节管理
- 调用 `scripts/chapter_manager.py` 执行章节管理操作:
  - 列出所有章节: `python /workspace/projects/novel-writer/scripts/chapter_manager.py --action list --project-path ./novel-project`
  - 查找最新章节: `python /workspace/projects/novel-writer/scripts/chapter_manager.py --action find-latest --project-path ./novel-project`
  - 验证章节格式: `python /workspace/projects/novel-writer/scripts/chapter_manager.py --action validate --project-path ./novel-project --chapter chapter-05`

### 7. 文风管理
- 智能体分析参考文本提取文风特征
- 生成文风指南: 词汇偏好、句式特征、叙事节奏
- 在内容生成时应用文风规则
- 文风变更时更新 `reference/style_guide.md`

## 资源索引
- 必要脚本:
  - [scripts/chapter_manager.py](scripts/chapter_manager.py): 章节文件管理（列表、查找、验证）
  - [scripts/state_manager.py](scripts/state_manager.py): 状态文件管理（创建、更新、验证）
  - [scripts/word_counter.py](scripts/word_counter.py): 字数统计工具
- 领域参考:
  - [references/writing_guide.md](references/writing_guide.md): 写作技巧与最佳实践
  - [references/genre_templates.md](references/genre_templates.md): 题材特征模板（玄幻、仙侠、都市等）
  - [references/audit_checklist.md](references/audit_checklist.md): 质量审计检查清单
- 输出资产:
  - [assets/templates/chapter_template.md](assets/templates/chapter_template.md): 章节文件模板
  - [assets/templates/character_template.md](assets/templates/character_template.md): 角色卡模板

## 注意事项
- 智能体主导创作流程，脚本仅提供文件管理和技术支持
- 写作、审计、分析等语言任务由智能体完成
- 状态文件是小说的唯一事实来源，创作时必须参考
- 每个章节完成后必须更新所有相关状态文件
- 审计不通过的章节必须修订后才能保存
- 充分利用智能体的语言理解和创作能力，避免为简单任务编写脚本

## 使用示例

### 示例 1: 创建新小说
- 功能: 初始化项目、生成设定、创建角色
- 执行方式: 智能体根据用户描述生成所有初始化文件
- 关键要点:
  ```
  用户: 我想写一本都市修仙小说，主角是程序员
  智能体:
  1. 创建项目结构
  2. 生成故事设定（现代修仙世界观）
  3. 创建主角角色卡（程序员背景、修仙天赋）
  4. 生成初始大纲（前 10 章）
  5. 初始化状态文件
  ```

### 示例 2: 续写章节
- 功能: 基于当前状态撰写下一章
- 执行方式: 智能体规划大纲 → 撰写正文 → 审计质量 → 更新状态
- 关键要点:
  ```
  用户: 写下一章，重点是主角突破境界
  智能体:
  1. 读取 state/world_state.md 检查主角当前境界
  2. 读取 outline.md 确认情节走向
  3. 生成章节大纲（突破过程、感悟、结果）
  4. 撰写正文（3000 字）
  5. 审计质量（境界提升合理性、伏笔连续性）
  6. 更新状态文件（新境界、新能力）
  7. 调用 word_counter.py 统计字数
  ```

### 示例 3: 导入已有小说续写
- 功能: 分析已有章节，逆向生成状态文件，继续创作
- 执行方式: 智能体分析文本 → 提取状态 → 续写
- 关键要点:
  ```
  用户: 续写这本已有的小说（提供已有章节文本）
  智能体:
  1. 分析已有章节，提取:
     - 角色信息 → 更新 character_matrix.md
     - 世界状态 → 更新 world_state.md
     - 关键事件 → 更新 chapter_summaries.md
     - 未解伏笔 → 更新 pending_hooks.md
  2. 生成文风指南
  3. 基于提取的状态续写下一章
  ```

### 示例 4: 质量审计
- 功能: 对已有章节进行全面质量检查
- 执行方式: 智能体对照审计清单逐项检查
- 关键要点:
  ```
  用户: 审计第 10 章的质量
  智能体:
  1. 读取章节内容
  2. 读取所有状态文件
  3. 对照 audit_checklist.md 检查:
     - 角色行为一致性
     - 物资连续性
     - 伏笔处理
     - 叙事节奏
     - 语言表达
  4. 输出审计报告（通过项、问题项、建议）
  ```
