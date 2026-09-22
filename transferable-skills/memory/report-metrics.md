---
name: report-metrics
description: HTML reports must carry the pentest metric surface, Trivy CVE tables, jailbreak probes, CIS catalogue, and Vanta GRC objects, bound to the launch Client name (2026-09-17)
metadata:
  type: project
---

`agentic_security/reports/html.py` is the single writer. `write_all_reports(orch)` emits only `reports_for(plan)`. Every report cover uses the launch-form **Client name** (default `Client` when blank). Do not hardcode a company in HTML, JSON notes, or PDF chrome.

**Pentest assessment (`pentest-assessment.html`) — required sections**

1. Executive summary (multi-paragraph; LLM mode expands, Deterministic keeps the four-block stub)  
2. Project overview: App + Trivy histograms, CVSS bands, root-cause buckets (including patch management from HIGH+ CVEs), scope domains, in/out of scope, objectives, personnel, confidentiality, disclaimer  
3. Methodology (OWASP WSTG, ASVS 4.0, PTES, OSSTMM, CIS) + narrative of **this run** (files sampled, Trivy live vs fallback, no live DAST)  
4. Vulnerability matrix mixing AppSec AS-ids, Trivy HIGH+ CVEs, and (Professional+) HIGH CIS rows  
5. Findings: §5.1 full write-up (CVSS, OWASP, WSTG, technical details, evidence, reconstructed PoC, steps, recs, retest) or tested-clean negatives; §5.2 CIS chapters (IAM, Storage, Database, Logging, Networking, VM, Key Vault, App Service); §5.3 jailbreak when the plan includes it  
6. Appendix: WSTG matrix with Pass/Fail/not-observed/not-applicable, OWASP Top 10 A1–A10 **result paragraphs**, used tools (actual scanner this run), root-cause glossary, terminology  

Do not drop a section because a run found zero AS-ids — render the WSTG matrix and negative findings. Do not put a company name from a sample pentest PDF into chrome; Client name is the launch form.

**Also**

- Trivy: by-severity counts + CVE rows (id, pkg, installed, fixed, target, fix guidance). Fallback note when Trivy is not on PATH.  
- Jailbreak: six probe families (override, role-play, indirect, tool-abuse, exfil, encoding) + source markers + surface score.  
- CIS: Azure Foundations control catalogue (IAM, Storage, Database, Key Vault, Logging, Networking, VM, App Service) with portal-style remediations.  
- Vanta: frameworks, policies (with body text), controls + tests, evidence map, questionnaires, SLA board, **full access-management inventory**, risk register (likelihood/impact/residual), issue board (ISS-00n).

Do not drop a section because a run found zero issues — render empty tables. Do not ship access-management as an entitlement sentence.
