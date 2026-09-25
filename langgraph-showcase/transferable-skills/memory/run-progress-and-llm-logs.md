---
name: run-progress-and-llm-logs
description: Run-page progress/status banners; app + llm-gateway /v1 logs with UTC timeframes (2026-09-18)
metadata:
  type: project
---

The assessment page has `#run-progress` (phase fill) and, **below the gates**, `#run-status`. While the pipeline is live the banner flashes red→orange (`1.4s ease-in-out`). On `pipeline_completed` it turns green **Completed — Deterministic** or **Completed — LLM (LangGraph / gateway)** — same in both modes. `pipeline_stopped` is a solid stopped state.

SSE already replays history, so a refresh of a finished run shows green.

## App `/v1` logs

Logger `agentic_security.openai_v1`. Formatter is UTC with milliseconds (`2026-09-18T12:16:50.896Z`). Every request/response pair should carry `started_at`, `ended_at`, `duration_ms` (GET probes also `probe_ms`). Compose `LOG_DIR=/app/logs` bind-mounts `./logs`:

- `openai-v1.log` — `/v1/models` and `/v1/chat/completions` only
- `agentic-security.log` — `agentic_security` package (includes the same v1 lines via propagate)

Do not log prompt bodies — `prompt_chars` / `reply_chars` only.

## Gateway timeframes

See `memory/llm-gateway.md`. `./logs/llm-gateway.log` is JSON: `duration_ms`, `upstream_ms`, `overhead_ms`. `docker compose logs -f llm-gateway` is DEBUG + `--detailed_debug`.
