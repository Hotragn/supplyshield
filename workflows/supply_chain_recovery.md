# Elastic Workflow: supply_chain_recovery

## Workflow Definition

```yaml
id: supply_chain_recovery
name: Supply Chain Recovery
description: Creates a purchase order with a replacement supplier and logs the recovery action to the audit trail.
version: "1.0"

inputs:
  new_supplier_id:
    type: string
    description: Supplier ID of the replacement supplier
    required: true
  product_ids:
    type: array
    items:
      type: string
    description: List of product IDs to source from the new supplier
    required: true
  total_quantity:
    type: integer
    description: Total units to order across all product IDs
    required: true
  reason:
    type: string
    description: Human-readable reason for the recovery action, e.g. "Shenzhen port congestion - 14 delayed shipments"
    required: true

steps:
  - id: create_purchase_order
    name: Create Purchase Order
    action: elasticsearch.index
    parameters:
      index: sc_purchase_orders
      document:
        po_id: "PO-{{ now() | date('yyyyMMddHHmmss') }}"
        supplier_id: "{{ inputs.new_supplier_id }}"
        product_ids: "{{ inputs.product_ids }}"
        quantity: "{{ inputs.total_quantity }}"
        status: "pending"
        reason: "{{ inputs.reason }}"
        created_at: "{{ now() }}"
        created_by: "supplyshield-agent"

  - id: log_recovery_action
    name: Log Recovery Action
    action: elasticsearch.index
    parameters:
      index: sc_actions_log
      document:
        action_id: "ACT-{{ now() | date('yyyyMMddHHmmss') }}"
        action_type: "purchase_order_created"
        agent_name: "supplyshield"
        details: "Created PO {{ steps.create_purchase_order.result._id }} with supplier {{ inputs.new_supplier_id }} for {{ inputs.product_ids | length }} product(s). Reason: {{ inputs.reason }}"
        timestamp: "{{ now() }}"

outputs:
  po_id: "{{ steps.create_purchase_order.result._id }}"
  message: "Recovery action completed. Purchase order created with {{ inputs.new_supplier_id }} for {{ inputs.total_quantity }} units. Action logged."
```

## Notes

- `po_id` uses a timestamp-based suffix to avoid collisions. In production you'd want a UUID or sequence.
- `created_by` is hardcoded to `supplyshield-agent` for auditing purposes. The agent should always pass `reason` as a human-readable explanation so the log is meaningful to a human auditor.
- Both documents are indexed with their natural ID fields. The Elasticsearch `_id` from the `create_purchase_order` step is referenced in the log entry.
- The workflow does not delete or modify any existing records. It only writes to `sc_purchase_orders` and `sc_actions_log`.
