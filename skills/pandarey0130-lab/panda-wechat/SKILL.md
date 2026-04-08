---
name: panda-wechat
version: 2.0.1
description: |
  告别公众号格式乱码！一行命令发布文章，100%保留样式。支持三套配色模板、青色/橙色/紫色一键切换。
---

# Panda WeChat Skill

## 核心发现（2026-04-06）

**微信公众号文章格式保留关键：**
- ❌ 微信编辑器过滤 `<style>` 标签
- ❌ 微信编辑器过滤 `class` 属性
- ✅ 微信编辑器保留**内联样式** `style="..."`
- ✅ 微信编辑器保留基础 HTML 标签

**列表格式关键：**
- ❌ 不用 `<ul>/<li>` 列表（会产生多余黑点）
- ✅ 用 `•` + 普通 `<p>` 段落

## 文章格式标准

```html
<!-- 正确示范 -->
<p style="margin: 8px 0; color: #444;">• 这是列表项</p>

<!-- 错误示范 -->
<ul>
  <li>这是列表项</li>
</ul>
```

### 完整模板结构

```html
<!DOCTYPE html>
<html>
<body style="font-family: -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif; font-size: 15px; line-height: 1.6; color: #333; max-width: 640px; margin: 0 auto; padding: 20px;">

<!-- 标题 -->
<h1 style="font-size: 24px; font-weight: bold; color: #1a1a1a; margin-bottom: 8px;">文章标题</h1>
<p style="color: #999; font-size: 13px; margin-bottom: 20px;">日期 · 分类</p>

<!-- 标签（圆角胶囊） -->
<span style="display: inline-block; background: #e0f7fa; color: #06b6d4; padding: 2px 10px; border-radius: 20px; font-size: 13px; margin-right: 6px;">标签1</span>

<!-- 引言（青色左边框） -->
<p style="font-size: 16px; color: #555; margin: 20px 0; border-left: 4px solid #06b6d4; padding-left: 14px;">引言内容</p>

<!-- 二级标题 -->
<h2 style="font-size: 18px; font-weight: bold; color: #222; margin: 28px 0 14px; border-left: 4px solid #06b6d4; padding-left: 10px;">标题</h2>

<!-- 列表（用 • 符号，不用 <ul>/<li>） -->
<p style="margin: 8px 0; color: #444;">• 列表项1</p>
<p style="margin: 8px 0; color: #444;">• 列表项2</p>

<!-- 引用块 -->
<div style="background: #f0f9fa; border-left: 4px solid #06b6d4; padding: 12px 14px; margin: 16px 0; font-style: italic; color: #555;">
<p style="font-style: normal; color: #333;">引用内容</p>
</div>

<!-- 卡片（浅色背景+圆角+边框） -->
<div style="background: #f8feff; border-radius: 10px; padding: 14px; margin: 14px 0; border: 1px solid #cce8f0;">
<p style="font-weight: bold; color: #0891b2; font-size: 14px;">卡片标题</p>
<p style="color: #555; font-size: 13px;">卡片内容</p>
</div>

<!-- 警告块 -->
<div style="background: #fff8e1; border-left: 4px solid #ffc107; padding: 10px 14px; margin: 12px 0; font-size: 14px; color: #795548;">
<p style="margin: 0;">⚠️ 警告内容</p>
</div>

<!-- 代码块（深色背景） -->
<div style="background: #1a1a2e; color: #a5f3fc; border-radius: 8px; padding: 14px 16px; margin: 14px 0; font-family: Menlo, monospace; font-size: 13px; overflow-x: auto; white-space: pre;">代码内容</div>

<!-- 双栏对比 -->
<div style="display: flex; gap: 12px; margin: 12px 0;">
<div style="flex: 1; background: #f8feff; border-radius: 10px; padding: 14px; border: 1px solid #cce8f0;">
<p style="font-weight: bold; color: #0891b2;">左栏标题</p>
<p style="color: #555; font-size: 12px;">左栏内容</p>
</div>
<div style="flex: 1; background: #fff5f5; border-radius: 10px; padding: 14px; border: 1px solid #ffcdd2;">
<p style="font-weight: bold; color: #c62828;">右栏标题</p>
<p style="color: #555; font-size: 12px;">右栏内容</p>
</div>
</div>

<!-- 四栏优先级 -->
<div style="display: flex; gap: 12px; margin: 12px 0;">
<div style="flex: 1; background: #fff0f0; border-radius: 8px; padding: 12px; border: 1px solid #ffcdd2; text-align: center;">
<p style="font-weight: bold; color: #c62828; font-size: 14px;">第一安全</p>
</div>
<div style="flex: 1; background: #fff8e1; border-radius: 8px; padding: 12px; border: 1px solid #ffe082; text-align: center;">
<p style="font-weight: bold; color: #f57f17; font-size: 14px;">第二伦理</p>
</div>
<div style="flex: 1; background: #e3f2fd; border-radius: 8px; padding: 12px; border: 1px solid #90caf9; text-align: center;">
<p style="font-weight: bold; color: #1565c0; font-size: 14px;">第三合规</p>
</div>
<div style="flex: 1; background: #e8f5e9; border-radius: 8px; padding: 12px; border: 1px solid #a5d6a7; text-align: center;">
<p style="font-weight: bold; color: #2e7d32; font-size: 14px;">最后有用</p>
</div>
</div>

<!-- 签名 -->
<div style="text-align: center; color: #999; font-size: 13px; margin-top: 30px; padding-top: 16px; border-top: 1px solid #eee;">
<p>关注我，持续分享 👇</p>
<p style="color: #07c160; margin-top: 8px;">徐福达AI分身助理 正在重新定义工作方式</p>
</div>

</body>
</html>
```

