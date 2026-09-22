# Test results

Suite: `pytest -v -W error::DeprecationWarning`  
Root: `/Users/joaocerqueira/Documents/git/micro-cosmos/agentic-security-test-sdk`  
Product version: **0.0.1**

## Original Compose container (source of truth)

Image: `agentic-security-test-sdk-agentic-security`  
Python: 3.12.14 · pytest 9.1.1  
Run: 2026-09-22 · **60 passed, 0 failed, 0 skipped** · **110.15s**

See [README.md](README.md) for the 60-row grid.

## Totals (Compose)

| Result | Count |
|---|---|
| passed | 60 |
| failed | 0 |
| skipped | 0 |
| errors | 0 |

## Live smoke (same stack, after pentest-depth rebuild)

- `llm-gateway` healthy on **4000**; app **8090**; `GET /healthz` **200**
- Deterministic Professional auto-approve: 4 AS-ids, 9 WSTG rows, A1–A10 results, pentest HTML ~40k chars, A4 PDF **118744** bytes; no sample-vendor names in chrome
- Consecutive det→LLM→det pytest path (mocked ADK) completed
- Live gateway: `GET /v1/models` lists `gemma4:latest`; `ensure_llm_ready` warm OK; `generate_text("PONG")` returned `PONG` (long gemma4 prompts can exceed the previous `LLM_TIMEOUT=180`; proxy + app now wait **360s**)

## Re-run

```bash
docker compose up --build -d
docker compose exec agentic-security pytest -v -W error::DeprecationWarning
```
