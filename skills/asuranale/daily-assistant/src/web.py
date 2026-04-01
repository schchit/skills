"""
日常小助手 — Web UI 面板

本地 Web 界面，浏览器访问 http://localhost:5000 即可管理任务。
与 MCP Server (server.py) 共享 core.py 和 config.json。

用法:
    py -X utf8 web.py
    py -X utf8 web.py --port 8080
"""

import json
import sys
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from core import (
    get_tasks_with_lines, toggle_task, add_task_to_file, delete_task,
    scan_overdue_files,
    find_latest_daily, extract_uncompleted_tasks, create_today_file,
    mark_tasks_inherited,
    parse_all_tasks, generate_review as _generate_review_text,
    scan_split_needed,
    t,
)


# ============================================================
# 配置
# ============================================================

SCRIPT_DIR = Path(__file__).parent.resolve()
STATIC_DIR = SCRIPT_DIR / "static"
CONFIG_PATH = SCRIPT_DIR / "config.json"


def load_config() -> dict:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    raise FileNotFoundError("config.json not found. Run setup.py first.")


config = load_config()
DAILY_DIR = Path(config["daily_dir"])

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="/static")


def get_lang():
    return config.get("language", "zh")


# ============================================================
# 页面
# ============================================================

@app.route("/")
def index():
    return send_from_directory(str(STATIC_DIR), "index.html")


# ============================================================
# API — 任务
# ============================================================

@app.route("/api/tasks")
def api_tasks():
    date = request.args.get("date", datetime.now().strftime("%Y-%m-%d"))
    file_path = DAILY_DIR / f"{date}.md"
    if not file_path.exists():
        return jsonify({"tasks": [], "exists": False, "date": date})
    today = datetime.strptime(date, "%Y-%m-%d")
    tasks = get_tasks_with_lines(file_path, today)
    return jsonify({"tasks": tasks, "exists": True, "date": date})


@app.route("/api/tasks/toggle", methods=["POST"])
def api_toggle():
    data = request.json
    date = data.get("date", datetime.now().strftime("%Y-%m-%d"))
    line = data.get("line")
    file_path = DAILY_DIR / f"{date}.md"
    if not file_path.exists():
        return jsonify({"success": False, "error": "File not found"})
    result = toggle_task(file_path, line)
    return jsonify(result)


@app.route("/api/tasks/create", methods=["POST"])
def api_create():
    data = request.json
    date = data.get("date", datetime.now().strftime("%Y-%m-%d"))
    file_path = DAILY_DIR / f"{date}.md"
    if not file_path.exists():
        return jsonify({"success": False, "error": "File not found"})
    result = add_task_to_file(
        file_path,
        data["description"],
        data.get("est_minutes"),
        data.get("deadline"),
        data.get("priority", "medium"),
    )
    return jsonify(result)


@app.route("/api/tasks/delete", methods=["POST"])
def api_delete():
    data = request.json
    date = data.get("date", datetime.now().strftime("%Y-%m-%d"))
    line = data.get("line")
    file_path = DAILY_DIR / f"{date}.md"
    if not file_path.exists():
        return jsonify({"success": False, "error": "File not found"})
    result = delete_task(file_path, line)
    return jsonify(result)


# ============================================================
# API — 操作
# ============================================================

@app.route("/api/inherit", methods=["POST"])
def api_inherit():
    lang = get_lang()
    data = request.json or {}
    date_str = data.get("date", datetime.now().strftime("%Y-%m-%d"))
    today = datetime.strptime(date_str, "%Y-%m-%d")
    file_path = DAILY_DIR / f"{date_str}.md"

    if file_path.exists():
        return jsonify({"success": False,
                        "message": t("srv_already_exists", lang, file=f"{date_str}.md")})

    latest = find_latest_daily(DAILY_DIR, before_date=today)
    if not latest:
        create_today_file(DAILY_DIR, today, [], None, lang)
        return jsonify({"success": True,
                        "message": t("srv_no_previous", lang, file=f"{date_str}.md"),
                        "inherited": 0})

    uncompleted = extract_uncompleted_tasks(latest)
    if not uncompleted:
        create_today_file(DAILY_DIR, today, [], None, lang)
        return jsonify({"success": True,
                        "message": t("srv_all_completed", lang,
                                     src=latest.name, file=f"{date_str}.md"),
                        "inherited": 0})

    source_date = latest.stem
    create_today_file(DAILY_DIR, today, uncompleted, source_date, lang)
    marked = mark_tasks_inherited(latest, date_str)

    return jsonify({
        "success": True,
        "message": t("srv_inherit_done", lang,
                     file=f"{date_str}.md", src=latest.name,
                     marked=marked, count=len(uncompleted)),
        "inherited": len(uncompleted),
    })


