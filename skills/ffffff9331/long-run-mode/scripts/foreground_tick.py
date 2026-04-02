#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / 'scripts' / 'check_foreground_progress.py'
BUILD = ROOT / 'scripts' / 'build_progress_update.py'


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
    p = argparse.ArgumentParser(description='Foreground heartbeat helper: decide whether to report progress now and build the message if due')
    p.add_argument('--task', required=True)
    args = p.parse_args()

    status_code, check = run_json([sys.executable, str(CHECK), '--task', args.task])
    out = {
        'task': args.task,
        'due': bool(check.get('due')),
        'check': check,
        'message': None,
        'delivery': 'session',
        'sessionKey': check.get('origin_session_key') or check.get('session'),
        'session_label': check.get('session_label') or check.get('session'),
        'state': check.get('state'),
    }
    if status_code == 1 and check.get('due'):
        _, built = run_json([sys.executable, str(BUILD), '--task', args.task])
        built_session_key = built.get('origin_session_key')
        if not built_session_key:
            raise RuntimeError('missing origin_session_key in built progress update')
        out['message'] = built.get('message')
        out['state'] = built.get('state')
        out['sessionKey'] = built_session_key
        out['session_label'] = built.get('session_label') or out.get('session_label')

    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 1 if out['due'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
