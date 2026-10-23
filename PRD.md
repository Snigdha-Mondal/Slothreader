# Product Requirements Document (PRD) — Slothreader

> **Slothreader is the zero-effort, local-first morning gazette that rewards information laziness.**

---

## 1. Executive Summary & Vision

Developers and technical knowledge workers face **chronic newsletter debt**: dozens of subscriptions accumulating thousands of unread emails. When major events happen (e.g., a major framework release or security vulnerability), multiple newsletters cover the same story with differing intros, while 40–60% of newsletter space is filled with sponsor banners, affiliate links, and navigation boilerplate. Sending raw inboxes to cloud LLMs poses severe privacy and security risks.

**Slothreader** solves this through an offline-first newsletter compiler and cross-source deduplicator powered by local **Google Gemma 2** (via Ollama) and instrumented with **Sentry Agent Tracing**. It ingests unread newsletters (via live IMAP or bundled demo fixtures), deterministically strips sponsor fluff and boilerplate, groups and deduplicates overlapping stories across publishers, and synthesizes a high-density, 1-page retro **"Sloth Gazette"** (Terminal TUI + Markdown/HTML) with zero private email data ever leaving the user's machine.

---

## 2. Target Personas

### 2.1 The Tech Hoarder / Habitual Procrastinator
- **Characteristics:** 1,000+ unread emails in a `Newsletters` folder.
- **Pain Point:** Anxious about missing key architectural news or security CVEs, but dreads sifting through pages of fluff.
- **Value:** Hands off the reading burden to a local agent and catches up in 60 seconds.

### 2.2 The Privacy-Conscious Developer
- **Characteristics:** Strictly avoids granting third-party SaaS apps IMAP or OAuth access to corporate or personal email.
- **Pain Point:** Cloud summarizers transmit private inbox content across the internet.
- **Value:** 100% on-device processing. Emails stay in RAM on localhost; Sentry tracing captures only sanitized operational telemetry (`send_default_pii=False`).

### 2.3 The Commuter / Offline Builder
- **Characteristics:** Works on trains, planes, or off-grid environments without constant internet.
- **Pain Point:** Web-based readers fail completely without a network connection.
- **Value:** Compiles locally and saves offline Markdown/HTML gazettes viewable anywhere.

---

## 3. Product Scope & Requirements

### 3.1 In-Scope (MVP & v1.0)

1. **Deterministic Fluff Stripper (`app/parser/fluff_stripper.py`):**
   - Clean HTML/DOM structures (strip `<header>`, `<nav>`, `<footer>`, styles, tracking pixels).
   - Regex & semantic rules to identify and drop sponsor segments (`[Sponsor]`, `Presented by...`, `A message from...`).
   - Extract raw word count metrics before and after stripping to compute noise reduction.

2. **Ingestion Layer (`app/ingest/`):**
   - **Local `--demo` Mode:** Bundles 4 pre-curated realistic tech newsletters (e.g. TLDR Tech, ByteByteGo, PyCoder's Weekly, Hacker Newsletter) for instant offline execution and hackathon evaluation without credentials.
   - **Live IMAP Connector:** Connects securely over TLS (`BODY.PEEK[]` to prevent altering email state) with app-specific password, filtering by folder/label.

3. **Gemma 2 Cross-Deduplication Engine (`app/engine/`):**
   - Connects to local Ollama instance (`http://localhost:11434`) running `gemma2:2b`, `gemma2:9b`, or compatible Gemma models.
   - Strict prompt engineering producing structured JSON:
     - `big_moves`: Top 3 macro events or releases, merging duplicate reports from multiple publishers.
     - `tool_radar`: Notable open-source tools or libraries mentioned.
     - `quick_concept`: A single architectural or engineering lesson.
     - `sponsors_detected_and_skipped`: Count of detected advertisements omitted.

4. **Sentry Agent Tracing (`app/telemetry/`):**
   - Full span instrumentation: `email.fetch`, `email.clean`, `ai.gemma.deduplicate`, `gazette.render`.
   - Tracks TTFT (Time-To-First-Token), total latency, character/token throughput, and pipeline error states.
   - Strict privacy assertion: `send_default_pii=False`. Zero email subject/body text sent to Sentry.

5. **Sloth Gazette Publisher & Sloth Badge (`app/output/`):**
   - Rich terminal UI with styled tables, progress indicators, and attribution badges (e.g., `[TLDR + ByteByteGo]`).
   - Offline 1-page retro HTML newspaper and clean Markdown export (`GAZETTE-YYYY-MM-DD.md`).
   - **Sloth Badge Calculation:**
     $$\text{Reading Time Saved (min)} = \frac{\text{Raw Ingested Words} - \text{Gazette Words}}{200 \text{ wpm}}$$

6. **Agent Skills Open Standard Bundle (`skills/newsletter-digest/SKILL.md`):**
   - Reusable Agent Skill definition enabling external agents to trigger local newsletter triage.

### 3.2 Out-of-Scope (Deferred to Future Iterations)
- Browser extensions or web bookmarklets.
- Hosted multi-tenant cloud SaaS backend.
- Paid commercial LLM APIs (OpenAI/Anthropic).
- Audio TTS narration / podcast generation.
- Two-way email manipulation (e.g., automated unsubscribe links or inbox deletion).

---

## 4. Non-Functional Requirements & Guardrails

- **Zero Data Leakage:** Raw email contents never leave local machine memory.
- **Performance:** End-to-end demo execution under 30 seconds on standard developer laptops with `gemma2:2b`.
- **Reliability & Resilience:** Graceful degradation if Ollama is unreachable (clear, user-friendly error messages with guidance to run `ollama serve`).
- **Dependencies:** Python 3.10+, standard open-source libraries (`rich`, `beautifulsoup4`, `pydantic`, `sentry-sdk`, `requests`).

---

## 5. Evaluation Benchmarks

| Metric | Target |
|---|---|
| Deduplication Precision | > 90% cross-newsletter event grouping |
| Sponsor Rejection Rate | 100% sponsor elimination |
| Word Compression Ratio | > 85% reduction in reading volume |
| Generation Latency | < 20 sec for 4 bundled newsletters |
| Privacy Guarantee | 0 bytes of email body/subject in Sentry traces |
