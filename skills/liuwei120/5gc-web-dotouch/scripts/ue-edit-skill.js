/**
 * UE 编辑脚本 - ue-edit-skill.js
 *
 * 单个编辑: node ue-edit-skill.js --id <ue_id> [--field <字段名> --value <值>]
 *          node ue-edit-skill.js --name <ue_name> --set-<field> <value>
 *
 * 批量编辑: node ue-edit-skill.js --project <工程> --set-<field> <value>
 *
 * 可编辑字段: name, mcc, mnc, s_imsi, key, op_opc, imeisv, msisdn,
 *            user_sip_ip_v4, user_sip_ip_v6, replay_ip, replay_port,
 *            nssai_sst, nssai_sd 等
 *
 * 示例:
 *   node ue-edit-skill.js --id 10337 --set-msisdn 8611111111112
 *   node ue-edit-skill.js --name UE_TEST_001 --set-msisdn 8611111111112
 *   node ue-edit-skill.js --project XW_S5GC_1 --set-msisdn 8611111111112
 */
const { chromium } = require('playwright');

const BASE_URL = 'https://192.168.3.89';
const LOGIN_EMAIL = 'dotouch@dotouch.com.cn';
const LOGIN_PWD = 'dotouch';

// 解析 --set-<field> <value> 参数
function parseSetArgs(argv) {
  const sets = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--set-msisdn') sets.msisdn = argv[++i];
    else if (argv[i] === '--set-imsi') sets.s_imsi = argv[++i];
    else if (argv[i] === '--set-mcc') sets.mcc = argv[++i];
    else if (argv[i] === '--set-mnc') sets.mnc = argv[++i];
    else if (argv[i] === '--set-key') sets.key = argv[++i];
    else if (argv[i] === '--set-opc') sets.op_opc = argv[++i];
    else if (argv[i] === '--set-imeisv') sets.imeisv = argv[++i];
    else if (argv[i] === '--set-name') sets.name = argv[++i];
    else if (argv[i] === '--set-sst') sets.nssai_sst = argv[++i];
    else if (argv[i] === '--set-sd') sets.nssai_sd = argv[++i];
    else if (argv[i] === '--set-user_sip_ip_v4') sets.user_sip_ip_v4 = argv[++i];
    else if (argv[i] === '--set-user_sip_ip_v6') sets.user_sip_ip_v6 = argv[++i];
    else if (argv[i] === '--set-replay_ip') sets.replay_ip = argv[++i];
    else if (argv[i] === '--set-replay_port') sets.replay_port = argv[++i];
    else if (argv[i] === '--set-count') sets.count = argv[++i];
  }
  return sets;
}

const argv = process.argv.slice(2);
const args = {};
let projectExplicit = false; // 标记 project 是否显式传入
for (let i = 0; i < argv.length; i++) {
  if (argv[i] === '--id') args.id = argv[++i];
  else if (argv[i] === '--name') args.name = argv[++i];
  else if (argv[i] === '--project') { args.project = argv[++i]; projectExplicit = true; }
  else if (argv[i] === '--url') args.url = argv[++i];
  else if (argv[i] === '--headed') args.headed = true;
}
args.sets = parseSetArgs(argv);
args.url = args.url || BASE_URL;

if (!args.id && !args.name && !args.project) {
  console.log('用法:');
  console.log('  单个编辑: node ue-edit-skill.js --id <ue_id> --set-<field> <value>');
  console.log('  按名称:   node ue-edit-skill.js --name <ue_name> --set-<field> <value>');
  console.log('  批量:     node ue-edit-skill.js --project <工程> --set-<field> <value>');
  console.log('\n可编辑字段: msisdn, imsi, mcc, mnc, key, opc, imeisv, name, sst, sd, user_sip_ip_v4, user_sip_ip_v6, replay_ip, replay_port, count');
  process.exit(1);
}

const BASE = args.url;
const HEADLESS = !args.headed;
console.log('▶ UE 编辑');
console.log('  URL:', BASE);
if (args.id) console.log('  UE ID:', args.id);
if (args.name) console.log('  UE 名称:', args.name);
if (args.project) console.log('  工程:', args.project);
console.log('  修改字段:', args.sets);

