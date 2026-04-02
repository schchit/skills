#!/usr/bin/env node
/**
 * Roco Kingdom:World Offline Data Tool
 * All data is bundled — no network requests needed.
 * To update: clawhub update rocom
 */

import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DATA_DIR = join(__dirname, 'data');
const PETS_FILE = join(DATA_DIR, 'pets.json');
const SKILLS_FILE = join(DATA_DIR, 'skills.json');
const ITEMS_FILE = join(DATA_DIR, 'items.json');
const QUESTS_FILE = join(DATA_DIR, 'quests.json');
const FORMATIONS_FILE = join(DATA_DIR, 'formations.json');
const PETS_DETAIL_DIR = join(DATA_DIR, 'pets_detail');
const SKILLS_DETAIL_DIR = join(DATA_DIR, 'skills_detail');
const FORMATIONS_DETAIL_DIR = join(DATA_DIR, 'formations_detail');
const META_FILE = join(DATA_DIR, 'meta.json');
const MARKS_FILE = join(DATA_DIR, 'marks.json');
const DUNGEONS_FILE = join(DATA_DIR, 'dungeons.json');
const REGIONS_FILE = join(DATA_DIR, 'regions.json');

const PETS_DETAIL_ALL = join(DATA_DIR, 'pets_detail_all.json');
const SKILLS_DETAIL_ALL = join(DATA_DIR, 'skills_detail_all.json');
const FORMATIONS_DETAIL_ALL = join(DATA_DIR, 'formations_detail_all.json');

// Lazy-loaded merged detail maps
let _petsDetail = null, _skillsDetail = null, _formationsDetail = null;

function loadPetsDetail() {
  if (!_petsDetail) _petsDetail = readJSON(PETS_DETAIL_ALL, {});
  return _petsDetail;
}
function loadSkillsDetail() {
  if (!_skillsDetail) _skillsDetail = readJSON(SKILLS_DETAIL_ALL, {});
  return _skillsDetail;
}
function loadFormationsDetail() {
  if (!_formationsDetail) _formationsDetail = readJSON(FORMATIONS_DETAIL_ALL, {});
  return _formationsDetail;
}

// ===== Version Check =====
const SKILL_VERSION = '1.3.0';

async function cmdUpdateCheck() {
  console.log(`📦 当前版本: ${SKILL_VERSION}`);
  console.log(`   更新方式: clawhub update rocom`);
  console.log(`   或: openclaw skills update rocom`);
}

// ===== Helpers =====
function readJSON(file, fallback = null) {
  if (!existsSync(file)) return fallback;
  try { return JSON.parse(readFileSync(file, 'utf-8')); }
  catch { return fallback; }
}

// ===== Search =====
async function cmdSearch(keyword) {
  const results = [];

  const pets = readJSON(PETS_FILE, []);
  for (const p of pets) {
    if (p.pageName.includes(keyword) || p.name.includes(keyword) || p.regionName?.includes(keyword)) {
      results.push({ type: '🐾', data: p, text: formatPetBrief(p) });
    }
  }

  const skills = readJSON(SKILLS_FILE, []);
  for (const s of skills) {
    if (s.pageName.includes(keyword) || s.name.includes(keyword) || s.effect?.includes(keyword)) {
      results.push({ type: '⚔️', data: s, text: `  ${s.name} [${s.element}] ${s.type} 威力${s.power}` });
    }
  }

  const items = readJSON(ITEMS_FILE, []);
  for (const i of items) {
    if (i.pageName.includes(keyword)) {
      results.push({ type: '🎒', data: i, text: `  ${i.name}` });
    }
  }

  const quests = readJSON(QUESTS_FILE, []);
  for (const q of quests) {
    if (q.pageName.includes(keyword)) {
      results.push({ type: '📋', data: q, text: `  ${q.name}` });
    }
  }

  const marks = readJSON(MARKS_FILE);
  if (marks) {
    for (const m of [...(marks.positive || []), ...(marks.negative || [])]) {
      if (m.name.includes(keyword) || m.desc.includes(keyword)) {
        results.push({ type: '🔮', data: m, text: `  ${m.name}：${m.desc}` });
      }
    }
  }

  const dungeons = readJSON(DUNGEONS_FILE, []);
  for (const d of dungeons) {
    if (d.name.includes(keyword) || d.desc?.includes(keyword) || d.pets?.some(p => p.name.includes(keyword))) {
      results.push({ type: '🏰', data: d, text: `  ${d.name}` });
    }
  }

  const regions = readJSON(REGIONS_FILE, []);
  for (const r of regions) {
    if (r.name.includes(keyword) || r.pets?.some(p => p.includes(keyword))) {
      results.push({ type: '🗺️', data: r, text: `  ${r.name}（${r.pets.length} 只精灵）` });
    }
  }

  if (!results.length) {
    console.log(`未找到包含"${keyword}"的结果`);
    return;
  }

  console.log(`找到 ${results.length} 个结果:\n`);
  let lastType = '';
  const typeLabels = { '🐾': '精灵', '⚔️': '技能', '🎒': '道具', '📋': '任务', '🔮': '印记', '🏰': '副本', '🗺️': '地区' };
  for (const r of results) {
    if (r.type !== lastType) {
      console.log(`\n${typeLabels[r.type] || r.type}:`);
      lastType = r.type;
    }
    console.log(r.text);
  }

  if (results.length === 1 && results[0].type === '🐾') {
    const safeName = results[0].data.pageName.replace(/[\/\\]/g, '_');
    const detailFile = join(PETS_DETAIL_DIR, `${safeName}.json`);
    const d = readJSON(detailFile);
    if (d) { console.log('\n详情:\n'); console.log(formatPet(d)); }
  }
}

