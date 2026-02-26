# SupplyShield

Supply chain disruption detection and automated recovery, built on Elastic Agent Builder.

## What This Is

Supply chain disruptions are expensive. We're talking roughly $4.4 trillion in lost value globally per year, and that number keeps climbing as geopolitical instability, climate events, and capacity crunches stack up. The real problem isn't that companies don't know disruptions happen - it's that the response is painfully slow. Someone spots an issue, loops in procurement, emails 6 people, schedules a meeting, and 3 to 7 days later you have a recovery plan. Meanwhile orders are slipping and customers are getting antsy.

SupplyShield is a multi-step agent built on Elastic Agent Builder that compresses that response time to minutes. It detects disruptions, calculates the financial blast radius across your order book, ranks alternative suppliers, and executes recovery actions through Elastic Workflows - all in one conversation.

## How It Works

The agent orchestrates 4 tools in sequence:

1. **detect_shipment_anomalies** - ES|QL query that finds delayed shipments, groups them by supplier and port using LOOKUP JOINs across `sc_shipments`, `sc_suppliers`, and `sc_products`. You ask about a disruption, it tells you exactly which shipments are affected and for how long.

2. **assess_revenue_impact** - Calculates the financial blast radius. Joins `sc_orders` to `sc_products` to `sc_suppliers` to figure out total revenue at risk, affected customers, and earliest due dates. Gives you actual dollar figures, not hand-wavy estimates.

3. **find_alternative_suppliers** - Ranks replacement suppliers using a weighted score: reliability (40%), capacity (30%), and lead time (30%). Excludes the disrupted supplier and optionally the disrupted region. Returns the top 5 with estimated cost premium.

4. **search_disruption_news** - Hybrid semantic and keyword search across `sc_news` to corroborate what you're seeing in shipment data. Useful for confirming whether port congestion is local or part of a broader regional issue.

5. **execute_recovery_workflow** - Elastic Workflow that creates a purchase order in `sc_purchase_orders` and logs the action to `sc_actions_log`. The agent always asks for confirmation before triggering this.

## Elastic Features Used

- **ES|QL LOOKUP JOINs** across 6 indices for cross-index correlation without denormalization. `sc_suppliers` and `sc_products` are configured with `index.mode: lookup` which is required for LOOKUP JOIN to work.
- **Parameterized queries** using `?param` syntax - the LLM fills in parameter values, but the query structure is fixed. This prevents injection and makes tool behavior predictable.
- **Hybrid search** on `sc_news` using dense vector embeddings (384 dims, cosine) combined with keyword matching on title and body.
- **Elastic Workflows** for write operations - keeps the agent on the read side of data and uses a structured workflow for any state changes.

## Tech Stack

- Elasticsearch Serverless
- Elastic Agent Builder
- Elastic Workflows
- Python (data generation and setup scripts)

## Quick Start

You need Python 3.9+ and valid Elasticsearch Serverless credentials.

```bash
# Set credentials
export ES_ENDPOINT="https://your-deployment.es.us-east-1.aws.elastic.cloud"
export ES_API_KEY="your-api-key-here"
export KIBANA_URL="https://your-deployment.kb.us-east-1.aws.elastic.cloud"

# Install dependencies
pip install elasticsearch faker

# Run setup
python scripts/setup_indices.py    # Create indices with correct mappings
python data/generate_data.py       # Generate synthetic supply chain data
python data/load_data.py           # Load data into Elasticsearch
python scripts/create_tools.py     # Create Agent Builder tools via API
python scripts/create_agent.py     # Create the SupplyShield agent via API
```

If the API scripts fail (Agent Builder API endpoints are in preview), the setup guide covers creating tools and the agent manually in Kibana. It takes about 10 minutes.

## Project Structure

