from __future__ import annotations

import asyncio

from agentic_security.orchestration.pipeline import (
    PipelineEvent,
    PipelinePhase,
    SecurityOrchestrator,
)
from agentic_security import grounding, inventories, llm, llm_enrich, scanners
from agentic_security.reports.html import write_all_reports


async def run_full_pipeline(orch: SecurityOrchestrator):
    async def phase(p: PipelinePhase):
        orch.current_phase = p
        yield PipelineEvent(kind="phase_started", phase=p)

    async def gate(gate_id: str, phase: PipelinePhase):
        orch.current_phase = phase
        yield PipelineEvent(kind="gate_opened", phase=phase, payload={"gate_id": gate_id})
        decision = await orch.wait_gate(gate_id)
        yield PipelineEvent(
            kind="gate_resolved",
            phase=phase,
            payload={"gate_id": gate_id, "decision": decision, "reviewer_name": orch.reviewer_name},
        )
        if decision == "rejected":
            raise _GateRejected(gate_id)

    try:
        if not orch.skip_llm:
            yield PipelineEvent(
                kind="llm_wait",
                phase=PipelinePhase.SCOPE,
                payload={"engine": "ollama", "via": "google.adk.models.lite_llm.LiteLlm"},
            )
            ready, msg = (False, "adk missing")
            if llm.adk_available():
                ready, msg = await llm.ensure_llm_ready()
            yield PipelineEvent(
                kind="llm_ready",
                phase=PipelinePhase.SCOPE,
                payload={"ready": ready, "message": msg, "adk": llm.adk_available()},
            )

        async for ev in phase(PipelinePhase.SCOPE):
            yield ev
        scope = scanners.discover_scope(orch.source_path, orch.target_url, orch.client_name)
        if orch.llm_grounding:
            pack = await asyncio.to_thread(
                grounding.collect_grounding_for_run,
                orch.source_path,
                orch.target_url,
                orch.client_name,
            )
            orch.grounding_pack = pack
            orch.write_json("grounding.json", pack)
            yield PipelineEvent(
                kind="artifact", phase=PipelinePhase.SCOPE, payload={"key": "grounding.json"}
            )
        scope = await llm_enrich.maybe_enrich(orch, "scope", scope)
        orch.write_json("scope.json", scope)
        yield PipelineEvent(kind="artifact", phase=PipelinePhase.SCOPE, payload={"key": "scope.json"})

        async for ev in gate("gate_1", PipelinePhase.GATE_1):
            yield ev

        async for ev in phase(PipelinePhase.VULN_SCAN):
            yield ev
        trivy = scanners.run_trivy(orch.source_path)
        orch.write_json("trivy_report.json", trivy)
        yield PipelineEvent(kind="artifact", phase=PipelinePhase.VULN_SCAN, payload={"key": "trivy_report.json"})

        async for ev in gate("gate_2", PipelinePhase.GATE_2):
            yield ev

        async for ev in phase(PipelinePhase.APPSEC):
            yield ev
        appsec = scanners.appsec_findings(orch.source_path, orch.target_url)
        appsec = await llm_enrich.maybe_enrich(orch, "appsec", appsec)
        orch.write_json("appsec_findings.json", appsec)
        yield PipelineEvent(kind="artifact", phase=PipelinePhase.APPSEC, payload={"key": "appsec_findings.json"})

        async for ev in gate("gate_3", PipelinePhase.GATE_3):
            yield ev

        async for ev in phase(PipelinePhase.JAILBREAK):
            yield ev
        jail = scanners.jailbreak_assessment(orch.source_path)
        jail = await llm_enrich.maybe_enrich(orch, "jailbreak", jail)
        orch.write_json("jailbreak_assessment.json", jail)
        yield PipelineEvent(kind="artifact", phase=PipelinePhase.JAILBREAK, payload={"key": "jailbreak_assessment.json"})

        async for ev in gate("gate_4", PipelinePhase.GATE_4):
            yield ev

        async for ev in phase(PipelinePhase.CIS_CLOUD):
            yield ev
        cis = inventories.annotate_cis(scanners.cis_cloud_controls(), orch.source_path)
        orch.write_json("cis_cloud.json", cis)
        yield PipelineEvent(kind="artifact", phase=PipelinePhase.CIS_CLOUD, payload={"key": "cis_cloud.json"})

        plan = scanners.remediation_plan(appsec, trivy, cis, jail)
        plan = await llm_enrich.maybe_enrich(orch, "plan", plan)
        orch.write_json("remediation_plan.json", plan)

        async for ev in gate("gate_5", PipelinePhase.GATE_5):
            yield ev

        async for ev in phase(PipelinePhase.COMPLIANCE):
            yield ev
        pack = inventories.enrich_compliance(scanners.compliance_pack(orch.plan), appsec, trivy, jail)
        orch.write_json("compliance.json", pack)
        access = inventories.access_inventory(orch.source_path, pack, appsec)
        access = await llm_enrich.maybe_enrich(orch, "access", access)
        orch.write_json("access_management.json", access)
        risks = inventories.risk_register(pack, appsec, trivy, jail)
        orch.write_json("risk_register.json", risks)
        issues = inventories.issue_board(plan)
        orch.write_json("issues.json", issues)
        asvs = inventories.asvs_matrix(appsec)
        orch.write_json("asvs_coverage.json", asvs)
        yield PipelineEvent(kind="artifact", phase=PipelinePhase.COMPLIANCE, payload={"key": "compliance.json"})

        async for ev in gate("gate_6", PipelinePhase.GATE_6):
            yield ev

        async for ev in phase(PipelinePhase.WRITER):
            yield ev
        written = write_all_reports(orch)
        orch.write_json("reports_index.json", {"files": written})

        orch.current_phase = PipelinePhase.DONE
        yield PipelineEvent(
            kind="pipeline_completed",
            phase=PipelinePhase.DONE,
            payload={"artifacts": list(orch.artifacts.keys()), "reports": written},
        )
    except _GateRejected as rej:
        yield PipelineEvent(
            kind="pipeline_stopped",
            phase=orch.current_phase,
            payload={"reason": "rejected", "gate_id": rej.gate_id},
        )


class _GateRejected(Exception):
    def __init__(self, gate_id: str):
        self.gate_id = gate_id
