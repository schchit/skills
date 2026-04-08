#!/usr/bin/env node

const fs = require('fs');
const http = require('http');
const https = require('https');
const path = require('path');
const zlib = require('zlib');

const { fetchWechatArticle, htmlToMarkdown } = require('./fetch_wechat_article');
const { sanitizePathSegment, slugify } = require('./build_knowledge_base');

const USER_AGENTS = [
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
];

function getRandomUserAgent() {
  return USER_AGENTS[Math.floor(Math.random() * USER_AGENTS.length)];
}

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

function writeJson(filePath, payload) {
  fs.writeFileSync(filePath, `${JSON.stringify(payload, null, 2)}\n`, 'utf-8');
}

function formatNow() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  const seconds = String(now.getSeconds()).padStart(2, '0');
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

function toYamlScalar(value) {
  return JSON.stringify(String(value || ''));
}

function buildMarkdownDocument(article, topic) {
  const header = [
    '---',
    `topic: ${toYamlScalar(topic)}`,
    `title: ${toYamlScalar(article.title)}`,
    `author: ${toYamlScalar(article.author)}`,
    `publish_time: ${toYamlScalar(article.publish_time)}`,
    `source_url: ${toYamlScalar(article.source_url)}`,
    `saved_at: ${toYamlScalar(formatNow())}`,
    '---',
    ''
  ];

  return `${header.join('\n')}${article.markdown.trim()}\n`;
}

function parseUrls(value) {
  if (!value) return [];

  return String(value)
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);
}

