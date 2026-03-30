#!/usr/bin/env python3
"""
A 股选股工具 - 主程序
支持分阶段筛选、批量查询、自动化选股
版本：v0.3.0
"""

import argparse
import json
import os
import sys
import requests
import datetime
from pathlib import Path

# 配置
DEFAULT_POOL_FILE = os.path.join(os.path.dirname(__file__), 'stock_pool.json')
DEFAULT_OUTPUT_DIR = os.environ.get('STOCK_OUTPUT_DIR', './.stock')

def load_stock_pool(pool_file=DEFAULT_POOL_FILE):
    """加载候选股票池"""
    if not os.path.exists(pool_file):
        print(f"❌ 股票池文件不存在：{pool_file}")
        sys.exit(1)
    
    with open(pool_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📊 加载股票池：{data.get('total', 0)} 只股票")
    return data

def get_batch_quotes(codes, batch_size=100):
    """批量获取行情（腾讯财经）"""
    results = []
    
    for i in range(0, len(codes), batch_size):
        batch = codes[i:i+batch_size]
        symbols = []
        for code in batch:
            if code.startswith('6'):
                symbols.append(f'sh{code}')
            else:
                symbols.append(f'sz{code}')
        
        symbol_str = ','.join(symbols)
        url = f'https://qt.gtimg.cn/q={symbol_str}'
        
        try:
            resp = requests.get(url, timeout=15)
            resp.encoding = 'gbk'
            lines = resp.text.strip().split('\n')
            
            for line in lines:
                parts = line.strip().split('~')
                if len(parts) >= 50:
                    code = parts[2]
                    results.append({
                        'code': code,
                        'name': parts[1],
                        'price': float(parts[3]) if parts[3] else 0,
                        'change_pct': float(parts[2]) if parts[2] else 0,
                        'amount': float(parts[42]) if len(parts) > 42 and parts[42] else 0,
                        'turnover_rate': float(parts[40]) if len(parts) > 40 and parts[40] else 0,
                        'market_cap': float(parts[46]) if len(parts) > 46 and parts[46] else 0,
                        'high': float(parts[33]) if len(parts) > 33 and parts[33] else 0,
                        'low': float(parts[34]) if len(parts) > 34 and parts[34] else 0,
                    })
            
            print(f"   进度：{i+len(batch)}/{len(codes)} ({(i+len(batch))*100//len(codes)}%)，符合：{len(results)}")
        except Exception as e:
            print(f"⚠️ 获取行情失败：{e}")
    
    return results

def stage1_filter_change_pct(quotes, min_pct=3, max_pct=7):
    """第 1 阶段：筛选涨跌幅"""
    filtered = [q for q in quotes if min_pct <= q['change_pct'] <= max_pct]
    print(f"✅ 第 1 阶段完成：{len(filtered)}/{len(quotes)} ({len(filtered)*100//max(len(quotes),1)}%)")
    return filtered

def stage2_filter_amount(quotes, min_amount=1):
    """第 2 阶段：筛选成交额（亿）"""
    filtered = [q for q in quotes if q['amount'] >= min_amount * 100000000]
    print(f"✅ 第 2 阶段完成：{len(filtered)}/{len(quotes)} ({len(filtered)*100//max(len(quotes),1)}%)")
    return filtered

def stage3_filter_turnover(quotes, min_rate=3, max_rate=15):
    """第 3 阶段：筛选换手率"""
    filtered = [q for q in quotes if min_rate <= q['turnover_rate'] <= max_rate]
    print(f"✅ 第 3 阶段完成：{len(filtered)}/{len(quotes)} ({len(filtered)*100//max(len(quotes),1)}%)")
    return filtered

def stage4_filter_exclusions(quotes):
    """第 4 阶段：排除 ST、涨停"""
    filtered = [q for q in quotes if 'ST' not in q['name'] and q['change_pct'] < 9.8]
    print(f"✅ 第 4 阶段完成：{len(filtered)}/{len(quotes)} ({len(filtered)*100//max(len(quotes),1)}%)")
    return filtered

def select_stocks(pool_file=DEFAULT_POOL_FILE, output_dir=DEFAULT_OUTPUT_DIR, top=3):
    """执行选股"""
    print("=" * 60)
    print("A 股选股工具 v0.3.0")
    print("=" * 60)
    print()
    
    # 加载股票池
    pool_data = load_stock_pool(pool_file)
    stocks = pool_data.get('stocks', [])
    codes = [s['code'] for s in stocks]
    
    print()
    print("🔍 开始选股...")
    print()
    
    # 第 1 阶段：获取行情并筛选涨跌幅
    print("第 1 阶段：筛选涨跌幅 3-7%")
    quotes = get_batch_quotes(codes)
    stage1_results = stage1_filter_change_pct(quotes)
    
    if not stage1_results:
        print("❌ 未找到符合条件的股票")
        return []
    
    # 第 2 阶段：筛选成交额
    print()
    print("第 2 阶段：筛选成交额>1 亿")
    stage2_results = stage2_filter_amount(stage1_results)
    
    if not stage2_results:
        print("❌ 未找到符合条件的股票")
        return []
    
    # 第 3 阶段：筛选换手率
    print()
    print("第 3 阶段：筛选换手率 3-15%")
    stage3_results = stage3_filter_turnover(stage2_results)
    
    if not stage3_results:
        print("❌ 未找到符合条件的股票")
        return []
    
    # 第 4 阶段：排除 ST、涨停
    print()
    print("第 4 阶段：排除 ST、涨停")
    final_results = stage4_filter_exclusions(stage3_results)
    
    if not final_results:
        print("❌ 未找到符合条件的股票")
        return []
    
    # 排序并推荐
    print()
    print("📊 选股完成！")
    print(f"   符合：{len(final_results)} 只")
    print(f"   推荐：{min(top, len(final_results))} 只")
    print()
    
    # 计算推荐分数
    for stock in final_results:
        score = (
            stock['change_pct'] * 10 +
            stock['turnover_rate'] * 2 +
            stock['amount'] / 100000000
        )
        stock['score'] = score
    
    # 按分数排序
    final_results.sort(key=lambda x: x['score'], reverse=True)
    recommended = final_results[:top]
    
    # 输出结果
    print("🎯 推荐股票：")
    print()
    for i, stock in enumerate(recommended, 1):
        print(f"{i}. {stock['code']} {stock['name']}")
        print(f"   涨幅：{stock['change_pct']:.2f}%")
        print(f"   成交：{stock['amount']/100000000:.2f}亿")
        print(f"   换手：{stock['turnover_rate']:.2f}%")
        print(f"   价格：{stock['price']:.2f}元")
        print(f"   高低：{stock['low']:.2f} - {stock['high']:.2f}元")
        print()
    
    # 保存结果
    os.makedirs(output_dir, exist_ok=True)
    result_file = os.path.join(output_dir, f'select_result_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    
    result_data = {
        'timestamp': datetime.datetime.now().isoformat(),
        'total_scanned': len(codes),
        'total_matched': len(final_results),
        'recommended': recommended,
        'strategy': 'overnight'
    }
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 结果已保存：{result_file}")
    print()
    
    return recommended

def main():
    parser = argparse.ArgumentParser(description='A 股选股工具 v0.3.0')
    subparsers = parser.add_subparsers(dest='command', help='子命令')
    
    # select 命令
    p_select = subparsers.add_parser('select', help='执行选股')
    p_select.add_argument('--pool', default=DEFAULT_POOL_FILE, help='股票池文件')
    p_select.add_argument('--output-dir', default=DEFAULT_OUTPUT_DIR, help='输出目录')
    p_select.add_argument('--top', type=int, default=3, help='推荐数量')
    p_select.set_defaults(func=lambda args: select_stocks(args.pool, args.output_dir, args.top))
    
    args = parser.parse_args()
    
    if args.command is None:
        # 默认执行选股
        select_stocks()
    else:
        args.func(args)

if __name__ == '__main__':
    main()
