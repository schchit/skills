#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WATCHDOG = ROOT / 'scripts' / 'watchdog.py'


def run_watchdog(stale_minutes: int):
    cmd = [sys.executable, str(WATCHDOG), 'check', '--json', '--stale-minutes', str(stale_minutes)]
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode not in (0, 1):
        raise RuntimeError(proc.stderr.strip() or f'watchdog.py failed with code {proc.returncode}')
    return json.loads(proc.stdout)


def require_origin_session_key(item):
    session_key = item.get('origin_session_key')
    if not session_key:
        raise RuntimeError(f"missing origin_session_key for task: {item.get('task')}")
    return session_key


def suggest_action(item):
    state = item.get('state')
    session = item.get('session_label') or item.get('session')
    origin_session_key = require_origin_session_key(item)
    reason = item.get('reason')
    note = item.get('note')

    if state == 'waiting':
        return {
            'kind': 'check-waiting',
            'summary': f'任务处于等待态但已到检查点，去确认外部条件是否已满足：{note}',
            'suggested_session': session,
            'suggested_session_key': origin_session_key,
            'suggested_message': f'长任务回收：你之前处于 waiting，原因是 {note}。现在检查等待条件是否已满足；若仍未满足，更新 next_check；若已满足，继续推进并回报结果。',
        }

    if state == 'executing':
        return {
            'kind': 'check-progress',
            'summary': f'任务仍在执行态但超过检查窗口，确认是否卡住：{note}',
            'suggested_session': session,
            'suggested_session_key': origin_session_key,
            'suggested_message': f'长任务回收：你之前处于 executing，但已超出检查窗口（{reason}）。请立刻回报当前进展；若已阻塞，转 blocked 并说明缺什么；若仍可继续，更新状态并继续推进。',
        }

    if state == 'analyzing':
        return {
            'kind': 'force-decision',
            'summary': f'分析态停留过久，要求给结论或切执行：{note}',
            'suggested_session': session,
            'suggested_session_key': origin_session_key,
            'suggested_message': f'长任务回收：你之前处于 analyzing，但已超出检查窗口（{reason}）。请在本轮给出阶段结论，并明确进入 executing、blocked 或 handoff，不能继续停留在纯分析。',
        }

    return {
        'kind': 'manual-review',
        'summary': f'任务需要人工查看：{note}',
        'suggested_session': session,
        'suggested_session_key': origin_session_key,
        'suggested_message': f'长任务回收：任务状态为 {state}，触发原因 {reason}。请检查并更新状态。',
    }


def suggest_progress(item):
    return {
        'kind': 'progress-ping',
        'summary': f'任务持续推进中，需要发一条可见进度：{item.get("note")}',
        'suggested_session': item.get('session'),
        'suggested_session_key': require_origin_session_key(item),
        'suggested_message': f'长任务进度：当前仍处于 {item.get("state")}。正在处理：{item.get("note")}。刚确认：{item.get("goal")}。下一步：继续沿当前链路推进，并在本轮更新学习结论。',
    }


def build_report(data):
    due = data.get('due', [])
    progress = data.get('progress', [])
    items = []
    for item in due:
        session_label = item.get('session_label') or item.get('session')
        items.append({
            'task': item.get('task'),
            'state': item.get('state'),
            'session': session_label,
            'session_label': session_label,
            'origin_session_key': require_origin_session_key(item),
            'boundary': item.get('boundary'),
            'reason': item.get('reason'),
            'goal': item.get('goal'),
            'next_check': item.get('next_check'),
            'updated_at': item.get('updated_at'),
            'note': item.get('note'),
            'kind': 'recovery',
            'recovery': suggest_action(item),
        })
    for item in progress:
        session_label = item.get('session_label') or item.get('session')
        items.append({
            'task': item.get('task'),
            'state': item.get('state'),
            'session': session_label,
            'session_label': session_label,
            'origin_session_key': require_origin_session_key(item),
            'boundary': item.get('boundary'),
            'reason': item.get('reason'),
            'goal': item.get('goal'),
            'next_check': item.get('next_check'),
            'updated_at': item.get('updated_at'),
            'note': item.get('note'),
            'kind': 'progress',
            'recovery': suggest_progress(item),
        })
    return {
        'due_count': len(due),
        'progress_count': len(progress),
        'items': items,
    }


def print_human(report):
    if report['due_count'] == 0 and report.get('progress_count', 0) == 0:
        print('recover: no overdue tasks')
        return 0

    print(f"recover: {report['due_count']} overdue task(s), {report.get('progress_count', 0)} progress update(s)")
    for item in report['items']:
        print(f"- task: {item['task']}")
        print(f"  kind: {item['kind']}")
        print(f"  state/session: {item['state']} / {item['session']}")
        print(f"  reason: {item['reason']}")
        print(f"  goal: {item['goal']}")
        print(f"  note: {item['note']}")
        print(f"  suggested action: {item['recovery']['kind']}")
        print(f"  suggested session: {item['recovery']['suggested_session']}")
        print(f"  suggested sessionKey: {item['recovery'].get('suggested_session_key')}")
        print(f"  suggested message: {item['recovery']['suggested_message']}")
    return 1


def main():
    p = argparse.ArgumentParser(description='Build recovery suggestions for overdue long-run tasks')
    p.add_argument('--stale-minutes', type=int, default=10)
    p.add_argument('--json', action='store_true')
    args = p.parse_args()

    data = run_watchdog(args.stale_minutes)
    report = build_report(data)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report['due_count'] == 0 and report.get('progress_count', 0) == 0 else 1
    return print_human(report)


if __name__ == '__main__':
    raise SystemExit(main())
