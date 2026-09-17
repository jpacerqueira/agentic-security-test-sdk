---
name: skip-llm-toggle
description: Landing and run-page Mode toggle is skip_llm (checked=deterministic); consecutive runs must both succeed (2026-09-17)
metadata:
  type: project
---

Same CSS class as Micro-Cosmos (`.skip-llm-toggle`).

Landing: hidden `name=skip_llm` is always posted (`true`/`false`). The checkbox has **no** `name` so an unchecked box cannot fall back to process `SKIP_LLM`. landing.js syncs the hidden field on change/submit. Unchecked (LLM) still shows the inline confirm.

Run page: the same toggle POSTs `/runs/{id}/mode`. That calls `Run.apply_mode()` which sets **both** `run.skip_llm` and `orch.skip_llm` and rewrites `run_meta.json`. Remaining phases read `orch.skip_llm` at `maybe_enrich` time — flipping mid-gate is how a live run switches between scanners-only and ADK LiteLlm.

Consecutive launches (deterministic → LLM → deterministic) are independent runs. Each must complete; do not cache skip_llm on the process from the previous form post.
