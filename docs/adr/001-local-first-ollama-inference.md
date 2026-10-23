# ADR 001: Local-First Inference via Ollama

## Status
Accepted

## Context
Developers' email inboxes contain proprietary code snippets, password reset links, personal correspondence, and confidential work discussions. Conventional AI summarization products require sending this raw text to cloud APIs (such as OpenAI or Anthropic), which introduces severe privacy risks, potential data leakage, and ongoing subscription costs.

## Decision
Slothreader will perform all inference exclusively on localhost using **Ollama** and open-weight models (primarily **Google Gemma 2** `gemma2:2b` or `gemma2:9b`). Zero raw email text or synthesized articles will ever be transmitted to external cloud APIs or servers.

## Consequences
- **Positive:** Absolute data privacy; zero token API expenses; complete offline operation.
- **Trade-off:** The user's machine must have sufficient RAM/VRAM to run local models (minimum ~4GB RAM for `gemma2:2b`).
