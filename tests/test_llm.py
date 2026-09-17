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


def test_compose_ollama_defaults_gemma4():
    s = Settings()
    assert s.llm_engine == "ollama"
    assert s.model_reasoning == "gemma4:latest"
    assert s.model_fast == "gemma4:latest"
    assert s.model_context_length == 131072
    assert s.llm_api_key == "ollama"


def test_ollama_native_base_strips_v1():
    from agentic_security.llm import ollama_native_base

    assert ollama_native_base("http://host.docker.internal:11434/v1") == "http://host.docker.internal:11434"
    assert ollama_native_base("http://localhost:11434/v1/") == "http://localhost:11434"


def test_openai_v1_urls_and_file_log(tmp_path, monkeypatch):
    from agentic_security.logging_config import (
        chat_completions_url,
        configure_logging,
        models_url,
    )
    from agentic_security.settings import get_settings

    assert (
        chat_completions_url("http://host.docker.internal:11434/v1")
        == "http://host.docker.internal:11434/v1/chat/completions"
    )
    assert models_url("http://host.docker.internal:11434/v1") == (
        "http://host.docker.internal:11434/v1/models"
    )
    monkeypatch.setenv("LOG_DIR", str(tmp_path))
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    get_settings.cache_clear()
    import agentic_security.logging_config as lc

    lc._CONFIGURED = False
    configure_logging()
    assert (tmp_path / "openai-v1.log").exists()
    get_settings.cache_clear()
