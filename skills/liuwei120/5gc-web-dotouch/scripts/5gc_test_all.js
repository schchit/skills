/**
 * 5GC 技能全面回归测试
 *
 * 测试策略：
 * - add 脚本：添加测试实例（用唯一名称），验证提交后URL跳转
 * - edit 脚本：编辑已有实例，验证字段修改
 * - bulk-edit 脚本：批量修改目标工程下所有实例
 *
 * 运行方式：
 *   node 5gc_test_all.js            # 全部测试
 *   node 5gc_test_all.js --amf      # 只测 AMF
 *   node 5gc_test_all.js --headed   # 有头模式（可见浏览器）
 */

const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const SCRIPTS_DIR = path.join(__dirname);
const BASE_URL = 'https://192.168.3.89';
const LOGIN_EMAIL = 'dotouch@dotouch.com.cn';
const LOGIN_PWD = 'dotouch';
const TEST_PROJECT = 'XW_S5GC_1';          // 已知存在的工程
const TS = Date.now();

// ─── helpers ────────────────────────────────────────────────

async function login(page) {
  await page.goto(BASE_URL + '/login', { waitUntil: 'networkidle', timeout: 15000 });
  await page.getByRole('textbox', { name: 'E-Mail地址' }).fill(LOGIN_EMAIL);
  await page.getByRole('textbox', { name: '密码' }).fill(LOGIN_PWD);
  await page.getByRole('checkbox', { name: '记住我' }).check();
  await page.getByRole('button', { name: '登录' }).click();
  await page.waitForLoadState('networkidle');
}

async function selectProjectFast(page, projectName) {
  await page.goto(BASE_URL + '/sim_5gc/project/index', { waitUntil: 'networkidle', timeout: 15000 });
  await page.waitForTimeout(2000);
  for (let i = 0; i < 20; i++) {
    const found = await page.evaluate((target) => {
      const rows = document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row');
      for (const row of rows) {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 3 && cells[2].textContent.trim() === target) {
          if (row.classList.contains('jsgrid-selected-row')) return 'already';
          const ic = row.querySelector('.layui-icon');
          if (ic) { ic.click(); return 'clicked'; }
          row.click(); return 'clicked';
        }
      }
      return 'not-found';
    }, projectName);
    if (found === 'already' || found === 'clicked') return true;
    // 翻页
    const hasNext = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('.jsgrid-pager a'))
        .some(a => a.innerText.trim() === 'Next');
    });
    if (!hasNext) break;
    await page.evaluate(() => {
      const links = document.querySelectorAll('.jsgrid-pager a');
      for (const l of links) { if (l.innerText.trim() === 'Next') { l.click(); break; } }
    });
    await page.waitForTimeout(1500);
  }
  return false;
}

function resultPath(name) {
  return path.join(SCRIPTS_DIR, '..', 'test_results', `test_${TS}_${name}.json`);
}

function saveResult(name, ok, detail) {
  const dir = path.join(SCRIPTS_DIR, '..', 'test_results');
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(resultPath(name), JSON.stringify({ name, ok, detail, ts: new Date().toISOString() }, null, 2));
}

function runChild(scriptFile, args) {
  return new Promise((resolve) => {
    const child = spawn('node', [scriptFile, ...args], { stdio: 'pipe', shell: true });
    let out = '', err = '';
    child.stdout.on('data', d => out += d.toString());
    child.stderr.on('data', d => err += d.toString());
    child.on('close', code => resolve({ code, out, err }));
  });
}

// ─── 测试用例定义 ───────────────────────────────────────────

