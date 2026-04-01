"""
DocHub - Document Workbench v3 (universal)
- init mode: analyze content, auto-generate category structure
- run mode: incremental conversion (new/changed files only)
- Security: path traversal guard, safe subprocess, temp cleanup, log write safety
"""
import os
import re
import sys
import shutil
import subprocess
import tempfile
import hashlib
from pathlib import Path
from collections import defaultdict

# ============================================================
# Constants
# ============================================================

MARKITDOWN_CMD = [sys.executable, "-m", "markitdown"]
LOG_FILE = None

# Output directory names (English)
DOCS_MD_DIR = "_docs_md"
INDEX_FILE = "_index.md"
CONVERT_LOG_FILE = "_convert_log.txt"
UPDATE_DIR = "update"

# Skip directories when scanning
SKIP_DIRS = {DOCS_MD_DIR, "_markdown", UPDATE_DIR, "_sanitized_output",
             "_restored_output", "node_modules", ".git", "__pycache__"}

# Supported extensions
DOC_EXTENSIONS = {".docx", ".xlsx", ".pdf", ".doc"}

# Single text max processing length (10 MB), skip oversized to avoid OOM
MAX_TEXT_LENGTH = 10 * 1024 * 1024

# ============================================================
# Utility Functions
# ============================================================


def log(msg):
    """Log output with write safety — never crashes main process / 日志容错"""
    try:
        clean = ''.join(c for c in str(msg) if c.isprintable() or c in '\n\r\t')
        print(clean)
    except Exception:
        pass
    if LOG_FILE:
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(str(msg) + "\n")
        except Exception:
            pass


def init_log(workspace):
    global LOG_FILE
    LOG_FILE = workspace / CONVERT_LOG_FILE
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write(f"DocHub v3 - {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    except Exception as e:
        print(f"[WARN] Cannot create log file: {e}")


def validate_workspace(workspace):
    """Validate workspace path — ensure it exists and is a directory / 校验工作区路径"""
    p = Path(workspace)
    if not p.exists():
        log(f"[ERROR] Workspace does not exist: {p}")
        sys.exit(1)
    if not p.is_dir():
        log(f"[ERROR] Workspace is not a directory: {p}")
        sys.exit(1)
    return p.resolve()


def sanitize_path(base, target):
    """Ensure resolved target is within base directory — prevent path traversal / 路径穿越防护"""
    resolved = (base / target).resolve()
    base_resolved = base.resolve()
    if not str(resolved).startswith(str(base_resolved)):
        log(f"[ERROR] Path traversal detected: {target}")
        return None
    return resolved


# ============================================================
# Keyword Analysis
# ============================================================


def extract_keywords(text, top_n=20):
    """Extract keywords from text (simple word frequency) / 从文本中提取关键词"""
    if not text or len(text) > MAX_TEXT_LENGTH:
        return []
    # Remove punctuation and numbers
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z]', ' ', text.lower())
    words = text.split()
    # Filter stopwords
    stopwords = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
                 '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
                 '自己', '这', '那', '他', '她', '它', '们', '为', '与', '对', '以', '及',
                 'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                 'should', 'may', 'might', 'can', 'to', 'of', 'in', 'for', 'on', 'with',
                 'at', 'by', 'from', 'as', 'into', 'through', 'and', 'or', 'but', 'if'}
    words = [w for w in words if len(w) >= 2 and w not in stopwords]
    freq = defaultdict(int)
    for w in words:
        freq[w] += 1
    return sorted(freq.items(), key=lambda x: x[1], reverse=True)[:top_n]


