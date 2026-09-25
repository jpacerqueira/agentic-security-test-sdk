from __future__ import annotations

from functools import lru_cache
import logging

from pydantic_settings import BaseSettings, SettingsConfigDict

log = logging.getLogger("agentic_security.settings")


class Settings(BaseSettings):
    """OpenAI-compatible /v1 via LangChain ChatOpenAI, or deterministic scanners.

    Compose points ``llm_base_url`` at ``llm-gateway`` (LiteLLM Proxy). A host
    venv can still talk to Ollama on localhost without the gateway. The proxy
    model alias is the bare tag (``gemma4:latest``), which is what ChatOpenAI
    sends. Switching ``LLM_PROFILE`` to ``bedrock`` is the AWS path; ``vertex``
    stays available for Google Cloud.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    skip_llm: bool = True
    llm_base_url: str = "http://localhost:11434/v1"
    llm_api_key: str = "ollama"
    llm_engine: str = "ollama"
    llm_profile: str = "ollama"
    model_reasoning: str = "gemma4:latest"
    model_fast: str = "gemma4:latest"
    # KV-cache window. Sent as extra_body num_ctx for LM Studio only.
    # Ollama takes context from the server / Modelfile — do not send num_ctx.
    model_context_length: int = 131072
    model_temperature: float | None = None
    llm_timeout: int = 360
    llm_ready_timeout_seconds: int = 120
    log_level: str = "INFO"
    # Empty = stdout only. Compose sets /app/logs (bind-mounted to ./logs).
    log_dir: str = ""

    runs_dir: str = "runs"
    demo_username: str = "demo"
    demo_password: str = "demobxyz"
    session_secret: str = "agentic-security-dev-secret"

    default_plan: str = "essentials"

    def gateway_model_id(self, role: str = "reasoning") -> str:
        """LiteLLM proxy model_name. ChatOpenAI sends this on /v1/chat/completions."""
        return self.model_reasoning if role == "reasoning" else self.model_fast

    def build_chat_model(self, role: str = "reasoning"):
        """LangChain ChatOpenAI pointed at the LiteLLM proxy (or any OpenAI /v1)."""
        from langchain_openai import ChatOpenAI

        model_name = self.gateway_model_id(role)
        kwargs: dict = {
            "model": model_name,
            "base_url": self.llm_base_url,
            "api_key": self.llm_api_key or "ollama",
            "timeout": self.llm_timeout,
            "max_retries": 1,
        }
        if self.model_temperature is not None:
            kwargs["temperature"] = self.model_temperature
        if self.llm_engine == "lmstudio":
            kwargs["extra_body"] = {"num_ctx": self.model_context_length}
        log.info(
            "build_chat_model(role=%s): engine=%s profile=%s model=%s api_base=%s",
            role,
            self.llm_engine,
            self.llm_profile,
            model_name,
            self.llm_base_url,
        )
        return ChatOpenAI(**kwargs)


@lru_cache
def get_settings() -> Settings:
    return Settings()
