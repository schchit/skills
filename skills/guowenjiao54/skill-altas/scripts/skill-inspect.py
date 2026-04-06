# -*- coding: utf-8 -*-
"""
技能审视 (Skill Inspect) - 分析所有已安装技能的状态
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# 设置输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

WORKSPACE = Path(os.environ.get('OPENCLAW_WORKSPACE', 'C:/Users/23210/.openclaw/workspace'))
SKILLS_DIR = WORKSPACE / 'skills'
SCENES_PATH = WORKSPACE / 'skills' / 'skill-atlas' / 'config' / 'scenes.json'
MEMORY_CLI = WORKSPACE / 'scripts' / 'memory.py'


def load_scenes():
    with open(SCENES_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_dir_size(path):
    """获取目录大小 KB"""
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = Path(dirpath) / f
            total += fp.stat().st_size
    return total / 1024


def read_skill_md(skill_path):
    """读取 SKILL.md，处理编码"""
    md_path = skill_path / 'SKILL.md'
    if not md_path.exists():
        return None
    for enc in ('utf-8', 'utf-8-sig', 'gbk', 'gb2312'):
        try:
            return md_path.read_text(encoding=enc)
        except:
            continue
    return None


def parse_frontmatter(content):
    """解析 YAML frontmatter"""
    if not content or not content.startswith('---'):
        return {}
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}
    lines = parts[1].strip().split('\n')
    meta = {}
    for line in lines:
        if ':' in line:
            key, val = line.split(':', 1)
            meta[key.strip()] = val.strip()
    return meta


def check_dependencies(content):
    """检查依赖状态"""
    deps = {'bins': [], 'env': [], 'skills': []}
    issues = []

    if not content:
        return deps, ['SKILL.md 不存在或无法读取']

    import re
    # 只在代码块外的 frontmatter 或说明文字里找 binary 引用
    # 过滤掉已知是 skill 内置文件的脚本名
    internal_scripts = {
        'extract_passages.py', 'security-audit.sh', 'extract-skill.sh',
        'activator.sh', 'error-detector.sh', 'skill-inspect.py',
        'daily-skill-sync.ps1', 'add_bgm.sh', 'generate_music.sh',
        'generate_long_video.sh', 'generate_video.sh', 'generate_template_video.sh',
        'generate_image.sh', 'check_environment.sh', 'media_tools.sh',
        'generate_voice.sh', 'memory-remember.ps1', 'memory.py',
    }
    # 实际需要检查的外部 binary
    external_bins = {'node', 'python', 'npx', 'npm', 'git', 'sqlite3'}

    for ext in external_bins:
        if re.search(rf'\b{re.escape(ext)}\b', content, re.IGNORECASE):
            # Windows: check both .exe and .ps1
            if sys.platform == 'win32':
                found = any(
                    Path(p, f'{ext}.exe').exists() or Path(p, f'{ext}.ps1').exists()
                    for p in os.environ.get('PATH', '').split(os.pathsep)
                )
            else:
                found = any(
                    Path(p, ext).exists()
                    for p in os.environ.get('PATH', '').split(os.pathsep)
                )
            if not found:
                issues.append(f'缺少 binary: {ext}')

    # 检查 API key 环境变量
    envs = re.findall(r'\$([A-Z_][A-Z0-9_]+)_API[_KEY]*', content)
    envs += re.findall(r'`\$([A-Z_][A-Z0-9_]+)`', content)
    envs = list(set(envs) - {'OPENAI', 'ANTHROPIC', 'GOOGLE', 'XAI', 'MINIMAX', 'TAVILY'})
    for e in envs:
        if not os.environ.get(e) and not os.environ.get(e.lower()):
            issues.append(f'缺少环境变量: {e}')

    return deps, issues

    for b in bins:
        found = bool(Path(os.environ.get('SYSTEMROOT', 'C:/Windows'), f'{b}.exe').exists()) or \
                any(Path(p).exists() and (Path(p) / b).exists() for p in os.environ.get('PATH', '').split(os.pathsep))
        if not found:
            issues.append(f'缺少 binary: {b}')

    # env vars in skill docs
    envs = re.findall(r'\$([A-Z_][A-Z0-9_]+)_API[_KEY]*', content)
    envs += re.findall(r'`\$([A-Z_][A-Z0-9_]+)`', content)
    envs = list(set(envs))
    for e in envs:
        if e not in ('OPENAI', 'ANTHROPIC', 'GOOGLE', 'XAI', 'MINIMAX'):
            val = os.environ.get(e) or os.environ.get(e.lower())
            if not val:
                issues.append(f'缺少环境变量: {e}')

    return deps, issues


def inspect_skill(skill_name, skill_path, config):
    """审视单个技能"""
    info = {
        'name': skill_name,
        'path': str(skill_path),
        'version': None,
        'description': None,
        'size_kb': 0,
        'status': 'unknown',
        'issues': [],
        'layers': [],
        'custom_modified': False,
        'files': [],
        'version_remote': None,
        'version_local': None,
        'update_available': False,
    }

    # 读取 SKILL.md
    content = read_skill_md(skill_path)
    if content:
        meta = parse_frontmatter(content)
        info['version'] = meta.get('version')
        info['description'] = meta.get('description', '')[:60]
        deps, dep_issues = check_dependencies(content)
        info['issues'].extend(dep_issues)

    # 体积
    info['size_kb'] = round(get_dir_size(skill_path), 1)

    # 文件清单
    for f in skill_path.rglob('*'):
        if f.is_file() and not f.name.startswith('.'):
            info['files'].append(str(f.relative_to(skill_path)))

    # 判断层级
    core = config.get('core_skills', [])
    resident = config.get('resident_skills', [])
    scenes_skills = []
    for cat in config.get('categories', {}).values():
        scenes_skills.extend(cat.get('skills', []))
    custom_cats = config.get('custom_categories', {})
    custom_skills = []
    for cat in custom_cats.values():
        custom_skills.extend(cat.get('skills', []))

    if skill_name in core:
        info['layers'].append('核心')
    if skill_name in resident:
        info['layers'].append('常驻')
    if skill_name in scenes_skills:
        info['layers'].append('场景')
    if skill_name in custom_skills:
        info['layers'].append('自定义分类')

    # 检查是否本地修改
    origin_file = skill_path / '.clawhub' / 'origin.json'
    if origin_file.exists():
        try:
            origin = json.loads(origin_file.read_text(encoding='utf-8'))
            installed_ver = origin.get('installedVersion')
            info['version_local'] = installed_ver
            info['custom_modified'] = True
        except:
            pass

    # 版本
    if not info['version']:
        info['version'] = info['version_local'] or '未知'

    # 状态判断
    critical_issues = [i for i in info['issues'] if '缺少' in i and 'binary' in i]
    if critical_issues:
        info['status'] = 'unavailable' if 'python' in ' '.join(critical_issues) or 'API' in ' '.join(critical_issues) else 'partially_available'
    elif info['issues']:
        info['status'] = 'partially_available'
    elif info['custom_modified']:
        info['status'] = 'custom'
    else:
        info['status'] = 'normal'

    return info


def run_inspect():
    """执行审视"""
    config = load_scenes()
    skills = []

    for d in SKILLS_DIR.iterdir():
        if d.is_dir() and (d / 'SKILL.md').exists():
            skills.append(inspect_skill(d.name, d, config))

    skills.sort(key=lambda x: x['name'])

    # 分类输出
    normal = [s for s in skills if s['status'] == 'normal']
    partial = [s for s in skills if s['status'] == 'partially_available']
    unavailable = [s for s in skills if s['status'] == 'unavailable']
    custom = [s for s in skills if s['status'] == 'custom']

    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    core_count = len([s for s in skills if '核心' in s['layers']])
    resident_count = len([s for s in skills if '常驻' in s['layers']])

    print(f"\n🔍 技能审视报告")
    print(f"═══════════════════════════════════════════════════════")
    print(f"审视时间: {now}   共 {len(skills)} 个技能 ·核心 {core_count} 个 ·常驻 {resident_count} 个")
    print(f"───────────────────────────────────────────────────────")

    if normal:
        print(f"\n✅ 正常 ({len(normal)} 个)")
        for s in normal:
            ver = s['version'] or '未知'
            layers = '/'.join(s['layers']) if s['layers'] else '独立'
            print(f"  • {s['name']} · v{ver} · {s['size_kb']}KB · {layers}")

    if custom:
        print(f"\n🔵 自定义修改 ({len(custom)} 个)")
        for s in custom:
            layers = '/'.join(s['layers']) if s['layers'] else '独立'
            print(f"  • {s['name']} · v{s['version']} · {s['size_kb']}KB · {layers}")
            for iss in s['issues']:
                print(f"    🔵 {iss}")

    if partial:
        print(f"\n⚠️  部分可用 ({len(partial)} 个)")
        for s in partial:
            print(f"  • {s['name']} · v{s['version'] or '?'} · {s['size_kb']}KB")
            for iss in s['issues']:
                print(f"    ⚠️  {iss}")

    if unavailable:
        print(f"\n🔴 不可用 ({len(unavailable)} 个)")
        for s in unavailable:
            print(f"  • {s['name']} · v{s['version'] or '?'} · {s['size_kb']}KB")
            for iss in s['issues']:
                print(f"    🔴 {iss}")

    # 汇总建议
    action_items = []
    for s in skills:
        if s['status'] == 'unavailable':
            action_items.append(f"  🔴 {s['name']}: 缺少关键依赖，建议卸载或修复")
        elif s['status'] == 'partially_available':
            action_items.append(f"  ⚠️  {s['name']}: {'; '.join(s['issues'][:2])}")
        elif s['custom_modified']:
            action_items.append(f"  🔵 {s['name']}: 本地有修改，更新时会保留本地变更")

    if action_items:
        print(f"\n───────────────────────────────────────────────────────")
        print(f"📌 建议操作")
        for item in action_items[:8]:
            print(item)

    print(f"\n═══════════════════════════════════════════════════════\n")
    return skills


if __name__ == '__main__':
    run_inspect()
