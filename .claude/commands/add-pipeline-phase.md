# Add a pipeline phase

1. `PipelinePhase` in `agentic_security/orchestration/pipeline.py`
2. A step in `run_full_pipeline` (`driver.py`)
3. Pill on `run.html`
4. Scanner writing a JSON artifact
5. Report generator in `reports/html.py` if the phase is user-visible — and a plan entitlement in `plans.py` if it is tier-gated
