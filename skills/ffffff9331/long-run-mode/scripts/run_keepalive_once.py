#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_FILE = ROOT / '.task-state.json'
EMIT = ROOT / 'scripts' / 'emit_keepalive_resume.py'
TASK_STATE = ROOT / 'scripts' / 'task_state.py'
OPENCLAW_BIN = os.environ.get('OPENCLAW_BIN', 'openclaw')
AUTO_RESUME = os.environ.get('LONG_RUN_MODE_AUTO_RESUME', '').strip().lower() in {'1', 'true', 'yes', 'on'}
SESSIONS_FILE = Path(
    os.environ.get(
        'OPENCLAW_SESSIONS_FILE',
        str(Path.home() / '.openclaw' / 'agents' / 'main' / 'sessions' / 'sessions.json'),
    )
)
ACTIVE_STATES = {'analyzing', 'executing'}


def load_state():
    if not STATE_FILE.exists():
        return {'tasks': {}}
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception as e:
        raise RuntimeError(f'failed to read state file: {e}')


def run_json(cmd, ok_codes=(0, 1)):
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode not in ok_codes:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or f'command failed with code {proc.returncode}')
    try:
        data = json.loads(proc.stdout)
    except Exception as e:
        raise RuntimeError(f'failed to parse JSON: {e}')
    return proc.returncode, data


def run_plain(cmd, ok_codes=(0,)):
    proc = subprocess.run(cmd, text=True, capture_output=True)
    ok = proc.returncode in ok_codes
    return ok, proc


def load_sessions_index():
    if not SESSIONS_FILE.exists():
        return {}
    try:
        return json.loads(SESSIONS_FILE.read_text())
    except Exception:
        return {}


def resolve_session_id(item, event, sessions_index):
    candidates = [
        item.get('origin_session_key'),
        event.get('sessionKey'),
    ]
    for candidate in candidates:
        if not candidate:
            continue
        if candidate in sessions_index and isinstance(sessions_index[candidate], dict):
            sid = sessions_index[candidate].get('sessionId')
            if sid:
                return sid, candidate, 'sessions_index'
        if isinstance(candidate, str) and len(candidate) >= 32 and '-' in candidate:
            return candidate, candidate, 'direct'
    return None, None, 'missing'


def sha256_text(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def mark_attempt(task, message_hash):
    run_plain([
        sys.executable, str(TASK_STATE), 'mark-progress-attempt',
        '--task', task,
        '--message-hash', message_hash,
        '--note', '保活续跑准备执行 openclaw agent',
    ], ok_codes=(0, 1))


def mark_sent(task, message_hash, note):
    run_plain([
        sys.executable, str(TASK_STATE), 'mark-progress-sent',
        '--task', task,
        '--message-hash', message_hash,
        '--note', note,
    ], ok_codes=(0, 1))


def mark_failed(task, message_hash, error, note):
    run_plain([
        sys.executable, str(TASK_STATE), 'mark-progress-failed',
        '--task', task,
        '--message-hash', message_hash,
        '--error', error[:500],
        '--note', note,
    ], ok_codes=(0, 1))


def mark_resume(task, reason, note):
    run_plain([
        sys.executable, str(TASK_STATE), 'mark-resume',
        '--task', task,
        '--reason', reason or 'idle_timeout',
        '--note', note,
    ], ok_codes=(0, 1))


def resume_via_agent(session_id, message):
    cmd = [
        OPENCLAW_BIN, 'agent',
        '--session-id', session_id,
        '--message', message,
        '--json',
    ]
    try:
        proc = subprocess.Popen(
            cmd,
            text=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
        return True, proc
    except Exception as e:
        class FailedProc:
            returncode = 1
            stdout = ''
            stderr = str(e)
        return False, FailedProc()


def main():
    p = argparse.ArgumentParser(description='Run keepalive once for all active long-run tasks and auto-resume overdue sessions')
    p.add_argument('--idle-seconds', type=int, default=60)
    args = p.parse_args()

    data = load_state()
    sessions_index = load_sessions_index()
    dispatches = []
    scanned = 0
    resumed = 0
    failed = 0
    for task, item in data.get('tasks', {}).items():
        if item.get('state') not in ACTIVE_STATES:
            continue
        scanned += 1
        _, emitted = run_json([sys.executable, str(EMIT), '--task', task, '--idle-seconds', str(args.idle_seconds)])
        for event in emitted.get('events', []):
            message = event.get('message') or ''
            message_hash = sha256_text(message)
            dispatch = {
                'tool': 'openclaw_agent_resume',
                'sessionKey': event.get('sessionKey') or item.get('origin_session_key'),
                'origin_session_key': item.get('origin_session_key'),
                'sessionId': None,
                'resolvedFrom': None,
                'resolveMode': 'not-resolved',
                'message': message,
                'task': event.get('task'),
                'reason': event.get('reason'),
                'idle_for_seconds': event.get('idle_for_seconds'),
                'last_activity_source': event.get('last_activity_source'),
            }
            dispatches.append(dispatch)

            mark_attempt(task, message_hash)
            if not AUTO_RESUME:
                dispatch['status'] = 'planned'
                dispatch['note'] = 'auto resume disabled; set LONG_RUN_MODE_AUTO_RESUME=1 to execute openclaw agent'
                continue

            session_id, resolved_from, resolve_mode = resolve_session_id(item, event, sessions_index)
            dispatch['sessionId'] = session_id
            dispatch['resolvedFrom'] = resolved_from
            dispatch['resolveMode'] = resolve_mode

            if not session_id:
                failed += 1
                dispatch['status'] = 'failed'
                dispatch['error'] = 'missing session id in task state'
                mark_failed(task, message_hash, dispatch['error'], '保活续跑失败：缺少 session')
                continue

            ok, proc = resume_via_agent(session_id, message)
            if ok:
                resumed += 1
                dispatch['status'] = 'spawned'
                dispatch['spawn_pid'] = getattr(proc, 'pid', None)
                mark_sent(task, message_hash, '保活续跑已后台触发')
                mark_resume(task, event.get('reason'), '保活续跑已触发，继续沿上次锚点推进')
            else:
                failed += 1
                dispatch['status'] = 'failed'
                dispatch['exit_code'] = proc.returncode
                dispatch['error'] = (proc.stderr or proc.stdout or 'openclaw agent failed').strip()[:2000]
                mark_failed(task, message_hash, dispatch['error'], '保活续跑执行失败')

    out = {
        'scanned_active_tasks': scanned,
        'dispatch_count': len(dispatches),
        'resumed_count': resumed,
        'failed_count': failed,
        'dispatches': dispatches,
        'note': '默认只生成跟进计划；设置 LONG_RUN_MODE_AUTO_RESUME=1 后才会真正执行自动续跑。建议每 60s 运行一次。',
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
mExit(main())
(main())
emExit(main())