def get_doc_keywords(path, tmp_path):
    """Get document keywords via markitdown / 获取文档关键词"""
    try:
        shutil.copy2(path, tmp_path)
        result = subprocess.run(
            MARKITDOWN_CMD + [tmp_path],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0 and result.stdout.strip():
            return extract_keywords(result.stdout)
    except subprocess.TimeoutExpired:
        log(f"  [WARN] markitdown timeout for {path.name}")
    except Exception:
        pass
    return []


# ============================================================
# Categorization (Auto Mode)
# ============================================================


def analyze_and_categorize(workspace):
    """
    Dynamically analyze document content, auto-generate category structure
    动态分析文档内容，自动生成分类结构
    Returns: {category_name: [doc_paths]}
    """
    log("\n[STEP 1] Scanning documents...")
    all_docs = []
    for root, dirs, files in os.walk(workspace):
        # Normalize root for skip check
        root_parts = set(Path(root).parts)
        if any(d in root_parts for d in SKIP_DIRS):
            continue
        for f in files:
            if Path(f).suffix.lower() in DOC_EXTENSIONS:
                all_docs.append(Path(root) / f)

    log(f"  Found {len(all_docs)} documents")
    if not all_docs:
        return {}

    # Sample analysis (max 30 docs)
    sample = all_docs[:30] if len(all_docs) > 30 else all_docs
    doc_signatures = {}  # path -> keywords

    log("\n[STEP 2] Analyzing document content...")
    for i, doc in enumerate(sample):
        fd, tmp = tempfile.mkstemp(suffix=doc.suffix)
        os.close(fd)
        try:
            kw = get_doc_keywords(doc, tmp)
            doc_signatures[str(doc)] = kw
            if (i + 1) % 5 == 0:
                log(f"  Analyzed {i+1}/{len(sample)}...")
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)

    # Cluster by keyword similarity
    log("\n[STEP 3] Generating category structure...")
    categories = defaultdict(list)
    category_keywords = {}  # category -> top keywords

    for doc in all_docs:
        doc_str = str(doc)
        kw = doc_signatures.get(doc_str, [])

        # Use top 5 keywords as signature
        sig = set([w for w, _ in kw[:5]])

        if not sig:
            categories["Other"].append(doc)
            continue

        # Match to existing category
        matched = False
        best_score = 0
        best_cat = None
        for cat, cat_kw in category_keywords.items():
            cat_set = set([w for w, _ in cat_kw[:10]])
            score = len(sig & cat_set)
            if score > best_score:
                best_score = score
                best_cat = cat

        if best_score >= 1:
            categories[best_cat].append(doc)
        else:
            # Create new category
            new_cat = f"_{kw[0][0]}" if kw else "Other"
            base = new_cat
            n = 1
            while new_cat in categories:
                new_cat = f"{base}_{n}"
                n += 1
            categories[new_cat] = [doc]
            category_keywords[new_cat] = kw

    # Clean empty categories
    for cat in list(categories.keys()):
        if not categories[cat]:
            del categories[cat]

    # Generate final category names
    final_cats = {}
    for cat, docs in categories.items():
        if cat.startswith("_"):
            kw_list = category_keywords.get(cat, [])
            if kw_list:
                final_cats[f"docs_{kw_list[0][0]}"] = docs
            else:
                final_cats["Uncategorized"] = docs
        else:
            final_cats[cat] = docs

    return final_cats


# ============================================================
# Directory Structure
# ============================================================


def create_folder_structure(workspace, categories):
    """
    Create folder structure based on categories
    根据分类创建文件夹结构
    Returns: {original_path: new_path}
    """
    log("\n[STEP 4] Creating category directories...")
    md_base = workspace / DOCS_MD_DIR
    md_base.mkdir(exist_ok=True)

    move_map = {}  # original_path -> new_relative_path

    for cat_name, docs in sorted(categories.items()):
        # Path traversal guard
        safe_dir = sanitize_path(md_base, cat_name)
        if safe_dir is None:
            log(f"  [SKIP] Unsafe category name: {cat_name}")
            continue
        safe_dir.mkdir(exist_ok=True)
        log(f"  Created: {cat_name}/ ({len(docs)} docs)")

        for doc in docs:
            new_path = safe_dir / doc.name
            # Handle duplicate names
            if new_path.exists():
                stem = doc.stem
                suffix = doc.suffix
                counter = 1
                while new_path.exists():
                    new_path = safe_dir / f"{stem}_{counter}{suffix}"
                    counter += 1
            move_map[str(doc)] = new_path

    # Create update folder
    update_dir = workspace / UPDATE_DIR
    update_dir.mkdir(exist_ok=True)
    log(f"\n  Created: {UPDATE_DIR}/ (new document drop zone)")

    return move_map


