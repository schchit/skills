/**
 * PRD Workflow 测试套件 v4.2.5
 *
 * 运行方式：
 * node tests/test.js
 * node tests/test.js --unit
 * node tests/test.js --integration
 */

const path = require('path');
const fs = require('fs');

// 测试计数
let passed = 0;
let failed = 0;
let skipped = 0;

/**
 * 简单测试框架
 */
function test(name, fn) {
  try {
    fn();
    console.log(`  ✅ ${name}`);
    passed++;
  } catch (error) {
    console.log(`  ❌ ${name}`);
    console.log(`     Error: ${error.message}`);
    failed++;
  }
}

function skip(name, reason) {
  console.log(`  ⏭️  ${name} (${reason})`);
  skipped++;
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message || 'Assertion failed');
  }
}

function assertEqual(actual, expected, message) {
  if (actual !== expected) {
    throw new Error(message || `Expected "${expected}", got "${actual}"`);
  }
}

function assertExists(filePath, message) {
  if (!fs.existsSync(filePath)) {
    throw new Error(message || `File not found: ${filePath}`);
  }
}

// ============================================
// 单元测试
// ============================================

function runUnitTests() {
  console.log('\n📦 单元测试\n');

  // ---------- utils.js 测试 ----------
  console.log('📋 utils.js');

  test('findSkillPath 返回函数', () => {
    const utils = require('../workflows/utils.js');
    assert(typeof utils.findSkillPath === 'function');
  });

  test('getWorkspaceRoot 返回字符串', () => {
    const utils = require('../workflows/utils.js');
    const root = utils.getWorkspaceRoot();
    assert(typeof root === 'string');
    assert(root.length > 0);
  });

  test('findSkillPath 查找 prd-workflow 自身', () => {
    const utils = require('../workflows/utils.js');
    const skillPath = utils.findSkillPath('prd-workflow');
    // 可能为 null（如果不在标准位置）
    if (skillPath) {
      assert(skillPath.includes('prd-workflow'));
    }
  });

  // ---------- data_bus.js 测试 ----------
  console.log('\n📋 data_bus.js');

  test('DataBus 类存在', () => {
    const { DataBus } = require('../workflows/data_bus.js');
    assert(typeof DataBus === 'function');
  });

  test('sanitizePath 过滤危险字符', () => {
    const { DataBus } = require('../workflows/data_bus.js');
    const dataBus = new DataBus('测试需求', { userId: 'test-user' });

    // 测试路径安全化（通过构造函数已调用）
    assert(dataBus.outputDir.includes('test-user'));
  });

  // ---------- smart_router.js 测试 ----------
  console.log('\n📋 smart_router.js');

  test('SmartRouter 类存在', () => {
    const { SmartRouter } = require('../workflows/smart_router.js');
    assert(typeof SmartRouter === 'function');
  });

  test('SmartRouter 有正确的技能定义', () => {
    const { SmartRouter } = require('../workflows/smart_router.js');
    const router = new SmartRouter();

    assert(router.skills['precheck'], '应有 precheck 技能');
    assert(router.skills['interview'], '应有 interview 技能');
    assert(router.skills['prd'], '应有 prd 技能');
    assert(router.templates['full'].length === 10, 'full 模板应有 10 步');
  });

  test('SmartRouter getModule 返回模块', () => {
    const { SmartRouter } = require('../workflows/smart_router.js');
    const router = new SmartRouter();

    const precheckModule = router.getModule('precheck');
    assert(precheckModule !== null, 'precheck 模块应存在');
  });

  // ---------- data_bus_schema.js 测试 ----------
  console.log('\n📋 data_bus_schema.js');

  test('DataBusSchema 类存在', () => {
    const { DataBusSchema } = require('../workflows/data_bus_schema.js');
    assert(typeof DataBusSchema === 'function');
  });

  test('Schema 定义完整', () => {
    const { SCHEMA } = require('../workflows/data_bus_schema.js');

    assert(SCHEMA['interview'], '应有 interview schema');
    assert(SCHEMA['prd'], '应有 prd schema');
    assert(SCHEMA['interview'].required.includes('sharedUnderstanding'));
    assert(SCHEMA['interview'].required.includes('keyDecisions'));
  });

  test('Schema validate 方法工作', () => {
    const { DataBusSchema } = require('../workflows/data_bus_schema.js');
    const schema = new DataBusSchema();

    // 构造符合 schema 的完整数据
    const validData = {
      sharedUnderstanding: { summary: 'test' },
      keyDecisions: Array(12).fill(null).map((_, i) => ({
        id: `d${i}`,
        topic: 'test',
        decision: 'test'
      })),
      questions: Array(16).fill(null).map((_, i) => ({
        question: `question ${i}`,
        answer: 'answer'
      }))
    };

    const result = schema.validate('interview', validData);
    assert(result.valid === true, '有效数据应通过验证，错误: ' + (result.errors?.join(', ') || ''));
  });

  // ---------- 模块文件存在性测试 ----------
  console.log('\n📋 模块文件存在性');

  const modules = [
    'precheck_module.js',
    'interview_module.js',
    'decomposition_module.js',
    'prd_module.js',
    'review_module.js',
    'flowchart_module.js',
    'design_module.js',
    'prototype_module.js',
    'export_module.js',
    'quality_module.js'
  ];

  modules.forEach(mod => {
    test(`${mod} 存在`, () => {
      const modPath = path.join(__dirname, '../workflows/modules', mod);
      assertExists(modPath);
    });
  });

  // ---------- v3.0.0 新增模块测试 ----------
  console.log('\n📋 v3.0.0 新增模块');

  test('image_renderer.js 存在', () => {
    const rendererPath = path.join(__dirname, '../workflows/image_renderer.js');
    assertExists(rendererPath);
  });

  test('ImageRenderer 类存在', () => {
    const { ImageRenderer } = require('../workflows/image_renderer.js');
    assert(typeof ImageRenderer === 'function');
  });

  test('ImageRenderer getChromePaths 返回数组', () => {
    const { ImageRenderer } = require('../workflows/image_renderer.js');
    const renderer = new ImageRenderer({ verbose: false });
    const paths = renderer.getChromePaths();
    assert(Array.isArray(paths), '应返回数组');
    assert(paths.length > 0, '应有至少一个 Chrome 路径');
  });

  test('ai_diagram_extractor.js 存在', () => {
    const extractorPath = path.join(__dirname, '../workflows/ai_diagram_extractor.js');
    assertExists(extractorPath);
  });

  test('AIDiagramExtractor 类存在', () => {
    const { AIDiagramExtractor } = require('../workflows/ai_diagram_extractor.js');
    assert(typeof AIDiagramExtractor === 'function');
  });

  test('AIDiagramExtractor 方法完整', () => {
    const { AIDiagramExtractor } = require('../workflows/ai_diagram_extractor.js');
    const extractor = new AIDiagramExtractor();

    assert(typeof extractor.inferFlow === 'function', '应有 inferFlow 方法');
    assert(typeof extractor.flowToMermaid === 'function', '应有 flowToMermaid 方法');
    assert(typeof extractor.architectureToMermaid === 'function', '应有 architectureToMermaid 方法');
    assert(typeof extractor.generatePrototypeConfig === 'function', '应有 generatePrototypeConfig 方法');
  });

  test('PRDTemplate 版本为 3.0.0', () => {
    const { PRDTemplate } = require('../workflows/prd_template.js');
    const template = new PRDTemplate();
    assertEqual(template.version, '4.2.5');
  });
}

