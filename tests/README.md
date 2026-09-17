# Tests

Markup index of the Macro-Search - Agentic Security Scan suite. Latest numbers: [RESULTS.md](RESULTS.md). Version **0.0.1**.

Suite: `pytest -v -W error::DeprecationWarning`  
Where: original Compose container `agentic-security-test-sdk-agentic-security`  
Python 3.12.14 · pytest 9.1.1 · 2026-09-17 · **31.90s**

| File | Tests | Role |
|---|---|---|
| `test_llm.py` | 4 | OpenAI-compat id, LiteLlm prefix, Compose gemma4 defaults, Ollama native base |
| `test_pipeline.py` | 6 | Plans, scanners, Professional run, consecutive det→LLM→det |
| `test_reports_complete.py` | 5 | Access/ASVS/risk/issues, JSON parse, skip_llm toggle, backfill |
| `test_output_pdf.py` | 2 | PDF order; WeasyPrint A4 pack |
| `test_run_mode.py` | 2 | skip_llm false is LLM; run-page apply_mode writes orch + meta |

| # | File | Test | Result | What it proves |
|---|---|---|---|---|
| 1 | `test_llm.py` | `test_openai_compat_model_id` | **passed** | LiteLlm id is `openai/<tag>` |
| 2 | `test_llm.py` | `test_build_llm_uses_openai_prefix` | **passed** | Prefix; `build_llm()` when ADK present |
| 3 | `test_llm.py` | `test_compose_ollama_defaults_gemma4` | **passed** | engine ollama, gemma4:latest, context 131072 |
| 4 | `test_llm.py` | `test_ollama_native_base_strips_v1` | **passed** | `/v1` stripped for `/api/generate` warm |
| 5 | `test_output_pdf.py` | `test_pdf_order_starts_with_executive_summary` | **passed** | PDF order; no iframe pack |
| 6 | `test_output_pdf.py` | `test_output_pdf_is_a4_pack` | **passed** | WeasyPrint `%PDF` output-report.pdf |
| 7 | `test_pipeline.py` | `test_professional_has_full_report` | **passed** | Professional vs Essentials reports |
| 8 | `test_pipeline.py` | `test_scope_discovers_example` | **passed** | Scope reads sample-web-api |
| 9 | `test_pipeline.py` | `test_appsec_flags_pickle_and_tls` | **passed** | AS- ids, evidence, WSTG, Top 10 |
| 10 | `test_pipeline.py` | `test_jailbreak_catalogue_has_six_probes` | **passed** | Six probe families |
| 11 | `test_pipeline.py` | `test_pipeline_auto_approves` | **passed** | Full Professional deterministic run |
| 12 | `test_pipeline.py` | `test_consecutive_deterministic_then_llm_then_deterministic` | **passed** | Three successive runs complete after mode flips |
| 13 | `test_reports_complete.py` | `test_access_inventory_is_not_a_stub` | **passed** | Identities, reviews, JML |
| 14 | `test_reports_complete.py` | `test_asvs_and_risk_and_issues_complete` | **passed** | 14 ASVS chapters, residual, ISS-001 |
| 15 | `test_reports_complete.py` | `test_classify_refusal_and_json_parse` | **passed** | Refusal helper + JSON fence |
| 16 | `test_reports_complete.py` | `test_parse_skip_llm_toggle` | **passed** | true/false/1 |
| 17 | `test_reports_complete.py` | `test_backfill_rewrites_access_report` | **passed** | Backfill identity inventory HTML |
| 18 | `test_run_mode.py` | `test_parse_skip_llm_false_is_llm` | **passed** | `false` means LLM |
| 19 | `test_run_mode.py` | `test_apply_run_mode_toggles_orchestrator` | **passed** | Run toggle writes orch.skip_llm + run_meta.json |

**19 passed · 0 failed · 0 skipped · 0 errors** (original Compose container)
