#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const { searchWechatArticles, normalizeSearchResult } = require('./search_wechat');
const { fetchWechatArticle } = require('./fetch_wechat_article');

function sanitizePathSegment(value, fallback = 'untitled') {
  const sanitized = String(value || '')
    .replace(/[<>:"/\\|?*\u0000-\u001F]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 80);

  return sanitized || fallback;
}

function slugify(value, fallback = 'topic') {
  const slug = String(value || '')
    .toLowerCase()
    .replace(/[^a-z0-9\u4e00-\u9fa5]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 80);

  return slug || fallback;
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

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function buildKnowledgeBase(topic, options = {}) {
  const normalizedTopic = String(topic || '').trim();
  if (!normalizedTopic) {
    throw new Error('topic is required');
  }

  const limit = Math.min(Math.max(parseInt(options.limit, 10) || 5, 1), 50);
  const delayMs = Math.max(parseInt(options.delayMs, 10) || 3000, 0);
  const outputRoot = path.resolve(options.outputDir || path.join(process.cwd(), 'knowledge-base'));
  const topicDirName = sanitizePathSegment(options.topicDirName || slugify(normalizedTopic, 'topic'));
  const topicDir = path.join(outputRoot, topicDirName);

  ensureDir(topicDir);

  const articles = await searchWechatArticles(normalizedTopic, limit);
  const searchResult = normalizeSearchResult(normalizedTopic, articles);
  writeJson(path.join(topicDir, 'search-results.json'), searchResult);

  const savedArticles = [];
  const failedArticles = [];

  for (let index = 0; index < searchResult.items.length; index += 1) {
    const item = searchResult.items[index];

    try {
      const article = await fetchWechatArticle(item.url);
      const fileBaseName = `${String(index + 1).padStart(2, '0')}-${sanitizePathSegment(article.title || item.title, `article-${index + 1}`)}`;
      const fileName = `${fileBaseName}.md`;
      const filePath = path.join(topicDir, fileName);

      fs.writeFileSync(filePath, buildMarkdownDocument(article, normalizedTopic), 'utf-8');

      savedArticles.push({
        index: index + 1,
        title: article.title || item.title,
        author: article.author || '',
        publish_time: article.publish_time || item.publish_time || '',
        source_url: article.source_url || item.url,
        file_name: fileName,
        file_path: filePath
      });
    } catch (error) {
      failedArticles.push({
        index: index + 1,
        title: item.title,
        source_url: item.url,
        error: error.message
      });
    }

    if (delayMs > 0 && index < searchResult.items.length - 1) {
      await sleep(delayMs);
    }
  }

  const manifest = {
    action: 'build-kb',
    topic: normalizedTopic,
    output_dir: topicDir,
    requested_limit: limit,
    delay_ms: delayMs,
    searched_count: searchResult.total,
    saved_count: savedArticles.length,
    failed_count: failedArticles.length,
    saved_articles: savedArticles,
    failed_articles: failedArticles
  };

  writeJson(path.join(topicDir, 'manifest.json'), manifest);
  return manifest;
}

function parseCliArgs(args) {
  let topic = '';
  let limit = 5;
  let outputDir = '';
  let topicDirName = '';
  let delayMs = 3000;

  for (let i = 0; i < args.length; i += 1) {
    const value = args[i];

    if (value === '--limit' || value === '-n') {
      limit = parseInt(args[i + 1], 10) || 5;
      i += 1;
    } else if (value === '--delay' || value === '--delay-ms') {
      delayMs = parseInt(args[i + 1], 10) || 3000;
      i += 1;
    } else if (value === '--output-dir' || value === '-o') {
      outputDir = args[i + 1] || '';
      i += 1;
    } else if (value === '--topic-dir') {
      topicDirName = args[i + 1] || '';
      i += 1;
    } else if (!value.startsWith('-') && !topic) {
      topic = value;
    }
  }

  return { topic, limit, outputDir, topicDirName, delayMs };
}

async function main() {
  const { topic, limit, outputDir, topicDirName, delayMs } = parseCliArgs(process.argv.slice(2));

  if (!topic) {
    console.log(`
文章知识库搭建工具

用法:
  node scripts/build_knowledge_base.js <topic> [选项]

选项:
  -n, --limit <数量>         搜索并尝试下载的文章数（默认5，最大50）
  --delay, --delay-ms <毫秒> 每篇文章之间的抓取间隔（默认3000）
  -o, --output-dir <目录>    知识库存储根目录（默认 ./knowledge-base）
  --topic-dir <目录名>       topic 子目录名（默认由 topic 自动生成）
`);
    process.exit(0);
  }

  try {
    const result = await buildKnowledgeBase(topic, { limit, outputDir, topicDirName, delayMs });
    console.log(JSON.stringify(result, null, 2));
  } catch (error) {
    console.error(`知识库搭建失败: ${error.message}`);
    process.exit(1);
  }
}

module.exports = {
  buildKnowledgeBase,
  sanitizePathSegment,
  slugify
};

if (require.main === module) {
  main();
}
