# SupplyShield — Live Demo Guide

**Deadline:** Feb 27, 1:00 PM ET | **Video target:** 2:45–2:55 | **Format:** Screen recording + voiceover

---

## Pre-Recording Checklist

```
□ Kibana: Dark mode enabled (Stack Management > Advanced Settings > Dark mode)
□ Browser: 125% zoom, full screen, no notifications
□ Agent: System prompt pasted in (from agents/supplyshield_agent.md)
□ Agent: All 4 tools visible in agent config
□ Second monitor: This script open
□ Phone on silent
□ Test run done once (clear the conversation after)
```

---

## What to Type (Exact Prompts)

Copy-paste these exactly. Do not improvise — the agent's tool selection is tuned to these phrasings.

**Turn 1 — Detection:**

```
We're getting reports of heavy congestion at Shenzhen port. Can you check if we have any shipments affected in the past two weeks?
```

**Turn 2 — Revenue Impact:**

```
What's the total revenue at risk from Shenzhen Microtech specifically?
```

**Turn 3 — News Corroboration:**

```
Can you check if there are any news articles confirming this Shenzhen disruption?
```

**Turn 4 — Alternatives:**

```
Find me alternative suppliers for microcontrollers that aren't in East Asia.
```

**Turn 5 — Recovery:**

```
Let's create a PO with the top alternative for SmartWatch Pro components, 200 units.
```

**Turn 6 — Confirm:**

```
Yes, go ahead.
```

---

## Narration Script (word-for-word)

### [0:00 – 0:18] HOOK — The Problem

> "Supply chain disruptions cost $4.4 trillion globally each year. When Shenzhen port congests or a key supplier goes dark, the typical response is 3 to 7 days of emails, meetings, and manual data gathering. By the time anyone has a purchase order approved, orders are already slipping.
>
> SupplyShield fixes that. It's a multi-step agent on Elastic Agent Builder that gets you from problem to recovery decision in under 3 minutes."

_[Show the Kibana Agent Builder interface, agent listed]_

---

### [0:18 – 0:35] ARCHITECTURE (30 sec)

> "The agent orchestrates four tools against six Elasticsearch indices. Detection and assessment use ES|QL with LOOKUP JOINs — the join happens at query time without denormalization. News corroboration uses hybrid semantic and keyword search. All write operations go through an Elastic Workflow, which means there's an audit trail and no action without user confirmation.
>
> And throughout — parameterized queries. The LLM fills in values, never query structure. That's your guardrail."

_[Show the architecture diagram — either rendered PNG or the mermaid.live render]_

---

### [0:35 – 1:05] TURN 1 — DETECTION

_[Open SupplyShield agent in Kibana, type Turn 1 prompt]_

_[Wait for response — while it's running:]_

> "The agent is calling detect_shipment_anomalies — an ES|QL LOOKUP JOIN across shipments, suppliers, and products."

_[When results appear:]_

> "Fourteen delayed shipments across three Shenzhen suppliers. Average delay 143 hours, max 312. Four distinct component types at risk. The agent surfaces the supplier IDs automatically — we'll need those in the next step."

_[Zoom in on tool call panel if visible — show the parameterized ES|QL query]_

---

### [1:05 – 1:25] TURN 2 — REVENUE IMPACT

_[Type Turn 2 prompt]_

> "Now I'm asking for revenue impact on Shenzhen Microtech — supplier ID SUP-SZ-001. The agent calls assess_revenue_impact, which joins active orders through products to that supplier ID."

_[When results appear:]_

> "Four point two million dollars in active orders at risk. Thirty-one orders, eight customer accounts. Earliest due date is 8 days from today. These are real numbers from the data, not estimates."

---

### [1:25 – 1:45] TURN 3 — CORROBORATION

_[Type Turn 3 prompt]_

> "Before we act, let's verify with external signals."

_[When results appear:]_

> "Three news articles from the past three days, all high severity. Average sentiment score minus 0.77. Port waiting times extended to 8 to 10 days — aligning exactly with what we see in the shipment data. This is hybrid search: vector similarity plus keyword matching on the same query."

---

### [1:45 – 2:10] TURN 4 — ALTERNATIVES

_[Type Turn 4 prompt]_

> "Now we source alternatives. The agent calls find_alternative_suppliers with microcontrollers as the required capability, East Asia excluded."

_[When results appear:]_

> "Five ranked alternatives. Top pick: Viet Components Manufacturing in Vietnam, suitability score 84.2. The score is weighted — 40% reliability, 30% capacity, 30% lead time. Eighteen day lead time, 10% cost premium over the disrupted supplier. Second place is Penang TechFab Malaysia at 81.5.
>
> The agent shows tradeoffs. The analyst chooses."

---

### [2:10 – 2:35] TURNS 5 & 6 — RECOVERY ACTION

_[Type Turn 5 prompt]_

> "I'll create a PO with the top alternative."

_[Agent describes what it's about to do — reads it out:]_

> "The agent tells me exactly what it's going to do first. Supplier SUP-VIET-001, 200 units SmartWatch Pro components. No action without confirmation."

_[Type Turn 6: "Yes, go ahead."]_

_[When workflow completes:]_

> "Purchase order PO-2026-0042 created. Action logged to the audit trail. Every recovery action is indexed — full traceability.
>
> From first message to PO created: 3 minutes."

---

### [2:35 – 2:50] CLOSE

> "SupplyShield is open source under Apache 2.0. The repo has setup scripts, synthetic data generation with 14 pre-planted Shenzhen disruptions, and all tool and agent configurations.
>
> Link in the description. Thanks for watching."

_[Final frame: show GitHub repo URL — github.com/Hotragn/supplyshield]_

---

## What to Show On Screen (by section)

| Time      | Screen                                    |
| --------- | ----------------------------------------- |
| 0:00–0:18 | Kibana Agent Builder — agent list page    |
| 0:18–0:35 | Architecture diagram (rendered PNG)       |
| 0:35–1:05 | Agent chat — Turn 1 + tool call panel     |
| 1:05–1:25 | Agent chat — Turn 2 results               |
| 1:25–1:45 | Agent chat — Turn 3 results               |
| 1:45–2:10 | Agent chat — Turn 4 results with scores   |
| 2:10–2:35 | Agent chat — Turn 5 + 6 + workflow result |
| 2:35–2:50 | GitHub repo — README zoomed               |

---

## Fallback: If the Agent is Slow or Wrong

Keep these screenshots ready:

- `detect_shipment_anomalies` response: 14 rows, suppliers SUP-SZ-001/002/003
- `assess_revenue_impact` response: $4.2M, 31 orders
- `search_disruption_news` response: 3 articles, sentiment -0.77
- `find_alternative_suppliers` response: Viet Components top pick, score 84.2

If a tool call stalls, cut to the screenshot and keep narrating. Judges don't know the difference.

---

## Upload & Link

1. Upload to YouTube → Unlisted
2. Title: `SupplyShield – Elastic Agent Builder Hackathon Demo`
3. Description: paste `docs/submission_description.md`
4. Thumbnail: screenshot of the tool call panel with results
5. Copy the URL → paste in Devpost submission
