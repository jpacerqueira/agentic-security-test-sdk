from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any
import asyncio
import json


class PipelinePhase(str, Enum):
    SCOPE = "scope"
    GATE_1 = "gate_1"
    VULN_SCAN = "vuln_scan"
    GATE_2 = "gate_2"
    APPSEC = "appsec"
    GATE_3 = "gate_3"
    JAILBREAK = "jailbreak"
    GATE_4 = "gate_4"
    CIS_CLOUD = "cis_cloud"
    GATE_4_5 = "gate_4_5"
    COMPLIANCE = "compliance"
    GATE_5 = "gate_5"
    WRITER = "writer"
    DONE = "done"


PHASE_LABELS = {
    PipelinePhase.SCOPE: "Scope",
    PipelinePhase.GATE_1: "Gate 1",
    PipelinePhase.VULN_SCAN: "Trivy / vuln",
    PipelinePhase.GATE_2: "Gate 2",
    PipelinePhase.APPSEC: "AppSec",
    PipelinePhase.GATE_3: "Gate 3",
    PipelinePhase.JAILBREAK: "Jailbreak",
    PipelinePhase.GATE_4: "Gate 4",
    PipelinePhase.CIS_CLOUD: "CIS / cloud",
    PipelinePhase.GATE_4_5: "Planning",
    PipelinePhase.COMPLIANCE: "Trust / GRC",
    PipelinePhase.GATE_5: "Gate 5",
    PipelinePhase.WRITER: "Reports",
    PipelinePhase.DONE: "Done",
}

GATES = (
    {"id": "gate_1", "title": "Scope of engagement", "phase": "gate_1"},
    {"id": "gate_2", "title": "Vulnerability scan findings", "phase": "gate_2"},
    {"id": "gate_3", "title": "Application & API findings", "phase": "gate_3"},
    {"id": "gate_4", "title": "Jailbreak & LLM-risk findings", "phase": "gate_4"},
    {"id": "gate_4_5", "title": "Remediation plan", "phase": "gate_4_5"},
    {"id": "gate_5", "title": "Report release", "phase": "gate_5"},
)


@dataclass
class PipelineEvent:
    kind: str
    phase: PipelinePhase
    payload: dict[str, Any] = field(default_factory=dict)


class SecurityOrchestrator:
    def __init__(
        self,
        run_id: str,
        run_dir: Path,
        plan: str = "essentials",
        skip_llm: bool = True,
        auto_approve_gates: bool = False,
        reviewer_name: str = "",
        client_name: str = "Client",
        target_url: str = "",
        source_path: str = "",
    ) -> None:
        self.run_id = run_id
        self.run_dir = Path(run_dir)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.plan = plan
        self.skip_llm = skip_llm
        self.auto_approve_gates = auto_approve_gates
        self.reviewer_name = reviewer_name
        self.client_name = client_name
        self.target_url = target_url
        self.source_path = source_path
        self.current_phase = PipelinePhase.SCOPE
        self.artifacts: dict[str, Any] = {}
        self._gate_events: dict[str, asyncio.Event] = {g["id"]: asyncio.Event() for g in GATES}
        self._gate_decisions: dict[str, str] = {}
        self.stop_requested = False

    def write_json(self, name: str, data: Any) -> Path:
        path = self.run_dir / name
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        self.artifacts[name] = name
        return path

    def approve_gate(self, gate_id: str, reviewer_name: str = "", notes: str = "") -> None:
        self._gate_decisions[gate_id] = "approved"
        self.write_json(
            f"{gate_id}_decision.json",
            {"decision": "approved", "reviewer_name": reviewer_name, "notes": notes},
        )
        ev = self._gate_events.get(gate_id)
        if ev:
            ev.set()

    def reject_gate(self, gate_id: str, reviewer_name: str = "", notes: str = "") -> None:
        self._gate_decisions[gate_id] = "rejected"
        self.write_json(
            f"{gate_id}_decision.json",
            {"decision": "rejected", "reviewer_name": reviewer_name, "notes": notes},
        )
        ev = self._gate_events.get(gate_id)
        if ev:
            ev.set()

    async def wait_gate(self, gate_id: str) -> str:
        if self.auto_approve_gates:
            self.approve_gate(
                gate_id,
                reviewer_name=self.reviewer_name or "auto",
                notes="auto-approved to next gate",
            )
        await self._gate_events[gate_id].wait()
        self._gate_events[gate_id].clear()
        return self._gate_decisions.get(gate_id, "approved")
