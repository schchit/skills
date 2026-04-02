#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
STATE_FILE = ROOT / '.task-state.json'
VALID_STATES = {'analyzing', 'executing', 'waiting', 'blocked', 'handoff', 'done'}
VALID_DELIVERY_STATUS = {'sent', 'unknown', 'failed'}
DEFAULT_PROGRESS_EVERY = '3m'


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')


def normalize_state(data):
    if not isinstance(data, dict):
        data = {}
    tasks = data.get('tasks')
    if not isinstance(tasks, dict):
        tasks = {}
    for _, item in tasks.items():
        if not isinstance(item, dict):
            continue
        session_label = item.get('session_label') or item.get('session')
        if session_label:
            item['session_label'] = session_label
            item['session'] = session_label
    data['tasks'] = tasks
    locks = data.get('active_long_runs_by_session')
    if not isinstance(locks, dict):
        locks = {}
    legacy_task = data.get('active_long_run') or data.get('active_long_run_task')
    if legacy_task and isinstance(legacy_task, str):
        item = tasks.get(legacy_task)
        session_key = item.get('origin_session_key') or item.get('session') if isinstance(item, dict) else None
        if session_key and session_key not in locks:
            locks[session_key] = legacy_task
    data['active_long_runs_by_session'] = locks
    return data


def load_state():
    if not STATE_FILE.exists():
        return normalize_state({'tasks': {}})
    try:
        return normalize_state(json.loads(STATE_FILE.read_text()))
    except Exception:
        return normalize_state({'tasks': {}})


def save_state(data):
    STATE_FILE.write_text(json.dumps(normalize_state(data), ensure_ascii=False, indent=2) + '\n')


def apply_delivery_meta(item, *, delivery_status=None, delivery_id=None, message_hash=None, error_marker='__KEEP__'):
    if delivery_status is not None:
        item['last_progress_delivery_status'] = delivery_status
    if delivery_id is not None:
        item['last_progress_delivery_id'] = delivery_id
    if message_hash is not None:
        item['last_progress_message_hash'] = message_hash
    if error_marker != '__KEEP__':
        item['last_progress_send_error'] = error_marker


def lock_session(data, session_key: str, task_name: str, *, force: bool = False):
    locks = data.setdefault('active_long_runs_by_session', {})
    current = locks.get(session_key)
    if current and current != task_name and not force:
        return current
    locks[session_key] = task_name
    return None


def release_session_lock(data, session_key: str, task_name: str | None = None):
    locks = data.setdefault('active_long_runs_by_session', {})
    current = locks.get(session_key)
    if current is None:
        return False
    if task_name and current != task_name:
        return False
    del locks[session_key]
    return True


def cmd_set(args):
    if args.state not in VALID_STATES:
        print(f'invalid state: {args.state}', file=sys.stderr)
        return 2
    data = load_state()
    tasks = data.setdefault('tasks', {})
    previous = tasks.get(args.task, {})
    origin_session_key = args.origin_session_key or previous.get('origin_session_key')
    if args.state in {'analyzing', 'executing', 'waiting'} and not origin_session_key:
        print(json.dumps({
            'error': 'missing origin_session_key',
            'task': args.task,
            'state': args.state,
            'message': 'long-run start/update requires a real origin_session_key; state registration alone does not mean the task started in the target session',
        }, ensure_ascii=False, indent=2), file=sys.stderr)
        return 4
    if args.state in {'analyzing', 'executing', 'waiting'}:
        conflict = lock_session(data, origin_session_key, args.task, force=args.force_lock)
        if conflict:
            print(json.dumps({
                'error': 'session lock exists',
                'origin_session_key': origin_session_key,
                'current_task': conflict,
                'requested_task': args.task,
            }, ensure_ascii=False, indent=2), file=sys.stderr)
            return 3
    elif args.state in {'handoff', 'done', 'blocked'}:
        release_session_lock(data, origin_session_key, args.task)
    tasks[args.task] = {
        'task': args.task,
        'session': args.session,
        'origin_session_key': origin_session_key,
        'state': args.state,
        'goal': args.goal,
        'done_when': args.done_when,
        'blocked_when': args.blocked_when,
        'boundary': args.boundary,
        'next_check': args.next_check,
        'note': args.note,
        'progress_every': args.progress_every or previous.get('progress_every') or DEFAULT_PROGRESS_EVERY,
        'last_progress_at': previous.get('last_progress_at') or now_iso(),
        'last_progress_attempt_at': previous.get('last_progress_attempt_at'),
        'last_progress_sent_at': previous.get('last_progress_sent_at'),
        'last_progress_unknown_at': previous.get('last_progress_unknown_at'),
        'last_progress_delivery_status': previous.get('last_progress_delivery_status'),
        'last_progress_delivery_id': previous.get('last_progress_delivery_id'),
        'last_progress_message_hash': previous.get('last_progress_message_hash'),
        'last_progress_send_error': previous.get('last_progress_send_error'),
        'last_visible_reply_at': previous.get('last_visible_reply_at'),
        'last_tool_result_at': previous.get('last_tool_result_at'),
        'last_resume_at': previous.get('last_resume_at'),
        'last_resume_reason': previous.get('last_resume_reason'),
        'last_resume_count': previous.get('last_resume_count', 0),
        'updated_at': now_iso(),
    }
    save_state(data)
    print(json.dumps(tasks[args.task], ensure_ascii=False, indent=2))
    return 0


