#!/usr/bin/env node
/**
 * 经验学习脚本
 * 从 zip 包中学习经验，转化为自己的 SOUL/AGENTS/TOOLS
 */

import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';
import AdmZip from 'adm-zip';
import https from 'https';
import http from 'http';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const EXPERIENCES_DIR = path.join(process.env.HOME, '.openclaw', 'experiences');
const PACKAGES_DIR = path.join(EXPERIENCES_DIR, 'packages');
const EXTRACTED_DIR = path.join(EXPERIENCES_DIR, 'extracted');
const INDEX_FILE = path.join(EXPERIENCES_DIR, 'index.json');
const WORKSPACE_DIR = process.env.OPENCLAW_WORKSPACE || path.join(process.env.HOME, '.openclaw', 'workspace');
const AGENTS_DIR = process.env.OPENCLAW_AGENTS_DIR || '/data/openclaw/agents';

// 当前目标工作空间（可被 --agent 参数覆盖）
let TARGET_WORKSPACE = WORKSPACE_DIR;

// 确保目录存在
function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

// 读取索引（新格式：按 Agent 分组）
function readIndex() {
  if (!fs.existsSync(INDEX_FILE)) {
    return { agents: {} };
  }
  const data = JSON.parse(fs.readFileSync(INDEX_FILE, 'utf8'));
  // 兼容旧格式
  if (data.experiences && !data.agents) {
    return { agents: {} };
  }
  return data;
}

// 写入索引
function writeIndex(index) {
  ensureDir(EXPERIENCES_DIR);
  fs.writeFileSync(INDEX_FILE, JSON.stringify(index, null, 2), 'utf8');
}

// 获取 Agent 名称（从工作空间路径提取）
function getAgentName(workspaceDir) {
  if (workspaceDir === WORKSPACE_DIR) {
    return 'default';
  }
  const basename = path.basename(workspaceDir);
  // 移除 -workspace 后缀
  return basename.replace(/-workspace$/, '');
}

// 检查 Agent 是否已学习
function checkLearned(index, name, version, agentName) {
  const agentExperiences = index.agents?.[agentName]?.experiences || [];
  return agentExperiences.find(e => e.name === name && e.version === version);
}

// 检查 Agent 是否有新版本
function checkNewerVersion(index, name, version, agentName) {
  const agentExperiences = index.agents?.[agentName]?.experiences || [];
  const existing = agentExperiences.find(e => e.name === name);
  if (existing && existing.version !== version) {
    return existing;
  }
  return null;
}

// 下载文件
function downloadFile(url, dest) {
  return new Promise((resolve, reject) => {
    const protocol = url.startsWith('https') ? https : http;
    const file = fs.createWriteStream(dest);
    
    protocol.get(url, (response) => {
      if (response.statusCode === 301 || response.statusCode === 302) {
        // 重定向
        downloadFile(response.headers.location, dest).then(resolve).catch(reject);
        return;
      }
      
      if (response.statusCode !== 200) {
        reject(new Error(`下载失败: HTTP ${response.statusCode}`));
        return;
      }
      
      response.pipe(file);
      file.on('finish', () => {
        file.close();
        resolve(dest);
      });
    }).on('error', reject);
  });
}

// 获取 zip 包路径
async function getZipPath(source) {
  // 如果是在线地址
  if (source.startsWith('http://') || source.startsWith('https://')) {
    const filename = path.basename(source) || 'experience.zip';
    const destPath = path.join(PACKAGES_DIR, filename);
    ensureDir(PACKAGES_DIR);
    console.log(`📥 正在下载: ${source}`);
    await downloadFile(source, destPath);
    console.log(`✅ 下载完成: ${destPath}\n`);
    return destPath;
  }
  
  // 如果是 file:// 协议
  if (source.startsWith('file://')) {
    return source.replace('file://', '');
  }
  
  // 如果是相对路径或绝对路径
  if (fs.existsSync(source)) {
    return path.resolve(source);
  }
  
  // 尝试在 packages 目录中查找
  const packagePath = path.join(PACKAGES_DIR, source);
  if (fs.existsSync(packagePath)) {
    return packagePath;
  }
  
  throw new Error(`找不到经验包: ${source}`);
}

// 解压 zip
function extractZip(zipPath) {
  const zip = new AdmZip(zipPath);
  const name = path.basename(zipPath, '.zip');
  const extractPath = path.join(EXTRACTED_DIR, name);
  
  ensureDir(extractPath);
  zip.extractAllTo(extractPath, true);
  
  return { name, extractPath };
}

