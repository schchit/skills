"""
Wyckoff 2.0 Volume Profile + Phase 检测
efinance 数据接口版
"""

import numpy as np
import pandas as pd
from scipy.signal import argrelmax, argrelmin

# 自动检测列名映射
def detect_columns(df: pd.DataFrame) -> dict:
    """自动检测并映射列名"""
    col_map = {}
    for c in df.columns:
        c_lower = str(c).lower()
        if '开' in c or 'open' in c_lower:
            col_map['open'] = c
        elif '收' in c or 'close' in c_lower:
            col_map['close'] = c
        elif '高' in c or 'high' in c_lower:
            col_map['high'] = c
        elif '低' in c or 'low' in c_lower:
            col_map['low'] = c
        elif '成交量' in c or 'volume' in c_lower or 'vol' in c_lower:
            col_map['volume'] = c
        elif '成交额' in c or 'amount' in c_lower:
            col_map['amount'] = c
        elif '日期' in c or 'date' in c_lower:
            col_map['date'] = c
        elif '代码' in c or 'code' in c_lower:
            col_map['code'] = c
        elif '名称' in c or 'name' in c_lower:
            col_map['name'] = c
    return col_map


def calculate_vp(df: pd.DataFrame, lookback: int = 60) -> dict:
    """计算 Volume Profile（VPOC/VAH/VAL/HVN/LVN）"""
    if len(df) < 20:
        return None

    # 自动检测列名
    cols = detect_columns(df)
    if not all(k in cols for k in ['close', 'high', 'low', 'volume']):
        print(f"  [warn] 列名检测失败: {df.columns.tolist()}")
        return None

    df = df.tail(lookback).copy()

    col_close = cols['close']
    col_high = cols['high']
    col_low = cols['low']
    col_volume = cols['volume']

    min_price = df[col_low].min()
    max_price = df[col_high].max()
    price_range = max_price - min_price
    if price_range == 0:
        return None

    n_bins = 50
    bin_size = price_range / n_bins
    volume_at_price = np.zeros(n_bins)

    for _, row in df.iterrows():
        low_bin = max(0, int((row[col_low] - min_price) / bin_size))
        high_bin = min(n_bins - 1, int((row[col_high] - min_price) / bin_size))
        vol_per_bin = row[col_volume] / (high_bin - low_bin + 1) if high_bin >= low_bin else row[col_volume]
        for b in range(low_bin, high_bin + 1):
            volume_at_price[b] += vol_per_bin

    price_levels = np.array([min_price + (i + 0.5) * bin_size for i in range(n_bins)])
    vpoc_idx = np.argmax(volume_at_price)
    vpoc_price = price_levels[vpoc_idx]
    vpoc_volume = volume_at_price[vpoc_idx]

    # Value Area（68.2%）
    total_volume = volume_at_price.sum()
    va_threshold = total_volume * 0.682
    cumsum = 0
    va_low_idx = vpoc_idx
    va_high_idx = vpoc_idx
    while cumsum < va_threshold and (va_low_idx > 0 or va_high_idx < n_bins - 1):
        low_vol = volume_at_price[va_low_idx - 1] if va_low_idx > 0 else 0
        high_vol = volume_at_price[va_high_idx + 1] if va_high_idx < n_bins - 1 else 0
        if low_vol > high_vol:
            cumsum += low_vol
            va_low_idx -= 1
        else:
            cumsum += high_vol
            va_high_idx += 1

    val_price = price_levels[va_low_idx]
    vah_price = price_levels[va_high_idx]

    # HVN / LVN
    hvn_indices = argrelmax(volume_at_price, order=3)[0]
    hvn_levels = [{'price': round(price_levels[i], 2), 'volume': round(volume_at_price[i], 0)}
                  for i in hvn_indices if volume_at_price[i] > vpoc_volume * 0.5]

    lvn_indices = argrelmin(volume_at_price, order=3)[0]
    lvn_levels = [{'price': round(price_levels[i], 2), 'volume': round(volume_at_price[i], 0)}
                  for i in lvn_indices if volume_at_price[i] < vpoc_volume * 0.3]

    current_price = df[col_close].iloc[-1]

    if current_price > vah_price:
        position = 'above_vah'
    elif current_price > vpoc_price:
        position = 'above_vpoc'
    elif current_price > val_price:
        position = 'within_va'
    elif current_price > vpoc_price:
        position = 'below_vpoc'
    else:
        position = 'below_val'

    return {
        'vpoc': round(vpoc_price, 2),
        'vpoc_vol': round(vpoc_volume, 0),
        'vah': round(vah_price, 2),
        'val': round(val_price, 2),
        'hvn': hvn_levels,
        'lvn': lvn_levels,
        'cur': round(current_price, 2),
        'position': position,
        'min_p': round(min_price, 2),
        'max_p': round(max_price, 2),
        'total_vol': round(total_volume, 0),
    }


