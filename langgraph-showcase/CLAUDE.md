# Macro-Search - Agentic Security Scan — Claude / Cursor context

**Project:** Security-only LangGraph pipeline (pentest + Trivy + jailbreak + Vanta-shaped GRC)  
**Version:** 0.0.1  
**Stack:** Python 3.12, FastAPI, HTMX, LangGraph `StateGraph`, LangChain `ChatOpenAI` (optional, via this folder’s Compose `llm-gateway` OpenAI `/v1`), Trivy when on PATH  
**Entry:** `uvicorn agentic_security.web.app:app --port 8090` or `docker compose up` from this folder  
**Git home:** `public-git/agentic-security-test-sdk/langgraph-showcase`. Sibling `google-cloud-showcase` is the Google ADK deployment. Deploy one at a time; both bind host **8090** and **4000**.

## What this is

Sister product to Micro-Cosmos. Same visual language, **no source-to-source translation**. A run is a gated security assessment that writes HTML reports.

## Pipeline

```
Scope → Gate 1 → Vuln/Trivy → Gate 2 → AppSec → Gate 3
→ Jailbreak → Gate 4 → CIS cloud → Gate 5 Planning
→ Compliance pack (plan-gated) → Gate 6 → Writer → Done
```

Gates: `agentic_security/orchestration/pipeline.py` `GATES`.  
Control flow: `agentic_security/orchestration/graph.py` `build_assessment_graph()` (LangGraph). `driver.py` `run_full_pipeline()` only streams that graph’s events. A rejected gate routes to the `stopped` node.  
Scanners: `agentic_security/scanners.py` (deterministic; Trivy subprocess if installed).  
LLM: `agentic_security/settings.py` `build_chat_model()` → LangChain `ChatOpenAI(model="<tag>", base_url=LLM_BASE_URL)`. The tag is the gateway `model_name` (`gemma4:latest`), not an `openai/` provider prefix. `llm.llm_stack_available()` checks `langgraph` and `langchain_openai`.  
Inventories: `agentic_security/inventories.py` (access, ASVS, risk, issues).  
Reports: `agentic_security/reports/html.py`. Combined A4 PDF: `agentic_security/reports/pdf.py` (`GET /runs/{id}/output-report.pdf`).  
Plans: `agentic_security/plans.py` (`reports_for_pdf` puts executive summary first). Ultra-Professional adds optional LLM grounding (`agentic_security/grounding.py`) — launch switch only; lower tiers cannot enable it.

## Run modes

Landing toggle (same Micro-Cosmos `skip-llm-toggle` pattern): checked = **Deterministic**; unchecked = **LLM**. Mode is chosen **before Start assessment** and is fixed for that run — the run page shows a label, not a switch. Compose: app → `llm-gateway:4000/v1` (LiteLLM Proxy) → active profile **ollama** / host `gemma4:latest`. Dormant profiles: `lmstudio`, `bedrock`, `vertex` (`LLM_PROFILE` + restart `llm-gateway` only). LLM mode waits for gateway `GET /v1/models` then a 1-token `POST /v1/chat/completions`. Host venv without the gateway still uses `http://localhost:11434/v1` and Ollama `/api/generate` warm.

## Report metrics (must not regress)

Pentest HTML must include: severity histogram (App + Trivy), CVSS bands, root-cause buckets, scope domains, **§2.5 personnel**, objectives, confidentiality/disclaimer, methodology narrative of this run, vulnerability matrix with **AS-00n** ids plus Trivy HIGH+, per-finding CVSS + evidence + reconstructed PoC, **WSTG result matrix** (not-observed when clean), OWASP Top 10 **result paragraphs**, §5.2 CIS chapters, §5.3 jailbreak when entitled. Cover classification and titles use the launch-form **Client name** (default `Client`) — never a hardcoded company.

Access-management HTML must include identity inventory, connectors, reviews, JML, break-glass — never an entitlement-only stub.

## UI

Landing `/` = plan cards (including **Ultra-Professional**) + **Choose a source tree** (example cards; click one to analyse that tree) + **Source from new URL REPO** (`POST /examples/fetch-github` downloads a public GitHub zip into `examples/`, then click the new card). There is no Target URL field and no auto-select of `sample-web-api`. Launch form stacks three `.switch-toggle` rows under Client name (Mode, LLM grounding, Auto-approve); **LLM grounding** is shown only when Ultra-Professional is selected. Requires a selected `source_path`.  
Run `/runs/{id}` = step progress bar, phase pills, Gates / Reports / Artifacts tabs, SSE `/runs/{id}/events`. Each gate lists JSON artifacts to review before approve/reject. `GET /runs/{id}/artifacts` reads the run directory (not SSE-only). Below the gates a status banner **flashes red/orange while running** and turns **green Completed** (Deterministic or LLM). Header shows a static mode label (not a toggle) and an **LLM grounding** badge when that extra was on. Reports tab **Generate output report** downloads one A4 PDF (executive summary first). Runs restore from `runs/<id>/run_meta.json` after a container rebuild.  

LLM /v1 calls log to stdout (`docker compose logs -f agentic-security`) and `./logs/openai-v1.log` / `./logs/agentic-security.log` with UTC `started_at` / `ended_at` / `duration_ms`. Gateway DEBUG + `--detailed_debug` plus `./logs/llm-gateway.log` (JSON `call_start` / `call_end` / `duration_ms` / `upstream_ms` / `overhead_ms`). Look for `openai-v1 request` / `openai-v1 response` and `gateway_call_success`. Skills: `transferable-skills/memory/llm-gateway.md`, `run-progress-and-llm-logs.md`.  
Login cookie session, default `demo` / `demobxyz`.
