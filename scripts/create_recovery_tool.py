"""create_recovery_tool.py - Adds the execute_recovery_workflow tool to Orchestrator"""
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

# The agent needs a webhook tool to "execute" the PO.
# For the hackathon, we simulate a workflow trigger by calling an Elasticsearch API
# to index an audit log document. This proves the agent can "act" and write data back.

print("[1] Creating execute_recovery_workflow tool...")
# Delete if it exists
requests.delete(f"{base}/tools/execute_recovery_workflow", headers=h)
time.sleep(1)

r = requests.post(f"{base}/tools", headers=h, json={
    "id": "execute_recovery_workflow",
    "type": "webhook",  # Using webhook instead of esql for an action
    "description": (
        "Triggers the automated recovery workflow to create a purchase order with an alternative supplier. "
        "Use this only after the user explicitly says 'yes' or confirms the action. "
        "Requires supplier_id, product_name, and quantity."
    ),
    "configuration": {
        "url": os.environ["ES_ENDPOINT"] + "/sc_actions_log/_doc",
        "method": "post",
        "headers": {
            "Authorization": "ApiKey " + os.environ["ES_API_KEY"],
            "Content-Type": "application/json"
        },
        "body": '{\n  "action": "CREATE_PO",\n  "supplier_id": "{{supplier_id}}",\n  "product_name": "{{product_name}}",\n  "quantity": {{quantity}},\n  "status": "triggered",\n  "timestamp": "{{now}}"\n}',
        "params": {
            "supplier_id": {
                "type": "string",
                "description": "ID of the alternative supplier chosen (e.g. SUP-VN-001)"
            },
            "product_name": {
                "type": "string",
                "description": "Name of the product/component to order"
            },
            "quantity": {
                "type": "integer",
                "description": "Number of units to order"
            }
        }
    }
})
print("Create response:", r.status_code, r.text[:150])

print("\n[2] Attaching to Orchestrator...")
r2 = requests.put(f"{base}/agents/supplyshield", headers=h, json={
    "name": "SupplyShield",
    "description": "Supply chain disruption detection and automated recovery agent",
    "configuration": {"tools": [{"tool_ids": [
        "detect_shipment_anomalies", 
        "assess_revenue_impact", 
        "find_alternative_suppliers", 
        "news_scout_query",
        "execute_recovery_workflow"
    ]}]}
})
print("Attach response:", r2.status_code)
print("Finished!")
