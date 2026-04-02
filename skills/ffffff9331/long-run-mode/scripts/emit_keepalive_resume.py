#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEEPALIVE = ROOT / 'scripts' / 'keepalive_tick.py'


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
    p = argparse.ArgumentParser(description='Emit keepalive resume event for a long-run task when idle too long')
    p.add_argument('--task', required=True)
    p.add_argument('--idle-seconds', type=int, default=60)
    args = p.parse_args()

    _, tick = run_json([sys.executable, str(KEEPALIVE), '--task', args.task, '--idle-seconds', str(args.idle_seconds)])
    if not tick.get('should_resume'):
        out = {
            'event_count': 0,
            'events': [],
            'reason': tick.get('reason', 'still_active'),
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    session_key = tick.get('origin_session_key')
    if not session_key:
        raise RuntimeError('missing origin_session_key; cannot emit portable keepalive event')

    event = {
        'kind': 'keepalive-resume',
        'delivery': 'session',
        'sessionKey': session_key,
        'task': tick.get('task'),
        'state': tick.get('state'),
        'message': tick.get('resume_message'),
        'reason': tick.get('reason'),
        'idle_for_seconds': tick.get('idle_for_seconds'),
        'last_activity_source': tick.get('last_activity_source'),
        'onSuccess': {
            'script': 'task_state.py mark-resume',
            'task': tick.get('task'),
            'reason': tick.get('reason') or 'idle_timeout',
            'note': '保活续跑已触发，继续沿上次锚点推进',
        }
    }
    out = {
        'event_count': 1,
        'events': [event],
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
