# Tool: search_disruption_news

## Tool Details

- **Tool ID:** search_disruption_news
- **Type:** search
- **Labels:** supply-chain, news, intelligence, hybrid-search
- **Index:** sc_news
- **Description:**

Searches news articles about supply chain disruptions using hybrid semantic and keyword search. Returns articles with sentiment scores, severity ratings, and disruption type classifications. Use this to corroborate shipment anomalies with external signals, or to get early warning of emerging disruptions before they show up in shipment data.

Use this tool when a user mentions a disruption event by name or location, or when you want to verify whether a detected anomaly is a known event. Also useful for scanning for news about specific regions.

Do NOT use this tool to find supplier data, shipment counts, or financial figures - those come from the ES|QL tools.

## Search Configuration

```json
{
  "tool_id": "search_disruption_news",
  "type": "search",
  "index": "sc_news",
  "search_type": "hybrid",
  "fields": ["title", "body"],
  "vector_field": "body_embedding",
  "return_fields": [
    "title",
    "body",
    "regions",
    "sentiment_score",
    "disruption_type",
    "severity",
    "published_date"
  ],
  "top_k": 5
}
```

## Hybrid Search Behavior

The search combines:

- **Semantic search** on `body_embedding` (384-dim dense vector, cosine similarity) - catches articles that describe the same situation with different terminology
- **Keyword search** on `title` and `body` - ensures exact matches for port names, company names, and disruption types

## Return Fields

| Field             | Type          | Description                                                                |
| ----------------- | ------------- | -------------------------------------------------------------------------- |
| `title`           | text          | Article headline                                                           |
| `body`            | text          | Full article text                                                          |
| `regions`         | keyword array | Affected regions, e.g. ["Southeast Asia", "China"]                         |
| `sentiment_score` | float         | -1.0 (very negative) to 1.0 (positive). Negative scores indicate bad news. |
| `disruption_type` | keyword       | e.g. "port_congestion", "weather", "geopolitical", "labor_action"          |
| `severity`        | keyword       | "low", "medium", "high", "critical"                                        |
| `published_date`  | date          | When the article was published                                             |

## Example Queries

- "Shenzhen port congestion" - finds articles about current Shenzhen situation
- "Taiwan semiconductor shortage" - corroborates chip supply concerns
- "Vietnam factory floods" - identifies regional weather impacts

## Interpreting Results

- Multiple recent articles with `severity: "high"` and `sentiment_score < -0.5` in the same region = credible signal
- Single article with low severity = may not yet be impacting shipments
- Articles older than 7 days about the same disruption = event is ongoing or has lingering effects
