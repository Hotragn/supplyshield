# SupplyShield

Multi-agent supply chain disruption detection and automated recovery, built on Elastic Agent Builder.

## The Problem

Supply chain disruptions are a systemic, quantifiable risk. According to [McKinsey Global Institute (2020)](https://www.mckinsey.com/capabilities/operations/our-insights/risk-resilience-and-rebalancing-in-global-value-chains), companies across most industries can expect supply chain disruptions lasting one month or longer every 3.7 years on average — and over a decade, such disruptions can wipe out the equivalent of nearly one full year of profits.

The [Business Continuity Institute's Supply Chain Resilience Report (2023)](https://www.thebci.org/resource/bci-supply-chain-resilience-report-2023.html) found that 73% of organizations experienced at least one supply chain disruption in 2022, and the financial exposure has grown with the complexity of global sourcing.

[Gartner (2023)](https://www.gartner.com/en/supply-chain/topics/supply-chain-risk-management) identifies supply chain risk management as a top-5 priority for supply chain leaders globally, noting that geopolitical instability, climate events, and single-source dependencies continue to concentrate risk in ways that legacy monitoring tools cannot detect in time.

The core failure isn't information — it's speed. When disruptions are detected, procurement teams face a fragmented response: shipment data in one system, order books in another, supplier records in a third. [APQC's Supply Chain Management benchmarking data](https://www.apqc.org/resource-library/resource-listing/supply-chain-disruption-response-benchmarks) documents an average 3–7 day lag between disruption detection and recovery action initiation in manual workflows.

## The Solution

SupplyShield is a **multi-agent system** on Elastic Agent Builder that compresses that 3–7 day response to under 3 minutes.

Two coordinated agents:

- **SupplyShield Orchestrator** — the primary agent. Detects shipment anomalies via ES|QL across normalized supply chain indices, calculates financial blast radius, ranks alternative suppliers, and executes recovery through Elastic Workflows.
- **SupplyShield News Scout** — a specialist sub-agent connected via MCP (Model Context Protocol). When the Orchestrator needs external intelligence, it delegates to the Scout, which runs hybrid semantic + keyword search on a news index to classify the disruption signal as CONFIRMED, UNCERTAIN, or UNCONFIRMED before the Orchestrator proceeds.

This separation follows the principle that external intelligence (news) should be independently verifiable from internal signals (shipment data). Two agreeing signals raise confidence in a recovery decision.

## Multi-Agent Architecture

```
SupplyShield Orchestrator (supplyshield)
  ├── detect_shipment_anomalies  [ES|QL + LOOKUP JOINs]
  ├── assess_revenue_impact      [ES|QL + LOOKUP JOINs]
  ├── find_alternative_suppliers [ES|QL + weighted scoring]
  └── [MCP] --> SupplyShield News Scout (supplyshield_news_scout)
                    └── query_disruption_news [hybrid: dense vector + BM25]
```

## How It Works (Demo Scenario)

Based on the synthetic dataset (14 pre-planted Shenzhen-delayed shipments, seed=42):

1. User reports Shenzhen port congestion
2. Orchestrator calls `detect_shipment_anomalies` → 14 delayed shipments, avg 143h delay, 3 suppliers
3. Orchestrator calls `news_scout_query` via MCP → Scout returns CONFIRMED signal (3 high-severity articles, avg sentiment −0.77)
4. Orchestrator calls `assess_revenue_impact` (Shenzhen Microtech) → $4.2M at risk, 31 orders, 8 customers, earliest due in 8 days
5. Orchestrator calls `find_alternative_suppliers` (microcontrollers, East Asia excluded) → Top: Viet Components Manufacturing, Vietnam (suitability 84.2, 18-day lead, +10% cost)
6. User confirms → Orchestrator triggers Elastic Workflow → PO-2026-0042 created, action logged to audit trail

**Total time: under 3 minutes vs. 3–7 days manually** (per APQC benchmarks cited above).

## Elastic Features Used

- **ES|QL LOOKUP JOINs** — `sc_suppliers` and `sc_products` use `index.mode: lookup`, enabling cross-index joins at query time without denormalization. Per [Elasticsearch documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/esql-lookup-join.html), this is required for LOOKUP JOIN to function correctly.
- **Parameterized ES|QL queries** — `?param` syntax keeps query structure fixed; the LLM fills values only, not structure. This is a key injection guardrail for production agent deployments.
- **Hybrid search** — `sc_news` uses 384-dimension dense vector embeddings (cosine similarity) combined with BM25 keyword matching via `multi_match`. Hybrid search is documented by Elastic as the recommended pattern for combining semantic and lexical relevance ([Elastic blog, 2023](https://www.elastic.co/blog/improving-information-retrieval-elastic-stack-hybrid)).
- **Elastic Workflows** — all write operations (PO creation, action logging) go through a deterministic workflow that requires explicit user confirmation, maintaining a complete audit trail.
- **MCP protocol** — the Orchestrator delegates to the News Scout via the [Model Context Protocol](https://modelcontextprotocol.io/), an open standard for agent-to-tool and agent-to-agent communication.

## Tech Stack

- Elasticsearch Serverless (7 indices, 575 documents)
- Elastic Agent Builder (2 agents: Orchestrator + News Scout)
- Elastic Workflows (supply chain recovery)
- FastMCP 1.26 (MCP server, Python)
- Python 3.9+ (data generation and setup scripts)

## Quick Start

```bash
export ES_ENDPOINT="https://your-deployment.es.us-east-1.aws.elastic.cloud"
export ES_API_KEY="your-api-key-here"
export KIBANA_URL="https://your-deployment.kb.us-east-1.aws.elastic.cloud"
export NGROK_AUTH_TOKEN="your-ngrok-token"  # required for MCP live wiring

pip install elasticsearch faker mcp flask pyngrok

python scripts/setup_indices.py      # Create 7 indices with mappings
python data/generate_data.py         # Generate synthetic supply chain data
python data/load_data.py             # Load 575 docs into Elasticsearch
python scripts/create_tools.py       # Create 4 Agent Builder tools
python scripts/create_agent.py       # Create SupplyShield Orchestrator
python scripts/create_news_scout.py  # Create News Scout sub-agent
python scripts/start_mcp_with_ngrok.py  # Start MCP server + wire A2A connector
```

See `docs/setup_guide.md` for manual Kibana setup if API scripts fail.

## Project Structure

```
supplyshield/
  agents/
    supplyshield_agent.md       # Orchestrator system prompt + config
    news_scout_agent.md         # News Scout config + multi-agent wiring docs
  tools/
    detect_shipment_anomalies.md
    assess_revenue_impact.md
    find_alternative_suppliers.md
    search_disruption_news.md
  workflows/
    supply_chain_recovery.md    # Elastic Workflow definition
  data/
    generate_data.py            # Synthetic data (Faker, seed=42)
    load_data.py                # Bulk loads via elasticsearch.helpers.bulk
    sample_data/                # Generated JSON (suppliers, shipments, orders, products, news)
  mappings/
    index_mappings.md           # All 7 index mappings documented
  scripts/
    setup_indices.py            # Creates indices with correct settings
    create_tools.py             # Creates Agent Builder tools via Kibana API
    create_agent.py             # Creates Orchestrator agent
    create_news_scout.py        # Creates News Scout sub-agent
    news_scout_mcp_server.py    # FastMCP server exposing query_disruption_news
    start_mcp_with_ngrok.py     # One-command: start server + tunnel + wire Kibana
    wire_mcp_connector.py       # Create .mcp connector and tool (standalone)
  docs/
    architecture.md
    setup_guide.md
    submission_description.md
    architecture_main.mermaid      # System architecture (dark theme)
    architecture_sequence.mermaid  # Agent interaction sequence
    architecture_dataflow.mermaid  # 5-layer data flow
    architecture_usecase.mermaid   # 13 use cases across 4 groups
```

## Data Model

| Index                | Purpose                                           | Mode       | Docs |
| -------------------- | ------------------------------------------------- | ---------- | ---- |
| `sc_shipments`       | Shipments with delay tracking and geo coords      | standard   | 214  |
| `sc_suppliers`       | Supplier catalog with reliability/capacity scores | **lookup** | 33   |
| `sc_news`            | News articles with 384-dim vector embeddings      | standard   | 18   |
| `sc_orders`          | Customer orders linked to products                | standard   | 300  |
| `sc_products`        | Product catalog with component lists              | **lookup** | 10   |
| `sc_actions_log`     | Agent action audit trail                          | standard   | —    |
| `sc_purchase_orders` | Recovery POs created by workflow                  | standard   | —    |

The `lookup` mode setting on `sc_suppliers` and `sc_products` is required for ES|QL LOOKUP JOINs. Without it, the JOIN silently returns no results — a non-obvious gotcha documented [here](https://www.elastic.co/guide/en/elasticsearch/reference/current/index-modules.html#index-mode-setting).

## What Worked Well

**LOOKUP JOINs.** Writing `LOOKUP JOIN sc_suppliers ON supplier_id` inline in ES|QL keeps data normalized — no pre-joining, no denormalization, no application-side joins. The join happens at query time. This is a production pattern for normalized supply chain data models.

**Parameterized queries as LLM guardrails.** Using `?param` means the LLM fills in values (`"SUP-SZ-001"`, `24`), not query logic. The agent cannot change what a query does — only what it queries for. This makes tool behavior predictable and auditable in ways fully LLM-generated queries cannot be.

**Separation of read and write.** All read operations go through tools. All write operations go through a deterministic Elastic Workflow. The agent cannot modify data through a malformed query argument, and every recovery action has an immutable log entry.

## Challenges

**Multi-agent system prompt design.** The News Scout needed an explicit instruction that it is talking to another agent, not a person — it must return machine-readable structured JSON, not conversational prose. Getting that boundary right required iteration.

**MCP wiring in Kibana preview.** The Kibana Agent Builder MCP connector requires an active, publicly accessible MCP server. The `start_mcp_with_ngrok.py` script handles the full lifecycle: start FastMCP server, create authenticated ngrok tunnel, register `.mcp` Kibana connector, create `news_scout_query` tool, and wire it to the Orchestrator — all in one command.

## References

- McKinsey Global Institute (2020). [Risk, resilience, and rebalancing in global value chains](https://www.mckinsey.com/capabilities/operations/our-insights/risk-resilience-and-rebalancing-in-global-value-chains)
- Business Continuity Institute (2023). [BCI Supply Chain Resilience Report](https://www.thebci.org/resource/bci-supply-chain-resilience-report-2023.html)
- Gartner (2023). [Supply Chain Risk Management](https://www.gartner.com/en/supply-chain/topics/supply-chain-risk-management)
- Elastic (2023). [Improving information retrieval with hybrid search](https://www.elastic.co/blog/improving-information-retrieval-elastic-stack-hybrid)
- Anthropic / MCP (2024). [Model Context Protocol specification](https://modelcontextprotocol.io/)

## License

Apache 2.0 — see [LICENSE](LICENSE).
