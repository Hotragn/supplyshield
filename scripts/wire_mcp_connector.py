"""
wire_mcp_connector.py - Create .mcp Kibana connector + mcp tool + update Orchestrator.

Run after news_scout_mcp_server.py is running and tunnel is live.

Usage:
    python scripts/wire_mcp_connector.py --tunnel-url https://709a6d92152389.lhr.life

Requires: KIBANA_URL and ES_API_KEY environment variables.
"""
import os, sys, requests, json, argparse

KIBANA_URL = os.environ.get("KIBANA_URL", "").rstrip("/")
ES_API_KEY = os.environ.get("ES_API_KEY")
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"ApiKey {ES_API_KEY}",
    "kbn-xsrf": "true"
}
BASE = f"{KIBANA_URL}/api/agent_builder"

parser = argparse.ArgumentParser()
parser.add_argument("--tunnel-url", required=True, help="Public tunnel URL, e.g. https://abc.lhr.life")
args = parser.parse_args()

TUNNEL_URL = args.tunnel_url.rstrip("/")
SSE_URL = f"{TUNNEL_URL}/sse"

print(f"Wiring MCP connector to: {SSE_URL}")

# ── Step 1: Test SSE endpoint is reachable ─────────────────────────────────────
print("\n[1] Testing SSE endpoint reachability...")
try:
    r = requests.get(SSE_URL, timeout=8, stream=True)
    print(f"  SSE endpoint: {r.status_code} (200 or stream OK means server is up)")
    r.close()
except Exception as e:
    print(f"  WARNING: Could not reach {SSE_URL}: {e}")
    print("  Proceeding anyway - Kibana will test at connection time.")

# ── Step 2: Create .mcp Kibana connector ──────────────────────────────────────
print("\n[2] Creating .mcp Kibana connector...")
# Clean up any old one
requests.delete(f"{KIBANA_URL}/api/actions/connector/supplyshield-news-scout-mcp",
                headers=HEADERS, timeout=10)

# Try serverUrl camelCase
for cfg_key in ["serverUrl", "server_url", "url"]:
    r2 = requests.post(f"{KIBANA_URL}/api/actions/connector", headers=HEADERS, json={
        "name": "SupplyShield News Scout MCP",
        "connector_type_id": ".mcp",
        "config": {cfg_key: SSE_URL},
        "secrets": {}
    }, timeout=15)
    if r2.status_code in (200, 201):
        connector = r2.json()
        connector_id = connector.get("id")
        print(f"  Connector created: id={connector_id} (key={cfg_key})")
        break
    else:
        msg = r2.json().get("message", r2.text[:300])
        print(f"  {cfg_key}: {r2.status_code} {msg[:200]}")
        connector_id = None

if not connector_id:
    print("\nERROR: Could not create .mcp connector. Aborting.")
    sys.exit(1)

# ── Step 3: Create mcp tool on Agent Builder ──────────────────────────────────
print("\n[3] Creating mcp tool 'news_scout_query'...")
requests.delete(f"{BASE}/tools/news_scout_query", headers=HEADERS, timeout=10)

# Probe the correct mcp tool config schema
for conf in [
    {"connector_id": connector_id, "tool_name": "query_disruption_news"},
    {"connector_id": connector_id, "tool_name": "query_disruption_news", "server_url": SSE_URL},
    {"connector_id": connector_id, "toolName": "query_disruption_news"},
]:
    r3 = requests.post(f"{BASE}/tools", headers=HEADERS, json={
        "id": "news_scout_query",
        "type": "mcp",
        "description": (
            "Delegate news intelligence to the SupplyShield News Scout sub-agent. "
            "Searches sc_news for disruption articles and returns a signal classification: "
            "CONFIRMED, UNCERTAIN, or UNCONFIRMED with sentiment scores and article summaries. "
            "Use this to corroborate shipment anomalies with external intelligence BEFORE "
            "assessing revenue impact."
        ),
        "configuration": conf
    }, timeout=15)
    if r3.status_code in (200, 201):
        tool_data = r3.json()
        print(f"  Tool created: {tool_data.get('id')} (conf keys={list(conf.keys())})")
        break
    else:
        msg = r3.json().get("message", r3.text[:300])
        print(f"  conf {list(conf.keys())}: {r3.status_code} {msg[:250]}")
        r3_status = r3.status_code

# ── Step 4: Update Orchestrator to include news_scout_query tool ───────────────
print("\n[4] Updating SupplyShield Orchestrator agent...")
r4 = requests.get(f"{BASE}/agents/supplyshield", headers=HEADERS)
current = r4.json()
current_tools = current.get("configuration", {}).get("tools", [{}])[0].get("tool_ids", [])
print(f"  Current tools: {current_tools}")

# Add news_scout_query if not already there
updated_tools = list(dict.fromkeys(current_tools + ["news_scout_query"]))
print(f"  Updated tools: {updated_tools}")

r5 = requests.put(f"{BASE}/agents/supplyshield", headers=HEADERS, json={
    "name": "SupplyShield",
    "description": "Supply chain disruption detection and automated recovery agent",
    "configuration": {
        "tools": [{"tool_ids": updated_tools}]
    }
}, timeout=15)

if r5.status_code in (200, 201):
    print(f"  Orchestrator updated OK: {r5.json().get('id')}")
else:
    print(f"  Orchestrator update: {r5.status_code} {r5.text[:300]}")

# ── Summary ────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("MCP WIRING STATUS")
print("="*60)
print(f"  MCP Server URL    : {SSE_URL}")
print(f"  Kibana Connector  : {connector_id}")
print(f"  Tool              : news_scout_query")
print(f"  Orchestrator tools: {updated_tools}")
print("\nOrchestrator will now call News Scout via MCP for news intelligence.")
print("Test it: ask the Orchestrator about Shenzhen congestion news.")
