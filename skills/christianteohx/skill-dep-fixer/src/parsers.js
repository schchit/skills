const fs = require('fs');
const path = require('path');
const os = require('os');
const yaml = require('js-yaml');

function getSkillMarkdownPaths() {
  const home = os.homedir();
  const roots = [
    path.join(home, '.openclaw', 'skills'),
    path.join(home, '.openclaw', 'workspace', 'skills'),
  ];

  const results = [];

  for (const root of roots) {
    if (!fs.existsSync(root)) continue;

    const entries = fs.readdirSync(root, { withFileTypes: true });
    for (const entry of entries) {
      if (!entry.isDirectory()) continue;
      const skillPath = path.join(root, entry.name, 'SKILL.md');
      if (fs.existsSync(skillPath)) {
        results.push(skillPath);
      }
    }
  }

  return results;
}

function parseFrontmatter(content) {
  const text = content || '';
  const match = text.match(/^---\n([\s\S]*?)\n---\n?/);
  if (!match) return {};

  try {
    return yaml.load(match[1]) || {};
  } catch {
    return {};
  }
}

function toArray(value) {
  return Array.isArray(value) ? value : [];
}

function normalizeInstallEntry(item) {
  if (!item || typeof item !== 'object') return null;

  return {
    id: typeof item.id === 'string' ? item.id : undefined,
    kind: typeof item.kind === 'string' ? item.kind : undefined,
    formula: typeof item.formula === 'string' ? item.formula : undefined,
    version: typeof item.version === 'string' ? item.version : undefined,
    bins: toArray(item.bins).filter((v) => typeof v === 'string'),
  };
}

function parseSkillFile(skillFilePath) {
  const content = fs.readFileSync(skillFilePath, 'utf8');
  const frontmatter = parseFrontmatter(content);

  const openclaw = frontmatter?.metadata?.openclaw || {};
  const requiredBins = toArray(openclaw?.requires?.bins).filter((v) => typeof v === 'string');
  const install = toArray(openclaw?.install)
    .map(normalizeInstallEntry)
    .filter(Boolean);

  return {
    skillName: path.basename(path.dirname(skillFilePath)),
    skillPath: skillFilePath,
    requires: { bins: requiredBins },
    install,
  };
}

function parseSkills() {
  return getSkillMarkdownPaths().map(parseSkillFile);
}

module.exports = {
  getSkillMarkdownPaths,
  parseFrontmatter,
  parseSkillFile,
  parseSkills,
};
