"""
FastAPI 服务 — 知识库 RAG API
提供 RESTful 接口供 Bot 调用
"""
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import JSONResponse
import uvicorn

from .rag import RAGQuery
from .indexer import KnowledgeIndexer
from .watcher import create_watcher

# ── 允许上传的文件类型 ─────────────────────────────────
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".docx"}

# ── 配置 ──────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent
CHROMA_DIR = str(BASE_DIR / "knowledge_base" / "chroma_db")
KNOWLEDGE_DIR = str(BASE_DIR / "knowledge")
STATE_FILE = str(BASE_DIR / "knowledge_base" / ".index_state.json")

# ── FastAPI App ───────────────────────────────────────
app = FastAPI(title="CommunityOS Knowledge Base API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局单例
_rag: Optional[RAGQuery] = None
_indexer: Optional[KnowledgeIndexer] = None


def get_rag() -> RAGQuery:
    global _rag
    if _rag is None:
        _rag = RAGQuery(CHROMA_DIR)
    return _rag


def get_indexer() -> KnowledgeIndexer:
    global _indexer
    if _indexer is None:
        _indexer = KnowledgeIndexer(KNOWLEDGE_DIR, CHROMA_DIR, STATE_FILE)
    return _indexer


# ── 请求/响应模型 ─────────────────────────────────────
class QueryRequest(BaseModel):
    query: str
    collection: Optional[str] = None
    top_k: int = 5


class QueryResponse(BaseModel):
    answer: str
    context: str
    sources: list[str]


class RetrieveRequest(BaseModel):
    query: str
    collection: Optional[str] = None
    top_k: int = 5


class RetrieveResult(BaseModel):
    text: str
    source: str
    collection: str
    distance: float


class IndexRequest(BaseModel):
    subfolder: Optional[str] = None  # 空=全量


# ── API 路由 ──────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "chroma_dir": CHROMA_DIR, "knowledge_dir": KNOWLEDGE_DIR}


@app.get("/collections")
def list_collections():
    """列出所有 collection"""
    return {"collections": get_rag().vector_store.list_collections()}


@app.post("/rag/retrieve", response_model=list[RetrieveResult])
def retrieve(req: RetrieveRequest):
    """纯检索，不调 LLM"""
    try:
        chunks = get_rag().retrieve(
            query=req.query,
            collection=req.collection or "default",
            top_k=req.top_k,
        )
        return chunks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rag/query", response_model=QueryResponse)
def rag_query(req: QueryRequest):
    """
    完整的 RAG 问答
    注意：answer 字段需要调用方自行用 LLM 处理 context
    此接口返回 context 和 sources，调用方组装 prompt
    """
    try:
        rag = get_rag()
        context = rag.build_context(
            query=req.query,
            collection=req.collection,
            top_k=req.top_k,
        )
        sources = list({
            c["source"]
            for c in rag.retrieve(req.query, req.collection or "default", req.top_k)
        })
        return QueryResponse(
            answer="",  # 调用方用 LLM 处理 context
            context=context,
            sources=sources,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/index")
def index(req: IndexRequest):
    """触发增量/全量索引"""
    try:
        indexer = get_indexer()
        if req.subfolder:
            result = indexer.index_folder(req.subfolder)
        else:
            result = indexer.index_all()
        return {"status": "ok", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/state")
def index_state():
    """查看当前索引状态"""
    indexer = get_indexer()
    return {"state": indexer.state}


# ── 文件上传 ──────────────────────────────────────────

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    collection: str = Form("default"),
):
    """
    上传文件到知识库并自动触发索引重建。
    支持 .pdf .txt .md .docx
    - file: 要上传的文件
    - collection: 保存到的子文件夹（默认 "default"）
    """
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {ext}，仅支持 {ALLOWED_EXTENSIONS}"
        )

    # 确保目标目录存在
    target_dir = Path(KNOWLEDGE_DIR) / collection
    target_dir.mkdir(parents=True, exist_ok=True)

    file_path = target_dir / file.filename

    # 保存文件
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # 触发索引（仅索引刚上传的文件所在 collection）
    try:
        indexer = get_indexer()
        index_result = indexer.index_folder(collection)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "partial",
                "message": f"文件已保存但索引失败: {str(e)}",
                "file": str(file_path),
                "index_result": None
            }
        )

    return {
        "status": "ok",
        "filename": file.filename,
        "saved_path": str(file_path),
        "size_bytes": len(content),
        "collection": collection,
        "index_result": index_result,
    }


@app.post("/upload/multiple")
async def upload_multiple_files(
    files: list[UploadFile] = File(...),
    collection: str = Form("default"),
):
    """
    批量上传文件到知识库并自动触发索引重建。
    """
    results = []
    errors = []

    target_dir = Path(KNOWLEDGE_DIR) / collection
    target_dir.mkdir(parents=True, exist_ok=True)

    for file in files:
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            errors.append({"filename": file.filename, "error": f"不支持的文件类型: {ext}"})
            continue

        file_path = target_dir / file.filename
        try:
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            results.append({
                "filename": file.filename,
                "saved_path": str(file_path),
                "size_bytes": len(content),
            })
        except Exception as e:
            errors.append({"filename": file.filename, "error": str(e)})

    # 统一触发索引
    try:
        indexer = get_indexer()
        index_result = indexer.index_folder(collection)
    except Exception as e:
        index_result = {"error": str(e)}

    return {
        "status": "ok" if not errors else "partial",
        "uploaded": results,
        "errors": errors,
        "collection": collection,
        "index_result": index_result,
    }


# ── 启动入口 ──────────────────────────────────────────
def run_server(host: str = "0.0.0.0", port: int = 8000):
    print(f"启动知识库 API: http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