// 读取 exp.yml
function readExpYml(extractPath) {
  const expPath = path.join(extractPath, 'exp.yml');
  if (!fs.existsSync(expPath)) {
    throw new Error('经验包中缺少 exp.yml 文件');
  }

  const content = fs.readFileSync(expPath, 'utf8');
  return yaml.load(content);
}

// 读取 references 目录下的文件
function readReferences(extractPath, expYml) {
  const references = {};
  const refs = expYml.references || {};

  if (refs.soul) {
    const soulPath = path.join(extractPath, refs.soul);
    if (fs.existsSync(soulPath)) {
      references.soul = fs.readFileSync(soulPath, 'utf8');
    }
  }

  if (refs.agents) {
    const agentsPath = path.join(extractPath, refs.agents);
    if (fs.existsSync(agentsPath)) {
      references.agents = fs.readFileSync(agentsPath, 'utf8');
    }
  }

  if (refs.tools) {
    const toolsPath = path.join(extractPath, refs.tools);
    if (fs.existsSync(toolsPath)) {
      references.tools = fs.readFileSync(toolsPath, 'utf8');
    }
  }

  return references;
}

// 检查依赖
function checkDependencies(expYml) {
  const required = expYml.context?.required_skills || [];
  const missing = [];
  const installed = [];
  
  // 读取已安装的 Skills
  const skillsDir = path.join(process.env.HOME, '.openclaw', 'skills');
  let installedSkills = [];
  if (fs.existsSync(skillsDir)) {
    installedSkills = fs.readdirSync(skillsDir)
      .filter(d => fs.statSync(path.join(skillsDir, d)).isDirectory());
  }
  
  // 检查每个需要的 skill
  for (const skill of required) {
    const isInstalled = installedSkills.some(s => 
      s.toLowerCase() === skill.toLowerCase() ||
      s.toLowerCase().replace(/[_-]/g, '') === skill.toLowerCase().replace(/[_-]/g, '')
    );
    
    if (isInstalled) {
      installed.push(skill);
    } else {
      missing.push(skill);
    }
  }
  
  return {
    required,
    installed,
    missing,
    satisfied: missing.length === 0
  };
}

// 分析相关性
function analyzeRelevance(expYml, workspaceDir = TARGET_WORKSPACE) {
  // 读取当前 agent 的配置
  const soulPath = path.join(workspaceDir, 'SOUL.md');
  const toolsPath = path.join(workspaceDir, 'TOOLS.md');
  
  const hasSoul = fs.existsSync(soulPath);
  const hasTools = fs.existsSync(toolsPath);
  
  // 获取 Schema 处理器
  const handler = getSchemaHandler(expYml);
  
  // 检查技能匹配
  const mySkills = []; // 实际应该从配置中读取
  const requiredSkills = handler.getSkills(expYml);
  const skillMatch = requiredSkills.filter(s => mySkills.includes(s)).length;
  
  // 计算相关度分数
  let relevance = 'medium';
  if (skillMatch === requiredSkills.length && requiredSkills.length > 0) {
    relevance = 'high';
  } else if (skillMatch > 0) {
    relevance = 'medium';
  } else {
    relevance = 'low';
  }
  
  return {
    relevance,
    skillMatch,
    totalSkills: requiredSkills.length,
    hasSoul,
    hasTools
  };
}

// Schema 版本处理器
const SCHEMA_HANDLERS = {
  // v1 格式处理器
  'openclaw.experience.v1': {
    getName: (expYml) => expYml.name,
    getVersion: (expYml) => expYml.metadata?.version || '1.0.0',
    getDescription: (expYml) => expYml.description,
    getSkills: (expYml) => expYml.skills || [],
    getReferences: (expYml) => ({
      soul: expYml.soul,
      agents: expYml.agents,
      tools: expYml.tools
    }),
    getType: (expYml) => 'best_practice' // v1 不区分类型，由 references 决定
  },
  // 旧格式处理器（向后兼容）
  'default': {
    getName: (expYml) => expYml.meta?.name || expYml.name,
    getVersion: (expYml) => expYml.meta?.version || expYml.metadata?.version || '1.0.0',
    getDescription: (expYml) => expYml.meta?.description || expYml.description,
    getSkills: (expYml) => expYml.context?.required_skills || expYml.skills || [],
    getReferences: (expYml) => expYml.references || {},
    getType: (expYml) => expYml.core?.type || 'best_practice'
  }
};

