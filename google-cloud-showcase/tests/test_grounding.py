from __future__ import annotations

import importlib
import warnings
from pathlib import Path

import pytest

from agentic_security.grounding import (
    collect_grounding,
    collect_grounding_for_run,
    fetch_github_meta,
    format_grounding_prompt,
)
from agentic_security.plans import grounding_entitled, reports_for, reports_for_pdf
from agentic_security.scanners import compliance_pack
from agentic_security.settings import get_settings

pytestmark = pytest.mark.filterwarnings(
    "ignore:The anyio.abc.BlockingPortal alias is deprecated:DeprecationWarning"
)


def test_ultra_professional_has_grounding_report():
    assert "llm-grounding.html" in reports_for("ultra-professional")
    assert "full-security-report.html" in reports_for("ultra-professional")
    assert reports_for("ultra-professional")[-1] == "full-security-report.html"
    assert "llm-grounding.html" in reports_for_pdf("ultra-professional")
    assert "llm-grounding.html" not in reports_for("professional")
    assert grounding_entitled("ultra-professional") is True
    assert grounding_entitled("professional") is False
    assert grounding_entitled("essentials") is False


def test_ultra_professional_inherits_professional_grc():
    pack = compliance_pack("ultra-professional")
    assert pack["risk_register_enabled"] is True
    assert pack["issue_management_enabled"] is True
    assert pack["access_reviews_enabled"] is True
    assert "PCI DSS" in pack["frameworks"]
    assert compliance_pack("essentials")["risk_register_enabled"] is False


def test_collect_grounding_from_sample():
    pack = collect_grounding(
        "examples/sample-web-api",
        target_url="",
        client_name="Acme",
    )
    assert pack["enabled"] is True
    assert pack["client"] == "Acme"
    assert pack["inventory"]["files"] >= 2
    assert pack["facts"]
    prompt = format_grounding_prompt(pack)
    assert "G-" in prompt
    assert "cite fact ids" in prompt.lower()
    assert format_grounding_prompt(None) == ""


def test_collect_grounding_includes_github_meta(tmp_path: Path):
    src = tmp_path / "app"
    src.mkdir()
    (src / "README.md").write_text("# Demo\n", encoding="utf-8")
    (src / ".source.json").write_text(
        '{"github_url": "https://github.com/octocat/Hello-World"}', encoding="utf-8"
    )
    (src / "app.py").write_text("password = 'secret'\n@app.get('/login')\n", encoding="utf-8")
    meta = {
        "full_name": "octocat/Hello-World",
        "description": "demo",
        "language": "Python",
        "topics": ["demo"],
        "html_url": "https://github.com/octocat/Hello-World",
        "license": "MIT",
    }
    pack = collect_grounding(str(src), client_name="Acme", github_meta=meta)
    kinds = {f["kind"] for f in pack["facts"]}
    assert "github" in kinds
    assert "manifest" in kinds
    prompt = format_grounding_prompt(pack)
    assert "octocat/Hello-World" in prompt


def test_fetch_github_meta_rejects_non_github_host(monkeypatch):
    def boom(*_a, **_k):
        raise AssertionError("must not fetch a client-supplied host")

    monkeypatch.setattr("agentic_security.grounding.httpx.Client", boom)
    meta = fetch_github_meta("https://evil.com/octocat/Hello-World")
    assert "error" in meta


def test_collect_grounding_for_run_uses_api_github_only(tmp_path: Path, monkeypatch):
    src = tmp_path / "app"
    src.mkdir()
    (src / "README.md").write_text("# Demo\n", encoding="utf-8")
    (src / ".source.json").write_text(
        '{"github_url": "https://github.com/octocat/Hello-World"}', encoding="utf-8"
    )

    seen: list[str] = []

    class FakeResp:
        status_code = 200

        def json(self):
            return {
                "full_name": "octocat/Hello-World",
                "description": "demo",
                "language": "Python",
                "topics": [],
                "license": {"spdx_id": "MIT"},
            }

    class FakeClient:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def get(self, url):
            seen.append(url)
            return FakeResp()

    monkeypatch.setattr("agentic_security.grounding.httpx.Client", FakeClient)
    pack = collect_grounding_for_run(str(src), client_name="Acme")
    assert seen == ["https://api.github.com/repos/octocat/Hello-World"]
    assert pack["github_meta"]["full_name"] == "octocat/Hello-World"


