---
name: newsletter-digest
description: Ingests technical newsletters, deterministically strips sponsor clutter, deduplicates overlapping stories across sources, and compiles a high-density 1-page digest using local Gemma 2. Use when a user wants to catch up on email reading with zero mental effort. Never forwards email text to external cloud APIs.
license: Apache-2.0
compatibility: Requires local Ollama running gemma2:2b, gemma4:e4b or compatible Gemma model, and Python 3.10+.
metadata:
  author: Slothreader Contributors
  version: "0.1.0"
---

# Newsletter Digest Skill

The `newsletter-digest` skill automates the compilation of unread technical newsletters into a consolidated, ad-free daily morning briefing without leaking private email contents.

## What It Does
1. **Ingests:** Pulls unread newsletters from an IMAP folder (via read-only `BODY.PEEK[]`) or loads bundled demo fixtures.
2. **Cleans:** Deterministically removes sponsor blocks, tracking pixels, navigation clutter, and footers.
3. **Deduplicates:** Uses local Google Gemma 2 via Ollama to merge multi-publisher reporting of identical stories into single high-impact insights.
4. **Publishes:** Produces a terminal briefing, retro HTML newspaper (`gazette.html`), and Markdown edition (`GAZETTE-YYYY-MM-DD.md`).
5. **Observability:** Tracks pipeline execution with Sentry Agent Tracing while strictly guaranteeing zero PII transmission (`send_default_pii=False`).

## When to Run
- When a user asks: "Catch me up on my technical newsletters", "Summarize today's tech news", or "Run my morning briefing".
- During daily scheduled morning automation.

## Quick Execution
Run the bundled demo fixtures:
```bash
python -m app.main --demo
```

Or execute against a live configured inbox:
```bash
python -m app.main --live
```
