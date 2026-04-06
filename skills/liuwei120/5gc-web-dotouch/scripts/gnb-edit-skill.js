#!/usr/bin/env node
/**
 * GNB 编辑脚本（单条 + 批量二合一）
 * 用法: node gnb-edit-skill.js [--project 工程] [--headed] --set-<字段名> <值>
 * 示例: node gnb-edit-skill.js --project XW_S5GC_basic --set-replay_ip 200.20.20.250
 *       node gnb-edit-skill.js --project XW_S5GC_basic --set-stac 0 --set-etac 0 --headed
 *
 * 支持的字段: name, count, ngap_sip, ngap_port, user_sip_ip_v4, user_sip_ip_v6,
 *            mcc, mnc, stac, etac, node_id, node_id_len, replay_ip, replay_port,
 *            cell_count, position_x, position_y, gateway_ind
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'https://192.168.3.89';
const CONFIG = {
  urls: { login: '/login', gnbList: '/sim_5gc/gnb/index' },
  credentials: { email: 'dotouch@dotouch.com.cn', password: 'dotouch' },
  sessionDir: path.join(__dirname, '.sessions'),
  getSessionFile() {
    return `5gc_gnb_bulk_${BASE_URL.replace(/https?:\/\//, '').replace(/\./g, '_')}.json`;
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
      for (const row of rows) {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 3 && cells[2].textContent.trim() === target) {
          if (row.classList.contains('jsgrid-selected-row')) return 'already-selected';
          const controlCell = row.querySelector('.jsgrid-cell.jsgrid-control-field');
          if (controlCell) {
            const icon = controlCell.querySelector('.layui-icon');
            if (icon) { icon.click(); return 'clicked'; }
          }
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

// 获取 GNB 列表所有 ID（layui-table）
async function fetchAllGnbIds(page, nameFilter = null) {
  // 等待行出现
  await page.waitForTimeout(3000);

  return await page.evaluate((filter) => {
    // layui-table: tbody tr 中每行 td 顺序对应列
    const tbody = document.querySelector('.layui-table-body');
    if (!tbody) return [];
    const rows = tbody.querySelectorAll('tr');
    const ids = [];
    const seen = new Set();
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 3) {
        // GNB 列表列顺序: ID(col1), 名称(col2), NGAP起始IP(col3), ...
        const id = cells[1].textContent.trim();  // 第2列是 ID
        const name = cells[2].textContent.trim(); // 第3列是名称
        // filter 为空则全部通过，为空字符串则跳过表头
        if (id && !seen.has(id) && (!filter || name === filter)) {
          seen.add(id);
          ids.push(id);
        }
      }
    }
    return ids;
  }, nameFilter);
}

// 编辑单个 GNB
async function editSingleGnb(page, gnbId, edits) {
  const editUrl = `${BASE_URL}/sim_5gc/gnb/edit/${gnbId}`;
  await page.goto(editUrl, { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  for (const [field, val] of Object.entries(edits)) {
    const inputSelector = `input[name="${field}"], textarea[name="${field}"]`;
    try {
      const exists = await page.locator(inputSelector).count();
      if (exists === 0) {
        console.log(`  ⚠ 字段 ${field} 不存在，跳过`);
        continue;
      }
      await page.locator(inputSelector).fill(String(val));
      console.log(`  ✓ ${field} → ${val}`);
    } catch (e) {
      console.log(`  ⚠ 字段 ${field} 填写失败`);
    }
  }

  // 提交
  await page.getByRole('button', { name: '确定' }).click();
  await page.waitForTimeout(3000);

  const success = page.url().includes('gnb/index');
  if (!success) console.log('  ⚠ 提交后未返回列表，可能失败');
  return success;
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length < 1) {
    console.log('用法: node gnb-edit-skill.js [--project 工程] [--headed] --set-<字段名> <值>');
    console.log('示例: node gnb-edit-skill.js --project XW_S5GC_basic --set-replay_ip 200.20.20.250');
    console.log('       node gnb-edit-skill.js --project XW_S5GC_basic --set-stac 0 --set-etac 0 --headed');
    console.log('');
    console.log('支持的字段: name, count, ngap_sip, ngap_port, user_sip_ip_v4, user_sip_ip_v6,');
    console.log('           mcc, mnc, stac, etac, node_id, node_id_len, replay_ip, replay_port,');
    console.log('           cell_count, position_x, position_y, gateway_ind');
    process.exit(1);
  }

  let projectName = 'XW_S5GC_1';
  let headless = true;
  let nameFilter = null; // --name 时只编辑该名称的 GNB
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
      // 兼容不带 --name 的位置参数
      if (!nameFilter) nameFilter = args[i];
    }
  }

  if (Object.keys(edits).length === 0) {
    console.log('请指定要修改的字段，例如: --set-replay_ip 200.20.20.250');
    process.exit(1);
  }

  console.log(`▶ 批量编辑 GNB，工程: ${projectName}${nameFilter ? '，名称: ' + nameFilter : ''}`);
  for (const [k, v] of Object.entries(edits)) console.log(`  修改: ${k} = ${v}`);
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

  // 进 GNB 列表
  await page.goto(`${BASE_URL}${CONFIG.urls.gnbList}`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(4000);  // 等待 layui-table 渲染

  // 获取所有 GNB ID
  const gnbIds = await fetchAllGnbIds(page, nameFilter);
  if (gnbIds.length === 0) {
    console.log('  ⚠ 工程下没有 GNB');
    await browser.close();
    return;
  }
  console.log(`  ✓ 找到 ${gnbIds.length} 个 GNB`);

  // 逐个编辑
  let successCount = 0;
  for (let i = 0; i < gnbIds.length; i++) {
    const gnbId = gnbIds[i];
    console.log(`\n[${i + 1}/${gnbIds.length}] 编辑 GNB ID: ${gnbId}`);
    const ok = await editSingleGnb(page, gnbId, edits);
    if (ok) successCount++;
  }

  console.log(`\n=== 完成 ===`);
  console.log(`成功编辑 ${successCount} / ${gnbIds.length} 个 GNB`);

  await browser.close();
}

main().catch(e => { console.error('异常:', e.message); process.exit(1); });
