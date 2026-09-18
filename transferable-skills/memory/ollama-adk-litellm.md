---
name: ollama-adk-litellm
description: LLM mode uses Google ADK LiteLlm against Compose llm-gateway OpenAI /v1 (2026-09-18)
metadata:
  type: project
---

`Settings.build_llm()` returns `google.adk.models.lite_llm.LiteLlm(model="openai/<tag>", api_base=LLM_BASE_URL, api_key=LLM_API_KEY, drop_params=True)`. Same Micro-Cosmos pattern: LiteLLM (client) speaks `/v1/chat/completions` to `api_base`.

Compose (`docker-compose.yml`) talks to **`llm-gateway`**, not Ollama directly:

- `LLM_BASE_URL` default `http://llm-gateway:4000/v1`
- `LLM_ENGINE=gateway`, `LLM_PROFILE=ollama`, `LLM_API_KEY=sk-agentic-local` (gateway master key)
- `MODEL_REASONING` / `MODEL_FAST` default `gemma4:latest` (stable alias on every gateway profile)
- `MODEL_CONTEXT_LENGTH` default `131072` (Ollama: server/Modelfile; LM Studio profile: gateway `extra_body.num_ctx`)

The gateway’s ollama profile uses `ollama_chat/gemma4:latest` at `http://host.docker.internal:11434` (`extra_hosts` on **llm-gateway**).

Host venv default (no gateway): `http://localhost:11434/v1`, `LLM_ENGINE=ollama`, `LLM_API_KEY=ollama`. Do not put `localhost` in Compose `.env` as `LLM_BASE_URL` or the app container cannot reach the gateway.

`agentic_security/llm.py` waits on `GET {base}/models`, warms via `/v1/chat/completions` when the engine is the gateway, then `generate_text` / `generate_json` via `LiteLlm.generate_content_async(LlmRequest)`. Jailbreak LLM mode plays a constrained assistant and classifies refuse vs follow.

Do not add a second HTTP client that bypasses ADK LiteLlm for pipeline completions. Optional extra: `pip install -e ".[llm]"` / Docker image already installs it.

Call logs: `memory/run-progress-and-llm-logs.md` (app) and `memory/llm-gateway.md` (proxy JSON timeframes).
