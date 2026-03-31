#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

SECTION_TITLE_DEFAULT = "三、模型列表与倍率价格表（所有模型可用）"
TITLE_DEFAULT = "贵州大模型算力倍率更新啦"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"


def fetch_html(url: str) -> str:
    try:
        import requests  # type: ignore
    except Exception as e:
        raise RuntimeError(f"缺少 requests 依赖: {e}")

    resp = requests.get(
        url,
        timeout=30,
        headers={"User-Agent": USER_AGENT},
        allow_redirects=True,
    )
    resp.raise_for_status()
    resp.encoding = resp.encoding or "utf-8"
    return resp.text


def extract_client_vars_json(html: str) -> dict[str, Any]:
    marker = "window.DATA = Object.assign({}, window.DATA, { clientVars: Object("
    start = html.find(marker)
    if start == -1:
        raise RuntimeError("找不到飞书页面数据块")
    start = html.find("Object(", start)
    if start == -1:
        raise RuntimeError("找不到 Object( 起点")
    start += len("Object(")

    brace = 0
    end = None
    for i in range(start, len(html)):
        ch = html[i]
        if ch == "{":
            brace += 1
        elif ch == "}":
            brace -= 1
            if brace == 0:
                end = i + 1
                break
    if end is None:
        raise RuntimeError("解析飞书 JSON 失败")
    return json.loads(html[start:end])


def block_plain_text(block_map: dict[str, Any], block_id: str) -> str:
    block = block_map.get(block_id)
    if not block:
        return ""
    data = block.get("data", {})
    parts: list[str] = []
    text_obj = data.get("text", {})
    initial = text_obj.get("initialAttributedTexts", {})
    text_map = initial.get("text", {})
    if isinstance(text_map, dict):
        for _, value in sorted(text_map.items(), key=lambda kv: kv[0]):
            if isinstance(value, str):
                parts.append(value)
    for child_id in data.get("children", []) or []:
        child_text = block_plain_text(block_map, child_id)
        if child_text:
            parts.append(child_text)
    return " ".join(p.strip() for p in parts if p and p.strip()).strip()


def find_target_table(block_map: dict[str, Any], sequence: list[str], section_title: str) -> tuple[str, str | None]:
    section_index = None
    effective_date = None
    for i, bid in enumerate(sequence):
        data = block_map[bid]["data"]
        if data.get("type") == "heading2" and block_plain_text(block_map, bid) == section_title:
            section_index = i
            break
    if section_index is None:
        raise RuntimeError(f"找不到目标章节：{section_title}")

    for bid in sequence[section_index + 1 :]:
        data = block_map[bid]["data"]
        btype = data.get("type")
        text = block_plain_text(block_map, bid)
        if btype == "heading2":
            break
        if btype == "heading1" and re.fullmatch(r"\d{4}-\d{2}-\d{2}\s*调整", text):
            effective_date = text.replace(" 调整", "")
        if btype == "table":
            return bid, effective_date
    raise RuntimeError("目标章节下找不到表格")


def table_to_rows(block_map: dict[str, Any], table_id: str) -> list[list[str]]:
    table = block_map[table_id]["data"]
    rows: list[list[str]] = []
    for row_id in table.get("rows_id", []):
        row: list[str] = []
        for col_id in table.get("columns_id", []):
            cell_key = f"{row_id}{col_id}"
            cell_info = table.get("cell_set", {}).get(cell_key)
            if not cell_info:
                row.append("")
                continue
            cell_block_id = cell_info.get("block_id")
            row.append(block_plain_text(block_map, cell_block_id))
        rows.append(row)
    return rows


def normalize_rows(rows: list[list[str]]) -> dict[str, Any]:
    if not rows:
        return {"headers": [], "items": []}
    headers = rows[0]
    items = []
    for row in rows[1:]:
        row = row + [""] * (len(headers) - len(row))
        item = {headers[i]: row[i].strip() for i in range(len(headers))}
        items.append(item)
    return {"headers": headers, "items": items}


