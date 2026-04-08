#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path
from statistics import median

KEYWORD_WEIGHTS = {
    '登录': 1.0,
    '注册': 1.0,
    '搜索': 1.5,
    '列表': 1.0,
    '详情': 1.0,
    '支付': 3.0,
    '订单': 2.5,
    '会员': 2.0,
    '消息': 2.0,
    '审核': 1.5,
    '后台': 2.0,
    '管理': 1.5,
    '报表': 2.0,
    '推荐': 2.0,
    '地图': 2.0,
    'AI': 3.5,
    '智能体': 4.0,
    '知识库': 4.0,
    '大模型': 4.0,
    '语音': 3.0,
    'OCR': 3.0,
    '视频': 4.0,
    '直播': 4.0,
    '硬件': 4.0,
    '设备': 3.5,
    '接口': 2.5,
    'ERP': 3.0,
    '物流': 2.5,
    '多端': 3.0,
    '小程序': 1.5,
    'APP': 2.5,
    'Web': 2.0,
}

ROLE_RATES = {
    '产品经理': 1200,
    'UI设计': 1200,
    '前端开发': 1200,
    '后端开发': 1200,
    '测试': 1200,
    '项目管理': 1200,
    '部署运维': 1200,
}

STANDARD_DAY_RATE = 1200

PAYMENT_SCHEDULE = [
    ('项目启动', '50%'),
    ('功能验收', '40%'),
    ('质保结束', '10%'),
]

HEADING_ONLY = {
    '功能模块',
    '功能需求',
    '需求模块',
    '需求清单',
    '非功能需求',
    '功能列表',
    '需求说明',
}

CATEGORY_KEYWORDS = {
    'testing': ['测试', '压测', '漏洞扫描', '渗透'],
    'distribution': ['上架', '应用商店', '开发者账号'],
    'deployment': ['部署', '培训', '交付上线'],
    'maintenance': ['运维', '质保', '维护'],
    'design': ['ui', '设计', '原型', '视觉'],
    'integration': ['接口', 'erp', '对接', '支付', '短信', '物流', '企业微信', '公众号'],
    'infra': ['服务器', '域名', '证书', '存储', 'cdn', 'oss'],
    'development': ['开发', '后台', '前台', '小程序', 'app', 'web', '管理', '系统', '平台', '知识库', 'ai', '智能体'],
}

DOMAIN_KEYWORDS = {
    'ai': ['ai', '智能体', '知识库', '大模型', '模型', '问答'],
    'miniapp': ['小程序', '公众号', '商户号'],
    'app': ['app', 'ios', 'android'],
    'platform': ['平台', '后台', '系统', '管理'],
    'iot': ['硬件', '设备', '蓝牙', 'rfid', '传感', '体温'],
    'crossborder': ['跨境', '海外', '香港', '澳洲', '信托', '谷歌', '苹果应用商店'],
}


def normalize(text: str) -> str:
    text = text.replace('\u00a0', ' ')
    text = re.sub(r'\r\n?', '\n', text)
    return text.strip()


def read_requirement(path: Path) -> str:
    return normalize(path.read_text(encoding='utf-8'))


def normalize_project_label(text: str) -> str:
    cleaned = normalize(text)
    cleaned = cleaned.replace('项目报价方案', '').replace('报价方案', '').replace('项目', '')
    return cleaned.strip()


def extract_feature_lines(text: str) -> list[str]:
    features = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        line = re.sub(r'^[#>*\-\d\.\)\s]+', '', line).strip()
        if len(line) < 2:
            continue
        if line in HEADING_ONLY:
            continue
        if any(token in line for token in ['登录', '注册', '搜索', '列表', '详情', '支付', '订单', '会员', '消息', '流程', '页面', '管理', '系统', '平台', '小程序', 'APP', 'AI', '知识库', '报表', '后台', '部署', '接口', '权限']):
            features.append(line)
            continue
        if raw_line.lstrip().startswith(('-', '*')):
            features.append(line)
    if not features:
        features = [line.strip() for line in text.splitlines() if line.strip()]
    deduped = []
    seen = set()
    for item in features:
        if item not in seen:
            deduped.append(item)
            seen.add(item)
    return deduped


