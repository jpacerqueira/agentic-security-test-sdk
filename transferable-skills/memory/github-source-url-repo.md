---
name: github-source-url-repo
description: Source from new URL REPO downloads a GitHub zip into examples/; click a card to analyse that tree (2026-09-17)
metadata:
  type: project
---

Do **not** treat a pasted URL as a live Target URL while analysing `examples/sample-web-api`. The pipeline source is always `source_path` from a clicked examples card.

Landing:

1. **Source from new URL REPO** (`POST /examples/fetch-github`) — public `https://github.com/owner/repo` only. Outbound hosts are `api.github.com` / `codeload.github.com`, built from the parsed `(owner, repo, ref)` (SSRF closed by construction). Zip lands under `examples/<owner>_<repo>/` with `.source.json`. Compose bind-mounts `./examples`, so the new card is visible without rebuilding the image.
2. **Choose a source tree** — click a card. That sets hidden `source_path` (and `target_url` from `.source.json` if present). Nothing is auto-selected; Start assessment 400s without a card.

Fetched trees are gitignored except `examples/sample-web-api/`.

LLM mode on an existing run: `POST /runs/{id}/mode` must import `PipelineEvent` from `orchestration.pipeline` (NameError 500 if missing). The image copies `agentic_security/` at build time — rebuild after that import change.
