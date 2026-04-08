#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

PRICE_RE = re.compile(r'(?P<amount>\d+(?:\.\d+)?(?:\s*[~-]\s*\d+(?:\.\d+)?)?)\s*(?P<unit>万元|万|元)')
DAY_RE = re.compile(r'(?P<days>\d+(?:\.\d+)?)\s*(?:人/天|人天|天)')
MONTH_RE = re.compile(r'(?P<months>\d+(?:\.\d+)?)\s*/\s*月|(?P<month_only>\d+(?:\.\d+)?)$')
IGNORE_TITLES = {
    '总计', '合计', '其他', '收费', '备注', '费用', '小计', '上架费用合计：', '项目', '内容', '造价（单位：元）',
}
CATEGORY_HINTS = {
    '测试': 'testing',
    '上架': 'distribution',
    '应用商店': 'distribution',
    '开发者账号': 'distribution',
    '运维': 'maintenance',
    '部署': 'deployment',
    'ui': 'design',
    '设计': 'design',
    '接口': 'integration',
    'erp': 'integration',
    '短信': 'third_party',
    'token': 'third_party',
    'ocr': 'third_party',
    '开发': 'development',
    '后台': 'development',
    '小程序': 'development',
    'app': 'development',
    '服务器': 'infra',
    '云服务': 'infra',
    '存储': 'infra',
    '域名': 'infra',
    '证书': 'infra',
}


