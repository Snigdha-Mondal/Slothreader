"""Local Gemma 2 Ollama adapter for cross-newsletter deduplication."""

import json
import re
import time
from typing import Dict, List, Optional, Tuple
import requests

from app.config import settings
from app.engine.prompts import SYSTEM_PROMPT, build_deduplication_prompt
from app.parser.schemas import CleanedArticle, GazettePayload, SlothMetrics


class GemmaClient:
    """Communicates with local Ollama instance running Gemma 2."""

    def __init__(self, host: str = None, model: str = None, timeout: float = None):
        self.host = (host or settings.ollama_host).rstrip("/")
        self.model = model or settings.gemma_model
        self.timeout = timeout or settings.inference_timeout_seconds

    def check_ollama_status(self) -> Tuple[bool, List[str]]:
        """Checks if local Ollama daemon is active and retrieves list of installed models."""
        try:
            resp = requests.get(f"{self.host}/api/tags", timeout=3.0)
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                return True, models
        except Exception:
            pass
        return False, []

    def resolve_model(self) -> str:
        """Determines best available local Gemma model if default is not installed."""
        is_up, available = self.check_ollama_status()
        if not is_up:
            return self.model

        # If configured model is present, use it
        for m in available:
            if m.startswith(self.model):
                return m

        # Check for any other Gemma model
        for m in available:
            if "gemma" in m.lower():
                return m

        return self.model

    def deduplicate(
        self,
        articles: List[CleanedArticle],
        gazette_date: str = "2026-10-23",
        model_override: Optional[str] = None
    ) -> Tuple[GazettePayload, Dict[str, any]]:
        """Invokes local Gemma to synthesize and deduplicate articles into a GazettePayload."""
        model_to_use = model_override or self.resolve_model()
        prompt = build_deduplication_prompt(articles, gazette_date=gazette_date)

        payload = {
            "model": model_to_use,
            "prompt": prompt,
            "system": SYSTEM_PROMPT,
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.2,
                "top_p": 0.9,
            }
        }

        start_time = time.time()
        resp = requests.post(
            f"{self.host}/api/generate",
            json=payload,
            timeout=self.timeout
        )
        duration = time.time() - start_time

        if resp.status_code != 200:
            raise RuntimeError(
                f"Ollama inference failed (HTTP {resp.status_code}): {resp.text}\n"
                f"Ensure Ollama is running and model '{model_to_use}' is pulled (`ollama pull {model_to_use}`)."
            )

        data = resp.json()
        raw_response_text = data.get("response", "").strip()

        # Sanitize any accidental code block markers from response
        clean_json_str = re.sub(r"^```(?:json)?\s*", "", raw_response_text, flags=re.MULTILINE)
        clean_json_str = re.sub(r"```$", "", clean_json_str, flags=re.MULTILINE).strip()

        try:
            parsed_dict = json.loads(clean_json_str)
            gazette = GazettePayload.model_validate(parsed_dict)
        except Exception as e:
            raise ValueError(f"Failed to parse Gemma 2 output into GazettePayload: {e}\nRaw output: {raw_response_text}")

        # Compute and attach metrics
        total_raw_words = sum(a.raw_word_count for a in articles)
        total_fluff_stripped = sum(a.raw_word_count - a.cleaned_word_count for a in articles)
        total_sponsors = sum(a.sponsors_removed for a in articles)

        # Count gazette output words
        gazette_words = len(json.dumps(parsed_dict).split())
        words_saved = max(0, total_raw_words - gazette_words)
        minutes_saved = round(words_saved / 200.0, 1)
        compression_ratio = round(((total_raw_words - gazette_words) / total_raw_words * 100), 1) if total_raw_words else 0.0

        gazette.metrics = SlothMetrics(
            raw_ingested_words=total_raw_words,
            fluff_stripped_words=total_fluff_stripped,
            gazette_words=gazette_words,
            sponsors_eliminated=total_sponsors,
            reading_minutes_saved=minutes_saved,
            compression_ratio_pct=compression_ratio,
        )

        metadata = {
            "model": model_to_use,
            "duration_seconds": duration,
            "eval_count": data.get("eval_count", 0),
            "prompt_eval_count": data.get("prompt_eval_count", 0),
            "eval_duration_ns": data.get("eval_duration", 0),
        }

        return gazette, metadata

    def mock_deduplicate(
        self,
        articles: List[CleanedArticle],
        gazette_date: str = "2026-10-23"
    ) -> Tuple[GazettePayload, Dict[str, any]]:
        """Produces a deterministic synthesized gazette without requiring Ollama compute."""
        total_raw_words = sum(a.raw_word_count for a in articles)
        total_fluff_stripped = sum(a.raw_word_count - a.cleaned_word_count for a in articles)
        total_sponsors = sum(a.sponsors_removed for a in articles)

        sample_data = {
            "gazette_date": gazette_date,
            "edition_title": "The Daily Sloth Gazette",
            "big_moves": [
                {
                    "headline": "Google Releases Gemma 2 Open Weights (2B and 9B Architectures)",
                    "sources": ["TLDR Tech", "ByteByteGo", "PyCoder's Weekly", "Hacker Newsletter"],
                    "summary": "Google officially released Gemma 2 in 2B and 9B parameter variants, featuring alternating sliding-window and global attention layers. The 2B model runs at over 80 tokens/sec on consumer hardware while cutting KV cache consumption by 50%.",
                    "technical_impact": "Permits capable local LLM execution on developer laptops with zero token bills and absolute data privacy."
                },
                {
                    "headline": "PostgreSQL 17 Officially Released with Optimized Vacuuming",
                    "sources": ["TLDR Tech", "Hacker Newsletter"],
                    "summary": "Postgres 17 introduces a redesigned vacuum engine using up to 20x less memory, enhanced logical replication failover, and native JSON_TABLE support.",
                    "technical_impact": "Reduces peak IOPS spikes during high-concurrency writes by 42% on high-scale transactional workloads."
                },
                {
                    "headline": "Git 2.47 Bundles Incremental Multi-Pack Indexes (MIDX)",
                    "sources": ["TLDR Tech"],
                    "summary": "Git 2.47 introduces incremental multi-pack indexes to substantially lower repack overhead on massive mono-repositories.",
                    "technical_impact": "Improves server-side git fetch performance by 15-30% on active repositories."
                }
            ],
            "tool_radar": [
                {
                    "name": "uv",
                    "url_or_ref": "astral-sh/uv",
                    "one_liner": "Extremely fast Python package manager written in Rust, dropping installation times by 10-100x."
                },
                {
                    "name": "Ghostty",
                    "url_or_ref": "ghostty",
                    "one_liner": "Fast, feature-rich GPU-accelerated terminal emulator written in Zig with butter-smooth 120fps rendering."
                },
                {
                    "name": "Rich 13.7",
                    "url_or_ref": "Textualize/rich",
                    "one_liner": "Python library for rich text, animated progress bars, syntax highlighting, and styled tables in the terminal."
                }
            ],
            "quick_concept": {
                "topic": "Consistent Hashing with Virtual Nodes",
                "explanation": "Maps servers and keys to a circular 360-degree hash ring to prevent cache storms. Virtual nodes ensure even partition distribution without hot-spotting."
            },
            "sponsors_detected_and_skipped": total_sponsors
        }

        gazette = GazettePayload.model_validate(sample_data)
        gazette_words = len(json.dumps(sample_data).split())
        words_saved = max(0, total_raw_words - gazette_words)
        minutes_saved = round(words_saved / 200.0, 1)
        compression_ratio = round(((total_raw_words - gazette_words) / total_raw_words * 100), 1) if total_raw_words else 0.0

        gazette.metrics = SlothMetrics(
            raw_ingested_words=total_raw_words,
            fluff_stripped_words=total_fluff_stripped,
            gazette_words=gazette_words,
            sponsors_eliminated=total_sponsors,
            reading_minutes_saved=minutes_saved,
            compression_ratio_pct=compression_ratio,
        )

        metadata = {
            "model": "offline-deterministic-fallback",
            "duration_seconds": 0.05,
            "eval_count": 320,
            "prompt_eval_count": 674,
            "eval_duration_ns": 50000000,
        }

        return gazette, metadata
