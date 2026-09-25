"""LangGraph assessment pipeline. Same phases and gates as the ADK showcase.

Human gates stay on ``SecurityOrchestrator.wait_gate`` so the web UI approve/reject
endpoints are unchanged. The graph is the control flow: each phase is a node, and a
rejected gate routes to ``stopped`` instead of the next phase.
"""

from __future__ import annotations

import asyncio
from typing import Any

from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

from agentic_security import grounding, inventories, llm, llm_enrich, scanners
from agentic_security.orchestration.pipeline import (
    KEY_TO_GATE,
    PipelineEvent,
    PipelinePhase,
    SecurityOrchestrator,
)
from agentic_security.reports.html import write_all_reports


class AssessmentState(TypedDict, total=False):
    rejected: str
    appsec: dict[str, Any]
    trivy: dict[str, Any]
    jail: dict[str, Any]
    cis: dict[str, Any]
    plan: dict[str, Any]


def _artifact(phase: PipelinePhase, key: str) -> PipelineEvent:
    return PipelineEvent(
        kind="artifact",
        phase=phase,
        payload={"key": key, "gate_id": KEY_TO_GATE.get(key, "")},
    )


def build_assessment_graph(orch: SecurityOrchestrator, events: asyncio.Queue):
    """Compile the assessment graph. Nodes push ``PipelineEvent`` onto ``events``."""

    async def emit(event: PipelineEvent) -> None:
        await events.put(event)

    async def phase(p: PipelinePhase) -> None:
        orch.current_phase = p
        await emit(PipelineEvent(kind="phase_started", phase=p))

    async def open_gate(gate_id: str, p: PipelinePhase) -> dict[str, Any]:
        orch.current_phase = p
        await emit(PipelineEvent(kind="gate_opened", phase=p, payload={"gate_id": gate_id}))
        decision = await orch.wait_gate(gate_id)
        await emit(
            PipelineEvent(
                kind="gate_resolved",
                phase=p,
                payload={
                    "gate_id": gate_id,
                    "decision": decision,
                    "reviewer_name": orch.reviewer_name,
                },
            )
        )
        if decision == "rejected":
            return {"rejected": gate_id}
        return {}

    async def prepare(state: AssessmentState) -> AssessmentState:
        if orch.skip_llm:
            return {}
        await emit(
            PipelineEvent(
                kind="llm_wait",
                phase=PipelinePhase.SCOPE,
                payload={
                    "engine": "gateway",
                    "via": "langgraph+langchain_openai.ChatOpenAI",
                },
            )
        )
        ready, msg = (False, "langgraph stack missing")
        if llm.llm_stack_available():
            ready, msg = await llm.ensure_llm_ready()
        await emit(
            PipelineEvent(
                kind="llm_ready",
                phase=PipelinePhase.SCOPE,
                payload={"ready": ready, "message": msg, "langgraph": llm.llm_stack_available()},
            )
        )
        return {}

    async def scope(state: AssessmentState) -> AssessmentState:
        await phase(PipelinePhase.SCOPE)
        found = scanners.discover_scope(orch.source_path, orch.target_url, orch.client_name)
        if orch.llm_grounding:
            pack = await asyncio.to_thread(
                grounding.collect_grounding_for_run,
                orch.source_path,
                orch.target_url,
                orch.client_name,
            )
            orch.grounding_pack = pack
            orch.write_json("grounding.json", pack)
            await emit(_artifact(PipelinePhase.SCOPE, "grounding.json"))
        found = await llm_enrich.maybe_enrich(orch, "scope", found)
        orch.write_json("scope.json", found)
        await emit(_artifact(PipelinePhase.SCOPE, "scope.json"))
        return {}

    async def gate_1(state: AssessmentState) -> AssessmentState:
        return await open_gate("gate_1", PipelinePhase.GATE_1)

    async def vuln_scan(state: AssessmentState) -> AssessmentState:
        await phase(PipelinePhase.VULN_SCAN)
        trivy = scanners.run_trivy(orch.source_path)
        orch.write_json("trivy_report.json", trivy)
        await emit(_artifact(PipelinePhase.VULN_SCAN, "trivy_report.json"))
        return {"trivy": trivy}

    async def gate_2(state: AssessmentState) -> AssessmentState:
        return await open_gate("gate_2", PipelinePhase.GATE_2)

    async def appsec(state: AssessmentState) -> AssessmentState:
        await phase(PipelinePhase.APPSEC)
        findings = scanners.appsec_findings(orch.source_path, orch.target_url)
        findings = await llm_enrich.maybe_enrich(orch, "appsec", findings)
        orch.write_json("appsec_findings.json", findings)
        await emit(_artifact(PipelinePhase.APPSEC, "appsec_findings.json"))
        return {"appsec": findings}

    async def gate_3(state: AssessmentState) -> AssessmentState:
        return await open_gate("gate_3", PipelinePhase.GATE_3)

    async def jailbreak(state: AssessmentState) -> AssessmentState:
        await phase(PipelinePhase.JAILBREAK)
        jail = scanners.jailbreak_assessment(orch.source_path)
        jail = await llm_enrich.maybe_enrich(orch, "jailbreak", jail)
        orch.write_json("jailbreak_assessment.json", jail)
        await emit(_artifact(PipelinePhase.JAILBREAK, "jailbreak_assessment.json"))
        return {"jail": jail}

    async def gate_4(state: AssessmentState) -> AssessmentState:
        return await open_gate("gate_4", PipelinePhase.GATE_4)

    async def cis_cloud(state: AssessmentState) -> AssessmentState:
        await phase(PipelinePhase.CIS_CLOUD)
        cis = inventories.annotate_cis(scanners.cis_cloud_controls(), orch.source_path)
        orch.write_json("cis_cloud.json", cis)
        await emit(_artifact(PipelinePhase.CIS_CLOUD, "cis_cloud.json"))
        appsec_doc = state.get("appsec") or {}
        trivy = state.get("trivy") or {}
        jail = state.get("jail") or {}
        plan = scanners.remediation_plan(appsec_doc, trivy, cis, jail)
        plan = await llm_enrich.maybe_enrich(orch, "plan", plan)
        orch.write_json("remediation_plan.json", plan)
        await emit(_artifact(PipelinePhase.GATE_5, "remediation_plan.json"))
        return {"cis": cis, "plan": plan}

    async def gate_5(state: AssessmentState) -> AssessmentState:
        return await open_gate("gate_5", PipelinePhase.GATE_5)

    async def compliance(state: AssessmentState) -> AssessmentState:
        await phase(PipelinePhase.COMPLIANCE)
        appsec_doc = state.get("appsec") or {}
        trivy = state.get("trivy") or {}
        jail = state.get("jail") or {}
        plan = state.get("plan") or {}
        pack = inventories.enrich_compliance(
            scanners.compliance_pack(orch.plan), appsec_doc, trivy, jail
        )
        orch.write_json("compliance.json", pack)
        access = inventories.access_inventory(orch.source_path, pack, appsec_doc)
        access = await llm_enrich.maybe_enrich(orch, "access", access)
        orch.write_json("access_management.json", access)
        risks = inventories.risk_register(pack, appsec_doc, trivy, jail)
        orch.write_json("risk_register.json", risks)
        issues = inventories.issue_board(plan)
        orch.write_json("issues.json", issues)
        asvs = inventories.asvs_matrix(appsec_doc)
        orch.write_json("asvs_coverage.json", asvs)
        await emit(_artifact(PipelinePhase.COMPLIANCE, "compliance.json"))
        await emit(_artifact(PipelinePhase.COMPLIANCE, "access_management.json"))
        await emit(_artifact(PipelinePhase.COMPLIANCE, "risk_register.json"))
        await emit(_artifact(PipelinePhase.COMPLIANCE, "issues.json"))
        await emit(_artifact(PipelinePhase.COMPLIANCE, "asvs_coverage.json"))
        return {}

    async def gate_6(state: AssessmentState) -> AssessmentState:
        return await open_gate("gate_6", PipelinePhase.GATE_6)

    async def writer(state: AssessmentState) -> AssessmentState:
        await phase(PipelinePhase.WRITER)
        written = write_all_reports(orch)
        orch.write_json("reports_index.json", {"files": written})
        await emit(_artifact(PipelinePhase.WRITER, "reports_index.json"))
        for name in written:
            await emit(_artifact(PipelinePhase.WRITER, name))
        orch.current_phase = PipelinePhase.DONE
        await emit(
            PipelineEvent(
                kind="pipeline_completed",
                phase=PipelinePhase.DONE,
                payload={"artifacts": list(orch.artifacts.keys()), "reports": written},
            )
        )
        return {}

    async def stopped(state: AssessmentState) -> AssessmentState:
        await emit(
            PipelineEvent(
                kind="pipeline_stopped",
                phase=orch.current_phase,
                payload={"reason": "rejected", "gate_id": state.get("rejected", "")},
            )
        )
        return {}

    def _route(nxt: str):
        def choose(state: AssessmentState) -> str:
            return "stopped" if state.get("rejected") else nxt

        return choose

    graph = StateGraph(AssessmentState)
    for name, node in (
        ("prepare", prepare),
        ("scope", scope),
        ("gate_1", gate_1),
        ("vuln_scan", vuln_scan),
        ("gate_2", gate_2),
        ("appsec", appsec),
        ("gate_3", gate_3),
        ("jailbreak", jailbreak),
        ("gate_4", gate_4),
        ("cis_cloud", cis_cloud),
        ("gate_5", gate_5),
        ("compliance", compliance),
        ("gate_6", gate_6),
        ("writer", writer),
        ("stopped", stopped),
    ):
        graph.add_node(name, node)

    graph.add_edge(START, "prepare")
    graph.add_edge("prepare", "scope")
    graph.add_edge("scope", "gate_1")
    graph.add_conditional_edges("gate_1", _route("vuln_scan"), ["vuln_scan", "stopped"])
    graph.add_edge("vuln_scan", "gate_2")
    graph.add_conditional_edges("gate_2", _route("appsec"), ["appsec", "stopped"])
    graph.add_edge("appsec", "gate_3")
    graph.add_conditional_edges("gate_3", _route("jailbreak"), ["jailbreak", "stopped"])
    graph.add_edge("jailbreak", "gate_4")
    graph.add_conditional_edges("gate_4", _route("cis_cloud"), ["cis_cloud", "stopped"])
    graph.add_edge("cis_cloud", "gate_5")
    graph.add_conditional_edges("gate_5", _route("compliance"), ["compliance", "stopped"])
    graph.add_edge("compliance", "gate_6")
    graph.add_conditional_edges("gate_6", _route("writer"), ["writer", "stopped"])
    graph.add_edge("writer", END)
    graph.add_edge("stopped", END)
    return graph.compile()


GRAPH_NODES = (
    "prepare",
    "scope",
    "gate_1",
    "vuln_scan",
    "gate_2",
    "appsec",
    "gate_3",
    "jailbreak",
    "gate_4",
    "cis_cloud",
    "gate_5",
    "compliance",
    "gate_6",
    "writer",
    "stopped",
)
