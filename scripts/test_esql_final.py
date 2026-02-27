import os
from elasticsearch import Elasticsearch

es = Elasticsearch(os.environ['ES_ENDPOINT'], api_key=os.environ['ES_API_KEY'])

# Test MV_CONTAINS for capabilities array in alternative_suppliers
# because `capabilities == "microcontrollers"` won't work perfectly if it's not supported
q_mv = 'FROM sc_suppliers | WHERE MV_CONTAINS(capabilities, "microcontrollers") | LIMIT 5'
try:
    print("Testing MV_CONTAINS:")
    r = es.esql.query(query=q_mv)
    print("SUCCESS, found", len(r['values']))
except Exception as e:
    print("MV_CONTAINS Error:", e)

# Test assess_revenue_impact with parameters
q_assess = '''
FROM sc_orders
| WHERE status == "active"
| LOOKUP JOIN sc_products ON product_id
| WHERE primary_supplier_id == ?affected_supplier_id
| LOOKUP JOIN sc_suppliers ON primary_supplier_id
| STATS total = SUM(revenue_value) BY product_name
'''
try:
    print("\nTesting assess_revenue_impact with param:")
    r2 = es.esql.query(query=q_assess, params=['SUP-SZ-001'])
    print("SUCCESS")
except Exception as e:
    print("assess Error:", e)
