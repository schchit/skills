#!/usr/bin/env python3
"""
n8n Skill – safe, admin-approved workflow management via REST API.

Usage:
  python3 skill.py list
  python3 skill.py get <workflow_id>
  python3 skill.py clone <workflow_id> [--suffix "_test"]
  python3 skill.py execute <workflow_id> [--input '{"key":"value"}']
  python3 skill.py check <execution_id>
  python3 skill.py promote <test_id> <original_id> [--confirm]
  python3 skill.py delete <workflow_id> [--confirm]
  python3 skill.py create --file workflow.json
  python3 skill.py activate <workflow_id>
  python3 skill.py deactivate <workflow_id>
  python3 skill.py history <workflow_id> [--limit 10]
"""

import os
import json
import sys
import time
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional

import requests
from dotenv import load_dotenv

# ── Load environment ────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
load_dotenv(SCRIPT_DIR / ".env")

BASE_URL = os.getenv("N8N_URL", "").rstrip("/")
API_TOKEN = os.getenv("N8N_API_TOKEN")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "nel@illicocash.com")

if not (BASE_URL and API_TOKEN):
    print("❗ N8N_URL and N8N_API_TOKEN must be set in .env or environment")
    sys.exit(1)

HEADERS = {
    "X-N8N-API-KEY": API_TOKEN,
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# ── API helpers ─────────────────────────────────────────────────
def api_get(path: str, params: Optional[Dict] = None) -> Any:
    resp = requests.get(f"{BASE_URL}{path}", headers=HEADERS, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()

def api_post(path: str, payload: Optional[Dict] = None) -> Any:
    resp = requests.post(f"{BASE_URL}{path}", headers=HEADERS, json=payload or {}, timeout=60)
    resp.raise_for_status()
    return resp.json()

def api_put(path: str, payload: Dict) -> Any:
    resp = requests.put(f"{BASE_URL}{path}", headers=HEADERS, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()

def api_delete(path: str) -> Any:
    resp = requests.delete(f"{BASE_URL}{path}", headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()

# ── Core functions ──────────────────────────────────────────────
def list_workflows(limit: int = 100) -> List[Dict]:
    """List all workflows."""
    data = api_get("/api/v1/workflows", {"limit": limit})
    return data.get("data", [])

def get_workflow(wid: str) -> Dict:
    """Fetch a single workflow."""
    return api_get(f"/api/v1/workflows/{wid}")

def clone_workflow(wid: str, suffix: str = "_test") -> Dict:
    """Clone a workflow with suffix."""
    orig = get_workflow(wid)
    new_name = f"{orig['name']}{suffix}"
    # Clean fields
    for key in ["id", "createdAt", "updatedAt", "active", "versionId"]:
        orig.pop(key, None)
    orig["name"] = new_name
    orig["active"] = False
    cloned = api_post("/api/v1/workflows", orig)
    print(f"✅ Cloned '{orig['name']}' → '{new_name}' (id={cloned['id']})")
    return cloned

def execute_workflow(wid: str, data: Optional[Dict] = None) -> Dict:
    """Execute a workflow and poll until finished."""
    payload: Dict[str, Any] = {"workflowId": wid}
    if data:
        payload["data"] = data
    exec_resp = api_post("/api/v1/executions", payload)
    exec_id = exec_resp.get("id")
    print(f"🚀 Execution started: {exec_id}")
    # Poll
    for _ in range(120):  # max 60 seconds
        time.sleep(0.5)
        status = api_get(f"/api/v1/executions/{exec_id}")
        if status.get("finished", False):
            break
    else:
        print("⚠️ Execution timed out (60s)")
    result = api_get(f"/api/v1/executions/{exec_id}")
    if result.get("finished"):
        print(f"✅ Execution finished (status: {result.get('status', 'unknown')})")
    else:
        print(f"⏳ Execution still running")
    return result

def sanity_checks(execution: Dict) -> List[str]:
    """Run sanity checks on execution result."""
    errors = []
    # 1. Node errors
    for node in execution.get("nodes", []):
        if node.get("error"):
            errors.append(f"Node '{node.get('name', '?')}' has error: {node.get('error', '')}")
    # 2. Execution status
    if execution.get("status") == "error":
        errors.append(f"Execution failed: {execution.get('error', {}).get('message', 'unknown')}")
    # 3. Duration check
    started = execution.get("startedAt", 0)
    stopped = execution.get("stoppedAt", 0)
    if started and stopped:
        duration_ms = stopped - started
        if duration_ms > 30000:
            errors.append(f"Execution took {duration_ms/1000:.1f}s (>30s)")
        else:
            print(f"  ⏱️ Duration: {duration_ms/1000:.1f}s")
    # 4. Data output check
    run_data = execution.get("data", {}).get("resultData", {}).get("runData", {})
    for node_name, runs in run_data.items():
        if not runs:
            errors.append(f"Node '{node_name}' produced no output")
    return errors

def promote_test_workflow(test_id: str, original_id: str) -> None:
    """Promote a test workflow to production."""
    orig = get_workflow(original_id)
    test = get_workflow(test_id)
    # 1. Deactivate original
    api_put(f"/api/v1/workflows/{original_id}", {"active": False})
    print(f"  ⏸️ Deactivated original: {orig['name']}")
    # 2. Rename test to original name
    api_put(f"/api/v1/workflows/{test_id}", {"name": orig["name"]})
    print(f"  ✏️ Renamed test to: {orig['name']}")
    # 3. Activate test (now bearing original name)
    api_put(f"/api/v1/workflows/{test_id}", {"active": True})
    print(f"  ▶️ Activated: {orig['name']}")
    print(f"🚀 Promoted test workflow to production")

def create_workflow(filepath: str) -> Dict:
    """Create a workflow from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    data.setdefault("active", False)
    result = api_post("/api/v1/workflows", data)
    print(f"✅ Workflow created: {data['name']} (id={result['id']})")
    return result

def activate_workflow(wid: str) -> None:
    api_put(f"/api/v1/workflows/{wid}", {"active": True})
    print(f"▶️ Workflow {wid} activated")

def deactivate_workflow(wid: str) -> None:
    api_put(f"/api/v1/workflows/{wid}", {"active": False})
    print(f"⏸️ Workflow {wid} deactivated")

def get_execution_history(wid: str, limit: int = 10) -> List[Dict]:
    """Get recent executions for a workflow."""
    data = api_get("/api/v1/executions", {"workflowId": wid, "limit": limit})
    return data.get("data", [])

# ── CLI ─────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="n8n Safe-Control Skill")
    sub = parser.add_subparsers(dest="command")

    # list
    sub.add_parser("list", help="List all workflows")

    # get
    p = sub.add_parser("get", help="Get workflow details")
    p.add_argument("workflow_id")

    # clone
    p = sub.add_parser("clone", help="Clone workflow")
    p.add_argument("workflow_id")
    p.add_argument("--suffix", default="_test")

    # execute
    p = sub.add_parser("execute", help="Execute workflow")
    p.add_argument("workflow_id")
    p.add_argument("--input", default=None, help="Input JSON data")

    # check
    p = sub.add_parser("check", help="Run sanity checks on execution")
    p.add_argument("execution_id")

    # promote
    p = sub.add_parser("promote", help="Promote test to production")
    p.add_argument("test_id")
    p.add_argument("original_id")
    p.add_argument("--confirm", action="store_true", help="Skip confirmation")

    # delete
    p = sub.add_parser("delete", help="Delete workflow (admin only)")
    p.add_argument("workflow_id")
    p.add_argument("--confirm", action="store_true", help="Skip confirmation")

    # create
    p = sub.add_parser("create", help="Create workflow from JSON")
    p.add_argument("--file", required=True, help="Workflow JSON file")

    # activate/deactivate
    p = sub.add_parser("activate", help="Activate workflow")
    p.add_argument("workflow_id")

    p = sub.add_parser("deactivate", help="Deactivate workflow")
    p.add_argument("workflow_id")

    # history
    p = sub.add_parser("history", help="Execution history")
    p.add_argument("workflow_id")
    p.add_argument("--limit", type=int, default=10)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == "list":
            wfs = list_workflows()
            print(f"\n🗂️  {len(wfs)} workflow(s):\n")
            for wf in wfs:
                status = "✅" if wf.get("active") else "⏸️"
                archived = " [ARCHIVED]" if wf.get("isArchived") else ""
                print(f"  {status} {wf['id']}: {wf['name']}{archived}")

        elif args.command == "get":
            wf = get_workflow(args.workflow_id)
            print(json.dumps(wf, indent=2))

        elif args.command == "clone":
            clone_workflow(args.workflow_id, args.suffix)

        elif args.command == "execute":
            data = None
            if args.input:
                data = json.loads(args.input)
            result = execute_workflow(args.workflow_id, data)
            # Auto sanity check
            print("\n🔍 Running sanity checks...")
            problems = sanity_checks(result)
            if problems:
                print("⚠️ Issues found:")
                for p in problems:
                    print(f"  • {p}")
            else:
                print("✅ All checks passed")

        elif args.command == "check":
            exec_data = api_get(f"/api/v1/executions/{args.execution_id}")
            problems = sanity_checks(exec_data)
            if problems:
                print("⚠️ Issues:")
                for p in problems:
                    print(f"  • {p}")
            else:
                print("✅ All checks passed")

        elif args.command == "promote":
            if not args.confirm:
                orig = get_workflow(args.original_id)
                print(f"⚠️ This will replace '{orig['name']}' with the test version")
                print("   Pass --confirm to proceed")
                return
            promote_test_workflow(args.test_id, args.original_id)

        elif args.command == "delete":
            if not args.confirm:
                print("❌ Pass --confirm to delete. This cannot be undone.")
                return
            api_delete(f"/api/v1/workflows/{args.workflow_id}")
            print(f"🗑️ Workflow {args.workflow_id} deleted")

        elif args.command == "create":
            create_workflow(args.file)

        elif args.command == "activate":
            activate_workflow(args.workflow_id)

        elif args.command == "deactivate":
            deactivate_workflow(args.workflow_id)

        elif args.command == "history":
            execs = get_execution_history(args.workflow_id, args.limit)
            print(f"\n📜 {len(execs)} execution(s):\n")
            for ex in execs:
                status_icon = "✅" if ex.get("status") == "success" else "❌"
                finished = ex.get("stoppedAt", "?")
                print(f"  {status_icon} {ex['id']} | status={ex.get('status')} | stopped={finished}")

    except requests.exceptions.HTTPError as e:
        print(f"❌ API Error: {e.response.status_code}")
        try:
            print(f"   {e.response.json()}")
        except:
            print(f"   {e.response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
