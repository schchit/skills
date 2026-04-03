"""
知识库文档加载器
支持格式: .pdf .txt .md .docx
"""
import os
from pathlib import Path
from typing import List, Tuple


def load_pdf(file_path: str) -> str:
    """加载 PDF 文件"""
    try:
        import fitz  # pymupdf
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except ImportError:
        raise ImportError("请安装 pymupdf: pip install pymupdf")


def load_txt(file_path: str) -> str:
    """加载纯文本文件"""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def load_markdown(file_path: str) -> str:
    """加载 Markdown 文件"""
    return load_txt(file_path)


def load_docx(file_path: str) -> str:
    """加载 Word 文档"""
    try:
        from docx import Document
        doc = Document(file_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except ImportError:
        raise ImportError("请安装 python-docx: pip install python-docx")


LOADERS = {
    ".pdf": load_pdf,
    ".txt": load_txt,
    ".md": load_markdown,
    ".docx": load_docx,
}


def load_document(file_path: str) -> str:
    """根据文件扩展名调用对应加载器"""
    ext = Path(file_path).suffix.lower()
    if ext not in LOADERS:
        raise ValueError(f"不支持的文件格式: {ext}")
    return LOADERS[ext](file_path)


def scan_folder(folder_path: str) -> List[Tuple[str, str]]:
    """
    扫描文件夹，返回 [(文件路径, 文本内容)] 列表
    """
    results = []
    for root, _, files in os.walk(folder_path):
        for fname in files:
            ext = Path(fname).suffix.lower()
            if ext in LOADERS:
                fpath = os.path.join(root, fname)
                try:
                    content = load_document(fpath)
                    results.append((fpath, content))
                except Exception as e:
                    print(f"加载失败 {fpath}: {e}")
    return results


if __name__ == "__main__":
    # 测试
    import sys
    if len(sys.argv) > 1:
        path = sys.argv[1]
        if os.path.isdir(path):
            docs = scan_folder(path)
            for fp, content in docs:
                print(f"文件: {fp}, 长度: {len(content)}")
        else:
            print(load_document(path))