def extract_requirement_groups(text: str) -> list[dict]:
    groups: list[dict] = []
    current: dict | None = None
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        heading = re.sub(r'^#{1,6}\s*', '', stripped).strip()
        if raw_line.lstrip().startswith('## '):
            if current and current['items']:
                groups.append(current)
            current = {'module': heading, 'items': []}
            continue
        if raw_line.lstrip().startswith(('-', '*')):
            item = re.sub(r'^[*-]\s*', '', stripped).strip()
            if not current:
                current = {'module': '需求内容', 'items': []}
            if item:
                current['items'].append(item)
    if current and current['items']:
        groups.append(current)
    return groups


def extract_billable_modules(text: str, requirement_groups: list[dict]) -> list[str]:
    modules = []
    seen = set()
    for group in requirement_groups:
        module = normalize(group.get('module', ''))
        if not module or module in HEADING_ONLY or module in seen:
            continue
        modules.append(module)
        seen.add(module)
    if modules:
        return modules
    return extract_feature_lines(text)


def infer_category(text: str) -> str:
    lowered = text.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            return category
    return 'development'


def infer_channels(text: str) -> list[str]:
    lowered = text.lower()
    channels = []
    if '小程序' in lowered:
        channels.append('miniapp')
    if 'app' in lowered:
        channels.append('app')
    if 'web' in lowered or 'h5' in lowered or '网站' in lowered or '官网' in lowered:
        channels.append('web')
    if '后台' in lowered or '管理系统' in lowered or 'pc' in lowered:
        channels.append('backend')
    return channels


def infer_project_domains(text: str) -> list[str]:
    lowered = text.lower()
    domains = []
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            domains.append(domain)
    return domains


def estimate_feature_days(feature: str) -> float:
    score = 0.8
    for keyword, weight in KEYWORD_WEIGHTS.items():
        if keyword.lower() in feature.lower():
            score += weight
    score += min(feature.count('、') + feature.count('/') + feature.count('及') * 0.5, 3)
    return round(max(1.0, score), 1)


def build_line_items(
    features: list[str],
    project_domains: list[str],
    sample_library: dict | None = None,
    profiles: dict | None = None,
    rate_cards: dict | None = None,
) -> list[dict]:
    items = []
    for feature in features:
        complexity = estimate_feature_days(feature)
        frontend_days = math.ceil(complexity * 0.35)
        backend_days = math.ceil(complexity * 0.4)
        ui_days = math.ceil(complexity * 0.15)
        qa_days = math.ceil(complexity * 0.1)
        category = infer_category(feature)
        channels = infer_channels(feature)
        total_days = frontend_days + backend_days + ui_days + qa_days
        items.append({
            'module': feature,
            'category': category,
            'channels': channels,
            'complexity': complexity,
            'frontend_days': frontend_days,
            'backend_days': backend_days,
            'ui_days': ui_days,
            'qa_days': qa_days,
            'total_days': total_days,
            'subtotal': total_days * STANDARD_DAY_RATE,
            'calibration': {
                'method': 'standard_day_rate',
                'reference': {'day_rate': STANDARD_DAY_RATE},
            },
        })
    return items


def load_sample_library(path: Path | None) -> dict | None:
    if not path or not path.exists():
        return None
    return json.loads(path.read_text(encoding='utf-8'))


def load_profiles(path: Path | None) -> dict | None:
    if not path or not path.exists():
        return None
    payload = json.loads(path.read_text(encoding='utf-8'))
    payload['profile_map'] = {profile['key']: profile for profile in payload.get('profiles', [])}
    return payload


def load_rate_cards(path: Path | None) -> dict | None:
    if not path or not path.exists():
        return None
    payload = json.loads(path.read_text(encoding='utf-8'))
    payload['rate_card_map'] = {card['domain']: card for card in payload.get('rate_cards', [])}
    return payload


def sample_amount(sample: dict) -> float | None:
    price = sample.get('price')
    if not price:
        return None
    return (price['amount_min'] + price['amount_max']) / 2


def category_reference_price(category: str, channels: list[str], sample_library: dict | None) -> dict | None:
    if not sample_library:
        return None
    priced_samples = []
    for sample in sample_library.get('samples', []):
        amount = sample_amount(sample)
        if amount is None:
            continue
        if sample.get('category') != category:
            continue
        if category == 'project_total':
            continue
        priced_samples.append(sample)
    if not priced_samples:
        return None

    channel_matched = []
    requested = set(channels)
    for sample in priced_samples:
        sample_channels = set(sample.get('channels', []))
        if requested and sample_channels & requested:
            channel_matched.append(sample)
    chosen = channel_matched or priced_samples
    amounts = [sample_amount(sample) for sample in chosen if sample_amount(sample) is not None]
    if not amounts:
        return None
    return {
        'sample_count': len(chosen),
        'median_price': int(median(amounts)),
        'titles': [sample['title'] for sample in chosen[:5]],
    }


