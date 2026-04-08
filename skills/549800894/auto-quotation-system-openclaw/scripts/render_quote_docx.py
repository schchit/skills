#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path


def format_currency(amount: int | float | None) -> str:
    if amount is None:
        return '-'
    return f"{int(round(amount)):,} 元"


def bullet_list(items: list[str]) -> str:
    if not items:
        return '<p>无</p>'
    return '<ul>' + ''.join(f'<li>{html.escape(item)}</li>' for item in items) + '</ul>'


def table(headers: list[str], rows: list[list[str]]) -> str:
    head = '<tr>' + ''.join(f'<th>{html.escape(h)}</th>' for h in headers) + '</tr>'
    body_rows = []
    for row in rows:
        body_rows.append('<tr>' + ''.join(f'<td>{cell}</td>' for cell in row) + '</tr>')
    return '<table><thead>' + head + '</thead><tbody>' + ''.join(body_rows) + '</tbody></table>'


def section(title: str, body: str) -> str:
    return '<div class="section"><p class="section-title">' + html.escape(title) + '</p>' + body + '</div>'


def payment_bullets(payment_schedule: list[list[str] | tuple[str, str]]) -> str:
    items = []
    for stage, percent in payment_schedule:
        items.append(f'{stage}：{percent}')
    return bullet_list(items)


def render_html(payload: dict) -> str:
    project_name = html.escape(payload.get('project_name', '项目报价方案'))
    features = payload.get('features', [])
    line_items = payload.get('line_items', [])
    roles = payload.get('roles', [])
    assumptions = payload.get('assumptions', [])
    payment_schedule = payload.get('payment_schedule', [])
    total_price = payload.get('total_price', 0)
    requirement_groups = payload.get('requirement_groups', [])
    total_days = payload.get('total_days') or sum(row.get('days', 0) for row in roles) or sum(item.get('total_days', 0) for item in line_items)
    today = payload.get('quote_date') or date.today().isoformat()
    vendor_name = payload.get('vendor_name', '自动报价系统')
    tax_note = payload.get('tax_note', '含税与否以最终商务确认版本为准')
    project_weeks = max(4, round(sum(row.get('days', 0) for row in roles) / 10))
    design_weeks = max(1, round(project_weeks * 0.2))
    develop_weeks = max(2, round(project_weeks * 0.6))
    accept_weeks = max(1, project_weeks - design_weeks - develop_weeks)

    service_scope = [
        '产品需求梳理',
        '技术方案设计',
        '软件设计开发',
        '项目部署和运维1年（从提交验收日开始算）',
    ]
    deliverables = [
        '产品文档',
        '前后端源代码',
        '测试用例',
        '项目部署文档，接口文档',
    ]
    acceptance = [
        '默认是在我方的测试环境上进行验收。',
        '管理后台交付标准以满足小程序端的业务为准，UI样式、交互以实际开发为标准。',
        '验收依据按照当前确认的需求文档内容。',
        '文档未提及内容均视为优化或拓展需求，需另行评估。',
    ]
    prerequisites = [
        '账号等第三方资源需在规定时间内提供，不能及时提供时可先在我方测试账号完成验收。',
        '如涉及其他第三方协作，需确保沟通链路畅通。',
    ]
    dependencies = [
        '小程序、公众号相关账号',
        '服务器、域名、证书',
        '短信推送平台等第三方服务账号信息',
        '设计素材、内容素材',
    ]
    communication = [
        '每周项目沟通例会',
        '需求评审会、方案评审会、验收评审会',
        '日常沟通确认',
    ]

    if requirement_groups:
        requirement_rows = []
        for group in requirement_groups:
            requirement_rows.append([
                html.escape(group.get('module', '')),
                '<br/>'.join(html.escape(item) for item in group.get('items', [])),
            ])
        requirement_html = table(['模块', '功能内容'], requirement_rows)
    else:
        requirement_html = bullet_list(features)

    line_rows = []
    for item in line_items:
        line_rows.append([
            html.escape(item.get('module', '')),
            str(item.get('frontend_days', 0)),
            str(item.get('backend_days', 0)),
            str(item.get('ui_days', 0)),
            str(item.get('qa_days', 0)),
            str(item.get('total_days', 0)),
        ])

    role_rows = []
    for row in roles:
        role_rows.append([
            html.escape(row.get('role', '')),
            str(row.get('days', 0)),
        ])

    quote_html = (
        f'<p><strong>项目总人天：</strong>{total_days} 人天</p>'
        f'<p><strong>统一人天单价：</strong>1200 元/人天</p>'
        f'<p><strong>项目总价：</strong>{html.escape(format_currency(total_price))}（{html.escape(tax_note)}）</p>'
        + payment_bullets(payment_schedule)
    )
    period_html = bullet_list([
        f'项目周期：{project_weeks} 周（以收到项目预付款为启动时间）',
        f'设计阶段：{design_weeks} 周',
        f'开发测试：{develop_weeks} 周',
        f'验收周期：{accept_weeks} 周',
    ])

    sections = [
        f'<h1>{project_name}</h1>',
        f'<p class="meta">报价日期：{html.escape(today)}</p>',
        f'<p class="meta">乙方报价单位：{html.escape(vendor_name)}</p>',
        section('服务范围', bullet_list(service_scope)),
        section('需求内容', requirement_html),
        section('交付物', bullet_list(deliverables)),
        section('项目报价与付款方式', quote_html),
        section('模块人天明细', table(['模块', '前端人天', '后端人天', 'UI人天', '测试人天', '合计人天'], line_rows)),
        section('角色投入测算', table(['角色', '人天'], role_rows)),
        section('项目周期', period_html),
        section('验收标准', bullet_list(acceptance)),
        section('前置条件', bullet_list(prerequisites)),
        section('依赖资源', bullet_list(dependencies)),
        section('沟通机制', bullet_list(communication)),
    ]
    if assumptions:
        sections.append(section('备注', bullet_list(assumptions)))

    return f'''<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <style>
    body {{ font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; margin: 28px 34px; color: #222; line-height: 1.6; font-size: 12px; }}
    h1 {{ font-size: 20px; margin: 0 0 16px; text-align: center; font-weight: 700; }}
    .meta {{ margin: 3px 0; font-size: 11px; }}
    .section {{ margin-top: 14px; page-break-inside: avoid; }}
    .section-title {{ margin: 0 0 6px; font-size: 12px; font-weight: 700; }}
    p {{ margin: 4px 0; }}
    ul {{ margin: 4px 0 4px 20px; padding: 0; }}
    li {{ margin: 2px 0; }}
    table {{ width: 100%; border-collapse: collapse; margin: 6px 0 10px; font-size: 11px; }}
    th {{ background: #f5f5f5; border: 1px solid #888; padding: 6px 7px; text-align: left; }}
    td {{ border: 1px solid #888; padding: 6px 7px; vertical-align: top; }}
  </style>
</head>
<body>
{''.join(sections)}
</body>
</html>
'''


