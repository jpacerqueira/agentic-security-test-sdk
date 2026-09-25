from pathlib import Path

from agentic_security.orchestration.graph import GRAPH_NODES, build_assessment_graph
from agentic_security.orchestration.pipeline import SecurityOrchestrator


def test_graph_nodes_match_pipeline():
    assert GRAPH_NODES == (
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


def test_compiled_graph_has_every_node(tmp_path: Path):
    import asyncio

    orch = SecurityOrchestrator(
        run_id="g",
        run_dir=tmp_path / "g",
        plan="essentials",
        skip_llm=True,
        auto_approve_gates=True,
        source_path="examples/sample-web-api",
    )
    graph = build_assessment_graph(orch, asyncio.Queue())
    names = set(graph.get_graph().nodes)
    for node in GRAPH_NODES:
        assert node in names
    assert "google.adk" not in Path("agentic_security/orchestration/graph.py").read_text()
    assert "langgraph" in Path("pyproject.toml").read_text()


async def test_rejected_gate_stops_graph(tmp_path: Path):
    from agentic_security.orchestration.driver import run_full_pipeline

    orch = SecurityOrchestrator(
        run_id="rej",
        run_dir=tmp_path / "rej",
        plan="essentials",
        skip_llm=True,
        auto_approve_gates=False,
        source_path="examples/sample-web-api",
        client_name="Client",
    )

    async def _reject_after_open():
        events = []
        async for ev in run_full_pipeline(orch):
            events.append(ev)
            if ev.kind == "gate_opened" and ev.payload.get("gate_id") == "gate_1":
                orch.reject_gate("gate_1", reviewer_name="Jane", notes="stop")
        return events

    events = await _reject_after_open()
    kinds = [e.kind for e in events]
    assert "pipeline_stopped" in kinds
    assert "pipeline_completed" not in kinds
    stopped = next(e for e in events if e.kind == "pipeline_stopped")
    assert stopped.payload["gate_id"] == "gate_1"
    assert not (tmp_path / "rej" / "reports" / "pentest-assessment.html").exists()