(async () => {
  const browser = await chromium.launch({ headless: HEADLESS, args: ['--no-sandbox','--ignore-certificate-errors'] });
  const context = await browser.newContext({ ignoreHTTPSErrors: true });
  const page = await context.newPage();

  // 登录
  await page.goto(BASE + '/login', { waitUntil: 'networkidle', timeout: 15000 });
  await page.getByRole('textbox', { name: 'E-Mail地址' }).fill(LOGIN_EMAIL);
  await page.getByRole('textbox', { name: '密码' }).fill(LOGIN_PWD);
  await page.getByRole('checkbox', { name: '记住我' }).check();
  await page.getByRole('button', { name: '登录' }).click();
  await page.waitForLoadState('networkidle');
  console.log('  ✓ 登录成功');

  // 选择工程（单个编辑和批量编辑都需要）
  if (args.project) {
    const ok = await selectProject(page, args.project);
    if (!ok) throw new Error('工程选择失败: ' + args.project);
    console.log('  ✓ 工程已选:', args.project);
  } else if (!args.id && !args.name) {
    // 既没有 --id/--name 也没有 --project，报错
    console.error('用法: node ue-edit-skill.js --id <ue_id> --set-<field> <value>');
    console.error('       node ue-edit-skill.js --project <工程> --set-<field> <value>');
    process.exit(1);
  }

  // ===== 单个编辑 =====
  if (args.id || args.name) {
    let ueId = args.id;
    if (!ueId) {
      ueId = await findUeIdByName(page, args.name);
      if (!ueId) throw new Error('未找到 UE: ' + args.name);
      console.log('  ✓ 找到 UE ID:', ueId);
    }
    await editUeById(page, ueId, args.sets);
  } else if (projectExplicit) {
    // ===== 批量编辑: 仅在显式传入 --project 时执行 =====
    const count = await bulkEditUe(page, args.sets, args.name || null);
    console.log('  ✓ 批量编辑完成，共', count, '个 UE');
  }

  await browser.close();
  console.log('完成');
})().catch(e => { console.error('异常:', e.message); process.exit(1); });

/**
 * 填写 UE 表单字段
 */
async function fillUeForm(page, sets) {
  // 基本字段
  if (sets.name) { await page.locator('input[name="name"]').fill(sets.name); await page.waitForTimeout(100); }
  if (sets.count) { await page.locator('input[name="count"]').fill(sets.count); await page.waitForTimeout(100); }
  if (sets.mcc) { await page.locator('input[name="mcc"]').fill(sets.mcc); await page.waitForTimeout(100); }
  if (sets.mnc) { await page.locator('input[name="mnc"]').fill(sets.mnc); await page.waitForTimeout(100); }
  if (sets.s_imsi) { await page.locator('input[name="s_imsi"]').fill(sets.s_imsi); await page.waitForTimeout(100); }
  if (sets.key) { await page.locator('input[name="key"]').fill(sets.key); await page.waitForTimeout(100); }
  if (sets.op_opc) { await page.locator('input[name="op_opc"]').fill(sets.op_opc); await page.waitForTimeout(100); }
  if (sets.imeisv) { await page.locator('input[name="imeisv"]').fill(sets.imeisv); await page.waitForTimeout(100); }
  if (sets.msisdn) { await page.locator('input[name="msisdn"]').fill(sets.msisdn); await page.waitForTimeout(100); }
  if (sets.user_sip_ip_v4) { await page.locator('input[name="user_sip_ip_v4"]').fill(sets.user_sip_ip_v4); await page.waitForTimeout(100); }
  if (sets.user_sip_ip_v6) { await page.locator('input[name="user_sip_ip_v6"]').fill(sets.user_sip_ip_v6); await page.waitForTimeout(100); }
  if (sets.replay_ip) { await page.locator('input[name="replay_ip"]').fill(sets.replay_ip); await page.waitForTimeout(100); }
  if (sets.replay_port) { await page.locator('input[name="replay_port"]').fill(sets.replay_port); await page.waitForTimeout(100); }

  // NSSAI
  if (sets.nssai_sst || sets.nssai_sd) {
    const nssaiAddBtn = page.locator('button.nssaiAdd');
    if (await nssaiAddBtn.count() > 0) {
      await nssaiAddBtn.click();
      await page.waitForTimeout(500);
    }
    if (sets.nssai_sst) {
      const sst = page.locator('input[name="nssai[snssai_sst][]"]');
      if (await sst.count() > 0) await sst.first().fill(sets.nssai_sst);
    }
    if (sets.nssai_sd) {
      const sd = page.locator('input[name="nssai[snssai_sd][]"]');
      if (await sd.count() > 0) await sd.first().fill(sets.nssai_sd);
    }
  }
}

/**
 * 通过 ID 编辑单个 UE
 */
