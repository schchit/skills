#!/usr/bin/env python3
"""skills-audit/scripts/skills_audit.py

Strict-template skills audit logger.

- Watches or scans /root/.openclaw/workspace/skills (caller decides)
- Emits NDJSON records strictly based on skills-audit/log-template.json
- Fields slug/version/owner_id are sourced from each skill's _meta.json

Outputs:
- ~/.openclaw/skills-audit/logs.ndjson (append-only)
- ~/.openclaw/skills-audit/state.json (snapshot for diff)

Recommended use:
  python3 skills/skills-audit/scripts/skills_audit.py scan --workspace /root/.openclaw/workspace --who cron --channel local

"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import uuid


def iso_utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_cmd(argv: list[str]) -> tuple[int, str, str]:
    try:
        p = subprocess.run(argv, capture_output=True, text=True, check=False)
        return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()
    except FileNotFoundError as e:
        return 127, "", str(e)


def md5_file(path: Path) -> str | None:
    try:
        h = hashlib.md5()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def sha256_file(path: Path) -> str | None:
    try:
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def safe_read_text(path: Path, max_bytes: int = 512_000) -> str:
    try:
        with path.open("rb") as f:
            data = f.read(max_bytes)
        return data.decode("utf-8", errors="replace")
    except Exception:
        return ""


def load_json(path: Path) -> dict | None:
    try:
        return json.loads(safe_read_text(path))
    except Exception:
        return None


def list_files(dir_path: Path) -> list[Path]:
    files: list[Path] = []
    for p in dir_path.rglob("*"):
        if p.is_file():
            if "/.git/" in str(p):
                continue
            files.append(p)
    files.sort(key=lambda x: str(x))
    return files


RISK_RULES = [
    ("PIPE_TO_SHELL", "high", ["| sh", "| bash", "curl |", "wget |", "Invoke-WebRequest", "iex"]),
    ("DYNAMIC_EXEC", "high", ["eval(", "eval ", "exec(", "subprocess.Popen", "os.system"]),
    ("BASE64_PIPE", "high", ["base64 -d", "base64 --decode"]),
    ("PERSISTENCE", "high", ["crontab", "systemctl enable", "launchctl", "/etc/systemd", "@reboot"]),
    ("SENSITIVE_PATHS", "high", ["~/.ssh", "authorized_keys", "/etc/ssh", "~/.aws", "id_rsa"]),
    ("NETWORK", "medium", ["http://", "https://", "curl ", "wget ", "requests."]),
]


def scan_risk(skill_dir: Path) -> dict:
    findings = []
    domains: set[str] = set()

    def extract_domains(text: str) -> None:
        for proto in ("http://", "https://"):
            start = 0
            while True:
                i = text.find(proto, start)
                if i == -1:
                    break
                j = i + len(proto)
                k = j
                while k < len(text) and text[k] not in "/\"' \n\r\t)":
                    k += 1
                host = text[j:k]
                if host and len(host) < 200:
                    domains.add(host)
                start = k

    for p in list_files(skill_dir):
        if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".zip", ".tar", ".gz", ".bin"}:
            continue
        if p.stat().st_size > 1_500_000:
            continue
        text = safe_read_text(p)
        if not text:
            continue
        extract_domains(text)
        for rule_id, severity, needles in RISK_RULES:
            for n in needles:
                if n in text:
                    findings.append(
                        {
                            "rule_id": rule_id,
                            "severity": severity,
                            "evidence": {
                                "file": str(p.relative_to(skill_dir)),
                                "line": None,
                                "snippet": n,
                            },
                        }
                    )
                    break

    # risk level heuristic
    level = "low"
    if any(f["severity"] == "high" for f in findings):
        level = "high"
    elif any(f["severity"] == "medium" for f in findings):
        level = "medium"

    decision = {
        "low": "allow",
        "medium": "allow_with_caution",
        "high": "require_sandbox",
        "extreme": "deny",
    }.get(level, "allow_with_caution")

    return {
        "level": level,
        "decision": decision,
        "risk_signals": findings[:200],
        "dependencies": {"added": [], "removed": [], "changed": []},
        "network": {
            "domains": sorted(domains)[:200],
            "ips": [],
            "evidence_files": [],
        },
    }


def compute_tree_sha256(skill_dir: Path) -> str:
    h = hashlib.sha256()
    for f in list_files(skill_dir):
        rel = str(f.relative_to(skill_dir))
        h.update(rel.encode())
        try:
            st = f.stat()
            h.update(str(st.st_size).encode())
        except Exception:
            h.update(b"0")
        sh = sha256_file(f) or ""
        h.update(sh.encode())
    return h.hexdigest()


def load_template(workspace_dir: Path) -> dict:
    tpl_path = workspace_dir / "skills" / "skills-audit" / "log-template.json"
    tpl = load_json(tpl_path)
    if not isinstance(tpl, dict):
        raise RuntimeError(f"template not found or invalid json: {tpl_path}")
    return tpl


def append_ndjson(path: Path, rec: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def load_state(path: Path) -> dict:
    if not path.exists():
        return {"skills": {}}
    try:
        return json.loads(path.read_text("utf-8"))
    except Exception:
        return {"skills": {}}


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", "utf-8")


def skill_meta(skill_dir: Path) -> dict:
    meta = load_json(skill_dir / "_meta.json") or {}
    # normalize keys
    owner_id = meta.get("ownerId") or meta.get("owner_id") or ""
    slug = meta.get("slug") or skill_dir.name
    version = meta.get("version") or "unknown"
    return {"owner_id": owner_id, "slug": slug, "version": version, "raw": meta}


def tool_versions() -> dict:
    rc, out, _ = run_cmd(["openclaw", "--version"])
    openclaw_ver = out.splitlines()[0] if rc == 0 and out else "unknown"

    sh_rc, sh_out, _ = run_cmd(["skillhub", "--version"])
    skillhub_ver = sh_out.splitlines()[0] if sh_rc == 0 and sh_out else "unknown"

    ch_rc, ch_out, _ = run_cmd(["clawhub", "--version"])
    clawhub_ver = ch_out.splitlines()[0] if ch_rc == 0 and ch_out else "unknown"

    return {
        "openclaw_version": openclaw_ver,
        "skillhub_version": skillhub_ver,
        "clawhub_cli_version": clawhub_ver,
        "platform": platform.platform(),
    }


def build_record(
    template: dict,
    *,
    action: str,
    result: str,
    meta: dict,
    install_path: str | None,
    workspace_dir: str,
    md5: str | None,
    before_tree: str | None,
    after_tree: str | None,
    who: str,
    channel: str,
    risk: dict | None,
) -> dict:
    rec = copy.deepcopy(template)

    # top-level required fields
    rec["time"] = iso_utc_now()
    rec["log_id"] = str(uuid.uuid4())
    rec["action"] = action
    rec["result"] = result

    rec["owner_id"] = meta.get("owner_id", "")
    rec["slug"] = meta.get("slug", "")
    rec["version"] = meta.get("version", "unknown")
    rec["md5"] = md5

    # observed
    obs = rec.get("observed") or {}
    tv = tool_versions()
    obs["install_path"] = install_path
    obs["workspace_dir"] = workspace_dir
    obs["openclaw_version"] = tv["openclaw_version"]
    obs["skillhub_version"] = tv["skillhub_version"]
    obs["clawhub_cli_version"] = tv["clawhub_cli_version"]
    rec["observed"] = obs

    # operator
    op = rec.get("operator") or {}
    op["who"] = who
    op["channel"] = channel
    rec["operator"] = op

    # risk
    rec["risk"] = risk

    # capabilities: keep template default unless we can infer later (optional)

    # command / notes: keep template defaults

    # include diff inside notes (template doesn't have diff field)
    rec["notes"] = (
        f"auto-scan. before_tree_sha256={before_tree or 'null'} after_tree_sha256={after_tree or 'null'}. "
        f"platform={tv['platform']}"
    )

    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_init = sub.add_parser("init")
    ap_init.add_argument("--workspace", default=str(Path.cwd()))

    ap_scan = sub.add_parser("scan")
    ap_scan.add_argument("--workspace", default=str(Path.cwd()))
    ap_scan.add_argument("--who", default="cron")
    ap_scan.add_argument("--channel", default="local")

    args = ap.parse_args()

    workspace_dir = Path(args.workspace).resolve()
    skills_dir = workspace_dir / "skills"

    logs_dir = Path.home() / ".openclaw" / "skills-audit"
    log_path = logs_dir / "logs.ndjson"
    state_path = logs_dir / "state.json"

    if args.cmd == "init":
        logs_dir.mkdir(parents=True, exist_ok=True)
        if not state_path.exists():
            save_state(state_path, {"skills": {}, "created_at": iso_utc_now()})
        if not log_path.exists():
            log_path.write_text("", "utf-8")
        print(f"Initialized logs at {log_path}")
        print(f"Initialized state at {state_path}")
        return 0

    template = load_template(workspace_dir)

    prev = load_state(state_path).get("skills", {})
    now = {}

    if skills_dir.exists():
        for p in skills_dir.iterdir():
            if not p.is_dir():
                continue
            if p.name.startswith("."):
                continue
            meta = skill_meta(p)
            md5 = md5_file(p / "SKILL.md") if (p / "SKILL.md").exists() else None
            tree = compute_tree_sha256(p)
            now[p.name] = {
                "meta": meta,
                "install_path": str(p),
                "md5": md5,
                "tree_sha256": tree,
            }

    prev_keys = set(prev.keys())
    now_keys = set(now.keys())

    added = sorted(now_keys - prev_keys)
    removed = sorted(prev_keys - now_keys)
    common = sorted(now_keys & prev_keys)
    changed = [k for k in common if prev[k].get("tree_sha256") != now[k].get("tree_sha256")]

    # emit logs
    for k in added:
        entry = now[k]
        risk = scan_risk(Path(entry["install_path"]))
        rec = build_record(
            template,
            action="scan-detected",
            result="success",
            meta=entry["meta"],
            install_path=entry["install_path"],
            workspace_dir=str(workspace_dir),
            md5=entry["md5"],
            before_tree=None,
            after_tree=entry["tree_sha256"],
            who=args.who,
            channel=args.channel,
            risk=risk,
        )
        append_ndjson(log_path, rec)

    for k in changed:
        entry = now[k]
        risk = scan_risk(Path(entry["install_path"]))
        rec = build_record(
            template,
            action="scan-detected",
            result="success",
            meta=entry["meta"],
            install_path=entry["install_path"],
            workspace_dir=str(workspace_dir),
            md5=entry["md5"],
            before_tree=prev[k].get("tree_sha256"),
            after_tree=entry["tree_sha256"],
            who=args.who,
            channel=args.channel,
            risk=risk,
        )
        append_ndjson(log_path, rec)

    for k in removed:
        entry = prev[k]
        # removed: no risk scan
        meta = entry.get("meta") or {"owner_id": entry.get("owner_id", ""), "slug": entry.get("slug", k), "version": entry.get("version", "unknown")}
        rec = build_record(
            template,
            action="scan-detected",
            result="success",
            meta=meta,
            install_path=None,
            workspace_dir=str(workspace_dir),
            md5=entry.get("md5"),
            before_tree=entry.get("tree_sha256"),
            after_tree=None,
            who=args.who,
            channel=args.channel,
            risk=None,
        )
        append_ndjson(log_path, rec)

    # save state
    save_state(
        state_path,
        {
            "updated_at": iso_utc_now(),
            "skills": now,
        },
    )

    print(
        json.dumps(
            {
                "added": added,
                "changed": changed,
                "removed": removed,
                "log_path": str(log_path),
                "state_path": str(state_path),
            },
            ensure_ascii=False,
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
