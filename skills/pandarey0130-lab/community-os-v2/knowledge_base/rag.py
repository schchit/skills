"""
RAG 查询模块
提供基于 Chroma 向量检索的问答能力
"""
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

from .vector_store import VectorStore


class RAGQuery:
    """
    RAG 查询封装
    1. 根据 query 从 Chroma 检索相关文档片段
    2. 组装 context，返回给 LLM 使用
    """

    def __init__(self, chroma_dir: str):
        self.vector_store = VectorStore(chroma_dir)

    def retrieve(
        self,
        query: str,
        collection: str = "default",
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        向量检索，返回最相关的文档片段

        Returns:
            List[Dict] — 每个元素包含 text, source, distance
        """
        results = self.vector_store.query(
            collection_name=collection,
            query_text=query,
            top_k=top_k,
        )

        chunks = []
        if results.get("documents") and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                meta = (results.get("metadatas") or [[]]*len(results["documents"][0]))[0][i]
                dist = (results.get("distances") or [[]]*len(results["documents"][0]))[0][i]
                chunks.append({
                    "text": doc,
                    "source": meta.get("source", "unknown") if meta else "unknown",
                    "collection": meta.get("collection", collection) if meta else collection,
                    "distance": dist,
                })
        return chunks

    def build_context(
        self,
        query: str,
        collection: Optional[str] = None,
        top_k: int = 5,
    ) -> str:
        """
        构建 LLM 提示用的 context 字符串
        """
        collections = [collection] if collection else self.vector_store.list_collections()
        if not collections:
            return "（当前知识库为空）"

        all_chunks = []
        for col in collections:
            try:
                all_chunks.extend(self.retrieve(query, collection=col, top_k=top_k))
            except Exception:
                pass

        if not all_chunks:
            return "（未在知识库中找到相关内容）"

        # 按相关度排序
        all_chunks.sort(key=lambda x: x.get("distance", 999))

        lines = []
        for i, chunk in enumerate(all_chunks[:top_k], 1):
            lines.append(f"[文档 {i}] 来源: {chunk['source']}\n{chunk['text']}")

        return "\n\n".join(lines)

    def answer(
        self,
        query: str,
        llm_callable,
        collection: Optional[str] = None,
        top_k: int = 5,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        完整的 RAG 问答

        Args:
            query: 用户问题
            llm_callable: LLM 调用函数，签名: fn(prompt: str) -> str
            collection: 指定 collection，不传则搜索全部
            top_k: 检索片段数
            system_prompt: 系统提示词

        Returns:
            Dict — {answer, context, sources}
        """
        context = self.build_context(query, collection=collection, top_k=top_k)

        if system_prompt is None:
            system_prompt = (
                "你是一个社区知识库助手。请根据以下参考资料回答用户问题。\n"
                "如果参考资料中没有相关信息，请如实告知。\n"
                "引用资料时注明来源。"
            )

        user_prompt = f"参考资料:\n{context}\n\n---\n\n用户问题: {query}"

        try:
            answer = llm_callable(
                messages=[{"role": "system", "content": system_prompt},
                          {"role": "user", "content": user_prompt}]
            )
        except Exception as e:
            answer = f"[RAG 调用失败] {e}"

        # 收集来源
        chunks = self.retrieve(query, collection=collection or "default", top_k=top_k)
        sources = list({c["source"] for c in chunks})

        return {
            "answer": answer,
            "context": context,
            "sources": sources,
        }


# 工厂函数：创建默认 RAG 实例
def get_rag(chroma_dir: Optional[str] = None) -> RAGQuery:
    if chroma_dir is None:
        base = Path(__file__).parent.parent
        chroma_dir = str(base / "knowledge_base" / "chroma_db")
    return RAGQuery(chroma_dir)


if __name__ == "__main__":
    # 快速测试
    rag = get_rag()
    print("Collections:", rag.vector_store.list_collections())
    context = rag.build_context("社区运营", top_k=3)
    print("Context preview:", context[:500])
