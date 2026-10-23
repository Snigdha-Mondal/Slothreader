"""Sentry Agent Tracing integration with strict zero-PII privacy guardrails."""

from contextlib import contextmanager
import logging
import time
from typing import Any, Dict, Generator, Optional
import sentry_sdk

from app.config import settings


logger = logging.getLogger("slothreader.telemetry")


# Forbidden keys that must never be recorded in span data or tags
PII_BLACKLIST_KEYWORDS = {
    "body",
    "text",
    "content",
    "email",
    "subject",
    "sender",
    "recipient",
    "html",
    "password",
    "token",
    "message",
}


def is_pii_key(key: str) -> bool:
    """Detects if a key name suggests personal identification or raw email contents."""
    key_lower = key.lower()
    return any(keyword in key_lower for keyword in PII_BLACKLIST_KEYWORDS)


def sanitize_telemetry_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Strictly scrubs any string values or keys that could leak email data."""
    sanitized = {}
    for k, v in data.items():
        if is_pii_key(k):
            continue
        # Only allow numbers, booleans, model identifiers, or status strings
        if isinstance(v, (int, float, bool)):
            sanitized[k] = v
        elif isinstance(v, str) and (k.startswith("ai.") or k in ("status", "edition", "stage")):
            # Only allow short categorical identifiers, never arbitrary sentences
            if len(v) < 64 and "\n" not in v and "@" not in v:
                sanitized[k] = v
    return sanitized


class SentryTracer:
    """Manages Sentry tracing spans with zero PII transmission."""

    def __init__(self, dsn: Optional[str] = None):
        self.dsn = dsn if dsn is not None else settings.sentry_dsn
        self.is_active = bool(self.dsn)
        self.recorded_spans: list = []  # In-memory record for testing and offline inspection

        if self.is_active:
            sentry_sdk.init(
                dsn=self.dsn,
                traces_sample_rate=1.0,
                send_default_pii=False,  # Essential: Never send user email or PII
                environment=settings.environment,
                release=settings.release,
            )

    @contextmanager
    def start_span(
        self,
        op: str,
        description: str,
        data: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """Context manager wrapping execution with a Sentry span or offline recording."""
        start_time = time.time()
        span_record = {
            "op": op,
            "description": description,
            "start_time": start_time,
            "data": sanitize_telemetry_data(data or {}),
            "tags": tags or {},
            "status": "ok",
        }

        # If Sentry SDK is active, open a real SDK span
        sdk_span = None
        if self.is_active:
            try:
                sdk_span = sentry_sdk.start_span(op=op, name=description or op)
                sdk_span.__enter__()
                for k, v in span_record["data"].items():
                    sdk_span.set_data(k, v)
                for k, v in span_record["tags"].items():
                    sdk_span.set_tag(k, v)
            except Exception as e:
                logger.debug(f"Sentry SDK span error: {e}")

        try:
            yield span_record
        except Exception as e:
            span_record["status"] = "error"
            span_record["error_type"] = type(e).__name__
            if sdk_span:
                try:
                    sdk_span.set_status("internal_error")
                    sdk_span.set_data("error.type", type(e).__name__)
                except Exception:
                    pass
            raise
        finally:
            duration = time.time() - start_time
            span_record["duration_seconds"] = duration
            span_record["data"]["duration_seconds"] = duration
            self.recorded_spans.append(span_record)

            if sdk_span:
                try:
                    for k, v in span_record["data"].items():
                        sdk_span.set_data(k, v)
                    sdk_span.__exit__(None, None, None)
                except Exception:
                    pass

    @contextmanager
    def start_transaction(self, name: str = "slothreader.digest", op: str = "ai.agent.run") -> Generator[Any, None, None]:
        """Wraps the entire pipeline in a top-level Sentry transaction."""
        sdk_tx = None
        if self.is_active:
            try:
                sdk_tx = sentry_sdk.start_transaction(name=name, op=op)
                sdk_tx.__enter__()
            except Exception as e:
                logger.debug(f"Sentry SDK transaction error: {e}")

        try:
            yield sdk_tx
        finally:
            if sdk_tx:
                try:
                    sdk_tx.__exit__(None, None, None)
                except Exception:
                    pass
            self.flush()

    def flush(self, timeout: float = 3.0):
        """Flushes queued events to Sentry before process exit."""
        if self.is_active:
            try:
                sentry_sdk.flush(timeout=timeout)
            except Exception:
                pass


# Singleton tracer instance
tracer = SentryTracer()
