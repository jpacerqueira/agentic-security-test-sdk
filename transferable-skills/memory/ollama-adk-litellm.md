---
name: ollama-adk-litellm
description: LLM mode uses Google ADK LiteLlm against local Ollama OpenAI-compatible /v1 (2026-09-17)
metadata:
  type: project
---

`Settings.build_llm()` returns `google.adk.models.lite_llm.LiteLlm(model="openai/<tag>", api_base=LLM_BASE_URL, api_key=LLM_API_KEY, drop_params=True)`. Same Micro-Cosmos pattern: Ollama speaks `/v1/chat/completions`; LiteLLM needs a non-empty api_key even though Ollama does not authenticate.

Compose (`docker-compose.yml`) talks to **Ollama on the host**:

- `LLM_BASE_URL` default `http://host.docker.internal:11434/v1`
- `extra_hosts: ["host.docker.internal:host-gateway"]` (Linux + Docker Desktop)
- `LLM_ENGINE=ollama`, `LLM_API_KEY=ollama`
- `MODEL_REASONING` / `MODEL_FAST` default `gemma4:latest`
- `MODEL_CONTEXT_LENGTH` default `131072` (documented; per-request `num_ctx` is **not** sent when engine is ollama — set context on the Ollama server / Modelfile)

Host venv default: `http://localhost:11434/v1`. Do not put `localhost` in Compose `.env` or the container cannot reach host Ollama.

`agentic_security/llm.py` waits on `GET {base}/models`, then `generate_text` / `generate_json` via `LiteLlm.generate_content_async(LlmRequest)`. Jailbreak LLM mode plays a constrained assistant and classifies refuse vs follow.

Do not add a second HTTP client that bypasses ADK LiteLlm for pipeline completions. Optional extra: `pip install -e ".[llm]"` / Docker image already installs it.