def main() -> None:
    parser = argparse.ArgumentParser(description='Render quotation JSON into a DOCX file via HTML + textutil.')
    parser.add_argument('--input-json', required=True, help='Path to quote JSON payload')
    parser.add_argument('--output-docx', required=True, help='Output DOCX path')
    parser.add_argument('--keep-html', help='Optional path to keep the intermediate HTML')
    args = parser.parse_args()

    payload = json.loads(Path(args.input_json).read_text(encoding='utf-8'))
    html_content = render_html(payload)

    output_docx = Path(args.output_docx)
    output_docx.parent.mkdir(parents=True, exist_ok=True)
    html_path = Path(args.keep_html) if args.keep_html else output_docx.with_suffix('.html')
    html_path.write_text(html_content, encoding='utf-8')

    if not shutil.which('textutil'):
        native_renderer = Path(__file__).with_name('render_manual_quote_docx.py')
        subprocess.run([
            sys.executable,
            str(native_renderer),
            '--input-json',
            args.input_json,
            '--output-docx',
            str(output_docx),
        ], check=True)
        print(f'Wrote DOCX quote to {output_docx}')
        if args.keep_html:
            print(f'Kept HTML at {html_path}')
        return

    subprocess.run([
        'textutil', '-convert', 'docx', str(html_path), '-output', str(output_docx)
    ], check=True)
    print(f'Wrote DOCX quote to {output_docx}')
    if args.keep_html:
        print(f'Kept HTML at {html_path}')


if __name__ == '__main__':
    main()
