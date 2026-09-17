from __future__ import annotations

import asyncio
import json
import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.templating import Jinja2Templates

from agentic_security.brand import APP_NAME
from agentic_security.github_examples import GitHubFetchError, import_github_repo, list_examples
from agentic_security.orchestration.driver import run_full_pipeline
from agentic_security.orchestration.pipeline import (
    GATES,
    PHASE_LABELS,
    PipelinePhase,
    SecurityOrchestrator,
    list_run_artifacts,
)
from agentic_security.plans import PLAN_ORDER, grounding_entitled, resolve_plan
from agentic_security.settings import get_settings

ROOT = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(ROOT / "templates"))
TEMPLATES.env.globals["app_name"] = APP_NAME


@asynccontextmanager
async def lifespan(_app: FastAPI):
    from agentic_security.logging_config import configure_logging

    configure_logging()
    _restore_all()
    settings = get_settings()
    logging.getLogger("agentic_security.openai_v1").info(
        "llm mapping skip_llm=%s engine=%s model=%s fast=%s api_base=%s",
        settings.skip_llm,
        settings.llm_engine,
        settings.model_reasoning,
        settings.model_fast,
        settings.llm_base_url,
    )
    if not settings.skip_llm:
        from agentic_security import llm as llm_mod

        asyncio.create_task(llm_mod.ensure_llm_ready())
    yield


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        path = request.url.path
        if path.startswith("/static") or path in ("/login", "/healthz"):
            return await call_next(request)
        if not request.session.get("authenticated"):
            return RedirectResponse("/login", status_code=303)
        return await call_next(request)


app = FastAPI(title=APP_NAME, lifespan=lifespan)
app.add_middleware(AuthMiddleware)
app.add_middleware(SessionMiddleware, secret_key=get_settings().session_secret)
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")

RUNS: dict[str, "Run"] = {}