def profile_reference_price(category: str, project_domains: list[str], channels: list[str], profiles: dict | None) -> dict | None:
    if not profiles:
        return None
    project_domain_set = set(project_domains)
    channel_set = set(channels)
    best_profile = None
    best_score = -1.0
    for profile in profiles.get('profiles', []):
        if profile.get('category') != category:
            continue
        profile_domains = set(profile.get('domains', []))
        profile_channels = set(profile.get('channels', []))
        sample_count = profile.get('sample_count', 0)
        domain_overlap = len(project_domain_set & profile_domains)
        channel_overlap = len(channel_set & profile_channels)
        score = 0.0
        if profile['level'] == 'category+domains+channels':
            score += 4
        elif profile['level'] == 'category+domains':
            score += 3
        elif profile['level'] == 'category+channels':
            score += 2
        else:
            score += 1
        score += domain_overlap * 2
        score += channel_overlap * 1.5
        if project_domain_set and profile_domains and not domain_overlap:
            score -= 2
        if channel_set and profile_channels and not channel_overlap:
            score -= 1
        score += min(sample_count, 6) * 0.25
        if sample_count < 2 and profile['level'] != 'category':
            score -= 2.5
        if score > best_score:
            best_score = score
            best_profile = profile
    return best_profile


def domain_rate_card_reference(category: str, project_domains: list[str], rate_cards: dict | None) -> dict | None:
    if not rate_cards:
        return None
    best = None
    for domain in project_domains:
        card = rate_cards.get('rate_card_map', {}).get(domain)
        if not card:
            continue
        category_row = next((row for row in card.get('categories', []) if row['category'] == category), None)
        if not category_row:
            continue
        candidate = {
            'domain': domain,
            'document_count': card.get('document_count', 0),
            'project_total_median': card.get('project_total_median'),
            **category_row,
        }
        if not best or candidate['sample_count'] > best['sample_count']:
            best = candidate
    return best


def calibrate_subtotal(
    feature: str,
    category: str,
    channels: list[str],
    project_domains: list[str],
    complexity: float,
    heuristic_subtotal: int,
    sample_library: dict | None,
    profiles: dict | None,
    rate_cards: dict | None,
) -> dict:
    profile = profile_reference_price(category, project_domains, channels, profiles)
    if profile:
        complexity_factor = max(0.55, min(1.8, complexity / 3.0))
        reference_subtotal = int(profile['median_price'] * complexity_factor)
        blended = int(round(heuristic_subtotal * 0.55 + reference_subtotal * 0.45))
        floor = int(heuristic_subtotal * 0.75)
        ceiling = int(heuristic_subtotal * 2.0)
        subtotal = max(floor, min(blended, ceiling))
        return {
            'method': 'profile_calibrated',
            'reference': {
                'level': profile['level'],
                'category': category,
                'domains': profile['domains'],
                'channels': profile['channels'],
                'median_price': profile['median_price'],
                'sample_count': profile['sample_count'],
                'sample_titles': [example['title'] for example in profile.get('examples', [])],
                'complexity_factor': round(complexity_factor, 2),
                'reference_subtotal': reference_subtotal,
            },
            'subtotal': subtotal,
        }

    rate_card = domain_rate_card_reference(category, project_domains, rate_cards)
    if rate_card:
        complexity_factor = max(0.55, min(1.8, complexity / 3.0))
        reference_subtotal = int(rate_card['median_price'] * complexity_factor)
        blended = int(round(heuristic_subtotal * 0.65 + reference_subtotal * 0.35))
        floor = int(heuristic_subtotal * 0.75)
        ceiling = int(heuristic_subtotal * 1.9)
        subtotal = max(floor, min(blended, ceiling))
        return {
            'method': 'domain_rate_card',
            'reference': {
                'domain': rate_card['domain'],
                'category': category,
                'median_price': rate_card['median_price'],
                'sample_count': rate_card['sample_count'],
                'project_total_median': rate_card.get('project_total_median'),
                'complexity_factor': round(complexity_factor, 2),
                'reference_subtotal': reference_subtotal,
                'sample_titles': [example['title'] for example in rate_card.get('examples', [])],
            },
            'subtotal': subtotal,
        }

    reference = category_reference_price(category, channels, sample_library)
    if not reference:
        return {
            'method': 'heuristic_only',
            'reference': None,
            'subtotal': heuristic_subtotal,
        }

    complexity_factor = max(0.55, min(1.8, complexity / 3.0))
    reference_subtotal = int(reference['median_price'] * complexity_factor)
    blended = int(round(heuristic_subtotal * 0.6 + reference_subtotal * 0.4))
    floor = int(heuristic_subtotal * 0.75)
    ceiling = int(heuristic_subtotal * 1.8)
    subtotal = max(floor, min(blended, ceiling))
    return {
        'method': 'sample_calibrated',
        'reference': {
            'category': category,
            'domains': project_domains,
            'channels': channels,
            'median_price': reference['median_price'],
            'sample_count': reference['sample_count'],
            'sample_titles': reference['titles'],
            'complexity_factor': round(complexity_factor, 2),
            'reference_subtotal': reference_subtotal,
        },
        'subtotal': subtotal,
    }


