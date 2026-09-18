# Test results

Suite: `pytest -v -W error::DeprecationWarning`  
Root: `/Users/joaocerqueira/Documents/git/micro-cosmos/agentic-security-test-sdk`  
Product version: **0.0.1**

## Original Compose container (source of truth)

Image: `agentic-security-test-sdk-agentic-security`  
Python: 3.12.14 · pytest 9.1.1  
Run: 2026-09-18 · **54 passed, 0 failed, 0 skipped** · **140.27s**

See [README.md](README.md) for the 54-row grid.

## Totals (Compose)

| Result | Count |
|---|---|
| passed | 54 |
| failed | 0 |
| skipped | 0 |
| errors | 0 |

## Live smoke (same stack, after llm-gateway)

- `llm-gateway` healthy on **4000**; app **8090**; `GET /healthz` **200**
- `GET http://127.0.0.1:4000/v1/models` (Bearer `sk-agentic-local`) lists `gemma4:latest`
- `POST /v1/chat/completions` ping wrote `./logs/llm-gateway.log` with `call_start` / `call_end` / `duration_ms` / `upstream_ms` / `overhead_ms`
- App logs use UTC ms (`…Z`) in `./logs/openai-v1.log` and `./logs/agentic-security.log`
- Landing `/` has four plan cards including Ultra-Professional; `#grounding-field` is Ultra-Professional only
- Run page has no `#run-skip-llm`; header `.mode-badge` is text only; `POST /runs/{id}/mode` → **404**

## Re-run

```bash
docker compose up --build -d
docker compose exec agentic-security pytest -v -W error::DeprecationWarning
```
