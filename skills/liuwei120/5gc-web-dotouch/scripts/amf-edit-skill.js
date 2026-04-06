#!/usr/bin/env node
/**
 * 🚀 AMF配置修改技能 - 智能版本
 * 特性:
 * 1. 智能AMF选择逻辑
 * 2. 基于文字匹配，不使用固定ID
 * 3. 支持部分字段修改
 * 4. 继承登录优化和成功算法配置
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// 配置
let globalBaseUrl = 'https://192.168.3.89';
const CONFIG = {
  baseUrl: globalBaseUrl,
  urls: {
    login: '/login',
    amfManagement: '/sim_5gc/amf/index',
    amfEdit: '/sim_5gc/amf/edit'
  },
  credentials: {
    email: 'dotouch@dotouch.com.cn',
    password: 'dotouch'
  },
  sessionDir: path.join(__dirname, '.sessions'),
  // 动态session文件名：根据URL生成，避免跨仪表缓存冲突
  getSessionFile: function() {
    const host = this.baseUrl.replace(/https?:\/\//, '').replace(/\./g, '_');
    return `5gc_session_${host}.json`;
  }
};

// 会话管理器（复用登录优化）
class SessionManager {
  constructor() {
    this.sessionPath = path.join(CONFIG.sessionDir, CONFIG.getSessionFile());
  }
  
  async saveSession(context) {
    try {
      const storageState = await context.storageState();
      fs.writeFileSync(this.sessionPath, JSON.stringify({ storageState }, null, 2));
      return true;
    } catch (error) {
      return false;
    }
  }
  
  async loadSession(browser) {
    try {
      if (!fs.existsSync(this.sessionPath)) return null;
      
      const { storageState } = JSON.parse(fs.readFileSync(this.sessionPath, 'utf8'));
      const context = await browser.newContext({
        storageState,
        ignoreHTTPSErrors: true,
        viewport: { width: 1920, height: 1080 }
      });
      
      return context;
    } catch (error) {
      return null;
    }
  }
}

// 智能AMF选择器
class AMFSelector {
  constructor(page) {
    this.page = page;
  }
  
  // 获取AMF列表
  async getAMFList() {
    console.log('🔍 获取AMF列表...');
    
    await this.page.goto(`${CONFIG.baseUrl}${CONFIG.urls.amfManagement}`, {
      waitUntil: 'networkidle',
      timeout: 15000
    });
    
    await this.page.waitForTimeout(1000);
    
    // 查找AMF表格
    const tableSelector = 'table.layui-table';
    const tableExists = await this.page.locator(tableSelector).count() > 0;
    
    if (!tableExists) {
      console.log('⚠️ 未找到AMF表格，可能没有配置或页面结构不同');
      
      // 调试：查看页面结构
      const pageText = await this.page.textContent('body').catch(() => '');
      console.log('📄 页面内容片段:', pageText.substring(0, 300));
      
      // 查找其他可能的表格
      const allTables = await this.page.locator('table').all();
      console.log(`🔍 找到 ${allTables.length} 个表格`);
      
      for (let i = 0; i < allTables.length; i++) {
        const table = allTables[i];
        const tableHtml = await table.innerHTML().catch(() => '');
        console.log(`表格 ${i + 1} 片段:`, tableHtml.substring(0, 200));
      }
      
      return [];
    }
    
    // 调试：查看表格内容
    const tableHtml = await this.page.locator(tableSelector).innerHTML().catch(() => '');
    console.log('📊 表格HTML片段:', tableHtml.substring(0, 500));
    
    // 提取AMF名称 - 使用 layui-table 单元格直接定位（稳定可靠）
    // layui-table 列结构: 复选框(0) | ID(1) | 名称(2) | NGAP IP(3) | HTTP2 IP(4) | ...
    const rowSelector = 'table.layui-table tbody tr, .layui-table-body tbody tr';
    const amfRows = await this.page.locator(rowSelector).all();
    const amfList = [];
    
    console.log(`📊 找到 ${amfRows.length} 行数据`);
    
    for (let i = 0; i < amfRows.length; i++) {
      const row = amfRows[i];
      
      // layui-table 列: 复选框(0) | ID(1) | 名称(2) | NGAP IP(3) | HTTP2 IP(4) | 端口(5) | ...
      const cells = await row.locator('td').all();
      if (cells.length < 3) continue;
      
      const idCell = await cells[1].textContent().catch(() => '');
      const nameCell = await cells[2].textContent().catch(() => '');
      const id = idCell.trim();
      const name = nameCell.trim();
      
      if (!id || !id.match(/^\d+$/) || !name || name === '名称' || name === '编辑') continue;
      
      amfList.push({ id, name, row });
      console.log(`    ✅ 提取到: ID=${id}, 名称=${name}`);
    }
    
    // 去重
    const uniqueAmfList = [];
    const seenNames = new Set();
    
    for (const amf of amfList) {
      if (!seenNames.has(amf.name)) {
        seenNames.add(amf.name);
        uniqueAmfList.push(amf);
      }
    }
    
    console.log(`📋 找到 ${uniqueAmfList.length} 个AMF配置:`);
    uniqueAmfList.forEach((amf, idx) => {
      console.log(`  ${idx + 1}. [${amf.id}] ${amf.name}`);
    });
    
    return uniqueAmfList;
  }
  
  // 智能选择AMF
  async selectAMF(amfName = null) {
    const amfList = await this.getAMFList();
    
    if (amfList.length === 0) {
      throw new Error('未找到任何AMF配置，请先添加AMF');
    }
    
    // 情况1: 用户指定了AMF名称
    if (amfName) {
      console.log(`🎯 用户指定AMF名称: "${amfName}"`);
      
      // 精确匹配
      const exactMatch = amfList.find(amf => amf.name === amfName);
      if (exactMatch) {
        console.log(`✅ 找到精确匹配: ${exactMatch.name}`);
        return exactMatch;
      }
      
      // 模糊匹配（包含）
      const fuzzyMatches = amfList.filter(amf => amf.name.includes(amfName));
      if (fuzzyMatches.length === 1) {
        console.log(`✅ 找到模糊匹配: ${fuzzyMatches[0].name}`);
        return fuzzyMatches[0];
      } else if (fuzzyMatches.length > 1) {
        console.log(`⚠️ 找到多个模糊匹配:`);
        fuzzyMatches.forEach((amf, idx) => {
          console.log(`  ${idx + 1}. ${amf.name}`);
        });
        throw new Error(`找到多个匹配的AMF，请指定更精确的名称`);
      }
      
      throw new Error(`未找到名称为"${amfName}"的AMF配置`);
    }
    
    // 情况2: 未指定名称，但只有一个AMF
    if (amfList.length === 1) {
      console.log(`✅ 只有一个AMF配置，自动选择: ${amfList[0].name}`);
      return amfList[0];
    }
    
    // 情况3: 多个AMF，未指定名称 → 返回全部（批量模式）
    console.log(`⚠️ 未指定AMF名称，找到 ${amfList.length} 个AMF → 进入批量修改模式`);
    amfList.forEach((amf, idx) => {
      console.log(`  ${idx + 1}. [${amf.id}] ${amf.name}`);
    });
    return amfList; // 返回数组，editAMF 将检测到并进入批量
  }
  
  // 点击编辑按钮进入编辑页面 - 优先使用URL直接访问
  async clickEditButton(selectedAMF) {
    console.log(`🖱️ 进入编辑页面: ${selectedAMF.name}`);
    
    // 方法1: 直接用ID访问编辑页面（最稳定）
    if (selectedAMF.id) {
      console.log(`  直接访问: /sim_5gc/amf/edit/${selectedAMF.id}`);
      await this.page.goto(`${CONFIG.baseUrl}/sim_5gc/amf/edit/${selectedAMF.id}`);
      await this.page.waitForSelector('input[name="name"]', { timeout: 10000 });
      await this.page.waitForTimeout(1000);
      console.log('✅ 通过URL进入编辑页面');
      return true;
    }
    
    // 方法2: 使用编辑按钮（备用）
    if (selectedAMF.editButton) {
      try {
        await selectedAMF.editButton.click({ timeout: 5000 });
        await this.page.waitForLoadState('networkidle', { timeout: 10000 });
        await this.page.waitForTimeout(1000);
        
        if (this.page.url().includes('/amf/edit')) {
          console.log('✅ 通过编辑按钮进入编辑页面');
          return true;
        }
      } catch (error) {
        console.log(`⚠️ 编辑按钮点击失败: ${error.message}`);
      }
    }
    
    // 方法3: 查找所有编辑按钮，按索引点击
    console.log('🔍 查找所有编辑按钮...');
    const allEditButtons = await this.page.locator('a:has-text("编辑"), button:has-text("编辑")').all();
    console.log(`找到 ${allEditButtons.length} 个编辑按钮`);
    
    if (allEditButtons.length > selectedAMF.index) {
      try {
        await allEditButtons[selectedAMF.index].click({ timeout: 5000 });
        await this.page.waitForLoadState('networkidle', { timeout: 10000 });
        await this.page.waitForTimeout(1000);
        
        if (this.page.url().includes('/amf/edit')) {
          console.log(`✅ 通过索引 ${selectedAMF.index} 进入编辑页面`);
          return true;
        }
      } catch (error) {
        console.log(`⚠️ 索引点击失败: ${error.message}`);
      }
    }
    
    // 方法3: 直接构造编辑URL（RESTful风格）
    console.log('🔗 尝试直接访问编辑URL...');
    if (selectedAMF.id) {
      // 正确的URL格式: /amf/edit/6084 (不是 /amf/edit?id=6084)
      const editUrl = `${CONFIG.baseUrl}/sim_5gc/amf/edit/${selectedAMF.id}`;
      console.log(`访问: ${editUrl}`);
      
      await this.page.goto(editUrl, {
        waitUntil: 'networkidle',
        timeout: 15000
      });
      
      await this.page.waitForTimeout(1000);
      
      if (this.page.url().includes('/amf/edit')) {
        console.log('✅ 通过直接URL进入编辑页面');
        return true;
      }
    }
    
    // 方法4: 使用标准编辑页面URL
    console.log('🌐 尝试标准编辑页面...');
    await this.page.goto(`${CONFIG.baseUrl}${CONFIG.urls.amfEdit}`, {
      waitUntil: 'networkidle',
      timeout: 15000
    });
    
    await this.page.waitForTimeout(1000);
    
    if (this.page.url().includes('/amf/edit')) {
      console.log('✅ 通过标准URL进入编辑页面');
      return true;
    }
    
    throw new Error('无法进入编辑页面，请检查页面结构或权限');
  }
}

// 配置修改器
class ConfigModifier {
  constructor(page) {
    this.page = page;
  }
  
  // 修改配置字段
  async modifyConfig(fieldUpdates = {}) {
    console.log('🔧 修改配置字段...');
    
    if (Object.keys(fieldUpdates).length === 0) {
      console.log('⚠️ 没有需要修改的字段，直接提交');
      return;
    }
    
    // 等待页面加载完成
    await this.page.waitForLoadState('networkidle', { timeout: 10000 });
    
    // 修改字段
    for (const [fieldName, newValue] of Object.entries(fieldUpdates)) {
      await this.updateField(fieldName, newValue);
    }
    
    console.log('✅ 配置修改完成');
  }
  
  // 更新单个字段
  async updateField(fieldName, newValue) {
    console.log(`  📝 修改 ${fieldName}: ${newValue}`);
    
    // 常见字段映射
    const fieldSelectors = {
      // 基础字段
      name: 'input[name="name"]',
      mcc: 'input[name="mcc"]',
      mnc: 'input[name="mnc"]',
      region_id: 'input[name="region_id"]',
      set_id: 'input[name="set_id"]',
      pointer: 'input[name="pointer"]',
      ngap_sip: 'input[name="ngap_sip"]',
      ngap_port: 'input[name="ngap_port"]',
      http2_sip: 'input[name="http2_sip"]',
      http2_port: 'input[name="http2_port"]',
      stac: 'input[name="stac"]',
      etac: 'input[name="etac"]',

      // 算法字段
      'ea[NEA0]': 'input[name="ea[NEA0]"]',
      'ea[128-NEA1]': 'input[name="ea[128-NEA1]"]',
      'ea[128-NEA2]': 'input[name="ea[128-NEA2]"]',
      'ea[128-NEA3]': 'input[name="ea[128-NEA3]"]',
      'ia[NIA0]': 'input[name="ia[NIA0]"]',
      'ia[128-NIA1]': 'input[name="ia[128-NIA1]"]',
      'ia[128-NIA2]': 'input[name="ia[128-NIA2]"]',
      'ia[128-NIA3]': 'input[name="ia[128-NIA3]"]',

      // 设备类型（特殊处理）
      deviceType: 'input[placeholder*="选择"], input[name*="device"]'
    };

    // 设备类型特殊处理（支持仿真设备/被测设备）
    if (fieldName === 'deviceType' || fieldName === 'type') {
      try {
        await this.page.locator('.layui-unselect').first().click();
        await this.page.waitForTimeout(300);
        const targetLabel = newValue === '被测设备' ? '被测设备' : '仿真设备';
        await this.page.locator('dd').filter({ hasText: targetLabel }).click();
        console.log(`    ✅ deviceType 已设置为 ${targetLabel}`);
      } catch (error) {
        console.log(`    ❌ deviceType 设置失败: ${error.message}`);
      }
      return;
    }

    // 算法字段特殊处理（点击 layui 可见复选框，与 amf-add 保持一致）
    if (fieldName.startsWith('ea[') || fieldName.startsWith('ia[')) {
      try {
        const algoMap = {
          'ea[NEA0]': 0, 'ea[128-NEA1]': 1, 'ea[128-NEA2]': 2, 'ea[128-NEA3]': 3,
          'ia[NIA0]': 4, 'ia[128-NIA1]': 5, 'ia[128-NIA2]': 6, 'ia[128-NIA3]': 7
        };
        const idx = algoMap[fieldName];
        if (idx !== undefined) {
          await this.page.locator('.layui-form-checkbox').nth(idx).click();
          await this.page.waitForTimeout(80);
          const inp = this.page.locator(`input[name="${fieldName}"]`);
          if (await inp.count() > 0) {
            await inp.fill(newValue.toString());
          }
          console.log(`    ✅ ${fieldName} 已勾选并设置优先级为 ${newValue}`);
        }
      } catch (error) {
        console.log(`    ❌ ${fieldName} 设置失败: ${error.message}`);
      }
      return;
    }

    let selector = fieldSelectors[fieldName];
    
    if (!selector) {
      // 尝试通用查找
      selector = `input[name*="${fieldName}"], input[placeholder*="${fieldName}"]`;
    }
    
    try {
      const field = this.page.locator(selector).first();
      const count = await field.count();
      
      if (count > 0) {
        await field.click();
        await field.fill('');
        await field.fill(newValue.toString());
        await this.page.waitForTimeout(100);
        console.log(`    ✅ ${fieldName} 修改成功`);
      } else {
        console.log(`    ⚠️ 未找到字段: ${fieldName}`);
      }
    } catch (error) {
      console.log(`    ❌ 修改 ${fieldName} 失败: ${error.message}`);
    }
  }
  
  // 提交修改
  async submitChanges() {
    console.log('📤 提交修改...');
    
    const beforeUrl = this.page.url();
    
    // 查找提交按钮
    const submitButtons = await this.page.locator('button:has-text("提交"), input[type="submit"][value*="提交"]').all();
    
    if (submitButtons.length === 0) {
      throw new Error('未找到提交按钮');
    }
    
    await submitButtons[0].click();
    await this.page.waitForTimeout(5000);
    
    const afterUrl = this.page.url();
    const urlChanged = afterUrl !== beforeUrl;
    
    if (urlChanged) {
      console.log('✅ 提交成功，URL已变化');
    } else {
      console.log('⚠️ URL未变化，但可能已提交成功');
    }
    
    return urlChanged;
  }
}

/**
 * 选择工程函数（支持翻页）
 * @param {Page} page - Playwright页面对象
 * @param {string} projectName - 工程名称
 * @param {boolean} forceSwitch - 是否强制切换工程
 */