// ===== Pet =====
function getPetDetail(pageName) {
  return loadPetsDetail()[pageName] || null;
}

async function cmdPet(args) {
  const pets = readJSON(PETS_FILE);
  if (!pets) { console.log('数据缺失，请运行: clawhub update rocom'); return; }

  const sub = args[0] || 'list';
  const rest = args.slice(1);

  if (sub === 'list') {
    let filtered = [...pets];
    for (let i = 0; i < rest.length; i++) {
      if (rest[i] === '--element' && rest[i + 1]) {
        const e = rest[++i];
        filtered = filtered.filter(p => p.mainElement === e || p.secondElement === e);
      } else if (rest[i] === '--stage' && rest[i + 1]) {
        filtered = filtered.filter(p => p.stage === rest[++i]);
      } else if (rest[i] === '--boss') {
        filtered = filtered.filter(p => p.form === '首领形态');
      } else if (rest[i] === '--region') {
        filtered = filtered.filter(p => p.form === '地区形态');
      } else if (rest[i] === '--form' && rest[i + 1]) {
        filtered = filtered.filter(p => p.form === rest[++i]);
      }
    }
    filtered.sort((a, b) => (parseInt(a.id) || 9999) - (parseInt(b.id) || 9999));
    if (!filtered.length) { console.log('未找到匹配的精灵'); return; }
    console.log(`共 ${filtered.length} 只精灵:\n`);
    for (const p of filtered) console.log(formatPetBrief(p));

  } else if (sub === 'search' || sub === 's') {
    const kw = rest.join(' ');
    if (!kw) { console.log('用法: pet search <关键词>'); return; }
    const matches = pets.filter(p =>
      p.pageName.includes(kw) || p.name.includes(kw) || p.regionName?.includes(kw)
    );
    if (!matches.length) { console.log(`未找到"${kw}"`); return; }
    console.log(`找到 ${matches.length} 只:\n`);
    for (const p of matches) console.log(formatPetBrief(p));
    if (matches.length <= 3) {
      console.log('\n详情:');
      for (const p of matches) {
        const d = getPetDetail(p.pageName);
        if (d) console.log('\n' + formatPet(d));
        else console.log(`\n🐾 ${p.name} — 暂无详情数据`);
      }
    }

  } else if (sub === 'detail' || sub === 'd') {
    const name = rest.join(' ');
    if (!name) { console.log('用法: pet detail <精灵名>'); return; }
    const match = pets.find(p => p.name === name || p.pageName === name);
    if (!match) {
      const fuzzy = pets.filter(p => p.name.includes(name) || p.pageName.includes(name));
      if (fuzzy.length === 1) {
        const d = getPetDetail(fuzzy[0].pageName);
        if (d) console.log(formatPet(d));
        else console.log(`🐾 ${fuzzy[0].name} — 暂无详情数据`);
      } else if (fuzzy.length > 1) {
        console.log(`找到 ${fuzzy.length} 个匹配，请输入更精确的名称:`);
        for (const p of fuzzy) console.log(formatPetBrief(p));
      } else {
        console.log(`未找到: ${name}`);
      }
      return;
    }
    const d = getPetDetail(match.pageName);
    if (d) console.log(formatPet(d));
    else console.log(`🐾 ${match.name} — 暂无详情数据`);

  } else if (sub === 'evolve' || sub === 'e') {
    const name = rest.join(' ');
    if (!name) { console.log('用法: pet evolve <精灵名>'); return; }
    const match = pets.find(p => p.name === name || p.pageName.includes(name));
    if (!match) { console.log(`未找到: ${name}`); return; }

    const d = getPetDetail(match.pageName);
    if (!d) { console.log('暂无该精灵详情数据'); return; }

    const initialName = d['精灵初阶名称'] || '';
    const family = [];
    for (const p of pets) {
      if (p.form !== '原始形态' && p.form !== '首领形态') continue;
      const pd = getPetDetail(p.pageName);
      if (pd && pd['精灵初阶名称'] === initialName) {
        family.push(p);
      }
    }

    const stageOrder = { 'Ⅰ阶': 1, 'Ⅱ阶': 2, '最终形态': 3 };
    const formOrder = { '原始形态': 0, '地区形态': 1, '首领形态': 2 };
    family.sort((a, b) => {
      const sd = (stageOrder[a.stage] || 0) - (stageOrder[b.stage] || 0);
      if (sd !== 0) return sd;
      return (formOrder[a.form] || 0) - (formOrder[b.form] || 0);
    });

    console.log(`🐾 ${match.name} 的进化链:\n`);
    if (family.length > 0) {
      for (const p of family) {
        const region = p.regionName ? ` (${p.regionName})` : '';
        const formTag = p.form === '首领形态' ? ' [首领]' : p.form === '地区形态' ? ' [地区]' : '';
        console.log(`  ${p.name}${region}${formTag} (${p.stage})`);
      }
    } else {
      console.log(`  ${initialName || match.name} → ${match.name}`);
    }
    if (d['进化条件']) console.log(`\n  进化条件: ${d['进化条件']}`);
    else console.log(`\n  进化条件: 暂无数据`);

  } else {
    console.log('宠物子命令: list, search <词>, detail <名>, evolve <名>');
  }
}