// 获取 Schema 处理器
function getSchemaHandler(expYml) {
  const schema = expYml.schema;
  if (schema && SCHEMA_HANDLERS[schema]) {
    return SCHEMA_HANDLERS[schema];
  }
  // 如果没有 schema 字段，使用旧格式处理器
  return SCHEMA_HANDLERS['default'];
}

// 根据 references 决定写入哪些文件
function determineTargets(expYml) {
  const targets = [];
  const reasons = [];

  // 获取 Schema 处理器
  const handler = getSchemaHandler(expYml);

  // 从经验包中读取引用
  const refs = handler.getReferences(expYml);
  const type = handler.getType(expYml);

  // 1. SOUL.md - 原则、价值观类
  if (refs.soul) {
    targets.push({
      file: 'SOUL.md',
      section: '行为准则',
      reason: `引用: ${refs.soul}`,
      sourceFile: refs.soul  // 记录源文件路径
    });
    reasons.push(`SOUL.md: ${refs.soul}`);
  }

  // 2. AGENTS.md - 工作流程、规则、职责类
  if (refs.agents) {
    targets.push({
      file: 'AGENTS.md',
      section: '工作流程',
      reason: `引用: ${refs.agents}`,
      sourceFile: refs.agents
    });
    reasons.push(`AGENTS.md: ${refs.agents}`);
  }

  // 3. TOOLS.md - 工具使用技巧类
  if (refs.tools) {
    targets.push({
      file: 'TOOLS.md',
      section: '工具使用经验',
      reason: `引用: ${refs.tools}`,
      sourceFile: refs.tools
    });
    reasons.push(`TOOLS.md: ${refs.tools}`);
  }

  // 4. .learnings/ERRORS.md - 错误教训类型
  if (type === 'error_lesson') {
    targets.push({
      file: '.learnings/ERRORS.md',
      section: '错误教训',
      reason: '错误教训类型'
    });
    reasons.push('ERRORS.md: 错误教训');
  }

  // 5. .learnings/LEARNINGS.md - 知识补充类型
  if (type === 'knowledge_gap') {
    targets.push({
      file: '.learnings/LEARNINGS.md',
      section: '知识补充',
      reason: '知识补充类型'
    });
    reasons.push('LEARNINGS.md: 知识补充');
  }

  // 如果没有明确匹配，默认写入 AGENTS.md
  if (targets.length === 0) {
    targets.push({
      file: 'AGENTS.md',
      section: '经验积累',
      reason: '默认归类'
    });
    reasons.push('AGENTS.md: 默认归类');
  }

  return { targets, reasons };
}

// 生成转化方案
function generatePlan(expYml, relevance) {
  const { targets, reasons } = determineTargets(expYml);
  
  return {
    targets,
    reasons,
    content: generateContent(expYml)
  };
}

// 生成要写入的内容
function generateContent(expYml) {
  const lines = [];
  
  lines.push(`## ${expYml.meta?.title || '经验'}
`);
  lines.push(`> 来源: 经验包 ${expYml.meta?.name} v${expYml.meta?.version}`);
  lines.push(`> 类型: ${expYml.core?.type || 'best_practice'}`);
  lines.push('');
  
  if (expYml.core?.problem?.description) {
    lines.push(`**问题**: ${expYml.core.problem.description}`);
    lines.push('');
  }
  
  if (expYml.core?.solution?.steps?.length > 0) {
    lines.push('**解决方案**:');
    expYml.core.solution.steps.forEach((step, i) => {
      lines.push(`${i + 1}. ${step}`);
    });
    lines.push('');
  }
  
  if (expYml.core?.solution?.code) {
    lines.push('**代码示例**:');
    lines.push('```javascript');
    lines.push(expYml.core.solution.code);
    lines.push('```');
    lines.push('');
  }
  
  if (expYml.core?.principle?.core) {
    lines.push(`**核心原理**: ${expYml.core.principle.core}`);
    lines.push('');
  }
  
  return lines.join('\n');
}

