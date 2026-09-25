"""LiteLLM Proxy callback: one structured line per call with full UTC timeframes.

Loaded by every profile YAML as ``custom_callbacks.proxy_handler_instance``.
Must live in the same directory as the profile YAML (LiteLLM adds that dir to
sys.path). Does not log prompt bodies — chars / token counts only.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import os
import threading

from litellm.integrations.custom_logger import CustomLogger

_LOCK = threading.Lock()
_LOG_PATH = Path(os.environ.get("GATEWAY_LOG_DIR", "/app/logs")) / "llm-gateway.log"


def _as_utc(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        dt = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(float(value), tz=timezone.utc)
        except (OSError, OverflowError, ValueError):
            return None
    return None


def _iso(value) -> str:
    dt = _as_utc(value)
    if dt is None:
        return "n/a" if value is None else str(value)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"


def _ms(start, end) -> str:
    a, b = _as_utc(start), _as_utc(end)
    if a is None or b is None:
        return "n/a"
    return f"{(b - a).total_seconds() * 1000:.1f}"


def _usage(response_obj) -> dict:
    usage = getattr(response_obj, "usage", None)
    if usage is None and isinstance(response_obj, dict):
        usage = response_obj.get("usage")
    if usage is None:
        return {}
    if isinstance(usage, dict):
        return {
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "total_tokens": usage.get("total_tokens"),
        }
    return {
        "prompt_tokens": getattr(usage, "prompt_tokens", None),
        "completion_tokens": getattr(usage, "completion_tokens", None),
        "total_tokens": getattr(usage, "total_tokens", None),
    }


def _prompt_chars(kwargs: dict) -> int:
    messages = kwargs.get("messages") or []
    n = 0
    for msg in messages:
        if isinstance(msg, dict):
            content = msg.get("content") or ""
        else:
            content = getattr(msg, "content", "") or ""
        n += len(content) if isinstance(content, str) else len(str(content))
    return n


def _emit(payload: dict) -> None:
    line = json.dumps(payload, default=str, separators=(",", ":"))
    print(line, flush=True)
    try:
        _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with _LOCK:
            with _LOG_PATH.open("a", encoding="utf-8") as fh:
                fh.write(line + "\n")
    except OSError:
        pass


class GatewayTimingLogger(CustomLogger):
    def log_pre_api_call(self, model, messages, kwargs):
        now = datetime.now(timezone.utc)
        kw = kwargs or {}
        params = kw.get("litellm_params") or {}
        _emit(
            {
                "event": "gateway_call_start",
                "logged_at": _iso(now),
                "profile": os.environ.get("LLM_PROFILE", ""),
                "model": model or kw.get("model"),
                "upstream_model": params.get("model"),
                "api_base": params.get("api_base") or kw.get("api_base"),
                "call_id": kw.get("litellm_call_id") or kw.get("id"),
                "call_start": _iso(now),
                "message_count": len(messages or kw.get("messages") or []),
                "prompt_chars": _prompt_chars({"messages": messages or kw.get("messages")}),
                "stream": bool(kw.get("stream")),
            }
        )

    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        self._finish("gateway_call_success", kwargs, response_obj, start_time, end_time)

    def log_failure_event(self, kwargs, response_obj, start_time, end_time):
        self._finish("gateway_call_failure", kwargs, response_obj, start_time, end_time)

    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        self._finish("gateway_call_success", kwargs, response_obj, start_time, end_time)

    async def async_log_failure_event(self, kwargs, response_obj, start_time, end_time):
        self._finish("gateway_call_failure", kwargs, response_obj, start_time, end_time)

    def _finish(self, event: str, kwargs, response_obj, start_time, end_time) -> None:
        kw = kwargs or {}
        params = kw.get("litellm_params") or {}
        metadata = params.get("metadata") or {}
        api_start = kw.get("api_call_start_time") or params.get("api_call_start_time")
        api_end = kw.get("api_call_end_time") or params.get("api_call_end_time") or end_time
        err = None
        if event.endswith("failure"):
            err = str(kw.get("exception") or response_obj or "")[:500]
        payload = {
            "event": event,
            "logged_at": _iso(datetime.now(timezone.utc)),
            "profile": os.environ.get("LLM_PROFILE", ""),
            "call_id": kw.get("litellm_call_id") or metadata.get("litellm_call_id"),
            "model": kw.get("model") or params.get("model_alias") or params.get("model"),
            "upstream_model": params.get("model") or kw.get("custom_llm_provider"),
            "custom_llm_provider": kw.get("custom_llm_provider")
            or params.get("custom_llm_provider"),
            "api_base": params.get("api_base") or kw.get("api_base"),
            "call_start": _iso(start_time),
            "call_end": _iso(end_time),
            "duration_ms": _ms(start_time, end_time),
            "upstream_start": _iso(api_start) if api_start else "n/a",
            "upstream_end": _iso(api_end) if api_end else "n/a",
            "upstream_ms": _ms(api_start, api_end) if api_start else "n/a",
            "overhead_ms": _overhead_ms(start_time, end_time, api_start, api_end),
            "stream": bool(kw.get("stream")),
            "message_count": len(kw.get("messages") or []),
            "prompt_chars": _prompt_chars(kw),
            "error": err,
        }
        payload.update(_usage(response_obj))
        std = kw.get("standard_logging_object") or {}
        if isinstance(std, dict):
            for key in (
                "response_time",
                "overhead_duration_ms",
                "api_call_duration_ms",
                "status",
                "status_code",
            ):
                if std.get(key) is not None:
                    payload[key] = std.get(key)
        _emit(payload)


def _overhead_ms(start, end, api_start, api_end) -> str:
    total = _ms(start, end)
    up = _ms(api_start, api_end) if api_start else "n/a"
    try:
        return f"{float(total) - float(up):.1f}"
    except (TypeError, ValueError):
        return "n/a"


proxy_handler_instance = GatewayTimingLogger()
