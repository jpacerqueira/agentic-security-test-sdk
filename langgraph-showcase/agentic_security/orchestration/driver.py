from __future__ import annotations

import asyncio

from agentic_security.orchestration.graph import build_assessment_graph
from agentic_security.orchestration.pipeline import SecurityOrchestrator


async def run_full_pipeline(orch: SecurityOrchestrator):
    """Run the LangGraph assessment and yield the same events the web UI consumes."""
    events: asyncio.Queue = asyncio.Queue()
    graph = build_assessment_graph(orch, events)

    async def _invoke() -> None:
        try:
            await graph.ainvoke({})
        except Exception as exc:
            await events.put(exc)
        finally:
            await events.put(None)

    task = asyncio.create_task(_invoke())
    try:
        while True:
            item = await events.get()
            if item is None:
                break
            if isinstance(item, Exception):
                raise item
            yield item
    finally:
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
