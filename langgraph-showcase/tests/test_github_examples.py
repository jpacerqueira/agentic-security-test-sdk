"""GitHub zip → examples/ source trees; launch-time mode toggle only."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pytest

from agentic_security.github_examples import (
    GitHubFetchError,
    extract_zip_to_examples,
    import_github_repo,
    list_examples,
    parse_github_url,
)
from agentic_security.settings import get_settings

pytestmark = pytest.mark.filterwarnings(
    "ignore:The anyio.abc.BlockingPortal alias is deprecated:DeprecationWarning"
)


def test_parse_github_url_accepts_https_github():
    assert parse_github_url("https://github.com/octocat/Hello-World") == (
        "octocat",
        "Hello-World",
        None,
    )
    assert parse_github_url("https://www.github.com/octocat/Hello-World.git/tree/main") == (
        "octocat",
        "Hello-World",
        "main",
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://evil.com/octocat/Hello-World",
        "http://github.com/octocat/Hello-World",
        "https://github.com/just-an-owner",
        "ftp://github.com/octocat/Hello-World",
        "",
    ],
)
def test_parse_github_url_rejects_ssrf_and_junk(url):
    with pytest.raises(GitHubFetchError) as exc:
        parse_github_url(url)
    assert exc.value.status == 400


def _zip_bytes(root: str, files: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, content in files.items():
            zf.writestr(f"{root}/{name}", content)
    return buf.getvalue()


def test_extract_zip_strips_common_root(tmp_path: Path):
    content = _zip_bytes("Hello-World-main", {"app.py": b"print(1)\n", "README.md": b"# hi\n"})
    card = extract_zip_to_examples(content, "octocat_Hello-World", examples_dir=tmp_path)
    dest = Path(card["path"])
    assert dest.parent == tmp_path
    assert (dest / "app.py").read_text() == "print(1)\n"
    assert not (dest / "Hello-World-main").exists()


def test_extract_zip_skips_path_traversal(tmp_path: Path):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("ok/app.py", b"x")
        zf.writestr("../escape.txt", b"nope")
    card = extract_zip_to_examples(buf.getvalue(), "safe", examples_dir=tmp_path)
    dest = Path(card["path"])
    assert (dest / "ok" / "app.py").exists()
    assert not (tmp_path / "escape.txt").exists()


def test_extract_zip_bomb_rejected(tmp_path: Path, monkeypatch):
    from agentic_security import github_examples as ge

    monkeypatch.setattr(ge, "_MAX_UNCOMPRESSED", 10)
    content = _zip_bytes("r", {"big.txt": b"0123456789abcdef"})
    with pytest.raises(GitHubFetchError) as exc:
        extract_zip_to_examples(content, "bomb", examples_dir=tmp_path)
    assert exc.value.status == 413
    assert not (tmp_path / "bomb").exists()


def test_import_github_repo_writes_source_meta(tmp_path: Path, monkeypatch):
    from agentic_security import github_examples as ge

    content = _zip_bytes("repo-main", {"main.py": b"x = 1\n"})
    monkeypatch.setattr(ge, "fetch_github_zip", lambda owner, repo, ref: (content, "main"))
    card = import_github_repo("https://github.com/octocat/Hello-World", examples_dir=tmp_path)
    assert card["github_url"] == "https://github.com/octocat/Hello-World"
    assert (Path(card["path"]) / "main.py").exists()
    listed = list_examples(tmp_path)
    assert listed[0]["github_url"] == "https://github.com/octocat/Hello-World"


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("RUNS_DIR", str(tmp_path / "runs"))
    get_settings.cache_clear()

    import importlib
    import warnings

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

    async def _noop_warm(*_a, **_k):
        return True

    monkeypatch.setattr("agentic_security.llm.ensure_llm_ready", _noop_warm)

    c = TestClient(app_module.app)
    resp = c.post("/login", data={"username": "demo", "password": "demobxyz"})
    assert resp.status_code in (200, 303)
    yield c, app_module, tmp_path
    get_settings.cache_clear()
    app_module.RUNS.clear()


def test_fetch_github_rejects_non_github_host(client):
    c, _app, _tmp = client
    resp = c.post("/examples/fetch-github", data={"github_url": "https://evil.com/owner/repo"})
    assert resp.status_code == 400
    assert "GitHub" in resp.json()["error"]


def test_fetch_github_success_extracts_into_examples(client, monkeypatch, tmp_path):
    c, app_module, _ = client
    dest = tmp_path / "ex" / "octocat_Hello-World"
    dest.mkdir(parents=True)
    (dest / "app.py").write_text("x=1\n")

    def fake_import(_url: str) -> dict:
        return {
            "name": dest.name,
            "path": str(dest),
            "github_url": "https://github.com/octocat/Hello-World",
            "ref": "main",
        }

    monkeypatch.setattr(app_module, "import_github_repo", fake_import)
    resp = c.post(
        "/examples/fetch-github",
        data={"github_url": "https://github.com/octocat/Hello-World/tree/main"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["path"] == str(dest)
    assert data["github_url"] == "https://github.com/octocat/Hello-World"


def test_landing_does_not_preselect_sample(client):
    c, _app, _tmp = client
    resp = c.get("/")
    assert resp.status_code == 200
    html = resp.text
    assert "Source from new URL REPO" in html
    assert "Target URL" not in html
    assert 'id="source-path" value="">' in html or 'id="source-path" value=""' in html
    assert "demo-card selected" not in html
    assert 'id="skip-llm-input"' in html
    assert "skip-llm-toggle" in html
    assert "switch-toggle" in html
    assert 'id="auto-approve-input"' in html
    assert 'id="llm-grounding-input"' in html
    assert "auto-approve-toggle" not in html


def test_create_run_requires_source_tree(client):
    c, _app, _tmp = client
    resp = c.post("/runs", data={"plan": "essentials", "source_path": "", "skip_llm": "true"})
    assert resp.status_code == 400
    assert "source tree" in resp.text.lower()


def test_run_page_has_no_mode_toggle(client):
    c, _app, _tmp = client
    src = Path("examples/sample-web-api")
    resp = c.post(
        "/runs",
        data={
            "plan": "essentials",
            "source_path": str(src),
            "skip_llm": "true",
            "client_name": "Acme",
        },
        follow_redirects=False,
    )
    assert resp.status_code == 303
    run_id = resp.headers["location"].rsplit("/", 1)[-1]
    page = c.get(f"/runs/{run_id}")
    assert page.status_code == 200
    html = page.text
    assert 'id="run-skip-llm"' not in html
    assert "skip-llm-toggle" not in html
    assert "Deterministic" in html
    assert 'id="run-progress"' in html
    assert 'id="run-status"' in html
    assert "run-status running" in html
    assert "gate_4_5" not in html
    assert "Gate 5" in html
    assert "Gate 6" in html
    assert 'id="artifact-list"' in html
    assert 'id="gate-artifacts-gate_1"' in html
    mode = c.post(f"/runs/{run_id}/mode", data={"skip_llm": "false"})
    assert mode.status_code == 404


def test_artifacts_listed_from_disk(client):
    c, app_module, _tmp = client
    src = Path("examples/sample-web-api")
    resp = c.post(
        "/runs",
        data={
            "plan": "essentials",
            "source_path": str(src),
            "skip_llm": "true",
            "client_name": "Acme",
        },
        follow_redirects=False,
    )
    assert resp.status_code == 303
    run_id = resp.headers["location"].rsplit("/", 1)[-1]
    run = app_module.RUNS[run_id]
    run.orchestrator.write_json("scope.json", {"client": "Acme"})
    listed = c.get(f"/runs/{run_id}/artifacts")
    assert listed.status_code == 200
    keys = [f["key"] for f in listed.json()["files"]]
    assert "scope.json" in keys
    assert listed.json()["files"][0]["gate_id"] == "gate_1"
