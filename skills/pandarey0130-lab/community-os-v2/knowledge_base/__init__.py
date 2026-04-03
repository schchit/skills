"""
CommunityOS Knowledge Base
模块结构:
  loader.py      — 文档加载 (PDF/TXT/MD/DOCX)
  vector_store.py — Chroma 向量存储封装
  indexer.py     — 增量索引管理
  rag.py         — RAG 检索与问答
  watcher.py     — 文件夹监听自动索引
  api.py         — FastAPI REST 接口
"""
from .loader import load_document, scan_folder
from .vector_store import VectorStore
from .indexer import KnowledgeIndexer
from .rag import RAGQuery, get_rag
from .watcher import KnowledgeWatcher, create_watcher

__all__ = [
    "load_document",
    "scan_folder",
    "VectorStore",
    "KnowledgeIndexer",
    "RAGQuery",
    "get_rag",
    "KnowledgeWatcher",
    "create_watcher",
]
