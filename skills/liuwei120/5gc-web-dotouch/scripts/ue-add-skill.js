/**
 * UE 添加脚本 - ue-add-skill.js
 * 用法: node ue-add-skill.js --name <名称> [--imsi <imsi>] [--msisdn <msisdn>] [--mcc <mcc>] [--mnc <mnc>] [--project <工程>] [--headed]
 *
 * 工程默认: XW_S5GC_1
 * UE 表单: /sim_5gc/ue/edit（不是工单弹窗）
 */
const { chromium } = require('playwright');

const BASE_URL = 'https://192.168.3.89';
const LOGIN_EMAIL = 'dotouch@dotouch.com.cn';
const LOGIN_PWD = 'dotouch';

const yargs = require('yargs');
const args = yargs(process.argv.slice(2))
  .option('name', { alias: 'n', type: 'string', demandOption: true, describe: 'UE名称（只支持字母/数字/下划线）' })
  .option('url', { alias: 'u', type: 'string', default: BASE_URL, describe: '5GC仪表地址' })
  .option('imsi', { type: 'string', default: '460001234567890', describe: '起始IMSI（15位）' })
  .option('msisdn', { type: 'string', default: '8611111111111', describe: 'MSISDN（13-15位）' })
  .option('mcc', { type: 'string', default: '460', describe: 'MCC' })
  .option('mnc', { type: 'string', default: '01', describe: 'MNC' })
  .option('project', { alias: 'p', type: 'string', default: 'XW_S5GC_1', describe: '工程名称' })
  .option('count', { alias: 'c', type: 'string', default: '1', describe: '数量' })
  .option('key', { type: 'string', default: '11111111111111111111111111111111', describe: 'KI密钥（32位hex）' })
  .option('opc', { type: 'string', default: '11111111111111111111111111111111', describe: 'OPc密钥（32位hex）' })
  .option('imeisv', { type: 'string', default: '8611111111111111', describe: 'IMEISV' })
  .option('sst', { type: 'string', default: '1', describe: 'NSSAI SST' })
  .option('sd', { type: 'string', default: '111111', describe: 'NSSAI SD' })
  .option('headed', { type: 'boolean', default: false, describe: '显示浏览器' })
  .parse();

const HEADLESS = !args.headed;
const BASE = args.url;

console.log('▶ 添加 UE: ' + args.name);
console.log('  URL: ' + BASE);
console.log('  工程: ' + args.project);