# ============================================================
# Conversion
# ============================================================


def convert_single(src_path, dst_path):
    """Convert a single file to Markdown / 转换单个文件到 MD"""
    try:
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(suffix=src_path.suffix)
        os.close(fd)
        try:
            shutil.copy2(src_path, tmp)
            result = subprocess.run(
                MARKITDOWN_CMD + [tmp],
                capture_output=True, text=True, timeout=120
            )
            if result.returncode == 0 and result.stdout.strip():
                md_path = dst_path.with_suffix(".md")
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(result.stdout)
                return True
            else:
                log(f"    [WARN] markitdown returned empty for {src_path.name}")
        except subprocess.TimeoutExpired:
            log(f"    [WARN] Conversion timeout for {src_path.name}")
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
    except Exception as e:
        log(f"    [ERROR] {e}")
    return False


# ============================================================
# Incremental Mode
# ============================================================


def run_incremental(workspace):
    """
    Incremental mode: scan _docs_md/ structure, convert new/changed files
    增量模式：扫描 _docs_md/ 目录结构，只转换新增/变更的文件
    """
    md_base = workspace / DOCS_MD_DIR
    if not md_base.exists():
        log(f"[WARN] {DOCS_MD_DIR}/ does not exist, please run init first")
        return

    log("\n[INCREMENTAL] Incremental conversion mode")
    log("=" * 50)

    # Build source -> target mapping from existing MD files
    md_to_source = {}
    for md_file in md_base.rglob("*.md"):
        rel = md_file.relative_to(md_base)
        # Find matching source file by replacing .md with source extension
        for ext in [".docx", ".xlsx", ".pdf", ".doc"]:
            src_candidate = workspace / str(rel).replace(".md", ext)
            if src_candidate.exists():
                md_to_source[str(md_file)] = src_candidate
                break

    total = 0
    success = 0
    for md_path_str, src_path in md_to_source.items():
        md_path = Path(md_path_str)
        # Check if update needed
        if md_path.exists() and md_path.stat().st_mtime > src_path.stat().st_mtime:
            continue  # Already up to date
        total += 1
        if convert_single(src_path, md_path.with_suffix("")):
            success += 1

    log(f"\nIncremental conversion complete: {success}/{total} files updated")


# ============================================================
# Interactive Mode Selection
# ============================================================


def ask_classify_mode():
    """
    Ask user to select categorization mode
    询问用户选择分类模式
    Supports --mode parameter for non-interactive execution
    Returns: "keep" or "auto"
    """
    if "--mode" in sys.argv:
        idx = sys.argv.index("--mode")
        if idx + 1 < len(sys.argv):
            choice = sys.argv[idx + 1].strip()
            if choice == "1":
                print("\n[MODE] Parameter: Keep original structure (mode=1)")
                return "keep"
            elif choice == "2":
                print("\n[MODE] Parameter: Auto-analyze & categorize (mode=2)")
                return "auto"

    # Interactive mode
    print("\n" + "=" * 60)
    print("[INIT] DocHub Initialization / 文档工作流初始化")
    print("=" * 60)
    print("\nSelect categorization mode / 请选择分类结构创建方式：\n")
    print("  [1] Keep original structure / 保持原有目录结构")
    print("      - Organize docs into _docs_md/ preserving current folders")
    print()
    print("  [2] Auto-analyze & categorize / 系统自动分析创建分类")
    print("      - Analyze document keywords")
    print("      - Group by content similarity")
    print()
    print("=" * 60)

    while True:
        choice = input("\nEnter [1/2] (default 1) / 请输入选择 [1/2]（默认 1）: ").strip()
        if choice == "" or choice == "1":
            return "keep"
        elif choice == "2":
            return "auto"
        else:
            print("Invalid input / 无效输入，请输入 1 或 2")