async function selectProject(page, projectName, forceSwitch = true) {
  if (!forceSwitch) {
    console.log(`  🔧 保持当前工程（用户未指定工程）`);
    return true;
  }
  await page.goto(`${CONFIG.baseUrl}/sim_5gc/project/index`, {
    waitUntil: 'networkidle',
    timeout: 15000
  });
  await page.waitForSelector('.jsgrid-row, .jsgrid-alt-row', { timeout: 5000 }).catch(() => {});

  // 清除搜索框，避免残留内容干扰
  await page.evaluate(() => {
    const inputs = document.querySelectorAll('input[type="text"], input[name="name"]');
    for (const inp of inputs) { inp.value = ''; }
  });
  await page.waitForTimeout(300);

  for (let pageNum = 1; pageNum <= 200; pageNum++) {
    // 通过 evaluate 点击操作列 td:nth(1) 里的 ● 图标（iconfont layui-ext-xuanzhong1）
    const clicked = await page.evaluate((targetName) => {
      const rows = document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row');
      for (const row of rows) {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 3 && cells[2].textContent.trim() === targetName) {
          // 操作列 td:nth(1) 里的 iconfont 元素是●选择图标
          const icon = cells[1].querySelector('.iconfont');
          if (icon) {
            icon.click();
            return true;
          }
        }
      }
      return false;
    }, projectName);

    if (clicked) {
      await page.waitForTimeout(2000);
      return true;
    }

    const nextBtn = page.locator('.jsgrid-pager a:has-text("Next")');
    if (!(await nextBtn.count())) break;
    try {
      await page.evaluate(() => { var links = document.querySelectorAll('.jsgrid-pager a'); for (var i = 0; i < links.length; i++) { if (links[i].innerText.trim() === 'Next') { links[i].click(); break; } } });
      await page.waitForTimeout(2000);
    } catch { break; }
  }

  console.log(`  ❌ 未找到工程 "${projectName}"（精确匹配）`);
  return false;
}