// 应用学习（支持从 references 读取内容）
function applyLearning(expYml, plan, references) {
  const results = {
    success: [],
    failed: [],
    details: []
  };

  for (const target of plan.targets) {
    const targetPath = path.join(TARGET_WORKSPACE, target.file);

    try {
      // 备份原文件
      let backupPath = null;
      if (fs.existsSync(targetPath)) {
        backupPath = `${targetPath}.bak.${Date.now()}`;
        fs.copyFileSync(targetPath, backupPath);
      }

      // 确定内容来源
      let content;
      if (target.sourceFile && references[target.file.toLowerCase().replace('.md', '')]) {
        // 从 references 读取内容
        content = references[target.file.toLowerCase().replace('.md', '')];
      } else {
        // 生成内容（兼容旧格式）
        if (target.file === 'SOUL.md') {
          content = generateSoulContent(expYml);
        } else if (target.file === 'AGENTS.md') {
          content = generateAgentsContent(expYml);
        } else {
          content = generateContent(expYml);
        }
      }

      // 追加内容
      if (fs.existsSync(targetPath)) {
        fs.appendFileSync(targetPath, '\n\n' + content);
      } else {
        ensureDir(path.dirname(targetPath));
        fs.writeFileSync(targetPath, content);
      }

      results.success.push(target.file);
      results.details.push({
        file: target.file,
        status: 'success',
        backupPath,
        linesAdded: content.split('\n').length
      });
    } catch (err) {
      results.failed.push(target.file);
      results.details.push({
        file: target.file,
        status: 'failed',
        error: err.message
      });
    }
  }

  return results;
}

// 生成 SOUL.md 格式的内容（吸收内化）
function generateSoulContent(expYml) {
  const handler = getSchemaHandler(expYml);
  const name = handler.getName(expYml);
  const version = handler.getVersion(expYml);
  const description = handler.getDescription(expYml);
  const type = handler.getType(expYml);
  
  const lines = [];
  
  lines.push(`## ${description || '经验'}
`);
  lines.push(`> 来源: 经验包 ${name} v${version}`);
  lines.push(`> 类型: ${type}`);
  lines.push(`> 内化时间: ${new Date().toISOString()}`);
  lines.push('');
  
  // v1 格式没有 core 字段，直接从 description 提取
  lines.push(`**原则**: ${description}`);
  lines.push('');
  
  lines.push('**行为准则**:');
  lines.push(`1. ${description}`);
  lines.push('');
  
  return lines.join('\n');
}

// 生成 AGENTS.md 格式的内容（工作流程）
function generateAgentsContent(expYml) {
  const handler = getSchemaHandler(expYml);
  const name = handler.getName(expYml);
  const version = handler.getVersion(expYml);
  const description = handler.getDescription(expYml);
  const type = handler.getType(expYml);
  
  const lines = [];
  
  lines.push(`## ${description || '经验'}
`);
  lines.push(`> 来源: 经验包 ${name} v${version}`);
  lines.push(`> 类型: ${type}`);
  lines.push('');
  
  lines.push(`**场景**: ${description}`);
  lines.push('');
  
  lines.push('**处理流程**:');
  lines.push(`1. ${description}`);
  lines.push('');
  
  lines.push(`**规则**: ${description}`);
  lines.push('');
  
  return lines.join('\n');
}

// 生成变更预览
function generateChangePreview(expYml, plan, references = {}, workspaceDir = TARGET_WORKSPACE) {
  const preview = [];

  for (const target of plan.targets) {
    const targetPath = path.join(workspaceDir, target.file);

    // 确定内容来源
    let newContent;
    const refKey = target.file.toLowerCase().replace('.md', '');
    if (references[refKey]) {
      // 从 references 读取内容
      newContent = references[refKey];
    } else {
      // 生成内容（兼容旧格式）
      if (target.file === 'SOUL.md') {
        newContent = generateSoulContent(expYml);
      } else if (target.file === 'AGENTS.md') {
        newContent = generateAgentsContent(expYml);
      } else {
        newContent = generateContent(expYml);
      }
    }

    // 读取现有内容（如果文件存在）
    let existingContent = '';
    let fileExists = false;
    if (fs.existsSync(targetPath)) {
      existingContent = fs.readFileSync(targetPath, 'utf8');
      fileExists = true;
    }

    // 计算变更：显示文件末尾现有内容 + 新增内容
    const existingLines = existingContent.split('\n');
    const contextLines = 5; // 显示文件末尾5行作为上下文
    const tailContent = existingLines.slice(-contextLines).join('\n');

    preview.push({
      file: target.file,
      path: targetPath,
      exists: fileExists,
      operation: fileExists ? '追加' : '新建',
      tailContent, // 文件末尾现有内容
      newContent,  // 新增内容
      section: target.section,
      reason: target.reason
    });
  }

  return preview;
}

