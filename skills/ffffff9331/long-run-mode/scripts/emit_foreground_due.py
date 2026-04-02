#!/usr/bin/env python3
import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WATCHDOG = ROOT / 'scripts' / 'watchdog.py'
BUILD = ROOT / 'scripts' / 'build_progress_update.py'
STATE_FILE = ROOT / '.task-state.json'
DEFAULT_UNKNOWN_COOLDOWN_MINUTES = 2


def run_json(cmd):
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode not in (0, 1):
        raise RuntimeError(proc.stderr.strip() or f'command failed with code {proc.returncode}')
    try:
        data = json.loads(proc.stdout)
    except Exception as e:
        raise RuntimeError(f'failed to parse JSON: {e}')
    return proc.returncode, data


def load_state():
    if not STATE_FILE.exists():
        return {'tasks': {}}
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception:
        return {'tasks': {}}


def parse_iso(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def parse_progress_every_minutes(value):
    if not value:
        return 3
    text = str(value).strip().lower()
    if text.endswith('m'):
        try:
            return max(1, int(text[:-1]))
        except Exception:
            return 3
    try:
        return max(1, int(text))
    except Exception:
        return 3


def build_progress_slot(progress_every):
    minutes = parse_progress_every_minutes(progress_every)
    now = datetime.now().astimezone()
    epoch_minutes = int(now.timestamp() // 60)
    return epoch_minutes // minutes


def build_delivery_meta(task, built, task_state):
    progress_every = task_state.get('progress_every') or '3m'
    progress_slot = build_progress_slot(progress_every)
    raw = json.dumps({
        'task': task,
        'state': built.get('state'),
        'sessionKey': built.get('origin_session_key'),
        'progressEvery': progress_every,
        'progressSlot': progress_slot,
    }, ensure_ascii=False, sort_keys=True)
    message_hash = hashlib.sha256(raw.encode('utf-8')).hexdigest()
    delivery_id = f'fg-{message_hash[:16]}'
    return delivery_id, message_hash


def should_skip_unknown(item, message_hash, cooldown_minutes):
    if item.get('last_progress_delivery_status') != 'unknown':
        return False
    if item.get('last_progress_message_hash') != message_hash:
        return False
    unknown_at = parse_iso(item.get('last_progress_unknown_at'))
    if not unknown_at:
        return False
    now = datetime.now().astimezone()
    return now - unknown_at < timedelta(minutes=cooldown_minutes)


def main():
    p = argparse.ArgumentParser(description='Emit foreground progress events for due long-run tasks')
    p.add_argument('--stale-minutes', type=int, default=10)
    p.add_argument('--unknown-cooldown-minutes', type=int, default=DEFAULT_UNKNOWN_COOLDOWN_MINUTES)
    args = p.parse_args()

    state = load_state().get('tasks', {})
    _, report = run_json([sys.executable, str(WATCHDOG), 'check', '--json', '--stale-minutes', str(args.stale_minutes)])
    events = []
    skipped_unknown = []
    for item in report.get('progress', []):
        task = item.get('task')
        if not task:
            continue
        _, built = run_json([sys.executable, str(BUILD), '--task', task])
        task_state = state.get(task, {})
        delivery_id, message_hash = build_delivery_meta(task, built, task_state)
        if should_skip_unknown(task_state, message_hash, args.unknown_cooldown_minutes):
            skipped_unknown.append({
                'task': task,
                'delivery_id': delivery_id,
                'message_hash': message_hash,
                'reason': 'recent_unknown_delivery',
            })
            continue
        events.append({
            'kind': 'foreground-progress',
            'delivery': 'session',
            'sessionKey': built.get('origin_session_key'),
            'task': task,
            'session_label': built.get('session_label') or item.get('session_label') or item.get('session'),
            'state': built.get('state') or item.get('state'),
            'reason': item.get('reason'),
            'message': built.get('message'),
            'delivery_id': delivery_id,
            'message_hash': message_hash,
            'onSuccess': {
                'script': 'task_state.py mark-progress-sent',
                'task': task,
                'note': item.get('note'),
                'delivery_id': delivery_id,
                'message_hash': message_hash,
            },
            'onUnknown': {
                'script': 'task_state.py mark-progress-unknown',
                'task': task,
                'note': item.get('note'),
                'delivery_id': delivery_id,
                'message_hash': message_hash,
            },
            'onError': {
                'script': 'task_state.py mark-progress-failed',
                'task': task,
                'note': item.get('note'),
                'delivery_id': delivery_id,
                'message_hash': message_hash,
            },
        })

    out = {
        'event_count': len(events),
        'events': events,
        'skipped_unknown_count': len(skipped_unknown),
        'skipped_unknown': skipped_unknown,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if not events else 1


if __name__ == '__main__':
    raise SystemExit(main())
