# transferable-skills/

Project skills for Macro-Search - Agentic Security Scan. They travel as markdown in this folder — **do not install them into `~/.cursor/skills/`**. In a new Cursor/Claude session, read `README.md` here plus the memory file that matches the task.

## How to use

1. `../CLAUDE.md` is the short always-on map.
2. Open `memory/<topic>.md` before editing that area.
3. Prompt: `Read transferable-skills/README.md and the memory files relevant to this task.`

| File | When |
|---|---|
| `memory/product-shape.md` | What this app is (and is not) |
| `memory/report-metrics.md` | Pentest + Trivy + Vanta metrics that HTML must carry |
| `memory/plans-and-gates.md` | Essentials/Plus/Professional/Ultra-Professional and the six gates |
| `memory/llm-grounding.md` | Optional Ultra-Professional scrape + cite-or-unknown LLM contract |
| `memory/no-git-in-this-tree.md` | Working tree vs public-git clone |
| `memory/ollama-adk-litellm.md` | ADK LiteLlm → Ollama `/v1` |
| `memory/complete-reports.md` | Full GRC/pentest HTML, not stubs |
| `memory/skip-llm-toggle.md` | Deterministic / LLM launch only (no run-page switch) |
| `memory/github-source-url-repo.md` | GitHub zip → examples/; click card for source_path |
| `memory/git-home-public-clone.md` | v0.0.1 clone/commit home |
| `memory/output-report-pdf.md` | Combined A4 PDF (executive summary first) |
| `memory/ollama-warm-on-llm.md` | Warm gemma4 when skip_llm is false |

## Adding a skill

Write `memory/<kebab-name>.md` with:

```yaml
---
name: kebab-name
description: one sentence (YYYY-MM-DD)
metadata:
  type: project
---
```

Add a row to the table. Append `../changes-log.md`.
