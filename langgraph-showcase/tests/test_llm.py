import os
from pathlib import Path

from agentic_security.settings import Settings

ROOT = Path(__file__).resolve().parents[1]


def test_gateway_model_id_is_proxy_alias():
    s = Settings(
        llm_base_url="http://localhost:11434/v1",
        llm_api_key="ollama",
        llm_engine="ollama",
        model_reasoning="gemma4:latest",
        model_fast="llama3.2:latest",
    )
    assert s.gateway_model_id("reasoning") == "gemma4:latest"
    assert s.gateway_model_id("fast") == "llama3.2:latest"


def test_build_chat_model_targets_gateway():
    from agentic_security.llm import llm_stack_available

    s = Settings(
        llm_base_url="http://llm-gateway:4000/v1",
        llm_api_key="sk-agentic-local",
        llm_engine="gateway",
        model_reasoning="gemma4:latest",
    )
    assert s.gateway_model_id() == "gemma4:latest"
    if not llm_stack_available():
        return
    chat = s.build_chat_model()
    assert chat.model_name == "gemma4:latest"
    assert str(chat.openai_api_base).rstrip("/") == "http://llm-gateway:4000/v1"


def test_code_defaults_gemma4_ollama(monkeypatch):
    """Host-venv defaults: direct Ollama. Compose overrides these via env."""
    for key in list(os.environ):
        if key.startswith(("LLM_", "MODEL_")):
            monkeypatch.delenv(key, raising=False)
    s = Settings(_env_file=None)
    assert s.llm_engine == "ollama"
    assert s.llm_profile == "ollama"
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
    assert (tmp_path / "agentic-security.log").exists()
    logged = (tmp_path / "openai-v1.log").read_text()
    assert "Z" in logged and "T" in logged
    get_settings.cache_clear()


def test_utc_iso_ms_has_milliseconds():
    from agentic_security.logging_config import utc_iso_ms

    stamp = utc_iso_ms()
    assert stamp.endswith("Z")
    assert "T" in stamp
    frac = stamp.split(".")[-1]
    assert len(frac) == 4  # 123Z


def test_uses_ollama_native_warm_skips_gateway():
    from agentic_security.llm import uses_ollama_native_warm

    assert uses_ollama_native_warm("ollama", "http://localhost:11434/v1") is True
    assert uses_ollama_native_warm("gateway", "http://llm-gateway:4000/v1") is False
    assert uses_ollama_native_warm("ollama", "http://llm-gateway:4000/v1") is False
    assert uses_ollama_native_warm("lmstudio", "http://host.docker.internal:1234/v1") is False
    assert uses_ollama_native_warm("bedrock", "http://llm-gateway:4000/v1") is False
    assert uses_ollama_native_warm("vertex", "http://llm-gateway:4000/v1") is False


def test_compose_routes_app_through_llm_gateway():
    compose = (ROOT / "docker-compose.yml").read_text()
    assert "\n  llm-gateway:" in compose or "\n  llm-gateway:\n" in compose or "llm-gateway:" in compose
    assert "http://llm-gateway:4000/v1" in compose
    assert '"8090:8090"' in compose
    assert '"4000:4000"' in compose
    assert "OLLAMA_LITELLM_MODEL: ${OLLAMA_LITELLM_MODEL:-ollama_chat/gemma4:latest}" in compose
    assert "MODEL_REASONING: ${MODEL_REASONING:-gemma4:latest}" in compose
    assert "LLM_PROFILE: ${LLM_PROFILE:-ollama}" in compose
    assert "ghcr.io/berriai/litellm:main-stable" in compose
    profiles = {p.name for p in (ROOT / "llm-gateway" / "profiles").glob("*.yaml")}
    assert profiles == {"ollama.yaml", "lmstudio.yaml", "bedrock.yaml", "vertex.yaml"}
    ollama = (ROOT / "llm-gateway" / "profiles" / "ollama.yaml").read_text()
    assert "gemma4:latest" in ollama
    assert "OLLAMA_API_BASE" in ollama
    assert "keep_alive" in ollama
    assert "custom_callbacks.proxy_handler_instance" in ollama
    assert "json_logs: true" in ollama
    for name in ("lmstudio.yaml", "bedrock.yaml", "vertex.yaml"):
        text = (ROOT / "llm-gateway" / "profiles" / name).read_text()
        assert "custom_callbacks.proxy_handler_instance" in text
        assert "json_logs: true" in text
    entry = (ROOT / "llm-gateway" / "entrypoint.sh").read_text()
    assert "ollama|lmstudio|bedrock|vertex" in entry
    assert "no failover" in entry
    assert "--detailed_debug" in entry
    callback = (ROOT / "llm-gateway" / "profiles" / "custom_callbacks.py").read_text()
    assert "duration_ms" in callback
    assert "proxy_handler_instance" in callback
    assert "GATEWAY_LOG_DIR" in compose


async def test_warm_model_uses_chat_completions_on_gateway(monkeypatch):
    from agentic_security import llm as llm_mod
    from agentic_security.settings import get_settings

    monkeypatch.setenv("LLM_ENGINE", "gateway")
    monkeypatch.setenv("LLM_BASE_URL", "http://llm-gateway:4000/v1")
    monkeypatch.setenv("LLM_API_KEY", "sk-agentic-local")
    monkeypatch.setenv("LLM_PROFILE", "ollama")
    get_settings.cache_clear()
    calls: list[tuple[str, object, object]] = []

    class _Resp:
        status_code = 200

    class _Client:
        def __init__(self, *a, **k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def post(self, url, headers=None, json=None):
            calls.append((url, headers, json))
            return _Resp()

    monkeypatch.setattr(llm_mod.httpx, "AsyncClient", _Client)
    try:
        msg = await llm_mod.warm_model()
    finally:
        get_settings.cache_clear()
    assert "warmed" in msg
    assert calls
    assert calls[0][0] == "http://llm-gateway:4000/v1/chat/completions"
    assert calls[0][2]["model"] == "gemma4:latest"
    assert calls[0][1]["Authorization"] == "Bearer sk-agentic-local"
