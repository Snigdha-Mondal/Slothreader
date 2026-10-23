"""Local fixture loader for zero-credential offline --demo mode."""

from pathlib import Path
from typing import List
from bs4 import BeautifulSoup

from app.parser.schemas import RawEmail


# Known source mappings for bundled demo fixtures
FIXTURE_SOURCES = {
    "sample_tldr.html": ("TLDR Tech", "TLDR Tech Daily: Google Releases Gemma 2"),
    "sample_bytebytego.html": ("ByteByteGo", "ByteByteGo Systems: Gemma 2 Attention & Consistent Hashing"),
    "sample_pycoders.html": ("PyCoder's Weekly", "PyCoder's Weekly #640: Running Gemma 2 Locally"),
    "sample_hacker_newsletter.html": ("Hacker Newsletter", "Hacker Newsletter #712: Gemma 2 Consumer Benchmarks"),
}


class LocalNewsletterLoader:
    """Loads bundled HTML newsletter fixtures from disk for demo and offline evaluations."""

    def __init__(self, fixtures_dir: Path = None):
        if fixtures_dir is None:
            # Default to tests/fixtures relative to repo root
            self.fixtures_dir = Path(__file__).resolve().parent.parent.parent / "tests" / "fixtures"
        else:
            self.fixtures_dir = Path(fixtures_dir)

    def load_demo_newsletters(self) -> List[RawEmail]:
        """Loads all bundled demo HTML newsletters into RawEmail objects."""
        if not self.fixtures_dir.exists():
            raise FileNotFoundError(f"Fixtures directory not found at: {self.fixtures_dir}")

        emails: List[RawEmail] = []
        html_files = sorted(self.fixtures_dir.glob("*.html"))

        if not html_files:
            raise ValueError(f"No .html fixtures found in {self.fixtures_dir}")

        for filepath in html_files:
            raw_html = filepath.read_text(encoding="utf-8")
            
            # Determine source and subject from mapping or fallback to DOM title
            if filepath.name in FIXTURE_SOURCES:
                source, subject = FIXTURE_SOURCES[filepath.name]
            else:
                soup = BeautifulSoup(raw_html, "html.parser")
                title_tag = soup.find("title")
                subject = title_tag.get_text(strip=True) if title_tag else filepath.stem
                source = filepath.stem.replace("sample_", "").replace("_", " ").title()

            soup = BeautifulSoup(raw_html, "html.parser")
            raw_text = soup.get_text(separator=" ", strip=True)
            word_count = len(raw_text.split())

            emails.append(
                RawEmail(
                    id=filepath.stem,
                    source=source,
                    subject=subject,
                    date="2026-10-23",
                    raw_html=raw_html,
                    raw_text=raw_text,
                    raw_word_count=word_count,
                )
            )

        return emails
