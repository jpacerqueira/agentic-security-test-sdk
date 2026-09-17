from __future__ import annotations

from functools import lru_cache
import logging

from pydantic_settings import BaseSettings, SettingsConfigDict

log = logging.getLogger("agentic_security.settings")


class Settings(BaseSettings):
    """Ollama (OpenAI-compatible /v1) via Google ADK LiteLlm, or deterministic scanners."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    skip_llm: bool = True
    llm_base_url: str = "http://localhost:11434/v1"
    llm_api_key: str = "ollama"
    llm_engine: str = "ollama"
    model_reasoning: str = "gemma4:latest"
    model_fast: str = "gemma4:latest"
    model_temperature: float | None = None
    llm_timeout: int = 180
    llm_ready_timeout_seconds: int = 120

    runs_dir: str = "runs"
    demo_username: str = "demo"
    demo_password: str = "demobxyz"
    session_secret: str = "agentic-security-dev-secret"

    default_plan: str = "essentials"

    def build_llm(self, role: str = "reasoning"):
        """ADK LiteLlm pointed at an OpenAI-compatible /v1 endpoint (Ollama).

        Same pattern as Micro-Cosmos: `openai/<tag>` so LiteLLM speaks the
        OpenAI Chat Completions schema against `llm_base_url`. Ollama needs a
        non-empty api_key string even though it does not authenticate.
        """
        from google.adk.models.lite_llm import LiteLlm

        model_name = self.model_reasoning if role == "reasoning" else self.model_fast
        extra_body = None
        if self.llm_engine == "lmstudio":
            extra_body = {"num_ctx": 16384}
        log.info(
            "build_llm(role=%s): engine=%s model=%s api_base=%s",
            role,
            self.llm_engine,
            model_name,
            self.llm_base_url,
        )
        return LiteLlm(
            model=f"openai/{model_name}",
            api_base=self.llm_base_url,
            api_key=self.llm_api_key or "ollama",
            drop_params=True,
            extra_body=extra_body,
            timeout=self.llm_timeout,
            temperature=self.model_temperature,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
