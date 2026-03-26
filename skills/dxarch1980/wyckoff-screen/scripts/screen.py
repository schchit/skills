"""
Wyckoff 2.0 选股扫描
每天收盘后运行，扫描全市场，找出积累末期候选股
"""

import sys
import time
import sqlite3
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from wyckoff_engine import calculate_vp, detect_phase, score_stock

import efinance as ef
import akshare as ak
import pandas as pd

# ========== 配置 ==========
DB_PATH = Path(__file__).parent.parent / 'data' / 'stocks.db'
LOOKBACK = 120  # 分析最近120根日线
MAX_STOCKS = 100  # 每次最多扫多少只（全市场5491只太慢，先做100只演示）
TOP_N = 20  # 输出前N只


def init_db():
    """初始化SQLite数据库"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS stock_daily (
            code TEXT, date TEXT,
            open REAL, close REAL, high REAL, low REAL,
            volume INTEGER, amount REAL,
            PRIMARY KEY (code, date)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS screening_results (
            date TEXT, rank INTEGER,
            code TEXT, name TEXT,
            phase TEXT, phase_dir TEXT,
            score INTEGER, signals TEXT,
            vpoc REAL, cur_price REAL,
            reason TEXT,
            PRIMARY KEY (date, rank)
        )
    ''')
    conn.commit()
    return conn


def get_all_codes() -> list:
    """获取所有A股代码"""
    df = ak.stock_info_a_code_name()
    codes = df['code'].tolist()
    print(f'  A股总数: {len(codes)}')
    return codes


def update_daily_data(conn: sqlite3.Connection, force: bool = False):
    """
    拉取/更新日线数据到SQLite
    每天收盘后跑，force=True 时强制全量拉取
    """
    codes = get_all_codes()
    today = pd.Timestamp.today().strftime('%Y-%m-%d')

    done = 0
    errors = 0

    # 限制数量，避免太慢（演示用）
    codes = codes[:MAX_STOCKS]

    print(f'  开始更新日线数据（{len(codes)}只）...')

    for i, code in enumerate(codes):
        if i % 20 == 0:
            print(f'  进度: {i}/{len(codes)}...')

        # 查是否已有今日数据
        if not force:
            c = conn.cursor()
            c.execute('SELECT 1 FROM stock_daily WHERE code=? AND date=?', (code, today))
            if c.fetchone():
                done += 1
                continue

        try:
            df = ef.stock.get_quote_history(
                code,
                beg='20230101',
                end='20500101',
                klt=101,
                fqt=1
            )
            if df is None or len(df) == 0:
                continue

            df = df.rename(columns={
                '股票代码': 'code', '日期': 'date',
                '开盘': 'open', '收盘': 'close',
                '最高': 'high', '最低': 'low',
                '成交量': 'volume', '成交额': 'amount'
            })

            rows = df[['code', 'date', 'open', 'close', 'high', 'low', 'volume', 'amount']].values.tolist()
            conn.executemany(
                'INSERT OR REPLACE INTO stock_daily VALUES (?,?,?,?,?,?,?,?)', rows
            )
            done += 1
        except Exception as e:
            errors += 1
            continue

    conn.commit()
    print(f'  更新完成: {done}只成功, {errors}只失败')


def screen(conn: sqlite3.Connection) -> pd.DataFrame:
    """
    执行选股扫描
    返回 TOP_N 只候选股（按评分排序）
    """
    today = pd.Timestamp.today().strftime('%Y-%m-%d')
    c = conn.cursor()

    # 取所有有数据的股票
    c.execute('SELECT DISTINCT code FROM stock_daily')
    all_codes = [r[0] for r in c.fetchall()]

    results = []

    print(f'  开始扫描 {len(all_codes)} 只股票...')

    for i, code in enumerate(all_codes):
        if i % 50 == 0:
            print(f'  进度: {i}/{len(all_codes)}...')

        # 拉日线
        try:
            df = ef.stock.get_quote_history(
                code,
                beg='20230101',
                end='20500101',
                klt=101,
                fqt=1
            )
            if df is None or len(df) < 60:
                continue
            df = df.rename(columns={
                '股票代码': 'code', '日期': 'date',
                '开盘': 'open', '收盘': 'close',
                '最高': 'high', '最低': 'low',
                '成交量': 'volume', '成交额': 'amount'
            })
        except:
            continue

        # 评分
        r = score_stock(df)
        if not r['pass']:
            continue

        # 取名称
        try:
            name = df['股票名称'].iloc[-1] if '股票名称' in df.columns else code
        except:
            name = code

        results.append({
            'code': code,
            'name': name,
            'phase': r['phase']['phase'],
            'phase_dir': r['phase']['dir'],
            'score': r['score'],
            'signals': ' | '.join(r['signals']),
            'vpoc': r['profile']['vpoc'],
            'cur': r['profile']['cur'],
            'position': r['profile']['position'],
        })

    # 排序
    df_result = pd.DataFrame(results)
    if len(df_result) == 0:
        print('  没有找到符合条件的股票')
        return pd.DataFrame()

    df_result = df_result.sort_values('score', ascending=False).head(TOP_N)
    df_result = df_result.reset_index(drop=True)
    df_result.index = df_result.index + 1
    df_result.index.name = 'rank'

    # 存库
    c.execute('DELETE FROM screening_results WHERE date=?', (today,))
    for rank, row in df_result.iterrows():
        c.execute('''
            INSERT INTO screening_results VALUES (?,?,?,?,?,?,?,?,?,?,?)
        ''', (today, rank, row['code'], row['name'],
              row['phase'], row['phase_dir'], row['score'],
              row['signals'], row['vpoc'], row['cur'], row['position']))
    conn.commit()

    print(f'  扫描完成，找到 {len(df_result)} 只候选股')
    return df_result


def format_result(df: pd.DataFrame) -> str:
    """格式化输出"""
    if len(df) == 0:
        return '今日无符合条件的股票'

    lines = []
    lines.append(f"{'='*60}")
    lines.append(f"  Wyckoff 选股结果  ({pd.Timestamp.today().strftime('%Y-%m-%d')})")
    lines.append(f"{'='*60}")

    for rank, row in df.iterrows():
        lines.append(f"\n#{rank}  {row['name']} ({row['code']})")
        lines.append(f"   Phase: {row['phase']} | {row['phase_dir']} | 评分: {row['score']}/100")
        lines.append(f"   现价: {row['cur']}  |  VPOC: {row['vpoc']}  |  位置: {row['position']}")
        lines.append(f"   信号: {row['signals']}")

    lines.append(f"\n{'='*60}")
    lines.append(f"  共 {len(df)} 只候选股 | 规则: 评分≥60 + Wyckoff积累结构")
    lines.append(f"{'='*60}")
    return '\n'.join(lines)


if __name__ == '__main__':
    print('Wyckoff 选股系统 启动...')

    conn = init_db()
    update_daily_data(conn)
    result = screen(conn)

    txt = format_result(result)
    print('\n' + txt)

    # 保存今日结果
    today = pd.Timestamp.today().strftime('%Y-%m-%d')
    out_path = Path(__file__).parent.parent / 'data' / f'screen_{today}.txt'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(txt)
    print(f'\n结果已保存: {out_path}')
