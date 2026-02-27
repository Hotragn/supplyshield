"""fix_all_tools.py - Fix broken Kibana tool queries (correct API format)"""
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

ASSESS_QUERY = (
    'FROM sc_orders\n'
    '| WHERE status == "active"\n'
    '| LOOKUP JOIN sc_products ON product_id\n'
    '| WHERE primary_supplier_id == ?affected_supplier_id\n'
    '| LOOKUP JOIN sc_suppliers ON primary_supplier_id\n'
    '| STATS\n'
    '    total_revenue_at_risk = SUM(revenue_value),\n'
    '    affected_orders = COUNT(*),\n'
    '    affected_customers = COUNT_DISTINCT(customer_id),\n'
    '    earliest_due = MIN(required_date),\n'
    '    avg_order_value = AVG(revenue_value)\n'
    '  BY product_id, product_name, supplier_name\n'
    '| SORT total_revenue_at_risk DESC'
)

ALTS_QUERY = (
    'FROM sc_suppliers\n'
    '| WHERE active == true\n'
    '  AND supplier_id != ?excluded_supplier_id\n'
    '  AND region != ?excluded_region\n'
    '| EVAL suitability_score = (reliability_score * 0.4) + (capacity_score * 0.3) + ((100.0 - lead_time_days) * 0.3)\n'
    '| EVAL cost_premium_pct = CASE(\n'
    '    lead_time_days <= 14, 5.0,\n'
    '    lead_time_days <= 21, 10.0,\n'
    '    lead_time_days <= 30, 15.0,\n'
    '    20.0\n'
    '  )\n'
    '| KEEP supplier_id, supplier_name, region, country, capabilities, reliability_score, capacity_score, lead_time_days, suitability_score, cost_premium_pct\n'
    '| SORT suitability_score DESC\n'
    '| LIMIT 5'
)

ALL_TOOLS = ["detect_shipment_anomalies", "assess_revenue_impact", "find_alternative_suppliers", "news_scout_query"]

def remove_from_orch(tools_list):
    r = requests.put(f"{base}/agents/supplyshield", headers=h, json={
        "name": "SupplyShield",
        "description": "Supply chain disruption detection and automated recovery agent",
        "configuration": {"tools": [{"tool_ids": tools_list}]}
    })
    print(f"  Orch updated to {tools_list}: {r.status_code}")
    time.sleep(1)

# ── FIX 1: assess_revenue_impact ──────────────────────────────────────────────
print("[1] Fixing assess_revenue_impact...")
remove_from_orch(["detect_shipment_anomalies", "find_alternative_suppliers", "news_scout_query"])
requests.delete(f"{base}/tools/assess_revenue_impact", headers=h)
time.sleep(1)
r1 = requests.post(f"{base}/tools", headers=h, json={
    "id": "assess_revenue_impact",
    "type": "esql",
    "description": (
        "Calculates revenue at risk for a disrupted supplier. "
        "REQUIRED: affected_supplier_id (e.g. SUP-SZ-001). "
        "Joins active orders to products. Returns total_revenue_at_risk, affected_orders, affected_customers, earliest_due, avg_order_value."
    ),
    "configuration": {
        "query": ASSESS_QUERY,
        "params": [
            {
                "name": "affected_supplier_id",
                "description": "Supplier ID of the disrupted supplier (e.g. SUP-SZ-001). Get exact ID from detect_shipment_anomalies results.",
                "type": "text"
            }
        ]
    }
})
print(f"  Created: {r1.status_code} {r1.text[:200]}")
time.sleep(1)

# ── FIX 2: find_alternative_suppliers ─────────────────────────────────────────
print("\n[2] Fixing find_alternative_suppliers...")
remove_from_orch(["detect_shipment_anomalies", "assess_revenue_impact", "news_scout_query"])
requests.delete(f"{base}/tools/find_alternative_suppliers", headers=h)
time.sleep(1)
r2 = requests.post(f"{base}/tools", headers=h, json={
    "id": "find_alternative_suppliers",
    "type": "esql",
    "description": (
        "Ranks top 5 active alternative suppliers by weighted suitability score. "
        "REQUIRED: excluded_supplier_id (disrupted supplier). "
        "OPTIONAL: excluded_region (e.g. East Asia). "
        "Returns suitability_score, lead_time_days, cost_premium_pct, capabilities."
    ),
    "configuration": {
        "query": ALTS_QUERY,
        "params": [
            {
                "name": "excluded_supplier_id",
                "description": "Supplier ID to exclude - the disrupted supplier (e.g. SUP-SZ-001).",
                "type": "text"
            },
            {
                "name": "excluded_region",
                "description": "Region to exclude (e.g. East Asia). Pass empty string for no exclusion.",
                "type": "text"
            }
        ]
    }
})
print(f"  Created: {r2.status_code} {r2.text[:200]}")
time.sleep(1)

# ── RE-ADD all 4 tools to orchestrator ───────────────────────────────────────
print("\n[3] Re-adding all 4 tools to Orchestrator...")
remove_from_orch(ALL_TOOLS)
print(f"Final tools: {ALL_TOOLS}")
print("\nDone. Now update the system prompt in Kibana UI (see instructions below).")
print("""
SYSTEM PROMPT MUST BE UPDATED MANUALLY IN KIBANA UI:
Go to Agent Builder -> SupplyShield -> Edit -> Instructions

Replace with:
---
You are SupplyShield, a supply chain disruption detection and recovery agent.

TOOL USAGE RULES:
1. On EVERY disruption message: call BOTH detect_shipment_anomalies AND news_scout_query immediately.
2. Use exact supplier_id values from tool results (e.g. SUP-SZ-001) as parameters - not supplier names.
3. For assess_revenue_impact: affected_supplier_id is REQUIRED.
4. For find_alternative_suppliers: excluded_supplier_id is REQUIRED, excluded_region is optional.
5. Always report actual numbers from tools. Never guess.

SEQUENCE:
1. DETECT: detect_shipment_anomalies + news_scout_query (run both)
2. ASSESS: assess_revenue_impact with supplier_id from step 1
3. ALTERNATIVES: find_alternative_suppliers with excluded_supplier_id and excluded_region
4. ACT: Describe what you will do, wait for explicit user confirmation before proceeding.
---
""")
