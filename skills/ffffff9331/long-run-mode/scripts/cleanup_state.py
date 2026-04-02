#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_FILE = ROOT / '.task-state.json'
ACTIVE_STATES = {'analyzing', 'executing', 'waiting'}


def load_state():
    if not STATE_FILE.exists():
        return {'tasks': {}, 'active_long_runs_by_session': {}}
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception:
        return {'tasks': {}, 'active_long_runs_by_session': {}}


def save_state(data):
    STATE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def normalize_task(item):
    if not isinstance(item, dict):
        return item, []
    changes = []
    session_label = item.get('session_label') or item.get('session')
    if session_label and item.get('session_label') != session_label:
        item['session_label'] = session_label
        changes.append('set_session_label')
    if session_label and item.get('session') != session_label:
        item['session'] = session_label
        changes.append('normalize_session_to_label')
    return item, changes


def main():
    p = argparse.ArgumentParser(description='Clean up long-run-mode state file and drop invalid test/stale records')
    p.add_argument('--apply', action='store_true')
    p.add_argument('--drop-task', action='append', default=[])
    p.add_argument('--drop-test-prefix', action='append', default=['回归-'])
    args = p.parse_args()

    data = load_state()
    tasks = data.get('tasks', {}) or {}
    locks = data.get('active_long_runs_by_session', {}) or {}
    report = {'normalized': [], 'dropped': [], 'lock_repairs': []}

    new_tasks = {}
    for name, item in tasks.items():
        if name in args.drop_task or any(name.startswith(prefix) for prefix in args.drop_test_prefix):
            report['dropped'].append({'task': name, 'reason': 'matched_drop_rule'})
            continue
        item, changes = normalize_task(item)
        state = item.get('state')
        origin_session_key = item.get('origin_session_key')
        if state in ACTIVE_STATES and not origin_session_key:
            report['dropped'].append({'task': name, 'reason': 'active_state_missing_origin_session_key'})
            continue
        if changes:
            report['normalized'].append({'task': name, 'changes': changes})
        new_tasks[name] = item

    new_locks = {}
    for session_key, task_name in locks.items():
        if task_name not in new_tasks:
            report['lock_repairs'].append({'session_key': session_key, 'old_task': task_name, 'action': 'drop_orphan_lock'})
            continue
        task = new_tasks[task_name]
        if task.get('origin_session_key') != session_key:
            report['lock_repairs'].append({'session_key': session_key, 'task': task_name, 'action': 'replace_with_task_origin_session_key', 'new_session_key': task.get('origin_session_key')})
            if task.get('origin_session_key'):
                new_locks[task['origin_session_key']] = task_name
            continue
        new_locks[session_key] = task_name

    for task_name, task in new_tasks.items():
        session_key = task.get('origin_session_key')
        state = task.get('state')
        if state in ACTIVE_STATES and session_key and new_locks.get(session_key) != task_name:
            new_locks[session_key] = task_name
            report['lock_repairs'].append({'session_key': session_key, 'task': task_name, 'action': 'restore_missing_lock'})

    cleaned = {'tasks': new_tasks, 'active_long_runs_by_session': new_locks}
    report['task_count_before'] = len(tasks)
    report['task_count_after'] = len(new_tasks)
    report['lock_count_before'] = len(locks)
    report['lock_count_after'] = len(new_locks)
    report['apply'] = args.apply

    if args.apply:
        save_state(cleaned)

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