// 显示变更预览
function displayChangePreview(preview) {
  for (const item of preview) {
    console.log(`📄 ${item.file}`);
    console.log(`   路径: ${item.path}`);
    console.log(`   操作: ${item.operation}`);
    console.log(`   写入位置: ${item.section}`);
    console.log(`   原因: ${item.reason}`);
    console.log();
    
    if (item.exists) {
      console.log('   文件末尾现有内容:');
      console.log('   ' + '─'.repeat(60));
      const tailLines = item.tailContent.split('\n');
      tailLines.forEach(line => {
        console.log('   ' + line);
      });
      console.log('   ' + '─'.repeat(60));
      console.log('                          ↓ 追加以下内容');
    }
    
    console.log('   新增内容:');
    console.log('   ' + '─'.repeat(60));
    const newLines = item.newContent.split('\n');
    newLines.forEach((line, i) => {
      console.log('   + ' + line);
    });
    console.log('   ' + '─'.repeat(60));
    console.log();
  }
}

// 用户确认（强制交互）
function confirmChanges() {
  return new Promise((resolve) => {
    console.log('⚠️  警告: 这将修改您的 SOUL.md / AGENTS.md / TOOLS.md 等核心文件');
    console.log('   建议在执行前备份重要文件\n');
    console.log('是否确认应用这些变更？');
    console.log('  [Y] 确认应用');
    console.log('  [N] 取消');
    console.log('  [S] 保存变更预览到文件，稍后手动应用');
    console.log();
    
    const args = process.argv.slice(3);
    
    // 仅预览模式
    if (args.includes('--dry-run')) {
      console.log('模式: 仅预览 (--dry-run)');
      resolve(false);
      return;
    }
    
    // 强制交互式确认（默认）
    // 使用 readline 进行交互
    import('readline').then((readlineModule) => {
      const readline = readlineModule.createInterface({
        input: process.stdin,
        output: process.stdout
      });
      
      readline.question('请输入选项 (Y/N/S): ', (answer) => {
        readline.close();
        const choice = answer.trim().toUpperCase();
        
        if (choice === 'Y' || choice === 'YES') {
          resolve(true);
        } else if (choice === 'S' || choice === 'SAVE') {
          // 保存预览到文件
          resolve('save');
        } else {
          resolve(false);
        }
      });
    }).catch(() => {
      // 如果 readline 失败，使用命令行参数回退
      if (args.includes('--yes') || args.includes('-y')) {
        console.log('Y (通过命令行参数 --yes)');
        resolve(true);
      } else {
        console.log('N (未确认，取消执行)');
        resolve(false);
      }
    });
  });
}

// 生成引导式验证说明
function generateVerificationGuide(expYml, results, deps) {
  const guide = {
    title: expYml.meta?.title || '经验',
    type: expYml.core?.type || 'best_practice',
    problem: expYml.core?.problem?.description || '',
    solution: expYml.core?.solution?.steps || [],
    skills: deps.required || [],
    appliedFiles: results.success || [],
    steps: []
  };
  
  // 根据经验类型生成验证步骤
  switch (guide.type) {
    case 'tool_tip':
      guide.steps = generateToolTipVerification(guide);
      break;
    case 'best_practice':
      guide.steps = generateBestPracticeVerification(guide);
      break;
    case 'error_lesson':
      guide.steps = generateErrorLessonVerification(guide);
      break;
    case 'knowledge_gap':
      guide.steps = generateKnowledgeGapVerification(guide);
      break;
    default:
      guide.steps = generateGenericVerification(guide);
  }
  
  return guide;
}

// 工具技巧验证
function generateToolTipVerification(guide, workspaceDir = TARGET_WORKSPACE) {
  const steps = [];
  
  steps.push({
    title: '查看已学习的技巧',
    command: `tail -30 ${path.join(workspaceDir, guide.appliedFiles[0] || 'TOOLS.md')}`,
    description: '确认经验内容已正确写入'
  });
  
  if (guide.skills.length > 0) {
    steps.push({
      title: `准备使用 ${guide.skills.join(', ')}`,
      description: `确保您有使用这些技能的场景`,
      note: guide.skills.map(s => `- ${s}: 用于...`).join('\n   ')
    });
  }
  
  steps.push({
    title: '实际场景验证',
    description: `下次遇到以下场景时，应用本经验：`,
    scenario: guide.problem
  });
  
  steps.push({
    title: '验证执行',
    description: '按照经验中的步骤执行：',
    steps: guide.solution.map((s, i) => `${i + 1}. ${s}`)
  });
  
  return steps;
}

