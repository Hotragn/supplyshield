# Architecture

SupplyShield is a multi-step agent that orchestrates read (ES|QL tools + search) and write (Elastic Workflow) operations across a normalized supply chain data model. Here's how pieces fit together.

## Data Flow

```
User Message
    |
    v
SupplyShield Agent (Elastic Agent Builder)
    |
    |-- [1] detect_shipment_anomalies
    |       ES|QL: sc_shipments
    |               LOOKUP JOIN sc_suppliers ON supplier_id
    |               LOOKUP JOIN sc_products ON product_id
    |       --> Returns: supplier_id, affected_shipments, avg_delay_hours
    |
    |-- [2] assess_revenue_impact
    |       ES|QL: sc_orders (WHERE status = active)
    |               LOOKUP JOIN sc_products ON product_id (WHERE primary_supplier_id = ?)
    |               LOOKUP JOIN sc_suppliers ON primary_supplier_id
    |       --> Returns: total_revenue_at_risk, affected_orders, earliest_due
    |
    |-- [3] find_alternative_suppliers
    |       ES|QL: sc_suppliers (WHERE active, capabilities LIKE ?, exclude disrupted)
    |               EVAL suitability_score, cost_premium_pct
    |       --> Returns: ranked replacement suppliers
    |
    |-- [4] search_disruption_news
    |       Hybrid Search: sc_news (semantic + keyword on title, body)
    |       --> Returns: corroborating news with sentiment_score, severity
    |
    |-- [5] execute_recovery_workflow (after confirmation)
            Elastic Workflow: supply_chain_recovery
                Step 1: elasticsearch.index -> sc_purchase_orders
                Step 2: elasticsearch.index -> sc_actions_log
            --> Returns: po_id, confirmation message
```

## Index Relationships

```
sc_shipments
  supplier_id ---[LOOKUP JOIN]---> sc_suppliers.supplier_id
  product_id  ---[LOOKUP JOIN]---> sc_products.product_id

sc_orders
  product_id  ---[LOOKUP JOIN]---> sc_products.product_id
  (sc_products.primary_supplier_id ---[LOOKUP JOIN]---> sc_suppliers.supplier_id)

sc_news (standalone, hybrid search)

sc_purchase_orders (written by workflow)
sc_actions_log (written by workflow)
```

## Why LOOKUP JOINs Instead of Denormalization

The data model keeps suppliers, products, shipments, and orders in separate indices. You could denormalize all this into a single fat document per shipment, but there are real costs to that approach:

- **Stale data:** When a supplier's reliability score changes, you'd have to reindex every shipment document. With a lookup index, you update one document.
- **Redundancy:** 214 shipments from 40 suppliers means 214 copies of supplier metadata if you embed it. That's wasted storage and update complexity.
- **LOOKUP JOIN performance:** Lookup-mode indices are optimized for exactly this use case. They're loaded into node memory for fast hash-join operations at query time.

The trade-off is that you need `index.mode: lookup` set correctly, and the join field names must match exactly. That's a one-time setup cost.

## Why Parameterized Queries as Guardrails

All ES|QL tools use the `?param` syntax for LLM-controlled inputs:

```esql
FROM sc_shipments
| WHERE @timestamp > NOW() - ?time_window::DURATION
  AND delay_hours > ?delay_threshold
```

The LLM fills in `time_window` and `delay_threshold` based on what the user asks. The query structure is fixed in the tool definition. This means:

- The LLM can't accidentally drop a WHERE clause or join to the wrong index
- The query is deterministic and auditable
- You get type safety: `delay_threshold` is defined as `integer`, so the LLM knows not to pass "24 hours"

This is the key architectural difference from letting an LLM generate raw ES|QL. Parameterized queries give you LLM flexibility within a guardrailed structure.

## Why Workflows for Write Operations

The agent's tools are all read-only. The only write operation is the recovery workflow, and it's explicitly separated for good reasons:

- **Auditability:** Every recovery action writes to `sc_actions_log` with agent name, timestamp, and a human-readable description. You have a full audit trail.
- **Confirmation gate:** The agent requires user confirmation before triggering the workflow. This is enforced in the system prompt, but the architectural separation reinforces it - tools can't accidentally write.
- **Idempotency:** The workflow uses timestamp-based IDs, so if it's triggered twice, you get two POs with different IDs rather than a silent duplicate.

## Tool Selection Logic

The agent selects tools based on the tool descriptions in Agent Builder. Key design decisions:

1. Each tool description explicitly says when NOT to use it, not just when to use it
2. Tool names are named after actions, not data sources ("`assess_revenue_impact`" not "`query_orders`")
3. The system prompt enforces an ordered sequence (detect -> assess -> find -> act)
4. Required parameters are marked `required: true` in the schema, so the agent knows to ask if it doesn't have them

## Hybrid Search on News

The `sc_news` index uses `dense_vector` (384 dims, cosine similarity) on the `body` field. In the current implementation, embeddings are placeholder zeros (`[0.0] * 384`) - real semantic search would require running body text through a sentence transformer like `all-MiniLM-L6-v2` before indexing.

In production or with real embeddings, the hybrid search combines:

- **Semantic search** using the vector field (catches paraphrased descriptions)
- **Keyword search** on title and body (exact matches for port names, disruption types)

The final score is a weighted combination of both, so an article about "Pearl River Delta port backup" would match a query for "Shenzhen congestion" via semantic similarity even without exact keyword overlap.
