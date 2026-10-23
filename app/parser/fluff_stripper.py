"""Deterministic Fluff Stripper for Slothreader.

Strips DOM boilerplate (navigation, headers, footers, tracking pixels)
and eliminates sponsor and affiliate blocks before text reaches the LLM.
"""

import re
from typing import List, Tuple
from bs4 import BeautifulSoup, Tag

from app.parser.schemas import RawEmail, CleanedArticle


# Regex patterns identifying sponsor advertisements across tech newsletters
SPONSOR_PATTERNS = [
    re.compile(r"\[\s*sponsor\s*\]", re.IGNORECASE),
    re.compile(r"sponsored\s*by\b", re.IGNORECASE),
    re.compile(r"\bsponsored\s*:", re.IGNORECASE),
    re.compile(r"presented\s*by\b", re.IGNORECASE),
    re.compile(r"a\s+message\s+from\s+(?:our\s+)?(?:sponsor|partner)\b", re.IGNORECASE),
    re.compile(r"thanks\s+to\s+(?:our\s+)?sponsor\b", re.IGNORECASE),
    re.compile(r"\bpartner\s+content\b", re.IGNORECASE),
]

# Elements that contain only navigation, framing, or boilerplate
UNWANTED_TAGS = [
    "header",
    "footer",
    "nav",
    "script",
    "style",
    "noscript",
    "meta",
    "link",
    "iframe",
    "svg",
    "button",
]


class FluffStripper:
    """Deterministic parser and sanitizer for raw newsletter HTML."""

    def __init__(self, additional_sponsor_patterns: List[re.Pattern] = None):
        self.sponsor_patterns = list(SPONSOR_PATTERNS)
        if additional_sponsor_patterns:
            self.sponsor_patterns.extend(additional_sponsor_patterns)

    def is_sponsor_text(self, text: str) -> bool:
        """Check if a text snippet matches known sponsor indicators."""
        return any(pattern.search(text) for pattern in self.sponsor_patterns)

    def is_tracking_pixel(self, tag: Tag) -> bool:
        """Detect tracking pixels (1x1 images, open trackers)."""
        if tag.name != "img":
            return False
        width = tag.get("width", "")
        height = tag.get("height", "")
        src = tag.get("src", "").lower()
        if width in ("1", "0") or height in ("1", "0"):
            return True
        if "pixel" in src or "track" in src or "open" in src:
            return True
        return False

    def clean_html(self, raw_html: str, source: str = "", subject: str = "", article_id: str = "") -> CleanedArticle:
        """Sanitizes raw HTML into clean, sponsor-free plain text."""
        raw_soup = BeautifulSoup(raw_html, "html.parser")
        raw_text_full = raw_soup.get_text(separator=" ", strip=True)
        raw_word_count = len(raw_text_full.split())

        soup = BeautifulSoup(raw_html, "html.parser")

        # 1. Strip tracking pixels
        for img in soup.find_all("img"):
            if self.is_tracking_pixel(img):
                img.decompose()

        # 2. Decompose generic unwanted framing tags
        for tag_name in UNWANTED_TAGS:
            for el in soup.find_all(tag_name):
                el.decompose()

        # 3. Strip sponsor containers based on class/id attributes
        sponsors_removed = 0
        sponsor_selectors = [
            lambda tag: any("sponsor" in str(cls).lower() for cls in tag.get("class", [])),
            lambda tag: any("partner-ad" in str(cls).lower() for cls in tag.get("class", [])),
            lambda tag: "sponsor" in str(tag.get("id", "")).lower(),
            lambda tag: "partner-ad" in str(tag.get("id", "")).lower(),
        ]

        for check_fn in sponsor_selectors:
            for match in soup.find_all(check_fn):
                match.decompose()
                sponsors_removed += 1

        # 4. Strip elements where the text matches sponsor patterns
        candidates = soup.find_all(["p", "div", "section", "article", "blockquote", "td", "li"])
        for el in candidates:
            if not el or not el.parent:
                continue
            text = el.get_text(separator=" ", strip=True)
            if self.is_sponsor_text(text):
                el.decompose()
                sponsors_removed += 1

        # 5. Extract cleaned text and collapse irregular whitespace
        cleaned_text = soup.get_text(separator="\n", strip=True)
        
        # Clean up lines and drop remaining unsubscribe/boilerplate remnants
        cleaned_lines = []
        for line in cleaned_text.splitlines():
            line_str = line.strip()
            if not line_str:
                continue
            # Drop trailing unsubscribe or web view links
            if re.search(r"\b(unsubscribe|view\s+online|preferences|manage\s+subscription)\b", line_str, re.IGNORECASE):
                continue
            # Double check remaining sponsor lines
            if self.is_sponsor_text(line_str):
                sponsors_removed += 1
                continue
            cleaned_lines.append(line_str)

        final_clean_text = "\n\n".join(cleaned_lines)
        cleaned_word_count = len(final_clean_text.split())

        return CleanedArticle(
            id=article_id,
            source=source,
            subject=subject,
            clean_text=final_clean_text,
            raw_word_count=raw_word_count,
            cleaned_word_count=cleaned_word_count,
            sponsors_removed=sponsors_removed,
        )

    def clean_email(self, raw_email: RawEmail) -> CleanedArticle:
        """Convenience method to clean a RawEmail model."""
        return self.clean_html(
            raw_html=raw_email.raw_html,
            source=raw_email.source,
            subject=raw_email.subject,
            article_id=raw_email.id,
        )
