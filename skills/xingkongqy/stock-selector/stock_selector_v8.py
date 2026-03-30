#!/usr/bin/env python3
"""
【短线快刀客】选股脚本 v8.0 - 分阶段筛选优化版

优化策略：
1. 第 1 阶段：批量筛选涨跌幅 3-7%（快速过滤）
2. 汇总第 1 阶段结果
3. 第 2 阶段：筛选成交额 >1 亿
4. 第 3 阶段：筛选换手率 3-15%
5. 第 4 阶段：排除 ST、涨停
6. 如某阶段结果过多，继续分批处理

核心思想：先粗筛，再精筛，逐步缩小范围
"""

import json
import requests
import datetime
import os
import sys
import time

POOL_FILE = "/home/admin/openclaw/workspace/strategies/候选股票池.json"
BATCH_SIZE = 100  # 批量大小

def log(msg):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}", file=sys.stderr)

def get_batch_quotes(codes):
    """批量获取行情（腾讯财经）"""
    symbols = []
    for code in codes:
        if code.startswith('6'):
            symbols.append(f'sh{code}')
        else:
            symbols.append(f'sz{code}')
    
    symbol_str = ','.join(symbols)
    url = f"https://qt.gtimg.cn/q={symbol_str}"
    
    try:
        resp = requests.get(url, timeout=15)
        resp.encoding = 'gbk'
        lines = resp.text.strip().split('\n')
        
        results = {}
        for line in lines:
            parts = line.strip().split('~')
            if len(parts) >= 50:
                code = parts[2]
                results[code] = {
                    'code': code,
                    'name': parts[1],
                    'price': float(parts[3]) if parts[3] else 0,
                    'change_pct': float(parts[32]) if parts[32] else 0,
                    'amount_yi': float(parts[37]) / 10000,
                    'turnover_rate': float(parts[38]) if parts[38] else 0,
                    'high': float(parts[33]) if parts[33] else 0,
                    'low': float(parts[34]) if parts[34] else 0,
                    'open': float(parts[5]) if parts[5] else 0,
                    'prev_close': float(parts[2]) if parts[2] else 0,
                }
        return results
    except Exception as e:
        log(f"批量查询失败：{e}")
        return {}

def stage1_filter_change_pct(all_stocks):
    """
    第 1 阶段：筛选涨跌幅 3-7%
    这是最快的过滤条件，先大幅缩小范围
    """
    log("=" * 50)
    log("第 1 阶段：筛选涨跌幅 3-7%")
    log("=" * 50)
    
    total = len(all_stocks)
    matched = []
    
    # 分批处理
    for i in range(0, total, BATCH_SIZE):
        batch = all_stocks[i:i+BATCH_SIZE]
        codes = [s.get('code', '') for s in batch if s.get('code')]
        
        # 批量查询
        quotes = get_batch_quotes(codes)
        
        # 筛选涨跌幅
        for code, q in quotes.items():
            if 3 <= q['change_pct'] <= 7:
                matched.append(q)
        
        # 进度
        processed = min(i + BATCH_SIZE, total)
        log(f"进度：{processed}/{total} ({processed*100//total}%)，符合：{len(matched)}")
        time.sleep(0.05)
    
    log(f"第 1 阶段完成：{len(matched)}/{total} ({len(matched)*100//total}%)")
    return matched

def stage2_filter_amount(stage1_results):
    """
    第 2 阶段：筛选成交额 >1 亿
    数据已在第 1 阶段获取，直接内存筛选
    """
    log("=" * 50)
    log("第 2 阶段：筛选成交额 >1 亿")
    log("=" * 50)
    
    matched = [q for q in stage1_results if q['amount_yi'] > 1]
    
    log(f"第 2 阶段完成：{len(matched)}/{len(stage1_results)} ({len(matched)*100//max(len(stage1_results),1)}%)")
    return matched

def stage3_filter_turnover(stage2_results):
    """
    第 3 阶段：筛选换手率 3-15%
    数据已在第 1 阶段获取，直接内存筛选
    """
    log("=" * 50)
    log("第 3 阶段：筛选换手率 3-15%")
    log("=" * 50)
    
    matched = [q for q in stage2_results if 3 <= q['turnover_rate'] <= 15]
    
    log(f"第 3 阶段完成：{len(matched)}/{len(stage2_results)} ({len(matched)*100//max(len(stage2_results),1)}%)")
    return matched

def stage4_filter_exclusions(stage3_results):
    """
    第 4 阶段：排除 ST 股、涨停股
    说明：ST/*ST 已在候选池策略中排除（A 股龙渊王维护）
         涨停已在涨跌幅 3-7% 中排除（>9.8% 不符合）
    此阶段保留用于双重保险，但理论上不会过滤
    """
    log("=" * 50)
    log("第 4 阶段：排除 ST 股、涨停股（双重保险）")
    log("=" * 50)
    log("注：ST/*ST 已在候选池排除，涨停已在涨跌幅排除")
    
    matched = [q for q in stage3_results if 'ST' not in q['name'] and q['change_pct'] < 9.8]
    
    if len(matched) == len(stage3_results):
        log("✓ 候选池策略有效，无需额外过滤")
    else:
        log(f"⚠️ 发现 {len(stage3_results)-len(matched)} 只需要过滤的股票")
    
    log(f"第 4 阶段完成：{len(matched)}/{len(stage3_results)} ({len(matched)*100//max(len(stage3_results),1)}%)")
    return matched

