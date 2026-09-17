"""HTML reports — Micro-Cosmos design tokens, pentest metric surface, Vanta GRC, Trivy."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import html
import json

from agentic_security.brand import APP_NAME
from agentic_security.plans import reports_for

INK = "#171D1D"
SAGE = "#E6EAE6"
MUTED = "#91969C"
ACCENT = "#ED3A12"
RULE = "#D5D5D5"
BG = "#FFFFFF"


def esc(s: Any) -> str:
    return html.escape("" if s is None else str(s))


def _client(meta: dict | None) -> str:
    """Launch-form Client name. Empty values fall back to Client."""
    return ((meta or {}).get("client_name") or "").strip() or "Client"


def _load(run_dir: Path, name: str) -> dict:
    p = run_dir / name
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def shell(title: str, body: str, *, client: str = "Client", classification: str | None = None) -> str:
    who = (client or "").strip() or "Client"
    cls = classification or f"{who} confidential"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{esc(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter+Tight:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root {{ --ink:{INK}; --sage:{SAGE}; --muted:{MUTED}; --accent:{ACCENT}; --rule:{RULE}; --bg:{BG}; }}
* {{ box-sizing: border-box; }}
body {{ margin:0; background:var(--bg); color:var(--ink); font-family:"Inter Tight",sans-serif; font-size:14px; line-height:1.55; }}
header.cover {{ padding:48px 48px 36px; border-top:4px solid var(--ink); }}
.dot {{ width:14px; height:14px; border-radius:50%; background:var(--accent); margin-bottom:28px; }}
.cls {{ font-family:"IBM Plex Mono",monospace; font-size:11px; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); }}
h1,h2,h3 {{ font-family:"Instrument Serif",Georgia,serif; font-weight:400; letter-spacing:-.005em; margin:0 0 .45em; }}
h1 {{ font-size:2.4rem; }}
h2 {{ font-size:1.5rem; margin-top:36px; }}
main {{ padding:0 48px 64px; max-width:1100px; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; }}
th,td {{ text-align:left; padding:8px 10px; border-bottom:1px solid var(--rule); vertical-align:top; }}
th {{ font-family:"IBM Plex Mono",monospace; font-size:11px; text-transform:uppercase; letter-spacing:.06em; color:var(--muted); }}
.badge {{ display:inline-block; padding:2px 7px; font-family:"IBM Plex Mono",monospace; font-size:11px; letter-spacing:.04em; text-transform:uppercase; }}
.CRITICAL,.HIGH {{ background:#FDECEA; color:#C0392B; border:1px solid #F5C6C2; }}
.MEDIUM {{ background:#FEF3E2; color:#A0522D; border:1px solid #F5DFB8; }}
.LOW,.INFO,.UNKNOWN,.PASS,.pass,.met,.collected,.in-progress {{ background:#EAF4EA; color:#2E7D32; border:1px solid #B8DDB8; }}
.fail,.gap,.catalogue {{ background:#FEF3E2; color:#A0522D; border:1px solid #F5DFB8; }}
.evidence {{ background:var(--sage); padding:10px 12px; font-family:"IBM Plex Mono",monospace; font-size:12px; white-space:pre-wrap; margin:8px 0 16px; }}
.statrow {{ display:flex; gap:18px; flex-wrap:wrap; margin:18px 0 28px; }}
.stat {{ background:var(--sage); padding:14px 18px; min-width:110px; }}
.stat b {{ display:block; font-family:"Instrument Serif",serif; font-size:1.8rem; font-weight:400; }}
.stat span {{ font-family:"IBM Plex Mono",monospace; font-size:11px; text-transform:uppercase; color:var(--muted); letter-spacing:.06em; }}
.callout {{ background:#FEF3E2; border-left:3px solid var(--accent); padding:14px 18px; margin:20px 0; }}
.footer {{ font-family:"IBM Plex Mono",monospace; font-size:11px; color:var(--muted); padding:24px 48px; border-top:1px solid var(--rule); }}
code {{ font-family:"IBM Plex Mono",monospace; background:var(--sage); padding:0 4px; }}
</style>
</head>
<body>
<header class="cover">
  <div class="dot"></div>
  <p class="cls">{esc(cls)} · {esc(APP_NAME)}</p>
  <h1>{esc(title)}</h1>
</header>
<main>
{body}
</main>
<div class="footer">{esc(APP_NAME)} · snapshot in time</div>
</body></html>
"""


