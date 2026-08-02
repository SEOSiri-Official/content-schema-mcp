# tests/test_content_schema.py
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main_server import (
    generate_tech_article_schema,
    generate_faq_page_schema,
    validate_ga4_report_metrics,
    calculate_content_stickiness_score,
    validate_llm_txt_formatting,
    audit_rfc_9116_security_txt,
    extract_structured_answer_snippets,
    sanitize_content_payload,
    get_live_schema_throughput_metrics,
    get_schema_server_specifications
)


def test_1_tech_article_schema():
    res = json.loads(generate_tech_article_schema("Headline", "Description", "https://seosiri.com/test.html"))
    assert res["status"] == "GENERATED"
    assert res["json_ld"]["@type"] == "TechArticle"


def test_2_faq_page_schema():
    qa_data = json.dumps([{"question": "Q1?", "answer": "A1."}])
    res = json.loads(generate_faq_page_schema(qa_data, "https://seosiri.com/faq.html"))
    assert res["status"] == "GENERATED"
    assert res["entity_count"] == 1


def test_3_ga4_metrics_validation():
    res = json.loads(validate_ga4_report_metrics("pagePath", "averageSessionDuration"))
    assert res["status"] == "VALIDATED"
    assert res["ready_for_api_call"] is True


def test_4_content_stickiness():
    res = json.loads(calculate_content_stickiness_score(180.0, 30.0))
    assert res["status"] == "CALCULATED"
    assert res["classification"] == "RETENTION_GOLD"


def test_5_llm_txt_formatting():
    res = json.loads(validate_llm_txt_formatting("seosiri.com"))
    assert "status" in res


def test_6_security_txt_audit():
    res = json.loads(audit_rfc_9116_security_txt("seosiri.com"))
    assert "status" in res


def test_7_answer_snippets_extraction():
    text = "SEOSiri is an open-source research initiative. It builds local-first MCP servers. Every server is fully open-source."
    res = json.loads(extract_structured_answer_snippets(text))
    assert res["status"] == "EXTRACTED"


def test_8_sanitize_payload():
    res = json.loads(sanitize_content_payload("<div>content</div>"))
    assert res["status"] == "SANITIZED"


def test_9_throughput_metrics():
    res = json.loads(get_live_schema_throughput_metrics())
    assert res["status"] == "HEALTHY"


def test_10_server_specs():
    res = json.loads(get_schema_server_specifications())
    assert res["total_tools"] == 10