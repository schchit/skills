#!/usr/bin/env node
/**
 * SMF/PGW-C 添加脚本
 * 用法: node smf-pgwc-add-skill.js <名称> [--project <工程>] [--url <地址>] [--headed] \
 *       [--pfcp_sip <IP>] [--http2_sip <IP>] [--mcc <值>] [--mnc <值>] \
 *       [--pdu_capacity <数量>] [--ue_min <IP>] [--ue_max <IP>] \
 *       [--interest_tac <TAC列表>]
 * 示例: node smf-pgwc-add-skill.js SMF-TEST --project XW_S5GC_1
 *       node smf-pgwc-add-skill.js SMF-PROD --pfcp_sip 10.10.10.50 --http2_sip 10.10.10.51 --mcc 460 --mnc 01
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
    return `5gc_smf_add_${BASE_URL.replace(/https?:\/\//, '').replace(/\./g, '_')}.json`;
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

// 选择工程（点击目标工程行内的 .layui-icon 图标）
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
    console.log('用法: node smf-pgwc-add-skill.js <名称> [--project <工程>] [--url <地址>] [--headed]');
    console.log('       [--pfcp_sip <IP>] [--http2_sip <IP>] [--mcc <值>] [--mnc <值>]');
    console.log('       [--pdu_capacity <数量>] [--ue_min <IP>] [--ue_max <IP>] [--interest_tac <TAC列表>]');
    console.log('示例: node smf-pgwc-add-skill.js SMF-TEST --project XW_S5GC_1');
    console.log('       node smf-pgwc-add-skill.js SMF-PROD --pfcp_sip 10.10.10.50 --mcc 460 --mnc 01');
    process.exit(1);
  }

  const smfName = args[0];
  let headless = true;
  let url = BASE_URL;
  let project = 'XW_S5GC_1';
  // 可选字段
  let pfcp_sip = '200.20.20.25';
  let http2_sip = '200.20.20.25';
  let mcc = '460';
  let mnc = '01';
  let pdu_capacity = '200000';
  let ue_min = '30.30.30.20';
  let ue_max = '30.31.30.20';
  let interest_tac = '101\n102';

  for (let i = 1; i < args.length; i++) {
    if (args[i] === '--headed') {
      headless = false;
    } else if (args[i] === '--url') {
      url = args[++i].startsWith('http') ? args[i] : `https://${args[i]}`;
    } else if (args[i] === '--project') {
      project = args[++i];
    } else if (args[i] === '--pfcp_sip') {
      pfcp_sip = args[++i];
    } else if (args[i] === '--http2_sip') {
      http2_sip = args[++i];
    } else if (args[i] === '--mcc') {
      mcc = args[++i];
    } else if (args[i] === '--mnc') {
      mnc = args[++i];
    } else if (args[i] === '--pdu_capacity') {
      pdu_capacity = args[++i];
    } else if (args[i] === '--ue_min') {
      ue_min = args[++i];
    } else if (args[i] === '--ue_max') {
      ue_max = args[++i];
    } else if (args[i] === '--interest_tac') {
      interest_tac = args[++i].replace(/,/g, '\n');
    }
  }

  BASE_URL = url;
  console.log(`▶ 添加 SMF: ${smfName}`);
  console.log(`  模式: ${headless ? '无头' : '有头'}`);
  console.log(`  工程: ${project}`);
  console.log(`  pfcp_sip=${pfcp_sip} http2_sip=${http2_sip} mcc=${mcc} mnc=${mnc} pdu_capacity=${pdu_capacity}`);

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

  // 进 SMF 列表
  await page.goto(`${BASE_URL}${CONFIG.urls.smfList}`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  // 点添加按钮
  await page.locator('button:has-text("添加"), a:has-text("添加")').first().click();
  await page.waitForTimeout(2000);
  console.log('  ✓ 进入添加页面');

  // ===== 填写表单 =====
  // 1. 名称
  await page.locator('input[name="name"]').fill(smfName);
  console.log(`  ✓ name = ${smfName}`);

  // 2. N4/Sxb起始IP（必填）
  await page.locator('input[name="pfcp_sip"]').fill(pfcp_sip);
  console.log(`  ✓ pfcp_sip = ${pfcp_sip}`);

  // 3. SBI起始地址
  await page.locator('input[name="http2_sip"]').fill(http2_sip);
  console.log(`  ✓ http2_sip = ${http2_sip}`);

  // 4. 选择类型：仿真设备
  await page.getByRole('textbox', { name: '请选择' }).first().click();
  await page.waitForTimeout(300);
  await page.getByRole('definition').filter({ hasText: '仿真设备' }).click();
  await page.waitForTimeout(300);
  console.log('  ✓ 类型 = 仿真设备');

  // 5. 上行隧道信息分配：UPF
  await page.getByRole('textbox', { name: '请选择' }).nth(1).click();
  await page.waitForTimeout(300);
  await page.getByRole('definition').filter({ hasText: 'UPF' }).click();
  await page.waitForTimeout(300);
  console.log('  ✓ 上行隧道 = UPF');

  // 6. UE IP分配：SMF
  await page.getByRole('textbox', { name: '请选择' }).nth(2).click();
  await page.waitForTimeout(300);
  await page.getByRole('definition').filter({ hasText: 'SMF' }).click();
  await page.waitForTimeout(300);
  console.log('  ✓ UE IP分配 = SMF');

  // 7. UE IPv4池
  await page.locator('input[name="ue_min"]').fill(ue_min);
  await page.locator('input[name="ue_max"]').fill(ue_max);
  console.log(`  ✓ ue_min = ${ue_min}, ue_max = ${ue_max}`);

  // 8. UE IPv6池
  await page.locator('input[name="ue_sip6"]').fill('1:2:3:1::1');
  await page.locator('input[name="ue_eip6"]').fill('1:2:3:ffff::1');
  console.log('  ✓ ue_sip6 = 1:2:3:1::1, ue_eip6 = 1:2:3:ffff::1');

  // 9. MCC/MNC
  await page.getByRole('textbox', { name: '三位数字', exact: true }).fill(mcc);
  await page.getByRole('textbox', { name: '二位或三位数字' }).fill(mnc);
  console.log(`  ✓ MCC = ${mcc}, MNC = ${mnc}`);

  // 10. PDU容量
  await page.locator('input[name="pdu_capacity"]').fill(pdu_capacity);
  console.log(`  ✓ pdu_capacity = ${pdu_capacity}`);

  // 11. TAC列表
  await page.locator('textarea[name="interest_tac"]').fill(interest_tac);
  console.log(`  ✓ interest_tac = ${interest_tac.replace(/\n/g, ',')}`);

  // 12. TAC/NSSAI 配置区域（可选，暂跳过避免弹窗干扰提交）
  // 如需配置，请在添加成功后手动编辑
  console.log('  ℹ TAC/NSSAI配置暂跳过（添加后可手动编辑）');

  console.log('  ✓ 表单填写完成');

  // 关闭遮罩层
  await page.evaluate(() => {
    document.querySelectorAll('.layui-layer-shade').forEach(el => el.remove());
    document.querySelectorAll('.layui-layer').forEach(el => el.style.display = 'none');
  });
  await page.waitForTimeout(300);

  // 提交
  await page.getByRole('button', { name: '提交' }).click();
  await page.waitForTimeout(3000);
  console.log('  最终 URL:', page.url());

  const success = page.url().includes('smf/index');
  console.log(success ? '  ✅ 添加成功' : '  ⚠ 可能未保存，请检查页面（可加 --headed 查看）');

  await browser.close();
}

main().catch(e => { console.error('异常:', e.message); process.exit(1); });