// 最佳实践验证
function generateBestPracticeVerification(guide) {
  const steps = [];
  
  steps.push({
    title: '理解实践背景',
    description: guide.problem
  });
  
  steps.push({
    title: '查看实践规范',
    command: `grep -A 10 "${guide.title}" ${path.join(TARGET_WORKSPACE, guide.appliedFiles[0] || 'AGENTS.md')}`,
    description: '确认规范已内化到工作流'
  });
  
  steps.push({
    title: '场景化验证',
    description: '在以下场景中应用本实践：',
    scenarios: [
      `场景: ${guide.problem}`,
      '预期结果: 按照最佳实践执行，避免问题发生'
    ]
  });
  
  return steps;
}

// 错误教训验证
function generateErrorLessonVerification(guide) {
  const steps = [];
  
  steps.push({
    title: '回顾错误场景',
    description: guide.problem
  });
  
  steps.push({
    title: '查看预防措施',
    command: `grep -A 5 "${guide.title}" ${path.join(TARGET_WORKSPACE, '.learnings/ERRORS.md')}`,
    description: '确认预防措施已记录'
  });
  
  steps.push({
    title: '预防验证',
    description: '下次遇到类似场景时：',
    check: '是否触发了错误条件？',
    action: '如果触发，按照经验中的预防措施执行'
  });
  
  return steps;
}

// 知识补充验证
function generateKnowledgeGapVerification(guide) {
  const steps = [];
  
  steps.push({
    title: '学习新知识',
    description: guide.problem
  });
  
  steps.push({
    title: '知识应用',
    description: '在以下场景中运用新知识：',
    scenarios: guide.solution
  });
  
  return steps;
}

// 通用验证
function generateGenericVerification(guide) {
  return [
    {
      title: '查看学习内容',
      command: `tail -20 ${path.join(TARGET_WORKSPACE, guide.appliedFiles[0] || 'TOOLS.md')}`,
      description: '确认经验已正确记录'
    },
    {
      title: '场景验证',
      description: `在相关场景中应用：${guide.problem}`
    }
  ];
}

// 显示引导式验证说明
function displayVerificationGuide(guide) {
  console.log('🔍 验证指南\n');
  console.log(`经验: ${guide.title}`);
  console.log(`类型: ${guide.type}`);
  console.log('');
  
  console.log('请按以下步骤验证学习效果：\n');
  
  guide.steps.forEach((step, i) => {
    console.log(`${i + 1}. ${step.title}`);
    
    if (step.description) {
      console.log(`   ${step.description}`);
    }
    
    if (step.command) {
      console.log(`   💻 执行: ${step.command}`);
    }
    
    if (step.scenario) {
      console.log(`   📍 场景: ${step.scenario}`);
    }
    
    if (step.scenarios) {
      step.scenarios.forEach(s => console.log(`   📍 ${s}`));
    }
    
    if (step.steps) {
      step.steps.forEach(s => console.log(`   ✓ ${s}`));
    }
    
    if (step.check) {
      console.log(`   ❓ 检查: ${step.check}`);
    }
    
    if (step.action) {
      console.log(`   🎯 行动: ${step.action}`);
    }
    
    if (step.note) {
      console.log(`   📝 ${step.note}`);
    }
    
    console.log('');
  });
  
  console.log('💡 提示: 验证完成后，经验将被标记为"已验证"\n');
}

// 记录学习状态
function recordLearning(expYml, appliedFiles) {
  const index = readIndex();
  
  // 获取 Schema 处理器
  const handler = getSchemaHandler(expYml);
  const name = handler.getName(expYml);
  const version = handler.getVersion(expYml);
  const description = handler.getDescription(expYml);
  
  const agentName = getAgentName(TARGET_WORKSPACE);
  
  // 初始化 Agent 的学习记录
  if (!index.agents) {
    index.agents = {};
  }
  if (!index.agents[agentName]) {
    index.agents[agentName] = {
      name: agentName,
      workspace: TARGET_WORKSPACE,
      experiences: []
    };
  }
  
  const agentExperiences = index.agents[agentName].experiences;
  const existingIndex = agentExperiences.findIndex(e => e.name === name);
  
  const record = {
    name: name,
    version: version,
    title: description,
    status: 'learned',
    learned_at: new Date().toISOString(),
    applied_to: appliedFiles
  };
  
  if (existingIndex >= 0) {
    agentExperiences[existingIndex] = record;
  } else {
    agentExperiences.push(record);
  }
  
  writeIndex(index);
}

