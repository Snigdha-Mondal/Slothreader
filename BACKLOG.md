# Product Backlog — Slothreader

> Organized into phases with clear exit goals. Each task is a small, testable slice.
> Items marked with 🔒 require explicit Product Owner approval before proceeding.

---

## Phase 1: Environment, Data Schemas & Fixtures
**Exit Goal:** Modern Python environment configured, Pydantic data schemas established, and 4 realistic sample newsletters created as test fixtures.

- [x] **1.1 Project Setup & Packaging:** Configure `pyproject.toml`, `.env.example`, `.gitignore`, and verify Python 3.13 dependencies (`rich`, `pydantic`, `beautifulsoup4`, `sentry-sdk`, `requests`).
- [x] **1.2 Data Schemas (`app/parser/schemas.py`):** Define Pydantic models for `RawEmail`, `CleanedArticle`, `BigMove`, `ToolRadarItem`, `QuickConcept`, `SlothMetrics`, and `GazettePayload`.
- [x] **1.3 Bundled Fixtures (`tests/fixtures/`):** Create 4 realistic technical newsletter samples (TLDR Tech, ByteByteGo, PyCoder's Weekly, Hacker Newsletter) containing deliberate overlapping coverage of a shared major story and prominent sponsor advertisements.

---

## Phase 2: Deterministic Fluff Stripper
**Exit Goal:** Deterministic parser completely eliminates HTML clutter and sponsor blocks, producing clean, compressed article text with verified word count reduction.

- [x] **2.1 Fluff Stripper Implementation (`app/parser/fluff_stripper.py`):** BeautifulSoup4 DOM sanitization (strip nav, footers, scripts, tracking pixels) combined with regex rules to eliminate sponsor advertisements (`[Sponsor]`, `Presented by...`, `Thanks to our sponsor...`).
- [x] **2.2 Automated Unit Tests (`tests/test_fluff_stripper.py`):** Test suite proving 100% sponsor rejection, clean extraction of headlines/bodies, and accurate before/after word counts.

---

## Phase 3: Ingestion Layer & Demo CLI Runner
**Exit Goal:** Ingestion pipeline can load from local files (`--demo`) or TLS IMAP, and run through the fluff stripper from the command line.

- [x] **3.1 Local Loader (`app/ingest/local_loader.py`):** Load and parse bundled fixture files for zero-credential offline demo execution.
- [x] **3.2 TLS IMAP Client (`app/ingest/imap_client.py`):** Secure IMAP reader utilizing `BODY.PEEK[]` to ensure unread flags are never modified during read operations.
- [x] **3.3 CLI Orchestrator (`app/main.py`):** CLI entry point supporting `--demo` flag, config loading (`app/config.py`), and ingestion pipeline execution.

---

## Phase 4: Gemma 2 Deduplication Engine
**Exit Goal:** Local Ollama integration clusters multi-newsletter stories into deduplicated technical highlights and returns validated JSON.

- [x] **4.1 Ollama Adapter (`app/engine/gemma_client.py`):** Local HTTP client communicating with `http://localhost:11434` for model inference, handling timeouts and connectivity checks.
- [x] **4.2 Deduplication Prompts (`app/engine/prompts.py`):** System and user prompts strictly instructing Gemma 2 to deduplicate overlapping stories, reject ads, and output JSON conforming to `GazettePayload`.
- [x] **4.3 Model Selection & Fallback Approval:** Verified local Ollama has `gemma4:e4b` installed; adapter supports automatic resolution to available local Gemma models.
- [x] **4.4 Schema Validation Test (`tests/test_gemma_schema.py`):** Validate that model outputs conform strictly to the Pydantic JSON schema.

---

## Phase 5: Sentry Agent Tracing & Privacy Guardrails
**Exit Goal:** Every pipeline step is instrumented with Sentry spans, with automated tests proving zero private email text is transmitted.

- [ ] **5.1 Sentry Instrumentation (`app/telemetry/sentry_tracer.py`):** Spans for `email.clean`, `ai.gemma.deduplicate`, and `gazette.render` tracking latency, token metrics, and character compression.
- [ ] **5.2 Privacy Verification Tests (`tests/test_privacy_guarantees.py`):** Automated tests confirming `send_default_pii=False` and verifying that no email subject, sender, or body text exists in Sentry payloads.

---

## Phase 6: The Sloth Gazette Publisher & Sloth Badge
**Exit Goal:** Beautiful terminal presentation via Rich, offline HTML newspaper generation, and accurate Sloth Badge calculation.

- [ ] **6.1 Rich Terminal TUI (`app/output/tui_view.py`):** Formatted terminal tables, consolidated attribution badges (e.g. `[TLDR + ByteByteGo]`), and the Sloth Badge banner.
- [ ] **6.2 Retro HTML Newspaper & Markdown (`app/output/html_generator.py`):** Render a single-page printable retro newspaper (`gazette.html`) and clean Markdown document (`GAZETTE-YYYY-MM-DD.md`).
- [ ] **6.3 Sloth Badge Metrics:** Calculate time saved: `(Raw Ingested Words - Gazette Words) / 200 wpm`.

---

## Phase 7: Agent Skill, Documentation & Final Polish
**Exit Goal:** Agent Skills standard bundle ready, comprehensive README, and verified 3-minute hackathon judge flow.

- [ ] **7.1 Agent Skill Bundle (`skills/newsletter-digest/SKILL.md`):** Packaged skill and runner script adhering to the Agent Skills Open Standard.
- [ ] **7.2 Project Documentation (`README.md`, `LICENSE`):** Architecture diagrams, offline demo instructions, benchmark tables, and Apache-2.0 license.
- [ ] **🔒 7.3 Final End-to-End Demo Sign-Off:** Human review of complete `--demo` flow in terminal, HTML output, and Sentry trace validation.
