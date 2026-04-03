"""
Chroma 向量存储封装
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional


class VectorStore:
    def __init__(self, persist_dir: str):
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )

    def create_collection(self, name: str) -> chromadb.Collection:
        """创建或获取 collection"""
        return self.client.get_or_create_collection(name=name)

    def add_documents(
        self,
        collection_name: str,
        texts: List[str],
        ids: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """添加文档到指定 collection"""
        collection = self.create_collection(collection_name)
        collection.add(
            documents=texts,
            ids=ids,
            metadatas=metadatas
        )

    def query(
        self,
        collection_name: str,
        query_text: str,
        top_k: int = 5,
        where: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """检索最相关的文档片段"""
        collection = self.create_collection(collection_name)
        results = collection.query(
            query_texts=[query_text],
            n_results=top_k,
            where=where
        )
        return results

    def delete_collection(self, name: str) -> None:
        """删除 collection"""
        self.client.delete_collection(name)

    def list_collections(self) -> List[str]:
        """列出所有 collection"""
        return [c.name for c in self.client.list_collections()]


if __name__ == "__main__":
    # 简单测试
    vs = VectorStore("/tmp/test_chroma")
    vs.create_collection("test")
    vs.add_documents(
        "test",
        ["Hello world", "Python is great"],
        ["id1", "id2"]
    )
    result = vs.query("test", "Python", top_k=1)
    print(result)
