# Execution Plan

Deadline: Feb 27, 1:00 PM Eastern. Current time: Feb 26, ~2:30 PM Eastern. You have roughly 22 hours.

---

## Tonight (Feb 26)

### Start your Elasticsearch trial (15 min)

- Go to cloud.elastic.co and start a Serverless trial
- Copy ES_ENDPOINT, API_KEY, KIBANA_URL
- Set environment variables in your shell

### Push the code (10 min)

- Create a GitHub repo called `supplyshield` (public)
- Add remote: `git remote add origin https://github.com/YOUR_USERNAME/supplyshield.git`
- `git add -A`
- `git commit -m "Initial SupplyShield submission for Elasticsearch Agent Builder Hackathon"`
- `git push -u origin main`

### Run setup scripts (20 min)

```bash
pip install elasticsearch requests faker
python scripts/setup_indices.py
python data/generate_data.py
python data/load_data.py
```

Verify counts printed at end. Should see ~40 suppliers, ~10 products, ~214 shipments, ~300 orders, ~18 news.

### Create tools (15 min)

```bash
python scripts/create_tools.py
```

If 404 or auth error, create manually in Kibana. Don't spend more than 5 minutes debugging.

### Create agent (10 min)

```bash
python scripts/create_agent.py
```

Same fallback: create manually in Kibana if API fails.

### Test the agent (20 min)

Run these 3 conversations and verify each tool call works:

1. "We're hearing about congestion at Shenzhen port. Can you check if we have affected shipments?"
2. "How much revenue is at risk from the Shenzhen disruption?"
3. "Find alternative suppliers for microcontrollers outside East Asia."

---

## Tomorrow Morning (Feb 27)

### Record demo video (45 min)

- Set browser to dark mode and 125% zoom
- Open `docs/demo_script.md` and follow it exactly for the first take
- Record 3-5 takes
- Pick the cleanest one (doesn't need to be perfect)
- Upload to YouTube as Unlisted
- Copy the URL for your Devpost submission

### Render architecture diagram (10 min)

Option A - If you have Node.js:

```bash
npm install -g @mermaid-js/mermaid-cli
mmdc -i docs/architecture_diagram.mermaid -o docs/architecture_diagram.png
```

Option B - Go to mermaid.live, paste the contents of `docs/architecture_diagram.mermaid`, export as PNG.
Save as `docs/architecture_diagram.png`.

### Post on social media (5 min)

- Post the X/Twitter content from `docs/social_posts.md`
- Tag @elastic_devs
- Optional: post the LinkedIn version too

### Register on Devpost (15 min)

- Go to the Elasticsearch Agent Builder Hackathon page on Devpost
- Click "Enter the Hackathon"
- Fill in team info
- Start your project submission draft

### Fill in Devpost project (20 min)

- Title: "SupplyShield: Supply Chain Disruption Detection Agent"
- Short description: copy from top of `docs/submission_description.md`
- Long description: paste full content of `docs/submission_description.md`
- Demo video: paste YouTube URL
- GitHub repo: paste repo URL
- Screenshots: take 2-3 screenshots of the agent conversation in Kibana
- Architecture diagram: upload `docs/architecture_diagram.png`
- Tags: supply-chain, elasticsearch, agent-builder, esql, hybrid-search

---

## Day of Deadline (Feb 27, before 1:00 PM Eastern)

### Final 30-item pre-submission checklist

**Code:**

- [ ] setup_indices.py runs without errors
- [ ] generate_data.py produces correct counts (14 Shenzhen delayed shipments)
- [ ] load_data.py bulk loads all 5 data files
- [ ] All 7 indices exist with correct mappings (verify in Kibana Dev Tools)
- [ ] sc_suppliers has mode: lookup
- [ ] sc_products has mode: lookup
- [ ] sc_news has dense_vector body_embedding with 384 dims
- [ ] create_tools.py creates all 4 tools (or tools exist manually)
- [ ] create_agent.py creates agent (or agent exists manually)

**Agent functionality:**

- [ ] detect_shipment_anomalies returns results for a 336-hour window
- [ ] Shenzhen port query returns at least 14 delayed shipments
- [ ] assess_revenue_impact returns dollar figures for SUP-SZ-001
- [ ] find_alternative_suppliers returns ranked results excluding East Asia
- [ ] search_disruption_news returns Shenzhen articles
- [ ] Agent asks for confirmation before workflow (not implemented but documented)

**Repo:**

- [ ] GitHub repo is public
- [ ] README.md renders correctly on GitHub
- [ ] LICENSE file is Apache 2.0 and present at root
- [ ] .gitignore excludes .env
- [ ] All files committed and pushed

**Submission:**

- [ ] Devpost project created
- [ ] Demo video uploaded to YouTube (unlisted)
- [ ] YouTube link pasted in Devpost
- [ ] GitHub repo URL added to Devpost
- [ ] Submission description filled in (use docs/submission_description.md)
- [ ] At least 2 Kibana screenshots attached
- [ ] Architecture diagram uploaded
- [ ] Tags added

**Final:**

- [ ] Click "Submit" on Devpost before 1:00 PM Eastern on Feb 27
- [ ] Confirm submission confirmation email received
- [ ] Post social media links if not done yesterday
- [ ] Done. Go get some sleep.
