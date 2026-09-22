# Changes log — Macro-Search - Agentic Security Scan

Working folder: `/Users/joaocerqueira/Documents/git/micro-cosmos/agentic-security-test-sdk`  
No git operations in this tree (owner instruction, 2026-09-17).

---

## 2026-09-22 — Pentest-grade report depth (all standard runs)

Reports were heading-complete but shallow (A4 packs ~76–98 KB vs a 95-page sample pentest). Deterministic scanners now emit a WSTG result matrix, negative findings, OWASP Top 10 result paragraphs, reconstructed PoCs, and a real methodology narrative. LLM mode expands that prose (min lengths; never invents AS/CVE ids). `pentest-assessment.html` inlines §5.2 CIS chapters and §5.3 jailbreak when the plan entitles them; §4 mixes AppSec + Trivy HIGH+ + CIS. Client chrome stays the launch-form name.

| Path | Role |
|---|---|
| `agentic_security/scanners.py` | Extra language/needle checks; `wstg_matrix`; `owasp_top10_results`; Trivy `fix_guidance` |
| `agentic_security/llm_enrich.py` | Long pentest JSON; `_keep_longer`; OWASP/WSTG appendix job |
| `agentic_security/reports/html.py` | Full §1–6 bodies |
| `tests/test_pentest_depth.py` | Matrix, clean-tree HTML, JS eval, LLM merge |

Compose pytest after rebuild (see `tests/RESULTS.md`).

---

## 2026-09-18 — Compose `llm-gateway` (LiteLLM Proxy)

Second service: OpenAI `/v1` proxy. App `LLM_BASE_URL=http://llm-gateway:4000/v1`. Active profile **ollama** / `gemma4:latest`. Dormant YAML: LM Studio, AWS Bedrock, Vertex AI Gemini (`LLM_PROFILE` + restart gateway; no failover). Warm through gateway `/v1/chat/completions`; native Ollama `/api/generate` only for host venv.

Call logs (UTC ms): app `./logs/openai-v1.log` + `./logs/agentic-security.log` (`started_at` / `ended_at` / `duration_ms`); gateway DEBUG/`--detailed_debug` plus JSON `./logs/llm-gateway.log` (`call_start` / `call_end` / `duration_ms` / `upstream_ms`).

| Path | Role |
|---|---|
| `docker-compose.yml` | `llm-gateway` + `agentic-security` `depends_on` healthy |
| `llm-gateway/profiles/*.yaml` | One backend per file |
| `llm-gateway/profiles/custom_callbacks.py` | JSON UTC timeframes (`duration_ms` / `upstream_ms` / `overhead_ms`) |
| `llm-gateway/entrypoint.sh` | Rejects unknown `LLM_PROFILE`; `--detailed_debug`; no Prisma DB |
| `agentic_security/llm.py` | `uses_ollama_native_warm`; gateway warm via `/v1`; `started_at`/`ended_at` |
| `agentic_security/logging_config.py` | `UtcIsoFormatter`; `openai-v1.log` + `agentic-security.log` |

Compose pytest **54 passed** (2026-09-18). Live `POST /v1/chat/completions` ping wrote `logs/llm-gateway.log` (`duration_ms` ≈ 72897, `upstream_ms` ≈ 72843, `overhead_ms` ≈ 55).

---

## 2026-09-17 — Initial application

Created a security-only ADK-style pipeline with Micro-Cosmos look and feel.

### Ask

