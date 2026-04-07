---
name: xhs-publisher
description: 小红书通用自动发帖技能。全流程自动化：AI生成帖子内容 → 生成封面图（6套风格模板）→ Puppeteer自动发布到小红书创作者中心。内置 stealth 反风控、人类化打字模拟。适合运营任意垂直领域小红书账号（科技、生活、美食、旅行、节日、知识分享等）。当用户需要自动发小红书帖子、生成封面图、或定时发帖时使用。
---

# xhs-publisher · 小红书自动发帖

> 你说主题，AI 写文案、配封面、发帖子。一句话搞定，不用懂技术。

---

## ✨ 为什么选这个 skill？

市面上的小红书自动化工具要么需要复杂配置，要么发完就被风控限流。这个 skill 做了三件别人没做的事：

**1. 真正的反风控**
内置 `puppeteer-extra-plugin-stealth`，自动处理几十项浏览器指纹特征（webdriver、plugins、languages、UA……），让平台识别不出是自动化程序。

**2. 人类化操作模拟**
打字速度随机变化（30~150ms/字），中文通过输入法模拟，偶尔停顿思考——行为上和真人发帖无法区分。

**3. AI 全程生成内容**
不只是自动发，文案、封面、话题标签全部由 AI 生成，你只需要说一个主题。

---

## 🚀 快速开始（小白版）

**第一步：说你想发什么**

```
帮我发一篇清明节的小红书
帮我发一篇职场新人避坑的帖子
帮我发一篇推荐深圳周末去处的小红书
```

**第二步：确认封面和内容**

AI 会先把封面图和文案发给你预览，你觉得 OK 就说"发布"。

**第三步：首次需要登录**

第一次用时，AI 会让你输入手机号 + 验证码登录小红书。登录一次后自动保存，**约 7 天内不用再登录**。

> 登录信息只存在你自己的电脑上，不会上传任何地方。

---

## 🎨 6 套封面模板

根据标题自动匹配，同一标题每次用同一套模板，保持账号风格统一。

| 模板 | 配色 | 适合内容 |
|------|------|----------|
| 🔴 珊瑚红·撞色 | 红白对撞，冲击力强 | 热点、节日、话题性内容 |
| ⬜ 奶油白·极简 | 白底黑字，高级留白 | 知识干货、深度观点 |
| 🌿 墨绿·自然风 | 深绿奶白，清新文艺 | 人文、旅行、生活方式 |
| 🌊 深蓝·知性风 | 深海蓝渐变，沉稳理性 | 科普、职场、财经 |
| 💛 柠黄·活力风 | 明黄黑字，年轻活泼 | 美食、穿搭、娱乐 |
| 💜 丁香紫·治愈风 | 薰衣草紫，圆润柔和 | 情感、心理、治愈系 |

封面尺寸 **1080×1440px**，符合小红书图文比例标准。

---

## 🛠️ 第一次用的准备工作

### 1. 安装字体（必须）

封面中文渲染需要 Noto Sans SC 字体，否则文字显示为方块。

```bash
mkdir -p ~/.fonts
# 下载 NotoSansSC-Regular.otf 和 NotoSansSC-Bold.otf 放入 ~/.fonts/
# 详细步骤见 references/setup.md
```

### 2. 安装依赖

```bash
cd skills/xhs-publisher/scripts
npm install
```

> ⚠️ **国内网络 Puppeteer 下载 Chrome 超时？** 三选一：

**方案 A：用国内镜像（推荐）**
```bash
npm run install:cn
```

**方案 B：跳过下载，用系统已安装的 Chrome**
```bash
npm run install:skip
```
脚本会自动探测系统 Chrome 路径，支持：
- **macOS**：`/Applications/Google Chrome.app`
- **Windows**：`C:\Program Files\Google\Chrome\...`
- **Linux**：`/usr/bin/google-chrome`、`/usr/bin/chromium-browser`、`/snap/bin/chromium` 等

也可以手动指定路径：
```bash
export PUPPETEER_EXECUTABLE_PATH=/path/to/your/chrome
```

**方案 C：先安装 Chromium 再跳过下载**
```bash
# Ubuntu / Debian
sudo apt-get install -y chromium-browser
npm run install:skip

# macOS (Homebrew)
brew install --cask chromium
npm run install:skip
```

