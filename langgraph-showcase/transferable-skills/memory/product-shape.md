---
name: product-shape
description: This folder is the LangGraph security pipeline — pentest, Trivy, jailbreak, Vanta-shaped GRC — not a code translator and not Google ADK (2026-09-25)
metadata:
  type: project
---

Joao asked for a new application inside `agentic-security-test-sdk` that only does security review, vulnerability review, and jailbreak assessment, starting from the Micro-Cosmos look and feel, with gate reviews and a plan of identified issues, plus Vanta-like Essentials / Plus / Professional capacity.

It is **not** Micro-Cosmos: no Observer IR graph, no seam TDD loop, no language translation. Reports are the product. The launch-form **Client name** (default `Client`) is the only organisation name that appears in report chrome.

This folder’s agent framework is LangGraph. The sibling `google-cloud-showcase` is the Google ADK deployment of the same product. Each has its own Compose file and its own LiteLLM gateway. Default profile on both is `ollama` / `gemma4:latest`. Do not import `google.adk` here.

Vanta public plan page: https://www.vanta.com/lp/demo
