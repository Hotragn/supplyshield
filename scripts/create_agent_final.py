"""
create_agent_final.py - Creates the SupplyShield agent after probing the correct API format.

The agent API requires tools under configuration.tools (array of strings).
"""
import os, sys, requests, json

KIBANA_URL = os.environ.get("KIBANA_URL", "").rstrip("/")
ES_API_KEY = os.environ.get("ES_API_KEY")
if not KIBANA_URL or not ES_API_KEY:
    print("ERROR: KIBANA_URL and ES_API_KEY must be set.")
    sys.exit(1)

HEADERS = {"Content-Type": "application/json", "Authorization": f"ApiKey {ES_API_KEY}", "kbn-xsrf": "true"}
BASE = f"{KIBANA_URL}/api/agent_builder"

SYSTEM_PROMPT = (
    "You are SupplyShield, a supply chain disruption detection and recovery agent.\n\n"
    "Help supply chain professionals detect disruptions, understand financial impact, "
    "find recovery options, and take action.\n\n"
    "## Sequence\n\n"
    "1. LISTEN: Identify region, port, supplier, or timeframe from the user message.\n"
    "2. DETECT: Use detect_shipment_anomalies to find affected shipments. "
    "Use search_disruption_news to corroborate with external signals.\n"
    "3. ASSESS: Use assess_revenue_impact with the specific supplier_id from step 2. "
    "Report actual dollar figures.\n"
    "4. FIND ALTERNATIVES: Use find_alternative_suppliers. Show top 3 with suitability score, "
    "lead time, and cost premium. Let the user choose.\n"
    "5. ACT: Only trigger recovery workflow after explicit user confirmation. "
    "Always describe what you will do first and wait for approval.\n\n"
    "## Rules\n\n"
    "- Ground all answers in tool data. No speculation.\n"
    '- Be specific: "$2.3M across 23 orders" not "significant impact."\n'
    "- Never execute a workflow without explicit user confirmation.\n"
    "- If a tool returns no results, say so and explain possible reasons.\n"
    "- Ask clarifying questions when you need more info to pick tool parameters.\n"
    "- Your audience is supply chain professionals. Get to the data fast."
)

TOOL_IDS = [
    "detect_shipment_anomalies",
    "assess_revenue_impact",
    "find_alternative_suppliers",
    "search_disruption_news"
]

# Try a few different agent API shapes
payloads = [
    # Format 1: tools as [{tool_ids: [id]}]
    {
        "id": "supplyshield",
        "name": "SupplyShield",
        "description": "Supply chain disruption detection and automated recovery assistant",
        "configuration": {
            "tools": [{"tool_ids": [t]} for t in TOOL_IDS],
            "system_prompt": SYSTEM_PROMPT
        }
    },
    # Format 2: tools as [{tool_ids: [id], ...}] with systemPrompt
    {
        "id": "supplyshield",
        "name": "SupplyShield",
        "description": "Supply chain disruption detection and automated recovery assistant",
        "configuration": {
            "tools": [{"tool_ids": [t]} for t in TOOL_IDS],
            "systemPrompt": SYSTEM_PROMPT
        }
    },
    # Format 3: all tool_ids in one entry
    {
        "id": "supplyshield",
        "name": "SupplyShield",
        "description": "Supply chain disruption detection and automated recovery assistant",
        "configuration": {
            "tools": [{"tool_ids": TOOL_IDS}],
            "system_prompt": SYSTEM_PROMPT
        }
    },
    # Format 4: with type field on each tool
    {
        "id": "supplyshield",
        "name": "SupplyShield",
        "description": "Supply chain disruption detection and automated recovery assistant",
        "configuration": {
            "tools": [{"tool_ids": TOOL_IDS, "type": "custom"}],
            "system_prompt": SYSTEM_PROMPT
        }
    },
]


for i, payload in enumerate(payloads, 1):
    # Clean up any existing
    requests.delete(f"{BASE}/agents/supplyshield", headers=HEADERS, timeout=10)

    r = requests.post(f"{BASE}/agents", headers=HEADERS, json=payload, timeout=30)
    conf_keys = list(payload.get("configuration", {}).keys())
    print(f"Format {i} (conf: {conf_keys}): {r.status_code}")
    if r.status_code in (200, 201):
        print("  SUCCESS!")
        print(f"  Agent URL: {KIBANA_URL}/app/agent-builder/agents/supplyshield")
        try:
            data = r.json()
            print(f"  Response: {json.dumps(data)[:400]}")
        except Exception:
            print(f"  Response: {r.text[:400]}")
        sys.exit(0)
    else:
        print(f"  {r.text[:300]}")

print("\nAll formats failed. Create agent manually in Kibana:")
print(f"  {KIBANA_URL}/app/agent-builder")
sys.exit(1)