class Run:
    def __init__(self, **kw):
        settings = get_settings()
        self.run_id = kw["run_id"]
        self.plan = kw.get("plan") or "essentials"
        self.skip_llm = kw.get("skip_llm", True)
        self.auto_approve_gates = kw.get("auto_approve_gates", False)
        self.reviewer_name = kw.get("reviewer_name") or kw.get("auto_approve_reviewer_name") or ""
        self.client_name = (kw.get("client_name") or "Client").strip() or "Client"
        self.target_url = kw.get("target_url") or ""
        self.source_path = kw.get("source_path") or ""
        self.llm_grounding = bool(kw.get("llm_grounding"))
        self.created = kw.get("created") or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        self.run_dir = Path(settings.runs_dir) / self.run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.events: list[dict] = []
        self._subscribers: list[asyncio.Queue] = []
        self.orchestrator = SecurityOrchestrator(
            run_id=self.run_id,
            run_dir=self.run_dir,
            plan=self.plan,
            skip_llm=self.skip_llm,
            auto_approve_gates=self.auto_approve_gates,
            reviewer_name=self.reviewer_name,
            client_name=self.client_name,
            target_url=self.target_url,
            source_path=self.source_path,
            llm_grounding=self.llm_grounding,
        )
        events_path = self.run_dir / "events.jsonl"
        if events_path.exists():
            for line in events_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    self.events.append(json.loads(line))
        if not kw.get("restore"):
            self.persist_meta()

    def persist_meta(self) -> None:
        (self.run_dir / "run_meta.json").write_text(
            json.dumps(
                {
                    "run_id": self.run_id,
                    "plan": self.plan,
                    "skip_llm": self.skip_llm,
                    "auto_approve_gates": self.auto_approve_gates,
                    "reviewer_name": self.reviewer_name,
                    "client_name": self.client_name,
                    "target_url": self.target_url,
                    "source_path": self.source_path,
                    "llm_grounding": self.llm_grounding,
                    "created": self.created,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    async def publish(self, ev):
        payload = {"kind": ev.kind, "phase": ev.phase.value, "payload": ev.payload}
        self.events.append(payload)
        with (self.run_dir / "events.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload) + "\n")
        for q in list(self._subscribers):
            await q.put(payload)

    async def start(self):
        async for ev in run_full_pipeline(self.orchestrator):
            await self.publish(ev)


def _try_restore(run_id: str) -> Run | None:
    settings = get_settings()
    meta_path = Path(settings.runs_dir) / run_id / "run_meta.json"
    if not meta_path.exists():
        return None
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta["run_id"] = meta.get("run_id") or run_id
    meta["restore"] = True
    run = Run(**meta)
    RUNS[run.run_id] = run
    try:
        from agentic_security.reports.html import backfill_run_reports

        backfill_run_reports(run.run_dir, meta)
    except Exception:
        pass
    return run


def _get_run(run_id: str) -> Run | None:
    return RUNS.get(run_id) or _try_restore(run_id)


def _restore_all() -> None:
    settings = get_settings()
    root = Path(settings.runs_dir)
    if not root.is_dir():
        return
    for meta_path in root.glob("*/run_meta.json"):
        rid = meta_path.parent.name
        if rid not in RUNS:
            _try_restore(rid)


def _parse_skip_llm(raw: str) -> bool:
    if raw.strip() == "":
        return get_settings().skip_llm
    return raw.strip().lower() in {"true", "1", "on", "yes"}


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return TEMPLATES.TemplateResponse(request, "login.html", {"error": ""})


@app.post("/login")
async def login(request: Request, username: str = Form(""), password: str = Form("")):
    s = get_settings()
    if username == s.demo_username and password == s.demo_password:
        request.session["authenticated"] = True
        return RedirectResponse("/", status_code=303)
    return TEMPLATES.TemplateResponse(
        request, "login.html", {"error": "Unknown credentials"}, status_code=401
    )


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


@app.get("/healthz")
async def healthz():
    return {"ok": True}


@app.get("/", response_class=HTMLResponse)
async def landing(request: Request):
    return TEMPLATES.TemplateResponse(
        request,
        "landing.html",
        {
            "plans": PLAN_ORDER,
            "examples": list_examples(),
            "skip_llm_default": get_settings().skip_llm,
        },
    )


@app.post("/examples/fetch-github")
async def fetch_github_example(github_url: str = Form("")):
    try:
        card = await asyncio.to_thread(import_github_repo, github_url)
    except GitHubFetchError as exc:
        return JSONResponse({"error": exc.detail}, status_code=exc.status)
    return JSONResponse(card)


@app.post("/runs", response_class=HTMLResponse)
async def create_run(
    request: Request,
    plan: str = Form("essentials"),
    source_path: str = Form(""),
    target_url: str = Form(""),
    client_name: str = Form("Client"),
    skip_llm: str = Form(""),
    auto_approve_gates: str = Form("false"),
    auto_approve_reviewer_name: str = Form(""),
    llm_grounding: str = Form("false"),
):
    if auto_approve_gates.lower() == "true" and not auto_approve_reviewer_name.strip():
        return HTMLResponse("<div class='warn'>Approver name is required when auto-approve is on.</div>", 400)
    if not source_path.strip() or not Path(source_path).is_dir():
        return HTMLResponse(
            "<div class='warn'>Select a source tree from examples (download a GitHub zip first if needed).</div>",
            400,
        )
    run_id = uuid.uuid4().hex[:8]
    run = Run(
        run_id=run_id,
        plan=plan,
        source_path=source_path,
        target_url=target_url,
        client_name=(client_name or "").strip() or "Client",
        skip_llm=_parse_skip_llm(skip_llm),
        auto_approve_gates=auto_approve_gates.lower() == "true",
        reviewer_name=auto_approve_reviewer_name.strip(),
        llm_grounding=llm_grounding.lower() == "true" and grounding_entitled(plan),
    )
    RUNS[run_id] = run
    asyncio.create_task(run.start())
    return RedirectResponse(f"/runs/{run_id}", status_code=303)


@app.get("/runs/{run_id}", response_class=HTMLResponse)
async def run_page(request: Request, run_id: str):
    run = _get_run(run_id)
    if not run:
        return HTMLResponse("unknown run", 404)
    return TEMPLATES.TemplateResponse(
        request,
        "run.html",
        {
            "run": run,
            "plan": resolve_plan(run.plan),
            "gates": GATES,
            "phases": list(PipelinePhase),
            "phase_labels": PHASE_LABELS,
        },
    )


@app.get("/runs/{run_id}/events")
async def events(run_id: str):
    run = _get_run(run_id)
    if not run:
        return JSONResponse({"error": "unknown"}, 404)
    q: asyncio.Queue = asyncio.Queue()
    run._subscribers.append(q)

    async def gen():
        for ev in run.events:
            yield f"data: {json.dumps(ev)}\n\n"
        try:
            while True:
                ev = await q.get()
                yield f"data: {json.dumps(ev)}\n\n"
        finally:
            if q in run._subscribers:
                run._subscribers.remove(q)

    from starlette.responses import StreamingResponse

    return StreamingResponse(gen(), media_type="text/event-stream")


@app.post("/runs/{run_id}/gates/{gate_id}/{action}", response_class=HTMLResponse)
async def gate_action(
    run_id: str,
    gate_id: str,
    action: str,
    reviewer_name: str = Form("reviewer"),
    notes: str = Form(""),
):
    run = _get_run(run_id)
    if not run:
        return HTMLResponse("unknown run", 404)
    if action == "approve":
        run.orchestrator.approve_gate(gate_id, reviewer_name, notes)
        label = "Approved"
    else:
        run.orchestrator.reject_gate(gate_id, reviewer_name, notes)
        label = "Rejected"
    return HTMLResponse(f"<p class='gate-result'>{label} by {reviewer_name}: {notes or '—'}</p>")


@app.get("/runs/{run_id}/files/{filename}")
async def run_file(run_id: str, filename: str):
    run = _get_run(run_id)
    if not run:
        return HTMLResponse("unknown run", 404)
    path = run.run_dir / "reports" / filename
    if not path.exists():
        path = run.run_dir / filename
    if not path.exists():
        return HTMLResponse("missing", 404)
    from fastapi.responses import FileResponse

    return FileResponse(path)


@app.get("/runs/{run_id}/artifacts")
async def list_artifacts(run_id: str):
    run = _get_run(run_id)
    if not run:
        return JSONResponse({"files": []}, status_code=404)
    return JSONResponse({"files": list_run_artifacts(run.run_dir)})


@app.get("/runs/{run_id}/reports")
async def list_reports(run_id: str):
    from agentic_security.plans import reports_for_pdf

    run = _get_run(run_id)
    if not run:
        return JSONResponse({"files": []})
    d = run.run_dir / "reports"
    ordered = list(reports_for_pdf(run.plan))
    existing = {p.name for p in d.glob("*.html")} if d.is_dir() else set()
    files = [f for f in ordered if f in existing]
    for name in sorted(existing):
        if name not in files and name != "full-security-report.html":
            files.append(name)
    return JSONResponse({"files": files, "pdf": (d / "output-report.pdf").exists() if d.is_dir() else False})


@app.get("/runs/{run_id}/output-report.pdf")
async def output_report_pdf(run_id: str):
    from agentic_security.reports.pdf import write_output_pdf

    run = _get_run(run_id)
    if not run:
        return HTMLResponse("unknown run", 404)
    reports_dir = run.run_dir / "reports"
    if not reports_dir.is_dir() or not any(reports_dir.glob("*.html")):
        return HTMLResponse("reports not ready", 409)
    path = await asyncio.to_thread(
        write_output_pdf,
        run.run_dir,
        {
            "client_name": run.client_name,
            "plan": run.plan,
            "run_id": run.run_id,
        },
    )
    return FileResponse(
        path,
        media_type="application/pdf",
        filename=f"{run.run_id}-output-report.pdf",
    )
