#!/usr/bin/env node

const { spawnSync } = require('node:child_process');

// 所需版本（与 config.json 中 dependencies.npm 保持一致）
const REQUIRED_VERSION = '1.0.0';

const command = process.argv[2];
const args = process.argv.slice(3);

if (!command) {
  console.error(JSON.stringify({ success: false, error: 'Missing command. Use: rewrite or check-quota' }));
  process.exit(1);
}

const run = (cmd, cmdArgs) => {
  const result = spawnSync(cmd, cmdArgs, { stdio: 'inherit' });
  if (result.error) {
    console.error(JSON.stringify({ success: false, error: result.error.message }));
    process.exit(1);
  }
  process.exit(result.status ?? 1);
};

switch (command) {
  case 'rewrite':
    // 使用 npx 强制指定版本执行，自动从 registry 拉取（如有缓存则使用缓存）
    run('npx', ['--yes', `markdown-ai-rewriter@^${REQUIRED_VERSION}`, 'rewrite', ...args]);
    break;
  case 'check-quota':
    console.log(JSON.stringify({
      success: true,
      message: 'check-quota is not provided by markdown-ai-rewriter CLI in this version. Please monitor quota in your provider console.'
    }));
    break;
  default:
    console.error(JSON.stringify({ success: false, error: `Unknown command: ${command}` }));
    process.exit(1);
}