async function editUeById(page, ueId, sets) {
  // 确保工程上下文：先进入 UE 列表
  await page.goto(BASE_URL + '/sim_5gc/ue/index', { waitUntil: 'networkidle', timeout: 15000 });
  await page.waitForTimeout(3000);
  const url0 = page.url();
  // 如果在工程选择页，说明需要先选工程
  if (url0.includes('/project/index')) {
    await selectProject(page, 'XW_S5GC_1');
    console.log('  ✓ 工程已选: XW_S5GC_1');
    await page.waitForTimeout(1000);
  }

  await page.goto(BASE_URL + '/sim_5gc/ue/edit/' + ueId, { waitUntil: 'networkidle', timeout: 15000 });
  await page.waitForTimeout(3000);
  const url = page.url();
  if (!url.includes('/ue/edit/')) {
    console.log('  ⚠ UE ID ' + ueId + ' 不存在（URL: ' + url + ')');
    return;
  }
  await fillUeForm(page, sets);
  await page.waitForTimeout(500);

  // 提交
  await page.evaluate(() => {
    const btn = document.querySelector('button[lay-filter="formDemo"]');
    if (btn) btn.click();
  });
  await page.waitForTimeout(4000);

  const finalUrl = page.url();
  if (finalUrl.includes('/ue/index')) {
    console.log('  ✓ UE ID', ueId, '修改成功');
  } else {
    const err = await page.locator('.layui-layer-msg').innerText().catch(() => '');
    console.log('  ⚠ UE ID', ueId, '修改后 URL:', finalUrl, err ? '错误: ' + err : '');
  }
}

/**
 * 在 UE 列表中根据名称找 ID
 */
async function findUeIdByName(page, name) {
  await page.goto(BASE_URL + '/sim_5gc/ue/index', { waitUntil: 'networkidle', timeout: 15000 });
  await page.waitForTimeout(3000);
  const rows = await page.locator('.layui-table tbody tr').all();
  for (const row of rows) {
    const cells = await row.locator('td').all();
    if (cells.length >= 3) {
      const cell2 = await cells[2].innerText().catch(() => '');
      if (cell2.trim() === name) {
        // ID 在 cells[1]
        const idCell = await cells[1].innerText().catch(() => '');
        return idCell.trim();
      }
    }
  }
  return null;
}

/**
 * 批量编辑: 对工程下所有 UE 进行字段修改
 * @param {string|null} nameFilter - 可选，按名称过滤
 */
async function bulkEditUe(page, sets, nameFilter = null) {
  await page.goto(BASE_URL + '/sim_5gc/ue/index', { waitUntil: 'networkidle', timeout: 15000 });
  await page.waitForTimeout(3000);

  const rows = await page.locator('.layui-table tbody tr').all();
  let count = 0;
  const processedIds = new Set();
  for (const row of rows) {
    const cells = await row.locator('td').all();
    if (cells.length < 3) continue;
    const idCell = await cells[1].innerText().catch(() => '');
    const nameCell = await cells[2].innerText().catch(() => '');
    const id = idCell.trim();
    const name = nameCell.trim();
    // 跳过表头、空行、按钮行、或已处理过的 ID
    if (!id || id === 'ID' || !name || name === '编辑' || processedIds.has(id)) continue;
    // 如果指定了 nameFilter，只处理该名称的 UE
    if (nameFilter && name !== nameFilter) continue;
    processedIds.add(id);
    await editUeById(page, id, sets);
    count++;
  }
  return count;
}

/**
 * 选择工程
 */
async function selectProject(page, projectName) {
  await page.goto(BASE_URL + '/sim_5gc/project/index', { waitUntil: 'networkidle', timeout: 15000 });
  try { await page.waitForSelector('.jsgrid-row, .jsgrid-alt-row', { timeout: 10000 }); } catch {}
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

    if (result === 'already-selected') { await page.waitForTimeout(2000); return true; }
    if (result === 'clicked') { await page.waitForTimeout(3000); return true; }

    const nextBtn = page.locator('.jsgrid-pager a').filter({ hasText: 'Next' }).first();
    if (!(await nextBtn.count())) break;
    try {
      // Use JS click instead of Playwright click for jsgrid pagination reliability
      await page.evaluate(() => {
        const links = document.querySelectorAll('.jsgrid-pager a');
        for (const link of links) {
          if (link.innerText.trim() === 'Next') { link.click(); break; }
        }
      });
      await page.waitForTimeout(2000);
    } catch { break; }
  }
  return false;
}
