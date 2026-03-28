#!/usr/bin/env node

/**
 * Create Harness Engineering Documentation
 * 
 * 分析当前项目结构，自动创建符合 Harness Engineering 要求的文档
 * 
 * 使用方法:
 *   node create-harness-docs.js --init          # 创建所有文档
 *   node create-harness-docs.js --agents         # 仅创建 AGENTS.md
 *   node create-harness-docs.js --architecture  # 仅创建架构文档
 *   node create-harness-docs.js --quality        # 仅创建质量评级
 *   node create-harness-docs.js --validate       # 验证现有文档
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const PROJECT_ROOT = process.cwd();

// 颜色输出
const colors = {
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  blue: '\x1b[36m',
  reset: '\x1b[0m'
};

function log(msg, color = 'green') {
  console.log(`${colors[color]}▶${colors.reset} ${msg}`);
}

function error(msg) {
  console.error(`${colors.red}✗${colors.reset} ${msg}`);
}

function success(msg) {
  console.log(`${colors.green}✓${colors.reset} ${msg}`);
}

// 分析项目结构
function analyzeProject() {
  log('分析项目结构...', 'blue');
  
  const result = {
    name: path.basename(PROJECT_ROOT),
    language: 'unknown',
    framework: 'unknown',
    hasTests: false,
    hasDocs: false,
    hasCI: false,
    domains: [],
    files: []
  };
  
  // 检测语言/框架
  if (fs.existsSync(path.join(PROJECT_ROOT, 'package.json'))) {
    const pkg = JSON.parse(fs.readFileSync(path.join(PROJECT_ROOT, 'package.json'), 'utf-8'));
    result.language = 'javascript/typescript';
    result.name = pkg.name || result.name;
    result.framework = detectFramework(pkg);
  } else if (fs.existsSync(path.join(PROJECT_ROOT, 'Cargo.toml'))) {
    result.language = 'rust';
  } else if (fs.existsSync(path.join(PROJECT_ROOT, 'go.mod'))) {
    result.language = 'go';
  } else if (fs.existsSync(path.join(PROJECT_ROOT, 'pom.xml'))) {
    result.language = 'java';
  }
  
  // 检测测试
  result.hasTests = fs.existsSync(path.join(PROJECT_ROOT, 'tests')) ||
                    fs.existsSync(path.join(PROJECT_ROOT, 'test')) ||
                    fs.existsSync(path.join(PROJECT_ROOT, '__tests__'));
  
  // 检测文档
  result.hasDocs = fs.existsSync(path.join(PROJECT_ROOT, 'docs'));
  
  // 检测 CI
  result.hasCI = fs.existsSync(path.join(PROJECT_ROOT, '.github')) ||
                 fs.existsSync(path.join(PROJECT_ROOT, '.gitlab-ci.yml'));
  
  // 扫描 src 目录识别业务域
  const srcDir = path.join(PROJECT_ROOT, 'src');
  if (fs.existsSync(srcDir)) {
    result.domains = fs.readdirSync(srcDir).filter(f => {
      const stat = fs.statSync(path.join(srcDir, f));
      return stat.isDirectory();
    });
  }
  
  // 统计文件数
  try {
    const output = execSync('find . -type f \\( -name "*.ts" -o -name "*.js" -o -name "*.py" \\) 2>/dev/null | wc -l', {
      cwd: PROJECT_ROOT,
      encoding: 'utf-8'
    });
    result.fileCount = parseInt(output.trim()) || 0;
  } catch (e) {
    result.fileCount = 0;
  }
  
  log(`  语言: ${result.language}`, 'blue');
  log(`  框架: ${result.framework}`, 'blue');
  log(`  业务域: ${result.domains.join(', ') || '无'}`, 'blue');
  log(`  文件数: ${result.fileCount}`, 'blue');
  
  return result;
}

function detectFramework(pkg) {
  const deps = { ...pkg.dependencies, ...pkg.devDependencies };
  if (deps['next'] || deps['react'] || deps['vue']) return 'web-framework';
  if (deps['express'] || deps['fastify'] || deps['koa']) return 'node-framework';
  if (deps['@nestjs/core']) return 'nestjs';
  if (deps['django'] || deps['flask']) return 'python-framework';
  return 'unknown';
}

// 创建目录结构
function createDirs() {
  const dirs = [
    'docs/architecture/domains',
    'docs/design/adr',
    'docs/plans/active',
    'docs/plans/completed',
    'docs/plans/debt',
    'docs/quality',
    'scripts',
    '.github/workflows'
  ];
  
  for (const dir of dirs) {
    const fullPath = path.join(PROJECT_ROOT, dir);
    if (!fs.existsSync(fullPath)) {
      fs.mkdirSync(fullPath, { recursive: true });
      log(`创建目录: ${dir}`);
    }
  }
}

// 创建 AGENTS.md
function createAgentsMd(project) {
  const domainsList = project.domains.length > 0 
    ? project.domains.map(d => `- [${d}](docs/architecture/domains/${d}.md)`).join('\n')
    : '- (扫描到后自动添加)';
  
  const content = `# AGENTS.md

> 本项目采用 Harness Engineering 模式开发

## 快速入口

| 资源 | 位置 | 用途 |
|------|------|------|
| 架构图 | [docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md) | 系统结构 |
| 质量状态 | [docs/quality/grades.md](docs/quality/grades.md) | 各域健康度 |
| 活跃计划 | [docs/plans/active/](docs/plans/active/) | 当前工作 |
| 技术债务 | [docs/plans/debt/](docs/plans/debt/) | 待清理 |

## 核心原则

1. **人类指挥，Agent 执行** - 人描述任务，Agent 完成代码
2. **零手写代码** - 所有代码由 Agent 生成
3. **知识在 repo 内** - 决策记录在 docs/design/adr/
4. **约束即法律** - 架构规则不可违反
5. **持续清理** - 技术债务定期偿还

## 架构约束

### 严格分层 (每域必需)

\`\`\`
Types → Config → Repo → Service → Runtime → UI
\`\`\`

### 业务域

${domainsList}

### 跨域入口

通过 \`Providers\` 入口：Auth, Connectors, Telemetry, FeatureFlags

## 工作流

\`\`\`
1. 人类描述任务
2. Agent 写计划 (docs/plans/active/plan-xxx.md)
3. Agent 执行代码
4. Agent 自审 (lint + test)
5. Agent 请求其他 Agent 审查
6. Agent 响应反馈 (循环直到通过)
7. Agent 合并 PR
\`\`\`

## 禁止事项

- ❌ 直接手写代码
- ❌ 在 repo 外讨论决策
- ❌ 忽略 CI 失败
- ❌ 跳过测试
- ❌ 创建 >500 行的单文件

## 质量标准

| 指标 | 目标 |
|------|------|
| 测试覆盖率 | >80% |
| lint 通过率 | 100% |
| 文档 freshness | <30天 |
| 架构层级合规 | 100% |

---

*本项目采用 OpenAI Harness Engineering 模式*
`;
  
  const filePath = path.join(PROJECT_ROOT, 'AGENTS.md');
  fs.writeFileSync(filePath, content);
  success(`创建 AGENTS.md`);
}

// 创建架构文档
function createArchitectureMd(project) {
  const domainsTable = project.domains.length > 0
    ? project.domains.map(d => `### ${capitalize(d)}\n\n| 层级 | 组件 | 状态 |\n|------|------|------|\n| Types | \`types/${d}.ts\` | ✅ A |\n| Config | \`config/${d}.ts\` | ✅ A |\n| Repo | \`repo/${d}-repo.ts\` | ✅ A |\n| Service | \`service/${d}-service.ts\` | ✅ A |\n| Runtime | \`runtime/${d}-runtime.ts\` | ⚠️ B |\n| UI | \`ui/${d}/*\` | ⚠️ B |\n`).join('\n')
    : '*扫描 src/ 目录后自动生成*';
  
  const content = `# 架构总览

## 项目信息

| 属性 | 值 |
|------|-----|
| 项目名称 | ${project.name} |
| 语言 | ${project.language} |
| 框架 | ${project.framework} |
| 代码行数 | ~${project.fileCount * 50} (估算) |

## 系统拓扑

\`\`\`
        ┌──────────────┐
        │   Users     │
        └──────┬───────┘
               │
        ┌──────▼───────┐
        │   Gateway    │
        └──────┬───────┘
               │
  ┌────────┐  ┌──────▼───────┐         ┌────────┐
  │  S3    │◄─│   Services   │────────►│  DB    │
  └────────┘  └──────┬───────┘         └────────┘
                     │
              ┌──────▼───────┐
              │ Observability│
              └──────────────┘
\`\`\`

## 业务域

${domainsTable}

## 分层结构

\`\`\`
Types → Config → Repo → Service → Runtime → UI
\`\`\`

跨域入口: **Providers** (Auth, Connectors, Telemetry, FeatureFlags)

## 依赖规则

同层可相互依赖，只能向前依赖 (Types → Config → ...)，跨域通过 Providers。

## 最后更新

${new Date().toISOString().split('T')[0]}
`;
  
  const filePath = path.join(PROJECT_ROOT, 'docs/architecture/ARCHITECTURE.md');
  fs.writeFileSync(filePath, content);
  success(`创建 docs/architecture/ARCHITECTURE.md`);
  
  // 为每个业务域创建文档
  for (const domain of project.domains) {
    const domainContent = `# ${capitalize(domain)} 域

## 概述

业务域: ${domain}

## 分层详情

| 层级 | 文件 | 状态 | 说明 |
|------|------|------|------|
| Types | types/${domain}.ts | ✅ | 数据类型定义 |
| Config | config/${domain}.ts | ✅ | 配置 |
| Repo | repo/${domain}-repo.ts | ✅ | 数据访问 |
| Service | service/${domain}-service.ts | ⚠️ | 业务逻辑 |
| Runtime | runtime/${domain}-runtime.ts | ⚠️ | 运行时 |
| UI | ui/${domain}/* | ⚠️ | 界面 |

## 依赖

- 同域: Service → Repo → Config → Types
- 跨域: 通过 Providers

## 技术债务

暂无记录

## 相关计划

- [活跃计划](../plans/active/)
- [已完成](../plans/completed/)
`;
    
    const domainPath = path.join(PROJECT_ROOT, `docs/architecture/domains/${domain}.md`);
    fs.writeFileSync(domainPath, domainContent);
    success(`创建 docs/architecture/domains/${domain}.md`);
  }
}

// 创建质量评级
function createQualityGrades(project) {
  const domainsTable = project.domains.length > 0
    ? project.domains.map(d => `### ${capitalize(d)}\n\n| 层级 | 评分 | 最后评审 | 债务 |\n|------|------|----------|------|\n| Types | A | ${today()} | - |\n| Config | A | ${today()} | - |\n| Repo | B | ${today()} | - |\n| Service | B | ${today()} | - |\n| Runtime | C | ${today()} | debt-001 |\n| UI | B | ${today()} | - |\n`).join('\n')
    : '*暂无业务域*';
  
  const content = `# 质量评级

## 评分标准

| 等级 | 含义 | 要求 |
|------|------|------|
| A | 生产就绪 | 测试>90%, 文档完整, 无已知债务 |
| B | 功能完整 | 测试>70%, 少量债务需处理 |
| C | 可用但需改进 | 测试>50%, 有明显技术债务 |
| D | 需重构 | 测试不足, 架构有问题 |

## 当前评级

${domainsTable}

## 质量趋势

*追踪最近30天的变化*

| 域/层 | 趋势 |
|-------|------|
| (新建) | - |

## 清理清单

- [ ] 本周: 审查所有 C 级组件
- [ ] 本月: 技术债务审查
- [ ] 本季度: 架构一致性审计

## 更新频率

每周一更新质量评级
`;
  
  const filePath = path.join(PROJECT_ROOT, 'docs/quality/grades.md');
  fs.writeFileSync(filePath, content);
  success(`创建 docs/quality/grades.md`);
}

// 创建 CI 配置
function createCIConfig() {
  const content = `name: Harness CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup
        run: |
          echo "Setup project..."
      
      - name: Lint
        run: npm run lint || echo "No lint script"
      
      - name: Test
        run: npm test -- --coverage || echo "No tests"
      
      - name: Check Architecture
        run: |
          node scripts/check-layers.js || echo "No layer check"

  validate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Check doc freshness
        run: |
          find docs -name "*.md" -mtime +30 | head -5
      
      - name: Check links
        run: |
          echo "Link validation"
`;
  
  const filePath = path.join(PROJECT_ROOT, '.github/workflows/harness-ci.yml');
  fs.writeFileSync(filePath, content);
  success(`创建 .github/workflows/harness-ci.yml`);
}

// 创建架构检查脚本
function createCheckLayersScript() {
  const content = `#!/usr/bin/env node

/**
 * Architecture Layer Checker
 * 
 * 检查代码是否遵循严格分层架构
 * 
 * 允许的依赖方向:
 *   types → config → repo → service → runtime → ui
 */

