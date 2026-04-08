#!/usr/bin/env node

/**
 * 微信公众号文章抓取与 Markdown 转换
 * 零依赖实现，优先支持 mp.weixin.qq.com 链接，并尽量兼容搜狗跳转链接。
 */

const https = require('https');
const zlib = require('zlib');

const USER_AGENTS = [
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
  'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1'
];

function getRandomUserAgent() {
  return USER_AGENTS[Math.floor(Math.random() * USER_AGENTS.length)];
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function decodeHtmlEntities(value) {
  return String(value || '')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&#x([0-9a-f]+);/gi, (_, hex) => String.fromCodePoint(parseInt(hex, 16)))
    .replace(/&#(\d+);/g, (_, dec) => String.fromCodePoint(parseInt(dec, 10)));
}

function decodeJsString(value) {
  return decodeHtmlEntities(
    String(value || '')
      .replace(/\\u([0-9a-fA-F]{4})/g, (_, hex) => String.fromCharCode(parseInt(hex, 16)))
      .replace(/\\x([0-9a-fA-F]{2})/g, (_, hex) => String.fromCharCode(parseInt(hex, 16)))
      .replace(/\\n/g, '\n')
      .replace(/\\r/g, '\r')
      .replace(/\\t/g, '\t')
      .replace(/\\"/g, '"')
      .replace(/\\'/g, "'")
      .replace(/\\\\/g, '\\')
  );
}

function stripTags(value) {
  return decodeHtmlEntities(
    String(value || '')
      .replace(/<script[\s\S]*?<\/script>/gi, ' ')
      .replace(/<style[\s\S]*?<\/style>/gi, ' ')
      .replace(/<[^>]+>/g, ' ')
      .replace(/\s+/g, ' ')
      .trim()
  );
}

function extractAttr(tagHtml, attrName) {
  const patterns = [
    new RegExp(`\\b${attrName}="([^"]*)"`, 'i'),
    new RegExp(`\\b${attrName}='([^']*)'`, 'i')
  ];

  for (const pattern of patterns) {
    const match = tagHtml.match(pattern);
    if (match) return decodeHtmlEntities(match[1]);
  }

  return '';
}

function escapeMarkdown(text) {
  return String(text || '').replace(/([\\`*_{}\[\]()#+!|-])/g, '\\$1');
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

async function request({ url, headers = {}, timeoutMs = 20000, retries = 0 }) {
  const lastErrorPrefix = `Request failed: GET ${url}`;

  for (let attempt = 0; attempt <= retries; attempt += 1) {
    try {
      const result = await new Promise((resolve, reject) => {
        const urlObj = new URL(url);
        const req = https.request(
          {
            hostname: urlObj.hostname,
            path: urlObj.pathname + urlObj.search,
            method: 'GET',
            headers
          },
          (res) => {
            const chunks = [];
            res.on('data', (chunk) => chunks.push(chunk));
            res.on('end', () => {
              const raw = Buffer.concat(chunks);
              resolve({
                statusCode: res.statusCode || 0,
                headers: res.headers,
                body: decompressBody(raw, res.headers['content-encoding'])
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
      await sleep(400 + attempt * 300);
    }
  }

  throw new Error(`${lastErrorPrefix}: unexpected`);
}

async function requestText(options) {
  const response = await request(options);
  return {
    ...response,
    text: response.body.toString('utf-8')
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
    const response = await request({
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

    const cookieStr = extractCookies(response.headers);
    const cookieObj = {};

    if (cookieStr) {
      cookieStr.split('; ').forEach((cookie) => {
        const [key, value] = cookie.split('=');
        if (key && value) cookieObj[key.trim()] = value.trim();
      });
    }

    return { cookieStr: cookieStr || '', cookieObj };
  } catch {
    return { cookieStr: '', cookieObj: {} };
  }
}

function extractRedirectUrlFromHtml(html) {
  const metaMatch = html.match(/<meta[^>]*http-equiv=["']refresh["'][^>]*content=["']\d+;\s*url=([^"']+)["'][^>]*>/i);
  if (metaMatch) return decodeHtmlEntities(metaMatch[1]);

  const directJsMatch =
    html.match(/location\.href\s*=\s*["']([^"']+)["']/i) ||
    html.match(/location\s*=\s*["']([^"']+)["']/i) ||
    html.match(/window\.location(?:\.href)?\s*=\s*["']([^"']+)["']/i) ||
    html.match(/window\.location\.replace\(\s*["']([^"']+)["']\s*\)/i);
  if (directJsMatch) return decodeHtmlEntities(directJsMatch[1]);

  const urlParts = [];
  for (const match of html.matchAll(/url\s*\+=\s*'([^']*)'/g)) urlParts.push(match[1]);
  for (const match of html.matchAll(/url\s*\+=\s*"([^"]*)"/g)) urlParts.push(match[1]);
  if (urlParts.length > 0) {
    const joined = decodeHtmlEntities(urlParts.join(''));
    if (joined.includes('mp.weixin.qq.com')) return joined;
    return joined;
  }

  return '';
}

async function resolveSogouUrl(url) {
  const { cookieObj } = await getSogouCookie();
  const baseCookies =
    'ABTEST=7|1716888919|v1; IPLOC=CN5101; ariaDefaultTheme=default; ariaFixed=true; ariaReadtype=1; ariaStatus=false';
  const snuid = cookieObj.SNUID || '';
  const cookieStr = snuid ? `${baseCookies}; SNUID=${snuid}` : baseCookies;

  for (let attempt = 0; attempt < 3; attempt += 1) {
    try {
      const response = await requestText({
        url,
        headers: {
          Accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
          'Accept-Encoding': 'identity',
          'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
          Cookie: cookieStr,
          'User-Agent': getRandomUserAgent(),
          Referer: 'https://weixin.sogou.com/'
        },
        timeoutMs: 5000,
        retries: 0
      });

      if (response.statusCode >= 300 && response.statusCode < 400 && response.headers.location) {
        const location = decodeHtmlEntities(response.headers.location);
        if (location.includes('antispider')) {
          throw new Error('Sogou antispider blocked URL resolution');
        }
        if (location.includes('mp.weixin.qq.com')) {
          return location;
        }
      }

      const resolved = extractRedirectUrlFromHtml(response.text);
      if (resolved.includes('antispider')) {
        throw new Error('Sogou antispider blocked URL resolution');
      }
      if (resolved && resolved.includes('mp.weixin.qq.com')) {
        return resolved;
      }
    } catch (error) {
      if (attempt >= 2) {
        throw error;
      }
    }

    await sleep(1000);
  }

  throw new Error('Unable to resolve Sogou redirect URL');
}

function normalizeWechatUrl(inputUrl) {
  const url = String(inputUrl || '').trim();
  if (!url) throw new Error('url is required');

  const parsed = new URL(url);
  if (!['https:', 'http:'].includes(parsed.protocol)) {
    throw new Error('Only http/https URLs are supported');
  }

  return parsed.toString();
}

async function resolveArticleUrl(inputUrl) {
  const normalized = normalizeWechatUrl(inputUrl);
  const host = new URL(normalized).hostname;

  if (host === 'mp.weixin.qq.com') return normalized;
  if (host === 'weixin.sogou.com') return resolveSogouUrl(normalized);

  throw new Error('Unsupported URL host, expected mp.weixin.qq.com or weixin.sogou.com');
}

function extractElementById(html, id) {
  const openTagPattern = new RegExp(`<div[^>]*\\bid=["']${id}["'][^>]*>`, 'i');
  const openMatch = openTagPattern.exec(html);
  if (!openMatch) return '';

  const start = openMatch.index;
  const openEnd = html.indexOf('>', start);
  if (openEnd === -1) return '';

  let depth = 1;
  let cursor = openEnd + 1;

  while (depth > 0 && cursor < html.length) {
    const nextOpen = html.slice(cursor).search(/<div\b/i);
    const nextClose = html.slice(cursor).search(/<\/div>/i);

    if (nextClose === -1) return '';

    const nextOpenIndex = nextOpen === -1 ? -1 : cursor + nextOpen;
    const nextCloseIndex = cursor + nextClose;

    if (nextOpenIndex !== -1 && nextOpenIndex < nextCloseIndex) {
      depth += 1;
      cursor = nextOpenIndex + 4;
    } else {
      depth -= 1;
      cursor = nextCloseIndex + 6;
    }
  }

  return html.slice(openEnd + 1, cursor - 6);
}

function extractStringAssignment(html, names) {
  for (const name of names) {
    const pattern =
      new RegExp(`\\b${name}\\b\\s*[:=]\\s*"([\\s\\S]*?)"`, 'i') ||
      new RegExp(`\\b${name}\\b\\s*[:=]\\s*'([\\s\\S]*?)'`, 'i');
    const match = html.match(pattern);
    if (match && match[1]) return decodeJsString(match[1]);
  }

  for (const name of names) {
    const doubleQuoted = html.match(new RegExp(`\\b${name}\\b\\s*[:=]\\s*"([\\s\\S]*?)"`, 'i'));
    if (doubleQuoted && doubleQuoted[1]) return decodeJsString(doubleQuoted[1]);
    const singleQuoted = html.match(new RegExp(`\\b${name}\\b\\s*[:=]\\s*'([\\s\\S]*?)'`, 'i'));
    if (singleQuoted && singleQuoted[1]) return decodeJsString(singleQuoted[1]);
  }

  return '';
}

function extractTextById(html, id) {
  const match = html.match(new RegExp(`<[^>]*\\bid=["']${id}["'][^>]*>([\\s\\S]*?)<\\/[^>]+>`, 'i'));
  return match ? stripTags(match[1]) : '';
}

function formatPublishTime(timestampText) {
  if (!timestampText) return '';
  if (/^\d{10}$/.test(timestampText)) {
    const date = new Date(parseInt(timestampText, 10) * 1000);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hour = String(date.getHours()).padStart(2, '0');
    const minute = String(date.getMinutes()).padStart(2, '0');
    const second = String(date.getSeconds()).padStart(2, '0');
    return `${year}-${month}-${day} ${hour}:${minute}:${second}`;
  }

  return stripTags(timestampText);
}

function detectAccessError(html) {
  if (/wappoc_appmsgcaptcha/i.test(html)) return 'Article requires WeChat captcha verification';
  if (/暂无权限查看此页面内容/i.test(html)) return 'Article is not accessible from the current environment';
  if (/该内容已被发布者删除|内容无法查看/i.test(html)) return 'Article content is unavailable';
  return '';
}

function preprocessInlineHtml(html) {
  let result = String(html || '');

  result = result.replace(/<script[\s\S]*?<\/script>/gi, '');
  result = result.replace(/<style[\s\S]*?<\/style>/gi, '');
  result = result.replace(/<!--[\s\S]*?-->/g, '');
  result = result.replace(/<img\b[^>]*>/gi, (tag) => {
    const src = extractAttr(tag, 'data-src') || extractAttr(tag, 'src');
    const alt = extractAttr(tag, 'data-alt') || extractAttr(tag, 'alt') || 'image';
    if (!src) return '';
    return `\n\n![${escapeMarkdown(stripTags(alt) || 'image')}](${src})\n\n`;
  });
  result = result.replace(/<a\b[^>]*href=(['"])(.*?)\1[^>]*>([\s\S]*?)<\/a>/gi, (_, _q, href, inner) => {
    const text = stripTags(inner);
    if (!text) return '';
    return `[${escapeMarkdown(text)}](${decodeHtmlEntities(href)})`;
  });

  return result;
}

function htmlToMarkdown(html) {
  const tokens = preprocessInlineHtml(html).match(/<[^>]+>|[^<]+/g) || [];
  let markdown = '';
  let lineStart = true;
  let blockquoteDepth = 0;
  const stack = [];

  function appendText(text) {
    const normalized = decodeHtmlEntities(text).replace(/\s+/g, ' ');
    const clean = normalized.trim();
    if (!clean) return;

    if (lineStart && blockquoteDepth > 0) {
      markdown += `${'> '.repeat(blockquoteDepth)}`;
      lineStart = false;
    }

    const needsLeadingSpace =
      !lineStart &&
      !markdown.endsWith(' ') &&
      !markdown.endsWith('\n') &&
      /^\s/.test(normalized);
    const needsTrailingSpace = /\s$/.test(normalized);

    if (needsLeadingSpace) markdown += ' ';
    markdown += clean;
    if (needsTrailingSpace) markdown += ' ';
    lineStart = false;
  }

  function appendRaw(text) {
    if (!text) return;
    if (lineStart && blockquoteDepth > 0 && !text.startsWith('\n')) {
      markdown += `${'> '.repeat(blockquoteDepth)}`;
      lineStart = false;
    }
    markdown += text;
    lineStart = /\n$/.test(text);
  }

  function ensureBlockBreak() {
    markdown = markdown.replace(/[ \t]+\n/g, '\n');
    if (!markdown.endsWith('\n\n')) {
      markdown = markdown.replace(/\n?$/, '\n\n');
    }
    lineStart = true;
  }

  for (const token of tokens) {
    if (token.startsWith('<')) {
      const closeMatch = token.match(/^<\/\s*([a-z0-9]+)/i);
      const openMatch = token.match(/^<\s*([a-z0-9]+)/i);

      if (closeMatch) {
        const tag = closeMatch[1].toLowerCase();
        if (tag === 'strong' || tag === 'b') appendRaw('**');
        if (tag === 'em' || tag === 'i') appendRaw('*');
        if (tag === 'blockquote') {
          blockquoteDepth = Math.max(0, blockquoteDepth - 1);
          ensureBlockBreak();
        }
        if (['p', 'section', 'div', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'].includes(tag)) {
          ensureBlockBreak();
        }
        stack.pop();
        continue;
      }

      if (!openMatch) continue;
      const tag = openMatch[1].toLowerCase();
      stack.push(tag);

      if (tag === 'br') {
        appendRaw('\n');
        continue;
      }
      if (tag === 'strong' || tag === 'b') {
        appendRaw('**');
        continue;
      }
      if (tag === 'em' || tag === 'i') {
        appendRaw('*');
        continue;
      }
      if (tag === 'blockquote') {
        ensureBlockBreak();
        blockquoteDepth += 1;
        continue;
      }
      if (/^h[1-6]$/.test(tag)) {
        const level = parseInt(tag.slice(1), 10);
        ensureBlockBreak();
        appendRaw(`${'#'.repeat(level)} `);
        continue;
      }
      if (tag === 'li') {
        ensureBlockBreak();
        appendRaw('- ');
        continue;
      }
      if (['p', 'section', 'div'].includes(tag)) {
        ensureBlockBreak();
      }
      continue;
    }

    appendText(token);
  }

  return markdown
    .replace(/\n{3,}/g, '\n\n')
    .replace(/[ \t]+\n/g, '\n')
    .trim();
}

function parseArticlePage(html, sourceUrl) {
  const accessError = detectAccessError(html);
  if (accessError) {
    throw new Error(accessError);
  }

  const title =
    extractTextById(html, 'activity-name') ||
    extractStringAssignment(html, ['msg_title', 'title']) ||
    stripTags((html.match(/<meta[^>]*property=["']og:title["'][^>]*content=["']([^"']+)["']/i) || [])[1]);

  const author =
    extractTextById(html, 'js_name') ||
    extractStringAssignment(html, ['nickname', 'author', 'user_name']) ||
    stripTags((html.match(/<meta[^>]*name=["']author["'][^>]*content=["']([^"']+)["']/i) || [])[1]);

  const publishTime =
    formatPublishTime(extractStringAssignment(html, ['ct', 'publish_time'])) ||
    stripTags((html.match(/<em[^>]*id=["']publish_time["'][^>]*>([\s\S]*?)<\/em>/i) || [])[1]);

  const contentHtml = extractElementById(html, 'js_content');
  if (!contentHtml) {
    throw new Error('Unable to extract article content from page');
  }

  const markdown = htmlToMarkdown(contentHtml);
  if (!markdown) {
    throw new Error('Article content was empty after Markdown conversion');
  }

  return {
    action: 'fetch',
    title: title || '',
    author: author || '',
    publish_time: publishTime || '',
    source_url: sourceUrl,
    markdown
  };
}

async function fetchWechatArticle(inputUrl) {
  const articleUrl = await resolveArticleUrl(inputUrl);
  const response = await requestText({
    url: articleUrl,
    headers: {
      Accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'Accept-Encoding': 'identity',
      'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
      'User-Agent': getRandomUserAgent(),
      Referer: 'https://mp.weixin.qq.com/'
    },
    timeoutMs: 20000,
    retries: 1
  });

  if (response.statusCode >= 300 && response.statusCode < 400 && response.headers.location) {
    const location = String(response.headers.location);
    if (location.includes('wappoc_appmsgcaptcha')) {
      throw new Error('Article requires WeChat captcha verification');
    }
    throw new Error(`Article redirected to an unsupported page: ${location}`);
  }

  if (response.statusCode !== 200) {
    throw new Error(`Unexpected status code: ${response.statusCode}`);
  }

  return parseArticlePage(response.text, articleUrl);
}

function parseCliArgs(args) {
  let url = '';
  let output = '';

  for (let i = 0; i < args.length; i += 1) {
    if (args[i] === '-o' || args[i] === '--output') {
      output = args[i + 1] || '';
      i += 1;
    } else if (!args[i].startsWith('-')) {
      url = args[i];
    }
  }

  return { url, output };
}

async function main() {
  const { url, output } = parseCliArgs(process.argv.slice(2));

  if (!url) {
    console.log(`
微信公众号文章抓取工具

用法:
  node scripts/fetch_wechat_article.js <文章链接> [选项]

选项:
  -o, --output <文件>    输出 JSON 文件路径

示例:
  node scripts/fetch_wechat_article.js "https://mp.weixin.qq.com/..."
`);
    process.exit(0);
  }

  try {
    const result = await fetchWechatArticle(url);
    const outputText = JSON.stringify(result, null, 2);

    if (output) {
      const fs = require('fs');
      fs.writeFileSync(output, outputText, 'utf-8');
    }

    console.log(outputText);
  } catch (error) {
    console.error(`抓取失败: ${error.message}`);
    process.exit(1);
  }
}

module.exports = {
  fetchWechatArticle,
  htmlToMarkdown,
  parseArticlePage
};

if (require.main === module) {
  main();
}
