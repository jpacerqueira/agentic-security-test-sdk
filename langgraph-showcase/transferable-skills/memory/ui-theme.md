---
name: ui-theme
description: LangGraph showcase uses a lighter blue-slate theme; the ADK showcase stays light with Google colours (2026-10-02)
metadata:
  type: project
---

Themes live only in each showcase's `agentic_security/web/static/css/app.css`. Do not copy one showcase's palette into the other.

## This folder (LangGraph)

Lighter blue-slate field: `--bg` `#1B2838`, panel `#243447`, blue `--accent` `#6CB0FF`, text `--ink` `#E7EEF8`. `color-scheme: dark`. Errors use `--danger`, not the blue.

## Sibling `google-cloud-showcase`

White page in the adk.dev direction: Google blue `#1A73E8` for actions, red `#EA4335` / yellow `#FBBC04` / green `#34A853` on the top bar. Done phase pills are green. Reject stays red.

Layout and pipeline behaviour are the same in both showcases.