**验证安装是否成功：**
```bash
npm run check
# 输出示例：Chrome: /usr/bin/google-chrome
```

---

## ❓ 常见问题

**Q：发帖会被风控吗？**
风险已大幅降低。内置 stealth 反指纹 + 人类化行为模拟，是目前最接近真人操作的方案。但小红书风控持续升级，建议每天发帖不超过 3 篇，不要在短时间内连续发。

**Q：会不会发出去奇怪的内容？**
不会。每次发布前都有预览确认环节。另外脚本内置内容安全检查，自动拦截人身攻击、煽动对立等违规内容，避免封号风险。

**Q：登录信息安全吗？**
安全。Session 只保存在本地 `~/.openclaw-sessions/xiaohongshu/`，不经过任何第三方服务器。

**Q：发帖失败了怎么排查？**
失败时会自动截图保存到工作目录（`xhs_pre_publish.png`），可以直接看到发布前的页面状态。

**Q：话题标签加不上怎么办？**
v1.2.1 已修复话题选择器，使用小红书真实 DOM 结构精确匹配。如果仍然失败，说明小红书更新了页面结构，欢迎提 issue。

---

## 👨‍💻 开发者文档

### 安装

```bash
npx clawhub@latest install xhs-publisher-pro
```

### 基础用法

```js
const { generateCoverImage, publishPost } = require('./scripts/xhs_publisher.js');

// 生成封面图
const imgPath = await generateCoverImage(
  '五一去哪儿玩？这几个地方别错过',          // 标题（≤20字）
  '人少景美还不贵\n亲测三个宝藏目的地\n每个都值得去一次', // 副标题（\n换行）
  '/tmp/xhs_cover.png'                       // 输出路径
);

// 发布帖子
const result = await publishPost({
  title: '五一去哪儿玩？这几个地方别错过',
  content: '每年五一都在纠结去哪玩...',       // 正文（不含话题标签）
  topics: ['五一旅游', '旅行攻略', '小众目的地'], // 最多 5 个话题
  imagePath: imgPath,
  phone: '13812345678',                      // session 失效时自动触发登录
  askCodeFn: async (prompt) => await askUser(prompt), // 返回 6 位验证码
});

console.log(result.success, result.postUrl);
```

### API 文档

| 函数 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `generateCoverImage(title, subtitle, outputPath, footer?)` | 标题、副标题、输出路径、可选署名 | `Promise<string>` 输出路径 | 生成 1080×1440px 封面图 |
| `publishPost(options)` | 见下方 | `Promise<{ success, postUrl }>` | 发帖主函数，含安全检查和登录引导 |
| `checkContentSafety(title, content)` | 标题、正文 | `{ safe, reason }` | 独立内容安全检查 |
| `detectPageState(page)` | Puppeteer page | `{ loggedIn, blocked, reason }` | 检测页面登录/风控状态 |
| `isSessionLikelyValid()` | — | `boolean` | 判断 session 是否在 7 天有效期内 |

**publishPost 参数：**

```ts
{
  title: string,       // 标题，≤20 字
  content: string,     // 正文，200~400 字效果最佳
  topics: string[],    // 话题标签，最多 5 个，不含 #
  imagePath: string,   // 封面图绝对路径
  phone?: string,      // 手机号，session 失效时使用
  askCodeFn?: (prompt: string) => Promise<string>, // 向用户索取验证码
}
```

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `XHS_PROFILE_DIR` | Session 存储目录 | `~/.openclaw-sessions/xiaohongshu` |

### 版本历史

| 版本 | 更新内容 |
|------|----------|
| v1.2.1 | 修复话题选择器（使用真实 DOM 结构）；修复 postUrl 变量作用域 bug |
| v1.2.0 | humanType 支持中文；字体路径动态查找；段落空行逻辑优化；话题上限 3→5；publishPost 返回 postUrl |
| v1.1.0 | 引入 stealth 反指纹插件；人类化打字速度；随机视口 |
| v1.0.0 | 初始版本 |

---

更多配置说明见 [references/setup.md](references/setup.md)，写作规范见 [references/posting-guide.md](references/posting-guide.md)。
