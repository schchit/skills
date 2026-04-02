#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EMIT = ROOT / 'scripts' / 'emit_recovery_message.py'


def load_messages(stale_minutes: int):
    cmd = [sys.executable, str(EMIT), '--json', '--stale-minutes', str(stale_minutes)]
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode not in (0, 1):
        raise RuntimeError(proc.stderr.strip() or f'emit_recovery_message.py failed with code {proc.returncode}')
    return json.loads(proc.stdout)


def main():
    p = argparse.ArgumentParser(description='Build tool-ready payloads for sessions_send from overdue long-run tasks')
    p.add_argument('--stale-minutes', type=int, default=10)
    p.add_argument('--json', action='store_true', help='kept for symmetry; JSON is always emitted')
    args = p.parse_args()

    payload = load_messages(args.stale_minutes)
    messages = payload.get('messages', [])
    missing = [item.get('task') for item in messages if not item.get('origin_session_key')]
    if missing:
        raise RuntimeError(f'missing origin_session_key for task(s): {", ".join(missing)}')

    out = {
        'due_count': payload.get('due_count', 0),
        'progress_count': payload.get('progress_count', 0),
        'tool': 'sessions_send',
        'payloads': [
            {
                'sessionKey': item['origin_session_key'],
                'label': item['session'],
                'message': item['message'],
                'kind': item.get('kind'),
                'timeoutSeconds': 30,
            }
            for item in messages
        ],
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out['due_count'] == 0 and out.get('progress_count', 0) == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
