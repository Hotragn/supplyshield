"""
news_scout_mcp_server.py - MCP server exposing the News Scout's capabilities.

This server exposes a query_disruption_news tool via MCP SSE transport.
The SupplyShield Orchestrator in Kibana calls this via a .mcp connector.

Usage:
    # Terminal 1 - start server:
    python scripts/news_scout_mcp_server.py

    # Terminal 2 - create public tunnel (no auth needed):
    ssh -R 80:localhost:8000 nokey@localhost.run

    # Then use the printed https://xxxx.lhr.life URL as serverUrl in Kibana .mcp connector.

Requirements: pip install mcp elasticsearch
"""

import os
import sys
import json
import logging
from mcp.server.fastmcp import FastMCP
try:
    from mcp.server.fastmcp.security import TransportSecuritySettings
    HAS_SECURITY = True
except ImportError:
    HAS_SECURITY = False
from elasticsearch import Elasticsearch

# ── Config ────────────────────────────────────────────────────────────────────
ES_ENDPOINT = os.environ.get("ES_ENDPOINT", "").rstrip("/")
ES_API_KEY  = os.environ.get("ES_API_KEY", "")
PORT        = int(os.environ.get("MCP_PORT", "8000"))

if not ES_ENDPOINT or not ES_API_KEY:
    print("ERROR: ES_ENDPOINT and ES_API_KEY must be set")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("news_scout_mcp")

# ── Elasticsearch client ───────────────────────────────────────────────────────
es = Elasticsearch(ES_ENDPOINT, api_key=ES_API_KEY, verify_certs=True)

# ── MCP Server ────────────────────────────────────────────────────────────────
# Set env vars that FastMCP reads for host/port/security config
os.environ["FASTMCP_HOST"] = "0.0.0.0"
os.environ["FASTMCP_PORT"] = str(PORT)

if HAS_SECURITY:
    security = TransportSecuritySettings(
        enable_dns_rebinding_protection=False,
        allowed_hosts=["*"],
        allowed_origins=["*"],
    )
    mcp = FastMCP(
        name="supplyshield-news-scout",
        instructions=(
            "You are the SupplyShield News Scout. Search news articles about "
            "supply chain disruptions and classify signal strength. "
            "Return structured machine-readable summaries for the Orchestrator."
        ),
        transport_security=security,
        host="0.0.0.0",
        port=PORT,
    )
else:
    mcp = FastMCP(
        name="supplyshield-news-scout",
        instructions=(
            "You are the SupplyShield News Scout. Search news articles about "
            "supply chain disruptions and classify signal strength. "
            "Return structured machine-readable summaries for the Orchestrator."
        ),
        host="0.0.0.0",
        port=PORT,
    )


@mcp.tool()
def query_disruption_news(query: str, region: str = "", min_severity: str = "") -> str:
    """
    Search supply chain disruption news using hybrid semantic + keyword search.

    Returns a JSON object with signal classification and article summaries.
    Always returns CONFIRMED, UNCERTAIN, or UNCONFIRMED signal classification.

    Args:
        query: Natural language search query (e.g., 'Shenzhen port congestion 2026')
        region: Optional region filter (e.g., 'East Asia', 'Asia Pacific')
        min_severity: Optional minimum severity filter ('low', 'medium', 'high', 'critical')
    """
    try:
        must_clauses = [{
            "multi_match": {
                "query": query,
                "fields": ["title^2", "body"],
                "type": "best_fields"
            }
        }]
        filter_clauses = []
        if region:
            filter_clauses.append({"term": {"regions": region}})
        severity_order = ["low", "medium", "high", "critical"]
        if min_severity and min_severity in severity_order:
            idx = severity_order.index(min_severity)
            filter_clauses.append({"terms": {"severity": severity_order[idx:]}})

        resp = es.search(index="sc_news", body={
            "query": {"bool": {"must": must_clauses, "filter": filter_clauses}},
            "_source": ["title", "body", "regions", "sentiment_score",
                        "disruption_type", "severity", "published_date"],
            "size": 5
        })
        hits = resp["hits"]["hits"]

        if not hits:
            return json.dumps({
                "signal": "UNCONFIRMED",
                "article_count": 0,
                "message": "No relevant news articles found.",
                "recommendation": "Proceed with caution based on shipment data alone.",
                "articles": []
            })

        sentiments = [h["_source"].get("sentiment_score", 0) for h in hits]
        severities = [h["_source"].get("severity", "low") for h in hits]
        avg_sentiment = sum(sentiments) / len(sentiments)
        high_sev_count = sum(1 for s in severities if s in ("high", "critical"))

        signal = "CONFIRMED" if high_sev_count >= 2 and avg_sentiment < -0.5 else "UNCERTAIN"

        articles = [{
            "title": h["_source"].get("title", ""),
            "published_date": h["_source"].get("published_date", ""),
            "severity": h["_source"].get("severity", ""),
            "sentiment_score": h["_source"].get("sentiment_score", 0),
            "disruption_type": h["_source"].get("disruption_type", ""),
            "regions": h["_source"].get("regions", []),
            "summary": h["_source"].get("body", "")[:250]
        } for h in hits]

        return json.dumps({
            "signal": signal,
            "article_count": len(hits),
            "avg_sentiment_score": round(avg_sentiment, 3),
            "high_severity_articles": high_sev_count,
            "disruption_types": list(set(a["disruption_type"] for a in articles)),
            "regions_affected": list(set(r for a in articles for r in a["regions"])),
            "articles": articles,
            "interpretation": (
                f"{signal}: {len(hits)} article(s), avg sentiment {round(avg_sentiment, 2)}, "
                f"{high_sev_count} high/critical severity article(s)."
            )
        }, indent=2)

    except Exception as e:
        log.error(f"ES query error: {e}")
        return json.dumps({"signal": "ERROR", "message": str(e), "articles": []})


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Test ES
    try:
        es.info()
        log.info("Elasticsearch connection OK")
    except Exception as e:
        print(f"ERROR: Cannot connect to Elasticsearch: {e}")
        sys.exit(1)

    print(f"\nStarting News Scout MCP Server on port {PORT}")
    print(f"SSE endpoint: http://0.0.0.0:{PORT}/sse")
    print()
    print("To expose publicly (open a SECOND terminal and run):")
    print(f"  ssh -R 80:localhost:{PORT} nokey@localhost.run")
    print()
    print("Then use the printed https://xxxx.lhr.life URL as:")
    print("  serverUrl in your Kibana .mcp connector")
    print()
    print("Kibana connector tool_name: query_disruption_news")
    print()

    # Use streamable-http (regular HTTP POST) — works through tunnels unlike SSE
    # Kibana .mcp connector will call POST /mcp
    mcp.run(transport="streamable-http")
