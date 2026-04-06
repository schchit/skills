#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
skill_atlas.py - Skill Atlas CLI 管理工具
用法:
    python skill_atlas.py status
    python skill_atlas.py search <query>
    python skill_atlas.py install <slug>
    python skill_atlas.py update <slug>
    python skill_atlas.py update-all
    python skill_atlas.py vet <slug>
    python skill_atlas.py inspect
    python skill_atlas.py cat-create <name> [description]
    python skill_atlas.py cat-delete <name>
    python skill_atlas.py cat-add <cat> <slug>
    python skill_atlas.py cat-remove <cat> <slug>
    python skill_atlas.py cat-enable <name>
    python skill_atlas.py cat-disable <name>
    python skill_atlas.py cat-list
    python skill_atlas.py cat-detail <name>
    python skill_atlas.py resident-add <slug>
    python skill_atlas.py resident-remove <slug>
    python skill_atlas.py daily-report
"""
import sys
import io
import os
import re
import json
import subprocess
from pathlib import Path
from datetime import datetime

# UTF-8 output
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

WORKSPACE = Path(os.environ.get('OPENCLAW_WORKSPACE', 'C:/Users/23210/.openclaw/workspace'))
SKILLS_DIR = WORKSPACE / 'skills'
SCRIPTS_DIR = WORKSPACE / 'scripts'
CONFIG_DIR = WORKSPACE / 'skills' / 'skill-atlas' / 'config'
SCENES_PATH = CONFIG_DIR / 'scenes.json'
DAILY_DIR = CONFIG_DIR / 'daily'
VETTER_SCRIPT = WORKSPACE / 'scripts' / 'skill-vetter.py'
INSPECT_SCRIPT = Path(__file__).parent / 'skill-inspect.py'


def run_pwsh(cmd, timeout=60):
    """Run a command via PowerShell"""
    result = subprocess.run(
        ['powershell', '-Command', cmd],
        capture_output=True, text=True, timeout=timeout,
        cwd=str(WORKSPACE)
    )
    return result


def load_scenes():
    with open(SCENES_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_scenes(data):
    with open(SCENES_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.utime(SCENES_PATH, None)


def get_installed_skills():
    result = run_pwsh(f'clawhub --workdir "{WORKSPACE}" list')
    skills = {}
    if result.returncode == 0:
        for line in result.stdout.strip().split('\n'):
            m = re.match(r'^(\S+)\s+([\d.]+)', line.strip())
            if m:
                skills[m.group(1)] = m.group(2)
    return skills


# ─── status ─────────────────────────────────────────────────

def cmd_status():
    scenes = load_scenes()
    installed = get_installed_skills()
    custom_cats = scenes.get('custom_categories', {})
    resident = scenes.get('resident_skills', [])
    core = scenes.get('core_skills', [])

    all_dirs = [d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and (d / 'SKILL.md').exists()]

    print('\n[Skill Atlas] Status')
    print('=' * 48)

    print(f'\n## Core ({len(core)})')
    for s in core:
        print(f'  {s:42s}  v{installed.get(s, "?")}')

    print(f'\n## Resident ({len(resident)})')
    for s in resident:
        print(f'  {s:42s}  v{installed.get(s, "?")}')

    if custom_cats:
        print(f'\n## Custom Categories ({len(custom_cats)})')
        for cat_name, cat_data in custom_cats.items():
            enabled = 'ON ' if cat_data.get('enabled') else 'OFF'
            skills = cat_data.get('skills', [])
            print(f'  [{enabled}] {cat_name}  ({len(skills)} skills)')
            for sk in skills:
                print(f'         - {sk}')

    independent = [s for s in all_dirs
                  if s not in core and s not in resident
                  and s not in [cs for cat in custom_cats.values() for cs in cat.get('skills', [])]]
    if independent:
        print(f'\n## Other ({len(independent)})')
        for s in independent:
            print(f'  {s:42s}  v{installed.get(s, "?")}')

    print(f'\nTotal: {len(all_dirs)} skills installed')
    print()


# ─── search ───────────────────────────────────────────────

def cmd_search(query):
    print(f'\n[Skill Atlas] Searching: {query}')
    print('=' * 48)
    result = run_pwsh(f'clawhub search {query}')
    if result.returncode == 0:
        print(result.stdout)
    else:
        print(f'[-] Search failed: {result.stderr[:200]}')
    print()


# ─── vet ───────────────────────────────────────────────────

def cmd_vet(slug):
    print(f'\n[Skill Atlas] Vetting: {slug}')
    print('=' * 48)
    result = subprocess.run(
        [sys.executable, str(VETTER_SCRIPT), 'inspect', slug],
        capture_output=True, text=True, timeout=60,
        encoding='utf-8', errors='replace'
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr[:200])
    return result.returncode


# ─── install ───────────────────────────────────────────────

def cmd_install(slug, force=False):
    print(f'\n[Skill Atlas] Installing: {slug}')
    print('=' * 48)

    print('[1/3] Security vet...')
    vet = subprocess.run(
        [sys.executable, str(VETTER_SCRIPT), 'inspect', slug],
        capture_output=True, text=True, timeout=60,
        encoding='utf-8', errors='replace'
    )
    print(vet.stdout)
    ec = vet.returncode
    if ec == 2:
        print('[!!] BLOCKED - extreme risk detected.')
        return 2
    elif ec == 1 and not force:
        print('[!!] HIGH risk - approval required. Use --force to bypass.')
        return 1

    print('[2/3] Installing via clawhub...')
    result = run_pwsh(f'clawhub --workdir "{WORKSPACE}" install {slug}')
    if result.returncode == 0:
        print('[OK] Installed.')
        if result.stdout:
            print(result.stdout[:300])
    else:
        print(f'[-] Install failed: {result.stderr[:200]}')
        return 1

    print('[3/3] Post-install vet...')
    vet2 = subprocess.run(
        [sys.executable, str(VETTER_SCRIPT), 'inspect', slug],
        capture_output=True, text=True, timeout=60,
        encoding='utf-8', errors='replace'
    )
    print(vet2.stdout)

    print(f'\n[OK] {slug} installed.')
    return 0


# ─── update ────────────────────────────────────────────────

def cmd_update(slug):
    print(f'\n[Skill Atlas] Updating: {slug}')
    print('=' * 48)

    print('[1/3] Security vet...')
    vet = subprocess.run(
        [sys.executable, str(VETTER_SCRIPT), 'inspect', slug],
        capture_output=True, text=True, timeout=60,
        encoding='utf-8', errors='replace'
    )
    print(vet.stdout)
    ec = vet.returncode
    if ec == 2:
        print('[!!] BLOCKED - extreme risk.')
        return 2
    elif ec == 1:
        print('[!!] HIGH risk - approval required.')
        return 1

    print('[2/3] Updating via clawhub...')
    result = run_pwsh(f'clawhub --workdir "{WORKSPACE}" update {slug}')
    if result.returncode == 0:
        print('[OK] Updated.')
        if result.stdout:
            print(result.stdout[:300])
    else:
        print(f'[-] Update failed: {result.stderr[:200]}')
        return 1

    print('[3/3] Post-update vet...')
    vet2 = subprocess.run(
        [sys.executable, str(VETTER_SCRIPT), 'inspect', slug],
        capture_output=True, text=True, timeout=60,
        encoding='utf-8', errors='replace'
    )
    print(vet2.stdout)
    return 0


def cmd_update_all():
    print('\n[Skill Atlas] Update All')
    print('=' * 48)
    installed = get_installed_skills()
    scenes = load_scenes()
    skip = set(scenes.get('core_skills', [])) | set(scenes.get('resident_skills', []))
    for slug, ver in installed.items():
        if slug in skip:
            continue
        print(f'\n-- {slug} (v{ver}) --')
        cmd_update(slug)
    print('\n[OK] Batch update done.')


# ─── inspect ──────────────────────────────────────────────

def cmd_inspect():
    print('\n[Skill Atlas] Running skill inspection...')
    result = subprocess.run(
        [sys.executable, str(INSPECT_SCRIPT)],
        capture_output=True, text=True, timeout=30,
        encoding='utf-8', errors='replace'
    )
    print(result.stdout)


# ─── category commands ─────────────────────────────────────

def cmd_cat_create(name, description=''):
    scenes = load_scenes()
    cats = scenes.setdefault('custom_categories', {})
    if name in cats:
        print(f'[-] Category already exists: {name}')
        return 1
    cats[name] = {
        'description': description or name,
        'enabled': False,
        'skills': [],
        'created_at': datetime.now().strftime('%Y-%m-%d'),
        'last_vetted_at': datetime.now().strftime('%Y-%m-%d')
    }
    save_scenes(scenes)
    print(f'[OK] Created: {name}')
    return 0


def cmd_cat_delete(name):
    scenes = load_scenes()
    cats = scenes.get('custom_categories', {})
    if name not in cats:
        print(f'[-] Not found: {name}')
        return 1
    n = len(cats[name].get('skills', []))
    del cats[name]
    save_scenes(scenes)
    print(f'[OK] Deleted: {name} ({n} skills preserved)')
    return 0


def cmd_cat_add(cat_name, slug):
    scenes = load_scenes()
    cats = scenes.get('custom_categories', {})
    if cat_name not in cats:
        print(f'[-] Category not found: {cat_name}')
        return 1
    if slug in cats[cat_name].get('skills', []):
        print(f'[-] {slug} already in {cat_name}')
        return 1

    print(f'[1/2] Vetting {slug}...')
    vet = subprocess.run(
        [sys.executable, str(VETTER_SCRIPT), 'inspect', slug],
        capture_output=True, text=True, timeout=60,
        encoding='utf-8', errors='replace'
    )
    print(vet.stdout)
    ec = vet.returncode
    if ec == 2:
        print('[!!] BLOCKED - extreme risk.')
        return 2
    elif ec == 1:
        print('[!!] HIGH risk - approval required first.')
        return 1

    cats[cat_name].setdefault('skills', []).append(slug)
    cats[cat_name]['last_vetted_at'] = datetime.now().strftime('%Y-%m-%d')
    save_scenes(scenes)
    print(f'[OK] Added {slug} to {cat_name}')
    return 0


def cmd_cat_remove(cat_name, slug):
    scenes = load_scenes()
    cats = scenes.get('custom_categories', {})
    if cat_name not in cats:
        print(f'[-] Not found: {cat_name}')
        return 1
    skills = cats[cat_name].get('skills', [])
    if slug not in skills:
        print(f'[-] {slug} not in {cat_name}')
        return 1
    skills.remove(slug)
    cats[cat_name]['skills'] = skills
    save_scenes(scenes)
    print(f'[OK] Removed {slug} from {cat_name}')
    return 0


def cmd_cat_enable(name):
    scenes = load_scenes()
    cats = scenes.get('custom_categories', {})
    if name not in cats:
        print(f'[-] Not found: {name}')
        return 1
    cats[name]['enabled'] = True
    resident = set(scenes.get('resident_skills', []))
    new_skills = set(cats[name].get('skills', []))
    resident.update(new_skills)
    scenes['resident_skills'] = list(resident)
    save_scenes(scenes)
    print(f'[OK] Enabled: {name} ({len(new_skills)} skills -> resident)')
    return 0


def cmd_cat_disable(name):
    scenes = load_scenes()
    cats = scenes.get('custom_categories', {})
    if name not in cats:
        print(f'[-] Not found: {name}')
        return 1
    cats[name]['enabled'] = False
    resident = set(scenes.get('resident_skills', []))
    resident -= set(cats[name].get('skills', []))
    scenes['resident_skills'] = list(resident)
    save_scenes(scenes)
    print(f'[OK] Disabled: {name}')
    return 0


def cmd_cat_list():
    scenes = load_scenes()
    cats = scenes.get('custom_categories', {})
    print('\n[Skill Atlas] Custom Categories')
    print('=' * 48)
    if not cats:
        print('  (no custom categories)')
    for name, data in cats.items():
        enabled = 'ON ' if data.get('enabled') else 'OFF'
        skills = data.get('skills', [])
        desc = data.get('description', '')
        print(f'  [{enabled}] {name}')
        if desc and desc != name:
            print(f'       {desc}')
        print(f'       {len(skills)} skills: {", ".join(skills) if skills else "(empty)"}')
    print()


def cmd_cat_detail(name):
    scenes = load_scenes()
    cats = scenes.get('custom_categories', {})
    if name not in cats:
        print(f'[-] Not found: {name}')
        return 1
    data = cats[name]
    print(f'\n[Skill Atlas] Category: {name}')
    print('=' * 48)
    print(f'Description:   {data.get("description", "")}')
    print(f'Enabled:       {data.get("enabled", False)}')
    print(f'Created:      {data.get("created_at", "?")}')
    print(f'Last vetted:   {data.get("last_vetted_at", "?")}')
    print(f'\nSkills ({len(data.get("skills", []))}):')
    for s in data.get('skills', []):
        print(f'  - {s}')
    print()


# ─── resident ──────────────────────────────────────────────

def cmd_resident_add(slug):
    scenes = load_scenes()
    resident = set(scenes.get('resident_skills', []))
    resident.add(slug)
    scenes['resident_skills'] = sorted(resident)
    save_scenes(scenes)
    print(f'[OK] Added to resident: {slug}')
    return 0


def cmd_resident_remove(slug):
    scenes = load_scenes()
    resident = set(scenes.get('resident_skills', []))
    resident.discard(slug)
    scenes['resident_skills'] = sorted(resident)
    save_scenes(scenes)
    print(f'[OK] Removed from resident: {slug}')
    return 0


# ─── daily report ──────────────────────────────────────────

def cmd_daily_report():
    today = datetime.now().strftime('%Y-%m-%d')
    daily_file = DAILY_DIR / f'daily_{today}.md'
    update_file = DAILY_DIR / f'updates_{today}.md'

    if daily_file.exists():
        print(f'\n[Daily Report: {today}]')
        print('=' * 48)
        print(daily_file.read_text(encoding='utf-8'))
    else:
        print(f'[-] No report for today.')
        latest = sorted(DAILY_DIR.glob('daily_*.md'), key=lambda p: p.stat().st_mtime, reverse=True)
        if latest:
            print(f'\nLatest: {latest[0].name}')
            print(latest[0].read_text(encoding='utf-8')[:600])
        else:
            print('(no reports found)')
    return 0


# ─── main ─────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    dispatcher = {
        'status':            (cmd_status, 0),
        'search':           (lambda: cmd_search(' '.join(args)) if args else None, None),
        'vet':              (lambda: cmd_vet(args[0]) if args else None, None),
        'inspect':          (cmd_inspect, 0),
        'install':          (lambda: cmd_install(args[0], force='--force' in args) if args else None, None),
        'update':           (lambda: cmd_update(args[0]) if args else None, None),
        'update-all':       (cmd_update_all, 0),
        'cat-create':       (lambda: cmd_cat_create(args[0], args[1] if len(args) > 1 else '') if args else None, None),
        'cat-delete':       (lambda: cmd_cat_delete(args[0]) if args else None, None),
        'cat-add':          (lambda: cmd_cat_add(args[0], args[1]) if len(args) >= 2 else None, None),
        'cat-remove':       (lambda: cmd_cat_remove(args[0], args[1]) if len(args) >= 2 else None, None),
        'cat-enable':       (lambda: cmd_cat_enable(args[0]) if args else None, None),
        'cat-disable':      (lambda: cmd_cat_disable(args[0]) if args else None, None),
        'cat-list':         (cmd_cat_list, 0),
        'cat-detail':       (lambda: cmd_cat_detail(args[0]) if args else None, None),
        'resident-add':     (lambda: cmd_resident_add(args[0]) if args else None, None),
        'resident-remove':  (lambda: cmd_resident_remove(args[0]) if args else None, None),
        'daily-report':     (cmd_daily_report, 0),
    }

    if cmd not in dispatcher:
        print(__doc__)
        sys.exit(1)

    fn, fallback_ec = dispatcher[cmd]
    if fn is None:
        print(__doc__)
        sys.exit(1)
    result = fn()
    sys.exit(result if result is not None else (fallback_ec if fallback_ec is not None else 0))


if __name__ == '__main__':
    main()
