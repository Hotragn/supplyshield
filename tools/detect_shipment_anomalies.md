# Tool: detect_shipment_anomalies

## Tool Details

- **Tool ID:** detect_shipment_anomalies
- **Type:** esql
- **Labels:** supply-chain, detection, shipments, anomaly
- **Description:**

Finds delayed shipments by joining shipment data with supplier and product information. Use this tool when a user reports a disruption at a specific port, region, or from a specific supplier, and wants to know which shipments are affected. Also use it when you want a baseline count of delayed shipments in the current window.

Do NOT use this tool if the user is asking about financial impact, customer orders, or revenue - use assess_revenue_impact for that. Do NOT use this tool to find alternative suppliers - use find_alternative_suppliers for that.

## ES|QL Query

```esql
FROM sc_shipments
| WHERE @timestamp > NOW() - ?time_window::DURATION
  AND delay_hours > ?delay_threshold
| LOOKUP JOIN sc_suppliers ON supplier_id
| LOOKUP JOIN sc_products ON product_id
| STATS
    affected_shipments = COUNT(*),
    avg_delay_hours = AVG(delay_hours),
    max_delay_hours = MAX(delay_hours),
    distinct_components = COUNT_DISTINCT(product_id)
  BY supplier_id, supplier_name, region, country, origin_port
| SORT affected_shipments DESC
| LIMIT 20
```

## Parameters

| Parameter         | Type    | Default     | Required | Description                                                                                                                         |
| ----------------- | ------- | ----------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `time_window`     | keyword | `336 hours` | No       | Lookback window for shipment detection. Use ES duration format, e.g. "336 hours", "168 hours", "720 hours".                         |
| `delay_threshold` | integer | `24`        | No       | Minimum delay in hours to flag a shipment as anomalous. Lower values catch more shipments; raise it to focus on severe delays only. |

## Example Usage

- User says "check shipments from Shenzhen" => time_window: "336 hours", delay_threshold: 24
- User says "only critical delays" => time_window: "168 hours", delay_threshold: 72
- User says "check the past month" => time_window: "720 hours", delay_threshold: 24

## Expected Output Fields

- `supplier_id`, `supplier_name`, `region`, `country`, `origin_port`
- `affected_shipments` - count of delayed shipments from this supplier/port group
- `avg_delay_hours` - average delay across the group
- `max_delay_hours` - worst single shipment delay
- `distinct_components` - number of distinct product types affected

Results are sorted by `affected_shipments` descending so the worst-hit suppliers appear first.
