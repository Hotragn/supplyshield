# Tool: find_alternative_suppliers

## Tool Details

- **Tool ID:** find_alternative_suppliers
- **Type:** esql
- **Labels:** supply-chain, sourcing, suppliers, alternatives
- **Description:**

Ranks active alternative suppliers by suitability score for a specific capability requirement. Excludes the disrupted supplier and optionally excludes suppliers in the same region (useful when a regional event has taken out multiple suppliers at once).

Use this tool after you have identified the affected supplier and know what capability you need (e.g., "battery-cells", "microcontrollers*", "display*").

Do NOT use this tool to detect disruptions or calculate revenue impact. Do NOT use it without a required_capability - the results won't be useful without something to filter on.

## ES|QL Query

```esql
FROM sc_suppliers
| WHERE active == true
  AND capabilities LIKE ?required_capability
  AND supplier_id != ?excluded_supplier_id
  AND region != ?excluded_region
| EVAL suitability_score = (reliability_score * 0.4) + (capacity_score * 0.3) + ((100.0 - lead_time_days) * 0.3)
| EVAL cost_premium_pct = CASE(
    lead_time_days <= 14, 5.0,
    lead_time_days <= 21, 10.0,
    lead_time_days <= 30, 15.0,
    20.0
  )
| KEEP supplier_id, supplier_name, region, country, capabilities,
       reliability_score, capacity_score, lead_time_days,
       suitability_score, cost_premium_pct
| SORT suitability_score DESC
| LIMIT 5
```

## Parameters

| Parameter              | Type    | Default | Required | Description                                                                                                                                   |
| ---------------------- | ------- | ------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `required_capability`  | keyword | —       | **Yes**  | Capability filter. Supports wildcards, e.g. "battery-cells", "microcontrollers*", "*display\*". Match the capabilities field in sc_suppliers. |
| `excluded_supplier_id` | keyword | —       | **Yes**  | Supplier ID to exclude (the disrupted supplier).                                                                                              |
| `excluded_region`      | keyword | `""`    | No       | Region to exclude. Pass empty string or omit if you want global options.                                                                      |

## Suitability Score Formula

```
score = (reliability_score × 0.4) + (capacity_score × 0.3) + ((100 - lead_time_days) × 0.3)
```

- `reliability_score`: 0-100, based on historical on-time delivery
- `capacity_score`: 0-100, current available capacity headroom
- Lead time component inverts lead_time_days so lower lead time = higher score

## Cost Premium Estimate

| Lead Time  | Estimated Premium |
| ---------- | ----------------- |
| ≤14 days   | 5%                |
| 15-21 days | 10%               |
| 22-30 days | 15%               |
| >30 days   | 20%               |

These are rough estimates for planning purposes. Actual premiums depend on negotiated pricing.

## Expected Output Fields

- `supplier_id`, `supplier_name`, `region`, `country`
- `capabilities` - list of capabilities this supplier can cover
- `reliability_score`, `capacity_score`, `lead_time_days` - raw scores
- `suitability_score` - weighted composite score (higher is better)
- `cost_premium_pct` - estimated cost increase vs. primary supplier

Present the top 3 to the user with the key tradeoffs highlighted. Let the user decide which one to engage.
