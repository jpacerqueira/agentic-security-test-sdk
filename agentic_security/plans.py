"""Vanta-shaped plan entitlements: Essentials, Plus, Professional, Ultra-Professional.

Enterprise is out of the launch surface (fully custom). The first three public
tiers match https://www.vanta.com/lp/demo "Find your plan". Ultra-Professional
is this product's extra: optional per-run LLM grounding on top of Professional.
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

ULTRA_PROFESSIONAL = Plan(
    id="ultra-professional",
    name="Ultra-Professional",
    tagline="Professional plus optional LLM grounding — facts scraped for this run, not invented.",
    audience="Teams who need LLM narrative tied to this assessment's evidence pack.",
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
        "llm-grounding.html",
        "full-security-report.html",
    ),
    features=(
        "Everything in Professional",
        "Optional per-run LLM grounding (launch checkbox)",
        "Runtime scrape of this source tree, tailored to the assessment",
        "GitHub metadata when the tree was fetched from a repo URL",
        "LLM text must cite grounding fact ids or say unknown",
        "llm-grounding.html evidence report",
    ),
    includes=("essentials", "plus", "professional"),
)

PLANS: dict[str, Plan] = {
    ESSENTIALS.id: ESSENTIALS,
    PLUS.id: PLUS,
    PROFESSIONAL.id: PROFESSIONAL,
    ULTRA_PROFESSIONAL.id: ULTRA_PROFESSIONAL,
}

PLAN_ORDER = (ESSENTIALS, PLUS, PROFESSIONAL, ULTRA_PROFESSIONAL)
GROUNDING_PLAN_ID = ULTRA_PROFESSIONAL.id


def resolve_plan(plan_id: str) -> Plan:
    return PLANS.get((plan_id or "").lower(), ESSENTIALS)


def reports_for(plan_id: str) -> tuple[str, ...]:
    return resolve_plan(plan_id).reports


def grounding_entitled(plan_id: str) -> bool:
    """LLM grounding is an Ultra-Professional extra — not available on lower tiers."""
    return resolve_plan(plan_id).id == GROUNDING_PLAN_ID


def reports_for_pdf(plan_id: str) -> tuple[str, ...]:
    """HTML reports to bind into the A4 output PDF.

    Executive summary is always first. The full-pack HTML (iframes of the
    other files) is omitted so the PDF contains each report once, in full.
    """
    lead = "executive-summary.html"
    skip = {"full-security-report.html"}
    files = [f for f in reports_for(plan_id) if f not in skip]
    if lead in files:
        files = [lead] + [f for f in files if f != lead]
    return tuple(files)
