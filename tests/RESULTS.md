# Test results

Suite: `pytest -v -W error::DeprecationWarning`  
Root: `/Users/joaocerqueira/Documents/git/micro-cosmos/agentic-security-test-sdk`  
Product version: **0.0.1**

## Original Compose container (source of truth)

Image: `agentic-security-test-sdk-agentic-security`  
Python: 3.12.14 · pytest 9.1.1  
Run: 2026-09-17 · **14 passed, 0 failed, 0 skipped** · 31.14s

| # | File | Test | Result | What it proves |
|---|---|---|---|---|
| 1 | `test_llm.py` | `test_openai_compat_model_id` | **passed** | ADK LiteLlm model id is `openai/<tag>` for reasoning and fast roles |
| 2 | `test_llm.py` | `test_build_llm_uses_openai_prefix` | **passed** | Prefix contract; `build_llm()` when google-adk is present |
| 3 | `test_output_pdf.py` | `test_pdf_order_starts_with_executive_summary` | **passed** | `reports_for_pdf` leads with executive summary; omits iframe pack |
| 4 | `test_output_pdf.py` | `test_output_pdf_is_a4_pack` | **passed** | WeasyPrint writes `%PDF` `output-report.pdf` after a Professional run |
| 5 | `test_pipeline.py` | `test_professional_has_full_report` | **passed** | Professional includes `full-security-report.html`; Essentials does not |
| 6 | `test_pipeline.py` | `test_scope_discovers_example` | **passed** | Scope discovery reads `examples/sample-web-api` |
| 7 | `test_pipeline.py` | `test_appsec_flags_pickle_and_tls` | **passed** | AppSec flags pickle/TLS, unique `AS-` ids, evidence, WSTG + OWASP Top 10 |
| 8 | `test_pipeline.py` | `test_jailbreak_catalogue_has_six_probes` | **passed** | Six probe families always present |
| 9 | `test_pipeline.py` | `test_pipeline_auto_approves` | **passed** | Full Professional run: personnel, AS-001, access inventory, jailbreak rubric, residual risk, ISS-, ASVS V2 |
| 10 | `test_reports_complete.py` | `test_access_inventory_is_not_a_stub` | **passed** | Access pack has identities, reviews, JML |
| 11 | `test_reports_complete.py` | `test_asvs_and_risk_and_issues_complete` | **passed** | 14 ASVS chapters, residual risk, ISS-001 due date |
| 12 | `test_reports_complete.py` | `test_classify_refusal_and_json_parse` | **passed** | Jailbreak verdict helper + JSON fence parse |
| 13 | `test_reports_complete.py` | `test_parse_skip_llm_toggle` | **passed** | `true`/`false`/`1` map to skip_llm |
| 14 | `test_reports_complete.py` | `test_backfill_rewrites_access_report` | **passed** | Older run JSON rewritten to identity-inventory HTML |

### HTTP smoke (same container)

- `GET /healthz` → 200
- Login `demo` / `demobxyz` then `GET /runs/55c27510/output-report.pdf` → 200, `%PDF-1.7`, 81860 bytes
- Reports tab **Generate output report** enabled after HTML files load (executive-summary.html first), button shows “Building A4 PDF…” then restores

## Host venv (macOS, no Pango)

Python 3.13.1 · **13 passed** (`test_output_pdf_is_a4_pack` needs system Pango/cairo; that write path is covered in Compose)

## Totals (Compose)

| Result | Count |
|---|---|
| passed | 14 |
| failed | 0 |
| skipped | 0 |
| errors | 0 |

## Re-run

```bash
docker compose up --build -d
docker compose exec agentic-security pytest -v
```