@app.route("/api/review", methods=["POST"])
def api_review():
    lang = get_lang()
    data = request.json or {}
    date_str = data.get("date", datetime.now().strftime("%Y-%m-%d"))
    file_path = DAILY_DIR / f"{date_str}.md"

    if not file_path.exists():
        return jsonify({"success": False,
                        "message": t("srv_no_daily_file", lang, file=f"{date_str}.md")})

    content = file_path.read_text(encoding="utf-8")
    completed, uncompleted = parse_all_tasks(content)
    total = len(completed) + len(uncompleted)

    if total == 0:
        return jsonify({"success": False, "message": t("srv_no_task_record", lang)})

    review = _generate_review_text(completed, uncompleted, date_str, lang)

    # 写入文件
    marker_zh = "## 📊 日终回顾（自动生成"
    marker_en = "## 📊 Daily Review (auto-generated"
    if marker_zh in content or marker_en in content:
        split_marker = marker_zh if marker_zh in content else marker_en
        parts = content.split(split_marker)
        before = parts[0].rstrip()
        new_content = before + "\n\n" + review + "\n"
    else:
        manual_zh = "## 📊 日终回顾"
        manual_en = "## 📊 End of Day Review"
        if manual_zh in content:
            before = content[: content.index(manual_zh)].rstrip()
            new_content = before + "\n\n" + review + "\n"
        elif manual_en in content:
            before = content[: content.index(manual_en)].rstrip()
            new_content = before + "\n\n" + review + "\n"
        else:
            new_content = content.rstrip() + "\n\n" + review + "\n"

    file_path.write_text(new_content, encoding="utf-8")
    return jsonify({"success": True, "review": review})


# ============================================================
# API — 统计
# ============================================================

@app.route("/api/overdue")
def api_overdue():
    date_str = request.args.get("date", datetime.now().strftime("%Y-%m-%d"))
    today = datetime.strptime(date_str, "%Y-%m-%d")
    overdue = scan_overdue_files(DAILY_DIR, today)
    items = [{"date": it["date"], "days_ago": it["days_ago"],
              "tasks": it["uncompleted"]} for it in overdue]
    return jsonify({"overdue": items, "count": len(overdue)})


@app.route("/api/history")
def api_history():
    today = datetime.now()
    days = []
    for i in range(7):
        day = today - timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        day_file = DAILY_DIR / f"{day_str}.md"
        if not day_file.exists():
            days.append({"date": day_str, "completed": 0, "uncompleted": 0,
                         "total": 0, "exists": False})
            continue
        content = day_file.read_text(encoding="utf-8")
        completed, uncompleted = parse_all_tasks(content)
        days.append({
            "date": day_str,
            "completed": len(completed),
            "uncompleted": len(uncompleted),
            "total": len(completed) + len(uncompleted),
            "exists": True,
        })
    return jsonify({"history": days})


@app.route("/api/split")
def api_split():
    date_str = request.args.get("date", datetime.now().strftime("%Y-%m-%d"))
    today = datetime.strptime(date_str, "%Y-%m-%d")
    issues = scan_split_needed(DAILY_DIR, today)
    return jsonify({"issues": issues, "count": len(issues)})


# ============================================================
# API — 配置
# ============================================================

@app.route("/api/config")
def api_get_config():
    return jsonify({
        "language": config.get("language", "zh"),
        "daily_dir": config.get("daily_dir", ""),
    })


@app.route("/api/config", methods=["PUT"])
def api_update_config():
    data = request.json
    if "language" in data:
        config["language"] = data["language"]
    CONFIG_PATH.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return jsonify({"success": True})


# ============================================================
# 入口
# ============================================================

if __name__ == "__main__":
    port = 5000
    if "--port" in sys.argv:
        idx = sys.argv.index("--port")
        if idx + 1 < len(sys.argv):
            port = int(sys.argv[idx + 1])

    print(f"🚀 日常小助手 Web UI")
    print(f"   http://localhost:{port}")
    print(f"   Ctrl+C 停止")

    webbrowser.open(f"http://localhost:{port}")
    app.run(host="127.0.0.1", port=port, debug=False)
