---
name: langgraph-gateway
description: LLM mode uses LangGraph plus LangChain ChatOpenAI against this folder's Compose llm-gateway OpenAI /v1 (2026-09-25)
metadata:
  type: project
---

`Settings.build_chat_model()` returns `langchain_openai.ChatOpenAI(model="<tag>", base_url=LLM_BASE_URL, api_key=LLM_API_KEY)`. The tag is the LiteLLM proxy `model_name` (`gemma4:latest`). Do not send `openai/<tag>` — that prefix is the Google ADK showcase’s `LiteLlm` convention. The gateway still lists `openai/gemma4:latest` as a spare alias.

Compose (`docker-compose.yml` in this folder) talks to **this folder’s** `llm-gateway`, not Ollama directly and not the ADK showcase’s gateway:

- `LLM_BASE_URL` default `http://llm-gateway:4000/v1` (compose network)
- `LLM_ENGINE=gateway`, `LLM_PROFILE=ollama`, `LLM_API_KEY=sk-agentic-local` (gateway master key)
- `MODEL_REASONING` / `MODEL_FAST` default `gemma4:latest`
- `MODEL_CONTEXT_LENGTH` default `131072` (Ollama: server/Modelfile; LM Studio profile: `extra_body.num_ctx` on the ChatOpenAI client)

The gateway’s ollama profile uses `ollama_chat/gemma4:latest` at `http://host.docker.internal:11434` (`extra_hosts` on **llm-gateway**).

Host venv default (no gateway): `http://localhost:11434/v1`, `LLM_ENGINE=ollama`, `LLM_API_KEY=ollama`. Do not put `localhost` in Compose `.env` as `LLM_BASE_URL` or the app container cannot reach the gateway.

`agentic_security/llm.py` waits on `GET {base}/models`, warms via `/v1/chat/completions` when the engine is the gateway, then `generate_text` / `generate_json` via `ChatOpenAI.ainvoke`. Pipeline control flow is the LangGraph in `orchestration/graph.py`; the driver only yields events. Jailbreak LLM mode plays a constrained assistant and classifies refuse vs follow.

Do not add a second HTTP client that bypasses `ChatOpenAI` for pipeline completions, and do not import `google.adk`. Optional extra: `pip install -e ".[llm]"` (`langgraph`, `langchain-core`, `langchain-openai`). The Docker image already installs it.

Call logs: `memory/run-progress-and-llm-logs.md` (app) and `memory/llm-gateway.md` (proxy JSON timeframes).
