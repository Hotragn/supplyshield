"""probe_param_types.py - Find correct type string for esql tool params"""
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
b = f"{KB}/api/agent_builder"

Q = (
    'FROM sc_orders '
    '| WHERE status == "active" '
    '| LOOKUP JOIN sc_products ON product_id '
    '| WHERE primary_supplier_id == ?affected_supplier_id '
    '| STATS total = SUM(revenue_value), cnt = COUNT(*) BY product_name'
)

ASSESS_Q = (
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

ALTS_Q = (
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

for ptype in ["str", "string", "keyword"]:
    r = requests.post(f"{b}/tools", headers=h, json={
        "id": "assess_revenue_impact",
        "type": "esql",
        "description": "Revenue impact tool. REQUIRED: affected_supplier_id.",
        "configuration": {
            "query": Q,
            "params": {"affected_supplier_id": {"type": ptype, "description": "Supplier ID (e.g. SUP-SZ-001)"}}
        }
    }, timeout=15)
    print(f"type={ptype}: {r.status_code} {r.text[:120]}")
    if r.status_code in (200, 201):
        print(f"  SUCCESS with type='{ptype}'")
        # Now create the proper tool with full query
        requests.delete(f"{b}/tools/assess_revenue_impact", headers=h)
        time.sleep(0.5)

        r2 = requests.post(f"{b}/tools", headers=h, json={
            "id": "assess_revenue_impact",
            "type": "esql",
            "description": (
                "Calculates revenue at risk for a disrupted supplier. "
                "REQUIRED: affected_supplier_id (e.g. SUP-SZ-001). "
                "Returns total_revenue_at_risk, affected_orders, affected_customers, earliest_due."
            ),
            "configuration": {
                "query": ASSESS_Q,
                "params": {"affected_supplier_id": {"type": ptype, "description": "Exact supplier_id (e.g. SUP-SZ-001). Get from detect_shipment_anomalies results."}}
            }
        }, timeout=20)
        print(f"  Full assess_revenue_impact: {r2.status_code} {r2.text[:150]}")
        time.sleep(1)

        r3 = requests.post(f"{b}/tools", headers=h, json={
            "id": "find_alternative_suppliers",
            "type": "esql",
            "description": (
                "Ranks top 5 active alternative suppliers by weighted suitability score. "
                "REQUIRED: excluded_supplier_id. OPTIONAL: excluded_region (e.g. East Asia). "
                "Returns suitability_score, lead_time_days, cost_premium_pct, capabilities."
            ),
            "configuration": {
                "query": ALTS_Q,
                "params": {
                    "excluded_supplier_id": {"type": ptype, "description": "Supplier ID to exclude (e.g. SUP-SZ-001)."},
                    "excluded_region": {"type": ptype, "description": "Region to exclude (e.g. East Asia). Pass empty string if no exclusion needed."}
                }
            }
        }, timeout=20)
        print(f"  find_alternative_suppliers: {r3.status_code} {r3.text[:150]}")
        time.sleep(1)

        # Restore all tools
        r4 = requests.put(f"{b}/agents/supplyshield", headers=h, json={
            "name": "SupplyShield",
            "description": "Supply chain disruption detection and automated recovery agent",
            "configuration": {"tools": [{"tool_ids": ["detect_shipment_anomalies", "assess_revenue_impact", "find_alternative_suppliers", "news_scout_query"]}]}
        })
        tools = r4.json().get("configuration", {}).get("tools", [{}])[0].get("tool_ids", [])
        print(f"  Final Orchestrator tools: {tools}")
        break
    requests.delete(f"{b}/tools/assess_revenue_impact", headers=h)
    time.sleep(0.5)
