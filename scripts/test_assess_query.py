import os
from elasticsearch import Elasticsearch

es = Elasticsearch(os.environ['ES_ENDPOINT'], api_key=os.environ['ES_API_KEY'])

q = '''
FROM sc_orders
| WHERE status == "active"
| LOOKUP JOIN sc_products ON product_id
| EVAL supplier_id = primary_supplier_id
| LOOKUP JOIN sc_suppliers ON supplier_id
| STATS
    total_revenue_at_risk = SUM(revenue_value),
    affected_orders = COUNT(*),
    affected_customers = COUNT_DISTINCT(customer_id),
    earliest_due = MIN(required_date),
    avg_order_value = AVG(revenue_value)
  BY supplier_id, supplier_name
| SORT total_revenue_at_risk DESC
| LIMIT 50
'''

try:
    r = es.esql.query(query=q)
    print("SUCCESS! Returned:")
    cols = [c["name"] for c in r["columns"]]
    for row in r.get("values", []):
        print(dict(zip(cols, row)))
except Exception as e:
    print('Error:', e)
