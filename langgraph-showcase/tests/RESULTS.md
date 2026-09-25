# Test results

Suite: `docker compose run --no-deps --rm agentic-security pytest -v`  
Root: `langgraph-showcase/` inside `public-git/agentic-security-test-sdk`  
Product version: **0.0.1**  
Stack: LangGraph + LangChain `ChatOpenAI` + this folder’s LiteLLM gateway (default `ollama` / `gemma4:latest`)

## This folder’s Compose image (source of truth)

Image: `langgraph-showcase-agentic-security`  
Python: 3.12.14 · pytest 9.1.1  
Run: 2026-09-25 · **63 passed, 0 failed, 0 skipped** · **39.68s**

See [README.md](README.md) for the 63-row grid. Three tests are LangGraph-only (`test_graph.py`).

## Totals

| Result | Count |
|---|---|
| passed | 63 |
| failed | 0 |
| skipped | 0 |
| errors | 0 |

## What the LLM tests cover

- Gateway model id is the bare alias `gemma4:latest` (not `openai/<tag>`)
- `build_chat_model()` points `ChatOpenAI` at `http://llm-gateway:4000/v1`
- Consecutive det→LLM→det path completed with the LangGraph stack mocked
- Gateway warm is `POST /v1/chat/completions`

## Re-run

From this folder only (do not start `google-cloud-showcase` at the same time; both bind 8090 and 4000):

```bash
docker compose build agentic-security
docker compose run --no-deps --rm agentic-security pytest -v
```