def format_recommendations(results, top_n=3):
    """格式化推荐股票"""
    # 按涨幅排序
    results.sort(key=lambda x: x['change_pct'], reverse=True)
    top = results[:top_n]
    
    formatted = []
    for stock in top:
        target_price = round(stock['price'] * 1.03, 2)
        stop_loss = round(stock['price'] * 0.97, 2)
        formatted.append({
            'code': stock['code'],
            'name': stock['name'],
            'price': stock['price'],
            'change_pct': stock['change_pct'],
            'amount_yi': round(stock['amount_yi'], 2),
            'turnover_rate': round(stock['turnover_rate'], 2),
            'target_price': target_price,
            'stop_loss': stop_loss,
            'high': stock['high'],
            'low': stock['low'],
            'open': stock['open'],
        })
    
    return formatted

def main():
    start_time = datetime.datetime.now()
    log("=" * 60)
    log("【短线快刀客】选股脚本 v8.0（分阶段筛选优化版）")
    log("=" * 60)
    
    # 加载候选池
    log("加载候选池...")
    with open(POOL_FILE, 'r', encoding='utf-8') as f:
        pool = json.load(f)
    
    all_stocks = pool.get("stocks", [])
    log(f"候选池：{len(all_stocks)} 只股票")
    log("")
    
    # 第 1 阶段：筛选涨跌幅
    stage1_results = stage1_filter_change_pct(all_stocks)
    log("")
    
    if not stage1_results:
        log("❌ 第 1 阶段无符合股票，结束筛选")
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(json.dumps({
            'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'duration_seconds': duration,
            'stage1_matched': 0,
            'final_matched': 0,
            'recommendations': []
        }, ensure_ascii=False, indent=2))
        return
    
    # 第 2 阶段：筛选成交额
    stage2_results = stage2_filter_amount(stage1_results)
    log("")
    
    if not stage2_results:
        log("❌ 第 2 阶段无符合股票，结束筛选")
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(json.dumps({
            'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'duration_seconds': duration,
            'stage1_matched': len(stage1_results),
            'stage2_matched': 0,
            'final_matched': 0,
            'recommendations': []
        }, ensure_ascii=False, indent=2))
        return
    
    # 第 3 阶段：筛选换手率
    stage3_results = stage3_filter_turnover(stage2_results)
    log("")
    
    if not stage3_results:
        log("❌ 第 3 阶段无符合股票，结束筛选")
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(json.dumps({
            'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'duration_seconds': duration,
            'stage1_matched': len(stage1_results),
            'stage2_matched': len(stage2_results),
            'stage3_matched': 0,
            'final_matched': 0,
            'recommendations': []
        }, ensure_ascii=False, indent=2))
        return
    
    # 第 4 阶段：排除 ST、涨停
    final_results = stage4_filter_exclusions(stage3_results)
    log("")
    
    # 格式化推荐
    recommendations = format_recommendations(final_results, top_n=3)
    
    # 输出结果
    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "=" * 60)
    print(f"执行时间：{duration:.2f} 秒")
    print(f"候选池：{len(all_stocks)} 只")
    print(f"第 1 阶段（涨跌幅 3-7%）：{len(stage1_results)} 只")
    print(f"第 2 阶段（成交>1 亿）：{len(stage2_results)} 只")
    print(f"第 3 阶段（换手 3-15%）：{len(stage3_results)} 只")
    print(f"第 4 阶段（排除 ST/涨停）：{len(final_results)} 只")
    print(f"推荐股票：{len(recommendations)} 只")
    print("=" * 60)
    
    if recommendations:
        print("\n📈 推荐股票：")
        for i, stock in enumerate(recommendations, 1):
            print(f"\n{i}. {stock['code']} {stock['name']}")
            print(f"   涨幅：{stock['change_pct']}%")
            print(f"   现价：{stock['price']} 元")
            print(f"   成交：{stock['amount_yi']} 亿")
            print(f"   换手：{stock['turnover_rate']}%")
            print(f"   高点：{stock['high']} 元 | 低点：{stock['low']} 元")
            print(f"   建议买入：{stock['price']} 元")
            print(f"   止盈：{stock['target_price']} 元 (+3%)")
            print(f"   止损：{stock['stop_loss']} 元 (-3%)")
    else:
        print("\n❌ 今日无符合选股条件的股票")
        print("建议：空仓观望，等待明日机会")
    
    # JSON 输出
    output = {
        'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'duration_seconds': duration,
        'stages': {
            'total': len(all_stocks),
            'stage1_change_pct': len(stage1_results),
            'stage2_amount': len(stage2_results),
            'stage3_turnover': len(stage3_results),
            'stage4_exclusions': len(final_results)
        },
        'recommendations': recommendations
    }
    
    print("\n" + "=" * 60)
    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
