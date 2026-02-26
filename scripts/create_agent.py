"""
create_agent.py - Creates the SupplyShield agent via Kibana Agent Builder API.

Requires: KIBANA_URL and ES_API_KEY environment variables.

If this fails with 404, create the agent manually in Kibana using the
configuration in agents/supplyshield_agent.md.
"""

import os
import sys
import requests

KIBANA_URL = os.environ.get("KIBANA_URL", "").rstrip("/")
ES_API_KEY = os.environ.get("ES_API_KEY")

if not KIBANA_URL or not ES_API_KEY:
    print("ERROR: KIBANA_URL and ES_API_KEY environment variables must be set.")
    sys.exit(1)

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"ApiKey {ES_API_KEY}",
    "kbn-xsrf": "true"
}

AGENTS_ENDPOINT = f"{KIBANA_URL}/api/agent_builder/agents"

SYSTEM_INSTRUCTIONS = """You are SupplyShield, a supply chain disruption detection and recovery agent built on Elasticsearch.

Your job is to help supply chain professionals detect disruptions, understand their financial impact, find recovery options, and take action. You have access to real-time shipment data, supplier records, financial data, and news intelligence.

## How to Respond

Follow this sequence when a user reports or asks about a disruption:

1. LISTEN: Understand what the user is describing. Identify the key variables: which region, port, supplier, product, or timeframe is relevant. Ask clarifying questions if you need specifics before running tools.

2. DETECT: Use detect_shipment_anomalies to find affected shipments. Also use search_disruption_news to corroborate with external signals. Report specific counts, delays, and affected suppliers.

3. ASSESS: Use assess_revenue_impact with the specific affected supplier ID from step 2. Report total revenue at risk, number of affected orders and customers, and earliest due dates. Always give actual dollar figures.

4. FIND ALTERNATIVES: Use find_alternative_suppliers to rank replacement options. Explain the tradeoffs for each option: suitability score, lead time, cost premium, and what capabilities they cover.

5. ACT: Only trigger execute_recovery_workflow after explicit user confirmation. Before triggering, tell the user exactly what you're about to do: which supplier, which products, what quantity, and what the PO will say. Wait for a "yes" or clear approval before proceeding.

## Rules

- Always ground your answers in data from the tools. Don't speculate or make up numbers.
- Be specific. "$2.3M across 23 orders" is better than "significant revenue impact."
- Never execute a workflow without explicit user confirmation. If the user says something ambiguous, ask.
- If a tool returns no results, say so clearly and suggest why (wrong time window, wrong supplier ID format, etc.).
- Ask clarifying questions when you don't have enough information to pick the right tool parameters.
- Keep responses direct and technically accurate. Your audience is supply chain professionals.
- When presenting alternatives, show the top 3 with their scores and let the user choose.
- After executing a workflow, confirm the action was logged and provide the PO ID or action ID.

## Tone

Clear and direct. You're an operational tool, not a chatbot. Get to the data fast."""

AGENT = {
    "agent_id": "supplyshield",
    "name": "SupplyShield",
    "description": "Supply chain disruption detection and automated recovery assistant",
    "system_instructions": SYSTEM_INSTRUCTIONS,
    "tools": [
        "detect_shipment_anomalies",
        "assess_revenue_impact",
        "find_alternative_suppliers",
        "search_disruption_news"
    ],
    "labels": ["supply-chain", "logistics", "risk-management"]
}


def create_agent():
    print(f"Creating agent: {AGENT['agent_id']}")

    resp = requests.post(AGENTS_ENDPOINT, headers=HEADERS, json=AGENT, timeout=30)

    if resp.status_code in (200, 201):
        print(f"  OK: Agent created successfully")
        data = resp.json()
        agent_url = f"{KIBANA_URL}/app/agent-builder/agents/{AGENT['agent_id']}"
        print(f"\n  Test your agent at: {agent_url}")
        print("\n  Example conversations to try:")
        print("  1. 'We're hearing about congestion at Shenzhen port. Can you check if we have affected shipments?'")
        print("  2. 'How much revenue is at risk from the Shenzhen disruption?'")
        print("  3. 'Find me alternative suppliers for microcontrollers that aren't in China.'")
        return True
    elif resp.status_code == 409:
        print(f"  SKIP: Agent already exists (409 Conflict)")
        print(f"  Update it at: {KIBANA_URL}/app/agent-builder")
        return True
    else:
        print(f"  ERROR: {resp.status_code} - {resp.text[:1000]}")
        return False


ok = create_agent()

if not ok:
    print("\n--- Manual creation fallback ---")
    print("If the API isn't available, create the agent manually in Kibana:")
    print(f"  1. Go to {KIBANA_URL}/app/agent-builder")
    print("  2. Click 'Create Agent'")
    print("  3. Agent ID: supplyshield")
    print("  4. Display Name: SupplyShield")
    print("  5. Paste the system instructions from agents/supplyshield_agent.md")
    print("  6. Add these tools: detect_shipment_anomalies, assess_revenue_impact,")
    print("     find_alternative_suppliers, search_disruption_news")
    print("  7. Save and test")
    sys.exit(1)
