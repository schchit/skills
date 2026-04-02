#!/usr/bin/env python3
import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_FILE = ROOT / '.task-state.json'
ACTIVE_STATES = {'analyzing', 'executing'}


def load_state():
    if not STATE_FILE.exists():
        return {'tasks': {}}
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception as e:
        raise RuntimeError(f'failed to read state file: {e}')


def parse_iso(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def latest_activity(item):
    candidates = {
        'last_visible_reply_at': parse_iso(item.get('last_visible_reply_at')),
        'last_tool_result_at': parse_iso(item.get('last_tool_result_at')),
        'last_progress_at': parse_iso(item.get('last_progress_at')),
        'updated_at': parse_iso(item.get('updated_at')),
    }
    valid = {k: v for k, v in candidates.items() if v is not None}
    if not valid:
        return None, None
    source, ts = max(valid.items(), key=lambda kv: kv[1])
    return source, ts


def build_resume_message(item, idle_for_seconds, source):
    note = item.get('note') or '继续沿上次锚点推进'
    goal = item.get('goal') or '继续推进当前任务'
    return '\n'.join([
        f'保活续跑：{item.get("task")}',
        f'当前状态：{item.get("state") or "analyzing"}',
        f'静默时长：约 {idle_for_seconds} 秒（最近活动源：{source or "unknown"}）',
        f'任务目标：{goal}',
        f'立即继续：{note}',
        '要求：不要停在说明，直接继续当前任务，并尽快给出新的可见进展。',
    ])


def main():
    p = argparse.ArgumentParser(description='Keepalive check for long-run tasks: resume if idle for too long')
    p.add_argument('--task', required=True)
    p.add_argument('--idle-seconds', type=int, default=60)
    args = p.parse_args()

    data = load_state()
    item = data.get('tasks', {}).get(args.task)
    if not item:
        print(f'task not found: {args.task}', file=sys.stderr)
        return 1

    state = item.get('state')
    source, ts = latest_activity(item)
    now = datetime.now().astimezone()
    idle_for = None if ts is None else int((now - ts).total_seconds())
    should_resume = state in ACTIVE_STATES and (idle_for is None or idle_for > args.idle_seconds)

    session_label = item.get('session_label') or item.get('session')
    out = {
        'task': args.task,
        'state': state,
        'origin_session_key': item.get('origin_session_key'),
        'session_label': session_label,
        'active_states': sorted(ACTIVE_STATES),
        'idle_seconds_threshold': args.idle_seconds,
        'last_activity_source': source,
        'last_activity_at': None if ts is None else ts.isoformat(timespec='seconds'),
        'idle_for_seconds': idle_for,
        'should_resume': should_resume,
        'reason': 'idle_timeout' if should_resume else 'still_active',
        'resume_message': build_resume_message(item, idle_for or args.idle_seconds, source) if should_resume else None,
        'instruction': '若 should_resume=true：先发 resume_message 到当前会话，再执行 task_state.py mark-resume --task <任务名> --reason idle_timeout。',
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 1 if should_resume else 0


if __name__ == '__main__':
    raise SystemExit(main())
