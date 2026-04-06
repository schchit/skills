#!/usr/bin/env node
/**
 * UPF/PGW-U 编辑脚本（单条 + 批量二合一） - 生产版
 * 用法: node upf-edit-skill.js [--project <工程名称>] --set-<字段名> <值>
 * 示例: node upf-edit-skill.js --project XW_S5GC_basic \
 *          --set-n4_ip 9.9.9.9 --set-n3_ip 3.3.3.3
 *
 * 脚本会在指定工程下遍历所有 UPF,逐个打开编辑页面并写入提供的字段值。
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

let BASE_URL = 'https://192.168.3.89';
const CONFIG = {
  urls: { login: '/login', upfList: '/sim_5gc/upf/index' },
  credentials: { email: 'dotouch@dotouch.com.cn', password: 'dotouch' },
  sessionDir: path.join(__dirname, '.sessions'),
  getSessionFile() {
    return `5gc_upf_bulk_${BASE_URL.replace(/https?:\/\//, '').replace(/\./g, '_')}.json`;
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

// 选择工程（点击目标工程行内的 .layui-icon 图标）
async function selectProject(page, projectName) {
  await page.goto(`${BASE_URL}/sim_5gc/project/index`, { waitUntil: 'networkidle', timeout: 15000 });
  // 等待 jsgrid 表格渲染完成（最多 10 秒）
  try {
    await page.waitForSelector('.jsgrid-row, .jsgrid-alt-row', { timeout: 10000 });
  } catch {
    console.log('  ⚠ 等待 jsgrid 行超时');
  }
  await page.waitForTimeout(2000); // 额外等待确保页面完全就绪

  for (let pageNum = 1; pageNum <= 20; pageNum++) {
    // 在当前页查找目标工程行
    const result = await page.evaluate((target) => {
      const rows = document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row');
      for (const row of rows) {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 3 && cells[2].textContent.trim() === target) {
          // 只有同时具备 'jsgrid-selected-row' class 才认为已选中
          if (row.classList.contains('jsgrid-selected-row')) {
            return 'already-selected';
          }
          // 未选中，点击该行控制列中的 .layui-icon 图标进行切换
          const controlCell = row.querySelector('.jsgrid-cell.jsgrid-control-field');
          if (controlCell) {
            const icon = controlCell.querySelector('.layui-icon');
            if (icon) {
              icon.click();
              return 'clicked';
            }
          }
          // 备用：直接点击行
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
      await page.waitForTimeout(3000); // 等待工程切换（行会跑到第一行）
      return true;
    }

    // 当前页未找到，尝试翻页
    const nextBtn = page.locator('.jsgrid-pager a').filter({ hasText: 'Next' }).first();
    if (!(await nextBtn.count())) {
      console.log('  ⚠ 已到最后一页，仍未找到工程');
      break;
    }
    try {
      await nextBtn.click({ force: true });
      await page.waitForTimeout(2000);
    } catch {
      break;
    }
  }
  console.log(`  ❌ 未找到工程 "${projectName}"`);
  return false;
}

/**
 * 获取当前列表页所有 UPF 的 ID
 */
async function fetchAllUpfIds(page, nameFilter = null) {
  // 表格结构: 第2列为 ID,第3列为名称（去重）
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

/**
 * 对单个 UPF 执行编辑操作
 */
async function editSingleUpf(page, upfId, edits) {
  // 只修改用户指定的字段，不触碰其他字段
  const editUrl = `${BASE_URL}/sim_5gc/upf/edit/${upfId}`;
  await page.goto(editUrl, { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  // 使用 page.fill 方式写入字段（点击 → 输入 → 触发完整事件链）
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
  // 通过是否回到列表页判断成功
  const success = page.url().includes('upf/index');
  if (!success) console.log('  ⚠ 提交后未返回列表，可能失败');
  return success;
}

async function main() {
  // 参数解析
  const args = process.argv.slice(2);
  let projectName = 'XW_S5GC_1';
  let nameFilter = null;
  const edits = {};
  let headless = true; // 默认无头模式
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--project') {
      projectName = args[++i];
    } else if (args[i] === '--name') {
      nameFilter = args[++i];
    } else if (args[i] === '--headed') {
      headless = false;
    } else if (args[i].startsWith('--set-')) {
      // '--set-' is 5 chars, the field name starts after that. Slice from index 6 to drop the extra '-'
      const field = args[i].slice(6);
      edits[field] = args[++i];
    } else if (!args[i].startsWith('-')) {
      if (!nameFilter) nameFilter = args[i];
    }
  }
  if (Object.keys(edits).length === 0) {
    console.log('用法: node upf-edit-skill.js [--project <工程>] [--headed] --set-<字段> <值>');
    console.log('示例: node upf-edit-skill.js --project XW_S5GC_basic --set-n4_ip 9.9.9.9');
    console.log('  --headed  打开浏览器窗口（调试用）');
    process.exit(1);
  }
  console.log(`▶ 批量编辑 UPF,工程: ${projectName}${nameFilter ? '，名称: ' + nameFilter : ''}`);
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
  const projOk = await selectProject(page, projectName);
  if (!projOk) throw new Error('工程选择失败');
  console.log('  ✓ 工程已选');

  // 进入 UPF 列表
  await page.goto(`${BASE_URL}${CONFIG.urls.upfList}`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  // 读取全部 UPF ID
  const upfIds = await fetchAllUpfIds(page, nameFilter);
  console.log(`  found ${upfIds.length} UPF(s) in project "${projectName}"`);

  let successCount = 0;
  for (let idx = 0; idx < upfIds.length; idx++) {
    const id = upfIds[idx];
    console.log(`\n[${idx + 1}/${upfIds.length}] 编辑 UPF ID: ${id}`);
    try {
      const ok = await editSingleUpf(page, id, edits);
      if (ok) {
        console.log('  ✅ 编辑成功');
        successCount++;
      } else {
        console.log('  ⚠ 编辑后未返回列表,可能失败');
      }
    } catch (e) {
      console.log('  ❌ 异常:', e.message);
    }
    // 防止触发风控,稍作延迟
    await page.waitForTimeout(1500);
  }

  console.log('\n=== 完成 ===');
  console.log(`成功编辑 ${successCount} / ${upfIds.length} 个 UPF`);
  await browser.close();
}

main().catch(e => { console.error('异常:', e.message); process.exit(1); });
