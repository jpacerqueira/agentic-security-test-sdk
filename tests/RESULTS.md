# Test results

Suite: `pytest -v -W error::DeprecationWarning`  
Root: `/Users/joaocerqueira/Documents/git/micro-cosmos/agentic-security-test-sdk`  
Product version: **0.0.1**

## Original Compose container (source of truth)

Image: `agentic-security-test-sdk-agentic-security`  
Python: 3.12.14 · pytest 9.1.1  
Run: 2026-09-17 · **34 passed, 0 failed, 0 skipped** · 42.28s

See [README.md](README.md) for the 34-row grid.

## Totals (Compose)

| Result | Count |
|---|---|
| passed | 34 |
| failed | 0 |
| skipped | 0 |
| errors | 0 |

## Live smoke (same container, after rebuild)

- `POST /login` 303; landing contains **Source from new URL REPO**, no Target URL, empty `source_path`, no pre-selected example card
- `POST /runs/8f2cedbc/mode` `skip_llm=false` → **200** `{"skip_llm":false,"mode":"llm"}` (was 500 `PipelineEvent` NameError)
- `POST /examples/fetch-github` `https://evil.com/owner/repo` → **400**

## Re-run

```bash
docker compose up --build -d
docker compose exec agentic-security pytest -v -W error::DeprecationWarning
```
