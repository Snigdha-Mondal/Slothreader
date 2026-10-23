# Architecture & Technical Design — Slothreader

> **Offline-first, privacy-preserving newsletter compiler powered by local Gemma 2 and Sentry Agent Tracing.**

---

## 1. System Overview

```text
┌────────────────────────────────────────────────────────────────────────┐
│ INGESTION LAYER                                                        │
│ [Live IMAP (TLS, Read-Only)]   OR   [Bundled Newsletters (--demo)]     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ raw MIME / HTML / text
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ STAGE 1: DETERMINISTIC FLUFF STRIPPER (app/parser/fluff_stripper.py)   │
│ • DOM sanitization (strip nav, footers, scripts, tracking pixels)      │
│ • Regex sponsor block filtering                                        │
│ • Raw word counting & noise reduction calculation                     │
│ [Sentry Span: email.clean]                                             │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ List[CleanedArticle]
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ STAGE 2: GEMMA 2 DEDUPLICATION ENGINE (app/engine/gemma_client.py)     │
│ • Local Ollama endpoint (http://localhost:11434)                       │
│ • Models: Google Gemma 2 (2B / 9B) or compatible open-weight models    │
│ • Cross-publisher clustering & structured JSON extraction              │
│ [Sentry Span: ai.gemma.deduplicate]                                    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ GazettePayload (JSON schema)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ STAGE 3: THE SLOTH GAZETTE PUBLISHER (app/output/)                     │
│ • Rich Terminal TUI View (tui_view.py)                                 │
│ • Offline Markdown Gazette: GAZETTE-YYYY-MM-DD.md                      │
│ • Retro 1-Page HTML Newspaper (html_generator.py)                      │
│ • The Sloth Badge (Reading minutes saved calculation)                  │
│ [Sentry Span: gazette.render]                                          │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Directory Layout & Module Responsibilities

```text
Slothreader/
├── PRD.md                                 # Product requirements and scope
├── ARCHITECTURE.md                        # Technical shape & fixed decisions (this file)
├── ENGINEERING_PLAYBOOK.md                # Operating manual & engineering manager rules
├── AGENTS.md                              # Front door for AI agents (golden rules & index)
├── CLAUDE.md                              # Forwarding alias to AGENTS.md
├── BACKLOG.md                             # Work split into phases with exit goals
├── PROGRESS.md                            # Memory log, decisions diary & known issues
├── pyproject.toml                         # Project metadata, dependencies & scripts
├── .env.example                           # Template for Sentry DSN & IMAP settings
├── .gitignore                             # Git ignore patterns
├── app/
│   ├── __init__.py
│   ├── main.py                            # CLI entrypoint (--demo or live)
│   ├── config.py                          # Pydantic Settings & environment variables
│   ├── ingest/
│   │   ├── __init__.py
│   │   ├── imap_client.py                 # TLS IMAP fetcher with BODY.PEEK[]
│   │   └── local_loader.py                # Local fixture loader for --demo mode
│   ├── parser/
│   │   ├── __init__.py
│   │   ├── fluff_stripper.py              # HTML sanitizer & regex sponsor remover
│   │   └── schemas.py                     # Pydantic models for raw/cleaned articles & digest
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── gemma_client.py                # Local Ollama Gemma 2 adapter
│   │   └── prompts.py                     # Zero-fluff deduplication system prompts
│   ├── telemetry/
│   │   ├── __init__.py
│   │   └── sentry_tracer.py               # Sentry Agent Tracing spans, metrics & privacy filters
│   └── output/
│       ├── __init__.py
│       ├── tui_view.py                    # Rich terminal layout & Sloth Badge
│       └── html_generator.py              # Retro offline newspaper generator
├── skills/
│   └── newsletter-digest/
│       ├── SKILL.md                       # Agent Skills Open Standard bundle
│       └── scripts/
│           └── run_digest.py
├── tests/
│   ├── fixtures/                          # Realistic sample newsletters (TLDR, ByteByteGo, etc.)
│   ├── test_fluff_stripper.py             # Verifies sponsor removal and DOM cleaning
│   ├── test_gemma_schema.py               # Validates JSON generation schema compliance
│   └── test_privacy_guarantees.py         # Asserts no email text or PII touches Sentry
└── docs/
    ├── README.md                          # Index of ADRs, stories, plans, manual tests
    ├── adr/                               # Architecture Decision Records
    ├── stories/                           # Detailed feature stories
    ├── plans/                             # Step-by-step implementation plans
    └── manual-tests/                      # Scripts for human verification
```

---

## 3. Fixed Decisions (Locked Tech Choices)

These decisions are locked. Changing any of them requires explicit human Product Owner approval:

1. **Local-First Inference via Ollama:**
   - Inference strictly runs on localhost (`http://localhost:11434`) using open-weight models (default: `gemma2:2b`, optional: `gemma2:9b`).
   - No external commercial cloud LLMs (OpenAI, Anthropic, cloud APIs) are allowed.

2. **Absolute Privacy & Zero PII in Sentry:**
   - Sentry instrumentation must initialize with `send_default_pii=False`.
   - Spans record only execution timings, token metrics, character counts, and sanitized error classifications.
   - Raw email bodies, email headers, sender addresses, and recipient names must **never** be passed into Sentry span data or tags.

3. **Deterministic Pre-Filtering Before LLM:**
   - Fluff stripping (ad banners, tracking pixels, navigation boilerplate) is done by deterministic code (BeautifulSoup + compiled regex) before sending text to the LLM. The LLM must not waste context tokens parsing raw HTML or sponsor blocks.

4. **Read-Only IMAP Safety:**
   - IMAP email retrieval must use `BODY.PEEK[]` to ensure message flags (`\Seen`) are never modified without explicit user command.
   - Passwords reside in local `.env` only, never logged or committed.

5. **Dual Presentation (TUI + Offline Files):**
   - Every run delivers an immediate terminal view (Rich) and writes an offline Markdown file (`GAZETTE-YYYY-MM-DD.md`) and a self-contained retro HTML newspaper.

6. **Agent Skills Open Standard Compliance:**
   - Package reusable procedures in `skills/newsletter-digest/SKILL.md` compliant with the Agent Skills standard.
