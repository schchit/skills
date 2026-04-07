#!/usr/bin/env node

const { parseArgs } = require('util');
const fs = require('fs/promises');
const os = require('os');
const path = require('path');
const { createInterface } = require('readline/promises');
const { parseSkills } = require('./src/parsers');
const { checkBinary, checkBrew, checkNpm, checkPip } = require('./src/checkers');
const { installBrew, installNpm, installPip } = require('./src/installer');
const { textReport, jsonReport, discordReport, summarize } = require('./src/reporter');

function usage() {
  return [
    'Usage: skill-dep-fixer [options]',
    '',
    'Options:',
    '  --dry-run       Show what would be installed',
    '  --fix           Install missing dependencies',
    '  --skill <name>  Check only one skill',
    '  --init <name>   Create a new skill template',
    '  --name <name>   Skill display name for --init',
    '  --description   Skill description for --init',
    '  --json          Output JSON report',
    '  --report        Output Discord-formatted report',
    '  --help          Show this help text',
  ].join('\n');
}

function toDisplayName(skillName) {
  return skillName
    .split(/[-_\s]+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');
}

async function ask(question) {
  const rl = createInterface({ input: process.stdin, output: process.stdout });
  try {
    return (await rl.question(question)).trim();
  } finally {
    rl.close();
  }
}

async function resolveInitFields(skillName, values) {
  let displayName = values.name ? String(values.name).trim() : '';
  let description = values.description ? String(values.description).trim() : '';

  if (!displayName) {
    const defaultName = toDisplayName(skillName);
    const input = await ask(`Skill display name [${defaultName}]: `);
    displayName = input || defaultName;
  }

  if (!description) {
    description = await ask('Skill description: ');
  }

  return { displayName, description };
}

function buildSkillTemplate(skillName, displayName, description) {
  return `---
name: ${skillName}
description: "${description.replace(/"/g, '\\"')}"
metadata:
  openclaw:
    emoji: "🛠️"
    requires:
      bins: []
    install:
      # Add dependencies below, e.g.:
      # - id: my-binary
      #   kind: brew
      #   formula: my-binary
      #   bins: [my-binary]
      #   label: "Install my-binary"
---

# ${displayName}

Brief description of what this skill does.

## Usage

Describe when and how to use this skill.

## Commands

List any commands or tools this skill provides.

## Notes

Any additional context or caveats.
`;
}

async function initSkill(skillName, values) {
  const baseDir = path.join(os.homedir(), '.openclaw', 'workspace', 'skills');
  const skillDir = path.join(baseDir, skillName);
  const skillFile = path.join(skillDir, 'SKILL.md');

  try {
    await fs.access(skillFile);
    process.stderr.write(`Skill already exists: ~/.openclaw/workspace/skills/${skillName}/SKILL.md\n`);
    return 1;
  } catch {
    // File does not exist, continue.
  }

  const { displayName, description } = await resolveInitFields(skillName, values);
  await fs.mkdir(skillDir, { recursive: true });
  await fs.writeFile(skillFile, buildSkillTemplate(skillName, displayName, description), 'utf8');
  process.stdout.write(`Created skill at ~/.openclaw/workspace/skills/${skillName}/SKILL.md\n`);
  return 0;
}

function installForDirective(directive) {
  if (directive.kind === 'brew' && directive.formula) return installBrew(directive.formula);
  if (directive.kind === 'npm' && directive.id) return installNpm(directive.id);
  if (directive.kind === 'pip' && directive.id) return installPip(directive.id);
  return null;
}

async function checkDirective(directive) {
  if (directive.kind === 'brew' && directive.formula) {
    return checkBrew(directive.formula);
  }
  if (directive.kind === 'npm' && directive.id) {
    return checkNpm(directive.id);
  }
  if (directive.kind === 'pip' && directive.id) {
    return checkPip(directive.id);
  }
  return null;
}

async function analyzeSkill(skill, opts) {
  const checks = [];
  const mismatches = [];

  for (const bin of skill.requires.bins || []) {
    const result = await checkBinary(bin);
    checks.push({ type: 'bin', name: bin, label: `bin:${bin}`, ...result });
  }

  for (const directive of skill.install || []) {
    const depResult = await checkDirective(directive);
    if (depResult) {
      const depLabel = directive.kind === 'brew' ? `brew:${directive.formula}` : `${directive.kind}:${directive.id}`;
      checks.push({ type: directive.kind, label: depLabel, via: directive, ...depResult });

      if (directive.version && depResult.found && depResult.version !== directive.version) {
        mismatches.push({
          name: depResult.name,
          declared: directive.version,
          installed: depResult.version,
        });
      }
    }

    for (const bin of directive.bins || []) {
      const existing = checks.find((c) => c.type === 'bin' && c.name === bin);
      if (!existing) {
        const result = await checkBinary(bin);
        checks.push({ type: 'bin', name: bin, label: `bin:${bin}`, via: directive, ...result });
      }
    }
  }

  const missing = checks.filter((c) => !c.found);
  const actions = [];
  let error = null;

  if (missing.length > 0) {
    for (const directive of skill.install || []) {
      const bins = directive.bins || [];
      const depName = directive.kind === 'brew' ? directive.formula : directive.id;
      const depMissing = depName ? missing.some((m) => m.name === depName) : false;
      const binMissing = bins.some((bin) => missing.some((m) => m.name === bin));
      const needed = depMissing || binMissing;
      if (!needed) continue;

      const installResult = installForDirective(directive);
      if (!installResult) continue;

      if (opts.fix) {
        actions.push({ command: `${installResult.name} via ${directive.kind}`, ok: installResult.status === 'installed' });
        if (installResult.status === 'failed' && !error) {
          error = installResult.message;
        }
      } else {
        actions.push({ command: `${installResult.name} via ${directive.kind}`, ok: null, dryRun: true });
      }
    }
  }

  let status = 'ok';
  if (missing.length > 0 && !opts.fix) status = 'skipped';
  if (missing.length > 0 && opts.fix) {
    status = actions.length > 0 && actions.every((a) => a.ok) ? 'fixed' : 'failed';
    if (actions.length === 0) status = 'failed';
  }
  if (mismatches.length > 0 && status !== 'failed') status = 'mismatch';

  const dependencies = checks
    .filter((c) => c.type !== 'bin')
    .map((c) => ({
      name: c.name,
      type: c.type,
      found: c.found,
      version: c.version,
      declared: c.via?.version,
    }));

  return {
    name: skill.skillName,
    skillPath: skill.skillPath,
    status,
    missing,
    mismatches,
    dependencies,
    actions,
    error,
  };
}

async function runCli(argv = process.argv.slice(2)) {
  const { values } = parseArgs({
    args: argv,
    options: {
      'dry-run': { type: 'boolean', default: false },
      fix: { type: 'boolean', default: false },
      skill: { type: 'string' },
      init: { type: 'string' },
      name: { type: 'string' },
      description: { type: 'string' },
      json: { type: 'boolean', default: false },
      report: { type: 'boolean', default: false },
      help: { type: 'boolean', default: false },
    },
    allowPositionals: false,
  });

  if (values.help) {
    process.stdout.write(`${usage()}\n`);
    return 0;
  }

  if (values.init) {
    return initSkill(String(values.init).trim(), values);
  }

  const opts = {
    fix: Boolean(values.fix),
  };

  const allSkills = parseSkills();
  const selectedSkills = values.skill
    ? allSkills.filter((s) => s.skillName === values.skill)
    : allSkills;

  if (values.skill && selectedSkills.length === 0) {
    process.stderr.write(`Skill not found: ${values.skill}\n`);
    return 1;
  }

  const skills = [];
  for (const skill of selectedSkills) {
    skills.push(await analyzeSkill(skill, opts));
  }

  const results = { skills };
  results.summary = summarize(results);

  if (values.json) {
    process.stdout.write(`${JSON.stringify(jsonReport(results), null, 2)}\n`);
  } else if (values.report) {
    process.stdout.write(`${discordReport(results)}\n`);
  } else {
    process.stdout.write(`${textReport(results)}\n`);
    if (values['dry-run']) {
      const commands = skills.flatMap((s) => s.actions).map((a) => a.command);
      if (commands.length > 0) {
        process.stdout.write('\nPlanned install commands:\n');
        for (const command of commands) process.stdout.write(`- ${command}\n`);
      }
    }
  }

  return results.summary.failed > 0 ? 1 : 0;
}

if (require.main === module) {
  runCli().then((code) => {
    process.exitCode = code;
  });
}

module.exports = {
  usage,
  runCli,
};
