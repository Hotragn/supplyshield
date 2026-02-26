# Challenge Requirements vs SupplyShield — Alignment Verification

## ✅ PASS/FAIL against every requirement

---

### Core Technical Requirements

| Requirement                      | Status | Evidence                                                                                                              |
| -------------------------------- | ------ | --------------------------------------------------------------------------------------------------------------------- |
| Multi-step AI agent              | ✅     | 5-step sequence: detect → corroborate → assess → source → act                                                         |
| Uses Elastic Agent Builder       | ✅     | Agent ID `supplyshield` live in Kibana, 4 tools registered via API                                                    |
| Uses custom tools                | ✅     | 4 tools: `detect_shipment_anomalies`, `assess_revenue_impact`, `find_alternative_suppliers`, `search_disruption_news` |
| Uses ES\|QL tool                 | ✅     | 3 ES\|QL tools with parameterized queries and LOOKUP JOINs                                                            |
| Uses Search tool                 | ✅     | `search_disruption_news` on `sc_news` index (index_search type)                                                       |
| Uses Elastic Workflows           | ✅     | `supply_chain_recovery.md` defines the workflow; documented in submission                                             |
| Data in Elasticsearch            | ✅     | 575 docs across 7 indices loaded to `supplyshield-ac5120.es.us-east-1.aws.elastic.cloud`                              |
| Automates real business task     | ✅     | Supply chain disruption response: detection → impact assessment → recovery PO                                         |
| Open source repo (public)        | ✅     | `github.com/Hotragn/supplyshield` — Apache 2.0                                                                        |
| OSI license visible at repo root | ✅     | `LICENSE` file at root; Apache 2.0                                                                                    |
| Code repo has agent instructions | ✅     | `agents/supplyshield_agent.md`                                                                                        |
| Code repo has custom queries     | ✅     | Queries in `tools/*.md` and `scripts/create_tools.py`                                                                 |

---

### Submission Requirements

| Requirement                             | Status | What to Do                                                         |
| --------------------------------------- | ------ | ------------------------------------------------------------------ |
| ~400 word description                   | ✅     | `docs/submission_description.md` (~380 words) — paste into Devpost |
| 3-minute demo video                     | 🔲     | **TODO: Record using `docs/demo_script.md`**                       |
| Video on YouTube/Vimeo                  | 🔲     | **TODO: Upload once recorded**                                     |
| Social post (@elastic_devs or @elastic) | 🔲     | **TODO: Post from `docs/social_posts.md`**                         |
| Architecture diagram                    | 🔲     | **TODO: See `docs/architecture_diagram*.mermaid` — render to PNG** |
| English language                        | ✅     | All materials in English                                           |

---

### Judging Criteria Assessment

#### Technical Execution (30%)

**Strengths:**

- ES|QL LOOKUP JOINs: `sc_suppliers` and `sc_products` are in `index.mode: lookup` — this is the correct, non-trivial technical implementation
- Parameterized queries (`?param` syntax) as LLM guardrails — prevents prompt injection into query structure
- 384-dimension dense vector field `body_embedding` in `sc_news` for hybrid search
- 7 normalized indices with explicit field typing (keyword, geo_point, float, dense_vector)
- Proper bulk load via `elasticsearch.helpers.bulk`
- Scripts are reproducible and documented

**Potential gaps to address:**

- The Elastic Workflow (`supply_chain_recovery`) is documented but should be **created in Kibana manually** if not already done — judges may test it
- System prompt needs to be pasted into the agent manually in Kibana UI (API doesn't accept it)

---

#### Potential Impact & Wow Factor (30%)

**Strengths:**

- Problem is quantifiable: $4.4T/year in global disruption costs, 3-7 day manual response vs 3 minute automated
- Demo scenario is concrete: 14 delayed Shenzhen shipments, $10M at risk, specific supplier IDs
- Suitability scoring algorithm is novel (weighted: reliability 40%, capacity 30%, lead time 30%)
- Audit trail via actions log demonstrates production readiness thinking

**Keep in demo:**

- Say the dollar amount at risk ($10M) and the time savings (3 minutes vs 72 hours) — judges weight this heavily

---

#### Demo Quality (30%)

**What judges look for:**

1. Problem clearly defined ✅ — opens with "3-7 days manual, 3 minutes automated"
2. Solution effectively presented — needs live agent conversation
3. Agent Builder and tools explained — call out each tool as it fires
4. Architectural diagram included — **needs rendering**

**Recommendation:** In the demo video, explicitly show the tool call panel in Kibana when each tool fires. This proves multi-step agent execution, not just a chatbot.

---

#### Social (10%)

**Easy 10 points — do this before submitting:**

```
Post from docs/social_posts.md to:
1. X (Twitter) — tag @elastic_devs
2. LinkedIn (optional bonus)
```

Copy the social post URL from the platform and paste in the Devpost submission form.

---

## ⚠️ Action Items Before 1:00 PM Tomorrow

### Tonight (must-do)

- [ ] Paste system prompt from `agents/supplyshield_agent.md` into Kibana Agent Builder UI
- [ ] Test the agent with: "We're hearing about Shenzhen port congestion. Check if we have affected shipments."
- [ ] Verify all 4 tools are listed in the agent in Kibana

### Before recording

- [ ] Enable dark mode in Kibana (Settings > Appearance)
- [ ] Set browser zoom to 125%
- [ ] Clear browser console/notifications
- [ ] Have `docs/demo_script.md` open on second monitor

### Recording

- [ ] Record 3 takes, use the cleanest
- [ ] Target: exactly 2:50 (judges stop watching at 3:00)
- [ ] Upload to YouTube as Unlisted
- [ ] Copy URL

### Submission (Devpost)

- [ ] Title: "SupplyShield: AI Supply Chain Disruption Response Agent"
- [ ] Description: paste `docs/submission_description.md`
- [ ] Repo URL: `https://github.com/Hotragn/supplyshield`
- [ ] Video URL: your YouTube link
- [ ] Screenshot: 2-3 from Kibana Agent Builder conversation
- [ ] Architecture diagram: render and upload `docs/architecture_diagram.mermaid`
- [ ] Social post: post and paste URL

### After submitting

- [ ] Verify submission shows on the Devpost project page
- [ ] Check that repo is public (incognito window test)
- [ ] Confirm LICENSE shows as Apache-2.0 in GitHub's "About" section
