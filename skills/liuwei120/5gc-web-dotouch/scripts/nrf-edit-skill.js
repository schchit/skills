/**
 * NRF 编辑脚本
 * 完整流程：登录 → 选工程 → 进NRF列表 → 点编辑(弹窗iframe) → 填表单 → 提交 → 验证
 * 用法:
 *   node nrf-edit-skill.js --project <工程> --set-<字段> <值>     # 批量
 *   node nrf-edit-skill.js --name <名称> --project <工程> --set-<字段> <值>  # 单条
 * 示例:
 *   node nrf-edit-skill.js --project XW_S5GC_1 --set-http2_sip 10.0.0.1
 *   node nrf-edit-skill.js --name NRF-TEST --project XW_S5GC_1 --set-http2_sip 10.0.0.1
 */

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const BASE_URL = 'https://192.168.3.89';
const SESSION_DIR = path.join(__dirname, '.sessions');

function getSessionFile() {
  const host = BASE_URL.replace(/https?:\/\//, '').replace(/\./g, '_');
  return `5gc_session_${host}.json`;
}

function parseArgs() {
  const args = process.argv.slice(2);
  const fields = {};
  let name = null, project = 'XW_S5GC_1', headed = false;
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--name' && i + 1 < args.length) name = args[++i];
    else if ((args[i] === '--project' || args[i] === '-p') && i + 1 < args.length) project = args[++i];
    else if (args[i] === '--headed') headed = true;
    else if (args[i].startsWith('--set-')) {
      const k = args[i].slice(6).replace(/-/g, '_');
      fields[k] = args[i + 1] != null && !args[i + 1].startsWith('--') ? args[++i] : 'true';
    }
  }
  return { fields, name, project, headed };
}

async function login(page) {
  const sessionPath = path.join(SESSION_DIR, getSessionFile());
  if (fs.existsSync(sessionPath)) {
    try {
      const storageState = JSON.parse(fs.readFileSync(sessionPath, 'utf8'));
      if (storageState.cookies) {
        await page.context().addCookies(storageState.cookies);
        await page.goto(BASE_URL + '/sim_5gc/project/index', { waitUntil: 'networkidle', timeout: 8000 }).catch(() => {});
        if (!page.url().includes('/login')) {
          console.log('  ✅ 使用缓存会话');
          return true;
        }
      }
    } catch {}
  }
  await page.goto(BASE_URL + '/login', { waitUntil: 'networkidle', timeout: 15000 });
  await page.getByRole('textbox', { name: 'E-Mail地址' }).fill('dotouch@dotouch.com.cn');
  await page.getByRole('textbox', { name: '密码' }).fill('dotouch');
  await page.getByRole('button', { name: '登录' }).click();
  await page.waitForLoadState('networkidle');
  const ctx = page.context();
  const storageState = await ctx.storageState();
  fs.writeFileSync(sessionPath, JSON.stringify({ cookies: storageState.cookies }, null, 2));
  console.log('  ✅ 登录成功');
  return true;
}

async function selectProject(page, projectName) {
  await page.goto(BASE_URL + '/sim_5gc/project/index', { waitUntil: 'networkidle', timeout: 15000 });
  await page.waitForSelector('.jsgrid-row, .jsgrid-alt-row', { timeout: 5000 }).catch(() => {});
  await page.waitForTimeout(300);

  for (let pageNum = 1; pageNum <= 200; pageNum++) {
    const clicked = await page.evaluate((targetName) => {
      const rows = document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row');
      for (const row of rows) {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 3 && cells[2].textContent.trim() === targetName) {
          const icon = cells[1].querySelector('.iconfont');
          if (icon) { icon.click(); return true; }
        }
      }
      return false;
    }, projectName);

    if (clicked) { await page.waitForTimeout(2000); return true; }

    const nextBtn = page.locator('.jsgrid-pager a:has-text("Next")');
    if (!(await nextBtn.count())) break;
    try { await nextBtn.click(); } catch { break; }
    await page.waitForTimeout(1500);
  }
  console.log(`  ❌ 未找到工程 "${projectName}"`);
  return false;
}