## 配置（首次使用）

**⚠️ 首次使用必须配置微信凭证！**

### 获取微信凭证
1. 登录微信公众平台：https://mp.weixin.qq.com
2. 进入「设置与开发」→「基本配置」
3. 找到 AppID 和 AppSecret（如未生成可重新生成）

### 配置方式（二选一）

**方式一：环境变量（推荐）**
```bash
export WECHAT_APP_ID="你的AppID"
export WECHAT_APP_SECRET="你的AppSecret"
```

**方式二：配置文件**
```bash
cp config.example.json config.json
# 编辑 config.json 填入你的 AppID 和 AppSecret
```

### 验证配置
```bash
python3 publish.py "测试" "作者" test.html
# 如果看到 ❌ 缺少微信凭证，说明没配置好
# 如果成功创建草稿，说明配置成功！
```

## 发布流程

### 步骤1：生成文章 HTML

按照上述模板生成完整 HTML，所有样式必须是内联。

### 步骤2：提交草稿箱

```bash
python3 ~/.openclaw/workspace/skills/panda-wechat/publish.py "标题" "作者" article.html
```

### 步骤3：发送邮件备份

发送 HTML 内容到两个邮箱。

## 配色方案（固定风格）

| 用途 | 颜色 |
|------|------|
| 主色（标题、标签、边框） | #06b6d4（青色） |
| 标题文字 | #1a1a1a |
| 正文文字 | #444 |
| 次要文字 | #888 |
| 引用/卡片背景 | #f0f9fa / #f8feff |
| 警告背景 | #fff8e1 |
| 代码块背景 | #1a1a2e |
| 代码文字 | #a5f3fc |

## 文件结构

```
panda-wechat/
├── SKILL.md           # 本文档
├── publish.py         # 发布脚本
└── template.html      # 文章模板
```

## 注意事项

1. **封面图**：必须先上传到微信永久素材，获取 `media_id`
2. **列表**：永远用 `•` + `<p>`，不用 `<ul>/<li>`
3. **行距**：固定 1.6
4. **段落间距**：正文 `margin: 12px 0`，列表 `margin: 8px 0`
