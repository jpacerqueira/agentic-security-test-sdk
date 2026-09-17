# Tests

Markup index of the Macro-Search - Agentic Security Scan suite. Latest numbers: [RESULTS.md](RESULTS.md). Version **0.0.1**.

Suite: `pytest -v -W error::DeprecationWarning`  
Where: original Compose container `agentic-security-test-sdk-agentic-security`  
Python 3.12.14 · pytest 9.1.1 · 2026-09-17 · **42.28s**

| File | Tests | Role |
|---|---|---|
| `test_github_examples.py` | 15 | GitHub zip → examples/; landing picker; `POST /runs/{id}/mode` PipelineEvent |
| `test_llm.py` | 4 | OpenAI-compat id, LiteLlm prefix, Compose gemma4 defaults, Ollama native base |
| `test_pipeline.py` | 6 | Plans, scanners, Professional run, consecutive det→LLM→det |
| `test_reports_complete.py` | 5 | Access/ASVS/risk/issues, JSON parse, skip_llm toggle, backfill |
| `test_output_pdf.py` | 2 | PDF order; WeasyPrint A4 pack |
| `test_run_mode.py` | 2 | skip_llm false is LLM; run-page apply_mode writes orch + meta |

| # | File | Test | Result | What it proves |
|---|---|---|---|---|
| 1 | `test_github_examples.py` | `test_parse_github_url_accepts_https_github` | **passed** | owner/repo and /tree/ref parse |
| 2 | `test_github_examples.py` | `test_parse_github_url_rejects_ssrf_and_junk[https://evil.com/octocat/Hello-World]` | **passed** | Non-github.com host rejected |
| 3 | `test_github_examples.py` | `test_parse_github_url_rejects_ssrf_and_junk[http://github.com/octocat/Hello-World]` | **passed** | http:// rejected |
| 4 | `test_github_examples.py` | `test_parse_github_url_rejects_ssrf_and_junk[https://github.com/just-an-owner]` | **passed** | Incomplete path rejected |
| 5 | `test_github_examples.py` | `test_parse_github_url_rejects_ssrf_and_junk[ftp://github.com/octocat/Hello-World]` | **passed** | Non-https scheme rejected |
| 6 | `test_github_examples.py` | `test_parse_github_url_rejects_ssrf_and_junk[]` | **passed** | Empty URL rejected |
| 7 | `test_github_examples.py` | `test_extract_zip_strips_common_root` | **passed** | GitHub zip root prefix stripped |
| 8 | `test_github_examples.py` | `test_extract_zip_skips_path_traversal` | **passed** | `../` zip members skipped |
| 9 | `test_github_examples.py` | `test_extract_zip_bomb_rejected` | **passed** | Uncompressed size cap 413 |
| 10 | `test_github_examples.py` | `test_import_github_repo_writes_source_meta` | **passed** | `.source.json` github_url |
| 11 | `test_github_examples.py` | `test_fetch_github_rejects_non_github_host` | **passed** | `POST /examples/fetch-github` 400 |
| 12 | `test_github_examples.py` | `test_fetch_github_success_extracts_into_examples` | **passed** | Mocked fetch returns card JSON |
| 13 | `test_github_examples.py` | `test_landing_does_not_preselect_sample` | **passed** | No Target URL; empty source_path |
| 14 | `test_github_examples.py` | `test_create_run_requires_source_tree` | **passed** | Launch 400 without a card |
| 15 | `test_github_examples.py` | `test_set_run_mode_publishes_pipeline_event` | **passed** | `POST /mode` 200 + mode_changed |
| 16 | `test_llm.py` | `test_openai_compat_model_id` | **passed** | LiteLlm id is `openai/<tag>` |
| 17 | `test_llm.py` | `test_build_llm_uses_openai_prefix` | **passed** | Prefix; `build_llm()` when ADK present |
| 18 | `test_llm.py` | `test_compose_ollama_defaults_gemma4` | **passed** | engine ollama, gemma4:latest, context 131072 |
| 19 | `test_llm.py` | `test_ollama_native_base_strips_v1` | **passed** | `/v1` stripped for `/api/generate` warm |
| 20 | `test_output_pdf.py` | `test_pdf_order_starts_with_executive_summary` | **passed** | PDF order; no iframe pack |
| 21 | `test_output_pdf.py` | `test_output_pdf_is_a4_pack` | **passed** | WeasyPrint `%PDF` output-report.pdf |
| 22 | `test_pipeline.py` | `test_professional_has_full_report` | **passed** | Professional vs Essentials reports |
| 23 | `test_pipeline.py` | `test_scope_discovers_example` | **passed** | Scope reads sample-web-api |
| 24 | `test_pipeline.py` | `test_appsec_flags_pickle_and_tls` | **passed** | AS- ids, evidence, WSTG, Top 10 |
| 25 | `test_pipeline.py` | `test_jailbreak_catalogue_has_six_probes` | **passed** | Six probe families |
| 26 | `test_pipeline.py` | `test_pipeline_auto_approves` | **passed** | Full Professional deterministic run |
| 27 | `test_pipeline.py` | `test_consecutive_deterministic_then_llm_then_deterministic` | **passed** | Three successive runs complete after mode flips |
| 28 | `test_reports_complete.py` | `test_access_inventory_is_not_a_stub` | **passed** | Identities, reviews, JML |
| 29 | `test_reports_complete.py` | `test_asvs_and_risk_and_issues_complete` | **passed** | 14 ASVS chapters, residual, ISS-001 |
| 30 | `test_reports_complete.py` | `test_classify_refusal_and_json_parse` | **passed** | Refusal helper + JSON fence |
| 31 | `test_reports_complete.py` | `test_parse_skip_llm_toggle` | **passed** | true/false/1 |
| 32 | `test_reports_complete.py` | `test_backfill_rewrites_access_report` | **passed** | Backfill identity inventory HTML |
| 33 | `test_run_mode.py` | `test_parse_skip_llm_false_is_llm` | **passed** | `false` means LLM |
| 34 | `test_run_mode.py` | `test_apply_run_mode_toggles_orchestrator` | **passed** | Run toggle writes orch.skip_llm + run_meta.json |

**34 passed · 0 failed · 0 skipped · 0 errors** (original Compose container)
