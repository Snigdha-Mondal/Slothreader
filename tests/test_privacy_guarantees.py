"""Unit tests verifying zero-PII and absolute privacy guarantees for Sentry telemetry."""

from unittest.mock import patch
import pytest

from app.telemetry.sentry_tracer import SentryTracer, sanitize_telemetry_data, is_pii_key


def test_is_pii_key_detection():
    assert is_pii_key("email_body") is True
    assert is_pii_key("sender_address") is True
    assert is_pii_key("raw_content") is True
    assert is_pii_key("subject_line") is True
    assert is_pii_key("html_payload") is True
    assert is_pii_key("password") is True
    assert is_pii_key("auth_token") is True

    # Allowed operational metrics
    assert is_pii_key("articles_count") is False
    assert is_pii_key("raw_word_count") is False
    assert is_pii_key("duration_seconds") is False
    assert is_pii_key("ai.model") is False


def test_sanitize_telemetry_data_strips_pii_and_arbitrary_text():
    dirty_data = {
        "email_body": "Secret confidential project email contents...",
        "sender": "ceo@enterprise.com",
        "subject": "Q3 Board Meeting Notes",
        "raw_words": 1400,
        "clean_words": 850,
        "sponsors_dropped": 3,
        "ai.model": "gemma2:2b",
        "suspicious_long_text": "This is an arbitrarily long string that should never be permitted into telemetry.",
    }

    sanitized = sanitize_telemetry_data(dirty_data)

    # Assert PII keys are purged
    assert "email_body" not in sanitized
    assert "sender" not in sanitized
    assert "subject" not in sanitized
    assert "suspicious_long_text" not in sanitized

    # Assert safe metrics remain intact
    assert sanitized["raw_words"] == 1400
    assert sanitized["clean_words"] == 850
    assert sanitized["sponsors_dropped"] == 3
    assert sanitized["ai.model"] == "gemma2:2b"


@patch("sentry_sdk.init")
def test_sentry_init_enforces_send_default_pii_false(mock_sentry_init):
    tracer = SentryTracer(dsn="https://dummykey@o0.ingest.sentry.io/0")

    mock_sentry_init.assert_called_once()
    kwargs = mock_sentry_init.call_args[1]
    assert kwargs.get("send_default_pii") is False


def test_span_recording_retains_no_email_content():
    tracer = SentryTracer(dsn=None)  # Offline mode

    with tracer.start_span(
        op="email.clean",
        description="Fluff stripping",
        data={
            "raw_word_count": 922,
            "cleaned_word_count": 674,
            "email_body": "This body must be scrubbed",
        }
    ) as span:
        pass

    assert len(tracer.recorded_spans) >= 1
    last_span = tracer.recorded_spans[-1]

    assert last_span["op"] == "email.clean"
    assert "email_body" not in last_span["data"]
    assert last_span["data"]["raw_word_count"] == 922
    assert last_span["data"]["cleaned_word_count"] == 674
    assert last_span["duration_seconds"] >= 0.0
