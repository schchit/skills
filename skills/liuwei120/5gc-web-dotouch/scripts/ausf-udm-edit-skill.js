#!/usr/bin/env node

/**
 * AUSF/UDM 编辑技能（单条+批量二合一）
 *
 * 单个编辑: node ausf-udm-edit-skill.js <名称> --project <工程> --set-<字段> <值>
 *          node ausf-udm-edit-skill.js --name <名称> --project <工程> --set-<字段> <值>
 *          node ausf-udm-edit-skill.js --id <ID> --set-<字段> <值>
 *
 * 批量编辑: node ausf-udm-edit-skill.js --project <工程> --set-<字段> <值>
 *
 * 可编辑字段: sip, port, mcc, mnc, ngap_port, http2_port
 *
 * 示例:
 *   node ausf-udm-edit-skill.js --project XW_S5GC_1 --set-sip 10.0.0.99   (批量)
 *   node ausf-udm-edit-skill.js --name udm --project XW_S5GC_1 --set-sip 10.0.0.99
 *   node ausf-udm-edit-skill.js --id 4772 --set-sip 10.0.0.99
 */

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

// 全局配置
let globalBaseUrl = 'https://192.168.3.89';
const CONFIG = {
  sessionDir: path.join(__dirname, '.sessions'),
  getSessionFile() {
    const host = globalBaseUrl.replace(/https?:\/\//, '').replace(/\./g, '_');
    return `5gc_session_${host}.json`;
  },
  credentials: {
    email: 'dotouch@dotouch.com.cn',
    password: 'dotouch'
  },
  urls: {
    login: '/login',
    ausfManagement: '/sim_5gc/ausf/index',
  }
};

// 会话管理
class SessionManager {
  constructor() {
    this.sessionPath = path.join(CONFIG.sessionDir, CONFIG.getSessionFile());
  }
  async saveSession(context) {
    try {
      const storageState = await context.storageState();
      fs.writeFileSync(this.sessionPath, JSON.stringify({ storageState }, null, 2));
    } catch {}
  }
  async loadSession(browser) {
    try {
      if (!fs.existsSync(this.sessionPath)) return null;
      const { storageState } = JSON.parse(fs.readFileSync(this.sessionPath, 'utf8'));
      return await browser.newContext({ storageState, ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
    } catch { return null; }
  }
}

// ─── 参数解析 ─────────────────────────────────────────────────

function parseArgs() {
  const args = process.argv.slice(2);
  const result = { name: null, project: 'XW_S5GC_1', targetId: null, fields: {} };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--help' || arg === '-h') { printHelp(); process.exit(0); }
    else if (!arg.startsWith('-')) { if (!result.name) result.name = arg; }
    else if (arg === '--url') { globalBaseUrl = args[++i]; }
    else if (arg === '--project' || arg === '-p') { result.project = args[++i]; }
    else if (arg === '--name') { result.name = args[++i]; }
    else if (arg === '--id') { result.targetId = args[++i]; }
    else if (arg.startsWith('--set-')) {
      const key = arg.substring(6).replace(/-/g, '_');
      result.fields[key] = args[++i];
    } else if (arg.startsWith('--')) {
      const key = arg.substring(2).replace(/-/g, '_');
      result.fields[key] = args[++i];
    }
  }
  return result;
}

function printHelp() {
  console.log(`
AUSF/UDM 编辑（单条+批量二合一）
===============================
用法:
  node ausf-udm-edit-skill.js --project <工程> --set-<字段> <值>   (批量)
  node ausf-udm-edit-skill.js --name <名称> --project <工程> --set-<字段> <值>
  node ausf-udm-edit-skill.js --id <ID> --set-<字段> <值>

可编辑字段: sip, port, mcc, mnc, ngap_port, http2_port
`);
}

// ─── 工程选择 ─────────────────────────────────────────────────

async function selectProject(page, projectName) {
  await page.goto(`${globalBaseUrl}/sim_5gc/project/index`, { waitUntil: 'networkidle', timeout: 15000 });
  await page.waitForTimeout(2000);
  for (let pageNum = 1; pageNum <= 20; pageNum++) {
    const clicked = await page.evaluate((name) => {
      const rows = document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row');
      for (const row of rows) {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 3 && cells[2].textContent.trim() === name) {
          if (row.classList.contains('jsgrid-selected-row')) return 'already';
          const icon = cells[1].querySelector('.iconfont');
          if (icon) { icon.click(); return 'clicked'; }
          const td = row.querySelector('td.project_select');
          if (td) { td.click(); return 'clicked'; }
          row.click(); return 'clicked';
        }
      }
      return 'not-found';
    }, projectName);
    if (clicked !== 'not-found') { await page.waitForTimeout(2000); return true; }
    const hasNext = await page.evaluate(() =>
      Array.from(document.querySelectorAll('.jsgrid-pager a')).some(a => a.innerText.trim() === 'Next'));
    if (!hasNext) break;
    await page.evaluate(() => {
      const links = document.querySelectorAll('.jsgrid-pager a');
      for (const l of links) { if (l.innerText.trim() === 'Next') { l.click(); break; } }
    });
    await page.waitForTimeout(1500);
  }
  return false;
}

// ─── 查找 AUSF 列表 ───────────────────────────────────────────

async function findAusfList(page) {
  const sidebarUrl = await page.evaluate(() => {
    const links = document.querySelectorAll('a[href*="/ausf/index"]');
    return links[0]?.href || '';
  });
  if (!sidebarUrl) throw new Error('未找到 AUSF 侧边栏链接');

  let ausfList = [];
  await page.goto(sidebarUrl, { waitUntil: 'networkidle', timeout: 15000 });
  await page.waitForTimeout(2000);

  for (let pageNum = 1; pageNum <= 50; pageNum++) {
    const rows = await page.locator('.layui-table tbody tr').all();
    for (const row of rows) {
      const cells = await row.locator('td').all();
      if (cells.length >= 3) {
        const id = (await cells[1].textContent()).trim();
        const n = (await cells[2].textContent()).trim();
        if (id && id.match(/^\d+$/) && n && n !== '名称' && n !== '编辑') {
          if (!ausfList.some(u => u.id === id)) ausfList.push({ id, name: n });
        }
      }
    }
    const hasNext = await page.evaluate(() =>
      Array.from(document.querySelectorAll('.layui-table .layui-laypage a'))
        .some(a => a.innerText.trim() === 'Next'));
    if (!hasNext) break;
    await page.evaluate(() => {
      const links = document.querySelectorAll('.layui-table .layui-laypage a');
      for (const l of links) { if (l.innerText.trim() === 'Next') { l.click(); break; } }
    });
    await page.waitForTimeout(2000);
  }
  return ausfList;
}

// ─── 修改单个 AUSF ────────────────────────────────────────────

async function modifyAndSubmit(page, ausfId, fields) {
  await page.goto(`${globalBaseUrl}/sim_5gc/ausf/edit/${ausfId}`, { waitUntil: 'networkidle', timeout: 15000 });
  await page.waitForTimeout(3000);

  if (fields.sip) { await page.locator('input[name="sip"]').fill(fields.sip); }
  if (fields.port) { await page.locator('input[name="port"]').fill(fields.port); }
  if (fields.mcc) { await page.locator('input[name="mcc"]').fill(fields.mcc); }
  if (fields.mnc) { await page.locator('input[name="mnc"]').fill(fields.mnc); }
  if (fields.ngap_port) { await page.locator('input[name="ngap_port"]').fill(fields.ngap_port); }
  if (fields.http2_port) { await page.locator('input[name="http2_port"]').fill(fields.http2_port); }

  await page.getByRole('button', { name: '提交' }).click();
  await page.waitForTimeout(3000);
  try { await page.waitForURL('**/ausf/index', { timeout: 5000 }); } catch {}
  return page.url().includes('/ausf/index');
}

// ─── 主函数 ──────────────────────────────────────────────────

async function main() {
  const args = parseArgs();

  if (Object.keys(args.fields).length === 0) {
    console.error('请至少指定一个 --set-<字段>'); printHelp(); process.exit(1);
  }

  console.log('▶ AUSF/UDM 编辑  工程:', args.project, '  字段:', JSON.stringify(args.fields));

  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox', '--ignore-certificate-errors'] });
  const sessionManager = new SessionManager();
  let context = await sessionManager.loadSession(browser);
  let needLogin = true;
  if (context) {
    const testPage = await context.newPage();
    await testPage.goto(`${globalBaseUrl}${CONFIG.urls.ausfManagement}`, { waitUntil: 'networkidle', timeout: 8000 }).catch(() => {});
    if (!testPage.url().includes('/login')) needLogin = false;
    await testPage.close();
  }
  if (needLogin) context = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await context.newPage();

  if (needLogin) {
    console.log('  🔐 登录...');
    await page.goto(`${globalBaseUrl}${CONFIG.urls.login}`, { waitUntil: 'networkidle', timeout: 15000 });
    await page.getByRole('textbox', { name: 'E-Mail地址' }).fill(CONFIG.credentials.email);
    await page.getByRole('textbox', { name: '密码' }).fill(CONFIG.credentials.password);
    await page.getByRole('button', { name: '登录' }).click();
    await page.waitForLoadState('networkidle');
    await sessionManager.saveSession(context);
    console.log('  ✅ 登录成功');
  } else {
    console.log('  ✅ 使用缓存会话');
  }

  if (!await selectProject(page, args.project)) {
    console.log('  ❌ 工程未找到:', args.project);
    await browser.close(); process.exit(1);
  }
  console.log('  ✅ 工程已选');

  // ── 批量模式：无 name 且无 targetId ──────────────────────
  if (!args.name && !args.targetId) {
    const ausfList = await findAusfList(page);
    if (ausfList.length === 0) { console.log('  ⚠ 没有 AUSF/UDM'); await browser.close(); process.exit(0); }
    console.log('  找到', ausfList.length, '个 AUSF/UDM，进入批量模式');
    let success = 0;
    for (const { id, name } of ausfList) {
      process.stdout.write('  ▶ [' + id + '] ' + name + ' ... ');
      try {
        const ok = await modifyAndSubmit(page, id, args.fields);
        console.log(ok ? '✅' : '❌');
        if (ok) success++;
      } catch (e) { console.log('❌', e.message); }
      await page.waitForTimeout(500);
    }
    await browser.close();
    console.log('\n完成:', success + '/' + ausfList.length, '成功');
    process.exit(success > 0 ? 0 : 1);
  }

  // ── 单个模式 ────────────────────────────────────────────
  let resolvedId = args.targetId;
  if (!resolvedId) {
    const ausfList = await findAusfList(page);
    const target = ausfList.find(u => u.name === args.name);
    if (!target) { console.log('  ❌ 未找到:', args.name); await browser.close(); process.exit(1); }
    resolvedId = target.id;
  }

  process.stdout.write('  → AUSF/UDM ' + resolvedId + ' ... ');
  try {
    const ok = await modifyAndSubmit(page, resolvedId, args.fields);
    console.log(ok ? '✅' : '❌');
    await browser.close();
    process.exit(ok ? 0 : 1);
  } catch (e) { console.log('❌', e.message); await browser.close(); process.exit(1); }
}

main().catch(e => { console.error('错误:', e.message); process.exit(1); });
