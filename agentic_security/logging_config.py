"""Stdout + optional file logs for the selected LLM and OpenAI-compatible /v1 calls."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from agentic_security.settings import get_settings

_CONFIGURED = False
V1_LOGGER = "agentic_security.openai_v1"


def chat_completions_url(llm_base_url: str) -> str:
    """OpenAI Chat Completions path on an api_base that already ends with /v1."""
    base = (llm_base_url or "").rstrip("/")
    if base.endswith("/chat/completions"):
        return base
    return f"{base}/chat/completions"


def models_url(llm_base_url: str) -> str:
    base = (llm_base_url or "").rstrip("/")
    if base.endswith("/models"):
        return base
    return f"{base}/models"


def configure_logging() -> None:
    """Idempotent. Compose sets PYTHONUNBUFFERED so these lines hit `docker compose logs`."""
    global _CONFIGURED
    if _CONFIGURED:
        return
    settings = get_settings()
    level_name = (settings.log_level or "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    root = logging.getLogger()
    if not root.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(fmt)
        root.addHandler(handler)
    root.setLevel(level)
    for name in ("httpx", "httpcore", "openai", "litellm", "LiteLLM"):
        logging.getLogger(name).setLevel(level)

    v1 = logging.getLogger(V1_LOGGER)
    v1.setLevel(level)
    log_dir = (settings.log_dir or "").strip()
    if log_dir:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
        file_path = path / "openai-v1.log"
        if not any(isinstance(h, logging.FileHandler) for h in v1.handlers):
            fh = logging.FileHandler(file_path, encoding="utf-8")
            fh.setFormatter(fmt)
            v1.addHandler(fh)
        v1.info("openai-v1 file log %s", file_path)
    _CONFIGURED = True
    logging.getLogger("agentic_security").info(
        "logging ready level=%s log_dir=%s engine=%s model=%s fast=%s api_base=%s",
        level_name,
        log_dir or "(stdout)",
        settings.llm_engine,
        settings.model_reasoning,
        settings.model_fast,
        settings.llm_base_url,
    )
