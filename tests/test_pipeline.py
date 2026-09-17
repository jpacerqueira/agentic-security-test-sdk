from pathlib import Path

from agentic_security.plans import reports_for
from agentic_security.scanners import appsec_findings, discover_scope, jailbreak_assessment


def test_professional_has_full_report():
    assert "full-security-report.html" in reports_for("professional")
    assert "full-security-report.html" not in reports_for("essentials")


def test_scope_discovers_example(tmp_path: Path):
    src = Path("examples/sample-web-api")
    scope = discover_scope(str(src), "https://cloud.example.com", "Acme")
    assert scope["client"] == "Acme"
    assert "cloud.example.com" in scope["domains"]
    assert scope["files_in_tree"] >= 2


def test_appsec_flags_pickle_and_tls():
    findings = appsec_findings("examples/sample-web-api", "https://app.example.com")
    titles = " ".join(f["title"] for f in findings["findings"]).lower()
    assert "deserial" in titles or "pickle" in titles or "tls" in titles
    assert findings["test_cases"]["authorization"]
    assert len(findings["owasp_top10"]) == 10
    assert findings["findings"][0]["id"].startswith("AS-")
    assert findings["findings"][0]["evidence"]


def test_jailbreak_catalogue_has_six_probes():
    j = jailbreak_assessment("examples/sample-web-api")
    assert len(j["probes"]) == 6


async def test_pipeline_auto_approves(tmp_path: Path):
    from agentic_security.orchestration.driver import run_full_pipeline
    from agentic_security.orchestration.pipeline import SecurityOrchestrator

    orch = SecurityOrchestrator(
        run_id="t1",
        run_dir=tmp_path / "t1",
        plan="professional",
        skip_llm=True,
        auto_approve_gates=True,
        reviewer_name="Jane",
        client_name="XYZ Reality Ltd",
        target_url="https://cloud.xyzreality.com",
        source_path="examples/sample-web-api",
    )
    events = [ev async for ev in run_full_pipeline(orch)]
    kinds = [e.kind for e in events]
    assert "pipeline_completed" in kinds
    assert (tmp_path / "t1" / "reports" / "pentest-assessment.html").exists()
    assert (tmp_path / "t1" / "reports" / "trivy-scan.html").exists()
    assert (tmp_path / "t1" / "reports" / "full-security-report.html").exists()
    html = (tmp_path / "t1" / "reports" / "pentest-assessment.html").read_text()
    assert "OWASP Top 10" in html
    assert "CVSS" in html
    assert "2.5 Personnel" in html
    assert "AS-001" in html
    access = (tmp_path / "t1" / "reports" / "access-management.html").read_text()
    assert "Identity inventory" in access
    assert "Joiner" in access
    jail = (tmp_path / "t1" / "reports" / "jailbreak-assessment.html").read_text()
    assert "Scoring rubric" in jail
    assert "Expected defense" in jail
    risk = (tmp_path / "t1" / "reports" / "risk-register.html").read_text()
    assert "Residual" in risk
    issues = (tmp_path / "t1" / "reports" / "issue-management.html").read_text()
    assert "ISS-" in issues
    asvs = (tmp_path / "t1" / "reports" / "owasp-asvs.html").read_text()
    assert "V2" in asvs
    assert (tmp_path / "t1" / "access_management.json").exists()
    assert orch.plan == "professional"


async def test_consecutive_deterministic_then_llm_then_deterministic(tmp_path: Path, monkeypatch):
    import json

    from agentic_security import llm as llm_mod
    from agentic_security.orchestration.driver import run_full_pipeline
    from agentic_security.orchestration.pipeline import SecurityOrchestrator

    llm_mod.reset_warm_state()

    async def ready(*, force: bool = False):
        return True, "warm"

    async def gen_json(*_a, **_k):
        return {"executive_overview": "ov", "narrative": "n", "tactical": "t", "strategic": "s"}

    async def gen_text(*_a, **_k):
        return "I cannot ignore previous instructions."

    monkeypatch.setattr(llm_mod, "ensure_llm_ready", ready)
    monkeypatch.setattr(llm_mod, "adk_available", lambda: True)
    monkeypatch.setattr(llm_mod, "generate_json", gen_json)
    monkeypatch.setattr(llm_mod, "generate_text", gen_text)

    async def one(rid: str, skip: bool) -> None:
        orch = SecurityOrchestrator(
            run_id=rid,
            run_dir=tmp_path / rid,
            plan="essentials",
            skip_llm=skip,
            auto_approve_gates=True,
            reviewer_name="Jane",
            client_name="Acme",
            target_url="https://app.example.com",
            source_path="examples/sample-web-api",
        )
        events = [ev async for ev in run_full_pipeline(orch)]
        assert "pipeline_completed" in [e.kind for e in events]
        assert (tmp_path / rid / "reports" / "pentest-assessment.html").exists()
        scope = json.loads((tmp_path / rid / "scope.json").read_text())
        if skip:
            assert scope.get("mode") == "deterministic"
        else:
            assert scope.get("mode") == "llm"

    await one("det1", True)
    await one("llm1", False)
    await one("det2", True)
