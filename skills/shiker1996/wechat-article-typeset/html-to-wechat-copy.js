#!/usr/bin/env node
/**
 * 将已有 HTML 文章转为公众号可复制的内联样式格式，并 POST 到 edit.shiker.tech 获取复制页 URL。
 * 用法：node html-to-wechat-copy.js <path-to-article.html>
 *
 * === AI 生成 HTML 时的输入要求（二选一） ===
 * 文章类型对应：大厂早报→格式一；AI 职场文/单厂深度/轻松吃瓜/下周职场预警→格式二；
 * 技术摸鱼周报、一周速读→视结构选格式一（多条 item+影响）或格式二（自由小节+表格）。
 *
 * 【格式一】早报/资讯列表（推荐用于：周一 大厂早报；周四/周六 若写成多条 item+影响）
 * - 整篇包在 <body> 内，且有一层 <div class="article"> 包裹正文。
 * - 结构必须包含（顺序固定）：
 *   - <h1>标题</h1>
 *   - <div class="intro">引言一段或多段</div>
 *   - 多个 <div class="item">
 *        <div class="item-title">序号. 【标签】标题</div>
 *        <div class="item-content">正文</div>
 *        <div class="item-impact"><strong>影响：</strong>说明</div>
 *     </div>
 *   - <div class="thinking"><p>今日思考</p><p>内容</p></div>
 *   - <div class="divider"></div>
 *   - <div class="footer"><p>...</p></div>
 * - 无需写 <style>，脚本会按「引用」+ 统一背景输出。
 *
 * 【格式二】通用长文（推荐用于：周二 AI 职场文、周三 单厂深度、周五 轻松吃瓜、周日 下周职场预警；周四/周六 若为自由小节+表格）
 * - 标准 HTML，<body> 内直接放内容（或一层 <section> 包裹全文）。
 * - 需要带背景/边框的块：用 <section style="...">...</section>，内联样式可写 background、border-left、padding 等；
 *   脚本会把 <section> 转为 <blockquote>，公众号会保留引用样式。
 * - 表格：用 <table>，公众号会保留表格背景与边框，无需改标签。
 * - 标题用 <h1>、<h2>、<h3>，段落用 <p>，列表用 <ul>/<li>；分割可用 <hr> 或留空。
 * - 整篇会被包一层统一背景的 section。
 */

import { readFileSync } from 'fs'
import { resolve } from 'path'

const articlePath = process.argv[2]
if (!articlePath) {
  console.error('用法: node html-to-wechat-copy.js <path-to-article.html>')
  process.exit(1)
}

const raw = readFileSync(resolve(process.cwd(), articlePath), 'utf8')

// 优先：大厂早报等 .article 结构；否则：通用 HTML（body 或 section 包裹）
let inner
let useGeneric = false
const articleMatch = raw.match(/<div class="article">([\s\S]*?)<\/div>\s*<\/body>/)
if (articleMatch) {
  inner = articleMatch[1]
} else {
  const bodyMatch = raw.match(/<body[^>]*>([\s\S]*?)<\/body>/i)
  if (bodyMatch) {
    inner = bodyMatch[1].trim()
    useGeneric = true
  } else {
    console.error('未找到 .article 或 <body> 内容')
    process.exit(1)
  }
}

// 内联样式：公众号仅对「引用 blockquote」和「表格」保留背景色与边框，整篇用统一背景
const styles = {
  // 整篇文章统一背景
  section: "margin:0;padding:16px 14px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Microsoft YaHei',sans-serif;font-size:16px;color:#333;line-height:1.6;word-break:break-word;background:#f5f5f5;box-sizing:border-box",
  h1: "font-size:20px;font-weight:700;color:#1a1a1a;margin-bottom:15px;line-height:1.4;text-align:center",
  // 引用：intro（公众号引用支持背景+边框）
  blockquoteIntro: "margin:20px 0 25px;padding:18px;border-left:4px solid #667eea;background:#f0f4ff;font-size:14px;color:#555;line-height:1.7;box-sizing:border-box",
  // 引用：每条资讯卡片
  blockquoteItem: "margin:22px 0;padding:18px;border-left:4px solid #ff6b6b;background:#fafafa;box-sizing:border-box",
  itemTitle: "font-size:15px;font-weight:600;color:#333;margin-bottom:10px",
  itemContent: "font-size:14px;color:#555;line-height:1.7;margin-bottom:8px",
  // 引用：影响（嵌套在 item 内的小引用块）
  blockquoteImpact: "margin-top:10px;padding:10px;border-left:3px solid #ff9500;background:#fff;font-size:13px;color:#666;box-sizing:border-box",
  // 引用：今日思考（深色块）
  blockquoteThinking: "margin:25px 0;padding:18px;border-left:4px solid #764ba2;background:#667eea;color:#fff;font-size:14px;line-height:1.7;box-sizing:border-box",
  thinkingP: "margin:0 0 8px 0",
  // 分割线：无背景/边框的 div 可能被吞，用段落间距代替
  divider: "margin:25px 0;font-size:0;line-height:0",
  // 页脚：仅文字样式，无背景边框
  footer: "margin-top:25px;padding-top:20px;text-align:center;color:#999;font-size:13px",
  footerStrong: "color:#666",
}

