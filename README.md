<div align="center">

# 🛡️ SupplyShield

**Multi-agent supply chain disruption detection and automated recovery**  
_Built on Elastic Agent Builder · Hackathon 2026_

[![Elastic](https://img.shields.io/badge/Elastic-Agent_Builder-005571?style=for-the-badge&logo=elastic&logoColor=white)](https://www.elastic.co/agent-builder)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-Model_Context_Protocol-6B46C1?style=for-the-badge&logo=anthropic&logoColor=white)](https://modelcontextprotocol.io)
[![License](https://img.shields.io/badge/License-Apache_2.0-green?style=for-the-badge)](LICENSE)
[![GitHub](https://img.shields.io/badge/Repo-Hotragn/supplyshield-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Hotragn/supplyshield)

</div>

---

## 🚨 The Problem

Supply chain disruptions are accelerating in both frequency and cost:

| Metric                                  | Data                 | Source                                   |
| --------------------------------------- | -------------------- | ---------------------------------------- |
| Annual global cost                      | **$184 billion**     | J.S. Held Global Risk Report, 2025       |
| Orgs disrupted in past year             | **80%** (↑ from 73%) | BCI Supply Chain Resilience Report, 2024 |
| SC leaders facing resilience challenges | **90%**              | McKinsey Global SC Survey, 2024          |
| Orgs adequately prepared                | **only 29%**         | Gartner Future of Supply Chain, 2025     |
| Supply chains that can't respond in 24h | **83%**              | Kinaxis, 2024 (n=1,800)                  |
| **Average manual response time**        | **5 days**           | Kinaxis, 2024                            |

The core failure is speed. Shipment data lives in one system, order books in another, supplier records in a third. Coordinating across them manually takes days that supply chains don't have.

**SupplyShield cuts 5 days to under 3 minutes.**

---

## 💡 The Solution

A **multi-agent system** on Elastic Agent Builder with two coordinated agents:

| Agent                            | Role                                                                                                                         |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| 🤖 **SupplyShield Orchestrator** | Detects anomalies, assesses revenue impact, ranks alternatives, executes recovery                                            |
| 🔭 **News Scout**                | Specialist sub-agent for external intelligence via MCP — classifies disruption signal as CONFIRMED / UNCERTAIN / UNCONFIRMED |

The key principle: internal signals (shipment data) and external signals (news) are independently verified by separate agents before a recovery decision is made.

---

## 🏗️ Architecture

```
SupplyShield Orchestrator  (Kibana Agent Builder)
  ├── detect_shipment_anomalies      [ES|QL + LOOKUP JOINs]
  ├── assess_revenue_impact          [ES|QL + LOOKUP JOINs]
  ├── find_alternative_suppliers     [ES|QL + weighted scoring]
  └── news_scout_query [MCP] ───────► News Scout MCP Server
                                          └── query_disruption_news
                                              └── sc_news  [hybrid: kNN + BM25]
```

---

## ⚡ Tech Stack

<div align="center">

| Layer                | Technology                                                                                                        |
| -------------------- | ----------------------------------------------------------------------------------------------------------------- | ----------------------------------- | ---------------------------------------------------- |
| **Agent Platform**   | ![Elastic](https://img.shields.io/badge/Elastic_Agent_Builder-005571?logo=elastic&logoColor=white)                |
| **Search & Storage** | ![Elasticsearch](https://img.shields.io/badge/Elasticsearch_Serverless-005571?logo=elasticsearch&logoColor=white) |
| **Query Language**   | ![ES                                                                                                              | QL](https://img.shields.io/badge/ES | QL-LOOKUP_JOINs-FEB600?logo=elastic&logoColor=black) |
| **A2A Protocol**     | ![MCP](https://img.shields.io/badge/Model_Context_Protocol-6B46C1?logo=anthropic&logoColor=white)                 |
| **MCP Framework**    | ![FastMCP](https://img.shields.io/badge/FastMCP-1.26-3776AB?logo=python&logoColor=white)                          |
| **Workflow Engine**  | ![Elastic Workflows](https://img.shields.io/badge/Elastic_Workflows-005571?logo=elastic&logoColor=white)          |
| **Language**         | ![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)                            |
| **Tunnel**           | ![ngrok](https://img.shields.io/badge/ngrok-MCP_tunnel-1F1E37?logo=ngrok&logoColor=white)                         |

</div>

---

## 🎬 Demo Flow

Based on synthetic data (14 pre-planted Shenzhen delays, seed=42):

```
User: "Shenzhen port congestion — any affected shipments?"
  │
  ├─ [Tool 1] detect_shipment_anomalies
  │     └─► 14 delayed shipments, avg 143h delay, 3 suppliers
  │
  ├─ [MCP]   news_scout_query → News Scout → sc_news hybrid search
  │     └─► CONFIRMED: 3 high-severity articles, sentiment −0.77
  │
  ├─ [Tool 2] assess_revenue_impact (Shenzhen Microtech)
  │     └─► $4.2M at risk, 31 orders, 8 customers, due in 8 days
  │
  ├─ [Tool 3] find_alternative_suppliers (microcontrollers, excl. East Asia)
  │     └─► #1 Viet Components Vietnam: score 84.2, 18d lead, +10% cost
  │
  └─ [Workflow] supply_chain_recovery (after explicit user confirmation)
        └─► PO-2026-0042 created + immutable audit log entry
```

**Total: < 3 minutes vs. 5-day industry average**

---

## 📊 Data Model

| Index                | Purpose                               | Mode       | Docs |
| -------------------- | ------------------------------------- | ---------- | ---- |
| `sc_shipments`       | Shipments with delay tracking + geo   | standard   | 214  |
| `sc_suppliers`       | Supplier catalog with scoring         | **lookup** | 33   |
| `sc_news`            | News articles with 384-dim embeddings | standard   | 18   |
| `sc_orders`          | Customer orders                       | standard   | 300  |
| `sc_products`        | Product catalog                       | **lookup** | 10   |
| `sc_actions_log`     | Agent action audit trail              | standard   | —    |
| `sc_purchase_orders` | Recovery POs                          | standard   | —    |

> ⚠️ `lookup` mode on `sc_suppliers` and `sc_products` is **required** for ES|QL `LOOKUP JOIN`. Without it, joins silently return no results.

---

## 🚀 Quick Start

```bash
# 1. Set credentials
export ES_ENDPOINT="https://your-deployment.es.us-east-1.aws.elastic.cloud"
export ES_API_KEY="your-api-key"
export KIBANA_URL="https://your-deployment.kb.us-east-1.aws.elastic.cloud"
export NGROK_AUTH_TOKEN="your-ngrok-token"   # required for live MCP wiring

# 2. Install dependencies
pip install elasticsearch faker mcp flask pyngrok

# 3. Set up data and agents
python scripts/setup_indices.py       # Create 7 indices with mappings
python data/generate_data.py          # Synthetic supply chain data
python data/load_data.py              # Load 575 docs into Elasticsearch
python scripts/create_tools.py        # Create 4 Agent Builder tools
python scripts/create_agent.py        # Create SupplyShield Orchestrator
python scripts/create_news_scout.py   # Create News Scout sub-agent

# 4. Start MCP server + wire A2A connector (one command)
python scripts/start_mcp_with_ngrok.py
```

See [`docs/setup_guide.md`](docs/setup_guide.md) for manual Kibana setup.

---

## 📁 Project Structure

```
supplyshield/
├── agents/
│   ├── supplyshield_agent.md       # Orchestrator system prompt + config
│   └── news_scout_agent.md         # News Scout config + MCP wiring docs
├── tools/
│   ├── detect_shipment_anomalies.md
│   ├── assess_revenue_impact.md
│   ├── find_alternative_suppliers.md
│   └── search_disruption_news.md
├── workflows/
│   └── supply_chain_recovery.md    # Elastic Workflow definition
├── data/
│   ├── generate_data.py            # Synthetic data (Faker, seed=42)
│   ├── load_data.py                # Bulk load via elasticsearch-py
│   └── sample_data/                # Generated JSON
├── mappings/
│   └── index_mappings.md           # All 7 index mappings documented
├── scripts/
│   ├── setup_indices.py
│   ├── create_tools.py
│   ├── create_agent.py
│   ├── create_news_scout.py
│   ├── news_scout_mcp_server.py    # FastMCP server (query_disruption_news)
│   ├── start_mcp_with_ngrok.py     # One-command: server + tunnel + wire Kibana
│   └── wire_mcp_connector.py
└── docs/
    ├── architecture.md
    ├── setup_guide.md
    ├── submission_description.md
    ├── architecture_main.mermaid
    ├── architecture_sequence.mermaid
    ├── architecture_dataflow.mermaid
    └── architecture_usecase.mermaid
```

---

## 🔑 Key Design Decisions

### ES|QL Parameterized Queries as LLM Guardrails

The LLM fills **values** (`"SUP-SZ-001"`, `24`) but never **query structure**. Using `?param` syntax keeps tool behavior fixed and auditable — the agent cannot alter what a query does, only what it queries for.

### Separation of Read and Write

All reads go through tools. All writes go through a deterministic Elastic Workflow requiring explicit user confirmation. The agent cannot modify data through a malformed query argument, and every action has an immutable log entry.

### Hybrid Search on News

`sc_news` combines 384-dimension dense vector embeddings (cosine similarity) with BM25 keyword matching, following Elastic's recommended hybrid search pattern for balancing semantic and lexical relevance.

### MCP for Agent-to-Agent Delegation

The Orchestrator calls the News Scout via the [Model Context Protocol](https://modelcontextprotocol.io/) — an open standard for agent communication. This keeps the agents independently deployable and testable, with a clean interface boundary.

---

## 📚 References

- J.S. Held (2025). [Global Risk Report 2025](https://www.jsheld.com/insights/articles/global-risk-report-2025) — $184B annual cost
- BCI (2024). [Supply Chain Resilience Report 2024](https://www.thebci.org/resource/bci-supply-chain-resilience-report-2024.html) — 80% of orgs disrupted
- McKinsey (2024). [Global Supply Chain Leader Survey](https://www.mckinsey.com/capabilities/operations/our-insights/supply-chain) — 90% resilience challenges
- McKinsey (Jan 2026). Supply Chain Risk Outlook — 82% hit by tariffs, +39% costs
- Gartner (2025). [Future of Supply Chain 2025](https://www.gartner.com/en/supply-chain/topics/supply-chain-risk-management) — 29% prepared
- Kinaxis (2024). [Disruption Response Study](https://www.kinaxis.com/en/resources/report/supply-chain-disruption) — 83% can't respond in 24h; avg = 5 days
- Elastic (2023). [Hybrid Search Blog](https://www.elastic.co/blog/improving-information-retrieval-elastic-stack-hybrid)
- Anthropic (2024). [Model Context Protocol](https://modelcontextprotocol.io/)

---

## 📄 License

Apache 2.0 — see [LICENSE](LICENSE).

---

<div align="center">
<sub>Built for the Elastic Agent Builder Hackathon · January–February 2026</sub>
</div>