def normalize(text: str) -> str:
    text = str(text).replace('\u00a0', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def parse_amount(raw: str) -> dict | None:
    text = normalize(raw).replace(',', '')
    match = PRICE_RE.search(text)
    if not match:
        return None
    amount_text = match.group('amount').replace(' ', '')
    unit = match.group('unit')
    is_range = '-' in amount_text or '~' in amount_text
    if is_range:
        parts = re.split(r'[~-]', amount_text)
        values = [float(p) for p in parts if p]
        low = min(values)
        high = max(values)
        multiplier = 10000 if unit in {'万', '万元'} else 1
        return {
            'display': match.group(0),
            'amount_min': int(low * multiplier),
            'amount_max': int(high * multiplier),
            'unit': unit,
            'is_range': True,
        }
    value = float(amount_text)
    multiplier = 10000 if unit in {'万', '万元'} else 1
    amount = int(value * multiplier)
    return {
        'display': match.group(0),
        'amount_min': amount,
        'amount_max': amount,
        'unit': unit,
        'is_range': False,
    }


def parse_days(text: str) -> float | None:
    text = normalize(text)
    match = DAY_RE.search(text)
    if match:
        return float(match.group('days'))
    return None


def infer_category(text: str) -> str:
    lowered = normalize(text).lower()
    for hint, category in CATEGORY_HINTS.items():
        if hint in lowered:
            return category
    return 'unspecified'


def infer_channel(text: str) -> list[str]:
    lowered = normalize(text).lower()
    channels = []
    if '小程序' in lowered:
        channels.append('miniapp')
    if 'app' in lowered:
        channels.append('app')
    if 'h5' in lowered or 'web' in lowered or '网站' in lowered or '官网' in lowered:
        channels.append('web')
    if '后台' in lowered or '管理系统' in lowered or 'pc' in lowered:
        channels.append('backend')
    return channels


def looks_like_line_item(title: str) -> bool:
    title = normalize(title)
    if not title or title in IGNORE_TITLES:
        return False
    if len(title) == 1 and title.isdigit():
        return False
    if re.fullmatch(r'\d+(?:\.\d+)?\s*人\s*/\s*天', title) or re.fullmatch(r'\d+(?:\.\d+)?\s*人天', title):
        return False
    return True


def sample_from_table_row(doc: dict, row: list[str], header: list[str] | None) -> dict | None:
    cells = [normalize(c) for c in row]
    if not any(cells):
        return None

    amount_info = None
    amount_cell = ''
    for cell in reversed(cells):
        amount_info = parse_amount(cell)
        if amount_info:
            amount_cell = cell
            break
    if not amount_info:
        return None

    title_candidates = []
    note_candidates = []
    for idx, cell in enumerate(cells):
        if not cell or cell == amount_cell:
            continue
        header_name = normalize(header[idx]).lower() if header and idx < len(header) else ''
        if header_name in {'序号', '数量', '人数'}:
            continue
        if header_name in {'备注', '内容', '内容和规格', '项目说明'}:
            note_candidates.append(cell)
            continue
        title_candidates.append(cell)

    filtered_titles = [c for c in title_candidates if looks_like_line_item(c)]
    title = next((c for c in filtered_titles if not parse_days(c)), '')
    if not title:
        title = next(iter(filtered_titles), '')
    if not title:
        return None

    days = None
    for cell in cells:
        days = parse_days(cell)
        if days is not None:
            break

    return {
        'source_file': doc['file_path'],
        'source_title': doc['title'],
        'source_type': 'table',
        'title': title,
        'description': ' | '.join(note_candidates),
        'category': infer_category(' '.join(cells)),
        'channels': infer_channel(' '.join(cells)),
        'price': amount_info,
        'days': days,
        'raw_row': row,
    }


def sample_from_paragraph(doc: dict, paragraph: str) -> dict | None:
    text = normalize(paragraph)
    if '：' not in text and ':' not in text:
        return None
    amount_info = parse_amount(text)
    if not amount_info:
        return None
    parts = re.split(r'[：:]', text, maxsplit=1)
    if len(parts) != 2:
        return None
    title = normalize(parts[0])
    description = normalize(parts[1])
    if not looks_like_line_item(title):
        return None
    lowered_title = title.lower()
    lowered_desc = description.lower()
    if '数据规模' in title or '预计用户' in lowered_desc or '支持' in lowered_desc and '订单' in lowered_desc:
        return None
    if '条' in description and all(marker not in lowered_title for marker in ['报价', '费用', '开发', '上架', '运维', '部署', '短信']):
        return None
    if title.startswith('项目报价') or title.startswith('项目含税报价') or title.startswith('项目总价'):
        category = 'project_total'
    else:
        category = infer_category(title + ' ' + description)
    return {
        'source_file': doc['file_path'],
        'source_title': doc['title'],
        'source_type': 'paragraph',
        'title': title,
        'description': description,
        'category': category,
        'channels': infer_channel(title + ' ' + description),
        'price': amount_info,
        'days': parse_days(text),
        'raw_row': [paragraph],
    }


def role_row_sample(doc: dict, row: list[str], header: list[str] | None) -> dict | None:
    header_join = ' '.join(header or [])
    if '角色' not in header_join or '时长/月' not in header_join:
        return None
    cells = [normalize(c) for c in row]
    if len(cells) < 5:
        return None
    role = cells[1]
    work = cells[2]
    months = None
    tail = cells[-1]
    m = MONTH_RE.search(tail)
    if m:
        months = float(m.group('months') or m.group('month_only'))
    people = None
    if header:
        for idx, name in enumerate(header):
            if normalize(name) == '人数' and idx < len(cells):
                try:
                    people = int(float(cells[idx]))
                except ValueError:
                    people = None
                break
    if not role:
        return None
    return {
        'source_file': doc['file_path'],
        'source_title': doc['title'],
        'source_type': 'role_table',
        'title': role,
        'description': work,
        'category': 'role_effort',
        'channels': infer_channel(work),
        'price': None,
        'days': None,
        'people': people,
        'months': months,
        'raw_row': row,
    }


def extract_samples(doc: dict) -> list[dict]:
    samples = []
    for table in doc.get('tables', []):
        header = table[0] if table else None
        for row in table[1:] if header else table:
            role_sample = role_row_sample(doc, row, header)
            if role_sample:
                samples.append(role_sample)
            sample = sample_from_table_row(doc, row, header)
            if sample:
                samples.append(sample)
    for paragraph in doc.get('paragraphs', []):
        sample = sample_from_paragraph(doc, paragraph)
        if sample:
            samples.append(sample)
    return dedupe_samples(samples)


def dedupe_samples(samples: list[dict]) -> list[dict]:
    deduped = []
    seen = set()
    for sample in samples:
        key = (
            sample['source_file'],
            sample['source_type'],
            sample['title'],
            sample.get('price', {}).get('display') if sample.get('price') else None,
            sample.get('description', ''),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(sample)
    return deduped


def build_summary(samples: list[dict]) -> dict:
    by_category = {}
    by_source_type = {}
    priced = 0
    for sample in samples:
        by_category[sample['category']] = by_category.get(sample['category'], 0) + 1
        by_source_type[sample['source_type']] = by_source_type.get(sample['source_type'], 0) + 1
        if sample.get('price'):
            priced += 1
    return {
        'sample_count': len(samples),
        'priced_sample_count': priced,
        'categories': sorted(by_category.items(), key=lambda x: x[1], reverse=True),
        'source_types': sorted(by_source_type.items(), key=lambda x: x[1], reverse=True),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Build a structured quote sample library from extracted corpus JSON.')
    parser.add_argument('--corpus', required=True, help='Corpus JSON path from extract_docx_corpus.py')
    parser.add_argument('--output', required=True, help='Output sample library JSON path')
    args = parser.parse_args()

    corpus = json.loads(Path(args.corpus).read_text(encoding='utf-8'))
    all_samples = []
    for doc in corpus.get('documents', []):
        if 'error' in doc:
            continue
        all_samples.extend(extract_samples(doc))

    payload = {
        'source_corpus': args.corpus,
        'summary': build_summary(all_samples),
        'samples': all_samples,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Wrote {len(all_samples)} structured quote samples to {out}')


if __name__ == '__main__':
    main()
