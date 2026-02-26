# Social Posts

## X (Twitter)

Built SupplyShield for the @elastic_devs Agent Builder Hackathon. It's a multi-step supply chain agent that detects disruptions, calculates revenue at risk, ranks alternatives, and creates recovery POs - using ES|QL LOOKUP JOINs, hybrid search, and Elastic Workflows. 72 hours -> 3 minutes.

[link to your GitHub repo or Devpost]

---

## LinkedIn

**Just wrapped up SupplyShield for the Elasticsearch Agent Builder Hackathon.**

Supply chain disruptions cost $4.4T globally per year. The response to a port disruption or supplier outage typically takes 3-7 days - gathering data, looping in procurement, finding alternatives, getting PO approval. SupplyShield gets that down to under 3 minutes.

Here's what I built:

**The agent** lives in Elastic Agent Builder and orchestrates 4 tools in sequence:

1. **detect_shipment_anomalies** - ES|QL query with LOOKUP JOINs across shipments, suppliers, and products. Finds delayed shipments grouped by supplier and port, returns exact counts and delay statistics.

2. **assess_revenue_impact** - Joins active orders through products to suppliers, calculates total revenue at risk, affected customers, and earliest due dates in actual dollar figures.

3. **find_alternative_suppliers** - Ranks alternatives using a weighted score: reliability, capacity, and lead time. Excludes the disrupted supplier and optionally the disrupted region.

4. **search_disruption_news** - Hybrid semantic + keyword search on a news index with 384-dim vector embeddings. Corroborates shipment anomalies with external signals.

A recovery Elastic Workflow handles write operations (purchase orders + audit log) with explicit confirmation gates.

**The architecture choice I'm most happy with:** ES|QL LOOKUP JOINs instead of denormalization. Keeping suppliers, products, and shipments in separate normalized indices meant I could update a supplier's reliability score once and have it reflected everywhere immediately. The `index.mode: lookup` setting on the supplier and product indices is what makes this work.

**What was harder than expected:** Prompt engineering for reliable tool selection. The tool descriptions matter as much as the system prompt. Adding explicit "do NOT use this tool for X" guidance made tool selection noticeably more reliable.

The full repo is open source (Apache 2.0), with setup scripts, synthetic data generation, and all tool/agent configurations.

[Architecture diagram embedded here]

[GitHub link]

#elasticsearch #supplychain #agentbuilder #hackathon #elasticsearch
