"""Data schemas for Slothreader pipelines, articles, and gazettes."""

from typing import List, Optional
from pydantic import BaseModel, Field


class RawEmail(BaseModel):
    """Represents an unprocessed email fetched from IMAP or local mock fixtures."""
    id: str = Field(description="Unique identifier for the raw email or fixture.")
    source: str = Field(description="Newsletter publisher name, e.g. 'TLDR Tech'.")
    subject: str = Field(description="Email subject line.")
    date: Optional[str] = Field(default=None, description="Date string when email was received.")
    raw_html: str = Field(description="Raw HTML string of the email body.")
    raw_text: Optional[str] = Field(default=None, description="Optional raw text fallback.")
    raw_word_count: int = Field(default=0, description="Word count of the uncleaned content.")


class CleanedArticle(BaseModel):
    """Article content sanitized by the deterministic fluff stripper."""
    id: str = Field(description="Article identifier corresponding to the raw email.")
    source: str = Field(description="Newsletter publisher name.")
    subject: str = Field(description="Original subject line.")
    clean_text: str = Field(description="Sanitized plain text free of HTML tags and sponsor blocks.")
    raw_word_count: int = Field(default=0, description="Word count prior to cleaning.")
    cleaned_word_count: int = Field(description="Word count after removing HTML and sponsor clutter.")
    sponsors_removed: int = Field(default=0, description="Count of sponsor blocks detected and stripped.")


class BigMove(BaseModel):
    """A major macro industry event or release synthesized across newsletters."""
    headline: str = Field(description="Concise, high-impact headline.")
    sources: List[str] = Field(description="List of newsletter sources that reported this story.")
    summary: str = Field(description="High-density summary (max 2 sentences).")
    technical_impact: str = Field(description="Core engineering consequence or architectural takeaway.")


class ToolRadarItem(BaseModel):
    """An open-source repo, CLI utility, or library highlighted across newsletters."""
    name: str = Field(description="Name of the tool or library.")
    url_or_ref: str = Field(description="URL, GitHub repo slug, or official reference.")
    one_liner: str = Field(description="One-sentence description of what it solves.")


class QuickConcept(BaseModel):
    """An architectural pattern, algorithmic insight, or systems concept of the day."""
    topic: str = Field(description="Concept name, e.g. 'Consistent Hashing' or 'Event Sourcing'.")
    explanation: str = Field(description="Crystal-clear technical summary (max 3 sentences).")


class SlothMetrics(BaseModel):
    """Laziness metrics quantifying saved time and avoided noise."""
    raw_ingested_words: int = Field(description="Total word count across all raw ingested newsletters.")
    fluff_stripped_words: int = Field(description="Words eliminated by deterministic HTML and sponsor stripping.")
    gazette_words: int = Field(description="Total word count of the final synthesized Sloth Gazette.")
    sponsors_eliminated: int = Field(description="Total sponsor and affiliate blocks eliminated.")
    reading_minutes_saved: float = Field(description="Minutes of human reading time saved at 200 wpm.")
    compression_ratio_pct: float = Field(description="Percentage reduction in total word count.")


class GazettePayload(BaseModel):
    """The structured daily gazette payload synthesized by Gemma 2."""
    gazette_date: str = Field(description="Publication date (YYYY-MM-DD).")
    edition_title: str = Field(default="The Daily Sloth Gazette", description="Edition header title.")
    big_moves: List[BigMove] = Field(description="Consolidated macro developments.")
    tool_radar: List[ToolRadarItem] = Field(description="Highlighted developer tools and open-source repos.")
    quick_concept: QuickConcept = Field(description="Systems design or engineering insight of the day.")
    sponsors_detected_and_skipped: int = Field(default=0, description="Count of ads identified and rejected.")
    metrics: Optional[SlothMetrics] = Field(default=None, description="Calculated laziness metrics.")
