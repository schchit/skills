#!/usr/bin/env python3
"""
元数据生成脚本
Supports: SQLite, MySQL, PostgreSQL
Usage: 
  sqlite: python generate_metadata.py --source users --db sqlite:///data.db
  mysql:  python generate_metadata.py --source users --db mysql://user:pass@localhost:3306/db
  pg:     python generate_metadata.py --source users --db postgresql://user:pass@localhost:5432/db
"""

import argparse
import json
from typing import Dict, List, Any
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


def get_table_schema(conn, table_name: str) -> List[Dict]:
    """获取表结构"""
    cursor = conn.cursor()
    schema = []
    
    try:
        # SQLite
        cursor.execute(f"PRAGMA table_info({table_name})")
        for row in cursor.fetchall():
            schema.append({
                "name": row[1],
                "type": row[2],
                "nullable": not row[3],
                "primary_key": bool(row[5]),
                "default": row[4]
            })
    except:
        pass
    
    # 尝试 MySQL/PostgreSQL
    if not schema:
        try:
            cursor.execute(f"DESCRIBE {table_name}")
            for row in cursor.fetchall():
                schema.append({
                    "name": row['Field'],
                    "type": row['Type'],
                    "nullable": row['Null'] == 'YES',
                    "primary_key": row['Key'] == 'PRI',
                    "default": row['Default']
                })
        except:
            pass
    
    if not schema:
        try:
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable, column_key, column_default
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
            """)
            for row in cursor.fetchall():
                schema.append({
                    "name": row['column_name'],
                    "type": row['data_type'],
                    "nullable": row['is_nullable'] == 'YES',
                    "primary_key": row['column_key'] == 'PRI',
                    "default": row['column_default']
                })
        except:
            pass
    
    cursor.close()
    return schema


def get_table_indexes(conn, table_name: str) -> List[Dict]:
    """获取索引信息"""
    cursor = conn.cursor()
    indexes = []
    
    try:
        # SQLite
        cursor.execute(f"PRAGMA index_list({table_name})")
        for row in cursor.fetchall():
            indexes.append({
                "name": row[1],
                "unique": row[2] == 1
            })
    except:
        pass
    
    cursor.close()
    return indexes


def get_foreign_keys(conn, table_name: str) -> List[Dict]:
    """获取外键信息"""
    cursor = conn.cursor()
    fks = []
    
    try:
        # SQLite
        cursor.execute(f"PRAGMA foreign_key_list({table_name})")
        for row in cursor.fetchall():
            fks.append({
                "column": row[3],
                "references": f"{row[2]}.{row[4]}"
            })
    except:
        pass
    
    cursor.close()
    return fks


def infer_description(field_name: str) -> str:
    """根据字段名推断描述"""
    field_lower = field_name.lower()
    
    mappings = {
        'id': '唯一标识符',
        'name': '名称',
        'title': '标题',
        'desc': '描述',
        'description': '描述',
        'status': '状态',
        'type': '类型',
        'code': '编码',
        'date': '日期',
        'time': '时间',
        'created_at': '创建时间',
        'updated_at': '更新时间',
        'created_by': '创建人',
        'updated_by': '更新人',
        'amount': '金额',
        'price': '价格',
        'count': '数量',
        'num': '数量',
        'remark': '备注',
        'note': '备注',
        'phone': '电话',
        'email': '邮箱',
        'address': '地址',
        'user_id': '用户ID',
        'order_id': '订单ID',
        'product_id': '商品ID',
    }
    
    for key, desc in mappings.items():
        if key in field_lower:
            return desc
    
    return ""


def generate_metadata(conn, table_name: str) -> Dict:
    """生成元数据"""
    schema = get_table_schema(conn, table_name)
    indexes = get_table_indexes(conn, table_name)
    fks = get_foreign_keys(conn, table_name)
    
    # 丰富字段信息
    for col in schema:
        if not col.get('description'):
            col['description'] = infer_description(col['name'])
    
    metadata = {
        "table_name": table_name,
        "columns": schema,
        "indexes": indexes,
        "foreign_keys": fks,
        "column_count": len(schema)
    }
    
    return metadata


def generate_data_dict(metadata: Dict) -> str:
    """生成数据字典"""
    md = f"""# 数据字典 - {metadata['table_name']}

## 基本信息
- 字段数量: {metadata['column_count']}
- 索引数量: {len(metadata.get('indexes', []))}
- 外键数量: {len(metadata.get('foreign_keys', []))}

## 字段说明

| 字段名 | 类型 | 必填 | 主键 | 说明 |
|--------|------|------|------|------|
"""
    
    for col in metadata.get("columns", []):
        md += f"| {col['name']} | {col['type']} | "
        md += f"{'是' if not col.get('nullable') else '否'} | "
        md += f"{'是' if col.get('primary_key') else '否'} | "
        md += f"{col.get('description', '')} |\n"
    
    # 索引
    if metadata.get('indexes'):
        md += "\n## 索引\n\n"
        for idx in metadata['indexes']:
            md += f"- {idx['name']} ({'唯一' if idx.get('unique') else '普通'})\n"
    
    # 外键
    if metadata.get('foreign_keys'):
        md += "\n## 外键\n\n"
        for fk in metadata['foreign_keys']:
            md += f"- {fk['column']} → {fk['references']}\n"
    
    return md


def main():
    parser = argparse.ArgumentParser(description='生成元数据')
    parser.add_argument('--source', required=True, help='表名')
    parser.add_argument('--db', '--connection', dest='db', required=True,
                       help='数据库连接字符串')
    parser.add_argument('--output', help='输出文件路径')
    parser.add_argument('--format', choices=['json', 'markdown'], default='json', 
                       help='输出格式')
    args = parser.parse_args()
    
    try:
        conn = get_connection(args.db)
        print(f"✅ 已连接到数据库")
        
        metadata = generate_metadata(conn, args.source)
        print(f"✅ 已生成元数据: {metadata['column_count']} 个字段")
        
        conn.close()
        
        if args.format == 'markdown':
            output = generate_data_dict(metadata)
        else:
            output = json.dumps(metadata, ensure_ascii=False, indent=2)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"✅ 已保存到 {args.output}")
        else:
            print(output)
            
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请安装: pip install pymysql psycopg2-binary")
    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == '__main__':
    main()
