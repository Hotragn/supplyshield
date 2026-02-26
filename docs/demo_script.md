# SupplyShield Demo Script

**Target time:** 2 minutes 50 seconds
**Format:** Screen recording with narration

---

## Section 1: Problem Statement (0:00 - 0:20)

_[Show a simple slide or your terminal with a stats display]_

"Supply chain disruptions cost the global economy roughly $4.4 trillion per year. When a port goes down or a supplier goes dark, the manual response loop - emails, meetings, procurement negotiations - takes 3 to 7 days. By the time you have a recovery plan, orders are already slipping.

SupplyShield is an AI agent built on Elastic Agent Builder that compresses that response to under 3 minutes."

---

## Section 2: Architecture Overview (0:20 - 0:35)

_[Show the architecture diagram from docs/architecture_diagram.mermaid rendered as an image]_

"The agent orchestrates 4 tools across 6 Elasticsearch indices. Detection and assessment use ES|QL with LOOKUP JOINs across normalized data. News corroboration uses hybrid semantic search. Recovery uses an Elastic Workflow that writes to a purchase order index and audit log.

The key design choice: parameterized queries. The LLM fills in values, but never touches query structure. That's your guardrail."

---

## Section 3: Live Demo (0:35 - 2:15)

_[Open Kibana, navigate to Agent Builder, open SupplyShield]_

### Turn 1 - Detection (0:35 - 1:00)

Type: **"We're getting reports of congestion at Shenzhen port. Can you check if we have affected shipments in the past 2 weeks?"**

_[Wait for response - agent calls detect_shipment_anomalies]_

"The agent found 14 delayed shipments out of Shenzhen across 3 suppliers - Shenzhen Microtech, GreenCell Battery, and Optolink Displays. Average delay is 143 hours. Max delay is 312 hours. Four distinct component types affected."

_[Show the tool call that was made with parameters highlighted]_

### Turn 2 - Revenue Impact (1:00 - 1:25)

Type: **"What's the revenue impact from Shenzhen Microtech specifically?"**

_[Agent calls assess_revenue_impact with SUP-SZ-001]_

"Revenue at risk: $1.4M across 18 active orders, spanning 9 customer accounts. Earliest due date is 8 days from today. Products affected are SmartWatch Pro and HomeHub Controller."

### Turn 3 - Corroborate with News (1:25 - 1:45)

Type: **"Are there any news reports confirming this?"**

_[Agent calls search_disruption_news with "Shenzhen port congestion"]_

"Three articles from the past 3 days, all high severity, average sentiment score -0.76. Port waiting times extended to 8-10 days. This aligns with what we're seeing in the shipment data."

### Turn 4 - Find Alternatives (1:45 - 2:05)

Type: **"Find me alternative suppliers for microcontrollers outside of East Asia."**

_[Agent calls find_alternative_suppliers, excluded_region: East Asia]_

"Top alternative is Viet Components Manufacturing in Vietnam - suitability score 84.2, 18-day lead time, 10% cost premium. Second is Penang TechFab in Malaysia, similar score. Both can cover the microcontroller and PCB assembly capability gap."

### Turn 5 - Recovery Action (2:05 - 2:15)

Type: **"Go ahead and create a PO with Viet Components for the SmartWatch Pro components, 200 units."**

_[Agent confirms what it's about to do, you type "yes"]_
_[Workflow runs, creates PO and logs action]_

"PO created. Action logged to audit trail. Recovery initiated in under 3 minutes."

---

## Section 4: Results Summary (2:15 - 2:40)

_[Show a quick slide or annotated screenshot]_

"What just happened, quantified:

- 14 delayed shipments detected across 3 suppliers
- $2.3M+ in total revenue at risk identified
- 5 ranked alternatives surfaced, with cost and lead time tradeoffs
- Purchase order created and logged

Time from problem to recovery action: 3 minutes. Previous manual process: 3 to 7 days."

---

## Section 5: Closing (2:40 - 2:50)

"SupplyShield is fully open source under Apache 2.0. The repo has setup scripts, sample data generation, and all the tool and agent configurations.

Give it a star if you find it useful. Thanks for watching."

---

## Recording Tips

- **Dark mode:** Enable dark mode in Kibana before recording. It reads better on video.
- **Zoom:** Set browser to 125% zoom for readability on smaller screens.
- **Takes:** Plan for 3-5 takes. The first one is never the keeper.
- **Pauses:** Give yourself 1-2 seconds after each agent response before speaking. Makes editing easier.
- **Demo fail prep:** Have the expected output ready as screenshots in case the live agent is slow.
- **Upload:** YouTube unlisted is fine for hackathon submissions. Vimeo also works.
- **Music:** Skip background music unless it's royalty-free. Not worth the copyright flag.
- **Resolution:** Record at 1080p minimum. 4K if your machine handles it.
