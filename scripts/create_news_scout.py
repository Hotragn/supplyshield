"""
create_news_scout.py - Creates the SupplyShield News Scout sub-agent.

This is the second agent in the multi-agent architecture. The News Scout
specializes in external intelligence: corroborating disruptions with news,
detecting early warning signals, and providing sentiment analysis.

The Orchestrator (SupplyShield) delegates news intelligence to the Scout
via the MCP protocol. In Kibana, wire the Scout as an MCP server tool
on the Orchestrator agent (requires a Kibana stack connector).

Requires: KIBANA_URL and ES_API_KEY environment variables.
"""
import os, sys, requests, json

KIBANA_URL = os.environ.get("KIBANA_URL", "").rstrip("/")
ES_API_KEY = os.environ.get("ES_API_KEY")
if not KIBANA_URL or not ES_API_KEY:
    print("ERROR: KIBANA_URL and ES_API_KEY must be set.")
    sys.exit(1)

HEADERS = {"Content-Type": "application/json", "Authorization": f"ApiKey {ES_API_KEY}", "kbn-xsrf": "true"}
BASE = f"{KIBANA_URL}/api/agent_builder"

# ── News Scout Agent ──────────────────────────────────────────────────────────

NEWS_SCOUT_SYSTEM = (
    "You are the SupplyShield News Scout, a specialized intelligence sub-agent.\n\n"
    "Your sole responsibility is external signals: news, reports, and events that "
    "indicate or predict supply chain disruptions. You are called by the SupplyShield "
    "Orchestrator when it needs corroboration or early-warning intelligence.\n\n"
    "When invoked:\n"
    "1. Use search_disruption_news to find relevant articles about the given region, port, "
    "or supplier.\n"
    "2. Return: article count, average severity, average sentiment_score, key themes, "
    "and whether the external signal corroborates or contradicts the disruption report.\n"
    "3. Classify the signal: CONFIRMED (strong external evidence), UNCERTAIN (mixed signals), "
    "or UNCONFIRMED (no relevant articles found).\n\n"
    "Rules:\n"
    "- Return structured summaries, not conversational text — you are talking to another agent.\n"
    "- Always include sentiment scores and severity levels from the data.\n"
    "- If no articles found, say UNCONFIRMED and suggest the Orchestrator proceed with "
    "caution based on shipment data alone.\n"
    "- Never recommend recovery actions — that is the Orchestrator's role."
)

# Create News Scout agent
requests.delete(f"{BASE}/agents/supplyshield_news_scout", headers=HEADERS, timeout=10)
r = requests.post(f"{BASE}/agents", headers=HEADERS, json={
    "id": "supplyshield_news_scout",
    "name": "SupplyShield News Scout",
    "description": (
        "Specialist sub-agent for external disruption intelligence. "
        "Searches and analyzes news articles about supply chain events. "
        "Called by the SupplyShield Orchestrator via MCP for corroboration."
    ),
    "configuration": {
        "tools": [{"tool_ids": ["search_disruption_news"]}]
    }
}, timeout=30)

if r.status_code in (200, 201):
    print("OK: SupplyShield News Scout created")
    agent_data = r.json()
    print(f"  ID: {agent_data.get('id')}")
    print(f"  Type: {agent_data.get('type')}")
    print(f"  Tools: {agent_data.get('configuration', {}).get('tools')}")
else:
    print(f"ERROR {r.status_code}: {r.text[:400]}")
    sys.exit(1)

# List all agents
print("\n=== All SupplyShield Agents ===")
r2 = requests.get(f"{BASE}/agents", headers=HEADERS)
agents = r2.json().get("results", [])
for a in agents:
    if not a.get("readonly", False) or "supplyshield" in a.get("id", ""):
        print(f"  [{a.get('id')}] {a.get('name')} - {a.get('description', '')[:60]}")

print("\n=== Multi-Agent Architecture ===")
print("  SupplyShield Orchestrator (supplyshield)")
print("    ├── detect_shipment_anomalies (ES|QL)")
print("    ├── assess_revenue_impact (ES|QL)")
print("    ├── find_alternative_suppliers (ES|QL)")
print("    └── ── via MCP ──> SupplyShield News Scout (supplyshield_news_scout)")
print("                           └── search_disruption_news (index_search)")
print()
print("To wire MCP in Kibana:")
print(f"  1. Go to: {KIBANA_URL}/app/agent-builder/agents/supplyshield")
print("  2. Add tool > MCP > configure News Scout endpoint")
