"""add_capability_filter.py - Add capability filter to find_alternative_suppliers using MV_CONTAINS"""
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

ALTS_QUERY = (
    'FROM sc_suppliers\n'
    '| WHERE active == true\n'
    '  AND supplier_id != ?excluded_supplier_id\n'
    '  AND region != ?excluded_region\n'
    '  AND MV_CONTAINS(capabilities, ?required_capability)\n'
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

print("[1] Temporarily unlinking from Orchestrator...")
requests.put(f"{base}/agents/supplyshield", headers=h, json={
    "name": "SupplyShield",
    "description": "Supply chain disruption detection and automated recovery agent",
    "configuration": {"tools": [{"tool_ids": ["detect_shipment_anomalies", "assess_revenue_impact", "news_scout_query"]}]}
})
time.sleep(1)

print("[2] Deleting old find_alternative_suppliers...")
requests.delete(f"{base}/tools/find_alternative_suppliers", headers=h)
time.sleep(1)

print("[3] Creating new find_alternative_suppliers with capability filter...")
r = requests.post(f"{base}/tools", headers=h, json={
    "id": "find_alternative_suppliers",
    "type": "esql",
    "description": (
        "Ranks top 5 active alternative suppliers by weighted suitability score. "
        "REQUIRED: required_capability (e.g. microcontrollers), excluded_supplier_id. "
        "OPTIONAL: excluded_region. "
        "Returns suitability_score, lead_time_days, cost_premium_pct."
    ),
    "configuration": {
        "query": ALTS_QUERY,
        "params": {
            "required_capability": {"type": "string", "description": "Capability required (e.g. microcontrollers, battery-cells). MUST be a single word without wildcards."},
            "excluded_supplier_id": {"type": "string", "description": "Supplier ID to exclude (e.g. SUP-SZ-001)."},
            "excluded_region": {"type": "string", "description": "Region to exclude (e.g. East Asia). Pass empty string if no exclusion needed."}
        }
    }
})
print("Create response:", r.status_code)

print("[4] Relinking to Orchestrator...")
requests.put(f"{base}/agents/supplyshield", headers=h, json={
    "name": "SupplyShield",
    "description": "Supply chain disruption detection and automated recovery agent",
    "configuration": {"tools": [{"tool_ids": ["detect_shipment_anomalies", "assess_revenue_impact", "find_alternative_suppliers", "news_scout_query"]}]}
})
print("Done.")
