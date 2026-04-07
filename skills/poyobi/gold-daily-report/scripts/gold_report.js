#!/usr/bin/env node
/**
 * 金价日报 - 国际现货(XAU/USD) + 国内金价(Au9999) + 简要资讯
 * 数据源: gold-api.com(国际) | 东方财富(国内) | er-api(汇率) | 新闻: 新浪财经+金十
 */

const http = require('http');
const https = require('https');

function fetchHTTPS(url) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0', 'Accept': '*/*' } }, res => {
      let data = '';
      res.on('data', chunk => { data += chunk; });
      res.on('end', () => {
        try { resolve(JSON.parse(data)); } catch (e) { reject(e); }
      });
    }).on('error', reject);
  });
}

function fetchHTTP(url) {
  return new Promise((resolve, reject) => {
    http.get(url, res => {
      let data = '';
      res.on('data', chunk => { data += chunk; });
      res.on('end', () => {
        try { resolve(JSON.parse(data)); } catch (e) { reject(e); }
      });
    }).on('error', reject);
  });
}

function fetchText(url) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0', 'Accept': '*/*' } }, res => {
      let data = '';
      res.on('data', chunk => { data += chunk; });
      res.on('end', () => resolve(data));
    }).on('error', reject);
  });
}

// 国际金价 (美元/盎司)
async function getInternationalGold() {
  const data = await fetchHTTPS('https://api.gold-api.com/price/XAU');
  return parseFloat(data.price);
}

// 美元兑人民币汇率
async function getUSDCNY() {
  const data = await fetchHTTPS('https://open.er-api.com/v6/latest/USD');
  return parseFloat(data.rates.CNY);
}

// 国内金价 - 上海黄金交易所 AU9999
// secid 118 = 上海金交所, f43/f44/f45/f46 实际值需 ÷100
async function getDomesticGold(code) {
  const data = await fetchHTTP(
    `http://push2.eastmoney.com/api/qt/stock/get?secid=118.${code}&fields=f43,f44,f45,f46,f47,f48,f57,f58,f60,f170`
  );
  if (!data.data || data.data.f43 === null || data.data.f43 === '-') return null;
  const d = data.data;
  const unit = '元/克';
  const changePct = d.f170 !== null ? (d.f170 / 100).toFixed(2) + '%' : '-';
  return {
    code: d.f57 || code,
    name: d.f58 || code,
    latest: d.f43 !== null ? (d.f43 / 100).toFixed(2) : '暂停交易',
    high: d.f44 !== null ? (d.f44 / 100).toFixed(2) : '-',
    low: d.f45 !== null ? (d.f45 / 100).toFixed(2) : '-',
    open: d.f46 !== null ? (d.f46 / 100).toFixed(2) : '-',
    yesterdayclose: d.f60 !== null ? (d.f60 / 100).toFixed(2) : '-',
    changeamount: d.f47 !== null ? ((d.f43 - d.f60) / 100).toFixed(2) : '-',
    changePct: changePct,
    unit,
    turnover: d.f48 !== null ? (d.f48 / 1e8).toFixed(2) + '亿元' : '-'
  };
}

// 获取近期黄金资讯摘要
async function getGoldNews() {
  try {
    // 东方财富黄金期货新闻 - 返回 HTML, 用正则提取标题
    const html = await fetchText('https://finance.eastmoney.com/a/cywjh.html');

    const titles = [];
    const re = /<a\s+[^<>]*?href="(https:\/\/[a-z0-9._-]+\.eastmoney\.com\/[^"]+)"[^<>]*?>([^<>]+?)<\/a>/gi;
    let match;
    let count = 0;
    while ((match = re.exec(html)) !== null && count < 5) {
      const title = match[2].replace(/<[^>]*>/g, '').replace(/&nbsp;/g, ' ').trim();
      if (title.length > 5 && title.length < 100) {
        titles.push(title);
        count++;
      }
    }
    return titles;
  } catch (e) {
    // 备用: 新浪财经黄金
    try {
      const html = await fetchText('https://finance.sina.com.cn/money/metal/xhjqh/');
      const titles = [];
      const re = /<a\s[^>]*?>([^<>]{10,100})<\/a>/gi;
      let match;
      let count = 0;
      while ((match = re.exec(html)) !== null && count < 5) {
        const title = match[1].replace(/<[^>]*>/g, '').trim();
        if (title.length > 5 && !title.includes('新浪') && !title.includes('广告')) {
          titles.push(title);
          count++;
        }
      }
      return titles;
    } catch (e2) {
      return [];
    }
  }
}

