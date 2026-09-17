---
name: skip-llm-toggle
description: Landing Mode toggle is skip_llm (checked=deterministic) with an inline LLM confirm; persist on Run like auto_approve (2026-09-17)
metadata:
  type: project
---

Same CSS class as Micro-Cosmos (`.skip-llm-toggle`). Checked checkbox posts `skip_llm=true` (deterministic). Unchecked: landing.js writes a hidden `skip_llm=false` and asks for confirm before submit.

Server: `_parse_skip_llm` in `web/app.py`. Threaded through `Run.__init__` → `run_meta.json` → restore. Do not use `stop_requested` for this — it is a fixed per-run setting.
