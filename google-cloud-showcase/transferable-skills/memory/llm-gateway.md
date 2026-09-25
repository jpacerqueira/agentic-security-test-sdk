---
name: llm-gateway
description: Compose LiteLLM Proxy as OpenAI /v1 hop; Ollama active, LM Studio/Bedrock/Vertex dormant; UTC call timeframes (2026-09-18)
metadata:
  type: project
---

`llm-gateway` is a second Compose service (`ghcr.io/berriai/litellm:main-stable`) that speaks OpenAI `/v1` to the app and routes to **one** backend. It is not the OpenCode IDE; inbound spec is OpenAI, outbound depends on `LLM_PROFILE`.

- App: `LLM_BASE_URL=http://llm-gateway:4000/v1`, `LLM_ENGINE=gateway`, `LLM_API_KEY` = gateway `LITELLM_MASTER_KEY` (default `sk-agentic-local`).
- Active default: `LLM_PROFILE=ollama` → `ollama_chat/gemma4:latest` at `host.docker.internal:11434` with `keep_alive=60m`.
- Dormant: `lmstudio`, `bedrock`, `vertex` YAML under `llm-gateway/profiles/`. Switch = change `LLM_PROFILE` + `docker compose up -d llm-gateway`. **No load-balancing across profiles.**
- `entrypoint.sh` rejects unknown profiles, sets `PYTHONPATH` to `profiles/`, skips Prisma/DB (`STORE_MODEL_IN_DB=False`), runs `litellm --detailed_debug`.
- Timing callback **must** live next to the YAML: `llm-gateway/profiles/custom_callbacks.py` (`custom_callbacks.proxy_handler_instance`). LiteLLM imports from the config file’s directory.
- Cloud secrets stay in env / `llm-gateway/secrets/` (gitignored). Vertex needs a mounted service-account JSON when selected.
- Readiness: app `GET /v1/models` on the gateway, then a 1-token `POST /v1/chat/completions`. Native Ollama `/api/generate` warm is **only** for a host venv pointed at Ollama (`uses_ollama_native_warm`).

## Logs

| Where | Content |
|---|---|
| `docker compose logs -f llm-gateway` | DEBUG JSON + `--detailed_debug` (proxy internals) |
| `./logs/llm-gateway.log` | One JSON line per completion: `gateway_call_start` then `gateway_call_success` / `gateway_call_failure` |
| `docker compose logs -f agentic-security` | App `/v1` lines (`openai-v1 request\|response`) |
| `./logs/openai-v1.log` | App OpenAI-compat calls |
| `./logs/agentic-security.log` | Broader `agentic_security.*` file log |

Gateway JSON timeframes (UTC ms, suffix `Z`): `logged_at`, `call_start`, `call_end`, `duration_ms` (wall), `upstream_start`, `upstream_end`, `upstream_ms` (Ollama/LM Studio/cloud), `overhead_ms` (proxy), plus `profile`, `model`, token counts, `status`. App lines use the same clock via `utc_iso_ms()` / `started_at` / `ended_at` / `duration_ms` / `probe_ms`. **No prompt bodies** — `prompt_chars` / `reply_chars` only.

```bash
docker compose logs -f llm-gateway agentic-security
tail -f logs/llm-gateway.log logs/openai-v1.log logs/agentic-security.log
```
