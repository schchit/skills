#!/usr/bin/env node

/**
 * 微信公众号文章搜索
 * 参考外部脚本实现，并整理为当前项目可复用的模块。
 */

const https = require('https');
const zlib = require('zlib');

const USER_AGENTS = [
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edg/123.0.0.0 Chrome/123.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edg/122.0.0.0 Chrome/122.0.0.0 Safari/537.36',
  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
  'Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
  'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
  'Mozilla/5.0 (iPhone; CPU iPhone OS 16_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
  'Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
  'Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36',
  'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36',
  'Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36',
  'Mozilla/5.0 (Linux; Android 13; Mi 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36'
];

const HEADERS = {
  Accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
  'Accept-Encoding': 'identity',
  'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
  Host: 'weixin.sogou.com',
  Referer: 'https://weixin.sogou.com/'
};

function getRandomUserAgent() {
  return USER_AGENTS[Math.floor(Math.random() * USER_AGENTS.length)];
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function decompressBody(buffer, contentEncoding) {
  if (!contentEncoding) return buffer;

  const encoding = String(contentEncoding).toLowerCase();

  try {
    if (encoding.includes('gzip')) return zlib.gunzipSync(buffer);
    if (encoding.includes('deflate')) return zlib.inflateSync(buffer);
    if (encoding.includes('br')) return zlib.brotliDecompressSync(buffer);
  } catch {
    return buffer;
  }

  return buffer;
}

async function request({ url, method = 'GET', headers = {}, timeoutMs = 15000, retries = 0 }) {
  const lastErrorPrefix = `Request failed: ${method} ${url}`;

  for (let attempt = 0; attempt <= retries; attempt += 1) {
    try {
      const result = await new Promise((resolve, reject) => {
        const urlObj = new URL(url);
        const req = https.request(
          {
            hostname: urlObj.hostname,
            path: urlObj.pathname + urlObj.search,
            method,
            headers
          },
          (res) => {
            const chunks = [];
            res.on('data', (chunk) => chunks.push(chunk));
            res.on('end', () => {
              const raw = Buffer.concat(chunks);
              const body = decompressBody(raw, res.headers['content-encoding']);
              resolve({
                statusCode: res.statusCode || 0,
                headers: res.headers,
                body
              });
            });
          }
        );

        req.on('error', reject);
        req.setTimeout(timeoutMs, () => {
          req.destroy();
          reject(new Error('Request timeout'));
        });
        req.end();
      });

      return result;
    } catch (error) {
      if (attempt >= retries) {
        throw new Error(`${lastErrorPrefix}: ${error.message}`);
      }
      await sleep(300 + attempt * 300);
    }
  }

  throw new Error(`${lastErrorPrefix}: unexpected`);
}

async function requestText(options) {
  const resp = await request(options);
  return {
    ...resp,
    text: resp.body.toString('utf-8')
  };
}

function extractCookies(headers) {
  const cookies = [];
  const setCookieHeader = headers['set-cookie'];

  if (setCookieHeader) {
    setCookieHeader.forEach((cookie) => {
      const cookieValue = cookie.split(';')[0];
      if (cookieValue) cookies.push(cookieValue);
    });
  }

  return cookies.join('; ');
}

async function getSogouCookie() {
  try {
    const resp = await request({
      url: 'https://v.sogou.com/v?ie=utf8&query=&p=40030600',
      headers: {
        Accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'identity',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'User-Agent': getRandomUserAgent()
      },
      timeoutMs: 10000,
      retries: 1
    });

    const cookies = extractCookies(resp.headers);
    return { cookieStr: cookies || '' };
  } catch {
    return { cookieStr: '' };
  }
}

async function httpGet(url, cookieStr = '') {
  const headers = {
    ...HEADERS,
    'User-Agent': getRandomUserAgent()
  };

  if (cookieStr) {
    headers.Cookie = cookieStr;
  }

  const resp = await requestText({
    url,
    headers,
    timeoutMs: 30000,
    retries: 1
  });

  return resp.text;
}

function formatChinaDateTime(date) {
  const chinaTime = new Date(date.getTime() + 8 * 60 * 60 * 1000);
  const year = chinaTime.getUTCFullYear();
  const month = String(chinaTime.getUTCMonth() + 1).padStart(2, '0');
  const day = String(chinaTime.getUTCDate()).padStart(2, '0');
  const hours = String(chinaTime.getUTCHours()).padStart(2, '0');
  const minutes = String(chinaTime.getUTCMinutes()).padStart(2, '0');
  const seconds = String(chinaTime.getUTCSeconds()).padStart(2, '0');

  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

function parseRelativeTime(timeText) {
  if (!timeText) return { datetime: '', dateText: '' };

  const now = new Date();
  const targetDate = new Date(now);

  const dayMatch = timeText.match(/(\d+)天前/);
  const hourMatch = timeText.match(/(\d+)小时前/);
  const minuteMatch = timeText.match(/(\d+)分钟前/);

  if (dayMatch) {
    targetDate.setDate(now.getDate() - parseInt(dayMatch[1], 10));
  } else if (hourMatch) {
    targetDate.setHours(now.getHours() - parseInt(hourMatch[1], 10));
  } else if (minuteMatch) {
    targetDate.setMinutes(now.getMinutes() - parseInt(minuteMatch[1], 10));
  } else {
    const dateMatch = timeText.match(/(\d{4})-(\d{2})-(\d{2})/);
    if (!dateMatch) {
      return { datetime: '', dateText: timeText };
    }

    targetDate.setFullYear(parseInt(dateMatch[1], 10));
    targetDate.setMonth(parseInt(dateMatch[2], 10) - 1);
    targetDate.setDate(parseInt(dateMatch[3], 10));
  }

  return {
    datetime: formatChinaDateTime(new Date(targetDate.getTime() - 8 * 60 * 60 * 1000)),
    dateText: `${targetDate.getFullYear()}年${String(targetDate.getMonth() + 1).padStart(2, '0')}月${String(targetDate.getDate()).padStart(2, '0')}日`
  };
}

function stripTags(value) {
  return String(value || '')
    .replace(/<script[\s\S]*?<\/script>/gi, ' ')
    .replace(/<style[\s\S]*?<\/style>/gi, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&#39;/g, "'")
    .replace(/&quot;/g, '"')
    .replace(/\s+/g, ' ')
    .trim();
}

function decodeHtmlEntities(value) {
  return String(value || '')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&#39;/g, "'")
    .replace(/&quot;/g, '"');
}

function extractFirstMatch(text, pattern) {
  const match = text.match(pattern);
  return match ? match[1] : '';
}

function parseArticle(itemHtml) {
  try {
    const titleAnchorMatch = itemHtml.match(/<h3[^>]*>[\s\S]*?<a[^>]*href="([^"]+)"[^>]*>([\s\S]*?)<\/a>/i);
    if (!titleAnchorMatch) return null;

    let url = titleAnchorMatch[1] || '';
    url = decodeHtmlEntities(url);
    if (url.startsWith('/')) {
      url = `https://weixin.sogou.com${url}`;
    }
    const title = stripTags(titleAnchorMatch[2]);

    const summary = stripTags(extractFirstMatch(itemHtml, /<p[^>]*class="[^"]*\btxt-info\b[^"]*"[^>]*>([\s\S]*?)<\/p>/i));
    let datetime = '';
    let dateText = '';
    let source = '';
    let timeDescription = '';

    const timestampMatch = itemHtml.match(/(\d{10})/);
    if (timestampMatch) {
      const timestamp = parseInt(timestampMatch[1], 10) * 1000;
      const date = new Date(timestamp);
      datetime = formatChinaDateTime(date);
      dateText = `${date.getFullYear()}年${String(date.getMonth() + 1).padStart(2, '0')}月${String(date.getDate()).padStart(2, '0')}日`;

      const now = new Date();
      const diffMs = now - date;
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

      if (diffDays > 0) {
        timeDescription = `${diffDays}天前`;
      } else if (diffHours > 0) {
        timeDescription = `${diffHours}小时前`;
      } else {
        const diffMinutes = Math.floor(diffMs / (1000 * 60));
        timeDescription = diffMinutes > 0 ? `${diffMinutes}分钟前` : '刚刚';
      }
    } else {
      const timeText = stripTags(extractFirstMatch(itemHtml, /<span[^>]*class="[^"]*\bs2\b[^"]*"[^>]*>([\s\S]*?)<\/span>/i));
      if (timeText) {
        timeDescription = timeText;
        const parsedTime = parseRelativeTime(timeText);
        datetime = parsedTime.datetime;
        dateText = parsedTime.dateText;
      }
    }

    source = stripTags(extractFirstMatch(itemHtml, /<span[^>]*class="[^"]*\ball-time-y2\b[^"]*"[^>]*>([\s\S]*?)<\/span>/i));
    if (!source) {
      source = stripTags(extractFirstMatch(itemHtml, /<a[^>]*class="[^"]*\baccount\b[^"]*"[^>]*>([\s\S]*?)<\/a>/i));
    }

    return {
      title,
      url,
      summary,
      datetime,
      date_text: dateText,
      date_description: timeDescription || dateText,
      source
    };
  } catch (error) {
    console.error('解析文章失败:', error.message);
    return null;
  }
}

function parseArticlesFromSearchHtml(html, maxResults) {
  const articles = [];
  const newsListMatch = html.match(/<ul[^>]*class="[^"]*\bnews-list\b[^"]*"[^>]*>([\s\S]*?)<\/ul>/i);
  if (!newsListMatch) return [];

  const newsListHtml = newsListMatch[1];
  const itemMatches = newsListHtml.match(/<li[\s\S]*?<\/li>/gi) || [];

  for (const itemHtml of itemMatches) {
    if (articles.length >= maxResults) break;
    const article = parseArticle(itemHtml);
    if (article) articles.push(article);
  }

  return articles;
}

async function searchWechatArticles(query, maxResults = 10) {
  const normalizedQuery = String(query || '').trim();
  if (!normalizedQuery) {
    throw new Error('query is required');
  }

  const safeMaxResults = Math.min(Math.max(parseInt(maxResults, 10) || 10, 1), 50);
  const articles = [];
  let page = 1;
  const pagesNeeded = Math.ceil(safeMaxResults / 10);

  while (articles.length < safeMaxResults && page <= pagesNeeded) {
    try {
      const { cookieStr } = await getSogouCookie();
      const encodedQuery = encodeURIComponent(normalizedQuery);
      const url = `https://weixin.sogou.com/weixin?query=${encodedQuery}&s_from=input&_sug_=n&type=2&page=${page}&ie=utf8`;
      const html = await httpGet(url, cookieStr);
      const remaining = safeMaxResults - articles.length;
      const parsed = parseArticlesFromSearchHtml(html, remaining);

      if (parsed.length === 0) break;
      articles.push(...parsed);
      page += 1;

      if (page <= pagesNeeded) {
        await sleep(500 + Math.random() * 1000);
      }
    } catch (error) {
      console.error(`请求第${page}页失败: ${error.message}`);
      break;
    }
  }

  return articles.slice(0, safeMaxResults);
}

function normalizeSearchResult(query, articles) {
  return {
    action: 'search',
    keyword: query,
    total: articles.length,
    items: articles.map((article, index) => ({
      index: index + 1,
      title: article.title,
      summary: article.summary,
      account_name: article.source,
      publish_time: article.datetime || article.date_text || '',
      publish_time_text: article.date_description || '',
      url: article.url
    }))
  };
}

function parseCliArgs(args) {
  let query = '';
  let num = 10;
  let output = '';

  for (let i = 0; i < args.length; i += 1) {
    if (args[i] === '-n' || args[i] === '--num') {
      num = parseInt(args[i + 1], 10) || 10;
      i += 1;
    } else if (args[i] === '-o' || args[i] === '--output') {
      output = args[i + 1] || '';
      i += 1;
    } else if (!args[i].startsWith('-')) {
      query = args[i];
    }
  }

  return { query, num, output };
}

async function main() {
  const args = process.argv.slice(2);
  const { query, num, output } = parseCliArgs(args);

  if (!query) {
    console.log(`
微信公众号文章搜索工具

用法:
  node scripts/search_wechat.js <关键词> [选项]

选项:
  -n, --num <数量>       返回结果数量（默认10，最大50）
  -o, --output <文件>    输出JSON文件路径

示例:
  node scripts/search_wechat.js "人工智能" -n 10
  node scripts/search_wechat.js "ChatGPT" -n 5 -o result.json
`);
    process.exit(0);
  }

  try {
    console.error(`正在搜索: "${query}"...`);
    const articles = await searchWechatArticles(query, num);
    const result = normalizeSearchResult(query, articles);
    const jsonOutput = JSON.stringify(result, null, 2);

    if (output) {
      const fs = require('fs');
      fs.writeFileSync(output, jsonOutput, 'utf-8');
      console.error(`结果已保存到: ${output}`);
    }

    console.log(jsonOutput);
  } catch (error) {
    console.error(`搜索失败: ${error.message}`);
    process.exit(1);
  }
}

module.exports = {
  searchWechatArticles,
  normalizeSearchResult
};

if (require.main === module) {
  main();
}
