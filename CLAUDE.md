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
Plans: `agentic_security/plans.py` (`reports_for_pdf` puts executive summary first). Ultra-Professional adds optional LLM grounding (`agentic_security/grounding.py`) — launch switch only; lower tiers cannot enable it.

## Run modes

Landing toggle (same Micro-Cosmos `skip-llm-toggle` pattern): checked = **Deterministic**; unchecked = **LLM**. Mode is chosen **before Start assessment** and is fixed for that run — the run page shows a label, not a switch. Compose talks to host Ollama at `http://host.docker.internal:11434/v1` (`gemma4:latest`, `MODEL_CONTEXT_LENGTH=131072`). LLM mode waits for `/v1/models` then warms via Ollama `/api/generate`.

## Report metrics (must not regress)

Pentest HTML must include: severity histogram, CVSS bands, root-cause buckets, scope domains, **§2.5 personnel**, objectives, confidentiality/disclaimer, methodology, narrative, vulnerability matrix with **AS-00n** ids, per-finding CVSS + evidence snippets, WSTG appendix, OWASP Top 10. Cover classification and titles use the launch-form **Client name** (default `Client`) — never a hardcoded company.

Access-management HTML must include identity inventory, connectors, reviews, JML, break-glass — never an entitlement-only stub.

## UI

Landing `/` = plan cards (including **Ultra-Professional**) + **Choose a source tree** (example cards; click one to analyse that tree) + **Source from new URL REPO** (`POST /examples/fetch-github` downloads a public GitHub zip into `examples/`, then click the new card). There is no Target URL field and no auto-select of `sample-web-api`. Launch form stacks three `.switch-toggle` rows under Client name (Mode, LLM grounding, Auto-approve); **LLM grounding** is shown only when Ultra-Professional is selected. Requires a selected `source_path`.  
Run `/runs/{id}` = step progress bar, phase pills, Gates / Reports / Artifacts tabs, SSE `/runs/{id}/events`. Below the gates a status banner **flashes red/orange while running** and turns **green Completed** (Deterministic or LLM). Header shows a static mode label (not a toggle) and an **LLM grounding** badge when that extra was on. Reports tab **Generate output report** downloads one A4 PDF (executive summary first). Runs restore from `runs/<id>/run_meta.json` after a container rebuild.  

LLM /v1 calls log to stdout (`docker compose logs -f agentic-security`) and `./logs/openai-v1.log` (Compose bind-mount). Look for `openai-v1 request` / `openai-v1 response` with `POST …/v1/chat/completions` and the selected `openai/<model>`.  
Login cookie session, default `demo` / `demobxyz`.
