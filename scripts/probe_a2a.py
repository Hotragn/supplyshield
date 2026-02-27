"""
probe_a2a.py - Probe Kibana Agent Builder A2A / multi-agent tool support.
"""
import os, requests, json

KIBANA_URL = os.environ.get("KIBANA_URL", "").rstrip("/")
ES_API_KEY = os.environ.get("ES_API_KEY")
HEADERS = {"Content-Type": "application/json", "Authorization": f"ApiKey {ES_API_KEY}", "kbn-xsrf": "true"}
BASE = f"{KIBANA_URL}/api/agent_builder"

# 1. List existing agents
r = requests.get(f"{BASE}/agents", headers=HEADERS)
agents = r.json().get("results", [])
print("=== Existing agents ===")
for a in agents:
    print(f"  {a.get('id')} / {a.get('name')} (type={a.get('type')})")

# 2. Probe various A2A-style tool types
print("\n=== Probing tool types ===")
for tool_type, conf in [
    ("agent", {"agent_id": "supplyshield"}),
    ("a2a", {"agent_id": "supplyshield"}),
    ("mcp", {"server_url": "http://localhost:3000"}),
    ("http", {"url": "http://localhost:3000"}),
]:
    requests.delete(f"{BASE}/tools/probe_type", headers=HEADERS, timeout=5)
    r2 = requests.post(f"{BASE}/tools", headers=HEADERS, json={
        "id": "probe_type",
        "type": tool_type,
        "description": "probe",
        "configuration": conf
    }, timeout=10)
    print(f"  type={tool_type}: {r2.status_code} {r2.text[:200]}")
    requests.delete(f"{BASE}/tools/probe_type", headers=HEADERS, timeout=5)

# 3. Check if agents have an A2A endpoint
print("\n=== Checking A2A endpoint ===")
r3 = requests.get(f"{BASE}/agents/supplyshield", headers=HEADERS)
print(json.dumps(r3.json(), indent=2)[:1000])
