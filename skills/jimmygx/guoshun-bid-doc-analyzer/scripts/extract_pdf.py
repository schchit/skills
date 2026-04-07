#!/usr/bin/env python3
"""
招标文件PDF文本提取脚本
使用pdfplumber提取文本，保留表格结构
"""

import sys
import json
import argparse

def extract_pdf_text(pdf_path, max_chars=50000):
    """提取PDF文本内容"""
    try:
        import pdfplumber
    except ImportError:
        print("请先安装: pip install pdfplumber", file=sys.stderr)
        sys.exit(1)
    
    text_parts = []
    
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        
        for i, page in enumerate(pdf.pages):
            # 提取文本
            text = page.extract_text()
            if text:
                text_parts.append(f"--- 第{i+1}/{total_pages}页 ---\n{text}")
            
            # 提取表格
            tables = page.extract_tables()
            for j, table in enumerate(tables):
                if table:
                    table_text = "\n".join(["\t".join([str(cell) if cell else "" for cell in row]) for row in table])
                    text_parts.append(f"--- 第{i+1}页 表格{j+1} ---\n{table_text}")
    
    full_text = "\n\n".join(text_parts)
    
    # 截断超长文本
    if len(full_text) > max_chars:
        full_text = full_text[:max_chars] + f"\n\n... (内容已截断，共{len(full_text)}字符)"
    
    return full_text


def main():
    parser = argparse.ArgumentParser(description='提取招标文件PDF文本')
    parser.add_argument('pdf_path', help='PDF文件路径')
    parser.add_argument('-o', '--output', help='输出文件路径')
    parser.add_argument('-m', '--max-chars', type=int, default=50000, help='最大字符数')
    
    args = parser.parse_args()
    
    text = extract_pdf_text(args.pdf_path, args.max_chars)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"已保存到: {args.output}")
    else:
        print(text)


if __name__ == '__main__':
    main()
