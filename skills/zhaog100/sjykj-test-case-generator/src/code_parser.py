# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

from dataclasses import dataclass, field
from typing import List, Optional
import ast


@dataclass
class ParamInfo:
    """函数参数信息"""
    name: str
    type_hint: Optional[str] = None
    default: Optional[str] = None
    has_default: bool = False


@dataclass
class FunctionInfo:
    """函数信息"""
    name: str
    params: List[ParamInfo] = field(default_factory=list)
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    source: str = ""
    start_line: int = 0


class CodeParser:
    """AST解析Python文件，提取函数签名/类型注解/参数/返回值"""

    def parse_file(self, filepath: str) -> List[FunctionInfo]:
        """解析Python文件，返回所有顶层函数信息"""
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        tree = ast.parse(source)
        results = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef):
                results.append(self._extract_function(node, source))
        return results

    def parse_source(self, source: str) -> List[FunctionInfo]:
        """解析Python源码字符串"""
        tree = ast.parse(source)
        results = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef):
                results.append(self._extract_function(node, source))
        return results

    def _extract_function(self, node: ast.FunctionDef, full_source: str) -> FunctionInfo:
        params = self._extract_params(node.args)
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]
        # Get function source lines
        lines = full_source.splitlines()
        start = node.lineno - 1
        end = node.end_lineno or (start + 1)
        source = '\n'.join(lines[start:end])
        return_type = ast.unparse(node.returns) if node.returns else None
        return FunctionInfo(
            name=node.name,
            params=params,
            return_type=return_type,
            docstring=ast.get_docstring(node),
            decorators=decorators,
            source=source,
            start_line=node.lineno,
        )

    def _extract_params(self, args: ast.arguments) -> List[ParamInfo]:
        params = []
        all_args = args.args + args.posonlyargs + args.kwonlyargs
        defaults = args.defaults
        kw_defaults = args.kw_defaults

        num_no_default = len(all_args) - len(defaults)
        for i, arg in enumerate(all_args):
            type_hint = ast.unparse(arg.annotation) if arg.annotation else None
            if i < num_no_default:
                params.append(ParamInfo(name=arg.arg, type_hint=type_hint, has_default=False))
            else:
                default_idx = i - num_no_default
                default_val = ast.unparse(defaults[default_idx]) if default_idx < len(defaults) else None
                params.append(ParamInfo(name=arg.arg, type_hint=type_hint, default=default_val, has_default=True))
        return params

    def _get_decorator_name(self, dec) -> str:
        if isinstance(dec, ast.Name):
            return dec.id
        elif isinstance(dec, ast.Attribute):
            return ast.unparse(dec)
        elif isinstance(dec, ast.Call):
            return ast.unparse(dec.func)
        return ast.unparse(dec)
