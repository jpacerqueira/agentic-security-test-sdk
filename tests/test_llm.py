from agentic_security.settings import Settings


def test_openai_compat_model_id():
    s = Settings(
        llm_base_url="http://localhost:11434/v1",
        llm_api_key="ollama",
        llm_engine="ollama",
        model_reasoning="gemma4:latest",
        model_fast="llama3.2:latest",
    )
    assert s.openai_model_id("reasoning") == "openai/gemma4:latest"
    assert s.openai_model_id("fast") == "openai/llama3.2:latest"


def test_build_llm_uses_openai_prefix():
    from agentic_security.llm import adk_available

    s = Settings(
        llm_base_url="http://localhost:11434/v1",
        llm_api_key="ollama",
        llm_engine="ollama",
        model_reasoning="gemma4:latest",
    )
    assert s.openai_model_id().startswith("openai/")
    if not adk_available():
        return
    llm = s.build_llm()
    assert llm.model == "openai/gemma4:latest"
