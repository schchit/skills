#!/usr/bin/env node
/**
 * SMF/PGW-C 编辑脚本（单条 + 批量二合一）
 * 用法: node smf-pgwc-edit-skill.js [--project 工程] [--headed] --set-<字段名> <值>
 * 示例: node smf-pgwc-edit-skill.js --project XW_S5GC_basic --set-http2_sip 200.20.20.99
 *       node smf-pgwc-edit-skill.js --project XW_S5GC_basic --set-http2_sip 200.20.20.99 --set-pfcp_sip 200.20.20.88 --headed
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

let BASE_URL = 'https://192.168.3.89';
const CONFIG = {
  urls: { login: '/login', smfList: '/sim_5gc/smf/index' },
  credentials: { email: 'dotouch@dotouch.com.cn', password: 'dotouch' },
  sessionDir: path.join(__dirname, '.sessions'),
  getSessionFile() {
    return `5gc_smf_bulk_${BASE_URL.replace(/https?:\/\//, '').replace(/\./g, '_')}.json`;
  }
};

class SessionManager {
  constructor() {
    if (!fs.existsSync(CONFIG.sessionDir)) fs.mkdirSync(CONFIG.sessionDir, { recursive: true });
    this.sp = path.join(CONFIG.sessionDir, CONFIG.getSessionFile());
  }
  async loadSession(browser) {
    if (!fs.existsSync(this.sp)) return null;
    try {
      const { storageState } = JSON.parse(fs.readFileSync(this.sp, 'utf8'));
      return await browser.newContext({ storageState, ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
    } catch { return null; }
  }
  async saveSession(context) {
    fs.writeFileSync(this.sp, JSON.stringify({ storageState: await context.storageState() }, null, 2));
  }
}

// 选择工程
async function selectProject(page, projectName) {
  await page.goto(`${BASE_URL}/sim_5gc/project/index`, { waitUntil: 'networkidle', timeout: 15000 });
  try {
    await page.waitForSelector('.jsgrid-row, .jsgrid-alt-row', { timeout: 10000 });
  } catch {
    console.log('  ⚠ 等待 jsgrid 行超时');
  }
  await page.waitForTimeout(2000);

  for (let pageNum = 1; pageNum <= 20; pageNum++) {
    const result = await page.evaluate((target) => {
      const rows = document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row');
      // 遍历所有行的工程名，找到目标工程
      for (const row of rows) {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 3 && cells[2].textContent.trim() === target) {
          // 只有同时具备 'jsgrid-selected-row' class 才认为已选中
          if (row.classList.contains('jsgrid-selected-row')) {
            return 'already-selected';
          }
          // 未选中，则尝试点击该行的控制按钮（图标）进行切换
          const controlCell = row.querySelector('.jsgrid-cell.jsgrid-control-field');
          if (controlCell) {
            const icon = controlCell.querySelector('.layui-icon');
            if (icon) { icon.click(); return 'clicked'; }
          }
          // 若没有控制按钮，直接点击行
          row.click();
          return 'clicked';
        }
      }
      return 'not-found';
    }, projectName);

    if (result === 'already-selected') {
      console.log('  ✓ 工程已在第一行（已选中状态），跳过');
      await page.waitForTimeout(2000);
      return true;
    }
    if (result === 'clicked') {
      console.log('  ✓ 已点击工程行图标，等待切换...');
      await page.waitForTimeout(3000);
      return true;
    }

    const nextBtn = page.locator('.jsgrid-pager a').filter({ hasText: 'Next' }).first();
    if (!(await nextBtn.count())) { console.log('  ⚠ 已到最后一页'); break; }
    try {
      await nextBtn.click({ force: true });
      await page.waitForTimeout(2000);
    } catch { break; }
  }
  console.log(`  ❌ 未找到工程 "${projectName}"`);
  return false;
}

// 获取 SMF 列表所有 ID（去重）
async function fetchAllSmfIds(page, nameFilter = null) {
  return await page.evaluate((filter) => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    const ids = [];
    const seen = new Set();
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 3) {
        const id = cells[1].textContent.trim();
        const name = cells[2].textContent.trim();
        if (id && !seen.has(id) && (!filter || name === filter)) {
          seen.add(id);
          ids.push(id);
        }
      }
    }
    return ids;
  }, nameFilter);
}

// 编辑单个 SMF
async function editSingleSmf(page, smfId, edits) {
  const editUrl = `${BASE_URL}/sim_5gc/smf/edit/${smfId}`;
  await page.goto(editUrl, { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  // 只修改用户指定的字段
  for (const [field, val] of Object.entries(edits)) {
    const selector = `input[name="${field}"]`;
    try {
      await page.waitForSelector(selector, { state: 'visible', timeout: 5000 });
      await page.click(selector, { force: true });
      await page.fill(selector, val);
      console.log(`  ✓ ${field} → ${val}`);
    } catch {
      console.log(`  ⚠ 字段 ${field} 未找到或无法填写`);
    }
  }
  console.log('  ✓ 字段修改完成');

  // 提交
  await page.getByRole('button', { name: '提交' }).click();
  await page.waitForTimeout(3000);

  const success = page.url().includes('smf/index');
  if (!success) console.log('  ⚠ 提交后未返回列表，可能失败');
  return success;
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length < 1) {
    console.log('用法: node smf-pgwc-edit-skill.js [--project 工程] [--headed] --set-<字段名> <值>');
    console.log('示例: node smf-pgwc-edit-skill.js --project XW_S5GC_basic --set-http2_sip 200.20.20.99');
    console.log('       node smf-pgwc-edit-skill.js --project XW_S5GC_basic --set-http2_sip 200.20.20.99 --set-pfcp_sip 200.20.20.88 --headed');
    console.log('');
    console.log('支持的字段: http2_sip, http2_port, pfcp_sip, pfcp_port, ue_min, ue_max, pdu_capacity, mcc, mnc');
    process.exit(1);
  }

  let projectName = 'XW_S5GC_1';
  let nameFilter = null;
  let headless = true;
  const edits = {};

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--project') {
      projectName = args[++i];
    } else if (args[i] === '--name') {
      nameFilter = args[++i];
    } else if (args[i] === '--headed') {
      headless = false;
    } else if (args[i].startsWith('--set-')) {
      const field = args[i].slice(6);
      edits[field] = args[++i];
    } else if (!args[i].startsWith('-')) {
      if (!nameFilter) nameFilter = args[i];
    }
  }

  if (Object.keys(edits).length === 0) {
    console.log('用法: node smf-pgwc-edit-skill.js [--project 工程] [--name <名称>] [--headed] --set-<字段名> <值>');
    console.log('示例: node smf-pgwc-edit-skill.js --project XW_S5GC_1 --name SMF001 --set-pfcp_ip 10.0.0.5');
    process.exit(1);
  }

  console.log(`▶ 批量编辑 SMF,工程: ${projectName}${nameFilter ? '，名称: ' + nameFilter : ''}`);
  console.log(`  修改字段:`, edits);
  console.log(`  模式: ${headless ? '无头' : '有头'}`);

  const sessionMgr = new SessionManager();
  const browser = await chromium.launch({ headless, args: ['--no-sandbox', '--ignore-certificate-errors'] });
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

  // 选工程
  const ok = await selectProject(page, projectName);
  if (!ok) throw new Error('工程选择失败');
  console.log('  ✓ 工程已选');

  // 进 SMF 列表
  await page.goto(`${BASE_URL}${CONFIG.urls.smfList}`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  // 获取所有 SMF ID
  const smfIds = await fetchAllSmfIds(page, nameFilter);
  if (smfIds.length === 0) {
    console.log('  ⚠ 工程下没有 SMF');
    await browser.close();
    return;
  }
  console.log(`  found ${smfIds.length} SMF(s) in project "${projectName}"`);

  // 逐个编辑
  let successCount = 0;
  for (let i = 0; i < smfIds.length; i++) {
    const smfId = smfIds[i];
    console.log(`\n[${i + 1}/${smfIds.length}] 编辑 SMF ID: ${smfId}`);
    const ok = await editSingleSmf(page, smfId, edits);
    if (ok) successCount++;
  }

  console.log(`\n=== 完成 ===`);
  console.log(`成功编辑 ${successCount} / ${smfIds.length} 个 SMF`);

  await browser.close();
}

main().catch(e => { console.error('异常:', e.message); process.exit(1); });
