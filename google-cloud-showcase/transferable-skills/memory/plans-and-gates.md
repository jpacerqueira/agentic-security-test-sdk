---
name: plans-and-gates
description: Four public plans (Essentials, Plus, Professional, Ultra-Professional); six human gates copy Micro-Cosmos auto_approve persistence, not stop_requested (2026-09-17)
metadata:
  type: project
---

Plans live in `agentic_security/plans.py`. Writer must not emit a Professional report on an Essentials run. Ultra-Professional is Professional plus `llm-grounding.html` and an optional launch checkbox; see `memory/llm-grounding.md`.

Gates (`gate_1` … `gate_6`) all funnel through `SecurityOrchestrator.wait_gate`. Auto-approve is a launch-time flag that requires a reviewer name (same rule as Micro-Cosmos). Rejection stops the pipeline after emitting `gate_resolved`.

Gate 5 is the remediation-plan checkpoint (formerly 4.5) — SLA board of AppSec + high Trivy + jailbreak-program items. Gate 6 is report release. Do not skip Gate 5 to "get to reports faster"; the owner asked for a plan of identified issues as a first-class gate.
