#!/usr/bin/env python3
"""
章节管理脚本
提供章节文件的创建、列表、查找、验证功能
"""

import os
import re
import argparse
import json
from pathlib import Path
from typing import List, Dict, Optional


class ChapterManager:
    """章节文件管理器"""
    
    def __init__(self, project_path: str):
        """
        初始化章节管理器
        
        Args:
            project_path: 小说项目根目录
        """
        self.project_path = Path(project_path)
        self.chapters_dir = self.project_path / "chapters"
        self.chapter_pattern = re.compile(r'^chapter-(\d+)\.md$')
        
    def list_chapters(self) -> List[Dict[str, any]]:
        """
        列出所有章节
        
        Returns:
            章节信息列表，每项包含序号、文件名、路径、字数
        """
        if not self.chapters_dir.exists():
            return []
        
        chapters = []
        for file in sorted(self.chapters_dir.glob("chapter-*.md")):
            match = self.chapter_pattern.match(file.name)
            if match:
                chapter_num = int(match.group(1))
                word_count = self._count_words(file)
                chapters.append({
                    "number": chapter_num,
                    "filename": file.name,
                    "path": str(file),
                    "word_count": word_count
                })
        
        return sorted(chapters, key=lambda x: x["number"])
    
    def find_latest_chapter(self) -> Optional[Dict[str, any]]:
        """
        查找最新章节
        
        Returns:
            最新章节信息，如果没有章节则返回 None
        """
        chapters = self.list_chapters()
        if not chapters:
            return None
        return chapters[-1]
    
    def find_next_chapter_number(self) -> int:
        """
        获取下一章节的编号
        
        Returns:
            下一章节编号（从 1 开始）
        """
        chapters = self.list_chapters()
        if not chapters:
            return 1
        return chapters[-1]["number"] + 1
    
    def create_chapter(self, chapter_num: int, content: str = "") -> str:
        """
        创建新章节文件
        
        Args:
            chapter_num: 章节编号
            content: 章节内容（可选）
        
        Returns:
            创建的章节文件路径
        """
        if not self.chapters_dir.exists():
            self.chapters_dir.mkdir(parents=True)
        
        filename = f"chapter-{chapter_num:02d}.md"
        filepath = self.chapters_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(filepath)
    
    def read_chapter(self, chapter_num: int) -> Optional[str]:
        """
        读取章节内容
        
        Args:
            chapter_num: 章节编号
        
        Returns:
            章节内容，如果文件不存在则返回 None
        """
        filename = f"chapter-{chapter_num:02d}.md"
        filepath = self.chapters_dir / filename
        
        if not filepath.exists():
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    
    def update_chapter(self, chapter_num: int, content: str) -> bool:
        """
        更新章节内容
        
        Args:
            chapter_num: 章节编号
            content: 新内容
        
        Returns:
            是否更新成功
        """
        filename = f"chapter-{chapter_num:02d}.md"
        filepath = self.chapters_dir / filename
        
        if not filepath.exists():
            return False
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    
    def validate_chapter(self, chapter_num: int) -> Dict[str, any]:
        """
        验证章节格式
        
        Args:
            chapter_num: 章节编号
        
        Returns:
            验证结果，包含 is_valid、errors、warnings
        """
        content = self.read_chapter(chapter_num)
        if content is None:
            return {
                "is_valid": False,
                "errors": [f"章节 {chapter_num} 不存在"],
                "warnings": []
            }
        
        errors = []
        warnings = []
        
        # 检查是否为空
        if not content.strip():
            errors.append("章节内容为空")
        
        # 检查字数
        word_count = self._count_words(self.chapters_dir / f"chapter-{chapter_num:02d}.md")
        if word_count < 500:
            warnings.append(f"字数过少 ({word_count} 字)")
        
        # 检查是否有章节标题
        if not re.search(r'^#+\s*第?\d+[章回]', content, re.MULTILINE):
            warnings.append("缺少标准的章节标题")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "word_count": word_count
        }
    
    def delete_chapter(self, chapter_num: int) -> bool:
        """
        删除章节
        
        Args:
            chapter_num: 章节编号
        
        Returns:
            是否删除成功
        """
        filename = f"chapter-{chapter_num:02d}.md"
        filepath = self.chapters_dir / filename
        
        if not filepath.exists():
            return False
        
        filepath.unlink()
        return True
    
    def _count_words(self, filepath: Path) -> int:
        """
        统计文件字数（中文字符+英文单词）
        
        Args:
            filepath: 文件路径
        
        Returns:
            字数
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 移除 markdown 标记
        content = re.sub(r'#+\s*', '', content)  # 标题
        content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)  # 粗体
        content = re.sub(r'\*([^*]+)\*', r'\1', content)  # 斜体
        content = re.sub(r'`([^`]+)`', r'\1', content)  # 代码
        
        # 统计中文字符
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
        
        # 统计英文单词
        english_words = len(re.findall(r'[a-zA-Z]+', content))
        
        return chinese_chars + english_words


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='章节管理工具')
    parser.add_argument('--action', required=True, 
                       choices=['list', 'find-latest', 'find-next', 'create', 'read', 'update', 'validate', 'delete'],
                       help='操作类型')
    parser.add_argument('--project-path', required=True, help='小说项目路径')
    parser.add_argument('--chapter', type=int, help='章节编号')
    parser.add_argument('--content', help='章节内容')
    parser.add_argument('--output', choices=['text', 'json'], default='text', help='输出格式')
    
    args = parser.parse_args()
    
    manager = ChapterManager(args.project_path)
    result = None
    
    if args.action == 'list':
        result = manager.list_chapters()
    
    elif args.action == 'find-latest':
        result = manager.find_latest_chapter()
    
    elif args.action == 'find-next':
        result = {"next_chapter_number": manager.find_next_chapter_number()}
    
    elif args.action == 'create':
        if args.chapter is None:
            args.chapter = manager.find_next_chapter_number()
        filepath = manager.create_chapter(args.chapter, args.content or "")
        result = {"path": filepath, "chapter_number": args.chapter}
    
    elif args.action == 'read':
        if args.chapter is None:
            result = {"error": "需要指定章节编号 --chapter"}
        else:
            content = manager.read_chapter(args.chapter)
            if content is None:
                result = {"error": f"章节 {args.chapter} 不存在"}
            else:
                result = {"chapter": args.chapter, "content": content}
    
    elif args.action == 'update':
        if args.chapter is None or args.content is None:
            result = {"error": "需要指定章节编号 --chapter 和内容 --content"}
        else:
            success = manager.update_chapter(args.chapter, args.content)
            result = {"success": success, "chapter": args.chapter}
    
    elif args.action == 'validate':
        if args.chapter is None:
            result = {"error": "需要指定章节编号 --chapter"}
        else:
            result = manager.validate_chapter(args.chapter)
    
    elif args.action == 'delete':
        if args.chapter is None:
            result = {"error": "需要指定章节编号 --chapter"}
        else:
            success = manager.delete_chapter(args.chapter)
            result = {"success": success, "chapter": args.chapter}
    
    # 输出结果
    if args.output == 'json':
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if isinstance(result, list):
            for item in result:
                print(f"Chapter {item['number']}: {item['filename']} ({item['word_count']} 字)")
        elif isinstance(result, dict):
            if 'error' in result:
                print(f"错误: {result['error']}")
            else:
                for key, value in result.items():
                    print(f"{key}: {value}")


if __name__ == '__main__':
    main()
