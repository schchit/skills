#!/usr/bin/env python3
"""
Feishu Wiki → Obsidian PARA Sync (feishu-sync-obsidian)

从飞书多维表格读取映射规则，将飞书文档同步到本地 Obsidian vault。
支持按需创建 Obsidian 不存在的目录。

Usage:
    echo '[{"title":"...","obj_token":"...","obj_type":"docx","node_token":"...","wiki_name":"个人成长"}]' \
      | python3 sync.py --stdin [--dry-run]
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ── 路径配置 ──────────────────────────────────────────────────────────────
VAULT_DIR  = Path("/home/ink/个人知识库")
CACHE_DIR  = Path("/tmp/feishu-sync-obsidian")

# ── 飞书多维表格配置（PARA映射规则）─────────────────────────────────────
BITABLE_APP_TOKEN = "VfcMbtzZUaWpOKs6PeOcamEjn1f"
BITABLE_TABLE_ID  = "tblrRBUXGjBXda6z"

# ── Wiki Space 配置 ──────────────────────────────────────────────────────
WIKI_SPACES = {
    "个人成长":       "7619963059842419643",
    "openclaw知识库": "7617330356886178745",
}

# ── 缓存的映射规则（内存缓存）───────────────────────────────────────────
_mapping_cache: Dict[str, List[Tuple[str, str]]] = {}

# ── 内嵌规则（无 token 时使用，来自飞书表格快照）────────────────────────
EMBEDDED_RULES: Dict[str, List[Tuple[str, str]]] = {
    "个人成长": [
        ("软考笔记", "01务实之道/学习计划-软考"),
        ("软考",     "01务实之道/学习计划-软考"),
        ("学习计划", "01务实之道/学习计划-软考"),
        ("英语",     "01务实之道/英语学习"),
        ("三言二拍", "01务实之道/读书计划/三言二拍"),
        ("思维框架", "02修持之域/自我成长"),
        ("思维变迁", "02修持之域/自我成长"),
        ("人生困境", "02修持之域/自我成长"),
        ("认知框架", "02修持之域/自我成长"),
    ],
    "openclaw知识库": [
        ("事故",      "04归藏之府"),
        ("报告",      "04归藏之府"),
        ("skills",   "03藏珍之库/工具"),
        ("evoclaw",  "03藏珍之库/工具"),
        ("openclaw", "03藏珍之库/工具"),
        ("Proactive-Agent", "03藏珍之库/工具"),
        ("默认",     "03藏珍之库/工具"),
    ],
}

# ── 飞书 API ─────────────────────────────────────────────────────────────

def get_access_token() -> str:
    """获取飞书 Access Token。"""
    token = os.environ.get("FEISHU_ACCESS_TOKEN", "")
    if token:
        return token
    token_file = Path.home() / ".openclaw" / "plugins" / "feishu-oauth" / "tokens.json"
    if token_file.exists():
        try:
            tokens = json.loads(token_file.read_text())
            for k, v in tokens.items():
                if isinstance(v, dict) and "access_token" in v:
                    return v["access_token"]
        except Exception:
            pass
    print("[ERROR] No Feishu access token found. Set FEISHU_ACCESS_TOKEN env.", file=sys.stderr)
    sys.exit(1)

def feishu_get(endpoint: str, token: str) -> dict:
    """GET 请求飞书 Open API。"""
    import urllib.request
    url = f"https://open.feishu.cn/open-apis/{endpoint}"
    headers = {"Authorization": f"Bearer {token}"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            if result.get("code", 1) != 0:
                raise Exception(f"API error {result.get('code')}: {result.get('msg')}")
            return result.get("data", {})
    except Exception as e:
        print(f"[ERROR] GET {endpoint} failed: {e}", file=sys.stderr)
        return {}

# ── 从飞书表格读取映射规则 ───────────────────────────────────────────────

def load_rules_from_bitable(token: str, wiki_name: str) -> List[Tuple[str, str]]:
    """从飞书多维表格读取指定 wiki 的映射规则（无 token 时使用内嵌规则）。"""
    """
    从飞书多维表格读取指定 wiki 的映射规则。
    返回 [(关键词, 目标PARA路径), ...]，已按优先级排序。
    """
    global _mapping_cache
    cache_key = wiki_name

    if cache_key in _mapping_cache:
        return _mapping_cache[cache_key]

    # 无 token 时使用内嵌规则
    if not token:
        _mapping_cache[cache_key] = EMBEDDED_RULES.get(wiki_name, [])
        return _mapping_cache[cache_key]

    rules: List[Tuple[str, str]] = []
    page_token = ""

    while True:
        endpoint = f"bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{BITABLE_TABLE_ID}/records"
        params = f"?page_size=100&field_names=%5B%22wiki%E5%90%8D%E7%A7%B0%22,%22%E6%A0%87%E9%A2%98%E5%85%B3%E9%94%AE%E8%AF%8D%22,%22%E7%9B%AE%E6%A0%87PARA%E8%B7%AF%E5%BE%84%22,%22%E4%BC%98%E5%85%88%E7%BA%A7%22%5D"
        if page_token:
            params += f"&page_token={page_token}"
        data = feishu_get(endpoint + params, token)
        items = data.get("items", [])

        for item in items:
            fields = item.get("fields", {})
            wiki_field = fields.get("wiki名称", {})
            if isinstance(wiki_field, list) and len(wiki_field) > 0:
                wiki_val = wiki_field[0].get("text", "") if isinstance(wiki_field[0], dict) else str(wiki_field[0])
            elif isinstance(wiki_field, str):
                wiki_val = wiki_field
            else:
                wiki_val = ""
            if wiki_val != wiki_name:
                continue

            keyword = fields.get("标题关键词", "")
            para_path = fields.get("目标PARA路径", "")
            if keyword and para_path:
                rules.append((str(keyword), str(para_path)))

        if not data.get("has_more"):
            break
        page_token = data.get("page_token", "")
        if not page_token:
            break

    _mapping_cache[cache_key] = rules
    return rules


def resolve_para_folder(title: str, wiki_name: str, token: str) -> str:
    """
    根据标题和 wiki 名，从飞书表格规则中匹配 PARA 文件夹。
    规则：优先级最小（数字最小）最先命中；关键词精确包含即命中。
    """
    # 兜底路径
    fallback = "05进思斋" if wiki_name == "个人成长" else "03藏珍之库/工具"

    rules = load_rules_from_bitable(token, wiki_name)
    if not rules:
        return fallback

    title_lower = title.lower()

    # 优先级已经在表格里定义，这里取第一个命中（表格已按优先级排好）
    # 关键词精确包含匹配
    for keyword, folder in rules:
        if keyword == "默认":
            continue
        if keyword.lower() in title_lower or keyword in title:
            return folder

    # 默认兜底
    for keyword, folder in rules:
        if keyword == "默认":
            return folder

    return fallback

# ── Obsidian 写入 ───────────────────────────────────────────────────────────

def sanitize_filename(title: str) -> str:
    """标题转为安全文件名。"""
    s = re.sub(r'[\\/:*?"<>|]', "", title)
    s = re.sub(r'\s+', "-", s.strip())
    return s[:80] + ".md"

def ensure_obsidian_folder(para_path: str) -> Path:
    """确保 Obsidian 目录存在，不存在则新建。"""
    dest_dir = VAULT_DIR / para_path
    dest_dir.mkdir(parents=True, exist_ok=True)
    return dest_dir

def build_frontmatter(doc_token: str, node_token: str, wiki_name: str,
                     created: str, doc_type: str = "随记",
                     status: str = "2-进行中") -> str:
    """生成 YAML frontmatter。"""
    return f"""---
