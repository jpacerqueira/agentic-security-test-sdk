import pytest

from agentic_security.llm import adk_available


def test_build_llm_uses_openai_prefix():
    if not adk_available():
        pytest.skip("google-adk[extensions] not installed")
    from agentic_security.settings import Settings

    llm = Settings(
        llm_base_url="http://localhost:11434/v1",
        llm_api_key="ollama",
        llm_engine="ollama",
        model_reasoning="gemma4:latest",
    ).build_llm()
    assert llm.model.startswith("openai/")
    assert "gemma4" in llm.model
