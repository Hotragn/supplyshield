# Tool: assess_revenue_impact

## Tool Details

- **Tool ID:** assess_revenue_impact
- **Type:** esql
- **Labels:** supply-chain, finance, orders, revenue
- **Description:**

Calculates the financial blast radius of a supplier disruption. Given an affected supplier ID, joins active orders to products to determine which orders are at risk, then rolls up total revenue, customer count, and earliest due dates.

Use this tool after detect_shipment_anomalies has identified a specific affected supplier. You need the supplier_id to run this query accurately.

Do NOT use this tool without a specific supplier ID - the query will return misleading aggregate results. Do NOT use this tool to find alternative suppliers; use find_alternative_suppliers for that.

## ES|QL Query

```esql
FROM sc_orders
| WHERE status == "active"
  AND required_date < NOW() + ?planning_horizon::DURATION
| LOOKUP JOIN sc_products ON product_id
| WHERE primary_supplier_id == ?affected_supplier_id
| LOOKUP JOIN sc_suppliers ON primary_supplier_id
| STATS
    total_revenue_at_risk = SUM(revenue_value),
    affected_orders = COUNT(*),
    affected_customers = COUNT_DISTINCT(customer_id),
    earliest_due = MIN(required_date),
    avg_order_value = AVG(revenue_value)
  BY product_id, product_name, supplier_name
| SORT total_revenue_at_risk DESC
```

## Parameters

| Parameter              | Type    | Default   | Required | Description                                                                                         |
| ---------------------- | ------- | --------- | -------- | --------------------------------------------------------------------------------------------------- |
| `planning_horizon`     | keyword | `30 days` | No       | How far ahead to look for due orders. Use ES duration format, e.g. "30 days", "14 days", "60 days". |
| `affected_supplier_id` | keyword | —         | **Yes**  | The supplier_id of the disrupted supplier. Get this from detect_shipment_anomalies results.         |

## Example Usage

- After detection reveals supplier_id "SUP-001" is disrupted: affected_supplier_id: "SUP-001", planning_horizon: "30 days"
- User asks for urgent orders only: planning_horizon: "14 days"

## Expected Output Fields

- `product_id`, `product_name` - which products are affected
- `supplier_name` - the disrupted supplier name
- `total_revenue_at_risk` - sum of revenue_value across matched active orders
- `affected_orders` - count of active orders at risk
- `affected_customers` - number of distinct customer accounts at risk
- `earliest_due` - the most urgent order due date
- `avg_order_value` - average size of at-risk orders

Results are sorted by revenue at risk descending, so you lead with the most financially exposed products.
