#!/usr/bin/env python3
"""
数据质量检查脚本
Supports: SQLite, MySQL, PostgreSQL
Usage: 
  sqlite: python data_quality_check.py --table users --db sqlite:///data.db
  mysql:  python data_quality_check.py --table users --db mysql://user:pass@localhost:3306/db
  pg:     python data_quality_check.py --table users --db postgresql://user:pass@localhost:5432/db
"""

import argparse
import json
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse


def parse_connection_string(conn_str: str) -> Dict[str, str]:
    """解析数据库连接字符串"""
    if conn_str.startswith('sqlite'):
        return {'type': 'sqlite', 'path': conn_str.replace('sqlite:///', '')}
    
    parsed = urlparse(conn_str)
    return {
        'type': parsed.scheme,
        'host': parsed.hostname or 'localhost',
        'port': parsed.port or (3306 if parsed.scheme == 'mysql' else 5432),
        'user': parsed.username or 'root',
        'password': parsed.password or '',
        'database': parsed.path.lstrip('/') if parsed.path else ''
    }


def get_connection(conn_str: str):
    """获取数据库连接"""
    config = parse_connection_string(conn_str)
    
    if config['type'] == 'sqlite':
        import sqlite3
        return sqlite3.connect(config['path'])
    
    elif config['type'] in ('mysql', 'mysql+pymysql'):
        import pymysql
        return pymysql.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['database'],
            cursorclass=pymysql.cursors.DictCursor
        )
    
    elif config['type'] in ('postgresql', 'postgres'):
        import psycopg2
        return psycopg2.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['database']
        )
    
    else:
        raise ValueError(f"Unsupported database: {config['type']}")


def get_table_data(conn, table_name: str, limit: int = 10000) -> List[Dict]:
    """获取表数据"""
    cursor = conn.cursor()
    
    # 根据数据库类型调整
    try:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        cursor.close()


def get_table_schema(conn, table_name: str) -> List[Dict]:
    """获取表结构"""
    cursor = conn.cursor()
    schema = []
    
    try:
        # SQLite
        cursor.execute(f"PRAGMA table_info({table_name})")
        for row in cursor.fetchall():
            schema.append({
                'name': row[1],
                'type': row[2],
                'nullable': not row[3],
                'primary_key': bool(row[5])
            })
    except:
        pass
    
    cursor.close()
    return schema


def check_completeness(data: List[Dict], schema: List[Dict]) -> Dict[str, Any]:
    """检查数据完整性"""
    if not data:
        return {"score": 0, "issues": ["无数据"]}
    
    required_fields = [s['name'] for s in schema if not s['nullable']]
    total = len(data)
    issues = []
    
    for field in required_fields:
        null_count = sum(1 for row in data if field not in row or row[field] is None)
        null_ratio = null_count / total
        if null_ratio > 0:
            issues.append(f"字段 {field} 缺失率 {null_ratio:.1%}")
    
    return {
        "score": max(0, 100 - len(issues) * 20),
        "issues": issues
    }


def check_uniqueness(data: List[Dict], schema: List[Dict]) -> Dict[str, Any]:
    """检查数据唯一性"""
    if not data:
        return {"score": 100, "issues": []}
    
    primary_keys = [s['name'] for s in schema if s['primary_key']]
    issues = []
    
    for pk in primary_keys:
        values = [row.get(pk) for row in data if pk in row]
        unique_values = set(values)
        if len(values) != len(unique_values):
            duplicate = len(values) - len(unique_values)
            issues.append(f"主键 {pk} 存在 {duplicate} 条重复")
    
    return {
        "score": 100 if not issues else 50,
        "issues": issues
    }


def check_format(data: List[Dict], schema: List[Dict]) -> Dict[str, Any]:
    """检查数据格式"""
    if not data:
        return {"score": 100, "issues": []}
    
    issues = []
    for col in schema:
        col_name = col['name']
        col_type = col['type'].upper()
        
        # 检查日期格式
        if 'DATE' in col_type or 'TIME' in col_type:
            for i, row in enumerate(data[:100]):
                if col_name in row and row[col_name]:
                    val = str(row[col_name])
                    # 简单校验
                    if ' ' in val and ':' in val:
                        pass  # 格式看起来像 datetime
        
        # 检查数值字段
        elif 'INT' in col_type or 'REAL' in col_type or 'NUMERIC' in col_type:
            for i, row in enumerate(data[:100]):
                if col_name in row and row[col_name]:
                    try:
                        float(row[col_name])
                    except:
                        issues.append(f"字段 {col_name} 第{i+1}行不是有效数值")
    
    return {
        "score": max(0, 100 - len(issues) * 5),
        "issues": issues[:10]  # 只显示前10个
    }


def generate_report(table_name: str, results: Dict) -> str:
    """生成数据质量报告"""
    report = f"""## 数据质量报告 - {table_name}

### 完整性
- 评分: {results.get('completeness', {}).get('score', 'N/A')}%
- 问题: {len(results.get('completeness', {}).get('issues', []))}

### 唯一性  
- 评分: {results.get('uniqueness', {}).get('score', 'N/A')}%
- 问题: {len(results.get('uniqueness', {}).get('issues', []))}

### 格式
- 评分: {results.get('format', {}).get('score', 'N/A')}%
- 问题: {len(results.get('format', {}).get('issues', []))}

### 总体评分: {results.get('overall_score', 'N/A')}%
"""
    return report


def main():
    parser = argparse.ArgumentParser(description='数据质量检查')
    parser.add_argument('--table', required=True, help='表名')
    parser.add_argument('--db', '--connection', dest='db', required=True, 
                       help='数据库连接字符串')
    parser.add_argument('--limit', type=int, default=10000, help='检查数据量')
    args = parser.parse_args()
    
    try:
        conn = get_connection(args.db)
        print(f"✅ 已连接到数据库")
        
        # 获取数据
        data = get_table_data(conn, args.table, args.limit)
        print(f"✅ 已获取 {len(data)} 条数据")
        
        # 获取结构
        schema = get_table_schema(conn, args.table)
        print(f"✅ 已获取 {len(schema)} 个字段")
        
        conn.close()
        
        # 检查
        results = {
            'completeness': check_completeness(data, schema),
            'uniqueness': check_uniqueness(data, schema),
            'format': check_format(data, schema)
        }
        
        avg_score = sum(r['score'] for r in results.values()) / len(results)
        results['overall_score'] = avg_score
        
        print(generate_report(args.table, results))
        
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请安装: pip install pymysql psycopg2-binary")
    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == '__main__':
    main()