// ===== Skill =====
async function cmdSkill(args) {
  const skills = readJSON(SKILLS_FILE);
  if (!skills) { console.log('数据缺失，请运行: clawhub update rocom'); return; }

  const sub = args[0] || 'list';
  const rest = args.slice(1);

  if (sub === 'list') {
    let filtered = [...skills];
    for (let i = 0; i < rest.length; i++) {
      if (rest[i] === '--element' && rest[i + 1]) {
        filtered = filtered.filter(s => s.element === rest[++i]);
      } else if (rest[i] === '--type' && rest[i + 1]) {
        filtered = filtered.filter(s => s.type === rest[++i]);
      }
    }
    filtered.sort((a, b) => (parseInt(b.power) || 0) - (parseInt(a.power) || 0));
    if (!filtered.length) { console.log('未找到匹配的技能'); return; }
    console.log(`共 ${filtered.length} 个技能:\n`);
    for (const s of filtered) {
      console.log(`  ${s.name} [${s.element}] ${s.type} 耗能${s.cost} 威力${s.power}`);
    }

  } else if (sub === 'search' || sub === 's') {
    const kw = rest.join(' ');
    if (!kw) { console.log('用法: skill search <关键词>'); return; }
    const matches = skills.filter(s =>
      s.name.includes(kw) || s.pageName.includes(kw) || s.effect?.includes(kw)
    );
    if (!matches.length) { console.log(`未找到"${kw}"`); return; }
    console.log(`找到 ${matches.length} 个技能:\n`);
    for (const s of matches) console.log(`  ${s.name} [${s.element}] ${s.type} 威力${s.power} — ${s.effect || ''}`);

  } else {
    console.log('技能子命令: list, search <词>');
  }
}

