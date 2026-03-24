import requests, json

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkMThhNzQyNS00NDM4LTRhMmYtOTQ2YS1jZmE2MDJlMTY1ZTQiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiNzhmMzJmZTUtYjI1NS00MDE3LTg2NTAtYjVjYjY3NWZkOWVmIiwiaWF0IjoxNzc0MDA0MDEzLCJleHAiOjE3NzY1NDk2MDB9.Tw1RBqRbCQn3LKQQyx32pkct3VYDh09k2PpApmfWtf8"
H = {"X-N8N-API-KEY": TOKEN}
URL = "https://n8n.nelflow.cloud/api/v1/workflows"

critical = {
    "2U5DkXM35mOjSmrY": "Tool_Order_Create",
    "7MnQIfTj22NQJszi": "Tool_Cancel_Order",
    "D13RULaXV29stSPU": "Tool_Stock_Update",
    "kDswppLiCb2h1hoS": "Tool_Payment_Register",
    "CoxMeBxrfgVrY9re": "Tool_Payment_Callback_Handler",
    "kG07yHj5X5ux1vdq": "Tool_Logistics_Orchestrator",
    "6vJo21JT3GeeNOYc": "Tool_Stock_Order",
}

for wid, name in critical.items():
    wf = requests.get(f"{URL}/{wid}", headers=H).json()

    # Add onError to critical nodes
    modified = False
    for node in wf.get("nodes", []):
        if node["type"] in ["n8n-nodes-base.googleSheets", "n8n-nodes-base.code", "n8n-nodes-base.executeWorkflow"]:
            if "onError" not in node:
                node["onError"] = "continueErrorOutput"
                modified = True

    if not modified:
        print(f"⏭️ {name}: déjà OK")
        continue

    settings = wf.get("settings", {})
    # Remove unknown settings keys
    clean_settings = {"executionOrder": "v1"}
    body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"], "settings": clean_settings}
    result = requests.put(f"{URL}/{wid}", headers=H, json=body)

    if result.status_code == 200:
        print(f"✅ {name}: error handling ajouté")
    else:
        print(f"❌ {name}: {result.status_code} - {result.text[:200]}")