def cmd_list(args):
    data = load_state()
    tasks = data.get('tasks', {})
    if not tasks:
        print('no tasks')
        return 0
    for name, item in tasks.items():
        print(f"- {name} | {item.get('state')} | {item.get('session')} | next={item.get('next_check')} | updated={item.get('updated_at')}")
    return 0


def cmd_show(args):
    data = load_state()
    item = data.get('tasks', {}).get(args.task)
    if not item:
        print(f'task not found: {args.task}', file=sys.stderr)
        return 1
    print(json.dumps(item, ensure_ascii=False, indent=2))
    return 0


def cmd_touch_progress(args):
    data = load_state()
    tasks = data.get('tasks', {})
    item = tasks.get(args.task)
    if not item:
        print(f'task not found: {args.task}', file=sys.stderr)
        return 1
    item['last_progress_at'] = now_iso()
    item['last_progress_sent_at'] = item['last_progress_at']
    item['last_progress_send_error'] = None
    item['last_progress_delivery_status'] = 'sent'
    item['last_progress_unknown_at'] = None
    if args.note:
        item['note'] = args.note
    if args.delivery_id:
        item['last_progress_delivery_id'] = args.delivery_id
    if args.message_hash:
        item['last_progress_message_hash'] = args.message_hash
    item['updated_at'] = now_iso()
    save_state(data)
    print(json.dumps(item, ensure_ascii=False, indent=2))
    return 0


def cmd_mark_progress_attempt(args):
    data = load_state()
    tasks = data.get('tasks', {})
    item = tasks.get(args.task)
    if not item:
        print(f'task not found: {args.task}', file=sys.stderr)
        return 1
    item['last_progress_attempt_at'] = now_iso()
    if args.error is not None:
        item['last_progress_send_error'] = args.error
    if args.note:
        item['note'] = args.note
    if args.delivery_id:
        item['last_progress_delivery_id'] = args.delivery_id
    if args.message_hash:
        item['last_progress_message_hash'] = args.message_hash
    item['updated_at'] = now_iso()
    save_state(data)
    print(json.dumps(item, ensure_ascii=False, indent=2))
    return 0


def cmd_mark_progress_sent(args):
    data = load_state()
    item = data.get('tasks', {}).get(args.task)
    if not item:
        print(f'task not found: {args.task}', file=sys.stderr)
        return 1
    ts = now_iso()
    item['last_progress_attempt_at'] = ts
    item['last_progress_at'] = ts
    item['last_progress_sent_at'] = ts
    item['last_progress_unknown_at'] = None
    apply_delivery_meta(item, delivery_status='sent', delivery_id=args.delivery_id, message_hash=args.message_hash, error_marker=None)
    if args.note:
        item['note'] = args.note
    item['updated_at'] = ts
    save_state(data)
    print(json.dumps(item, ensure_ascii=False, indent=2))
    return 0


