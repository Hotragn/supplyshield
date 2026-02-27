# SupplyShield: Multi-Agent Supply Chain Disruption Detection on Elastic

## The Problem

Supply chain disruptions cost $4.4 trillion globally per year. When a port congests or a key supplier goes offline, procurement teams spend 3 to 7 days gathering data, running impact analyses, and getting approval to act. The tools for responding are fragmented — shipment data, order books, and supplier records all live in separate systems with no unified view.

## The Solution

SupplyShield is a **multi-agent system** on Elastic Agent Builder:

- **SupplyShield Orchestrator** — the main conversational agent. Detects shipment anomalies, assesses financial impact, sources alternative suppliers, and triggers recovery through Elastic Workflows.
- **SupplyShield News Scout** — a specialist sub-agent called by the Orchestrator via MCP. Its sole job is external intelligence: search `sc_news`, classify signal strength (CONFIRMED / UNCERTAIN / UNCONFIRMED), and return machine-readable summaries the Orchestrator synthesizes for the user.

When a user reports a disruption, the Orchestrator runs `detect_shipment_anomalies` (ES|QL LOOKUP JOIN across shipments, suppliers, and products), then delegates corroboration to the News Scout. Only after the Scout's signal classification does the Orchestrator proceed to assess revenue impact with `assess_revenue_impact`, rank alternatives with `find_alternative_suppliers`, and optionally execute recovery through an Elastic Workflow. Every write action requires explicit user confirmation.

**Result:** 72-hour manual process reduced to 3 minutes. With real data: 14 Shenzhen-delayed shipments, over $10M revenue at risk, recovery PO created in the same conversation.

## Elastic Features Used

- **ES|QL LOOKUP JOINs** across 6 normalized indices — `sc_suppliers` and `sc_products` use `index.mode: lookup`, required for in-query joins without denormalization
- **Parameterized ES|QL queries** using `?param` syntax — LLM fills in values, never query structure (injection guardrail)
- **Hybrid search** on `sc_news` — 384-dim dense vector (cosine) combined with keyword matching on title and body
- **Elastic Workflows** — separates read from write, maintains audit trail, requires confirmation before executing
- **MCP protocol** — Orchestrator-to-Scout communication follows Model Context Protocol for clean agent specialization
- **Multi-agent architecture** — two agents with distinct roles, independent system prompts, and clear handoff boundaries

## What I Found Genuinely Useful

**LOOKUP JOINs changed how I think about index design.** Being able to join a fact table (shipments) to dimension tables (suppliers, products) at query time keeps data normalized without paying the query cost of nested documents or application-side joins. The `lookup` mode requirement is the kind of gotcha that trips you up once, then becomes a clean mental model.

**Parameterized queries as LLM guardrails** turned out better than I expected. The agent handles "what" and the query handles "how." That separation made tool behavior predictable and auditable in ways a fully LLM-generated query never could be.

## Challenge

Designing the multi-agent handoff was harder than expected. The News Scout needed to be told explicitly that it's talking to another agent, not a person — it should return structured, machine-readable summaries, not conversational prose. Getting that system prompt right took multiple iterations and made me think carefully about agent-to-agent communication patterns vs human-to-agent ones.

## Impact

72 hours reduced to 3 minutes. Fully auditable. Every recovery action is logged. The agent explains what it did and why before it does it.
