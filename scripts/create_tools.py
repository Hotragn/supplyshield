"""
create_tools.py - Creates SupplyShield Agent Builder tools via Kibana API.

Correct API format discovered:
  - Top level: id, type, description (NO 'name', NO 'labels')
  - configuration: { query, params }
  - params: flat dict { param_name: { type, description } }

Requires: KIBANA_URL and ES_API_KEY environment variables.
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

TOOLS_ENDPOINT = f"{KIBANA_URL}/api/agent_builder/tools"

DETECT_QUERY = "\n".join([
    "FROM sc_shipments",
    "| WHERE @timestamp > NOW() - ?time_window::DURATION",
    "  AND delay_hours > ?delay_threshold",
    "| LOOKUP JOIN sc_suppliers ON supplier_id",
    "| LOOKUP JOIN sc_products ON product_id",
    "| STATS",
    "    affected_shipments = COUNT(*),",
    "    avg_delay_hours = AVG(delay_hours),",
    "    max_delay_hours = MAX(delay_hours),",
    "    distinct_components = COUNT_DISTINCT(product_id)",
    "  BY supplier_id, supplier_name, region, country, origin_port",
    "| SORT affected_shipments DESC",
    "| LIMIT 20",
])

ASSESS_QUERY = "\n".join([
    'FROM sc_orders',
    '| WHERE status == "active"',
    '  AND required_date < NOW() + ?planning_horizon::DURATION',
    '| LOOKUP JOIN sc_products ON product_id',
    '| WHERE primary_supplier_id == ?affected_supplier_id',
    '| LOOKUP JOIN sc_suppliers ON primary_supplier_id',
    '| STATS',
    '    total_revenue_at_risk = SUM(revenue_value),',
    '    affected_orders = COUNT(*),',
    '    affected_customers = COUNT_DISTINCT(customer_id),',
    '    earliest_due = MIN(required_date),',
    '    avg_order_value = AVG(revenue_value)',
    '  BY product_id, product_name, supplier_name',
    '| SORT total_revenue_at_risk DESC',
])

FIND_QUERY = "\n".join([
    "FROM sc_suppliers",
    "| WHERE active == true",
    "  AND capabilities LIKE ?required_capability",
    "  AND supplier_id != ?excluded_supplier_id",
    "  AND region != ?excluded_region",
    "| EVAL suitability_score = (reliability_score * 0.4) + (capacity_score * 0.3) + ((100.0 - lead_time_days) * 0.3)",
    "| EVAL cost_premium_pct = CASE(",
    "    lead_time_days <= 14, 5.0,",
    "    lead_time_days <= 21, 10.0,",
    "    lead_time_days <= 30, 15.0,",
    "    20.0",
    "  )",
    "| KEEP supplier_id, supplier_name, region, country, capabilities,",
    "       reliability_score, capacity_score, lead_time_days,",
    "       suitability_score, cost_premium_pct",
    "| SORT suitability_score DESC",
    "| LIMIT 5",
])

TOOLS = [
    {
        "id": "detect_shipment_anomalies",
        "type": "esql",
        "description": (
            "Finds delayed shipments by joining shipment data with supplier and product information using ES|QL LOOKUP JOINs. "
            "Use this tool when a user reports a disruption at a specific port, region, or supplier and wants to know which "
            "shipments are affected. Returns counts, average delay, max delay, and distinct components grouped by supplier and port. "
            "Do NOT use for financial impact analysis, customer orders, or revenue - use assess_revenue_impact for that."
        ),
        "configuration": {
            "query": DETECT_QUERY,
            "params": {
                "time_window": {
                    "type": "string",
                    "description": "Lookback window in ES duration format, e.g. '336 hours', '168 hours'. Default: 336 hours."
                },
                "delay_threshold": {
                    "type": "integer",
                    "description": "Minimum delay in hours to flag a shipment. Default: 24."
                }
            }
        }
    },
    {
        "id": "assess_revenue_impact",
        "type": "esql",
        "description": (
            "Calculates the financial blast radius of a supplier disruption. Given an affected_supplier_id, joins active orders "
            "to products and suppliers to determine total revenue at risk, order count, customer count, and earliest due dates. "
            "Always requires a specific affected_supplier_id from the detect_shipment_anomalies results. "
            "Do NOT use without a supplier ID, and do NOT use to find alternatives."
        ),
        "configuration": {
            "query": ASSESS_QUERY,
            "params": {
                "planning_horizon": {
                    "type": "string",
                    "description": "How far ahead to look for due orders. E.g. '30 days', '14 days'. Default: 30 days."
                },
                "affected_supplier_id": {
                    "type": "string",
                    "description": "REQUIRED. The supplier_id of the disrupted supplier from detect_shipment_anomalies results."
                }
            }
        }
    },
    {
        "id": "find_alternative_suppliers",
        "type": "esql",
        "description": (
            "Ranks active alternative suppliers by weighted suitability score for a required capability. "
            "Excludes the disrupted supplier and optionally the disrupted region. Use after detect_shipment_anomalies "
            "identifies the affected supplier and you know what capability is needed. "
            "Do NOT use for disruption detection or revenue calculations."
        ),
        "configuration": {
            "query": FIND_QUERY,
            "params": {
                "required_capability": {
                    "type": "string",
                    "description": "Capability to filter on. Supports wildcards, e.g. 'battery-cells', 'microcontrollers*'."
                },
                "excluded_supplier_id": {
                    "type": "string",
                    "description": "Supplier ID to exclude (the disrupted supplier)."
                },
                "excluded_region": {
                    "type": "string",
                    "description": "Region to exclude. Pass empty string for global search."
                }
            }
        }
    },
    {
        "id": "search_disruption_news",
        "type": "index_search",
        "description": (
            "Hybrid semantic and keyword search across news articles about supply chain disruptions. "
            "Use to corroborate shipment anomalies with external signals, get early warning of emerging disruptions, "
            "or verify whether a detected anomaly is a known event. "
            "Do NOT use for supplier data, shipment counts, or financial figures."
        ),
        "configuration": {
            "index": "sc_news",
            "fields": ["title", "body"],
            "knn_field": "body_embedding",
            "source_fields": ["title", "body", "regions", "sentiment_score", "disruption_type", "severity", "published_date"]
        }
    }
]


def create_tool(tool):
    tool_id = tool["id"]
    print(f"\n  Creating tool: {tool_id}")

    # Try DELETE first to avoid conflicts from previous attempts
    requests.delete(f"{TOOLS_ENDPOINT}/{tool_id}", headers=HEADERS, timeout=10)

    resp = requests.post(TOOLS_ENDPOINT, headers=HEADERS, json=tool, timeout=30)

    if resp.status_code in (200, 201):
        print(f"    OK ({resp.status_code})")
        return True
    elif resp.status_code == 409:
        print(f"    SKIP: already exists")
        return True
    else:
        print(f"    ERROR {resp.status_code}: {resp.text[:600]}")
        return False


print(f"Creating Agent Builder tools...")
all_ok = True
for tool in TOOLS:
    ok = create_tool(tool)
    if not ok:
        all_ok = False

if all_ok:
    print("\nAll tools created successfully.")
    print("Next: python scripts/create_agent.py")
else:
    print("\nSome tools failed.")
    print("Create manually in Kibana: Management > Agent Builder > Tools")
    sys.exit(1)
