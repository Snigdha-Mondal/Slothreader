"""Unit tests for the presentation layer (HTML generator, Markdown, and TUI)."""

from pathlib import Path
import pytest

from app.output.html_generator import render_html, render_markdown, save_gazette_files
from app.output.tui_view import display_gazette
from app.parser.schemas import BigMove, GazettePayload, QuickConcept, SlothMetrics, ToolRadarItem


@pytest.fixture
def sample_gazette() -> GazettePayload:
    return GazettePayload(
        gazette_date="2026-10-23",
        edition_title="The Daily Sloth Gazette",
        big_moves=[
            BigMove(
                headline="Google Releases Gemma 2 Open Weights",
                sources=["TLDR Tech", "ByteByteGo", "PyCoder's Weekly", "Hacker Newsletter"],
                summary="Gemma 2 has launched in 2B and 9B sizes with alternating sliding window attention.",
                technical_impact="Enables consumer laptops to run capable models locally with zero token costs."
            ),
            BigMove(
                headline="PostgreSQL 17 Released",
                sources=["TLDR Tech", "Hacker Newsletter"],
                summary="Features improved vacuum memory utilization and logical replication failover.",
                technical_impact="Eliminates high-concurrency IOPS bottlenecks."
            )
        ],
        tool_radar=[
            ToolRadarItem(
                name="uv",
                url_or_ref="astral-sh/uv",
                one_liner="Fast Python package manager written in Rust."
            )
        ],
        quick_concept=QuickConcept(
            topic="Consistent Hashing",
            explanation="Distributes keys over a 360-degree hash ring to prevent cache storms."
        ),
        sponsors_detected_and_skipped=7,
        metrics=SlothMetrics(
            raw_ingested_words=922,
            fluff_stripped_words=248,
            gazette_words=120,
            sponsors_eliminated=7,
            reading_minutes_saved=4.0,
            compression_ratio_pct=87.0
        )
    )


def test_render_html_contains_all_sections(sample_gazette: GazettePayload):
    html = render_html(sample_gazette)

    assert "The Daily Sloth Gazette" in html
    assert "Google Releases Gemma 2 Open Weights" in html
    assert "TLDR Tech + ByteByteGo + PyCoder's Weekly + Hacker Newsletter" in html
    assert "Consistent Hashing" in html
    assert "uv" in html
    assert "Sloth Badge of Honor" in html
    assert "4 Minutes" in html


def test_render_markdown_contains_all_sections(sample_gazette: GazettePayload):
    md = render_markdown(sample_gazette)

    assert "# The Daily Sloth Gazette" in md
    assert "## 🏆 Sloth Badge of Honor" in md
    assert "Google Releases Gemma 2 Open Weights" in md
    assert "astral-sh/uv" in md
    assert "Consistent Hashing" in md


def test_save_gazette_files_creates_files(tmp_path: Path, sample_gazette: GazettePayload):
    md_file, html_file = save_gazette_files(sample_gazette, output_dir=tmp_path)

    assert md_file.exists()
    assert html_file.exists()
    assert md_file.name == "GAZETTE-2026-10-23.md"
    assert html_file.name == "gazette.html"
    assert len(html_file.read_text(encoding="utf-8")) > 500


def test_display_gazette_executes_without_error(sample_gazette: GazettePayload):
    # Verifies Rich console formatting doesn't raise exception
    display_gazette(sample_gazette)