function escapeHtml(str) {
  if (!str) return ''
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

// 将原文结构转为公众号兼容 HTML：仅用 blockquote（引用）和整篇统一背景保留背景/边框
function convertToWechatHtml(html) {
  let out = ''
  // 标题（无背景无边框）
  const h1Match = html.match(/<h1>([\s\S]*?)<\/h1>/)
  if (h1Match) {
    out += `<h1 style="${styles.h1}">${h1Match[1].trim()}</h1>\n`
  }
  // intro → 引用（支持背景+边框）
  const introMatch = html.match(/<div class="intro">\s*([\s\S]*?)\s*<\/div>/)
  if (introMatch) {
    out += `<blockquote style="${styles.blockquoteIntro}">${introMatch[1].trim()}</blockquote>\n`
  }
  // items → 每条一条引用，内里「影响」再包一层引用
  const itemReg = /<div class="item">\s*<div class="item-title">([\s\S]*?)<\/div>\s*<div class="item-content">([\s\S]*?)<\/div>\s*<div class="item-impact">([\s\S]*?)<\/div>\s*<\/div>/g
  let m
  while ((m = itemReg.exec(html)) !== null) {
    out += `<blockquote style="${styles.blockquoteItem}">`
    out += `<div style="${styles.itemTitle}">${m[1].trim()}</div>`
    out += `<div style="${styles.itemContent}">${m[2].trim()}</div>`
    out += `<blockquote style="${styles.blockquoteImpact}">${m[3].trim()}</blockquote>`
    out += `</blockquote>\n`
  }
  // thinking → 引用（深色背景+边框）
  const thinkingMatch = html.match(/<div class="thinking">\s*([\s\S]*?)\s*<\/div>/)
  if (thinkingMatch) {
    const inner = thinkingMatch[1].trim()
      .replace(/<p>/g, `<p style="${styles.thinkingP}">`)
      .replace(/<p style="[^"]*">/g, `<p style="${styles.thinkingP}">`)
    out += `<blockquote style="${styles.blockquoteThinking}">${inner}</blockquote>\n`
  }
  // divider：仅留间距，不用带背景的 div
  if (/<div class="divider">/.test(html)) {
    out += `<p style="${styles.divider}">&#8203;</p>\n`
  }
  // footer：仅文字样式
  const footerMatch = html.match(/<div class="footer">\s*([\s\S]*?)\s*<\/div>/)
  if (footerMatch) {
    let footerInner = footerMatch[1]
      .replace(/<p style="margin-top: 8px;">/g, '<p style="margin:8px 0 0 0;">')
      .replace(/<p style="margin-top: 15px;">/g, '<p style="margin:15px 0 0 0;">')
      .replace(/<strong>/g, `<strong style="${styles.footerStrong}">`)
    out += `<div style="${styles.footer}">${footerInner.trim()}</div>\n`
  }
  return out
}

// 通用 HTML：带样式的 section 改为 blockquote（公众号保留引用背景/边框），表格不动，整篇包一层统一背景
function convertGenericToWechatHtml(html) {
  // section → blockquote，以便公众号保留背景与边框
  let out = html.replace(/<section\s/g, '<blockquote ').replace(/<\/section>/g, '</blockquote>')
  return out
}

const bodyHtml = useGeneric ? convertGenericToWechatHtml(inner) : convertToWechatHtml(inner)
const sectionStyle = styles.section
const html = `<section data-tool="公众号排版" style="${sectionStyle}">\n${bodyHtml}</section>`

const res = await fetch('https://edit.shiker.tech/api/copy', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ html }),
})

const data = await res.json()
if (data.success && data.data?.url) {
  console.log(data.data.url)
} else {
  console.error('请求失败:', data.message || res.status, data)
  process.exit(1)
}