def snapshot_from_url(url: str, section_title: str, title: str) -> dict[str, Any]:
    html = fetch_html(url)
    client_vars = extract_client_vars_json(html)
    data = client_vars["data"]
    block_map = data["block_map"]
    sequence = data["block_sequence"]
    table_id, effective_date = find_target_table(block_map, sequence, section_title)
    rows = table_to_rows(block_map, table_id)
    normalized = normalize_rows(rows)
    snapshot = {
        "url": url,
        "title": title,
        "section_title": section_title,
        "effective_date": effective_date,
        "headers": normalized["headers"],
        "items": normalized["items"],
    }
    snapshot["hash"] = hashlib.sha256(
        json.dumps(snapshot, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return snapshot


def summarize_item(item: dict[str, str]) -> str:
    vendor = item.get("厂家", "").strip()
    model = item.get("模型名称", "").strip()
    ratio = item.get("倍率", "").strip()
    price = item.get("1 亿 Tokens 价格（换算价格）", "").strip()
    left = " / ".join([p for p in [vendor, model] if p])
    right = " · ".join([p for p in [ratio, price] if p])
    return f"{left} -> {right}".strip(" -> ")


def diff_snapshots(old: dict[str, Any], new: dict[str, Any]) -> str:
    old_items = {json.dumps(item, ensure_ascii=False, sort_keys=True): item for item in old.get("items", [])}
    new_items = {json.dumps(item, ensure_ascii=False, sort_keys=True): item for item in new.get("items", [])}

    old_by_model = {item.get("模型名称", ""): item for item in old.get("items", [])}
    new_by_model = {item.get("模型名称", ""): item for item in new.get("items", [])}

    added_models = [m for m in new_by_model if m and m not in old_by_model]
    removed_models = [m for m in old_by_model if m and m not in new_by_model]
    common_models = [m for m in new_by_model if m in old_by_model]

    price_lines: list[str] = []
    for model in common_models:
        old_item = old_by_model[model]
        new_item = new_by_model[model]
        parts = []
        if (old_item.get("倍率", "") or "") != (new_item.get("倍率", "") or ""):
            parts.append(f"倍率 {old_item.get('倍率', '') or '空'} → {new_item.get('倍率', '') or '空'}")
        if (old_item.get("1 亿 Tokens 价格（换算价格）", "") or "") != (
            new_item.get("1 亿 Tokens 价格（换算价格）", "") or ""
        ):
            parts.append(
                f"价格 {old_item.get('1 亿 Tokens 价格（换算价格）', '') or '空'} → {new_item.get('1 亿 Tokens 价格（换算价格）', '') or '空'}"
            )
        if (old_item.get("厂家", "") or "") != (new_item.get("厂家", "") or ""):
            parts.append(f"厂家 {old_item.get('厂家', '') or '空'} → {new_item.get('厂家', '') or '空'}")
        if parts:
            price_lines.append(f"- **{model}**：" + "；".join(parts))

    extra_lines: list[str] = []
    if not added_models and not removed_models and not price_lines and old.get("hash") != new.get("hash"):
        old_extra = set(old_items) - set(new_items)
        new_extra = set(new_items) - set(old_items)
        if new_extra:
            extra_lines.extend(f"- {summarize_item(new_items[k])}" for k in sorted(new_extra))
        if old_extra:
            extra_lines.extend(f"- {summarize_item(old_items[k])}" for k in sorted(old_extra))

    has_effective_date_change = old.get("effective_date") != new.get("effective_date")
    if not (has_effective_date_change or added_models or removed_models or price_lines or extra_lines):
        return "NO_REPLY"

    summary_parts = []
    if added_models:
        summary_parts.append(f"新增 {len(added_models)}")
    if removed_models:
        summary_parts.append(f"移除 {len(removed_models)}")
    if price_lines:
        summary_parts.append(f"调价 {len(price_lines)}")
    if has_effective_date_change:
        summary_parts.append("版本更新")
    if not summary_parts:
        summary_parts.append("表格变化")

    lines = [
        f"# {new.get('title') or TITLE_DEFAULT}",
        "",
        f"- **文档**：{new['section_title']}",
        f"- **摘要**：{' · '.join(summary_parts)}",
    ]

    if has_effective_date_change:
        lines.append(f"- **版本**：{old.get('effective_date') or '无'} → {new.get('effective_date') or '无'}")
    elif new.get("effective_date"):
        lines.append(f"- **版本**：{new['effective_date']}")

    lines.append("")

    if price_lines:
        lines.append("## 💸 调价模型")
        lines.extend(price_lines)
        lines.append("")

    if added_models:
        lines.append("## 🆕 新增模型")
        lines.extend(f"- {summarize_item(new_by_model[m])}" for m in added_models)
        lines.append("")

    if removed_models:
        lines.append("## 🗑️ 移除模型")
        lines.extend(f"- {summarize_item(old_by_model[m])}" for m in removed_models)
        lines.append("")

    if extra_lines:
        lines.append("## 📝 其他表格变化")
        lines.extend(extra_lines)
        lines.append("")

    lines.append(f"- **链接**：{new['url']}")
    return "\n".join(line for line in lines if line is not None).rstrip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Monitor public Feishu table under a named section")
    parser.add_argument("url")
    parser.add_argument("--section-title", default=SECTION_TITLE_DEFAULT)
    parser.add_argument("--title", default=TITLE_DEFAULT)
    parser.add_argument("--state-dir", default=str(Path.home() / ".openclaw" / "workspace" / "data" / "feishu-monitors"))
    parser.add_argument("--print-snapshot", action="store_true")
    args = parser.parse_args()

    state_dir = Path(args.state_dir)
    state_dir.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(f"{args.url}::{args.section_title}".encode("utf-8")).hexdigest()[:16]
    state_path = state_dir / f"{key}.json"

    snapshot = snapshot_from_url(args.url, args.section_title, args.title)

    if args.print_snapshot:
        print(json.dumps(snapshot, ensure_ascii=False, indent=2))
        return 0

    if not state_path.exists():
        state_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
        print("INIT_ONLY")
        return 0

    old = json.loads(state_path.read_text(encoding="utf-8"))
    message = diff_snapshots(old, snapshot)
    if message != "NO_REPLY":
        state_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    print(message)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"飞书公开表格监控出错喵：{e}")
        raise