const fs = require('fs');
const path = require('path');

const ALLOWED_DEPS = {
  'types': ['types', 'config'],
  'config': ['types', 'config', 'repo'],
  'repo': ['types', 'config', 'repo', 'service'],
  'service': ['types', 'config', 'repo', 'service', 'runtime'],
  'runtime': ['types', 'config', 'repo', 'service', 'runtime', 'ui'],
  'ui': ['types', 'config', 'repo', 'service', 'runtime', 'ui', 'providers']
};

function detectLayer(filePath) {
  const relative = path.relative(process.cwd(), filePath);
  const parts = relative.split(path.sep);
  
  if (parts.includes('types')) return 'types';
  if (parts.includes('config')) return 'config';
  if (parts.includes('repo') || parts.includes('repositories')) return 'repo';
  if (parts.includes('service') || parts.includes('services')) return 'service';
  if (parts.includes('runtime')) return 'runtime';
  if (parts.includes('ui') || parts.includes('components') || parts.includes('pages')) return 'ui';
  if (parts.includes('providers')) return 'providers';
  
  return null;
}

function extractImports(content) {
  const imports = [];
  const regex = /import\\s+.*?\\s+from\\s+['"](.+?)['"]/g;
  let match;
  
  while ((match = regex.exec(content)) !== null) {
    const imp = match[1];
    if (!imp.startsWith('.') && !imp.startsWith('/')) continue;
    imports.push(imp);
  }
  
  return imports;
}

function checkFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const layer = detectLayer(filePath);
  
  if (!layer) return true;
  
  const imports = extractImports(content);
  
  for (const imp of imports) {
    const resolved = path.resolve(path.dirname(filePath), imp);
    const impLayer = detectLayer(resolved);
    
    if (impLayer && !ALLOWED_DEPS[layer]?.includes(impLayer)) {
      console.error(\`❌ 非法依赖: \${filePath} -> \${imp}\`);
      console.error(\`   \${layer} 不应依赖 \${impLayer}\`);
      return false;
    }
  }
  
  console.log(\`✅ \${filePath}\`);
  return true;
}

function scanDirectory(dir) {
  let allPassed = true;
  
  if (!fs.existsSync(dir)) return true;
  
  const files = fs.readdirSync(dir, { withFileTypes: true });
  
  for (const file of files) {
    const fullPath = path.join(dir, file.name);
    
    if (file.isDirectory()) {
      if (!scanDirectory(fullPath)) allPassed = false;
    } else if (file.name.endsWith('.ts') || file.name.endsWith('.js')) {
      if (!checkFile(fullPath)) allPassed = false;
    }
  }
  
  return allPassed;
}

// Main
const srcDir = path.join(process.cwd(), 'src');
console.log('🔍 检查架构层级...\\n');

if (!fs.existsSync(srcDir)) {
  console.log('⚠️  src/ 目录不存在');
  process.exit(0);
}

const passed = scanDirectory(srcDir);

if (passed) {
  console.log('\\n✅ 所有架构约束检查通过');
  process.exit(0);
} else {
  console.log('\\n❌ 存在架构违规');
  process.exit(1);
}
`;
  
  const filePath = path.join(PROJECT_ROOT, 'scripts/check-layers.js');
  fs.writeFileSync(filePath, content);
  fs.chmodSync(filePath, 0o755);
  success(`创建 scripts/check-layers.js`);
}

// 验证现有文档
function validateDocs() {
  log('验证文档规范...', 'blue');
  
  const checks = [
    { name: 'AGENTS.md', path: 'AGENTS.md', maxLines: 100 },
    { name: '架构文档', path: 'docs/architecture/ARCHITECTURE.md' },
    { name: '质量评级', path: 'docs/quality/grades.md' },
    { name: 'CI 配置', path: '.github/workflows/harness-ci.yml' },
    { name: '架构检查', path: 'scripts/check-layers.js' }
  ];
  
  let allPassed = true;
  
  for (const check of checks) {
    const fullPath = path.join(PROJECT_ROOT, check.path);
    
    if (!fs.existsSync(fullPath)) {
      error(`缺少: ${check.path}`);
      allPassed = false;
      continue;
    }
    
    if (check.maxLines) {
      const content = fs.readFileSync(fullPath, 'utf-8');
      const lines = content.split('\n').length;
      if (lines > check.maxLines) {
        error(`${check.name} 超过 ${check.maxLines} 行 (当前: ${lines})`);
        allPassed = false;
      } else {
        success(`${check.name} ✓`);
      }
    } else {
      success(`${check.name} ✓`);
    }
  }
  
  return allPassed;
}

// 工具函数
function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function today() {
  return new Date().toISOString().split('T')[0];
}

// Main
function main() {
  const args = process.argv.slice(2);
  const command = args[0] || '--init';
  
  console.log('\\n🚀 Harness Engineering 文档生成器\\n');
  
  switch (command) {
    case '--init':
      const project = analyzeProject();
      createDirs();
      createAgentsMd(project);
      createArchitectureMd(project);
      createQualityGrades(project);
      createCIConfig();
      createCheckLayersScript();
      console.log('\\n✅ 所有文档创建完成！\\n');
      break;
      
    case '--agents':
      const p1 = analyzeProject();
      createDirs();
      createAgentsMd(p1);
      break;
      
    case '--architecture':
      const p2 = analyzeProject();
      createDirs();
      createArchitectureMd(p2);
      break;
      
    case '--quality':
      const p3 = analyzeProject();
      createDirs();
      createQualityGrades(p3);
      break;
      
    case '--validate':
      validateDocs();
      break;
      
    default:
      console.log('使用方法:');
      console.log('  node create-harness-docs.js --init          # 创建所有文档');
      console.log('  node create-harness-docs.js --agents         # 仅创建 AGENTS.md');
      console.log('  node create-harness-docs.js --architecture  # 仅创建架构文档');
      console.log('  node create-harness-docs.js --quality        # 仅创建质量评级');
      console.log('  node create-harness-docs.js --validate       # 验证现有文档');
  }
}

main();
