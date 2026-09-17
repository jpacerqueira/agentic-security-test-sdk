# Test results

Suite: `pytest -v -W error::DeprecationWarning`  
Root: `/Users/joaocerqueira/Documents/git/micro-cosmos/agentic-security-test-sdk`  
Product version: **0.0.1**

## Original Compose container (source of truth)

Image: `agentic-security-test-sdk-agentic-security`  
Python: 3.12.14 · pytest 9.1.1  
Run: 2026-09-17 · **48 passed, 0 failed, 0 skipped** · 30.55s

See [README.md](README.md) for the 48-row grid.

## Totals (Compose)

| Result | Count |
|---|---|
| passed | 48 |
| failed | 0 |
| skipped | 0 |
| errors | 0 |

## Live smoke (same container, after rebuild)

- Landing `/` has four plan cards including Ultra-Professional; `#grounding-field` is Ultra-Professional only
- Launch form Client name defaults to `Client`; reports use that name (or the value filled at start)
- Run page has no `#run-skip-llm` / `.skip-llm-toggle`; header `.mode-badge` is text only
- `POST /runs/{id}/mode` → **404**
- `#run-status` below gates: red/orange flash **Running** (1.4s) in Deterministic and LLM; green **Completed — Deterministic** after auto-approve
- `./logs/openai-v1.log` maps `GET /v1/models` and `POST /v1/chat/completions` (no prompt bodies)

## Re-run

```bash
docker compose up --build -d
docker compose exec agentic-security pytest -v -W error::DeprecationWarning
```
