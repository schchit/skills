# mbti-from-ai

分析用户与 AI 的聊天历史，根据沟通方式和思维模式推断 MBTI 人格类型，生成结构化 JSON 并在网页上展示可视化画像。

## 安装

将 `openclaw-skill/` 整个文件夹复制到 OpenClaw 的 skills 目录：

```bash
cp -r openclaw-skill/ ~/.openclaw/skills/mbti-from-ai/
```

或者创建符号链接：

```bash
ln -s /path/to/mbti-from-ai/openclaw-skill ~/.openclaw/skills/mbti-from-ai
```

## 使用

在 OpenClaw 中输入：

```
/mbti
```

## 文件结构

```
openclaw-skill/
├── SKILL.md              ← 主 Skill 定义（OpenClaw 读取的入口）
├── skill.json            ← Skill 元数据（名称、版本、触发词等）
├── README.md             ← 本文件
├── TESTING.md            ← 测试指南
└── scripts/
    ├── discover-sessions.sh   ← Step 1: 扫描会话文件
    ├── extract-messages.sh    ← Step 2: 提取用户消息
    └── encode-and-open.sh     ← Step 4: 编码并打开浏览器
```