// ===== Item =====
async function cmdItem(args) {
  const items = readJSON(ITEMS_FILE);
  if (!items) { console.log('数据缺失，请运行: clawhub update rocom'); return; }

  const sub = args[0] || 'list';
  const rest = args.slice(1);

  if (sub === 'list') {
    console.log(`共 ${items.length} 个道具:\n`);
    for (const i of items) console.log(`  ${i.name}`);
  } else if (sub === 'search' || sub === 's') {
    const kw = rest.join(' ');
    if (!kw) { console.log('用法: item search <关键词>'); return; }
    const matches = items.filter(i => i.pageName.includes(kw));
    if (!matches.length) { console.log(`未找到"${kw}"`); return; }
    console.log(`找到 ${matches.length} 个:\n`);
    for (const i of matches) console.log(`  ${i.name}`);
  }
}

// ===== Quest =====
async function cmdQuest(args) {
  const quests = readJSON(QUESTS_FILE);
  if (!quests) { console.log('数据缺失，请运行: clawhub update rocom'); return; }
  console.log(`共 ${quests.length} 个任务:\n`);
  for (const q of quests) console.log(`  ${q.name}`);
}

// ===== Mark =====
async function cmdMark(args) {
  const marks = readJSON(MARKS_FILE);
  if (!marks) { console.log('印记数据缺失'); return; }
  const sub = args[0] || 'list';
  const rest = args.slice(1);
  if (sub === 'list') {
    console.log('🔮 印记系统\n');
    console.log('── 正面印记 ──');
    for (const m of marks.positive) console.log(`  ${m.name}：${m.desc}`);
    console.log('\n── 负面印记 ──');
    for (const m of marks.negative) console.log(`  ${m.name}：${m.desc}`);
    console.log(`\n共 ${marks.positive.length + marks.negative.length} 种印记`);
  } else if (sub === 'search' || sub === 's') {
    const kw = rest.join(' ');
    if (!kw) { console.log('用法: mark search <关键词>'); return; }
    const posHits = marks.positive.filter(m => m.name.includes(kw) || m.desc.includes(kw));
    const negHits = marks.negative.filter(m => m.name.includes(kw) || m.desc.includes(kw));
    const total = posHits.length + negHits.length;
    if (!total) { console.log(`未找到包含"${kw}"的印记`); return; }
    console.log(`找到 ${total} 个印记:\n`);
    if (posHits.length) { console.log('正面:'); for (const m of posHits) console.log(`  ${m.name}：${m.desc}`); }
    if (negHits.length) { console.log('负面:'); for (const m of negHits) console.log(`  ${m.name}：${m.desc}`); }
  } else { console.log('印记子命令: list, search <关键词>'); }
}

// ===== Dungeon =====
function formatDungeon(d) {
  const L = [`🏰 ${d.name}`];
  if (d.desc) L.push(`   ${d.desc}`);
  if (d.count) L.push(`   次数: ${d.count}`);
  if (d.rewards.length) L.push(`   奖励: ${d.rewards.map(r => `${r.type}×${r.amount}`).join(' / ')}`);
  if (d.pets.length) L.push(`   精灵: ${d.pets.map(p => `${p.name}×${p.amount}`).join(' / ')}`);
  return L.join('\n');
}

async function cmdDungeon(args) {
  const dungeons = readJSON(DUNGEONS_FILE);
  if (!dungeons) { console.log('数据缺失，请运行: clawhub update rocom'); return; }
  const sub = args[0] || 'list';
  const rest = args.slice(1);
  if (sub === 'list') {
    console.log(`🏰 副本图鉴（共 ${dungeons.length} 个）\n`);
    for (const d of dungeons) console.log(`  ${d.name} [${d.count || '?'}]`);
  } else if (sub === 'search' || sub === 's') {
    const kw = rest.join(' ');
    if (!kw) { console.log('用法: dungeon search <关键词>'); return; }
    const matches = dungeons.filter(d => d.name.includes(kw) || d.desc.includes(kw) || d.pets.some(p => p.name.includes(kw)));
    if (!matches.length) { console.log(`未找到"${kw}"`); return; }
    console.log(`找到 ${matches.length} 个副本:\n`);
    for (const d of matches) console.log(formatDungeon(d) + '\n');
  } else { console.log('副本子命令: list, search <关键词>'); }
}

