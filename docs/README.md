# Documentation Index & Paper Trail — Slothreader

> This directory houses the formal paper trail for Slothreader as specified in the AI Agent Loop operating manual.

---

## Directory Organization

- **[`adr/`](adr/):** Architecture Decision Records (ADRs). Documents *why* a particular architectural choice was made, the context, alternatives considered, and consequences.
- **[`stories/`](stories/):** Feature requirements and user stories linking PRD goals to specific technical criteria.
- **[`plans/`](plans/):** Detailed step-by-step implementation plans for complex multi-slice features.
- **[`manual-tests/`](manual-tests/):** Human verification checklists for capabilities that automated test suites cannot fully prove (e.g. visual layout inspection, offline UX).

---

## Active Records

### ADRs
- [`adr/001-local-first-ollama-inference.md`](adr/001-local-first-ollama-inference.md): Selection of local Ollama over cloud LLM APIs.
- [`adr/002-deterministic-fluff-stripping.md`](adr/002-deterministic-fluff-stripping.md): Pre-filtering sponsor ads and boilerplate with deterministic parsers.
