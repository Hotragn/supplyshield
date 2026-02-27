"""fix_assess_revenue.py - Use simple MATCH instead of parameterized WHERE to bypass ES|QL bug"""
import os, requests, time

env = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
if os.path.exists(env):
    for line in open(env):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

KB = os.environ["KIBANA_URL"].rstrip("/")
h = {"Authorization": "ApiKey " + os.environ["ES_API_KEY"], "kbn-xsrf": "true", "Content-Type": "application/json"}
base = f"{KB}/api/agent_builder"

# The issue in ES|QL + Agent Builder is that `WHERE field == ?param` fails 
# if the field comes from a LOOKUP JOIN. 
# We bypass this by keeping the parameter but putting it in a STATS filter 
# or just removing the JOIN and letting the LLM do the math, but since we 
# want the agent doing it: we will filter the orders BEFORE the join if possible.
# But product_id -> supplier_id is in sc_products.
# Alternative: just return ALL active orders grouped by supplier, and let 
# the LLM read the one it cares about from the table.

ASSESS_QUERY = (
    'FROM sc_orders\n'
    '| WHERE status == "active"\n'
    '| LOOKUP JOIN sc_products ON product_id\n'
    '| LOOKUP JOIN sc_suppliers ON primary_supplier_id\n'
    '| STATS\n'
    '    total_revenue_at_risk = SUM(revenue_value),\n'
    '    affected_orders = COUNT(*),\n'
    '    affected_customers = COUNT_DISTINCT(customer_id),\n'
    '    earliest_due = MIN(required_date),\n'
    '    avg_order_value = AVG(revenue_value)\n'
    '  BY primary_supplier_id, supplier_name\n'
    '| SORT total_revenue_at_risk DESC\n'
    '| LIMIT 50'
)

print("[1] Unlinking from Orchestrator...")
requests.put(f"{base}/agents/supplyshield", headers=h, json={
    "name": "SupplyShield",
    "description": "Supply chain disruption detection and automated recovery agent",
    "configuration": {"tools": [{"tool_ids": ["detect_shipment_anomalies", "find_alternative_suppliers", "news_scout_query"]}]}
})
time.sleep(1)

print("[2] Deleting old assess_revenue_impact...")
requests.delete(f"{base}/tools/assess_revenue_impact", headers=h)
time.sleep(1)

print("[3] Creating new assess_revenue_impact (No Parameters)...")
r = requests.post(f"{base}/tools", headers=h, json={
    "id": "assess_revenue_impact",
    "type": "esql",
    "description": (
        "Calculates revenue at risk grouped by supplier. Requires NO parameters. "
        "It returns the financial exposure for ALL suppliers. You must find the row matching the disrupted supplier_id "
        "and report those specific numbers back to the user."
    ),
    "configuration": {
        "query": ASSESS_QUERY,
        "params": {}
    }
})
print("Create response:", r.status_code, r.text[:100])

print("[4] Relinking to Orchestrator...")
requests.put(f"{base}/agents/supplyshield", headers=h, json={
    "name": "SupplyShield",
    "description": "Supply chain disruption detection and automated recovery agent",
    "configuration": {"tools": [{"tool_ids": ["detect_shipment_anomalies", "assess_revenue_impact", "find_alternative_suppliers", "news_scout_query"]}]}
})
print("Done.")
