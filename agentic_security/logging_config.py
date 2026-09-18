"""Stdout + optional file logs for the selected LLM and OpenAI-compatible /v1 calls."""

from __future__ import annotations

import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from agentic_security.settings import get_settings

_CONFIGURED = False
V1_LOGGER = "agentic_security.openai_v1"


def utc_iso_ms(ts: float | None = None) -> str:
    """UTC timestamp with milliseconds, e.g. 2026-09-18T12:07:01.123Z."""
    if ts is None:
        ts = time.time()
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"


class UtcIsoFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        return utc_iso_ms(record.created)


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
    fmt = UtcIsoFormatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    root = logging.getLogger()
    if not root.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(fmt)
        root.addHandler(handler)
    else:
        for handler in root.handlers:
            handler.setFormatter(fmt)
    root.setLevel(level)
    for name in ("httpx", "httpcore", "openai", "litellm", "LiteLLM"):
        logging.getLogger(name).setLevel(level)

    v1 = logging.getLogger(V1_LOGGER)
    v1.setLevel(level)
    app_log = logging.getLogger("agentic_security")
    app_log.setLevel(level)
    log_dir = (settings.log_dir or "").strip()
    if log_dir:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
        if not any(
            isinstance(h, logging.FileHandler)
            and getattr(h, "baseFilename", "").endswith("openai-v1.log")
            for h in v1.handlers
        ):
            v1_fh = logging.FileHandler(path / "openai-v1.log", encoding="utf-8")
            v1_fh.setFormatter(fmt)
            v1.addHandler(v1_fh)
        if not any(
            isinstance(h, logging.FileHandler)
            and getattr(h, "baseFilename", "").endswith("agentic-security.log")
            for h in app_log.handlers
        ):
            app_fh = logging.FileHandler(path / "agentic-security.log", encoding="utf-8")
            app_fh.setFormatter(fmt)
            app_log.addHandler(app_fh)
        v1.info("openai-v1 file log %s", path / "openai-v1.log")
        app_log.info("agentic-security file log %s", path / "agentic-security.log")
    _CONFIGURED = True
    logging.getLogger("agentic_security").info(
        "logging ready level=%s log_dir=%s engine=%s profile=%s model=%s fast=%s api_base=%s",
        level_name,
        log_dir or "(stdout)",
        settings.llm_engine,
        settings.llm_profile,
        settings.model_reasoning,
        settings.model_fast,
        settings.llm_base_url,
    )
