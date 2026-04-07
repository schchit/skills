#!/usr/bin/env node
/**
 * xhs-publisher · 小红书通用发帖脚本
 *
 * 功能：生成封面图 + 自动发布到小红书创作者中心
 * 适用于任意主题，不限领域
 */

const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());
const fs = require('fs');
const path = require('path');
const os = require('os');

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// ============================================================
// 跨平台 Chrome/Chromium 路径探测
// 优先级：环境变量 > 系统已安装 > Puppeteer 自带（自动下载）
// ============================================================
function detectChromePath() {
  // 1. 用户通过环境变量手动指定
  if (process.env.PUPPETEER_EXECUTABLE_PATH) {
    return process.env.PUPPETEER_EXECUTABLE_PATH;
  }

  const platform = os.platform();

  // 2. 各平台候选路径
  const candidates = {
    darwin: [
      '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
      '/Applications/Chromium.app/Contents/MacOS/Chromium',
      '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
      '/usr/bin/chromium',
    ],
    win32: [
      'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
      'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
      process.env.LOCALAPPDATA ? path.join(process.env.LOCALAPPDATA, 'Google\\Chrome\\Application\\chrome.exe') : null,
      'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
      'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
    ].filter(Boolean),
    linux: [
      '/usr/bin/google-chrome',
      '/usr/bin/google-chrome-stable',
      '/usr/bin/chromium',
      '/usr/bin/chromium-browser',
      '/snap/bin/chromium',
      '/usr/local/bin/chromium',
      '/opt/google/chrome/chrome',
    ],
  };

  const paths = candidates[platform] || candidates.linux;
  for (const p of paths) {
    try {
      if (fs.existsSync(p)) {
        console.log(`🌐 使用系统 Chrome：${p}`);
        return p;
      }
    } catch { /* 忽略权限错误 */ }
  }

  // 3. 没找到系统 Chrome，返回 null 让 Puppeteer 用自带的（需提前下载）
  console.log('ℹ️ 未找到系统 Chrome，使用 Puppeteer 自带浏览器（需确保已完成 npm install）');
  return null;
}

/** 构造 Puppeteer launch 配置（跨平台通用） */
function buildLaunchOptions(extra = {}) {
  const chromePath = detectChromePath();
  const isLinux = os.platform() === 'linux';

  const args = [
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-dev-shm-usage',         // Linux Docker/CI 必须
    '--disable-gpu',                   // headless 模式稳定性
    '--disable-blink-features=AutomationControlled',
    '--font-render-hinting=none',      // 封面图字体渲染
    '--no-first-run',
    '--no-default-browser-check',
  ];

  // Windows 下不需要 --no-sandbox（反而可能出错）
  const safeArgs = os.platform() === 'win32'
    ? args.filter(a => !a.includes('sandbox') && !a.includes('setuid'))
    : args;

  return {
    headless: true,
    args: safeArgs,
    ...(chromePath ? { executablePath: chromePath } : {}),
    ...extra,
  };
}

/** 模拟人类打字：支持中英文混合，每个字符随机延迟，偶尔有短暂停顿 */
async function humanType(page, selector_or_element, text) {
  const el = typeof selector_or_element === 'string'
    ? await page.$(selector_or_element)
    : selector_or_element;
  if (!el) return;

  // 中文字符无法逐字 type，改用剪贴板粘贴 + 随机停顿模拟
  // 将文本按"中文段落"和"英文/符号片段"切分，分段处理
  const segments = text.match(/[\u4e00-\u9fa5\u3000-\u303f\uff00-\uffef]+|[^\u4e00-\u9fa5\u3000-\u303f\uff00-\uffef]+/g) || [];

  for (const seg of segments) {
    const isChinese = /[\u4e00-\u9fa5]/.test(seg);
    if (isChinese) {
      // 中文段：剪贴板写入后粘贴，模拟真实输入法行为
      await page.evaluate((s) => {
        const dt = new DataTransfer();
        dt.setData('text/plain', s);
        document.activeElement?.dispatchEvent(new ClipboardEvent('paste', { clipboardData: dt, bubbles: true }));
      }, seg);
      // 粘贴后随机停顿，模拟思考节奏
      await sleep(100 + Math.random() * 300);
    } else {
      // 英文/符号/换行：逐字符 type，随机延迟
      for (const char of seg) {
        await el.type(char, { delay: 30 + Math.random() * 100 });
        if (Math.random() < 0.08) await sleep(150 + Math.random() * 350);
      }
    }
  }
}

// ============================================================
// 内容安全过滤
// 小红书平台对以下内容敏感，发布前必须过滤
// ============================================================

// 高风险词：涉及人身攻击、站队煽动、不实指控
const BLOCKED_PATTERNS = [
  /傻[逼X比]/,
  /智障|脑残|废物|垃圾人/,
  /死[去全]|去死|滚[出去]/,
  /你[们]?支持谁|你[们]?站哪边|你[们]?选[哪边谁]/,  // 煽动站队
  /谁对谁错|谁[更]?有理|谁[更]?过分/,               // 煽动对立
  /[强逼]行侵权|故意侵权|明知故犯/,                 // 未经证实的定性指控
  /[黑白]粉|水军|控评/,                             // 煽动粉圈对立
];

