#!/usr/bin/env python3
import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_FILE = ROOT / '.task-state.json'
REL_RE = re.compile(r'^(\d+)([mh])$')
ACTIVE_STATES = {'analyzing', 'executing'}


def load_state():
    if not STATE_FILE.exists():
        return {'tasks': {}}
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception as e:
        raise RuntimeError(f'failed to read state file: {e}')


def parse_iso(value: str):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def parse_relative(value: str, anchor: datetime):
    if not value:
        return None
    m = REL_RE.match(value.strip())
    if not m:
        return None
    count = int(m.group(1))
    unit = m.group(2)
    if unit == 'm':
        return anchor + timedelta(minutes=count)
    if unit == 'h':
        return anchor + timedelta(hours=count)
    return None


def main():
    p = argparse.ArgumentParser(description='Check whether a tracked task must emit a foreground progress update now')
    p.add_argument('--task', required=True)
    args = p.parse_args()

    data = load_state()
    item = data.get('tasks', {}).get(args.task)
    if not item:
        print(f'task not found: {args.task}', file=sys.stderr)
        return 1

    state = item.get('state')
    if state not in ACTIVE_STATES:
        print(json.dumps({'task': args.task, 'due': False, 'reason': f'state={state}'}, ensure_ascii=False, indent=2))
        return 0

    now = datetime.now().astimezone()
    updated = parse_iso(item.get('updated_at', '')) or now
    last_sent = parse_iso(item.get('last_progress_sent_at', '')) or parse_iso(item.get('last_progress_at', '')) or updated
    every = item.get('progress_every', '5m')
    due_at = parse_relative(every, last_sent)
    due = bool(due_at and now >= due_at)

    origin_session_key = item.get('origin_session_key')
    if not origin_session_key:
        raise RuntimeError(f'missing origin_session_key for task: {args.task}')

    session_label = item.get('session_label') or item.get('session')
    out = {
        'task': item.get('task'),
        'session': session_label,
        'session_label': session_label,
        'origin_session_key': origin_session_key,
        'state': state,
        'progress_every': every,
        'last_progress_sent_at': item.get('last_progress_sent_at'),
        'last_progress_at': item.get('last_progress_at'),
        'updated_at': item.get('updated_at'),
        'due': due,
        'reason': f'progress_due ({every})' if due else 'within_window',
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 1 if due else 0


if __name__ == '__main__':
    raise SystemExit(main())
