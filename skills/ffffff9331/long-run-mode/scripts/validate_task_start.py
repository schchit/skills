#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_FILE = ROOT / '.task-state.json'
ACTIVE_STATES = {'analyzing', 'executing', 'waiting'}


def load_state():
    if not STATE_FILE.exists():
        return {'tasks': {}, 'active_long_runs_by_session': {}}
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception as e:
        raise RuntimeError(f'failed to read state file: {e}')


def main():
    p = argparse.ArgumentParser(description='Validate that a long-run task was actually bound to the intended real session')
    p.add_argument('--task', required=True)
    p.add_argument('--expect-session-key')
    p.add_argument('--expect-state', action='append', dest='expect_states')
    args = p.parse_args()

    data = load_state()
    tasks = data.get('tasks', {}) or {}
    locks = data.get('active_long_runs_by_session', {}) or {}
    item = tasks.get(args.task)
    if not item:
        print(json.dumps({
            'ok': False,
            'error': 'task_not_found',
            'task': args.task,
            'message': '任务不存在，不能视为已启动。',
        }, ensure_ascii=False, indent=2))
        return 1

    state = item.get('state')
    origin_session_key = item.get('origin_session_key')
    expected_states = args.expect_states or sorted(ACTIVE_STATES)
    errors = []

    if state not in expected_states:
        errors.append(f'state_mismatch:{state}')
    if state in ACTIVE_STATES and not origin_session_key:
        errors.append('missing_origin_session_key')
    if args.expect_session_key and origin_session_key != args.expect_session_key:
        errors.append('origin_session_key_mismatch')
    if state in ACTIVE_STATES and origin_session_key:
        locked_task = locks.get(origin_session_key)
        if locked_task != args.task:
            errors.append('session_lock_mismatch')

    session_label = item.get('session_label') or item.get('session')
    out = {
        'ok': not errors,
        'task': args.task,
        'state': state,
        'session': session_label,
        'session_label': session_label,
        'origin_session_key': origin_session_key,
        'lock_owner': locks.get(origin_session_key) if origin_session_key else None,
        'expected_states': expected_states,
        'errors': errors,
        'message': '启动校验通过：任务已绑定到真实目标会话。' if not errors else '启动校验失败：不能宣称长任务已在目标会话启动成功。',
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == '__main__':
    raise SystemExit(main())
