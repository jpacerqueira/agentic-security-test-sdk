---
name: llm-grounding
description: Ultra-Professional optional per-run scrape so LLM text cites this assessment's facts instead of inventing them (2026-09-17)
metadata:
  type: project
---

Ultra-Professional is a fourth plan above Professional. **LLM grounding is optional** (launch checkbox `#llm-grounding-input`) and **only that tier** can enable it. `create_run()` sets `llm_grounding = form_true AND grounding_entitled(plan)` — tampering `llm_grounding=true` on Essentials/Plus/Professional is ignored.

When the flag is on, the LangGraph `scope` node (`orchestration/graph.py`) calls `grounding.collect_grounding_for_run` in `asyncio.to_thread`, writes `grounding.json`, and `llm_enrich.maybe_enrich` prepends `format_grounding_prompt(orch.grounding_pack)` so ChatOpenAI must cite `G-00n` or say unknown.

Scrape is this run's source tree (manifests, routes, secret-pattern names — not secret values). GitHub metadata is fetched only when `.source.json` / `target_url` parses as `github.com`; the outbound host is always `api.github.com` (same SSRF-closed construction as zip fetch). Deterministic Ultra-Professional still writes the pack and `llm-grounding.html`; LLM mode is what uses the contract in prompts.

Do not add a second grounding toggle on the run page. Do not enable the extra on lower tiers to "try it".
