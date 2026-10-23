"""Unit tests for Gemma 2 JSON schema parsing and client validation."""

import json
from unittest.mock import MagicMock, patch
import pytest

from app.engine.gemma_client import GemmaClient
from app.parser.schemas import BigMove, CleanedArticle, GazettePayload, QuickConcept, ToolRadarItem


SAMPLE_VALID_PAYLOAD = {
    "gazette_date": "2026-10-23",
    "edition_title": "The Daily Sloth Gazette",
    "big_moves": [
        {
            "headline": "Google Releases Gemma 2 Open Weights",
            "sources": ["TLDR Tech", "ByteByteGo", "PyCoder's Weekly", "Hacker Newsletter"],
            "summary": "Google has launched open weights for Gemma 2 in 2B and 9B sizes. It features alternating sliding window attention to cut KV cache memory in half.",
            "technical_impact": "Permits consumer-grade edge hardware to run capable LLMs locally with zero token fees."
        },
        {
            "headline": "PostgreSQL 17 Officially Released",
            "sources": ["TLDR Tech", "Hacker Newsletter"],
            "summary": "Postgres 17 brings a redesigned vacuum engine that consumes up to 20x less memory and improves logical replication failover.",
            "technical_impact": "Reduces peak IOPS spikes during write-heavy transactions by over 40%."
        }
    ],
    "tool_radar": [
        {
            "name": "uv",
            "url_or_ref": "astral-sh/uv",
            "one_liner": "Extremely fast Python package manager written in Rust, 10x-100x faster than pip."
        },
        {
            "name": "Ghostty",
            "url_or_ref": "ghostty",
            "one_liner": "GPU-accelerated terminal emulator written in Zig with native cross-platform rendering."
        }
    ],
    "quick_concept": {
        "topic": "Consistent Hashing with Virtual Nodes",
        "explanation": "Distributes keys over a 360-degree hash ring to prevent cache storms when adding or removing database cluster nodes."
    },
    "sponsors_detected_and_skipped": 7
}


def test_gazette_payload_validation_success():
    payload = GazettePayload.model_validate(SAMPLE_VALID_PAYLOAD)

    assert payload.gazette_date == "2026-10-23"
    assert len(payload.big_moves) == 2
    assert "TLDR Tech" in payload.big_moves[0].sources
    assert "ByteByteGo" in payload.big_moves[0].sources
    assert len(payload.tool_radar) == 2
    assert payload.quick_concept.topic == "Consistent Hashing with Virtual Nodes"
    assert payload.sponsors_detected_and_skipped == 7


def test_gazette_payload_missing_required_field_raises_error():
    invalid_data = {
        "gazette_date": "2026-10-23",
        # Missing big_moves
        "tool_radar": [],
        "quick_concept": {
            "topic": "Testing",
            "explanation": "Valid test explanation."
        }
    }
    with pytest.raises(Exception):
        GazettePayload.model_validate(invalid_data)


@patch("requests.post")
def test_gemma_client_deduplicate_with_mock(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "response": json.dumps(SAMPLE_VALID_PAYLOAD),
        "eval_count": 350,
        "prompt_eval_count": 800,
        "eval_duration": 4000000000,
    }
    mock_post.return_value = mock_resp

    client = GemmaClient(model="gemma2:2b")
    dummy_articles = [
        CleanedArticle(
            id="1",
            source="TLDR Tech",
            subject="Gemma 2",
            clean_text="Google launched Gemma 2 today.",
            raw_word_count=200,
            cleaned_word_count=150,
            sponsors_removed=1,
        )
    ]

    gazette, metadata = client.deduplicate(dummy_articles)

    assert gazette.gazette_date == "2026-10-23"
    assert len(gazette.big_moves) == 2
    assert gazette.metrics is not None
    assert gazette.metrics.raw_ingested_words == 200
    assert metadata["eval_count"] == 350
