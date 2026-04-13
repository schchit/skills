#!/usr/bin/env python3
"""
状态文件管理脚本
维护小说的真相文件（世界状态、角色矩阵、伏笔等）
"""

import os
import re
import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Any


class StateManager:
    """状态文件管理器"""
    
    def __init__(self, project_path: str):
        """
        初始化状态管理器
        
        Args:
            project_path: 小说项目根目录
        """
        self.project_path = Path(project_path)
        self.state_dir = self.project_path / "state"
        self.reference_dir = self.project_path / "reference"
        
        # 定义状态文件
        self.state_files = {
            'world_state': 'world_state.md',
            'character_matrix': 'character_matrix.md',
            'pending_hooks': 'pending_hooks.md',
            'chapter_summaries': 'chapter_summaries.md',
            'subplot_board': 'subplot_board.md',
            'emotional_arcs': 'emotional_arcs.md',
            'particle_ledger': 'particle_ledger.md'
        }
    
    def initialize_state_files(self) -> Dict[str, str]:
        """
        初始化所有状态文件
        
        Returns:
            创建的文件路径字典
        """
        if not self.state_dir.exists():
            self.state_dir.mkdir(parents=True)
        
        if not self.reference_dir.exists():
            self.reference_dir.mkdir(parents=True)
        
        created_files = {}
        
        # 初始化世界状态
        created_files['world_state'] = self._init_world_state()
        
        # 初始化角色矩阵
        created_files['character_matrix'] = self._init_character_matrix()
        
        # 初始化伏笔
        created_files['pending_hooks'] = self._init_pending_hooks()
        
        # 初始化章节摘要
        created_files['chapter_summaries'] = self._init_chapter_summaries()
        
        # 初始化支线板
        created_files['subplot_board'] = self._init_subplot_board()
        
        # 初始化情感弧线
        created_files['emotional_arcs'] = self._init_emotional_arcs()
        
        # 初始化物资账本
        created_files['particle_ledger'] = self._init_particle_ledger()
        
        return created_files
    
    def read_state(self, state_name: str) -> Optional[str]:
        """
        读取状态文件内容
        
        Args:
            state_name: 状态文件名称（如 'world_state'）
        
        Returns:
            文件内容，如果文件不存在则返回 None
        """
        if state_name not in self.state_files:
            return None
        
        filepath = self.state_dir / self.state_files[state_name]
        if not filepath.exists():
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    
    def update_state(self, state_name: str, content: str) -> bool:
        """
        更新状态文件
        
        Args:
            state_name: 状态文件名称
            content: 新内容
        
        Returns:
            是否更新成功
        """
        if state_name not in self.state_files:
            return False
        
        if not self.state_dir.exists():
            self.state_dir.mkdir(parents=True)
        
        filepath = self.state_dir / self.state_files[state_name]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    
    def validate_state(self, state_name: str) -> Dict[str, Any]:
        """
        验证状态文件格式
        
        Args:
            state_name: 状态文件名称
        
        Returns:
            验证结果
        """
        content = self.read_state(state_name)
        if content is None:
            return {
                "is_valid": False,
                "errors": [f"状态文件 {state_name} 不存在"],
                "warnings": []
            }
        
        errors = []
        warnings = []
        
        # 基础检查
        if not content.strip():
            warnings.append(f"{state_name} 内容为空")
        
        # 根据不同状态文件进行特定检查
        if state_name == 'world_state':
            if '## 角色' not in content:
                warnings.append("缺少角色状态部分")
            if '## 位置' not in content:
                warnings.append("缺少位置信息部分")
        
        elif state_name == 'character_matrix':
            characters = re.findall(r'-\s*\*\*([^*]+)\*\*', content)
            if len(characters) < 1:
                warnings.append("角色矩阵为空")
        
        elif state_name == 'pending_hooks':
            hooks = re.findall(r'-\s*\[状态:\s*(\w+)\]', content)
            if 'open' not in hooks and 'progressing' not in hooks:
                warnings.append("没有活跃的伏笔")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def validate_all_states(self) -> Dict[str, Any]:
        """
        验证所有状态文件
        
        Returns:
            所有状态文件的验证结果
        """
        results = {}
        for state_name in self.state_files.keys():
            results[state_name] = self.validate_state(state_name)
        
        # 检查是否有任何错误
        has_errors = any(r['errors'] for r in results.values())
        
        return {
            "overall_valid": not has_errors,
            "states": results
        }
    
    def extract_characters(self) -> List[Dict[str, str]]:
        """
        从角色矩阵中提取角色列表
        
        Returns:
            角色列表，每项包含名字和简短描述
        """
        content = self.read_state('character_matrix')
        if content is None:
            return []
        
        characters = []
        pattern = re.compile(r'-\s*\*\*([^*]+)\*\*.*?\n\s*(.+)', re.MULTILINE)
        for match in pattern.finditer(content):
            characters.append({
                "name": match.group(1).strip(),
                "description": match.group(2).strip()
            })
        
        return characters
    
    def extract_hooks(self) -> List[Dict[str, str]]:
        """
        从伏笔文件中提取伏笔列表
        
        Returns:
            伏笔列表
        """
        content = self.read_state('pending_hooks')
        if content is None:
            return []
        
        hooks = []
        pattern = re.compile(r'-\s*\*\*([^*]+)\*\*.*?\[状态:\s*(\w+)\]', re.MULTILINE)
        for match in pattern.finditer(content):
            hooks.append({
                "title": match.group(1).strip(),
                "status": match.group(2).strip()
            })
        
        return hooks
    
    def _init_world_state(self) -> str:
        """初始化世界状态文件"""
        content = """# 世界状态

## 当前时间
- 时间点: 故事开始

## 角色
- 主角: 待补充
- 重要配角: 待补充

## 位置
- 当前地点: 待补充
- 重要地点: 待补充

## 关系网络
- 角色间关系: 待补充

## 已知信息
- 主角已知: 待补充
- 世界设定: 待补充
"""
        filepath = self.state_dir / self.state_files['world_state']
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return str(filepath)
    
    def _init_character_matrix(self) -> str:
        """初始化角色矩阵文件"""
        content = """# 角色矩阵

## 主角
- **主角**: 待补充
  - 性格: 待补充
  - 背景: 待补充
  - 目标: 待补充

## 重要配角
- 待补充

## 角色关系
- 主角 ↔ 配角: 待补充

## 交互记录
- 无
"""
        filepath = self.state_dir / self.state_files['character_matrix']
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return str(filepath)
    
    def _init_pending_hooks(self) -> str:
        """初始化伏笔文件"""
        content = """# 未闭合伏笔

## 活跃伏笔 [状态: open]
- 无

## 进行中 [状态: progressing]
- 无

## 已推迟 [状态: deferred]
- 无

## 已解决 [状态: resolved]
- 无
"""
        filepath = self.state_dir / self.state_files['pending_hooks']
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return str(filepath)
    
    def _init_chapter_summaries(self) -> str:
        """初始化章节摘要文件"""
        content = """# 章节摘要

## 章节列表
- 无
"""
        filepath = self.state_dir / self.state_files['chapter_summaries']
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return str(filepath)
    
    def _init_subplot_board(self) -> str:
        """初始化支线板文件"""
        content = """# 支线进度板

## A 线（主线）
- 状态: 未开始
- 当前进度: 待补充
- 下一目标: 待补充

## B 线
- 状态: 未开始
- 当前进度: 待补充

## C 线
- 状态: 未开始
- 当前进度: 待补充
"""
        filepath = self.state_dir / self.state_files['subplot_board']
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return str(filepath)
    
    def _init_emotional_arcs(self) -> str:
        """初始化情感弧线文件"""
        content = """# 情感弧线

## 主角情感变化
- 起始状态: 待补充
- 当前状态: 待补充
- 预期发展: 待补充

## 关键情感节点
- 无
"""
        filepath = self.state_dir / self.state_files['emotional_arcs']
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return str(filepath)
    
    def _init_particle_ledger(self) -> str:
        """初始化物资账本文件"""
        content = """# 物资账本

## 主角物品
- 无

## 资源
- 金钱: 待补充
- 能量: 待补充

## 重要物品追踪
- 无
"""
        filepath = self.state_dir / self.state_files['particle_ledger']
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return str(filepath)


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='状态文件管理工具')
    parser.add_argument('--action', required=True,
                       choices=['init', 'read', 'update', 'validate', 'validate-all', 'list-characters', 'list-hooks'],
                       help='操作类型')
    parser.add_argument('--project-path', required=True, help='小说项目路径')
    parser.add_argument('--state', help='状态文件名称（如 world_state）')
    parser.add_argument('--content', help='状态文件内容')
    parser.add_argument('--output', choices=['text', 'json'], default='text', help='输出格式')
    
    args = parser.parse_args()
    
    manager = StateManager(args.project_path)
    result = None
    
    if args.action == 'init':
        result = manager.initialize_state_files()
    
    elif args.action == 'read':
        if args.state is None:
            result = {"error": "需要指定状态文件 --state"}
        else:
            content = manager.read_state(args.state)
            if content is None:
                result = {"error": f"状态文件 {args.state} 不存在"}
            else:
                result = {"state": args.state, "content": content}
    
    elif args.action == 'update':
        if args.state is None or args.content is None:
            result = {"error": "需要指定状态文件 --state 和内容 --content"}
        else:
            success = manager.update_state(args.state, args.content)
            result = {"success": success, "state": args.state}
    
    elif args.action == 'validate':
        if args.state is None:
            result = {"error": "需要指定状态文件 --state"}
        else:
            result = manager.validate_state(args.state)
    
    elif args.action == 'validate-all':
        result = manager.validate_all_states()
    
    elif args.action == 'list-characters':
        result = {"characters": manager.extract_characters()}
    
    elif args.action == 'list-hooks':
        result = {"hooks": manager.extract_hooks()}
    
    # 输出结果
    if args.output == 'json':
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if isinstance(result, dict):
            if 'error' in result:
                print(f"错误: {result['error']}")
            elif 'content' in result:
                print(result['content'])
            elif 'states' in result:
                for state_name, validation in result['states'].items():
                    status = "✓" if validation['is_valid'] else "✗"
                    print(f"{status} {state_name}")
                    for err in validation['errors']:
                        print(f"  错误: {err}")
                    for warn in validation['warnings']:
                        print(f"  警告: {warn}")
            elif 'characters' in result:
                for char in result['characters']:
                    print(f"- {char['name']}: {char['description']}")
            elif 'hooks' in result:
                for hook in result['hooks']:
                    print(f"- {hook['title']} [{hook['status']}]")
            else:
                for key, value in result.items():
                    print(f"{key}: {value}")


if __name__ == '__main__':
    main()
