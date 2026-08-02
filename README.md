# seosiri-content-schema-mcp

> 📖 **Official Architecture & Documentation:** [SEOSiri Content Schema Guide](https://seosiri.com) | [Central MCP Directory](https://seosiri.com)

An open-source, local-first Model Context Protocol (MCP) server for **Automated Schema.org JSON-LD Generation, GA4 Metric Validation, /llm.txt Auditing, and Content Stickiness Analytics**.

## 💖 Sponsorship, B2B Custom Solutions & Attribution

### 👨‍💻 Lead Architect & Attribution
Designed and engineered by **[Momenul Ahmad](https://github.com)**, Lead Architect and Founder of **[SEOSiri](https://seosiri.com)**.

### 🚀 Capabilities & Tools (10 Production Tools)
- **`generate_tech_article_schema`**: Generates multi-entity TechArticle JSON-LD markup.
- **`generate_faq_page_schema`**: Compiles structured FAQPage JSON-LD schema blocks for voice search.
- **`validate_ga4_report_metrics`**: Validates GA4 metric and dimension compatibility.
- **`calculate_content_stickiness_score`**: Computes GA4 "Retention Gold" scores comparing Duration against Bounce Rate.
- **`validate_llm_txt_formatting`**: Audits presence and Markdown syntax structure of `/llm.txt`.
- **`audit_rfc_9116_security_txt`**: Audits RFC 9116 `/.well-known/security.txt` headers.
- **`extract_structured_answer_snippets`**: Extracts direct-answer snippets for Perplexity and SearchGPT.
- **`sanitize_content_payload`**: Strips script injections and unverified metadata.
- **`get_live_schema_throughput_metrics`**: Monitors system health and processing latency.
- **`get_schema_server_specifications`**: Returns protocol specs and capability matrices.

## Quickstart

```bash
pip install -e .
pytest tests/test_content_schema.py
```

### 🔌 Claude Desktop / Cursor Configuration
Add this block to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "seosiri-content-schema": {
      "command": "uv",
      "args": [
        "run",
        "--github",
        "SEOSiri-Official/content-schema-mcp",
        "src/main_server.py"
      ]
    }
  }
}
```

## License
Distributed under the MIT License. See [LICENSE](https://github.com/SEOSiri-Official/content-schema-mcp/blob/main/LICENSE) for more information.
