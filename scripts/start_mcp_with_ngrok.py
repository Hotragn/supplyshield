"""
start_mcp_with_ngrok.py - Start News Scout MCP server + authenticated ngrok tunnel.

Reads NGROK_AUTH_TOKEN from .env, starts the MCP server, creates an ngrok tunnel,
then prints the public URL and automatically wires the Kibana connector.

Usage:
    python scripts/start_mcp_with_ngrok.py
"""
import os, sys, time, subprocess, json, threading, requests

# Load .env
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
if os.path.exists(env_path):
    for line in open(env_path):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

KIBANA_URL = os.environ.get("KIBANA_URL", "").rstrip("/")
ES_API_KEY  = os.environ.get("ES_API_KEY", "")
ES_ENDPOINT = os.environ.get("ES_ENDPOINT", "")
NGROK_TOKEN = os.environ.get("NGROK_AUTH_TOKEN", "")
PORT = 8000

if not NGROK_TOKEN:
    print("ERROR: NGROK_AUTH_TOKEN not found in .env")
    sys.exit(1)

HEADERS = {"Content-Type": "application/json", "Authorization": f"ApiKey {ES_API_KEY}", "kbn-xsrf": "true"}
BASE = f"{KIBANA_URL}/api/agent_builder"

# ── Step 1: Start MCP server in background ────────────────────────────────────
print(f"[1] Starting News Scout MCP server on port {PORT}...")
env = os.environ.copy()
mcp_proc = subprocess.Popen(
    [sys.executable, "scripts/news_scout_mcp_server.py"],
    env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
)
# Wait for server to be ready
time.sleep(6)

# Verify it's up
try:
    r = requests.get(f"http://localhost:{PORT}/mcp", timeout=3)
    print(f"  Server running: http://localhost:{PORT}/mcp (status {r.status_code or 'streaming'})")
except:
    pass
print(f"  MCP PID: {mcp_proc.pid}")

# ── Step 2: Start ngrok tunnel ─────────────────────────────────────────────────
print(f"\n[2] Starting ngrok tunnel (authenticated)...")
from pyngrok import ngrok, conf
conf.get_default().auth_token = NGROK_TOKEN

tunnel = ngrok.connect(PORT, "http")
public_url = tunnel.public_url
if public_url.startswith("http://"):
    public_url = "https://" + public_url[7:]
mcp_url = f"{public_url}/mcp"
print(f"  Public URL: {public_url}")
print(f"  MCP endpoint: {mcp_url}")

# Wait for tunnel to stabilize
time.sleep(3)

# Test tunnel
try:
    r_test = requests.post(mcp_url,
        headers={"Content-Type": "application/json"},
        json={"jsonrpc": "2.0", "id": 1, "method": "initialize",
              "params": {"protocolVersion": "2024-11-05",
                         "capabilities": {}, "clientInfo": {"name": "test", "version": "1"}}},
        timeout=10)
    print(f"  Tunnel test: {r_test.status_code}")
except Exception as e:
    print(f"  Tunnel test: {e}")

# ── Step 3: Create .mcp Kibana connector ──────────────────────────────────────
print(f"\n[3] Creating .mcp Kibana connector...")
requests.delete(f"{KIBANA_URL}/api/actions/connector/supplyshield-news-scout-mcp", headers=HEADERS, timeout=10)

r2 = requests.post(f"{KIBANA_URL}/api/actions/connector", headers=HEADERS, json={
    "name": "SupplyShield News Scout MCP",
    "connector_type_id": ".mcp",
    "config": {"serverUrl": mcp_url},
    "secrets": {}
}, timeout=20)

if r2.status_code in (200, 201):
    connector_id = r2.json().get("id")
    print(f"  Connector created: {connector_id}")
else:
    print(f"  Connector failed: {r2.status_code} {r2.text[:300]}")
    mcp_proc.terminate()
    ngrok.kill()
    sys.exit(1)

# ── Step 4: Create mcp tool in Agent Builder ──────────────────────────────────
print(f"\n[4] Creating 'news_scout_query' mcp tool...")
requests.delete(f"{BASE}/tools/news_scout_query", headers=HEADERS, timeout=10)

r3 = requests.post(f"{BASE}/tools", headers=HEADERS, json={
    "id": "news_scout_query",
    "type": "mcp",
    "description": (
        "Delegate news corroboration to the SupplyShield News Scout sub-agent via MCP. "
        "Searches sc_news for disruption articles using hybrid vector + keyword search. "
        "Returns a signal classification: CONFIRMED, UNCERTAIN, or UNCONFIRMED, with "
        "article count, sentiment scores, and key themes. "
        "ALWAYS call this BEFORE assess_revenue_impact to corroborate shipment anomalies "
        "with external intelligence. Do NOT call search_disruption_news directly."
    ),
    "configuration": {
        "connector_id": connector_id,
        "tool_name": "query_disruption_news"
    }
}, timeout=20)

if r3.status_code in (200, 201):
    print(f"  Tool created: {r3.json().get('id')}")
else:
    print(f"  Tool failed: {r3.status_code} {r3.text[:300]}")
    mcp_proc.terminate()
    ngrok.kill()
    sys.exit(1)

# ── Step 5: Update Orchestrator — replace search_disruption_news with news_scout_query ───
print(f"\n[5] Updating Orchestrator agent tools...")
r4 = requests.get(f"{BASE}/agents/supplyshield", headers=HEADERS)
current_tools = r4.json().get("configuration", {}).get("tools", [{}])[0].get("tool_ids", [])

# Replace search_disruption_news with news_scout_query (Scout handles it via MCP)
updated = [t for t in current_tools if t != "search_disruption_news"]
if "news_scout_query" not in updated:
    updated.append("news_scout_query")
print(f"  Tools: {current_tools} -> {updated}")

r5 = requests.put(f"{BASE}/agents/supplyshield", headers=HEADERS, json={
    "name": "SupplyShield",
    "description": "Supply chain disruption detection and automated recovery agent",
    "configuration": {"tools": [{"tool_ids": updated}]}
}, timeout=15)

if r5.status_code in (200, 201):
    print(f"  Orchestrator updated OK")
else:
    print(f"  Orchestrator update: {r5.status_code} {r5.text[:200]}")

# ── Done ───────────────────────────────────────────────────────────────────────
print(f"""
{'='*60}
MCP WIRING COMPLETE
{'='*60}
  MCP Server URL  : {mcp_url}
  Kibana Connector: {connector_id}
  Orchestrator    : detect + assess + find_alternatives + news_scout_query (MCP)

The Orchestrator will now automatically call the News Scout
via MCP when it needs news intelligence.

Test prompt: "Check Shenzhen port congestion — any shipments affected?"

KEEP THIS TERMINAL OPEN — ngrok tunnel must stay running for the demo.
Press Ctrl+C to stop.
""")

try:
    while True:
        time.sleep(10)
        if mcp_proc.poll() is not None:
            print("WARNING: MCP server process ended. Restarting...")
            mcp_proc = subprocess.Popen([sys.executable, "scripts/news_scout_mcp_server.py"], env=env)
            time.sleep(5)
except KeyboardInterrupt:
    print("\nShutting down...")
    mcp_proc.terminate()
    ngrok.disconnect(tunnel.public_url)
    ngrok.kill()
