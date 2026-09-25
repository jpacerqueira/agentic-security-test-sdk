# Tests

Markup index of the Macro-Search - Agentic Security Scan suite. Latest numbers: [RESULTS.md](RESULTS.md). Version **0.0.1**.

Suite: `pytest -v -W error::DeprecationWarning`  
Where: original Compose container `agentic-security-test-sdk-agentic-security`  
Python 3.12.14 · pytest 9.1.1 · 2026-09-22 · **110.15s**

| File | Tests | Role |
|---|---|---|
| `test_github_examples.py` | 16 | GitHub zip → examples/; landing picker; no run-page mode toggle; progress/status; artifacts from disk |
| `test_grounding.py` | 12 | Ultra-Professional entitlements; scrape pack; launch-only checkbox; Client name default |
| `test_llm.py` | 9 | OpenAI-compat id, LiteLlm prefix, venv gemma4 defaults, gateway profiles, UTC `/v1` logs |
| `test_output_pdf.py` | 2 | PDF order; WeasyPrint A4 pack |
| `test_pentest_depth.py` | 6 | WSTG matrix, OWASP results, clean-tree HTML, JS eval, LLM merge without dropping AS-ids |
| `test_pipeline.py` | 8 | Plans, scanners, Professional run, launch Client name, consecutive det→LLM→det, gates 1–6 |
| `test_reports_complete.py` | 5 | Access/ASVS/risk/issues, JSON parse, skip_llm toggle, backfill |
| `test_run_mode.py` | 2 | skip_llm false is LLM; skip_llm fixed at run creation |

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
| 13 | `test_github_examples.py` | `test_landing_does_not_preselect_sample` | **passed** | No Target URL; empty source_path; landing toggle present |
| 14 | `test_github_examples.py` | `test_create_run_requires_source_tree` | **passed** | Launch 400 without a card |
| 15 | `test_github_examples.py` | `test_run_page_has_no_mode_toggle` | **passed** | No `#run-skip-llm`; `POST /mode` 404 |
| 16 | `test_github_examples.py` | `test_artifacts_listed_from_disk` | **passed** | `GET /runs/{id}/artifacts` lists JSON on disk |
| 17 | `test_grounding.py` | `test_ultra_professional_has_grounding_report` | **passed** | Ultra-Professional has `llm-grounding.html` |
| 18 | `test_grounding.py` | `test_ultra_professional_inherits_professional_grc` | **passed** | Risk/issues/access flags on Ultra-Professional |
| 19 | `test_grounding.py` | `test_collect_grounding_from_sample` | **passed** | Sample tree yields G- facts |
| 20 | `test_grounding.py` | `test_collect_grounding_includes_github_meta` | **passed** | GitHub meta becomes a fact |
| 21 | `test_grounding.py` | `test_fetch_github_meta_rejects_non_github_host` | **passed** | No fetch to a client-supplied host |
| 22 | `test_grounding.py` | `test_collect_grounding_for_run_uses_api_github_only` | **passed** | Outbound host is api.github.com |
| 23 | `test_grounding.py` | `test_ultra_pipeline_writes_grounding_pack` | **passed** | Flag on writes `grounding.json` + HTML |
| 24 | `test_grounding.py` | `test_ultra_without_checkbox_skips_grounding_json` | **passed** | Flag off skips scrape; HTML callout |
| 25 | `test_grounding.py` | `test_landing_shows_ultra_professional_and_hidden_grounding` | **passed** | Fourth plan card; `#grounding-field` |
| 26 | `test_grounding.py` | `test_create_run_ignores_grounding_on_lower_tiers` | **passed** | Tamper on Essentials ignored |
| 27 | `test_grounding.py` | `test_create_run_honours_grounding_on_ultra` | **passed** | Ultra-Professional flag + run badge |
| 28 | `test_grounding.py` | `test_create_run_blank_client_defaults_to_client` | **passed** | Blank launch name becomes `Client` |
| 29 | `test_llm.py` | `test_openai_compat_model_id` | **passed** | LiteLlm id is `openai/<tag>` |
| 30 | `test_llm.py` | `test_build_llm_uses_openai_prefix` | **passed** | Prefix; `build_llm()` when ADK present |
| 31 | `test_llm.py` | `test_code_defaults_gemma4_ollama` | **passed** | Host-venv defaults: engine ollama, gemma4, context 131072 |
| 32 | `test_llm.py` | `test_ollama_native_base_strips_v1` | **passed** | `/v1` stripped for host-venv `/api/generate` warm |
| 33 | `test_llm.py` | `test_openai_v1_urls_and_file_log` | **passed** | `/v1` URLs; `openai-v1.log` + `agentic-security.log`; UTC `Z` |
| 34 | `test_llm.py` | `test_utc_iso_ms_has_milliseconds` | **passed** | `utc_iso_ms()` is `…T…SSS Z` |
| 35 | `test_llm.py` | `test_uses_ollama_native_warm_skips_gateway` | **passed** | Native warm off for `gateway` / `llm-gateway` URL |
| 36 | `test_llm.py` | `test_compose_routes_app_through_llm_gateway` | **passed** | Compose `llm-gateway:4000/v1`; four profiles; timing callback |
| 37 | `test_llm.py` | `test_warm_model_uses_chat_completions_on_gateway` | **passed** | Gateway warm is `POST /v1/chat/completions`, not `/api/generate` |
| 38 | `test_output_pdf.py` | `test_pdf_order_starts_with_executive_summary` | **passed** | PDF order; no iframe pack |
| 39 | `test_output_pdf.py` | `test_output_pdf_is_a4_pack` | **passed** | WeasyPrint `%PDF` output-report.pdf |
| 40 | `test_pentest_depth.py` | `test_appsec_emits_wstg_matrix_and_owasp_results` | **passed** | Nine WSTG families; A1–A10 results; PoC; SSRF/TLS/pickle |
| 41 | `test_pentest_depth.py` | `test_clean_js_tree_still_has_full_matrix` | **passed** | Zero AS-ids still emit not-observed / not-applicable rows |
| 42 | `test_pentest_depth.py` | `test_js_eval_emits_finding` | **passed** | JS `eval` becomes AS-001 with evidence |
| 43 | `test_pentest_depth.py` | `test_pentest_html_has_required_depth_on_clean_tree` | **passed** | §6.1 / A10 / §5.2 / personnel; no sample-vendor names |
| 44 | `test_pentest_depth.py` | `test_keep_longer_prefers_deterministic_when_llm_is_stub` | **passed** | Short LLM replies do not wipe deterministic prose |
| 45 | `test_pentest_depth.py` | `test_llm_enrich_merges_without_dropping_ids` | **passed** | Enrich adds recs; AS-ids remain |
| 46 | `test_pipeline.py` | `test_professional_has_full_report` | **passed** | Professional vs Essentials reports |
| 47 | `test_pipeline.py` | `test_scope_discovers_example` | **passed** | Scope reads sample-web-api |
| 48 | `test_pipeline.py` | `test_appsec_flags_pickle_and_tls` | **passed** | AS- ids, evidence, WSTG, Top 10 |
| 49 | `test_pipeline.py` | `test_jailbreak_catalogue_has_six_probes` | **passed** | Six probe families |
| 50 | `test_pipeline.py` | `test_gates_are_integers_one_to_six` | **passed** | `gate_1`…`gate_6`; 4.5→5, 5→6 |
| 51 | `test_pipeline.py` | `test_pipeline_auto_approves` | **passed** | Full Professional deterministic run; default Client |
| 52 | `test_pipeline.py` | `test_reports_use_launch_client_name` | **passed** | Custom launch name in HTML cover |
| 53 | `test_pipeline.py` | `test_consecutive_deterministic_then_llm_then_deterministic` | **passed** | Three successive runs complete after mode flips |
| 54 | `test_reports_complete.py` | `test_access_inventory_is_not_a_stub` | **passed** | Identities, reviews, JML |
| 55 | `test_reports_complete.py` | `test_asvs_and_risk_and_issues_complete` | **passed** | 14 ASVS chapters, residual, ISS-001 |
| 56 | `test_reports_complete.py` | `test_classify_refusal_and_json_parse` | **passed** | Refusal helper + JSON fence |
| 57 | `test_reports_complete.py` | `test_parse_skip_llm_toggle` | **passed** | true/false/1 |
| 58 | `test_reports_complete.py` | `test_backfill_rewrites_access_report` | **passed** | Backfill identity inventory HTML |
| 59 | `test_run_mode.py` | `test_parse_skip_llm_false_is_llm` | **passed** | `false` means LLM |
| 60 | `test_run_mode.py` | `test_skip_llm_is_fixed_at_run_creation` | **passed** | skip_llm written at create; no apply_mode |

**60 passed · 0 failed · 0 skipped · 0 errors** (original Compose container, 2026-09-22)
