---
name: ollama-adk-litellm
description: LLM mode uses Google ADK LiteLlm against local Ollama OpenAI-compatible /v1 (2026-09-17)
metadata:
  type: project
---

`Settings.build_llm()` returns `google.adk.models.lite_llm.LiteLlm(model="openai/<tag>", api_base=LLM_BASE_URL, api_key=LLM_API_KEY, drop_params=True)`. Same Micro-Cosmos pattern: Ollama speaks `/v1/chat/completions`; LiteLLM needs a non-empty api_key even though Ollama does not authenticate.

Compose default: `LLM_BASE_URL=http://host.docker.internal:11434/v1`. Host default: `http://localhost:11434/v1`. `MODEL_REASONING` / `MODEL_FAST` default `gemma4:latest`.

`agentic_security/llm.py` waits on `GET {base}/models`, then `generate_text` / `generate_json` via `LiteLlm.generate_content_async(LlmRequest)`. Jailbreak LLM mode plays a constrained assistant and classifies refuse vs follow.

Do not add a second HTTP client that bypasses ADK LiteLlm for pipeline completions. Optional extra: `pip install -e ".[llm]"` / Docker image already installs it.
