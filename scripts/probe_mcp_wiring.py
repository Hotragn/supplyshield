"""
probe_mcp_wiring.py - Probe Kibana connectors API for MCP wiring between agents.

Goal: Understand what connector types are available, whether the News Scout
chat endpoint is accessible, and how to wire MCP on the Orchestrator.
"""
import os, requests, json

KIBANA_URL = os.environ.get("KIBANA_URL", "").rstrip("/")
ES_API_KEY = os.environ.get("ES_API_KEY")
HEADERS = {"Content-Type": "application/json", "Authorization": f"ApiKey {ES_API_KEY}", "kbn-xsrf": "true"}

# 1. List available connector types
print("=== Available Kibana Connector Types ===")
r = requests.get(f"{KIBANA_URL}/api/actions/connector_types", headers=HEADERS, timeout=15)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    types = r.json()
    for ct in types:
        print(f"  {ct.get('id'):40s} {ct.get('name')}")
else:
    print(r.text[:500])

# 2. List existing connectors
print("\n=== Existing Connectors ===")
r2 = requests.get(f"{KIBANA_URL}/api/actions/connectors", headers=HEADERS, timeout=15)
print(f"Status: {r2.status_code}")
if r2.status_code == 200:
    conns = r2.json()
    for c in conns:
        print(f"  {c.get('id','')[:30]:32s} {c.get('connector_type_id'):30s} {c.get('name')}")
else:
    print(r2.text[:500])

# 3. Try to hit the News Scout chat endpoint directly
print("\n=== Testing News Scout chat endpoint ===")
for path in [
    "/api/agent_builder/agents/supplyshield_news_scout/chat",
    "/internal/agent_builder/agents/supplyshield_news_scout/chat",
    "/api/agent_builder/agents/supplyshield_news_scout/invoke",
]:
    r3 = requests.post(f"{KIBANA_URL}{path}", headers=HEADERS,
                       json={"input": "test"}, timeout=10)
    print(f"  {path}: {r3.status_code} {r3.text[:150]}")