// 敏感话题词：可发但需谨慎处理（不能用对立煽动视角）
const SENSITIVE_TOPICS = [
  '版权纠纷', '艺人纠纷', '明星争议', '维权', '道歉',
  '出轨', '离婚', '抄袭', '造假', '诈骗',
];

/**
 * 内容安全检查
 * @param {string} title
 * @param {string} content
 * @returns {{ safe: boolean, reason: string }}
 */
function checkContentSafety(title, content) {
  const fullText = title + '\n' + content;

  // 高风险词：直接拦截
  for (const pattern of BLOCKED_PATTERNS) {
    if (pattern.test(fullText)) {
      return { safe: false, reason: `内容包含违禁表达（匹配规则：${pattern}），请修改后重试` };
    }
  }

  // 标题不得含煽动对立词
  const opinionPhrases = ['你支持谁', '你站哪边', '谁对谁错', '谁更有理', '我支持'];
  for (const phrase of opinionPhrases) {
    if (title.includes(phrase)) {
      return { safe: false, reason: `标题含煽动对立词「${phrase}」，建议改为陈述/提问视角，如「这件事你怎么看？」` };
    }
  }

  // 强烈倾向性定性：无论是否涉及敏感话题，一律拦截
  const biasedPhrases = ['全是他的错', '全是她的错', '活该', '罪有应得', '早该被', '咎由自取', '死有余辜'];
  for (const phrase of biasedPhrases) {
    if (content.includes(phrase)) {
      const hitSensitive = SENSITIVE_TOPICS.filter(t => fullText.includes(t));
      const context = hitSensitive.length > 0 ? `涉及敏感话题「${hitSensitive.join('、')}」时，` : '';
      return { safe: false, reason: `${context}正文含强烈倾向性定性「${phrase}」，容易引发平台风控，建议改为客观陈述` };
    }
  }

  return { safe: true, reason: '' };
}

// ============================================================
// 配置项
// ============================================================
// Session 目录：通过环境变量 XHS_PROFILE_DIR 自定义，默认为 ~/.openclaw-sessions/xiaohongshu
const PROFILE_DIR = process.env.XHS_PROFILE_DIR ||
  path.join(os.homedir(), '.openclaw-sessions', 'xiaohongshu');
// ============================================================

// 确保 session 目录存在
function ensureProfileDir() {
  if (!fs.existsSync(PROFILE_DIR)) {
    fs.mkdirSync(PROFILE_DIR, { recursive: true });
    console.log('📁 Session 目录已创建:', PROFILE_DIR);
  }
}

