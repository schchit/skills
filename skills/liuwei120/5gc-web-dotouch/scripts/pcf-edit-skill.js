/**
 * pcf-edit-skill.js - PCF/PCRF 编辑
 */
const { chromium } = require('playwright');

const globalBaseUrl = 'https://192.168.3.89';

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
  await page.goto(`${globalBaseUrl}/login`, { ignoreHTTPSErrors: true, timeout: 15000 });
  await page.waitForTimeout(1500);
  await page.getByRole('textbox', { name: 'E-Mail地址' }).fill('dotouch@dotouch.com.cn');
  await page.getByRole('textbox', { name: '密码' }).fill('dotouch');
  await page.getByRole('button', { name: '登录' }).click();
  await page.waitForTimeout(2500);
  console.log('✅ 登录成功');
}

async function selectProject(page, projectName) {
  await page.goto(`${globalBaseUrl}/sim_5gc/project/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(2000);
  let found = false;
  for (const row of await page.locator('.jsgrid-row, .jsgrid-alt-row').all()) {
    const cells = await row.locator('td').all();
    if (cells.length >= 3) {
      const text = (await cells[2].textContent()).trim();
      if (text === projectName) {
        await cells[1].locator('.iconfont').click();
        found = true;
        break;
      }
    }
  }
  if (!found) { console.error(`❌ 未找到工程: ${projectName}`); process.exit(1); }
  await page.waitForTimeout(3000);
  console.log(`✅ 工程 "${projectName}" 已选`);
}

async function main() {
  const { fields, name: targetName, project, headed } = parseArgs();
  if (Object.keys(fields).length === 0) {
    console.error('请至少指定一个 --set-<字段>'); process.exit(1);
  }

  const browser = await chromium.launch({ headless: !headed, args: ['--no-sandbox', '--ignore-certificate-errors'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();

  await login(page);
  await selectProject(page, project);

  await page.goto(`${globalBaseUrl}/sim_5gc/pcf/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(2000);

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

  if (targets.length === 0) { console.log('未找到匹配的 PCF'); await browser.close(); return; }
  console.log(`找到 ${targets.length} 个 PCF`);

  for (const pcf of targets) {
    process.stdout.write(`▶ [${pcf.id}] ${pcf.name} ... `);
    try {
      await page.goto(`${globalBaseUrl}/sim_5gc/pcf/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
      await page.waitForTimeout(2000);

      const allRows = await page.locator('.layui-table tbody tr').all();
      let opened = false;
      for (const row of allRows) {
        const cells = await row.locator('td').all();
        if (cells.length >= 10 && parseInt((await cells[1].textContent()).trim(), 10) === pcf.id) {
          await cells[9].locator('a:has-text("编辑")').click();
          opened = true;
          break;
        }
      }
      if (!opened) { console.log('❌ 打开弹窗失败'); continue; }

      await page.waitForSelector('iframe[name="layui-layer-iframe2"]', { timeout: 5000 });
      await page.waitForTimeout(2000);

      const frame = page.locator('iframe[name="layui-layer-iframe2"]').contentFrame();
      await page.waitForTimeout(500);

      if (fields.http2_sip) await frame.locator('input[name="http2_sip"]').fill(fields.http2_sip);
      if (fields.http2_port) await frame.locator('input[name="http2_port"]').fill(fields.http2_port);
      if (fields.MCC) await frame.locator('input[name="MCC"]').fill(fields.MCC);
      if (fields.MNC) await frame.locator('input[name="MNC"]').fill(fields.MNC);
      if (fields.count) await frame.locator('input[name="count"]').fill(String(fields.count));

      await frame.locator('button:has-text("提交")').click();

      await page.waitForTimeout(2000);
      await page.evaluate(() => {
        const b = document.querySelector('.layui-layer-close');
        if (b) b.click();
      });
      await page.waitForTimeout(1000);

      await page.goto(`${globalBaseUrl}/sim_5gc/pcf/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
      await page.waitForTimeout(2000);

      const rows2 = await page.locator('.layui-table tbody tr').all();
      let found = false;
      for (const row of rows2) {
        const cells = await row.locator('td').all();
        if (cells.length >= 10 && parseInt((await cells[1].textContent()).trim(), 10) === pcf.id) {
          await cells[9].locator('a:has-text("编辑")').click();
          await page.waitForTimeout(2000);
          await page.waitForSelector('iframe[name="layui-layer-iframe2"]', { timeout: 5000 });
          await page.waitForTimeout(500);

          const frame2 = page.locator('iframe[name="layui-layer-iframe2"]').contentFrame();

          let verified = true;
          let actualVal = 'N/A';
          if (fields.http2_sip) {
            actualVal = await frame2.locator('input[name="http2_sip"]').inputValue();
            verified = verified && actualVal === fields.http2_sip;
          }
          if (fields.http2_port) verified = verified && (await frame2.locator('input[name="http2_port"]').inputValue()) === fields.http2_port;
          if (fields.MCC) verified = verified && (await frame2.locator('input[name="MCC"]').inputValue()) === fields.MCC;
          if (fields.MNC) verified = verified && (await frame2.locator('input[name="MNC"]').inputValue()) === fields.MNC;

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

main().catch(e => { console.error(e); process.exit(1); });
