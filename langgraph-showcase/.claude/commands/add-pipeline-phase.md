# Add a pipeline phase

1. `PipelinePhase` in `agentic_security/orchestration/pipeline.py`
2. A node in `build_assessment_graph` (`agentic_security/orchestration/graph.py`) and an edge from the previous node. `driver.py` only streams the graph; do not put phase work back in the driver.
3. If the phase has a human gate, add a gate node that calls `orch.wait_gate` and a conditional edge to `stopped` on rejection. Register the node name in `GRAPH_NODES`.
4. Pill on `run.html`
5. Scanner writing a JSON artifact
6. Report generator in `reports/html.py` if the phase is user-visible — and a plan entitlement in `plans.py` if it is tier-gated