// 主执行函数
async function editAMF(amfName = null, projectName = '5G_basic_process', fieldUpdates = {}) {
  console.log('='.repeat(60));
  console.log('🚀 AMF配置修改技能 - 智能版本');
  console.log('='.repeat(60));
  
  const startTime = Date.now();
  const sessionManager = new SessionManager();
  let browser = null;
  let skippedLogin = false;
  
  try {
    // 1. 初始化浏览器
    console.log('1. 初始化...');
    browser = await chromium.launch({
      headless: true,
      args: ['--no-sandbox', '--ignore-certificate-errors']
    });
    
    // 2. 尝试加载会话
    let context = await sessionManager.loadSession(browser);
    
    if (context) {
      console.log('✅ 使用缓存会话，跳过登录');
      skippedLogin = true;
    } else {
      console.log('📝 需要登录');
      context = await browser.newContext({
        ignoreHTTPSErrors: true,
        viewport: { width: 1920, height: 1080 }
      });
    }
    
    const page = await context.newPage();
    
    // 3. 登录（如果需要）
    if (!skippedLogin) {
      console.log('2. 登录...');
      await page.goto(`${CONFIG.baseUrl}${CONFIG.urls.login}`, {
        waitUntil: 'networkidle',
        timeout: 15000
      });
      
      await page.getByRole('textbox', { name: 'E-Mail地址' }).fill(CONFIG.credentials.email);
      await page.getByRole('textbox', { name: '密码' }).fill(CONFIG.credentials.password);
      await page.getByRole('button', { name: '登录' }).click();
      await page.waitForLoadState('networkidle', { timeout: 10000 });
      await page.waitForTimeout(1000);
      
      // 保存会话
      await sessionManager.saveSession(context);
      console.log('✅ 登录成功，会话已保存');
    }
    
    // 4. 选择工程
    console.log('3. 选择工程...');
    if (!(await selectProject(page, projectName, true))) {
      throw new Error(`工程 "${projectName}" 不存在或无法选中`);
    }
    
    // 4. 智能选择AMF（支持单条和批量）
    console.log('4. 智能选择AMF...');
    const selector = new AMFSelector(page);
    const selected = await selector.selectAMF(amfName);

    // 5. 进入编辑页面（单条或批量）
    console.log('5. 进入编辑页面...');

    // 批量模式：selected 是 AMF 数组
    if (Array.isArray(selected)) {
      let batchSuccess = 0;
      for (const amf of selected) {
        process.stdout.write(`  ▶ ${amf.name} [${amf.id}] ... `);
        try {
          await selector.clickEditButton(amf);
          const modifier = new ConfigModifier(page);
          await modifier.modifyConfig(fieldUpdates);
          const urlChanged = await modifier.submitChanges();
          await page.waitForTimeout(2000);
          const ok = page.url().includes('/amf/index');
          console.log(ok ? '✅' : '❌');
          if (ok) batchSuccess++;
          // 返回列表页继续下一个
          await page.goto(`${CONFIG.baseUrl}${CONFIG.urls.amfManagement}`, { waitUntil: 'networkidle', timeout: 10000 });
          await page.waitForTimeout(1500);
        } catch (e) {
          console.log(`❌ ${e.message}`);
        }
        await page.waitForTimeout(500);
      }
      await browser.close();
      const totalTime = (Date.now() - startTime) / 1000;
      console.log(`\n批量完成: ${batchSuccess}/${selected.length} 成功  耗时: ${totalTime.toFixed(1)}s`);
      return { success: batchSuccess > 0, batchSummary: { total: selected.length, success: batchSuccess } };
    }

    // 单条模式
    const selectedAMF = selected;
    await selector.clickEditButton(selectedAMF);
    
    // 验证是否在编辑页面
    if (!page.url().includes('/amf/edit')) {
      console.log('⚠️ 当前URL:', page.url());
      console.log('尝试直接访问编辑页面...');
      await page.goto(`${CONFIG.baseUrl}${CONFIG.urls.amfEdit}`, {
        waitUntil: 'networkidle',
        timeout: 10000
      });
    }
    
    console.log('✅ 进入编辑页面');
    
    // 7. 修改配置
    console.log('6. 修改配置...');
    const modifier = new ConfigModifier(page);
    await modifier.modifyConfig(fieldUpdates);
    
    // 8. 提交修改
    console.log('7. 提交修改...');
    const urlChanged = await modifier.submitChanges();
    
    // 9. 验证结果
    console.log('8. 验证结果...');
    await page.goto(`${CONFIG.baseUrl}${CONFIG.urls.amfManagement}`, {
      waitUntil: 'networkidle',
      timeout: 10000
    });
    
    await page.waitForTimeout(2000);
    const pageText = await page.textContent('body').catch(() => '');
    const found = pageText.includes(selectedAMF.name);
    
    // 9. 清理
    await browser.close();
    
    const totalTime = (Date.now() - startTime) / 1000;
    
    console.log('\n' + '='.repeat(60));
    console.log('📊 执行结果');
    console.log('='.repeat(60));
    
    if (found) {
      console.log(`✅ 成功！AMF "${selectedAMF.name}" 修改完成`);
      console.log(`⏱️ 总耗时: ${totalTime.toFixed(2)}秒`);
      console.log(`🔗 URL变化: ${urlChanged ? '是' : '否'}`);
      console.log(`🔑 登录优化: ${skippedLogin ? '使用缓存' : '重新登录'}`);
      console.log(`📝 修改字段: ${Object.keys(fieldUpdates).length} 个`);
      
      if (Object.keys(fieldUpdates).length > 0) {
        console.log('修改详情:');
        Object.entries(fieldUpdates).forEach(([field, value]) => {
          console.log(`  - ${field}: ${value}`);
        });
      }
      
      return {
        success: true,
        amfName: selectedAMF.name,
        totalTime: totalTime,
        urlChanged: urlChanged,
        skippedLogin: skippedLogin,
        modifiedFields: Object.keys(fieldUpdates)
      };
    } else {
      console.log(`❌ 失败！未找到配置 "${selectedAMF.name}"`);
      console.log(`⏱️ 总耗时: ${totalTime.toFixed(2)}秒`);
      
      return {
        success: false,
        amfName: selectedAMF.name,
        totalTime: totalTime
      };
    }
    
  } catch (error) {
    console.error(`❌ 执行失败: ${error.message}`);
    
    if (browser) {
      await browser.close();
    }
    
    return {
      success: false,
      amfName: amfName,
      error: error.message,
      totalTime: (Date.now() - startTime) / 1000
    };
  }
}

