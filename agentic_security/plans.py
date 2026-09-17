"""Vanta-shaped plan entitlements: Essentials, Plus, Professional.

Enterprise is out of the launch surface (fully custom) — the three public
tiers match https://www.vanta.com/lp/demo "Find your plan".
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Plan:
    id: str
    name: str
    tagline: str
    audience: str
    questionnaires_per_year: int
    frameworks: int | str
    reports: tuple[str, ...]
    features: tuple[str, ...]
    includes: tuple[str, ...] = field(default_factory=tuple)


ESSENTIALS = Plan(
    id="essentials",
    name="Essentials",
    tagline="The fastest, simplest path to compliance — stay focused on building.",
    audience="Companies who want to stay focused on building.",
    questionnaires_per_year=0,
    frameworks=1,
    reports=(
        "pentest-assessment.html",
        "trivy-scan.html",
        "executive-summary.html",
    ),
    features=(
        "One compliance framework with agentic policy generator",
        "AI agent: search and ask across policies, controls, frameworks, tests, documents",
        "Evidence checks and policy template library",
        "Automated evidence collection for audit readiness",
        "Basic reporting and audit workflows",
        "Code-change and continuous controls monitoring",
        "Auditor API",
        "Trust Center",
        "Access to expert partners for additional compliance services",
    ),
    includes=(),
)

PLUS = Plan(
    id="plus",
    name="Plus",
    tagline="A strong compliance foundation plus security — build trust early.",
    audience="Companies who want to build trust and credibility early.",
    questionnaires_per_year=25,
    frameworks="expanded",
    reports=(
        "pentest-assessment.html",
        "trivy-scan.html",
        "executive-summary.html",
        "jailbreak-assessment.html",
        "access-management.html",
        "policy-control-map.html",
    ),
    features=(
        "Automated policy onboarding",
        "Control mapping to policies",
        "Policy change summaries",
        "SLA tracking and remediation",
        "AI-powered questionnaire automation (25 / year)",
        "Access management (reviews and requests)",
    ),
    includes=("essentials",),
)

PROFESSIONAL = Plan(
    id="professional",
    name="Professional",
    tagline="Compliance, risk, and reporting in one package — scale the trust program.",
    audience="Organizations who want to scale their trust program with ease.",
    questionnaires_per_year=144,
    frameworks="all",
    reports=(
        "pentest-assessment.html",
        "trivy-scan.html",
        "executive-summary.html",
        "jailbreak-assessment.html",
        "access-management.html",
        "policy-control-map.html",
        "risk-register.html",
        "cis-cloud.html",
        "owasp-asvs.html",
        "issue-management.html",
        "full-security-report.html",
    ),
    features=(
        "AI-powered questionnaire automation (144 / year)",
        "Risk management with customization, dashboard, and reporting",
        "Advanced Trust Center",
        "Custom monitoring tests and automation",
        "Automated access management",
        "Advanced reporting (six customizable reports)",
        "Advanced control management",
        "Agentic issue management",
    ),
    includes=("essentials", "plus"),
)

PLANS: dict[str, Plan] = {
    ESSENTIALS.id: ESSENTIALS,
    PLUS.id: PLUS,
    PROFESSIONAL.id: PROFESSIONAL,
}

PLAN_ORDER = (ESSENTIALS, PLUS, PROFESSIONAL)


def resolve_plan(plan_id: str) -> Plan:
    return PLANS.get((plan_id or "").lower(), ESSENTIALS)


def reports_for(plan_id: str) -> tuple[str, ...]:
    return resolve_plan(plan_id).reports
