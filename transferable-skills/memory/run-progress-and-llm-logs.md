---
name: run-progress-and-llm-logs
description: Run-page step progress + green completed / red-orange running banner; Compose maps OpenAI /v1 logs to stdout and ./logs (2026-09-17)
metadata:
  type: project
---

The assessment page has `#run-progress` (phase fill) and, **below the gates**, `#run-status`. While the pipeline is live the banner flashes red→orange (`1.4s ease-in-out`). On `pipeline_completed` it turns green **Completed — Deterministic** or **Completed — LLM (Ollama / ADK LiteLLM)** — same in both modes. `pipeline_stopped` is a solid stopped state.

SSE already replays history, so a refresh of a finished run shows green.

OpenAI-compatible calls (`GET /v1/models`, `POST /v1/chat/completions`) log on `agentic_security.openai_v1`. Compose sets `PYTHONUNBUFFERED=1`, `LOG_DIR=/app/logs`, bind-mounts `./logs`, and lists the full LLM env (`LLM_BASE_URL`, models, engine). Use `docker compose logs -f agentic-security`. Do not log prompt bodies — `prompt_chars` / `reply_chars` only.
