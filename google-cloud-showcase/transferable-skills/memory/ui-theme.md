---
name: ui-theme
description: This ADK showcase is a light Google-colour theme; the LangGraph sibling is the lighter blue-slate theme (2026-10-02)
metadata:
  type: project
---

Themes live only in each showcase's `agentic_security/web/static/css/app.css`. Do not copy one showcase's palette into the other.

## This folder (Google ADK)

White field in the adk.dev direction. Actions use Google blue `--accent` `#1A73E8`. The top bar is a red / yellow / green / blue stripe (`--danger`, `--g-yellow`, `--g-green`, `--g-blue`). Done phase pills are green. Reject and error states stay red via `--danger`.

## Sibling `langgraph-showcase`

Lighter blue-slate field: `--bg` `#1B2838`, blue `--accent` `#6CB0FF`, light text. `color-scheme: dark`.

Layout and pipeline behaviour are the same in both showcases.