function uniqueUrls(urls) {
  return Array.from(new Set(urls));
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

function stripTags(value) {
  return decodeHtmlEntities(
    String(value || '')
      .replace(/<script[\s\S]*?<\/script>/gi, ' ')
      .replace(/<style[\s\S]*?<\/style>/gi, ' ')
      .replace(/<noscript[\s\S]*?<\/noscript>/gi, ' ')
      .replace(/<[^>]+>/g, ' ')
      .replace(/\s+/g, ' ')
      .trim()
  );
}

function extractMetaContent(html, attrName, attrValue) {
  const patterns = [
    new RegExp(`<meta[^>]*${attrName}=["']${attrValue}["'][^>]*content=["']([^"']*)["'][^>]*>`, 'i'),
    new RegExp(`<meta[^>]*content=["']([^"']*)["'][^>]*${attrName}=["']${attrValue}["'][^>]*>`, 'i')
  ];

  for (const pattern of patterns) {
    const match = html.match(pattern);
    if (match && match[1]) return decodeHtmlEntities(match[1]);
  }

  return '';
}

function extractTitle(html) {
  return (
    extractMetaContent(html, 'property', 'og:title') ||
    extractMetaContent(html, 'name', 'twitter:title') ||
    stripTags((html.match(/<title[^>]*>([\s\S]*?)<\/title>/i) || [])[1])
  );
}

function extractAuthor(html) {
  return (
    extractMetaContent(html, 'name', 'author') ||
    extractMetaContent(html, 'property', 'article:author') ||
    stripTags((html.match(/<meta[^>]*name=["']byl["'][^>]*content=["']([^"']*)["']/i) || [])[1])
  );
}

function extractPublishTime(html) {
  return (
    extractMetaContent(html, 'property', 'article:published_time') ||
    extractMetaContent(html, 'name', 'publish_date') ||
    extractMetaContent(html, 'name', 'pubdate') ||
    stripTags((html.match(/<time[^>]*datetime=["']([^"']+)["']/i) || [])[1])
  );
}

function extractBlocksByPattern(html, pattern) {
  const match = html.match(pattern);
  return match ? match[1] : '';
}

function extractGenericContentHtml(html) {
  const candidatePatterns = [
    /<article\b[^>]*>([\s\S]*?)<\/article>/i,
    /<main\b[^>]*>([\s\S]*?)<\/main>/i,
    /<div[^>]*id=["'][^"']*(?:content|article|post|entry|main)[^"']*["'][^>]*>([\s\S]*?)<\/div>/i,
    /<section[^>]*id=["'][^"']*(?:content|article|post|entry|main)[^"']*["'][^>]*>([\s\S]*?)<\/section>/i,
    /<div[^>]*class=["'][^"']*(?:content|article|post-content|entry-content|article-content|post-body|markdown-body)[^"']*["'][^>]*>([\s\S]*?)<\/div>/i,
    /<section[^>]*class=["'][^"']*(?:content|article|post-content|entry-content|article-content|post-body|markdown-body)[^"']*["'][^>]*>([\s\S]*?)<\/section>/i
  ];

  for (const pattern of candidatePatterns) {
    const extracted = extractBlocksByPattern(html, pattern);
    if (extracted && stripTags(extracted).length > 200) {
      return extracted;
    }
  }

  const body = extractBlocksByPattern(html, /<body[^>]*>([\s\S]*?)<\/body>/i);
  if (!body) return '';

  return body
    .replace(/<header[\s\S]*?<\/header>/gi, '')
    .replace(/<footer[\s\S]*?<\/footer>/gi, '')
    .replace(/<nav[\s\S]*?<\/nav>/gi, '')
    .replace(/<aside[\s\S]*?<\/aside>/gi, '')
    .replace(/<form[\s\S]*?<\/form>/gi, '')
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/<style[\s\S]*?<\/style>/gi, '');
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

async function requestText(url, options = {}) {
  const maxRedirects = options.maxRedirects ?? 5;
  const retries = options.retries ?? 1;

  async function doRequest(targetUrl, redirectCount = 0, attempt = 0, allowInsecure = false) {
    const parsed = new URL(targetUrl);
    const client = parsed.protocol === 'http:' ? http : https;

    try {
      const response = await new Promise((resolve, reject) => {
        const req = client.request(
          {
            hostname: parsed.hostname,
            port: parsed.port || undefined,
            path: parsed.pathname + parsed.search,
            method: 'GET',
            rejectUnauthorized: !allowInsecure,
            headers: {
              Accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
              'Accept-Encoding': 'gzip, deflate, br',
              'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
              'User-Agent': getRandomUserAgent(),
              Referer: `${parsed.protocol}//${parsed.hostname}/`
            }
          },
          (res) => {
            const chunks = [];
            res.on('data', (chunk) => chunks.push(chunk));
            res.on('end', () => {
              resolve({
                statusCode: res.statusCode || 0,
                headers: res.headers,
                body: decompressBody(Buffer.concat(chunks), res.headers['content-encoding'])
              });
            });
          }
        );

        req.on('error', reject);
        req.setTimeout(20000, () => {
          req.destroy();
          reject(new Error('Request timeout'));
        });
        req.end();
      });

      if (
        response.statusCode >= 300 &&
        response.statusCode < 400 &&
        response.headers.location &&
        redirectCount < maxRedirects
      ) {
        const nextUrl = new URL(response.headers.location, targetUrl).toString();
        return doRequest(nextUrl, redirectCount + 1, attempt, allowInsecure);
      }

      return {
        url: targetUrl,
        statusCode: response.statusCode,
        headers: response.headers,
        text: response.body.toString('utf-8')
      };
    } catch (error) {
      if (
        !allowInsecure &&
        parsed.protocol === 'https:' &&
        /issuer certificate|self[- ]signed|unable to verify the first certificate/i.test(error.message)
      ) {
        return doRequest(targetUrl, redirectCount, attempt, true);
      }

      if (attempt >= retries) {
        throw error;
      }

      await sleep(400 + attempt * 400);
      return doRequest(targetUrl, redirectCount, attempt + 1, allowInsecure);
    }
  }

  return doRequest(url);
}

function parseGenericArticle(html, sourceUrl) {
  const title = extractTitle(html);
  const author = extractAuthor(html);
  const publishTime = extractPublishTime(html);
  const contentHtml = extractGenericContentHtml(html);

  if (!contentHtml) {
    throw new Error('Unable to extract generic article content from page');
  }

  let markdown = htmlToMarkdown(contentHtml);
  if (!markdown || markdown.length < 80) {
    const body = extractBlocksByPattern(html, /<body[^>]*>([\s\S]*?)<\/body>/i);
    markdown = htmlToMarkdown(body || contentHtml);
  }

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

function isWechatLikeUrl(value) {
  try {
    const host = new URL(value).hostname;
    return host === 'mp.weixin.qq.com' || host === 'weixin.sogou.com';
  } catch {
    return false;
  }
}

async function fetchArticle(url) {
  if (isWechatLikeUrl(url)) {
    return fetchWechatArticle(url);
  }

  const response = await requestText(url);
  if (response.statusCode !== 200) {
    throw new Error(`Unexpected status code: ${response.statusCode}`);
  }

  return parseGenericArticle(response.text, response.url);
}

async function saveWebArticles(topic, urls, options = {}) {
  const normalizedTopic = String(topic || '').trim();
  if (!normalizedTopic) {
    throw new Error('topic is required');
  }

  const cleanedUrls = uniqueUrls(urls.map((item) => String(item || '').trim()).filter(Boolean));
  if (cleanedUrls.length === 0) {
    throw new Error('at least one article url is required');
  }

  const outputRoot = path.resolve(options.outputDir || path.join(process.cwd(), 'knowledge-base'));
  const topicDirName = sanitizePathSegment(options.topicDirName || slugify(normalizedTopic, 'topic'));
  const topicDir = path.join(outputRoot, topicDirName);

  ensureDir(topicDir);

  const savedArticles = [];
  const failedArticles = [];

  for (let index = 0; index < cleanedUrls.length; index += 1) {
    const url = cleanedUrls[index];

    try {
      const article = await fetchArticle(url);
      const fileBaseName = `${String(index + 1).padStart(2, '0')}-${sanitizePathSegment(article.title || `article-${index + 1}`, `article-${index + 1}`)}`;
      const fileName = `${fileBaseName}.md`;
      const filePath = path.join(topicDir, fileName);

      fs.writeFileSync(filePath, buildMarkdownDocument(article, normalizedTopic), 'utf-8');

      savedArticles.push({
        index: index + 1,
        title: article.title || '',
        author: article.author || '',
        publish_time: article.publish_time || '',
        source_url: article.source_url || url,
        file_name: fileName,
        file_path: filePath
      });
    } catch (error) {
      failedArticles.push({
        index: index + 1,
        source_url: url,
        error: error.message
      });
    }
  }

  const manifest = {
    action: 'save-articles',
    topic: normalizedTopic,
    output_dir: topicDir,
    requested_count: cleanedUrls.length,
    saved_count: savedArticles.length,
    failed_count: failedArticles.length,
    saved_articles: savedArticles,
    failed_articles: failedArticles
  };

  writeJson(path.join(topicDir, 'download-manifest.json'), manifest);
  return manifest;
}

function parseCliArgs(args) {
  let topic = '';
  let outputDir = '';
  let topicDirName = '';
  let urls = [];

  for (let i = 0; i < args.length; i += 1) {
    const value = args[i];

    if (value === '--output-dir' || value === '-o') {
      outputDir = args[i + 1] || '';
      i += 1;
    } else if (value === '--topic-dir') {
      topicDirName = args[i + 1] || '';
      i += 1;
    } else if (value === '--urls') {
      urls.push(...parseUrls(args[i + 1] || ''));
      i += 1;
    } else if (!value.startsWith('-') && !topic) {
      topic = value;
    } else if (!value.startsWith('-')) {
      urls.push(value);
    }
  }

  return {
    topic,
    outputDir,
    topicDirName,
    urls: uniqueUrls(urls)
  };
}

async function main() {
  const { topic, outputDir, topicDirName, urls } = parseCliArgs(process.argv.slice(2));

  if (!topic || urls.length === 0) {
    console.log(`
网页文章入库工具

用法:
  node scripts/save_web_articles.js <topic> [文章链接...] [选项]

选项:
  -o, --output-dir <目录>    知识库存储根目录（默认 ./knowledge-base）
  --topic-dir <目录名>       topic 子目录名（默认由 topic 自动生成）
  --urls <链接列表>          逗号分隔的网址列表

说明:
  微信文章会走 fetch_wechat_article 专用抓取。
  其他博客或网页文章会走通用 HTML 提取并转换为 Markdown。
`);
    process.exit(0);
  }

  try {
    const result = await saveWebArticles(topic, urls, { outputDir, topicDirName });
    console.log(JSON.stringify(result, null, 2));
  } catch (error) {
    console.error(`文章入库失败: ${error.message}`);
    process.exit(1);
  }
}

module.exports = {
  saveWebArticles
};

if (require.main === module) {
  main();
}
