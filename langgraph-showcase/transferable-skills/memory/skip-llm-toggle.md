---
name: skip-llm-toggle
description: Mode toggle exists only on the launch form; a started run shows a label, not a switch (2026-09-17)
metadata:
  type: project
---

Same CSS class as Micro-Cosmos (`.skip-llm-toggle`), **landing only**.

Landing: hidden `name=skip_llm` is always posted (`true`/`false`). The checkbox has **no** `name` so an unchecked box cannot fall back to process `SKIP_LLM`. landing.js syncs the hidden field on change/submit. Unchecked (LLM) still shows the inline confirm.

Run page: **no toggle**. Header shows a static `.mode-badge` (Deterministic or LLM) from `run.skip_llm` chosen at launch. There is no `POST /runs/{id}/mode` and no `Run.apply_mode()`. Remaining phases keep the launch-time `orch.skip_llm`.

Consecutive launches (deterministic → LLM → deterministic) are independent runs. Each must complete; do not cache skip_llm on the process from the previous form post.
