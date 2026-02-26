"""
setup_indices.py - Creates all SupplyShield indices with correct mappings.

Run this before generate_data.py and load_data.py.
Requires: ES_ENDPOINT and ES_API_KEY environment variables.
"""

import os
import sys
from elasticsearch import Elasticsearch

ES_ENDPOINT = os.environ.get("ES_ENDPOINT")
ES_API_KEY = os.environ.get("ES_API_KEY")

if not ES_ENDPOINT or not ES_API_KEY:
    print("ERROR: ES_ENDPOINT and ES_API_KEY environment variables must be set.")
    sys.exit(1)

es = Elasticsearch(ES_ENDPOINT, api_key=ES_API_KEY)

# Test connection
try:
    info = es.info()
    print(f"Connected to Elasticsearch: {info['cluster_name']}")
except Exception as e:
    print(f"ERROR: Could not connect to Elasticsearch: {e}")
    sys.exit(1)

INDICES = {
    "sc_shipments": {
        "mappings": {
            "properties": {
                "shipment_id":          {"type": "keyword"},
                "supplier_id":          {"type": "keyword"},
                "product_id":           {"type": "keyword"},
                "status":               {"type": "keyword"},
                "origin_port":          {"type": "keyword"},
                "destination_port":     {"type": "keyword"},
                "origin_location":      {"type": "geo_point"},
                "destination_location": {"type": "geo_point"},
                "delay_hours":          {"type": "float"},
                "quantity":             {"type": "integer"},
                "@timestamp":           {"type": "date"},
                "estimated_arrival":    {"type": "date"},
                "actual_arrival":       {"type": "date"}
            }
        }
    },
    "sc_suppliers": {
        "settings": {
            "index": {
                "mode": "lookup"
            }
        },
        "mappings": {
            "properties": {
                "supplier_id":       {"type": "keyword"},
                "supplier_name":     {"type": "keyword"},
                "region":            {"type": "keyword"},
                "country":           {"type": "keyword"},
                "origin_port":       {"type": "keyword"},
                "capabilities":      {"type": "keyword"},
                "reliability_score": {"type": "float"},
                "capacity_score":    {"type": "float"},
                "lead_time_days":    {"type": "integer"},
                "active":            {"type": "boolean"},
                "location":          {"type": "geo_point"}
            }
        }
    },
    "sc_news": {
        "mappings": {
            "properties": {
                "article_id":     {"type": "keyword"},
                "title":          {"type": "text"},
                "body":           {"type": "text"},
                "body_embedding": {
                    "type": "dense_vector",
                    "dims": 384,
                    "index": True,
                    "similarity": "cosine"
                },
                "regions":         {"type": "keyword"},
                "disruption_type": {"type": "keyword"},
                "severity":        {"type": "keyword"},
                "sentiment_score": {"type": "float"},
                "published_date":  {"type": "date"}
            }
        }
    },
    "sc_orders": {
        "mappings": {
            "properties": {
                "order_id":      {"type": "keyword"},
                "customer_id":   {"type": "keyword"},
                "customer_name": {"type": "keyword"},
                "product_id":    {"type": "keyword"},
                "status":        {"type": "keyword"},
                "priority":      {"type": "keyword"},
                "revenue_value": {"type": "float"},
                "quantity":      {"type": "integer"},
                "required_date": {"type": "date"},
                "@timestamp":    {"type": "date"}
            }
        }
    },
    "sc_products": {
        "settings": {
            "index": {
                "mode": "lookup"
            }
        },
        "mappings": {
            "properties": {
                "product_id":          {"type": "keyword"},
                "product_name":        {"type": "keyword"},
                "category":            {"type": "keyword"},
                "components":          {"type": "keyword"},
                "primary_supplier_id": {"type": "keyword"},
                "backup_supplier_ids": {"type": "keyword"}
            }
        }
    },
    "sc_actions_log": {
        "mappings": {
            "properties": {
                "action_id":   {"type": "keyword"},
                "action_type": {"type": "keyword"},
                "agent_name":  {"type": "keyword"},
                "details":     {"type": "text"},
                "timestamp":   {"type": "date"}
            }
        }
    },
    "sc_purchase_orders": {
        "mappings": {
            "properties": {
                "po_id":       {"type": "keyword"},
                "supplier_id": {"type": "keyword"},
                "product_ids": {"type": "keyword"},
                "quantity":    {"type": "integer"},
                "status":      {"type": "keyword"},
                "reason":      {"type": "text"},
                "created_at":  {"type": "date"},
                "created_by":  {"type": "keyword"}
            }
        }
    }
}


def create_index(name, body):
    # Delete if exists
    if es.indices.exists(index=name):
        es.indices.delete(index=name)
        print(f"  Deleted existing index: {name}")

    es.indices.create(index=name, body=body)
    print(f"  Created index: {name}")


print("\nCreating SupplyShield indices...")
for index_name, index_body in INDICES.items():
    try:
        create_index(index_name, index_body)
    except Exception as e:
        print(f"  ERROR creating {index_name}: {e}")
        sys.exit(1)

print(f"\nDone. Created {len(INDICES)} indices.")
print("Next: python data/generate_data.py")
