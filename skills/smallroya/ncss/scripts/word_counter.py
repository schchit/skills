#!/usr/bin/env python3
"""
字数统计工具
精确统计中文和英文文本的字数
"""

import argparse
import re
from pathlib import Path
from typing import Dict, List


class WordCounter:
    """字数统计器"""
    
    @staticmethod
    def count_words(text: str) -> Dict[str, int]:
        """
        统计文本字数
        
        Args:
            text: 待统计的文本
        
        Returns:
            统计结果，包含 total, chinese, english, punctuation
        """
        # 统计中文字符
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        
        # 统计英文单词
        english_words = len(re.findall(r'[a-zA-Z]+', text))
        
        # 统计标点符号
        punctuation = len(re.findall(r'[^\w\s]', text))
        
        # 统计数字
        numbers = len(re.findall(r'\d+', text))
        
        # 总字数（中文字符 + 英文单词）
        total = chinese_chars + english_words
        
        return {
            "total": total,
            "chinese": chinese_chars,
            "english": english_words,
            "punctuation": punctuation,
            "numbers": numbers
        }
    
    @staticmethod
    def count_words_in_file(filepath: str) -> Dict[str, int]:
        """
        统计文件字数
        
        Args:
            filepath: 文件路径
        
        Returns:
            统计结果
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {filepath}")
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return WordCounter.count_words(content)
    
    @staticmethod
    def count_words_in_directory(directory: str, pattern: str = "*.md") -> List[Dict[str, any]]:
        """
        统计目录下所有匹配文件的字数
        
        Args:
            directory: 目录路径
            pattern: 文件匹配模式
        
        Returns:
            文件统计结果列表
        """
        dir_path = Path(directory)
        if not dir_path.exists():
            raise FileNotFoundError(f"目录不存在: {directory}")
        
        results = []
        for file in sorted(dir_path.glob(pattern)):
            try:
                stats = WordCounter.count_words_in_file(str(file))
                results.append({
                    "filename": file.name,
                    "path": str(file),
                    **stats
                })
            except Exception as e:
                results.append({
                    "filename": file.name,
                    "path": str(file),
                    "error": str(e)
                })
        
        return results
    
    @staticmethod
    def calculate_target_words(current_words: int, target: int, tolerance: float = 0.1) -> Dict[str, any]:
        """
        计算字数是否符合目标
        
        Args:
            current_words: 当前字数
            target: 目标字数
            tolerance: 允许的误差比例（默认 10%）
        
        Returns:
            判断结果
        """
        min_words = int(target * (1 - tolerance))
        max_words = int(target * (1 + tolerance))
        
        is_within_range = min_words <= current_words <= max_words
        
        if current_words < min_words:
            advice = f"需要增加 {min_words - current_words} 字"
        elif current_words > max_words:
            advice = f"需要减少 {current_words - max_words} 字"
        else:
            advice = "字数符合要求"
        
        return {
            "current": current_words,
            "target": target,
            "min": min_words,
            "max": max_words,
            "is_within_range": is_within_range,
            "difference": current_words - target,
            "advice": advice
        }


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='字数统计工具')
    parser.add_argument('--action', required=True,
                       choices=['count-text', 'count-file', 'count-dir', 'check-target'],
                       help='操作类型')
    parser.add_argument('--text', help='待统计的文本')
    parser.add_argument('--file', help='待统计的文件路径')
    parser.add_argument('--directory', help='待统计的目录路径')
    parser.add_argument('--pattern', default='*.md', help='文件匹配模式（用于目录统计）')
    parser.add_argument('--current', type=int, help='当前字数')
    parser.add_argument('--target', type=int, help='目标字数')
    parser.add_argument('--tolerance', type=float, default=0.1, help='允许误差比例（默认 0.1）')
    parser.add_argument('--output', choices=['text', 'json'], default='text', help='输出格式')
    
    args = parser.parse_args()
    
    result = None
    
    if args.action == 'count-text':
        if args.text is None:
            result = {"error": "需要指定文本 --text"}
        else:
            result = WordCounter.count_words(args.text)
    
    elif args.action == 'count-file':
        if args.file is None:
            result = {"error": "需要指定文件路径 --file"}
        else:
            try:
                result = WordCounter.count_words_in_file(args.file)
                result["file"] = args.file
            except Exception as e:
                result = {"error": str(e)}
    
    elif args.action == 'count-dir':
        if args.directory is None:
            result = {"error": "需要指定目录路径 --directory"}
        else:
            try:
                result = WordCounter.count_words_in_directory(args.directory, args.pattern)
            except Exception as e:
                result = {"error": str(e)}
    
    elif args.action == 'check-target':
        if args.current is None or args.target is None:
            result = {"error": "需要指定当前字数 --current 和目标字数 --target"}
        else:
            result = WordCounter.calculate_target_words(args.current, args.target, args.tolerance)
    
    # 输出结果
    if args.output == 'json':
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if isinstance(result, dict):
            if 'error' in result:
                print(f"错误: {result['error']}")
            elif 'file' in result:
                print(f"文件: {result['file']}")
                print(f"总字数: {result['total']}")
                print(f"中文字符: {result['chinese']}")
                print(f"英文单词: {result['english']}")
                print(f"标点符号: {result['punctuation']}")
                print(f"数字: {result['numbers']}")
            elif 'is_within_range' in result:
                status = "✓" if result['is_within_range'] else "✗"
                print(f"当前字数: {result['current']}")
                print(f"目标字数: {result['target']} (范围: {result['min']}-{result['max']})")
                print(f"差异: {result['difference']} 字")
                print(f"状态: {status} {result['advice']}")
            else:
                for key, value in result.items():
                    print(f"{key}: {value}")
        elif isinstance(result, list):
            total_words = 0
            for item in result:
                if 'error' in item:
                    print(f"{item['filename']}: 错误 - {item['error']}")
                else:
                    print(f"{item['filename']}: {item['total']} 字")
                    total_words += item['total']
            print(f"\n总计: {total_words} 字")


if __name__ == '__main__':
    main()
