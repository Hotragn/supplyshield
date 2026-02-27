# SupplyShield: Multi-Agent Supply Chain Disruption Detection on Elastic

Supply chain disruption detection and automated recovery, built on Elastic Agent Builder — using a **multi-agent architecture** with a specialist News Scout sub-agent.

## What This Is

Supply chain disruptions cost roughly $4.4 trillion globally per year. The real problem isn't that companies don't know disruptions happen — it's that the response is painfully slow. Someone spots an issue, loops in procurement, emails 6 people, schedules a meeting, and 3 to 7 days later you have a recovery plan. Meanwhile orders are slipping.

SupplyShield compresses that response time to minutes using two coordinated agents:

- **SupplyShield Orchestrator** — the main agent. Detects disruptions, calculates financial impact, sources alternatives, and executes recovery through Elastic Workflows.
- **SupplyShield News Scout** — a specialist sub-agent focused purely on external intelligence. The Orchestrator delegates corroboration to the Scout via MCP. The Scout queries `sc_news`, classifies signal strength (CONFIRMED / UNCERTAIN / UNCONFIRMED), and returns structured results the Orchestrator synthesizes for the user.

## Multi-Agent Architecture

```
SupplyShield Orchestrator (supplyshield)
  ├── detect_shipment_anomalies  [ES|QL + LOOKUP JOINs]
  ├── assess_revenue_impact      [ES|QL + LOOKUP JOINs]
  ├── find_alternative_suppliers [ES|QL + weighted scoring]
  └── [MCP] --> SupplyShield News Scout (supplyshield_news_scout)
                    └── search_disruption_news [hybrid: vector + keyword]
```

Each agent has a distinct role, its own system prompt, and operates independently. The Orchestrator never searches news directly — it always delegates that to the Scout and waits for a classified signal before proceeding with assessment.

## How It Works

A typical session:

1. **User reports a disruption** → Orchestrator calls `detect_shipment_anomalies` (ES|QL LOOKUP JOIN across shipments, suppliers, products)
2. **Orchestrator delegates to News Scout** → Scout runs hybrid search on `sc_news`, returns: article count, severity, sentiment score, signal classification
3. **Orchestrator assesses impact** → calls `assess_revenue_impact` with the affected supplier_id
4. **Orchestrator sources alternatives** → calls `find_alternative_suppliers` with capability filter, region exclusion, weighted suitability score
5. **User approves** → Orchestrator triggers `execute_recovery_workflow` via Elastic Workflow → PO created + action logged

Total time: ~3 minutes vs 3–7 days.

## Elastic Features Used

- **ES|QL LOOKUP JOINs** — `sc_suppliers` and `sc_products` use `index.mode: lookup`, enabling cross-index joins at query time without denormalization
- **Parameterized queries** — `?param` syntax keeps query structure fixed; the LLM fills in values only, not structure (injection guardrail)
- **Hybrid search** — `sc_news` uses 384-dim dense vector embeddings (cosine) + keyword matching for semantic + lexical corroboration
- **Elastic Workflows** — separates read from write; every recovery action is auditable; requires explicit user confirmation
- **MCP protocol** — Orchestrator-to-Scout communication follows the Model Context Protocol pattern for agent specialization

## Tech Stack

- Elasticsearch Serverless
- Elastic Agent Builder (2 agents)
- Elastic Workflows
- Python (data generation and setup scripts)

## Quick Start

```bash
export ES_ENDPOINT="https://your-deployment.es.us-east-1.aws.elastic.cloud"
export ES_API_KEY="your-api-key-here"
export KIBANA_URL="https://your-deployment.kb.us-east-1.aws.elastic.cloud"

pip install elasticsearch faker

python scripts/setup_indices.py      # Create 7 indices with correct mappings
python data/generate_data.py         # Generate synthetic supply chain data
python data/load_data.py             # Load 575 docs into Elasticsearch
python scripts/create_tools.py       # Create 4 Agent Builder tools via API
python scripts/create_agent.py       # Create SupplyShield Orchestrator
python scripts/create_news_scout.py  # Create News Scout sub-agent
```

See `docs/setup_guide.md` for manual Kibana setup if API scripts fail.

## Project Structure

```
supplyshield/
  agents/
    supplyshield_agent.md       # Orchestrator configuration and system prompt
    news_scout_agent.md         # News Scout configuration and multi-agent wiring
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
    setup_indices.py            # Creates indices
    create_tools.py             # Creates tools via Kibana API
    create_agent.py             # Creates Orchestrator agent
    create_news_scout.py        # Creates News Scout sub-agent
  docs/
    setup_guide.md
    architecture.md
    submission_description.md
    architecture_main.mermaid
    architecture_sequence.mermaid
    architecture_dataflow.mermaid
    architecture_usecase.mermaid
```

## Data Model

| Index                | Purpose                                           | Mode       |
| -------------------- | ------------------------------------------------- | ---------- |
| `sc_shipments`       | Shipments with delay tracking and geo coords      | standard   |
| `sc_suppliers`       | Supplier catalog with reliability/capacity scores | **lookup** |
| `sc_news`            | News articles with 384-dim vector embeddings      | standard   |
| `sc_orders`          | Customer orders linked to products                | standard   |
| `sc_products`        | Product catalog with component lists              | **lookup** |
| `sc_actions_log`     | Audit trail of agent actions                      | standard   |
| `sc_purchase_orders` | Created by recovery workflow                      | standard   |

The `lookup` mode is required for ES|QL LOOKUP JOINs to work.

## What I Liked Building

**LOOKUP JOINs are genuinely useful.** Writing `LOOKUP JOIN sc_suppliers ON supplier_id` inline in ES|QL without pre-joining or denormalizing keeps indices clean and normalized with joins at query time.

**Parameterized queries as LLM guardrails.** Using `?param` means the LLM fills in values, not query structure. The agent can customize queries without write access to query logic.

**Workflows for write operations.** Separating read (tools) from write (workflows) means the agent can't accidentally modify data. Every recovery action is deterministic and auditable.

## Challenges

Getting the two-agent system to hand off cleanly required careful system prompt design for both agents. The News Scout needed to be explicitly told to return structured, machine-readable summaries rather than conversational text — it's talking to an agent, not a person.

## License

Apache 2.0 — see [LICENSE](LICENSE).
