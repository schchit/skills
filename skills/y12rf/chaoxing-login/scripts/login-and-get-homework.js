/**
 * 超星学习通 - 登录并获取作业列表
 * 
 * 使用方法：
 *   node login-and-get-homework.js [courseId] [classId] [cpi] [workId] [answerId] [enc]
 * 
 * 示例 - 获取国际贸易课程作业：
 *   node login-and-get-homework.js 261272097 142692269 429828790 51363737 54926481 538e9693d6dee7f9c0e75339090ba2b1
 */

const puppeteer = require('puppeteer-extra');
const stealthPlugin = require('puppeteer-extra-plugin-stealth');

puppeteer.use(stealthPlugin());

const PHONE = process.argv[2] || '13393675650';
const PASSWORD = process.argv[3] || 'hxcibbmm124816.,';
const COURSE_ID = process.argv[4] || '261272097';
const CLASS_ID = process.argv[5] || '142692269';
const CPI = process.argv[6] || '429828790';
const WORK_ID = process.argv[7] || '51363737';
const ANSWER_ID = process.argv[8] || '54926481';
const ENC = process.argv[9] || '538e9693d6dee7f9c0e75339090ba2b1';

async function login(page) {
  await page.goto('https://passport2.chaoxing.com/login?fid=&newversion=true&refer=https%3A%2F%2Fi.chaoxing.com', { waitUntil: 'networkidle2', timeout: 30000 });

  await page.evaluate((phone, pwd) => {
    const phoneInput = document.getElementById('phone');
    const pwdInput = document.getElementById('pwd');
    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    nativeInputValueSetter.call(phoneInput, phone);
    phoneInput.dispatchEvent(new Event('input', { bubbles: true }));
    nativeInputValueSetter.call(pwdInput, pwd);
    pwdInput.dispatchEvent(new Event('input', { bubbles: true }));
  }, PHONE, PASSWORD);

  await page.evaluate(() => {
    document.querySelector('.btn-big-blue')?.click();
  });
  await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 30000 });
  console.log('Logged in, URL:', page.url());
}

async function goToCourse(page, courseId, classId, cpi) {
  await page.goto(`https://mooc1-2.chaoxing.com/mooc-ans/visit/stucoursemiddle?courseid=${courseId}&clazzid=${classId}&vc=1&cpi=${cpi}&ismooc2=1&v=2`, { waitUntil: 'networkidle2', timeout: 30000 });
  await new Promise(r => setTimeout(r, 3000));
  console.log('Course page, URL:', page.url());
}

async function clickHomeworkTab(page) {
  const frames = page.frames();
  const courseFrame = frames.find(f => f.url().includes('mooc'));
  
  if (courseFrame) {
    await courseFrame.evaluate(() => {
      const links = Array.from(document.querySelectorAll('a'));
      const hwLink = links.find(l => l.textContent?.trim().includes('作业'));
      if (hwLink) hwLink.click();
    });
    await new Promise(r => setTimeout(r, 5000));
    console.log('Clicked homework tab');
  }
}

async function getHomeworkList(page) {
  const hwFrame = page.frames().find(f => f.url().includes('work/list'));
  if (!hwFrame) {
    console.log('No homework frame found');
    return null;
  }

  const hwText = await hwFrame.evaluate(() => document.body.innerText);
  console.log('Homework list:\n', hwText.substring(0, 2000));
  return hwText;
}

async function getHomeworkDetail(page, workId, answerId, enc) {
  await page.goto(`https://mooc1.chaoxing.com/mooc-ans/mooc2/work/task?courseId=${COURSE_ID}&classId=${CLASS_ID}&cpi=${CPI}&workId=${workId}&answerId=${answerId}&enc=${enc}`, { waitUntil: 'networkidle2', timeout: 30000 });
  await new Promise(r => setTimeout(r, 5000));

  const pageInfo = await page.evaluate(() => ({
    title: document.title,
    text: document.body.innerText.substring(0, 3000)
  }));
  console.log('Homework detail:\n', JSON.stringify(pageInfo, null, 2));
  return pageInfo;
}

async function takeScreenshot(page, path) {
  await page.screenshot({ path: path || '/home/xiaochang/.openclaw/workspace/chaoxing-screenshot.png', timeout: 60000 });
  console.log('Screenshot saved:', path);
}

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--no-first-run',
      '--no-zygote',
      '--single-process',
      '--ignore-certificate-errors',
      '--ignore-certificate-errors-spki-list'
    ],
    protocolTimeout: 120000
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });
  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');

  try {
    await login(page);
    await goToCourse(page, COURSE_ID, CLASS_ID, CPI);
    await clickHomeworkTab(page);
    await getHomeworkList(page);
    await getHomeworkDetail(page, WORK_ID, ANSWER_ID, ENC);
    await takeScreenshot(page);
  } catch (e) {
    console.error('Error:', e.message);
    await takeScreenshot(page, '/home/xiaochang/.openclaw/workspace/chaoxing-error.png');
  }

  await browser.close();
})();
