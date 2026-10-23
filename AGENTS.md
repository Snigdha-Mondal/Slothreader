# AGENTS.md — The Front Door

> Welcome to **Slothreader**. Read this document completely at the start of every session.

---

## 1. Read the Playbook First
Before undertaking any implementation, read [`ENGINEERING_PLAYBOOK.md`](file:///c:/Users/snigd/OneDrive/Documents/Projects/Slothreader/ENGINEERING_PLAYBOOK.md). It is your operating manual and engineering manager: it defines the 9-step loop, Ready/Done definitions, and stop signs.

---

## 2. What This Project Is
**Slothreader** is a zero-effort, local-first morning gazette that rewards information laziness. It ingests unread technical newsletters, strips ads and fluff, uses local **Gemma 2** to deduplicate cross-publisher stories, and compiles a 1-page daily briefing instrumented with **Sentry Agent Tracing** without leaking a single byte of private email data.
- Product Details: [`PRD.md`](file:///c:/Users/snigd/OneDrive/Documents/Projects/Slothreader/PRD.md)
- System Architecture: [`ARCHITECTURE.md`](file:///c:/Users/snigd/OneDrive/Documents/Projects/Slothreader/ARCHITECTURE.md)

---

## 3. The 8 Golden Rules
1. **Small, verified slices:** Work in small increments. Never leave the main build broken.
2. **Evidence over assertion:** "Done" means you executed the code and witnessed the evidence.
3. **Respect fixed decisions:** Changing any locked decision requires human approval.
4. **Use shared building blocks:** Clean module boundaries; keep LLM adapters swappable.
5. **Zero secrets, zero PII:** Never commit credentials or pass email body/headers to Sentry.
6. **Stop and ask:** Pause at checkpoints (🔒 in backlog, schema changes, security boundaries).
7. **Sync docs with code:** Every commit that modifies functionality updates specs and [`PROGRESS.md`](file:///c:/Users/snigd/OneDrive/Documents/Projects/Slothreader/PROGRESS.md).
8. **Signal over stream:** Avoid noisy log dumps; search for signal and inspect errors cleanly.

---

## 4. Fixed Decisions
- **Inference:** Local-only via Ollama (`http://localhost:11434`), default model `gemma2:2b`. No cloud LLM APIs.
- **Privacy:** Sentry configured with `send_default_pii=False`. No email text or sender/recipient info in traces.
- **Fluff Stripping:** Deterministic regex & DOM parsing precedes any LLM invocation.
- **Email Access:** IMAP connections strictly read-only using `BODY.PEEK[]`.
- **Packaging:** Agent skill housed in `skills/newsletter-digest/SKILL.md` (Agent Skills Open Standard).

---

## 5. Where to Find Things

| Need | File / Location | Description |
|---|---|---|
| Operating Manual | [`ENGINEERING_PLAYBOOK.md`](file:///c:/Users/snigd/OneDrive/Documents/Projects/Slothreader/ENGINEERING_PLAYBOOK.md) | Loop, checklists, escalation, and standards |
| Product & Scope | [`PRD.md`](file:///c:/Users/snigd/OneDrive/Documents/Projects/Slothreader/PRD.md) | Personas, requirements, out-of-scope, benchmarks |
| Technical Architecture | [`ARCHITECTURE.md`](file:///c:/Users/snigd/OneDrive/Documents/Projects/Slothreader/ARCHITECTURE.md) | Data flow, module diagrams, locked tech choices |
| Current Tasks & Plan | [`BACKLOG.md`](file:///c:/Users/snigd/OneDrive/Documents/Projects/Slothreader/BACKLOG.md) | Phases, task slices, exit criteria, approval locks (`🔒`) |
| Running Memory | [`PROGRESS.md`](file:///c:/Users/snigd/OneDrive/Documents/Projects/Slothreader/PROGRESS.md) | Work diary, decisions log, known issues, next steps |
| Architecture Decisions | [`docs/adr/`](file:///c:/Users/snigd/OneDrive/Documents/Projects/Slothreader/docs/adr/) | Formal ADR records for major design decisions |
| Feature Stories & Plans| [`docs/stories/`](file:///c:/Users/snigd/OneDrive/Documents/Projects/Slothreader/docs/stories/) & [`docs/plans/`](file:///c:/Users/snigd/OneDrive/Documents/Projects/Slothreader/docs/plans/) | Deep-dive feature requirements and step-by-step plans |
| Manual Test Scripts | [`docs/manual-tests/`](file:///c:/Users/snigd/OneDrive/Documents/Projects/Slothreader/docs/manual-tests/) | Verification checklists for tests automation cannot prove |
| Agent Skill Bundle | [`skills/newsletter-digest/`](file:///c:/Users/snigd/OneDrive/Documents/Projects/Slothreader/skills/newsletter-digest/) | Agent Skills specification file and runner |
