"""
probe_mcp_connector.py - Probe .mcp connector schema and try to create one.
"""
import os, requests, json

KIBANA_URL = os.environ.get("KIBANA_URL", "").rstrip("/")
ES_API_KEY = os.environ.get("ES_API_KEY")
HEADERS = {"Content-Type": "application/json", "Authorization": f"ApiKey {ES_API_KEY}", "kbn-xsrf": "true"}

# 1. Get .mcp connector type schema
print("=== .mcp connector type info ===")
r = requests.get(f"{KIBANA_URL}/api/actions/connector_types", headers=HEADERS, timeout=15)
for ct in r.json():
    if ct.get("id") == ".mcp":
        print(json.dumps(ct, indent=2))

# 2. Try creating a .mcp connector with minimal config
print("\n=== Creating .mcp connector (probe) ===")
for config in [
    {"url": "http://localhost:3000"},
    {"server_url": "http://localhost:3000"},
    {"mcp_server_url": "http://localhost:3000"},
    {"url": "http://localhost:3000", "api_key": "test"},
]:
    r2 = requests.post(f"{KIBANA_URL}/api/actions/connector", headers=HEADERS, json={
        "name": "probe_mcp",
        "connector_type_id": ".mcp",
        "config": config,
        "secrets": {}
    }, timeout=10)
    if r2.status_code in (200, 201):
        data = r2.json()
        print(f"  SUCCESS with config keys {list(config.keys())}: id={data.get('id')}")
        # clean up
        requests.delete(f"{KIBANA_URL}/api/actions/connector/{data.get('id')}", headers=HEADERS)
        break
    else:
        err = r2.json().get("message", r2.text[:200])
        print(f"  config {list(config.keys())}: {r2.status_code} {err[:200]}")

# 3. Also check what agent builder MCP tool expects
print("\n=== Probing MCP tool on Orchestrator ===")
r3 = requests.post(f"{KIBANA_URL}/api/agent_builder/tools", headers=HEADERS, json={
    "id": "probe_mcp_tool",
    "type": "mcp",
    "description": "probe",
    "configuration": {"connector_id": "fake-id-123"}
})
print(f"mcp tool with connector_id: {r3.status_code} {r3.text[:400]}")
requests.delete(f"{KIBANA_URL}/api/agent_builder/tools/probe_mcp_tool", headers=HEADERS)
