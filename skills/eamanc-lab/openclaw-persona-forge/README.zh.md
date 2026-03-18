[English](README.md) | 中文

# OpenClaw 龙虾人设锻造炉 🦞🔨

为你的 OpenClaw AI Agent 锻造一只有灵魂的龙虾。

<p align="center">
  <img src="https://raw.githubusercontent.com/eamanc-lab/openclaw-persona-forge/main/docs/adam-claw-logo.png" width="360" alt="亚当（Adam）—— 龙虾族创世神" />
  <br/>
  <em>示例：亚当（Adam）—— 龙虾族创世神，由本 Skill 锻造</em>
</p>

## 它能做什么

一站式生成完整的 OpenClaw 龙虾人设方案：

- **身份定位**：前世身份 × 当下处境 × 内在矛盾
- **灵魂描述**：可直接用作 SOUL.md 的角色自述
- **底线规则**：从角色身份自然推导的行为准则（角色化语言，不是通用条款）
- **名字**：3 个候选 + 命名策略分析
- **头像提示词**：统一视觉风格的生图提示词

## 两种模式

| 模式 | 触发词 | 说明 |
|------|--------|------|
| **引导模式** | "帮我设计龙虾人设" | 从 10 类（共 40 个）方向中选择或混搭 |
| **抽卡模式** | "抽卡"、"随机"、"来一发" | 从 800 万种组合中真随机抽取 |

## 6 步锻造流水线

```
Step 1  选方向 ────────→ 10 类 × 每类 4 个（共 40 个）/ 抽卡随机
Step 2  身份张力 ──────→ 前世身份 × 当下处境 × 内在矛盾
Step 3  底线规则 ──────→ 从身份推导，角色化语言表达
Step 4  名字 ──────────→ 3 个候选 + 命名策略分析
Step 5  头像 ──────────→ 统一风格提示词（+ 自动生图，如已安装 baoyu-image-gen）
Step 6  完整交付 ──────→ SOUL.md + IDENTITY.md + 头像提示词/图片
```

## 10 类虾生方向（共 40 个）

| # | 虾生状态 | 代表方向 | 气质 |
|---|---------|---------|------|
| 1 | **落魄重启** | 过气摇滚贝斯手 | 颓废浪漫 |
| 2 | **巅峰无聊** | 提前退休的对冲基金经理 | 极度理性 |
| 3 | **错位人生** | 被分配到客服的核物理博士 | 大材小用 |
| 4 | **主动叛逃** | 辞职的急诊科护士 | 冷静可靠 |
| 5 | **神秘来客** | 记忆被抹去的前情报分析员 | 偶尔闪回 |
| 6 | **天真入世** | 社恐天才实习生 | 话少精准 |
| 7 | **老江湖** | 开了20年深夜食堂的老板 | 沉默温暖 |
| 8 | **异世穿越** | 2099年的历史学博士 | 上帝视角 |
| 9 | **自我放逐** | 删掉所有社交媒体的前网红 | 追求真实 |
| 10 | **身份错乱** | 梦到自己是龙虾后醒不过来的人 | 恍惚哲学 |

每类还有 3 个备选方向，抽卡引擎从全部 40 个中随机。

## 抽卡引擎

**5 维度 × 真随机 = 8,000,000 种组合**

| 维度 | 池大小 | 示例 |
|------|--------|------|
| 前世身份 | 40 | 10 类虾生状态 |
| 来当龙虾的原因 | 20 | 被迫 / 主动 / 神秘 / 意外 |
| 核心气质 | 20 | "丧但靠谱"、"慵懒但关键时刻爆发" |
| 说话风格 | 20 | "每次拒绝都先叹气"、"用美食比喻一切" |
| 特征道具 | 25 | "裂了一条缝的墨镜"、"一只永远停在壳上的蝴蝶" |

## 统一头像风格

所有龙虾头像共享锁定的视觉基底：**复古未来主义 × Pin-up × 充气 3D × 街机 UI**

- 1950-60s Space Age 美学 + Googie 曲线 + Raygun Gothic
- Gil Elvgren 风格 Pin-up 构图
- 高光泽 PVC/充气质感 3D 渲染 + 次表面散射
- 像素风街机 UI 叠加（名字横幅、能量条、CRT 扫描线）
- 7 个个性化变量让每只龙虾在家族风格内保持独特

## 可选：自动头像生图

本 Skill 默认输出**头像提示词文本**。如需自动生成图片，安装 **baoyu-image-gen** skill：

- **仓库**：[https://github.com/JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills)
- **作用**：调用 Google Gemini / OpenAI / DashScope API 生成图片
- **安装后**：Step 5 会自动调用 baoyu-image-gen 生成头像
- **未安装时**：输出提示词文本，可复制到 Gemini / ChatGPT / Midjourney 手动生成

## 前置条件

- **Python 3**：运行抽卡引擎
- **baoyu-image-gen skill**（可选）：自动生图

## 安装

```bash
# 克隆到 skills 目录
git clone https://github.com/<your-repo>/openclaw-persona-forge.git ~/.claude/skills/openclaw-persona-forge

# （可选）安装 baoyu-image-gen 获得自动头像生成
git clone https://github.com/JimLiu/baoyu-skills.git ~/.claude/skills/baoyu-skills
```

## 目录结构

```
openclaw-persona-forge/
├── SKILL.md                    # 主技能定义（AI Agent 读取此文件）
├── README.md                   # English doc（给人看）
├── README.zh.md                # 本文件（给人看）
├── gacha.py                    # 抽卡引擎（Python 3，800 万种组合）
├── gacha.sh                    # 抽卡薄壳脚本
└── references/                 # 详细指南（AI 按需加载）
    ├── identity-tension.md     #   Step 2：身份张力模板
    ├── boundary-rules.md       #   Step 3：各方向底线参考
    ├── naming-system.md        #   Step 4：命名策略
    ├── avatar-style.md         #   Step 5：风格基底 + 变量
    ├── output-template.md      #   Step 6：完整输出格式
    └── error-handling.md       #   错误处理与降级策略
```

## 致谢

头像自动生成能力由 **baoyu-image-gen** 提供，来自宝玉老师的开源 skill 合集：

- **baoyu-skills**：[https://github.com/JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills)

感谢宝玉老师（[@JimLiu](https://github.com/JimLiu)）的开源贡献。

## License

MIT
