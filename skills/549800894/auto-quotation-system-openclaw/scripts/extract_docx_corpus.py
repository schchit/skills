#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import zipfile
from collections import Counter
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET

NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}

SECTION_HINTS = [
    '服务范围', '需求内容', '功能需求', '非功能需求', '交付物', '项目报价', '付款方式',
    '项目周期', '验收标准', 'UI设计标准', '前置条件', '依赖资源', '沟通机制',
    '报价功能范围', '项目造价方案预估', '其他约定', '备注', '报价范围'
]

DOMAIN_KEYWORDS = {
    'ai': ['ai', '智能体', '知识库', '模型', 'deepseek', '大模型'],
    'miniapp': ['小程序', '公众号', '商户号'],
    'app': ['app', 'ios', 'android'],
    'platform': ['平台', '后台', 'saas', '管理系统', 'b2b'],
    'iot': ['硬件', 'rfid', '设备', '门店', '温度', '传感'],
    'crossborder': ['跨境', '香港', '海外', '澳洲', '信托'],
}


def normalize_space(text: str) -> str:
    text = text.replace('\u00a0', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def tokenize(text: str) -> list[str]:
    lowered = text.lower()
    tokens: list[str] = []
    for word in re.findall(r'[0-9a-z]{2,}', lowered):
        tokens.append(word)
    for chunk in re.findall(r'[\u4e00-\u9fff]{2,}', lowered):
        if len(chunk) <= 4:
            tokens.append(chunk)
            continue
        for size in (2, 3, 4):
            for idx in range(0, len(chunk) - size + 1):
                tokens.append(chunk[idx : idx + size])
    return tokens


def paragraph_text(paragraph: ET.Element) -> str:
    parts: list[str] = []
    for node in paragraph.findall('.//w:t', NS):
        if node.text:
            parts.append(node.text)
    return normalize_space(''.join(parts))


def extract_table(table: ET.Element) -> list[list[str]]:
    rows: list[list[str]] = []
    for tr in table.findall('./w:tr', NS):
        row: list[str] = []
        for tc in tr.findall('./w:tc', NS):
            cell_parts = []
            for p in tc.findall('./w:p', NS):
                text = paragraph_text(p)
                if text:
                    cell_parts.append(text)
            row.append('\n'.join(cell_parts).strip())
        if any(cell for cell in row):
            rows.append(row)
    return rows


def detect_sections(paragraphs: Iterable[str]) -> list[str]:
    found = []
    for text in paragraphs:
        if text in SECTION_HINTS:
            found.append(text)
    return found


def detect_domains(text: str) -> list[str]:
    lowered = text.lower()
    matched = []
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            matched.append(domain)
    return matched


def parse_docx(path: Path) -> dict:
    with zipfile.ZipFile(path) as zf:
        document_xml = zf.read('word/document.xml')
        root = ET.fromstring(document_xml)
        body = root.find('w:body', NS)
        if body is None:
            raise ValueError(f'No body found in {path}')

        blocks = []
        paragraphs: list[str] = []
        tables: list[list[list[str]]] = []
        image_count = 0

        for child in list(body):
            tag = child.tag.rsplit('}', 1)[-1]
            if tag == 'p':
                text = paragraph_text(child)
                if text:
                    paragraphs.append(text)
                    blocks.append({'type': 'paragraph', 'text': text})
                if child.findall('.//w:drawing', NS):
                    image_count += len(child.findall('.//w:drawing', NS))
            elif tag == 'tbl':
                table = extract_table(child)
                if table:
                    tables.append(table)
                    blocks.append({'type': 'table', 'rows': table})

        combined_text = '\n'.join(paragraphs)
        counter = Counter(tokenize(combined_text))
        title = paragraphs[0] if paragraphs else path.stem
        sections = detect_sections(paragraphs)

        return {
            'file_name': path.name,
            'file_path': str(path),
            'title': title,
            'paragraphs': paragraphs,
            'tables': tables,
            'image_count': image_count,
            'sections': sections,
            'domains': detect_domains(combined_text),
            'top_keywords': counter.most_common(30),
            'block_count': len(blocks),
        }


def build_summary(documents: list[dict]) -> dict:
    section_counter = Counter()
    domain_counter = Counter()
    keyword_counter = Counter()
    for doc in documents:
        section_counter.update(doc['sections'])
        domain_counter.update(doc['domains'])
        keyword_counter.update({k: v for k, v in doc['top_keywords']})

    return {
        'document_count': len(documents),
        'sections': section_counter.most_common(),
        'domains': domain_counter.most_common(),
        'keywords': keyword_counter.most_common(50),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Extract text, tables, and metadata from historical quotation DOCX files.')
    parser.add_argument('--input-dir', required=True, help='Directory containing .docx quotation files')
    parser.add_argument('--output', required=True, help='Output JSON path')
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output = Path(args.output)
    docs = []
    for path in sorted(input_dir.glob('*.docx')):
        try:
            docs.append(parse_docx(path))
        except Exception as exc:  # noqa: BLE001
            docs.append({
                'file_name': path.name,
                'file_path': str(path),
                'error': str(exc),
            })

    payload = {
        'source_dir': str(input_dir),
        'documents': docs,
        'summary': build_summary([doc for doc in docs if 'error' not in doc]),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Wrote corpus index for {len(docs)} documents to {output}')


if __name__ == '__main__':
    main()