(async () => {
  const browser = await chromium.launch({
    headless: HEADLESS,
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--ignore-certificate-errors']
  });
  const context = await browser.newContext({
    ignoreHTTPSErrors: true,
  });
  const page = await context.newPage();

  // 登录
  await page.goto(BASE + '/login', { waitUntil: 'networkidle', timeout: 15000 });
  await page.getByRole('textbox', { name: 'E-Mail地址' }).fill(LOGIN_EMAIL);
  await page.getByRole('textbox', { name: '密码' }).fill(LOGIN_PWD);
  await page.getByRole('checkbox', { name: '记住我' }).check();
  await page.getByRole('button', { name: '登录' }).click();
  await page.waitForLoadState('networkidle');
  console.log('  ✓ 登录成功');

  // 选择工程
  const ok = await selectProject(page, args.project);
  if (!ok) throw new Error('工程选择失败');
  console.log('  ✓ 工程已选: ' + args.project);

  // 直接打开 UE 添加页面（/sim_5gc/ue/edit）
  await page.goto(BASE + '/sim_5gc/ue/edit', { waitUntil: 'networkidle', timeout: 15000 });
  await page.waitForTimeout(3000);
  console.log('  ✓ UE 编辑页已打开');

  // ===== 填写表单 =====
  // 名称
  await page.locator('input[name="name"]').fill(args.name);
  await page.waitForTimeout(100);

  // 数量（必填）
  await page.locator('input[name="count"]').fill(args.count || '1');

  // MCC
  await page.locator('input[name="mcc"]').fill(args.mcc);

  // MNC
  await page.locator('input[name="mnc"]').fill(args.mnc);

  // 勾选所有加密算法（NEA0, NEA1, NEA2, NEA3）和完整性算法（NIA0, NIA1, NIA2, NIA3）
  // layui 隐藏 input → 用 page.evaluate() 直接设 checked + 触发 change 事件
  await page.evaluate(() => {
    const eas = document.querySelectorAll('input[name="ea[]"]');
    for (const cb of eas) {
      if (!cb.checked) {
        cb.checked = true;
        cb.dispatchEvent(new Event('change', { bubbles: true }));
      }
    }
    const ias = document.querySelectorAll('input[name="ia[]"]');
    for (const cb of ias) {
      if (!cb.checked) {
        cb.checked = true;
        cb.dispatchEvent(new Event('change', { bubbles: true }));
      }
    }
  });
  await page.waitForTimeout(200);
  console.log('  → 已勾选全部加密/完整性算法');

  // 起始 IMSI（必填）
  await page.locator('input[name="s_imsi"]').fill(args.imsi);

  // KI（key，必填）
  await page.locator('input[name="key"]').fill(args.key);

  // OPc 类型选择（layui select: 点击 .layui-form-select，再选 dd）
  // 找到 op_opc_tp 对应的 layui-select（通过兄弟元素或位置）
  const opcSelectWrapper = page.locator('.layui-form-select').filter({ has: page.locator('select[name="op_opc_tp"]') });
  if (await opcSelectWrapper.count() > 0) {
    await opcSelectWrapper.click();
    await page.waitForTimeout(500);
    await page.locator('dd[lay-value="opc"]').first().click();
    await page.waitForTimeout(200);
  }

  // OPc 值
  await page.locator('input[name="op_opc"]').fill(args.opc);

  // IMEISV（必填）
  await page.locator('input[name="imeisv"]').fill(args.imeisv || '8611111111111111');

  // MSISDN（必填）
  await page.locator('input[name="msisdn"]').fill(args.msisdn);

  // ===== NSSAI 配置：点击"添加NSSAI"按钮添加一行 =====
  const nssaiAddBtn = page.locator('button.nssaiAdd');
  if (await nssaiAddBtn.count() > 0) {
    await nssaiAddBtn.click();
    await page.waitForTimeout(500);
    console.log('  → NSSAI 行已添加');
  }

  // 填写 NSSAI（SST 和 SD）
  const nssaiSst = page.locator('input[name="nssai[snssai_sst][]"]');
  if (await nssaiSst.count() > 0) {
    await nssaiSst.first().fill(args.sst);
  }
  const nssaiSd = page.locator('input[name="nssai[snssai_sd][]"]');
  if (await nssaiSd.count() > 0) {
    await nssaiSd.first().fill(args.sd);
  }
  console.log('  → NSSAI: SST=' + args.sst + ', SD=' + args.sd);

  await page.waitForTimeout(500);

  // ===== 提交：layui form，用 JS 点击提交按钮 =====
  console.log('  → 提交表单...');
  await page.evaluate(() => {
    const btn = document.querySelector('button[lay-filter="formDemo"]');
    if (btn) btn.click();
  });
  await page.waitForTimeout(5000);

  // 判断是否成功：URL 变成 /ue/index，或者停留在 /ue/edit 但有空值
  const finalUrl = page.url();
  console.log('  → 提交后 URL:', finalUrl);

  // 判断是否成功：跳转到列表验证
  await page.goto(BASE + '/sim_5gc/ue/index', { waitUntil: 'networkidle', timeout: 15000 });
  await page.waitForTimeout(2000);
  const rows = await page.locator('.layui-table tbody tr').all();
  let found = false;
  for (const row of rows) {
    const text = await row.innerText().catch(() => '');
    if (text.includes(args.name)) {
      found = true;
      break;
    }
  }

  if (found) {
    console.log('  ✅ UE 添加成功: ' + args.name);
  } else {
    console.log('  ⚠ UE 添加后列表中未找到（可能在其他页）');
  }

  await browser.close();
  console.log('完成');
})().catch(e => { console.error('异常:', e.message); process.exit(1); });

/**
 * 选择工程（jsgrid 列表，点击控制列图标）
 */
async function selectProject(page, projectName) {
  await page.goto(BASE_URL + '/sim_5gc/project/index', { waitUntil: 'networkidle', timeout: 15000 });
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
      await page.waitForTimeout(2000);
      return true;
    }
    if (result === 'clicked') {
      await page.waitForTimeout(3000);
      return true;
    }

    // 翻页
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
  return false;
}
