# ADR 002: Deterministic Pre-Filtering for Fluff and Sponsors

## Status
Accepted

## Context
Technical newsletters often contain 40% to 60% non-content: HTML navigation blocks, social share buttons, tracking pixels, unsubscribe links, and prominent sponsor advertisements (`[Sponsor]`, `Sponsored by...`, etc.). Passing raw, uncleaned newsletter HTML directly into an LLM context window causes token bloat, increases inference latency, and risks the LLM mistakenly treating sponsor promotions as legitimate technical news.

## Decision
Slothreader implements a deterministic pre-filtering pipeline using `BeautifulSoup4` and compiled regular expressions in `app/parser/fluff_stripper.py`. This pipeline strips DOM noise, removes sponsor blocks, and computes accurate word counts before passing clean plain text to Gemma 2.

## Consequences
- **Positive:** Reduces LLM context token usage by >50%; prevents sponsor ads from polluting the daily gazette; speeds up local inference; provides exact, un-hallucinated metrics for the Sloth Badge.
- **Trade-off:** Deterministic regex patterns must be maintained to cover diverse newsletter formatting patterns.