# ============================================================
# Scan Existing Structure (Keep Mode)
# ============================================================


def scan_existing_structure(workspace):
    """
    Scan existing directory structure, return {directory_name: [doc_paths]}
    扫描现有目录结构
    """
    structure = defaultdict(list)

    for root, dirs, files in os.walk(workspace):
        # Skip output directories
        root_parts = set(Path(root).parts)
        if any(d in root_parts for d in SKIP_DIRS):
            continue
        for f in files:
            if Path(f).suffix.lower() in DOC_EXTENSIONS:
                rel_path = Path(root).relative_to(workspace)
                if rel_path.parts:
                    cat_name = rel_path.parts[0]
                else:
                    cat_name = "root"
                structure[cat_name].append(Path(root) / f)

    return dict(structure)


# ============================================================
# Init Mode
# ============================================================


def run_init(workspace):
    """Initialize: ask mode, create structure, batch convert / 初始化模式"""

    # Ask user for mode selection
    mode = ask_classify_mode()

    init_log(workspace)

    if mode == "keep":
        log("\n[MODE] Keep original directory structure / 保持原有目录结构")
        log("=" * 60)
        categories = scan_existing_structure(workspace)
        if not categories:
            log("[WARN] No documents found / 未发现任何文档")
            return
        log(f"Found {len(categories)} original directories / 发现 {len(categories)} 个原始目录")
        for cat, docs in sorted(categories.items()):
            log(f"  {cat}/ ({len(docs)} docs)")
    else:
        log("\n[MODE] Auto-analyze & categorize / 系统自动分析创建分类")
        log("=" * 60)
        categories = analyze_and_categorize(workspace)
        if not categories:
            log("[WARN] No documents found / 未发现任何文档")
            return

    # Create directory structure
    move_map = create_folder_structure(workspace, categories)

    # Batch convert
    log("\n[STEP 5] Converting documents to Markdown...")
    total = len(move_map)
    success = 0
    failed = []

    for src_str, dst in move_map.items():
        src = Path(src_str)
        log(f"  [{success+1}/{total}] {src.name}")
        if convert_single(src, dst.with_suffix("")):
            success += 1
            log(f"    [OK]")
        else:
            failed.append(src_str)
            log(f"    [FAIL]")

    # Generate index
    log("\n[STEP 6] Generating document index...")
    generate_index(workspace, categories)

    # Report
    log("\n" + "=" * 60)
    log(f"[RESULT] Conversion complete: {success}/{total} succeeded / 转换完成: {success}/{total} 成功")
    if failed:
        log(f"Failed files / 失败文件数: {len(failed)}")
        for f in failed:
            log(f"  - {f}")
    else:
        log("All succeeded! / 全部成功!")
    log("=" * 60)
    log(f"\n[INDEX] Document index / 文档索引: {workspace / DOCS_MD_DIR / INDEX_FILE}")
    log(f"[LOG] Processing log / 处理日志: {LOG_FILE}")


# ============================================================
# Index Generation
# ============================================================


