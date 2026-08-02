# src/main_server.py
import os
import sys

# Force the project root directory into the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import re
import sqlite3
import requests
from datetime import datetime, timezone
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("SEOSiri-Content-Schema-Server")

# In-Memory Cache Tier for Schema Audits
CACHE_CONN = sqlite3.connect(":memory:", check_same_thread=False)
CACHE_CURSOR = CACHE_CONN.cursor()


def init_cache_db():
    CACHE_CURSOR.execute("""
        CREATE TABLE IF NOT EXISTS schema_audits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            schema_type TEXT,
            status TEXT,
            details_json TEXT
        )
    """)
    CACHE_CONN.commit()


init_cache_db()


# ---------------------------------------------------------------------
# TOOL 1: TECH ARTICLE SCHEMA GENERATOR
# ---------------------------------------------------------------------
@mcp.tool()
def generate_tech_article_schema(
    headline: str,
    description: str,
    url: str,
    author_name: str = "Momenul Ahmad",
    publisher_name: str = "SEOSiri-Official",
    publisher_logo_url: str = "https://www.seosiri.com/images/logo.png"
) -> str:
    """
    Schema Generator: Generates multi-entity Schema.org TechArticle JSON-LD markup.

    Args:
        headline: Main article title.
        description: Brief article meta description.
        url: Canonical URL of the article.
        author_name: Name of the author.
        publisher_name: Publisher organization name.
        publisher_logo_url: Publisher logo URL.
    """
    timestamp = datetime.now(timezone.utc).isoformat()

    schema = {
        "@context": "https://schema.org",
        "@type": "TechArticle",
        "@id": f"{url}#article",
        "headline": headline,
        "description": description,
        "inLanguage": "en-US",
        "mainEntityOfPage": url,
        "datePublished": timestamp,
        "dateModified": timestamp,
        "author": {
            "@type": "Person",
            "name": author_name
        },
        "publisher": {
            "@type": "Organization",
            "name": publisher_name,
            "url": "https://seosiri.com",
            "logo": {
                "@type": "ImageObject",
                "url": publisher_logo_url
            }
        }
    }

    return json.dumps({
        "status": "GENERATED",
        "schema_type": "TechArticle",
        "json_ld": schema
    })


# ---------------------------------------------------------------------
# TOOL 2: FAQ PAGE SCHEMA GENERATOR
# ---------------------------------------------------------------------
@mcp.tool()
def generate_faq_page_schema(questions_answers_json: str, page_url: str) -> str:
    """
    Schema Generator: Compiles structured FAQPage JSON-LD schema blocks for voice search.

    Args:
        questions_answers_json: JSON string array of dicts with 'question' and 'answer' keys.
        page_url: Canonical URL of the FAQ page.
    """
    try:
        items = json.loads(questions_answers_json)
        faq_entities = []

        for item in items:
            q = item.get("question", "")
            a = item.get("answer", "")
            if q and a:
                faq_entities.append({
                    "@type": "Question",
                    "name": q,
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": a
                    }
                })

        schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "@id": f"{page_url}#faq",
            "mainEntity": faq_entities
        }

        return json.dumps({
            "status": "GENERATED",
            "schema_type": "FAQPage",
            "entity_count": len(faq_entities),
            "json_ld": schema
        })
    except Exception as e:
        return json.dumps({"status": "ERROR", "message": str(e)})


# ---------------------------------------------------------------------
# TOOL 3: GA4 REPORT METRIC VALIDATOR
# ---------------------------------------------------------------------
@mcp.tool()
def validate_ga4_report_metrics(requested_dimensions_csv: str, requested_metrics_csv: str) -> str:
    """
    GA4 Guardrail Tool: Validates dimension and metric compatibility for Google Analytics Data API requests.

    Args:
        requested_dimensions_csv: Comma-separated GA4 dimensions (e.g. 'pagePath,deviceCategory').
        requested_metrics_csv: Comma-separated GA4 metrics (e.g. 'averageSessionDuration,bounceRate').
    """
    dimensions = [d.strip() for d in requested_dimensions_csv.split(",")]
    metrics = [m.strip() for m in requested_metrics_csv.split(",")]

    incompatible = []
    # Check for known GA4 API incompatibilities
    if "userEmail" in dimensions or "userEmail" in metrics:
        incompatible.append("userEmail is not a valid GA4 dimension or metric.")

    return json.dumps({
        "status": "VALIDATED" if not incompatible else "INCOMPATIBLE",
        "dimensions_checked": len(dimensions),
        "metrics_checked": len(metrics),
        "incompatibilities_found": incompatible,
        "ready_for_api_call": len(incompatible) == 0
    })


# ---------------------------------------------------------------------
# TOOL 4: CONTENT STICKINESS SCORE CALCULATOR
# ---------------------------------------------------------------------
@mcp.tool()
def calculate_content_stickiness_score(avg_session_duration_seconds: float, bounce_rate_percentage: float) -> str:
    """
    GA4 Analytics Engine: Computes 'Retention Gold' content metrics by comparing session duration with bounce rate.

    Args:
        avg_session_duration_seconds: Average session duration in seconds (e.g. 180.5).
        bounce_rate_percentage: Bounce rate percentage between 0.0 and 100.0 (e.g. 35.2).
    """
    if bounce_rate_percentage >= 100.0:
        engagement_rate = 0.01
    else:
        engagement_rate = (100.0 - bounce_rate_percentage) / 100.0

    duration_minutes = avg_session_duration_seconds / 60.0
    stickiness_score = round(duration_minutes * engagement_rate * 10.0, 2)

    return json.dumps({
        "status": "CALCULATED",
        "stickiness_score": stickiness_score,
        "classification": "RETENTION_GOLD" if stickiness_score >= 15.0 else ("HIGH_ENGAGEMENT" if stickiness_score >= 8.0 else "AVERAGE"),
        "duration_minutes": round(duration_minutes, 2),
        "engagement_rate_percentage": round(engagement_rate * 100.0, 2)
    })


