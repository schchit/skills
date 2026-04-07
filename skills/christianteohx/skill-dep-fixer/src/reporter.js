const chalk = require('chalk');

function summarize(results) {
  const summary = {
    total: results.skills.length,
    fixed: 0,
    failed: 0,
    skipped: 0,
  };

  for (const skill of results.skills) {
    if (skill.status === 'fixed' || skill.status === 'ok') summary.fixed += 1;
    else if (skill.status === 'failed') summary.failed += 1;
    else summary.skipped += 1;
  }

  return summary;
}

function iconForStatus(status) {
  if (status === 'ok') return '✅';
  if (status === 'fixed') return '🔧';
  if (status === 'failed') return '❌';
  if (status === 'mismatch') return '⚠️';
  return '⚠️';
}

function colorStatus(status) {
  if (status === 'ok') return chalk.green(status);
  if (status === 'fixed') return chalk.cyan(status);
  if (status === 'failed') return chalk.red(status);
  return chalk.yellow(status);
}

function textReport(results) {
  const lines = [];
  lines.push(chalk.bold('Skill Dependency Report'));
  lines.push('');
  lines.push('Skill'.padEnd(32) + 'Status'.padEnd(12) + 'Details');
  lines.push('-'.repeat(100));

  for (const skill of results.skills) {
    const missing = (skill.missing || []).map((m) => m.label).join(', ') || 'none';
    const left = `${iconForStatus(skill.status)} ${skill.name}`.padEnd(32);
    const status = colorStatus(skill.status).padEnd(12);
    lines.push(`${left}${status}missing: ${missing}`);

    const mismatchNames = new Set((skill.mismatches || []).map((m) => m.name));
    for (const dep of skill.dependencies || []) {
      const depStatus = mismatchNames.has(dep.name) ? 'mismatch' : dep.found ? 'ok' : 'missing';
      const declared = dep.declared ? ` (declared: ${dep.declared})` : '';
      const version = dep.version || 'unknown';
      const depIcon = depStatus === 'ok' ? '✅' : depStatus === 'mismatch' ? '⚠️' : '❌';
      lines.push(`   ${depIcon} ${dep.name} ${version}${declared} :: ${depStatus}`);
    }

    if (skill.error) lines.push(`   ${chalk.red('error:')} ${skill.error}`);
  }

  const summary = results.summary || summarize(results);
  lines.push('');
  lines.push(chalk.bold('Summary'));
  lines.push(
    `total=${summary.total}  fixed=${chalk.cyan(summary.fixed)}  failed=${chalk.red(summary.failed)}  skipped=${chalk.yellow(summary.skipped)}`,
  );

  return lines.join('\n');
}

function jsonReport(results) {
  const summary = results.summary || summarize(results);
  return {
    skills: results.skills,
    summary,
  };
}

function discordReport(results) {
  const summary = results.summary || summarize(results);
  const lines = [];
  lines.push('**Skill Dependency Report**');
  lines.push('```');
  for (const skill of results.skills) {
    const missing = (skill.missing || []).map((m) => m.label).join(', ') || 'none';
    lines.push(`${iconForStatus(skill.status)} ${skill.name} :: ${skill.status} :: missing: ${missing}`);

    const mismatchNames = new Set((skill.mismatches || []).map((m) => m.name));
    for (const dep of skill.dependencies || []) {
      const depStatus = mismatchNames.has(dep.name) ? 'mismatch' : dep.found ? 'ok' : 'missing';
      const declared = dep.declared ? ` (declared: ${dep.declared})` : '';
      const version = dep.version || 'unknown';
      const depIcon = depStatus === 'ok' ? '✅' : depStatus === 'mismatch' ? '⚠️' : '❌';
      lines.push(`${depIcon} ${dep.name} ${version}${declared} :: ${depStatus}`);
    }

    if (skill.error) lines.push(`   error: ${skill.error}`);
  }
  lines.push('```');
  lines.push(
    `summary: total=${summary.total}, fixed=${summary.fixed}, failed=${summary.failed}, skipped=${summary.skipped}`,
  );
  return lines.join('\n');
}

module.exports = {
  summarize,
  textReport,
  jsonReport,
  discordReport,
};
