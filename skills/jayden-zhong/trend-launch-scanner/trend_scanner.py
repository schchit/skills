#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
趋势启动扫描器
基于对照组验证的规律，筛选当前处于上升趋势初期的潜力股
"""
import pandas as pd
import numpy as np
import requests
import time
import random
import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("C:/Users/Administrator/.qclaw/workspace-ag01/data/trend_scan")
DATA_DIR.mkdir(parents=True, exist_ok=True)


def fetch_kline_tencent(code, days=100):
    """使用腾讯API获取前复权日K线"""
    code = str(code).zfill(6)
    symbol = "sh" + code if code.startswith("6") else "sz" + code
    
    url = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
    params = {
        "_var": "kline_dayqfq",
        "param": f"{symbol},day,,,{days},qfq",
        "r": str(random.random())
    }
    
    try:
        r = requests.get(url, params=params, timeout=10)
        text = r.text
        json_str = text.split("=")[1]
        data = json.loads(json_str)
        
        if data.get("code") != 0:
            return pd.DataFrame()
        
        kline_data = data.get("data", {}).get(symbol, {}).get("qfqday", [])
        
        if not kline_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(kline_data, columns=["date", "open", "close", "high", "low", "volume"])
        
        for col in ["open", "close", "high", "low", "volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)
        
        return df
    except:
        return pd.DataFrame()


def add_indicators(df):
    """添加技术指标"""
    closes = df["close"]
    
    df["ma5"] = closes.rolling(5).mean()
    df["ma10"] = closes.rolling(10).mean()
    df["ma20"] = closes.rolling(20).mean()
    
    # RSI
    delta = closes.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    df["rsi"] = 100 - 100 / (1 + gain / loss.replace(0, 1e-9))
    
    # MACD
    ema12 = closes.ewm(span=12, adjust=False).mean()
    ema26 = closes.ewm(span=26, adjust=False).mean()
    df["dif"] = ema12 - ema26
    df["dea"] = df["dif"].ewm(span=9, adjust=False).mean()
    df["hist"] = (df["dif"] - df["dea"]) * 2
    
    # 量比
    df["vol_ratio"] = df["volume"] / df["volume"].rolling(5).mean()
    
    # 布林带
    df["boll_mid"] = closes.rolling(20).mean()
    df["boll_std"] = closes.rolling(20).std()
    df["boll_pos"] = (closes - df["boll_mid"]) / (df["boll_std"] * 2 + 1e-9)
    
    return df


def calc_trend_score(df):
    """
    计算趋势启动评分（基于对照组验证的规律）
    
    核心信号（按区分度排序）：
    1. MACD柱线为正（+26%）— 权重25分
    2. 价格在MA20上方（+21%）— 权重20分
    3. RSI在上升（+19%）— 权重15分
    4. RSI>50（+18%）— 权重15分
    5. 窗口内价格上升（+18%）— 权重10分
    6. 均线多头排列（+16%）— 权重10分
    7. MACD柱线在增大（+15%）— 权重5分
    """
    if len(df) < 25:
        return None
    
    last = df.iloc[-1]
    prev5 = df.iloc[-6:-1]  # 前5天
    
    score = 0
    signals = {}
    
    # 1. MACD柱线为正（25分）
    if last["hist"] > 0:
        score += 25
        signals["macd_hist_pos"] = 1
    else:
        signals["macd_hist_pos"] = 0
    
    # 2. 价格在MA20上方（20分）
    if last["close"] > last["ma20"]:
        score += 20
        signals["above_ma20"] = 1
    else:
        signals["above_ma20"] = 0
    
    # 3. RSI在上升（15分）
    if len(prev5) > 1 and last["rsi"] > prev5["rsi"].iloc[0]:
        score += 15
        signals["rsi_rising"] = 1
    else:
        signals["rsi_rising"] = 0
    
    # 4. RSI>50（15分）
    if last["rsi"] > 50:
        score += 15
        signals["rsi_above50"] = 1
    else:
        signals["rsi_above50"] = 0
    
    # 5. 窗口内价格上升（10分）
    if len(prev5) > 1:
        slope = np.polyfit(np.arange(len(prev5)), prev5["close"].values, 1)[0]
        if slope > 0:
            score += 10
            signals["price_rising"] = 1
        else:
            signals["price_rising"] = 0
    else:
        signals["price_rising"] = 0
    
    # 6. 均线多头排列（10分）
    if last["ma5"] > last["ma10"] > last["ma20"]:
        score += 10
        signals["ma_bullish"] = 1
    else:
        signals["ma_bullish"] = 0
    
    # 7. MACD柱线在增大（5分）
    if len(prev5) > 1 and last["hist"] > prev5["hist"].iloc[0]:
        score += 5
        signals["macd_hist_rising"] = 1
    else:
        signals["macd_hist_rising"] = 0
    
    # 额外信息
    signals["score"] = score
    signals["rsi"] = round(last["rsi"], 1)
    signals["boll_pos"] = round(last["boll_pos"], 2)
    signals["vol_ratio"] = round(last["vol_ratio"], 2)
    signals["close"] = last["close"]
    signals["ma5"] = round(last["ma5"], 2)
    signals["ma10"] = round(last["ma10"], 2)
    signals["ma20"] = round(last["ma20"], 2)
    
    # 近5日涨幅
    if len(df) >= 6:
        gain_5d = (last["close"] / df.iloc[-6]["close"] - 1) * 100
        signals["gain_5d"] = round(gain_5d, 2)
    else:
        signals["gain_5d"] = 0
    
    return signals


def fetch_all_stocks():
    """获取股票列表"""
    stocks = [
        "000001", "000002", "000063", "000333", "000338",
        "000425", "000568", "000625", "000651", "000708",
        "000725", "000768", "000776", "000858", "000876",
        "000938", "000963", "001979", "002001", "002007",
        "002008", "002024", "002027", "002049", "002050",
        "002120", "002142", "002230", "002236", "002241",
        "002271", "002304", "002311", "002352", "002371",
        "002410", "002415", "002422", "002460", "002475",
        "002493", "002508", "002594", "002601", "002607",
        "002624", "002653", "002709", "002714", "002756",
        "002812", "002841", "002850", "002938", "003816",
        "600000", "600009", "600010", "600011", "600015",
        "600016", "600019", "600025", "600028", "600029",
        "600030", "600031", "600036", "600048", "600050",
        "600104", "600109", "600111", "600115", "600118",
        "600132", "600150", "600183", "600196", "600276",
        "600309", "600332", "600340", "600346", "600352",
        "600406", "600438", "600486", "600489", "600498",
        "600519", "600547", "600570", "600585", "600588",
        "600660", "600690", "600703", "600745", "600809",
        "600837", "600845", "600848", "600887", "600893",
        "600900", "600918", "600926", "600941", "601012",
        "601021", "601066", "601088", "601111", "601138",
        "601166", "601211", "601225", "601236", "601288",
        "601318", "601319", "601328", "601336", "601390",
        "601398", "601601", "601628", "601633", "601658",
        "601668", "601669", "601688", "601728", "601766",
        "601788", "601800", "601808", "601818", "601857",
        "601877", "601888", "601899", "601901", "601919",
        "601933", "601939", "601985", "601988", "601989",
        "603019", "603087", "601127", "603160", "601727",
        "603259", "603260", "603288", "603369", "603501",
        "603596", "603833", "603899", "603986",
    ]
    return [{"code": code, "name": ""} for code in stocks]


def get_stock_name(code):
    """获取股票名称"""
    code = str(code).zfill(6)
    symbol = "sh" + code if code.startswith("6") else "sz" + code
    try:
        url = "https://qt.gtimg.cn/q=" + symbol
        r = requests.get(url, timeout=5)
        text = r.text
        if "~" in text:
            parts = text.split("~")
            if len(parts) > 1:
                return parts[1]
    except:
        pass
    return ""


def main():
    print("=" * 60)
    print("趋势启动扫描器")
    print("基于对照组验证的规律筛选潜力股")
    print("=" * 60)
    
    print("\n[Step 1] 获取股票列表...")
    stocks = fetch_all_stocks()
    print("  共 {} 只".format(len(stocks)))
    
    print("\n[Step 2] 扫描评分...")
    results = []
    
    for i, stock in enumerate(stocks, 1):
        if i % 30 == 0:
            print("  进度: {}/{}  已筛选: {} 只".format(i, len(stocks), len(results)))
        
        df = fetch_kline_tencent(stock["code"], days=100)
        if df.empty or len(df) < 30:
            continue
        
        df = add_indicators(df)
        signals = calc_trend_score(df)
        
        if signals and signals["score"] >= 60:  # 60分以上筛选
            signals["code"] = stock["code"]
            signals["name"] = get_stock_name(stock["code"]) or stock["code"]
            results.append(signals)
        
        time.sleep(0.15)
    
    if not results:
        print("\n未找到符合条件的股票")
        return
    
    df_result = pd.DataFrame(results)
    df_result = df_result.sort_values("score", ascending=False)
    
    # 保存结果
    today = datetime.now().strftime("%Y-%m-%d")
    output_path = DATA_DIR / f"trend_scan_{today}.csv"
    df_result.to_csv(output_path, index=False, encoding="utf-8-sig")
    
    print("\n" + "=" * 60)
    print("扫描结果")
    print("=" * 60)
    
    print("\n【统计】")
    print("  扫描: {} 只".format(len(stocks)))
    print("  符合条件: {} 只".format(len(df_result)))
    print("  平均分: {:.1f}".format(df_result["score"].mean()))
    
    print("\n【评分标准】")
    print("  MACD柱线为正: 25分")
    print("  价格>MA20: 20分")
    print("  RSI上升: 15分")
    print("  RSI>50: 15分")
    print("  窗口内上升: 10分")
    print("  均线多头: 10分")
    print("  MACD柱线增: 5分")
    print("  满分: 100分")
    print("  筛选: >=60分")
    
    print("\n【TOP 20 潜力股】")
    print("-" * 70)
    print("{:<4} {:<8} {:<10} {:>4} {:>6} {:>6} {:>5} {:>5} {:>5} {:>5}".format(
        "排名", "代码", "名称", "评分", "RSI", "布林", "5日%", "MA多", "MACD", "量比"
    ))
    print("-" * 70)
    
    for idx, row in df_result.head(20).iterrows():
        rank = df_result.index.get_loc(idx) + 1
        ma_flag = "Y" if row["ma_bullish"] else "N"
        macd_flag = "Y" if row["macd_hist_pos"] else "N"
        print("{:<4} {:<8} {:<10} {:>4.0f} {:>6.1f} {:>+6.2f} {:>+5.1f}% {:>5} {:>5} {:>5.2f}".format(
            rank, row["code"], row["name"][:8], row["score"],
            row["rsi"], row["boll_pos"], row["gain_5d"],
            ma_flag, macd_flag, row["vol_ratio"]
        ))
    
    # 信号分布
    print("\n【信号分布】")
    for col, label in [
        ("macd_hist_pos", "MACD柱线正"),
        ("above_ma20", "价格>MA20"),
        ("rsi_rising", "RSI上升"),
        ("rsi_above50", "RSI>50"),
        ("price_rising", "窗口上升"),
        ("ma_bullish", "均线多头"),
        ("macd_hist_rising", "MACD柱增"),
    ]:
        pct = df_result[col].mean() * 100
        bar = "#" * int(pct / 5) + "-" * (20 - int(pct / 5))
        print("  {} {:>5.0f}%  {}".format(label, pct, bar))
    
    print("\n【文件保存】")
    print("  {}".format(output_path))
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
    
    return df_result


if __name__ == "__main__":
    main()
