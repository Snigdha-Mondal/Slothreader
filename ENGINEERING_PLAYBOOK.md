# Engineering Playbook — Slothreader

> **The Operating Manual and Engineering Manager for Slothreader.**
> This playbook governs how we build, how we test, when we stop, and how we preserve memory across sessions.

---

## 1. The Three Roles

| Role | Who | What They Own |
|---|---|---|
| **Product Owner** | You (the Human) | Priorities, approvals, scope changes, and anything risky, costly, or visible to the outside world. Final say on all tradeoffs. |
| **Engineering Manager** | The Playbook (this file) | The process, standards, checklists, escalation rules, and guardrails the agent must obey. |
| **Engineer** | The AI Agent | Planning, building, testing, self-reviewing, logging evidence, and keeping documentation in sync with code. |

---

## 2. Source of Truth Hierarchy

When documents or code appear to conflict, the higher level **always** wins:

```text
1. What the Human says right now     ▲ Most Trusted
2. PRD.md (Product Intent & Scope)   │
3. ARCHITECTURE.md (Technical Shape) │
4. ENGINEERING_PLAYBOOK.md (Process) │
5. BACKLOG.md (Concrete Slices)      │
6. Existing Code & Comments          ▼ Least Trusted (may be stale)
```

### The Three Rules of Truth:
1. **Found a conflict?** Don't quietly guess or pick one. Tell the user and propose a fix.
2. **Missing a detail?** Propose adding it. Never invent an unwritten architectural or product decision.
3. **Already decided?** Don't re-argue settled decisions. The Decisions Log in `PROGRESS.md` and `docs/adr/` exists so settled calls stay settled.

---

## 3. The 9-Step Loop

Every work slice goes around this loop once, producing **one small, verified, working piece**:

```text
       [1. ORIENT]  ───▶  [2. SELECT]  ───▶  [3. PLAN]
            ▲                                      │
            │                                      ▼
       [9. REFLECT]                             [4. BUILD]
            ▲                                      │
            │                                      ▼
       [8. COMMIT]  ◀───  [7. RECORD]  ◀───   [5. TEST]
                               ▲                   │
                               │                   ▼
                               └──────────────  [6. REVIEW]
```

1. **Orient:** Read `AGENTS.md`, `ENGINEERING_PLAYBOOK.md`, `PROGRESS.md`, and the current phase of `BACKLOG.md`.
2. **Select:** Pick the next unblocked task in the current phase. If it has a lock icon (`🔒`), stop and ask the user for approval.
3. **Plan:** Draft a short plan: what changes, which files are touched, and exactly how it will be verified.
4. **Build:** Write the smallest clean piece of code that fulfills the slice.
5. **Test:** Write automated tests and run the real application/command to see it work with actual output.
6. **Review:** Self-audit against security (zero PII, no hardcoded secrets), performance, and code quality standards.
7. **Record:** Update `PROGRESS.md` (what was done, what was seen, new decisions) and update relevant spec files in `docs/`.
8. **Commit:** Commit with a clear, descriptive message. Never commit broken builds.
9. **Reflect:** Log any newly discovered tasks, edge cases, or risks in `BACKLOG.md`, then start the next slice.

---

## 4. Definition of Ready & Definition of Done

### Definition of Ready (Before starting a task)
- [ ] The outcome and acceptance criteria are crystal clear.
- [ ] All prerequisite tasks are already completed.
- [ ] The slice fits neatly within one iteration.
- [ ] Relevant documentation (`PRD.md`, `ARCHITECTURE.md`, relevant specs) has been read.
- [ ] If marked with 🔒, human approval has been granted.

### Definition of Done (Before calling a task finished)
- [ ] The code implements the planned slice without scope creep.
- [ ] Automated tests pass with 100% success.
- [ ] The code was **executed for real** and verified working with observable output.
- [ ] Self-review completed: no secrets, no PII leakage, clean error handling.
- [ ] Documentation and specs are updated to match the code in the same commit.
- [ ] `PROGRESS.md` has a dated entry recording what was done, what was seen, and any decisions.
- [ ] Git commit is clean and atomic.

---

## 5. Stop Signs: When the Agent Must Stop and Ask

```text
┌─────────────────────────┬─────────────────────────┬─────────────────────────┐
│ ● GO: Do It Yourself    │ 🟡 PAUSE: Checkpoint    │ 🔴 NEVER Without        │
│                         │                         │    Explicit Approval    │
├─────────────────────────┼─────────────────────────┼─────────────────────────┤
│ • Pick next task        │ • Schema / model shifts │ • Delete data           │
│ • Write & run tests     │ • Telemetry / data logs │ • Deploy / spend money  │
│ • Follow existing code  │ • Security-related code │ • Commit secrets or PII │
│ • Small in-scope fixes  │ • External dependencies │ • Weaken security rules │
│ • Update docs & PROGRESS│ • Ambiguous requirements│ • Alter fixed decisions │
│ • Low-level choices     │ • Blocked after 2 tries │ • Expand product scope  │
└─────────────────────────┴─────────────────────────┴─────────────────────────┘
```

### How to Ask Well:
When stopping at a checkpoint or when stuck:
- Present a clear, concise question with all relevant context.
- Provide a recommended option and rationale (not an open-ended "what should I do?").
- State the tradeoff clearly so the Product Owner can make an informed decision in seconds.

### The Two-Try Rule:
If an approach fails twice (e.g., UI automation, fragile parsing, or tricky test failure), **stop banging against it**. Drop down a level of abstraction (e.g., call the parser directly, test the isolated function, or ask for guidance).

---

## 6. Core Engineering Standards

1. **Evidence Beats Assertion:** "Done" means you executed the code and observed the evidence with your own eyes. Never assume code works because it looks right.
2. **Get the Signal, Not the Stream:** Run commands quietly. Grep logs for errors or summarize results rather than dumping 20,000 tokens of noisy logs into the context.
3. **Docs Drift Quietly:** Code and docs must change together in the same commit. Out-of-date documentation is a bug.
4. **Fix the Cause, Don't Hide It:** If a linter, type-checker, or test flags an error, resolve the underlying root cause. Never suppress warnings or disable tests to force a green status.
5. **Never Fake It:** If real data or a dependency is temporarily missing, log it as `deferred` or mock it explicitly with honest indicators. A reliable red result is infinitely better than a deceptive green result.
6. **Keep the Entry File Clean:** `AGENTS.md` is read on every single interaction. Keep it concise, structured, and free of sprawling notes.

---

## 7. Memory & The Paper Trail

The agent does not carry persistent biological memory between fresh sessions. **The repository files are the memory.**

- **`PROGRESS.md`:** The running diary. Contains the current status, dated accomplishments with verified evidence, next immediate steps, the Decisions Log, and "Notes for Next Iteration".
- **`docs/adr/`:** Architecture Decision Records explaining *why* key architectural paths were chosen over alternatives.
- **`docs/stories/`:** Feature user stories linking requirements to acceptance criteria.
- **`docs/plans/`:** Detailed implementation plans for non-trivial features.
- **`docs/manual-tests/`:** Test scripts specifying what a human must verify by hand that automation cannot prove.
