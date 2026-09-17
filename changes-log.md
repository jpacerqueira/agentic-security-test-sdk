# Changes log — Macro-Search - Agentic Security Scan

Working folder: `/Users/joaocerqueira/Documents/git/micro-cosmos/agentic-security-test-sdk`  
No git operations in this tree (owner instruction, 2026-09-17).

---

## 2026-09-17 — Initial application

Created a security-only ADK-style pipeline with Micro-Cosmos look and feel.

### Ask

- Security review, vulnerability review, jailbreak assessment
- Gate reviews and a plan of identified issues
- Vanta-like Essentials / Plus / Professional (https://www.vanta.com/lp/demo)
- HTML reports covering the XYZ Reality 2022 pentest pack metrics, Vanta GRC objects, and Trivy-style scans
- README, Claude skills, this log
- Files only — no git

### What landed

| Path | Role |
|---|---|
| `agentic_security/orchestration/pipeline.py` | Phases, six gates, orchestrator |
| `agentic_security/orchestration/driver.py` | Sequential run |
| `agentic_security/scanners.py` | Scope, Trivy (or fallback), AppSec, jailbreak, CIS, compliance pack, remediation plan |
| `agentic_security/reports/html.py` | All HTML writers |
| `agentic_security/plans.py` | Tier entitlements |
| `agentic_security/web/` | FastAPI + HTMX UI (login, landing, run dashboard, reports tab) |
| `examples/sample-web-api/` | Deliberate pickle / TLS / password footguns |
| `transferable-skills/` | How-to + four memory files |
| `CLAUDE.md` / `README.md` | Operator map |

### Report coverage vs XYZ pack

Executive summary, vulnerability chart buckets, root-cause analysis, scope (domains), objectives, confidentiality, disclaimer, methodology (OWASP/PTES/OSSTMM/CIS), narrative of tests, vulnerability matrix, per-finding CVSS (base, vector, impact, exploitability), WSTG appendix, OWASP Top 10, tools, root-cause glossary, terminology. Cloud CIS catalogue taken from the Azure section of that pack (IAM, storage, key vault, logging, networking, VM, App Service).

### Vanta mapping

Essentials: 1 framework, policy templates, evidence, Trust Center entitlement, 3 core reports.  
Plus: jailbreak + access management + policy-control map, 25 questionnaires/year.  
Professional: risk register, CIS HTML, ASVS, issue management, full pack, 144 questionnaires/year.

### Not in this cut (logged, not silent)

- Live jailbreak probes against a running model (catalogue + surface score only in deterministic mode)
- Live Azure/CIS API audits (catalogue + manual status)
- Enterprise custom GRC package
- Questionnaire automation runtime (entitlement + count only)
- Git repository

### Verification

Verified 2026-09-17: `docker compose up --build -d` — image built, container Up, `GET /healthz` 200, `GET /login` 200 on port 8090. Trivy is in the image.

---

## 2026-09-17 — Product rename

User-facing name is **Macro-Search - Agentic Security Scan** (`agentic_security/brand.py` `APP_NAME`). Applied in FastAPI title, CLI help, templates (via Jinja `app_name`), HTML report chrome, pyproject description/authors, README, CLAUDE.md, transferable-skills, tests/README.md. Python import path remains `agentic_security`.

---

## 2026-09-17 — README screenshots

`images/` filenames: spaces → `_`. README “What this app is” shows landing page, jailbreak/prompt-injection report, and access-management report.

---

## 2026-09-17 — v0.0.1 LLM mode, complete reports, clone-ready

### Ask

Incomplete reports on run `55c27510`. Use local Ollama through Google ADK LiteLlm (OpenAI-compatible `/v1`). Complete every HTML report. Landing toggle Deterministic vs LLM. Rebuild/test. Port to `public-git/agentic-security-test-sdk` as version **0.0.1**.

### What landed

| Path | Role |
|---|---|
| `settings.build_llm()` | `LiteLlm(model="openai/<tag>", api_base=LLM_BASE_URL)` |
| `llm.py` / `llm_enrich.py` | Readiness probe, generate_text/json, jailbreak live probes |
| `inventories.py` | Access, ASVS, risk, issues, CIS annotate, compliance bodies |
| `reports/html.py` | Full tables + `backfill_run_reports` for restored runs |
| Landing `.skip-llm-toggle` | Checked = deterministic; confirm when LLM |
| Dockerfile `[llm]` extra | Clone-and-`docker compose up --build` includes ADK+LiteLLM+Trivy |

### Verification

Host: `pytest -v -W error::DeprecationWarning` — **12 passed, 0 skipped** (2026-09-17). FastAPI `on_event` replaced with `lifespan`. LiteLlm model id is tested without skipping when ADK is absent (`openai_model_id()`).

- Live Azure/CIS API audits (catalogue + not-in-scope when no IaC)
- Enterprise custom GRC
- Questionnaire runtime (templates + entitlement counts)

---

## 2026-09-17 — Generate output report (A4 PDF)

### Ask

Reports tab button that downloads one A4 PDF of every report, executive summary first. Implement in the original Compose app, then one commit in `public-git/agentic-security-test-sdk`.

### What landed

| Path | Role |
|---|---|
| `plans.reports_for_pdf()` | Executive summary first; skip `full-security-report.html` |
| `agentic_security/reports/pdf.py` | WeasyPrint combined HTML → A4 `output-report.pdf` |
| `GET /runs/{id}/output-report.pdf` | Builds and streams the PDF |
| Reports tab `#btn-output-pdf` | Client download of `{run_id}-output-report.pdf` |
| Dockerfile | cairo/pango/gdk-pixbuf + Liberation/DejaVu fonts |

### Verification

Host pytest (no Pango): 13 passed. Compose image: `pytest -v -W error::DeprecationWarning` — **14 passed, 0 skipped**. Smoke: `GET /healthz` 200; authenticated `GET /runs/55c27510/output-report.pdf` 200 `%PDF-1.7`. Reports tab **Generate output report** builds and downloads the A4 pack (executive summary first).

---

## 2026-09-17 — Compose Ollama defaults (gemma4)

Aligned `docker-compose.yml` with the Micro-Cosmos host-Ollama block: `LLM_BASE_URL=http://host.docker.internal:11434/v1`, `LLM_ENGINE=ollama`, `gemma4:latest`, `MODEL_CONTEXT_LENGTH=131072`, `extra_hosts` for Linux. Settings reads `MODEL_CONTEXT_LENGTH` but still does **not** send per-request `num_ctx` when the engine is ollama.

---

## 2026-09-17 — Run-page mode toggle, LLM warm, consecutive runs

### Ask

Add `MODEL_CONTEXT_LENGTH`. Warm the model when `skip_llm=false`. Toggle on the run to switch remaining phases between deterministic and ADK LLM. Consecutive deterministic and LLM runs must both complete after the user flips the toggle.

### What landed

| Path | Role |
|---|---|
| `llm.ensure_llm_ready()` / `warm_model()` | `/v1/models` then Ollama `/api/generate` keep_alive |
| `POST /runs/{id}/mode` | `Run.apply_mode()` writes `orch.skip_llm` + `run_meta.json` |
| Run header `.skip-llm-toggle` | Same control as landing; remaining phases honour it |
| Landing hidden `skip_llm` | Checkbox has no `name` so LLM (`false`) is posted explicitly |

### Verification

Compose `pytest -v -W error::DeprecationWarning` — **19 passed, 0 skipped** (2026-09-17). Consecutive det → LLM → det pipeline test included. Container env: `MODEL_REASONING=gemma4:latest`, `MODEL_CONTEXT_LENGTH=131072`, `LLM_BASE_URL=http://host.docker.internal:11434/v1`.

---

## 2026-09-17 — Source from new URL REPO + LLM mode 500

### Ask

Selecting a Target URL still analysed the static sample. Target URL should download a GitHub zip into `examples/` and that tree becomes the pipeline source after a card click. LLM mode on `http://localhost:8090/runs/8f2cedbc` 500ed: `NameError: PipelineEvent is not defined` in `set_run_mode`.

### What landed

| Path | Role |
|---|---|
| `agentic_security/github_examples.py` | Parse github.com URL, zip from codeload, extract into `examples/` |
| `POST /examples/fetch-github` | Landing **Source from new URL REPO** |
| Landing picker | Click a card → `source_path`; no auto-select of sample-web-api |
| `create_run` | 400 unless `source_path` is an existing directory |
| `PipelineEvent` import in `web/app.py` | Fixes `POST /runs/{id}/mode` 500 |

### Verification

Compose `pytest -v -W error::DeprecationWarning` — **34 passed, 0 skipped** (2026-09-17, 42.28s). Live: `POST /runs/8f2cedbc/mode` 200; landing has **Source from new URL REPO** (octocat/Hello-World zip extracted to `examples/octocat_Hello-World` and selected as source); no Target URL; no auto-select of sample-web-api.