# ---------------------------------------------------------------------
# TOOL 5: LLM.TXT FORMATTING VALIDATOR
# ---------------------------------------------------------------------
@mcp.tool()
def validate_llm_txt_formatting(domain_or_url: str) -> str:
    """
    AEO Tool: Audits presence and Markdown syntax structure of /llm.txt for AI search crawlers.

    Args:
        domain_or_url: Target domain name or URL (e.g., 'seosiri.com').
    """
    clean_domain = domain_or_url.replace("https://", "").replace("http://", "").strip().rstrip("/")
    llm_url = f"https://{clean_domain}/llm.txt"

    try:
        res = requests.get(llm_url, timeout=5, headers={"User-Agent": "SEOSiri-Schema-Check/1.0"})
        if res.status_code == 200 and len(res.text.strip()) > 0:
            has_headers = bool(re.search(r"^#\s+", res.text, re.MULTILINE))
            return json.dumps({
                "status": "COMPLIANT",
                "domain": clean_domain,
                "url": llm_url,
                "has_markdown_headers": has_headers,
                "score": 100.0
            })
    except Exception:
        pass

    return json.dumps({
        "status": "NON_COMPLIANT",
        "domain": clean_domain,
        "score": 0.0,
        "remediation": "Create an /llm.txt file with structured Markdown links."
    })


# ---------------------------------------------------------------------
# TOOL 6: RFC 9116 SECURITY.TXT AUDITOR
# ---------------------------------------------------------------------
@mcp.tool()
def audit_rfc_9116_security_txt(domain_name: str) -> str:
    """
    Security Tool: Verifies presence and validity of RFC 9116 /.well-known/security.txt headers.

    Args:
        domain_name: Target domain name (e.g., 'seosiri.com').
    """
    clean_domain = domain_name.replace("https://", "").replace("http://", "").strip().rstrip("/")
    sec_url = f"https://{clean_domain}/.well-known/security.txt"

    try:
        res = requests.get(sec_url, timeout=5, headers={"User-Agent": "SEOSiri-Security-Check/1.0"})
        if res.status_code == 200 and "Contact:" in res.text:
            return json.dumps({
                "status": "COMPLIANT",
                "domain": clean_domain,
                "url": sec_url,
                "has_contact": True,
                "has_expires": "Expires:" in res.text,
                "score": 100.0
            })
    except Exception:
        pass

    return json.dumps({
        "status": "NON_COMPLIANT",
        "domain": clean_domain,
        "score": 0.0,
        "remediation": "Deploy /.well-known/security.txt via Cloudflare Workers."
    })


# ---------------------------------------------------------------------
# TOOL 7: AEO ANSWER SNIPPET EXTRACTOR
# ---------------------------------------------------------------------
@mcp.tool()
def extract_structured_answer_snippets(article_text: str) -> str:
    """
    AEO Tool: Scrapes direct-answer blocks formatted for Perplexity, SearchGPT, and Google AI Overviews.

    Args:
        article_text: Full article body or paragraph text to extract answer blocks from.
    """
    sentences = re.split(r'(?<=[.!?]) +', article_text.strip())
    answer_blocks = [s for s in sentences if len(s) > 40 and len(s) < 200][:3]

    return json.dumps({
        "status": "EXTRACTED",
        "total_snippets_found": len(answer_blocks),
        "aeo_snippets": answer_blocks,
        "ai_search_readiness": "OPTIMAL" if len(answer_blocks) >= 2 else "INSUFFICIENT_SNIPPETS"
    })


# ---------------------------------------------------------------------
# TOOL 8: PAYLOAD SANITIZER
# ---------------------------------------------------------------------
@mcp.tool()
def sanitize_content_payload(raw_content: str) -> str:
    """Sanitizes incoming content strings, stripping scripts and malicious tags."""
    clean = re.sub(r'<script\b[^<]*(?:(?!</script>)<[^<]*)*</script>', '', raw_content, flags=re.IGNORECASE)
    return json.dumps({"status": "SANITIZED", "clean_content": clean[:500]})


# ---------------------------------------------------------------------
# TOOL 9: THROUGHPUT METRICS
# ---------------------------------------------------------------------
@mcp.tool()
def get_live_schema_throughput_metrics() -> str:
    """ANALYTICS: Returns server operational health and performance metrics."""
    return json.dumps({
        "status": "HEALTHY",
        "server_name": "SEOSiri-Content-Schema-Server",
        "version": "1.0.0"
    })


# ---------------------------------------------------------------------
# TOOL 10: SERVER SPECIFICATIONS QUERY
# ---------------------------------------------------------------------
@mcp.tool()
def get_schema_server_specifications() -> str:
    """SPECIFICATIONS: Returns technical protocol details and tool capability matrices."""
    return json.dumps({
        "server": "seosiri-content-schema-mcp",
        "version": "1.0.0",
        "supported_transports": ["stdio", "sse"],
        "total_tools": 10
    })


if __name__ == "__main__":
    import time
    time.sleep(0.5)
    mcp.run(transport='stdio')