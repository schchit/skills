#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EMIT = ROOT / 'scripts' / 'emit_foreground_due.py'


def run_json(cmd):
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode not in (0, 1):
        raise RuntimeError(proc.stderr.strip() or f'command failed with code {proc.returncode}')
    try:
        data = json.loads(proc.stdout)
    except Exception as e:
        raise RuntimeError(f'failed to parse JSON: {e}')
    return proc.returncode, data


def main():
    p = argparse.ArgumentParser(description='Build dispatcher plan for foreground due events; actual sessions_send must be done by OpenClaw tool layer')
    p.add_argument('--unknown-cooldown-minutes', type=int, default=2)
    args = p.parse_args()

    _, emitted = run_json([sys.executable, str(EMIT), '--unknown-cooldown-minutes', str(args.unknown_cooldown_minutes)])
    dispatches = []
    for event in emitted.get('events', []):
        dispatches.append({
            'tool': 'sessions_send',
            'sessionKey': event.get('sessionKey'),
            'message': event.get('message'),
            'task': event.get('task'),
            'delivery': event.get('delivery'),
            'delivery_id': event.get('delivery_id'),
            'message_hash': event.get('message_hash'),
            'session_label': event.get('session_label'),
            'origin_session_key': event.get('sessionKey'),
            'onSuccess': event.get('onSuccess'),
            'onUnknown': event.get('onUnknown'),
            'onError': event.get('onError'),
        })
    out = {
        'dispatch_count': len(dispatches),
        'dispatches': dispatches,
        'skipped_unknown_count': emitted.get('skipped_unknown_count', 0),
        'skipped_unknown': emitted.get('skipped_unknown', []),
        'note': '此脚本只生成 dispatcher 计划；真正 sessions_send 需由 OpenClaw agent/tool 层执行。timeout 应记为 unknown，不要直接当 failed 重发。',
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if not dispatches else 1


if __name__ == '__main__':
    raise SystemExit(main())
