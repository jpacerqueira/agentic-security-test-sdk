from pathlib import Path

from agentic_security.plans import reports_for, reports_for_pdf
from agentic_security.reports.pdf import combined_html, write_output_pdf


def test_pdf_order_starts_with_executive_summary():
    essentials = reports_for_pdf("essentials")
    assert essentials[0] == "executive-summary.html"
    assert "pentest-assessment.html" in essentials
    assert "full-security-report.html" not in reports_for_pdf("professional")
    assert reports_for("professional")[-1] == "full-security-report.html"
    assert reports_for_pdf("professional")[0] == "executive-summary.html"


async def test_output_pdf_is_a4_pack(tmp_path: Path):
    from agentic_security.orchestration.driver import run_full_pipeline
    from agentic_security.orchestration.pipeline import SecurityOrchestrator

    orch = SecurityOrchestrator(
        run_id="pdf1",
        run_dir=tmp_path / "pdf1",
        plan="professional",
        skip_llm=True,
        auto_approve_gates=True,
        reviewer_name="Jane",
        client_name="Client",
        target_url="https://app.example.com",
        source_path="examples/sample-web-api",
    )
    async for _ in run_full_pipeline(orch):
        pass
    meta = {"client_name": orch.client_name, "plan": orch.plan, "run_id": orch.run_id}
    html, names = combined_html(orch.run_dir, meta)
    assert names[0] == "executive-summary.html"
    assert "Output report" in html
    assert "Contents (executive summary first)" in html
    path = write_output_pdf(orch.run_dir, meta)
    data = path.read_bytes()
    assert data.startswith(b"%PDF")
    assert len(data) > 2000
    assert path.name == "output-report.pdf"
