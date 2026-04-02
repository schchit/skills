#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_FILE = ROOT / '.task-state.json'


def load_state():
    if not STATE_FILE.exists():
        return {'tasks': {}}
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception as e:
        raise RuntimeError(f'failed to read state file: {e}')


def build_message(item):
    note = item.get('note') or '继续沿当前链路推进'
    goal = item.get('goal') or '继续推进当前长任务'
    state = item.get('state') or 'analyzing'
    next_check = item.get('next_check') or '待更新'
    lines = [
        f'长任务进度提醒：{item.get("task")}',
        f'当前状态：{state}',
        f'正在看：{note}',
        f'刚确认：{goal}',
        f'下一步：继续沿当前链路推进，并在 {next_check} 前给出新的阶段结论。',
    ]
    return '\n'.join(lines)


def main():
    p = argparse.ArgumentParser(description='Build a foreground progress update message for a tracked long-run task')
    p.add_argument('--task', required=True)
    args = p.parse_args()

    data = load_state()
    item = data.get('tasks', {}).get(args.task)
    if not item:
        print(f'task not found: {args.task}', file=sys.stderr)
        return 1

    payload = {
        'task': item.get('task'),
        'session_label': item.get('session_label') or item.get('session'),
        'origin_session_key': item.get('origin_session_key'),
        'state': item.get('state'),
        'message': build_message(item),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
