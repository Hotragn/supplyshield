import os
from elasticsearch import Elasticsearch

es = Elasticsearch(os.environ['ES_ENDPOINT'], api_key=os.environ['ES_API_KEY'])

q1 = 'FROM sc_orders | WHERE status == "active" | LOOKUP JOIN sc_products ON product_id | WHERE primary_supplier_id == ?affected_supplier_id | LOOKUP JOIN sc_suppliers ON primary_supplier_id | STATS total_revenue = SUM(revenue_value) BY product_name'

try:
    r1 = es.esql.query(query=q1, params=['SUP-SZ-001'])
    print('Q1 Success:', r1)
except Exception as e:
    print('Q1 Error:', e)