type: {doc_type}
status: {status}
tags: [来源/飞书同步]
created: {created}
feishu_doc_token: {doc_token}
feishu_node_token: {node_token}
feishu_wiki: {wiki_name}
---"""

def find_existing_by_doc_token(doc_token: str) -> Optional[Path]:
    """在 vault 中查找是否已存在相同 feishu_doc_token 的文件。"""
    if not doc_token:
        return None
    for md_file in VAULT_DIR.rglob("*.md"):
        try:
            text = md_file.read_text(encoding="utf-8")
            if text.startswith("---"):
                end = text.find("\n---", 3)
                if end < 0:
                    continue
                fm_text = text[3:end]
                for line in fm_text.splitlines():
                    if line.strip().startswith("feishu_doc_token:"):
                        existing_token = line.split(":", 1)[1].strip()
                        if existing_token == doc_token:
                            return md_file
        except Exception:
            continue
    return None

def write_obsidian_file(folder: str, title: str, content: str,
                        doc_token: str, node_token: str, wiki_name: str,
                        dry_run: bool = False) -> Optional[str]:
    """写入 Obsidian 文件，返回路径（已存在则返回 None）。"""
    # 去重：检查 vault 中是否已有相同 feishu_doc_token 的文件
    existing = find_existing_by_doc_token(doc_token)
    if existing:
        print(f"  [SKIP] {title} → 已存在，跳过写入 ({existing.name})")
        return None

    dest_dir = ensure_obsidian_folder(folder)
    filename = sanitize_filename(title)
    dest_path = dest_dir / filename

    # 避免重名（文件名冲突）
    counter = 1
    while dest_path.exists() and counter < 100:
        dest_path = dest_dir / sanitize_filename(f"{title}-{counter}")
        counter += 1

    if dry_run:
        print(f"  [DRY-RUN] {title} → {folder}/{dest_path.name}")
        return str(dest_path)

    frontmatter = build_frontmatter(
        doc_token, node_token, wiki_name,
        datetime.now().strftime("%Y-%m-%d")
    )
    full_content = f"{frontmatter}\n\n{content}"
    dest_path.write_text(full_content, encoding="utf-8")
    print(f"  [SYNCED] {title} → {folder}/{dest_path.name}")
    return str(dest_path)

# ── 主流程 ─────────────────────────────────────────────────────────────────

def main_from_nodes(nodes: List[dict], dry_run: bool = False):
    """从节点列表同步到 Obsidian（Agent 调用模式）。"""
    print(f"\n{'[DRY-RUN] ' if dry_run else ''}Feishu → Obsidian Sync")
    print(f"Vault: {VAULT_DIR}")
    print(f"Rules source: Feishu Bitable ({BITABLE_APP_TOKEN})")
    print()

    token = get_access_token() if "--no-token" not in sys.argv else ""
    sync_date = datetime.now().strftime("%Y-%m-%d")
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    all_synced_files = []

    # 按 wiki 分组
    for wiki_name, space_id in WIKI_SPACES.items():
        wiki_nodes = [n for n in nodes if n.get("wiki_name") == wiki_name
                     or n.get("space_id") == space_id]
        if not wiki_nodes:
            continue
        print(f"[INFO] Syncing wiki: {wiki_name} ({len(wiki_nodes)} nodes)")

        for node in wiki_nodes:
            obj_type = node.get("obj_type", "")
            title = node.get("title", "未命名")
            node_token = node.get("node_token", "")
            obj_token = node.get("obj_token", "")
            content = node.get("content", "")
            node_wiki = node.get("wiki_name", wiki_name)

            if not content:
                content = (f"[内容由 Agent 通过 feishu_fetch_doc 获取]\n"
                           f"obj_token: {obj_token}\nobj_type: {obj_type}")

            folder = resolve_para_folder(title, node_wiki, token)

            path = write_obsidian_file(
                folder, title, content,
                obj_token, node_token, node_wiki,
                dry_run=dry_run
            )
            if path:
                all_synced_files.append(path)

    cache_file = CACHE_DIR / "sync_state.json"
    cache_file.write_text(json.dumps({
        "sync_date": sync_date,
        "files": all_synced_files
    }, ensure_ascii=False, indent=2))

    print(f"\n[OK] {len(all_synced_files)} files processed.")
    if dry_run:
        print("(dry run - no files written)")


def main_stdin(dry_run: bool = False):
    """从 stdin 读取 JSON 节点列表。"""
    nodes = json.loads(sys.stdin.read())
    if not isinstance(nodes, list):
        print("[ERROR] Expected JSON array of nodes", file=sys.stderr)
        sys.exit(1)
    main_from_nodes(nodes, dry_run=dry_run)


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    if "--stdin" in sys.argv:
        main_stdin(dry_run=dry_run)
    else:
        print("[ERROR] 请使用 --stdin 模式传入节点数据", file=sys.stderr)
        print("示例: echo '[...]' | python3 sync.py --stdin [--dry-run]", file=sys.stderr)
        sys.exit(1)