```
supplyshield/
  agents/
    supplyshield_agent.md       # Agent configuration and system prompt
  tools/
    detect_shipment_anomalies.md
    assess_revenue_impact.md
    find_alternative_suppliers.md
    search_disruption_news.md
  workflows/
    supply_chain_recovery.md    # Elastic Workflow YAML
  data/
    generate_data.py            # Generates synthetic data (seed 42)
    load_data.py                # Bulk loads to ES
    sample_data/                # Generated JSON files
  mappings/
    index_mappings.md           # All 7 index mappings documented
  scripts/
    setup_indices.py            # Creates indices with correct settings
    create_tools.py             # Creates tools via Kibana API
    create_agent.py             # Creates agent via Kibana API
  docs/
    setup_guide.md
    architecture.md
    demo_script.md
    submission_description.md
```

## Data Model

Six read indices plus one written by the workflow:

| Index                | Purpose                                                 | Mode       |
| -------------------- | ------------------------------------------------------- | ---------- |
| `sc_shipments`       | Individual shipments with delay tracking and geo coords | standard   |
| `sc_suppliers`       | Supplier catalog with reliability/capacity scores       | **lookup** |
| `sc_news`            | News articles with 384-dim vector embeddings            | standard   |
| `sc_orders`          | Customer orders linked to products                      | standard   |
| `sc_products`        | Product catalog with component lists                    | **lookup** |
| `sc_actions_log`     | Audit trail of agent actions                            | standard   |
| `sc_purchase_orders` | Created by recovery workflow                            | standard   |

The `lookup` mode is critical. Without it, ES|QL LOOKUP JOINs silently fail.

## Demo Scenario

Here's what a real conversation looks like:

> **User:** We're hearing about congestion at Shenzhen port. Can you check if we have affected shipments?

The agent runs `detect_shipment_anomalies` with a 336-hour window and finds 14 shipments delayed 48-336 hours from Shenzhen port, affecting 3 suppliers and 4 component types.

> **Agent:** Found 14 delayed shipments out of Shenzhen. Want me to calculate the revenue impact?

After `assess_revenue_impact`: $2.3M in orders at risk across 23 active orders and 11 customer accounts, earliest due date in 8 days.

After `find_alternative_suppliers`: Top alternative is Viet Components Manufacturing in Ho Chi Minh - suitability score 87.4, 18-day lead time, ~8% cost premium. Two other Vietnam/Malaysia options also viable.

After `search_disruption_news`: 3 corroborating articles about Shenzhen port congestion and trucking shortages from the past week.

> **User:** Go ahead and create a purchase order with Viet Components Manufacturing for the SmartWatch Pro components.

Agent confirms the action, runs `execute_recovery_workflow`, and logs the PO to `sc_purchase_orders`.

Total time: about 3 minutes. Previously: 3-7 days.

## What I Liked Building

**LOOKUP JOINs are genuinely useful.** Being able to write `LOOKUP JOIN sc_suppliers ON supplier_id` inline in an ES|QL query without pre-joining or denormalizing the data is a real productivity win. You keep your indices clean and normalized, and the join happens at query time. The requirement for `lookup` mode in the index settings is a bit of a gotcha (it's not obvious from the docs), but once you know it, it's straightforward.

**Parameterized queries as LLM guardrails.** Using `?param` in ES|QL queries that the LLM fills in means the agent can customize queries without having write access to the query structure itself. The LLM provides values, not SQL. I used this for time windows, supplier IDs, and capability wildcards.

**Workflows for write operations.** Separating read (tools) from write (workflows) means the agent can't accidentally modify data through a poorly-formed query. The workflow is deterministic and auditable.

## Challenges

Getting the agent to reliably select the right tool in the right order took more prompt engineering than I expected. The tool descriptions matter a lot - being explicit about when NOT to use a tool helped as much as being clear about when to use it.

The Elasticsearch Serverless trial timing was also tight. Starting the trial too early means it might expire before the deadline; starting too late means less time to test.

## License

Apache 2.0 - see [LICENSE](LICENSE).