function toCnyPerGram(xauUsd, usdCny) {
  if (!xauUsd || !usdCny) return null;
  return (xauUsd * usdCny / 31.1035).toFixed(2);
}

function analyzeInternational(xauUsd) {
  if (!xauUsd) return '国际金价数据获取失败';
  if (xauUsd > 3500) return '国际金价创历史新高，避险情绪极强，注意回调风险';
  if (xauUsd > 3000) return '国际金价处历史高位区间，注意波动风险';
  if (xauUsd > 2500) return '金价强势运行，避险情绪支撑';
  if (xauUsd > 2000) return '金价中枢上移，关注美联储政策动向';
  return '金价低位震荡，关注经济数据';
}

function analyzeDomestic(domestic, intlCny) {
  if (!domestic || !intlCny) return '';
  const diff = (parseFloat(domestic.latest) - intlCny).toFixed(2);
  const premium = diff > 0 ? '溢价' : '折价';
  return `国内较国际${premium} ${Math.abs(diff)} 元/克`;
}

async function main() {
  const now = new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' });
  const lines = [`💰 金价日报 | ${now}\n`];

  let xauUsd = null, usdCny = null, au9999 = null;
  const errors = [];

  // 并行获取价格数据
  const results = await Promise.allSettled([
    getInternationalGold(),
    getUSDCNY(),
    getDomesticGold('AU9999')
  ]);

  if (results[0].status === 'fulfilled') xauUsd = results[0].value;
  else errors.push('国际金价: ' + results[0].reason?.message);

  if (results[1].status === 'fulfilled') usdCny = results[1].value;
  else errors.push('汇率: ' + results[1].reason?.message);

  if (results[2].status === 'fulfilled') au9999 = results[2].value;
  else errors.push('Au9999: ' + (results[2].reason?.message || '未知错误'));

  // 获取资讯 (异步, 不影响主数据)
  const newsPromise = getGoldNews().catch(() => []);

  // === 国际金价 ===
  lines.push('━━━ 国际金价 ━━━');
  if (xauUsd) {
    lines.push(`XAU/USD: ${xauUsd.toFixed(2)} 美元/盎司`);
    const cnyPerGram = toCnyPerGram(xauUsd, usdCny);
    if (cnyPerGram) {
      lines.push(`  换算: ${cnyPerGram} 元/克`);
    }
  }
  if (usdCny) {
    lines.push(`汇率(USD/CNY): ${usdCny.toFixed(4)}`);
  }

  // === 国内金价 ===
  lines.push('');
  lines.push('━━━ 国内金价 ━━━');
  if (au9999) {
    lines.push(`Au99.99: ${au9999.latest} 元/克  涨跌: ${au9999.changePct}`);
    if (au9999.high !== '-') {
      lines.push(`  最高: ${au9999.high}  最低: ${au9999.low}  昨收: ${au9999.yesterdayclose}`);
      lines.push(`  成交额: ${au9999.turnover}`);
    }
  }

  // === 分析 ===
  const intlCny = toCnyPerGram(xauUsd, usdCny);
  lines.push('');
  lines.push(`🌍 ${analyzeInternational(xauUsd)}`);
  const domAnalysis = analyzeDomestic(au9999, parseFloat(intlCny));
  if (domAnalysis) lines.push(`📊 ${domAnalysis}`);

  // === 近期资讯 ===
  lines.push('');
  lines.push('━━━ 近期资讯 ━━━');
  const news = await newsPromise;
  if (news.length > 0) {
    news.slice(0, 5).forEach((title, i) => {
      lines.push(`${i + 1}. ${title}`);
    });
  } else {
    lines.push('暂无最新资讯 (数据源暂时不可用)');
  }

  // === 数据来源 ===
  lines.push('\n📌 数据来源: gold-api.com | 东方财富 | er-api.com');

  // 错误信息
  if (errors.length > 0) {
    lines.push('⚠️ 部分数据获取失败: ' + errors.join(' | '));
  }

  return lines.join('\n');
}

main().then(report => {
  console.log(report);
}).catch(err => {
  console.error('执行失败:', err.message);
  process.exit(1);
});
