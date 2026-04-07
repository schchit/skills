#!/usr/bin/env node

const path = require('path');

let parsers;
let checkers;
let installer;

try {
  parsers = require('./src/parsers');
} catch {
  parsers = require('./parsers');
}

try {
  checkers = require('./src/checkers');
} catch {
  checkers = require('./checkers');
}

try {
  installer = require('./src/installer');
} catch {
  installer = require('./installer');
}

function parseArgs(argv) {
  return {
    fix: argv.includes('--fix'),
    dryRun: argv.includes('--dry-run'),
    manifest: (() => {
      const i = argv.findIndex((a) => a === '--manifest');
      return i >= 0 ? argv[i + 1] : undefined;
    })(),
  };
}

function normalizeDepsFromInstall(install = []) {
  const deps = { brew: [], npm: [], pip: [] };

  for (const item of install) {
    if (!item || typeof item !== 'object') continue;

    if (item.kind === 'brew') {
      const name = item.formula || item.id;
      if (name) deps.brew.push(name);
      continue;
    }

    if (item.kind === 'npm' && item.id) deps.npm.push(item.id);
    if (item.kind === 'pip' && item.id) deps.pip.push(item.id);
  }

  return deps;
}

function getDeps(skill) {
  const raw = skill?.dependencies;
  if (raw && typeof raw === 'object') {
    return {
      brew: Array.isArray(raw.brew) ? raw.brew : [],
      npm: Array.isArray(raw.npm) ? raw.npm : [],
      pip: Array.isArray(raw.pip) ? raw.pip : [],
    };
  }

  return normalizeDepsFromInstall(skill?.install || []);
}

function loadSkills(args) {
  if (typeof parsers.parseManifest === 'function') {
    return parsers.parseManifest(args.manifest);
  }
  if (typeof parsers.parseSkills === 'function') {
    return parsers.parseSkills();
  }
  return [];
}

function checkOne(type, name) {
  if (type === 'brew') return checkers.checkBrew(name);
  if (type === 'npm') return checkers.checkNpm(name);
  if (type === 'pip') return checkers.checkPip(name);
  return { name, found: false, error: `Unsupported dependency type: ${type}` };
}

function installOne(type, name) {
  if (type === 'brew') return installer.installBrew(name);
  if (type === 'npm') return installer.installNpm(name);
  if (type === 'pip') return installer.installPip(name);
  return { name, status: 'skipped', message: `Unsupported dependency type: ${type}` };
}

function processDependency({ type, name, fix, dryRun }) {
  const check = checkOne(type, name);

  if (check.found) {
    return { type, check, action: { name, status: 'skipped', message: 'Already installed' } };
  }

  if (!fix) {
    return { type, check, action: { name, status: 'skipped', message: 'Missing dependency (run with --fix to install)' } };
  }

  if (dryRun) {
    return { type, check, action: { name, status: 'skipped', message: `Would install missing ${type} dependency: ${name}` } };
  }

  return { type, check, action: installOne(type, name) };
}

function run() {
  const args = parseArgs(process.argv.slice(2));
  const skills = loadSkills(args);
  const results = [];

  for (const skill of skills) {
    const skillName = skill.name || skill.id || skill.skillName || 'unknown-skill';
    const deps = getDeps(skill);
    const entries = [];

    for (const name of deps.brew) entries.push(processDependency({ type: 'brew', name, fix: args.fix, dryRun: args.dryRun }));
    for (const name of deps.npm) entries.push(processDependency({ type: 'npm', name, fix: args.fix, dryRun: args.dryRun }));
    for (const name of deps.pip) entries.push(processDependency({ type: 'pip', name, fix: args.fix, dryRun: args.dryRun }));

    results.push({
      skill: skillName,
      path: skill.path || skill.skillPath ? path.resolve(skill.path || skill.skillPath) : undefined,
      dependencies: entries,
    });
  }

  process.stdout.write(`${JSON.stringify({
    manifest: args.manifest || null,
    fix: args.fix,
    dryRun: args.dryRun,
    skillCount: skills.length,
    results,
  }, null, 2)}\n`);
}

if (require.main === module) {
  run();
}

module.exports = { run };
