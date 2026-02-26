# Index Mappings

All index mappings for SupplyShield. The most important note: `sc_suppliers` and `sc_products` MUST use `"mode": "lookup"` in their index settings. Without this, ES|QL LOOKUP JOINs will silently fail with no error message - they'll just return no joined fields.

## sc_shipments

Tracks individual shipments with delay tracking and geo coordinates.

```json
{
  "settings": {
    "index": {
      "number_of_shards": 1,
      "number_of_replicas": 0
    }
  },
  "mappings": {
    "properties": {
      "shipment_id": { "type": "keyword" },
      "supplier_id": { "type": "keyword" },
      "product_id": { "type": "keyword" },
      "status": { "type": "keyword" },
      "origin_port": { "type": "keyword" },
      "destination_port": { "type": "keyword" },
      "origin_location": { "type": "geo_point" },
      "destination_location": { "type": "geo_point" },
      "delay_hours": { "type": "float" },
      "quantity": { "type": "integer" },
      "@timestamp": { "type": "date" },
      "estimated_arrival": { "type": "date" },
      "actual_arrival": { "type": "date" }
    }
  }
}
```

## sc_suppliers

Supplier catalog. **Must use `lookup` mode** for LOOKUP JOIN queries to work.

```json
{
  "settings": {
    "index": {
      "mode": "lookup"
    }
  },
  "mappings": {
    "properties": {
      "supplier_id": { "type": "keyword" },
      "supplier_name": { "type": "keyword" },
      "region": { "type": "keyword" },
      "country": { "type": "keyword" },
      "origin_port": { "type": "keyword" },
      "capabilities": { "type": "keyword" },
      "reliability_score": { "type": "float" },
      "capacity_score": { "type": "float" },
      "lead_time_days": { "type": "integer" },
      "active": { "type": "boolean" },
      "location": { "type": "geo_point" }
    }
  }
}
```

## sc_news

News articles with vector embeddings for semantic search.

```json
{
  "settings": {
    "index": {
      "number_of_shards": 1,
      "number_of_replicas": 0
    }
  },
  "mappings": {
    "properties": {
      "article_id": { "type": "keyword" },
      "title": { "type": "text" },
      "body": { "type": "text" },
      "body_embedding": {
        "type": "dense_vector",
        "dims": 384,
        "index": true,
        "similarity": "cosine"
      },
      "regions": { "type": "keyword" },
      "disruption_type": { "type": "keyword" },
      "severity": { "type": "keyword" },
      "sentiment_score": { "type": "float" },
      "published_date": { "type": "date" }
    }
  }
}
```

Note: `body_embedding` is 384 dimensions with cosine similarity. The current data uses placeholder zeros (`[0.0] * 384`). For real semantic search, you'd run the text through a sentence transformer (e.g., `all-MiniLM-L6-v2`) before indexing.

## sc_orders

Customer orders linked to products. Drives the revenue impact calculation.

```json
{
  "settings": {
    "index": {
      "number_of_shards": 1,
      "number_of_replicas": 0
    }
  },
  "mappings": {
    "properties": {
      "order_id": { "type": "keyword" },
      "customer_id": { "type": "keyword" },
      "customer_name": { "type": "keyword" },
      "product_id": { "type": "keyword" },
      "status": { "type": "keyword" },
      "priority": { "type": "keyword" },
      "revenue_value": { "type": "float" },
      "quantity": { "type": "integer" },
      "required_date": { "type": "date" },
      "@timestamp": { "type": "date" }
    }
  }
}
```

## sc_products

Product catalog. **Must use `lookup` mode** for LOOKUP JOIN queries to work.

```json
{
  "settings": {
    "index": {
      "mode": "lookup"
    }
  },
  "mappings": {
    "properties": {
      "product_id": { "type": "keyword" },
      "product_name": { "type": "keyword" },
      "category": { "type": "keyword" },
      "components": { "type": "keyword" },
      "primary_supplier_id": { "type": "keyword" },
      "backup_supplier_ids": { "type": "keyword" }
    }
  }
}
```

## sc_actions_log

Audit trail for all agent recovery actions.

```json
{
  "settings": {
    "index": {
      "number_of_shards": 1,
      "number_of_replicas": 0
    }
  },
  "mappings": {
    "properties": {
      "action_id": { "type": "keyword" },
      "action_type": { "type": "keyword" },
      "agent_name": { "type": "keyword" },
      "details": { "type": "text" },
      "timestamp": { "type": "date" }
    }
  }
}
```

## sc_purchase_orders

Written by the Elastic Workflow when the agent triggers recovery.

```json
{
  "settings": {
    "index": {
      "number_of_shards": 1,
      "number_of_replicas": 0
    }
  },
  "mappings": {
    "properties": {
      "po_id": { "type": "keyword" },
      "supplier_id": { "type": "keyword" },
      "product_ids": { "type": "keyword" },
      "quantity": { "type": "integer" },
      "status": { "type": "keyword" },
      "reason": { "type": "text" },
      "created_at": { "type": "date" },
      "created_by": { "type": "keyword" }
    }
  }
}
```
