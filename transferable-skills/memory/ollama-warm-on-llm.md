---
name: ollama-warm-on-llm
description: When skip_llm is false, wait for Ollama /v1/models then warm MODEL_REASONING via /api/generate keep_alive (2026-09-17)
metadata:
  type: project
---

`llm.ensure_llm_ready()` is the single entry: poll OpenAI-compat `GET {LLM_BASE_URL}/models`, then `POST {native}/api/generate` with `keep_alive=60m` so gemma4 is resident before ADK LiteLlm traffic. Native base is `LLM_BASE_URL` with trailing `/v1` stripped (`ollama_native_base`).

Call sites: `run_full_pipeline` when `not orch.skip_llm`; `maybe_enrich` before any generate. Compose default remains `SKIP_LLM=true`; warming is per LLM run, not at container boot unless `SKIP_LLM=false`. Mode cannot be flipped mid-run — `POST /runs/{id}/mode` was removed.

Best-effort: never raise. A failed warm still lets the pipeline finish (enrich records `llm_error` and continues scanners).
