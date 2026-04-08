#!/usr/bin/env node

const { searchWechatArticles, normalizeSearchResult } = require('./search_wechat');
const { fetchWechatArticle } = require('./fetch_wechat_article');
const { buildKnowledgeBase } = require('./build_knowledge_base');
const { saveWebArticles } = require('./save_web_articles');

function parseArgs(argv) {
  const [, , action, ...rest] = argv;
  let keyword = '';
  let limit = 10;
  let url = '';
  let topic = '';
  let outputDir = '';
  let topicDirName = '';
  let delayMs = 3000;
  const urls = [];

  for (let i = 0; i < rest.length; i += 1) {
    const value = rest[i];
    if (value === '--limit' || value === '-n') {
      limit = parseInt(rest[i + 1], 10) || 10;
      i += 1;
    } else if (value === '--delay' || value === '--delay-ms') {
      delayMs = parseInt(rest[i + 1], 10) || 3000;
      i += 1;
    } else if (value === '--output-dir' || value === '-o') {
      outputDir = rest[i + 1] || '';
      i += 1;
    } else if (value === '--topic-dir') {
      topicDirName = rest[i + 1] || '';
      i += 1;
    } else if (value === '--urls') {
      urls.push(
        ...String(rest[i + 1] || '')
          .split(',')
          .map((item) => item.trim())
          .filter(Boolean)
      );
      i += 1;
    } else if (!value.startsWith('-')) {
      if (action === 'search' && !keyword) keyword = value;
      if (action === 'fetch' && !url) url = value;
      if (action === 'build-kb' && !topic) topic = value;
      if (action === 'save-articles' && !topic) topic = value;
      else if (action === 'save-articles') urls.push(value);
    }
  }

  return { action, keyword, limit, url, topic, outputDir, topicDirName, urls, delayMs };
}

async function main() {
  const { action, keyword, limit, url, topic, outputDir, topicDirName, urls, delayMs } = parseArgs(process.argv);

  if (action === 'search') {
    if (!keyword) {
      console.error('缺少搜索关键词');
      process.exit(1);
    }

    const articles = await searchWechatArticles(keyword, limit);
    console.log(JSON.stringify(normalizeSearchResult(keyword, articles), null, 2));
    return;
  }

  if (action === 'fetch') {
    if (!url) {
      console.error('缺少文章链接');
      process.exit(1);
    }

    const result = await fetchWechatArticle(url);
    console.log(JSON.stringify(result, null, 2));
    return;
  }

  if (action === 'build-kb') {
    if (!topic) {
      console.error('缺少 topic');
      process.exit(1);
    }

    const result = await buildKnowledgeBase(topic, { limit, outputDir, topicDirName, delayMs });
    console.log(JSON.stringify(result, null, 2));
    return;
  }

  if (action === 'save-articles') {
    if (!topic) {
      console.error('缺少 topic');
      process.exit(1);
    }

    if (urls.length === 0) {
      console.error('缺少文章链接');
      process.exit(1);
    }

    const result = await saveWebArticles(topic, urls, { outputDir, topicDirName });
    console.log(JSON.stringify(result, null, 2));
    return;
  }

  console.error('当前支持的动作: search, fetch, build-kb, save-articles');
  process.exit(1);
}

if (require.main === module) {
  main().catch((error) => {
    console.error(error.message);
    process.exit(1);
  });
}
