---
name: ollama-warm-on-llm
description: When skip_llm is false, wait for /v1/models then warm MODEL_REASONING (2026-09-18)
metadata:
  type: project
---

`llm.ensure_llm_ready()` is the single entry: poll OpenAI-compat `GET {LLM_BASE_URL}/models`, then warm `MODEL_REASONING`.

- **Compose (`LLM_ENGINE=gateway`)** — `POST {base}/chat/completions` with `max_tokens=1`. The ollama profile also sets LiteLLM `keep_alive=60m` toward host Ollama. Do **not** strip `/v1` and hit `/api/generate` on the gateway (it is not Ollama).
- **Host venv pointed at Ollama** — `uses_ollama_native_warm` is true; `POST {native}/api/generate` with `keep_alive=60m`. Native base is `LLM_BASE_URL` with trailing `/v1` stripped (`ollama_native_base`).

Call sites: `run_full_pipeline` when `not orch.skip_llm`; `maybe_enrich` before any generate. Compose default remains `SKIP_LLM=true`; warming is per LLM run, not at container boot unless `SKIP_LLM=false`. Mode cannot be flipped mid-run — `POST /runs/{id}/mode` was removed.

Best-effort: never raise. A failed warm still lets the pipeline finish (enrich records `llm_error` and continues scanners).
