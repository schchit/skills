#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import median

PRIMARY_DOMAINS = ['ai', 'miniapp', 'app', 'platform', 'iot', 'crossborder']


def sample_amount(sample: dict) -> float | None:
    price = sample.get('price')
    if not price:
        return None
    return (price['amount_min'] + price['amount_max']) / 2


def main() -> None:
    parser = argparse.ArgumentParser(description='Build domain-specific rate cards from quote samples and corpus metadata.')
    parser.add_argument('--corpus', required=True, help='Corpus JSON path')
    parser.add_argument('--sample-library', required=True, help='Sample library JSON path')
    parser.add_argument('--output', required=True, help='Output domain rate card JSON path')
    args = parser.parse_args()

    corpus = json.loads(Path(args.corpus).read_text(encoding='utf-8'))
    samples = json.loads(Path(args.sample_library).read_text(encoding='utf-8'))
    doc_domains = {
        doc['file_path']: doc.get('domains', [])
        for doc in corpus.get('documents', [])
        if 'error' not in doc
    }

    domain_docs = defaultdict(set)
    category_amounts = defaultdict(list)
    category_examples = defaultdict(list)
    channel_counts = defaultdict(lambda: defaultdict(int))

    for sample in samples.get('samples', []):
        amount = sample_amount(sample)
        if amount is None:
            continue
        source_file = sample['source_file']
        domains = doc_domains.get(source_file, [])
        for domain in domains:
            if domain not in PRIMARY_DOMAINS:
                continue
            domain_docs[domain].add(source_file)
            category_amounts[(domain, sample['category'])].append(amount)
            if len(category_examples[(domain, sample['category'])]) < 5:
                category_examples[(domain, sample['category'])].append({
                    'source_title': sample['source_title'],
                    'title': sample['title'],
                    'amount': int(amount),
                })
            for channel in sample.get('channels', []):
                channel_counts[domain][channel] += 1

    rate_cards = []
    for domain in PRIMARY_DOMAINS:
        categories = []
        for (d, category), amounts in sorted(category_amounts.items()):
            if d != domain:
                continue
            categories.append({
                'category': category,
                'sample_count': len(amounts),
                'median_price': int(median(amounts)),
                'min_price': int(min(amounts)),
                'max_price': int(max(amounts)),
                'examples': category_examples[(domain, category)],
            })
        if not categories:
            continue
        categories.sort(key=lambda item: (-item['sample_count'], item['category']))
        total_row = next((row for row in categories if row['category'] == 'project_total'), None)
        rate_cards.append({
            'domain': domain,
            'document_count': len(domain_docs[domain]),
            'project_total_median': total_row['median_price'] if total_row else None,
            'project_total_range': [total_row['min_price'], total_row['max_price']] if total_row else None,
            'common_channels': [
                {'channel': channel, 'count': count}
                for channel, count in sorted(channel_counts[domain].items(), key=lambda x: (-x[1], x[0]))
            ],
            'categories': categories,
        })

    payload = {
        'primary_domains': PRIMARY_DOMAINS,
        'rate_card_count': len(rate_cards),
        'rate_cards': rate_cards,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Wrote {len(rate_cards)} domain rate cards to {output}')


if __name__ == '__main__':
    main()
