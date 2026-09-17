# Test results

Suite: `pytest -v -W error::DeprecationWarning`  
Root: `/Users/joaocerqueira/Documents/git/micro-cosmos/agentic-security-test-sdk`  
Product version: **0.0.1**

## Original Compose container (source of truth)

Image: `agentic-security-test-sdk-agentic-security`  
Python: 3.12.14 · pytest 9.1.1  
Run: 2026-09-17 · **47 passed, 0 failed, 0 skipped** · 33.31s

See [README.md](README.md) for the 47-row grid.

## Totals (Compose)

| Result | Count |
|---|---|
| passed | 47 |
| failed | 0 |
| skipped | 0 |
| errors | 0 |

## Live smoke (same container, after rebuild)

- Landing `/` has four plan cards including Ultra-Professional; `#grounding-field` is Ultra-Professional only
- Launch form Client name defaults to `Client`; reports use that name (or the value filled at start)
- Run page has no `#run-skip-llm` / `.skip-llm-toggle`; header `.mode-badge` is text only
- `POST /runs/{id}/mode` → **404**

## Re-run

```bash
docker compose up --build -d
docker compose exec agentic-security pytest -v -W error::DeprecationWarning
```