// ============================================
// 集成测试
// ============================================

function runIntegrationTests() {
  console.log('\n🔗 集成测试\n');

  // ---------- precheck 模块测试 ----------
  console.log('📋 precheck_module.js');

  test('precheck 返回正确的结构', async () => {
    const PrecheckModule = require('../workflows/modules/precheck_module.js');
    const precheck = new PrecheckModule();

    const result = await precheck.execute({});

    assert(result.checks !== undefined, '应有 checks');
    assert(result.summary !== undefined, '应有 summary');
    assert(typeof result.canProceed === 'boolean', '应有 canProceed');
  });

  // ---------- 流程模板测试 ----------
  console.log('\n📋 流程模板');

  test('full 模板包含 precheck', () => {
    const { SmartRouter } = require('../workflows/smart_router.js');
    const router = new SmartRouter();

    const fullTemplate = router.templates['full'];
    assert(fullTemplate[0] === 'precheck', 'full 第一步应为 precheck');
    assert(fullTemplate.length === 10, 'full 应有 10 步');
  });

  test('依赖关系正确', () => {
    const { SmartRouter } = require('../workflows/smart_router.js');
    const router = new SmartRouter();

    // interview 依赖 precheck
    assert(router.dependencies['interview'].includes('precheck'));
    // prd 依赖 decomposition
    assert(router.dependencies['prd'].includes('decomposition'));
    // quality 依赖 export
    assert(router.dependencies['quality'].includes('export'));
  });

  // ---------- 文件结构测试 ----------
  console.log('\n📋 文件结构');

  test('skills 目录存在', () => {
    const skillsPath = path.join(__dirname, '../skills');
    assertExists(skillsPath);
  });

  test('内置技能完整', () => {
    const expectedSkills = [
      'htmlPrototype',
      'mermaid-flow',
      'prd-export',
      'requirement-reviewer',
      'ui-ux-pro-max'
    ];

    expectedSkills.forEach(skill => {
      const skillPath = path.join(__dirname, '../skills', skill);
      assertExists(skillPath, `${skill} 应存在`);
    });
  });

  test('templates 目录存在', () => {
    const templatesPath = path.join(__dirname, '../templates');
    assertExists(templatesPath);
  });
}

// ============================================
// 主入口
// ============================================

function main() {
  console.log('════════════════════════════════════════════════════════');
  console.log('  PRD Workflow 测试套件 v4.2.5');
  console.log('════════════════════════════════════════════════════════');

  const args = process.argv.slice(2);

  if (args.includes('--unit')) {
    runUnitTests();
  } else if (args.includes('--integration')) {
    runIntegrationTests();
  } else {
    // 运行所有测试
    runUnitTests();
    runIntegrationTests();
  }

  console.log('\n════════════════════════════════════════════════════════');
  console.log(`  测试结果: ✅ ${passed} passed, ❌ ${failed} failed, ⏭️  ${skipped} skipped`);
  console.log('════════════════════════════════════════════════════════\n');

  // 返回退出码
  process.exit(failed > 0 ? 1 : 0);
}

main();