# Macro-Search - Agentic Security Scan — Claude / Cursor context

**Project:** Security-only ADK pipeline (pentest + Trivy + jailbreak + Vanta-shaped GRC)  
**Version:** 0.0.1  
**Stack:** Python 3.12, FastAPI, HTMX, Google ADK LiteLlm (optional, Ollama `/v1`), Trivy when on PATH  
**Entry:** `uvicorn agentic_security.web.app:app --port 8090` or `docker compose up`  
**Git home:** `public-git/agentic-security-test-sdk`. The sibling working tree may be file-only.

## What this is

Sister product to Micro-Cosmos. Same visual language, **no source-to-source translation**. A run is a gated security assessment that writes HTML reports.

## Pipeline

```
Scope → Gate 1 → Vuln/Trivy → Gate 2 → AppSec → Gate 3
→ Jailbreak → Gate 4 → CIS cloud → Gate 4.5 Planning
→ Compliance pack (plan-gated) → Gate 5 → Writer → Done
```

Gates: `agentic_security/orchestration/pipeline.py` `GATES`.  
Scanners: `agentic_security/scanners.py` (deterministic; Trivy subprocess if installed).  
LLM: `agentic_security/settings.py` `build_llm()` → `google.adk.models.lite_llm.LiteLlm(model="openai/<tag>", api_base=LLM_BASE_URL)`.  
Inventories: `agentic_security/inventories.py` (access, ASVS, risk, issues).  
Reports: `agentic_security/reports/html.py`. Combined A4 PDF: `agentic_security/reports/pdf.py` (`GET /runs/{id}/output-report.pdf`).  
Plans: `agentic_security/plans.py` (`reports_for_pdf` puts executive summary first).

## Run modes

Landing toggle (same Micro-Cosmos `skip-llm-toggle` pattern): checked = **Deterministic**; unchecked = **LLM**. LLM mode waits for Ollama `GET /v1/models`, enriches narratives, and executes the six jailbreak probes against the local model.

## Report metrics (must not regress)

Pentest HTML must include: severity histogram, CVSS bands, root-cause buckets, scope domains, **§2.5 personnel**, objectives, confidentiality/disclaimer, methodology, narrative, vulnerability matrix with **AS-00n** ids, per-finding CVSS + evidence snippets, WSTG appendix, OWASP Top 10.

Access-management HTML must include identity inventory, connectors, reviews, JML, break-glass — never an entitlement-only stub.

## UI

Landing `/` = plan cards + example picker + launch form (mode toggle + auto-approve).  
Run `/runs/{id}` = phase pills, Gates / Reports / Artifacts tabs, SSE `/runs/{id}/events`. Reports tab **Generate output report** downloads one A4 PDF (executive summary first). Runs restore from `runs/<id>/run_meta.json` after a container rebuild.  
Login cookie session, default `demo` / `demobxyz`.