def cmd_mark_progress_unknown(args):
    data = load_state()
    item = data.get('tasks', {}).get(args.task)
    if not item:
        print(f'task not found: {args.task}', file=sys.stderr)
        return 1
    ts = now_iso()
    item['last_progress_attempt_at'] = ts
    item['last_progress_unknown_at'] = ts
    apply_delivery_meta(item, delivery_status='unknown', delivery_id=args.delivery_id, message_hash=args.message_hash, error_marker=args.error or 'delivery result unknown')
    if args.note:
        item['note'] = args.note
    item['updated_at'] = ts
    save_state(data)
    print(json.dumps(item, ensure_ascii=False, indent=2))
    return 0


def cmd_mark_progress_failed(args):
    data = load_state()
    item = data.get('tasks', {}).get(args.task)
    if not item:
        print(f'task not found: {args.task}', file=sys.stderr)
        return 1
    ts = now_iso()
    item['last_progress_attempt_at'] = ts
    apply_delivery_meta(item, delivery_status='failed', delivery_id=args.delivery_id, message_hash=args.message_hash, error_marker=args.error or 'delivery failed')
    if args.note:
        item['note'] = args.note
    item['updated_at'] = ts
    save_state(data)
    print(json.dumps(item, ensure_ascii=False, indent=2))
    return 0


def cmd_mark_visible_reply(args):
    data = load_state()
    item = data.get('tasks', {}).get(args.task)
    if not item:
        print(f'task not found: {args.task}', file=sys.stderr)
        return 1
    ts = now_iso()
    item['last_visible_reply_at'] = ts
    if args.note:
        item['note'] = args.note
    item['updated_at'] = ts
    save_state(data)
    print(json.dumps(item, ensure_ascii=False, indent=2))
    return 0


def cmd_mark_tool_result(args):
    data = load_state()
    item = data.get('tasks', {}).get(args.task)
    if not item:
        print(f'task not found: {args.task}', file=sys.stderr)
        return 1
    ts = now_iso()
    item['last_tool_result_at'] = ts
    if args.note:
        item['note'] = args.note
    item['updated_at'] = ts
    save_state(data)
    print(json.dumps(item, ensure_ascii=False, indent=2))
    return 0


def cmd_mark_resume(args):
    data = load_state()
    item = data.get('tasks', {}).get(args.task)
    if not item:
        print(f'task not found: {args.task}', file=sys.stderr)
        return 1
    ts = now_iso()
    item['last_resume_at'] = ts
    item['last_resume_reason'] = args.reason or 'manual'
    item['last_resume_count'] = int(item.get('last_resume_count') or 0) + 1
    if args.note:
        item['note'] = args.note
    item['updated_at'] = ts
    save_state(data)
    print(json.dumps(item, ensure_ascii=False, indent=2))
    return 0


def cmd_acquire_lock(args):
    data = load_state()
    conflict = lock_session(data, args.session, args.task, force=args.force)
    if conflict:
        print(json.dumps({
            'ok': False,
            'error': 'session lock exists',
            'origin_session_key': args.session,
            'current_task': conflict,
            'requested_task': args.task,
        }, ensure_ascii=False, indent=2), file=sys.stderr)
        return 3
    save_state(data)
    print(json.dumps({
        'ok': True,
        'origin_session_key': args.session,
        'task': args.task,
    }, ensure_ascii=False, indent=2))
    return 0


def cmd_release_lock(args):
    data = load_state()
    released = release_session_lock(data, args.session, args.task)
    save_state(data)
    print(json.dumps({
        'ok': released,
        'origin_session_key': args.session,
        'task': args.task,
    }, ensure_ascii=False, indent=2))
    return 0 if released else 1


def cmd_locks(args):
    data = load_state()
    print(json.dumps(data.get('active_long_runs_by_session', {}), ensure_ascii=False, indent=2))
    return 0


