"""Prompt engineering templates for Gemma 2 cross-newsletter deduplication."""

from typing import List
from app.parser.schemas import CleanedArticle


SYSTEM_PROMPT = """You are Slothreader, an elite technical editor who values human time above all else.
Your mission is to read multiple technical newsletters, eliminate all fluff, and synthesize a single high-signal morning briefing.

Rules:
1. Deduplicate: If multiple newsletters talk about the same event, model release, or software update (e.g., Google Gemma 2, PostgreSQL 17), combine them into 1 concise insight citing all reporting sources in the 'sources' list.
2. Zero Ads: Never include sponsor messages, product pitches, or affiliate links.
3. Plain Truth: Focus strictly on engineering releases, architecture changes, systems benchmarks, and developer tools.
4. Output strictly valid JSON matching the schema provided. Do not include markdown code block formatting (```json) or outside conversational text.

Output JSON Schema:
{
  "gazette_date": "YYYY-MM-DD",
  "edition_title": "The Daily Sloth Gazette",
  "big_moves": [
    {
      "headline": "Concise headline of the consolidated event",
      "sources": ["List of publishers that reported this story"],
      "summary": "High-density technical summary (max 2 sentences)",
      "technical_impact": "Core architectural or engineering implication"
    }
  ],
  "tool_radar": [
    {
      "name": "Library or tool name",
      "url_or_ref": "GitHub repo slug or official URL",
      "one_liner": "One sentence explaining what problem it solves"
    }
  ],
  "quick_concept": {
    "topic": "Systems design or engineering concept of the day",
    "explanation": "Clear explanation of how it works and why it matters (max 3 sentences)"
  },
  "sponsors_detected_and_skipped": 0
}"""


def build_deduplication_prompt(articles: List[CleanedArticle], gazette_date: str = "2026-10-23") -> str:
    """Constructs the prompt containing all cleaned articles for Gemma 2 analysis."""
    sections = []
    for idx, article in enumerate(articles, start=1):
        sections.append(
            f"--- NEWSLETTER {idx}: {article.source} ---\n"
            f"Subject: {article.subject}\n\n"
            f"{article.clean_text}\n"
        )

    all_articles_text = "\n".join(sections)

    prompt = (
        f"Date: {gazette_date}\n\n"
        "Here are the cleaned technical newsletters for today. Analyze them, deduplicate overlapping stories, and produce the consolidated JSON gazette payload:\n\n"
        f"{all_articles_text}\n\n"
        "Return ONLY the raw JSON object conforming to the schema."
    )
    return prompt
