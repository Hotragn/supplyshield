# Setup Guide

This walks you through getting SupplyShield running end to end, including manual fallbacks if the API scripts don't work.

## Prerequisites

- Python 3.9+
- An Elasticsearch Serverless trial (start at cloud.elastic.co - takes about 2 minutes)
- Git

## Getting Your Credentials

After creating your Elasticsearch Serverless deployment:

1. Go to your deployment overview page
2. Copy the **Elasticsearch endpoint** (the URL starting with `https://`)
3. Click **API Keys** > **Create API key**
4. Give it a name like `supplyshield-hackathon`
5. Copy the key (you'll only see it once)
6. Copy the **Kibana URL** from the deployment overview

## Setting Environment Variables

**Windows (PowerShell):**

```powershell
$env:ES_ENDPOINT = "https://your-deployment.es.us-east-1.aws.elastic.cloud"
$env:ES_API_KEY = "your-api-key-here"
$env:KIBANA_URL = "https://your-deployment.kb.us-east-1.aws.elastic.cloud"
```

**Mac/Linux:**

```bash
export ES_ENDPOINT="https://your-deployment.es.us-east-1.aws.elastic.cloud"
export ES_API_KEY="your-api-key-here"
export KIBANA_URL="https://your-deployment.kb.us-east-1.aws.elastic.cloud"
```

## Installing Dependencies

```bash
pip install elasticsearch requests faker
```

## Step 1: Create Indices

```bash
python scripts/setup_indices.py
```

This creates all 7 indices with correct mappings. The important ones are `sc_suppliers` and `sc_products`, which need `index.mode: lookup` for ES|QL LOOKUP JOINs to work.

Expected output:

```
Connected to Elasticsearch: ...
Creating SupplyShield indices...
  Created index: sc_shipments
  Created index: sc_suppliers
  ...
Done. Created 7 indices.
```

## Step 2: Generate Data

```bash
python data/generate_data.py
```

Generates 40 suppliers, 10 products, 214 shipments, 300 orders, and 18 news articles. Writes JSON files to `data/sample_data/`. Uses `random.seed(42)` so results are reproducible.

At the end it prints a demo summary showing the Shenzhen delayed shipment count and revenue at risk.

## Step 3: Load Data

```bash
python data/load_data.py
```

Bulk loads all JSON files into Elasticsearch and prints a count verification for each index.

## Step 4: Create Tools

**Option A - API script:**

```bash
python scripts/create_tools.py
```

If this returns 404 or auth errors, use Option B.

**Option B - Manual in Kibana:**

1. Go to your Kibana URL
2. Navigate to **Management** > **Agent Builder** > **Tools**
3. Click **Create Tool** for each of the 4 tools
4. Copy the ES|QL queries and parameters from the `tools/` directory
5. For `search_disruption_news`, set type to **Search**, index to `sc_news`, and enable hybrid search

Key point: the tool description matters more than you'd expect. The agent uses it to decide which tool to call. Be explicit about when NOT to use each tool.

## Step 5: Create Agent

**Option A - API script:**

```bash
python scripts/create_agent.py
```

**Option B - Manual in Kibana:**

1. Navigate to **Management** > **Agent Builder** > **Agents**
2. Click **Create Agent**
3. Fill in:
   - ID: `supplyshield`
   - Name: `SupplyShield`
   - Description: `Supply chain disruption detection and automated recovery assistant`
4. Paste the system instructions from `agents/supplyshield_agent.md`
5. Add all 4 tools
6. Save

## Testing the Agent

Open SupplyShield in Kibana and try these conversations:

**Conversation 1 - Basic detection:**

> "We're hearing about port congestion in Shenzhen. Can you check if we have any affected shipments?"

Expected: Agent calls `detect_shipment_anomalies`, returns 14 delayed shipments from Shenzhen across 3 suppliers.

**Conversation 2 - Revenue impact:**

> "How much revenue is at risk from the Shenzhen suppliers?"

Expected: Agent calls `assess_revenue_impact` for each affected supplier, returns total revenue at risk, order count, and customer count.

**Conversation 3 - Alternative sourcing:**

> "What alternative suppliers do we have for microcontrollers that aren't in East Asia?"

Expected: Agent calls `find_alternative_suppliers` with `excluded_region: "East Asia"`, returns ranked alternatives with suitability scores.

## Troubleshooting

**LOOKUP JOINs returning no joined fields:**

- Check that `sc_suppliers` and `sc_products` were created with `index.mode: lookup`
- Verify data was loaded before testing (run `load_data.py` first)
- The join field name in the query must exactly match the field name in both indices

**Tool not being called correctly:**

- Edit the tool description to be more explicit about when to use it
- The LLM uses the description to determine which tool fits the user's question
- Adding "Do NOT use this tool for X" is often as effective as "Use for Y"

**Timestamp range returning no results:**

- `detect_shipment_anomalies` uses `@timestamp > NOW() - ?time_window::DURATION`
- The generated data uses timestamps relative to generation time
- If you generated data days ago and just loaded it, try extending the time_window parameter

**API key authentication errors:**

- Make sure you're using raw API key format (not base64-encoded)
- Kibana endpoints use `Authorization: ApiKey YOUR_KEY`, not Bearer
- The `kbn-xsrf: true` header is required for all Kibana API mutations

**`requests` module not found:**

- `pip install requests` (the create scripts use requests, not the es client)
