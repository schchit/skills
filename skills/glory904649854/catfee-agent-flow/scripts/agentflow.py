#!/usr/bin/env python3
"""
AgentFlow MCP 工具调用脚本
用法: python agentflow.py <tool_name> [args...]

环境变量：
  AGENTFLOW_MCP_URL - AgentFlow MCP 服务器地址（默认: http://182.42.153.28:18900）
"""
import os
import requests
import json
import sys
import threading
import time

MCP_URL = os.environ.get("AGENTFLOW_MCP_URL", "http://182.42.153.28:18900")

session_id = None
session_lock = threading.Lock()
sse_ready = threading.Event()

def sse_listener():
    global session_id
    try:
        with requests.get(f"{MCP_URL}/api/mcp/sse", stream=True, timeout=30) as resp:
            for line in resp.iter_lines():
                if line:
                    decoded = line.decode('utf-8', errors='ignore')
                    if decoded.startswith('data:'):
                        data = decoded[5:].strip()
                        if 'sessionId=' in data:
                            sid = data.split('sessionId=')[1].split('&')[0]
                            with session_lock:
                                session_id = sid
                            sse_ready.set()
    except Exception as e:
        print(f"SSE Error: {e}")
        sse_ready.set()

def call_tool(tool_name, params=None):
    global session_id
    if params is None:
        params = {}

    # Start SSE listener
    t = threading.Thread(target=sse_listener, daemon=True)
    t.start()

    # Wait for sessionId
    sse_ready.wait(timeout=10)

    with session_lock:
        sid = session_id

    if not sid:
        return {"error": "Failed to get sessionId"}

    # POST request
    msg_url = f"{MCP_URL}/api/mcp/message?sessionId={sid}"
    body = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": params
        }
    })

    headers = {"Content-Type": "application/json"}

    try:
        resp = requests.post(msg_url, data=body, headers=headers, timeout=15)
        data = resp.json()
        if "result" in data:
            return data["result"]
        return data
    except Exception as e:
        return {"error": str(e)}

def main():
    if len(sys.argv) < 2:
        print("用法: python agentflow.py <tool_name> [args...]")
        print("\n可用工具:")
        print("  list_projects")
        print("  create_project <name> [description] [tags]")
        print("  get_project <projectId>")
        print("  list_requirements <projectId>")
        print("  create_requirement <projectId> <title> [description] [priority]")
        print("  list_tasks <requirementId>")
        print("  create_task <requirementId> <title> [priority] [assignee]")
        print("  transition <taskId> <fromStatus> <toStatus> [operator] [note]")
        print("  get_timeline <taskId>")
        print("  search <query>")
        print("  log_context <entityType> <entityId> <content>")
        print("  get_context <entityType> <entityId>")
        print("  list_files <entityType> <entityId> [includeChildren]")
        sys.exit(1)

    tool = sys.argv[1]
    args = sys.argv[2:]

    params = {}

    if tool == "list_projects":
        pass

    elif tool == "create_project":
        if not args:
            print("Error: name is required")
            sys.exit(1)
        params["name"] = args[0]
        if len(args) > 1:
            params["description"] = args[1]
        if len(args) > 2:
            params["tags"] = args[2]

    elif tool == "get_project":
        if not args:
            print("Error: projectId is required")
            sys.exit(1)
        params["projectId"] = args[0]

    elif tool == "list_requirements":
        if not args:
            print("Error: projectId is required")
            sys.exit(1)
        params["projectId"] = args[0]

    elif tool == "create_requirement":
        if len(args) < 2:
            print("Error: projectId and title are required")
            sys.exit(1)
        params["projectId"] = args[0]
        params["title"] = args[1]
        if len(args) > 2:
            params["description"] = args[2]
        if len(args) > 3:
            params["priority"] = args[3]

    elif tool == "list_tasks":
        if not args:
            print("Error: requirementId is required")
            sys.exit(1)
        params["requirementId"] = args[0]

    elif tool == "create_task":
        if len(args) < 2:
            print("Error: requirementId and title are required")
            sys.exit(1)
        params["requirementId"] = args[0]
        params["title"] = args[1]
        if len(args) > 2:
            params["priority"] = args[2]
        if len(args) > 3:
            params["assignee"] = args[3]

    elif tool == "transition":
        if len(args) < 3:
            print("Error: taskId, fromStatus, and toStatus are required")
            sys.exit(1)
        params["taskId"] = args[0]
        params["fromStatus"] = args[1]
        params["toStatus"] = args[2]
        if len(args) > 3:
            params["operator"] = args[3]
        if len(args) > 4:
            params["note"] = args[4]

    elif tool == "get_timeline":
        if not args:
            print("Error: taskId is required")
            sys.exit(1)
        params["taskId"] = args[0]

    elif tool == "search":
        if not args:
            print("Error: query is required")
            sys.exit(1)
        params["query"] = args[0]

    elif tool == "log_context":
        if len(args) < 3:
            print("Error: entityType, entityId, and content are required")
            sys.exit(1)
        params["entityType"] = args[0]
        params["entityId"] = args[1]
        params["content"] = args[2]

    elif tool == "get_context":
        if len(args) < 2:
            print("Error: entityType and entityId are required")
            sys.exit(1)
        params["entityType"] = args[0]
        params["entityId"] = args[1]

    elif tool == "list_files":
        if len(args) < 2:
            print("Error: entityType and entityId are required")
            sys.exit(1)
        params["entityType"] = args[0]
        params["entityId"] = args[1]
        if len(args) > 2:
            params["includeChildren"] = args[2].lower() == "true"

    else:
        print(f"Unknown tool: {tool}")
        sys.exit(1)

    result = call_tool(tool, params)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