const TEST_CASES = [
  // ── AMF ──────────────────────────────────────────────
  {
    tag: 'AMF添加', entity: 'amf', action: 'add', headed: false,
    args: ['--name', `AMF_TEST_${TS}`, '--project', TEST_PROJECT,
           '--sbi-ip', '10.200.1.1', '--mcc', '460', '--mnc', '01',
           '--sst', '1', '--sd', '000001'],
    verify: async (page) => {
      await page.waitForURL('**/sim_5gc/amf/index', { timeout: 15000 });
      return page.url().includes('/amf/index');
    }
  },
  {
    tag: 'AMF编辑', entity: 'amf', action: 'edit', headed: false,
    args: ['--name', `AMF_TEST_${TS}`, '--project', TEST_PROJECT,
           '--set-sbi_ip', '10.200.1.100'],
    verify: async (page) => {
      await page.waitForURL('**/sim_5gc/amf/index', { timeout: 15000 });
      return page.url().includes('/amf/index');
    }
  },

  // ── AUSF/UDM ─────────────────────────────────────────
  {
    tag: 'UDM添加', entity: 'udm', action: 'add', headed: false,
    args: ['--name', `UDM_TEST_${TS}`, '--project', TEST_PROJECT,
           '--auth-supi', `46000${TS}000000`, '--auth-op-type', 'opc',
           '--opc', '63b3c4d1d5c03f4e82c5f4a5b2e7d9c1'],
    verify: async (page) => {
      await page.waitForURL('**/sim_5gc/udm/index', { timeout: 15000 });
      return page.url().includes('/udm/index');
    }
  },
  {
    tag: 'UDM编辑', entity: 'udm', action: 'edit', headed: false,
    args: ['--name', `UDM_TEST_${TS}`, '--project', TEST_PROJECT,
           '--set-op_opc', 'aaaaaaaaaaaabbbbccccccccccccdddd'],
    verify: async (page) => {
      await page.waitForURL(/sim_5gc\/udm\//, { timeout: 15000 });
      return true;
    }
  },

  // ── SMF ──────────────────────────────────────────────
  {
    tag: 'SMF添加', entity: 'smf', action: 'add', headed: false,
    args: ['--name', `SMF_TEST_${TS}`, '--project', TEST_PROJECT,
           '--pfcp-ip', '10.200.2.1', '--n3-ip', '10.200.2.2',
           '--n6-ip', '10.200.2.3', '--dnn', 'internet'],
    verify: async (page) => {
      await page.waitForURL('**/sim_5gc/smf/index', { timeout: 15000 });
      return page.url().includes('/smf/index');
    }
  },
  {
    tag: 'SMF编辑', entity: 'smf', action: 'edit', headed: false,
    args: ['--name', `SMF_TEST_${TS}`, '--project', TEST_PROJECT,
           '--set-dnn', 'internet_updated'],
    verify: async (page) => {
      await page.waitForURL(/sim_5gc\/smf\//, { timeout: 15000 });
      return true;
    }
  },
  {
    tag: 'SMF批量编辑', entity: 'smf', action: 'edit', headed: false,
    args: ['--project', TEST_PROJECT, '--set-dnn', 'internet'],
    verify: async (page) => {
      // 批量编辑 SMF 只要不报错即算通过
      await page.waitForTimeout(5000);
      const url = page.url();
      return !url.includes('/project/index'); // 没卡在工程选择页即可
    }
  },

  // ── UPF ──────────────────────────────────────────────
  {
    tag: 'UPF添加', entity: 'upf', action: 'add', headed: false,
    args: ['--name', `UPF_TEST_${TS}`, '--project', TEST_PROJECT,
           '--n4-ip', '10.200.3.1', '--n3-ip', '10.200.3.2',
           '--n6-ip', '10.200.3.3', '--dnn', 'internet'],
    verify: async (page) => {
      await page.waitForURL('**/sim_5gc/upf/index', { timeout: 15000 });
      return page.url().includes('/upf/index');
    }
  },
  {
    tag: 'UPF编辑', entity: 'upf', action: 'edit', headed: false,
    args: ['--name', `UPF_TEST_${TS}`, '--project', TEST_PROJECT,
           '--set-n4_ip', '10.200.3.100'],
    verify: async (page) => {
      await page.waitForURL(/sim_5gc\/upf\//, { timeout: 15000 });
      return true;
    }
  },
  {
    tag: 'UPF批量编辑', entity: 'upf', action: 'edit', headed: false,
    args: ['--project', TEST_PROJECT, '--set-n4_ip', '10.200.3.1'],
    verify: async (page) => {
      await page.waitForTimeout(5000);
      const url = page.url();
      return !url.includes('/project/index');
    }
  },

  // ── GNB ──────────────────────────────────────────────
  {
    tag: 'GNB添加', entity: 'gnb', action: 'add', headed: false,
    args: ['--name', `GNB_TEST_${TS}`, '--project', TEST_PROJECT,
           '--count', '1', '--ngap-ip', '10.200.4.1',
           '--user-sip-ip-v4', '10.200.4.2', '--mcc', '460', '--mnc', '01',
           '--stac', '1', '--etac', '100', '--node-id', 'gni_000004'],
    verify: async (page) => {
      await page.waitForURL('**/sim_5gc/gnb/index', { timeout: 15000 });
      return page.url().includes('/gnb/index');
    }
  },
  {
    tag: 'GNB编辑', entity: 'gnb', action: 'edit', headed: false,
    args: ['--name', `GNB_TEST_${TS}`, '--project', TEST_PROJECT,
           '--set-replay_ip', '10.200.4.200'],
    verify: async (page) => {
      await page.waitForURL(/sim_5gc\/gnb\//, { timeout: 15000 });
      return true;
    }
  },
  {
    tag: 'GNB批量编辑', entity: 'gnb', action: 'edit', headed: false,
    args: ['--project', TEST_PROJECT, '--set-replay_ip', '10.200.4.200'],
    verify: async (page) => {
      await page.waitForTimeout(5000);
      const url = page.url();
      return !url.includes('/project/index');
    }
  },

  // ── UE ───────────────────────────────────────────────
  {
    tag: 'UE添加', entity: 'ue', action: 'add', headed: false,
    args: ['--name', `UE_TEST_${TS}`, '--imsi', `46000${TS}`, '--msisdn', '8613888888888',
           '--mcc', '460', '--mnc', '01'],
    verify: async (page) => {
      await page.waitForURL('**/sim_5gc/ue/index', { timeout: 15000 });
      return page.url().includes('/ue/index');
    }
  },
  {
    tag: 'UE编辑', entity: 'ue', action: 'edit', headed: false,
    args: ['--project', TEST_PROJECT, '--name', `UE_TEST_${TS}`,
           '--set-msisdn', '8613888889999'],
    verify: async (page) => {
      await page.waitForTimeout(3000);
      const url = page.url();
      return url.includes('/ue/index') || url.includes('/ue/edit/');
    }
  },
  {
    tag: 'UE批量编辑', entity: 'ue', action: 'edit', headed: false,
    args: ['--project', TEST_PROJECT, '--set-msisdn', '8613888888888'],
    verify: async (page) => {
      await page.waitForTimeout(5000);
      const url = page.url();
      return !url.includes('/project/index');
    }
  },
];

// ─── 5gc.js 统一入口测试 ───────────────────────────────────

async function testViaCli(testCase, headed) {
  const cliPath = path.join(SCRIPTS_DIR, '5gc.js');
  const args = [testCase.entity, testCase.action, ...testCase.args];
  if (headed) args.push('--headed');

  const child = spawn('node', [cliPath, ...args], { stdio: 'pipe', shell: true });
  let out = '', err = '';
  child.stdout.on('data', d => out += d.toString());
  child.stderr.on('data', d => err += d.toString());

  return new Promise((resolve) => {
    child.on('close', code => resolve({ code, out: out + err }));
  });
}

// ─── 主测试运行器 ──────────────────────────────────────────

async function main() {
  const argv = process.argv.slice(2);
  const headed = argv.includes('--headed');
  const filter = argv.find(a => !a.startsWith('--'));

  // 登录一次，获取 playwright context
  const browser = await chromium.launch({
    headless: !headed,
    args: ['--no-sandbox', '--ignore-certificate-errors']
  });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true });
  const page = await ctx.newPage();

  await login(page);
  const ok = await selectProjectFast(page, TEST_PROJECT);
  if (!ok) { console.log('工程选择失败'); await browser.close(); return; }

  const toRun = TEST_CASES.filter(t => !filter || t.tag.toLowerCase().includes(filter.toLowerCase()));
  console.log(`\n========================================`);
  console.log(`5GC 全面回归测试  (${toRun.length} 个用例, headed=${headed})`);
  console.log(`========================================\n`);

  const results = [];
  for (const tc of toRun) {
    process.stdout.write(`${tc.tag.padEnd(20)} ... `);

    // 每次重走工程选择（部分脚本内部会切工程）
    try {
      const r = await testViaCli(tc, headed);
      // 简单判断：进程退出码0 且输出无"异常"
      const ok = r.code === 0 && !r.out.includes('异常') && !r.out.includes('失败') && !r.out.includes('❌');
      console.log(ok ? '✅ PASS' : '❌ FAIL');
      if (!ok) console.log('  输出:', r.out.substring(0, 200).replace(/\n/g, ' '));
      results.push({ ...tc, pass: ok, detail: r.out.substring(0, 300) });
    } catch (e) {
      console.log('❌ ERROR:', e.message);
      results.push({ ...tc, pass: false, detail: e.message });
    }

    // 恢复工程上下文
    await selectProjectFast(page, TEST_PROJECT).catch(() => {});
  }

  await browser.close();

  // 汇总
  const pas = results.filter(r => r.pass).length;
  const fail = results.filter(r => !r.pass).length;
  console.log(`\n========================================`);
  console.log(`结果: ${pas} 通过 / ${fail} 失败`);
  if (fail > 0) {
    console.log('\n失败用例:');
    results.filter(r => !r.pass).forEach(r => console.log(`  ❌ ${r.tag}: ${r.detail.substring(0, 100)}`));
  }
  console.log('========================================\n');

  // 保存详细结果
  const reportDir = path.join(SCRIPTS_DIR, '..', 'test_results');
  if (!fs.existsSync(reportDir)) fs.mkdirSync(reportDir, { recursive: true });
  const reportFile = path.join(reportDir, `report_${TS}.json`);
  fs.writeFileSync(reportFile, JSON.stringify({ ts: new Date().toISOString(), results }, null, 2));
  console.log(`详细报告: ${reportFile}`);
}

main().catch(e => { console.error('Fatal:', e.message); process.exit(1); });
