# Tests

Markup index of the Macro-Search - Agentic Security Scan suite. Latest numbers: [RESULTS.md](RESULTS.md). Version **0.0.1**.

| File | Tests | Role |
|---|---|---|
| `test_llm.py` | 4 | OpenAI-compat id, LiteLlm prefix, Compose gemma4 defaults, Ollama native base |
| `test_pipeline.py` | 6 | Plans, scanners, Professional run, consecutive det→LLM→det |
| `test_reports_complete.py` | 5 | Access/ASVS/risk/issues, JSON parse, skip_llm toggle, backfill |
| `test_output_pdf.py` | 2 | PDF order; WeasyPrint A4 pack |
| `test_run_mode.py` | 2 | skip_llm false is LLM; run-page apply_mode writes orch + meta |

**19 passed · 0 failed · 0 skipped** (original Compose container, 2026-09-17)
