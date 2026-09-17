from pathlib import Path

from agentic_security.settings import get_settings
from agentic_security.web.app import Run, _parse_skip_llm, apply_run_mode


def test_parse_skip_llm_false_is_llm():
    assert _parse_skip_llm("false") is False
    assert _parse_skip_llm("true") is True


def test_apply_run_mode_toggles_orchestrator(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("RUNS_DIR", str(tmp_path))
    get_settings.cache_clear()
    run = Run(
        run_id="mode1",
        skip_llm=True,
        source_path="examples/sample-web-api",
        plan="essentials",
        client_name="Acme",
    )
    assert run.orchestrator.skip_llm is True
    out = apply_run_mode(run, False)
    assert out["mode"] == "llm"
    assert run.skip_llm is False
    assert run.orchestrator.skip_llm is False
    meta = (tmp_path / "mode1" / "run_meta.json").read_text()
    assert '"skip_llm": false' in meta
    apply_run_mode(run, True)
    assert run.orchestrator.skip_llm is True
    get_settings.cache_clear()
