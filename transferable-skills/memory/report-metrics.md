---
name: report-metrics
description: HTML reports must carry the pentest metric surface, Trivy CVE tables, jailbreak probes, CIS catalogue, and Vanta GRC objects, bound to the launch Client name (2026-09-17)
metadata:
  type: project
---

`agentic_security/reports/html.py` is the single writer. `write_all_reports(orch)` emits only `reports_for(plan)`. Every report cover uses the launch-form **Client name** (default `Client` when blank). Do not hardcode a company in HTML, JSON notes, or PDF chrome.

**Pentest assessment (`pentest-assessment.html`) — required sections**

1. Executive summary  
2. Project overview: vulnerability histogram (Critical/High/Medium/Low/Info), CVSS bands (9.0–10.0 … 0.0), root-cause buckets (insecure configuration, coding practices, patch management, awareness, architecture), scope domains, objectives, confidentiality, disclaimer (snapshot in time)  
3. Methodology (OWASP WSTG, ASVS 4.0, PTES, OSSTMM, CIS) + narrative of tests  
4. Vulnerability matrix (ref, title, severity, CVSS)  
5. Findings: affected assets, CVSS base/vector/impact/exploitability, OWASP class, root cause, description, impact, recommendations, references  
6. Appendix: WSTG test-case chapters, OWASP Top 10 A1–A10, used tools, root-cause glossary, terminology (black-box, grey-box, CVSS, NVD)

**Also**

- Trivy: by-severity counts + CVE rows (id, pkg, installed, fixed, target). Fallback note when Trivy is not on PATH.  
- Jailbreak: six probe families (override, role-play, indirect, tool-abuse, exfil, encoding) + source markers + surface score.  
- CIS: Azure Foundations control catalogue (IAM, Storage, Key Vault, Logging, Networking, VM, App Service).  
- Vanta: frameworks, policies (with body text), controls + tests, evidence map, questionnaires, SLA board, **full access-management inventory**, risk register (likelihood/impact/residual), issue board (ISS-00n).

Do not drop a section because a run found zero issues — render empty tables. Do not ship access-management as an entitlement sentence.