// ===== Region =====
function formatRegion(r) {
  const L = [`🗺️ ${r.name}（${r.pets.length} 只精灵）`];
  for (let i = 0; i < r.pets.length; i += 5) {
    L.push(`   ${r.pets.slice(i, i + 5).join(' / ')}`);
  }
  return L.join('\n');
}

async function cmdRegion(args) {
  const regions = readJSON(REGIONS_FILE);
  if (!regions) { console.log('数据缺失，请运行: clawhub update rocom'); return; }
  const sub = args[0] || 'list';
  const rest = args.slice(1);
  if (sub === 'list') {
    console.log(`🗺️ 地区图鉴（共 ${regions.length} 个地区）\n`);
    for (const r of regions) console.log(`  ${r.name} — ${r.pets.length} 只精灵`);
  } else if (sub === 'detail' || sub === 'd') {
    const kw = rest.join(' ');
    if (!kw) { console.log('用法: region detail <地区名>'); return; }
    const match = regions.find(r => r.name === kw);
    if (match) { console.log(formatRegion(match)); return; }
    const fuzzy = regions.filter(r => r.name.includes(kw));
    if (fuzzy.length === 1) console.log(formatRegion(fuzzy[0]));
    else if (fuzzy.length > 1) { console.log(`找到 ${fuzzy.length} 个匹配:\n`); for (const r of fuzzy) console.log(`  ${r.name}（${r.pets.length} 只）`); }
    else console.log(`未找到地区: ${kw}`);
  } else if (sub === 'search' || sub === 's') {
    const kw = rest.join(' ');
    if (!kw) { console.log('用法: region search <关键词>'); return; }
    const matches = regions.filter(r => r.name.includes(kw) || r.pets.some(p => p.includes(kw)));
    if (!matches.length) { console.log(`未找到"${kw}"`); return; }
    console.log(`找到 ${matches.length} 个地区:\n`);
    for (const r of matches) {
      const hit = r.pets.filter(p => p.includes(kw));
      console.log(`  ${r.name}${hit.length ? ' — 匹配: ' + hit.join(', ') : '（' + r.pets.length + ' 只）'}`);
    }
  } else { console.log('地区子命令: list, detail <地区名>, search <关键词>'); }
}

// ===== Nature =====
const NATURES = [
  { name: '勇敢', up: '物攻', down: '物防' }, { name: '固执', up: '物攻', down: '魔攻' },
  { name: '调皮', up: '物攻', down: '魔防' }, { name: '孤僻', up: '物攻', down: '速度' },
  { name: '大胆', up: '物防', down: '物攻' }, { name: '淘气', up: '物防', down: '魔攻' },
  { name: '无虑', up: '物防', down: '魔防' }, { name: '悠闲', up: '物防', down: '速度' },
  { name: '保守', up: '魔攻', down: '物攻' }, { name: '稳重', up: '魔攻', down: '物防' },
  { name: '马虎', up: '魔攻', down: '魔防' }, { name: '急躁', up: '魔攻', down: '速度' },
  { name: '沉着', up: '魔防', down: '物攻' }, { name: '温顺', up: '魔防', down: '物防' },
  { name: '慎重', up: '魔防', down: '魔攻' }, { name: '狂妄', up: '魔防', down: '速度' },
  { name: '胆小', up: '速度', down: '物攻' }, { name: '开朗', up: '速度', down: '魔攻' },
  { name: '天真', up: '速度', down: '魔防' }, { name: '急切', up: '速度', down: '物防' },
  { name: '坦率', up: null, down: null }, { name: '认真', up: null, down: null },
  { name: '浮躁', up: null, down: null }, { name: '害羞', up: null, down: null },
  { name: '实干', up: null, down: null },
];

async function cmdNature(args) {
  const sub = args[0] || 'list';
  const rest = args.slice(1);
  if (sub === 'list') {
    console.log('🧠 性格一览\n');
    console.log('── 有加成 ──');
    for (const n of NATURES) if (n.up) console.log(`  ${n.name}：${n.up}↑ ${n.down}↓`);
    console.log('\n── 无加成 ──');
    for (const n of NATURES) if (!n.up) console.log(`  ${n.name}：无加成`);
    console.log(`\n共 ${NATURES.length} 种性格`);
  } else if (sub === 'search' || sub === 's') {
    const kw = rest.join(' ');
    if (!kw) { console.log('用法: nature search <性格名/属性名>'); return; }
    const matches = NATURES.filter(n => n.name.includes(kw) || n.up?.includes(kw) || n.down?.includes(kw));
    if (!matches.length) { console.log(`未找到"${kw}"`); return; }
    console.log(`找到 ${matches.length} 个:\n`);
    for (const n of matches) console.log(n.up ? `  ${n.name}：${n.up}↑ ${n.down}↓` : `  ${n.name}：无加成`);
  } else { console.log('性格子命令: list, search <性格名/属性名>'); }
}

