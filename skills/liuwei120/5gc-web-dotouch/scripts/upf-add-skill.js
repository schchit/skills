#!/usr/bin/env node
/**
 * UPF/PGW-U 添加脚本
 * 完整流程：登录 → 选工程 → 填表单 → 点NSSAI行按钮添加一行 → 填NSSAI/TAC → 提交
 * 用法: node upf-add-skill.js <名称> [--project <工程>] [--url <地址>] [--headed] \
 *       [--n4_ip <IP>] [--n3_ip <IP>] [--n6_ip <IP>] [--n4_port <端口>] \
 *       [--MCC <值>] [--MNC <值>] [--pdu_capacity <数量>] \
 *       [--ue_min <IP>] [--ue_max <IP>]
 * 示例: node upf-add-skill.js UPF-TEST --project XW_S5GC_1
 *       node upf-add-skill.js UPF-PROD --n4_ip 10.0.0.50 --n6_ip 10.0.0.51 --MCC 460 --MNC 01
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'https://192.168.3.89';
const CONFIG = {
  urls: { login: '/login', upfEdit: '/sim_5gc/upf/edit', upfList: '/sim_5gc/upf/index' },
  credentials: { email: 'dotouch@dotouch.com.cn', password: 'dotouch' },
  sessionDir: path.join(__dirname, '.sessions'),
  getSessionFile() {
    return `5gc_session_${BASE_URL.replace(/https?:\/\//, '').replace(/\./g, '_')}.json`;
  }
};

class SessionManager {
  constructor() {
    if (!fs.existsSync(CONFIG.sessionDir)) fs.mkdirSync(CONFIG.sessionDir, { recursive: true });
    this.sp = path.join(CONFIG.sessionDir, CONFIG.getSessionFile());
  }
  async loadSession(browser) {
    if (!fs.existsSync(this.sp)) return null;
    const { storageState } = JSON.parse(fs.readFileSync(this.sp, 'utf8'));
    return await browser.newContext({ storageState, ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  }
  async saveSession(context) {
    fs.writeFileSync(this.sp, JSON.stringify({ storageState: await context.storageState() }, null, 2));
  }
}

// 选择工程（jsgrid 分页遍历，精确匹配，点击 checkbox）
async function selectProject(page, projectName) {
  await page.goto(`${BASE_URL}/sim_5gc/project/index`, { waitUntil: 'networkidle', timeout: 15000 });
  await page.waitForSelector('.jsgrid-row, .jsgrid-alt-row', { timeout: 5000 }).catch(() => {});

  for (let pageNum = 1; pageNum <= 20; pageNum++) {
    const result = await page.evaluate((targetName) => {
      const rows = document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row');
      for (const row of rows) {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 3 && cells[2].textContent.trim() === targetName) {
          const checkbox = cells[0].querySelector('input[type="checkbox"]');
          if (checkbox) { checkbox.click(); return 'clicked'; }
          const icon = cells[1].querySelector('.iconfont');
          if (icon) { icon.click(); return 'icon-clicked'; }
        }
      }
      return 'not-found';
    }, projectName);

    if (result === 'clicked' || result === 'icon-clicked') {
      await page.waitForTimeout(2000);
      return true;
    }

    // 点下一页
    const nextBtn = page.locator('.jsgrid-pager a').filter({ hasText: 'Next' }).first();
    if (!(await nextBtn.count())) break;
    try {
      await page.evaluate(() => {
      var links = document.querySelectorAll('.jsgrid-pager a');
      for (var i = 0; i < links.length; i++) {
        if (links[i].innerText.trim() === 'Next') { links[i].click(); break; }
      }
    });
    await page.waitForTimeout(2000);
    } catch { break; }
  }
  console.log(`  ❌ 未找到工程 "${projectName}"`);
  return false;
}

// 添加 UPF 主流程
async function addUpf(upfName, projectName, upfConfig = {}) {
  const startTime = Date.now();
  const sessionMgr = new SessionManager();
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox', '--ignore-certificate-errors'] });

  const context = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await context.newPage();

  // 登录
  await page.goto(`${BASE_URL}${CONFIG.urls.login}`, { waitUntil: 'networkidle' });
  await page.getByRole('textbox', { name: 'E-Mail地址' }).fill(CONFIG.credentials.email);
  await page.getByRole('textbox', { name: '密码' }).fill(CONFIG.credentials.password);
  await page.getByRole('checkbox', { name: '记住我' }).check();
  await page.getByRole('button', { name: '登录' }).click();
  await page.waitForLoadState('networkidle');
  await sessionMgr.saveSession(context);
  console.log('  ✓ 登录成功');

  // 选工程（通过 jsgrid 精确匹配 + 点击 iconfont）
  const ok = await selectProject(page, projectName);
  if (!ok) throw new Error(`工程 "${projectName}" 未找到`);
  console.log(`  ✓ 工程 "${projectName}" 已选`);
  await page.waitForTimeout(1000);

  // 直接导航到 UPF 列表页（工程已在 sidebar 激活）
  await page.goto(`${BASE_URL}/sim_5gc/upf/index`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  console.log('  ✓ 进入 UPF/PGW-U');

  // 点添加
  await page.getByRole('button', { name: '添加' }).click();
  await page.waitForTimeout(1500);
  console.log('  ✓ 点添加');

  // === 填基本字段 ===
  await page.evaluate((name) => {
    const setVal = (n, v) => {
      const el = document.querySelector(`input[name="${n}"]`);
      if (!el) return;
      el.value = v;
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
    };
    setVal('name', name);
  }, upfName);

  // type: select → 1=仿真设备（layui隐藏了原select，用JS设值）
  await page.evaluate(() => {
    const sel = document.querySelector('select[name="type"]');
    if (sel) {
      sel.value = '1';
      sel.dispatchEvent(new Event('change', { bubbles: true }));
    }
  });
  console.log('  ✓ 类型已选');

  // 基本网络字段
  const cfg = {
    n4_ip: upfConfig.n4_ip || '192.168.20.30',
    n4_port: upfConfig.n4_port || '8805',
    n3_ip: upfConfig.n3_ip || '192.168.20.30',
    n6_ip: upfConfig.n6_ip || '192.168.20.31',
    pdu_capacity: upfConfig.pdu_capacity || '20000',
    ue_min: upfConfig.ue_min || '20.20.20.20',
    ue_max: upfConfig.ue_max || '20.20.60.20',
  };
  await page.evaluate((c) => {
    const setVal = (n, v) => {
      const el = document.querySelector(`input[name="${n}"]`);
      if (!el) return;
      el.value = v;
      el.dispatchEvent(new Event('input', { bubbles: true }));
    };
    setVal('n4_ip', c.n4_ip);
    setVal('n4_port', c.n4_port);
    setVal('n3_ip', c.n3_ip);
    setVal('n6_ip', c.n6_ip);
    setVal('pdu_capacity', c.pdu_capacity);
    setVal('ue_min', c.ue_min);
    setVal('ue_max', c.ue_max);
  }, cfg);
  console.log('  ✓ 基本字段已填');

  // MCC/MNC（通过 page.evaluate 设置，因为 layui 需要事件触发）
  if (upfConfig.MCC || upfConfig.MNC) {
    await page.evaluate((c) => {
      const setVal = (n, v) => {
        const el = document.querySelector(`input[name="${n}"]`);
        if (!el) return;
        el.value = v;
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
      };
      setVal('MCC', c.MCC || '460');
      setVal('MNC', c.MNC || '01');
    }, { MCC: upfConfig.MCC, MNC: upfConfig.MNC });
    console.log(`  ✓ MCC=${upfConfig.MCC || '460'} MNC=${upfConfig.MNC || '01'}`);
  }

  // === NSSAI / TAC 配置 ===
  // 点击"数量*nssai*类型*TAC起始*"行末尾的"刷新/添加"按钮（添加一行）
  await page.getByRole('row', { name: /\* 数量.*nssai.*类型.*TAC起始/ }).locator('button').click();
  await page.waitForTimeout(800);
  console.log('  ✓ NSSAI 行已添加');

  // 填写 config 字段
  await page.evaluate(() => {
    const setVal = (n, v) => {
      const el = document.querySelector(`input[name="${n}"]`);
      if (!el) return;
      el.value = v;
      el.dispatchEvent(new Event('input', { bubbles: true }));
    };
    setVal('config[count][]', '1');
    setVal('config[nssai][]', '1');
    setVal('config[stac][]', '101');
    setVal('config[etac][]', '102');
  });
  console.log('  ✓ NSSAI/TAC 已填');

  // === 提交 ===
  await page.getByRole('button', { name: '提交' }).click();
  console.log('  ✓ 已提交');
  await page.waitForTimeout(3000);

  const finalUrl = page.url();
  console.log('  最终 URL:', finalUrl);

  let success = finalUrl.includes('upf/index');
  if (success) {
    console.log('  ✅ 跳转成功 - UPF 添加完成');
  } else {
    const txt = await page.evaluate(() => document.body.innerText.slice(0, 300));
    console.log('  页面文本:', txt.replace(/\s+/g, ' ').slice(0, 200));
    await page.screenshot({ path: 'add-result.png' });
  }

  // 验证列表中是否存在
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);

  // UPF 表：ID在第2列(cells[1])，名称在第3列(cells[2])
  const debug = await page.evaluate((targetName) => {
    const allRows = document.querySelectorAll('table tbody tr');
    const entries = [];
    for (const row of allRows) {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 3) {
        entries.push(cells[2].textContent.trim());  // 名称列
      }
    }
    return { url: window.location.href, entries: entries.slice(0, 20), found: entries.includes(targetName) };
  }, upfName);
  console.log('列表调试 - URL:', debug.url);
  console.log('UPF 列表:', debug.entries.join(', '));
  console.log(debug.found ? `✅ UPF "${upfName}" 已出现在列表中！` : `⚠ UPF "${upfName}" 不在列表中`);

  await browser.close();
  const totalTime = (Date.now() - startTime) / 1000;
  return { success, upfName, totalTime };
}

// 主函数
async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.log('用法: node upf-add-skill.js <UPF名称> [--project <工程名>] [--url <地址>] [--headed]');
    console.log('       [--n4_ip <IP>] [--n3_ip <IP>] [--n6_ip <IP>]');
    console.log('       [--MCC <值>] [--MNC <值>] [--pdu_capacity <数量>]');
    console.log('       [--ue_min <IP>] [--ue_max <IP>]');
    console.log('示例: node upf-add-skill.js UPF-TEST --project XW_S5GC_1');
    console.log('       node upf-add-skill.js UPF-PROD --n4_ip 10.0.0.50 --n6_ip 10.0.0.51 --MCC 460 --MNC 01');
    process.exit(1);
  }

  let upfName = null, projectName = 'XW_S5GC_1', explicitProject = false;
  let urlOverride = null;
  const upfConfig = {
    n4_ip: '192.168.20.30',
    n4_port: '8805',
    n3_ip: '192.168.20.30',
    n6_ip: '192.168.20.31',
    MCC: '460',
    MNC: '01',
    pdu_capacity: '20000',
    ue_min: '20.20.20.20',
    ue_max: '20.20.60.20',
  };

  for (let i = 0; i < args.length; i++) {
    if (!args[i].startsWith('-')) upfName = args[i];
    else if (args[i] === '--project' || args[i] === '-p') { projectName = args[++i]; explicitProject = true; }
    else if (args[i] === '--url') { urlOverride = args[++i]; }
    else if (args[i] === '--n4_ip') { upfConfig.n4_ip = args[++i]; }
    else if (args[i] === '--n4_port') { upfConfig.n4_port = args[++i]; }
    else if (args[i] === '--n3_ip') { upfConfig.n3_ip = args[++i]; }
    else if (args[i] === '--n6_ip') { upfConfig.n6_ip = args[++i]; }
    else if (args[i] === '--MCC') { upfConfig.MCC = args[++i]; }
    else if (args[i] === '--MNC') { upfConfig.MNC = args[++i]; }
    else if (args[i] === '--pdu_capacity') { upfConfig.pdu_capacity = args[++i]; }
    else if (args[i] === '--ue_min') { upfConfig.ue_min = args[++i]; }
    else if (args[i] === '--ue_max') { upfConfig.ue_max = args[++i]; }
  }

  if (!upfName) { console.error('错误: 请指定 UPF 名称'); process.exit(1); }
  if (urlOverride) {
    if (!urlOverride.startsWith('http')) urlOverride = 'https://' + urlOverride;
  }

  const targetUrl = urlOverride || BASE_URL;
  console.log(`▶ 添加 UPF: ${upfName}  |  工程: ${projectName}  |  地址: ${targetUrl}`);
  console.log(`  n4_ip=${upfConfig.n4_ip} n3_ip=${upfConfig.n3_ip} n6_ip=${upfConfig.n6_ip} MCC=${upfConfig.MCC} MNC=${upfConfig.MNC}`);

  try {
    process.env.UPF_ADD_BASE_URL = targetUrl;
    const result = await addUpf(upfName, projectName, upfConfig);
    console.log(`\n总耗时: ${result.totalTime.toFixed(1)}s`);
    process.exit(result.success ? 0 : 1);
  } catch (err) {
    console.error('异常:', err.message);
    process.exit(1);
  }
}

main();
