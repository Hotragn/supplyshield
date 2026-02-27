"""debug_tools.py - Check actual ES data to diagnose tool failures"""
import os, json
from elasticsearch import Elasticsearch

env = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
if os.path.exists(env):
    for line in open(env):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

es = Elasticsearch(os.environ["ES_ENDPOINT"], api_key=os.environ["ES_API_KEY"])

# 1. Check sc_products - does primary_supplier_id exist?
print("=== sc_products sample ===")
r = es.search(index="sc_products", body={"size": 2})
for h in r["hits"]["hits"]:
    print(json.dumps(h["_source"], indent=2))

# 2. Check sc_orders - does revenue_value and primary_supplier_id exist?
print("\n=== sc_orders sample ===")
r = es.search(index="sc_orders", body={"size": 2, "query": {"term": {"status": "active"}}})
for h in r["hits"]["hits"]:
    print(json.dumps(h["_source"], indent=2))

# 3. Check sc_suppliers capabilities field
print("\n=== sc_suppliers capabilities field ===")
r = es.search(index="sc_suppliers", body={
    "size": 5,
    "_source": ["supplier_id", "supplier_name", "region", "capabilities", "active"]
})
for h in r["hits"]["hits"]:
    print(json.dumps(h["_source"], indent=2))

# 4. Try assess_revenue_impact ES|QL manually
print("\n=== assess_revenue_impact ESQL test ===")
try:
    r2 = es.esql.query(body={
        "query": """
FROM sc_orders
| WHERE status == "active"
| LOOKUP JOIN sc_products ON product_id
| WHERE primary_supplier_id == "SUP-SZ-001"
| STATS total = SUM(revenue_value), orders = COUNT(*) BY product_id, product_name
"""
    })
    print(f"Rows: {len(r2.get('values', []))}")
    if r2.get('values'):
        cols = [c['name'] for c in r2['columns']]
        print("Columns:", cols)
        for row in r2['values'][:3]:
            print(dict(zip(cols, row)))
    else:
        print("NO RESULTS - checking why...")
        # Check if sc_products has primary_supplier_id
        r3 = es.esql.query(body={"query": "FROM sc_products | LIMIT 1"})
        cols = [c['name'] for c in r3['columns']]
        print("sc_products columns:", cols)
except Exception as e:
    print(f"Error: {e}")

# 5. Try find_alternative_suppliers
print("\n=== find_alternatives ESQL test ===")
try:
    r4 = es.esql.query(body={
        "query": """
FROM sc_suppliers
| WHERE active == true
  AND region != "East Asia"
| EVAL suitability_score = (reliability_score * 0.4) + (capacity_score * 0.3) + ((100.0 - lead_time_days) * 0.3)
| KEEP supplier_id, supplier_name, region, capabilities, suitability_score, lead_time_days
| SORT suitability_score DESC
| LIMIT 5
"""
    })
    cols = [c['name'] for c in r4['columns']]
    print("Rows:", len(r4.get('values', [])))
    for row in r4.get('values', [])[:5]:
        print(dict(zip(cols, row)))
except Exception as e:
    print(f"Error: {e}")
