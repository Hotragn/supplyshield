# SupplyShield: Supply Chain Disruption Detection Agent on Elastic

## The Problem

Supply chain disruptions are expensive and slow to respond to. When a port goes down or a key supplier goes offline, procurement teams spend 3 to 7 days gathering data, running impact analyses, emailing alternatives, and getting approval to act. By the time a purchase order reaches a replacement supplier, the damage is done - orders are slipping, customers are unhappy, and revenue is at risk.

The core issue isn't that people don't know disruptions happen. It's that the tools for responding are fragmented. Shipment data is in one system, order books are in another, supplier records are somewhere else, and nobody has a unified view.

## The Solution

SupplyShield is a multi-step agent built on Elastic Agent Builder that gives supply chain teams a unified view and a path to action in a single conversation.

When a user reports a disruption, the agent:

1. **Detects** affected shipments using ES|QL with LOOKUP JOINs across the shipment, supplier, and product indices. It returns exact counts, average delays, and which component types are at risk.

2. **Assesses** the financial blast radius by joining active orders to products and suppliers. It gives you total revenue at risk, order count, customer count, and earliest due dates - in dollars and days, not vague estimates.

3. **Sources** alternatives using a weighted suitability score: reliability (40%), capacity (30%), lead time (30%). It excludes the disrupted supplier and optionally the disrupted region.

4. **Corroborates** with news using hybrid semantic and keyword search on a news index with 384-dimensional vector embeddings. This catches early warning signals before they show up in shipment delays.

5. **Acts** through an Elastic Workflow that creates purchase orders and logs every action to an audit trail. It won't pull the trigger without explicit user confirmation.

## How It Works in Practice

Here's what a real session looks like with the demo data:

A user types: "We're hearing about Shenzhen port congestion. Check if we have affected shipments."

The agent calls `detect_shipment_anomalies` with a 336-hour window and returns 14 delayed shipments across 3 Shenzhen suppliers, with delays ranging from 48 to 312 hours. It surfaces the affected supplier IDs automatically.

The user asks for revenue impact. The agent calls `assess_revenue_impact` for each affected supplier and returns $2.3M in active orders at risk across 23 orders and 11 customer accounts. Earliest due date is 8 days out.

The agent searches news and finds 3 corroborating articles from the past 3 days - high severity, negative sentiment, confirming port waiting times of 8-10 days.

The user asks for alternatives for microcontrollers outside East Asia. The agent returns 5 ranked options - Viet Components Manufacturing in Vietnam tops the list at a suitability score of 84.2, 18-day lead time, 10% cost premium.

The user approves. The agent triggers the recovery workflow, creates a purchase order, and logs the action. Total time: under 3 minutes.

## Elastic Features Used

- **ES|QL LOOKUP JOINs** across 6 normalized indices. `sc_suppliers` and `sc_products` use `index.mode: lookup` which is required for in-query joins without denormalization.
- **Parameterized ES|QL queries** using `?param` syntax - the LLM fills in values, never query structure. This is the guardrail that keeps queries deterministic and safe.
- **Hybrid search** on `sc_news` combining dense vector (384d, cosine) with keyword matching on title and body.
- **Elastic Workflows** for write operations - separates read from write, maintains an audit log, requires confirmation before executing.

## What I Found Genuinely Useful

LOOKUP JOINs are the standout feature here. Being able to join a fact table (shipments) to dimension tables (suppliers, products) at query time without pre-joining is exactly what normalized data models need. The `lookup` mode index setting is the kind of thing that trips you up if you don't know about it, but once you do it's a clean pattern.

Parameterized queries as LLM guardrails also turned out to be a better design than I expected. The agent handles the "what" and the query handles the "how." That separation makes the system predictable and auditable.

## Challenge

Getting the agent to reliably select the right tool in the right order took more prompt engineering than expected. The tool descriptions ended up being as important as the system prompt. Being explicit about when NOT to use a tool helped calibrate tool selection significantly.

## Impact

72 hours reduced to 3 minutes for supply chain disruption detection and initial recovery actions. With $4.4T in annual global disruption costs, even small improvements in response time have measurable impact on revenue preservation.
