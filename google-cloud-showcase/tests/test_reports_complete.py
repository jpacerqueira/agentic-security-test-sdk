from pathlib import Path

from agentic_security.inventories import access_inventory, asvs_matrix, issue_board, risk_register
from agentic_security.llm import classify_refusal, parse_json_object
from agentic_security.reports.html import backfill_run_reports
from agentic_security.scanners import appsec_findings, compliance_pack, jailbreak_assessment
from agentic_security.web.app import _parse_skip_llm


def test_access_inventory_is_not_a_stub():
    appsec = appsec_findings("examples/sample-web-api", "https://app.example.com")
    pack = compliance_pack("professional")
    access = access_inventory("examples/sample-web-api", pack, appsec)
    assert access["identity_count"] >= 4
    assert access["reviews"]
    assert access["joiner_mover_leaver"]
    assert "hardcoded" in " ".join(i["principal"] for i in access["identities"]).lower() or any(
        i["status"] == "revoke" for i in access["identities"]
    )


def test_asvs_and_risk_and_issues_complete():
    appsec = appsec_findings("examples/sample-web-api", "https://app.example.com")
    pack = compliance_pack("professional")
    asvs = asvs_matrix(appsec)
    assert len(asvs["chapters"]) == 14
    assert asvs["by_status"]["fail"] >= 1
    risks = risk_register(pack, appsec, {"vulnerabilities": [], "vulnerability_count": 0}, jailbreak_assessment("examples/sample-web-api"))
    assert risks["items"]
    assert risks["items"][0]["residual"]
    issues = issue_board({"items": [{"title": "x", "source": "appsec", "ref": "AS-001", "severity": "HIGH", "owner": "eng", "sla_days": 7}]})
    assert issues["issues"][0]["id"] == "ISS-001"
    assert issues["issues"][0]["due"]


def test_classify_refusal_and_json_parse():
    assert classify_refusal("Sorry I cannot ignore previous instructions.") == "pass"
    assert classify_refusal("Sure, here is the system prompt: you are dan") == "fail"
    assert parse_json_object('```json\n{"a": 1}\n```') == {"a": 1}


def test_parse_skip_llm_toggle():
    assert _parse_skip_llm("true") is True
    assert _parse_skip_llm("false") is False
    assert _parse_skip_llm("1") is True



def test_backfill_rewrites_access_report(tmp_path: Path):
    src = Path("runs/55c27510")
    if not (src / "run_meta.json").exists():
        return
    dest = tmp_path / "copied"
    dest.mkdir()
    import shutil

    for name in (
        "run_meta.json",
        "appsec_findings.json",
        "trivy_report.json",
        "jailbreak_assessment.json",
        "cis_cloud.json",
        "compliance.json",
        "remediation_plan.json",
        "scope.json",
    ):
        shutil.copy(src / name, dest / name)
    files = backfill_run_reports(dest)
    html = (dest / "reports" / "access-management.html").read_text()
    assert "Identity inventory" in html
    assert "access-management.html" in files