def generate_index(workspace, categories):
    """Generate document index / 生成文档索引"""
    md_base = workspace / DOCS_MD_DIR
    index_file = md_base / INDEX_FILE

    lines = [
        "# Document Index / 文档索引\n",
        f"> Auto-generated by DocHub v3 / 自动生成\n\n",
        f"## Categories / 分类目录\n\n",
    ]

    for cat_name, docs in sorted(categories.items()):
        md_files = []
        for doc in docs:
            md_path = md_base / cat_name / (doc.stem + ".md")
            if md_path.exists():
                md_files.append(md_path)

        if md_files:
            lines.append(f"### {cat_name} ({len(md_files)} files)\n")
            for mf in sorted(md_files):
                rel = mf.relative_to(md_base)
                lines.append(f"- [{mf.stem}]({rel.as_posix()})")
            lines.append("\n")

    try:
        with open(index_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
    except Exception as e:
        log(f"[ERROR] Failed to write index: {e}")


# ============================================================
# Process Update Folder
# ============================================================


def process_update_folder(workspace):
    """
    Process new documents in update/ folder:
    1. Analyze content → match category
    2. Copy to categorized directory
    3. Incremental convert
    4. Clear update/
    处理 update/ 中的新文档
    """
    update_dir = workspace / UPDATE_DIR
    md_base = workspace / DOCS_MD_DIR

    if not update_dir.exists() or not any(update_dir.iterdir()):
        log(f"[WARN] {UPDATE_DIR}/ is empty or does not exist")
        return

    # Path traversal guard for update_dir
    safe_update = sanitize_path(workspace, UPDATE_DIR)
    if safe_update is None:
        log(f"[ERROR] Unsafe update directory path")
        return

    log(f"\n[UPDATE] Processing new documents in {UPDATE_DIR}/...")
    log("=" * 50)

    # Get existing category directories
    existing_cats = [d.name for d in md_base.iterdir() if d.is_dir() and not d.name.startswith("_")]

    new_docs = list(safe_update.iterdir())
    for doc in new_docs:
        if doc.is_dir():
            continue
        # Analyze content
        fd, tmp = tempfile.mkstemp(suffix=doc.suffix)
        os.close(fd)
        kw = []
        try:
            shutil.copy2(doc, tmp)
            result = subprocess.run(
                MARKITDOWN_CMD + [tmp],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0 and result.stdout.strip():
                kw = extract_keywords(result.stdout)
        except subprocess.TimeoutExpired:
            log(f"  [WARN] Timeout analyzing {doc.name}")
        except Exception:
            pass
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)

        # Simple keyword matching
        matched_cat = None
        for cat in existing_cats:
            cat_clean = cat.replace("docs_", "")
            for word, _ in kw[:5]:
                if cat_clean in word or word in cat_clean:
                    matched_cat = cat
                    break
            if matched_cat:
                break

        if not matched_cat:
            matched_cat = "Other"

        # Copy to category directory with path traversal guard
        safe_cat = sanitize_path(md_base, matched_cat)
        if safe_cat is None:
            log(f"  [SKIP] Unsafe category: {matched_cat} for {doc.name}")
            continue
        safe_cat.mkdir(exist_ok=True)

        dest = sanitize_path(safe_cat, doc.name)
        if dest is None:
            log(f"  [SKIP] Unsafe filename: {doc.name}")
            continue

        shutil.copy2(doc, dest)
        log(f"  {doc.name} -> {matched_cat}/")

        # Incremental convert
        convert_single(dest, dest.with_suffix(""))

    # Clear update folder
    for doc in new_docs:
        if doc.is_file():
            try:
                doc.unlink()
            except Exception:
                pass
    log(f"\n{UPDATE_DIR}/ cleared (folder preserved) / 已清空（保留空文件夹）")


# ============================================================
# Main Entry
# ============================================================


def main():
    if len(sys.argv) < 2:
        print("Usage / 用法:")
        print("  python batch_convert.py init [--mode 1|2] <workspace>")
        print("  python batch_convert.py run <workspace>")
        print("  python batch_convert.py process <workspace>")
        print()
        print("  --mode 1  Keep original structure (default) / 保持原有目录结构（默认）")
        print("  --mode 2  Auto-analyze & categorize / 系统自动分析创建分类")
        sys.exit(1)

    mode = sys.argv[1].lower()
    # Extract workspace (skip --mode and its value)
    args = [a for i, a in enumerate(sys.argv[2:], 2)
            if not (a == "--mode" or (i > 2 and sys.argv[i-1] == "--mode"))]
    workspace = Path(args[0]).resolve() if args else Path.cwd()

    # Validate workspace
    workspace = validate_workspace(workspace)

    if mode == "init":
        run_init(workspace)
    elif mode == "run":
        run_incremental(workspace)
    elif mode == "process":
        process_update_folder(workspace)
    else:
        log(f"[ERROR] Unknown mode / 未知模式: {mode}")
        log("  Supported / 支持的模式: init / run / process")
        sys.exit(1)


if __name__ == "__main__":
    main()
