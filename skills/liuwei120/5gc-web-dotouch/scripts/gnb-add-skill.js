#!/usr/bin/env node
/**
 * GNB 添加脚本
 * 用法: node gnb-add-skill.js <名称> [--headed] [--ngap_sip IP] [--project 工程]
 * 示例: node gnb-add-skill.js GNB-TEST
 *       node gnb-add-skill.js GNB-TEST --ngap_sip 200.20.20.50 --headed
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

let BASE_URL = 'https://192.168.3.89';
const CONFIG = {
  urls: { login: '/login', gnbList: '/sim_5gc/gnb/index' },
  credentials: { email: 'dotouch@dotouch.com.cn', password: 'dotouch' },
  sessionDir: path.join(__dirname, '.sessions'),
  getSessionFile() {
    return `5gc_gnb_add_${BASE_URL.replace(/https?:\/\//, '').replace(/\./g, '_')}.json`;
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
    // Try Playwright click on .project_select td first (most reliable)
    const found = await page.evaluate((target) => {
      const rows = document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row');
      for (const row of rows) {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 3 && cells[2].textContent.trim() === target) {
          const td = row.querySelector('td.project_select');
          if (td) {
            td.click();
            return true;
          }
        }
      }
      return false;
    }, projectName);

    if (found) {
      await page.waitForTimeout(2000);
      return true;
    }

    const nextBtn = page.locator('.jsgrid-pager a').filter({ hasText: 'Next' }).first();
    if (!(await nextBtn.count())) { console.log('  ⚠ 已到最后一页'); break; }
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

async function main() {
  const args = process.argv.slice(2);
  if (args.length < 1) {
    console.log('用法: node gnb-add-skill.js <名称> [--project <工程>] [--ngap_sip <IP>] [--headed]');
    console.log('       [--user_sip_ip_v4 <IP>] [--mcc <值>] [--mnc <值>]');
    console.log('       [--stac <值>] [--etac <值>] [--node_id <ID>] [--cell_count <数量>]');
    console.log('示例: node gnb-add-skill.js GNB-TEST --project XW_S5GC_1');
    console.log('       node gnb-add-skill.js GNB-PROD --ngap_sip 200.20.20.100 --mcc 460 --mnc 60 --stac 1 --etac 10');
    process.exit(1);
  }

  const gnbName = args[0];
  let headless = true;
  let project = 'XW_S5GC_1';
  let ngap_sip = '200.20.20.50';
  let user_sip_ip_v4 = '2.2.2.2';
  let mcc = '460';
  let mnc = '60';
  let stac = '0';
  let etac = '0';
  let node_id = '70';
  let cell_count = '1';

  for (let i = 1; i < args.length; i++) {
    if (args[i] === '--headed') {
      headless = false;
    } else if ( args[i] === '--ngap_sip') {
      ngap_sip = args[++i];
    } else if (args[i] === '--project') {
      project = args[++i];
    } else if (args[i] === '--user_sip_ip_v4') {
      user_sip_ip_v4 = args[++i];
    } else if (args[i] === '--mcc') {
      mcc = args[++i];
    } else if (args[i] === '--mnc') {
      mnc = args[++i];
    } else if (args[i] === '--stac') {
      stac = args[++i];
    } else if (args[i] === '--etac') {
      etac = args[++i];
    } else if (args[i] === '--node_id') {
      node_id = args[++i];
    } else if (args[i] === '--cell_count') {
      cell_count = args[++i];
    }
  }

  console.log(`▶ 添加 GNB: ${gnbName}`);
  console.log(`  ngap_sip=${ngap_sip} user_sip_ip_v4=${user_sip_ip_v4} mcc=${mcc} mnc=${mnc}`);
  console.log(`  TAC=${stac}~${etac} node_id=${node_id} cell_count=${cell_count}`);
  console.log(`  模式: ${headless ? '无头' : '有头'}  工程: ${project}`);

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
  const ok = await selectProject(page, project);
  if (!ok) throw new Error('工程选择失败');
  console.log('  ✓ 工程已选');

  // 进 GNB 列表，点添加
  await page.goto(`${BASE_URL}${CONFIG.urls.gnbList}`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  await page.locator('button:has-text("添加"), a:has-text("添加")').first().click();
  await page.waitForTimeout(2000);
  console.log('  ✓ 进入添加页面');

  // ===== 填写表单（用 page.fill 确保 layui 能收到事件） =====

  // 1. 名称
  await page.locator('input[name="name"]').fill(gnbName);
  console.log(`  ✓ name = ${gnbName}`);

  // 2. 类型下拉：点击打开，再用 Playwright 点击 dd 选项（触发真实事件）
  await page.locator('.layui-form-select >> nth=0').click();
  await page.waitForTimeout(500);
  await page.locator('dd[lay-value="1"] >> nth=0').click();
  await page.waitForTimeout(500);
  console.log('  ✓ 类型 = 仿真设备');

  // 3. 数量
  await page.locator('input[name="count"]').fill(cell_count);
  console.log(`  ✓ count = ${cell_count}`);

  // 4. NGAP起始IP
  await page.locator('input[name="ngap_sip"]').fill(ngap_sip);
  console.log(`  ✓ ngap_sip = ${ngap_sip}`);

  // 5. 用户面起始IP（SBI IP地址）
  await page.locator('input[name="user_sip_ip_v4"]').fill(user_sip_ip_v4);
  console.log(`  ✓ user_sip_ip_v4 = ${user_sip_ip_v4}`);

  // 6. MCC/MNC
  await page.locator('textarea[name="mcc"]').fill(mcc);
  await page.locator('textarea[name="mnc"]').fill(mnc);
  console.log(`  ✓ mcc = ${mcc}, mnc = ${mnc}`);

  // 7. TAC范围
  await page.locator('input[name="stac"]').fill(stac);
  await page.locator('input[name="etac"]').fill(etac);
  console.log(`  ✓ TAC = ${stac}~${etac}`);

  // 8. node_id
  await page.locator('input[name="node_id"]').fill(node_id);
  console.log(`  ✓ node_id = ${node_id}`);

  console.log('  ✓ 表单填写完成');

  // 拦截提交后的 response
  let submitResponse = null;
  page.on('response', res => {
    if (res.url().includes('/sim_5gc/gnb/') && res.status() >= 200 && res.status() < 400) {
      submitResponse = { status: res.status(), url: res.url() };
    }
  });

  // 提交
  await page.getByRole('button', { name: '确定' }).click();
  await page.waitForTimeout(3000);
  console.log('  最终 URL:', page.url());

  // 判断成功：重定向到 /gnb/index，或者收到 200/302 响应
  const url = page.url();
  let success = false;
  if (url.includes('gnb/index')) {
    // 进一步检查：看是否还在添加页（可能失败）
    const onEditPage = await page.evaluate(() => document.querySelector('input[name="name"]') !== null);
    success = !onEditPage;
  }

  if (success) {
    console.log('  ✅ 添加成功');
  } else {
    console.log('  ⚠ 可能未保存，请检查页面');
    // 检查错误信息
    const errorMsg = await page.evaluate(() => {
      const err = document.querySelector('.layui-layer-msg, .layui-layer-content');
      return err ? err.textContent.trim() : '';
    });
    if (errorMsg) console.log('  错误信息:', errorMsg);
  }

  await browser.close();
}

main().catch(e => { console.error('异常:', e.message); process.exit(1); });
