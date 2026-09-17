---
name: complete-reports
description: Plus/Professional HTML must be full inventories, not entitlement stubs; pentest needs AS-ids, evidence, §2.5 personnel (2026-09-17)
metadata:
  type: project
---

`agentic_security/inventories.py` writes `access_management.json`, `asvs_coverage.json`, `risk_register.json`, `issues.json` and annotates CIS (`not-in-scope` when no cloud IaC). `reports/html.py` renders those files.

Access-management must show identity inventory, directory connectors, access reviews, joiner/mover/leaver, break-glass, SOC2 CC6 mapping. Jailbreak must show scoring rubric, expected defense, and live excerpts when `live=true`. Risk register: likelihood/impact/residual/treatment. Issues: ISS-00n, priority, SLA, due.

`backfill_run_reports()` upgrades older run directories (e.g. `55c27510`) so restored runs after a rebuild are not stuck on stub HTML.
