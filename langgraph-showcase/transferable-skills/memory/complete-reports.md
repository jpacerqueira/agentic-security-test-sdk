---
name: complete-reports
description: Plus/Professional HTML must be full inventories, not entitlement stubs; pentest needs AS-ids, evidence, §2.5 personnel (2026-09-17)
metadata:
  type: project
---

`agentic_security/inventories.py` writes `access_management.json`, `asvs_coverage.json`, `risk_register.json`, `issues.json` and annotates CIS (`not-in-scope` when no cloud IaC, portal-style remediations per domain). `reports/html.py` renders those files.

`appsec_findings.json` must include `wstg_matrix` (nine families), `negative_findings`, `owasp_top10_results` (A1–A10 with status + result paragraph), `methodology_narrative`, and per-finding `proof_of_concept`. LLM mode (`llm_enrich.py`) expands prose but must not invent ids; short model replies lose to the deterministic text (`_keep_longer`).

Access-management must show identity inventory, directory connectors, access reviews, joiner/mover/leaver, break-glass, SOC2 CC6 mapping. Jailbreak must show scoring rubric, expected defense, and live excerpts when `live=true`. Risk register: likelihood/impact/residual/treatment. Issues: ISS-00n, priority, SLA, due.

`backfill_run_reports()` upgrades older run directories (e.g. `55c27510`) so restored runs after a rebuild are not stuck on stub HTML.