async def test_ultra_pipeline_writes_grounding_pack(tmp_path: Path):
    from agentic_security.orchestration.driver import run_full_pipeline
    from agentic_security.orchestration.pipeline import SecurityOrchestrator

    orch = SecurityOrchestrator(
        run_id="ug1",
        run_dir=tmp_path / "ug1",
        plan="ultra-professional",
        skip_llm=True,
        auto_approve_gates=True,
        reviewer_name="Jane",
        client_name="Acme",
        source_path="examples/sample-web-api",
        llm_grounding=True,
    )
    events = [ev async for ev in run_full_pipeline(orch)]
    assert "pipeline_completed" in [e.kind for e in events]
    assert (tmp_path / "ug1" / "grounding.json").exists()
    html = (tmp_path / "ug1" / "reports" / "llm-grounding.html").read_text()
    assert "G-" in html
    assert "Grounding facts" in html


async def test_ultra_without_checkbox_skips_grounding_json(tmp_path: Path):
    from agentic_security.orchestration.driver import run_full_pipeline
    from agentic_security.orchestration.pipeline import SecurityOrchestrator

    orch = SecurityOrchestrator(
        run_id="ug0",
        run_dir=tmp_path / "ug0",
        plan="ultra-professional",
        skip_llm=True,
        auto_approve_gates=True,
        reviewer_name="Jane",
        client_name="Acme",
        source_path="examples/sample-web-api",
        llm_grounding=False,
    )
    async for _ in run_full_pipeline(orch):
        pass
    assert not (tmp_path / "ug0" / "grounding.json").exists()
    html = (tmp_path / "ug0" / "reports" / "llm-grounding.html").read_text()
    assert "not enabled" in html.lower()


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("RUNS_DIR", str(tmp_path / "runs"))
    get_settings.cache_clear()
    warnings.filterwarnings(
        "ignore",
        message="The anyio.abc.BlockingPortal alias is deprecated.*",
        category=DeprecationWarning,
    )
    from fastapi.testclient import TestClient

    app_module = importlib.import_module("agentic_security.web.app")

    async def _noop_start(self):
        return None

    monkeypatch.setattr(app_module.Run, "start", _noop_start)
    monkeypatch.setattr("agentic_security.llm.ensure_llm_ready", lambda *_a, **_k: True)

    c = TestClient(app_module.app)
    resp = c.post("/login", data={"username": "demo", "password": "demobxyz"})
    assert resp.status_code in (200, 303)
    yield c, app_module, tmp_path
    get_settings.cache_clear()
    app_module.RUNS.clear()


def test_landing_shows_ultra_professional_and_hidden_grounding(client):
    c, _app, _tmp = client
    html = c.get("/").text
    assert "Ultra-Professional" in html
    assert 'data-plan="ultra-professional"' in html
    assert 'id="grounding-field"' in html
    assert "LLM grounding (this run)" in html
    assert 'id="llm-grounding-input"' in html
    assert 'id="auto-approve-input"' in html


def test_create_run_ignores_grounding_on_lower_tiers(client):
    c, app_module, _tmp = client
    src = Path("examples/sample-web-api")
    resp = c.post(
        "/runs",
        data={
            "plan": "essentials",
            "source_path": str(src),
            "skip_llm": "true",
            "llm_grounding": "true",
            "client_name": "Acme",
        },
        follow_redirects=False,
    )
    assert resp.status_code == 303
    run_id = resp.headers["location"].rsplit("/", 1)[-1]
    run = app_module.RUNS[run_id]
    assert run.llm_grounding is False
    page = c.get(f"/runs/{run_id}").text
    assert "LLM grounding" not in page


def test_create_run_honours_grounding_on_ultra(client):
    c, app_module, _tmp = client
    src = Path("examples/sample-web-api")
    resp = c.post(
        "/runs",
        data={
            "plan": "ultra-professional",
            "source_path": str(src),
            "skip_llm": "true",
            "llm_grounding": "true",
            "client_name": "Acme",
        },
        follow_redirects=False,
    )
    assert resp.status_code == 303
    run_id = resp.headers["location"].rsplit("/", 1)[-1]
    run = app_module.RUNS[run_id]
    assert run.llm_grounding is True
    page = c.get(f"/runs/{run_id}").text
    assert "LLM grounding" in page
    assert "Ultra-Professional" in page


def test_create_run_blank_client_defaults_to_client(client):
    c, app_module, _tmp = client
    src = Path("examples/sample-web-api")
    resp = c.post(
        "/runs",
        data={
            "plan": "essentials",
            "source_path": str(src),
            "skip_llm": "true",
            "client_name": "  ",
        },
        follow_redirects=False,
    )
    assert resp.status_code == 303
    run_id = resp.headers["location"].rsplit("/", 1)[-1]
    run = app_module.RUNS[run_id]
    assert run.client_name == "Client"
    page = c.get(f"/runs/{run_id}").text
    assert "Client" in page