def detect_phase(df: pd.DataFrame, lookback: int = 120) -> dict:
    """识别 Wyckoff Phase（A/B/C/D/E）"""
    if len(df) < 40:
        return {'phase': 'unknown', 'dir': 'unknown', 'conf': 0}

    # 自动检测列名
    cols = detect_columns(df)
    if not all(k in cols for k in ['close', 'high', 'low', 'volume']):
        return {'phase': 'unknown', 'dir': 'unknown', 'conf': 0}

    df = df.tail(lookback).copy()

    col_close = cols['close']
    col_high = cols['high']
    col_low = cols['low']
    col_volume = cols['volume']

    df['vol_ma20'] = df[col_volume].rolling(20).mean()
    df['ma20'] = df[col_close].rolling(20).mean()
    df['ma60'] = df[col_close].rolling(60).mean()

    cur = df[col_close].iloc[-1]
    ma20 = df['ma20'].iloc[-1]
    ma60 = df['ma60'].iloc[-1]
    vol_ma = df['vol_ma20'].iloc[-1]

    rolling_high = df[col_high].tail(60).max()
    rolling_low = df[col_low].tail(60).min()
    range_w = rolling_high - rolling_low
    pct = (cur - rolling_low) / range_w if range_w > 0 else 0.5

    vol_r = df[col_volume].iloc[-1] / vol_ma if vol_ma > 0 else 1
    avg_v = df[col_volume].tail(20).mean()

    # Phase E: 趋势（强烈看多/看空）
    if ma20 > ma60 and cur > ma20 and pct > 0.7:
        return {'phase': 'E', 'dir': 'uptrend', 'conf': 80 if vol_r > 1.2 else 65}
    if ma20 < ma60 and cur < ma20 and pct < 0.3:
        return {'phase': 'E', 'dir': 'downtrend', 'conf': 80 if vol_r > 1.2 else 65}

    # Phase E 延伸：均线多头但价格回调（健康回踩）
    if ma20 > ma60 and cur < ma20 and pct > 0.3:
        if vol_r < 0.9:
            return {'phase': 'E', 'dir': 'uptrend_pullback', 'conf': 70}
        else:
            return {'phase': 'C', 'dir': 'spring_test', 'conf': 65}
    if ma20 < ma60 and cur > ma20 and pct < 0.7:
        if vol_r < 0.9:
            return {'phase': 'E', 'dir': 'downtrend_pullback', 'conf': 70}
        else:
            return {'phase': 'C', 'dir': 'upthrust_test', 'conf': 65}

    # Phase A: 停止（量能突然放大）
    if vol_r > 2.0 and 0.2 < pct < 0.8:
        return {'phase': 'A', 'dir': 'stopping', 'conf': 70}

    # Phase B: 横盘（区间震荡）
    if 0.25 <= pct <= 0.7:
        if avg_v < vol_ma * 0.9:
            return {'phase': 'B', 'dir': 'accumulation', 'conf': 75}
        else:
            return {'phase': 'B', 'dir': 'distribution', 'conf': 70}

    # Phase C: 测试（Spring / Upthrust）
    if 0.10 <= pct <= 0.4:
        if vol_r > 1.2:
            return {'phase': 'C', 'dir': 'spring_test', 'conf': 68}
        else:
            return {'phase': 'B', 'dir': 'accumulation', 'conf': 65}
    if 0.6 <= pct <= 0.9:
        if vol_r > 1.2:
            return {'phase': 'C', 'dir': 'upthrust_test', 'conf': 68}
        else:
            return {'phase': 'B', 'dir': 'distribution', 'conf': 65}

    # Phase D: 突破
    if pct > 0.85 and vol_r > 1.2:
        return {'phase': 'D', 'dir': 'breakout_up', 'conf': 72}
    if pct < 0.10 and vol_r > 1.2:
        return {'phase': 'D', 'dir': 'breakout_down', 'conf': 72}

    # 兜底：价格在区间极低位（pct < 0.10 但无量）
    if pct < 0.10:
        return {'phase': 'C', 'dir': 'spring_test', 'conf': 60}

    return {'phase': 'unknown', 'dir': 'unknown', 'conf': 40}

    return {'phase': 'unknown', 'dir': 'unknown', 'conf': 40}


