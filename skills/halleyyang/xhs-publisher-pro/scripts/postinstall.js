#!/usr/bin/env node
/**
 * postinstall.js
 * npm install 完成后自动运行，检测 Chrome 环境并给出指引
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const { execSync, spawnSync } = require('child_process');

const platform = os.platform();

// 各平台候选路径
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
    process.env.LOCALAPPDATA
      ? path.join(process.env.LOCALAPPDATA, 'Google\\Chrome\\Application\\chrome.exe')
      : null,
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

function findSystemChrome() {
  const paths = candidates[platform] || candidates.linux;
  for (const p of paths) {
    try { if (fs.existsSync(p)) return p; } catch {}
  }
  return null;
}

function findPuppeteerChrome() {
  try {
    const { executablePath } = require('puppeteer');
    if (typeof executablePath === 'function') {
      const p = executablePath();
      if (p && fs.existsSync(p)) return p;
    }
  } catch {}
  return null;
}

// 检测 Chrome 能否真正启动（系统依赖库是否齐全）
function canChromeRun(chromePath) {
  if (!chromePath) return false;
  try {
    const result = spawnSync(chromePath, ['--version', '--no-sandbox', '--headless'], {
      timeout: 5000,
      stdio: 'pipe',
    });
    return result.status === 0;
  } catch {
    return false;
  }
}

// 打印缺少系统依赖库时的修复指引
function printMissingLibsGuide() {
  console.log(`
💡 Chrome 已安装但无法启动，通常是缺少系统运行库。请执行以下命令：

  Ubuntu / Debian:
    sudo apt-get install -y libnss3 libatk1.0-0 libatk-bridge2.0-0 \\
      libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 \\
      libxfixes3 libxrandr2 libgbm1 libasound2 libpango-1.0-0 libcairo2

  CentOS / TencentOS / RHEL:
    sudo yum install -y nss atk at-spi2-atk cups-libs libdrm \\
      libxkbcommon libXcomposite libXdamage libXfixes \\
      libXrandr mesa-libgbm alsa-lib pango cairo

安装后重新运行 node postinstall.js 验证。
`);
}

function tryInstallChromium() {
  const managers = [
    { cmd: 'apt-get', install: 'apt-get install -y chromium-browser 2>/dev/null || apt-get install -y chromium 2>/dev/null' },
    { cmd: 'dnf',     install: 'dnf install -y chromium 2>/dev/null' },
    { cmd: 'yum',     install: 'yum install -y chromium 2>/dev/null' },
    { cmd: 'brew',    install: 'brew install --cask chromium 2>/dev/null' },
  ];
  for (const m of managers) {
    try {
      execSync(`which ${m.cmd}`, { stdio: 'ignore' });
      console.log(`  → 尝试用 ${m.cmd} 安装 Chromium...`);
      execSync(m.install, { stdio: 'inherit', shell: true });
      const found = findSystemChrome();
      if (found) return found;
    } catch {}
  }
  return null;
}

function tryPuppeteerDownloadCN() {
  console.log('  → 尝试通过国内镜像下载 Puppeteer Chrome...');
  const result = spawnSync('node', ['-e', `
    process.env.PUPPETEER_DOWNLOAD_HOST = 'https://npmmirror.com/mirrors';
    const { install } = require('puppeteer/internal/node/install.js');
    install().then(() => process.exit(0)).catch(() => process.exit(1));
  `], { stdio: 'inherit', timeout: 120000 });
  return result.status === 0;
}

// ---- 主流程 ----
console.log('\n🔍 xhs-publisher: 检测 Chrome 环境...');

const systemChrome = findSystemChrome();
if (systemChrome) {
  if (canChromeRun(systemChrome)) {
    console.log(`✅ 系统 Chrome 可正常使用：${systemChrome}\n`);
    process.exit(0);
  } else {
    console.log(`⚠️  找到 Chrome（${systemChrome}），但无法启动，可能缺少系统依赖库。`);
    printMissingLibsGuide();
    process.exit(0);
  }
}

const puppeteerChrome = findPuppeteerChrome();
if (puppeteerChrome) {
  if (canChromeRun(puppeteerChrome)) {
    console.log(`✅ Puppeteer 内置 Chrome 可正常使用\n`);
    process.exit(0);
  } else {
    console.log('⚠️  Puppeteer 内置 Chrome 无法启动，可能缺少系统依赖库。');
    printMissingLibsGuide();
    process.exit(0);
  }
}

// 都没有，自动修复
console.log('⚠️  未检测到可用的 Chrome/Chromium，尝试自动修复...');

if (platform === 'linux') {
  const installed = tryInstallChromium();
  if (installed && canChromeRun(installed)) {
    console.log(`✅ Chromium 安装并验证成功：${installed}\n`);
    process.exit(0);
  }
}

const downloaded = tryPuppeteerDownloadCN();
if (downloaded) {
  const p = findPuppeteerChrome();
  if (p && canChromeRun(p)) {
    console.log('✅ Chrome 下载并验证完成\n');
    process.exit(0);
  }
}

// 全部失败
console.log(`
❌ 自动修复未成功，请根据你的系统手动安装 Chrome：

  macOS:    brew install --cask google-chrome
  Ubuntu:   sudo apt-get install -y chromium-browser
  CentOS:   sudo yum install -y chromium
  Windows:  https://www.google.com/chrome/

或通过环境变量指定已有 Chrome 路径：
  export PUPPETEER_EXECUTABLE_PATH=/path/to/chrome
`);
printMissingLibsGuide();

process.exit(0); // 不报错，Chrome 缺失是运行时问题