async function main() {
  const { fields, name: targetName, project, headed } = parseArgs();
  if (Object.keys(fields).length === 0) {
    console.error('请至少指定一个 --set-<字段>'); process.exit(1);
  }

  console.log(`▶ NRF 编辑  工程: ${project}   字段: ${JSON.stringify(fields)}`);

  const browser = await chromium.launch({ headless: !headed, args: ['--no-sandbox', '--ignore-certificate-errors'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();

  await login(page);
  const ok = await selectProject(page, project);
  if (!ok) throw new Error('工程选择失败');
  console.log(`  ✅ 工程已选`);

  // 进入 NRF 列表
  await page.evaluate(() => {
    const links = document.querySelectorAll('a[href*="/nrf/"]');
    for (const l of links) {
      if (l.textContent.trim().includes('NRF')) { l.click(); return; }
    }
  });
  await page.waitForTimeout(2500);
  console.log('  ✓ 进入NRF列表，URL:', page.url());

  // 收集 NRF 行
  const rows = await page.locator('.layui-table tbody tr').all();
  const targets = [];
  for (const row of rows) {
    const cells = await row.locator('td').all();
    if (cells.length >= 10) {
      const id = parseInt((await cells[1].textContent()).trim(), 10);
      const name = (await cells[2].textContent()).trim();
      if (!isNaN(id) && name && (!targetName || name === targetName)) {
        targets.push({ id, name });
      }
    }
  }

  if (targets.length === 0) { console.log('  未找到匹配的 NRF'); await browser.close(); return; }
  console.log(`  找到 ${targets.length} 个 NRF`);

  for (const nrf of targets) {
    process.stdout.write(`▶ [${nrf.id}] ${nrf.name} ... `);
    try {
      // 重新进入 NRF 列表
      await page.evaluate(() => {
        const links = document.querySelectorAll('a[href*="/nrf/"]');
        for (const l of links) {
          if (l.textContent.trim().includes('NRF')) { l.click(); return; }
        }
      });
      await page.waitForTimeout(2000);

      // 找到该行的编辑按钮
      const allRows = await page.locator('.layui-table tbody tr').all();
      let opened = false;
      for (const row of allRows) {
        const cells = await row.locator('td').all();
        if (cells.length >= 10 && parseInt((await cells[1].textContent()).trim(), 10) === nrf.id) {
          await cells[9].locator('a:has-text("编辑")').click();
          opened = true;
          break;
        }
      }
      if (!opened) { console.log('❌ 打开编辑弹窗失败'); continue; }

      // 等待弹窗
      await page.waitForSelector('iframe[name="layui-layer-iframe2"]', { timeout: 5000 });
      await page.waitForTimeout(2000);

      const frame = page.frame('layui-layer-iframe2');
      if (!frame) { console.log('❌ 未找到 iframe'); continue; }
      await frame.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(500);

      // 填写字段（使用 locator.fill）
      if (fields.http2_sip) await frame.locator('input[name="http2_sip"]').fill(fields.http2_sip);
      if (fields.http2_port) await frame.locator('input[name="http2_port"]').fill(fields.http2_port);
      if (fields.MCC) await frame.getByRole('textbox', { name: '三位数字', exact: true }).fill(fields.MCC);
      if (fields.MNC) await frame.getByRole('textbox', { name: '二位或三位数字' }).fill(fields.MNC);

      // 点提交
      await frame.locator('button:has-text("提交")').click();
      await page.waitForTimeout(2000);

      // 强制关闭 layer
      await page.evaluate(() => {
        const b = document.querySelector('.layui-layer-close');
        if (b) b.click();
      });
      await page.waitForTimeout(1000);

      // 重新进入列表，验证
      await page.evaluate(() => {
        const links = document.querySelectorAll('a[href*="/nrf/"]');
        for (const l of links) {
          if (l.textContent.trim().includes('NRF')) { l.click(); return; }
        }
      });
      await page.waitForTimeout(2000);

      const rows2 = await page.locator('.layui-table tbody tr').all();
      let found = false;
      for (const row of rows2) {
        const cells = await row.locator('td').all();
        if (cells.length >= 10 && parseInt((await cells[1].textContent()).trim(), 10) === nrf.id) {
          await cells[9].locator('a:has-text("编辑")').click();
          await page.waitForTimeout(2000);
          await page.waitForSelector('iframe[name="layui-layer-iframe2"]', { timeout: 5000 });
          await page.waitForTimeout(500);

          const frame2 = page.frame('layui-layer-iframe2');

          let verified = true;
          let actualVal = 'N/A';
          if (fields.http2_sip) {
            actualVal = await frame2.locator('input[name="http2_sip"]').inputValue();
            verified = verified && actualVal === fields.http2_sip;
          }
          if (fields.http2_port) verified = verified && (await frame2.locator('input[name="http2_port"]').inputValue()) === fields.http2_port;
          if (fields.MCC) verified = verified && (await frame2.getByRole('textbox', { name: '三位数字', exact: true }).inputValue()) === fields.MCC;
          if (fields.MNC) verified = verified && (await frame2.getByRole('textbox', { name: '二位或三位数字' }).inputValue()) === fields.MNC;

          console.log(verified ? '✅' : '❌');
          found = true;

          await page.evaluate(() => { const b = document.querySelector('.layui-layer-close'); if (b) b.click(); });
          break;
        }
      }
      if (!found) console.log('❌');
    } catch (e) {
      console.log(`❌ ${e.message}`);
    }
  }

  await browser.close();
}

main().catch(e => { console.error('❌', e.message); process.exit(1); });
