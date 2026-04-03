"""
知识库索引管理
扫描 knowledge/ 目录下所有文档，自动解析 + 向量化 + 存入 Chroma
支持增量更新（文件变化才重新索引）
"""
import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List
from .loader import scan_folder
from .vector_store import VectorStore


class KnowledgeIndexer:
    def __init__(self, knowledge_dir: str, chroma_dir: str, state_file: str = ".index_state.json"):
        self.knowledge_dir = knowledge_dir
        self.chroma_dir = chroma_dir
        self.state_file = state_file
        self.vector_store = VectorStore(chroma_dir)
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        """加载索引状态"""
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as f:
                return json.load(f)
        return {}

    def _save_state(self):
        """保存索引状态"""
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=2)

    def _file_hash(self, path: str) -> str:
        """计算文件内容的 MD5"""
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def _needs_update(self, path: str) -> bool:
        """检查文件是否需要更新"""
        if path not in self.state:
            return True
        current_hash = self._file_hash(path)
        return self.state[path].get("hash") != current_hash

    def _chunk_text(self, text: str, max_chars: int = 500) -> List[str]:
        """简单分块：按段落分割"""
        if len(text) <= max_chars:
            return [text]
        # 按段落分割
        paragraphs = text.split("\n\n")
        chunks = []
        current = ""
        for para in paragraphs:
            if len(current) + len(para) <= max_chars:
                current += "\n\n" + para
            else:
                if current:
                    chunks.append(current.strip())
                current = para
        if current:
            chunks.append(current.strip())
        return chunks if chunks else [text[:max_chars]]

    def index_folder(self, subfolder: str = "") -> Dict[str, int]:
        """
        索引指定子文件夹
        返回: {collection_name: indexed_count}
        """
        target_dir = os.path.join(self.knowledge_dir, subfolder) if subfolder else self.knowledge_dir
        if not os.path.exists(target_dir):
            print(f"目录不存在: {target_dir}")
            return {}

        collection_name = f"kb_{subfolder}" if subfolder else "kb_default"
        docs = scan_folder(target_dir)

        if not docs:
            print(f"没有找到文档: {target_dir}")
            return {collection_name: 0}

        texts = []
        ids = []
        metadatas = []

        for fpath, content in docs:
            if not self._needs_update(fpath):
                continue

            # 简单分块：按段落分割
            chunks = self._chunk_text(content, max_chars=500)
            for i, chunk in enumerate(chunks):
                chunk_id = f"{os.path.basename(fpath)}_{i}"
                texts.append(chunk)
                ids.append(chunk_id)
                metadatas.append({
                    "source": fpath,
                    "collection": collection_name
                })

            # 更新状态
            self.state[fpath] = {
                "hash": self._file_hash(fpath),
                "collection": collection_name
            }

        if texts:
            self.vector_store.add_documents(
                collection_name=collection_name,
                texts=texts,
                ids=ids,
                metadatas=metadatas
            )
            self._save_state()
            print(f"已索引 {len(texts)} 个片段到 collection '{collection_name}'")

        return {collection_name: len(texts)}

    def index_all(self) -> Dict[str, int]:
        """索引所有子文件夹"""
        results = {}
        if os.path.exists(self.knowledge_dir):
            for subfolder in os.listdir(self.knowledge_dir):
                subpath = os.path.join(self.knowledge_dir, subfolder)
                if os.path.isdir(subpath):
                    results.update(self.index_folder(subfolder))
        return results


    def search(self, folder: str, query: str, top_k: int = 3) -> List[Dict]:
        """搜索知识库"""
        collection_name = f"kb_{folder}"
        try:
            results = self.vector_store.query(collection_name, query, top_k=top_k)
            if results and results.get("documents"):
                docs = []
                for i, doc in enumerate(results["documents"][0]):
                    docs.append({
                        "text": doc,
                        "distance": results.get("distances", [[]])[0][i] if results.get("distances") else 0
                    })
                return docs
        except Exception as e:
            print(f"知识库搜索失败: {e}")
        return []

    def index_urls(self, project_id: str, urls: List[Dict]) -> int:
        """抓取并索引URL内容"""
        docs = []
        for u in urls:
            try:
                resp = requests.get(u["url"], timeout=10)
                resp.encoding = resp.apparent_encoding or 'utf-8'
                text = self._clean_text(resp.text)
                if len(text) > 100:
                    docs.append(text[:5000])  # 限制长度
                    self.vector_store.add(collection_name=f"kb_{project_id}", documents=[text[:2000]], metadatas=[{"source": u["url"], "type": "url"}])
            except Exception as e:
                print(f"抓取失败 {u['url']}: {e}")
        return len(docs)
    
    def _fetch_url_content(self, url: str) -> str:
        """抓取单个URL内容"""
        try:
            resp = requests.get(url, timeout=10)
            resp.encoding = resp.apparent_encoding or 'utf-8'
            # 简单提取正文
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, 'html.parser')
            for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()
            text = soup.get_text(separator=' ', strip=True)
            return text[:5000]
        except:
            return ""
