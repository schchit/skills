#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOREGROUND = ROOT / 'scripts' / 'foreground_tick.py'


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
    p = argparse.ArgumentParser(description='Work-cycle hook for long-run tasks: run after each meaningful step')
    p.add_argument('--task', required=True)
    p.add_argument('--step', default='', help='What was just done in this work cycle')
    args = p.parse_args()

    code, tick = run_json([sys.executable, str(FOREGROUND), '--task', args.task])
    session_key = tick.get('sessionKey') or tick.get('check', {}).get('origin_session_key')
    if not session_key:
        raise RuntimeError('missing origin_session_key; work-cycle delivery requires a real session key')

    out = {
        'task': args.task,
        'step': args.step,
        'continue': True,
        'report_now': bool(tick.get('due')),
        'must_send_now': bool(tick.get('due')),
        'delivery': tick.get('delivery', 'session'),
        'sessionKey': session_key,
        'session_label': tick.get('session_label') or tick.get('check', {}).get('session_label') or tick.get('check', {}).get('session'),
        'message': tick.get('message'),
        'reason': tick.get('check', {}).get('reason'),
        'instruction': None,
        'protocol': {
            'on_success': '必须立即执行 task_state.py touch-progress，然后才能继续下一轮。',
            'on_error': '必须立即执行 task_state.py mark-progress-attempt --error <失败原因>；若连续触发仍未送达，应转 blocked。'
        }
    }
    if out['report_now']:
        out['instruction'] = '这是前台心跳，必须立即发往该任务绑定的 sessionKey；发送成功后必须 touch-progress；发送失败后必须 mark-progress-attempt，再决定是否继续。'
    else:
        out['instruction'] = '本轮无需汇报，直接继续下一轮；下一轮结束后再次运行 work_cycle_tick.py。'

    print(json.dumps(out, ensure_ascii=False, indent=2))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
