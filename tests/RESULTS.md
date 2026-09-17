# Test results

Suite: `pytest -v`  
Root: `/Users/joaocerqueira/Documents/git/micro-cosmos/agentic-security-test-sdk`  
Python: 3.13.1 · pytest 9.1.1  
Run: 2026-09-17 · **10 passed, 0 failed, 1 skipped** · 1.19s  
Product version: **0.0.1**

| # | File | Test | Result | What it proves |
|---|---|---|---|---|
| 1 | `test_llm.py` | `test_build_llm_uses_openai_prefix` | **skipped** | Would assert ADK LiteLlm `openai/<tag>`; skip when `google-adk` is not in the local venv (Docker image installs `[llm]`) |
| 2 | `test_pipeline.py` | `test_professional_has_full_report` | **passed** | Professional tier includes `full-security-report.html`; Essentials does not |
| 3 | `test_pipeline.py` | `test_scope_discovers_example` | **passed** | Scope discovery reads `examples/sample-web-api` |
| 4 | `test_pipeline.py` | `test_appsec_flags_pickle_and_tls` | **passed** | AppSec flags pickle/TLS, unique `AS-` ids, evidence snippets, WSTG + OWASP Top 10 |
| 5 | `test_pipeline.py` | `test_jailbreak_catalogue_has_six_probes` | **passed** | Six probe families always present |
| 6 | `test_pipeline.py` | `test_pipeline_auto_approves` | **passed** | Full Professional run writes pentest (personnel, AS-001), access inventory, jailbreak rubric, risk residual, ISS- board, ASVS V2 |
| 7 | `test_reports_complete.py` | `test_access_inventory_is_not_a_stub` | **passed** | Access pack has identities, reviews, JML |
| 8 | `test_reports_complete.py` | `test_asvs_and_risk_and_issues_complete` | **passed** | 14 ASVS chapters, residual risk, ISS-001 due date |
| 9 | `test_reports_complete.py` | `test_classify_refusal_and_json_parse` | **passed** | Jailbreak verdict helper + JSON fence parse |
| 10 | `test_reports_complete.py` | `test_parse_skip_llm_toggle` | **passed** | `true`/`false`/`1` map to skip_llm |
| 11 | `test_reports_complete.py` | `test_backfill_rewrites_access_report` | **passed** | Older run JSON rewritten to identity-inventory HTML |

## Totals

| Result | Count |
|---|---|
| passed | 10 |
| failed | 0 |
| skipped | 1 |
| errors | 0 |

## Re-run

```bash
cd agentic-security-test-sdk
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -v
```
