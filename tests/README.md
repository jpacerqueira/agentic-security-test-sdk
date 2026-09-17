# Tests

Markup index of the Macro-Search - Agentic Security Scan suite. Latest numbers: [RESULTS.md](RESULTS.md). Version **0.0.1**.

| File | Tests | Role |
|---|---|---|
| `test_pipeline.py` | 5 | Plans, scanners, end-to-end auto-approved Professional run |
| `test_reports_complete.py` | 5 | Access/ASVS/risk/issues completeness, JSON parse, skip_llm toggle, backfill of run `55c27510` |
| `test_llm.py` | 1 | ADK `LiteLlm` model prefix `openai/` (skipped if `[llm]` extra is not installed) |

| Test | Result (2026-09-17) |
|---|---|
| `test_build_llm_uses_openai_prefix` | skipped (no google-adk in local 3.13 venv; present in Docker `[llm]` image) |
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

**10 passed · 0 failed · 1 skipped**
