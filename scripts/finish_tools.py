"""
finish_tools.py - Creates remaining tools and agent.
Run after create_tools.py (which created find_alternative_suppliers and detect_shipment_anomalies).
"""
import os, sys, requests, json

KIBANA_URL = os.environ.get("KIBANA_URL", "").rstrip("/")
ES_API_KEY = os.environ.get("ES_API_KEY")
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"ApiKey {ES_API_KEY}",
    "kbn-xsrf": "true"
}
BASE = f"{KIBANA_URL}/api/agent_builder"

def upsert(endpoint, payload, label):
    tid = payload.get("id", "")
    requests.delete(f"{endpoint}/{tid}", headers=HEADERS, timeout=10)
    r = requests.post(endpoint, headers=HEADERS, json=payload, timeout=30)
    if r.status_code in (200, 201):
        print(f"  OK: {label}")
        return True
    else:
        print(f"  ERROR {r.status_code}: {label}: {r.text[:400]}")
        return False

# Assess revenue impact
assess_query = (
    'FROM sc_orders\n'
    '| WHERE status == "active"\n'
    '| LOOKUP JOIN sc_products ON product_id\n'
    '| WHERE primary_supplier_id == ?affected_supplier_id\n'
    '| LOOKUP JOIN sc_suppliers ON primary_supplier_id\n'
    '| STATS total_revenue_at_risk = SUM(revenue_value), affected_orders = COUNT(*), '
    'affected_customers = COUNT_DISTINCT(customer_id), earliest_due = MIN(required_date), '
    'avg_order_value = AVG(revenue_value) BY product_id, product_name, supplier_name\n'
    '| SORT total_revenue_at_risk DESC'
)
ok1 = upsert(f"{BASE}/tools", {
    "id": "assess_revenue_impact",
    "type": "esql",
    "description": (
        "Calculates financial blast radius of a supplier disruption. "
        "Joins active orders to products and suppliers to find total revenue at risk, "
        "order count, customer count, and earliest due dates. "
        "REQUIRES affected_supplier_id (get from detect_shipment_anomalies). "
        "Do NOT use without a supplier ID. Do NOT use to find alternatives."
    ),
    "configuration": {
        "query": assess_query,
        "params": {
            "affected_supplier_id": {
                "type": "string",
                "description": "The supplier_id of the disrupted supplier from detect_shipment_anomalies results."
            }
        }
    }
}, "assess_revenue_impact")

# Search disruption news
ok2 = upsert(f"{BASE}/tools", {
    "id": "search_disruption_news",
    "type": "index_search",
    "description": (
        "Searches news articles about supply chain disruptions using natural language. "
        "Use to verify whether a detected shipment anomaly matches a known external event, "
        "or to get early warning signals before they show in shipment data. "
        "Do NOT use for supplier data, shipment counts, or financial figures."
    ),
    "configuration": {"pattern": "sc_news"}
}, "search_disruption_news")

# Create agent
SYSTEM_INSTRUCTIONS = """You are SupplyShield, a supply chain disruption detection and recovery agent.

Help supply chain professionals detect disruptions, understand financial impact, find recovery options, and take action.

## Sequence

1. LISTEN: Identify region, port, supplier, or timeframe from the user's message.
2. DETECT: Use detect_shipment_anomalies to find affected shipments. Use search_disruption_news to corroborate.
3. ASSESS: Use assess_revenue_impact with the specific supplier_id from step 2. Give actual dollar figures.
4. FIND ALTERNATIVES: Use find_alternative_suppliers. Show top 3 with suitability score, lead time, cost premium.
5. ACT: Only trigger recovery workflow after explicit user confirmation. Always describe what you will do first.

## Rules

- Ground all answers in tool data. No speculation.
- Be specific: "$2.3M across 23 orders" not "significant impact."
- Never execute a workflow without explicit user confirmation.
- If a tool returns no results, say so and explain why (wrong time window, wrong ID format, etc.).
- Ask clarifying questions when you need more info to pick tool parameters.
- Your audience is supply chain professionals. Get to the data fast.
"""

ok3 = upsert(f"{BASE}/agents", {
    "id": "supplyshield",
    "name": "SupplyShield",
    "description": "Supply chain disruption detection and automated recovery assistant",
    "system_prompt": SYSTEM_INSTRUCTIONS,
    "tools": [
        "detect_shipment_anomalies",
        "assess_revenue_impact",
        "find_alternative_suppliers",
        "search_disruption_news"
    ]
}, "SupplyShield agent")

# List all user tools
print("\nUser-created tools:")
r = requests.get(f"{BASE}/tools", headers=HEADERS)
tools = json.loads(r.text).get("results", [])
for t in tools:
    if not t.get("readonly"):
        print(f"  - {t['id']} ({t['type']})")

print("\nAgents:")
r2 = requests.get(f"{BASE}/agents", headers=HEADERS)
if r2.status_code == 200:
    agents = r2.json().get("results", [])
    for a in agents:
        print(f"  - {a.get('id')} / {a.get('name')}")

if all([ok1, ok2, ok3]):
    print(f"\nAll done! Open: {KIBANA_URL}/app/agent-builder")
else:
    print("\nSome items failed - check above.")
    sys.exit(1)