// 参数解析
function parseArgs() {
  const args = process.argv.slice(2);
  const result = {
    amfName: null,
    projectName: '5G_basic_process', // 默认工程
    baseUrl: globalBaseUrl, // 默认5GC地址
    fieldUpdates: {}
  };
  
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    
    if (arg.startsWith('--')) {
      const key = arg.substring(2);
      
      if (i + 1 < args.length && !args[i + 1].startsWith('--')) {
        // 字段修改参数: --field value
        if (key.startsWith('set-')) {
          const fieldName = key.substring(4);
          result.fieldUpdates[fieldName] = args[i + 1];
          i++;
        } else if (key === 'amf' || key === 'name') {
          result.amfName = args[i + 1];
          i++;
        } else if (key === 'project' || key === 'p') {
          result.projectName = args[i + 1];
          i++;
        } else if (key === 'url') {
          result.baseUrl = args[i + 1];
          if (!result.baseUrl.startsWith('http')) result.baseUrl = 'https://' + result.baseUrl;
          globalBaseUrl = result.baseUrl;
          CONFIG.baseUrl = result.baseUrl;  // 同步更新CONFIG
          i++;
        }
      } else if (key === 'project' || key === 'p') {
        // --project 但没有指定值，使用默认值
        console.log('⚠️ 使用了--project参数但未指定工程名称，将使用默认工程');
      }
    } else if (i === 0 && !arg.startsWith('--')) {
      // 第一个非选项参数作为AMF名称
      result.amfName = arg;
    }
  }
  
  return result;
}

