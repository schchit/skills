#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECOVER = ROOT / 'scripts' / 'recover_due_tasks.py'


def load_report(stale_minutes: int):
    cmd = [sys.executable, str(RECOVER), '--json', '--stale-minutes', str(stale_minutes)]
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode not in (0, 1):
        raise RuntimeError(proc.stderr.strip() or f'recover_due_tasks.py failed with code {proc.returncode}')
    return json.loads(proc.stdout)


def build_message(item):
    recovery = item['recovery']
    lines = [
        f"长任务{'进度' if item.get('kind') == 'progress' else '回收'}提醒：{item['task']}",
        f"当前状态：{item['state']}",
        f"所属边界：{item['boundary']}",
        f"负责会话：{item['session']}",
        f"触发原因：{item['reason']}",
        f"任务目标：{item['goal']}",
        f"当前备注：{item['note']}",
        f"建议动作：{recovery['kind']}",
        f"建议发往：{recovery['suggested_session']}",
        '建议消息：',
        recovery['suggested_message'],
    ]
    return '\n'.join(lines)


def main():
    p = argparse.ArgumentParser(description='Emit human-readable recovery messages for overdue tasks')
    p.add_argument('--stale-minutes', type=int, default=10)
    p.add_argument('--json', action='store_true')
    args = p.parse_args()

    report = load_report(args.stale_minutes)
    items = report.get('items', [])

    if args.json:
        missing = [item.get('task') for item in items if not item.get('origin_session_key')]
        if missing:
            raise RuntimeError(f'missing origin_session_key for task(s): {", ".join(missing)}')
        payload = {
            'due_count': report.get('due_count', 0),
            'progress_count': report.get('progress_count', 0),
            'messages': [
                {
                    'task': item['task'],
                    'session': item['session'],
                    'origin_session_key': item['origin_session_key'],
                    'kind': item.get('kind'),
                    'message': build_message(item),
                }
                for item in items
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload['due_count'] == 0 and payload.get('progress_count', 0) == 0 else 1

    if not items:
        print('emit: no recovery messages to send')
        return 0

    for idx, item in enumerate(items, start=1):
        if idx > 1:
            print('\n' + '=' * 60 + '\n')
        print(build_message(item))

    return 1


if __name__ == '__main__':
    raise SystemExit(main())
