const { exec } = require('child_process');

function shellQuote(value) {
  return `'${String(value).replace(/'/g, `'\\''`)}'`;
}

function run(command) {
  return new Promise((resolve) => {
    exec(command, (error, stdout, stderr) => {
      resolve({ ok: !error, stdout, stderr, error });
    });
  });
}

async function checkBinary(name) {
  const result = await run(`which ${shellQuote(name)}`);
  const error = (result.stderr || result.error?.message || '').trim();

  if (!result.ok) {
    return { name, found: false, error: error || `binary not found: ${name}` };
  }

  return { name, found: true };
}

async function checkBrew(formula) {
  const result = await run(`brew list ${shellQuote(formula)} --versions`);
  const output = (result.stdout || '').trim();
  const error = (result.stderr || result.error?.message || '').trim();

  if (!result.ok || !output) {
    return { name: formula, found: false, error: error || `formula not installed: ${formula}` };
  }

  const parts = output.split(/\s+/);
  const version = parts.length > 1 ? parts.slice(1).join(' ') : undefined;
  return { name: formula, found: true, version };
}

async function checkNpm(pkg) {
  const result = await run(`npm list -g ${shellQuote(pkg)} --depth=0`);
  const output = `${result.stdout || ''}\n${result.stderr || ''}`;
  const error = (result.stderr || result.error?.message || '').trim();

  if (!result.ok) {
    return { name: pkg, found: false, error: error || `npm package not installed: ${pkg}` };
  }

  const match = output.match(new RegExp(`${pkg.replace(/[.*+?^${}()|[\\]\\]/g, '\\$&')}@(\\S+)`));
  return { name: pkg, found: true, version: match ? match[1] : undefined };
}

function parsePipVersion(output) {
  const match = output.match(/^Version:\s*(.+)$/mi);
  return match ? match[1].trim() : undefined;
}

async function checkPip(pkg) {
  let result = await run(`pip show ${shellQuote(pkg)}`);
  if (!result.ok) {
    result = await run(`pip3 show ${shellQuote(pkg)}`);
  }

  const output = (result.stdout || '').trim();
  const error = (result.stderr || result.error?.message || '').trim();

  if (!result.ok || !output) {
    return { name: pkg, found: false, error: error || `pip package not installed: ${pkg}` };
  }

  return { name: pkg, found: true, version: parsePipVersion(output) };
}

module.exports = {
  checkBinary,
  checkBrew,
  checkNpm,
  checkPip,
};