def load_corpus(path: Path | None) -> dict | None:
    if not path or not path.exists():
        return None
    return json.loads(path.read_text(encoding='utf-8'))


def similar_documents(requirement: str, corpus: dict | None, limit: int = 5) -> list[dict]:
    if not corpus:
        return []
    req_tokens = Counter()
    for token in re.findall(r'[0-9A-Za-z]{2,}|[\u4e00-\u9fff]{2,4}', requirement.lower()):
        req_tokens[token] += 1
    ranked = []
    for doc in corpus.get('documents', []):
        if 'error' in doc:
            continue
        score = 0
        doc_keywords = dict(doc.get('top_keywords', []))
        doc_title = doc.get('title', '').lower()
        for token, count in req_tokens.items():
            score += count * doc_keywords.get(token, 0)
            if token in doc_title:
                score += 5
        if score > 0:
            ranked.append({
                'title': doc['title'],
                'file_path': doc['file_path'],
                'score': score,
                'sections': doc.get('sections', []),
                'domains': doc.get('domains', []),
            })
    ranked.sort(key=lambda item: item['score'], reverse=True)
    return ranked[:limit]


def summarize_roles(line_items: list[dict], target_total: int | None = None) -> list[dict]:
    totals = {
        '产品经理': 0,
        'UI设计': 0,
        '前端开发': 0,
        '后端开发': 0,
        '测试': 0,
        '项目管理': max(2, math.ceil(len(line_items) * 0.5)),
        '部署运维': 2,
    }
    for item in line_items:
        totals['UI设计'] += item['ui_days']
        totals['前端开发'] += item['frontend_days']
        totals['后端开发'] += item['backend_days']
        totals['测试'] += item['qa_days']
        totals['产品经理'] += max(1, math.ceil((item['frontend_days'] + item['backend_days']) / 6))

    rows = []
    for role, days in totals.items():
        rows.append({
            'role': role,
            'days': days,
            'rate': STANDARD_DAY_RATE,
            'base_rate': ROLE_RATES[role],
            'subtotal': days * STANDARD_DAY_RATE,
        })
    return rows


def format_currency(amount: int) -> str:
    return f'{amount:,} 元'


def select_rate_cards(project_domains: list[str], rate_cards: dict | None) -> list[dict]:
    if not rate_cards:
        return []
    cards = []
    for domain in project_domains:
        card = rate_cards.get('rate_card_map', {}).get(domain)
        if card:
            cards.append(card)
    return cards


def choose_docx_renderer(requested: str) -> str:
    if requested in {'native', 'html'}:
        return requested
    if sys.platform != 'darwin':
        return 'native'
    if shutil.which('textutil'):
        return 'html'
    return 'native'