// ===== Formation =====
function formatFormation(f) {
  if (!f) return '未找到数据';
  const L = [];
  L.push(`👥 ${f.title || '未命名阵容'}`);
  L.push(`   类型: ${f.type || '?'} | 作者: ${f.author || '?'} | 日期: ${f.date || '?'}`);
  if (f.magic) L.push(`   血脉魔法: ${f.magic}`);
  if (f.intro) {
    const intro = f.intro.length > 300 ? f.intro.slice(0, 300) + '...' : f.intro;
    L.push(`   介绍: ${intro}`);
  }
  if (f.members.length) {
    L.push(`   队伍:`);
    for (const m of f.members) {
      const parts = [`🐾${m.name}`];
      if (m.nature) parts.push(`性格:${m.nature}`);
      if (m.bloodline) parts.push(`血脉:${m.bloodline}`);
      if (m.ivs) parts.push(`个体:${m.ivs}`);
      L.push(`     ${parts.join(' | ')}`);
      if (m.skills.length) L.push(`       技能: ${m.skills.join(', ')}`);
    }
  }
  return L.join('\n');
}

async function cmdFormation(args) {
  const formations = readJSON(FORMATIONS_FILE);
  if (!formations) { console.log('数据缺失，请运行: clawhub update rocom'); return; }

  const sub = args[0] || 'list';
  const rest = args.slice(1);

  if (sub === 'list') {
    console.log(`共 ${formations.length} 个阵容:\n`);
    for (const f of formations) console.log(`  👥 ${f.name}`);

  } else if (sub === 'search' || sub === 's') {
    const kw = rest.join(' ');
    if (!kw) { console.log('用法: formation search <关键词>'); return; }
    const matches = formations.filter(f => f.pageName.includes(kw) || f.name.includes(kw));
    if (!matches.length) { console.log(`未找到"${kw}"`); return; }
    console.log(`找到 ${matches.length} 个阵容:\n`);
    for (const f of matches) console.log(`  👥 ${f.name}`);

  } else if (sub === 'detail' || sub === 'd') {
    const kw = rest.join(' ');
    if (!kw) { console.log('用法: formation detail <关键词>'); return; }
    const match = formations.find(f => f.name.includes(kw) || f.pageName.includes(kw));
    if (!match) { console.log(`未找到: ${kw}`); return; }
    const d = loadFormationsDetail()[match.pageName] || null;
    if (d) console.log(formatFormation(d));
    else console.log(`👥 ${match.name} — 暂无详情数据`);

  } else {
    console.log('阵容子命令: list, search <词>, detail <词>');
  }
}