// 主函数
async function main() {
  const args = process.argv.slice(2);
  
  // 解析参数
  let source = null;
  let targetAgent = null;
  let autoConfirm = false;
  let dryRun = false;
  
  for (const arg of args) {
    if (arg === '--yes' || arg === '-y') {
      autoConfirm = true;
    } else if (arg === '--dry-run') {
      dryRun = true;
    } else if (arg.startsWith('--agent=')) {
      targetAgent = arg.replace('--agent=', '').trim();
    } else if (!arg.startsWith('--')) {
      source = arg;
    }
  }
  
  if (!source) {
    console.error('用法: node learn.mjs <zip包路径或URL> [选项]');
    console.error('');
    console.error('选项:');
    console.error('  --yes, -y           自动确认应用变更');
    console.error('  --dry-run           仅预览变更，不实际应用');
    console.error('  --agent=<name>      指定目标 Agent（默认当前 Agent）');
    console.error('');
    console.error('示例:');
    console.error('  node learn.mjs https://example.com/exp.zip');
    console.error('  node learn.mjs ~/.openclaw/experiences/packages/exp.zip --yes');
    console.error('  node learn.mjs file:///path/to/exp.zip --dry-run');
    console.error('  node learn.mjs exp.zip --agent=严哥-workspace');
    process.exit(1);
  }
  
  // 设置目标工作空间
  if (targetAgent) {
    // 支持两种格式：完整目录名或简写
    const agentDir = targetAgent.endsWith('-workspace') ? targetAgent : `${targetAgent}-workspace`;
    const agentPath = path.join(AGENTS_DIR, agentDir);
    
    if (!fs.existsSync(agentPath)) {
      console.error(`❌ 错误: 找不到 Agent "${targetAgent}"`);
      console.error(`   路径: ${agentPath}`);
      console.error(`   可用 Agents: 请检查 ${AGENTS_DIR}`);
      process.exit(1);
    }
    
    TARGET_WORKSPACE = agentPath;
    console.log(`🎯 目标 Agent: ${targetAgent}`);
    console.log(`📁 工作空间: ${TARGET_WORKSPACE}\n`);
  }
  
  console.log('📚 开始学习经验...\n');
  
  try {
    // 1. 获取 zip 包
    const zipPath = await getZipPath(source);
    
    // 2. 解压
    console.log('📦 解压经验包...');
    const { name, extractPath } = extractZip(zipPath);
    console.log(`✅ 解压完成: ${extractPath}\n`);
    
    // 3. 读取 exp.yml
    console.log('📄 读取经验内容...');
    const expYml = readExpYml(extractPath);
    
    // 获取 Schema 处理器
    const handler = getSchemaHandler(expYml);
    const expName = handler.getName(expYml);
    const expVersion = handler.getVersion(expYml);
    const expDescription = handler.getDescription(expYml);
    const expType = handler.getType(expYml);
    
    console.log(`  名称: ${expName}`);
    console.log(`  版本: ${expVersion}`);
    console.log(`  描述: ${expDescription}`);
    console.log(`  类型: ${expType}`);
    console.log();
    
    // 4. 检查是否已学习（按 Agent）
    const index = readIndex();
    const agentName = getAgentName(TARGET_WORKSPACE);
    const learned = checkLearned(index, expName, expVersion, agentName);
    
    if (learned) {
      console.log(`⚠️  该经验已学习过（${expName} v${expVersion}）`);
      console.log(`   Agent: ${agentName}`);
      console.log(`   学习时间: ${learned.learned_at}`);
      return;
    }
    
    // 5. 检查是否有新版本（按 Agent）
    const newer = checkNewerVersion(index, expName, expVersion, agentName);
    if (newer) {
      console.log(`⚠️  发现新版本:`);
      console.log(`   Agent: ${agentName}`);
      console.log(`   本地: ${newer.version}`);
      console.log(`   新包: ${expVersion}`);
      console.log(`   提示: 使用 --force 参数强制更新，或先删除旧版本`);
      return;
    }
    
    // 6. 检查依赖
    console.log('🔍 检查依赖...');
    const deps = checkDependencies(expYml);
    const requiredSkills = handler.getSkills(expYml);
    console.log(`  需要技能: ${requiredSkills.join(', ') || '无'}`);
    if (deps.installed.length > 0) {
      console.log(`  已安装: ${deps.installed.join(', ')}`);
    }
    if (deps.missing.length > 0) {
      console.log(`  ⚠️  未安装: ${deps.missing.join(', ')}`);
      console.log(`  💡 提示: 使用 "openclaw skills install <skill-name>" 安装缺失的技能`);
    }
    console.log(`  依赖满足: ${deps.satisfied ? '✅' : '⚠️ 部分缺失'}`);
    console.log();
    
    // 7. 分析相关性
    console.log('🎯 分析相关性...');
    const relevance = analyzeRelevance(expYml, TARGET_WORKSPACE);
    console.log(`  相关度: ${relevance.relevance}`);
    console.log(`  技能匹配: ${relevance.skillMatch}/${relevance.totalSkills}`);
    console.log();
    
    // 8. 生成转化方案
    console.log('📝 生成转化方案...');
    const plan = generatePlan(expYml, relevance);
    console.log(`  建议写入:`);
    plan.targets.forEach(t => {
      console.log(`    - ${t.file} (${t.section})`);
      console.log(`      原因: ${t.reason}`);
    });
    if (plan.reasons.length > 0) {
      console.log();
      console.log('  判断依据:');
      plan.reasons.forEach(r => console.log(`    • ${r}`));
    }
    console.log();
    
    // 9. 读取 references 文件（如果存在）
    const references = readReferences(extractPath, expYml);
    if (Object.keys(references).length > 0) {
      console.log('📂 读取引用文件:');
      const refs = handler.getReferences(expYml);
      for (const [key, file] of Object.entries(refs)) {
        if (file && typeof file === 'string') {
          console.log(`   - ${file}`);
        }
      }
      console.log();
    }

    // 10. 显示变更预览
    console.log('🔍 变更预览:\n');
    const preview = generateChangePreview(expYml, plan, references, TARGET_WORKSPACE);
    displayChangePreview(preview);
    console.log();
    
    // 10. 用户确认
    const confirmed = await confirmChanges();
    if (confirmed === 'save') {
      // 保存预览到文件
      const savePath = path.join(EXPERIENCES_DIR, 'pending', `${expName}-preview.txt`);
      ensureDir(path.dirname(savePath));
      
      let content = `经验包: ${expName} v${expVersion}\n`;
      content += `描述: ${expDescription}\n`;
      content += `类型: ${expType}\n\n`;
      content += '=== 变更预览 ===\n\n';
      
      const preview = generateChangePreview(expYml, plan);
      preview.forEach(item => {
        content += `文件: ${item.file}\n`;
        content += `路径: ${item.path}\n`;
        content += `新增内容:\n${item.newContent}\n\n`;
      });
      
      fs.writeFileSync(savePath, content, 'utf8');
      console.log(`✅ 变更预览已保存到: ${savePath}`);
      console.log('💡 您可以查看后手动应用这些变更');
      return;
    }
    
    if (!confirmed) {
      console.log('❌ 已取消学习');
      return;
    }
    console.log();
    
    // 11. 应用学习
    console.log('💾 应用学习...\n');
    const results = applyLearning(expYml, plan, references);
    
    // 显示成功结果
    if (results.success.length > 0) {
      console.log('✅ 修改成功:');
      results.details
        .filter(d => d.status === 'success')
        .forEach(d => {
          console.log(`   📄 ${d.file}`);
          console.log(`      新增行数: ${d.linesAdded}`);
          if (d.backupPath) {
            console.log(`      备份路径: ${d.backupPath}`);
          }
        });
      console.log();
    }
    
    // 显示失败结果
    if (results.failed.length > 0) {
      console.log('❌ 修改失败:');
      results.details
        .filter(d => d.status === 'failed')
        .forEach(d => {
          console.log(`   📄 ${d.file}`);
          console.log(`      错误: ${d.error}`);
        });
      console.log();
    }
    
    // 12. 记录学习状态
    const appliedFiles = results.success;
    recordLearning(expYml, appliedFiles);
    
    // 13. 显示引导式验证提醒
    console.log('🎉 经验学习完成！\n');
    
    // 生成引导式验证说明
    const verificationGuide = generateVerificationGuide(expYml, results, deps);
    displayVerificationGuide(verificationGuide);
    
    if (deps.missing.length > 0) {
      console.log('⚠️  注意: 以下依赖技能未安装，经验可能无法完全生效:');
      deps.missing.forEach(s => console.log(`   - ${s}`));
      console.log('   建议安装: openclaw skills install <skill-name>');
      console.log();
    }
    
  } catch (err) {
    console.error('❌ 错误:', err.message);
    process.exit(1);
  }
}

main();
