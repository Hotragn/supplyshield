"""fix_assess_tool_final.py - Fix the actual ES|QL join bug"""
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

# The REAL bug:
# LOOKUP JOIN sc_suppliers ON primary_supplier_id
# Fails because sc_suppliers doesn't have `primary_supplier_id`, it has `supplier_id`.
# The fix: EVAL supplier_id = primary_supplier_id BEFORE the join.

ASSESS_QUERY = (
    'FROM sc_orders\n'
    '| WHERE status == "active"\n'
    '| LOOKUP JOIN sc_products ON product_id\n'
    '| WHERE primary_supplier_id == ?affected_supplier_id\n'
    '| EVAL supplier_id = primary_supplier_id\n'
    '| LOOKUP JOIN sc_suppliers ON supplier_id\n'
    '| STATS\n'
    '    total_revenue_at_risk = SUM(revenue_value),\n'
    '    affected_orders = COUNT(*),\n'
    '    affected_customers = COUNT_DISTINCT(customer_id),\n'
    '    earliest_due = MIN(required_date),\n'
    '    avg_order_value = AVG(revenue_value)\n'
    '  BY product_id, product_name, supplier_name\n'
    '| SORT total_revenue_at_risk DESC'
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

print("[3] Creating correct assess_revenue_impact with parameters AND Eval mapping...")
r = requests.post(f"{base}/tools", headers=h, json={
    "id": "assess_revenue_impact",
    "type": "esql",
    "description": (
        "Calculates revenue at risk for a disrupted supplier. "
        "REQUIRED: affected_supplier_id (e.g. SUP-SZ-001). "
        "Returns total_revenue_at_risk, affected_orders, affected_customers, earliest_due."
    ),
    "configuration": {
        "query": ASSESS_QUERY,
        "params": {
            "affected_supplier_id": {
                "type": "string",
                "description": "Exact supplier_id of the disrupted supplier (e.g. SUP-SZ-001). Get from detect_shipment_anomalies results."
            }
        }
    }
})
print("Create response:", r.status_code, r.text[:100])
time.sleep(1)

print("[4] Relinking to Orchestrator...")
requests.put(f"{base}/agents/supplyshield", headers=h, json={
    "name": "SupplyShield",
    "description": "Supply chain disruption detection and automated recovery agent",
    "configuration": {"tools": [{"tool_ids": ["detect_shipment_anomalies", "assess_revenue_impact", "find_alternative_suppliers", "news_scout_query"]}]}
})
print("Done!")
