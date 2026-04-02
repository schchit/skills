"""
Office Pro - Enterprise Document Automation Suite

Enterprise-grade Word and Excel document automation tool
"""

from word_processor import WordProcessor
from excel_processor import ExcelProcessor, XlsxTemplateEngine, ChartFactory
from core import (
    DocumentProcessor,
    require_document,
    require_template,
    OfficeProError,
    ErrorCode,
    ParameterError,
    TemplateError,
    TemplateNotFoundError,
    TemplateRenderError,
    DataError,
    DataFileNotFoundError,
    DataParseError,
    DataEncodingError,
    FileError,
    PathTraversalError,
    FileAccessDeniedError,
    DependencyError,
    DocumentNotLoadedError,
    load_json_file,
    safe_resolve_path,
    ensure_directory,
    get_template_dir,
    validate_template_path,
    TemplateCache,
    get_cached_template_list,
    invalidate_template_cache,
)
from skill_interface import SkillInterface, SkillActions

__version__ = '1.0.0'
__all__ = [
    'WordProcessor',
    'ExcelProcessor',
    'XlsxTemplateEngine',
    'ChartFactory',
    'DocumentProcessor',
    'require_document',
    'require_template',
    'OfficeProError',
    'ErrorCode',
    'ParameterError',
    'TemplateError',
    'TemplateNotFoundError',
    'TemplateRenderError',
    'DataError',
    'DataFileNotFoundError',
    'DataParseError',
    'DataEncodingError',
    'FileError',
    'PathTraversalError',
    'FileAccessDeniedError',
    'DependencyError',
    'DocumentNotLoadedError',
    'load_json_file',
    'safe_resolve_path',
    'ensure_directory',
    'get_template_dir',
    'validate_template_path',
    'TemplateCache',
    'get_cached_template_list',
    'invalidate_template_cache',
    'SkillInterface',
    'SkillActions',
]
