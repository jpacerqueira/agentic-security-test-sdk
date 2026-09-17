# Tests

Markup index of the Macro-Search - Agentic Security Scan suite. Latest numbers: [RESULTS.md](RESULTS.md). Version **0.0.1**.

Suite: `pytest -v -W error::DeprecationWarning`  
Where: original Compose container `agentic-security-test-sdk-agentic-security`  
Python 3.12.14 · pytest 9.1.1 · 2026-09-17 · **30.55s**

| File | Tests | Role |
|---|---|---|
| `test_github_examples.py` | 15 | GitHub zip → examples/; landing picker; run page has no mode toggle; `#run-progress` / `#run-status` |
| `test_grounding.py` | 12 | Ultra-Professional entitlements; scrape pack; launch-only checkbox; Client name default |
| `test_llm.py` | 5 | OpenAI-compat id, LiteLlm prefix, Compose gemma4 defaults, Ollama native base, `/v1` log file |
| `test_pipeline.py` | 8 | Plans, scanners, Professional run, launch Client name, consecutive det→LLM→det, gates 1–6 |
| `test_reports_complete.py` | 5 | Access/ASVS/risk/issues, JSON parse, skip_llm toggle, backfill |
| `test_output_pdf.py` | 2 | PDF order; WeasyPrint A4 pack |
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
| 16 | `test_grounding.py` | `test_ultra_professional_has_grounding_report` | **passed** | Ultra-Professional has `llm-grounding.html` |
| 17 | `test_grounding.py` | `test_ultra_professional_inherits_professional_grc` | **passed** | Risk/issues/access flags on Ultra-Professional |
| 18 | `test_grounding.py` | `test_collect_grounding_from_sample` | **passed** | Sample tree yields G- facts |
| 19 | `test_grounding.py` | `test_collect_grounding_includes_github_meta` | **passed** | GitHub meta becomes a fact |
| 20 | `test_grounding.py` | `test_fetch_github_meta_rejects_non_github_host` | **passed** | No fetch to a client-supplied host |
| 21 | `test_grounding.py` | `test_collect_grounding_for_run_uses_api_github_only` | **passed** | Outbound host is api.github.com |
| 22 | `test_grounding.py` | `test_ultra_pipeline_writes_grounding_pack` | **passed** | Flag on writes `grounding.json` + HTML |
| 23 | `test_grounding.py` | `test_ultra_without_checkbox_skips_grounding_json` | **passed** | Flag off skips scrape; HTML callout |
| 24 | `test_grounding.py` | `test_landing_shows_ultra_professional_and_hidden_grounding` | **passed** | Fourth plan card; `#grounding-field` |
| 25 | `test_grounding.py` | `test_create_run_ignores_grounding_on_lower_tiers` | **passed** | Tamper on Essentials ignored |
| 26 | `test_grounding.py` | `test_create_run_honours_grounding_on_ultra` | **passed** | Ultra-Professional flag + run badge |
| 27 | `test_grounding.py` | `test_create_run_blank_client_defaults_to_client` | **passed** | Blank launch name becomes `Client` |
| 28 | `test_llm.py` | `test_openai_compat_model_id` | **passed** | LiteLlm id is `openai/<tag>` |
| 29 | `test_llm.py` | `test_build_llm_uses_openai_prefix` | **passed** | Prefix; `build_llm()` when ADK present |
| 30 | `test_llm.py` | `test_compose_ollama_defaults_gemma4` | **passed** | engine ollama, gemma4:latest, context 131072 |
| 31 | `test_llm.py` | `test_ollama_native_base_strips_v1` | **passed** | `/v1` stripped for `/api/generate` warm |
| 32 | `test_llm.py` | `test_openai_v1_urls_and_file_log` | **passed** | `/v1/models` + `/v1/chat/completions` URLs; `openai-v1.log` |
| 33 | `test_output_pdf.py` | `test_pdf_order_starts_with_executive_summary` | **passed** | PDF order; no iframe pack |
| 34 | `test_output_pdf.py` | `test_output_pdf_is_a4_pack` | **passed** | WeasyPrint `%PDF` output-report.pdf |
| 35 | `test_pipeline.py` | `test_professional_has_full_report` | **passed** | Professional vs Essentials reports |
| 36 | `test_pipeline.py` | `test_scope_discovers_example` | **passed** | Scope reads sample-web-api |
| 37 | `test_pipeline.py` | `test_appsec_flags_pickle_and_tls` | **passed** | AS- ids, evidence, WSTG, Top 10 |
| 38 | `test_pipeline.py` | `test_jailbreak_catalogue_has_six_probes` | **passed** | Six probe families |
| 39 | `test_pipeline.py` | `test_gates_are_integers_one_to_six` | **passed** | `gate_1`…`gate_6`; 4.5→5, 5→6 |
| 40 | `test_pipeline.py` | `test_pipeline_auto_approves` | **passed** | Full Professional deterministic run; default Client |
| 41 | `test_pipeline.py` | `test_reports_use_launch_client_name` | **passed** | Custom launch name in HTML cover |
| 42 | `test_pipeline.py` | `test_consecutive_deterministic_then_llm_then_deterministic` | **passed** | Three successive runs complete after mode flips |
| 43 | `test_reports_complete.py` | `test_access_inventory_is_not_a_stub` | **passed** | Identities, reviews, JML |
| 44 | `test_reports_complete.py` | `test_asvs_and_risk_and_issues_complete` | **passed** | 14 ASVS chapters, residual, ISS-001 |
| 45 | `test_reports_complete.py` | `test_classify_refusal_and_json_parse` | **passed** | Refusal helper + JSON fence |
| 46 | `test_reports_complete.py` | `test_parse_skip_llm_toggle` | **passed** | true/false/1 |
| 47 | `test_reports_complete.py` | `test_backfill_rewrites_access_report` | **passed** | Backfill identity inventory HTML |
| 48 | `test_run_mode.py` | `test_parse_skip_llm_false_is_llm` | **passed** | `false` means LLM |
| 49 | `test_run_mode.py` | `test_skip_llm_is_fixed_at_run_creation` | **passed** | skip_llm written at create; no apply_mode |

**49 passed · 0 failed · 0 skipped · 0 errors** (original Compose container)