def score_stock(df: pd.DataFrame) -> dict:
    """
    综合评分（0~100）评估"积累末期候选"资格
    重构：区分积累（看多）和派发（看空），增加红蓝信号
    """
    prof = calculate_vp(df)
    ph = detect_phase(df)

    if not prof or ph['phase'] == 'unknown':
        return {
            'pass': False, 'score': 0,
            'red_flags': [], 'green_flags': [],
            'signals': [], 'rating': 'N',
            'verdict': '数据不足，无法判断',
            'phase': ph, 'profile': prof,
        }

    green = []   # 利好信号
    red = []     # 利空/风险信号
    sc = 0        # 基础分

    cols = detect_columns(df)
    vol_col = cols.get('volume', None)
    avg5 = df[vol_col].tail(5).mean() if vol_col else 0
    avg60 = df[vol_col].tail(60).mean() if vol_col else 0
    vol_ratio = (avg5 / avg60) if avg60 > 0 else 1

    # ========== 核心判断：Phase 类型 ==========

    # --- 危险信号（直接扣分/禁止买入）---
    if ph['phase'] == 'E' and ph['dir'] == 'downtrend':
        red.append(f"⚠️ Phase E 下跌趋势，坚决回避")
        sc -= 30

    if ph['phase'] in ['B', 'C'] and ph['dir'] in ['distribution', 'upthrust_test']:
        red.append(f"🔴 Phase {ph['phase']}({ph['dir']}) = 派发/诱多，不宜买入")
        sc -= 20

    if prof['cur'] < prof['val']:
        red.append(f"🔴 价格在VAL({prof['val']})下方，偏弱")
        sc -= 15

    if prof['cur'] < prof['vpoc']:
        red.append(f"🔴 价格在VPOC({prof['vpoc']})下方，重心偏下")
        sc -= 10

    # --- 利好信号（加分）---
    # Phase E 上涨趋势
    if ph['phase'] == 'E' and ph['dir'] == 'uptrend':
        green.append(f"✅ Phase E 上涨趋势（强度{ph['conf']}%）")
        sc += 20

    if ph['phase'] == 'E' and ph['dir'] == 'uptrend_pullback':
        green.append(f"✅ Phase E 上涨趋势回踩（强度{ph['conf']}%）")
        sc += 15

    # Phase B 积累（看多）
    if ph['phase'] == 'B' and ph['dir'] == 'accumulation':
        green.append(f"✅ Phase B 积累区间（机构收集）")
        sc += 25

    # Phase C Spring 测试（未确认）
    if ph['phase'] == 'C' and ph['dir'] == 'spring_test':
        green.append(f"⚠️ Phase C Spring测试（未确认，需等待阳线收回）")
        sc += 10  # 只给一半分，因为未确认

    # Phase D 向上突破
    if ph['phase'] == 'D' and ph['dir'] == 'breakout_up':
        green.append(f"✅ Phase D 向上突破（强度{ph['conf']}%）")
        sc += 30

    # 价格在 VPOC 上方
    if prof['cur'] > prof['vpoc']:
        green.append(f"✅ 价格在VPOC({prof['vpoc']})上方，重心偏多")
        sc += 20

    # 价格在 VAH 上方（强势）
    if prof['cur'] > prof['vah']:
        green.append(f"✅ 价格在VAH({prof['vah']})上方，强势")
        sc += 10

    # 成交量放大（机构信号）
    if avg5 > avg60 * 1.5:
        green.append(f"✅ 成交量放大（近5日均量是60日均量的{avg5/avg60:.0%}，机构入场）")
        sc += 15
    elif avg5 > avg60 * 1.2:
        green.append(f"🟡 成交量温和放大（{avg5/avg60:.0%}）")
        sc += 5

    # 下方 LVN 支撑
    if prof['lvn']:
        nearest_gap = min([abs(prof['cur'] - l['price']) / prof['cur'] for l in prof['lvn']])
        if nearest_gap < 0.05:
            nearest_lvn = min(prof['lvn'], key=lambda x: abs(prof['cur'] - x['price']))
            green.append(f"✅ 下方LVN@{nearest_lvn['price']}形成支撑")
            sc += 10

    # ========== 评分归一化 ==========
    sc = max(0, min(100, sc))

    # ========== 综合评级 ==========
    if red and any('🔴' in r for r in red):
        if sc >= 70:
            rating = 'B'
            verdict = '有风险但有机会，谨慎参与'
        elif sc >= 50:
            rating = 'C'
            verdict = '风险信号明确，不建议买入'
        else:
            rating = 'D'
            verdict = '风险过高，建议回避'
    elif sc >= 75:
        rating = 'S'
        verdict = '强势候选，重点关注'
    elif sc >= 60:
        rating = 'A'
        verdict = '满足买入条件，可以关注'
    elif sc >= 40:
        rating = 'B'
        verdict = '信号不明确，继续观察'
    else:
        rating = 'C'
        verdict = '信号偏弱，不宜买入'

    all_signals = green + red

    return {
        'pass': rating in ['S', 'A'],
        'score': sc,
        'rating': rating,
        'red_flags': red,
        'green_flags': green,
        'signals': all_signals,
        'verdict': verdict,
        'phase': ph,
        'profile': prof,
    }
