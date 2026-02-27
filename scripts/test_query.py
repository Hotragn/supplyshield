"""test_query.py"""
import os, requests, json

KB = "https://supplyshield-ac5120.es.us-east-1.aws.elastic.cloud:443"
es_url = KB + "/_elasticsearch/_esql"
h = {"Authorization": "ApiKey TWZPcW1Kd0JCZzE4V19IOUNITmw6NHZRVElsSFlRa0h4UGp6NGZQQ2pFdw==", "Content-Type": "application/json"}

# 1. Test assess_revenue_impact query
q1 = """
FROM sc_orders
| WHERE status == "active"
| LOOKUP JOIN sc_products ON product_id
| WHERE primary_supplier_id == ?affected_supplier_id
| LOOKUP JOIN sc_suppliers ON primary_supplier_id
| STATS
    total_revenue_at_risk = SUM(revenue_value),
    affected_orders = COUNT(*),
    affected_customers = COUNT_DISTINCT(customer_id),
    earliest_due = MIN(required_date),
    avg_order_value = AVG(revenue_value)
  BY product_id, product_name, supplier_name
| SORT total_revenue_at_risk DESC
"""

body1 = {
    "query": q1,
    "params": [{"affected_supplier_id": "SUP-SZ-001"}]
}

r1 = requests.post(es_url, headers=h, json=body1)
print("Query 1:", r1.status_code)
print(json.dumps(r1.json(), indent=2))

# 2. Test find_alternative_suppliers query
q2 = """
FROM sc_suppliers
| WHERE active == true
  AND supplier_id != ?excluded_supplier_id
  AND region != ?excluded_region
| EVAL suitability_score = (reliability_score * 0.4) + (capacity_score * 0.3) + ((100.0 - lead_time_days) * 0.3)
| EVAL cost_premium_pct = CASE(
    lead_time_days <= 14, 5.0,
    lead_time_days <= 21, 10.0,
    lead_time_days <= 30, 15.0,
    20.0
  )
| KEEP supplier_id, supplier_name, region, country, capabilities, reliability_score, capacity_score, lead_time_days, suitability_score, cost_premium_pct
| SORT suitability_score DESC
| LIMIT 5
"""

body2 = {
    "query": q2,
    "params": [
        {"excluded_supplier_id": "SUP-SZ-001"},
        {"excluded_region": "East Asia"}
    ]
}

r2 = requests.post(es_url, headers=h, json=body2)
print("Query 2:", r2.status_code)
print(json.dumps(r2.json(), indent=2))
