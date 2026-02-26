"""
create_agent_v2.py - Tests agent API with system_prompt at top level and correct tool format.
"""
import os, sys, requests, json

KIBANA_URL = os.environ.get("KIBANA_URL", "").rstrip("/")
ES_API_KEY = os.environ.get("ES_API_KEY")
HEADERS = {"Content-Type": "application/json", "Authorization": f"ApiKey {ES_API_KEY}", "kbn-xsrf": "true"}
BASE = f"{KIBANA_URL}/api/agent_builder"

SYSTEM_PROMPT = (
    "You are SupplyShield, a supply chain disruption detection and recovery agent. "
    "Help supply chain professionals detect disruptions, understand financial impact, "
    "find recovery options, and take action.\n\n"
    "Sequence: 1) DETECT with detect_shipment_anomalies. 2) CORROBORATE with search_disruption_news. "
    "3) ASSESS revenue with assess_revenue_impact using the supplier_id from step 1. "
    "4) FIND alternatives with find_alternative_suppliers. "
    "5) ACT only after explicit user confirmation.\n\n"
    "Rules: Ground all answers in tool data. Be specific with dollar amounts and counts. "
    "Never execute workflows without explicit user confirmation. "
    "Ask clarifying questions when needed."
)

TOOL_IDS = [
    "detect_shipment_anomalies",
    "assess_revenue_impact",
    "find_alternative_suppliers",
    "search_disruption_news"
]

# Try: system_prompt at top level, tools in configuration
payloads = [
    # A: system_prompt top level, tools in configuration
    {"id": "supplyshield", "name": "SupplyShield", "description": "Supply chain disruption agent",
     "system_prompt": SYSTEM_PROMPT, "configuration": {"tools": [{"tool_ids": [t]} for t in TOOL_IDS]}},
    # B: systemPrompt top level
    {"id": "supplyshield", "name": "SupplyShield", "description": "Supply chain disruption agent",
     "systemPrompt": SYSTEM_PROMPT, "configuration": {"tools": [{"tool_ids": [t]} for t in TOOL_IDS]}},
    # C: instructions field
    {"id": "supplyshield", "name": "SupplyShield", "description": "Supply chain disruption agent",
     "instructions": SYSTEM_PROMPT, "configuration": {"tools": [{"tool_ids": [t]} for t in TOOL_IDS]}},
    # D: all tool_ids in single tools entry
    {"id": "supplyshield", "name": "SupplyShield", "description": "Supply chain disruption agent",
     "configuration": {"tools": [{"tool_ids": TOOL_IDS}]}},
    # E: no configuration, tools at top level
    {"id": "supplyshield", "name": "SupplyShield", "description": "Supply chain disruption agent",
     "tools": [{"tool_ids": TOOL_IDS}]},
]

for i, payload in enumerate(payloads, 1):
    requests.delete(f"{BASE}/agents/supplyshield", headers=HEADERS, timeout=10)
    r = requests.post(f"{BASE}/agents", headers=HEADERS, json=payload, timeout=30)
    top_keys = [k for k in payload if k not in ("id", "name", "description")]
    conf_keys = list(payload.get("configuration", {}).keys())
    print(f"Format {i} top:{top_keys} conf:{conf_keys}: {r.status_code} {r.text[:250]}")
    if r.status_code in (200, 201):
        print("  SUCCESS!")
        print(f"  {KIBANA_URL}/app/agent-builder")
        sys.exit(0)

print("\nAll formats failed.")
print("Please create the agent manually in Kibana Agent Builder:")
print(f"  {KIBANA_URL}/app/agent-builder")
print("Name: SupplyShield, add tools: detect_shipment_anomalies, assess_revenue_impact,")
print("  find_alternative_suppliers, search_disruption_news")
sys.exit(1)
