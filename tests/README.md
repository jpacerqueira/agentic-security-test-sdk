# Tests

Markup index of the Macro-Search - Agentic Security Scan suite. Latest numbers: [RESULTS.md](RESULTS.md). Version **0.0.1**.

| File | Tests | Role |
|---|---|---|
| `test_llm.py` | 2 | OpenAI-compat `openai/<tag>` id; LiteLlm prefix when ADK is installed |
| `test_pipeline.py` | 5 | Plans, scanners, end-to-end auto-approved Professional run |
| `test_reports_complete.py` | 5 | Access/ASVS/risk/issues completeness, JSON parse, skip_llm toggle, backfill of run `55c27510` |
| `test_output_pdf.py` | 2 | PDF order (executive summary first); WeasyPrint A4 pack `%PDF` |

| Test | Result (Compose image, 2026-09-17) |
|---|---|
| `test_openai_compat_model_id` | passed |
| `test_build_llm_uses_openai_prefix` | passed |
| `test_pdf_order_starts_with_executive_summary` | passed |
| `test_output_pdf_is_a4_pack` | passed |
| `test_professional_has_full_report` | passed |
| `test_scope_discovers_example` | passed |
| `test_appsec_flags_pickle_and_tls` | passed |
| `test_jailbreak_catalogue_has_six_probes` | passed |
| `test_pipeline_auto_approves` | passed |
| `test_access_inventory_is_not_a_stub` | passed |
| `test_asvs_and_risk_and_issues_complete` | passed |
| `test_classify_refusal_and_json_parse` | passed |
| `test_parse_skip_llm_toggle` | passed |
| `test_backfill_rewrites_access_report` | passed |

**14 passed · 0 failed · 0 skipped** (original Compose container)
