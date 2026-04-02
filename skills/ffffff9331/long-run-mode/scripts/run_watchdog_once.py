#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECOVER = ROOT / 'scripts' / 'recover_due_tasks.py'
TASK_STATE = ROOT / 'scripts' / 'task_state.py'


def load_report(stale_minutes: int):
    cmd = [sys.executable, str(RECOVER), '--json', '--stale-minutes', str(stale_minutes)]
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode not in (0, 1):
        raise RuntimeError(proc.stderr.strip() or f'recover_due_tasks.py failed with code {proc.returncode}')
    return json.loads(proc.stdout)


def record_attempt(task: str, note: str | None = None):
    cmd = [sys.executable, str(TASK_STATE), 'mark-progress-attempt', '--task', task]
    if note:
        cmd.extend(['--note', note])
    subprocess.run(cmd, text=True, capture_output=True)


def record_success(task: str, note: str | None = None):
    cmd = [sys.executable, str(TASK_STATE), 'touch-progress', '--task', task]
    if note:
        cmd.extend(['--note', note])
    subprocess.run(cmd, text=True, capture_output=True)


def record_error(task: str, error: str, note: str | None = None):
    cmd = [sys.executable, str(TASK_STATE), 'mark-progress-attempt', '--task', task, '--error', error]
    if note:
        cmd.extend(['--note', note])
    subprocess.run(cmd, text=True, capture_output=True)


def main():
    p = argparse.ArgumentParser(description='Run long-run-mode watchdog once and print tool payloads + state side effects')
    p.add_argument('--stale-minutes', type=int, default=10)
    args = p.parse_args()

    report = load_report(args.stale_minutes)
    out = {
        'due_count': report.get('due_count', 0),
        'progress_count': report.get('progress_count', 0),
        'tool': 'sessions_send',
        'payloads': [],
    }

    for item in report.get('items', []):
        task = item.get('task')
        session = item.get('recovery', {}).get('suggested_session') or item.get('session_label') or item.get('session')
        session_key = item.get('recovery', {}).get('suggested_session_key') or item.get('origin_session_key')
        message = item.get('recovery', {}).get('suggested_message')
        kind = item.get('kind')
        note = item.get('note')
        if not task or not session or not session_key or not message:
            continue
        if kind == 'progress':
            record_attempt(task, note)
        out['payloads'].append({
            'sessionKey': session_key,
            'label': session,
            'task': task,
            'kind': kind,
            'message': message,
            'timeoutSeconds': 30,
            'onSuccess': {
                'script': 'task_state.py touch-progress' if kind == 'progress' else None,
                'task': task,
                'note': note,
            },
            'onError': {
                'script': 'task_state.py mark-progress-attempt' if kind == 'progress' else None,
                'task': task,
                'note': note,
            },
        })

    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out['due_count'] == 0 and out['progress_count'] == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
