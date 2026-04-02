#!/usr/bin/env python3
import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_FILE = ROOT / '.task-state.json'
STALE_MINUTES_DEFAULT = 10
DUE_STATES = {'analyzing', 'executing', 'waiting'}
PROGRESS_STATES = {'analyzing', 'executing'}
REL_RE = re.compile(r'^(\d+)([mh])$')


def load_state():
    if not STATE_FILE.exists():
        return {'tasks': {}}
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception as e:
        print(f'failed to read state file: {e}', file=sys.stderr)
        return {'tasks': {}}


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


def progress_reason(item, now: datetime):
    state = item.get('state')
    if state not in PROGRESS_STATES:
        return None
    updated = parse_iso(item.get('updated_at', ''))
    if not updated:
        return None
    progress_every_raw = item.get('progress_every', '')
    last_progress = parse_iso(item.get('last_progress_at', '')) or updated
    expected_progress_at = parse_relative(progress_every_raw, last_progress)
    if expected_progress_at and now >= expected_progress_at:
        return f'progress_due ({progress_every_raw})'
    return None


def due_reason(item, now: datetime, stale_minutes: int):
    state = item.get('state')
    if state not in DUE_STATES:
        return None

    updated = parse_iso(item.get('updated_at', ''))
    if not updated:
        return 'missing updated_at'

    next_check_raw = item.get('next_check', '')
    next_check = parse_iso(next_check_raw) or parse_relative(next_check_raw, updated)
    if next_check and now >= next_check:
        return f'next_check_due ({next_check_raw})'

    if now - updated >= timedelta(minutes=stale_minutes):
        return f'stale_update ({stale_minutes}m)'

    return None


def summarize(item, reason, kind='recovery'):
    origin_session_key = item.get('origin_session_key')
    if not origin_session_key:
        raise RuntimeError(f"missing origin_session_key for task: {item.get('task')}")
    session_label = item.get('session_label') or item.get('session')
    return {
        'task': item.get('task'),
        'session': session_label,
        'session_label': session_label,
        'origin_session_key': origin_session_key,
        'state': item.get('state'),
        'reason': reason,
        'kind': kind,
        'goal': item.get('goal'),
        'boundary': item.get('boundary'),
        'next_check': item.get('next_check'),
        'progress_every': item.get('progress_every'),
        'last_progress_at': item.get('last_progress_at'),
        'updated_at': item.get('updated_at'),
        'note': item.get('note'),
    }


def cmd_check(args):
    data = load_state()
    tasks = data.get('tasks', {})
    now = datetime.now().astimezone()
    due = []
    progress = []
    ok = []

    for _, item in tasks.items():
        recovery_reason = due_reason(item, now, args.stale_minutes)
        if recovery_reason:
            due.append(summarize(item, recovery_reason, 'recovery'))
            continue
        progress_due_reason = progress_reason(item, now)
        if progress_due_reason:
            progress.append(summarize(item, progress_due_reason, 'progress'))
            continue
        ok.append(item.get('task'))

    if args.json:
        print(json.dumps({'due': due, 'progress': progress, 'ok': ok}, ensure_ascii=False, indent=2))
        return 0 if not due and not progress else 1

    if not due and not progress:
        print('watchdog: all tracked tasks are within expected window')
        return 0

    if due:
        print('watchdog: tasks needing follow-up')
        for item in due:
            print(f"- {item['task']} | {item['state']} | {item['session']} | {item['reason']}")
            print(f"  goal: {item['goal']}")
            print(f"  note: {item['note']}")
            print(f"  next: {item['next_check']} | updated: {item['updated_at']}")
    if progress:
        print('watchdog: tasks needing visible progress update')
        for item in progress:
            print(f"- {item['task']} | {item['state']} | {item['session']} | {item['reason']}")
            print(f"  goal: {item['goal']}")
            print(f"  note: {item['note']}")
            print(f"  progress_every: {item['progress_every']} | last_progress: {item['last_progress_at']}")
    return 1


def build_parser():
    p = argparse.ArgumentParser(description='Check long-run task state for overdue follow-up')
    sub = p.add_subparsers(dest='command', required=True)

    c = sub.add_parser('check')
    c.add_argument('--stale-minutes', type=int, default=STALE_MINUTES_DEFAULT)
    c.add_argument('--json', action='store_true')
    c.set_defaults(func=cmd_check)

    return p


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    raise SystemExit(args.func(args))