// 插入话题标签
async function insertTopics(page, topics) {
  const MAX_TOPICS = 5;
  if (topics.length > MAX_TOPICS) {
    console.warn(`⚠️ 话题数量 ${topics.length} 超过上限，自动截取前 ${MAX_TOPICS} 个`);
    topics = topics.slice(0, MAX_TOPICS);
  }

  for (const topic of topics) {
    const editables = await page.$$('[contenteditable="true"]');
    const editor = editables[editables.length - 1];
    if (!editor) break;

    await editor.click();
    await page.keyboard.down('Control');
    await page.keyboard.press('End');
    await page.keyboard.up('Control');
    await sleep(300);

    // 输入 # + 话题名，触发推荐面板
    await page.keyboard.type(' #', { delay: 200 });
    await sleep(400);
    for (const char of topic) {
      await page.keyboard.type(char, { delay: 120 });
    }

    // 等待推荐面板出现（最多 5 秒）
    let selected = false;
    for (let attempt = 0; attempt < 10 && !selected; attempt++) {
      await sleep(500);

      // 策略1：在 .recommend-topic-wrapper 中找精确匹配或前缀匹配的 span.tag
      selected = await page.evaluate((topicName) => {
        const tags = document.querySelectorAll('.recommend-topic-wrapper .tag');
        for (const tag of tags) {
          const text = (tag.textContent || '').replace(/^#/, '').trim();
          if (text === topicName || text.startsWith(topicName)) {
            tag.click();
            return true;
          }
        }
        return false;
      }, topic);

      if (selected) {
        console.log('✅ 话题已选（推荐面板）:', topic);
        break;
      }

      // 策略2：找 .suggestion span
      selected = await page.evaluate((topicName) => {
        const suggestions = document.querySelectorAll('.suggestion');
        for (const s of suggestions) {
          const text = (s.textContent || '').replace(/^#/, '').trim();
          if (text === topicName || text.startsWith(topicName)) {
            s.click();
            return true;
          }
        }
        return false;
      }, topic);

      if (selected) {
        console.log('✅ 话题已选（suggestion）:', topic);
      }
    }

    if (!selected) {
      // 降级：直接按 Enter 确认当前输入
      await page.keyboard.press('Enter');
      await sleep(300);
      console.log('⚠️ 话题推荐面板未匹配，已用 Enter 兜底:', topic);
    }

    await sleep(500);
  }
}

// HTML 特殊字符转义（防止标题/副标题中含 < > & 等字符破坏模板结构）
function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
    .replace(/\n/g, '<br>');
}

/**
 * 生成封面图
 * @param {string} title      - 标题（≤20字）
 * @param {string} subtitle   - 副标题，用 \n 换行，30-50字
 * @param {string} outputPath - 输出路径（绝对路径，.png）
 * @param {string} [footer]   - 可选底部署名，默认留空
 * @returns {Promise<string>} 输出路径
 */
async function generateCoverImage(title, subtitle, outputPath, footer = '') {
  const hash = [...title].reduce((a, c) => a + c.charCodeAt(0), 0);
  const idx = hash % 6;

  const templateNames = ['珊瑚红·撞色','奶油白·极简','墨绿·自然风','深蓝·知性风','柠黄·活力风','丁香紫·治愈风'];
  console.log(`🎨 封面模板: ${templateNames[idx]} (${idx+1}/6)`);

  // 对用户输入进行 HTML 转义，防止特殊字符破坏模板结构
  const safeTitle = escHtml(title);
  const safeSubtitle = escHtml(subtitle);
  const safeFooter = escHtml(footer);

  const styles = [
    // 0: 珊瑚红·撞色 — 上下撞色分割，大标题居中，冲击力强
    `*{margin:0;padding:0;box-sizing:border-box;}
    body{width:1080px;height:1440px;background:#FF5A5F;
      font-family:'Noto Sans SC',sans-serif;
      display:flex;flex-direction:column;position:relative;overflow:hidden;}
    .top{flex:1.1;background:#FF5A5F;display:flex;flex-direction:column;
      align-items:center;justify-content:flex-end;padding:0 80px 60px;}
    .bottom{flex:1;background:#FFF8F0;display:flex;flex-direction:column;
      align-items:center;justify-content:flex-start;padding:60px 80px 0;}
    .tag{font-size:28px;color:rgba(255,255,255,0.75);letter-spacing:4px;
      text-transform:uppercase;margin-bottom:28px;font-weight:500;}
    .title{font-size:108px;font-weight:900;line-height:1.15;color:#fff;
      text-align:center;word-break:break-all;
      text-shadow:0 4px 24px rgba(0,0,0,0.15);}
    .divider{width:60px;height:5px;background:#FF5A5F;border-radius:3px;margin:48px auto 40px;}
    .subtitle{font-size:42px;color:#333;line-height:1.7;text-align:center;max-width:860px;}
    .footer{position:absolute;bottom:52px;left:0;right:0;text-align:center;
      font-size:28px;color:#bbb;letter-spacing:1px;}`,

    // 1: 奶油白·极简 — 白底黑字，大面积留白，高级感
    `*{margin:0;padding:0;box-sizing:border-box;}
    body{width:1080px;height:1440px;background:#FAFAF8;
      font-family:'Noto Sans SC',sans-serif;
      display:flex;flex-direction:column;justify-content:center;
      padding:120px 100px;position:relative;overflow:hidden;}
    .bar{width:56px;height:8px;background:#1A1A1A;border-radius:4px;margin-bottom:60px;}
    .title{font-size:112px;font-weight:900;line-height:1.18;color:#1A1A1A;
      margin-bottom:52px;letter-spacing:-2px;}
    .line{width:100%;height:1px;background:#E0E0E0;margin-bottom:48px;}
    .subtitle{font-size:44px;color:#666;line-height:1.8;max-width:840px;}
    .num{position:absolute;top:100px;right:100px;font-size:200px;font-weight:900;
      color:rgba(0,0,0,0.04);line-height:1;letter-spacing:-8px;user-select:none;}
    .footer{position:absolute;bottom:60px;left:100px;
      font-size:28px;color:#ccc;letter-spacing:2px;}`,

    // 2: 墨绿·自然风 — 墨绿底，奶白大字，清新文艺
    `*{margin:0;padding:0;box-sizing:border-box;}
    body{width:1080px;height:1440px;background:#2D4A3E;
      font-family:'Noto Sans SC',sans-serif;
      display:flex;flex-direction:column;justify-content:center;
      padding:120px 90px;position:relative;overflow:hidden;}
    .circle1{position:absolute;top:-160px;right:-160px;width:500px;height:500px;border-radius:50%;
      background:rgba(255,255,255,0.04);}
    .circle2{position:absolute;bottom:-100px;left:-100px;width:340px;height:340px;border-radius:50%;
      background:rgba(255,255,255,0.03);}
    .leaf{position:absolute;top:60px;left:60px;width:160px;height:160px;border-radius:50% 0 50% 0;background:linear-gradient(135deg,rgba(168,197,184,0.35),rgba(168,197,184,0.08));transform:rotate(-30deg);}
    .label{font-size:28px;color:#A8C5B8;letter-spacing:4px;margin-bottom:44px;font-weight:500;}
    .title{font-size:110px;font-weight:900;line-height:1.2;color:#F5F0E8;
      margin-bottom:48px;}
    .dots{display:flex;gap:14px;margin-bottom:44px;}
    .dot{width:12px;height:12px;border-radius:50%;background:#A8C5B8;}
    .subtitle{font-size:43px;color:rgba(245,240,232,0.65);line-height:1.75;max-width:840px;}
    .footer{position:absolute;bottom:60px;left:90px;font-size:28px;color:rgba(168,197,184,0.5);}`,

    // 3: 深蓝·知性风 — 深海蓝底，白字，理性沉稳
    `*{margin:0;padding:0;box-sizing:border-box;}
    body{width:1080px;height:1440px;
      background:linear-gradient(160deg,#0F2342 0%,#1A3A6E 60%,#0F2342 100%);
      font-family:'Noto Sans SC',sans-serif;
      display:flex;flex-direction:column;justify-content:center;
      padding:120px 90px;position:relative;overflow:hidden;}
    .arc{position:absolute;right:-180px;top:50%;transform:translateY(-50%);
      width:560px;height:560px;border-radius:50%;
      border:80px solid rgba(255,255,255,0.04);}
    .arc2{position:absolute;right:-100px;top:50%;transform:translateY(-50%);
      width:360px;height:360px;border-radius:50%;
      border:40px solid rgba(255,255,255,0.03);}
    .tag{display:inline-block;font-size:26px;color:#7EB8F7;letter-spacing:3px;
      border:1px solid rgba(126,184,247,0.4);padding:8px 24px;border-radius:4px;
      margin-bottom:48px;}
    .title{font-size:108px;font-weight:900;line-height:1.2;color:#fff;
      margin-bottom:48px;}
    .rule{width:80px;height:3px;background:linear-gradient(90deg,#7EB8F7,transparent);
      margin-bottom:44px;border-radius:2px;}
    .subtitle{font-size:43px;color:rgba(255,255,255,0.55);line-height:1.75;max-width:820px;}
    .footer{position:absolute;bottom:64px;left:90px;font-size:28px;
      color:rgba(255,255,255,0.2);letter-spacing:1px;}`,

    // 4: 柠黄·活力风 — 明黄底，黑字，年轻有活力
    `*{margin:0;padding:0;box-sizing:border-box;}
    body{width:1080px;height:1440px;background:#F9E84E;
      font-family:'Noto Sans SC',sans-serif;
      display:flex;flex-direction:column;justify-content:center;
      padding:120px 90px;position:relative;overflow:hidden;}
    .stripe{position:absolute;top:0;right:120px;width:28px;height:100%;
      background:rgba(0,0,0,0.06);}
    .stripe2{position:absolute;top:0;right:180px;width:14px;height:100%;
      background:rgba(0,0,0,0.03);}
    .bubble{position:absolute;bottom:-60px;right:-60px;width:320px;height:320px;
      border-radius:50%;background:rgba(0,0,0,0.05);}
    .num{position:absolute;top:80px;right:90px;width:120px;height:120px;
      background:rgba(0,0,0,0.07);transform:rotate(45deg);border-radius:8px;}
    .title{font-size:112px;font-weight:900;line-height:1.18;color:#1A1A1A;
      margin-bottom:48px;position:relative;z-index:1;}
    .bar{width:100%;height:5px;background:#1A1A1A;margin-bottom:44px;border-radius:3px;}
    .subtitle{font-size:44px;color:#333;line-height:1.75;max-width:840px;}
    .footer{position:absolute;bottom:60px;left:90px;font-size:28px;color:rgba(0,0,0,0.3);}`,

    // 5: 丁香紫·治愈风 — 薰衣草紫，圆润柔和，温柔治愈
    `*{margin:0;padding:0;box-sizing:border-box;}
    body{width:1080px;height:1440px;
      background:linear-gradient(145deg,#EDE0F5 0%,#F5E8FF 50%,#E8E0F8 100%);
      font-family:'Noto Sans SC',sans-serif;
      display:flex;flex-direction:column;align-items:center;justify-content:center;
      padding:120px 80px;position:relative;overflow:hidden;}
    .blob1{position:absolute;top:-80px;right:-80px;width:400px;height:400px;border-radius:50%;
      background:rgba(180,130,220,0.18);filter:blur(60px);}
    .blob2{position:absolute;bottom:-80px;left:-60px;width:360px;height:360px;border-radius:50%;
      background:rgba(150,120,210,0.14);filter:blur(50px);}
    .card{background:rgba(255,255,255,0.6);border-radius:40px;padding:72px 72px 60px;
      width:100%;backdrop-filter:blur(8px);
      box-shadow:0 8px 40px rgba(160,120,200,0.12);position:relative;z-index:1;}
    .icon{width:80px;height:80px;border-radius:50%;background:linear-gradient(135deg,#C084FC,#818CF8);margin-bottom:36px;display:block;}
    .title{font-size:100px;font-weight:900;line-height:1.22;color:#2D1F4E;
      margin-bottom:36px;}
    .pill{display:inline-block;background:linear-gradient(135deg,#C084FC,#818CF8);
      color:white;font-size:28px;padding:10px 28px;border-radius:50px;
      margin-bottom:36px;font-weight:600;}
    .subtitle{font-size:41px;color:#5A4A7A;line-height:1.75;}
    .footer{position:absolute;bottom:52px;left:0;right:0;text-align:center;
      font-size:28px;color:rgba(90,74,122,0.35);}`,
  ];

  const bodies = [
    // 0: 珊瑚红·撞色
    `<div class="top">
      <div class="tag">好内容分享</div>
      <div class="title">${safeTitle}</div>
    </div>
    <div class="bottom">
      <div class="divider"></div>
      <div class="subtitle">${safeSubtitle}</div>
    </div>
    <div class="footer">${safeFooter}</div>`,

    // 1: 奶油白·极简
    `<div class="num">01</div>
    <div class="bar"></div>
    <div class="title">${safeTitle}</div>
    <div class="line"></div>
    <div class="subtitle">${safeSubtitle}</div>
    <div class="footer">${safeFooter}</div>`,

    // 2: 墨绿·自然风
    `<div class="circle1"></div><div class="circle2"></div>
    <div class="leaf"></div>
    <div class="label">知识分享</div>
    <div class="title">${safeTitle}</div>
    <div class="dots"><div class="dot"></div><div class="dot" style="opacity:.5"></div><div class="dot" style="opacity:.25"></div></div>
    <div class="subtitle">${safeSubtitle}</div>
    <div class="footer">${safeFooter}</div>`,

    // 3: 深蓝·知性风
    `<div class="arc"></div><div class="arc2"></div>
    <div class="tag">值得一读</div>
    <div class="title">${safeTitle}</div>
    <div class="rule"></div>
    <div class="subtitle">${safeSubtitle}</div>
    <div class="footer">${safeFooter}</div>`,

    // 4: 柠黄·活力风
    `<div class="stripe"></div><div class="stripe2"></div>
    <div class="bubble"></div>
    <div class="num"></div>
    <div class="title">${safeTitle}</div>
    <div class="bar"></div>
    <div class="subtitle">${safeSubtitle}</div>
    <div class="footer">${safeFooter}</div>`,

    // 5: 丁香紫·治愈风
    `<div class="blob1"></div><div class="blob2"></div>
    <div class="card">
      <span class="icon"></span>
      <div class="title">${safeTitle}</div>
      <div class="pill">好好看看</div>
      <div class="subtitle">${safeSubtitle}</div>
    </div>
    <div class="footer">${safeFooter}</div>`,
  ];

  // 字体路径：优先用户主目录 ~/.fonts，兜底系统路径
  const fontDirs = [
    path.join(os.homedir(), '.fonts'),
    '/usr/share/fonts/noto',
    '/usr/local/share/fonts',
  ];
  let fontDir = fontDirs.find(d => fs.existsSync(path.join(d, 'NotoSansSC-Regular.otf'))) || fontDirs[0];

  // 字体内嵌（解决中文乱码）
  const fontFace = `@font-face {
    font-family: 'Noto Sans SC';
    src: url('file://${fontDir}/NotoSansSC-Regular.otf') format('opentype');
    font-weight: 400;
  }
  @font-face {
    font-family: 'Noto Sans SC';
    src: url('file://${fontDir}/NotoSansSC-Bold.otf') format('opentype');
    font-weight: 700 900;
  }`;

  // 把所有模板的 font-family 统一替换为内嵌字体
  const style = styles[idx].replace(
    /font-family:[^;]+;/g,
    "font-family:'Noto Sans SC',sans-serif;"
  );

  const html = `<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>${fontFace}${style}</style></head>
<body>${bodies[idx]}</body></html>`;

  const tmpHtml = outputPath.replace(/\.png$/i, '') + '.html';
  fs.writeFileSync(tmpHtml, html);

  const b = await puppeteer.launch(buildLaunchOptions());
  try {
    const p = await b.newPage();
    await p.setViewport({ width: 1080, height: 1440, deviceScaleFactor: 1 });
    await p.goto(`file://${tmpHtml}`, { waitUntil: 'networkidle0' });
    // 等字体加载
    await new Promise(r => setTimeout(r, 1500));
    await p.screenshot({ path: outputPath });
  } finally {
    await b.close();
    if (fs.existsSync(tmpHtml)) fs.unlinkSync(tmpHtml);
  }
  return outputPath;
}

/**
 * 检测当前页面的登录/风控状态
 * @param {import('puppeteer').Page} page
 * @returns {Promise<{ loggedIn: boolean, blocked: boolean, reason: string }>}
 *   loggedIn - 是否已登录
 *   blocked  - 是否遇到人机验证/风控弹窗（需要人工干预）
 *   reason   - 诊断信息
 */
async function detectPageState(page) {
  const url = page.url();

  // 1. URL 判断：是否在登录页
  const isLoginPage = url.includes('/login') || url.includes('/signin');

  // 2. DOM 判断：是否存在滑块/验证码/风控特征元素
  const blocked = await page.evaluate(() => {
    // 常见人机验证容器选择器
    const captchaSelectors = [
      '[class*="captcha"]',
      '[class*="slider"]',
      '[class*="verify"]',
      '[class*="challenge"]',
      '[id*="captcha"]',
      '[id*="slider"]',
      // 小红书风控弹窗特征
      '[class*="risk"]',
      '[class*="block"]',
    ];
    for (const sel of captchaSelectors) {
      const el = document.querySelector(sel);
      if (el && el.offsetParent !== null) return true; // 可见
    }
    // 文字特征：页面出现"请完成验证"/"滑动"/"人机验证"等字样
    const bodyText = document.body?.innerText || '';
    return /请完成验证|请滑动|人机验证|安全验证|请拖动|拖动滑块/.test(bodyText);
  }).catch(() => false);

  if (blocked) {
    return { loggedIn: false, blocked: true, reason: '检测到人机验证/风控弹窗，需要人工处理' };
  }
  if (isLoginPage) {
    return { loggedIn: false, blocked: false, reason: '当前在登录页，session 已失效' };
  }
  return { loggedIn: true, blocked: false, reason: 'ok' };
}

/**
 * 检测是否已登录（兼容旧接口，内部调用 detectPageState）
 * @param {import('puppeteer').Page} page
 * @returns {Promise<boolean>}
 */
async function isLoggedIn(page) {
  const state = await detectPageState(page);
  return state.loggedIn;
}

/**
 * 保存 session 信息到 PROFILE_DIR（标记登录时间，方便后续判断是否需要续登）
 */
function saveSessionMeta() {
  try {
    ensureProfileDir();
    const metaPath = path.join(PROFILE_DIR, '.session-meta.json');
    const meta = {
      savedAt: new Date().toISOString(),
      savedAtTs: Date.now(),
    };
    fs.writeFileSync(metaPath, JSON.stringify(meta, null, 2));
    console.log('💾 Session 已持久化到:', PROFILE_DIR);
  } catch (e) {
    console.warn('⚠️ Session meta 保存失败:', e.message);
  }
}

/**
 * 读取 session meta，判断 session 是否可能仍然有效（< 7 天）
 */
function isSessionLikelyValid() {
  try {
    const metaPath = path.join(PROFILE_DIR, '.session-meta.json');
    if (!fs.existsSync(metaPath)) return false;
    const meta = JSON.parse(fs.readFileSync(metaPath, 'utf8'));
    const ageMs = Date.now() - (meta.savedAtTs || 0);
    const sevenDaysMs = 7 * 24 * 60 * 60 * 1000;
    return ageMs < sevenDaysMs;
  } catch {
    return false;
  }
}

/**
 * 手机号 + 验证码登录
 * 
 * @param {object} page - Puppeteer page
 * @param {string} phone - 手机号，如 '13812345678'
 * @param {Function} askCodeFn - 异步函数，向用户索要验证码
 *   签名：async (prompt: string) => string
 *   ⚠️ 安全提示：验证码仅用于本次登录，请勿在公开场合分享
 */
async function loginWithPhone(page, phone, askCodeFn) {
  console.log('🔐 开始手机号+验证码登录...');

  await page.goto('https://creator.xiaohongshu.com/login', { waitUntil: 'networkidle2', timeout: 20000 });
  await sleep(2000);

  // 切换到手机号/密码登录 tab
  await page.evaluate(() => {
    for (const el of document.querySelectorAll('*')) {
      const txt = el.textContent?.trim();
      if ((txt === '手机号登录' || txt === '账号登录' || txt === '密码登录') && el.childElementCount <= 2) {
        el.click(); return true;
      }
    }
    return false;
  });
  await sleep(1000);

  // 输入手机号
  const phoneInput = await page.$('input[placeholder*="手机号"], input[type="tel"], input[name="phone"], input[placeholder*="请输入手机"]');
  if (!phoneInput) {
    await page.screenshot({ path: '/tmp/xhs_login_debug.png' });
    throw new Error('未找到手机号输入框，调试截图已保存到 /tmp/xhs_login_debug.png');
  }
  await phoneInput.click({ clickCount: 3 });
  await phoneInput.type(phone, { delay: 80 });
  console.log('✅ 手机号输入完成');
  await sleep(500);

  // 点击发送验证码
  const sentCode = await page.evaluate(() => {
    const keywords = ['发送验证码', '获取验证码', '发送', '获取'];
    for (const el of document.querySelectorAll('*')) {
      if (el.childElementCount === 0 && keywords.includes(el.textContent?.trim())) {
        el.click(); return true;
      }
    }
    return false;
  });
  if (!sentCode) throw new Error('未找到发送验证码元素，请截图 /tmp/xhs_login_debug.png 检查');
  
  const maskedPhone = phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2');
  console.log('📱 验证码已发送到:', maskedPhone);

  // ⚠️ 验证码安全提示：通过 askCodeFn 向用户索取，不在日志中记录
  const code = await askCodeFn(`📱 验证码已发送到 ${maskedPhone}，请回复6位验证码（仅用于本次登录）：`);
  if (!code || !code.trim()) throw new Error('未收到验证码');

  // 输入验证码（不打印到日志）
  const codeInput = await page.$('input[placeholder*="验证码"], input[maxlength="6"], input[name="code"], input[placeholder*="请输入验证码"]');
  if (!codeInput) throw new Error('未找到验证码输入框');
  await codeInput.click({ clickCount: 3 });
  await codeInput.type(code.trim(), { delay: 100 });
  console.log('✅ 验证码已填入');
  await sleep(500);

  // 点击登录
  await page.evaluate(() => {
    for (const el of document.querySelectorAll('button, div, span')) {
      const txt = el.textContent?.trim().replace(/\s+/g, '');
      if (txt === '登录' || txt === '确认登录') { el.click(); return; }
    }
  });

  await sleep(4000);
  if (!await isLoggedIn(page)) {
    await page.screenshot({ path: '/tmp/xhs_after_login.png' });
    throw new Error('登录失败，可能验证码错误或已过期，截图已保存到 /tmp/xhs_after_login.png');
  }

  // ✅ 登录成功后持久化 session
  saveSessionMeta();
  console.log('✅ 手机号登录成功，session 已保存！');
  return true;
}

// 发布帖子到小红书
// askCodeFn: 可选，异步函数，用于在 session 失效时向用户索要验证码
// 示例：publishPost({ title, content, topics, imagePath, phone: '138xxxx', askCodeFn: async (prompt) => { ... } })
async function publishPost({ title, content, topics, imagePath, phone, askCodeFn }) {

  // ✅ 封面图校验：小红书图文帖必须有封面，缺失则直接报错
  if (!imagePath) {
    throw new Error(
      '❌ 缺少封面图（imagePath）。小红书图文帖必须有封面图，请先调用 generateCoverImage() 生成后再发布。\n\n' +
      '示例：\n' +
      'const imgPath = await generateCoverImage(title, subtitle, "/tmp/cover.png");\n' +
      'await publishPost({ title, content, topics, imagePath: imgPath, ... });'
    );
  }
  if (!fs.existsSync(imagePath)) {
    throw new Error(
      `❌ 封面图文件不存在：${imagePath}\n` +
      '请先调用 generateCoverImage() 生成封面图，或确认路径是否正确。'
    );
  }

  // ✅ 正文自动补段落空行（提升移动端阅读体验）
  // 仅对完全没有空行的正文补空行，已有空行的保持不变，避免破坏用户排版
  const hasBlankLine = /\n\s*\n/.test(content);
  if (!hasBlankLine) {
    content = content.replace(/\n/g, '\n\n');
  }

  // ✅ 内容安全检查（发布前必过，避免被平台打击）
  const safety = checkContentSafety(title, content);
  if (!safety.safe) {
    throw new Error(
      `🚫 内容安全检查未通过：${safety.reason}\n\n` +
      `【内容规范提示】\n` +
      `- 涉及艺人争议只陈述事实，不煽动站队对立\n` +
      `- 不含人身攻击或强烈倾向性定性\n` +
      `- 标题用陈述/好奇视角，结尾用开放式问句引发讨论\n` +
      `- 例：「这件事引发热议，背后原因聊一聊」✅\n` +
      `      「这件事我支持谁？」❌\n\n` +
      `请修改内容后重试。`
    );
  }

  // 确保 session 目录存在（首次使用自动创建，实现 session 持久化）
  ensureProfileDir();

  if (isSessionLikelyValid()) {
    console.log('✅ 检测到已保存的 session，尝试复用（将在页面加载后验证实际登录态）');
  } else {
    console.log('ℹ️ 未检测到有效 session，将在发布时引导登录');
  }

  const browser = await puppeteer.launch(buildLaunchOptions({
    userDataDir: PROFILE_DIR,
  }));
  let publishSuccess = false;
  let postUrl = null;
  try {
  const page = await browser.newPage();
  // stealth 插件已自动处理 webdriver/navigator/plugins 等指纹，无需手动覆盖
  // 随机化视口，减少指纹特征
  await page.setViewport({ width: 1280 + Math.floor(Math.random()*80), height: 900 + Math.floor(Math.random()*60) });

  await page.goto('https://creator.xiaohongshu.com/publish/publish?source=official', { waitUntil: 'networkidle2', timeout: 30000 });
  await sleep(3000);

  // 检测登录态（同时识别人机验证/风控）
  const pageState = await detectPageState(page);
  if (!pageState.loggedIn) {
    if (pageState.blocked) {
      // 人机验证：无法自动处理，截图后报错
      const blockedShot = path.join(os.homedir(), '.openclaw', 'workspace', 'xhs_blocked.png');
      await page.screenshot({ path: blockedShot }).catch(() => {});
      throw new Error(
        `❌ 小红书触发人机验证/风控，无法自动继续。\n` +
        `诊断：${pageState.reason}\n` +
        `截图已保存到：${blockedShot}\n\n` +
        `建议处理方式：\n` +
        `1. 等待 30 分钟后重试（风控通常会自动解除）\n` +
        `2. 手动用浏览器打开 https://creator.xiaohongshu.com 完成一次验证\n` +
        `3. 更换网络环境（如关闭代理）后重试`
      );
    }
    // 未登录：尝试引导登录
    console.log('⚠️ 未登录，尝试引导登录...');
    if (phone && askCodeFn) {
      await loginWithPhone(page, phone, askCodeFn);
      // 登录成功后跳到发布页
      await page.goto('https://creator.xiaohongshu.com/publish/publish?source=official', { waitUntil: 'networkidle2', timeout: 30000 });
      await sleep(3000);
      // 登录后再次检测，防止登录后立刻触发风控
      const postLoginState = await detectPageState(page);
      if (postLoginState.blocked) {
        const blockedShot = path.join(os.homedir(), '.openclaw', 'workspace', 'xhs_blocked.png');
        await page.screenshot({ path: blockedShot }).catch(() => {});
        throw new Error(`❌ 登录后触发人机验证，截图已保存到：${blockedShot}，请稍后重试`);
      }
    } else {
      throw new Error(
        '❌ 小红书 session 已失效，需要重新登录。\n' +
        '请在调用 publishPost 时传入 phone（手机号）和 askCodeFn（验证码获取函数），例如：\n\n' +
        'publishPost({\n' +
        '  title, content, topics, imagePath,\n' +
        '  phone: "13812345678",\n' +
        '  askCodeFn: async (prompt) => { /* 向用户提问，返回验证码 */ }\n' +
        '})'
      );
    }
  }

  // 切换到上传图文
  await page.evaluate(() => {
    for (const el of document.querySelectorAll('*')) {
      if (el.childElementCount <= 1 && el.textContent?.trim() === '上传图文') { el.click(); return; }
    }
  });
  await sleep(2000);

  // 上传图片
  const fileInput = await page.$('input[type="file"]');
  if (!fileInput) throw new Error('未找到文件上传');
  await fileInput.uploadFile(imagePath);
  console.log('📤 图片上传中...');
  // 优先等待预览元素出现，最多等 20 秒；超时则 sleep 兜底
  await Promise.race([
    page.waitForSelector('.imgItem, [class*="img-item"], [class*="upload-success"]', { timeout: 20000 }),
    sleep(20000),
  ]).catch(() => {});
  await sleep(2000);

  // 输入标题
  const allInputs = await page.$$('input');
  for (const inp of allInputs) {
    const ph = await page.evaluate(el => el.placeholder, inp);
    if (ph && ph.includes('标题')) {
      await inp.click({ clickCount: 3 });
      await humanType(page, inp, title);
      console.log('✅ 标题输入完成');
      break;
    }
  }
  await sleep(500);

  // 输入正文（不含话题，话题另外插入）
  const editables = await page.$$('[contenteditable="true"]');
  if (editables.length > 0) {
    const editor = editables[editables.length - 1];
    await editor.click();
    await humanType(page, editor, content);
    console.log('✅ 正文输入完成');
  }
  await sleep(1000);

  // 插入话题
  await insertTopics(page, topics);

  // 截图检查
  const debugShot = path.join(os.homedir(), '.openclaw', 'workspace', 'xhs_pre_publish.png');
  await page.screenshot({ path: debugShot }).catch(() => {});

  // 点发布
  // 发布按钮匹配：优先找 bg-red 类名，降级到任意包含"发布"文字的按钮
  const published = await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    // 优先：类名含 bg-red（当前已知样式）
    const redBtn = btns.find(b => b.textContent?.trim() === '发布' && b.className.includes('bg-red'));
    if (redBtn) { redBtn.click(); return 'red-btn'; }
    // 降级：任意可见的"发布"按钮（排除"保存"/"草稿"等）
    const fallbackBtn = btns.find(b => {
      const txt = b.textContent?.trim();
      return txt === '发布' && !b.disabled && b.offsetParent !== null;
    });
    if (fallbackBtn) { fallbackBtn.click(); return 'fallback-btn'; }
    return null;
  });
  if (!published) throw new Error('未找到发布按钮，请检查 xhs_pre_publish.png 截图');
  console.log('✅ 点击发布（策略:', published + ')');
  await sleep(5000);

  const finalUrl = page.url();
  const success = finalUrl.includes('success');

  // 尝试从页面获取已发布帖子的 URL
  if (success) {
    try {
      postUrl = await page.evaluate(() => {
        const link = document.querySelector('a[href*="xiaohongshu.com/explore"], a[href*="/discovery/item"]');
        return link ? link.href : null;
      });
    } catch { /* 忽略 */ }
  }

  console.log('发布结果:', success ? '✅ 成功' : '❌ 失败', finalUrl);
  if (postUrl) console.log('📎 帖子链接:', postUrl);

  publishSuccess = success;
  } finally {
    await browser.close();
  }
  return { success: publishSuccess, postUrl };
}

module.exports = { generateCoverImage, publishPost, insertTopics, loginWithPhone, isLoggedIn, detectPageState, saveSessionMeta, isSessionLikelyValid, checkContentSafety, detectChromePath, buildLaunchOptions };

// 如果直接运行则输出提示
if (require.main === module) {
  console.log('xhs-publisher 脚本加载完成 ✅');
}