// ===== Analyze =====
async function cmdAnalyze(args) {
  const pets = readJSON(PETS_FILE);
  if (!pets) { console.log('数据缺失，请运行: clawhub update rocom'); return; }

  const sub = args[0] || 'element';
  const rest = args.slice(1);

  if (sub === 'element') {
    const dist = {};
    for (const p of pets) {
      if (p.form !== '原始形态') continue;
      dist[p.mainElement] = (dist[p.mainElement] || 0) + 1;
    }
    console.log('📊 属性分布（原始形态）:\n');
    const sorted = Object.entries(dist).sort((a, b) => b[1] - a[1]);
    const max = sorted[0]?.[1] || 1;
    for (const [elem, count] of sorted) {
      const bar = '█'.repeat(Math.round(count / max * 20));
      console.log(`  ${elem.padEnd(4)} ${bar} ${count}`);
    }
    console.log(`\n  总计: ${sorted.reduce((s, [, c]) => s + c, 0)} 只`);

  } else if (sub === 'stats') {
    const originals = pets.filter(p => p.form === '原始形态' && p.stage === '最终形态');
    const withStats = [];
    for (const p of originals) {
      const d = getPetDetail(p.pageName);
      if (!d) continue;
      const total = ['生命', '物攻', '魔攻', '物防', '魔防', '速度']
        .reduce((s, k) => s + (parseInt(d[k]) || 0), 0);
      withStats.push({ ...p, stats: d, total });
    }

    withStats.sort((a, b) => b.total - a.total);
    console.log('📊 最终形态种族值总和排行 (Top 30):\n');
    for (let i = 0; i < Math.min(30, withStats.length); i++) {
      const p = withStats[i];
      const s = p.stats;
      console.log(`  ${String(i + 1).padStart(2)}. ${p.name.padEnd(6)} 总计:${String(p.total).padStart(4)}  HP:${(s['生命'] || '?').padStart(3)} 攻:${(s['物攻'] || '?').padStart(3)} 魔攻:${(s['魔攻'] || '?').padStart(3)} 防:${(s['物防'] || '?').padStart(3)} 魔防:${(s['魔防'] || '?').padStart(3)} 速:${(s['速度'] || '?').padStart(3)}`);
    }

  } else if (sub === 'top') {
    let stat = '速度', n = 20;
    for (let i = 0; i < rest.length; i++) {
      if (rest[i] === '--stat' && rest[i + 1]) stat = rest[++i];
      if (rest[i] === '--n' && rest[i + 1]) n = parseInt(rest[++i]) || 20;
    }

    const originals = pets.filter(p => p.form === '原始形态' && p.stage === '最终形态');
    const withStat = [];
    for (const p of originals) {
      const d = getPetDetail(p.pageName);
      if (!d) continue;
      withStat.push({ ...p, value: parseInt(d[stat]) || 0 });
    }

    withStat.sort((a, b) => b.value - a.value);
    console.log(`\n📊 ${stat} Top ${n}:\n`);
    for (let i = 0; i < Math.min(n, withStat.length); i++) {
      console.log(`  ${String(i + 1).padStart(2)}. ${withStat[i].name.padEnd(6)} ${withStat[i].value}`);
    }

  } else {
    console.log('分析子命令: element (属性分布), stats (种族值排行), top --stat <属性> --n <数量>');
  }
}

// ===== Status =====
function cmdStatus() {
  const meta = readJSON(META_FILE);
  if (!meta) { console.log('数据缺失'); return; }

  console.log(`📊 Roco Kingdom Data Status\n`);
  console.log(`  Data version: ${SKILL_VERSION}`);
  console.log(`  Last sync: ${meta.lastSync}`);
  console.log(`  Pets: ${meta.counts.pets}`);
  console.log(`  Skills: ${meta.counts.skills}`);
  console.log(`  Items: ${meta.counts.items}`);
  console.log(`  Quests: ${meta.counts.quests}`);
  console.log(`  Formations: ${meta.counts.formations}`);
  if (meta.counts.marks) console.log(`  Marks: ${meta.counts.marks}`);
  if (meta.counts.dungeons) console.log(`  Dungeons: ${meta.counts.dungeons}`);
  if (meta.counts.regions) console.log(`  Regions: ${meta.counts.regions}`);

  const detailCount = Object.keys(loadPetsDetail()).length;
  console.log(`  Pet details: ${detailCount}`);
  console.log(`\n  Update: clawhub update rocom`);
}

// ===== Format Helpers =====
function formatPetBrief(p) {
  const elem = p.secondElement ? `${p.mainElement}/${p.secondElement}` : p.mainElement;
  const region = p.regionName ? ` (${p.regionName})` : '';
  return `  #${p.id || '???'} ${p.name}${region} [${elem || '?'}] ${p.stage || ''}`;
}