- Security review, vulnerability review, jailbreak assessment
- Gate reviews and a plan of identified issues
- Vanta-like Essentials / Plus / Professional (https://www.vanta.com/lp/demo)
- HTML reports covering pentest pack metrics, Vanta GRC objects, and Trivy-style scans
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

### Report coverage vs pentest pack

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

`images/` filenames: spaces → `_`. README “What this app is” shows all five files: landing page, **completed run**, executive summary, jailbreak/prompt-injection report, and access-management report.

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

---

## 2026-09-17 — Run page has no mode toggle

### Ask

On a run the Deterministic/LLM switch should not exist. The toggle belongs only on the launch form before Start assessment.

### What landed

| Path | Role |
|---|---|
| `run.html` | Static `.mode-badge` (Deterministic or LLM); no checkbox |
| `dashboard.js` | Removed `/runs/{id}/mode` POST |
| `web/app.py` | Removed `POST /runs/{id}/mode`, `Run.apply_mode()`, `apply_run_mode()` |

### Verification

Compose `pytest -v -W error::DeprecationWarning` after rebuild. Landing still has `.skip-llm-toggle`. Run page has no `#run-skip-llm`. `POST /runs/{id}/mode` is 404.

Compose **34 passed, 0 skipped** (2026-09-17, 31.44s).

---

## 2026-09-17 — Ultra-Professional with optional LLM grounding

### Ask

Avoid LLM hallucinations with per-run grounding: scrape facts tailored to this assessment at runtime. Optional, top tier only, an extra beyond Professional. Name: **Ultra-Professional with LLM grounding**.

### What landed

| Path | Role |
|---|---|
| `plans.py` | Fourth plan `ultra-professional`; `grounding_entitled()` |
| `grounding.py` | Local tree scrape + `api.github.com` meta (SSRF-closed) |
| `driver.py` | Writes `grounding.json` when `orch.llm_grounding` |
| `llm_enrich.py` | Prepends cite-or-unknown contract to LLM excerpts |
| `reports/html.py` | `llm-grounding.html` |
| `landing.html` / `landing.js` | Checkbox shown only for Ultra-Professional |
| `create_run` | Flag ignored unless `grounding_entitled(plan)` |

Lower tiers cannot turn grounding on. Deterministic Ultra-Professional still writes the pack; LLM mode uses it in prompts.

### Verification

Compose `pytest -v -W error::DeprecationWarning` after rebuild. Landing has four plan cards; `#grounding-field` appears after selecting Ultra-Professional. Run header shows **LLM grounding** only when the extra was on.

---

## 2026-09-17 — Reports use launch Client name

### Ask

Company names in output reports should disappear. Replace them with the **Client name** filled at the start of the pipeline run (launch form, default `Client`). Public git must not carry those company names.

### What landed

| Path | Role |
|---|---|
| `create_run` / `Run` / `SecurityOrchestrator` | Blank client name becomes `Client` |
| `reports/html.py` `_client()` | Cover classification `{client} confidential`; pentest title includes the name |
| `reports/pdf.py` | Output pack chrome uses the same name |
| `scanners.py` / `inventories.py` | CIS notes no longer name a company |

Every HTML/PDF report is bound to `orch.client_name` from launch. Re-run an assessment to refresh already-written files under `runs/`.

### Verification

Compose **47 passed, 0 skipped** (2026-09-17, 33.31s). `test_reports_use_launch_client_name` and `test_create_run_blank_client_defaults_to_client`.

---

## 2026-09-17 — Progress bar, running/completed banner, LLM /v1 logs

### Ask

Progress bar on the steps and gates. Confirmation of completed in green below the gates; running in red/orange flashing at a smooth pace — Deterministic and LLM. Container logs for the selected LLM and OpenAI API /v1 calls, fully mapped in docker-compose.

### What landed

| Path | Role |
|---|---|
| `run.html` / `dashboard.js` / `app.css` | `#run-progress`; `#run-status` below gates |
| `logging_config.py` / `llm.py` | `openai-v1 request|response` for `/v1/models` and `/v1/chat/completions` |
| `docker-compose.yml` | `PYTHONUNBUFFERED`, `LOG_DIR`, `LITELLM_LOG`, `./logs` mount, json-file logging |

### Verification

Compose `docker compose exec -T agentic-security pytest -v -W error::DeprecationWarning` on the rebuilt service: **48 passed, 0 skipped** in 30.55s (2026-09-17). Live run `4320841e` banner `#run-status.completed` green **Completed — Deterministic**. Waiting Deterministic `4a148218` and LLM `743aadc3` banners `#run-status.running` with `run-status-flash` 1.4s (red `#ED3A12` ↔ orange `#E07A1F`). Host `./logs/openai-v1.log` recorded `GET …/v1/models` 200 and `POST …/v1/chat/completions`.

---

## 2026-09-17 — README uses all four `images/` screenshots

### Ask

Use the four files now in `images/` by the significance of their names to represent current product status in the source README, then port to public git and commit.

### What landed

`README.md` “What this app is” now shows, in product order: **landing page** (four plans, GitHub zip source, Deterministic/LLM), **executive summary** (Reports tab, A4 PDF, Client name, Ultra-Professional grounding), **jailbreak & prompt-injection**, **access management**.

### Verification

All four PNG paths resolve under `images/`. Public-git commit after rsync.

---

## 2026-09-17 — Completed-run screenshot; launch switches match Mode

### Ask

New `images/…_completed_run.png` for a finished assessment — explain and show it in README. LLM Grounding and Auto-approve looked like a different radio/checkbox; match the Deterministic/LLM toggle switch and sit in the same Launch analysis cluster.

### What landed

README adds **Completed run** (green banner below gates, 14/14). Landing uses `.launch-toggles` + `.switch-toggle` for Mode, LLM grounding, and Auto-approve (Off/On). Hidden `auto_approve_gates` posts `true`/`false` like `skip_llm`.

### Verification

Compose pytest after rebuild. Browser: three matching switches under Client name; Ultra-Professional reveals the grounding switch.

---

## 2026-09-17 — Gates numbered 1–6 (4.5 → 5, 5 → 6)

### Ask

Rename gates to consecutive integers. Planning 4.5 becomes Gate 5; report release 5 becomes Gate 6.

### What landed

`PipelinePhase` / `GATES` ids are `gate_1` … `gate_6`. Phase strip labels **Gate 5** (remediation plan) and **Gate 6** (report release). Run cards show `Gate n`. Reports unlock after Gate 6.

### Verification

Compose pytest including `test_gates_are_integers_one_to_six`.

---

## 2026-09-18 — Artifacts on each gate for approve/reject

### Ask

Artifacts tab was empty. Show run artifacts at each gate so a reviewer can analyse them then approve or reject.

### What landed

`GET /runs/{id}/artifacts` lists JSON/HTML on disk. Driver emits an `artifact` event for every write (including remediation plan, access, risk, issues, ASVS, reports). Gate cards and the Artifacts tab share those links.

### Verification

Compose pytest: `test_artifacts_listed_from_disk`, `test_pipeline_auto_approves` (artifact keys).