// 帮助信息
function showHelp() {
  console.log('='.repeat(60));
  console.log('🚀 AMF配置修改技能 - 使用说明');
  console.log('='.repeat(60));
  
  console.log('\n📋 功能特性:');
  console.log('  1. 智能工程选择（支持默认/指定工程）');
  console.log('  2. 智能AMF选择（按名称匹配）');
  console.log('  3. 支持部分字段修改');
  console.log('  4. 登录状态优化（会话缓存）');
  console.log('  5. 基于文字匹配，不使用固定ID');
  
  console.log('\n🚀 使用方法:');
  console.log('  node amf-edit-skill.js <AMF名称> [选项]');
  console.log('  node amf-edit-skill.js --amf <名称> [选项]');
  
  console.log('\n🎯 示例:');
  console.log('  # 修改指定AMF的IP地址');
  console.log('  node amf-edit-skill.js qqqwww --set-ngap_sip 192.168.99.99');
  
  console.log('  # 修改多个字段');
  console.log('  node amf-edit-skill.js test_001 --set-ngap_sip 10.0.0.1 --set-http2_sip 10.0.0.2');
  
  console.log('  # 自动选择（只有一个AMF时）');
  console.log('  node amf-edit-skill.js --set-stac 200');
  
  console.log('\n🔧 可修改字段:');
  console.log('  --set-name <新名称>       修改AMF名称');
  console.log('  --set-mcc <值>           修改MCC');
  console.log('  --set-mnc <值>           修改MNC');
  console.log('  --set-region_id <值>     修改Region ID');
  console.log('  --set-set_id <值>        修改Set ID');
  console.log('  --set-pointer <值>       修改Pointer');
  console.log('  --set-ngap_sip <IP>      修改NGAP SIP地址');
  console.log('  --set-ngap_port <端口>   修改NGAP端口');
  console.log('  --set-http2_sip <IP>     修改HTTP2 SIP地址');
  console.log('  --set-http2_port <端口>  修改HTTP2端口');
  console.log('  --set-stac <值>          修改起始TAC');
  console.log('  --set-etac <值>          修改结束TAC');
  console.log('  --set-ea[NEA0] <优先级> 修改加密算法NEA0');
  console.log('  --set-ea[128-NEA1] <优先级> ...');
  console.log('  --set-ia[NIA0] <优先级>  修改完保算法NIA0');
  console.log('  --set-deviceType <类型>  修改设备类型（仿真设备 / 被测设备）');
  
  console.log('\n🔧 工程选择:');
  console.log('  --project, -p <工程名>    指定工程（默认: 5G_basic_process）');
  console.log('  # 不指定工程时自动选择 "5G_basic_process"');
  console.log('  # 指定工程示例: node amf-edit-skill.js qqqwww --project 5G_basic_process');
  
  console.log('\n🎯 智能选择逻辑:');
  console.log('  工程选择:');
  console.log('    1. 用户指定工程 → 自动切换到指定工程');
  console.log('    2. 未指定工程 → 自动选择 "5G_basic_process"');
  console.log('  AMF选择:');
  console.log('    1. 用户指定AMF名称 → 按名称查找');
  console.log('    2. 未指定名称 + 单个AMF → 自动选择');
  console.log('    3. 未指定名称 + 多个AMF → 反问用户');
  
  console.log('\n💡 提示:');
  console.log('  - 字段名称区分大小写');
  console.log('  - 支持精确匹配和模糊匹配');
  console.log('  - 登录状态缓存24小时有效');
  
  console.log('\n' + '='.repeat(60));
}

