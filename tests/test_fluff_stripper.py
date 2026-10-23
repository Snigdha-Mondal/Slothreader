"""Unit tests for the Deterministic Fluff Stripper."""

from pathlib import Path
import pytest

from app.parser.fluff_stripper import FluffStripper


FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def stripper() -> FluffStripper:
    return FluffStripper()


def test_tldr_cleaning_removes_sponsors_and_preserves_content(stripper: FluffStripper):
    html = (FIXTURES_DIR / "sample_tldr.html").read_text(encoding="utf-8")
    article = stripper.clean_html(html, source="TLDR Tech", subject="TLDR Daily", article_id="tldr-1")

    # Content assertions
    assert "Google Releases Gemma 2 Open Weights" in article.clean_text
    assert "PostgreSQL 17 Officially Released" in article.clean_text
    assert "Git 2.47 Bundles Incremental Multi-Pack Indexes" in article.clean_text

    # Sponsor assertions - 100% rejection
    assert "[SPONSOR]" not in article.clean_text
    assert "Neon Serverless Postgres" not in article.clean_text
    assert "Sponsored by Warp" not in article.clean_text
    assert "Unsubscribe" not in article.clean_text
    assert article.sponsors_removed >= 2
    assert article.cleaned_word_count < article.raw_word_count


def test_bytebytego_cleaning_removes_ads_and_preserves_concepts(stripper: FluffStripper):
    html = (FIXTURES_DIR / "sample_bytebytego.html").read_text(encoding="utf-8")
    article = stripper.clean_html(html, source="ByteByteGo", subject="Systems #104", article_id="bbg-1")

    # Content assertions
    assert "Sliding Window Attention" in article.clean_text
    assert "Consistent Hashing with Virtual Nodes" in article.clean_text

    # Sponsor assertions
    assert "Presented by Datadog" not in article.clean_text
    assert "Cloudflare" not in article.clean_text
    assert "manage your subscription" not in article.clean_text
    assert article.sponsors_removed >= 2
    assert article.cleaned_word_count < article.raw_word_count


def test_pycoders_cleaning_removes_ads_and_preserves_tools(stripper: FluffStripper):
    html = (FIXTURES_DIR / "sample_pycoders.html").read_text(encoding="utf-8")
    article = stripper.clean_html(html, source="PyCoder's Weekly", subject="Issue #640", article_id="pyc-1")

    # Content assertions
    assert "Running Gemma 2 Locally in Python" in article.clean_text
    assert "uv: Extremely Fast Python Package Manager" in article.clean_text
    assert "Rich 13.7" in article.clean_text

    # Sponsor assertions
    assert "A message from our sponsor" not in article.clean_text
    assert "Try Sentry for free today" not in article.clean_text
    assert article.sponsors_removed >= 1
    assert article.cleaned_word_count < article.raw_word_count


def test_hacker_newsletter_cleaning_removes_ads(stripper: FluffStripper):
    html = (FIXTURES_DIR / "sample_hacker_newsletter.html").read_text(encoding="utf-8")
    article = stripper.clean_html(html, source="Hacker Newsletter", subject="#712", article_id="hn-1")

    # Content assertions
    assert "Gemma 2 Benchmark on Consumer GPUs" in article.clean_text
    assert "Ghostty" in article.clean_text
    assert "PostgreSQL 17 Migration Notes" in article.clean_text

    # Sponsor assertions
    assert "Raycast Pro" not in article.clean_text
    assert "Tailscale" not in article.clean_text
    assert article.sponsors_removed >= 2
    assert article.cleaned_word_count < article.raw_word_count
