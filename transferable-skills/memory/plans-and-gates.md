---
name: plans-and-gates
description: Three public plans (Essentials, Plus, Professional) gate which HTML reports exist; six human gates copy Micro-Cosmos auto_approve persistence, not stop_requested (2026-09-17)
metadata:
  type: project
---

Plans live in `agentic_security/plans.py`. Writer must not emit a Professional report on an Essentials run.

Gates (`gate_1` … `gate_5`, including `gate_4_5` planning) all funnel through `SecurityOrchestrator.wait_gate`. Auto-approve is a launch-time flag that requires a reviewer name (same rule as Micro-Cosmos). Rejection stops the pipeline after emitting `gate_resolved`.

Gate 4.5 is the remediation-plan checkpoint — SLA board of AppSec + high Trivy + jailbreak-program items. Do not skip it to "get to reports faster"; the owner asked for a plan of identified issues as a first-class gate.