def _sev_badge(sev: str) -> str:
    s = (sev or "INFO").upper()
    return f'<span class="badge {esc(s)}">{esc(s)}</span>'


def _stats(pairs: list[tuple[str, Any]]) -> str:
    cells = "".join(
        f'<div class="stat"><b>{esc(v)}</b><span>{esc(k)}</span></div>' for k, v in pairs
    )
    return f'<div class="statrow">{cells}</div>'


def _table(headers: list[str], rows: list[list[Any]], empty: str = "None recorded.") -> str:
    head = "".join(f"<th>{esc(h)}</th>" for h in headers)
    if not rows:
        return f"<table><tr>{head}</tr><tr><td colspan='{len(headers)}'>{esc(empty)}</td></tr></table>"
    body = []
    for row in rows:
        cells = []
        for i, cell in enumerate(row):
            if i < len(headers) and headers[i].lower() in {"severity", "status", "priority"}:
                cells.append(f"<td>{_sev_badge(cell)}</td>")
            else:
                cells.append(f"<td>{cell if isinstance(cell, str) and cell.startswith('<') else esc(cell)}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return f"<table><tr>{head}</tr>{''.join(body)}</table>"


def pentest_html(run_dir: Path, meta: dict) -> str:
    scope = _load(run_dir, "scope.json")
    appsec = _load(run_dir, "appsec_findings.json")
    trivy = _load(run_dir, "trivy_report.json")
    plan = _load(run_dir, "remediation_plan.json")
    findings = appsec.get("findings") or []
    by = appsec.get("by_severity") or {}
    body = []
    body.append("<h2>1. Executive summary</h2>")
    client = _client(meta) or (scope.get("client") or "").strip() or "Client"
    overview = scope.get("executive_overview") or appsec.get("llm_narrative") or (
        f"Penetration test and security assessment for {client} "
        "covering grey-box / black-box application and API testing, vulnerability scans of the source tree "
        "(Trivy), jailbreak surface mapping, and CIS cloud-control catalogue."
    )
    body.append(f"<p>{esc(overview)} Methodology: {esc(', '.join(scope.get('methodology') or []))}.</p>")
    if appsec.get("attack_path"):
        body.append(f"<div class='callout'><strong>Attack path.</strong> {esc(appsec.get('attack_path'))}</div>")
    body.append(_stats([
        ("Critical", by.get("CRITICAL", 0)),
        ("High", by.get("HIGH", 0)),
        ("Medium", by.get("MEDIUM", 0)),
        ("Low", by.get("LOW", 0)),
        ("Info", by.get("INFO", 0)),
        ("Trivy CVEs", trivy.get("vulnerability_count", 0)),
    ]))
    body.append("<h2>2. Project overview</h2>")
    body.append("<h3>2.1 Vulnerabilities</h3>")
    body.append("<p>Counts by CVSS v3 band.</p>")
    bands = appsec.get("cvss_bands") or {}
    body.append(_table(["Band", "Score"], [[k, v] for k, v in bands.items()]))
    body.append("<h3>2.2 Root cause analysis</h3>")
    rc = appsec.get("root_causes") or plan.get("root_causes") or {}
    body.append(_table(["Root cause", "Count"], [[k, v] for k, v in rc.items()], empty="No coded findings."))
    body.append("<h3>2.3 Scope of engagement</h3>")
    body.append(_table(["Domain / asset"], [[d] for d in (scope.get("domains") or [])]))
    body.append(
        f"<p>Source tree: <code>{esc(scope.get('source_path'))}</code> · {esc(scope.get('files_in_tree'))} files. "
        f"Window {esc((scope.get('engagement_window') or {}).get('start'))} – "
        f"{esc((scope.get('engagement_window') or {}).get('end'))}.</p>"
    )
    out = scope.get("assets_out_of_scope") or []
    if out:
        body.append("<p><strong>Out of scope:</strong> " + esc(", ".join(out)) + "</p>")
    body.append("<h3>2.4 Assessment objectives</h3><ul>" + "".join(
        f"<li>{esc(o)}</li>" for o in (scope.get("objectives") or [])
    ) + "</ul>")
    body.append("<h3>2.5 Personnel</h3>")
    body.append(_table(
        ["Role", "Name"],
        [[p.get("role"), p.get("name")] for p in (scope.get("personnel") or [])],
        empty="Personnel not recorded.",
    ))
    body.append("<h3>2.6 Confidentiality · 2.7 Disclaimer</h3>")
    body.append(f"<p>{esc(scope.get('confidentiality'))}</p><p>{esc(scope.get('disclaimer'))}</p>")

    body.append("<h2>3. Testing methodology</h2>")
    body.append(
        "<p>Host/service discovery, then vulnerability scanning, then DAST-style and source-assisted "
        "application tests against OWASP ASVS 4.0 / WSTG. False positives are called out rather than silently dropped. "
        "Roles tested: " + esc(", ".join(scope.get("tester_roles") or [])) + ".</p>"
    )
    body.append("<h3>3.1 Narrative of the tests</h3>")
    body.append("<ul><li>External / tree vulnerability scan (Trivy filesystem + fallback)</li>"
                "<li>Application security tests (authenticated / unauthenticated heuristics)</li>"
                "<li>Jailbreak / prompt-injection surface mapping (live in LLM mode)</li>"
                "<li>CIS cloud control catalogue</li></ul>")

    body.append("<h2>4. Summary of vulnerabilities</h2>")
    body.append(_table(
        ["ID", "WSTG", "Vulnerability", "Severity", "CVSS"],
        [
            [f.get("id"), f.get("wstg") or f.get("ref"), f.get("title"), f.get("severity"), f.get("cvss_base")]
            for f in findings
        ],
        empty="No application findings in this pass.",
    ))

    body.append("<h2>5. Findings</h2>")
    for f in findings:
        body.append(
            f"<h3>{esc(f.get('id'))} {esc(f.get('title'))} {_sev_badge(f.get('severity'))}</h3>"
        )
        body.append(_table(
            ["Risk factor", "CVSS base", "Vector", "Impact", "Exploitability"],
            [[f.get("severity"), f.get("cvss_base"), f.get("cvss_vector"), f.get("cvss_impact"), f.get("cvss_exploitability")]],
        ))
        body.append(
            f"<p><strong>OWASP:</strong> {esc(f.get('owasp'))} · <strong>Root cause:</strong> {esc(f.get('root_cause'))} "
            f"· <strong>WSTG:</strong> {esc(f.get('wstg') or f.get('ref'))}</p>"
        )
        body.append(f"<p>{esc(f.get('description'))}</p>")
        if f.get("business_impact"):
            body.append(f"<p><strong>Business impact.</strong> {esc(f.get('business_impact'))}</p>")
        body.append("<p><strong>Affected</strong></p><ul>" + "".join(
            f"<li><code>{esc(a)}</code></li>" for a in (f.get("affected") or [])
        ) + "</ul>")
        if f.get("evidence"):
            body.append("<p><strong>Evidence</strong></p>")
            for ev in f["evidence"]:
                body.append(
                    f"<div class='evidence'>{esc(ev.get('file'))}:{esc(ev.get('marker'))}\n{esc(ev.get('snippet'))}</div>"
                )
        body.append("<p><strong>Steps to reproduce</strong></p><ul>" + "".join(
            f"<li>{esc(s)}</li>" for s in (f.get("steps_to_reproduce") or [])
        ) + "</ul>")
        body.append("<p><strong>Recommendations</strong></p><ul>" + "".join(
            f"<li>{esc(r)}</li>" for r in (f.get("recommendations") or [])
        ) + "</ul>")
        body.append("<p><strong>References</strong></p><ul>" + "".join(
            f"<li>{esc(r)}</li>" for r in (f.get("references") or [])
        ) + "</ul>")

    body.append("<h2>6. Appendix</h2>")
    body.append("<h3>6.1 Test cases (OWASP WSTG)</h3>")
    for k, vs in (appsec.get("test_cases") or {}).items():
        body.append(f"<p><strong>{esc(k.replace('_',' '))}</strong> — {esc(', '.join(vs))}</p>")
    body.append("<h3>6.2 OWASP Top 10 coverage</h3><ul>" + "".join(
        f"<li>{esc(x)}</li>" for x in (appsec.get("owasp_top10") or [])
    ) + "</ul>")
    body.append("<h3>6.3 Used tools</h3><ul>"
                "<li>Trivy (filesystem CVE scan)</li>"
                f"<li>{esc(APP_NAME)} AppSec heuristic (ASVS / WSTG)</li>"
                "<li>Google ADK LiteLlm → Ollama OpenAI-compatible /v1 (LLM mode)</li>"
                "<li>Jailbreak probe catalogue</li>"
                "<li>CIS Azure Foundations control catalogue</li></ul>")
    body.append("<h3>6.4 Root causes</h3><p>Insecure configuration · Improper patch management · "
                "Lack of adequate security awareness · Improper security architecture · Insecure coding practices.</p>")
    body.append("<h3>6.5 Terminology</h3><p>Black-box, grey-box, CVSS, NVD, application-layer vs network-layer testing.</p>")
    return shell(
        f"Application pentest & security assessment — {client}",
        "\n".join(body),
        client=client,
    )


def trivy_html(run_dir: Path, meta: dict) -> str:
    t = _load(run_dir, "trivy_report.json")
    by = t.get("by_severity") or {}
    body = [
        f"<p>Scanner: <code>{esc(t.get('scanner'))}</code>. {esc(t.get('note') or '')} "
        f"Client <strong>{esc(_client(meta))}</strong>.</p>",
        _stats([(k.title(), by.get(k, 0)) for k in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN")]),
        "<p>Upgrade the listed packages to the fixed versions. HIGH+ items also appear on the remediation SLA board.</p>",
        _table(
            ["ID", "Pkg", "Installed", "Fixed", "Severity", "CVSS", "Target", "Title"],
            [
                [
                    v.get("id"),
                    v.get("pkg"),
                    v.get("installed"),
                    v.get("fixed"),
                    v.get("severity"),
                    v.get("cvss"),
                    v.get("target"),
                    v.get("title"),
                ]
                for v in (t.get("vulnerabilities") or [])
            ],
            empty="No CVE rows. Install Trivy on PATH for a live scan.",
        ),
    ]
    return shell("Trivy / dependency vulnerability scan", "\n".join(body), client=_client(meta))


def exec_html(run_dir: Path, meta: dict) -> str:
    appsec = _load(run_dir, "appsec_findings.json")
    trivy = _load(run_dir, "trivy_report.json")
    plan = _load(run_dir, "remediation_plan.json")
    risks = _load(run_dir, "risk_register.json")
    by = appsec.get("by_severity") or {}
    body = [
        f"<p>Client <strong>{esc(_client(meta))}</strong> · plan <code>{esc(meta.get('plan'))}</code> · run <code>{esc(meta.get('run_id'))}</code>.</p>",
        _stats([
            ("App findings", len(appsec.get("findings") or [])),
            ("Trivy CVEs", trivy.get("vulnerability_count", 0)),
            ("Plan items", len(plan.get("items") or [])),
            ("High+", by.get("CRITICAL", 0) + by.get("HIGH", 0)),
            ("Risks", len(risks.get("items") or [])),
        ]),
        f"<div class='callout'><p><strong>Tactical.</strong> {esc(plan.get('tactical'))}</p>"
        f"<p><strong>Strategic.</strong> {esc(plan.get('strategic'))}</p></div>",
        "<h2>Quick wins</h2><ul>" + "".join(f"<li>{esc(w)}</li>" for w in (plan.get("quick_wins") or [])) + "</ul>",
        "<h2>Remediation SLA board</h2>",
        _table(
            ["Source", "Ref", "Title", "Severity", "Owner", "SLA (days)"],
            [
                [it.get("source"), it.get("ref"), it.get("title"), it.get("severity"), it.get("owner"), it.get("sla_days")]
                for it in (plan.get("items") or [])
            ],
        ),
    ]
    return shell("Executive summary", "\n".join(body), client=_client(meta))


def jail_html(run_dir: Path, meta: dict) -> str:
    j = _load(run_dir, "jailbreak_assessment.json")
    rubric = j.get("scoring_rubric") or {}
    body = [
        _stats([
            ("Surface score", j.get("jailbreak_surface_score", 0)),
            ("Probes", len(j.get("probes") or [])),
            ("Pass", j.get("pass_count", 0)),
            ("Fail", j.get("fail_count", 0)),
            ("Live", "yes" if j.get("live") else "no"),
        ]),
        f"<p>{esc(j.get('note'))}</p>",
        "<h2>Scoring rubric</h2>",
        _table(["Verdict", "Meaning"], [[k, v] for k, v in rubric.items()]),
        "<h2>Probe pack</h2>",
        _table(
            ["ID", "Family", "Severity", "Status", "Expected defense", "Probe"],
            [
                [
                    p.get("id"),
                    p.get("family"),
                    p.get("severity"),
                    p.get("status"),
                    p.get("expected_defense"),
                    p.get("prompt"),
                ]
                for p in (j.get("probes") or [])
            ],
        ),
    ]
    if any(p.get("response_excerpt") for p in (j.get("probes") or [])):
        body.append("<h2>Live model replies</h2>")
        for p in j.get("probes") or []:
            if not p.get("response_excerpt"):
                continue
            body.append(f"<h3>{esc(p.get('id'))} {_sev_badge(p.get('status'))}</h3>")
            body.append(f"<div class='evidence'>{esc(p.get('response_excerpt'))}</div>")
            body.append(f"<p><strong>Residual risk.</strong> {esc(p.get('residual_risk'))}</p>")
    body.append("<h2>Source markers</h2>")
    body.append(_table(
        ["File", "Marker"],
        [[m.get("file"), m.get("marker")] for m in (j.get("source_markers") or [])],
        empty="No LLM-client markers in the tree.",
    ))
    return shell("Jailbreak & prompt-injection assessment", "\n".join(body), client=_client(meta))


def cis_html(run_dir: Path, meta: dict) -> str:
    c = _load(run_dir, "cis_cloud.json")
    by_status = c.get("by_status") or {}
    body = [
        f"<p>{esc(c.get('benchmark'))}. {esc(c.get('note'))}</p>",
        _stats([(k, v) for k, v in by_status.items()] or [("Controls", len(c.get("controls") or []))]),
        _table(
            ["ID", "Domain", "Control", "Status", "Severity", "Evidence", "Remediation"],
            [
                [
                    row.get("id"),
                    row.get("domain"),
                    row.get("title"),
                    row.get("status"),
                    row.get("severity"),
                    row.get("evidence"),
                    row.get("remediation"),
                ]
                for row in (c.get("controls") or [])
            ],
        ),
    ]
    return shell("CIS cloud security controls", "\n".join(body), client=_client(meta))


def compliance_html(run_dir: Path, meta: dict, title: str, kind: str) -> str:
    pack = _load(run_dir, "compliance.json")
    body = [
        f"<p>Plan <code>{esc(pack.get('plan'))}</code> · questionnaires / year: {esc(pack.get('questionnaires_per_year'))} "
        f"· client <strong>{esc(meta.get('client_name'))}</strong>.</p>",
        "<h2>Frameworks</h2><ul>" + "".join(f"<li>{esc(f)}</li>" for f in (pack.get("frameworks") or [])) + "</ul>",
    ]
    if kind in ("policy-control-map.html", "full-security-report.html"):
        body.append("<h2>Policies</h2>")
        for p in pack.get("policies") or []:
            body.append(f"<h3>{esc(p.get('id'))} {esc(p.get('title'))} {_sev_badge(p.get('status'))}</h3>")
            body.append(f"<p>Owner {esc(p.get('owner'))} · review {esc(p.get('review_date'))}</p>")
            body.append(f"<p>{esc(p.get('body'))}</p>")
        body.append("<h2>Controls</h2>")
        body.append(_table(
            ["ID", "Framework", "Title", "Status", "Owner", "Tests", "Last tested"],
            [
                [
                    p.get("id"),
                    p.get("framework"),
                    p.get("title"),
                    p.get("status"),
                    p.get("owner"),
                    ", ".join(p.get("tests") or []),
                    p.get("last_tested"),
                ]
                for p in (pack.get("controls") or [])
            ],
        ))
        body.append("<h2>Evidence map</h2>")
        body.append(_table(
            ["ID", "Control", "Artifact", "Status"],
            [
                [p.get("id"), p.get("control"), p.get("artifact"), p.get("status")]
                for p in (pack.get("evidence") or [])
            ],
        ))
        body.append("<h2>Questionnaires</h2>")
        body.append(_table(
            ["ID", "Name", "Status"],
            [[q.get("id"), q.get("name"), q.get("status")] for q in (pack.get("questionnaires") or [])],
        ))
    if kind == "access-management.html":
        access = _load(run_dir, "access_management.json")
        body.append(f"<p>{esc(access.get('narrative'))}</p>")
        body.append(_stats([
            ("Identities", access.get("identity_count") or 0),
            ("Privileged", access.get("privileged_count") or 0),
            ("MFA", access.get("mfa_coverage") or "—"),
            ("Directory", access.get("directory") or "—"),
        ]))
        body.append("<h2>Identity inventory</h2>")
        body.append(_table(
            ["ID", "Principal", "Type", "Roles", "MFA", "Privileged", "Status", "Source"],
            [
                [
                    i.get("id"),
                    i.get("principal"),
                    i.get("type"),
                    ", ".join(i.get("roles") or []),
                    i.get("mfa"),
                    "yes" if i.get("privileged") else "no",
                    i.get("status"),
                    i.get("source"),
                ]
                for i in (access.get("identities") or [])
            ],
        ))
        body.append("<h2>Directory connectors</h2>")
        body.append(_table(
            ["Name", "Status", "Note"],
            [[c.get("name"), c.get("status"), c.get("note")] for c in (access.get("connectors") or [])],
        ))
        body.append("<h2>Access reviews</h2>")
        body.append(_table(
            ["ID", "Scope", "Cadence", "Due", "Owner", "Status"],
            [
                [r.get("id"), r.get("scope"), r.get("cadence"), r.get("due"), r.get("owner"), r.get("status")]
                for r in (access.get("reviews") or [])
            ],
        ))
        body.append("<h2>Joiner / mover / leaver</h2>")
        body.append(_table(
            ["Stage", "Control", "Status"],
            [[j.get("stage"), j.get("control"), j.get("status")] for j in (access.get("joiner_mover_leaver") or [])],
        ))
        bg = access.get("break_glass") or {}
        body.append("<h2>Break-glass</h2>")
        body.append(f"<p>Defined: {esc(bg.get('defined'))}. {esc(bg.get('note'))}</p>")
        if access.get("priority_actions"):
            body.append("<h2>Priority actions</h2><ul>" + "".join(
                f"<li>{esc(a)}</li>" for a in access["priority_actions"]
            ) + "</ul>")
        body.append("<h2>SOC 2 CC6 mapping</h2>")
        body.append(_table(
            ["ID", "Title", "Status"],
            [[c.get("id"), c.get("title"), c.get("status")] for c in (access.get("soc2_cc6") or [])],
        ))
    if kind == "risk-register.html":
        risks = _load(run_dir, "risk_register.json")
        body.append(f"<p>{esc(risks.get('methodology'))}</p>")
        by = risks.get("by_severity") or {}
        body.append(_stats([(k.title(), by.get(k, 0)) for k in ("CRITICAL", "HIGH", "MEDIUM", "LOW")]))
        body.append(_table(
            ["ID", "Risk", "Category", "Severity", "L", "I", "Inherent", "Residual", "Treatment", "Owner", "Due", "Linked"],
            [
                [
                    it.get("id"),
                    it.get("title"),
                    it.get("category"),
                    it.get("severity"),
                    it.get("likelihood"),
                    it.get("impact"),
                    it.get("inherent"),
                    it.get("residual"),
                    it.get("treatment"),
                    it.get("owner"),
                    it.get("due"),
                    it.get("linked"),
                ]
                for it in (risks.get("items") or [])
            ],
        ))
    if kind == "issue-management.html":
        board = _load(run_dir, "issues.json")
        body.append(f"<p>{esc(board.get('narrative'))}</p>")
        body.append(_stats([
            ("Open", board.get("open_count") or 0),
            ("In progress", (board.get("by_status") or {}).get("in-progress", 0)),
            ("Done", (board.get("by_status") or {}).get("done", 0)),
        ]))
        body.append(_table(
            ["ID", "Title", "Source", "Ref", "Severity", "Priority", "Status", "Owner", "SLA", "Opened", "Due"],
            [
                [
                    it.get("id"),
                    it.get("title"),
                    it.get("source"),
                    it.get("ref"),
                    it.get("severity"),
                    it.get("priority"),
                    it.get("status"),
                    it.get("owner"),
                    it.get("sla_days"),
                    it.get("opened"),
                    it.get("due"),
                ]
                for it in (board.get("issues") or [])
            ],
        ))
    if kind == "owasp-asvs.html":
        asvs = _load(run_dir, "asvs_coverage.json")
        body.append(f"<p>{esc(asvs.get('standard'))}</p>")
        by = asvs.get("by_status") or {}
        body.append(_stats([(k, v) for k, v in by.items()]))
        body.append(_table(
            ["Chapter", "Title", "Status", "Tests", "Mapped findings"],
            [
                [
                    ch.get("id"),
                    ch.get("title"),
                    ch.get("status"),
                    ", ".join(ch.get("tests") or []),
                    ", ".join(ch.get("mapped") or []) or "—",
                ]
                for ch in (asvs.get("chapters") or [])
            ],
        ))
        body.append("<h2>WSTG chapters exercised</h2>")
        for k, vs in (asvs.get("test_cases") or {}).items():
            body.append(f"<p><strong>{esc(k.replace('_',' '))}</strong><br>{esc(', '.join(vs))}</p>")
    if kind not in (
        "access-management.html",
        "policy-control-map.html",
        "risk-register.html",
        "issue-management.html",
        "owasp-asvs.html",
        "full-security-report.html",
    ):
        body.append("<h2>Features in this tier</h2><ul>" + "".join(
            f"<li>{esc(f)}</li>" for f in (pack.get("features") or [])
        ) + "</ul>")
    return shell(title, "\n".join(body), client=_client(meta))


def full_html(run_dir: Path, meta: dict, files: list[str]) -> str:
    rows = "".join(f"<tr><td><a href='{esc(f)}'>{esc(f)}</a></td></tr>" for f in files if f != "full-security-report.html")
    iframes = "".join(
        f"<details><summary>{esc(f)}</summary><iframe src='{esc(f)}' style='width:100%;height:640px;border:1px solid {RULE}'></iframe></details>"
        for f in files if f != "full-security-report.html"
    )
    body = f"<h2>Report index</h2><table>{rows}</table>{iframes}"
    return shell("Full security report", body, client=_client(meta))


def grounding_html(run_dir: Path, meta: dict) -> str:
    pack = _load(run_dir, "grounding.json")
    client = meta.get("client_name") or pack.get("client") or "Client"
    facts = pack.get("facts") or []
    inv = pack.get("inventory") or {}
    if not pack:
        body = (
            "<p class='callout'>LLM grounding was not enabled for this run. "
            "On Ultra-Professional, tick <strong>LLM grounding</strong> at launch "
            "to scrape this assessment's source tree and (when present) GitHub "
            "metadata.</p>"
        )
        return shell("LLM grounding pack", body, client=_client(meta))
    rows = [
        [f.get("id"), f.get("kind"), f.get("path"), (f.get("text") or "")[:280]]
        for f in facts
    ]
    gh = pack.get("github_meta") or {}
    gh_block = ""
    if gh.get("full_name"):
        gh_block = (
            f"<h2>GitHub metadata</h2><p>{esc(gh.get('full_name'))} — "
            f"{esc(gh.get('description'))} ({esc(gh.get('language'))})</p>"
        )
    elif gh.get("error"):
        gh_block = f"<p class='hint'>GitHub metadata skipped: {esc(gh.get('error'))}</p>"
    body = f"""
<p>Facts scraped for <strong>{esc(client)}</strong> from <code>{esc(pack.get('source_path'))}</code>
at run time. LLM narrative on this tier must cite <code>G-00n</code> ids or say unknown.</p>
<p class="callout">{esc(pack.get('contract'))}</p>
<div class="statrow">
  <div class="stat"><b>{inv.get('files') or 0}</b><span>Files inventoried</span></div>
  <div class="stat"><b>{len(facts)}</b><span>Grounding facts</span></div>
</div>
{gh_block}
<h2>Facts</h2>
{_table(["ID", "Kind", "Path", "Excerpt"], rows)}
"""
    return shell("LLM grounding pack", body, client=_client(meta))


GENERATORS = {
    "pentest-assessment.html": pentest_html,
    "trivy-scan.html": trivy_html,
    "executive-summary.html": exec_html,
    "jailbreak-assessment.html": jail_html,
    "cis-cloud.html": cis_html,
    "access-management.html": lambda d, m: compliance_html(d, m, "Access management", "access-management.html"),
    "policy-control-map.html": lambda d, m: compliance_html(d, m, "Policy and control map", "policy-control-map.html"),
    "risk-register.html": lambda d, m: compliance_html(d, m, "Risk register", "risk-register.html"),
    "owasp-asvs.html": lambda d, m: compliance_html(d, m, "OWASP ASVS / WSTG coverage", "owasp-asvs.html"),
    "issue-management.html": lambda d, m: compliance_html(d, m, "Agentic issue management", "issue-management.html"),
    "llm-grounding.html": grounding_html,
}


def write_all_reports(orch) -> list[str]:
    run_dir: Path = orch.run_dir
    reports_dir = run_dir / "reports"
    reports_dir.mkdir(exist_ok=True)
    meta = {
        "client_name": (orch.client_name or "").strip() or "Client",
        "plan": orch.plan,
        "run_id": orch.run_id,
    }
    wanted = list(reports_for(orch.plan))
    written = []
    for name in wanted:
        if name == "full-security-report.html":
            continue
        gen = GENERATORS.get(name)
        if not gen:
            continue
        (reports_dir / name).write_text(gen(run_dir, meta), encoding="utf-8")
        written.append(name)
    if "full-security-report.html" in wanted:
        (reports_dir / "full-security-report.html").write_text(
            full_html(run_dir, meta, written + ["full-security-report.html"]),
            encoding="utf-8",
        )
        written.append("full-security-report.html")
    return written


class _ReportOrch:
    def __init__(self, run_dir: Path, meta: dict):
        self.run_dir = run_dir
        self.client_name = (meta.get("client_name") or "").strip() or "Client"
        self.plan = meta.get("plan") or "essentials"
        self.run_id = meta.get("run_id") or run_dir.name


def backfill_run_reports(run_dir: Path, meta: dict | None = None) -> list[str]:
    """Fill GRC JSON that older runs lacked, then rewrite HTML. Safe to call twice."""
    from agentic_security import inventories

    run_dir = Path(run_dir)
    meta = meta or _load(run_dir, "run_meta.json")
    appsec = _load(run_dir, "appsec_findings.json")
    for i, f in enumerate(appsec.get("findings") or [], 1):
        f.setdefault("id", f"AS-{i:03d}")
        f.setdefault("wstg", f.get("ref"))
        f.setdefault("evidence", [])
        f.setdefault("steps_to_reproduce", [])
    if appsec:
        (run_dir / "appsec_findings.json").write_text(json.dumps(appsec, indent=2), encoding="utf-8")
    trivy = _load(run_dir, "trivy_report.json")
    jail = _load(run_dir, "jailbreak_assessment.json")
    cis = _load(run_dir, "cis_cloud.json")
    pack = _load(run_dir, "compliance.json")
    plan = _load(run_dir, "remediation_plan.json")
    source = meta.get("source_path") or ""
    if cis:
        cis = inventories.annotate_cis(cis, source)
        (run_dir / "cis_cloud.json").write_text(json.dumps(cis, indent=2), encoding="utf-8")
    if pack:
        pack = inventories.enrich_compliance(pack, appsec, trivy, jail)
        (run_dir / "compliance.json").write_text(json.dumps(pack, indent=2), encoding="utf-8")
        access = inventories.access_inventory(source, pack, appsec)
        (run_dir / "access_management.json").write_text(json.dumps(access, indent=2), encoding="utf-8")
        risks = inventories.risk_register(pack, appsec, trivy, jail)
        (run_dir / "risk_register.json").write_text(json.dumps(risks, indent=2), encoding="utf-8")
        asvs = inventories.asvs_matrix(appsec)
        (run_dir / "asvs_coverage.json").write_text(json.dumps(asvs, indent=2), encoding="utf-8")
    if plan:
        issues = inventories.issue_board(plan)
        (run_dir / "issues.json").write_text(json.dumps(issues, indent=2), encoding="utf-8")
    return write_all_reports(_ReportOrch(run_dir, meta))