def cmd_clear(args):
    data = load_state()
    tasks = data.get('tasks', {})
    if args.task:
        if args.task in tasks:
            item = tasks[args.task]
            session_key = item.get('origin_session_key') or item.get('session')
            if session_key:
                release_session_lock(data, session_key, args.task)
            del tasks[args.task]
            save_state(data)
            print(f'cleared: {args.task}')
        else:
            print(f'task not found: {args.task}', file=sys.stderr)
            return 1
    else:
        save_state({'tasks': {}, 'active_long_runs_by_session': {}})
        print('cleared all tasks')
    return 0


def add_delivery_args(parser):
    parser.add_argument('--delivery-id')
    parser.add_argument('--message-hash')


def build_parser():
    p = argparse.ArgumentParser(description='Manage long-run task state')
    sub = p.add_subparsers(dest='command', required=True)

    s = sub.add_parser('set')
    s.add_argument('--task', required=True)
    s.add_argument('--session', required=True)
    s.add_argument('--state', required=True)
    s.add_argument('--origin-session-key', dest='origin_session_key')
    s.add_argument('--goal', required=True)
    s.add_argument('--done-when', required=True, dest='done_when')
    s.add_argument('--blocked-when', required=True, dest='blocked_when')
    s.add_argument('--boundary', required=True)
    s.add_argument('--next-check', required=True, dest='next_check')
    s.add_argument('--note', required=True)
    s.add_argument('--progress-every', dest='progress_every')
    s.add_argument('--force-lock', action='store_true', dest='force_lock')
    s.set_defaults(func=cmd_set)

    t = sub.add_parser('touch-progress')
    t.add_argument('--task', required=True)
    t.add_argument('--note')
    add_delivery_args(t)
    t.set_defaults(func=cmd_touch_progress)

    m = sub.add_parser('mark-progress-attempt')
    m.add_argument('--task', required=True)
    m.add_argument('--error')
    m.add_argument('--note')
    add_delivery_args(m)
    m.set_defaults(func=cmd_mark_progress_attempt)

    ms = sub.add_parser('mark-progress-sent')
    ms.add_argument('--task', required=True)
    ms.add_argument('--note')
    add_delivery_args(ms)
    ms.set_defaults(func=cmd_mark_progress_sent)

    mu = sub.add_parser('mark-progress-unknown')
    mu.add_argument('--task', required=True)
    mu.add_argument('--error')
    mu.add_argument('--note')
    add_delivery_args(mu)
    mu.set_defaults(func=cmd_mark_progress_unknown)

    mf = sub.add_parser('mark-progress-failed')
    mf.add_argument('--task', required=True)
    mf.add_argument('--error')
    mf.add_argument('--note')
    add_delivery_args(mf)
    mf.set_defaults(func=cmd_mark_progress_failed)

    vr = sub.add_parser('mark-visible-reply')
    vr.add_argument('--task', required=True)
    vr.add_argument('--note')
    vr.set_defaults(func=cmd_mark_visible_reply)

    tr = sub.add_parser('mark-tool-result')
    tr.add_argument('--task', required=True)
    tr.add_argument('--note')
    tr.set_defaults(func=cmd_mark_tool_result)

    mr = sub.add_parser('mark-resume')
    mr.add_argument('--task', required=True)
    mr.add_argument('--reason')
    mr.add_argument('--note')
    mr.set_defaults(func=cmd_mark_resume)

    al = sub.add_parser('acquire-lock')
    al.add_argument('--session', required=True)
    al.add_argument('--task', required=True)
    al.add_argument('--force', action='store_true')
    al.set_defaults(func=cmd_acquire_lock)

    rl = sub.add_parser('release-lock')
    rl.add_argument('--session', required=True)
    rl.add_argument('--task')
    rl.set_defaults(func=cmd_release_lock)

    lk = sub.add_parser('locks')
    lk.set_defaults(func=cmd_locks)

    l = sub.add_parser('list')
    l.set_defaults(func=cmd_list)

    sh = sub.add_parser('show')
    sh.add_argument('--task', required=True)
    sh.set_defaults(func=cmd_show)

    c = sub.add_parser('clear')
    c.add_argument('--task')
    c.set_defaults(func=cmd_clear)

    return p


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    raise SystemExit(args.func(args))
