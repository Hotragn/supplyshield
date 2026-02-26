"""
load_data.py - Bulk loads generated data into Elasticsearch.

Run after generate_data.py. Reads from data/sample_data/ and loads into
all SupplyShield indices.

Requires: ES_ENDPOINT and ES_API_KEY environment variables.
"""

import json
import os
import sys
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

ES_ENDPOINT = os.environ.get("ES_ENDPOINT")
ES_API_KEY = os.environ.get("ES_API_KEY")

if not ES_ENDPOINT or not ES_API_KEY:
    print("ERROR: ES_ENDPOINT and ES_API_KEY environment variables must be set.")
    sys.exit(1)

es = Elasticsearch(ES_ENDPOINT, api_key=ES_API_KEY)

try:
    es.info()
    print("Connected to Elasticsearch")
except Exception as e:
    print(f"ERROR: Could not connect to Elasticsearch: {e}")
    sys.exit(1)

DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")


def load_file(filename, index_name, id_field):
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        print(f"  SKIP: {filename} not found (run generate_data.py first)")
        return 0

    with open(filepath) as f:
        records = json.load(f)

    actions = []
    for record in records:
        action = {
            "_index": index_name,
            "_id": record.get(id_field),
            "_source": record
        }
        actions.append(action)

    success, errors = bulk(es, actions, raise_on_error=False)
    if errors:
        print(f"  WARNING: {len(errors)} errors loading {filename}")
        for err in errors[:3]:
            print(f"    {err}")
    print(f"  Loaded {success} documents into {index_name}")
    return success


print("\nLoading data into Elasticsearch...")
total = 0
total += load_file("suppliers.json", "sc_suppliers", "supplier_id")
total += load_file("products.json", "sc_products", "product_id")
total += load_file("shipments.json", "sc_shipments", "shipment_id")
total += load_file("orders.json", "sc_orders", "order_id")
total += load_file("news.json", "sc_news", "article_id")

print(f"\nTotal documents loaded: {total}")

# Verify counts
print("\nVerifying index counts...")
indices = ["sc_shipments", "sc_suppliers", "sc_news", "sc_orders", "sc_products"]
for index in indices:
    try:
        result = es.count(index=index)
        print(f"  {index}: {result['count']} documents")
    except Exception as e:
        print(f"  {index}: ERROR - {e}")

print("\nDone. Next: python scripts/create_tools.py")
