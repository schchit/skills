#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import median

PROFILE_LEVELS = (
    'category+domains+channels',
    'category+domains',
    'category+channels',
    'category',
)


def sample_amount(sample: dict) -> float | None:
    price = sample.get('price')
    if not price:
        return None
    return (price['amount_min'] + price['amount_max']) / 2


def normalize_domains(domains: list[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(sorted(domains or ()))


def normalize_channels(channels: list[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(sorted(channels or ()))


def make_key(level: str, category: str, domains: tuple[str, ...], channels: tuple[str, ...]) -> str:
    return f"{level}|{category}|{','.join(domains)}|{','.join(channels)}"


def main() -> None:
    parser = argparse.ArgumentParser(description='Build stratified calibration profiles from quote samples and corpus domains.')
    parser.add_argument('--corpus', required=True, help='Corpus JSON path')
    parser.add_argument('--sample-library', required=True, help='Structured sample library JSON path')
    parser.add_argument('--output', required=True, help='Output calibration profile JSON path')
    args = parser.parse_args()

    corpus = json.loads(Path(args.corpus).read_text(encoding='utf-8'))
    sample_library = json.loads(Path(args.sample_library).read_text(encoding='utf-8'))
    doc_domains = {
        doc['file_path']: normalize_domains(doc.get('domains', []))
        for doc in corpus.get('documents', [])
        if 'error' not in doc
    }

    buckets: dict[str, list[dict]] = defaultdict(list)
    for sample in sample_library.get('samples', []):
        amount = sample_amount(sample)
        if amount is None:
            continue
        category = sample.get('category', 'unspecified')
        domains = doc_domains.get(sample['source_file'], ())
        channels = normalize_channels(sample.get('channels', []))

        bucket_specs = [
            ('category+domains+channels', domains, channels),
            ('category+domains', domains, ()),
            ('category+channels', (), channels),
            ('category', (), ()),
        ]
        for level, d, c in bucket_specs:
            buckets[make_key(level, category, d, c)].append({
                'amount': amount,
                'source_title': sample['source_title'],
                'title': sample['title'],
                'domains': list(domains),
                'channels': list(channels),
            })

    profiles = []
    for key, entries in sorted(buckets.items()):
        if len(entries) < 1:
            continue
        level, category, domains_str, channels_str = key.split('|', 3)
        amounts = sorted(entry['amount'] for entry in entries)
        profiles.append({
            'key': key,
            'level': level,
            'category': category,
            'domains': [item for item in domains_str.split(',') if item],
            'channels': [item for item in channels_str.split(',') if item],
            'sample_count': len(entries),
            'median_price': int(median(amounts)),
            'min_price': int(min(amounts)),
            'max_price': int(max(amounts)),
            'examples': [
                {
                    'source_title': entry['source_title'],
                    'title': entry['title'],
                    'amount': int(entry['amount']),
                }
                for entry in entries[:5]
            ],
        })

    payload = {
        'profile_levels': PROFILE_LEVELS,
        'profile_count': len(profiles),
        'profiles': profiles,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Wrote {len(profiles)} calibration profiles to {output}')


if __name__ == '__main__':
    main()