def build_markdown(
    project_name: str,
    features: list[str],
    line_items: list[dict],
    role_rows: list[dict],
    similar: list[dict],
    matched_rate_cards: list[dict] | None = None,
) -> str:
    total_days = sum(row['days'] for row in role_rows)
    total = total_days * STANDARD_DAY_RATE
    weeks = max(4, math.ceil(total_days / 5 / 2))
    lines = [
        f'# {project_name} 报价草案',
        '',
        '## 1. 报价结论',
        '',
        f'- 预估总价：{format_currency(total)}',
        f'- 总人天：{total_days} 人天',
        f'- 统一人天单价：{STANDARD_DAY_RATE} 元/人天',
        f'- 预估周期：{weeks} 周',
        '- 适用前提：需求基于当前输入文档，未包含新增需求、第三方付费接口、硬件采购与大规模性能压测费用。',
        '',
        '## 2. 需求摘要',
        '',
    ]
    for feature in features:
        lines.append(f'- {feature}')
    if matched_rate_cards:
        lines.extend(['', '匹配领域价卡：'])
        for card in matched_rate_cards:
            lines.append(f"- `{card['domain']}`：样本文档 {card['document_count']} 份。")
    lines.extend(['', '## 3. 模块人天明细', '', '| 模块 | 前端人天 | 后端人天 | UI人天 | 测试人天 | 合计人天 |', '| --- | ---: | ---: | ---: | ---: | ---: |'])
    for item in line_items:
        lines.append(f"| {item['module']} | {item['frontend_days']} | {item['backend_days']} | {item['ui_days']} | {item['qa_days']} | {item['total_days']} |")
    lines.extend(['', '## 4. 角色投入测算', '', '| 角色 | 人天 |', '| --- | ---: |'])
    for row in role_rows:
        lines.append(f"| {row['role']} | {row['days']} |")
    lines.extend(['', '## 5. 付款方式建议', ''])
    for stage, percent in PAYMENT_SCHEDULE:
        lines.append(f'- {stage}：{percent}')
    lines.extend(['', '## 6. 交付与边界', '', '- 交付物：需求梳理说明、UI 设计稿、前后端代码、测试记录、部署说明。', '- 不含项：服务器、域名、短信、OCR/大模型 token、第三方 SaaS 订阅、应用市场上架费。', '- 变更机制：超出当前范围的新增需求，按补充评估的人天与单价另行报价。'])
    if similar:
        lines.extend(['', '## 7. 历史相似案例', ''])
        for doc in similar:
            lines.append(f"- {doc['title']} | 相似度分数：{doc['score']} | 领域：{', '.join(doc['domains']) or '未标注'} | 来源：{doc['file_path']}")
    lines.extend(['', '## 8. 待确认事项', '', '- 是否需要管理后台、运营后台或多角色权限。', '- 是否包含第三方接口对接、支付、消息推送、地图、OCR、知识库或智能体能力。', '- 是否需要正式 Word 排版版报价单，或仅需 Markdown/结构化 JSON 输出。'])
    return '\n'.join(lines) + '\n'


