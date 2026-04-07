const { chromium } = require('playwright');

/**
 * 微信公众号文章抓取
 * 
 * 使用方式：
 *   node wx-article-fetch.js <url>
 * 
 * 参数：
 *   url - 微信公众号文章链接（mp.weixin.qq.com/s/xxx）
 * 
 * 返回：
 *   标题 + 正文内容
 */

(async () => {
  const url = process.argv[2];
  
  if (!url) {
    console.error('请提供微信公众号文章链接');
    console.error('用法: node wx-article-fetch.js <url>');
    process.exit(1);
  }
  
  if (!url.includes('mp.weixin.qq.com')) {
    console.error('请提供有效的微信公众号文章链接（mp.weixin.qq.com/s/xxx）');
    process.exit(1);
  }

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    await page.goto(url, { timeout: 30000 });
    await page.waitForFunction(() => !document.URL.includes('login') && document.readyState === 'complete');
    
    try {
      await page.waitForSelector('#js_content', { timeout: 15000 });
    } catch {
      console.error('无法加载文章内容（可能需要登录或文章已删除）');
      await browser.close();
      process.exit(1);
    }
    
    const title = await page.evaluate(() => {
      const el = document.querySelector('h2.rich_media_title') || document.querySelector('#activity_name') || document.querySelector('meta[property="og:title"]');
      return el ? (el.getAttribute('content') || el.textContent || '').trim() : '';
    });
    
    const text = await page.evaluate(() => {
      const el = document.querySelector('#js_content');
      return el ? el.innerText.trim() : '';
    });
    
    const actualUrl = page.url();
    
    await browser.close();
    
    // 输出格式化结果
    console.log(JSON.stringify({
      success: true,
      title: title,
      content: text,
      url: actualUrl
    }, null, 2));
    
  } catch (error) {
    await browser.close();
    console.error('抓取失败:', error.message);
    process.exit(1);
  }
})();