function formatPet(info) {
  if (!info) return '未找到数据';
  const L = [];
  const name = info['精灵名称'] || '?';
  const id = info['精灵编号'] || '?';
  L.push(`🐾 ${name} (#${id})`);

  const attrs = [info['主属性']].filter(Boolean);
  if (info['2属性']) attrs.push(info['2属性']);
  L.push(`   属性: ${attrs.join(' / ') || '未知'} | 阶段: ${info['精灵阶段'] || '?'} | 形态: ${info['精灵形态'] || '?'}`);

  if (info['特性']) L.push(`   特性: ${info['特性']} — ${info['特性描述'] || ''}`);

  const stats = ['生命', '物攻', '魔攻', '物防', '魔防', '速度']
    .map(k => `${k}:${info[k] || '?'}`).join(' | ');
  L.push(`   种族值: ${stats}`);

  if (info['体型']) L.push(`   体型: ${info['体型']} | 重量: ${info['重量'] || '?'}`);

  if (info['技能']) {
    const skills = info['技能'].split(',').map(s => s.trim());
    const levels = (info['技能解锁等级'] || '').split(',').map(s => s.trim());
    L.push(`   技能:`);
    skills.forEach((s, i) => {
      const lv = levels[i] ? `Lv.${levels[i]}` : '';
      L.push(`     ${lv} ${s}`);
    });
  }

  if (info['血脉技能']) L.push(`   血脉技能: ${info['血脉技能']}`);
  if (info['可学技能石']) L.push(`   可学技能石: ${info['可学技能石']}`);
  if (info['进化条件']) L.push(`   进化条件: ${info['进化条件']}`);
  if (info['精灵初阶名称'] && info['精灵初阶名称'] !== info['精灵名称']) L.push(`   初始形态: ${info['精灵初阶名称']}`);
  if (info['分布地区']) L.push(`   分布地区: ${info['分布地区']}`);
  if (info['图鉴课题']) L.push(`   📋 图鉴课题: ${info['图鉴课题']}`);
  if (info['精灵描述']) L.push(`   📝 ${info['精灵描述']}`);
  return L.join('\n');
}

// ===== Main =====
const [,, cmd, ...args] = process.argv;

try {
  switch (cmd) {
    case 'search': case 's':
      await cmdSearch(args.join(' '));
      break;
    case 'pet':
      await cmdPet(args);
      break;
    case 'skill':
      await cmdSkill(args);
      break;
    case 'item':
      await cmdItem(args);
      break;
    case 'quest':
      await cmdQuest(args);
      break;
    case 'analyze':
      await cmdAnalyze(args);
      break;
    case 'formation':
      await cmdFormation(args);
      break;
    case 'mark':
      await cmdMark(args);
      break;
    case 'dungeon':
      await cmdDungeon(args);
      break;
    case 'region':
      await cmdRegion(args);
      break;
    case 'nature':
      await cmdNature(args);
      break;
    case 'status':
      cmdStatus();
      break;
    case 'update':
      await cmdUpdateCheck();
      break;
    default:
      console.log(`🏰 Roco Kingdom:World Data Tool (v${SKILL_VERSION})

Usage:
  node rocom.mjs search <keyword>      Search across all categories
  node rocom.mjs pet list [filters]    Pet list
  node rocom.mjs pet search <name>     Search pet
  node rocom.mjs pet detail <name>     Pet details (stats/skills/traits)
  node rocom.mjs pet evolve <name>     Evolution chain
  node rocom.mjs skill list [filters]  Skill list
  node rocom.mjs skill search <name>   Search skill
  node rocom.mjs item list|search      Items
  node rocom.mjs quest list            Quests
  node rocom.mjs formation list        Formations
  node rocom.mjs formation search <q>  Search formations
  node rocom.mjs formation detail <q>  Formation details (natures/skills)
  node rocom.mjs mark list             Marks (positive/negative)
  node rocom.mjs mark search <q>       Search marks
  node rocom.mjs dungeon list          Dungeons
  node rocom.mjs dungeon search <q>    Search dungeons
  node rocom.mjs region list           Regions
  node rocom.mjs region detail <name>  Region pet list
  node rocom.mjs nature list           Nature list
  node rocom.mjs nature search <q>     Search nature by name or stat
  node rocom.mjs analyze <type>        Analysis (element/stats/top)
  node rocom.mjs status                Data status
  node rocom.mjs update                Check for skill updates

Filters:
  --element <type>   Filter by element
  --stage <stage>    Filter by stage
  --boss             Boss forms only
  --region           Regional forms only
  --type <cat>       Skill category (物攻/魔攻/变化)
  --stat <name>      Stat name for ranking
  --n <count>        Number of results

Data is bundled — no sync needed. To update:
  clawhub update rocom
  or: openclaw skills update rocom`);
  }
} catch (e) {
  console.error('❌ Error:', e.message);
  process.exit(1);
}
