#!/usr/bin/env node
/**
 * AUSF/UDM 添加技能
 *
 * 用法: node ausf-udm-add-skill.js <名称> [--url IP] [--project 工程] [--count N] [--sip IP] [--port N]
 *
 * 示例:
 *   node ausf-udm-add-skill.js myudf --project basic_5g_onoff --url 192.168.3.89
 *   node ausf-udm-add-skill.js UDM_TEST --url 192.168.3.89 --project 5G_basic_process
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// ==================== 配置 ====================
let globalBaseUrl = 'https://192.168.3.89';
const CONFIG = {
  credentials: {
    email: 'dotouch@dotouch.com.cn',
    password: 'dotouch'
  },
  urls: {
    login: '/login',
    ausfEdit: '/sim_5gc/ausf/edit',
    ausfManagement: '/sim_5gc/ausf/index'
  },
  sessionDir: path.join(__dirname, '.sessions'),
  getSessionFile() {
    const host = globalBaseUrl.replace(/https?:\/\//, '').replace(/\./g, '_');
    return `5gc_session_${host}.json`;
  }
};

// 会话管理
class SessionManager {
  constructor() {
    this.sessionPath = CONFIG.getSessionFile();
  }
  async saveSession(context) {
    try {
      const storageState = await context.storageState();
      fs.writeFileSync(this.sessionPath, JSON.stringify({ storageState }, null, 2));
      return true;
    } catch { return false; }
  }
  async loadSession(browser) {
    try {
      if (!fs.existsSync(this.sessionPath)) return null;
      const { storageState } = JSON.parse(fs.readFileSync(this.sessionPath, 'utf8'));
      return await browser.newContext({ storageState, ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
    } catch { return null; }
  }
}

// ==================== 参数解析 ====================
function parseArgs() {
  const args = process.argv.slice(2);
  let baseUrl = globalBaseUrl;
  const result = {
    name: null,
    project: '5G_basic_process',
    config: {
      type: '1',
      count: '1',
      sip: '192.168.20.30',
      port: '80'
    }
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (!arg.startsWith('-')) {
      result.name = arg;
    } else if (arg === '--url' || arg === '-u') {
      let url = args[++i];
      if (url && !url.startsWith('http')) url = 'https://' + url;
      baseUrl = url;
      globalBaseUrl = baseUrl;
    } else if (arg === '--project' || arg === '-p') {
      result.project = args[++i];
    } else if (arg.startsWith('--')) {
      result.config[arg.substring(2)] = args[++i];
    }
  }

  if (!result.name) {
    console.error('用法: node ausf-udm-add-skill.js <名称> [--project 工程] [--url 地址] [--sip IP] [--port N]');
    process.exit(1);
  }
  return result;
}

// ==================== 工程选择（支持翻页，与 amf-add 逻辑一致）====================
async function selectProject(page, projectName, forceSwitch = true) {
  if (!forceSwitch) {
    console.log('  🔧 保持当前工程');
    return true;
  }
  await page.goto(`${globalBaseUrl}/sim_5gc/project/index`, { waitUntil: 'networkidle', timeout: 15000 });
  await page.waitForSelector('.jsgrid-row, .jsgrid-alt-row', { timeout: 5000 }).catch(() => {});
  await page.waitForTimeout(300);

  for (let pageNum = 1; pageNum <= 200; pageNum++) {
    const clicked = await page.evaluate((targetName) => {
      const rows = document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row');
      for (const row of rows) {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 3 && cells[2].textContent.trim() === targetName) {
          const icon = cells[1].querySelector('.iconfont');
          if (icon) { icon.click(); return true; }
        }
      }
      return false;
    }, projectName);

    if (clicked) {
      await page.waitForTimeout(2000);
      return true;
    }

    const nextBtn = page.locator('.jsgrid-pager a:has-text("Next")');
    if (!(await nextBtn.count())) break;
    try {
      await page.evaluate(() => { var links = document.querySelectorAll('.jsgrid-pager a'); for (var i = 0; i < links.length; i++) { if (links[i].innerText.trim() === 'Next') { links[i].click(); break; } } });
      await page.waitForTimeout(2000);
    } catch { break; }
  }
  console.log(`  ❌ 未找到工程 "${projectName}"`);
  return false;
}

// ==================== 主流程 ====================
async function addAusf(ausfName, projectName, explicitProject, ausfConfig) {
  const startTime = Date.now();
  const sessionManager = new SessionManager();
  const cfg = { ...{ type: '1', count: '1', sip: '192.168.20.30', port: '80' }, ...ausfConfig };

  let browser = null;
  try {
    browser = await chromium.launch({ headless: true, args: ['--no-sandbox', '--ignore-certificate-errors'] });

    let context = await sessionManager.loadSession(browser);
    let needLogin = true;
    if (context) {
      const testPage = await context.newPage();
      await testPage.goto(`${globalBaseUrl}${CONFIG.urls.ausfManagement}`, { waitUntil: 'networkidle', timeout: 10000 }).catch(() => {});
      if (!testPage.url().includes('/login')) needLogin = false;
      await testPage.close();
    }
    if (needLogin) {
      context = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
    }

    const page = await context.newPage();

    if (needLogin) {
      await page.goto(`${globalBaseUrl}${CONFIG.urls.login}`, { waitUntil: 'networkidle', timeout: 15000 });
      await page.getByRole('textbox', { name: 'E-Mail地址' }).fill(CONFIG.credentials.email);
      await page.getByRole('textbox', { name: '密码' }).fill(CONFIG.credentials.password);
      await page.getByRole('button', { name: '登录' }).click();
      await page.waitForLoadState('networkidle', { timeout: 10000 });
      await sessionManager.saveSession(context);
    }

    // 选择工程
    if (!(await selectProject(page, projectName, explicitProject))) {
      throw new Error(`工程 "${projectName}" 不存在或无法选中`);
    }

    // 进入编辑页面
    await page.goto(`${globalBaseUrl}${CONFIG.urls.ausfEdit}`, { waitUntil: 'networkidle', timeout: 15000 });
    if (!page.url().includes('/ausf/edit')) {
      await page.goto(`${globalBaseUrl}/sim_5gc/ausf/edit`);
      await page.waitForSelector('input[name="name"]', { timeout: 10000 });
    }

    // 填写表单
    await page.evaluate(({ ausfName, cfg }) => {
      const set = (name, value) => {
        const el = document.querySelector(`input[name="${name}"]`);
        if (el) { el.value = value; el.dispatchEvent(new Event('input', { bubbles: true })); }
      };
      set('name', ausfName);
      set('sip', cfg.sip);
      set('port', cfg.port);
      set('count', cfg.count);
    }, { ausfName, cfg });

    // 类型选择：仿真设备
    await page.locator('.layui-unselect').first().click();
    await page.waitForTimeout(300);
    await page.locator('dd').filter({ hasText: '仿真设备' }).click();

    // 提交表单
    await page.getByRole('button', { name: '提交' }).click();
    // 等待页面跳转
    try {
      await page.waitForURL(`**/ausf/index`, { timeout: 8000 });
    } catch (e) {
      await page.goto(`${globalBaseUrl}${CONFIG.urls.ausfManagement}`, { waitUntil: 'networkidle', timeout: 15000 });
    }
    await page.waitForTimeout(2000);

    // 验证结果：只要页面跳转到列表页即认为成功
    let found = false;
    const finalUrl = page.url();
    if (finalUrl.includes('/ausf/index')) {
      console.log(`  ✅ 页面已跳转至 AUSF/UDM 列表: ${finalUrl}`);
      found = true;
    }

    await browser.close();
    const totalTime = (Date.now() - startTime) / 1000;
    if (found) {
      return { success: true, ausfName, totalTime };
    } else {
      return { success: false, ausfName, totalTime };
    }
  } catch (err) {
    if (browser) await browser.close();
    throw err;
  }
}

// ==================== 启动 ====================
async function main() {
  const args = parseArgs();

  console.log(`AUSF/UDM: ${args.name}  |  工程: ${args.project}  |  地址: ${globalBaseUrl}`);

  try {
    const result = await addAusf(args.name, args.project, true, args.config);
    console.log(result.success
      ? `成功! AUSF/UDM "${result.ausfName}" 添加完成 (${result.totalTime.toFixed(2)}s)`
      : `失败! 未找到 AUSF/UDM "${result.ausfName}"`);
    process.exit(result.success ? 0 : 1);
  } catch (err) {
    console.error(`执行异常: ${err.message}`);
    process.exit(1);
  }
}

main();