def main() -> None:
    parser = argparse.ArgumentParser(description='Generate a quotation draft from markdown requirements.')
    parser.add_argument('--input', required=True, help='Path to requirement markdown/txt file')
    parser.add_argument('--project-name', default='项目', help='Project name used in the quote title')
    parser.add_argument('--corpus', help='Optional corpus JSON path from extract_docx_corpus.py')
    parser.add_argument('--sample-library', help='Optional structured sample library JSON path')
    parser.add_argument('--profiles', help='Optional stratified calibration profiles JSON path')
    parser.add_argument('--rate-cards', help='Optional domain rate cards JSON path')
    parser.add_argument('--vendor-name', default='自动报价系统', help='Vendor name for rendered quotation documents')
    parser.add_argument('--quote-date', help='Quotation date shown in rendered documents, e.g. 2026-04-07')
    parser.add_argument('--tax-note', default='含税与否以最终商务确认版本为准', help='Tax note shown in rendered documents')
    parser.add_argument('--output-md', required=True, help='Output markdown path')
    parser.add_argument('--output-json', required=True, help='Output JSON path')
    parser.add_argument('--output-docx', help='Optional output DOCX path')
    parser.add_argument('--keep-html', help='Optional path for intermediate HTML when rendering DOCX')
    parser.add_argument('--docx-renderer', choices=['auto', 'native', 'html'], default='auto', help='DOCX renderer to use. Default auto picks native on Windows/OpenClaw and html on macOS when textutil exists.')
    args = parser.parse_args()

    requirement_path = Path(args.input)
    requirement = read_requirement(requirement_path)
    requirement_groups = extract_requirement_groups(requirement)
    features = extract_billable_modules(requirement, requirement_groups)
    normalized_project_name = normalize_project_label(args.project_name)
    if len(features) > 1:
        filtered = []
        for feature in features:
            normalized_feature = normalize_project_label(feature)
            if normalized_feature and normalized_feature == normalized_project_name:
                continue
            filtered.append(feature)
        features = filtered
    project_domains = infer_project_domains(requirement)
    sample_library = load_sample_library(Path(args.sample_library)) if args.sample_library else None
    profiles = load_profiles(Path(args.profiles)) if args.profiles else None
    rate_cards = load_rate_cards(Path(args.rate_cards)) if args.rate_cards else None
    matched_rate_cards = select_rate_cards(project_domains, rate_cards)
    line_items = build_line_items(
        features,
        project_domains=project_domains,
        sample_library=sample_library,
        profiles=profiles,
        rate_cards=rate_cards,
    )
    role_rows = summarize_roles(line_items)
    total_days = sum(row['days'] for row in role_rows)
    total = total_days * STANDARD_DAY_RATE
    corpus = load_corpus(Path(args.corpus)) if args.corpus else None
    similar = similar_documents(requirement, corpus)

    payload = {
        'project_name': args.project_name,
        'vendor_name': args.vendor_name,
        'quote_date': args.quote_date,
        'tax_note': args.tax_note,
        'input_file': str(requirement_path),
        'feature_count': len(features),
        'features': features,
        'requirement_groups': requirement_groups,
        'project_domains': project_domains,
        'matched_rate_cards': matched_rate_cards,
        'line_items': line_items,
        'roles': role_rows,
        'payment_schedule': PAYMENT_SCHEDULE,
        'day_rate': STANDARD_DAY_RATE,
        'service_scope': [
            '产品需求梳理',
            '技术方案设计',
            '软件设计开发',
            '测试与上线支持',
        ],
        'deliverables': [
            '产品文档/需求说明',
            'UI设计稿',
            '前后端源代码',
            '测试记录与部署文档',
        ],
        'project_timeline': [
            f'项目周期：{max(4, math.ceil(total_days / 5 / 2))} 周',
            '设计阶段：1 周',
            f'开发测试：{max(2, math.ceil(total_days / 10))} 周',
            '验收阶段：1 周',
        ],
        'acceptance': [
            '默认在我方测试环境进行验收。',
            '验收以当前确认的需求范围和流程闭环为准。',
            '超出当前报价范围的新增需求，需补充评估后单独报价。',
        ],
        'prerequisites': [
            '需求资料、账号权限及第三方配置需按约定时间提供。',
            '如涉及第三方协作，需确保沟通链路畅通。',
        ],
        'dependencies': [
            '服务器、域名、证书',
            '支付、消息通知等第三方账号与配置权限',
            '设计素材、业务内容素材',
        ],
        'communication': [
            '每周项目沟通例会',
            '需求评审会、方案评审会、验收评审会',
            '日常问题在线沟通确认',
        ],
        'similar_documents': similar,
        'sample_library_used': str(Path(args.sample_library)) if args.sample_library else None,
        'profiles_used': str(Path(args.profiles)) if args.profiles else None,
        'rate_cards_used': str(Path(args.rate_cards)) if args.rate_cards else None,
        'total_days': total_days,
        'total_price': total,
        'assumptions': [
            '当前估算基于输入文档的显式需求项',
            '脑图图片需要先转换为结构化文字后再估算',
            '第三方采购成本与云资源成本默认不含在开发报价内',
        ],
    }

    output_md = Path(args.output_md)
    output_json = Path(args.output_json)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(
        build_markdown(args.project_name, features, line_items, role_rows, similar, matched_rate_cards=matched_rate_cards),
        encoding='utf-8',
    )
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Wrote markdown quote to {output_md}')
    print(f'Wrote json quote data to {output_json}')

    if args.output_docx:
        renderer = choose_docx_renderer(args.docx_renderer)
        render_script = Path(__file__).with_name('render_manual_quote_docx.py' if renderer == 'native' else 'render_quote_docx.py')
        command = [
            sys.executable,
            str(render_script),
            '--input-json',
            str(output_json),
            '--output-docx',
            args.output_docx,
        ]
        if renderer == 'html' and args.keep_html:
            command.extend(['--keep-html', args.keep_html])
        subprocess.run(command, check=True)


if __name__ == '__main__':
    main()