// 主函数
async function main() {
  const args = parseArgs();
  
  // 显示帮助
  if (args.amfName === '--help' || args.amfName === '-h' || process.argv.includes('--help')) {
    showHelp();
    process.exit(0);
  }
  
  // 显示版本
  if (args.amfName === '--version' || args.amfName === '-v' || process.argv.includes('--version')) {
    console.log('AMF编辑技能 v1.0 (智能版本)');
    console.log('状态: 🚧 开发中');
    console.log('更新: 2026-03-22');
    process.exit(0);
  }
  
  console.log('🎯 任务配置:');
  console.log(`  AMF名称: ${args.amfName || '(自动选择)'}`);
  console.log(`  工程选择: ${args.projectName} ${args.projectName === '5G_basic_process' ? '(默认)' : '(用户指定)'}`);
  console.log(`  修改字段: ${Object.keys(args.fieldUpdates).length} 个`);
  
  if (Object.keys(args.fieldUpdates).length > 0) {
    console.log('  修改详情:');
    Object.entries(args.fieldUpdates).forEach(([field, value]) => {
      console.log(`    - ${field}: ${value}`);
    });
  }
  
  // 执行编辑
  const result = await editAMF(args.amfName, args.projectName, args.fieldUpdates);
  
  console.log('\n' + '='.repeat(60));
  console.log('完成时间:', new Date().toLocaleString());
  console.log('='.repeat(60));
  
  process.exit(result.success ? 0 : 1);
}

// 执行
main().catch(error => {
  console.error('程序异常:', error);
  process.exit(1);
});