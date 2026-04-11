#!/usr/bin/env node

const { spawnSync } = require('node:child_process');

// 所需版本（与 config.json 中 dependencies.npm 保持一致）
const REQUIRED_VERSION = '1.0.2';

const action = process.argv[2];
const args = process.argv.slice(3);

if (!action) {
  showHelp();
  process.exit(0);
}

const run = (cmd, cmdArgs) => {
  const result = spawnSync(cmd, cmdArgs, { stdio: 'inherit' });
  if (result.error) {
    console.error(JSON.stringify({ success: false, error: result.error.message }));
    process.exit(1);
  }
  process.exit(result.status ?? 1);
};

/**
 * 使用 npx 执行 wechat-pub 命令
 */
const runWechatPub = (pubArgs) => {
  // 使用 npx 强制指定版本执行，自动从 registry 拉取（如有缓存则使用缓存）
  run('npx', ['--yes', `wechat-md-publisher@^${REQUIRED_VERSION}`, ...pubArgs]);
};

function showHelp() {
  console.log(`WeChat Publisher - 使用说明

用法:
  publish <file> [theme]     - 发布文章
  draft <file> [theme]       - 创建草稿
  list-drafts                - 列出草稿
  list-published             - 列出已发布文章
  themes                     - 列出可用主题
  help                       - 显示帮助

示例:
  publish article.md orangeheart
  draft article.md lapis
`);
}

switch (action) {
  case 'publish': {
    const file = args[0];
    const theme = args[1] || 'default';
    if (!file) {
      console.error('错误: 请提供文件路径');
      console.error('用法: publish <file> [theme]');
      process.exit(1);
    }
    console.log('正在发布文章...');
    runWechatPub(['publish', 'create', '--file', file, '--theme', theme]);
    break;
  }

  case 'draft': {
    const file = args[0];
    const theme = args[1] || 'default';
    if (!file) {
      console.error('错误: 请提供文件路径');
      console.error('用法: draft <file> [theme]');
      process.exit(1);
    }
    console.log('正在创建草稿...');
    runWechatPub(['draft', 'create', '--file', file, '--theme', theme]);
    break;
  }

  case 'wrapper': {
    // 透传所有参数给 wrapper 命令
    runWechatPub(['wrapper', ...args]);
    break;
  }

  case 'list-drafts':
    console.log('草稿列表:');
    runWechatPub(['draft', 'list']);
    break;

  case 'list-published':
    console.log('已发布文章:');
    runWechatPub(['publish', 'list']);
    break;

  case 'themes':
    console.log('可用主题:');
    runWechatPub(['theme', 'list']);
    break;

  case 'help':
  default:
    showHelp();
    break;
}
